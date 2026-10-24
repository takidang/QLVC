import pytest

from app.domain.tuyen import NutTuyen, canh_bao_br20, kiem_br66_thoi_gian_tuyen, kiem_cau_truc_tuyen
from app.loi import LoiNghiepVu

# Tuyến T01 kịch bản mục 11: HCM → Long An → Tiền Giang (nghỉ) → Vĩnh Long → Cần Thơ
T01 = [
    NutTuyen(1, 0, 0),
    NutTuyen(2, 60, 50),
    NutTuyen(3, 120, 75, la_diem_nghi=True),
    NutTuyen(4, 210, 135),
    NutTuyen(5, 270, 170),
]
TEN = {1: "TP.HCM", 2: "Long An", 3: "Tiền Giang", 4: "Vĩnh Long", 5: "Cần Thơ"}


# AC3 – cấu trúc tuyến
def test_uc05_ac3_t01_va_tuyen_mot_nut_hop_le():
    kiem_cau_truc_tuyen(T01)
    kiem_cau_truc_tuyen([NutTuyen(1, 0, 0)])  # nội thành (A3)


@pytest.mark.parametrize(
    "nut",
    [
        [],
        [NutTuyen(1, 5, 0), NutTuyen(2, 60, 50)],  # nút đầu phút ≠ 0
        [NutTuyen(1, 0, 3), NutTuyen(2, 60, 50)],  # nút đầu km ≠ 0
        [NutTuyen(1, 0, 0), NutTuyen(2, 60, 50), NutTuyen(3, 60, 70)],  # phút bằng nhau (biên)
        [NutTuyen(1, 0, 0), NutTuyen(2, 60, 50), NutTuyen(3, 90, 40)],  # km giảm
        [NutTuyen(1, 0, 0), NutTuyen(2, 60, 50), NutTuyen(1, 120, 90)],  # nút lặp
    ],
)
def test_uc05_ac3_cau_truc_sai(nut):
    with pytest.raises(LoiNghiepVu) as loi:
        kiem_cau_truc_tuyen(nut)
    assert loi.value.ma == "TUYEN_SAI"
    assert loi.value.chi_tiet


def test_uc05_ac3_km_bang_nhau_duoc():
    kiem_cau_truc_tuyen([NutTuyen(1, 0, 0), NutTuyen(2, 30, 0)])  # kho cạnh nút đầu: km không đổi


# AC4 – BR-66
def test_uc05_ac4_br66_bien_10_gio():
    kiem_br66_thoi_gian_tuyen([NutTuyen(1, 0, 0), NutTuyen(2, 600, 500)], gio_lai_ngay=10)
    with pytest.raises(LoiNghiepVu) as loi:
        kiem_br66_thoi_gian_tuyen([NutTuyen(1, 0, 0), NutTuyen(2, 601, 500)], gio_lai_ngay=10)
    assert loi.value.ma == "BR-66"


def test_uc05_ac4_br66_theo_cfg07():
    with pytest.raises(LoiNghiepVu):
        kiem_br66_thoi_gian_tuyen([NutTuyen(1, 0, 0), NutTuyen(2, 600, 500)], gio_lai_ngay=9)


# AC5 – BR-20
def test_uc05_ac5_t01_khong_canh_bao():
    assert canh_bao_br20(T01, TEN, gio_lai_lien_tuc=4) == []


def test_uc05_ac5_thieu_diem_nghi():
    nut = [NutTuyen(1, 0, 0), NutTuyen(2, 150, 100), NutTuyen(5, 300, 200)]
    cb = canh_bao_br20(nut, TEN, gio_lai_lien_tuc=4)
    assert len(cb) == 1
    assert "TP.HCM" in cb[0] and "Cần Thơ" in cb[0] and "300 phút" in cb[0]


@pytest.mark.parametrize(("phut", "so_canh_bao"), [(240, 0), (241, 1)])
def test_uc05_ac5_bien_4_gio(phut, so_canh_bao):
    assert len(canh_bao_br20([NutTuyen(1, 0, 0), NutTuyen(2, phut, 100)], TEN, gio_lai_lien_tuc=4)) == so_canh_bao


def test_uc05_ac5_diem_nghi_chia_doan():
    nut = [NutTuyen(1, 0, 0), NutTuyen(3, 200, 100, la_diem_nghi=True), NutTuyen(5, 400, 200)]
    assert canh_bao_br20(nut, TEN, gio_lai_lien_tuc=4) == []
