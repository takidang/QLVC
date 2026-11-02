import pytest

from app.models import Chuyen, NguoiDung, TaiXe, Xe
from tests.api.test_uc13_ghep_don import HAN_XA, ghep, kb, lap  # noqa: F401 – dùng lại dữ liệu kịch bản UC-13


@pytest.fixture
def them(db, kb):  # noqa: F811
    """Xe nhỏ X2 (tải 1.500 kg, toàn bộ 3.400 kg) và tài xế Bình hạng B (kịch bản mục 11)."""
    x2 = Xe(
        bien_so="51C-222.22",
        tai_trong_kg=1500,
        the_tich_m3=8,
        ktt_toan_bo_kg=3400,
        han_dang_kiem=HAN_XA,
        han_bao_hiem=HAN_XA,
    )
    nd = NguoiDung(ten_dang_nhap="binh", ho_ten="Bình", vai_tro="TAI_XE", mat_khau_bam="-")
    db.add_all([x2, nd])
    db.flush()
    binh = TaiXe(nguoi_dung_id=nd.id, so_gplx="GPLXBINH01", hang_gplx="B", han_gplx=HAN_XA, sdt="0909000001")
    db.add(binh)
    db.commit()
    return kb | {"x2": x2.id, "binh": binh.id}


def doi(client, chuyen_id, xe_id, tai_xe_id, **them_truong):
    return client.put(f"/api/chuyen/{chuyen_id}/phan-cong", json={"xe_id": xe_id, "tai_xe_id": tai_xe_id} | them_truong)


# AC1 – đổi hợp lệ
def test_uc12_ac1_doi_xe_va_tai_xe(client, dang_nhap_voi, db, them):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    ghep(client, c01, them["d1"], them["d4"])  # 2.600 kg
    r = doi(client, c01, them["x4"], them["dung"])
    assert r.status_code == 200
    assert (r.json()["bien_so"], r.json()["ten_tai_xe"]) == ("51C-444.44", "Dũng")
    assert r.json()["lich_trinh"] and len(r.json()["don"]) == 2  # đơn và lịch trình giữ nguyên
    db.expire_all()
    c = db.get(Chuyen, c01)
    assert (c.xe_id, c.tai_xe_id) == (them["x4"], them["dung"])
    # Giữ nguyên xe, tài xế hiện tại: không bị coi là trùng lịch với chính chuyến này
    assert doi(client, c01, them["x4"], them["dung"]).status_code == 200


# AC2 – bị chặn, không đổi gì
def test_uc12_ac2_xe_nho_hon_hang_dang_ghep(client, dang_nhap_voi, db, them):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    ghep(client, c01, them["d1"], them["d4"])
    r = doi(client, c01, them["x2"], them["an"])  # BR-01 theo BR-67: 2.600 kg > 1.500 kg
    assert r.status_code == 422
    assert [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-01"]
    db.expire_all()
    assert db.get(Chuyen, c01).xe_id == them["x1"]


def test_uc12_ac2_tai_xe_sai_hang_va_trung_lich(client, dang_nhap_voi, them):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    r = doi(client, c01, them["x1"], them["binh"])  # BR-14: xe 9.500 kg cần hạng C
    assert (r.status_code, r.json()["ma"]) == (422, "BR-14")
    lap(client, them, gio=8, xe="x4", tai_xe="dung")  # Dũng có chuyến 08:00, chồng [06:00, 11:30)
    r = doi(client, c01, them["x1"], them["dung"])
    assert (r.status_code, r.json()["ma"]) == (422, "BR-17")
    r = doi(client, c01, them["x4"], them["an"])
    assert (r.status_code, r.json()["ma"]) == (422, "BR-16")


def test_uc12_ac2_trang_thai_va_du_lieu_sai(client, dang_nhap_voi, db, them):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    assert doi(client, 999, them["x1"], them["an"]).status_code == 404
    assert doi(client, c01, 999, them["an"]).status_code == 404
    assert doi(client, c01, them["x1"], 999).status_code == 404
    assert doi(client, c01, them["x1"], them["an"], ghi_chu="x").status_code == 400
    db.get(Chuyen, c01).trang_thai = "DA_CHOT"
    db.commit()
    r = doi(client, c01, them["x4"], them["an"])
    assert (r.status_code, r.json()["ma"]) == (409, "BR-09")


# AC3 – xe, tài xế khả dụng cho chuyến đã có
def test_uc12_ac3_kha_dung_cho_chuyen(client, dang_nhap_voi, them):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    ghep(client, c01, them["d1"], them["d4"])
    xe = {x["bien_so"]: x for x in client.get(f"/api/chuyen/{c01}/xe-kha-dung").json()}
    assert xe["51C-111.11"]["kha_dung"] is True  # xe đang dùng không trùng lịch với chính nó
    assert [v["ma"] for v in xe["51C-222.22"]["ly_do"]] == ["BR-01"]
    tx = {t["ho_ten"]: t for t in client.get(f"/api/chuyen/{c01}/tai-xe-kha-dung").json()}
    assert tx["An"]["kha_dung"] is True
    assert [v["ma"] for v in tx["Bình"]["ly_do"]] == ["BR-14"]  # mặc định xét theo xe hiện tại
    tx = {t["ho_ten"]: t for t in client.get(f"/api/chuyen/{c01}/tai-xe-kha-dung", params={"xe_id": them["x2"]}).json()}
    assert tx["Bình"]["kha_dung"] is True  # xe nhỏ 3.400 kg: hạng B đủ
    assert client.get("/api/chuyen/999/xe-kha-dung").status_code == 404


# AC4 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc12_ac4_phan_quyen(client, dang_nhap_voi, db, them, vai_tro, ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, them)
    dang_nhap_voi(vai_tro)
    assert doi(client, c01, them["x4"], them["dung"]).status_code == ma
    assert client.get(f"/api/chuyen/{c01}/xe-kha-dung").status_code == ma
    assert client.get(f"/api/chuyen/{c01}/tai-xe-kha-dung").status_code == ma
    if ma == 403:
        db.expire_all()
        assert db.get(Chuyen, c01).xe_id == them["x1"]


def test_uc12_ac4_chua_dang_nhap(client):
    assert doi(client, 1, 1, 1).status_code == 401
