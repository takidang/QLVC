import unicodedata
from datetime import date

import pytest
from sqlalchemy import select

from app.models import BangGia, CauHinh
from app.modules.danh_muc.bang_gia.service import tra_gia
from app.thoi_gian import hom_nay_vn

HCM_CT = {
    "tinh_lay": "TP.HCM",
    "tinh_giao": "Cần Thơ",
    "don_gia_kg": 1500,
    "cuoc_toi_thieu": 50000,
    "hieu_luc_tu": "2026-10-01",
}


def them(client, **doi):
    return client.post("/api/bang-gia", json={**HCM_CT, **doi})


def gia(db, tinh_lay, tinh_giao, don_gia, ngay) -> BangGia:
    bg = BangGia(tinh_lay=tinh_lay, tinh_giao=tinh_giao, don_gia_kg=don_gia, cuoc_toi_thieu=0, hieu_luc_tu=ngay)
    db.add(bg)
    db.commit()
    return bg


# AC1 – thêm mức giá, ca biên
@pytest.mark.parametrize(
    ("doi", "mong_doi"),
    [
        ({}, 201),
        ({"tinh_lay": "  TP.HCM  "}, 201),
        ({"don_gia_kg": 0}, 400),
        ({"don_gia_kg": 1}, 201),
        ({"cuoc_toi_thieu": -1}, 400),
        ({"cuoc_toi_thieu": 0}, 201),
        ({"hieu_luc_tu": None}, 400),
        ({"tinh_giao": "   "}, 400),
        ({"tinh_lay": "Cần Thơ"}, 201),  # nội tỉnh: tỉnh lấy = tỉnh giao
    ],
)
def test_uc07_ac1_them_muc_gia(client, dang_nhap_voi, doi, mong_doi):
    dang_nhap_voi("QUAN_LY")
    r = them(client, **doi)
    assert r.status_code == mong_doi
    if mong_doi == 201:
        assert r.json()["tinh_lay"] == r.json()["tinh_lay"].strip()


# AC2 – trùng cặp + ngày (không phân biệt hoa thường), khác ngày được, unique ở CSDL
def test_uc07_ac2_trung_cap_tinh_va_ngay(client, dang_nhap_voi, db):
    dang_nhap_voi("QUAN_LY")
    assert them(client).status_code == 201
    r = them(client, tinh_lay="tp.hcm", tinh_giao="CẦN THƠ", don_gia_kg=9999)
    assert r.status_code == 409
    assert r.json()["ma"] == "BANG_GIA_TRUNG"
    assert them(client, hieu_luc_tu="2026-11-01").status_code == 201
    assert db.scalars(select(BangGia.don_gia_kg).order_by(BangGia.id)).all() == [1500, 1500]


# AC3 – tra giá theo ngày hiệu lực (BR-48)
def test_uc07_ac3_tra_gia_theo_ngay_hieu_luc(db):
    gia(db, "TP.HCM", "Cần Thơ", 1500, date(2026, 10, 1))
    gia(db, "TP.HCM", "Cần Thơ", 1600, date(2026, 11, 1))
    gia(db, "TP.HCM", "Cần Thơ", 9999, date(2027, 1, 1))  # mức tương lai

    assert tra_gia(db, "TP.HCM", "Cần Thơ", date(2026, 10, 15)).don_gia_kg == 1500
    assert tra_gia(db, "TP.HCM", "Cần Thơ", date(2026, 11, 1)).don_gia_kg == 1600  # biên: đúng ngày hiệu lực
    assert tra_gia(db, "TP.HCM", "Cần Thơ", date(2026, 12, 31)).don_gia_kg == 1600  # chưa tới mức tương lai
    assert tra_gia(db, "  tp.hcm ", "CẦN THƠ", date(2026, 10, 15)).don_gia_kg == 1500
    assert tra_gia(db, "Cần Thơ", "TP.HCM", date(2026, 10, 15)) is None  # chiều ngược
    assert tra_gia(db, "TP.HCM", "Cần Thơ", date(2026, 9, 30)) is None  # trước mọi mức
    assert tra_gia(db, "Cần Thơ", "Cà Mau", date(2026, 10, 15)) is None  # Đ7 kịch bản mục 11


# AC4 – danh sách, cờ đang áp dụng
def test_uc07_ac4_danh_sach_va_dang_ap_dung(client, dang_nhap_voi, db):
    hom_nay = hom_nay_vn()
    cu = gia(db, "TP.HCM", "Cần Thơ", 1500, date(2026, 1, 1))
    moi = gia(db, "TP.HCM", "Cần Thơ", 1600, hom_nay)
    tuong_lai = gia(db, "TP.HCM", "Cần Thơ", 1700, date(hom_nay.year + 1, 1, 1))
    khac = gia(db, "Long An", "Cần Thơ", 1200, date(2026, 1, 1))
    dang_nhap_voi("QUAN_LY")

    ds = client.get("/api/bang-gia").json()
    ap_dung = {bg["id"] for bg in ds["du_lieu"] if bg["dang_ap_dung"]}
    assert ap_dung == {moi.id, khac.id}  # mỗi cặp đúng một mức, mức hiệu lực hôm nay thắng mức cũ
    assert cu.id not in ap_dung and tuong_lai.id not in ap_dung
    assert ds["tong"] == 4

    assert client.get("/api/bang-gia", params={"tim": "long"}).json()["tong"] == 1
    assert len(client.get("/api/bang-gia", params={"trang": 2, "so_dong": 3}).json()["du_lieu"]) == 1
    assert client.get("/api/bang-gia/ten-tinh").json() == ["Cần Thơ", "Long An", "TP.HCM"]


# AC5 – sửa mức giá
def test_uc07_ac5_sua_muc_gia(client, dang_nhap_voi, db):
    a = gia(db, "TP.HCM", "Cần Thơ", 1500, date(2026, 10, 1))
    gia(db, "TP.HCM", "Cần Thơ", 1600, date(2026, 11, 1))
    dang_nhap_voi("QUAN_LY")
    r = client.patch(f"/api/bang-gia/{a.id}", json={"don_gia_kg": 1550})
    assert r.status_code == 200
    assert r.json()["don_gia_kg"] == 1550
    assert client.patch(f"/api/bang-gia/{a.id}", json={"hieu_luc_tu": "2026-11-01"}).status_code == 409
    assert client.patch(f"/api/bang-gia/{a.id}", json={"don_gia_kg": None}).status_code == 400
    assert client.patch("/api/bang-gia/999", json={"don_gia_kg": 1}).status_code == 404
    db.refresh(a)
    assert (a.don_gia_kg, a.hieu_luc_tu) == (1550, date(2026, 10, 1))


# AC6 – cấu hình mặc định
def test_uc07_ac6_cau_hinh_mac_dinh(client, dang_nhap_voi):
    dang_nhap_voi("QUAN_LY")
    ds = {ts["ma"]: ts for ts in client.get("/api/cau-hinh").json()}
    assert list(ds) == ["CFG-01", "CFG-02", "CFG-04", "CFG-05", "CFG-06", "CFG-07", "CFG-08", "CFG-09", "CFG-10"]
    assert (ds["CFG-01"]["gia_tri"], ds["CFG-01"]["don_vi"]) == ("333", "kg/m³")
    assert ds["CFG-07"]["gia_tri"] == "10/48/4"
    assert ds["CFG-08"]["gia_tri"] == "20"
    assert ds["CFG-10"]["gia_tri"] == "24"
    assert ds["CFG-01"]["nguoi_sua"] is None


# AC7 – sửa cấu hình, kiểm theo từng tham số
@pytest.mark.parametrize(
    ("ma", "gia_tri", "mong_doi"),
    [
        ("CFG-01", "300", 200),
        ("CFG-01", "0", 400),
        ("CFG-01", "abc", 400),
        ("CFG-06", "500", 200),
        ("CFG-06", "0", 400),
        ("CFG-04", "1", 200),
        ("CFG-04", "0", 400),
        ("CFG-02", "0", 200),
        ("CFG-08", "-5", 400),
        ("CFG-07", "9/45/4", 200),
        ("CFG-07", "10/48", 400),
        ("CFG-07", "10/0/4", 400),
        ("CFG-03", "2", 404),  # bỏ ở 0.5
        ("CFG-99", "1", 404),
    ],
)
def test_uc07_ac7_sua_cau_hinh(client, dang_nhap_voi, ma, gia_tri, mong_doi):
    dang_nhap_voi("QUAN_LY")
    r = client.put(f"/api/cau-hinh/{ma}", json={"gia_tri": gia_tri})
    assert r.status_code == mong_doi
    if mong_doi == 400:
        assert r.json()["ma"] == "CAU_HINH_SAI"
        assert ma in r.json()["thong_diep"]


def test_uc07_ac7_ghi_nguoi_sua_va_thoi_diem(client, dang_nhap_voi, db):
    ql = dang_nhap_voi("QUAN_LY")
    ds = client.put("/api/cau-hinh/CFG-08", json={"gia_tri": " 25 "}).json()
    cfg08 = next(ts for ts in ds if ts["ma"] == "CFG-08")
    assert cfg08["gia_tri"] == "25"
    assert cfg08["nguoi_sua"] == ql.ho_ten
    dong = db.get(CauHinh, "CFG-08")
    db.refresh(dong)
    assert dong.nguoi_sua == ql.id
    assert dong.luc is not None


# AC8 – chỉ Quản lý
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "TAI_XE"])
def test_uc07_ac8_chi_quan_ly(client, dang_nhap_voi, db, vai_tro):
    bg = gia(db, "TP.HCM", "Cần Thơ", 1500, date(2026, 10, 1))
    dang_nhap_voi(vai_tro)
    assert client.get("/api/bang-gia").status_code == 403
    assert them(client).status_code == 403
    assert client.patch(f"/api/bang-gia/{bg.id}", json={"don_gia_kg": 1}).status_code == 403
    assert client.get("/api/cau-hinh").status_code == 403
    assert client.put("/api/cau-hinh/CFG-08", json={"gia_tri": "1"}).status_code == 403


def test_uc07_ac8_chua_dang_nhap(client):
    assert client.get("/api/bang-gia").status_code == 401
    assert client.get("/api/cau-hinh").status_code == 401


# Review UC-08 mục 1: cùng chữ, hai kiểu Unicode (tổ hợp NFD và dựng sẵn NFC) phải là một
def test_uc07_ac3_tinh_go_kieu_to_hop_van_khop(client, dang_nhap_voi, db):
    to_hop = unicodedata.normalize("NFD", "Cần Thơ")
    assert to_hop != "Cần Thơ"  # khác nhau từng byte dù nhìn giống hệt
    dang_nhap_voi("QUAN_LY")
    assert them(client, tinh_giao=to_hop).status_code == 201
    assert tra_gia(db, "TP.HCM", "Cần Thơ", date(2026, 10, 15)).don_gia_kg == 1500
    assert them(client, tinh_giao="Cần Thơ").status_code == 409  # trùng sau khi chuẩn hóa
