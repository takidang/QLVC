# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
"""UC-23 Cấp / sửa / thu hồi tạm ứng (Kế toán). Chuyến C01 chốt với Đ1, Đ4: định mức 1.000.000 (BR-53)."""

import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Chuyen, NhatKyTien, TamUng
from tests.api.test_uc13_ghep_don import kb, lap  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import chot, chuyen, lap_c01, mo_chot, sua

DINH_MUC = 1_000_000


@pytest.fixture
def c01(client, dang_nhap_voi, kb) -> int:
    """C01 `DA_CHOT` (Điều phối lập, ghép, chốt), sau đó đăng nhập Kế toán."""
    dang_nhap_voi("DIEU_PHOI")
    c = lap_c01(client, kb, "d1", "d4")
    assert chot(client, c).status_code == 200
    dang_nhap_voi("KE_TOAN")
    return c


def cap(client, chuyen_id, so_tien, hinh_thuc="TIEN_MAT", **them):
    return client.post(f"/api/chuyen/{chuyen_id}/tam-ung", json={"so_tien": so_tien, "hinh_thuc": hinh_thuc, **them})


def sua_tu(client, tu_id, so_tien, ly_do="ghi nhầm", **them):
    body = {"so_tien": so_tien, **({"ly_do": ly_do} if ly_do is not None else {}), **them}
    return client.patch(f"/api/tam-ung/{tu_id}", json=body)


def thu_hoi(client, tu_id, **body):
    return client.post(f"/api/tam-ung/{tu_id}/thu-hoi", json=body or None)


def khoan(db, chuyen_id) -> list[TamUng]:
    db.expire_all()
    return list(db.scalars(select(TamUng).where(TamUng.chuyen_id == chuyen_id).order_by(TamUng.id)))


def nhat_ky(db, tu_id) -> list[NhatKyTien]:
    db.expire_all()
    return list(
        db.scalars(
            select(NhatKyTien)
            .where(NhatKyTien.bang == "tam_ung", NhatKyTien.ban_ghi_id == tu_id)
            .order_by(NhatKyTien.id)
        )
    )


def ma(r) -> tuple[int, str]:
    return r.status_code, r.json().get("ma")


# AC1 – cấp hợp lệ (TC-BR53-01)
def test_uc23_ac1_cap_hop_le(client, dang_nhap_voi, db, kb, c01):
    kt = dang_nhap_voi("KE_TOAN")
    r = cap(client, c01, DINH_MUC)
    assert r.status_code == 201, r.text
    j = r.json()
    assert (j["so_tien"], j["hinh_thuc"], j["trang_thai"], j["tai_xe_id"]) == (
        DINH_MUC,
        "TIEN_MAT",
        "HIEU_LUC",
        kb["an"],
    )
    assert j["ma_chuyen"] == chuyen(db, c01).ma_chuyen and j["ten_tai_xe"]
    (tu,) = khoan(db, c01)
    assert (tu.nguoi_tao, tu.tai_xe_id) == (kt.id, chuyen(db, c01).tai_xe_id)
    (nk,) = nhat_ky(db, tu.id)
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.nguoi) == ("TAO", None, "1000000 TIEN_MAT", kt.id)
    assert nk.ly_do and nk.luc is not None


# AC2 – biên tổng (TC-BR53-02…04)
def test_uc23_ac2_bien_tong(client, db, c01):
    assert cap(client, c01, 600_000).status_code == 201
    assert cap(client, c01, 400_000, "CHUYEN_KHOAN").status_code == 201  # tổng đúng bằng định mức
    r = cap(client, c01, 1)
    assert ma(r) == (422, "BR-53")
    assert r.json()["chi_tiet"][0]["con_duoc_cap"] == 0
    assert [k.so_tien for k in khoan(db, c01)] == [600_000, 400_000]


def test_uc23_ac2_vuot_mot_lan(client, db, c01):
    r = cap(client, c01, 1_200_000)
    assert ma(r) == (422, "BR-53")
    assert "1.000.000" in r.json()["thong_diep"]
    assert khoan(db, c01) == []


# AC3 – trạng thái chuyến (TC-BR53-06)
def test_uc23_ac3_dang_chay_cap_duoc(client, db, c01):
    sua(db, Chuyen, c01, trang_thai="DANG_CHAY")
    assert cap(client, c01, 500_000).status_code == 201


@pytest.mark.parametrize("tt", ["LAP", "HOAN_THANH", "HUY", "DA_QUYET_TOAN"])
def test_uc23_ac3_trang_thai_khong_cap(client, db, c01, tt):
    sua(db, Chuyen, c01, trang_thai=tt)
    assert ma(cap(client, c01, 500_000)) == (409, "BR-53")
    assert khoan(db, c01) == []


# AC4 – dữ liệu sai
@pytest.mark.parametrize(
    "body",
    [
        {"so_tien": 0, "hinh_thuc": "TIEN_MAT"},
        {"so_tien": -1, "hinh_thuc": "TIEN_MAT"},
        {"so_tien": 1000.5, "hinh_thuc": "TIEN_MAT"},
        {"so_tien": "500000", "hinh_thuc": "TIEN_MAT"},
        {"so_tien": True, "hinh_thuc": "TIEN_MAT"},
        {"so_tien": 1_000_000_000_001, "hinh_thuc": "TIEN_MAT"},
        {"so_tien": 500_000, "hinh_thuc": "SEC"},
        {"so_tien": 500_000},
        {"hinh_thuc": "TIEN_MAT"},
        {"so_tien": 500_000, "hinh_thuc": "TIEN_MAT", "tai_xe_id": 1},
    ],
)
def test_uc23_ac4_du_lieu_sai(client, db, c01, body):
    r = client.post(f"/api/chuyen/{c01}/tam-ung", json=body)
    assert r.status_code == 400, r.text
    assert khoan(db, c01) == []


def test_uc23_ac4_tran_so_tien_khong_vuot_dinh_muc_thi_qua_api(client, db, c01):
    sua(db, Chuyen, c01, dm_dau_chot=1_000_000_000_000)  # định mức lớn: đúng bằng trần vẫn nhận
    assert cap(client, c01, 1_000_000_000_000).status_code == 201


def test_uc23_ac4_khong_tim_thay(client, c01):
    assert ma(cap(client, 999999, 1000)) == (404, "KHONG_TIM_THAY")
    assert sua_tu(client, 999999, 1000).status_code == 404
    assert thu_hoi(client, 999999).status_code == 404
    assert client.get("/api/chuyen/999999/tam-ung").status_code == 404


# AC5 – khoản đã thu hồi không tính vào tổng
def test_uc23_ac5_thu_hoi_roi_cap_lai(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    assert thu_hoi(client, tu).status_code == 200
    assert cap(client, c01, DINH_MUC).status_code == 201
    assert [k.trang_thai for k in khoan(db, c01)] == ["DA_THU_HOI", "HIEU_LUC"]


# AC6 – sửa (TC-BR53-05)
def test_uc23_ac6_sua_giam(client, dang_nhap_voi, db, c01):
    kt = dang_nhap_voi("KE_TOAN")
    tu = cap(client, c01, DINH_MUC).json()["id"]
    r = sua_tu(client, tu, 800_000, ly_do="  ghi nhầm số  ", hinh_thuc="CHUYEN_KHOAN")
    assert r.status_code == 200, r.text
    assert (r.json()["so_tien"], r.json()["hinh_thuc"]) == (800_000, "CHUYEN_KHOAN")
    nk = nhat_ky(db, tu)[-1]
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.ly_do, nk.nguoi) == (
        "SUA",
        "1000000 TIEN_MAT",
        "800000 CHUYEN_KHOAN",
        "ghi nhầm số",
        kt.id,
    )


def test_uc23_ac6_sua_vuot(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    assert ma(sua_tu(client, tu, 1_100_000)) == (422, "BR-53")
    assert khoan(db, c01)[0].so_tien == DINH_MUC
    assert len(nhat_ky(db, tu)) == 1


def test_uc23_ac6_sua_bien_tinh_cac_khoan_khac(client, db, c01):
    a = cap(client, c01, 300_000).json()["id"]
    cap(client, c01, 500_000)
    assert sua_tu(client, a, 500_000).status_code == 200  # 500.000 + 500.000 = đúng định mức
    assert ma(sua_tu(client, a, 500_001)) == (422, "BR-53")
    assert sua_tu(client, a, 500_000, hinh_thuc="TIEN_MAT").status_code == 400  # giữ nguyên


@pytest.mark.parametrize("ly_do", [None, "", "   ", "x" * 301])
def test_uc23_ac6_ly_do_sai(client, db, c01, ly_do):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    assert sua_tu(client, tu, 900_000, ly_do=ly_do).status_code == 400
    assert khoan(db, c01)[0].so_tien == DINH_MUC


def test_uc23_ac6_khong_thay_doi(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    assert ma(sua_tu(client, tu, DINH_MUC)) == (400, "KHONG_CO_THAY_DOI")
    assert len(nhat_ky(db, tu)) == 1


# AC7 – sửa, thu hồi theo trạng thái
def test_uc23_ac7_hoan_thanh_van_sua_thu_hoi(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    sua(db, Chuyen, c01, trang_thai="HOAN_THANH")
    assert sua_tu(client, tu, 900_000).status_code == 200
    assert thu_hoi(client, tu).status_code == 200


def test_uc23_ac7_khoan_da_thu_hoi(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    thu_hoi(client, tu)
    assert ma(sua_tu(client, tu, 500_000)) == (409, "BR-53")
    assert khoan(db, c01)[0].so_tien == DINH_MUC


def test_uc23_ac7_da_quyet_toan(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    sua(db, Chuyen, c01, trang_thai="DA_QUYET_TOAN")
    assert ma(sua_tu(client, tu, 500_000)) == (409, "BR-29")
    assert ma(thu_hoi(client, tu)) == (409, "BR-29")
    assert (khoan(db, c01)[0].so_tien, khoan(db, c01)[0].trang_thai) == (DINH_MUC, "HIEU_LUC")
    assert len(nhat_ky(db, tu)) == 1


# AC8 – thu hồi (TC-BR62-01)
def test_uc23_ac8_thu_hoi(client, dang_nhap_voi, db, c01):
    kt = dang_nhap_voi("KE_TOAN")
    tu = cap(client, c01, DINH_MUC).json()["id"]
    r = thu_hoi(client, tu)
    assert (r.status_code, r.json()["trang_thai"]) == (200, "DA_THU_HOI")
    tao, th = nhat_ky(db, tu)
    assert (tao.hanh_dong, tao.gia_tri_cu, tao.gia_tri_moi) == ("TAO", None, "1000000 TIEN_MAT")
    assert (th.hanh_dong, th.gia_tri_cu, th.gia_tri_moi, th.ly_do) == (
        "THU_HOI",
        "HIEU_LUC",
        "DA_THU_HOI",
        "Tài xế đã nộp lại tạm ứng",
    )
    assert {tao.nguoi, th.nguoi} == {kt.id} and tao.luc <= th.luc
    assert ma(thu_hoi(client, tu)) == (409, "BR-53")
    assert len(nhat_ky(db, tu)) == 2


def test_uc23_ac8_thu_hoi_co_ly_do(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    assert thu_hoi(client, tu, ly_do="Mở chốt để ghép thêm").status_code == 200
    assert nhat_ky(db, tu)[-1].ly_do == "Mở chốt để ghép thêm"
    tu2 = cap(client, c01, DINH_MUC).json()["id"]
    assert thu_hoi(client, tu2, ly_do="x" * 301).status_code == 400


# AC9 – nối UC-15, 16 (TC-BR24-01/02, TC-BR25-02)
def test_uc23_ac9_mo_chot_sau_thu_hoi(client, dang_nhap_voi, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    dang_nhap_voi("DIEU_PHOI")
    assert ma(mo_chot(client, c01)) == (409, "BR-24")
    dang_nhap_voi("KE_TOAN")
    thu_hoi(client, tu)
    dang_nhap_voi("DIEU_PHOI")
    assert mo_chot(client, c01).status_code == 200
    assert chuyen(db, c01).trang_thai == "LAP"


def test_uc23_ac9_huy_sau_thu_hoi(client, dang_nhap_voi, db, c01):
    tu = cap(client, c01, 400_000).json()["id"]
    dang_nhap_voi("DIEU_PHOI")
    huy = lambda: client.post(f"/api/chuyen/{c01}/huy", json={"ly_do": "khách hoãn"})  # noqa: E731
    assert ma(huy()) == (409, "BR-25")
    dang_nhap_voi("KE_TOAN")
    thu_hoi(client, tu)
    dang_nhap_voi("DIEU_PHOI")
    assert huy().status_code == 200
    assert chuyen(db, c01).trang_thai == "HUY"


# AC10 – nhật ký chỉ thêm
def test_uc23_ac10_nhat_ky_chi_them(client, db, c01):
    tu = cap(client, c01, DINH_MUC).json()["id"]
    truoc = [(n.id, n.gia_tri_moi) for n in nhat_ky(db, tu)]
    sua_tu(client, tu, 700_000)
    thu_hoi(client, tu)
    dong = nhat_ky(db, tu)
    assert [n.hanh_dong for n in dong] == ["TAO", "SUA", "THU_HOI"]
    assert [(n.id, n.gia_tri_moi) for n in dong[:1]] == truoc
    assert dong[0].id < dong[1].id < dong[2].id


# AC11 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "TAI_XE", "QUAN_LY"])
def test_uc23_ac11_khong_phai_ke_toan_khong_ghi(client, dang_nhap_voi, db, c01, vai_tro):
    tu = cap(client, c01, 500_000).json()["id"]
    dang_nhap_voi(vai_tro)
    assert ma(cap(client, c01, 100_000)) == (403, "KHONG_DU_QUYEN")
    assert sua_tu(client, tu, 400_000).status_code == 403
    assert thu_hoi(client, tu).status_code == 403
    assert [(k.so_tien, k.trang_thai) for k in khoan(db, c01)] == [(500_000, "HIEU_LUC")]


@pytest.mark.parametrize(
    ("vai_tro", "ma_tt"), [("QUAN_LY", 200), ("KE_TOAN", 200), ("DIEU_PHOI", 403), ("TAI_XE", 403)]
)
def test_uc23_ac11_xem(client, dang_nhap_voi, c01, vai_tro, ma_tt):
    dang_nhap_voi(vai_tro)
    assert client.get(f"/api/chuyen/{c01}/tam-ung").status_code == ma_tt
    assert client.get("/api/tam-ung").status_code == ma_tt


def test_uc23_ac11_chua_dang_nhap(client, kb):
    assert cap(client, 1, 1000).status_code == 401
    assert sua_tu(client, 1, 1000).status_code == 401
    assert thu_hoi(client, 1).status_code == 401
    assert client.get("/api/chuyen/1/tam-ung").status_code == 401
    assert client.get("/api/tam-ung").status_code == 401


# AC12 – xem
def test_uc23_ac12_theo_chuyen(client, db, c01):
    j = client.get(f"/api/chuyen/{c01}/tam-ung").json()
    assert (j["dinh_muc"], j["tong_hieu_luc"], j["con_duoc_cap"], j["khoan"]) == (DINH_MUC, 0, DINH_MUC, [])
    a = cap(client, c01, 700_000).json()["id"]
    cap(client, c01, 300_000)
    thu_hoi(client, a)
    j = client.get(f"/api/chuyen/{c01}/tam-ung").json()
    assert (j["tong_hieu_luc"], j["con_duoc_cap"]) == (300_000, 700_000)
    assert [(k["so_tien"], k["trang_thai"]) for k in j["khoan"]] == [(700_000, "DA_THU_HOI"), (300_000, "HIEU_LUC")]


def test_uc23_ac12_con_duoc_cap_khong_am(client, db, c01):
    cap(client, c01, DINH_MUC)
    sua(db, Chuyen, c01, dm_dau_chot=0)  # định mức thấp hơn số đã cấp (dữ liệu cũ): gợi ý 0, không âm
    assert client.get(f"/api/chuyen/{c01}/tam-ung").json()["con_duoc_cap"] == 0


def test_uc23_ac12_danh_sach_loc(client, dang_nhap_voi, db, kb, c01):
    dang_nhap_voi("DIEU_PHOI")
    c02 = lap(client, kb, gio=13, xe="x4", tai_xe="dung")
    sua(db, Chuyen, c02, trang_thai="DA_CHOT", dm_dau_chot=500_000)
    dang_nhap_voi("KE_TOAN")
    a = cap(client, c01, 600_000).json()["id"]
    b = cap(client, c02, 200_000).json()["id"]
    thu_hoi(client, a)

    def ids(**loc):
        r = client.get("/api/tam-ung", params=loc)
        assert r.status_code == 200
        return [k["id"] for k in r.json()["du_lieu"]], r.json()["tong"]

    assert ids() == ([b, a], 2)
    assert ids(trang_thai="DA_THU_HOI") == ([a], 1)
    assert ids(chuyen_id=c02) == ([b], 1)
    assert ids(tai_xe_id=kb["dung"]) == ([b], 1)
    assert ids(trang_thai="HIEU_LUC", chuyen_id=c01) == ([], 0)
    assert ids(so_dong=1, trang=2) == ([a], 2)
    assert client.get("/api/tam-ung", params={"trang_thai": "XYZ"}).status_code == 400


# AC13 – đồng thời
def test_uc23_ac13_cap_dong_thoi(client, db, c01):
    ket_qua: list = []
    cho = threading.Barrier(2)

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "ke_toan", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua.append(cap(c, c01, 600_000))

    luong = [threading.Thread(target=gui) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sorted(r.status_code for r in ket_qua) == [201, 422]
    assert sum(k.so_tien for k in khoan(db, c01)) == 600_000
