"""Quét mã (UC-19; UC-20 thêm giao): điện thoại chỉ gửi mã đơn, tọa độ, ảnh; giờ, quyền, trạng thái do máy chủ quyết.

Thứ tự theo so-do.md mục 9: không thuộc chuyến → 403, chuyến sai trạng thái → 409, đơn đã có kết quả → BR-45.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import luu_tru
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, LyDo, NguoiDung, TaiXe, Tep

TEN_TRANG_THAI = {"DA_LAY": "đã lấy", "DA_GIAO": "đã giao", "THAT_BAI": "thất bại"}
VIEC = {"LAY": "quét lấy", "KHONG_LAY": "báo không lấy được"}
Gps = tuple[Decimal, Decimal, Decimal | None]  # vĩ độ, kinh độ, độ chính xác (m)


def quet(
    db: Session, nd: NguoiDung, ma_don: str, loai: str, gps: Gps | None, anh: list[bytes], ly_do_id: int | None
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

    if d.trang_thai != "DA_GHEP":
        # Quét lặp cùng ý → trả trạng thái hiện tại (BR-45); trái kết quả → báo rõ (TC-BR39-02, quyết định 6)
        if (loai == "LAY") == (d.trang_thai != "THAT_BAI"):
            return {"ma_don": d.ma_don, "trang_thai": d.trang_thai, "canh_bao": [], "lap_lai": True}
        ten = TEN_TRANG_THAI.get(d.trang_thai, d.trang_thai)
        raise LoiNghiepVu(
            "BR-39",
            f"Đơn {d.ma_don} {ten}, không {VIEC[loai]} được",
            409,
            chi_tiet=[{"ma": "BR-39", "thong_diep": f"Đơn {d.ma_don} {ten}", "trang_thai": d.trang_thai}],
        )

    ly_do = None
    if loai == "KHONG_LAY":
        ly_do = db.get(LyDo, ly_do_id) if ly_do_id is not None else None
        if ly_do is None or ly_do.ap_dung != "LAY":
            raise LoiNghiepVu("BR-42", "Chọn lý do không lấy được trong danh mục", 422)
        if not anh:
            raise LoiNghiepVu("BR-42", "Báo không lấy được cần ít nhất 1 ảnh", 422)
    else:
        anh = []  # Lấy hàng không cần ảnh: gửi kèm thì bỏ qua, không lưu (quyết định 7)
    duoi = [luu_tru.kiem_anh(a) for a in anh]  # sai loại 400, quá 500 KB 413, trước khi ghi gì

    sang = "DA_LAY" if loai == "LAY" else "THAT_BAI"
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
            thieu_gps=gps is None,  # BR-43: vẫn cho quét
            ly_do_id=ly_do.id if ly_do else None,
        )
        db.add(lq)
        db.flush()
        for a, du in zip(anh, duoi, strict=True):
            da_ghi.append(luu_tru.luu(a, du))
            db.add(Tep(luot_quet_id=lq.id, loai="ANH", duong_dan=da_ghi[-1], kich_thuoc=len(a)))
        ten_ly_do = ly_do.ten if ly_do else None
        db.add(
            LichSuTrangThai(
                doi_tuong="DON", doi_tuong_id=d.id, tu=d.trang_thai, sang=sang, ly_do=ten_ly_do, nguoi=nd.id
            )
        )
        d.trang_thai = sang
        if sang == "THAT_BAI":
            g.ket_qua = "THAT_BAI"  # ghép vẫn hiệu lực tới khi kết thúc chuyến (BR-36, UC-18)
        db.commit()
    except Exception:
        db.rollback()
        for ten in da_ghi:  # không để ảnh mồ côi khi CSDL lỗi
            luu_tru.xoa(ten)
        raise
    return {"ma_don": d.ma_don, "trang_thai": sang, "canh_bao": ["THIEU_GPS"] if gps is None else [], "lap_lai": False}
