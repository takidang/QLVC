# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
import unicodedata

import pytest

from app.models import NguoiDung
from tests.api.test_uc17_xem_chuyen import dang_nhap_tai_xe, kb, luc  # noqa: F401 (kb là fixture)

NHOM = {"chuyen", "don", "xe", "tai_xe", "khach_hang"}


@pytest.fixture
def tk(db, kb):
    """6 chuyến CH-01…CH-06, 6 đơn DH-0001…, tài xế An và Bình (họ tên "Bình" dựng sẵn), xe 51C-111.11, khách Cty A."""
    db.get(NguoiDung, kb["binh"].nguoi_dung_id).ho_ten = "Bình"
    ch = kb["chuyen"]
    ch(kb["an"], "LAP")  # CH-02
    ch(kb["an"], "HUY")  # CH-03
    ch(kb["binh"], "DA_CHOT")  # CH-04
    ch(kb["an"], "DANG_CHAY")  # CH-05
    ch(kb["an"], "HOAN_THANH")  # CH-06
    for so in (5, 6, 7):
        kb["don"](so, "TP.HCM", "Tiền Giang", 100, 1, luc(18))  # đủ 6 đơn: DH-0001, 0002, 0004, 0005, 0006, 0007
    return kb


def tim(client, q):
    r = client.get("/api/tim", params={"q": q})
    assert r.status_code == 200, r.text
    return r.json()


def ma(j, nhom, khoa):
    return [d[khoa] for d in j[nhom]["ds"]]


# AC1 – tìm đủ 5 nhóm, không phân biệt hoa thường, NFD
def test_uc36_ac1_dieu_phoi_tim_5_nhom(client, dang_nhap_voi, tk):
    dang_nhap_voi("DIEU_PHOI")
    j = tim(client, "cty a")
    assert set(j) == NHOM | {"q"} and j["q"] == "cty a"
    assert (j["khach_hang"]["tong"], j["khach_hang"]["ds"][0]["ten"]) == (1, "Cty A")
    assert j["don"]["tong"] == 6  # đơn của khách Cty A
    assert j["xe"]["tong"] == j["tai_xe"]["tong"] == j["chuyen"]["tong"] == 0
    j = tim(client, "51C-111")
    assert (ma(j, "xe", "bien_so"), j["chuyen"]["tong"]) == (["51C-111.11"], 6)  # xe chạy cả 6 chuyến
    j = tim(client, "dh-0004")
    assert ma(j, "don", "ma_don") == ["DH-0004"] and j["don"]["ds"][0]["ten_khach"] == "Cty A"
    assert tim(client, "0901116789")["khach_hang"]["tong"] == 1  # theo số điện thoại


def test_uc36_ac1_chuan_hoa_nfc(client, dang_nhap_voi, tk):
    dang_nhap_voi("DIEU_PHOI")
    for q in ("Bình", "BÌNH", unicodedata.normalize("NFD", "bình"), "  bình  "):
        j = tim(client, q)
        assert ma(j, "tai_xe", "ho_ten") == ["Bình"], q
        assert ma(j, "chuyen", "ma_chuyen") == ["CH-04"], q  # chuyến của Bình (khớp tên tài xế)


# AC2 – tối đa 5 dòng, tong là số khớp thật
def test_uc36_ac2_toi_da_5_dong(client, dang_nhap_voi, tk):
    dang_nhap_voi("DIEU_PHOI")
    j = tim(client, "CH-0")
    assert j["chuyen"]["tong"] == 6 and len(j["chuyen"]["ds"]) == 5
    assert ma(j, "chuyen", "ma_chuyen") == ["CH-06", "CH-05", "CH-04", "CH-03", "CH-02"]  # mới trước
    j = tim(client, "DH-000")
    assert j["don"]["tong"] == 6 and len(j["don"]["ds"]) == 5
    assert tim(client, "DH-0007")["don"]["tong"] == 1


# AC3 – quyền theo vai trò
def test_uc36_ac3_quan_ly_nhu_dieu_phoi(client, dang_nhap_voi, tk):
    dang_nhap_voi("QUAN_LY")
    j = tim(client, "Bình")
    assert (j["tai_xe"]["tong"], j["chuyen"]["tong"]) == (1, 1)
    assert tim(client, "51C-111")["xe"]["tong"] == 1


def test_uc36_ac3_ke_toan_khong_thay_xe_tai_xe(client, dang_nhap_voi, tk):
    dang_nhap_voi("KE_TOAN")
    j = tim(client, "cty a")
    assert (j["don"]["tong"], j["khach_hang"]["tong"]) == (6, 1)
    assert tim(client, "51C-111")["xe"] == {"tong": 0, "ds": []}  # xe khớp nhưng Kế toán không được xem
    j = tim(client, "Bình")
    assert j["tai_xe"] == {"tong": 0, "ds": []} and j["chuyen"]["tong"] == 1


def test_uc36_ac3_tai_xe_chi_thay_chuyen_cua_minh(client, tk):
    dang_nhap_tai_xe(client, "an")
    j = tim(client, "CH-0")
    # An có CH-01 (DA_CHOT), CH-05 (DANG_CHAY), CH-06 (HOAN_THANH); không thấy LAP, HUY, chuyến của Bình
    assert sorted(ma(j, "chuyen", "ma_chuyen")) == ["CH-01", "CH-05", "CH-06"] and j["chuyen"]["tong"] == 3
    assert tim(client, "51C-111")["chuyen"]["tong"] == 3  # tìm theo biển số
    assert tim(client, "Bình")["chuyen"]["tong"] == 0  # chuyến của Bình không phải của An
    for q in ("cty a", "DH-000", "Bình", "51C-111"):
        j = tim(client, q)
        assert all(j[n] == {"tong": 0, "ds": []} for n in ("don", "xe", "tai_xe", "khach_hang")), q


# AC4 – dữ liệu sai, ký tự đại diện, chưa đăng nhập
@pytest.mark.parametrize("q", ["", "   ", "a", " a ", "x" * 101])
def test_uc36_ac4_tu_khoa_sai(client, dang_nhap_voi, tk, q):
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/tim", params={"q": q}).status_code == 400


def test_uc36_ac4_thieu_hoac_tham_so_la(client, dang_nhap_voi, tk):
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/tim").status_code == 400
    assert client.get("/api/tim", params={"q": "cty", "x": 1}).status_code == 400


@pytest.mark.parametrize("q", ["%%", "__", "%_"])
def test_uc36_ac4_ky_tu_dai_dien_khong_khop_tat_ca(client, dang_nhap_voi, tk, q):
    dang_nhap_voi("DIEU_PHOI")
    j = tim(client, q)
    assert all(j[n]["tong"] == 0 for n in NHOM)


def test_uc36_ac4_chua_dang_nhap(client, tk):
    assert client.get("/api/tim", params={"q": "cty"}).status_code == 401
