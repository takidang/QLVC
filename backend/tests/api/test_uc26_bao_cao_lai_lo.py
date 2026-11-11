# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-26 Báo cáo lãi lỗ. Kịch bản mục 11 bước 8: X1 tháng 10 = Σ lãi các chuyến − chi phí cố định 9.000.000."""

from datetime import datetime

import pytest

from app.models import ChiPhiCoDinhXe, QuyetToan, Xe
from app.thoi_gian import GIO_VN, hom_nay_vn
from tests.api.test_uc17_xem_chuyen import HAN_XA, kb  # noqa: F401 (kb là fixture)

URL = "/api/bao-cao/lai-lo"
COT_TONG = ("so_chuyen", "doanh_thu", "tong_chi", "luong_tai_xe", "lai_chuyen", "chi_phi_co_dinh", "lai")


def lay(d, *khoa):
    return tuple(d[k] for k in khoa)


def vn(thang, ngay, gio=6, phut=0):
    return datetime(2030, thang, ngay, gio, phut, tzinfo=GIO_VN)


@pytest.fixture
def bc(db, kb, dang_nhap_voi):
    """X1: 2 chuyến quyết toán tháng 10 (lãi 3.000.000, 2.500.000), 1 chuyến HOAN_THANH chờ quyết toán, chuyến DA_CHOT
    của kb; X2 không chạy, chi phí cố định 4.000.000. Chi phí cố định X1 tháng 10 là 9.000.000. Đăng nhập Kế toán."""
    kt = dang_nhap_voi("KE_TOAN")
    x1_id = kb["c01"].xe_id
    x2 = Xe(
        bien_so="51C-222.22",
        tai_trong_kg=3000,
        the_tich_m3=15,
        ktt_toan_bo_kg=7000,
        han_dang_kiem=HAN_XA,
        han_bao_hiem=HAN_XA,
    )
    db.add(x2)
    db.flush()

    def chuyen(luc, lai=None, xe_id=x1_id, trang_thai="DA_QUYET_TOAN", doanh_thu=5_000_000):
        c = kb["chuyen"](kb["an"], trang_thai, 6, 22)
        c.xe_id, c.khoi_hanh_thuc_te = xe_id, luc
        if trang_thai == "DA_QUYET_TOAN":
            db.add(
                QuyetToan(
                    chuyen_id=c.id,
                    doanh_thu=doanh_thu,
                    tong_chi=1_400_000,
                    luong_tai_xe=600_000,
                    lai=lai,
                    chenh_lech_tam_ung=0,
                    xu_ly_chenh_lech="KHONG_CHENH",
                    ke_toan_id=kt.id,
                )
            )
        db.commit()
        return c

    def co_dinh(xe_id, thang, so_tien):
        db.add(ChiPhiCoDinhXe(xe_id=xe_id, thang=thang, so_tien=so_tien))
        db.commit()

    ca = chuyen(vn(10, 5), 3_000_000)
    cb = chuyen(vn(10, 20), 2_500_000, doanh_thu=4_500_000)
    chuyen(vn(10, 25), trang_thai="HOAN_THANH")
    co_dinh(x1_id, "2030-10", 9_000_000)
    co_dinh(x2.id, "2030-10", 4_000_000)
    return {"x1": x1_id, "x2": x2.id, "ca": ca, "cb": cb, "chuyen": chuyen, "co_dinh": co_dinh}


def xem(client, theo, tu="2030-10", den="2030-10"):
    r = client.get(URL, params={"theo": theo, "tu": tu, "den": den})
    assert r.status_code == 200, r.text
    return r.json()


# AC1 – theo chuyến: số đúng bằng QUYET_TOAN, chỉ chuyến DA_QUYET_TOAN, đếm chuyến chờ quyết toán
def test_uc26_ac1_theo_chuyen_lay_so_da_khoa(client, db, bc):
    j = xem(client, "chuyen")
    assert [d["ma_chuyen"] for d in j["du_lieu"]] == [bc["cb"].ma_chuyen, bc["ca"].ma_chuyen]  # mới trước
    d = j["du_lieu"][1]
    qt = db.query(QuyetToan).filter_by(chuyen_id=bc["ca"].id).one()
    assert (d["doanh_thu"], d["tong_chi"], d["luong_tai_xe"], d["lai"]) == (
        qt.doanh_thu,
        qt.tong_chi,
        qt.luong_tai_xe,
        qt.lai,
    )
    assert (d["chuyen_id"], d["ngay"], d["xe_id"], d["bien_so"], d["ten_tuyen"]) == (
        bc["ca"].id,
        "2030-10-05",
        bc["x1"],
        "51C-111.11",
        "TP.HCM – Cần Thơ",
    )
    assert (j["tong"]["so_chuyen"], j["tong"]["doanh_thu"], j["tong"]["lai"]) == (2, 9_500_000, 5_500_000)
    assert j["so_chuyen_cho_quyet_toan"] == 1  # chuyến HOAN_THANH; chuyến DA_CHOT của kb không đếm
    assert (j["theo"], j["tu"], j["den"], j["thieu_chi_phi_co_dinh"]) == ("chuyen", "2030-10", "2030-10", [])


def test_uc26_ac1_chuyen_ngoai_khoang_khong_vao(client, bc):
    bc["chuyen"](vn(11, 3), 1_000_000)
    assert len(xem(client, "chuyen")["du_lieu"]) == 2
    assert len(xem(client, "chuyen", "2030-11", "2030-11")["du_lieu"]) == 1


# AC2 – biên tháng theo giờ Việt Nam
def test_uc26_ac2_bien_thang_gio_viet_nam(client, bc):
    bc["chuyen"](vn(10, 31, 23, 59), 100_000)
    bc["chuyen"](vn(11, 1, 0, 0), 200_000)
    j = xem(client, "thang", "2030-10", "2030-11")
    assert {d["thang"]: d["lai_chuyen"] for d in j["du_lieu"]} == {"2030-10": 5_600_000, "2030-11": 200_000}
    # Xem riêng từng tháng: mốc lọc cũng phải theo giờ Việt Nam (00:00 ngày 1/11 VN là 17:00 ngày 31/10 UTC)
    assert xem(client, "chuyen", "2030-10", "2030-10")["tong"]["lai"] == 5_600_000
    assert xem(client, "chuyen", "2030-11", "2030-11")["tong"]["lai"] == 200_000


# AC3 – theo xe: lãi xe = Σ lãi chuyến − chi phí cố định; xe không chạy vẫn có dòng (lỗ)
def test_uc26_ac3_theo_xe_tru_chi_phi_co_dinh(client, bc):
    j = xem(client, "xe")
    x = {d["bien_so"]: d for d in j["du_lieu"]}
    assert list(x) == ["51C-111.11", "51C-222.22"]
    x1, x2 = x["51C-111.11"], x["51C-222.22"]
    assert lay(x1, "so_chuyen", "lai_chuyen", "chi_phi_co_dinh", "lai") == (2, 5_500_000, 9_000_000, -3_500_000)
    assert (x1["doanh_thu"], x1["tong_chi"], x1["luong_tai_xe"]) == (9_500_000, 2_800_000, 1_200_000)
    assert (x2["xe_id"], x2["so_chuyen"], x2["lai_chuyen"], x2["chi_phi_co_dinh"], x2["lai"]) == (
        bc["x2"],
        0,
        0,
        4_000_000,
        -4_000_000,
    )
    t = j["tong"]
    assert (t["lai_chuyen"], t["chi_phi_co_dinh"], t["lai"]) == (5_500_000, 13_000_000, -7_500_000)


# AC4 – theo tháng: đủ tháng kể cả tháng trống, mỗi tháng trừ chi phí cố định của tháng đó
def test_uc26_ac4_theo_thang_du_thang_tru_dung_thang(client, bc):
    bc["chuyen"](vn(11, 10), 800_000)
    bc["co_dinh"](bc["x1"], "2030-11", 1_000_000)
    bc["co_dinh"](bc["x1"], "2030-12", 7_000_000)  # ngoài khoảng, không trừ
    j = xem(client, "thang", "2030-09", "2030-11")
    assert [d["thang"] for d in j["du_lieu"]] == ["2030-09", "2030-10", "2030-11"]
    t9, t10, t11 = j["du_lieu"]
    assert (t9["so_chuyen"], t9["chi_phi_co_dinh"], t9["lai"]) == (0, 0, 0)
    assert (t10["so_chuyen"], t10["lai_chuyen"], t10["chi_phi_co_dinh"], t10["lai"]) == (
        2,
        5_500_000,
        13_000_000,
        -7_500_000,
    )
    assert lay(t11, "so_chuyen", "lai_chuyen", "chi_phi_co_dinh", "lai") == (1, 800_000, 1_000_000, -200_000)
    for k in COT_TONG:
        assert j["tong"][k] == sum(d[k] for d in j["du_lieu"]), k


# AC5 – thiếu chi phí cố định: tính 0 và báo
def test_uc26_ac5_thieu_chi_phi_co_dinh_tinh_0_va_bao(client, bc):
    bc["chuyen"](vn(11, 4), 700_000, xe_id=bc["x2"])  # X2 chạy tháng 11, chưa nhập chi phí cố định
    for theo in ("xe", "thang"):
        j = xem(client, theo, "2030-10", "2030-11")
        assert j["thieu_chi_phi_co_dinh"] == [{"xe_id": bc["x2"], "bien_so": "51C-222.22", "thang": "2030-11"}], theo
    x2 = next(d for d in xem(client, "xe", "2030-11", "2030-11")["du_lieu"] if d["xe_id"] == bc["x2"])
    assert (x2["chi_phi_co_dinh"], x2["lai"]) == (0, 700_000)
    bc["co_dinh"](bc["x2"], "2030-11", 500_000)
    assert xem(client, "xe", "2030-10", "2030-11")["thieu_chi_phi_co_dinh"] == []


# AC6 – tham số sai → 400; thiếu tháng → tháng hiện tại
@pytest.mark.parametrize(
    "params",
    [
        {"theo": "khach"},
        {"tu": "2030-13", "den": "2030-13"},
        {"tu": "2030-1", "den": "2030-1"},
        {"tu": "2030-10-01"},
        {"tu": "2030-11", "den": "2030-10"},
        {"tu": "2030-01", "den": "2031-01"},  # 13 tháng
        {"tu": "2030-10", "den": "2030-10", "xe_id": "1"},  # tham số lạ
    ],
)
def test_uc26_ac6_tham_so_sai_400(client, bc, params):
    r = client.get(URL, params=params)
    assert r.status_code == 400, r.text
    assert r.json()["ma"] == "DU_LIEU_KHONG_HOP_LE"


def test_uc26_ac6_bien_12_thang_duoc_va_mac_dinh_thang_nay(client, bc):
    assert len(xem(client, "thang", "2030-01", "2030-12")["du_lieu"]) == 12
    nay = hom_nay_vn().strftime("%Y-%m")
    r = client.get(URL)
    assert r.status_code == 200
    assert (r.json()["theo"], r.json()["tu"], r.json()["den"]) == ("thang", nay, nay)


# AC7 – phân quyền
@pytest.mark.parametrize("vai_tro", ["QUAN_LY", "KE_TOAN", "DIEU_PHOI"])
def test_uc26_ac7_vai_tro_duoc_xem(client, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert client.get(URL).status_code == 200


def test_uc26_ac7_tai_xe_403_chua_dang_nhap_401(client, dang_nhap_voi):
    assert client.get(URL).status_code == 401
    dang_nhap_voi("TAI_XE")
    r = client.get(URL)
    assert (r.status_code, r.json()["ma"]) == (403, "KHONG_DU_QUYEN")
