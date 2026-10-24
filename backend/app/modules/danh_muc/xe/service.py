from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.xe_tai_xe import kiem_br14_khoi_luong_toan_bo
from app.loi import LoiNghiepVu
from app.models import ChiPhiCoDinhXe, NguoiDung, NhatKyTien, Xe
from app.modules.danh_muc.xe.schemas import XeSua, XeVao
from app.phan_trang import PhanTrang


def _bien_so_trung(bien_so: str) -> LoiNghiepVu:
    return LoiNghiepVu("BIEN_SO_TRUNG", f"Biển số {bien_so} đã có trong hệ thống", 409)


def _luu(db: Session, xe: Xe) -> Xe:
    # Kiểm trùng bằng ràng buộc unique ở CSDL: hai người thêm cùng lúc thì chỉ một người thành công
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _bien_so_trung(xe.bien_so) from None
    return xe


def tao(db: Session, vao: XeVao) -> Xe:
    kiem_br14_khoi_luong_toan_bo(vao.tai_trong_kg, vao.ktt_toan_bo_kg)
    xe = Xe(**vao.model_dump())
    db.add(xe)
    return _luu(db, xe)


def lay(db: Session, xe_id: int, khoa: bool = False) -> Xe:
    xe = db.get(Xe, xe_id, with_for_update=khoa)
    if xe is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy xe", 404)
    return xe


def danh_sach(db: Session, pt: PhanTrang, trang_thai: str | None, tim: str | None) -> tuple[list[Xe], int]:
    loc = select(Xe)
    if trang_thai:
        loc = loc.where(Xe.trang_thai == trang_thai)
    if tim:
        loc = loc.where(Xe.bien_so.contains(tim.strip().upper(), autoescape=True))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    xe = db.scalars(loc.order_by(Xe.bien_so).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return list(xe), tong


def sua(db: Session, xe_id: int, vao: XeSua) -> Xe:
    xe = lay(db, xe_id, khoa=True)
    thay_doi = vao.model_dump(exclude_unset=True)
    kiem_br14_khoi_luong_toan_bo(
        thay_doi.get("tai_trong_kg", xe.tai_trong_kg), thay_doi.get("ktt_toan_bo_kg", xe.ktt_toan_bo_kg)
    )
    for truong, gia_tri in thay_doi.items():
        setattr(xe, truong, gia_tri)
    return _luu(db, xe)


def lay_chi_phi_co_dinh(db: Session, xe_id: int, thang: str) -> int | None:
    lay(db, xe_id)
    return db.scalar(select(ChiPhiCoDinhXe.so_tien).where(ChiPhiCoDinhXe.xe_id == xe_id, ChiPhiCoDinhXe.thang == thang))


def dat_chi_phi_co_dinh(db: Session, xe_id: int, thang: str, so_tien: int, nguoi: NguoiDung) -> int:
    lay(db, xe_id, khoa=True)  # khóa dòng xe: hai lần lưu cùng tháng không chèn trùng
    cp = db.scalar(select(ChiPhiCoDinhXe).where(ChiPhiCoDinhXe.xe_id == xe_id, ChiPhiCoDinhXe.thang == thang))
    cu = cp.so_tien if cp else None
    if cu == so_tien:
        db.rollback()
        return so_tien
    if cp is None:
        cp = ChiPhiCoDinhXe(xe_id=xe_id, thang=thang, so_tien=so_tien)
        db.add(cp)
    else:
        cp.so_tien = so_tien
    db.flush()
    # Nhật ký tiền chỉ thêm, không sửa xóa (BR-62)
    db.add(
        NhatKyTien(
            bang="chi_phi_co_dinh_xe",
            ban_ghi_id=cp.id,
            hanh_dong="TAO" if cu is None else "SUA",
            gia_tri_cu=None if cu is None else str(cu),
            gia_tri_moi=str(so_tien),
            ly_do=f"Chi phí cố định xe {xe_id} tháng {thang}",
            nguoi=nguoi.id,
        )
    )
    db.commit()
    return so_tien
