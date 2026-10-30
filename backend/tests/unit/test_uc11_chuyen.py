from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.chuyen import (
    LichChuyen,
    TaiXeXet,
    XeXet,
    ket_thuc_chay_rong,
    phut_lai_theo_ngay,
    phut_lai_theo_tuan,
    xet_gio_lai,
    xet_tai_xe,
    xet_trung_lich,
    xet_xe,
)
from app.thoi_gian import GIO_VN

# Kịch bản mục 11: C01 chạy T01 (270′) ngày 20/10/2026 (Thứ Ba), khởi hành 06:00, CFG-05 = 60′
NGAY = date(2026, 10, 20)


def luc(gio: int, phut: int = 0, ngay: date = NGAY) -> datetime:
    return datetime(ngay.year, ngay.month, ngay.day, gio, phut, tzinfo=GIO_VN)


KH, KT = luc(6), luc(11, 30)
X1 = XeXet("51C-111.11", "HOAT_DONG", date(2026, 11, 30), date(2026, 12, 31))
AN = TaiXeXet("An", "HOAT_DONG", "C", date(2030, 5, 31))


def ma(vp: list[dict]) -> list[str]:
    return [v["ma"] for v in vp]


# AC1 – BR-64, 65
def test_uc11_ac1_ket_thuc_chay_rong():
    assert ket_thuc_chay_rong(KH, 270, 60) == KT  # TC-BR64-02
    assert ket_thuc_chay_rong(KH, 270, 0) == luc(10, 30)


def test_uc11_ac1_gio_lai_theo_ngay():
    assert phut_lai_theo_ngay(KH, 270) == {NGAY: 270}  # TC-BR65-01
    # TC-BR65-02: 22:00 chia 120′ cho 20/10, 150′ cho 21/10
    assert phut_lai_theo_ngay(luc(22), 270) == {NGAY: 120, date(2026, 10, 21): 150}
    # Giờ UTC vẫn chia theo ngày Việt Nam: 15:00 UTC = 22:00 giờ VN
    assert phut_lai_theo_ngay(datetime(2026, 10, 20, 15, tzinfo=UTC), 270) == {NGAY: 120, date(2026, 10, 21): 150}


def test_uc11_ac1_gio_lai_theo_tuan_thu_hai_den_chu_nhat():
    chu_nhat = date(2026, 10, 25)
    assert phut_lai_theo_tuan(luc(22, ngay=chu_nhat), 270) == {date(2026, 10, 19): 120, date(2026, 10, 26): 150}


# AC2 – BR-11, 12, 13
def test_uc11_ac2_xe_dat():
    assert xet_xe(X1, NGAY) == []


@pytest.mark.parametrize(
    ("xe", "mong_doi"),
    [
        (XeXet("X3", "NGUNG", date(2026, 11, 30), date(2026, 12, 31)), ["BR-11"]),  # TC-BR11-02
        (XeXet("X2", "HOAT_DONG", date(2026, 10, 19), date(2026, 12, 31)), ["BR-12"]),  # TC-BR12-01
        (XeXet("X2", "HOAT_DONG", NGAY, date(2026, 12, 31)), []),  # TC-BR12-02 biên
        (XeXet("X5", "HOAT_DONG", date(2026, 11, 30), date(2026, 10, 19)), ["BR-13"]),  # TC-BR13-01
        (XeXet("X5", "HOAT_DONG", date(2026, 11, 30), NGAY), []),  # TC-BR13-02 biên
    ],
)
def test_uc11_ac2_xe(xe, mong_doi):
    assert ma(xet_xe(xe, NGAY)) == mong_doi


def test_uc11_ac2_chuyen_qua_dem_so_han_voi_ngay_ket_thuc():
    # Chuyến 22:00 kết thúc 21/10 03:30: đăng kiểm hết 20/10 bị chặn
    ket_thuc = ket_thuc_chay_rong(luc(22), 270, 60)
    xe = XeXet("X2", "HOAT_DONG", NGAY, date(2026, 12, 31))
    vp = xet_xe(xe, ket_thuc.astimezone(GIO_VN).date())
    assert ma(vp) == ["BR-12"]
    assert "20/10/2026" in vp[0]["thong_diep"] and "21/10/2026" in vp[0]["thong_diep"]


# AC3 – BR-14, 15, tài xế ngừng
@pytest.mark.parametrize(
    ("tx", "ktt", "mong_doi"),
    [
        (AN, 9500, []),  # TC-BR14-01
        (TaiXeXet("Bình", "HOAT_DONG", "B", date(2030, 1, 1)), 9500, ["BR-14"]),  # TC-BR14-02
        (TaiXeXet("Bình", "HOAT_DONG", "B", date(2030, 1, 1)), None, []),  # chưa chọn xe thì chưa xét BR-14
        (TaiXeXet("Cường", "HOAT_DONG", "C", date(2026, 10, 19)), 9500, ["BR-15"]),  # TC-BR15-01
        (TaiXeXet("Cường", "HOAT_DONG", "C", NGAY), 9500, []),  # TC-BR15-02 biên
        (TaiXeXet("Dũng", "NGUNG", "C", date(2030, 1, 1)), 9500, ["TAI_XE_NGUNG"]),
    ],
)
def test_uc11_ac3_tai_xe(tx, ktt, mong_doi):
    assert ma(xet_tai_xe(tx, NGAY, ktt)) == mong_doi


# AC4 – BR-16, 17 khoảng nửa mở
def chuyen(gio: int, phut: int = 0, phut_lai: int = 270, ma_chuyen: str = "C02") -> LichChuyen:
    kh = luc(gio, phut)
    return LichChuyen(ma_chuyen, kh, ket_thuc_chay_rong(kh, phut_lai, 60), phut_lai)


@pytest.mark.parametrize(
    ("lich", "so_vp"),
    [
        ([chuyen(10)], 1),  # TC-BR16-01 / TC-BR17-01: [06:00, 11:30) chồng [10:00, …)
        ([chuyen(11)], 1),
        ([chuyen(11, 30)], 0),  # TC-BR16-02 / TC-BR17-02 biên: 11:30 không chồng 11:30
        ([LichChuyen("C00", luc(0), luc(6), 300)], 0),  # chuyến trước kết thúc đúng 06:00
        ([], 0),
    ],
)
def test_uc11_ac4_trung_lich(lich, so_vp):
    for br in ("BR-16", "BR-17"):
        vp = xet_trung_lich(br, "Xe X1", KH, KT, lich)
        assert ma(vp) == [br] * so_vp
    if so_vp:
        assert "C02" in xet_trung_lich("BR-16", "Xe X1", KH, KT, lich)[0]["thong_diep"]


# AC5 – BR-18, 19
@pytest.mark.parametrize(
    ("phut_khac", "gio_ngay", "mong_doi"),
    [
        (360, 10, ["BR-18"]),  # TC-BR18-01: 4,5 + 6 = 10,5 > 10
        (330, 10, []),  # TC-BR18-02 biên: đúng 10 giờ
        (330, 9, ["BR-18"]),  # CFG-07 = 9/48/4
    ],
)
def test_uc11_ac5_gio_lai_ngay(phut_khac, gio_ngay, mong_doi):
    lich = [chuyen(14, phut_lai=phut_khac)]  # 14:00 cùng ngày, không chồng giờ
    assert ma(xet_gio_lai("An", KH, 270, lich, gio_ngay, 48)) == mong_doi


def test_uc11_ac5_gio_lai_ngay_qua_dem_chi_tinh_phan_trong_ngay():
    # Chuyến kia 19/10 22:00, 8 giờ lái: 2 giờ thuộc 19/10, 6 giờ thuộc 20/10 → 6 + 4,5 > 10
    lich = [LichChuyen("C00", luc(22, ngay=date(2026, 10, 19)), luc(6), 480)]
    vp = xet_gio_lai("An", KH, 270, lich, 10, 48)
    assert ma(vp) == ["BR-18"] and "10,5 giờ" in vp[0]["thong_diep"]


def tuan_da_co(gio: float) -> list[LichChuyen]:
    """Các chuyến 9 giờ lái/ngày vào các ngày khác 20/10 trong tuần 19–25/10, tổng `gio` giờ."""
    lich, con = [], int(gio * 60)
    for ngay in (19, 21, 22, 23, 24, 25):
        if con <= 0:
            break
        p = min(con, 540)
        kh = luc(6, ngay=date(2026, 10, ngay))
        lich.append(LichChuyen(f"C{ngay}", kh, kh + timedelta(minutes=p + 60), p))
        con -= p
    return lich


@pytest.mark.parametrize(
    ("gio", "mong_doi"),
    [(44, ["BR-19"]), (43.5, [])],  # TC-BR19-01: 48,5 > 48; TC-BR19-02 biên: đúng 48
)
def test_uc11_ac5_gio_lai_tuan(gio, mong_doi):
    assert ma(xet_gio_lai("An", KH, 270, tuan_da_co(gio), 10, 48)) == mong_doi


def test_uc11_ac5_tuan_truoc_khong_tinh():
    # 44 giờ ở tuần 12–18/10 không ảnh hưởng tuần 19–25/10
    lich = [
        LichChuyen(c.ma_chuyen, c.khoi_hanh - timedelta(days=7), c.ket_thuc - timedelta(days=7), c.phut_lai)
        for c in tuan_da_co(44)
    ]
    assert xet_gio_lai("An", KH, 270, lich, 10, 48) == []
