import threading
from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models import Chuyen, DonHang, Ghep, KhachHang, LichSuTrangThai, NguoiDung, Nut, TaiXe, Tuyen, TuyenNut, Xe
from app.thoi_gian import GIO_VN

# Ngày chạy ở tương lai (Thứ Ba 22/10/2030); tuyến, xe, đơn theo kịch bản mục 11
NGAY = date(2030, 10, 22)
HAN_XA = date(2031, 12, 31)


def luc(gio: int, phut: int = 0, ngay: int = 22) -> datetime:
    return datetime(2030, 10, ngay, gio, phut, tzinfo=GIO_VN)


def iso(gio: int, phut: int = 0) -> str:
    return luc(gio, phut).isoformat()


@pytest.fixture
def kb(db):
    ten_nut = ("TP.HCM", "Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ", "Bến Tre")
    nut = {t: Nut(ten=t, tinh=t, loai="TINH") for t in ten_nut}
    db.add_all(nut.values())
    t01 = Tuyen(
        ma="T01", ten="TP.HCM – Cần Thơ", dm_dau=550000, dm_cau_duong=200000, dm_boc_xep=250000, dm_luong_tai_xe=600000
    )
    db.add(t01)
    db.flush()
    for i, (t, phut) in enumerate(zip(ten_nut[:5], (0, 60, 120, 210, 270), strict=True), 1):
        db.add(TuyenNut(tuyen_id=t01.id, thu_tu=i, nut_id=nut[t].id, phut_tu_diem_dau=phut, km_tu_diem_dau=phut))

    def xe(bien_so, han=HAN_XA):
        x = Xe(
            bien_so=bien_so,
            tai_trong_kg=5000,
            the_tich_m3=20,
            ktt_toan_bo_kg=9500,
            han_dang_kiem=han,
            han_bao_hiem=HAN_XA,
        )
        db.add(x)
        return x

    def tai_xe(ten):
        nd = NguoiDung(ten_dang_nhap=ten.lower(), ho_ten=ten, vai_tro="TAI_XE", mat_khau_bam="-")
        db.add(nd)
        db.flush()
        tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=f"GPLX{nd.id}00", hang_gplx="C", han_gplx=HAN_XA, sdt="0909000000")
        db.add(tx)
        return tx

    kh = KhachHang(ten="Cty A", sdt="0901116789")
    db.add(kh)
    db.flush()

    def don(so, lay, giao, kg, m3, han, cuoc, khung=(None, None)):
        d = DonHang(
            ma_don=f"DH-{so:04d}",
            khach_hang_id=kh.id,
            kg=Decimal(kg),
            m3=Decimal(m3),
            so_kien=1,
            nut_lay_id=nut[lay].id,
            dia_chi_lay=f"Lấy {so}",
            sdt_lay="0901116789",
            lay_tu=khung[0],
            lay_den=khung[1],
            nut_giao_id=nut[giao].id,
            dia_chi_giao=f"Giao {so}",
            nguoi_nhan="Chị Lan",
            sdt_nhan="0907778888",
            han_giao=han,
            don_gia_chot=1000,
            cuoc_toi_thieu_chot=50000,
            he_so_quy_doi_chot=333,
            lam_tron_chot=1000,
            kl_tinh_cuoc=Decimal(kg),
            cuoc_tinh=cuoc,
        )
        db.add(d)
        return d

    ds = {
        "t01": t01,
        "x1": xe("51C-111.11"),
        "x4": xe("51C-444.44"),
        "x5": xe("51C-555.55", han=NGAY),  # đăng kiểm hết đúng ngày chạy
        "an": tai_xe("An"),
        "dung": tai_xe("Dũng"),
        "d1": don(1, "TP.HCM", "Cần Thơ", 1800, 6, luc(14), 2997000),
        "d2": don(2, "Long An", "Cần Thơ", 1200, 3, luc(12), 1440000, (luc(6, 30), luc(9))),
        "d2c": don(22, "Long An", "Cần Thơ", 1200, 3, luc(12), 1440000, (luc(7, 40), luc(9))),
        "d4": don(4, "TP.HCM", "Tiền Giang", 800, 2, luc(18), 800000),
        "d5": don(5, "Vĩnh Long", "Long An", 500, "1.5", luc(18), 600000),
        "d6": don(6, "TP.HCM", "Cần Thơ", 2500, 5, luc(18), 3750000),
        "d8": don(8, "TP.HCM", "Tiền Giang", 300, 1, luc(18), 333000),
        "d12": don(12, "TP.HCM", "Bến Tre", 100, 1, luc(18), 100000),
        "dem": don(30, "TP.HCM", "Cần Thơ", 100, 1, luc(6, ngay=23), 100000),  # hạn sáng hôm sau
    }
    db.commit()
    return {k: v.id for k, v in ds.items()}


def lap(client, kb, gio=6, xe="x1", tai_xe="an") -> int:
    r = client.post(
        "/api/chuyen",
        json={"tuyen_id": kb["t01"], "khoi_hanh_du_kien": iso(gio), "xe_id": kb[xe], "tai_xe_id": kb[tai_xe]},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def ghep(client, chuyen_id, *don_ids):
    return client.post(f"/api/chuyen/{chuyen_id}/ghep", json={"don_ids": list(don_ids)})


def go(client, chuyen_id, *don_ids):
    return client.post(f"/api/chuyen/{chuyen_id}/go", json={"don_ids": list(don_ids)})


def trang_thai(db, don_id) -> str:
    db.expire_all()
    return db.get(DonHang, don_id).trang_thai


def so_ghep(db, **loc) -> int:
    q = select(func.count()).select_from(Ghep)
    for k, v in loc.items():
        q = q.where(getattr(Ghep, k) == v)
    return db.scalar(q)


# AC7 – ghép hợp lệ
def test_uc13_ac7_ghep_c01(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    assert ghep(client, c01, kb["d1"], kb["d4"]).status_code == 200
    r = ghep(client, c01, kb["d2"])
    assert r.status_code == 200
    c = r.json()
    assert Decimal(c["tai_trong"]["da_dung_kg"]) == 3800 and c["tai_trong"]["toi_da_kg"] == 5000
    assert Decimal(c["the_tich"]["da_dung_m3"]) == 11 and Decimal(c["the_tich"]["toi_da_m3"]) == 20
    assert Decimal(c["ty_le_lap_day"]) == Decimal("0.76")
    assert datetime.fromisoformat(c["ket_thuc_du_kien"]) == luc(13, 30)
    assert [(d["viec"], d["ma_don"], datetime.fromisoformat(d["eta"])) for d in c["lich_trinh"]] == [
        ("LAY", "DH-0001", luc(6)),
        ("LAY", "DH-0004", luc(6, 20)),
        ("LAY", "DH-0002", luc(7, 40)),
        ("GIAO", "DH-0004", luc(9)),
        ("GIAO", "DH-0002", luc(11, 50)),
        ("GIAO", "DH-0001", luc(12, 10)),
    ]
    assert c["lich_trinh"][2]["nut"] == "Long An"
    assert c["lai_du_kien"] == 3637000 and c["canh_bao_lai_am"] is False
    assert sorted(d["ma_don"] for d in c["don"]) == ["DH-0001", "DH-0002", "DH-0004"]

    for k in ("d1", "d2", "d4"):
        assert trang_thai(db, kb[k]) == "DA_GHEP"
    assert so_ghep(db, chuyen_id=c01, hieu_luc=True) == 3
    ls = db.scalars(select(LichSuTrangThai).where(LichSuTrangThai.doi_tuong == "DON")).all()
    assert {(x.doi_tuong_id, x.tu, x.sang, x.nguoi) for x in ls} == {
        (kb[k], "CHO_GHEP", "DA_GHEP", dp.id) for k in ("d1", "d2", "d4")
    }
    assert db.get(Chuyen, c01).ket_thuc_du_kien == luc(13, 30)
    # GET có thêm phần theo dõi của UC-32 (cờ, dòng thời gian, tiền, sự cố); phần còn lại giống kết quả ghép
    them = {"co", "chong", "ket_thuc_dang_chay", "ket_thuc_bat_thuong", "ly_do_ket_thuc", "km_bat_dau", "km_ket_thuc"}
    them |= {"dong_thoi_gian", "tien", "su_co"}
    g = client.get(f"/api/chuyen/{c01}").json()
    assert {k: v for k, v in g.items() if k not in them} == {k: v for k, v in c.items() if k not in them}


# AC8 – ghép bị chặn, không ghép đơn nào trong lô
def test_uc13_ac8_lo_co_don_sai_khong_ghep_gi(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    ghep(client, c01, kb["d1"], kb["d4"])
    # Thêm Đ2 + Đ6: 6.300 kg vượt tải, và 2 điểm dừng thêm làm Đ2 giao 12:30 > 12:00 – báo đủ cả hai
    r = ghep(client, c01, kb["d2"], kb["d6"])
    assert r.status_code == 422
    assert r.json()["ma"] == "VI_PHAM_GHEP"
    assert [(v["don_id"], v["ma"]) for v in r.json()["chi_tiet"]] == [(None, "BR-01"), (kb["d2"], "BR-06")]
    assert trang_thai(db, kb["d2"]) == "CHO_GHEP" and trang_thai(db, kb["d6"]) == "CHO_GHEP"
    assert so_ghep(db) == 2

    r = ghep(client, c01, kb["d2"], kb["d8"])  # TC-BR67-01: lỗi nằm ở đơn đã ghép
    assert [(v["don_id"], v["ma"]) for v in r.json()["chi_tiet"]] == [(kb["d2"], "BR-06")]


def test_uc13_ac8_ket_thuc_lui_chong_chuyen_khac(client, dang_nhap_voi, db, kb):
    # TC-BR67-04: An có chuyến khác lúc 13:00; C01 có Đ1, Đ4 kết thúc 12:50, thêm Đ2 thành 13:30
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    lap(client, kb, gio=13, xe="x4")
    assert ghep(client, c01, kb["d1"], kb["d4"]).status_code == 200
    r = ghep(client, c01, kb["d2"])
    assert r.status_code == 422
    assert [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-17"]
    assert db.get(Chuyen, c01).ket_thuc_du_kien == luc(12, 50)  # không đổi


def test_uc13_ac8_ket_thuc_lui_chong_chuyen_khac_cua_xe(client, dang_nhap_voi, db, kb):
    # Như trên nhưng chuyến lúc 13:00 dùng cùng xe X1, tài xế khác → BR-16
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    lap(client, kb, gio=13, tai_xe="dung")
    assert ghep(client, c01, kb["d1"], kb["d4"]).status_code == 200
    r = ghep(client, c01, kb["d2"])
    assert r.status_code == 422
    assert [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-16"]
    assert trang_thai(db, kb["d2"]) == "CHO_GHEP"


def test_uc13_ac8_ket_thuc_sang_ngay_sau_het_dang_kiem(client, dang_nhap_voi, kb):
    # X5 đăng kiểm hết 22/10; chuyến 18:00 chạy rỗng xong 23:30 (lập được), ghép thêm thì sang 23/10
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb, gio=18, xe="x5", tai_xe="dung")
    r = ghep(client, c, kb["dem"])
    assert r.status_code == 422
    assert [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-12"]


# AC9 – trạng thái và xung đột
def test_uc13_ac9_trang_thai_va_du_lieu_sai(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    c02 = lap(client, kb, xe="x4", tai_xe="dung")
    assert ghep(client, c01, kb["d4"]).status_code == 200
    r = ghep(client, c02, kb["d4"])  # TC-BR09-02: đơn đang ghép ở chuyến khác
    assert (r.status_code, r.json()["ma"]) == (409, "BR-09")

    db.get(Chuyen, c02).trang_thai = "DA_CHOT"
    db.commit()
    r = ghep(client, c02, kb["d8"])  # TC-BR09-03: chuyến không ở LAP
    assert (r.status_code, r.json()["ma"]) == (409, "BR-09")

    assert ghep(client, 999, kb["d8"]).status_code == 404
    assert ghep(client, c01, 999).status_code == 404
    assert ghep(client, c01).status_code == 400  # don_ids rỗng
    r = client.post(f"/api/chuyen/{c01}/ghep", json={"don_ids": [kb["d8"]], "so_luong": 1})  # TC-BR08-01
    assert r.status_code == 400
    assert trang_thai(db, kb["d8"]) == "CHO_GHEP"


def test_uc13_ac9_go_roi_ghep_chuyen_khac(client, dang_nhap_voi, db, kb):
    # TC-BR07-01: đơn có 2 bản ghi ghép, đúng 1 hiệu lực
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    c02 = lap(client, kb, xe="x4", tai_xe="dung")
    ghep(client, c01, kb["d4"])
    assert go(client, c01, kb["d4"]).status_code == 200
    assert ghep(client, c02, kb["d4"]).status_code == 200
    assert so_ghep(db, don_hang_id=kb["d4"]) == 2
    assert so_ghep(db, don_hang_id=kb["d4"], hieu_luc=True) == 1


def test_uc13_ac9_ghep_dong_thoi_mot_don_hai_chuyen(client, dang_nhap_voi, db, kb):
    # TC-BR07-02: hai Điều phối cùng ghép Đ8 vào C01 và C02
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    c02 = lap(client, kb, xe="x4", tai_xe="dung")
    ket_qua: list = []
    cho = threading.Barrier(2)

    def gui(chuyen_id):
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieu_phoi", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua.append(ghep(c, chuyen_id, kb["d8"]))

    luong = [threading.Thread(target=gui, args=(c,)) for c in (c01, c02)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [200, 409]
    assert so_ghep(db, don_hang_id=kb["d8"], hieu_luc=True) == 1


# AC10 – gỡ đơn
def test_uc13_ac10_go_don(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    ghep(client, c01, kb["d1"], kb["d2"], kb["d4"])
    r = go(client, c01, kb["d4"])
    assert r.status_code == 200
    assert sorted(d["ma_don"] for d in r.json()["don"]) == ["DH-0001", "DH-0002"]
    assert datetime.fromisoformat(r.json()["ket_thuc_du_kien"]) == luc(12, 50)  # 4 điểm: giao Đ1 11:30
    assert trang_thai(db, kb["d4"]) == "CHO_GHEP"
    assert so_ghep(db, don_hang_id=kb["d4"], hieu_luc=False) == 1
    ls = db.scalars(select(LichSuTrangThai).where(LichSuTrangThai.sang == "CHO_GHEP")).all()
    assert [(x.doi_tuong_id, x.tu, x.nguoi) for x in ls] == [(kb["d4"], "DA_GHEP", dp.id)]
    assert db.get(Chuyen, c01).ket_thuc_du_kien == luc(12, 50)


def test_uc13_ac10_go_bi_chan(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    assert ghep(client, c01, kb["d1"], kb["d4"], kb["d2c"]).status_code == 200
    r = go(client, c01, kb["d4"])  # TC-BR67-02: lấy Đ2c dịch về 07:20 < 07:40
    assert r.status_code == 422
    assert r.json()["ma"] == "VI_PHAM_GO"
    assert [(v["don_id"], v["ma"]) for v in r.json()["chi_tiet"]] == [(kb["d2c"], "BR-05")]
    assert trang_thai(db, kb["d4"]) == "DA_GHEP"

    r = go(client, c01, kb["d8"])  # không thuộc chuyến
    assert (r.status_code, r.json()["ma"]) == (422, "DON_KHONG_THUOC_CHUYEN")
    db.get(Chuyen, c01).trang_thai = "DA_CHOT"
    db.commit()
    assert go(client, c01, kb["d1"]).status_code == 409


# AC11 – đơn phù hợp, chi tiết chuyến
def test_uc13_ac11_don_phu_hop(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    ghep(client, c01, kb["d2"])
    r = client.get(f"/api/chuyen/{c01}/don-phu-hop")
    assert r.status_code == 200
    ma = {d["ma_don"] for d in r.json()}
    assert {"DH-0001", "DH-0004", "DH-0006", "DH-0008"} <= ma
    assert not {"DH-0002", "DH-0005", "DH-0012"} & ma  # đã ghép, sai chiều, ngoài tuyến
    assert client.get("/api/chuyen/999/don-phu-hop").status_code == 404


def test_uc13_ac11_chi_tiet_lai_am(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    rong = client.get(f"/api/chuyen/{c01}").json()
    assert rong["lich_trinh"] == [] and rong["lai_du_kien"] == -1600000 and rong["canh_bao_lai_am"] is True
    c = ghep(client, c01, kb["d4"]).json()  # 800.000 − 1.000.000 − 600.000 < 0: vẫn ghép, chỉ cảnh báo
    assert c["lai_du_kien"] == -800000 and c["canh_bao_lai_am"] is True


# AC12 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "ghep_ma", "xem_ma"),
    [("DIEU_PHOI", 200, 200), ("QUAN_LY", 200, 200), ("KE_TOAN", 403, 200), ("TAI_XE", 403, 403)],
)
def test_uc13_ac12_phan_quyen(client, dang_nhap_voi, db, kb, vai_tro, ghep_ma, xem_ma):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    ghep(client, c01, kb["d1"])
    dang_nhap_voi(vai_tro)
    assert ghep(client, c01, kb["d4"]).status_code == ghep_ma
    assert go(client, c01, kb["d1"]).status_code == ghep_ma
    assert client.get(f"/api/chuyen/{c01}/don-phu-hop").status_code == ghep_ma
    assert client.get(f"/api/chuyen/{c01}").status_code == xem_ma
    if ghep_ma == 403:
        assert trang_thai(db, kb["d4"]) == "CHO_GHEP" and trang_thai(db, kb["d1"]) == "DA_GHEP"


def test_uc13_ac12_chua_dang_nhap(client, kb):
    assert ghep(client, 1, kb["d1"]).status_code == 401
    assert go(client, 1, kb["d1"]).status_code == 401
    assert client.get("/api/chuyen/1/don-phu-hop").status_code == 401
