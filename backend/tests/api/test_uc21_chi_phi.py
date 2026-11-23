# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-21 Ghi chi phí (tài xế). C01 của An đang chạy; kịch bản mục 11: dầu 26 lít 520.000, cầu đường 230.000."""

import threading
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import luu_tru
from app.main import app
from app.models import ChiPhi, Chuyen, NhatKyTien, TamUng, Tep
from tests.api.test_uc17_xem_chuyen import kb  # noqa: F401 (kb là fixture)

JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
PDF = b"%PDF-1.4" + b"0" * 100


def dang_nhap(client, ten="an"):
    r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": "matkhau123"})
    assert r.status_code == 200


@pytest.fixture
def ch(db, kb, client, tmp_path, monkeypatch):
    """C01 của An đang chạy; ảnh ghi vào thư mục tạm; client đăng nhập An."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    kb["c01"].trang_thai = "DANG_CHAY"
    db.commit()
    dang_nhap(client)
    return kb | {"thu_muc": tmp_path, "id": kb["c01"].id}


def ghi(client, chuyen_id, loai="DAU", so_tien="520000", so_lit="26", ghi_chu="Đổ dầu Cai Lậy", anh=(JPG,), **them):
    data = {"loai": loai, "so_tien": so_tien, **({"so_lit": so_lit} if so_lit is not None else {}), **them}
    if ghi_chu is not None:
        data["ghi_chu"] = ghi_chu
    files = [("anh", (f"a{i}.jpg", b, "image/jpeg")) for i, b in enumerate(anh)]
    return client.post(f"/api/toi/chuyen/{chuyen_id}/chi-phi", data=data, files=files or None)


def cau_duong(client, chuyen_id, so_tien="230000", **k):
    return ghi(client, chuyen_id, loai="CAU_DUONG", so_tien=so_tien, so_lit=None, ghi_chu="Trạm BOT", **k)


def khoan(db, chuyen_id) -> list[ChiPhi]:
    db.expire_all()
    return list(db.scalars(select(ChiPhi).where(ChiPhi.chuyen_id == chuyen_id).order_by(ChiPhi.id)))


def nhat_ky(db, cp_id) -> list[NhatKyTien]:
    db.expire_all()
    return list(
        db.scalars(
            select(NhatKyTien)
            .where(NhatKyTien.bang == "chi_phi", NhatKyTien.ban_ghi_id == cp_id)
            .order_by(NhatKyTien.id)
        )
    )


def so_tep(db) -> int:
    return db.scalar(select(func.count()).select_from(Tep))


def dat_chuyen(db, chuyen_id, trang_thai):
    db.get(Chuyen, chuyen_id).trang_thai = trang_thai
    db.commit()


def ma(r) -> tuple[int, str | None]:
    return r.status_code, (r.json() or {}).get("ma") if r.content else None


# AC1 – ghi hợp lệ (TC-BR54-01, kịch bản mục 11)
def test_uc21_ac1_ghi_dau(client, db, ch):
    r = ghi(client, ch["id"])
    assert r.status_code == 201, r.text
    j = r.json()
    assert (j["loai"], j["so_tien_khai"], Decimal(j["so_lit"]), j["trang_thai"], j["so_anh"]) == (
        "DAU",
        520000,
        Decimal("26"),
        "CHO_DUYET",
        1,
    )
    (cp,) = khoan(db, ch["id"])
    assert (cp.nguoi_tao, cp.ghi_chu, cp.so_tien_duyet) == (ch["an"].nguoi_dung_id, "Đổ dầu Cai Lậy", None)
    (tep,) = db.scalars(select(Tep).where(Tep.chi_phi_id == cp.id))
    assert tep.loai == "ANH" and (ch["thu_muc"] / tep.duong_dan).read_bytes() == JPG
    (nk,) = nhat_ky(db, cp.id)
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.nguoi) == (
        "TAO",
        None,
        "520000 DAU 26.00",
        ch["an"].nguoi_dung_id,
    )


def test_uc21_ac1_cac_loai_khong_so_lit(client, db, ch):
    assert cau_duong(client, ch["id"]).status_code == 201
    r = ghi(client, ch["id"], loai="BOC_XEP", so_tien="300000", so_lit=None, ghi_chu="Bốc xếp Cần Thơ", anh=(PNG,))
    assert r.status_code == 201
    assert ghi(client, ch["id"], loai="PHAT_SINH", so_tien="50000", so_lit=None, ghi_chu="Vá lốp").status_code == 201
    assert [(k.loai, k.so_tien_khai, k.so_lit) for k in khoan(db, ch["id"])] == [
        ("CAU_DUONG", 230000, None),
        ("BOC_XEP", 300000, None),
        ("PHAT_SINH", 50000, None),
    ]
    assert nhat_ky(db, khoan(db, ch["id"])[0].id)[0].gia_tri_moi == "230000 CAU_DUONG"


# AC2 – thiếu ghi chú, ảnh (TC-BR54-02)
@pytest.mark.parametrize(("ghi_chu", "anh"), [(None, (JPG,)), ("   ", (JPG,)), ("Đổ dầu", ()), (None, ())])
def test_uc21_ac2_thieu_ghi_chu_anh(client, db, ch, ghi_chu, anh):
    r = ghi(client, ch["id"], ghi_chu=ghi_chu, anh=anh)
    assert ma(r) == (422, "BR-54")
    assert khoan(db, ch["id"]) == [] and so_tep(db) == 0
    assert list(ch["thu_muc"].iterdir()) == []


# AC3 – biên số (TC-BR54-02, 03)
@pytest.mark.parametrize(
    "them",
    [
        {"so_tien": "0"},
        {"so_tien": "-1"},
        {"so_tien": "1000.5"},
        {"so_tien": "abc"},
        {"so_tien": "1000000000001"},
        {"so_lit": None},
        {"so_lit": "0"},
        {"so_lit": "-1"},
        {"so_lit": "26.125"},
        {"loai": "CAU_DUONG"},  # còn số lít 26
        {"ghi_chu": "x" * 501},
    ],
)
def test_uc21_ac3_du_lieu_sai(client, db, ch, them):
    assert ghi(client, ch["id"], **them).status_code == 400
    assert khoan(db, ch["id"]) == [] and so_tep(db) == 0


def test_uc21_ac3_bien_dung(client, db, ch):
    assert ghi(client, ch["id"], so_tien="1", so_lit="0.01", ghi_chu="x" * 500).status_code == 201
    assert [(k.so_tien_khai, k.so_lit) for k in khoan(db, ch["id"])] == [(1, Decimal("0.01"))]


# AC4 – ảnh
def test_uc21_ac4_so_anh(client, db, ch):
    assert ghi(client, ch["id"], anh=(JPG,) * 5).json()["so_anh"] == 5
    assert ma(ghi(client, ch["id"], anh=(JPG,) * 6)) == (400, "QUA_NHIEU_ANH")
    assert len(khoan(db, ch["id"])) == 1 and so_tep(db) == 5


def test_uc21_ac4_anh_sai_loai_va_qua_lon(client, db, ch):
    assert ma(ghi(client, ch["id"], anh=(JPG, PDF))) == (400, "ANH_SAI_LOAI")
    lon = b"\xff\xd8\xff\xe0" + b"0" * luu_tru.KICH_THUOC_TOI_DA
    assert ma(ghi(client, ch["id"], anh=(lon,))) == (413, "ANH_QUA_LON")
    vua = b"\xff\xd8\xff\xe0" + b"0" * (luu_tru.KICH_THUOC_TOI_DA - 4)  # đúng 500 KB
    assert ghi(client, ch["id"], anh=(vua,)).status_code == 201
    assert len(khoan(db, ch["id"])) == 1 and len(list(ch["thu_muc"].iterdir())) == 1


# AC5 – trạng thái chuyến
def test_uc21_ac5_hoan_thanh_ghi_duoc(client, db, ch):
    dat_chuyen(db, ch["id"], "HOAN_THANH")
    assert ghi(client, ch["id"]).status_code == 201


@pytest.mark.parametrize(("tt", "ket_qua"), [("DA_CHOT", (409, "BR-54")), ("DA_QUYET_TOAN", (409, "BR-29"))])
def test_uc21_ac5_trang_thai_khong_ghi(client, db, ch, tt, ket_qua):
    dat_chuyen(db, ch["id"], tt)
    assert ma(ghi(client, ch["id"])) == ket_qua
    assert khoan(db, ch["id"]) == []


@pytest.mark.parametrize("tt", ["LAP", "HUY"])
def test_uc21_ac5_lap_huy_tai_xe_khong_thay(client, db, ch, tt):
    dat_chuyen(db, ch["id"], tt)  # như UC-17: tài xế không thấy chuyến LAP, HUY → 404
    assert ma(ghi(client, ch["id"])) == (404, "KHONG_TIM_THAY")


# AC6 – chuyến của người khác, dữ liệu lạ
def test_uc21_ac6_chuyen_nguoi_khac(client, db, ch):
    c_binh = ch["chuyen"](ch["binh"], "DANG_CHAY", 13)
    assert ma(ghi(client, c_binh.id)) == (404, "KHONG_TIM_THAY")
    assert ma(ghi(client, 999999)) == (404, "KHONG_TIM_THAY")
    assert khoan(db, c_binh.id) == []


@pytest.mark.parametrize("them", [{"trang_thai": "DA_DUYET"}, {"nguoi_tao": "1"}, {"so_tien_duyet": "1"}])
def test_uc21_ac6_truong_la(client, db, ch, them):
    assert ghi(client, ch["id"], **them).status_code == 400
    assert khoan(db, ch["id"]) == []


def test_uc21_ac6_loai_sai(client, db, ch):
    assert ghi(client, ch["id"], loai="AN_UONG", so_lit=None).status_code == 400


# AC7 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "QUAN_LY"])
def test_uc21_ac7_khong_phai_tai_xe(client, dang_nhap_voi, db, ch, vai_tro):
    cp = ghi(client, ch["id"]).json()["id"]
    dang_nhap_voi(vai_tro)
    assert ma(ghi(client, ch["id"])) == (403, "KHONG_DU_QUYEN")
    assert client.get(f"/api/toi/chuyen/{ch['id']}/chi-phi").status_code == 403
    assert client.patch(f"/api/toi/chi-phi/{cp}", json={"so_tien": 1000}).status_code == 403
    assert client.delete(f"/api/toi/chi-phi/{cp}").status_code == 403
    assert [k.so_tien_khai for k in khoan(db, ch["id"])] == [520000]


def test_uc21_ac7_chua_dang_nhap(client, kb):
    c = kb["c01"].id
    assert ghi(client, c).status_code == 401
    assert client.get(f"/api/toi/chuyen/{c}/chi-phi").status_code == 401
    assert client.patch("/api/toi/chi-phi/1", json={"so_tien": 1000}).status_code == 401
    assert client.delete("/api/toi/chi-phi/1").status_code == 401


# AC8 – xem
def test_uc21_ac8_xem(client, db, ch):
    j = client.get(f"/api/toi/chuyen/{ch['id']}/chi-phi").json()
    assert (j["tam_ung_da_nhan"], j["tong_da_khai"], j["khoan"]) == (0, 0, [])

    db.add_all(
        [
            TamUng(chuyen_id=ch["id"], tai_xe_id=ch["an"].id, so_tien=1_000_000, hinh_thuc="TIEN_MAT", nguoi_tao=1),
            TamUng(
                chuyen_id=ch["id"],
                tai_xe_id=ch["an"].id,
                so_tien=300_000,
                hinh_thuc="TIEN_MAT",
                trang_thai="DA_THU_HOI",
                nguoi_tao=1,
            ),
        ]
    )
    db.commit()
    a = ghi(client, ch["id"], anh=(JPG, PNG)).json()["id"]
    b = cau_duong(client, ch["id"]).json()["id"]
    c = cau_duong(client, ch["id"], so_tien="99000").json()["id"]
    db.get(ChiPhi, c).trang_thai = "TU_CHOI"
    db.commit()

    j = client.get(f"/api/toi/chuyen/{ch['id']}/chi-phi").json()
    assert (j["tam_ung_da_nhan"], j["tong_da_khai"]) == (1_000_000, 750_000)  # thu hồi, từ chối không tính
    assert [(k["id"], k["so_anh"]) for k in j["khoan"]] == [(a, 2), (b, 1), (c, 1)]


def test_uc21_ac8_xem_chuyen_nguoi_khac(client, db, ch):
    c_binh = ch["chuyen"](ch["binh"], "DANG_CHAY", 13)
    assert client.get(f"/api/toi/chuyen/{c_binh.id}/chi-phi").status_code == 404


# AC9 – sửa
def sua(client, cp_id, **body):
    return client.patch(f"/api/toi/chi-phi/{cp_id}", json=body)


def test_uc21_ac9_sua(client, db, ch):
    cp = ghi(client, ch["id"]).json()["id"]
    r = sua(client, cp, so_tien=500000, ghi_chu="  Đổ dầu Cai Lậy (sửa)  ")
    assert r.status_code == 200, r.text
    assert (r.json()["so_tien_khai"], r.json()["ghi_chu"], r.json()["so_anh"]) == (500000, "Đổ dầu Cai Lậy (sửa)", 1)
    nk = nhat_ky(db, cp)[-1]
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi) == ("SUA", "520000 DAU 26.00", "500000 DAU 26.00")
    assert nk.ly_do


def test_uc21_ac9_doi_loai(client, db, ch):
    cp = ghi(client, ch["id"]).json()["id"]
    assert sua(client, cp, loai="CAU_DUONG").status_code == 400  # còn số lít
    assert sua(client, cp, loai="CAU_DUONG", so_lit=None).status_code == 200
    assert sua(client, cp, loai="DAU").status_code == 400  # dầu mà không có số lít
    assert sua(client, cp, loai="DAU", so_lit="30.5").status_code == 200
    assert (khoan(db, ch["id"])[0].loai, khoan(db, ch["id"])[0].so_lit) == ("DAU", Decimal("30.50"))


@pytest.mark.parametrize(
    ("body", "ket_qua"),
    [
        ({"ghi_chu": "   "}, (422, "BR-54")),
        ({"so_tien": 0}, (400, "DU_LIEU_KHONG_HOP_LE")),
        ({"so_tien": "500000"}, (400, "DU_LIEU_KHONG_HOP_LE")),
        ({"trang_thai": "DA_DUYET"}, (400, "DU_LIEU_KHONG_HOP_LE")),
        ({}, (400, "KHONG_CO_THAY_DOI")),
        ({"so_tien": 520000}, (400, "KHONG_CO_THAY_DOI")),
    ],
)
def test_uc21_ac9_sua_sai(client, db, ch, body, ket_qua):
    cp = ghi(client, ch["id"]).json()["id"]
    assert ma(sua(client, cp, **body)) == ket_qua
    assert (khoan(db, ch["id"])[0].so_tien_khai, khoan(db, ch["id"])[0].trang_thai) == (520000, "CHO_DUYET")
    assert len(nhat_ky(db, cp)) == 1


# AC10 – xóa
def test_uc21_ac10_xoa(client, db, ch):
    cp = ghi(client, ch["id"], anh=(JPG, PNG)).json()["id"]
    assert len(list(ch["thu_muc"].iterdir())) == 2
    r = client.delete(f"/api/toi/chi-phi/{cp}")
    assert r.status_code == 204
    assert khoan(db, ch["id"]) == [] and so_tep(db) == 0
    assert list(ch["thu_muc"].iterdir()) == []
    tao, xoa = nhat_ky(db, cp)
    assert (xoa.hanh_dong, xoa.gia_tri_cu, xoa.gia_tri_moi) == ("XOA", "520000 DAU 26.00", None)
    assert client.delete(f"/api/toi/chi-phi/{cp}").status_code == 404


# AC11 – sửa / xóa khi không được
@pytest.mark.parametrize("tt", ["DA_DUYET", "TU_CHOI"])
def test_uc21_ac11_khoan_da_xu_ly(client, db, ch, tt):
    cp = ghi(client, ch["id"]).json()["id"]
    db.get(ChiPhi, cp).trang_thai = tt
    db.commit()
    assert ma(sua(client, cp, so_tien=1000)) == (409, "BR-54")
    assert ma(client.delete(f"/api/toi/chi-phi/{cp}")) == (409, "BR-54")
    assert khoan(db, ch["id"])[0].so_tien_khai == 520000


def test_uc21_ac11_da_quyet_toan(client, db, ch):
    cp = ghi(client, ch["id"]).json()["id"]
    dat_chuyen(db, ch["id"], "DA_QUYET_TOAN")
    assert ma(sua(client, cp, so_tien=1000)) == (409, "BR-29")
    assert ma(client.delete(f"/api/toi/chi-phi/{cp}")) == (409, "BR-29")
    assert len(khoan(db, ch["id"])) == 1


def test_uc21_ac11_khoan_nguoi_khac(client, db, ch):
    cp = ghi(client, ch["id"]).json()["id"]
    dang_nhap(client, "binh")
    assert ma(sua(client, cp, so_tien=1000)) == (404, "KHONG_TIM_THAY")
    assert ma(client.delete(f"/api/toi/chi-phi/{cp}")) == (404, "KHONG_TIM_THAY")
    assert ma(sua(client, 999999, so_tien=1000)) == (404, "KHONG_TIM_THAY")
    assert [k.so_tien_khai for k in khoan(db, ch["id"])] == [520000]


# AC12 – CSDL lỗi giữa chừng không để ảnh mồ côi
def test_uc21_ac12_loi_giua_chung(client, db, ch, monkeypatch):
    from app.modules.tien.chi_phi import service

    def hong(*a, **k):
        raise RuntimeError("CSDL lỗi")

    monkeypatch.setattr(service, "_ghi_nhat_ky", hong)
    with TestClient(app, base_url="https://testserver", raise_server_exceptions=False) as c:
        dang_nhap(c)
        assert ghi(c, ch["id"], anh=(JPG, PNG)).status_code == 500
    assert khoan(db, ch["id"]) == [] and so_tep(db) == 0
    assert list(ch["thu_muc"].iterdir()) == []


# Khóa chuyến: ghi chi phí và đổi trạng thái chuyến (quyết toán, UC-24) không chen nhau
def test_uc21_ghi_cho_khoa_chuyen(client, db, ch):
    from sqlalchemy.orm import Session

    from app.db import get_engine

    s = Session(get_engine())
    s.get(Chuyen, ch["id"], with_for_update=True)  # như quyết toán đang giữ dòng chuyến
    ket_qua: list = []

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            dang_nhap(c)
            ket_qua.append(ghi(c, ch["id"]))

    t = threading.Thread(target=gui)
    t.start()
    t.join(1.5)
    assert t.is_alive()  # đang đợi khóa
    s.get(Chuyen, ch["id"]).trang_thai = "DA_QUYET_TOAN"
    s.commit()
    s.close()
    t.join()
    assert ma(ket_qua[0]) == (409, "BR-29")  # đọc lại trạng thái mới sau khi được khóa


# Kiểm thử khám phá 23/11: hai lần xóa cùng một khoản gửi song song → lần sau 404, không 500
def test_uc21_xoa_song_song(client, db, ch):
    from sqlalchemy import delete
    from sqlalchemy.orm import Session

    from app.db import get_engine

    cp = ghi(client, ch["id"]).json()["id"]
    s = Session(get_engine())
    s.get(Chuyen, ch["id"], with_for_update=True)  # như lần xóa thứ nhất đang giữ dòng chuyến
    ket_qua: list = []

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            dang_nhap(c)
            ket_qua.append(c.delete(f"/api/toi/chi-phi/{cp}"))

    try:
        t = threading.Thread(target=gui)
        t.start()
        t.join(1.5)
        assert t.is_alive()  # đã đọc chuyen_id, đang đợi khóa
        s.execute(delete(Tep).where(Tep.chi_phi_id == cp))
        s.execute(delete(ChiPhi).where(ChiPhi.id == cp))
        s.commit()  # lần xóa thứ nhất xong
    finally:
        s.close()
    t.join()
    assert ma(ket_qua[0]) == (404, "KHONG_TIM_THAY")
