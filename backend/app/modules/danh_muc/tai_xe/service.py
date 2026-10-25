import re

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.bao_mat import bam_mat_khau
from app.loi import LoiNghiepVu
from app.models import NguoiDung, TaiXe
from app.modules.danh_muc.tai_xe.schemas import TaiXeSua, TaiXeVao
from app.phan_trang import PhanTrang


def _ra(tx: TaiXe, nd: NguoiDung) -> dict:
    """Gộp hai bảng thành một bản ghi trả về; chỉ lấy trường công khai, không có mật khẩu băm."""
    return {
        "id": tx.id,
        "ten_dang_nhap": nd.ten_dang_nhap,
        "ho_ten": nd.ho_ten,
        "so_gplx": tx.so_gplx,
        "hang_gplx": tx.hang_gplx,
        "han_gplx": tx.han_gplx,
        "sdt": tx.sdt,
        "trang_thai": tx.trang_thai,
    }


def _luu(db: Session, tx: TaiXe) -> None:
    # Trùng số GPLX bắt bằng ràng buộc unique ở CSDL: hai người thêm cùng lúc chỉ một người thành công.
    # Rollback cả giao dịch: không để lại tài khoản thừa (UC-04-AC3). Trùng tên đăng nhập đã bắt ở flush trong tao.
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "so_gplx" not in (getattr(getattr(e.orig, "diag", None), "constraint_name", "") or ""):
            raise
        raise LoiNghiepVu("SO_GPLX_TRUNG", f"Số GPLX {tx.so_gplx} đã có trong hệ thống", 409) from None


def tao(db: Session, vao: TaiXeVao) -> dict:
    nd = NguoiDung(
        ten_dang_nhap=vao.ten_dang_nhap,
        ho_ten=vao.ho_ten,
        vai_tro="TAI_XE",
        mat_khau_bam=bam_mat_khau(vao.mat_khau),
    )
    db.add(nd)
    try:
        db.flush()  # lấy nd.id; trùng tên đăng nhập báo ở đây
    except IntegrityError:
        db.rollback()
        raise LoiNghiepVu("TEN_DANG_NHAP_TRUNG", f"Tên đăng nhập {vao.ten_dang_nhap} đã có người dùng", 409) from None
    tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=vao.so_gplx, hang_gplx=vao.hang_gplx, han_gplx=vao.han_gplx, sdt=vao.sdt)
    db.add(tx)
    _luu(db, tx)
    return _ra(tx, nd)


def _lay(db: Session, tx_id: int, khoa: bool = False) -> tuple[TaiXe, NguoiDung]:
    tx = db.get(TaiXe, tx_id, with_for_update=khoa)
    if tx is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tài xế", 404)
    return tx, db.get(NguoiDung, tx.nguoi_dung_id, with_for_update=khoa)


def lay(db: Session, tx_id: int) -> dict:
    return _ra(*_lay(db, tx_id))


def danh_sach(db: Session, pt: PhanTrang, trang_thai: str | None, tim: str | None) -> tuple[list[dict], int]:
    loc = select(TaiXe, NguoiDung).join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
    if trang_thai:
        loc = loc.where(TaiXe.trang_thai == trang_thai)
    if tim and (tim := tim.strip()):
        dieu_kien = [NguoiDung.ho_ten.icontains(tim, autoescape=True), TaiXe.so_gplx.icontains(tim, autoescape=True)]
        # SĐT lưu dạng liền số: "0909 111" hay "0909.111" vẫn tìm ra; chỉ gõ "." thì không khớp mọi SĐT
        if so := re.sub(r"[\s.\-]", "", tim):
            dieu_kien.append(TaiXe.sdt.contains(so, autoescape=True))
        loc = loc.where(or_(*dieu_kien))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    dong = db.execute(loc.order_by(NguoiDung.ho_ten, TaiXe.id).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return [_ra(tx, nd) for tx, nd in dong], tong


def sua(db: Session, tx_id: int, vao: TaiXeSua) -> dict:
    tx, nd = _lay(db, tx_id, khoa=True)
    thay_doi = vao.model_dump(exclude_unset=True)
    if "ho_ten" in thay_doi:
        nd.ho_ten = thay_doi.pop("ho_ten")
    if "trang_thai" in thay_doi:
        # Ngừng tài xế thì khóa luôn tài khoản, mất quyền ngay; hoạt động lại thì mở lại (BR-60, chốt 25/10)
        nd.trang_thai = thay_doi["trang_thai"]
    for truong, gia_tri in thay_doi.items():
        setattr(tx, truong, gia_tri)
    _luu(db, tx)
    return _ra(tx, nd)
