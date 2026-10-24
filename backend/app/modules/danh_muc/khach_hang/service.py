from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import KhachHang
from app.modules.danh_muc.khach_hang.schemas import KhachHangSua, KhachHangVao
from app.phan_trang import PhanTrang


def tao(db: Session, vao: KhachHangVao) -> KhachHang:
    kh = KhachHang(**vao.model_dump())
    db.add(kh)
    db.commit()
    return kh


def lay(db: Session, kh_id: int, khoa: bool = False) -> KhachHang:
    kh = db.get(KhachHang, kh_id, with_for_update=khoa)
    if kh is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khách hàng", 404)
    return kh


def danh_sach(db: Session, pt: PhanTrang, trang_thai: str | None, tim: str | None) -> tuple[list[KhachHang], int]:
    loc = select(KhachHang)
    if trang_thai:
        loc = loc.where(KhachHang.trang_thai == trang_thai)
    if tim and (tim := tim.strip()):
        loc = loc.where(
            or_(KhachHang.ten.icontains(tim, autoescape=True), KhachHang.sdt.contains(tim, autoescape=True))
        )
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    kh = db.scalars(loc.order_by(KhachHang.ten, KhachHang.id).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return list(kh), tong


def sua(db: Session, kh_id: int, vao: KhachHangSua) -> KhachHang:
    kh = lay(db, kh_id, khoa=True)
    for truong, gia_tri in vao.model_dump(exclude_unset=True).items():
        setattr(kh, truong, gia_tri)
    db.commit()
    return kh
