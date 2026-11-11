"""UC-28 tra cứu đơn cho khách, không đăng nhập (BR-59); giới hạn lần sai theo IP (NFR-SEC-05)."""

import threading
import time
from collections import defaultdict, deque

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import DonHang, LichSuTrangThai

SO_LAN_SAI = 10
CUA_SO_GIAY = 60
KHONG_THAY = "Không tìm thấy đơn"  # chung cho sai mã và sai số: không lộ mã có tồn tại (BR-59)

# shortcut: đếm trong bộ nhớ một tiến trình uvicorn; khởi động lại thì đếm lại (quyết định 4 story UC-28).
# Chạy nhiều tiến trình thì chuyển sang bảng CSDL như khóa đăng nhập.
_sai: dict[str, deque[float]] = defaultdict(deque)
_khoa = threading.Lock()
_gio = time.monotonic


def _con_sai(ip: str, bay_gio: float) -> deque[float]:
    ds = _sai[ip]
    while ds and ds[0] <= bay_gio - CUA_SO_GIAY:
        ds.popleft()
    return ds


def tra_cuu(db: Session, ip: str, ma_don: str, sdt_4_so_cuoi: str) -> dict:
    with _khoa:
        if len(_con_sai(ip, _gio())) >= SO_LAN_SAI:
            raise LoiNghiepVu("QUA_TAN_SUAT", "Tra cứu sai quá nhiều lần, vui lòng thử lại sau 1 phút", 429)
    d = db.scalar(
        select(DonHang).where(
            func.upper(DonHang.ma_don) == ma_don.strip().upper(),
            or_(DonHang.sdt_lay.endswith(sdt_4_so_cuoi), DonHang.sdt_nhan.endswith(sdt_4_so_cuoi)),
        )
    )
    if d is None:
        with _khoa:
            _con_sai(ip, _gio()).append(_gio())
        raise LoiNghiepVu("KHONG_TIM_THAY", KHONG_THAY, 404)
    ls = db.execute(
        select(LichSuTrangThai.sang, LichSuTrangThai.luc)
        .where(
            LichSuTrangThai.doi_tuong == "DON",
            LichSuTrangThai.doi_tuong_id == d.id,
            LichSuTrangThai.tu.is_not(None),  # mốc tạo đơn lấy từ tao_luc
        )
        .order_by(LichSuTrangThai.luc, LichSuTrangThai.id)
    ).all()
    moc = [{"trang_thai": "CHO_GHEP", "luc": d.tao_luc}] + [{"trang_thai": s, "luc": luc} for s, luc in ls]
    return {"ma_don": d.ma_don, "trang_thai": d.trang_thai, "moc": moc}
