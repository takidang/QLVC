from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.bao_mat import bam_mat_khau
from app.loi import LoiNghiepVu
from app.models import NguoiDung
from app.modules.nguoi_dung.schemas import NguoiDungSua, NguoiDungVao
from app.phan_trang import PhanTrang


def _luu(db: Session, nd: NguoiDung) -> None:
    # Bảng chỉ có một ràng buộc unique là tên đăng nhập: hai người cùng thêm một tên thì chỉ một người thành công
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise LoiNghiepVu("TEN_DANG_NHAP_TRUNG", f"Tên đăng nhập {nd.ten_dang_nhap} đã có người dùng", 409) from None


def _lay(db: Session, nd_id: int) -> NguoiDung:
    nd = db.get(NguoiDung, nd_id, with_for_update=True)
    if nd is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy người dùng", 404)
    return nd


def _mo_khoa_tam(nd: NguoiDung) -> None:
    nd.so_lan_sai, nd.khoa_den = 0, None  # NFR-SEC-05: Quản lý mở cho nhân viên bị khóa tạm vì sai mật khẩu


def tao(db: Session, vao: NguoiDungVao) -> NguoiDung:
    nd = NguoiDung(
        ten_dang_nhap=vao.ten_dang_nhap,
        ho_ten=vao.ho_ten,
        vai_tro=vao.vai_tro,
        mat_khau_bam=bam_mat_khau(vao.mat_khau),
    )
    db.add(nd)
    _luu(db, nd)
    return nd


def danh_sach(
    db: Session, pt: PhanTrang, vai_tro: str | None, trang_thai: str | None, tim: str | None
) -> tuple[list[NguoiDung], int]:
    loc = select(NguoiDung)
    if vai_tro:
        loc = loc.where(NguoiDung.vai_tro == vai_tro)
    if trang_thai:
        loc = loc.where(NguoiDung.trang_thai == trang_thai)
    if tim and (tim := tim.strip()):
        loc = loc.where(
            or_(
                NguoiDung.ten_dang_nhap.icontains(tim, autoescape=True),
                NguoiDung.ho_ten.icontains(tim, autoescape=True),
            )
        )
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    return list(db.scalars(loc.order_by(NguoiDung.ten_dang_nhap).offset(pt.bo_qua).limit(pt.so_dong))), tong


def sua(db: Session, nd_id: int, vao: NguoiDungSua, nguoi_lam: NguoiDung) -> NguoiDung:
    doi = vao.model_dump(exclude_unset=True)
    quan_ly: list[int] = []
    if "vai_tro" in doi or "trang_thai" in doi:
        # Khóa mọi Quản lý đang hoạt động, theo thứ tự id, trước khi khóa dòng cần sửa: hai Quản lý khóa nhau
        # cùng lúc thì xếp hàng (không deadlock) và người sau thấy kết quả của người trước (UC-02-AC9)
        quan_ly = db.scalars(
            select(NguoiDung.id)
            .where(NguoiDung.vai_tro == "QUAN_LY", NguoiDung.trang_thai == "HOAT_DONG")
            .order_by(NguoiDung.id)
            .with_for_update()
        ).all()
    nd = _lay(db, nd_id)

    vai_tro, trang_thai = doi.get("vai_tro", nd.vai_tro), doi.get("trang_thai", nd.trang_thai)
    if (vai_tro, trang_thai) != (nd.vai_tro, nd.trang_thai):
        if nd.vai_tro == "TAI_XE":
            raise LoiNghiepVu(
                "TAI_KHOAN_TAI_XE", "Tài khoản tài xế không đổi vai trò; khóa/mở ở trang Tài xế (UC-04)", 409
            )
        if nd.id == nguoi_lam.id:
            raise LoiNghiepVu("KHONG_TU_DOI_QUYEN", "Không tự đổi vai trò hoặc khóa tài khoản của chính mình", 409)
        if nd.id in quan_ly and len(quan_ly) == 1 and (vai_tro, trang_thai) != ("QUAN_LY", "HOAT_DONG"):
            raise LoiNghiepVu("QUAN_LY_CUOI", "Phải còn ít nhất một Quản lý đang hoạt động", 409)
    if trang_thai == "HOAT_DONG" and "trang_thai" in doi:
        _mo_khoa_tam(nd)
    for truong, gia_tri in doi.items():
        setattr(nd, truong, gia_tri)
    _luu(db, nd)
    return nd


def dat_lai_mat_khau(db: Session, nd_id: int, mat_khau: str) -> None:
    # Token đang dùng của người đó vẫn còn hạn (JWT không có phiên bản – story UC-02, quyết định 5)
    nd = _lay(db, nd_id)
    nd.mat_khau_bam = bam_mat_khau(mat_khau)
    _mo_khoa_tam(nd)
    db.commit()
