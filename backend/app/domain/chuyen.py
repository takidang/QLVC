"""Lập chuyến: thời gian chuyến (BR-64, 65) và điều kiện xe, tài xế (BR-11…19). Hàm thuần, không đụng CSDL."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.domain.xe_tai_xe import kiem_br14_hang_gplx
from app.loi import LoiNghiepVu
from app.thoi_gian import GIO_VN

PHUT = timedelta(minutes=1)


def ket_thuc_chay_rong(khoi_hanh: datetime, phut_tuyen: int, phut_dem: int) -> datetime:
    """BR-64, chuyến 0 đơn: khởi hành + thời gian toàn tuyến + CFG-05. Khoảng chiếm = [khởi hành, kết thúc)."""
    return khoi_hanh + (phut_tuyen + phut_dem) * PHUT


def phut_lai_theo_ngay(khoi_hanh: datetime, phut_lai: int) -> dict[date, int]:
    """BR-65: giờ lái nằm trong [khởi hành, khởi hành + phút lái), qua nửa đêm thì chia theo ngày giờ Việt Nam."""
    dau = khoi_hanh.astimezone(GIO_VN)
    cuoi = dau + phut_lai * PHUT
    ket_qua: dict[date, int] = {}
    while dau < cuoi:
        het = min(cuoi, datetime.combine(dau.date() + timedelta(days=1), time(), GIO_VN))
        ket_qua[dau.date()] = ket_qua.get(dau.date(), 0) + (het - dau) // PHUT
        dau = het
    return ket_qua


def phut_lai_theo_tuan(khoi_hanh: datetime, phut_lai: int) -> dict[date, int]:
    """BR-19: tuần Thứ Hai 00:00 → hết Chủ Nhật (chốt 30/10); khóa là ngày Thứ Hai của tuần."""
    ket_qua: dict[date, int] = {}
    for ngay, phut in phut_lai_theo_ngay(khoi_hanh, phut_lai).items():
        thu_hai = ngay - timedelta(days=ngay.weekday())
        ket_qua[thu_hai] = ket_qua.get(thu_hai, 0) + phut
    return ket_qua


def _gio(t: datetime) -> str:
    return t.astimezone(GIO_VN).strftime("%H:%M %d/%m")


def _ngay(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _vp(ma: str, thong_diep: str) -> dict:
    return {"ma": ma, "thong_diep": thong_diep}


@dataclass
class XeXet:
    bien_so: str
    trang_thai: str
    han_dang_kiem: date
    han_bao_hiem: date


@dataclass
class TaiXeXet:
    ho_ten: str
    trang_thai: str
    hang_gplx: str
    han_gplx: date


@dataclass
class LichChuyen:
    """Một chuyến khác (khác HUY) của cùng xe hoặc tài xế."""

    ma_chuyen: str
    khoi_hanh: datetime
    ket_thuc: datetime
    phut_lai: int


def xet_xe(xe: XeXet, ngay_ket_thuc: date) -> list[dict]:
    """BR-11, 12, 13. Hạn đúng bằng ngày kết thúc dự kiến vẫn đạt."""
    vp = []
    if xe.trang_thai != "HOAT_DONG":
        vp.append(_vp("BR-11", f"Xe {xe.bien_so} đang ngừng hoạt động"))
    if xe.han_dang_kiem < ngay_ket_thuc:
        vp.append(
            _vp(
                "BR-12",
                f"Xe {xe.bien_so} hết hạn đăng kiểm {_ngay(xe.han_dang_kiem)}, "
                f"trước ngày kết thúc chuyến {_ngay(ngay_ket_thuc)}",
            )
        )
    if xe.han_bao_hiem < ngay_ket_thuc:
        vp.append(
            _vp(
                "BR-13",
                f"Xe {xe.bien_so} hết hạn bảo hiểm {_ngay(xe.han_bao_hiem)}, "
                f"trước ngày kết thúc chuyến {_ngay(ngay_ket_thuc)}",
            )
        )
    return vp


def xet_tai_xe(tx: TaiXeXet, ngay_ket_thuc: date, ktt_xe: int | None) -> list[dict]:
    """Tài xế NGUNG (quyết định UC-11 số 3), BR-14 (khi đã biết xe), BR-15."""
    vp = []
    if tx.trang_thai != "HOAT_DONG":
        vp.append(_vp("TAI_XE_NGUNG", f"Tài xế {tx.ho_ten} đang ngừng hoạt động"))
    if ktt_xe is not None:
        try:
            kiem_br14_hang_gplx(tx.hang_gplx, ktt_xe)
        except LoiNghiepVu as e:
            vp.append(_vp(e.ma, f"Tài xế {tx.ho_ten}: {e.thong_diep}"))
    if tx.han_gplx < ngay_ket_thuc:
        vp.append(
            _vp(
                "BR-15",
                f"GPLX của {tx.ho_ten} hết hạn {_ngay(tx.han_gplx)}, trước ngày kết thúc chuyến {_ngay(ngay_ket_thuc)}",
            )
        )
    return vp


def xet_trung_lich(ma: str, ai: str, khoi_hanh: datetime, ket_thuc: datetime, lich: list[LichChuyen]) -> list[dict]:
    """BR-16 (xe), BR-17 (tài xế): khoảng chiếm nửa mở [a, b) – kết thúc 11:30 không chồng bắt đầu 11:30."""
    return [
        _vp(ma, f"{ai} trùng lịch chuyến {c.ma_chuyen} ({_gio(c.khoi_hanh)} → {_gio(c.ket_thuc)})")
        for c in lich
        if c.khoi_hanh < ket_thuc and khoi_hanh < c.ket_thuc
    ]


def xet_gio_lai(
    ten: str, khoi_hanh: datetime, phut_lai: int, lich: list[LichChuyen], gio_ngay: int, gio_tuan: int
) -> list[dict]:
    """BR-18 (ngày), BR-19 (tuần): chỉ xét ngày, tuần mà chuyến mới chạm tới; giới hạn từ CFG-07."""
    vp = []
    for ma, chia, gioi_han, ky in (
        ("BR-18", phut_lai_theo_ngay, gio_ngay, "ngày {}"),
        ("BR-19", phut_lai_theo_tuan, gio_tuan, "tuần từ {}"),
    ):
        da_co: dict[date, int] = {}
        for c in lich:
            for k, p in chia(c.khoi_hanh, c.phut_lai).items():
                da_co[k] = da_co.get(k, 0) + p
        for k, p in chia(khoi_hanh, phut_lai).items():
            tong = da_co.get(k, 0) + p
            if tong > gioi_han * 60:
                gio = f"{tong / 60:g}".replace(".", ",")
                vp.append(_vp(ma, f"{ten} lái {gio} giờ trong {ky.format(_ngay(k))}, vượt {gioi_han} giờ"))
    return vp
