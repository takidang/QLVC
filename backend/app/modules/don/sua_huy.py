"""UC-10 sửa / hủy đơn chưa lấy hàng (BR-33, 34). Đơn đang ghép: khóa chuyến → xe → tài xế → đơn (kien-truc.md),
kiểm lại cả chuyến (BR-67). Tách khỏi `don/service` vì cần hàm của `chuyen/service` (module đó đã nhập `don/service`).
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.cuoc import kiem_br31_don_hop_le, kl_quy_doi, kl_tinh_cuoc, tinh_cuoc
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, NguoiDung, NhatKyTien, TaiXe, Xe
from app.modules.chuyen import service as chuyen
from app.modules.don import service, that_bai
from app.modules.don.schemas import DonSua
from app.thoi_gian import bay_gio

TEN_TRANG_THAI = {
    "DA_LAY": "đã lấy hàng",
    "DA_GIAO": "đã giao",
    "THAT_BAI": "thất bại",
    "TRA_HANG": "đã trả hàng",
    "HUY": "đã hủy",
}


def _chuyen_cua(db: Session, don_id: int) -> int | None:
    return db.scalar(select(Ghep.chuyen_id).where(Ghep.don_hang_id == don_id, Ghep.hieu_luc))


def _khoa(db: Session, don_id: int, ma_br: str, viec: str) -> tuple[DonHang, tuple[Chuyen, Xe, TaiXe] | None]:
    """Khóa đơn, và chuyến của đơn nếu đang ghép (khóa chuyến trước đơn). Đơn vừa bị ghép / gỡ giữa lúc đọc và lúc
    khóa thì đọc lại."""
    for _ in range(3):
        cid = _chuyen_cua(db, don_id)
        khoa_chuyen = None
        if cid is not None:
            c = db.get(Chuyen, cid, with_for_update=True, populate_existing=True)
            if c.trang_thai != "LAP":
                goi_y = "mở chốt chuyến trước" if c.trang_thai == "DA_CHOT" else "chuyến đã chạy"
                raise LoiNghiepVu(
                    ma_br, f"Đơn đang ở chuyến {c.ma_chuyen} không còn Đang lập ({goi_y}), không {viec} được", 409
                )
            khoa_chuyen = (
                c,
                db.get(Xe, c.xe_id, with_for_update=True),
                db.get(TaiXe, c.tai_xe_id, with_for_update=True),
            )
        d = db.get(DonHang, don_id, with_for_update=True, populate_existing=True)
        if d is None:
            raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy đơn hàng", 404)
        if _chuyen_cua(db, don_id) == cid:
            if d.trang_thai not in ("CHO_GHEP", "DA_GHEP"):
                ten = TEN_TRANG_THAI.get(d.trang_thai, d.trang_thai)
                raise LoiNghiepVu(ma_br, f"Đơn {d.ma_don} {ten}, không {viec} được", 409)
            return d, khoa_chuyen
        db.rollback()
    raise LoiNghiepVu(ma_br, "Đơn vừa được ghép hoặc gỡ, vui lòng thử lại", 409)


def sua(db: Session, don_id: int, vao: DonSua, nguoi: NguoiDung) -> dict:
    d, khoa_chuyen = _khoa(db, don_id, "BR-33", "sửa")
    thay = vao.model_dump(exclude_unset=True)
    for k, v in thay.items():
        setattr(d, k, v)
    # BR-31 trên đơn sau khi sửa; hạn giao không đổi thì không bắt sau thời điểm sửa (quyết định 4)
    luc = bay_gio() if "han_giao" in thay else datetime.min.replace(tzinfo=UTC)
    kiem_br31_don_hop_le(d.dia_chi_lay, d.dia_chi_giao, d.lay_tu, d.lay_den, d.han_giao, luc)

    if khoa_chuyen:
        c, xe, tx = khoa_chuyen
        cu = [x for x, *_ in chuyen._dong_don_cua_chuyen(db, c.id)]
        ket_thuc, vp = chuyen.xet_ca_chuyen(db, c, xe, tx, cu, {d.id})
        if vp:
            raise LoiNghiepVu("VI_PHAM_SUA", "Sửa làm chuyến vi phạm quy tắc, chưa sửa", chi_tiet=vp)
        c.ket_thuc_du_kien = ket_thuc

    # Cước tính lại từ bản sao đã chốt trên đơn, không đọc bảng giá hiện tại (BR-32, 33, 46…48)
    kl_tc = kl_tinh_cuoc(d.kg, kl_quy_doi(d.m3, d.he_so_quy_doi_chot))
    cuoc = tinh_cuoc(kl_tc, d.don_gia_chot, d.cuoc_toi_thieu_chot, d.lam_tron_chot)
    if cuoc != d.cuoc_tinh:
        # Cước là dữ liệu tiền: ghi nhật ký chỉ thêm (BR-62, security-rules)
        db.add(
            NhatKyTien(
                bang="don_hang",
                ban_ghi_id=d.id,
                hanh_dong="SUA",
                gia_tri_cu=str(d.cuoc_tinh),
                gia_tri_moi=str(cuoc),
                ly_do=f"Sửa đơn {d.ma_don}",
                nguoi=nguoi.id,
            )
        )
    d.kl_tinh_cuoc, d.cuoc_tinh = kl_tc, cuoc
    db.commit()
    return service.lay(db, d.id)


def huy(db: Session, don_id: int, ly_do: str, nguoi: NguoiDung) -> dict:
    if db.scalar(select(DonHang.trang_thai).where(DonHang.id == don_id)) == "THAT_BAI":
        # UC-22: đơn thất bại của chuyến đã kết thúc, chỉ hủy được khi chưa lấy hàng (BR-34, 36)
        d = that_bai.khoa_that_bai(db, don_id, "hủy", "BR-34")
        if that_bai.da_lay(db, d.id):
            raise LoiNghiepVu("BR-34", f"Đơn {d.ma_don} đã lấy hàng, không hủy được: ghép lại hoặc trả hàng")
        chuyen._doi_trang_thai(db, [d], "HUY", nguoi, ly_do)
        db.commit()
        return service.lay(db, d.id)
    d, khoa_chuyen = _khoa(db, don_id, "BR-34", "hủy")
    if khoa_chuyen:
        # Đang ghép: gỡ khỏi chuyến trước (BR-34), lịch trình tính lại như gỡ ở UC-13
        c, xe, _ = khoa_chuyen
        cu = list(
            db.scalars(
                select(DonHang)
                .join(Ghep, Ghep.don_hang_id == DonHang.id)
                .where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)
                .order_by(DonHang.id)
                .with_for_update(of=DonHang)
            )
        )
        chuyen.go_da_khoa(db, c, xe, cu, {d.id}, nguoi, ly_do, "VI_PHAM_HUY")
    chuyen._doi_trang_thai(db, [d], "HUY", nguoi, ly_do)
    db.commit()
    return service.lay(db, d.id)
