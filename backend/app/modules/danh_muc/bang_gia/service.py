import unicodedata
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import distinct_on
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import BangGia
from app.modules.danh_muc.bang_gia.schemas import BangGiaSua, BangGiaVao
from app.phan_trang import PhanTrang
from app.thoi_gian import hom_nay_vn

CAP = (func.lower(BangGia.tinh_lay), func.lower(BangGia.tinh_giao))


def _chuan(tinh: str) -> str:
    return unicodedata.normalize("NFC", tinh).strip().lower()


def tra_gia(db: Session, tinh_lay: str, tinh_giao: str, ngay: date) -> BangGia | None:
    """BR-48: mức giá của cặp tỉnh đang có hiệu lực tại ngày đó (hiệu lực mới nhất ≤ ngày). Không có → None."""
    return db.scalar(
        select(BangGia)
        .where(
            func.lower(BangGia.tinh_lay) == _chuan(tinh_lay),
            func.lower(BangGia.tinh_giao) == _chuan(tinh_giao),
            BangGia.hieu_luc_tu <= ngay,
        )
        .order_by(BangGia.hieu_luc_tu.desc())
        .limit(1)
    )


def _luu(db: Session, bg: BangGia) -> BangGia:
    # Trùng cặp tỉnh + ngày hiệu lực bắt bằng unique ở CSDL: hai người thêm cùng lúc chỉ một người thành công
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise LoiNghiepVu(
            "BANG_GIA_TRUNG",
            f"Đã có giá {bg.tinh_lay} → {bg.tinh_giao} hiệu lực từ {bg.hieu_luc_tu:%d/%m/%Y}",
            409,
        ) from None
    return bg


def tao(db: Session, vao: BangGiaVao) -> BangGia:
    bg = BangGia(**vao.model_dump())
    db.add(bg)
    return _luu(db, bg)


def lay(db: Session, bg_id: int, khoa: bool = False) -> BangGia:
    bg = db.get(BangGia, bg_id, with_for_update=khoa)
    if bg is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy mức giá", 404)
    return bg


def sua(db: Session, bg_id: int, vao: BangGiaSua) -> BangGia:
    bg = lay(db, bg_id, khoa=True)
    for truong, gia_tri in vao.model_dump(exclude_unset=True).items():
        setattr(bg, truong, gia_tri)
    return _luu(db, bg)


def id_dang_ap_dung(db: Session) -> set[int]:
    """Mỗi cặp tỉnh một mức đang áp dụng hôm nay (giờ Việt Nam)."""
    q = (
        select(BangGia.id)
        .where(BangGia.hieu_luc_tu <= hom_nay_vn())
        .ext(distinct_on(*CAP))
        .order_by(*CAP, BangGia.hieu_luc_tu.desc())
    )
    return set(db.scalars(q))


def danh_sach(db: Session, pt: PhanTrang, tim: str | None) -> tuple[list[BangGia], int]:
    loc = select(BangGia)
    if tim and (tim := tim.strip()):
        loc = loc.where(
            or_(BangGia.tinh_lay.icontains(tim, autoescape=True), BangGia.tinh_giao.icontains(tim, autoescape=True))
        )
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    bg = db.scalars(loc.order_by(*CAP, BangGia.hieu_luc_tu.desc()).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return list(bg), tong


def ten_tinh_da_dung(db: Session) -> list[str]:
    """Gợi ý tên tỉnh trên giao diện để tránh gõ lệch (quyết định UC-07 số 1)."""
    lay_ = select(BangGia.tinh_lay.label("t"))
    giao = select(BangGia.tinh_giao.label("t"))
    return sorted(set(db.scalars(lay_.union(giao))), key=str.lower)
