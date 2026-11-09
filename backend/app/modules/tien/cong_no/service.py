"""UC-25 công nợ: xem phải thu, nợ theo khách; Kế toán đánh dấu đã thu một hoặc nhiều khoản của một khách (BR-56).

Trạng thái thanh toán là trường riêng của phải thu, không đổi vòng đời đơn (đơn giữ DA_GIAO).
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import DonHang, Ghep, KhachHang, LuotQuet, NguoiDung, NhatKyTien, PhaiThu, PhieuThu
from app.phan_trang import PhanTrang
from app.thoi_gian import hom_nay_vn


def _ngay_giao():
    # Giờ máy chủ của lượt quét GIAO (UC-20) của đơn
    return (
        select(func.max(LuotQuet.thoi_gian))
        .join(Ghep, Ghep.id == LuotQuet.ghep_id)
        .where(Ghep.don_hang_id == PhaiThu.don_hang_id, LuotQuet.loai == "GIAO")
        .correlate(PhaiThu)
        .scalar_subquery()
    )


def _loc(trang_thai_tt: str | None, khach_hang_id: int | None) -> list:
    return [
        dk
        for dk, co in (
            (PhaiThu.trang_thai_tt == trang_thai_tt, trang_thai_tt),
            (DonHang.khach_hang_id == khach_hang_id, khach_hang_id),
        )
        if co is not None
    ]


def danh_sach(
    db: Session, pt: PhanTrang, trang_thai_tt: str | None, khach_hang_id: int | None
) -> tuple[list[dict], int, int]:
    loc = _loc(trang_thai_tt, khach_hang_id)
    goc = select(PhaiThu).join(DonHang, DonHang.id == PhaiThu.don_hang_id).where(*loc)
    tong, tong_tien = db.execute(
        select(func.count(), func.coalesce(func.sum(PhaiThu.so_tien), 0))
        .select_from(PhaiThu)
        .join(DonHang, DonHang.id == PhaiThu.don_hang_id)
        .where(*loc)
    ).one()
    ngay_giao = _ngay_giao().label("ngay_giao")
    dong = db.execute(
        goc.add_columns(DonHang.ma_don, DonHang.khach_hang_id, KhachHang.ten, ngay_giao, PhieuThu.ngay)
        .join(KhachHang, KhachHang.id == DonHang.khach_hang_id)
        .outerjoin(PhieuThu, PhieuThu.id == PhaiThu.phieu_thu_id)
        .order_by(ngay_giao.desc().nulls_last(), PhaiThu.id.desc())
        .offset(pt.bo_qua)
        .limit(pt.so_dong)
    ).all()
    return (
        [
            {
                "id": p.id,
                "don_hang_id": p.don_hang_id,
                "ma_don": ma_don,
                "khach_hang_id": kh_id,
                "ten_khach": ten,
                "ngay_giao": giao,
                "so_tien": p.so_tien,
                "trang_thai_tt": p.trang_thai_tt,
                "phieu_thu_id": p.phieu_thu_id,
                "ngay_thu": ngay_thu,
            }
            for p, ma_don, kh_id, ten, giao, ngay_thu in dong
        ],
        tong,
        int(tong_tien),  # sum BIGINT trên PostgreSQL ra Decimal
    )


def theo_khach(db: Session) -> list[dict]:
    tong_no = func.sum(PhaiThu.so_tien)
    dong = db.execute(
        select(KhachHang.id, KhachHang.ten, func.count(PhaiThu.id), tong_no)
        .join(DonHang, DonHang.khach_hang_id == KhachHang.id)
        .join(PhaiThu, PhaiThu.don_hang_id == DonHang.id)
        .where(PhaiThu.trang_thai_tt == "CHUA_THU")
        .group_by(KhachHang.id, KhachHang.ten)
        .order_by(tong_no.desc(), KhachHang.id)
    ).all()
    return [{"khach_hang_id": i, "ten_khach": t, "so_khoan": n, "tong_no": int(s)} for i, t, n, s in dong]


def da_thu(db: Session, ids: list[int], ngay: date, nd: NguoiDung) -> dict:
    if len(set(ids)) != len(ids):
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Danh sách khoản có id trùng", 400)
    if ngay > hom_nay_vn():  # quyết định 4: được nhập muộn, không được ghi ngày chưa tới
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Ngày thu không được sau hôm nay", 400)

    # Khóa theo id tăng dần: hai lần đánh dấu chồng nhau xếp hàng, lần sau thấy DA_THU → 409 (quyết định 6)
    dong = db.execute(
        select(PhaiThu, DonHang.khach_hang_id, DonHang.ma_don)
        .join(DonHang, DonHang.id == PhaiThu.don_hang_id)
        .where(PhaiThu.id.in_(ids))
        .order_by(PhaiThu.id)
        .with_for_update(of=PhaiThu)
        .execution_options(populate_existing=True)
    ).all()
    if len(dong) != len(ids):
        thieu = sorted(set(ids) - {p.id for p, _, _ in dong})
        raise LoiNghiepVu("KHONG_TIM_THAY", f"Không tìm thấy khoản phải thu: {thieu}", 404)
    da = [ma for p, _, ma in dong if p.trang_thai_tt != "CHUA_THU"]
    if da:
        raise LoiNghiepVu(
            "BR-56",
            f"Đã thu trước đó: {', '.join(da)}; chưa đánh dấu khoản nào",
            409,
            chi_tiet=[{"ma_don": m} for m in da],
        )
    khach = {kh for _, kh, _ in dong}
    if len(khach) > 1:  # quyết định 2: một phiếu thu cho một khách
        raise LoiNghiepVu("BR-56", "Một lần đánh dấu chỉ cho các khoản của cùng một khách", 422)

    pt = PhieuThu(khach_hang_id=khach.pop(), tong_tien=sum(p.so_tien for p, _, _ in dong), ngay=ngay, nguoi_tao=nd.id)
    db.add(pt)
    db.flush()
    for p, _, _ in dong:
        p.trang_thai_tt, p.phieu_thu_id = "DA_THU", pt.id
        # Nhật ký tiền chỉ thêm (BR-62), mỗi khoản một dòng (quyết định 7)
        db.add(
            NhatKyTien(
                bang="phai_thu",
                ban_ghi_id=p.id,
                hanh_dong="DA_THU",
                gia_tri_cu="CHUA_THU",
                gia_tri_moi="DA_THU",
                ly_do=f"Phiếu thu #{pt.id} ngày {ngay:%d/%m/%Y}",
                nguoi=nd.id,
            )
        )
    db.commit()
    return {
        "phieu_thu_id": pt.id,
        "khach_hang_id": pt.khach_hang_id,
        "tong_tien": pt.tong_tien,
        "ngay": ngay,
        "so_khoan": len(dong),
    }
