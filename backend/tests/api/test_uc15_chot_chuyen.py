# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import threading
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, TaiXe, TamUng, Tuyen, Xe
from tests.api.test_uc13_ghep_don import ghep, go, kb, lap, luc  # noqa: F401 (kb là fixture)


def chot(client, chuyen_id, **xac_nhan):
    return client.post(f"/api/chuyen/{chuyen_id}/chot", json=xac_nhan or None)


def mo_chot(client, chuyen_id):
    return client.post(f"/api/chuyen/{chuyen_id}/mo-chot")


def chuyen(db, chuyen_id) -> Chuyen:
    db.expire_all()
    return db.get(Chuyen, chuyen_id)


def lap_c01(client, kb, *don):
    c01 = lap(client, kb)
    if don:
        assert ghep(client, c01, *(kb[d] for d in don)).status_code == 200
    return c01


def sua(db, model, id_, **gt):
    o = db.get(model, id_)
    for k, v in gt.items():
        setattr(o, k, v)
    db.commit()


def ma_vi_pham(r) -> set[str]:
    return {v["ma"] for v in r.json()["chi_tiet"]}


# AC1, AC2 – chốt hợp lệ, lưu định mức, lương, ETA kế hoạch
def test_uc15_ac1_ac2_chot_c01(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    r = chot(client, c01)
    assert r.status_code == 200, r.text
    assert (r.json()["trang_thai"], r.json()["lai_du_kien"], r.json()["chay_rong"]) == ("DA_CHOT", 3637000, False)

    c = chuyen(db, c01)
    assert (c.dm_dau_chot, c.dm_cau_duong_chot, c.dm_boc_xep_chot, c.luong_tai_xe_chot) == (
        550000,
        200000,
        250000,
        600000,
    )
    eta = {
        g.don_hang_id: (g.eta_lay_ke_hoach, g.eta_giao_ke_hoach)
        for g in db.scalars(select(Ghep).where(Ghep.chuyen_id == c01))
    }
    assert eta == {
        kb["d1"]: (luc(6), luc(12, 10)),
        kb["d4"]: (luc(6, 20), luc(9)),
        kb["d2"]: (luc(7, 40), luc(11, 50)),
    }
    assert {d.don_hang_id for d in db.scalars(select(Ghep).where(Ghep.chuyen_id == c01))} == {
        kb["d1"],
        kb["d2"],
        kb["d4"],
    }
    assert db.get(DonHang, kb["d1"]).trang_thai == "DA_GHEP"  # đơn không đổi trạng thái khi chốt

    # TC-BR71-01: đổi định mức tuyến sau khi chốt không ảnh hưởng chuyến
    sua(db, Tuyen, kb["t01"], dm_dau=600000)
    assert chuyen(db, c01).dm_dau_chot == 550000
    assert client.get(f"/api/chuyen/{c01}").json()["lai_du_kien"] == 3637000


# AC3 – chuyến rỗng
def test_uc15_ac3_chay_rong_can_xac_nhan(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c03 = lap_c01(client, kb)
    r = chot(client, c03)
    assert (r.status_code, r.json()["ma"]) == (422, "BR-23")
    assert chuyen(db, c03).trang_thai == "LAP"

    r = chot(client, c03, xac_nhan_chay_rong=True)  # không cần thêm xác nhận lãi âm (quyết định số 2)
    assert r.status_code == 200, r.text
    assert (r.json()["trang_thai"], r.json()["chay_rong"]) == ("DA_CHOT", True)
    assert chuyen(db, c03).chay_rong is True


# AC4 – lãi âm
def test_uc15_ac4_lai_am_can_xac_nhan(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d8")
    r = chot(client, c01)
    assert (r.status_code, r.json()["ma"]) == (422, "BR-52")
    assert "1.267.000" in r.json()["thong_diep"]
    assert chuyen(db, c01).trang_thai == "LAP"
    assert chot(client, c01, xac_nhan_chay_rong=True).status_code == 422  # xác nhận chạy rỗng không thay lãi âm

    r = chot(client, c01, xac_nhan_lai_am=True)
    assert (r.status_code, r.json()["trang_thai"]) == (200, "DA_CHOT")


def test_uc15_ac4_lai_bang_0_khong_can_xac_nhan(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    sua(db, DonHang, kb["d8"], cuoc_tinh=1600000)  # đúng bằng định mức 1.000.000 + lương 600.000
    c01 = lap_c01(client, kb, "d8")
    r = chot(client, c01)
    assert (r.status_code, r.json()["lai_du_kien"]) == (200, 0)


# AC5 – kiểm lại nhóm B
def test_uc15_ac5_giay_to_het_han_sau_khi_lap(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    sua(db, Xe, kb["x1"], han_dang_kiem=date(2030, 10, 21))  # trước ngày kết thúc 22/10
    r = chot(client, c01)
    assert (r.status_code, r.json()["ma"]) == (422, "VI_PHAM_CHOT")
    assert ma_vi_pham(r) == {"BR-12"}
    assert chuyen(db, c01).trang_thai == "LAP"

    sua(db, Xe, kb["x1"], han_dang_kiem=date(2030, 10, 22))  # biên: đúng ngày kết thúc
    assert chot(client, c01).status_code == 200


@pytest.mark.parametrize(("model", "khoa", "ma"), [(Xe, "x1", "BR-11"), (TaiXe, "an", "TAI_XE_NGUNG")])
def test_uc15_ac5_xe_tai_xe_ngung(client, dang_nhap_voi, db, kb, model, khoa, ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    sua(db, model, kb[khoa], trang_thai="NGUNG")
    r = chot(client, c01)
    assert r.status_code == 422 and ma in ma_vi_pham(r)
    assert chuyen(db, c01).trang_thai == "LAP"


# AC6 – kiểm lại nhóm A
def test_uc15_ac6_han_giao_doi_sau_khi_ghep(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    sua(db, DonHang, kb["d2"], han_giao=luc(11, 49))  # ETA giao Đ2 là 11:50
    r = chot(client, c01)
    assert r.status_code == 422
    assert [(v["ma"], v["don_id"]) for v in r.json()["chi_tiet"]] == [("BR-06", kb["d2"])]

    sua(db, DonHang, kb["d2"], han_giao=luc(11, 50))  # biên: đúng bằng ETA
    assert chot(client, c01).status_code == 200


# AC7 – mở chốt
def test_uc15_ac7_mo_chot_va_chot_lai(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    chot(client, c01)
    tu = TamUng(chuyen_id=c01, tai_xe_id=kb["an"], so_tien=1000000, hinh_thuc="TIEN_MAT", nguoi_tao=dp.id)
    db.add(tu)
    db.commit()

    r = mo_chot(client, c01)  # TC-BR24-01
    assert (r.status_code, r.json()["ma"]) == (409, "BR-24")
    assert chuyen(db, c01).trang_thai == "DA_CHOT"

    sua(db, TamUng, tu.id, trang_thai="DA_THU_HOI")  # TC-BR24-02
    sua(db, Tuyen, kb["t01"], dm_dau=600000)
    r = mo_chot(client, c01)
    assert (r.status_code, r.json()["trang_thai"]) == (200, "LAP")
    assert r.json()["lai_du_kien"] == 3587000  # về LAP: lấy định mức từ tuyến (dầu 600.000)
    c = chuyen(db, c01)
    assert (c.dm_dau_chot, c.luong_tai_xe_chot, c.chay_rong) == (None, None, False)
    assert all(g.eta_lay_ke_hoach is None for g in db.scalars(select(Ghep).where(Ghep.chuyen_id == c01)))

    assert chot(client, c01).status_code == 200  # TC-BR71-02: chốt lại lưu số mới
    assert chuyen(db, c01).dm_dau_chot == 600000


# AC8 – lịch sử trạng thái
def test_uc15_ac8_lich_su(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    chot(client, c01)
    mo_chot(client, c01)
    ls = db.execute(
        select(LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.nguoi)
        .where(LichSuTrangThai.doi_tuong == "CHUYEN", LichSuTrangThai.doi_tuong_id == c01)
        .order_by(LichSuTrangThai.id)
    ).all()
    assert ls == [(None, "LAP", dp.id), ("LAP", "DA_CHOT", dp.id), ("DA_CHOT", "LAP", dp.id)]


# AC9 – trạng thái, dữ liệu sai, đồng thời
def test_uc15_ac9_trang_thai_va_du_lieu_sai(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    r = mo_chot(client, c01)
    assert (r.status_code, r.json()["ma"]) == (409, "BR-09")
    assert chot(client, c01, lan=1).status_code == 400  # trường lạ
    assert chot(client, 999).status_code == 404
    assert mo_chot(client, 999).status_code == 404

    assert chot(client, c01).status_code == 200
    for r in (chot(client, c01), ghep(client, c01, kb["d8"]), go(client, c01, kb["d4"])):
        assert (r.status_code, r.json()["ma"]) == (409, "BR-09")


def test_uc15_ac9_chot_dong_thoi(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    ket_qua: list = []
    cho = threading.Barrier(2)

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieu_phoi", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua.append(chot(c, c01))

    luong = [threading.Thread(target=gui) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [200, 409]
    so_dong = db.scalars(
        select(LichSuTrangThai).where(LichSuTrangThai.doi_tuong_id == c01, LichSuTrangThai.sang == "DA_CHOT")
    ).all()
    assert len(so_dong) == 1


# AC10 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc15_ac10_phan_quyen(client, dang_nhap_voi, db, kb, vai_tro, ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")  # lãi dương, không cần xác nhận
    dang_nhap_voi(vai_tro)
    assert chot(client, c01).status_code == ma
    assert chuyen(db, c01).trang_thai == ("DA_CHOT" if ma == 200 else "LAP")
    if ma == 403:
        sua(db, Chuyen, c01, trang_thai="DA_CHOT")
    assert mo_chot(client, c01).status_code == ma
    assert chuyen(db, c01).trang_thai == ("LAP" if ma == 200 else "DA_CHOT")


def test_uc15_ac10_chua_dang_nhap(client, kb):
    assert chot(client, 1).status_code == 401
    assert mo_chot(client, 1).status_code == 401
