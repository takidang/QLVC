# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-34 Hiệu suất xe theo tháng. X1 tháng 10: 3 chuyến xong lấp đầy 76%, 50%, chạy rỗng → trung bình 42%."""

from datetime import datetime

import pytest

from app.models import ChiPhi, Ghep, Xe
from app.thoi_gian import GIO_VN, hom_nay_vn
from tests.api.test_uc17_xem_chuyen import HAN_XA, kb, luc  # noqa: F401 (kb là fixture)

URL = "/api/bao-cao/hieu-suat-xe"


def vn(thang, ngay, gio=6, phut=0):
    return datetime(2030, thang, ngay, gio, phut, tzinfo=GIO_VN)


@pytest.fixture
def hs(db, kb, dang_nhap_voi):
    """X1 (5.000 kg, 20 m³, định mức 20 lít/100 km): chuyến A (DA_QUYET_TOAN, 3.800 kg → 76%, 250 km),
    B (HOAN_THANH, 2.500 kg → 50%, 150 km), C (chạy rỗng, 100 km); thêm chuyến đang chạy và hủy không tính.
    X2 đang hoạt động không chạy, X3 ngừng không chạy. Đăng nhập Quản lý."""
    ql = dang_nhap_voi("QUAN_LY")
    x1 = db.get(Xe, kb["c01"].xe_id)
    x1.dinh_muc_lit_100km = 20

    def xe(bien_so, trang_thai="HOAT_DONG"):
        x = Xe(
            bien_so=bien_so,
            tai_trong_kg=3000,
            the_tich_m3=15,
            ktt_toan_bo_kg=7000,
            han_dang_kiem=HAN_XA,
            han_bao_hiem=HAN_XA,
            trang_thai=trang_thai,
        )
        db.add(x)
        db.flush()
        return x

    x2, x3 = xe("51C-222.22"), xe("51C-333.33", "NGUNG")
    so_don = iter(range(20, 99))

    def don(kg, m3):
        return kb["don"](next(so_don), "TP.HCM", "Cần Thơ", kg, m3, luc(18))

    def chuyen(trang_thai, luc_chay, km=None, *ds, xe_id=x1.id, chay_rong=False, **ghep_them):
        c = kb["chuyen"](kb["an"], trang_thai, 6, 22, *ds, **ghep_them)
        c.xe_id, c.khoi_hanh_thuc_te, c.chay_rong = xe_id, luc_chay, chay_rong
        if km:
            c.km_bat_dau, c.km_ket_thuc = km
        db.commit()
        return c

    def dau(c, lit, trang_thai="DA_DUYET"):
        db.add(
            ChiPhi(
                chuyen_id=c.id,
                loai="DAU",
                so_tien_khai=lit * 20_000,
                so_tien_duyet=lit * 20_000 if trang_thai == "DA_DUYET" else None,
                so_lit=lit,
                ghi_chu="Đổ dầu",
                trang_thai=trang_thai,
                nguoi_tao=ql.id,
            )
        )
        db.commit()

    a = chuyen("DA_QUYET_TOAN", vn(10, 5), (1000, 1250), don(3800, 10), ket_qua="DA_GIAO")
    db.add(Ghep(chuyen_id=a.id, don_hang_id=don(1000, 2).id, hieu_luc=False))  # đơn đã gỡ khỏi A: không vào lấp đầy
    chuyen("HUY", vn(10, 6), None, don(900, 2))  # chuyến hủy không tính
    b = chuyen("HOAN_THANH", vn(10, 12), (1250, 1400), don(2500, 4))
    c = chuyen("DA_QUYET_TOAN", vn(10, 20), (1400, 1500), chay_rong=True)
    chuyen("DANG_CHAY", vn(10, 25), (1500, 1500), don(1000, 2))
    dau(a, 60)
    dau(b, 45)
    dau(b, 30, "CHO_DUYET")
    dau(c, 10, "TU_CHOI")
    return {"x1": x1.id, "x2": x2.id, "x3": x3.id, "a": a, "b": b, "c": c, "chuyen": chuyen, "don": don}


def xem(client, thang="2030-10") -> dict:
    r = client.get(URL, params={"thang": thang})
    assert r.status_code == 200, r.text
    return r.json()


def dong(j, xe_id) -> dict:
    return next(d for d in j["du_lieu"] if d["xe_id"] == xe_id)


# AC1 – số chuyến, chạy rỗng, lấp đầy trung bình, km
def test_uc34_ac1_x1_thang_10(client, hs):
    x1 = dong(xem(client), hs["x1"])
    assert (x1["bien_so"], x1["so_chuyen"], x1["so_chuyen_rong"], x1["km"]) == ("51C-111.11", 3, 1, 500)
    assert x1["lap_day_tb"] == pytest.approx(0.42)  # (0,76 + 0,50 + 0) / 3


# AC2 – chỉ chuyến đã chạy xong trong tháng; biên tháng giờ VN; đơn đã gỡ không tính
def test_uc34_ac2_chi_chuyen_xong_trong_thang(client, hs):
    hs["chuyen"]("HOAN_THANH", vn(10, 31, 23, 59), (1500, 1600), hs["don"](5000, 1))  # cuối tháng 10: có (100%)
    hs["chuyen"]("HOAN_THANH", vn(11, 1, 0, 0), (1600, 1700))  # 00:00 ngày 1/11 giờ VN: tháng 11
    x1 = dong(xem(client), hs["x1"])
    assert (x1["so_chuyen"], x1["km"]) == (4, 600)  # chuyến đang chạy, hủy không tính
    assert x1["lap_day_tb"] == pytest.approx((0.76 + 0.5 + 0 + 1) / 4)  # A vẫn 76%: đơn 1.000 kg đã gỡ không vào
    assert dong(xem(client, "2030-11"), hs["x1"])["so_chuyen"] == 1


# AC3 – dầu thực tế (khoản dầu đã duyệt) so với tham khảo (km × định mức / 100)
def test_uc34_ac3_dau(client, db, hs):
    j = xem(client)
    x1, x2 = dong(j, hs["x1"]), dong(j, hs["x2"])
    assert (x1["dau_thuc_te_lit"], x1["dau_tham_khao_lit"], x1["chenh_lech_lit"]) == (105, 100, 5)
    assert x1["so_chuyen_chua_quyet_toan"] == 1  # B còn HOAN_THANH
    assert (x2["dau_tham_khao_lit"], x2["chenh_lech_lit"]) == (None, None)  # X2 chưa có định mức


# AC4 – xe hoạt động không chạy có dòng 0; xe ngừng không chạy không có; tổng
def test_uc34_ac4_xe_nam_bai_va_tong(client, hs):
    hs["chuyen"]("HOAN_THANH", vn(10, 15), (0, 300), hs["don"](3000, 1), xe_id=hs["x2"])  # X2: 100%
    j = xem(client, "2030-10")
    assert [d["bien_so"] for d in j["du_lieu"]] == ["51C-111.11", "51C-222.22"]  # X3 ngừng, không chạy
    hs["chuyen"]("HOAN_THANH", vn(10, 16), (0, 50), xe_id=hs["x3"])  # X3 ngừng nhưng có chuyến: có dòng
    j = xem(client, "2030-10")
    assert [d["bien_so"] for d in j["du_lieu"]] == ["51C-111.11", "51C-222.22", "51C-333.33"]
    t = j["tong"]
    assert (t["so_chuyen"], t["so_chuyen_rong"], t["km"], t["dau_thuc_te_lit"], t["so_chuyen_chua_quyet_toan"]) == (
        5,
        1,
        850,
        105,
        3,
    )
    # Trung bình trên 5 chuyến (0,76; 0,5; 0; 1; 0), không phải trung bình của 3 xe
    assert t["lap_day_tb"] == pytest.approx((0.76 + 0.5 + 0 + 1 + 0) / 5)
    assert t["dau_tham_khao_lit"] == 100  # chỉ X1 có định mức

    trong = dong(xem(client, "2030-09"), hs["x2"])
    assert (trong["so_chuyen"], trong["lap_day_tb"], trong["km"], trong["dau_thuc_te_lit"]) == (0, None, 0, 0)
    assert xem(client, "2030-09")["tong"]["lap_day_tb"] is None


# AC5 – tham số
@pytest.mark.parametrize("params", [{"thang": "2030-13"}, {"thang": "2030-1"}, {"thang": "2030-10", "xe_id": "1"}])
def test_uc34_ac5_tham_so_sai_400(client, hs, params):
    r = client.get(URL, params=params)
    assert (r.status_code, r.json()["ma"]) == (400, "DU_LIEU_KHONG_HOP_LE")


def test_uc34_ac5_mac_dinh_thang_nay(client, hs):
    r = client.get(URL)
    assert (r.status_code, r.json()["thang"]) == (200, hom_nay_vn().strftime("%Y-%m"))


# AC6 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("QUAN_LY", 200), ("KE_TOAN", 200), ("DIEU_PHOI", 403), ("TAI_XE", 403)])
def test_uc34_ac6_phan_quyen(client, dang_nhap_voi, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get(URL).status_code == ma


def test_uc34_ac6_chua_dang_nhap_401(client):
    assert client.get(URL).status_code == 401
