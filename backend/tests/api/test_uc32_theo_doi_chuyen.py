# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, Nut, SuCo, TamUng, Xe
from app.modules.chuyen import theo_doi
from tests.api.test_uc13_ghep_don import NGAY, kb, lap, luc, trang_thai  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import chot, chuyen, lap_c01, sua


@pytest.fixture
def dang_chay(client, dang_nhap_voi, db, kb):
    """C01 (Đ1, Đ2, Đ4) đã chốt rồi bắt đầu chạy lúc 06:00, km bắt đầu 120.000; ETA kế hoạch lưu lúc chốt."""
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    assert chot(client, c01).status_code == 200
    sua(db, Chuyen, c01, trang_thai="DANG_CHAY", km_bat_dau=120000, khoi_hanh_thuc_te=luc(6))
    for k in ("d1", "d2", "d4"):
        sua(db, DonHang, kb[k], trang_thai="DA_GHEP")
    return {"c01": c01, "dp": dp}


def ghep_cua(db, c01, don_id) -> Ghep:
    db.expire_all()
    return db.scalar(select(Ghep).where(Ghep.chuyen_id == c01, Ghep.don_hang_id == don_id, Ghep.hieu_luc))


def quet(db, kb, c01, don, loai, tre_phut=0, trang_thai_moi=None):
    """Lượt quét lúc ETA kế hoạch + tre_phut (giờ máy chủ ghi thẳng để test được độ trễ)."""
    g = ghep_cua(db, c01, kb[don])
    eta = g.eta_lay_ke_hoach if loai in ("LAY", "KHONG_LAY") else g.eta_giao_ke_hoach
    db.add(LuotQuet(ghep_id=g.id, tai_xe_id=kb["an"], loai=loai, thoi_gian=eta + timedelta(minutes=tre_phut)))
    if trang_thai_moi:
        db.get(DonHang, kb[don]).trang_thai = trang_thai_moi
    db.commit()
    return eta


def bang(client, c01) -> dict:
    ds = client.get("/api/chuyen", params={"ngay": NGAY.isoformat()}).json()["du_lieu"]
    return next(x["theo_doi"] for x in ds if x["id"] == c01)


def chi_tiet(client, c01) -> dict:
    return client.get(f"/api/chuyen/{c01}").json()


def chuyen_ke_tiep(db, kb, dp, gio, phut=0, **gt):
    c = Chuyen(
        ma_chuyen=f"CH-C00-{gio}{phut}",
        tuyen_id=kb["t01"],
        xe_id=kb["x4"],
        tai_xe_id=kb["an"],
        khoi_hanh_du_kien=luc(gio, phut),
        ket_thuc_du_kien=luc(gio + 4, phut),
        dieu_phoi_id=dp.id,
        **({"trang_thai": "DA_CHOT"} | gt),
    )
    db.add(c)
    db.commit()
    return c.ma_chuyen


# AC1 – tiến độ trên bảng ngày
def test_uc32_ac1_tien_do(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    td = bang(client, c01)
    assert (td["xong"], td["tong"], Decimal(td["ty_le_lap_day"])) == (0, 6, Decimal("0.76"))
    quet(db, kb, c01, "d4", "LAY", trang_thai_moi="DA_LAY")
    quet(db, kb, c01, "d1", "LAY", trang_thai_moi="DA_LAY")
    assert (bang(client, c01)["xong"], bang(client, c01)["tong"]) == (2, 6)
    quet(db, kb, c01, "d2", "KHONG_LAY", trang_thai_moi="THAT_BAI")  # điểm giao Đ2 cũng xong
    assert bang(client, c01)["xong"] == 4
    assert "theo_doi" not in client.get("/api/chuyen").json()["du_lieu"][0] or (
        client.get("/api/chuyen").json()["du_lieu"][0]["theo_doi"] is None
    )


# AC2 – cờ trễ theo CFG-09 (15 phút)
@pytest.mark.parametrize(("tre", "co"), [(30, True), (10, False), (15, False), (16, True)])
def test_uc32_ac2_co_tre(client, db, kb, dang_chay, tre, co):
    c01 = dang_chay["c01"]
    quet(db, kb, c01, "d2", "LAY", tre_phut=tre)
    assert ("TRE" in bang(client, c01)["co"]) is co
    diem = next(p for p in chi_tiet(client, c01)["lich_trinh"] if (p["ma_don"], p["viec"]) == ("DH-0002", "LAY"))
    assert (diem["tre_phut"], diem["ket_qua"]) == (tre, "LAY")


# AC3 – chồng lịch khi đang chạy (BR-73)
@pytest.mark.parametrize(("tre", "gio", "phut", "chong"), [(30, 13, 45, True), (30, 14, 0, False), (10, 13, 45, False)])
def test_uc32_ac3_chong_lich(client, db, kb, dang_chay, tre, gio, phut, chong):
    c01 = dang_chay["c01"]
    c00 = chuyen_ke_tiep(db, kb, dang_chay["dp"], gio, phut)
    quet(db, kb, c01, "d2", "LAY", tre_phut=tre)  # TC-BR73-01…03
    ct = chi_tiet(client, c01)
    assert datetime.fromisoformat(ct["ket_thuc_dang_chay"]) == luc(13, 30) + timedelta(minutes=tre)
    assert (c00 in ct["chong"], "CHONG_LICH" in ct["co"]) == (chong, chong)
    assert (c00 in bang(client, c01)["chong"]) is chong


def test_uc32_ac3_chuyen_huy_khong_tinh_chong(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    chuyen_ke_tiep(db, kb, dang_chay["dp"], 13, 45, trang_thai="HUY")
    quet(db, kb, c01, "d2", "LAY", tre_phut=30)
    assert chi_tiet(client, c01)["chong"] == []


# AC4 – cờ sự cố, thất bại, chưa quyết toán
def test_uc32_ac4_cac_co_khac(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    sc = SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="HONG_XE", ghi_chu="thủng lốp")
    db.add(sc)
    db.commit()
    assert "SU_CO" in bang(client, c01)["co"]
    assert client.post(f"/api/su-co/{sc.id}/dong", json={"cach_xu_ly": "đã vá"}).status_code == 200
    assert "SU_CO" not in bang(client, c01)["co"]
    quet(db, kb, c01, "d2", "KHONG_LAY", trang_thai_moi="THAT_BAI")
    assert "THAT_BAI" in bang(client, c01)["co"]
    sua(db, Chuyen, c01, trang_thai="HOAN_THANH")
    assert "CHUA_QUYET_TOAN" in bang(client, c01)["co"]


# AC5 – chi tiết: giờ quét, dòng thời gian, tiền
def test_uc32_ac5_chi_tiet(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    eta = quet(db, kb, c01, "d4", "LAY", tre_phut=5, trang_thai_moi="DA_LAY")
    db.add(
        TamUng(chuyen_id=c01, tai_xe_id=kb["an"], so_tien=700000, hinh_thuc="TIEN_MAT", nguoi_tao=dang_chay["dp"].id)
    )
    db.add(SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="KET_XE"))
    db.commit()
    ct = chi_tiet(client, c01)
    d4 = next(p for p in ct["lich_trinh"] if (p["ma_don"], p["viec"]) == ("DH-0004", "LAY"))
    assert datetime.fromisoformat(d4["eta_ke_hoach"]) == eta
    assert datetime.fromisoformat(d4["thuc_te"]) == eta + timedelta(minutes=5)
    assert ct["tien"] == {"dinh_muc": 1000000, "luong": 600000, "tam_ung_hieu_luc": 700000, "doanh_thu": 5237000}
    loai = [s["loai"] for s in ct["dong_thoi_gian"]]
    assert {"TRANG_THAI", "QUET", "SU_CO"} <= set(loai)
    luc_su_kien = [s["luc"] for s in ct["dong_thoi_gian"]]
    assert luc_su_kien == sorted(luc_su_kien)
    assert [s["loai"] for s in ct["su_co"]] == ["KET_XE"]
    # Dòng thời gian hiện chữ, không hiện mã trạng thái / mã quét
    noi_dung = [s["noi_dung"] for s in ct["dong_thoi_gian"]]
    assert "Quét lấy đơn DH-0004" in noi_dung
    assert any("Đang lập → Đã chốt" in x for x in noi_dung)
    assert not any(ma in x for x in noi_dung for ma in ("LAP", "DA_CHOT", "CHO_GHEP", "DA_GHEP", "Quét LAY"))


# Bản đồ chi tiết chuyến: mỗi điểm mang tọa độ của nút; nút chưa có tọa độ thì null (giao diện bỏ qua)
def test_chi_tiet_co_toa_do_diem(client, db, kb, dang_chay):
    nut = db.scalar(select(Nut).where(Nut.ten == "TP.HCM"))
    nut.lat, nut.lng = Decimal("10.776889"), Decimal("106.700806")
    db.commit()
    ds = chi_tiet(client, dang_chay["c01"])["lich_trinh"]
    co = [p for p in ds if p["nut"] == "TP.HCM"]
    assert co and all((Decimal(p["lat"]), Decimal(p["lng"])) == (nut.lat, nut.lng) for p in co)
    assert all(p["lat"] is None and p["lng"] is None for p in ds if p["nut"] != "TP.HCM")


# AC6 – kết thúc do sự cố (TC-BR68-01)
def test_uc32_ac6_ket_thuc_su_co(client, db, kb, dang_chay, monkeypatch):
    c01 = dang_chay["c01"]
    monkeypatch.setattr(theo_doi, "bay_gio", lambda: luc(10))
    quet(db, kb, c01, "d4", "LAY", trang_thai_moi="DA_LAY")
    quet(db, kb, c01, "d1", "LAY", trang_thai_moi="DA_LAY")
    quet(db, kb, c01, "d2", "LAY", trang_thai_moi="DA_LAY")
    quet(db, kb, c01, "d4", "GIAO", trang_thai_moi="DA_GIAO")
    r = client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json={"ly_do": "hỏng hộp số", "km_ket_thuc": 120090})
    assert r.status_code == 200, r.text
    c = chuyen(db, c01)
    assert (c.trang_thai, c.ket_thuc_bat_thuong, c.ly_do_ket_thuc, c.km_ket_thuc) == (
        "HOAN_THANH",
        True,
        "hỏng hộp số",
        120090,
    )
    assert c.ket_thuc_du_kien == c.ket_thuc_thuc_te
    assert db.get(Xe, kb["x1"]).km_dong_ho == 120090
    assert (trang_thai(db, kb["d1"]), trang_thai(db, kb["d2"]), trang_thai(db, kb["d4"])) == (
        "THAT_BAI",
        "THAT_BAI",
        "DA_GIAO",
    )
    assert ghep_cua(db, c01, kb["d1"]) is None  # BR-36: ghép hết hiệu lực
    ly_do = db.scalar(
        select(LichSuTrangThai.ly_do).where(
            LichSuTrangThai.doi_tuong_id == kb["d1"], LichSuTrangThai.sang == "THAT_BAI"
        )
    )
    assert ly_do == "Sự cố xe: hỏng hộp số"
    # Chi tiết chuyến đã kết thúc vẫn còn đủ 3 đơn (đơn thất bại có kết quả)
    assert len(r.json()["don"]) == 3 and r.json()["ket_thuc_bat_thuong"] is True


# AC7 – km, lý do, trạng thái
def test_uc32_ac7_khong_km_va_don_chua_lay(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    r = client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json={"ly_do": "tai nạn"})  # TC-BR68-04
    assert r.status_code == 200
    assert chuyen(db, c01).km_ket_thuc is None
    db.expire_all()
    assert db.get(Xe, kb["x1"]).km_dong_ho == 0
    assert trang_thai(db, kb["d2"]) == "THAT_BAI"  # đơn DA_GHEP (chưa lấy) cũng thất bại


@pytest.mark.parametrize(
    ("body", "ma"), [({}, 400), ({"ly_do": "   "}, 400), ({"ly_do": "x", "km_ket_thuc": 120000}, 422)]
)
def test_uc32_ac7_du_lieu_sai(client, db, kb, dang_chay, body, ma):
    c01 = dang_chay["c01"]
    r = client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json=body)  # TC-BR68-02; km = km bắt đầu → BR-70
    assert r.status_code == ma
    if ma == 422:
        assert r.json()["ma"] == "BR-70"
    assert chuyen(db, c01).trang_thai == "DANG_CHAY"


def test_uc32_ac7_chuyen_chua_chay(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    chot(client, c01)
    r = client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json={"ly_do": "x"})  # TC-BR68-03
    assert (r.status_code, r.json()["ma"]) == (409, "BR-68")
    assert client.post("/api/chuyen/999999/ket-thuc-su-co", json={"ly_do": "x"}).status_code == 404


# AC8 – sau kết thúc do sự cố: lịch được giải phóng, không tính BR-37
def test_uc32_ac8_giai_phong_lich(client, db, kb, dang_chay, monkeypatch):
    c01 = dang_chay["c01"]
    monkeypatch.setattr(theo_doi, "bay_gio", lambda: luc(8))
    assert client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json={"ly_do": "hỏng xe"}).status_code == 200
    assert chuyen(db, c01).ket_thuc_du_kien == luc(8)
    assert lap(client, kb, gio=9)  # cùng xe X1, tài xế An: trước đây C01 chiếm tới 13:30
    # Đơn thất bại do sự cố không có lượt quét giao thất bại nên không tính BR-37
    assert db.scalar(select(LuotQuet.id).where(LuotQuet.loai == "GIAO_THAT_BAI")) is None


# AC9 – đóng sự cố
def test_uc32_ac9_dong_su_co(client, db, kb, dang_chay):
    sc = SuCo(chuyen_id=dang_chay["c01"], tai_xe_id=kb["an"], loai="HONG_XE")
    db.add(sc)
    db.commit()
    assert client.post(f"/api/su-co/{sc.id}/dong", json={}).status_code == 400
    r = client.post(f"/api/su-co/{sc.id}/dong", json={"cach_xu_ly": "gọi cứu hộ"})
    assert (r.status_code, r.json()["trang_thai"], r.json()["cach_xu_ly"]) == (200, "DONG", "gọi cứu hộ")
    assert client.post(f"/api/su-co/{sc.id}/dong", json={"cach_xu_ly": "x"}).status_code == 409
    assert client.post("/api/su-co/999999/dong", json={"cach_xu_ly": "x"}).status_code == 404


# AC10 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "xem", "ghi"),
    [("DIEU_PHOI", 200, 200), ("QUAN_LY", 200, 200), ("KE_TOAN", 200, 403), ("TAI_XE", 403, 403)],
)
def test_uc32_ac10_phan_quyen(client, dang_nhap_voi, db, kb, dang_chay, vai_tro, xem, ghi):
    c01 = dang_chay["c01"]
    sc = SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="HONG_XE")
    db.add(sc)
    db.commit()
    dang_nhap_voi(vai_tro)
    assert client.get("/api/chuyen", params={"ngay": NGAY.isoformat()}).status_code == xem
    assert client.get(f"/api/chuyen/{c01}").status_code == xem
    assert client.post(f"/api/su-co/{sc.id}/dong", json={"cach_xu_ly": "x"}).status_code == ghi
    assert client.post(f"/api/chuyen/{c01}/ket-thuc-su-co", json={"ly_do": "x"}).status_code == ghi
    assert chuyen(db, c01).trang_thai == ("HOAN_THANH" if ghi == 200 else "DANG_CHAY")


def test_uc32_ac10_chua_dang_nhap(client, kb):
    assert client.post("/api/chuyen/1/ket-thuc-su-co", json={"ly_do": "x"}).status_code == 401
    assert client.post("/api/su-co/1/dong", json={"cach_xu_ly": "x"}).status_code == 401
