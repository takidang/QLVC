# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
import importlib.util
import threading
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import luu_tru
from app.domain.ly_do import LY_DO
from app.main import app
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, TaiXe, Tep
from tests.api.test_uc17_xem_chuyen import kb, luc  # noqa: F401 (kb là fixture)

JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
GPS = {"lat": "10.776900", "lng": "106.700900", "do_chinh_xac_m": "12.5"}
LY_DO_LAY, LY_DO_GIAO = 1, 7  # id theo thứ tự nạp: "Hàng chưa chuẩn bị xong", "Người nhận vắng"


def dang_nhap(client, ten="an"):
    r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": "matkhau123"})
    assert r.status_code == 200


def quet(client, ma="DH-0001", loai="LAY", gps=GPS, anh=(), **them):
    data = {"ma_don": ma, "loai": loai, **(gps or {}), **them}
    files = [("anh", (f"a{i}.jpg", b, "image/jpeg")) for i, b in enumerate(anh)]
    return client.post("/api/toi/quet", data=data, files=files or None)


def trang_thai(db, don) -> str:
    return db.scalar(select(DonHang.trang_thai).where(DonHang.id == don.id))


def luot(db, don) -> list[LuotQuet]:
    db.expire_all()
    return list(db.scalars(select(LuotQuet).join(Ghep, Ghep.id == LuotQuet.ghep_id).where(Ghep.don_hang_id == don.id)))


def so_tep(db) -> int:
    return db.scalar(select(func.count()).select_from(Tep))


@pytest.fixture
def ch(db, kb, client, tmp_path, monkeypatch):
    """C01 của An (Đ1, Đ2, Đ4) đang chạy; ảnh ghi vào thư mục tạm; client đăng nhập An."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    kb["c01"].trang_thai, kb["c01"].km_bat_dau = "DANG_CHAY", 50000
    db.commit()
    dang_nhap(client)
    return kb | {"thu_muc": tmp_path}


def dat_chuyen(db, c, trang_thai):
    db.get(Chuyen, c.id).trang_thai = trang_thai
    db.commit()


# AC1 – quét lấy hợp lệ có GPS
def test_uc19_ac1_quet_lay_hop_le(client, db, ch):
    truoc = datetime.now(UTC)
    r = quet(client, " dh-0001 ")  # gõ thường, có khoảng trắng (TC-BR38-01)
    assert r.status_code == 200, r.text
    assert r.json() == {"ma_don": "DH-0001", "trang_thai": "DA_LAY", "canh_bao": [], "lap_lai": False}
    assert trang_thai(db, ch["d1"]) == "DA_LAY"

    (lq,) = luot(db, ch["d1"])
    assert (lq.loai, lq.lat, lq.lng, lq.do_chinh_xac_m, lq.thieu_gps, lq.ly_do_id) == (
        "LAY",
        Decimal("10.776900"),
        Decimal("106.700900"),
        Decimal("12.5"),
        False,
        None,
    )
    assert lq.tai_xe_id == ch["an"].id
    assert truoc - timedelta(seconds=5) <= lq.thoi_gian <= datetime.now(UTC)  # giờ máy chủ (BR-43)
    ls = db.execute(
        select(LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.ly_do, LichSuTrangThai.nguoi).where(
            LichSuTrangThai.doi_tuong == "DON", LichSuTrangThai.doi_tuong_id == ch["d1"].id
        )
    ).all()
    assert ls == [("DA_GHEP", "DA_LAY", None, ch["an"].nguoi_dung_id)]
    assert trang_thai(db, ch["d2"]) == "DA_GHEP"  # đơn khác của chuyến không đổi


# AC2 – GPS
def test_uc19_ac2_thieu_gps_van_quet(client, db, ch):
    r = quet(client, gps=None)  # TC-BR43-01
    assert r.status_code == 200, r.text
    assert (r.json()["trang_thai"], r.json()["canh_bao"]) == ("DA_LAY", ["THIEU_GPS"])
    (lq,) = luot(db, ch["d1"])
    assert (lq.thieu_gps, lq.lat, lq.lng) == (True, None, None)


@pytest.mark.parametrize(
    ("gps", "ma"),
    [
        ({"lat": "10.7"}, 400),  # gửi một nửa (quyết định 5)
        ({"lng": "106.7"}, 400),
        ({"lat": "91", "lng": "106.7"}, 400),
        ({"lat": "10.7", "lng": "-180.000001"}, 400),
        ({"lat": "10.7", "lng": "106.7", "do_chinh_xac_m": "-1"}, 400),
        ({"lat": "abc", "lng": "106.7"}, 400),
        ({"lat": "90", "lng": "-180"}, 200),  # biên
        ({"lat": "-90", "lng": "180", "do_chinh_xac_m": "0"}, 200),
    ],
    ids=["chi-lat", "chi-lng", "lat-91", "lng-vuot", "chinh-xac-am", "chu", "bien-1", "bien-2"],
)
def test_uc19_ac2_gps_khong_hop_le(client, db, ch, gps, ma):
    assert quet(client, gps=gps).status_code == ma
    assert trang_thai(db, ch["d1"]) == ("DA_LAY" if ma == 200 else "DA_GHEP")
    assert len(luot(db, ch["d1"])) == (1 if ma == 200 else 0)


# AC3 – báo không lấy được hợp lệ
def test_uc19_ac3_khong_lay_duoc(client, db, ch):
    r = quet(client, "DH-0004", "KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY)  # TC-BR39-01
    assert r.status_code == 200, r.text
    assert r.json() == {"ma_don": "DH-0004", "trang_thai": "THAT_BAI", "canh_bao": [], "lap_lai": False}
    assert trang_thai(db, ch["d4"]) == "THAT_BAI"

    (lq,) = luot(db, ch["d4"])
    assert (lq.loai, lq.ly_do_id) == ("KHONG_LAY", LY_DO_LAY)
    (tep,) = db.scalars(select(Tep).where(Tep.luot_quet_id == lq.id))
    assert (tep.loai, tep.kich_thuoc) == ("ANH", len(JPG))
    assert (ch["thu_muc"] / tep.duong_dan).read_bytes() == JPG  # file thật, tên do máy chủ sinh
    assert tep.duong_dan.endswith(".jpg") and "a0" not in tep.duong_dan

    ly_do = db.scalar(
        select(LichSuTrangThai.ly_do).where(
            LichSuTrangThai.doi_tuong_id == ch["d4"].id, LichSuTrangThai.sang == "THAT_BAI"
        )
    )
    assert ly_do == "Hàng chưa chuẩn bị xong"
    g = db.execute(select(Ghep.ket_qua, Ghep.hieu_luc).where(Ghep.don_hang_id == ch["d4"].id)).one()
    assert tuple(g) == ("THAT_BAI", True)  # gỡ hiệu lực khi kết thúc chuyến (BR-36, UC-18)


def test_uc19_ac3_hai_anh_hai_tep(client, db, ch):
    r = quet(client, "DH-0004", "KHONG_LAY", anh=[JPG, PNG], ly_do_id=6)  # "Xe hỏng" phía SU_CO_XE
    assert r.status_code == 200, r.text
    (lq,) = luot(db, ch["d4"])
    duoi = sorted(Path(t).suffix for t in db.scalars(select(Tep.duong_dan).where(Tep.luot_quet_id == lq.id)))
    assert duoi == [".jpg", ".png"]
    assert len(list(ch["thu_muc"].iterdir())) == 2


# AC4 – thiếu lý do / ảnh, ảnh sai
@pytest.mark.parametrize(
    ("them", "anh", "ma", "ma_loi"),
    [
        ({}, [JPG], 422, "BR-42"),  # thiếu lý do
        ({"ly_do_id": 999}, [JPG], 422, "BR-42"),  # lý do không tồn tại
        ({"ly_do_id": LY_DO_GIAO}, [JPG], 422, "BR-42"),  # lý do của GIAO
        ({"ly_do_id": LY_DO_LAY}, [], 422, "BR-42"),  # thiếu ảnh
        ({"ly_do_id": LY_DO_LAY}, [b"GIF89a" + b"0" * 50], 400, "ANH_SAI_LOAI"),
        ({"ly_do_id": LY_DO_LAY}, [JPG, b"GIF89a"], 400, "ANH_SAI_LOAI"),  # một ảnh sai thì không lưu ảnh nào
        ({"ly_do_id": LY_DO_LAY}, [b"\xff\xd8\xff" + b"0" * (500 * 1024 - 2)], 413, "ANH_QUA_LON"),
    ],
    ids=["thieu-ly-do", "ly-do-khong-co", "ly-do-giao", "thieu-anh", "gif", "mot-anh-sai", "qua-500kb"],
)
def test_uc19_ac4_khong_lay_thieu_hoac_sai(client, db, ch, them, anh, ma, ma_loi):
    r = quet(client, "DH-0004", "KHONG_LAY", anh=anh, **them)
    assert (r.status_code, r.json()["ma"]) == (ma, ma_loi)
    assert trang_thai(db, ch["d4"]) == "DA_GHEP"
    assert luot(db, ch["d4"]) == []
    assert so_tep(db) == 0 and list(ch["thu_muc"].iterdir()) == []


def test_uc19_ac4_anh_dung_500kb(client, db, ch):
    anh = b"\xff\xd8\xff" + b"0" * (500 * 1024 - 3)  # đúng 500 KB: biên được nhận
    assert quet(client, "DH-0004", "KHONG_LAY", anh=[anh], ly_do_id=LY_DO_LAY).status_code == 200


# AC5 – đơn không thuộc chuyến của mình: cùng 403
def test_uc19_ac5_khong_thuoc_chuyen(client, db, ch):
    d5 = ch["don"](5, "TP.HCM", "Cần Thơ", 100, 1, luc(14))
    ch["chuyen"](ch["binh"], "DANG_CHAY", 6, 22, d5)  # đơn của chuyến Bình (TC-BR38-02)
    d6 = ch["don"](6, "TP.HCM", "Cần Thơ", 100, 1, luc(14), trang_thai="CHO_GHEP")  # chưa ghép

    tra_loi = [quet(client, ma) for ma in ("DH-0005", "DH-0006", "DH-9999")]
    assert {(r.status_code, r.json()["ma"], r.json()["thong_diep"]) for r in tra_loi} == {
        (403, "BR-38", "Đơn không thuộc chuyến của bạn")
    }
    assert (trang_thai(db, d5), trang_thai(db, d6)) == ("DA_GHEP", "CHO_GHEP")
    assert db.scalar(select(func.count()).select_from(LuotQuet)) == 0


def test_uc19_ac5_ghep_het_hieu_luc(client, db, ch):
    db.execute(Ghep.__table__.update().where(Ghep.don_hang_id == ch["d1"].id).values(hieu_luc=False))
    db.commit()
    assert quet(client).status_code == 403  # chỉ ghép hiệu lực mới tính (BR-38)


# AC6 – chuyến của mình nhưng không đang chạy
@pytest.mark.parametrize("tt", ["DA_CHOT", "HOAN_THANH"])
def test_uc19_ac6_chuyen_khong_dang_chay(client, db, ch, tt):
    dat_chuyen(db, ch["c01"], tt)
    r = quet(client)  # TC-BR38-03
    assert (r.status_code, r.json()["ma"]) == (409, "BR-38")
    assert trang_thai(db, ch["d1"]) == "DA_GHEP"
    assert luot(db, ch["d1"]) == []


# AC7 – quét lặp cùng ý / trái kết quả
def test_uc19_ac7_quet_lay_lan_hai(client, db, ch):
    assert quet(client).status_code == 200
    r = quet(client, gps=None)  # TC-BR45-01: mạng chập chờn gửi lại
    assert r.status_code == 200
    assert r.json() == {"ma_don": "DH-0001", "trang_thai": "DA_LAY", "canh_bao": [], "lap_lai": True}
    assert len(luot(db, ch["d1"])) == 1


def test_uc19_ac7_khong_lay_lan_hai(client, db, ch):
    assert quet(client, "DH-0004", "KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY).status_code == 200
    r = quet(client, "DH-0004", "KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY)
    assert (r.status_code, r.json()["lap_lai"], r.json()["trang_thai"]) == (200, True, "THAT_BAI")
    assert len(luot(db, ch["d4"])) == 1
    assert so_tep(db) == 1 and len(list(ch["thu_muc"].iterdir())) == 1  # lần hai không lưu ảnh


def test_uc19_ac7_khong_lay_don_da_lay(client, db, ch):
    assert quet(client).status_code == 200
    r = quet(client, "DH-0001", "KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY)  # TC-BR39-02
    assert (r.status_code, r.json()["ma"]) == (409, "BR-39")
    assert r.json()["chi_tiet"][0]["trang_thai"] == "DA_LAY"
    assert trang_thai(db, ch["d1"]) == "DA_LAY"
    assert len(luot(db, ch["d1"])) == 1 and so_tep(db) == 0


def test_uc19_ac7_lay_don_that_bai(client, db, ch):
    assert quet(client, "DH-0004", "KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY).status_code == 200
    r = quet(client, "DH-0004")
    assert (r.status_code, r.json()["ma"]) == (409, "BR-39")
    assert trang_thai(db, ch["d4"]) == "THAT_BAI"


def test_uc19_ac7_lay_don_da_giao(client, db, ch):
    db.get(DonHang, ch["d1"].id).trang_thai = "DA_GIAO"
    db.commit()
    r = quet(client)  # đơn đã giao thì chắc chắn đã lấy: cùng ý
    assert (r.status_code, r.json()["lap_lai"], r.json()["trang_thai"]) == (200, True, "DA_GIAO")


# AC8 – hai lượt lấy cùng đơn gửi cùng lúc
def test_uc19_ac8_quet_dong_thoi(db, ch, tmp_path):
    ket_qua = []
    cho = threading.Barrier(2)

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            dang_nhap(c)
            cho.wait()
            ket_qua.append(quet(c))

    luong = [threading.Thread(target=gui) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [200, 200]
    assert sorted(r.json()["lap_lai"] for r in ket_qua) == [False, True]
    assert len(luot(db, ch["d1"])) == 1


# AC9 – loại, trường thiếu, trường lạ
@pytest.mark.parametrize("loai", ["GIAO", "GIAO_THAT_BAI", "XYZ", "lay"])
def test_uc19_ac9_loai_chua_lam_hoac_la(client, db, ch, loai):
    assert quet(client, loai=loai).status_code == 400
    assert trang_thai(db, ch["d1"]) == "DA_GHEP"


def test_uc19_ac9_thieu_ma_don(client, ch):
    r = client.post("/api/toi/quet", data={"loai": "LAY"})
    assert r.status_code == 400
    assert quet(client, "").status_code == 400


@pytest.mark.parametrize(
    "them", [{"thoi_gian": "2030-10-22T06:00:00+07:00"}, {"tai_xe_id": "99"}], ids=["thoi-gian", "truong-la"]
)
def test_uc19_ac9_truong_la(client, db, ch, them):
    r = quet(client, **them)  # TC-BR43-02: giờ quét do máy chủ ghi
    assert (r.status_code, r.json()["ma"]) == (400, "DU_LIEU_KHONG_HOP_LE")
    assert luot(db, ch["d1"]) == []


def test_uc19_ac9_lay_gui_kem_anh_ly_do(client, db, ch):
    r = quet(client, anh=[JPG], ly_do_id=LY_DO_LAY)  # quyết định 7: bỏ qua, không lưu
    assert (r.status_code, r.json()["trang_thai"]) == (200, "DA_LAY")
    (lq,) = luot(db, ch["d1"])
    assert lq.ly_do_id is None
    assert so_tep(db) == 0 and list(ch["thu_muc"].iterdir()) == []


# AC10 – danh mục lý do
def test_uc19_ac10_danh_muc_ly_do(client, dang_nhap_voi):
    dang_nhap_voi("TAI_XE")
    lay = client.get("/api/danh-muc/ly-do", params={"ap_dung": "LAY"}).json()
    assert [(x["ten"], x["ap_dung"], x["phia"]) for x in lay] == [x for x in LY_DO if x[1] == "LAY"]
    assert {x["id"] for x in lay} == {1, 2, 3, 4, 5, 6}
    giao = client.get("/api/danh-muc/ly-do", params={"ap_dung": "GIAO"}).json()
    assert {x["ap_dung"] for x in giao} == {"GIAO"} and len(giao) == 6
    assert len(client.get("/api/danh-muc/ly-do").json()) == 12
    assert client.get("/api/danh-muc/ly-do", params={"ap_dung": "XYZ"}).status_code == 400


@pytest.mark.parametrize(("vai_tro", "ma"), [("TAI_XE", 200), ("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403)])
def test_uc19_ac10_phan_quyen_ly_do(client, dang_nhap_voi, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/danh-muc/ly-do").status_code == ma


def test_uc19_ac10_chua_dang_nhap(client):
    assert client.get("/api/danh-muc/ly-do").status_code == 401


# AC11 – phân quyền quét
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "QUAN_LY"])
def test_uc19_ac11_vai_tro_khac_bi_chan(client, db, kb, dang_nhap_voi, vai_tro):
    kb["c01"].trang_thai = "DANG_CHAY"
    db.commit()
    dang_nhap_voi(vai_tro)
    assert quet(client).status_code == 403
    assert trang_thai(db, kb["d1"]) == "DA_GHEP"


def test_uc19_ac11_tai_khoan_tai_xe_khong_ho_so(client, db, kb, dang_nhap_voi):
    kb["c01"].trang_thai = "DANG_CHAY"
    db.commit()
    dang_nhap_voi("TAI_XE")  # vai trò tài xế nhưng không có hồ sơ TAI_XE
    assert db.scalar(select(func.count()).select_from(TaiXe)) == 2
    assert (quet(client).status_code, trang_thai(db, kb["d1"])) == (403, "DA_GHEP")


def test_uc19_ac11_chua_dang_nhap(client, kb):
    assert quet(client).status_code == 401


# AC12 – migration nạp đúng danh mục (conftest còn so lại sau khi chạy migration thật)
def test_uc19_ac12_migration_khop_danh_muc():
    tep = next((Path(__file__).parents[2] / "alembic" / "versions").glob("*uc19_nap_danh_muc_ly_do.py"))
    spec = importlib.util.spec_from_file_location("mig_ly_do", tep)
    mig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mig)
    assert tuple(mig.LY_DO) == LY_DO
    assert len(LY_DO) == 12 and sum(a == "LAY" for _, a, _ in LY_DO) == 6
    assert {p for *_, p in LY_DO} == {"KHACH", "SU_CO_XE"}
