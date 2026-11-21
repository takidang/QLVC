"""UC-22 xử lý đơn thất bại sau khi chuyến kết thúc (BR-36): ghép lại (BR-37, 69), trả hàng. Hủy ở `sua_huy.huy`.

"Đã lấy hàng" = có lượt quét `LAY` ở bất kỳ lần ghép nào (quyết định 1), không suy từ trạng thái.
"""

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.domain.cuoc import kiem_br31_don_hop_le
from app.loi import LoiNghiepVu
from app.models import DonHang, Ghep, LichSuTrangThai, LuotQuet, LyDo, NguoiDung, Nut
from app.modules.chuyen.service import _doi_trang_thai
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.modules.don import service
from app.modules.don.schemas import GhepLaiVao
from app.thoi_gian import bay_gio


def _quet_cua(don_id: int):
    return select(LuotQuet).join(Ghep, Ghep.id == LuotQuet.ghep_id).where(Ghep.don_hang_id == don_id)


def da_lay(db: Session, don_id: int) -> bool:
    return db.scalar(select(exists(_quet_cua(don_id).where(LuotQuet.loai == "LAY"))))


def so_lan_giao_tb_khach(db: Session, don_id: int) -> int:
    """BR-37: chỉ đếm thất bại khi giao vì lý do phía khách; sự cố xe và thất bại khi lấy không tính."""
    q = (
        select(func.count())
        .select_from(LuotQuet)
        .join(Ghep, Ghep.id == LuotQuet.ghep_id)
        .join(LyDo, LyDo.id == LuotQuet.ly_do_id)
        .where(Ghep.don_hang_id == don_id, LuotQuet.loai == "GIAO_THAT_BAI", LyDo.phia == "KHACH")
    )
    return db.scalar(q)


def _con_ghep(db: Session, don_id: int) -> bool:
    return db.scalar(select(exists().where(Ghep.don_hang_id == don_id, Ghep.hieu_luc)))


def khoa_that_bai(db: Session, don_id: int, viec: str, ma_br: str = "BR-36") -> DonHang:
    """Khóa đơn THAT_BAI của chuyến đã kết thúc (ghép đã hết hiệu lực, BR-36)."""
    d = db.get(DonHang, don_id, with_for_update=True, populate_existing=True)
    if d is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy đơn hàng", 404)
    if d.trang_thai != "THAT_BAI":
        raise LoiNghiepVu(ma_br, f"Đơn {d.ma_don} không ở trạng thái Thất bại, không {viec} được", 409)
    if _con_ghep(db, d.id):
        raise LoiNghiepVu(ma_br, f"Đơn {d.ma_don} còn ở chuyến chưa kết thúc, chờ chuyến kết thúc rồi {viec}", 409)
    return d


def ghep_lai(db: Session, don_id: int, vao: GhepLaiVao, nguoi: NguoiDung) -> dict:
    d = khoa_that_bai(db, don_id, "ghép lại")
    nguong = int(cau_hinh.lay(db, "CFG-04"))
    if (so := so_lan_giao_tb_khach(db, d.id)) >= nguong:
        raise LoiNghiepVu(
            "BR-37", f"Đơn {d.ma_don} đã {so} lần giao thất bại vì phía khách (ngưỡng {nguong}), chỉ còn trả hàng"
        )
    co_noi_giu = vao.nut_giu_id is not None or vao.dia_chi_giu is not None
    ly_do = "Ghép lại"
    if da_lay(db, d.id):
        if vao.nut_giu_id is None or vao.dia_chi_giu is None:
            raise LoiNghiepVu("BR-69", f"Đơn {d.ma_don} đã lấy hàng: cần chọn nút và địa chỉ nơi giữ hàng")
        nut = db.get(Nut, vao.nut_giu_id)
        if nut is None:
            raise LoiNghiepVu("KHONG_TIM_THAY", f"Không tìm thấy nút {vao.nut_giu_id}", 404)
        # Nơi giữ thay điểm lấy khi ghép (BR-69); hàng đã ở kho nên bỏ khung giờ lấy hẹn với khách
        d.nut_giu_id, d.dia_chi_giu, d.lat_giu, d.lng_giu = nut.id, vao.dia_chi_giu, vao.lat_giu, vao.lng_giu
        d.lay_tu = d.lay_den = None
        ly_do = f"Ghép lại, giữ hàng tại {nut.ten}"
    elif co_noi_giu:
        raise LoiNghiepVu("BR-69", f"Đơn {d.ma_don} chưa lấy hàng, không có nơi giữ hàng")
    if vao.han_giao is not None:
        d.han_giao = vao.han_giao
        kiem_br31_don_hop_le(d.dia_chi_lay, d.dia_chi_giao, d.lay_tu, d.lay_den, d.han_giao, bay_gio())
    _doi_trang_thai(db, [d], "CHO_GHEP", nguoi, ly_do)  # cước giữ nguyên (BR-69)
    db.commit()
    return service.lay(db, d.id)


def tra_hang(db: Session, don_id: int, ly_do: str | None, nguoi: NguoiDung) -> dict:
    d = khoa_that_bai(db, don_id, "trả hàng")
    if not da_lay(db, d.id):
        raise LoiNghiepVu("BR-36", f"Đơn {d.ma_don} chưa lấy hàng, không có gì để trả: ghép lại hoặc hủy")
    # Xử lý ngoài hệ thống, không sinh doanh thu (BR-36)
    _doi_trang_thai(db, [d], "TRA_HANG", nguoi, ly_do or "Trả hàng cho khách")
    db.commit()
    return service.lay(db, d.id)


def can_xu_ly(db: Session) -> list[dict]:
    """Đơn THAT_BAI kèm thông tin để chọn cách xử lý (UC-22 bước 1)."""
    nguong = int(cau_hinh.lay(db, "CFG-04"))
    dong = db.execute(service.truy_van_don().where(DonHang.trang_thai == "THAT_BAI").order_by(DonHang.id)).all()
    ra = []
    for d in dong:
        don_id = d[0].id
        # Lý do của lần vào THAT_BAI gần nhất: quét thất bại ghi tên lý do, kết thúc do sự cố ghi "Sự cố xe: …"
        cuoi = db.scalar(
            select(LichSuTrangThai.ly_do)
            .where(
                LichSuTrangThai.doi_tuong == "DON",
                LichSuTrangThai.doi_tuong_id == don_id,
                LichSuTrangThai.sang == "THAT_BAI",
            )
            .order_by(LichSuTrangThai.id.desc())
            .limit(1)
        ) or db.scalar(
            _quet_cua(don_id)
            .with_only_columns(LyDo.ten)
            .join(LyDo, LyDo.id == LuotQuet.ly_do_id)
            .order_by(LuotQuet.id.desc())
            .limit(1)
        )
        ra.append(
            service.ra_don(d)
            | {
                "da_lay": da_lay(db, don_id),
                "so_lan_giao_tb_khach": so_lan_giao_tb_khach(db, don_id),
                "nguong": nguong,
                "ly_do_cuoi": cuoi,
                "cho_chuyen_xong": _con_ghep(db, don_id),
            }
        )
    return ra
