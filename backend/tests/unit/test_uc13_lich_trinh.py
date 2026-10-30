from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal

import pytest

from app.domain.lich_trinh import DonGhep, ket_thuc_du_kien, lai_du_kien, lich_trinh, ty_le_lap_day, xet_ghep
from app.thoi_gian import GIO_VN

# Kịch bản mục 11: T01 TP.HCM(1) → Long An(2) → Tiền Giang(3) → Vĩnh Long(4) → Cần Thơ(5); Bến Tre(9) ngoài tuyến
HCM, LA, TG, VL, CT, BEN_TRE = 1, 2, 3, 4, 5, 9
THU_TU = {HCM: 1, LA: 2, TG: 3, VL: 4, CT: 5}
PHUT = {HCM: 0, LA: 60, TG: 120, VL: 210, CT: 270}
NGAY = date(2026, 10, 20)


def luc(gio: int, phut: int = 0) -> datetime:
    return datetime(NGAY.year, NGAY.month, NGAY.day, gio, phut, tzinfo=GIO_VN)


KH = luc(6)


def don(so: int, lay: int, giao: int, kg, m3, han: datetime, khung: tuple[datetime, datetime] | None = None) -> DonGhep:
    lay_tu, lay_den = khung or (None, None)
    return DonGhep(so, f"DH-{so:04d}", Decimal(kg), Decimal(m3), lay, giao, lay_tu, lay_den, han)


D1 = don(1, HCM, CT, 1800, 6, luc(14))
D2 = don(2, LA, CT, 1200, 3, luc(12), (luc(6, 30), luc(9)))
D3 = don(3, HCM, VL, 1500, 5, luc(10))
D4 = don(4, HCM, TG, 800, 2, luc(18))
D5 = don(5, VL, LA, 500, "1.5", luc(18))
D6 = don(6, HCM, CT, 2500, 5, luc(18))
D8 = don(8, HCM, TG, 300, 1, luc(18))


def xet(ds: list[DonGhep], moi: set[int], tai=5000, the_tich="20"):
    return xet_ghep(ds, moi, THU_TU, PHUT, KH, 20, tai, Decimal(the_tich))


def ma(vp: list[dict]) -> list[str]:
    return [v["ma"] for v in vp]


def tom_tat(diem) -> list[tuple[str, str, str]]:
    return [(d.viec, d.don.ma_don, d.eta.strftime("%H:%M")) for d in diem]


# AC1 – BR-63
def test_uc13_ac1_lich_trinh_c01():
    # TC-BR63-01, 02: ở Cần Thơ giao Đ2 (hạn 12:00) trước Đ1 (hạn 14:00)
    assert tom_tat(lich_trinh(KH, THU_TU, PHUT, [D1, D2, D4], 20)) == [
        ("LAY", "DH-0001", "06:00"),
        ("LAY", "DH-0004", "06:20"),
        ("LAY", "DH-0002", "07:40"),
        ("GIAO", "DH-0004", "09:00"),
        ("GIAO", "DH-0002", "11:50"),
        ("GIAO", "DH-0001", "12:10"),
    ]


def test_uc13_ac1_thu_tu_lay():
    d14 = don(14, HCM, CT, 100, 1, luc(18), (luc(6), luc(7)))
    # TC-BR63-03: có khung lấy xếp trước đơn không khung
    assert [x[1] for x in tom_tat(lich_trinh(KH, THU_TU, PHUT, [D1, d14], 20))][:2] == ["DH-0014", "DH-0001"]
    # TC-BR63-04: cùng không khung thì theo mã đơn, không theo thứ tự truyền vào
    assert [x[1] for x in tom_tat(lich_trinh(KH, THU_TU, PHUT, [D4, D1], 20))][:2] == ["DH-0001", "DH-0004"]


def test_uc13_ac1_lay_giao_cung_nut_lay_truoc():
    d13 = don(13, CT, CT, 100, 1, luc(18))  # TC-BR04-03
    diem = lich_trinh(KH, THU_TU, PHUT, [D1, D4, d13], 20)
    o_can_tho = [(d.viec, d.don.ma_don) for d in diem if d.nut == CT]
    assert o_can_tho == [("LAY", "DH-0013"), ("GIAO", "DH-0001"), ("GIAO", "DH-0013")]


# AC2 – BR-64
def test_uc13_ac2_ket_thuc_du_kien():
    diem = lich_trinh(KH, THU_TU, PHUT, [D1, D2, D4], 20)
    assert ket_thuc_du_kien(KH, 270, diem, 20, 60) == luc(13, 30)  # TC-BR64-01: 12:10 + 20′ + 60′
    assert ket_thuc_du_kien(KH, 270, [], 20, 60) == luc(11, 30)  # chưa có đơn: chạy rỗng


# AC3 – BR-01, 02, 49
@pytest.mark.parametrize(
    ("them", "mong_doi"),
    [
        (D2, []),  # TC-BR01-01: 3.800 kg
        (D6, ["BR-01"]),  # TC-BR01-02: 5.100 kg
        (don(9, HCM, CT, 2400, 1, luc(18)), []),  # TC-BR01-03 biên: đúng 5.000 kg
        (don(10, HCM, CT, 500, 12, luc(18)), []),  # TC-BR02-01 biên: đúng 20 m³
        (don(11, HCM, CT, 500, "12.01", luc(18)), ["BR-02"]),  # TC-BR02-02
    ],
)
def test_uc13_ac3_tai_va_the_tich(them, mong_doi):
    _, vp = xet([D1, D4, them], {them.id})
    assert ma(vp) == mong_doi


def test_uc13_ac3_thong_diep_tai():
    _, vp = xet([D1, D4, D6], {6})
    assert vp[0]["don_id"] is None and "5.100 kg" in vp[0]["thong_diep"] and "5.000 kg" in vp[0]["thong_diep"]


def test_uc13_ac3_kiem_tai_theo_kg_thuc():
    # TC-BR49-01: Đ1 KL tính cước 1.998 nhưng kg thực 1.800 ≤ xe 1.900 kg
    assert xet([D1], {1}, tai=1900, the_tich="12")[1] == []


# AC4 – BR-03, 04
def test_uc13_ac4_dung_tuyen_dung_chieu():
    _, vp = xet([D1, D4, don(12, HCM, BEN_TRE, 100, 1, luc(18))], {12})  # TC-BR03-02
    assert ma(vp) == ["BR-03"] and vp[0]["don_id"] == 12
    assert ma(xet([D1, D4, D5], {5})[1]) == ["BR-04"]  # TC-BR04-02
    assert xet([D1, D4, don(13, CT, CT, 100, 1, luc(18))], {13})[1] == []  # TC-BR04-03 biên


def test_uc13_ac4_nut_giu_hang_thay_nut_lay():
    # Đơn ghép lại đang giữ ở Vĩnh Long, giao Cần Thơ: đúng chiều dù nút lấy gốc ngoài tuyến
    giu = don(15, VL, CT, 100, 1, luc(18))
    assert xet([giu], {15})[1] == []


# AC5 – BR-05, 06
@pytest.mark.parametrize(
    ("khung", "han", "mong_doi"),
    [
        ((luc(6, 30), luc(9)), luc(12), []),  # TC-BR05-01: ETA lấy 07:40
        ((luc(6, 30), luc(7, 30)), luc(12), ["BR-05"]),  # TC-BR05-02: trễ
        ((luc(8), luc(9)), luc(12), ["BR-05"]),  # TC-BR05-03: sớm, xe không đứng chờ
        ((luc(7, 40), luc(9)), luc(12), []),  # TC-BR05-04 biên: đúng đầu khung
        (None, luc(12), []),  # TC-BR05-05: không khung = cả ngày
        ((luc(6, 30), luc(9)), luc(11, 50), []),  # TC-BR06-03 biên: giao đúng 11:50 = hạn
    ],
)
def test_uc13_ac5_khung_lay_han_giao(khung, han, mong_doi):
    d2 = don(2, LA, CT, 1200, 3, han, khung)
    assert ma(xet([D1, D4, d2], {2})[1]) == mong_doi


def test_uc13_ac5_tre_han_giao():
    _, vp = xet([D1, D4, D3], {3})  # TC-BR06-02: 06:00 + 210′ + 4 × 20′ = 10:50 > 10:00
    assert ma(vp) == ["BR-06"] and "10:50" in vp[0]["thong_diep"] and "10:00" in vp[0]["thong_diep"]
    assert xet([D2, D4, D1], {1})[1] == []  # TC-BR06-01


# AC6 – BR-67
def test_uc13_ac6_ghep_lam_don_cu_vi_pham():
    # TC-BR67-01: Đ8 tự nó hợp lệ, nhưng ETA giao Đ2 dịch thành 12:30 > 12:00
    _, vp = xet([D1, D2, D4, D8], {8})
    assert [(v["don_id"], v["ma"]) for v in vp] == [(2, "BR-06")]
    assert vp[0]["thong_diep"].startswith("Đơn đã ghép DH-0002") and "12:30" in vp[0]["thong_diep"]


def test_uc13_ac6_go_lam_don_khac_vi_pham():
    # TC-BR67-02: gỡ Đ4 thì lấy Đ2c dịch về 07:20, sớm hơn khung 07:40–09:00
    d2c = replace(D2, lay_tu=luc(7, 40))
    assert xet([D1, D4, d2c], set())[1] == []
    _, vp = xet([D1, d2c], set())
    assert ma(vp) == ["BR-05"] and "07:20" in vp[0]["thong_diep"] and "sớm hơn" in vp[0]["thong_diep"]


# BR-52 và % đầy (dùng ở AC7)
def test_uc13_lai_du_kien_va_lap_day():
    assert lai_du_kien([2997000, 1440000, 800000], 1000000, 600000) == 3637000
    assert ty_le_lap_day(Decimal(3800), Decimal(11), 5000, Decimal(20)) == Decimal("0.76")
