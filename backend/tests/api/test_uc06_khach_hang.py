import pytest
from sqlalchemy import select

from app.models import KhachHang

CTY_A = {"ten": "Cty A", "sdt": "0909123456", "dia_chi": "12 Nguyễn Huệ, Q.1, TP.HCM", "ma_so_thue": "0312345678"}


def them(client, **doi):
    return client.post("/api/khach-hang", json={**CTY_A, **doi})


def kh_mau(db, **doi) -> KhachHang:
    kh = KhachHang(**{**CTY_A, **doi})
    db.add(kh)
    db.commit()
    return kh


# AC1 – thêm, chuẩn hóa tên và SĐT
@pytest.mark.parametrize(("sdt", "luu"), [("0909 123.456", "0909123456"), ("+84 909-123-456", "0909123456")])
def test_uc06_ac1_them_khach_chuan_hoa(client, dang_nhap_voi, sdt, luu):
    dang_nhap_voi("DIEU_PHOI")
    r = them(client, ten="  Cty A  ", sdt=sdt)
    assert r.status_code == 201
    assert r.json()["ten"] == "Cty A"
    assert r.json()["sdt"] == luu
    assert r.json()["trang_thai"] == "HOAT_DONG"


def test_uc06_ac1_chi_can_ten_va_sdt(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    r = client.post("/api/khach-hang", json={"ten": "Anh Ba", "sdt": "0911222333"})
    assert r.status_code == 201
    assert r.json()["dia_chi"] is None


# AC2 – dữ liệu sai, kèm ca biên độ dài SĐT
@pytest.mark.parametrize(
    ("doi", "mong_doi"),
    [
        ({"ten": ""}, 400),
        ({"ten": "   "}, 400),
        ({"sdt": "090912345"}, 400),  # 9 số
        ({"sdt": "0909123456"}, 201),  # 10 số
        ({"sdt": "02838123456"}, 201),  # 11 số
        ({"sdt": "028381234567"}, 400),  # 12 số
        ({"sdt": "09a9123456"}, 400),
        ({"sdt": "1909123456"}, 400),
        ({"ma_so_thue": "031234567"}, 400),
        ({"ma_so_thue": "0312345678-001"}, 201),
        ({"ma_so_thue": "0312345678001"}, 400),
    ],
)
def test_uc06_ac2_du_lieu_sai_bi_chan(client, dang_nhap_voi, db, doi, mong_doi):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client, **doi).status_code == mong_doi
    da_luu = db.scalar(select(KhachHang.id)) is not None
    assert da_luu == (mong_doi == 201)


def test_uc06_ac2_loi_sdt_la_tieng_viet(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    loi = them(client, sdt="123").json()["chi_tiet"]
    assert loi[0]["loc"][-1] == "sdt"
    assert "bắt đầu bằng 0" in loi[0]["msg"]


# AC3 – tìm, lọc, phân trang
def test_uc06_ac3_tim_loc_phan_trang(client, dang_nhap_voi, db):
    kh_mau(db, ten="Cty A", sdt="0901116789")
    kh_mau(db, ten="Cty B", sdt="0902220000")
    kh_mau(db, ten="Anh Ba chợ Bến Thành", sdt="0903336789")
    kh_mau(db, ten="Cty C ngừng", sdt="0904440000", trang_thai="NGUNG")
    dang_nhap_voi("DIEU_PHOI")

    ten = client.get("/api/khach-hang", params={"tim": "cty a"}).json()
    assert [k["ten"] for k in ten["du_lieu"]] == ["Cty A"]
    sdt = client.get("/api/khach-hang", params={"tim": "6789"}).json()
    assert sdt["tong"] == 2
    hoat_dong = client.get("/api/khach-hang", params={"tim": "cty", "trang_thai": "HOAT_DONG"}).json()
    assert hoat_dong["tong"] == 2
    trang2 = client.get("/api/khach-hang", params={"trang": 2, "so_dong": 3}).json()
    assert trang2["tong"] == 4
    assert len(trang2["du_lieu"]) == 1
    assert client.get("/api/khach-hang", params={"tim": "%"}).json()["tong"] == 0


# AC4 – sửa, trạng thái, không xóa
def test_uc06_ac4_sua_va_trang_thai(client, dang_nhap_voi, db):
    kh = kh_mau(db)
    dang_nhap_voi("DIEU_PHOI")
    r = client.patch(f"/api/khach-hang/{kh.id}", json={"sdt": "0909 999 888", "dia_chi": None})
    assert r.status_code == 200
    assert r.json()["sdt"] == "0909999888"
    assert r.json()["dia_chi"] is None  # trường không bắt buộc được xóa
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"ten": None}).status_code == 400
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"sdt": None}).status_code == 400
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"trang_thai": "NGUNG"}).json()["trang_thai"] == "NGUNG"
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"trang_thai": "HOAT_DONG"}).status_code == 200
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"trang_thai": "XOA"}).status_code == 400
    assert client.delete(f"/api/khach-hang/{kh.id}").status_code == 405
    assert client.get(f"/api/khach-hang/{kh.id}").json()["ten"] == "Cty A"


# AC5 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "xem", "sua"),
    [("DIEU_PHOI", 200, 201), ("QUAN_LY", 200, 201), ("KE_TOAN", 200, 403), ("TAI_XE", 403, 403)],
)
def test_uc06_ac5_phan_quyen(client, dang_nhap_voi, db, vai_tro, xem, sua):
    kh = kh_mau(db)
    dang_nhap_voi(vai_tro)
    assert client.get("/api/khach-hang").status_code == xem
    assert client.get(f"/api/khach-hang/{kh.id}").status_code == xem
    assert them(client).status_code == sua
    assert client.patch(f"/api/khach-hang/{kh.id}", json={"ten": "X"}).status_code == (200 if sua == 201 else 403)


def test_uc06_ac5_chua_dang_nhap_va_khong_ton_tai(client, dang_nhap_voi):
    assert client.get("/api/khach-hang").status_code == 401
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/khach-hang/999").status_code == 404
    assert client.patch("/api/khach-hang/999", json={"ten": "X"}).status_code == 404
