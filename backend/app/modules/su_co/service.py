"""UC-33 báo sự cố: tài xế báo trong chuyến đang chạy, không đổi trạng thái chuyến.

Điều phối xem, đóng sự cố và kết thúc do sự cố (BR-68) ở UC-32 (module chuyến).
"""

import unicodedata

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import luu_tru
from app.loi import LoiNghiepVu
from app.models import NguoiDung, SuCo, Tep
from app.modules.toi.service import _chuyen_cua_toi


def _ra(sc: SuCo, so_anh: int) -> dict:
    return {
        "id": sc.id,
        "chuyen_id": sc.chuyen_id,
        "loai": sc.loai,
        "ghi_chu": sc.ghi_chu,
        "trang_thai": sc.trang_thai,
        "cach_xu_ly": sc.cach_xu_ly,
        "so_anh": so_anh,
        "luc": sc.luc,
    }


def bao(db: Session, nd: NguoiDung, chuyen_id: int, loai: str, ghi_chu: str | None, anh: list[bytes]) -> dict:
    # Chuyến người khác / LAP / HUY / không có → 404 (UC-33 quyết định 4, như UC-17, 21); khóa dòng chuyến
    # để không chen với lúc kết thúc chuyến
    c = _chuyen_cua_toi(db, nd, chuyen_id, khoa=True)
    if c.trang_thai != "DANG_CHAY":
        raise LoiNghiepVu("CHUYEN_KHONG_DANG_CHAY", f"Chuyến {c.ma_chuyen} không đang chạy, không báo sự cố được", 409)
    ghi_chu = unicodedata.normalize("NFC", ghi_chu or "").strip()
    if not ghi_chu:
        raise LoiNghiepVu("THIEU_GHI_CHU", "Sự cố cần ghi chú", 422)
    duoi = [luu_tru.kiem_anh(a) for a in anh]  # sai loại 400, quá 500 KB 413, trước khi ghi gì

    da_ghi: list[str] = []
    try:
        sc = SuCo(chuyen_id=c.id, tai_xe_id=c.tai_xe_id, loai=loai, ghi_chu=ghi_chu)
        db.add(sc)
        db.flush()
        for du_lieu, du in zip(anh, duoi, strict=True):
            da_ghi.append(luu_tru.luu(du_lieu, du))
            db.add(Tep(su_co_id=sc.id, loai="ANH", duong_dan=da_ghi[-1], kich_thuoc=len(du_lieu)))
        db.commit()
    except Exception:
        db.rollback()
        for ten in da_ghi:  # không để ảnh mồ côi khi CSDL lỗi (NFR-REL-01)
            luu_tru.xoa(ten)
        raise
    return _ra(sc, len(anh))


def theo_chuyen(db: Session, nd: NguoiDung, chuyen_id: int) -> list[dict]:
    c = _chuyen_cua_toi(db, nd, chuyen_id)
    ds = list(db.scalars(select(SuCo).where(SuCo.chuyen_id == c.id).order_by(SuCo.luc, SuCo.id)))
    so_anh = dict(
        db.execute(
            select(Tep.su_co_id, func.count()).where(Tep.su_co_id.in_([s.id for s in ds])).group_by(Tep.su_co_id)
        ).all()
    )
    return [_ra(s, so_anh.get(s.id, 0)) for s in ds]
