import pytest

from app.domain.xe_tai_xe import hang_gplx_toi_thieu, kiem_br14_hang_gplx
from app.loi import LoiNghiepVu


# AC4 – BR-14: hạng GPLX theo khối lượng toàn bộ, thứ bậc C ⊇ C1 ⊇ B
@pytest.mark.parametrize(
    ("hang", "ktt_kg"),
    [
        ("B", 3500),  # biên: đúng 3.500 kg vẫn là B
        ("C1", 3501),
        ("C1", 7500),  # biên trên của C1
        ("C", 7501),
        ("C", 9500),  # xe X1 trong kịch bản nghiep-vu.md mục 11
        ("C1", 1000),  # hạng cao lái được xe nhỏ
        ("C", 1000),
        ("C", 3501),
    ],
)
def test_uc04_ac4_hang_du_thi_duoc_lai(hang, ktt_kg):
    kiem_br14_hang_gplx(hang, ktt_kg)


@pytest.mark.parametrize(
    ("hang", "ktt_kg", "can"),
    [
        ("B", 3501, "C1"),  # vượt 1 kg là cần C1
        ("B", 9500, "C"),  # tài xế Bình hạng B với xe X1 (kịch bản mục 11)
        ("C1", 7501, "C"),  # vượt 1 kg là cần C
    ],
)
def test_uc04_ac4_hang_thap_bi_chan(hang, ktt_kg, can):
    with pytest.raises(LoiNghiepVu) as loi:
        kiem_br14_hang_gplx(hang, ktt_kg)
    assert loi.value.ma == "BR-14"
    assert loi.value.status_code == 422
    assert f"hạng {can}" in loi.value.thong_diep


@pytest.mark.parametrize(("ktt_kg", "hang"), [(1, "B"), (3500, "B"), (3501, "C1"), (7500, "C1"), (7501, "C")])
def test_uc04_ac4_hang_toi_thieu_theo_khoi_luong(ktt_kg, hang):
    assert hang_gplx_toi_thieu(ktt_kg) == hang
