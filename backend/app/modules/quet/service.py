"""Quét mã (UC-19 lấy, UC-20 giao): điện thoại gửi mã đơn, tọa độ, ảnh, chữ ký; giờ, quyền, trạng thái máy chủ quyết.

Thứ tự theo so-do.md mục 9: không thuộc chuyến → 403, chuyến sai trạng thái → 409, đơn đã có kết quả → BR-45.
"""

import unicodedata
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import luu_tru
from app.loi import LoiNghiepVu
from app.models import (
    Chuyen,
    DonHang,
    Ghep,
    LichSuTrangThai,
    LuotQuet,
    LyDo,
    NguoiDung,
    NhatKyTien,
    PhaiThu,
    TaiXe,
    Tep,
)
from app.thoi_gian import bay_gio

TEN_TRANG_THAI = {"DA_LAY": "đã lấy", "DA_GIAO": "đã giao", "THAT_BAI": "thất bại"}
VIEC = {"LAY": "quét lấy", "KHONG_LAY": "báo không lấy được", "GIAO": "giao", "GIAO_THAT_BAI": "báo giao không được"}
# (trạng thái đơn, loại quét) → trạng thái mới (BR-39, BR-40)
LAM = {
    ("DA_GHEP", "LAY"): "DA_LAY",
    ("DA_GHEP", "KHONG_LAY"): "THAT_BAI",
    ("DA_LAY", "GIAO"): "DA_GIAO",
    ("DA_LAY", "GIAO_THAT_BAI"): "THAT_BAI",
}
# Quét lặp cùng ý với kết quả đã có → trả trạng thái hiện tại, không ghi gì (BR-45). Ô khác → 409 (UC-20 quyết định 3)
LAP = {
    ("DA_LAY", "LAY"),
    ("DA_GIAO", "LAY"),
    ("DA_GIAO", "GIAO"),
    ("THAT_BAI", "KHONG_LAY"),
    ("THAT_BAI", "GIAO_THAT_BAI"),
}
LY_DO_THEO_LOAI = {"KHONG_LAY": "LAY", "GIAO_THAT_BAI": "GIAO"}  # thất bại cần lý do đúng loại (BR-42)
Gps = tuple[Decimal, Decimal, Decimal | None]  # vĩ độ, kinh độ, độ chính xác (m)


def quet(
    db: Session,
    nd: NguoiDung,
    ma_don: str,
    loai: str,
    gps: Gps | None,
    anh: list[bytes],
    ly_do_id: int | None,
    chu_ky: bytes | None = None,
    ten_nguoi_nhan: str | None = None,
) -> dict:
    ma = ma_don.strip().upper()
    tai_xe_id = db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id))
    dong = db.execute(
        select(Ghep, Chuyen.tai_xe_id)
        .join(DonHang, DonHang.id == Ghep.don_hang_id)
        .join(Chuyen, Chuyen.id == Ghep.chuyen_id)
        .where(DonHang.ma_don == ma, Ghep.hieu_luc)
    ).first()
    # Mã không có, đơn chưa ghép, đơn của chuyến người khác: cùng một câu, không lộ đơn có tồn tại (BR-38, IDOR)
    if dong is None or dong.tai_xe_id != tai_xe_id:
        raise LoiNghiepVu("BR-38", "Đơn không thuộc chuyến của bạn", 403)
    g = dong.Ghep

    # Khóa chuyến dùng chung rồi đơn (kien-truc.md mục 6): kết thúc chuyến phải đợi lượt quét đang chạy;
    # hai lượt quét cùng đơn xếp hàng, lượt sau đọc lại đơn và thấy kết quả lượt trước (BR-45)
    c = db.get(Chuyen, g.chuyen_id, with_for_update={"read": True}, populate_existing=True)
    d = db.get(DonHang, g.don_hang_id, with_for_update=True, populate_existing=True)
    if c.trang_thai != "DANG_CHAY":
        raise LoiNghiepVu("BR-38", f"Chuyến {c.ma_chuyen} chưa chạy hoặc đã kết thúc, không quét được", 409)

    if (d.trang_thai, loai) in LAP:
        return {"ma_don": d.ma_don, "trang_thai": d.trang_thai, "canh_bao": [], "lap_lai": True}
    sang = LAM.get((d.trang_thai, loai))
    if sang is None:
        ma_br = "BR-39" if loai in ("LAY", "KHONG_LAY") else "BR-40"
        thong_diep = (
            f"Đơn {d.ma_don} chưa được quét lấy, không thể {VIEC[loai]}"  # TC-BR40-02
            if d.trang_thai == "DA_GHEP"
            else f"Đơn {d.ma_don} {TEN_TRANG_THAI.get(d.trang_thai, d.trang_thai)}, không thể {VIEC[loai]}"
        )
        raise LoiNghiepVu(
            ma_br, thong_diep, 409, chi_tiet=[{"ma": ma_br, "thong_diep": thong_diep, "trang_thai": d.trang_thai}]
        )

    ly_do = None
    if loai in LY_DO_THEO_LOAI:
        ly_do = db.get(LyDo, ly_do_id) if ly_do_id is not None else None
        if ly_do is None or ly_do.ap_dung != LY_DO_THEO_LOAI[loai]:
            raise LoiNghiepVu("BR-42", f"Chọn lý do {VIEC[loai].removeprefix('báo ')} trong danh mục", 422)
        if not anh:
            raise LoiNghiepVu("BR-42", f"Báo {VIEC[loai].removeprefix('báo ')} cần ít nhất 1 ảnh", 422)
    if loai == "GIAO":
        ten_nguoi_nhan = unicodedata.normalize("NFC", ten_nguoi_nhan or "").strip()
        thieu = [ten for ten, co in (("ảnh", anh), ("chữ ký", chu_ky), ("tên người nhận", ten_nguoi_nhan)) if not co]
        if thieu:
            raise LoiNghiepVu("BR-41", f"Giao hàng cần có {', '.join(thieu)} của người nhận", 422)
        if luu_tru.kiem_anh(chu_ky) != ".png":  # sai loại 400, quá 500 KB 413 (api.md 3.2: chữ ký PNG)
            raise LoiNghiepVu("ANH_SAI_LOAI", "Chữ ký phải là ảnh PNG", 400)
    else:
        chu_ky, ten_nguoi_nhan = None, None
    if loai == "LAY":
        anh = []  # Lấy hàng không cần ảnh: gửi kèm thì bỏ qua, không lưu (UC-19 quyết định 7)
    duoi = [luu_tru.kiem_anh(a) for a in anh]  # sai loại 400, quá 500 KB 413, trước khi ghi gì

    canh_bao = [] if gps else ["THIEU_GPS"]  # BR-43: vẫn cho quét
    lat, lng, chinh_xac = gps or (None, None, None)
    da_ghi: list[str] = []
    try:
        lq = LuotQuet(
            ghep_id=g.id,
            tai_xe_id=tai_xe_id,
            loai=loai,
            lat=lat,
            lng=lng,
            do_chinh_xac_m=chinh_xac,
            thieu_gps=gps is None,
            ly_do_id=ly_do.id if ly_do else None,
            ten_nguoi_nhan=ten_nguoi_nhan,
        )
        db.add(lq)
        db.flush()
        tep = [(a, du, "ANH") for a, du in zip(anh, duoi, strict=True)] + (
            [(chu_ky, ".png", "CHU_KY")] if chu_ky else []
        )
        for du_lieu, du, loai_tep in tep:
            da_ghi.append(luu_tru.luu(du_lieu, du))
            db.add(Tep(luot_quet_id=lq.id, loai=loai_tep, duong_dan=da_ghi[-1], kich_thuoc=len(du_lieu)))
        db.add(
            LichSuTrangThai(
                doi_tuong="DON", doi_tuong_id=d.id, tu=d.trang_thai, sang=sang, ly_do=ly_do and ly_do.ten, nguoi=nd.id
            )
        )
        d.trang_thai = sang
        if sang == "THAT_BAI":
            g.ket_qua = "THAT_BAI"  # ghép vẫn hiệu lực tới khi kết thúc chuyến (BR-36, UC-18)
        if sang == "DA_GIAO":
            g.ket_qua = "DA_GIAO"
            if bay_gio() > d.han_giao:  # giao sau hạn vẫn giao, cước giữ nguyên (BR-72)
                g.giao_tre = True
                canh_bao.append("GIAO_TRE")
            _sinh_phai_thu(db, d, nd)
        db.commit()
    except Exception:
        db.rollback()
        for ten in da_ghi:  # không để ảnh mồ côi khi CSDL lỗi
            luu_tru.xoa(ten)
        raise
    return {"ma_don": d.ma_don, "trang_thai": sang, "canh_bao": canh_bao, "lap_lai": False}


def _sinh_phai_thu(db: Session, d: DonHang, nd: NguoiDung) -> None:
    """BR-56: giao xong sinh khoản phải thu bằng cước đã chốt, chưa thu; cùng giao dịch với lượt quét (sơ đồ 9)."""
    pt = PhaiThu(don_hang_id=d.id, so_tien=d.cuoc_tinh)  # unique don_hang_id: không sinh hai lần
    db.add(pt)
    db.flush()
    # Nhật ký tiền chỉ thêm, không sửa xóa (BR-62)
    db.add(
        NhatKyTien(
            bang="phai_thu",
            ban_ghi_id=pt.id,
            hanh_dong="TAO",
            gia_tri_moi=str(d.cuoc_tinh),
            ly_do=f"Giao đơn {d.ma_don}",
            nguoi=nd.id,
        )
    )
