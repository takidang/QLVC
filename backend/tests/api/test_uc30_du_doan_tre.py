# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import json
import math
from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.models import Chuyen, Ghep, LichSuTrangThai
from app.modules.goi_y import service
from tests.api.test_uc13_ghep_don import NGAY, kb, lap, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import chot, lap_c01
from tests.api.test_uc16_huy_chuyen import huy

# Chuyến lap(client, kb) của UC-13: tuyến T01 dài 270 km, 06:00 → 11:30 (5,5 giờ), Thứ Ba 22/10/2030 (weekday 1).
# Chuẩn hóa sao cho z = [1, 1, -1, 1]; đóng góp he_so*z = [0,5; -0,2; -0,3; 0,1] → logit = chan + 0,1
MO_HINH = {
    "dac_trung": ["km", "thoi_gian_gio", "gio_khoi_hanh", "thu_trong_tuan"],
    "trung_binh": [170.0, 4.5, 8.0, 0.0],
    "do_lech": [100.0, 1.0, 2.0, 1.0],
    "he_so": [0.5, -0.2, 0.3, 0.1],
    "chan": 0.0,
    "nguong": {"trung_binh": 0.3, "cao": 0.6},
    "nguon": {"dataset": "mẫu test", "ngay_train": "2026-11-19", "so_mau": 100, "auc": 0.75},
}


@pytest.fixture
def mo_hinh(tmp_path, monkeypatch):
    """Ghi file mô hình vào tmp_path và trỏ service vào đó. Truyền dict (ghi JSON) hoặc chuỗi (ghi nguyên văn)."""
    duong_dan = tmp_path / "mo_hinh_tre.json"
    monkeypatch.setattr(service, "DUONG_DAN_MO_HINH", duong_dan)

    def ghi(noi_dung=None, **doi):
        if isinstance(noi_dung, str):
            duong_dan.write_text(noi_dung, encoding="utf-8")
        else:
            duong_dan.write_text(json.dumps((noi_dung or MO_HINH) | doi), encoding="utf-8")

    return ghi


def du_doan(client, chuyen_id):
    return client.get(f"/api/chuyen/{chuyen_id}/du-doan-tre")


# AC3 – dự đoán thành công: xác suất tự tính tay, thứ tự và hướng yếu tố
def test_uc30_ac3_du_doan_thanh_cong(client, dang_nhap_voi, db, kb, mo_hinh):
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb)
    ch = db.get(Chuyen, c)
    assert (ch.khoi_hanh_du_kien, ch.ket_thuc_du_kien) == (luc(6), luc(11, 30))  # tiền đề của MO_HINH
    mo_hinh()

    r = du_doan(client, c)
    assert r.status_code == 200, r.text
    kq = r.json()
    assert kq["co_du_doan"] is True
    # 1 / (1 + e^-0,1) tính tay = 0,52497918747894
    assert kq["xac_suat"] == pytest.approx(0.52497918747894, abs=1e-12)
    assert 0 <= kq["xac_suat"] <= 1
    assert kq["muc"] == "TRUNG_BINH"
    assert kq["yeu_to"] == [
        {"ma": "km", "ten": "Quãng đường", "huong": "TANG", "gia_tri": 270.0},  # +0,5
        {"ma": "gio_khoi_hanh", "ten": "Giờ khởi hành", "huong": "GIAM", "gia_tri": 6.0},  # -0,3
        {"ma": "thoi_gian_gio", "ten": "Thời gian dự kiến", "huong": "GIAM", "gia_tri": 5.5},  # -0,2
        {"ma": "thu_trong_tuan", "ten": "Thứ trong tuần", "huong": "TANG", "gia_tri": 1.0},  # +0,1
    ]
    assert kq["nguon"] == MO_HINH["nguon"]


# AC3 – mức đúng tại biên 0,3 và 0,6 (hệ số 0, chỉ dùng chặn: xác suất = sigmoid(chan))
@pytest.mark.parametrize(
    ("chan", "xac_suat", "muc"),
    [
        (-2.0, 1 / (1 + math.e**2), "THAP"),  # ≈ 0,1192
        (math.log(3 / 7), 0.3, "TRUNG_BINH"),  # đúng biên 0,3
        (0.0, 0.5, "TRUNG_BINH"),
        (math.log(0.6 / 0.4), 0.6, "CAO"),  # đúng biên 0,6
        (5.0, 1 / (1 + math.e**-5), "CAO"),  # ≈ 0,9933
    ],
)
def test_uc30_ac3_muc_tai_bien(client, dang_nhap_voi, kb, mo_hinh, chan, xac_suat, muc):
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb)
    mo_hinh(he_so=[0.0, 0.0, 0.0, 0.0], chan=chan)
    kq = du_doan(client, c).json()
    assert kq["xac_suat"] == pytest.approx(xac_suat, abs=1e-12)
    assert kq["muc"] == muc


# AC4 – không có file / file hỏng / tính lỗi → 200, không có gợi ý
@pytest.mark.parametrize(
    "hong",
    [
        "khong_co_file",
        "chu_rac",
        "thieu_khoa",
        "thieu_nguong",
        "do_dai_lech",
        "do_lech_bang_0",
        "dac_trung_la",
        "he_so_khong_phai_so",
        "nguon_khong_phai_object",
    ],
)
def test_uc30_ac4_mo_hinh_loi_khong_co_goi_y(client, dang_nhap_voi, kb, mo_hinh, hong):
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb)
    thieu = {k: v for k, v in MO_HINH.items() if k != "he_so"}
    thieu_nguong = {k: v for k, v in MO_HINH.items() if k != "nguong"}
    ghi = {
        "khong_co_file": lambda: None,
        "chu_rac": lambda: mo_hinh("@@ không phải JSON {{{"),
        "thieu_khoa": lambda: mo_hinh(thieu),
        "thieu_nguong": lambda: mo_hinh(thieu_nguong),
        "do_dai_lech": lambda: mo_hinh(he_so=[0.5, 0.1]),
        "do_lech_bang_0": lambda: mo_hinh(do_lech=[100.0, 0.0, 2.0, 1.0]),
        "dac_trung_la": lambda: mo_hinh(dac_trung=["km", "thoi_gian_gio", "gio_khoi_hanh", "mua"]),
        "he_so_khong_phai_so": lambda: mo_hinh(he_so=["a", 0.1, 0.1, 0.1]),
        "nguon_khong_phai_object": lambda: mo_hinh(nguon="Kaggle"),
    }
    ghi[hong]()
    r = du_doan(client, c)
    assert r.status_code == 200, r.text
    assert r.json() == {"co_du_doan": False, "xac_suat": None, "muc": None, "yeu_to": None, "nguon": None}


def test_uc30_ac4_chuyen_huy_khong_co_goi_y(client, dang_nhap_voi, kb, mo_hinh):
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb)
    mo_hinh()
    assert huy(client, c).status_code == 200
    r = du_doan(client, c)
    assert r.status_code == 200
    assert r.json()["co_du_doan"] is False


def test_uc30_ac4_chuyen_khong_ton_tai(client, dang_nhap_voi, mo_hinh):
    dang_nhap_voi("DIEU_PHOI")
    mo_hinh()
    r = du_doan(client, 999999)
    assert r.status_code == 404
    assert r.json()["ma"] == "KHONG_TIM_THAY"


# AC5 – chỉ gợi ý: gọi dự đoán không đổi trạng thái, ETA, giờ dự kiến của chuyến
def test_uc30_ac5_khong_doi_du_lieu_chuyen(client, dang_nhap_voi, db, kb, mo_hinh):
    dang_nhap_voi("DIEU_PHOI")
    c = lap_c01(client, kb, "d1", "d4")
    assert chot(client, c).status_code == 200  # chốt để có ETA kế hoạch trong ghép
    mo_hinh()

    def chup():
        db.expire_all()
        ch = db.get(Chuyen, c)
        ghep = db.scalars(select(Ghep).where(Ghep.chuyen_id == c).order_by(Ghep.id)).all()
        return (
            (ch.trang_thai, ch.khoi_hanh_du_kien, ch.ket_thuc_du_kien, ch.khoi_hanh_thuc_te, ch.ket_thuc_thuc_te),
            [(g.don_hang_id, g.hieu_luc, g.eta_lay_ke_hoach, g.eta_giao_ke_hoach) for g in ghep],
            db.scalar(select(func.count()).select_from(LichSuTrangThai)),
        )

    truoc = chup()
    assert all(eta_lay and eta_giao for _, _, eta_lay, eta_giao in truoc[1])
    assert du_doan(client, c).json()["co_du_doan"] is True
    assert chup() == truoc


# AC6 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403), (None, 401)]
)
def test_uc30_ac6_phan_quyen(client, dang_nhap_voi, kb, mo_hinh, vai_tro, ma):
    dang_nhap_voi("DIEU_PHOI")
    c = lap(client, kb)
    mo_hinh()
    if vai_tro:
        dang_nhap_voi(vai_tro)
    else:
        client.cookies.clear()
    assert du_doan(client, c).status_code == ma


def du_doan_ngay(client, ngay=None):
    return client.get("/api/du-doan-tre", params={} if ngay is None else {"ngay": ngay})


def _them_chuyen(db, kb, dp_id, ma, trang_thai, khoi_hanh, thoi_gian_gio=5.5) -> Chuyen:
    c = Chuyen(
        ma_chuyen=ma,
        tuyen_id=kb["t01"],
        xe_id=kb["x1"],
        tai_xe_id=kb["an"],
        khoi_hanh_du_kien=khoi_hanh,
        ket_thuc_du_kien=khoi_hanh + timedelta(hours=thoi_gian_gio),
        dieu_phoi_id=dp_id,
        trang_thai=trang_thai,
    )
    db.add(c)
    db.commit()
    return c


# AC8(a) – chỉ LAP, DA_CHOT, DANG_CHAY; sắp theo giờ khởi hành; khớp dự đoán từng chuyến
def test_uc30_ac8_loc_trang_thai_sap_xep_va_khop_tung_chuyen(client, dang_nhap_voi, db, kb, mo_hinh):
    dp = dang_nhap_voi("DIEU_PHOI")
    c_chay = _them_chuyen(db, kb, dp.id, "CH-301022-01", "DANG_CHAY", luc(10, 0), 6.0)
    c_lap = _them_chuyen(db, kb, dp.id, "CH-301022-02", "LAP", luc(5, 0), 4.5)
    c_chot = _them_chuyen(db, kb, dp.id, "CH-301022-03", "DA_CHOT", luc(8, 0), 5.5)
    _them_chuyen(db, kb, dp.id, "CH-301022-04", "HOAN_THANH", luc(6, 0), 5.0)
    _them_chuyen(db, kb, dp.id, "CH-301022-05", "HUY", luc(7, 0), 5.0)
    mo_hinh()

    r = du_doan_ngay(client, NGAY.isoformat())
    assert r.status_code == 200, r.text
    ds = r.json()["du_lieu"]
    assert [(x["chuyen_id"], x["ma_chuyen"]) for x in ds] == [
        (c_lap.id, c_lap.ma_chuyen),
        (c_chot.id, c_chot.ma_chuyen),
        (c_chay.id, c_chay.ma_chuyen),
    ]
    for item in ds:
        rieng = du_doan(client, item["chuyen_id"]).json()
        assert rieng["co_du_doan"] is True
        assert item["muc"] == rieng["muc"]
        assert item["xac_suat"] == pytest.approx(rieng["xac_suat"], abs=1e-12)


# AC8(b) – chỉ chuyến trong ngày (theo giờ VN), không lẫn chuyến ngày khác
def test_uc30_ac8_khong_co_chuyen_ngay_khac(client, dang_nhap_voi, db, kb, mo_hinh):
    dp = dang_nhap_voi("DIEU_PHOI")
    c_trong = _them_chuyen(db, kb, dp.id, "CH-301022-10", "LAP", luc(0, 0, ngay=22))
    _them_chuyen(db, kb, dp.id, "CH-301021-10", "LAP", luc(23, 59, ngay=21))
    _them_chuyen(db, kb, dp.id, "CH-301023-10", "LAP", luc(0, 0, ngay=23))
    mo_hinh()

    r = du_doan_ngay(client, NGAY.isoformat())
    assert r.status_code == 200, r.text
    assert [x["chuyen_id"] for x in r.json()["du_lieu"]] == [c_trong.id]
    assert du_doan_ngay(client, "2030-10-25").json() == {"du_lieu": []}


# AC8(c) – không có file hoặc mô hình hỏng → 200, danh sách rỗng (KT-08)
@pytest.mark.parametrize("hong", ["khong_co_file", "chu_rac", "thieu_khoa", "do_lech_bang_0", "dac_trung_la"])
def test_uc30_ac8_mo_hinh_loi_tra_rong(client, dang_nhap_voi, kb, mo_hinh, hong):
    dang_nhap_voi("DIEU_PHOI")
    lap(client, kb)
    thieu = {k: v for k, v in MO_HINH.items() if k != "he_so"}
    ghi = {
        "khong_co_file": lambda: None,
        "chu_rac": lambda: mo_hinh("@@ không phải JSON {{{"),
        "thieu_khoa": lambda: mo_hinh(thieu),
        "do_lech_bang_0": lambda: mo_hinh(do_lech=[100.0, 0.0, 2.0, 1.0]),
        "dac_trung_la": lambda: mo_hinh(dac_trung=["km", "thoi_gian_gio", "gio_khoi_hanh", "mua"]),
    }
    ghi[hong]()
    r = du_doan_ngay(client, NGAY.isoformat())
    assert r.status_code == 200, r.text
    assert r.json() == {"du_lieu": []}


# AC8(d) – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403), (None, 401)]
)
def test_uc30_ac8_phan_quyen(client, dang_nhap_voi, kb, mo_hinh, vai_tro, ma):
    dang_nhap_voi("DIEU_PHOI")
    lap(client, kb)
    mo_hinh()
    if vai_tro:
        dang_nhap_voi(vai_tro)
    else:
        client.cookies.clear()
    assert du_doan_ngay(client, NGAY.isoformat()).status_code == ma


# AC8(e) – thiếu `ngay` hoặc sai định dạng → 400 (app/main.py đổi RequestValidationError sang 400)
@pytest.mark.parametrize("ngay", [None, "", "abc", "2030-13-45", "22/10/2030", "2030-10-22T10:00"])
def test_uc30_ac8_ngay_thieu_hoac_sai_dinh_dang(client, dang_nhap_voi, ngay):
    dang_nhap_voi("DIEU_PHOI")
    r = du_doan_ngay(client, ngay)
    assert r.status_code == 400
    assert r.json()["ma"] == "DU_LIEU_KHONG_HOP_LE"


# AC8(f) – chỉ gợi ý: gọi API theo ngày không đổi dữ liệu chuyến
def test_uc30_ac8_khong_doi_du_lieu_chuyen(client, dang_nhap_voi, db, kb, mo_hinh):
    dang_nhap_voi("DIEU_PHOI")
    c = lap_c01(client, kb, "d1", "d4")
    assert chot(client, c).status_code == 200
    mo_hinh()

    def chup():
        db.expire_all()
        ch = db.get(Chuyen, c)
        ghep = db.scalars(select(Ghep).where(Ghep.chuyen_id == c).order_by(Ghep.id)).all()
        return (
            (ch.trang_thai, ch.khoi_hanh_du_kien, ch.ket_thuc_du_kien, ch.khoi_hanh_thuc_te, ch.ket_thuc_thuc_te),
            [(g.don_hang_id, g.hieu_luc, g.eta_lay_ke_hoach, g.eta_giao_ke_hoach) for g in ghep],
            db.scalar(select(func.count()).select_from(LichSuTrangThai)),
        )

    truoc = chup()
    r = du_doan_ngay(client, NGAY.isoformat())
    assert r.status_code == 200 and len(r.json()["du_lieu"]) == 1
    assert chup() == truoc
