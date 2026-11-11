# ruff: noqa: F811  (kb, dang_chay là fixture nhập từ test UC-13, UC-32, dùng làm tham số)
"""UC-27 Bảng cảnh báo. Chuyến trễ dùng kịch bản mục 11: quét lấy Đ2 trễ 30′ → kết thúc 14:00 chồng C00 13:45."""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import text

from app.models import Chuyen, DonHang, LuotQuet, SuCo, TaiXe, Xe
from app.modules.canh_bao import service
from app.thoi_gian import GIO_VN, hom_nay_vn
from tests.api.test_uc13_ghep_don import kb, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import sua
from tests.api.test_uc32_theo_doi_chuyen import chuyen_ke_tiep, dang_chay, ghep_cua, quet  # noqa: F401

URL = "/api/canh-bao"
NHOM = ("giay_to", "chuyen_tre", "su_co_mo", "don_sap_qua_han", "thieu_gps")


def xem(client) -> dict:
    r = client.get(URL)
    assert r.status_code == 200, r.text
    return r.json()


def dat_cfg(db, ma, gia_tri):
    db.execute(text("UPDATE cau_hinh SET gia_tri = :g WHERE ma = :m"), {"g": gia_tri, "m": ma})
    db.commit()


# AC1 – giấy tờ sắp / đã hết hạn (BR-21, CFG-02 tính cả ngày thứ 30)
def test_uc27_ac1_giay_to(client, db, dang_nhap_voi, tao_nguoi_dung):
    dang_nhap_voi("DIEU_PHOI")
    nay = hom_nay_vn()
    xa = nay + timedelta(days=400)

    def xe(bien_so, dang_kiem=xa, bao_hiem=xa, trang_thai="HOAT_DONG"):
        db.add(
            Xe(
                bien_so=bien_so,
                tai_trong_kg=5000,
                the_tich_m3=20,
                ktt_toan_bo_kg=9500,
                han_dang_kiem=dang_kiem,
                han_bao_hiem=bao_hiem,
                trang_thai=trang_thai,
            )
        )

    def tai_xe(ten, han, trang_thai="HOAT_DONG"):
        nd = tao_nguoi_dung(ten=ten, vai_tro="TAI_XE")
        db.add(
            TaiXe(
                nguoi_dung_id=nd.id,
                so_gplx=f"G{nd.id}",
                hang_gplx="C",
                han_gplx=han,
                sdt="0909000000",
                trang_thai=trang_thai,
            )
        )

    xe("51C-030.00", dang_kiem=nay + timedelta(days=30))  # biên: ngày thứ 30 có
    xe("51C-031.00", dang_kiem=nay + timedelta(days=31))  # ngày thứ 31 không
    xe("51C-011.00", bao_hiem=nay + timedelta(days=11))
    xe("51C-HQ.00", dang_kiem=nay - timedelta(days=1))  # đã hết hạn
    xe("51C-NG.00", dang_kiem=nay - timedelta(days=5), trang_thai="NGUNG")  # xe ngừng không nhắc
    tai_xe("binh", nay + timedelta(days=3))
    tai_xe("cuong", nay, trang_thai="NGUNG")
    db.commit()

    g = xem(client)["giay_to"]
    assert [(x["ten"], x["loai"], x["con_ngay"], x["het_han"]) for x in g] == [
        ("51C-HQ.00", "DANG_KIEM", -1, True),
        ("Người binh", "GPLX", 3, False),
        ("51C-011.00", "BAO_HIEM", 11, False),
        ("51C-030.00", "DANG_KIEM", 30, False),
    ]
    assert g[0]["doi_tuong"] == "XE" and g[1]["doi_tuong"] == "TAI_XE"
    assert g[0]["han"] == (nay - timedelta(days=1)).isoformat()

    dat_cfg(db, "CFG-02", "10")  # đổi CFG-02: hạn + 11 ngày, + 30 ngày biến mất
    g = xem(client)["giay_to"]
    assert [x["ten"] for x in g] == ["51C-HQ.00", "Người binh"]


# AC2 – chuyến trễ, chồng chuyến kế tiếp (BR-73, CFG-09 = 15)
def test_uc27_ac2_chuyen_tre_chong_lich(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    c00 = chuyen_ke_tiep(db, kb, dang_chay["dp"], 13, 45)
    assert xem(client)["chuyen_tre"] == []  # đang chạy nhưng chưa trễ
    quet(db, kb, c01, "d2", "LAY", tre_phut=30)  # TC-BR73-02
    [t] = xem(client)["chuyen_tre"]
    assert (t["chuyen_id"], t["tre_phut"], t["chong"], t["bien_so"], t["ten_tai_xe"]) == (
        c01,
        30,
        [c00],
        "51C-111.11",
        "An",
    )
    assert datetime.fromisoformat(t["ket_thuc_dang_chay"]) == luc(14)


@pytest.mark.parametrize(("tre", "co"), [(15, False), (16, True)])
def test_uc27_ac2_bien_nguong_tre(client, db, kb, dang_chay, tre, co):
    quet(db, kb, dang_chay["c01"], "d4", "LAY", tre_phut=tre)  # không có chuyến kế tiếp: chỉ xét cờ trễ
    assert (len(xem(client)["chuyen_tre"]) == 1) is co


def test_uc27_ac2_chuyen_khong_dang_chay_khong_vao(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    quet(db, kb, c01, "d2", "LAY", tre_phut=40)
    sua(db, Chuyen, c01, trang_thai="HOAN_THANH")
    assert xem(client)["chuyen_tre"] == []


# AC3 – sự cố đang mở
def test_uc27_ac3_su_co_mo(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    mo = SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="HONG_XE", ghi_chu="Nổ lốp")
    dong = SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="TAI_NAN", ghi_chu="Quẹt nhẹ", trang_thai="DONG")
    db.add_all([mo, dong])
    db.commit()
    [s] = xem(client)["su_co_mo"]
    assert (s["su_co_id"], s["chuyen_id"], s["loai"], s["ghi_chu"], s["bien_so"], s["ten_tai_xe"]) == (
        mo.id,
        c01,
        "HONG_XE",
        "Nổ lốp",
        "51C-111.11",
        "An",
    )
    assert s["ma_chuyen"] and s["luc"]
    sua(db, SuCo, mo.id, trang_thai="DONG")
    assert xem(client)["su_co_mo"] == []


# AC4 – đơn chờ ghép còn dưới CFG-10 (24) giờ tới hạn giao
def test_uc27_ac4_don_sap_qua_han(client, db, kb, dang_nhap_voi, monkeypatch):
    dang_nhap_voi("DIEU_PHOI")
    nay = datetime(2030, 10, 20, 8, 0, tzinfo=GIO_VN)
    monkeypatch.setattr(service, "bay_gio", lambda: nay)
    han = {
        "d1": nay + timedelta(hours=23, minutes=59),  # có
        "d2": nay + timedelta(hours=24),  # đúng 24 giờ: chưa báo
        "d4": nay - timedelta(hours=2),  # đã quá hạn: có
        "d5": nay + timedelta(hours=1),  # nhưng DA_GHEP: không
        "d6": nay + timedelta(hours=1),  # nhưng HUY: không
    }
    for k, h in han.items():
        sua(db, DonHang, kb[k], han_giao=h, trang_thai={"d5": "DA_GHEP", "d6": "HUY"}.get(k, "CHO_GHEP"))
    ds = xem(client)["don_sap_qua_han"]
    assert [(d["don_id"], d["con_phut"], d["qua_han"]) for d in ds] == [
        (kb["d4"], -120, True),
        (kb["d1"], 23 * 60 + 59, False),
    ]
    d1 = ds[1]
    assert (d1["ma_don"], d1["ten_khach"], d1["tinh_lay"], d1["tinh_giao"]) == ("DH-0001", "Cty A", "TP.HCM", "Cần Thơ")


# AC5 – lượt quét thiếu GPS (BR-43)
def test_uc27_ac5_thieu_gps(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    for don, gps in (("d1", False), ("d4", False), ("d2", True)):
        g = ghep_cua(db, c01, kb[don])
        db.add(LuotQuet(ghep_id=g.id, tai_xe_id=kb["an"], loai="LAY", thieu_gps=not gps))
    db.commit()
    [t] = xem(client)["thieu_gps"]
    assert (t["chuyen_id"], t["so_luot"], t["ten_tai_xe"]) == (c01, 2, "An")
    assert t["ma_chuyen"] and t["luc_gan_nhat"]

    nay = datetime.now(GIO_VN)
    sua(db, Chuyen, c01, trang_thai="HOAN_THANH", ket_thuc_thuc_te=nay - timedelta(hours=23))
    assert len(xem(client)["thieu_gps"]) == 1  # vừa kết thúc trong 24 giờ: vẫn nhắc
    sua(db, Chuyen, c01, ket_thuc_thuc_te=nay - timedelta(hours=25))
    assert xem(client)["thieu_gps"] == []


# AC6 – cấu hình, tổng số việc, rỗng, tham số lạ
def test_uc27_ac6_cau_hinh_so_viec(client, db, kb, dang_chay):
    j = xem(client)
    assert j["cau_hinh"] == {"ngay_bao_truoc": 30, "nguong_tre_phut": 15, "gio_cho_ghep": 24}
    assert j["so_viec"] == 0 and all(j[k] == [] for k in NHOM)
    dat_cfg(db, "CFG-09", "40")
    db.add(SuCo(chuyen_id=dang_chay["c01"], tai_xe_id=kb["an"], loai="KHAC", ghi_chu="x"))
    db.commit()
    quet(db, kb, dang_chay["c01"], "d2", "LAY", tre_phut=30)  # 30 ≤ CFG-09 mới (40): không trễ
    j = xem(client)
    assert j["cau_hinh"]["nguong_tre_phut"] == 40
    assert (len(j["su_co_mo"]), j["chuyen_tre"], j["so_viec"]) == (1, [], sum(len(j[k]) for k in NHOM))
    r = client.get(URL, params={"ngay": date(2030, 10, 22).isoformat()})
    assert (r.status_code, r.json()["ma"]) == (400, "DU_LIEU_KHONG_HOP_LE")


# AC7 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc27_ac7_phan_quyen(client, dang_nhap_voi, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get(URL).status_code == ma


def test_uc27_ac7_chua_dang_nhap_401(client):
    assert client.get(URL).status_code == 401
