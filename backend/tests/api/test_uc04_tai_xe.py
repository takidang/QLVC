from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.auth.bao_mat import bam_mat_khau
from app.main import app
from app.models import NguoiDung, TaiXe

AN = {  # tài xế An trong kịch bản nghiep-vu.md mục 11
    "ten_dang_nhap": "an",
    "ho_ten": "Nguyễn Văn An",
    "mat_khau": "matkhau123",
    "so_gplx": "790123456789",
    "hang_gplx": "C",
    "han_gplx": "2030-05-31",
    "sdt": "0909111222",
}


def them(client, **doi):
    return client.post("/api/tai-xe", json={**AN, **doi})


def dem(db, bang) -> int:
    return db.scalar(select(func.count()).select_from(bang))


def client_rieng():
    """Client thứ hai để tài xế đăng nhập song song với Điều phối (mỗi client giữ cookie riêng)."""
    return TestClient(app, base_url="https://testserver")


# AC1 – thêm tài xế tạo luôn tài khoản TAI_XE, không lộ mật khẩu, chuẩn hóa dữ liệu
def test_uc04_ac1_them_tai_xe_hop_le(client, dang_nhap_voi, db):
    dang_nhap_voi("DIEU_PHOI")
    r = them(client, so_gplx=" 79ab 123456 ", hang_gplx="c", sdt="+84 909.111.222")
    assert r.status_code == 201
    tx = r.json()
    assert tx["trang_thai"] == "HOAT_DONG"
    assert tx["so_gplx"] == "79AB123456"
    assert tx["hang_gplx"] == "C"
    assert tx["sdt"] == "0909111222"
    assert tx["ten_dang_nhap"] == "an" and tx["ho_ten"] == "Nguyễn Văn An"
    assert not {"mat_khau", "mat_khau_bam"} & tx.keys()
    assert "matkhau123" not in r.text

    nd = db.scalar(select(NguoiDung).where(NguoiDung.ten_dang_nhap == "an"))
    assert nd.vai_tro == "TAI_XE" and nd.trang_thai == "HOAT_DONG"
    assert nd.mat_khau_bam != "matkhau123"  # đã băm

    with client_rieng() as c:
        dn = c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "an", "mat_khau": "matkhau123"})
        assert dn.status_code == 200
        assert c.get("/api/auth/toi").json()["vai_tro"] == "TAI_XE"


def test_uc04_ac1_hang_c1_go_thuong_duoc_chuan_hoa(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client, hang_gplx=" c1 ").json()["hang_gplx"] == "C1"


# AC2 – dữ liệu sai bị chặn 400 và không lưu gì, kèm ca biên
@pytest.mark.parametrize(
    ("doi", "mong_doi"),
    [
        ({"mat_khau": "1234567"}, 400),  # 7 ký tự
        ({"mat_khau": "12345678"}, 201),  # biên: 8 ký tự được
        ({"hang_gplx": "D"}, 400),
        ({"hang_gplx": "A1"}, 400),
        ({"hang_gplx": ""}, 400),
        ({"so_gplx": "12345"}, 400),  # 5 ký tự
        ({"so_gplx": "123456"}, 201),  # biên: 6 ký tự được
        ({"so_gplx": "1" * 20}, 201),  # biên: 20 ký tự được
        ({"so_gplx": "1" * 21}, 400),
        ({"so_gplx": "79-0123"}, 400),  # chỉ chữ và số
        ({"ho_ten": "   "}, 400),
        ({"ten_dang_nhap": ""}, 400),
        ({"han_gplx": None}, 400),
        ({"han_gplx": "khong-phai-ngay"}, 400),
        ({"sdt": "12345"}, 400),
        ({"vai_tro": "QUAN_LY"}, 400),  # không cho tự chọn vai trò
    ],
)
def test_uc04_ac2_du_lieu_sai_bi_chan(client, dang_nhap_voi, db, doi, mong_doi):
    dang_nhap_voi("DIEU_PHOI")
    so_nd_truoc = dem(db, NguoiDung)
    assert them(client, **doi).status_code == mong_doi
    da_luu = mong_doi == 201
    assert dem(db, TaiXe) == (1 if da_luu else 0)
    assert dem(db, NguoiDung) == so_nd_truoc + (1 if da_luu else 0)


@pytest.mark.parametrize("thieu", ["ten_dang_nhap", "ho_ten", "mat_khau", "so_gplx", "hang_gplx", "han_gplx", "sdt"])
def test_uc04_ac2_thieu_truong_bi_chan(client, dang_nhap_voi, thieu):
    dang_nhap_voi("DIEU_PHOI")
    vao = {k: v for k, v in AN.items() if k != thieu}
    assert client.post("/api/tai-xe", json=vao).status_code == 400


# AC3 – trùng tên đăng nhập hoặc số GPLX: 409, không tạo gì (một giao dịch)
def test_uc04_ac3_trung_ten_dang_nhap(client, dang_nhap_voi, db):
    dp = dang_nhap_voi("DIEU_PHOI")
    so_nd = dem(db, NguoiDung)
    r = them(client, ten_dang_nhap=dp.ten_dang_nhap, so_gplx="111111")  # trùng cả tài khoản không phải tài xế
    assert r.status_code == 409
    assert r.json()["ma"] == "TEN_DANG_NHAP_TRUNG"
    assert dem(db, NguoiDung) == so_nd
    assert dem(db, TaiXe) == 0


def test_uc04_ac3_trung_so_gplx_khong_tao_thua_tai_khoan(client, dang_nhap_voi, db):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client).status_code == 201
    so_nd = dem(db, NguoiDung)
    r = them(client, ten_dang_nhap="binh", so_gplx=" 790123456789 ")
    assert r.status_code == 409
    assert r.json()["ma"] == "SO_GPLX_TRUNG"
    assert dem(db, NguoiDung) == so_nd  # tài khoản "binh" không bị tạo thừa
    assert db.scalar(select(NguoiDung.id).where(NguoiDung.ten_dang_nhap == "binh")) is None


def test_uc04_ac3_trung_so_gplx_khac_hoa_thuong(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client, so_gplx="79AB123456").status_code == 201
    assert them(client, ten_dang_nhap="binh", so_gplx="79ab 123456").status_code == 409


def test_uc04_ac3_rang_buoc_unique_o_csdl(client, dang_nhap_voi, db):
    # Giả lập người kia vừa lưu xong cùng số GPLX: yêu cầu này phải nhận 409 chứ không 500
    nd = NguoiDung(ten_dang_nhap="khac", ho_ten="Khác", vai_tro="TAI_XE", mat_khau_bam=bam_mat_khau("matkhau123"))
    db.add(nd)
    db.flush()
    db.add(
        TaiXe(nguoi_dung_id=nd.id, so_gplx=AN["so_gplx"], hang_gplx="C", han_gplx=date(2030, 1, 1), sdt="0909000000")
    )
    db.commit()
    dang_nhap_voi("DIEU_PHOI")
    assert them(client).status_code == 409
    assert db.scalar(select(NguoiDung.id).where(NguoiDung.ten_dang_nhap == "an")) is None


# AC5 – hạn GPLX đã qua vẫn lưu được (chặn ở UC-11, 12)
def test_uc04_ac5_han_gplx_da_qua_van_luu(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    r = them(client, han_gplx="2020-01-01")
    assert r.status_code == 201
    assert r.json()["han_gplx"] == "2020-01-01"
    tx_id = r.json()["id"]
    assert client.patch(f"/api/tai-xe/{tx_id}", json={"han_gplx": "2019-12-31"}).status_code == 200
    assert client.get("/api/tai-xe").json()["du_lieu"][0]["han_gplx"] == "2019-12-31"


# AC6 – danh sách: lọc, tìm theo họ tên / số GPLX / SĐT, phân trang
def _ba_tai_xe(client):
    them(client, ten_dang_nhap="an", ho_ten="Nguyễn Văn An", so_gplx="111111", sdt="0909111111")
    them(client, ten_dang_nhap="binh", ho_ten="Trần Bình", so_gplx="222222", sdt="0909222222")
    id_cuong = them(client, ten_dang_nhap="cuong", ho_ten="Lê Cường", so_gplx="AB3333", sdt="0909333333").json()["id"]
    client.patch(f"/api/tai-xe/{id_cuong}", json={"trang_thai": "NGUNG"})


def test_uc04_ac6_danh_sach_loc_tim_phan_trang(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    _ba_tai_xe(client)

    def tim(**p):
        return client.get("/api/tai-xe", params=p).json()

    assert [t["ten_dang_nhap"] for t in tim(tim="nguyễn")["du_lieu"]] == ["an"]  # họ tên, không phân biệt hoa thường
    assert [t["ten_dang_nhap"] for t in tim(tim="ab33")["du_lieu"]] == ["cuong"]  # số GPLX
    assert [t["ten_dang_nhap"] for t in tim(tim="222222")["du_lieu"]] == ["binh"]  # trùng cả SĐT lẫn GPLX vẫn 1 dòng
    assert [t["ten_dang_nhap"] for t in tim(tim="0909111")["du_lieu"]] == ["an"]  # SĐT
    assert tim(trang_thai="NGUNG")["tong"] == 1
    assert tim(trang_thai="HOAT_DONG")["tong"] == 2

    trang2 = tim(trang=2, so_dong=2)
    assert trang2["tong"] == 3 and len(trang2["du_lieu"]) == 1
    assert tim(trang=9, so_dong=2) == {"du_lieu": [], "tong": 3}
    assert client.get("/api/tai-xe", params={"trang_thai": "XOA"}).status_code == 400


def test_uc04_ac6_tim_khong_hieu_ky_tu_dac_biet(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    _ba_tai_xe(client)
    assert client.get("/api/tai-xe", params={"tim": "%"}).json()["tong"] == 0
    assert client.get("/api/tai-xe", params={"tim": "_"}).json()["tong"] == 0
    assert client.get("/api/tai-xe", params={"tim": "   "}).json()["tong"] == 3
    assert client.get("/api/tai-xe", params={"tim": "."}).json()["tong"] == 0  # không khớp mọi SĐT
    assert client.get("/api/tai-xe", params={"tim": "-"}).json()["tong"] == 0


def test_uc04_ac6_tim_sdt_co_dau_cach_hoac_cham(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    _ba_tai_xe(client)
    for go in ("0909 111", "0909.111", "0909-111"):
        assert [t["ten_dang_nhap"] for t in client.get("/api/tai-xe", params={"tim": go}).json()["du_lieu"]] == ["an"]


# AC7 – sửa: họ tên trên tài khoản, GPLX/SĐT trên tài xế; không sửa tên đăng nhập, mật khẩu
def test_uc04_ac7_sua_tai_xe(client, dang_nhap_voi, db):
    dang_nhap_voi("DIEU_PHOI")
    tx_id = them(client).json()["id"]
    r = client.patch(
        f"/api/tai-xe/{tx_id}",
        json={"ho_ten": "Nguyễn Văn An B", "so_gplx": "790999999999", "hang_gplx": "c1", "sdt": "0909999999"},
    )
    assert r.status_code == 200
    tx = r.json()
    assert (tx["ho_ten"], tx["so_gplx"], tx["hang_gplx"], tx["sdt"]) == (
        "Nguyễn Văn An B",
        "790999999999",
        "C1",
        "0909999999",
    )
    db.expire_all()
    assert db.scalar(select(NguoiDung.ho_ten).where(NguoiDung.ten_dang_nhap == "an")) == "Nguyễn Văn An B"
    assert client.get(f"/api/tai-xe/{tx_id}").json() == tx


@pytest.mark.parametrize(
    "vao",
    [
        {"ten_dang_nhap": "an2"},
        {"mat_khau": "matkhaumoi123"},
        {"ho_ten": None},
        {"so_gplx": None},
        {"hang_gplx": None},
        {"han_gplx": None},
        {"sdt": None},
        {"trang_thai": None},
        {"hang_gplx": "D"},
    ],
)
def test_uc04_ac7_sua_sai_bi_chan(client, dang_nhap_voi, vao):
    dang_nhap_voi("DIEU_PHOI")
    tx_id = them(client).json()["id"]
    assert client.patch(f"/api/tai-xe/{tx_id}", json=vao).status_code == 400
    assert client.get(f"/api/tai-xe/{tx_id}").json()["ten_dang_nhap"] == "an"


def test_uc04_ac7_sua_so_gplx_trung(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    them(client)
    id_binh = them(client, ten_dang_nhap="binh", so_gplx="222222").json()["id"]
    r = client.patch(f"/api/tai-xe/{id_binh}", json={"so_gplx": AN["so_gplx"]})
    assert r.status_code == 409
    assert r.json()["ma"] == "SO_GPLX_TRUNG"
    assert client.get(f"/api/tai-xe/{id_binh}").json()["so_gplx"] == "222222"


# AC8 – ngừng tài xế khóa luôn tài khoản ngay; hoạt động lại mở lại; không có xóa
def test_uc04_ac8_ngung_khoa_tai_khoan_va_mo_lai(client, dang_nhap_voi, db):
    dang_nhap_voi("DIEU_PHOI")
    tx_id = them(client).json()["id"]
    dang_nhap_an = {"ten_dang_nhap": "an", "mat_khau": "matkhau123"}

    with client_rieng() as tai_xe:
        assert tai_xe.post("/api/auth/dang-nhap", json=dang_nhap_an).status_code == 200
        assert tai_xe.get("/api/auth/toi").status_code == 200

        r = client.patch(f"/api/tai-xe/{tx_id}", json={"trang_thai": "NGUNG"})
        assert r.status_code == 200 and r.json()["trang_thai"] == "NGUNG"
        db.expire_all()
        assert db.scalar(select(NguoiDung.trang_thai).where(NguoiDung.ten_dang_nhap == "an")) == "NGUNG"
        assert tai_xe.get("/api/auth/toi").status_code == 401  # token đang dùng mất hiệu lực ngay
        assert tai_xe.post("/api/auth/dang-nhap", json=dang_nhap_an).status_code != 200

        assert client.patch(f"/api/tai-xe/{tx_id}", json={"trang_thai": "HOAT_DONG"}).status_code == 200
        assert tai_xe.post("/api/auth/dang-nhap", json=dang_nhap_an).status_code == 200
        assert tai_xe.get("/api/auth/toi").status_code == 200


def test_uc04_ac8_trang_thai_sai_va_khong_xoa(client, dang_nhap_voi, db):
    dang_nhap_voi("DIEU_PHOI")
    tx_id = them(client).json()["id"]
    assert client.patch(f"/api/tai-xe/{tx_id}", json={"trang_thai": "XOA"}).status_code == 400
    assert client.delete(f"/api/tai-xe/{tx_id}").status_code == 405
    assert dem(db, TaiXe) == 1


# AC9 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "xem", "sua"),
    [("DIEU_PHOI", 200, True), ("QUAN_LY", 200, True), ("KE_TOAN", 200, False), ("TAI_XE", 403, False)],
)
def test_uc04_ac9_phan_quyen(client, dang_nhap_voi, db, vai_tro, xem, sua):
    dang_nhap_voi("DIEU_PHOI")
    tx_id = them(client).json()["id"]
    dang_nhap_voi(vai_tro)
    assert client.get("/api/tai-xe").status_code == xem
    assert client.get(f"/api/tai-xe/{tx_id}").status_code == xem
    r_them = them(client, ten_dang_nhap="moi", so_gplx="555555")
    r_sua = client.patch(f"/api/tai-xe/{tx_id}", json={"ho_ten": "Đổi tên"})
    if sua:
        assert (r_them.status_code, r_sua.status_code) == (201, 200)
    else:
        assert (r_them.status_code, r_sua.status_code) == (403, 403)
        assert db.scalar(select(NguoiDung.id).where(NguoiDung.ten_dang_nhap == "moi")) is None


def test_uc04_ac9_chua_dang_nhap_va_khong_ton_tai(client, dang_nhap_voi):
    assert client.get("/api/tai-xe").status_code == 401
    assert them(client).status_code == 401
    assert client.patch("/api/tai-xe/1", json={"ho_ten": "X"}).status_code == 401
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/tai-xe/999").status_code == 404
    assert client.patch("/api/tai-xe/999", json={"ho_ten": "X"}).status_code == 404
