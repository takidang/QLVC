import unicodedata
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import BangGia, Chuyen, DonHang, KhachHang, Nut, TaiXe, TuyenNut, Xe
from app.thoi_gian import bay_gio


@pytest.fixture
def nut(db):
    """5 nút của tuyến T01 kịch bản mục 11."""
    ds = {
        ten: Nut(ten=ten, tinh=ten, loai="TINH") for ten in ("TP.HCM", "Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ")
    }
    db.add_all(ds.values())
    db.commit()
    return {k: v.id for k, v in ds.items()}


def t01(id_nut, **doi):
    return {
        "ma": "T01",
        "ten": "TP.HCM → Cần Thơ",
        "dm_dau": 550000,
        "dm_cau_duong": 200000,
        "dm_boc_xep": 250000,
        "dm_luong_tai_xe": 600000,
        "nut": [
            {"nut_id": id_nut["TP.HCM"], "phut_tu_diem_dau": 0, "km_tu_diem_dau": 0},
            {"nut_id": id_nut["Long An"], "phut_tu_diem_dau": 60, "km_tu_diem_dau": 50},
            {"nut_id": id_nut["Tiền Giang"], "phut_tu_diem_dau": 120, "km_tu_diem_dau": 75, "la_diem_nghi": True},
            {"nut_id": id_nut["Vĩnh Long"], "phut_tu_diem_dau": 210, "km_tu_diem_dau": 135},
            {"nut_id": id_nut["Cần Thơ"], "phut_tu_diem_dau": 270, "km_tu_diem_dau": 170},
        ],
    } | doi


# AC1 – nút
def test_uc05_ac1_them_nut(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    to_hop = unicodedata.normalize("NFD", "  Cần Thơ ")
    r = client.post(
        "/api/nut", json={"ten": "Kho Cần Thơ", "tinh": to_hop, "loai": "KHO", "lat": "10.03", "lng": "105.78"}
    )
    assert r.status_code == 201
    assert r.json()["tinh"] == "Cần Thơ"  # bỏ khoảng trắng, đưa về NFC
    assert client.post("/api/nut", json={"ten": "X", "tinh": "Y", "loai": "BEN_XE"}).status_code == 400
    assert client.post("/api/nut", json={"ten": "X", "tinh": "Y", "loai": "TINH", "lat": "91"}).status_code == 400
    client.post("/api/nut", json={"ten": "TP.HCM", "tinh": "TP.HCM", "loai": "TINH"})
    assert client.get("/api/nut", params={"tim": "cần"}).json()["tong"] == 1
    assert client.get("/api/nut").json()["tong"] == 2


# AC2 – sửa nút, không đổi tỉnh khi đã có đơn
def test_uc05_ac2_sua_nut_va_khoa_tinh_khi_co_don(client, dang_nhap_voi, db, nut):
    dang_nhap_voi("DIEU_PHOI")
    assert client.patch(f"/api/nut/{nut['Long An']}", json={"ten": "Long An (Tân An)"}).status_code == 200
    assert client.patch(f"/api/nut/{nut['Long An']}", json={"tinh": "Tây Ninh"}).json()["tinh"] == "Tây Ninh"
    assert client.patch(f"/api/nut/{nut['Long An']}", json={"ten": None}).status_code == 400

    kh = KhachHang(ten="Cty A", sdt="0901116789")
    db.add_all(
        [
            kh,
            BangGia(
                tinh_lay="TP.HCM", tinh_giao="Cần Thơ", don_gia_kg=1, cuoc_toi_thieu=0, hieu_luc_tu=date(2026, 1, 1)
            ),
        ]
    )
    db.commit()
    db.add(
        DonHang(
            ma_don="DH-TEST01",
            khach_hang_id=kh.id,
            kg=Decimal(1),
            m3=Decimal(1),
            so_kien=1,
            nut_lay_id=nut["TP.HCM"],
            dia_chi_lay="a",
            sdt_lay="0901116789",
            nut_giao_id=nut["Cần Thơ"],
            dia_chi_giao="b",
            nguoi_nhan="c",
            sdt_nhan="0901116789",
            han_giao=bay_gio() + timedelta(days=1),
            don_gia_chot=1,
            cuoc_toi_thieu_chot=0,
            he_so_quy_doi_chot=333,
            lam_tron_chot=1000,
            kl_tinh_cuoc=Decimal(333),
            cuoc_tinh=1000,
        )
    )
    db.commit()
    r = client.patch(f"/api/nut/{nut['Cần Thơ']}", json={"tinh": "Hậu Giang"})
    assert r.status_code == 422
    assert r.json()["ma"] == "NUT_DA_CO_DON"
    assert (
        client.patch(f"/api/nut/{nut['Cần Thơ']}", json={"ten": "Cần Thơ (bến xe)"}).status_code == 200
    )  # tên vẫn sửa được
    assert client.patch("/api/nut/999", json={"ten": "x"}).status_code == 404


# AC6 – thêm tuyến
def test_uc05_ac6_them_tuyen_t01(client, dang_nhap_voi, nut):
    dang_nhap_voi("DIEU_PHOI")
    r = client.post("/api/tuyen", json=t01(nut))
    assert r.status_code == 201
    t = r.json()
    assert [n["ten"] for n in t["nut"]] == ["TP.HCM", "Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ"]
    assert [n["thu_tu"] for n in t["nut"]] == [1, 2, 3, 4, 5]
    assert (t["tong_phut"], t["tong_km"], t["canh_bao"], t["trang_thai"]) == (270, 170, [], "HOAT_DONG")
    assert t["nut"][2]["la_diem_nghi"] is True


def test_uc05_ac6_canh_bao_br20_van_luu(client, dang_nhap_voi, nut):
    dang_nhap_voi("DIEU_PHOI")
    vao = t01(
        nut,
        nut=[
            {"nut_id": nut["TP.HCM"], "phut_tu_diem_dau": 0, "km_tu_diem_dau": 0},
            {"nut_id": nut["Cần Thơ"], "phut_tu_diem_dau": 300, "km_tu_diem_dau": 170},
        ],
    )
    r = client.post("/api/tuyen", json=vao)
    assert r.status_code == 201
    assert len(r.json()["canh_bao"]) == 1


@pytest.mark.parametrize(
    ("doi", "ma_http", "ma_loi"),
    [
        ({"dm_dau": -1}, 400, None),
        ({"dm_luong_tai_xe": -1}, 400, None),
        ({"nut": []}, 422, "TUYEN_SAI"),
    ],
)
def test_uc05_ac6_du_lieu_sai(client, dang_nhap_voi, nut, doi, ma_http, ma_loi):
    dang_nhap_voi("DIEU_PHOI")
    r = client.post("/api/tuyen", json=t01(nut, **doi))
    assert r.status_code == ma_http
    if ma_loi:
        assert r.json()["ma"] == ma_loi


def test_uc05_ac6_br66_va_trung_ma_va_nut_khong_co(client, dang_nhap_voi, db, nut):
    dang_nhap_voi("DIEU_PHOI")
    dai = t01(
        nut,
        ma="T99",
        nut=[
            {"nut_id": nut["TP.HCM"], "phut_tu_diem_dau": 0, "km_tu_diem_dau": 0},
            {"nut_id": nut["Cần Thơ"], "phut_tu_diem_dau": 601, "km_tu_diem_dau": 600, "la_diem_nghi": True},
        ],
    )
    r = client.post("/api/tuyen", json=dai)
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-66"

    assert client.post("/api/tuyen", json=t01(nut)).status_code == 201
    r = client.post("/api/tuyen", json=t01(nut, ten="khác"))
    assert r.status_code == 409
    assert r.json()["ma"] == "MA_TUYEN_TRUNG"

    sai_nut = t01(nut, ma="T02")
    sai_nut["nut"][1]["nut_id"] = 999
    assert client.post("/api/tuyen", json=sai_nut).status_code == 404
    assert db.scalar(select(TuyenNut.tuyen_id).where(TuyenNut.tuyen_id != 1)) is None  # tuyến lỗi không để lại nút


def test_uc05_ac4_br66_theo_cfg07_qua_api(client, dang_nhap_voi, nut):
    dang_nhap_voi("QUAN_LY")
    client.put("/api/cau-hinh/CFG-07", json={"gia_tri": "9/48/4"})
    vao = t01(
        nut,
        nut=[
            {"nut_id": nut["TP.HCM"], "phut_tu_diem_dau": 0, "km_tu_diem_dau": 0},
            {"nut_id": nut["Tiền Giang"], "phut_tu_diem_dau": 240, "km_tu_diem_dau": 100, "la_diem_nghi": True},
            {"nut_id": nut["Cần Thơ"], "phut_tu_diem_dau": 600, "km_tu_diem_dau": 300},
        ],
    )
    assert client.post("/api/tuyen", json=vao).json()["ma"] == "BR-66"


# AC7 – sửa tuyến
def test_uc05_ac7_sua_tuyen_chua_co_chuyen(client, dang_nhap_voi, nut):
    dang_nhap_voi("DIEU_PHOI")
    tid = client.post("/api/tuyen", json=t01(nut)).json()["id"]
    r = client.patch(f"/api/tuyen/{tid}", json={"dm_dau": 600000, "trang_thai": "NGUNG"})
    assert (r.json()["dm_dau"], r.json()["trang_thai"]) == (600000, "NGUNG")
    nut_moi = t01(nut)["nut"][:3]
    r = client.patch(f"/api/tuyen/{tid}", json={"nut": nut_moi})
    assert r.status_code == 200
    assert (len(r.json()["nut"]), r.json()["tong_phut"]) == (3, 120)
    assert (
        client.patch(
            f"/api/tuyen/{tid}", json={"nut": [{"nut_id": nut["TP.HCM"], "phut_tu_diem_dau": 5, "km_tu_diem_dau": 0}]}
        ).status_code
        == 422
    )
    assert client.patch(f"/api/tuyen/{tid}", json={"ten": None}).status_code == 400
    assert client.delete(f"/api/tuyen/{tid}").status_code == 405
    assert client.patch("/api/tuyen/999", json={"ten": "x"}).status_code == 404


@pytest.mark.parametrize(("trang_thai_chuyen", "doi_duoc"), [("LAP", False), ("HUY", True)])
def test_uc05_ac7_tuyen_da_co_chuyen_khong_doi_nut(
    client, dang_nhap_voi, db, nut, tao_nguoi_dung, trang_thai_chuyen, doi_duoc
):
    dp = dang_nhap_voi("DIEU_PHOI")
    tid = client.post("/api/tuyen", json=t01(nut)).json()["id"]
    xe = Xe(
        bien_so="51C-111.11",
        tai_trong_kg=5000,
        the_tich_m3=Decimal(20),
        ktt_toan_bo_kg=9500,
        han_dang_kiem=date(2027, 1, 1),
        han_bao_hiem=date(2027, 1, 1),
    )
    tx_nd = tao_nguoi_dung(ten="an", vai_tro="TAI_XE")
    tx = TaiXe(nguoi_dung_id=tx_nd.id, so_gplx="GPLX01", hang_gplx="C", han_gplx=date(2030, 1, 1), sdt="0909000111")
    db.add_all([xe, tx])
    db.commit()
    db.add(
        Chuyen(
            ma_chuyen="C01",
            tuyen_id=tid,
            xe_id=xe.id,
            tai_xe_id=tx.id,
            dieu_phoi_id=dp.id,
            khoi_hanh_du_kien=bay_gio(),
            ket_thuc_du_kien=bay_gio() + timedelta(hours=6),
            trang_thai=trang_thai_chuyen,
        )
    )
    db.commit()

    r = client.patch(f"/api/tuyen/{tid}", json={"nut": t01(nut)["nut"][:2]})
    assert r.status_code == (200 if doi_duoc else 409)
    if not doi_duoc:
        assert r.json()["ma"] == "TUYEN_DA_CO_CHUYEN"
        assert len(client.get(f"/api/tuyen/{tid}").json()["nut"]) == 5
        assert client.patch(f"/api/tuyen/{tid}", json={"dm_dau": 1}).status_code == 200  # định mức vẫn sửa được


# AC8 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc05_ac8_phan_quyen(client, dang_nhap_voi, nut, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/nut").status_code == ma
    assert client.get("/api/tuyen").status_code == ma
    assert client.post("/api/tuyen", json=t01(nut)).status_code == (201 if ma == 200 else 403)
    assert client.post("/api/nut", json={"ten": "Kho", "tinh": "X", "loai": "KHO"}).status_code == (
        201 if ma == 200 else 403
    )


def test_uc05_ac8_chua_dang_nhap(client):
    assert client.get("/api/nut").status_code == 401
    assert client.get("/api/tuyen").status_code == 401
