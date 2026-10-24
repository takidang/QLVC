from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.cau_hinh import THAM_SO
from app.loi import LoiNghiepVu
from app.models import CauHinh, NguoiDung
from app.thoi_gian import bay_gio


def danh_sach(db: Session) -> list[dict]:
    dong = {ch.ma: ch for ch in db.scalars(select(CauHinh))}
    ten_nguoi = dict(db.execute(select(NguoiDung.id, NguoiDung.ho_ten)).all())
    return [
        {
            "ma": ma,
            "ten": ts.ten,
            "don_vi": ts.don_vi,
            "gia_tri": dong[ma].gia_tri if ma in dong else ts.mac_dinh,
            "nguoi_sua": ten_nguoi.get(dong[ma].nguoi_sua) if ma in dong else None,
            "luc": dong[ma].luc if ma in dong else None,
        }
        for ma, ts in THAM_SO.items()
    ]


def sua(db: Session, ma: str, gia_tri: str, nguoi: NguoiDung) -> None:
    ts = THAM_SO.get(ma)
    if ts is None:  # gồm CFG-03 đã bỏ ở 0.5
        raise LoiNghiepVu("KHONG_TIM_THAY", f"Không có tham số {ma}", 404)
    try:
        gia_tri = ts.kiem(gia_tri)
    except ValueError as e:
        raise LoiNghiepVu("CAU_HINH_SAI", f"{ma}: {e}", 400) from None
    ch = db.get(CauHinh, ma, with_for_update=True) or CauHinh(ma=ma)
    ch.gia_tri, ch.nguoi_sua, ch.luc = gia_tri, nguoi.id, bay_gio()
    db.add(ch)
    db.commit()


def lay(db: Session, ma: str) -> str:
    """Giá trị hiện hành của một tham số, dùng ở các UC sau (cước, ETA, cảnh báo)."""
    return db.scalar(select(CauHinh.gia_tri).where(CauHinh.ma == ma)) or THAM_SO[ma].mac_dinh
