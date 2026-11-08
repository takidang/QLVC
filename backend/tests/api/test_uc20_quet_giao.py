# ruff: noqa: F811  (kb, ch là fixture nhập từ test UC-17, UC-19, dùng làm tham số)
import io
import threading
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, NhatKyTien, PhaiThu, Tep
from app.modules.quet.service import LAM
from tests.api.test_uc17_xem_chuyen import kb, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc19_quet_lay import (  # noqa: F401 (ch là fixture)
    GPS,
    JPG,
    LY_DO_GIAO,
    LY_DO_LAY,
    PNG,
    ch,
    dang_nhap,
    dat_chuyen,
    luot,
    quet,
    so_tep,
    trang_thai,
)

CUOC = 1234000  # cuoc_tinh của đơn trong fixture kb
TEN = "Lê Văn Nhận"


def giao(client, ma="DH-0001", anh=(JPG,), ky=PNG, ten=TEN, gps=GPS, loai="GIAO", **them):
    data = {"ma_don": ma, "loai": loai, **(gps or {}), **them}
    if ten is not None:
        data["ten_nguoi_nhan"] = ten
    files = [("anh", (f"a{i}.jpg", b, "image/jpeg")) for i, b in enumerate(anh)]
    if ky is not None:
        files.append(("chu_ky", ("ky.png", ky, "image/png")))
    return client.post("/api/toi/quet", data=data, files=files or None)


def bao_giao_khong_duoc(client, ma="DH-0001", anh=(JPG,), ly_do_id=LY_DO_GIAO):
    them = {} if ly_do_id is None else {"ly_do_id": ly_do_id}
    return giao(client, ma, anh=anh, ky=None, ten=None, loai="GIAO_THAT_BAI", **them)


def phai_thu(db) -> list[tuple]:
    return db.execute(select(PhaiThu.don_hang_id, PhaiThu.so_tien, PhaiThu.trang_thai_tt)).all()


def dem(db, bang) -> int:
    return db.scalar(select(func.count()).select_from(bang))


def ghep_cua(db, don):
    return db.execute(
        select(Ghep.ket_qua, Ghep.giao_tre, Ghep.hieu_luc).where(Ghep.don_hang_id == don.id, Ghep.hieu_luc)
    ).one()


@pytest.fixture
def gh(db, ch):
    """C01 đang chạy của An: Đ1, Đ4 đã lấy (giao được), Đ2 còn chờ lấy; hạn giao năm 2030 nên chưa trễ."""
    for ten in ("d1", "d4"):
        db.get(DonHang, ch[ten].id).trang_thai = "DA_LAY"
    db.commit()
    return ch


def dat_han(db, don, han):
    db.get(DonHang, don.id).han_giao = han
    db.commit()


# AC1 – giao hợp lệ
def test_uc20_ac1_giao_hop_le(client, db, gh):
    truoc = datetime.now(UTC)
    r = giao(client, " dh-0001 ")  # TC-BR40-01, TC-BR41-01
    assert r.status_code == 200, r.text
    assert r.json() == {"ma_don": "DH-0001", "trang_thai": "DA_GIAO", "canh_bao": [], "lap_lai": False}
    assert trang_thai(db, gh["d1"]) == "DA_GIAO"

    (lq,) = luot(db, gh["d1"])
    assert (lq.loai, lq.ten_nguoi_nhan, lq.lat, lq.thieu_gps, lq.ly_do_id) == (
        "GIAO",
        TEN,
        Decimal("10.776900"),
        False,
        None,
    )
    assert truoc - timedelta(seconds=5) <= lq.thoi_gian <= datetime.now(UTC)
    tep = {t.loai: t for t in db.scalars(select(Tep).where(Tep.luot_quet_id == lq.id))}
    assert set(tep) == {"ANH", "CHU_KY"}
    assert (gh["thu_muc"] / tep["CHU_KY"].duong_dan).read_bytes() == PNG
    assert tep["CHU_KY"].duong_dan.endswith(".png") and tep["ANH"].duong_dan.endswith(".jpg")
    assert tuple(ghep_cua(db, gh["d1"])) == ("DA_GIAO", False, True)
    ls = db.execute(
        select(LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.nguoi).where(
            LichSuTrangThai.doi_tuong == "DON", LichSuTrangThai.doi_tuong_id == gh["d1"].id
        )
    ).all()
    assert ls == [("DA_LAY", "DA_GIAO", gh["an"].nguoi_dung_id)]


# AC2 – phải thu và nhật ký tiền
def test_uc20_ac2_sinh_phai_thu(client, db, gh):
    assert giao(client).status_code == 200
    assert bao_giao_khong_duoc(client, "DH-0004").status_code == 200  # TC-BR56-01: thất bại không sinh
    assert phai_thu(db) == [(gh["d1"].id, CUOC, "CHUA_THU")]
    nk = db.execute(select(NhatKyTien.bang, NhatKyTien.hanh_dong, NhatKyTien.gia_tri_moi, NhatKyTien.nguoi)).all()
    assert nk == [("phai_thu", "TAO", str(CUOC), gh["an"].nguoi_dung_id)]


# AC3 – giao trễ
def test_uc20_ac3_giao_tre(client, db, gh):
    dat_han(db, gh["d1"], datetime.now(UTC) - timedelta(minutes=1))
    r = giao(client, gps=None)  # TC-BR72-01
    assert (r.status_code, r.json()["trang_thai"]) == (200, "DA_GIAO")
    assert r.json()["canh_bao"] == ["THIEU_GPS", "GIAO_TRE"]
    assert tuple(ghep_cua(db, gh["d1"])) == ("DA_GIAO", True, True)
    assert phai_thu(db) == [(gh["d1"].id, CUOC, "CHUA_THU")]  # không giảm cước


def test_uc20_ac3_giao_dung_han(client, db, gh):
    dat_han(db, gh["d1"], datetime.now(UTC) + timedelta(hours=1))
    r = giao(client)  # TC-BR72-02
    assert r.json()["canh_bao"] == []
    assert ghep_cua(db, gh["d1"]).giao_tre is False


# AC4 – thiếu ảnh, chữ ký, tên
@pytest.mark.parametrize(
    ("them", "ma", "ma_loi"),
    [
        ({"ky": None}, 422, "BR-41"),
        ({"anh": ()}, 422, "BR-41"),
        ({"ten": None}, 422, "BR-41"),
        ({"ten": "   "}, 422, "BR-41"),
        ({"ten": "x" * 101}, 400, "DU_LIEU_KHONG_HOP_LE"),
    ],
    ids=["thieu-chu-ky", "thieu-anh", "thieu-ten", "ten-trang", "ten-101"],
)
def test_uc20_ac4_thieu_bang_chung(client, db, gh, them, ma, ma_loi):
    r = giao(client, **them)  # TC-BR41-02
    assert (r.status_code, r.json()["ma"]) == (ma, ma_loi)
    assert trang_thai(db, gh["d1"]) == "DA_LAY"
    assert luot(db, gh["d1"]) == [] and so_tep(db) == 0 and phai_thu(db) == []
    assert list(gh["thu_muc"].iterdir()) == []


def test_uc20_ac4_ten_dung_100_ky_tu(client, db, gh):
    assert giao(client, ten="x" * 100).status_code == 200


# AC5 – chữ ký, ảnh sai loại hoặc quá lớn
@pytest.mark.parametrize(
    ("them", "ma", "ma_loi"),
    [
        ({"ky": JPG}, 400, "ANH_SAI_LOAI"),
        ({"ky": b"GIF89a" + b"0" * 50}, 400, "ANH_SAI_LOAI"),
        ({"ky": PNG[:8] + b"0" * (500 * 1024)}, 413, "ANH_QUA_LON"),
        ({"anh": (b"\xff\xd8\xff" + b"0" * (500 * 1024),)}, 413, "ANH_QUA_LON"),
    ],
    ids=["ky-jpg", "ky-gif", "ky-qua-500kb", "anh-qua-500kb"],
)
def test_uc20_ac5_chu_ky_sai(client, db, gh, them, ma, ma_loi):
    r = giao(client, **them)
    assert (r.status_code, r.json()["ma"]) == (ma, ma_loi)
    assert trang_thai(db, gh["d1"]) == "DA_LAY"
    assert so_tep(db) == 0 and list(gh["thu_muc"].iterdir()) == []


# AC6 – báo giao không được
def test_uc20_ac6_giao_khong_duoc(client, db, gh):
    r = bao_giao_khong_duoc(client)  # TC-BR42-01: "Người nhận vắng"
    assert r.status_code == 200, r.text
    assert r.json() == {"ma_don": "DH-0001", "trang_thai": "THAT_BAI", "canh_bao": [], "lap_lai": False}
    (lq,) = luot(db, gh["d1"])
    assert (lq.loai, lq.ly_do_id, lq.ten_nguoi_nhan) == ("GIAO_THAT_BAI", LY_DO_GIAO, None)
    assert db.scalars(select(Tep.loai).where(Tep.luot_quet_id == lq.id)).all() == ["ANH"]
    ly_do = db.scalar(
        select(LichSuTrangThai.ly_do).where(
            LichSuTrangThai.doi_tuong_id == gh["d1"].id, LichSuTrangThai.sang == "THAT_BAI"
        )
    )
    assert ly_do == "Người nhận vắng"
    assert tuple(ghep_cua(db, gh["d1"])) == ("THAT_BAI", False, True)
    assert phai_thu(db) == []


# AC7 – báo giao không được thiếu / sai
@pytest.mark.parametrize(
    ("anh", "ly_do_id"),
    [((), LY_DO_GIAO), ((JPG,), None), ((JPG,), LY_DO_LAY), ((JPG,), 999)],
    ids=["thieu-anh", "thieu-ly-do", "ly-do-lay", "ly-do-khong-co"],
)
def test_uc20_ac7_giao_khong_duoc_thieu(client, db, gh, anh, ly_do_id):
    r = bao_giao_khong_duoc(client, anh=anh, ly_do_id=ly_do_id)  # TC-BR42-02
    assert (r.status_code, r.json()["ma"]) == (422, "BR-42")
    assert trang_thai(db, gh["d1"]) == "DA_LAY"
    assert luot(db, gh["d1"]) == [] and so_tep(db) == 0


# AC8 – đơn chưa lấy
@pytest.mark.parametrize("viec", ["giao", "that_bai"])
def test_uc20_ac8_don_chua_lay(client, db, gh, viec):
    r = giao(client, "DH-0002") if viec == "giao" else bao_giao_khong_duoc(client, "DH-0002")  # TC-BR40-02
    assert (r.status_code, r.json()["ma"]) == (409, "BR-40")
    assert "chưa được quét lấy" in r.json()["thong_diep"]
    assert trang_thai(db, gh["d2"]) == "DA_GHEP"
    assert luot(db, gh["d2"]) == []


# AC9 – quét lặp và trái kết quả
def test_uc20_ac9_giao_lan_hai(client, db, gh):
    assert giao(client).status_code == 200
    r = giao(client)
    assert (r.status_code, r.json()["lap_lai"], r.json()["trang_thai"]) == (200, True, "DA_GIAO")
    assert len(luot(db, gh["d1"])) == 1 and len(phai_thu(db)) == 1
    assert so_tep(db) == 2 and len(list(gh["thu_muc"].iterdir())) == 2  # lần hai không lưu ảnh, chữ ký


def test_uc20_ac9_that_bai_lan_hai(client, db, gh):
    assert bao_giao_khong_duoc(client).status_code == 200
    r = bao_giao_khong_duoc(client)
    assert (r.status_code, r.json()["lap_lai"]) == (200, True)
    assert len(luot(db, gh["d1"])) == 1


@pytest.mark.parametrize(
    ("truoc", "sau", "ma"),
    [("giao", "that_bai", "BR-40"), ("that_bai", "giao", "BR-40"), ("giao", "khong_lay", "BR-39")],
    ids=["that-bai-don-da-giao", "giao-don-that-bai", "khong-lay-don-da-giao"],
)
def test_uc20_ac9_trai_ket_qua(client, db, gh, truoc, sau, ma):
    gui = {
        "giao": lambda: giao(client),
        "that_bai": lambda: bao_giao_khong_duoc(client),
        "khong_lay": lambda: quet(client, loai="KHONG_LAY", anh=[JPG], ly_do_id=LY_DO_LAY),
    }
    assert gui[truoc]().status_code == 200
    tt = trang_thai(db, gh["d1"])
    r = gui[sau]()
    assert (r.status_code, r.json()["ma"]) == (409, ma)
    assert r.json()["chi_tiet"][0]["trang_thai"] == tt
    assert trang_thai(db, gh["d1"]) == tt and len(luot(db, gh["d1"])) == 1


def test_uc20_ac9_lay_don_da_giao_la_lap(client, db, gh):
    assert giao(client).status_code == 200
    assert quet(client).json()["lap_lai"] is True  # đơn đã giao thì chắc chắn đã lấy


# AC10 – hai lượt giao cùng lúc
def test_uc20_ac10_giao_dong_thoi(db, gh):
    ket_qua = []
    cho = threading.Barrier(2)

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            dang_nhap(c)
            cho.wait()
            ket_qua.append(giao(c))

    luong = [threading.Thread(target=gui) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [200, 200]
    assert sorted(r.json()["lap_lai"] for r in ket_qua) == [False, True]
    assert len(luot(db, gh["d1"])) == 1 and len(phai_thu(db)) == 1


# AC11 – không giao một phần
def test_uc20_ac11_khong_giao_mot_phan(client, db, gh):
    r = giao(client, so_kien_giao="1")  # TC-BR35-01
    assert (r.status_code, r.json()["ma"]) == (400, "DU_LIEU_KHONG_HOP_LE")
    assert trang_thai(db, gh["d1"]) == "DA_LAY"
    # TC-BR35-02: quét giao chỉ dẫn tới DA_GIAO hoặc THAT_BAI cho cả đơn
    assert {sang for (_, loai), sang in LAM.items() if loai.startswith("GIAO")} == {"DA_GIAO", "THAT_BAI"}


# AC12 – BR-38 và phân quyền
def test_uc20_ac12_don_chuyen_khac(client, db, gh):
    d5 = gh["don"](5, "TP.HCM", "Cần Thơ", 100, 1, luc(14), trang_thai="DA_LAY")
    gh["chuyen"](gh["binh"], "DANG_CHAY", 6, 22, d5)
    r = giao(client, "DH-0005")
    assert (r.status_code, r.json()["ma"]) == (403, "BR-38")
    assert trang_thai(db, d5) == "DA_LAY"


def test_uc20_ac12_chuyen_da_ket_thuc(client, db, gh):
    dat_chuyen(db, gh["c01"], "HOAN_THANH")
    r = giao(client)
    assert (r.status_code, r.json()["ma"]) == (409, "BR-38")


@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "QUAN_LY"])
def test_uc20_ac12_vai_tro_khac(client, db, gh, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert giao(client).status_code == 403
    assert trang_thai(db, gh["d1"]) == "DA_LAY"


def test_uc20_ac12_chua_dang_nhap(client, db, gh):
    client.post("/api/auth/dang-xuat")
    assert giao(client).status_code == 401


# AC13 – giao hết rồi kết thúc chuyến (UC-18)
def test_uc20_ac13_ket_thuc_sau_khi_giao(client, db, gh):
    assert quet(client, "DH-0002").status_code == 200  # lấy Đ2
    assert giao(client, "DH-0001").status_code == 200
    assert giao(client, "DH-0004").status_code == 200
    assert bao_giao_khong_duoc(client, "DH-0002").status_code == 200
    r = client.post(
        f"/api/toi/chuyen/{gh['c01'].id}/ket-thuc",
        data={"km_ket_thuc": "50200"},
        files={"anh_dong_ho": ("dong-ho.jpg", io.BytesIO(JPG), "image/jpeg")},
    )
    assert r.status_code == 200, r.text
    assert db.scalar(select(Chuyen.trang_thai).where(Chuyen.id == gh["c01"].id)) == "HOAN_THANH"
    ghep = dict(db.execute(select(Ghep.don_hang_id, Ghep.hieu_luc).where(Ghep.chuyen_id == gh["c01"].id)).all())
    assert ghep == {gh["d1"].id: True, gh["d4"].id: True, gh["d2"].id: False}  # BR-36: chỉ gỡ đơn thất bại
    assert len(phai_thu(db)) == 2


# AC16 – theo review PR #15: trần số ảnh, độ chính xác GPS
def test_uc20_ac16_toi_da_5_anh(client, db, gh):
    r = giao(client, anh=(JPG,) * 6)
    assert (r.status_code, r.json()["ma"]) == (400, "QUA_NHIEU_ANH")
    assert so_tep(db) == 0
    assert giao(client, anh=(JPG,) * 5).status_code == 200
    assert db.scalar(select(func.count()).select_from(Tep).where(Tep.loai == "ANH")) == 5


@pytest.mark.parametrize(
    ("chinh_xac", "ma"),
    [("999999.9", 200), ("1000000", 400), ("9999999.95", 400)],
    ids=["duoi-tran", "dung-tran", "tung-gay-500"],
)
def test_uc20_ac16_do_chinh_xac_gps(client, db, gh, chinh_xac, ma):
    r = quet(client, "DH-0002", gps={"lat": "10.7", "lng": "106.7", "do_chinh_xac_m": chinh_xac})
    assert r.status_code == ma
