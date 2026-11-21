# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-25 Công nợ. Kịch bản mục 11 bước 8: Cty B nợ Đ2 (1.440.000) + Đ4 (800.000), đánh dấu đã thu một lần."""

import threading
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models import DonHang, Ghep, KhachHang, LuotQuet, NhatKyTien, PhaiThu, PhieuThu
from app.thoi_gian import bay_gio, hom_nay_vn
from tests.api.test_uc17_xem_chuyen import kb  # noqa: F401 (kb là fixture)


@pytest.fixture
def cn(db, kb, dang_nhap_voi):
    """Cty A (khách của kb) có Đ1; Cty B có Đ2, Đ4. Cả ba DA_GIAO, sinh phải thu như UC-20. Đăng nhập Kế toán."""
    cty_b = KhachHang(ten="Cty B", sdt="0902223333")
    db.add(cty_b)
    db.flush()
    kb["d2"].khach_hang_id = kb["d4"].khach_hang_id = cty_b.id
    tien = {"d1": 2_997_000, "d2": 1_440_000, "d4": 800_000}
    pt = {}
    for i, (k, so) in enumerate(tien.items()):
        d = kb[k]
        d.trang_thai, d.cuoc_tinh = "DA_GIAO", so
        g = db.scalar(select(Ghep).where(Ghep.don_hang_id == d.id))
        db.add(
            LuotQuet(
                ghep_id=g.id,
                tai_xe_id=kb["an"].id,
                loai="GIAO",
                thieu_gps=True,
                thoi_gian=bay_gio() - timedelta(hours=3 - i),
            )
        )
        pt[k] = PhaiThu(don_hang_id=d.id, so_tien=so)
        db.add(pt[k])
    db.commit()
    kt = dang_nhap_voi("KE_TOAN")
    return kb | {"cty_a": kb["d1"].khach_hang_id, "cty_b": cty_b.id, "pt": {k: v.id for k, v in pt.items()}, "kt": kt}


def da_thu(client, ids, ngay=None, **them):
    return client.post(
        "/api/phai-thu/da-thu", json={"phai_thu_ids": ids, "ngay": ngay or hom_nay_vn().isoformat(), **them}
    )


def ma(r) -> tuple[int, str | None]:
    return r.status_code, r.json().get("ma")


def trang_thai(db, *pt_ids) -> list[str]:
    db.expire_all()
    return [db.get(PhaiThu, i).trang_thai_tt for i in pt_ids]


def nhat_ky(db) -> list[NhatKyTien]:
    db.expire_all()
    return list(db.scalars(select(NhatKyTien).where(NhatKyTien.bang == "phai_thu").order_by(NhatKyTien.id)))


def so_phieu(db) -> int:
    return db.scalar(select(func.count()).select_from(PhieuThu))


# AC1 – đánh dấu nhiều khoản một lần (TC-BR56-02)
def test_uc25_ac1_thu_hai_khoan_mot_lan(client, db, cn):
    d2, d4 = cn["pt"]["d2"], cn["pt"]["d4"]
    r = da_thu(client, [d2, d4])
    assert r.status_code == 200, r.text
    j = r.json()
    assert (j["tong_tien"], j["so_khoan"], j["khach_hang_id"], j["ngay"]) == (
        2_240_000,
        2,
        cn["cty_b"],
        hom_nay_vn().isoformat(),
    )
    db.expire_all()
    phieu = db.get(PhieuThu, j["phieu_thu_id"])
    assert (phieu.tong_tien, phieu.khach_hang_id, phieu.nguoi_tao) == (2_240_000, cn["cty_b"], cn["kt"].id)
    assert {(p.trang_thai_tt, p.phieu_thu_id) for p in (db.get(PhaiThu, d2), db.get(PhaiThu, d4))} == {
        ("DA_THU", phieu.id)
    }
    assert [db.get(DonHang, cn[k].id).trang_thai for k in ("d2", "d4")] == ["DA_GIAO", "DA_GIAO"]
    assert trang_thai(db, cn["pt"]["d1"]) == ["CHUA_THU"]


# AC2 – nhật ký tiền
def test_uc25_ac2_nhat_ky(client, db, cn):
    phieu = da_thu(client, [cn["pt"]["d2"], cn["pt"]["d4"]]).json()["phieu_thu_id"]
    dong = nhat_ky(db)
    assert [(n.ban_ghi_id, n.hanh_dong, n.gia_tri_cu, n.gia_tri_moi, n.nguoi) for n in dong] == [
        (cn["pt"]["d2"], "DA_THU", "CHUA_THU", "DA_THU", cn["kt"].id),
        (cn["pt"]["d4"], "DA_THU", "CHUA_THU", "DA_THU", cn["kt"].id),
    ]
    assert all(f"#{phieu}" in n.ly_do and n.luc is not None for n in dong)


# AC3 – một khoản; lô có khoản đã thu
def test_uc25_ac3_mot_khoan_va_da_thu(client, db, cn):
    assert da_thu(client, [cn["pt"]["d4"]]).status_code == 200
    r = da_thu(client, [cn["pt"]["d2"], cn["pt"]["d4"]])
    assert ma(r) == (409, "BR-56")
    assert cn["d4"].ma_don in r.json()["thong_diep"]
    assert trang_thai(db, cn["pt"]["d2"], cn["pt"]["d4"]) == ["CHUA_THU", "DA_THU"]
    assert so_phieu(db) == 1 and len(nhat_ky(db)) == 1


# AC4 – khác khách
def test_uc25_ac4_khac_khach(client, db, cn):
    assert ma(da_thu(client, [cn["pt"]["d1"], cn["pt"]["d2"]])) == (422, "BR-56")
    assert trang_thai(db, *cn["pt"].values()) == ["CHUA_THU"] * 3
    assert so_phieu(db) == 0


# AC5 – dữ liệu sai, biên ngày
@pytest.mark.parametrize(
    "body",
    [
        {"phai_thu_ids": []},
        {"phai_thu_ids": list(range(1, 102))},
        {"phai_thu_ids": ["1"]},
        {"phai_thu_ids": [1.5]},
        {"ngay": "09/11/2026"},
        {"ngay": "2026-11-09T10:00:00"},
        {"ngay": 20261109},
        {"ghi_chu": "x"},
        {"ngay": None},
    ],
)
def test_uc25_ac5_du_lieu_sai(client, db, cn, body):
    r = client.post(
        "/api/phai-thu/da-thu", json={"phai_thu_ids": [cn["pt"]["d4"]], "ngay": hom_nay_vn().isoformat()} | body
    )
    assert r.status_code == 400, r.text
    assert trang_thai(db, cn["pt"]["d4"]) == ["CHUA_THU"] and so_phieu(db) == 0


def test_uc25_ac5_id_trung_va_ngay_mai(client, db, cn):
    d4 = cn["pt"]["d4"]
    assert da_thu(client, [d4, d4]).status_code == 400
    assert da_thu(client, [d4], (hom_nay_vn() + timedelta(days=1)).isoformat()).status_code == 400
    assert so_phieu(db) == 0
    assert da_thu(client, [d4], (hom_nay_vn() - timedelta(days=1)).isoformat()).status_code == 200  # nhập muộn được


def test_uc25_ac5_khong_tim_thay(client, db, cn):
    assert ma(da_thu(client, [cn["pt"]["d4"], 999999])) == (404, "KHONG_TIM_THAY")
    assert trang_thai(db, cn["pt"]["d4"]) == ["CHUA_THU"]


# AC6 – hai Kế toán cùng đánh dấu
def test_uc25_ac6_dong_thoi(client, db, cn):
    ket_qua: list = []
    cho = threading.Barrier(2)

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "ke_toan", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua.append(da_thu(c, [cn["pt"]["d2"], cn["pt"]["d4"]]))

    luong = [threading.Thread(target=gui) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [200, 409]
    assert so_phieu(db) == 1 and len(nhat_ky(db)) == 2


# AC7 – danh sách, lọc
def test_uc25_ac7_danh_sach(client, db, cn):
    phieu = da_thu(client, [cn["pt"]["d4"]]).json()["phieu_thu_id"]

    def lay(**loc):
        r = client.get("/api/phai-thu", params=loc)
        assert r.status_code == 200, r.text
        return r.json()

    j = lay()
    assert (j["tong"], j["tong_tien"]) == (3, 5_237_000)
    assert [d["ma_don"] for d in j["du_lieu"]] == [cn[k].ma_don for k in ("d4", "d2", "d1")]  # giao mới trước
    d4 = j["du_lieu"][0]
    assert (d4["trang_thai_tt"], d4["phieu_thu_id"], d4["ngay_thu"], d4["ten_khach"]) == (
        "DA_THU",
        phieu,
        hom_nay_vn().isoformat(),
        "Cty B",
    )
    assert d4["ngay_giao"] is not None
    assert (lay(trang_thai_tt="CHUA_THU")["tong"], lay(trang_thai_tt="CHUA_THU")["tong_tien"]) == (2, 4_437_000)
    assert [d["ma_don"] for d in lay(khach_hang_id=cn["cty_b"])["du_lieu"]] == [cn["d4"].ma_don, cn["d2"].ma_don]
    assert lay(khach_hang_id=cn["cty_b"], trang_thai_tt="CHUA_THU")["tong_tien"] == 1_440_000
    assert [d["ma_don"] for d in lay(so_dong=1, trang=2)["du_lieu"]] == [cn["d2"].ma_don]
    assert client.get("/api/phai-thu", params={"trang_thai_tt": "XYZ"}).status_code == 400


# AC8 – nợ theo khách
def test_uc25_ac8_theo_khach(client, db, cn):
    r = client.get("/api/phai-thu/theo-khach")
    assert r.status_code == 200
    assert [(k["ten_khach"], k["so_khoan"], k["tong_no"]) for k in r.json()] == [
        ("Cty A", 1, 2_997_000),
        ("Cty B", 2, 2_240_000),
    ]
    da_thu(client, [cn["pt"]["d2"]])
    assert [(k["ten_khach"], k["so_khoan"], k["tong_no"]) for k in client.get("/api/phai-thu/theo-khach").json()] == [
        ("Cty A", 1, 2_997_000),
        ("Cty B", 1, 800_000),
    ]
    da_thu(client, [cn["pt"]["d4"]])
    assert [k["ten_khach"] for k in client.get("/api/phai-thu/theo-khach").json()] == ["Cty A"]


# AC9 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "TAI_XE", "QUAN_LY"])
def test_uc25_ac9_khong_phai_ke_toan_khong_ghi(client, dang_nhap_voi, db, cn, vai_tro):
    dang_nhap_voi(vai_tro)
    assert ma(da_thu(client, [cn["pt"]["d4"]])) == (403, "KHONG_DU_QUYEN")
    assert trang_thai(db, cn["pt"]["d4"]) == ["CHUA_THU"]


@pytest.mark.parametrize(
    ("vai_tro", "ma_tt"), [("QUAN_LY", 200), ("KE_TOAN", 200), ("DIEU_PHOI", 403), ("TAI_XE", 403)]
)
def test_uc25_ac9_xem(client, dang_nhap_voi, cn, vai_tro, ma_tt):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/phai-thu").status_code == ma_tt
    assert client.get("/api/phai-thu/theo-khach").status_code == ma_tt


def test_uc25_ac9_chua_dang_nhap(client):
    assert client.post("/api/phai-thu/da-thu", json={"phai_thu_ids": [1], "ngay": "2026-11-09"}).status_code == 401
    assert client.get("/api/phai-thu").status_code == 401
    assert client.get("/api/phai-thu/theo-khach").status_code == 401
