import json
import math
from pathlib import Path

import pytest

from app.modules.goi_y import service
from app.modules.goi_y.du_doan_tre import du_doan, phan_muc

# 20 mẫu tập kiểm tra kèm xác suất scikit-learn, do ml/train_du_doan_tre.py xuất (AC2)
FILE_MAU_SKLEARN = Path(__file__).resolve().parent.parent / "du_lieu" / "mau_du_doan_tre.json"

NGUONG = {"trung_binh": 0.3, "cao": 0.6}
MO_HINH = {
    "dac_trung": ["km", "thoi_gian_gio", "gio_khoi_hanh", "thu_trong_tuan"],
    "trung_binh": [100.0, 3.0, 12.0, 3.0],
    "do_lech": [50.0, 2.0, 4.0, 2.0],
    "he_so": [0.4, 0.8, -0.5, 0.0],
    "chan": -0.2,
    "nguong": NGUONG,
    "nguon": {},
}
# z = [(200-100)/50, (4-3)/2, (8-12)/4, (3-3)/2] = [2; 0,5; -1; 0]; đóng góp = [0,8; 0,4; 0,5; 0]
CHUYEN = {"km": 200, "thoi_gian_gio": 4.0, "gio_khoi_hanh": 8, "thu_trong_tuan": 3}


# AC3 – mức theo ngưỡng, biên thuộc mức trên
@pytest.mark.parametrize(
    ("xs", "muc"),
    [(0.0, "THAP"), (0.2999999, "THAP"), (0.3, "TRUNG_BINH"), (0.5999999, "TRUNG_BINH"), (0.6, "CAO"), (1.0, "CAO")],
)
def test_uc30_ac3_phan_muc_bien(xs, muc):
    assert phan_muc(xs, NGUONG) == muc


def test_uc30_ac3_xac_suat_va_yeu_to():
    kq = du_doan(MO_HINH, CHUYEN)
    # logit = -0,2 + 0,8 + 0,4 + 0,5 + 0 = 1,5 → 1 / (1 + e^-1,5) = 0,8175744761936437
    assert kq["xac_suat"] == pytest.approx(0.8175744761936437, abs=1e-12)
    assert kq["muc"] == "CAO"
    assert kq["yeu_to"] == [
        {"ten": "Quãng đường", "huong": "TANG"},  # 0,8
        {"ten": "Giờ khởi hành", "huong": "TANG"},  # (-0,5) * (-1) = +0,5
        {"ten": "Thời gian dự kiến", "huong": "TANG"},  # 0,4
        {"ten": "Thứ trong tuần", "huong": "GIAM"},  # 0 → không lớn hơn 0
    ]


def test_uc30_ac3_xac_suat_trong_0_1_khi_logit_lon():
    for chan in (-30.0, 30.0):
        xs = du_doan(MO_HINH | {"he_so": [0.0] * 4, "chan": chan}, CHUYEN)["xac_suat"]
        assert 0 <= xs <= 1
    assert du_doan(MO_HINH | {"he_so": [0.0] * 4, "chan": math.log(3 / 7)}, CHUYEN)["muc"] == "TRUNG_BINH"


# AC4 – mô hình sai định dạng thì raise (service bắt và trả không có gợi ý)
@pytest.mark.parametrize(
    "doi",
    [
        {"he_so": [0.1, 0.2]},
        {"do_lech": [50.0, 0.0, 4.0, 2.0]},
        {"dac_trung": ["km", "thoi_gian_gio", "gio_khoi_hanh", "mua"]},
        {"dac_trung": [], "trung_binh": [], "do_lech": [], "he_so": []},
    ],
)
def test_uc30_ac4_mo_hinh_sai_raise(doi):
    with pytest.raises(ValueError):
        du_doan(MO_HINH | doi, CHUYEN)


def test_uc30_ac4_thieu_khoa_raise():
    with pytest.raises(KeyError):
        du_doan({k: v for k, v in MO_HINH.items() if k != "chan"}, CHUYEN)


# AC2 – mô hình thật (mo_hinh_tre.json) tính bằng `math` khớp predict_proba của scikit-learn
def test_uc30_ac2_khop_sklearn():
    mo_hinh = json.loads(service.DUONG_DAN_MO_HINH.read_text(encoding="utf-8"))
    mau = json.loads(FILE_MAU_SKLEARN.read_text(encoding="utf-8"))
    assert len(mau) == 20
    for m in mau:
        xs = du_doan(mo_hinh, m["dac_trung"])["xac_suat"]
        assert abs(xs - m["xac_suat_sklearn"]) < 1e-6
