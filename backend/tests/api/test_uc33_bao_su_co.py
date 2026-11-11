# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-33 Báo sự cố (tài xế). C01 của An đang chạy (ngày 22/10/2030); ảnh ghi vào thư mục tạm."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import luu_tru
from app.main import app
from app.models import Chuyen, DonHang, SuCo, Tep
from tests.api.test_uc17_xem_chuyen import kb  # noqa: F401 (kb là fixture)

JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
PDF = b"%PDF-1.4" + b"0" * 100
NGAY = "2030-10-22"


def dang_nhap(client, ten="an"):
    r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": "matkhau123"})
    assert r.status_code == 200


@pytest.fixture
def ch(db, kb, client, tmp_path, monkeypatch):
    """C01 của An đang chạy; client đăng nhập An."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    kb["c01"].trang_thai = "DANG_CHAY"
    db.commit()
    dang_nhap(client)
    return kb | {"thu_muc": tmp_path, "id": kb["c01"].id}


def bao(client, chuyen_id, loai="HONG_XE", ghi_chu="Nổ lốp", anh=(JPG,), **them):
    data = {"loai": loai, **them}
    if ghi_chu is not None:
        data["ghi_chu"] = ghi_chu
    files = [("anh", (f"a{i}.jpg", b, "image/jpeg")) for i, b in enumerate(anh)]
    return client.post(f"/api/toi/chuyen/{chuyen_id}/su-co", data=data, files=files or None)


def su_co(db, chuyen_id) -> list[SuCo]:
    db.expire_all()
    return list(db.scalars(select(SuCo).where(SuCo.chuyen_id == chuyen_id).order_by(SuCo.id)))


def so_tep(db) -> int:
    return db.scalar(select(func.count()).select_from(Tep))


def dat_chuyen(db, chuyen_id, trang_thai):
    db.get(Chuyen, chuyen_id).trang_thai = trang_thai
    db.commit()


def ma(r) -> tuple[int, str | None]:
    return r.status_code, (r.json() or {}).get("ma") if r.content else None


# AC1 – báo hợp lệ: lưu MO, ảnh gắn su_co_id, chuyến và đơn không đổi
def test_uc33_ac1_bao_su_co(client, db, ch):
    r = bao(client, ch["id"])
    assert r.status_code == 201, r.text
    j = r.json()
    tom_tat = (j["loai"], j["ghi_chu"], j["trang_thai"], j["cach_xu_ly"], j["so_anh"])
    assert tom_tat == ("HONG_XE", "Nổ lốp", "MO", None, 1)
    [sc] = su_co(db, ch["id"])
    assert (sc.tai_xe_id, sc.trang_thai) == (ch["an"].id, "MO")
    tep = db.scalars(select(Tep).where(Tep.su_co_id == sc.id)).all()
    assert [(t.loai, t.chi_phi_id, t.luot_quet_id, t.chuyen_id) for t in tep] == [("ANH", None, None, None)]
    assert (ch["thu_muc"] / tep[0].duong_dan).read_bytes() == JPG
    db.expire_all()
    assert db.get(Chuyen, ch["id"]).trang_thai == "DANG_CHAY"
    assert {db.get(DonHang, ch[k].id).trang_thai for k in ("d1", "d2", "d4")} == {"DA_GHEP"}


def test_uc33_ac1_ghi_chu_chuan_hoa(client, db, ch):
    # Chữ tổ hợp (NFD) → NFC, bỏ khoảng trắng hai đầu; báo nhiều lần được
    assert bao(client, ch["id"], loai="KET_XE", ghi_chu="  Kẹt xe  ").json()["ghi_chu"] == "Kẹt xe"
    assert bao(client, ch["id"], loai="KHAC").status_code == 201
    assert [s.loai for s in su_co(db, ch["id"])] == ["KET_XE", "KHAC"]


# AC2 – ảnh: 0 được (quyết định 3), 5 được, 6 → 400; sai loại 400; quá lớn 413; lỗi thì không lưu gì
def test_uc33_ac2_khong_anh_duoc(client, db, ch):
    r = bao(client, ch["id"], anh=())
    assert (r.status_code, r.json()["so_anh"]) == (201, 0)
    assert so_tep(db) == 0


def test_uc33_ac2_nam_anh(client, db, ch):
    assert bao(client, ch["id"], anh=(JPG, PNG, JPG, PNG, JPG)).json()["so_anh"] == 5


@pytest.mark.parametrize(
    ("anh", "ket_qua"),
    [
        ((JPG,) * 6, (400, "QUA_NHIEU_ANH")),
        ((JPG, PDF), (400, "ANH_SAI_LOAI")),
        ((b"\xff\xd8\xff" + b"0" * luu_tru.KICH_THUOC_TOI_DA,), (413, "ANH_QUA_LON")),
    ],
)
def test_uc33_ac2_anh_sai(client, db, ch, anh, ket_qua):
    assert ma(bao(client, ch["id"], anh=anh)) == ket_qua
    assert su_co(db, ch["id"]) == [] and so_tep(db) == 0
    assert list(ch["thu_muc"].iterdir()) == []


# AC3 – ghi chú, loại, trường lạ
@pytest.mark.parametrize("ghi_chu", [None, "", "   "])
def test_uc33_ac3_thieu_ghi_chu(client, db, ch, ghi_chu):
    assert ma(bao(client, ch["id"], ghi_chu=ghi_chu)) == (422, "THIEU_GHI_CHU")
    assert su_co(db, ch["id"]) == [] and so_tep(db) == 0


def test_uc33_ac3_ghi_chu_bien(client, db, ch):
    assert bao(client, ch["id"], ghi_chu="x" * 500).status_code == 201
    assert bao(client, ch["id"], ghi_chu="x" * 501).status_code == 400
    assert len(su_co(db, ch["id"])) == 1


@pytest.mark.parametrize(
    "them", [{"loai": "CHAY_NO"}, {"trang_thai": "DONG"}, {"tai_xe_id": "1"}, {"cach_xu_ly": "tự xử"}]
)
def test_uc33_ac3_loai_sai_truong_la(client, db, ch, them):
    assert bao(client, ch["id"], **them).status_code == 400
    assert su_co(db, ch["id"]) == []


# AC4 – trạng thái chuyến (quyết định 4) và chuyến của người khác
@pytest.mark.parametrize("tt", ["DA_CHOT", "HOAN_THANH", "DA_QUYET_TOAN"])
def test_uc33_ac4_khong_dang_chay(client, db, ch, tt):
    dat_chuyen(db, ch["id"], tt)
    assert ma(bao(client, ch["id"])) == (409, "CHUYEN_KHONG_DANG_CHAY")
    assert su_co(db, ch["id"]) == [] and so_tep(db) == 0


@pytest.mark.parametrize("tt", ["LAP", "HUY"])
def test_uc33_ac4_lap_huy_khong_thay(client, db, ch, tt):
    dat_chuyen(db, ch["id"], tt)  # như UC-17, 21: tài xế không thấy chuyến LAP, HUY → 404
    assert ma(bao(client, ch["id"])) == (404, "KHONG_TIM_THAY")
    assert client.get(f"/api/toi/chuyen/{ch['id']}/su-co").status_code == 404


def test_uc33_ac4_chuyen_nguoi_khac(client, db, ch):
    c_binh = ch["chuyen"](ch["binh"], "DANG_CHAY", 13)
    assert ma(bao(client, c_binh.id)) == (404, "KHONG_TIM_THAY")
    assert ma(bao(client, 999999)) == (404, "KHONG_TIM_THAY")
    assert su_co(db, c_binh.id) == []


# AC5 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "QUAN_LY"])
def test_uc33_ac5_khong_phai_tai_xe(client, dang_nhap_voi, db, ch, vai_tro):
    dang_nhap_voi(vai_tro)
    assert ma(bao(client, ch["id"])) == (403, "KHONG_DU_QUYEN")
    assert client.get(f"/api/toi/chuyen/{ch['id']}/su-co").status_code == 403
    assert su_co(db, ch["id"]) == []


def test_uc33_ac5_chua_dang_nhap(client, kb):
    c = kb["c01"].id
    assert bao(client, c).status_code == 401
    assert client.get(f"/api/toi/chuyen/{c}/su-co").status_code == 401


# AC6 – xem lại: cũ trước, số ảnh; Điều phối đóng thì thấy DONG và cách xử lý
def test_uc33_ac6_xem_lai(client, dang_nhap_voi, db, ch):
    assert client.get(f"/api/toi/chuyen/{ch['id']}/su-co").json() == []
    a = bao(client, ch["id"], anh=(JPG, PNG)).json()
    b = bao(client, ch["id"], loai="THOI_TIET", ghi_chu="Mưa lớn", anh=()).json()
    ds = client.get(f"/api/toi/chuyen/{ch['id']}/su-co").json()
    assert [(x["id"], x["so_anh"], x["trang_thai"]) for x in ds] == [(a["id"], 2, "MO"), (b["id"], 0, "MO")]

    dang_nhap_voi("DIEU_PHOI")
    assert client.post(f"/api/su-co/{a['id']}/dong", json={"cach_xu_ly": "Gọi cứu hộ thay lốp"}).status_code == 200
    dang_nhap(client)
    x = client.get(f"/api/toi/chuyen/{ch['id']}/su-co").json()[0]
    assert (x["trang_thai"], x["cach_xu_ly"]) == ("DONG", "Gọi cứu hộ thay lốp")


def test_uc33_ac6_xem_chuyen_da_ve(client, db, ch):
    bao(client, ch["id"])
    dat_chuyen(db, ch["id"], "HOAN_THANH")  # chuyến đã về vẫn xem được (chỉ không báo thêm)
    assert len(client.get(f"/api/toi/chuyen/{ch['id']}/su-co").json()) == 1


def test_uc33_ac6_xem_chuyen_nguoi_khac(client, db, ch):
    c_binh = ch["chuyen"](ch["binh"], "DANG_CHAY", 13)
    assert ma(client.get(f"/api/toi/chuyen/{c_binh.id}/su-co")) == (404, "KHONG_TIM_THAY")


# AC7 – cờ sự cố trên bảng chuyến của Điều phối (UC-32) và dòng thời gian
def test_uc33_ac7_co_tren_bang_dieu_phoi(client, dang_nhap_voi, db, ch):
    def co():
        ds = client.get("/api/chuyen", params={"ngay": NGAY}).json()["du_lieu"]
        return next(x["theo_doi"]["co"] for x in ds if x["id"] == ch["id"])

    sc = bao(client, ch["id"]).json()
    dang_nhap_voi("DIEU_PHOI")
    assert "SU_CO" in co()
    noi_dung = [s["noi_dung"] for s in client.get(f"/api/chuyen/{ch['id']}").json()["dong_thoi_gian"]]
    assert any(x.startswith("Sự cố") and "Nổ lốp" in x for x in noi_dung)
    assert client.post(f"/api/su-co/{sc['id']}/dong", json={"cach_xu_ly": "Đã thay lốp"}).status_code == 200
    assert "SU_CO" not in co()


# AC8 – CSDL lỗi giữa chừng: không có sự cố, không còn ảnh mồ côi
def test_uc33_ac8_loi_giua_chung(client, db, ch, monkeypatch):
    goc = luu_tru.luu
    lan = iter(range(10))

    def hong_lan_hai(du_lieu, duoi):
        if next(lan) == 1:
            raise RuntimeError("Đĩa đầy")
        return goc(du_lieu, duoi)

    monkeypatch.setattr(luu_tru, "luu", hong_lan_hai)
    with TestClient(app, base_url="https://testserver", raise_server_exceptions=False) as c:
        dang_nhap(c)
        assert bao(c, ch["id"], anh=(JPG, PNG)).status_code == 500
    assert su_co(db, ch["id"]) == [] and so_tep(db) == 0
    assert list(ch["thu_muc"].iterdir()) == []
