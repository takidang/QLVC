import pytest

from app.domain.xe_tai_xe import kiem_br14_khoi_luong_toan_bo
from app.loi import LoiNghiepVu


def test_uc03_ac3_khoi_luong_toan_bo_bang_tai_trong_duoc():
    kiem_br14_khoi_luong_toan_bo(tai_trong_kg=5000, ktt_toan_bo_kg=5000)  # biên: bằng nhau


def test_uc03_ac3_khoi_luong_toan_bo_nho_hon_1kg_bi_chan():
    with pytest.raises(LoiNghiepVu) as loi:
        kiem_br14_khoi_luong_toan_bo(tai_trong_kg=5000, ktt_toan_bo_kg=4999)
    assert loi.value.ma == "BR-14"
    assert loi.value.status_code == 422
