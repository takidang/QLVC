from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.cuoc import kiem_br31_don_hop_le, kl_quy_doi, kl_tinh_cuoc, tinh_cuoc
from app.loi import LoiNghiepVu

D = Decimal


def cuoc(kg, m3, don_gia, toi_thieu=0, he_so=333, buoc=1000):
    kl = kl_tinh_cuoc(D(kg), kl_quy_doi(D(m3), he_so))
    return kl, tinh_cuoc(kl, don_gia, toi_thieu, buoc)


# AC1 – kịch bản mục 11 (nghiep-vu.md)
@pytest.mark.parametrize(
    ("ten", "kg", "m3", "don_gia", "kl_mong_doi", "cuoc_mong_doi"),
    [
        ("Đ1 quy đổi lớn hơn", "1800", "6", 1500, D("1998"), 2_997_000),
        ("Đ2 kg thực lớn hơn", "1200", "3", 1200, D("1200"), 1_440_000),
        ("Đ3 làm tròn lên", "1500", "5", 1300, D("1665"), 2_165_000),
        ("Đ8 quy đổi 333", "300", "1", 1000, D("333"), 333_000),
        ("m³ thập phân", "100", "1.5", 1000, D("499.5"), 500_000),
    ],
)
def test_uc08_ac1_tinh_cuoc_theo_kich_ban(ten, kg, m3, don_gia, kl_mong_doi, cuoc_mong_doi):
    kl, tien = cuoc(kg, m3, don_gia)
    assert kl == kl_mong_doi
    assert tien == cuoc_mong_doi


def test_uc08_ac1_cuoc_toi_thieu():
    assert cuoc("10", "0.01", 1500, toi_thieu=50_000)[1] == 50_000
    assert cuoc("40", "0.01", 1500, toi_thieu=50_000)[1] == 60_000  # vượt tối thiểu thì dùng số tính


def test_uc08_ac1_dung_boi_so_khong_lam_tron_them():
    assert tinh_cuoc(D("2000"), 1500, 0, 1000) == 3_000_000  # 3.000.000 đúng bội, giữ nguyên
    assert tinh_cuoc(D("2000.0001"), 1500, 0, 1000) == 3_001_000  # vượt chút xíu thì lên bội kế


# AC4 – BR-31 phần giữa các trường
BAY_GIO = datetime(2026, 10, 19, 9, 0, tzinfo=UTC)


def hop_le(**doi):
    gia_tri = {
        "dia_chi_lay": "12 Nguyễn Huệ, Q.1",
        "dia_chi_giao": "5 Hòa Bình, Ninh Kiều",
        "lay_tu": None,
        "lay_den": None,
        "han_giao": BAY_GIO + timedelta(days=1),
        "bay_gio": BAY_GIO,
    }
    kiem_br31_don_hop_le(**(gia_tri | doi))


def test_uc08_ac4_don_hop_le_khong_khung_gio():
    hop_le()
    hop_le(lay_tu=BAY_GIO + timedelta(hours=1), lay_den=BAY_GIO + timedelta(hours=3))


@pytest.mark.parametrize(
    "doi",
    [
        {"dia_chi_giao": "  12 nguyễn huệ,   Q.1 "},  # trùng, khác hoa thường và khoảng trắng
        {"han_giao": BAY_GIO},  # biên: bằng thời điểm tạo
        {"lay_tu": BAY_GIO + timedelta(hours=1)},  # chỉ có một đầu
        {"lay_tu": BAY_GIO + timedelta(hours=3), "lay_den": BAY_GIO + timedelta(hours=3)},  # từ = đến
        {"lay_tu": BAY_GIO + timedelta(days=2), "lay_den": BAY_GIO + timedelta(days=3)},  # hạn giao ≤ từ
    ],
)
def test_uc08_ac4_br31_chan(doi):
    with pytest.raises(LoiNghiepVu) as loi:
        hop_le(**doi)
    assert loi.value.ma == "BR-31"
    assert loi.value.status_code == 422


def test_uc08_ac4_br31_gom_moi_vi_pham():
    with pytest.raises(LoiNghiepVu) as loi:
        hop_le(dia_chi_giao="12 Nguyễn Huệ, Q.1", han_giao=BAY_GIO - timedelta(hours=1))
    assert len(loi.value.chi_tiet) == 2
