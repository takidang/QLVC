import threading
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models import Chuyen, LichSuTrangThai, NguoiDung, TaiXe, Tuyen, TuyenNut, Xe
from app.models import Nut as NutModel

# Ngày chạy ở tương lai (Thứ Ba) để không bị chặn "giờ đã qua"; số liệu tuyến, xe theo kịch bản mục 11
KH = "2030-10-22T06:00:00+07:00"
HAN_XA = date(2031, 12, 31)


@pytest.fixture
def kb(db):
    nut = [NutModel(ten=t, tinh=t, loai="TINH") for t in ("TP.HCM", "Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ")]
    db.add_all(nut)
    db.flush()

    def tuyen(ma, trang_thai="HOAT_DONG"):
        t = Tuyen(
            ma=ma,
            ten=f"{ma} TP.HCM – Cần Thơ",
            dm_dau=550000,
            dm_cau_duong=200000,
            dm_boc_xep=250000,
            dm_luong_tai_xe=600000,
            trang_thai=trang_thai,
        )
        db.add(t)
        db.flush()
        for i, (n, phut, km) in enumerate(zip(nut, (0, 60, 120, 210, 270), (0, 50, 75, 135, 170), strict=True), 1):
            db.add(TuyenNut(tuyen_id=t.id, thu_tu=i, nut_id=n.id, phut_tu_diem_dau=phut, km_tu_diem_dau=km))
        return t

    def xe(bien_so, ktt=9500, trang_thai="HOAT_DONG"):
        x = Xe(
            bien_so=bien_so,
            tai_trong_kg=5000,
            the_tich_m3=20,
            ktt_toan_bo_kg=ktt,
            han_dang_kiem=HAN_XA,
            han_bao_hiem=HAN_XA,
            trang_thai=trang_thai,
        )
        db.add(x)
        return x

    def tai_xe(ten, hang):
        nd = NguoiDung(ten_dang_nhap=ten.lower(), ho_ten=ten, vai_tro="TAI_XE", mat_khau_bam="-")
        db.add(nd)
        db.flush()
        tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=f"GPLX{nd.id}00", hang_gplx=hang, han_gplx=HAN_XA, sdt="0909000000")
        db.add(tx)
        return tx

    ds = {
        "t01": tuyen("T01"),
        "t_ngung": tuyen("T09", "NGUNG"),
        "x1": xe("51C-111.11"),
        "x3": xe("51C-333.33", trang_thai="NGUNG"),
        "x4": xe("51C-444.44"),
        "an": tai_xe("An", "C"),
        "binh": tai_xe("Bình", "B"),
        "dung": tai_xe("Dũng", "C"),
    }
    db.commit()
    return {k: v.id for k, v in ds.items()}


def vao(kb, **doi):
    return {"tuyen_id": kb["t01"], "khoi_hanh_du_kien": KH, "xe_id": kb["x1"], "tai_xe_id": kb["an"]} | doi


def lap(client, kb, **doi):
    return client.post("/api/chuyen", json=vao(kb, **doi))


def dem(db, bang=Chuyen):
    return db.scalar(select(func.count()).select_from(bang))


# AC6 – lập chuyến hợp lệ
def test_uc11_ac6_lap_chuyen(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    r = lap(client, kb)
    assert r.status_code == 201
    c = r.json()
    assert c["trang_thai"] == "LAP"
    assert c["ma_chuyen"] == "CH-301022-01"
    assert datetime.fromisoformat(c["ket_thuc_du_kien"]) == datetime.fromisoformat("2030-10-22T11:30:00+07:00")
    assert (c["ma_tuyen"], c["bien_so"], c["ten_tai_xe"]) == ("T01", "51C-111.11", "An")

    chuyen = db.get(Chuyen, c["id"])
    assert chuyen.dieu_phoi_id == dp.id
    ls = db.scalars(select(LichSuTrangThai).where(LichSuTrangThai.doi_tuong == "CHUYEN")).all()
    assert [(x.doi_tuong_id, x.tu, x.sang, x.nguoi) for x in ls] == [(c["id"], None, "LAP", dp.id)]

    # Chuyến thứ hai cùng ngày khởi hành: số thứ tự tăng
    r2 = lap(client, kb, xe_id=kb["x4"], tai_xe_id=kb["dung"])
    assert r2.json()["ma_chuyen"] == "CH-301022-02"


# AC7 – bị chặn, không tạo gì
def test_uc11_ac7_vi_pham_bao_du(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    r = lap(client, kb, tai_xe_id=kb["binh"])  # TC-BR14-02
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-14"

    r = lap(client, kb, xe_id=kb["x3"], tai_xe_id=kb["binh"])  # hai vi phạm: báo đủ, mã là cái đầu
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-11"
    assert [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-11", "BR-14"]
    assert all(v["thong_diep"] for v in r.json()["chi_tiet"])
    assert dem(db) == 0
    assert dem(db, LichSuTrangThai) == 0


def test_uc11_ac7_trung_lich_xe_va_tai_xe(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    assert lap(client, kb).status_code == 201  # [06:00, 11:30)
    r = lap(client, kb, tai_xe_id=kb["dung"], khoi_hanh_du_kien="2030-10-22T10:00:00+07:00")
    assert (r.status_code, r.json()["ma"]) == (422, "BR-16")  # TC-BR16-01
    r = lap(client, kb, xe_id=kb["x4"], khoi_hanh_du_kien="2030-10-22T11:00:00+07:00")
    assert (r.status_code, r.json()["ma"]) == (422, "BR-17")  # TC-BR17-01
    assert lap(client, kb, khoi_hanh_du_kien="2030-10-22T11:30:00+07:00").status_code == 201  # biên nửa mở
    assert dem(db) == 2


def test_uc11_ac7_chuyen_huy_khong_tinh(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    db.get(Chuyen, lap(client, kb).json()["id"]).trang_thai = "HUY"
    db.commit()
    assert lap(client, kb).status_code == 201


@pytest.mark.parametrize(
    ("doi", "mong_doi", "ma"),
    [
        ({"xe_id": None}, 400, None),
        ({"tai_xe_id": None}, 400, None),
        ({"khoi_hanh_du_kien": "2030-10-22T06:00:00"}, 400, None),  # thiếu múi giờ
        ({"tuyen_id": 999}, 404, "KHONG_TIM_THAY"),
        ({"xe_id": 999}, 404, "KHONG_TIM_THAY"),
        ({"tai_xe_id": 999}, 404, "KHONG_TIM_THAY"),
        ({"tuyen_id": "t_ngung"}, 422, "TUYEN_NGUNG"),
        ({"khoi_hanh_du_kien": "2020-10-22T06:00:00+07:00"}, 422, "KHOI_HANH_DA_QUA"),
    ],
)
def test_uc11_ac7_du_lieu_sai(client, dang_nhap_voi, db, kb, doi, mong_doi, ma):
    dang_nhap_voi("DIEU_PHOI")
    doi = {k: kb[v] if v in kb else v for k, v in doi.items()}
    du_lieu = {k: v for k, v in vao(kb, **doi).items() if v is not None}
    r = client.post("/api/chuyen", json=du_lieu)
    assert r.status_code == mong_doi
    if ma:
        assert r.json()["ma"] == ma
    assert dem(db) == 0


# AC8 – hai người lập cùng lúc cùng xe
def test_uc11_ac8_lap_dong_thoi_chi_mot_thanh_cong(dang_nhap_voi, client, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    ket_qua: list = []
    cho = threading.Barrier(2)

    def gui(tai_xe_id):
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieu_phoi", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua.append(c.post("/api/chuyen", json=vao(kb, tai_xe_id=tai_xe_id)))

    luong = [threading.Thread(target=gui, args=(tx,)) for tx in (kb["an"], kb["dung"])]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [201, 422]
    assert next(r for r in ket_qua if r.status_code == 422).json()["ma"] == "BR-16"
    assert dem(db) == 1


# AC9 – danh sách xe, tài xế khả dụng kèm lý do
def test_uc11_ac9_xe_kha_dung(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    ds = client.get("/api/chuyen/xe-kha-dung", params={"tuyen_id": kb["t01"], "khoi_hanh": KH})
    assert ds.status_code == 200  # route cố định, không bị hiểu là /{chuyen_id}
    theo_bien = {x["bien_so"]: x for x in ds.json()}
    assert theo_bien["51C-111.11"]["kha_dung"] is True
    assert theo_bien["51C-333.33"]["kha_dung"] is False
    assert [v["ma"] for v in theo_bien["51C-333.33"]["ly_do"]] == ["BR-11"]
    assert ds.json()[-1]["bien_so"] == "51C-333.33"  # khả dụng xếp trước

    assert lap(client, kb).status_code == 201
    ds = client.get("/api/chuyen/xe-kha-dung", params={"tuyen_id": kb["t01"], "khoi_hanh": "2030-10-22T10:00:00+07:00"})
    x1 = next(x for x in ds.json() if x["bien_so"] == "51C-111.11")
    assert x1["kha_dung"] is False and x1["ly_do"][0]["ma"] == "BR-16"
    assert "CH-301022-01" in x1["ly_do"][0]["thong_diep"]


def test_uc11_ac9_tai_xe_kha_dung(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    p = {"tuyen_id": kb["t01"], "khoi_hanh": KH}
    r = client.get("/api/chuyen/tai-xe-kha-dung", params=p)
    assert r.status_code == 200
    assert all(t["kha_dung"] for t in r.json())  # chưa chọn xe: chưa xét hạng GPLX

    r = client.get("/api/chuyen/tai-xe-kha-dung", params=p | {"xe_id": kb["x1"]})
    binh = next(t for t in r.json() if t["ho_ten"] == "Bình")
    assert binh["kha_dung"] is False and [v["ma"] for v in binh["ly_do"]] == ["BR-14"]
    assert r.json()[-1]["ho_ten"] == "Bình"
    assert client.get("/api/chuyen/tai-xe-kha-dung", params=p | {"xe_id": 999}).status_code == 404
    assert client.get("/api/chuyen/xe-kha-dung", params={"tuyen_id": kb["t01"]}).status_code == 400
    assert client.get("/api/chuyen/xe-kha-dung", params={"tuyen_id": 999, "khoi_hanh": KH}).status_code == 404


# AC10 – danh sách, chi tiết
def test_uc11_ac10_danh_sach_va_chi_tiet(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    c1 = lap(client, kb).json()
    lap(client, kb, xe_id=kb["x4"], tai_xe_id=kb["dung"], khoi_hanh_du_kien="2030-10-23T06:00:00+07:00")

    def ds(**p):
        return client.get("/api/chuyen", params=p).json()

    assert ds()["tong"] == 2
    assert [c["ma_chuyen"] for c in ds()["du_lieu"]] == ["CH-301023-01", "CH-301022-01"]  # mới khởi hành sau lên trước
    assert [c["ma_chuyen"] for c in ds(ngay="2030-10-22")["du_lieu"]] == ["CH-301022-01"]
    assert ds(trang_thai="LAP")["tong"] == 2 and ds(trang_thai="HUY")["tong"] == 0
    assert ds(tuyen_id=kb["t01"])["tong"] == 2 and ds(tuyen_id=kb["t_ngung"])["tong"] == 0
    trang2 = ds(trang=2, so_dong=1)
    assert trang2["tong"] == 2 and len(trang2["du_lieu"]) == 1
    assert client.get("/api/chuyen", params={"trang_thai": "XOA"}).status_code == 400

    assert client.get(f"/api/chuyen/{c1['id']}").json() == c1
    assert client.get("/api/chuyen/999").status_code == 404


# AC11 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "lap_ma", "kha_dung_ma", "xem_ma"),
    [
        ("DIEU_PHOI", 201, 200, 200),
        ("QUAN_LY", 201, 200, 200),
        ("KE_TOAN", 403, 403, 200),
        ("TAI_XE", 403, 403, 403),
    ],
)
def test_uc11_ac11_phan_quyen(client, dang_nhap_voi, db, kb, vai_tro, lap_ma, kha_dung_ma, xem_ma):
    dang_nhap_voi("DIEU_PHOI")
    co_san = lap(client, kb).json()["id"]  # chuyến có sẵn để thử xem chi tiết
    dang_nhap_voi(vai_tro)
    assert lap(client, kb, khoi_hanh_du_kien="2030-10-23T06:00:00+07:00").status_code == lap_ma
    p = {"tuyen_id": kb["t01"], "khoi_hanh": KH}
    assert client.get("/api/chuyen/xe-kha-dung", params=p).status_code == kha_dung_ma
    assert client.get("/api/chuyen/tai-xe-kha-dung", params=p).status_code == kha_dung_ma
    assert client.get("/api/chuyen").status_code == xem_ma
    assert client.get(f"/api/chuyen/{co_san}").status_code == xem_ma
    if lap_ma == 403:
        assert dem(db) == 1


def test_uc11_ac11_chua_dang_nhap(client, kb):
    assert lap(client, kb).status_code == 401
    assert client.get("/api/chuyen").status_code == 401
    assert client.get("/api/chuyen/xe-kha-dung", params={"tuyen_id": kb["t01"], "khoi_hanh": KH}).status_code == 401
    assert client.get("/api/chuyen/1").status_code == 401
