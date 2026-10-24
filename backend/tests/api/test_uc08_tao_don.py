import re
import unicodedata
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models import BangGia, DonHang, KhachHang, LichSuTrangThai, Nut
from app.modules.don.service import KY_TU_MA
from app.thoi_gian import bay_gio


@pytest.fixture
def kich_ban(db):
    """Dữ liệu kịch bản mục 11: nút, bảng giá, khách (nghiep-vu.md)."""
    nut = {ten: Nut(ten=ten, tinh=ten, loai="TINH") for ten in ("TP.HCM", "Long An", "Vĩnh Long", "Cần Thơ", "Cà Mau")}
    db.add_all(nut.values())
    hom_qua = date.today() - timedelta(days=30)
    for lay, giao, gia in [("TP.HCM", "Cần Thơ", 1500), ("Long An", "Cần Thơ", 1200), ("TP.HCM", "Vĩnh Long", 1300)]:
        db.add(BangGia(tinh_lay=lay, tinh_giao=giao, don_gia_kg=gia, cuoc_toi_thieu=50000, hieu_luc_tu=hom_qua))
    kh = KhachHang(ten="Cty A", sdt="0901116789")
    ngung = KhachHang(ten="Cty Ngừng", sdt="0902220000", trang_thai="NGUNG")
    db.add_all([kh, ngung])
    db.commit()
    return {"nut": {k: v.id for k, v in nut.items()}, "kh": kh.id, "kh_ngung": ngung.id}


def han(gio=24):
    return (bay_gio() + timedelta(hours=gio)).isoformat()


def don_d1(kb, **doi):
    """Đ1: HCM → Cần Thơ, 1.800 kg, 6 m³."""
    return {
        "khach_hang_id": kb["kh"],
        "mo_ta": "Hàng gia dụng",
        "kg": "1800",
        "m3": "6",
        "so_kien": 12,
        "nut_lay_id": kb["nut"]["TP.HCM"],
        "dia_chi_lay": "12 Nguyễn Huệ, Q.1",
        "sdt_lay": "0901116789",
        "nut_giao_id": kb["nut"]["Cần Thơ"],
        "dia_chi_giao": "5 Hòa Bình, Ninh Kiều",
        "nguoi_nhan": "Chị Lan",
        "sdt_nhan": "0907778888",
        "han_giao": han(),
    } | doi


def tao(client, vao):
    return client.post("/api/don", json=vao)


# AC2 – tính thử, không lưu
def test_uc08_ac2_tinh_cuoc_khong_luu(client, dang_nhap_voi, db, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    vao = {
        "nut_lay_id": kich_ban["nut"]["TP.HCM"],
        "nut_giao_id": kich_ban["nut"]["Vĩnh Long"],
        "kg": "1500",
        "m3": "5",
    }
    r = client.post("/api/don/tinh-cuoc", json=vao)
    assert r.status_code == 200
    bg = r.json()
    assert (Decimal(bg["kl_quy_doi"]), Decimal(bg["kl_tinh_cuoc"])) == (1665, 1665)
    assert (bg["don_gia_kg"], bg["cuoc_toi_thieu"], bg["cuoc"]) == (1300, 50000, 2_165_000)
    assert db.scalar(select(func.count()).select_from(DonHang)) == 0


def test_uc08_ac2_tinh_cuoc_chua_co_gia(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    vao = {"nut_lay_id": kich_ban["nut"]["Cần Thơ"], "nut_giao_id": kich_ban["nut"]["Cà Mau"], "kg": "1", "m3": "1"}
    r = client.post("/api/don/tinh-cuoc", json=vao)
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-48"


# AC3 – tạo đơn, chốt cước, mã đơn, lịch sử
def test_uc08_ac3_tao_don_chot_cuoc(client, dang_nhap_voi, db, kich_ban):
    dp = dang_nhap_voi("DIEU_PHOI")
    r = tao(client, don_d1(kich_ban))
    assert r.status_code == 201
    d = r.json()
    assert d["trang_thai"] == "CHO_GHEP"
    assert d["cuoc_tinh"] == 2_997_000
    assert d["kl_tinh_cuoc"] == "1998.00"
    assert (d["ten_khach"], d["tinh_lay"], d["tinh_giao"]) == ("Cty A", "TP.HCM", "Cần Thơ")
    assert re.fullmatch(rf"DH-[{KY_TU_MA}]{{6}}", d["ma_don"])

    don = db.get(DonHang, d["id"])
    assert (don.don_gia_chot, don.cuoc_toi_thieu_chot, don.he_so_quy_doi_chot, don.lam_tron_chot) == (
        1500,
        50000,
        333,
        1000,
    )
    ls = db.scalars(select(LichSuTrangThai)).all()
    assert [(x.doi_tuong, x.doi_tuong_id, x.tu, x.sang, x.nguoi) for x in ls] == [
        ("DON", don.id, None, "CHO_GHEP", dp.id)
    ]


def test_uc08_ac3_ma_don_khac_nhau(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    ma = {tao(client, don_d1(kich_ban)).json()["ma_don"] for _ in range(5)}
    assert len(ma) == 5


# AC4 – BR-31
@pytest.mark.parametrize(
    ("doi", "mong_doi"),
    [
        ({"kg": "0"}, 400),
        ({"kg": "0.01"}, 201),
        ({"m3": "0"}, 400),
        ({"m3": "0.01"}, 201),
        ({"so_kien": 0}, 400),
        ({"so_kien": 1}, 201),
        ({"dia_chi_giao": " 12 nguyễn huệ,  Q.1 "}, 422),
        ({"han_giao": han(-1)}, 422),
        ({"lay_tu": han(1)}, 422),  # chỉ có một đầu khung giờ
        ({"lay_tu": han(3), "lay_den": han(2)}, 422),  # từ sau đến
        ({"lay_tu": han(30), "lay_den": han(31)}, 422),  # hạn giao (24 giờ) trước giờ bắt đầu lấy
        ({"lay_tu": han(1), "lay_den": han(3)}, 201),
    ],
)
def test_uc08_ac4_br31(client, dang_nhap_voi, db, kich_ban, doi, mong_doi):
    dang_nhap_voi("DIEU_PHOI")
    r = tao(client, don_d1(kich_ban, **doi))
    assert r.status_code == mong_doi
    if mong_doi == 422:
        assert r.json()["ma"] == "BR-31"
    assert db.scalar(select(func.count()).select_from(DonHang)) == (1 if mong_doi == 201 else 0)


def test_uc08_ac4_cung_nut_khac_dia_chi_duoc(client, dang_nhap_voi, db, kich_ban):
    # Tuyến nội thành một nút (A3): lấy và giao cùng nút, khác địa chỉ
    db.add(
        BangGia(tinh_lay="Cần Thơ", tinh_giao="Cần Thơ", don_gia_kg=500, cuoc_toi_thieu=0, hieu_luc_tu=date(2026, 1, 1))
    )
    db.commit()
    dang_nhap_voi("DIEU_PHOI")
    vao = don_d1(kich_ban, nut_lay_id=kich_ban["nut"]["Cần Thơ"], dia_chi_lay="1 Mậu Thân, Ninh Kiều")
    assert tao(client, vao).status_code == 201


# AC5 – khách, nút
def test_uc08_ac5_khach_va_nut(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    assert tao(client, don_d1(kich_ban, khach_hang_id=999)).status_code == 404
    assert tao(client, don_d1(kich_ban, nut_lay_id=999)).status_code == 404
    r = tao(client, don_d1(kich_ban, khach_hang_id=kich_ban["kh_ngung"]))
    assert r.status_code == 422
    assert r.json()["ma"] == "KHACH_NGUNG"


# AC6 – chưa có giá (Đ7)
def test_uc08_ac6_chua_co_gia_khong_tao(client, dang_nhap_voi, db, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    vao = don_d1(kich_ban, nut_lay_id=kich_ban["nut"]["Cần Thơ"], nut_giao_id=kich_ban["nut"]["Cà Mau"])
    r = tao(client, vao)
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-48"
    assert db.scalar(select(func.count()).select_from(DonHang)) == 0


# AC7 – đổi bảng giá, CFG sau khi tạo không ảnh hưởng đơn
def test_uc08_ac7_doi_gia_khong_anh_huong_don_cu(client, dang_nhap_voi, db, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    don_id = tao(client, don_d1(kich_ban)).json()["id"]
    db.add(BangGia(tinh_lay="TP.HCM", tinh_giao="Cần Thơ", don_gia_kg=9999, cuoc_toi_thieu=0, hieu_luc_tu=date.today()))
    db.commit()
    dang_nhap_voi("QUAN_LY")
    client.put("/api/cau-hinh/CFG-01", json={"gia_tri": "500"})
    client.put("/api/cau-hinh/CFG-06", json={"gia_tri": "5000"})

    d = client.get(f"/api/don/{don_id}").json()
    assert d["cuoc_tinh"] == 2_997_000
    don = db.get(DonHang, don_id)
    db.refresh(don)
    assert (don.don_gia_chot, don.he_so_quy_doi_chot, don.lam_tron_chot) == (1500, 333, 1000)
    # đơn mới dùng giá và CFG mới
    moi = tao(client, don_d1(kich_ban)).json()
    assert moi["cuoc_tinh"] == 30_000_000  # 3.000 kg quy đổi × 9.999 = 29.997.000 → bội 5.000


# AC8 – SĐT, múi giờ
def test_uc08_ac8_sdt_va_mui_gio(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    d = tao(client, don_d1(kich_ban, sdt_nhan="0907 778.888")).json()
    assert d["sdt_nhan"] == "0907778888"
    assert tao(client, don_d1(kich_ban, sdt_lay="123")).status_code == 400
    assert tao(client, don_d1(kich_ban, han_giao="2030-01-01T10:00:00")).status_code == 400  # thiếu múi giờ


# AC9 – danh sách, chi tiết
def test_uc08_ac9_danh_sach_va_chi_tiet(client, dang_nhap_voi, db, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    a = tao(client, don_d1(kich_ban)).json()
    tao(client, don_d1(kich_ban, kg="10"))
    khac = KhachHang(ten="Cty B", sdt="0903330000")
    db.add(khac)
    db.commit()
    tao(client, don_d1(kich_ban, khach_hang_id=khac.id))

    assert client.get("/api/don").json()["tong"] == 3
    assert client.get("/api/don", params={"khach_hang_id": kich_ban["kh"]}).json()["tong"] == 2
    assert client.get("/api/don", params={"trang_thai": "CHO_GHEP"}).json()["tong"] == 3
    assert client.get("/api/don", params={"trang_thai": "DA_GIAO"}).json()["tong"] == 0
    tim = client.get("/api/don", params={"tim": a["ma_don"][3:].lower()}).json()
    assert [d["id"] for d in tim["du_lieu"]] == [a["id"]]
    assert len(client.get("/api/don", params={"so_dong": 2}).json()["du_lieu"]) == 2
    assert client.get("/api/don", params={"trang_thai": "MOI"}).status_code == 400  # MOI bỏ ở 0.5
    assert client.get(f"/api/don/{a['id']}").json()["kg"] == "1800.00"
    assert client.get("/api/don/999").status_code == 404


# AC10 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "tao_ma", "xem_ma"),
    [("DIEU_PHOI", 201, 200), ("QUAN_LY", 201, 200), ("KE_TOAN", 403, 200), ("TAI_XE", 403, 403)],
)
def test_uc08_ac10_phan_quyen(client, dang_nhap_voi, kich_ban, vai_tro, tao_ma, xem_ma):
    dang_nhap_voi(vai_tro)
    assert tao(client, don_d1(kich_ban)).status_code == tao_ma
    assert client.get("/api/don").status_code == xem_ma
    vao = {"nut_lay_id": kich_ban["nut"]["TP.HCM"], "nut_giao_id": kich_ban["nut"]["Cần Thơ"], "kg": "1", "m3": "1"}
    assert client.post("/api/don/tinh-cuoc", json=vao).status_code == (200 if tao_ma == 201 else 403)


def test_uc08_ac10_chua_dang_nhap(client):
    assert client.get("/api/don").status_code == 401
    assert client.post("/api/don", json={}).status_code in (400, 401)


def test_uc08_review_vi_do_ngoai_khoang_bi_chan(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    assert tao(client, don_d1(kich_ban, lat_lay="120", lng_lay="105")).status_code == 400
    assert tao(client, don_d1(kich_ban, lat_lay="10.03", lng_lay="105.78")).status_code == 201


def test_uc08_review_dia_chi_khac_kieu_unicode_van_la_trung(client, dang_nhap_voi, kich_ban):
    dang_nhap_voi("DIEU_PHOI")
    vao = don_d1(kich_ban, dia_chi_giao=unicodedata.normalize("NFD", "12 Nguyễn Huệ, Q.1"))
    assert tao(client, vao).json()["ma"] == "BR-31"
