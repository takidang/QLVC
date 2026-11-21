"""Đồng hồ giả cho lệnh nạp dữ liệu demo: service vẫn chạy đúng quy tắc, chỉ "bây giờ" được đặt lùi.

- `bay_gio` / `hom_nay_vn` trong mọi module `app.*` đã nạp được thay bằng bản đọc đồng hồ giả.
- Cột thời điểm do CSDL ghi (`server_default=now()`) được điền giờ giả trước khi flush, để lịch sử,
  lượt quét, đơn… mang đúng giờ của sự kiện.
Đăng nhập (JWT) vẫn dùng giờ thật nên phiên không hết hạn giữa chừng.
"""

import sys
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import DateTime, event
from sqlalchemy.orm import Session

from app import thoi_gian

_goc = {"bay_gio": thoi_gian.bay_gio, "hom_nay_vn": thoi_gian.hom_nay_vn}
_luc: list[datetime | None] = [None]


def dat(luc: datetime) -> None:
    _luc[0] = luc.astimezone(UTC)


def bay_gio() -> datetime:
    return _luc[0] or _goc["bay_gio"]()


def hom_nay_vn():
    return bay_gio().astimezone(thoi_gian.GIO_VN).date()


def _dien_gio(session: Session, *_) -> None:
    if _luc[0] is None:
        return
    for obj in session.new:
        for cot in obj.__mapper__.columns:
            if cot.server_default is not None and isinstance(cot.type, DateTime):
                khoa = obj.__mapper__.get_property_by_column(cot).key
                if getattr(obj, khoa) is None:
                    setattr(obj, khoa, _luc[0])


@contextmanager
def gia():
    """Bật đồng hồ giả trong khối `with`, trả lại như cũ khi ra (kể cả khi lỗi)."""
    import app.main  # noqa: F401  nạp hết module để thay tên đã import

    doi = []
    for m in list(sys.modules.values()):
        if m is None or not (m.__name__ == "app" or m.__name__.startswith("app.")):
            continue
        for ten, ham in (("bay_gio", bay_gio), ("hom_nay_vn", hom_nay_vn)):
            if getattr(m, ten, None) is _goc[ten]:
                setattr(m, ten, ham)
                doi.append((m, ten))
    event.listen(Session, "before_flush", _dien_gio)
    try:
        yield
    finally:
        event.remove(Session, "before_flush", _dien_gio)
        for m, ten in doi:
            setattr(m, ten, _goc[ten])
        _luc[0] = None
