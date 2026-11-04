# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Chuyen, LichSuTrangThai, TamUng
from tests.api.test_uc13_ghep_don import ghep, kb, lap, so_ghep, trang_thai  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import chot, chuyen, lap_c01, sua


def huy(client, chuyen_id, ly_do="khách hoãn", **them):
    return client.post(f"/api/chuyen/{chuyen_id}/huy", json={"ly_do": ly_do, **them} if ly_do is not None else {})


def don_ve_cho_ghep(db, kb, *ten) -> bool:
    return all(trang_thai(db, kb[t]) == "CHO_GHEP" for t in ten)


# AC1 – hủy chuyến LAP
def test_uc16_ac1_huy_chuyen_lap(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    r = huy(client, c01)
    assert r.status_code == 200, r.text
    assert (r.json()["trang_thai"], r.json()["don"]) == ("HUY", [])
    assert don_ve_cho_ghep(db, kb, "d1", "d2", "d4")
    assert so_ghep(db, chuyen_id=c01) == 3
    assert so_ghep(db, chuyen_id=c01, hieu_luc=True) == 0


# AC2 – hủy chuyến đã chốt, giữ số đã chốt
def test_uc16_ac2_huy_chuyen_da_chot(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    assert chot(client, c01).status_code == 200
    assert huy(client, c01).status_code == 200
    c = chuyen(db, c01)
    assert (c.trang_thai, c.dm_dau_chot, c.luong_tai_xe_chot) == ("HUY", 550000, 600000)
    assert don_ve_cho_ghep(db, kb, "d1", "d4")


# AC3 – sau khi hủy: đơn ghép lại được, xe và tài xế rảnh
def test_uc16_ac3_don_va_lich_duoc_giai_phong(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1")
    huy(client, c01)
    c02 = lap(client, kb)  # cùng xe X1, tài xế An, cùng 06:00 (BR-16, 17 bỏ qua chuyến HUY)
    assert ghep(client, c02, kb["d1"]).status_code == 200
    assert so_ghep(db, don_hang_id=kb["d1"]) == 2
    assert so_ghep(db, don_hang_id=kb["d1"], hieu_luc=True) == 1


# AC4 – còn tạm ứng
def test_uc16_ac4_con_tam_ung(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    chot(client, c01)
    tu = TamUng(chuyen_id=c01, tai_xe_id=kb["an"], so_tien=1000000, hinh_thuc="TIEN_MAT", nguoi_tao=dp.id)
    db.add(tu)
    db.commit()

    r = huy(client, c01)  # TC-BR25-02
    assert (r.status_code, r.json()["ma"]) == (409, "BR-25")
    assert chuyen(db, c01).trang_thai == "DA_CHOT"
    assert trang_thai(db, kb["d1"]) == "DA_GHEP"

    sua(db, TamUng, tu.id, trang_thai="DA_THU_HOI")
    assert huy(client, c01).status_code == 200


# AC5 – trạng thái sai
@pytest.mark.parametrize("tt", ["DANG_CHAY", "HOAN_THANH", "DA_QUYET_TOAN"])
def test_uc16_ac5_trang_thai_khong_huy_duoc(client, dang_nhap_voi, db, kb, tt):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    sua(db, Chuyen, c01, trang_thai=tt)
    r = huy(client, c01)  # TC-BR25-03
    assert (r.status_code, r.json()["ma"]) == (409, "BR-25")
    assert chuyen(db, c01).trang_thai == tt
    assert trang_thai(db, kb["d1"]) == "DA_GHEP"


def test_uc16_ac5_huy_lan_hai_va_khong_ton_tai(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb)
    assert huy(client, c01).status_code == 200
    r = huy(client, c01)
    assert (r.status_code, r.json()["ma"]) == (409, "BR-25")
    assert huy(client, 999).status_code == 404


# AC6 – lý do
@pytest.mark.parametrize(("ly_do", "ma"), [(None, 400), ("", 400), ("   ", 400), ("x" * 301, 400), ("x" * 300, 200)])
def test_uc16_ac6_ly_do(client, dang_nhap_voi, db, kb, ly_do, ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb)
    assert huy(client, c01, ly_do).status_code == ma
    assert chuyen(db, c01).trang_thai == ("HUY" if ma == 200 else "LAP")


def test_uc16_ac6_truong_la(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb)
    assert huy(client, c01, xoa_luon=True).status_code == 400


# AC7 – lịch sử
def test_uc16_ac7_lich_su_co_ly_do(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    huy(client, c01, "  khách hoãn  ")
    ls = db.execute(
        select(LichSuTrangThai.doi_tuong, LichSuTrangThai.doi_tuong_id, LichSuTrangThai.tu, LichSuTrangThai.ly_do)
        .where(LichSuTrangThai.sang.in_(("HUY", "CHO_GHEP")), LichSuTrangThai.nguoi == dp.id)
        .order_by(LichSuTrangThai.id)
    ).all()
    assert ls == [
        ("DON", kb["d1"], "DA_GHEP", "khách hoãn"),
        ("DON", kb["d4"], "DA_GHEP", "khách hoãn"),
        ("CHUYEN", c01, "LAP", "khách hoãn"),
    ]


# AC8 – hủy và ghép cùng lúc
def test_uc16_ac8_huy_va_ghep_dong_thoi(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1")
    ket_qua: dict = {}
    cho = threading.Barrier(2)

    def gui(viec):
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieu_phoi", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua[viec] = huy(c, c01) if viec == "huy" else ghep(c, c01, kb["d4"])

    luong = [threading.Thread(target=gui, args=(v,)) for v in ("huy", "ghep")]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert ket_qua["huy"].status_code == 200
    assert ket_qua["ghep"].status_code in (200, 409)
    # Dù ai chạy trước: không đơn nào kẹt ở DA_GHEP của chuyến đã hủy
    assert so_ghep(db, chuyen_id=c01, hieu_luc=True) == 0
    assert don_ve_cho_ghep(db, kb, "d1", "d4")


# AC9 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc16_ac9_phan_quyen(client, dang_nhap_voi, db, kb, vai_tro, ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1")
    dang_nhap_voi(vai_tro)
    assert huy(client, c01).status_code == ma
    assert chuyen(db, c01).trang_thai == ("HUY" if ma == 200 else "LAP")


def test_uc16_ac9_chua_dang_nhap(client, kb):
    assert huy(client, 1).status_code == 401
