from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.loi import LoiNghiepVu
from app.main import app
from app.models import NguoiDung
from app.modules.nguoi_dung import service
from app.modules.nguoi_dung.schemas import NguoiDungSua

BINH = {"ten_dang_nhap": "binh", "ho_ten": "Trần Thị Bình", "mat_khau": "matkhau123", "vai_tro": "KE_TOAN"}


def them(client, **doi):
    return client.post("/api/nguoi-dung", json={**BINH, **doi})


def dem(db) -> int:
    return db.scalar(select(func.count()).select_from(NguoiDung))


def client_rieng():
    """Client thứ hai giữ cookie riêng, để người bị sửa đăng nhập song song với Quản lý."""
    return TestClient(app, base_url="https://testserver")


def dang_nhap(c, ten, mat_khau="matkhau123"):
    return c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": mat_khau})


# AC1 – thêm tài khoản, mật khẩu băm, không lộ mật khẩu
@pytest.mark.parametrize("vai_tro", ["QUAN_LY", "DIEU_PHOI", "KE_TOAN"])
def test_uc02_ac1_them_hop_le(client, dang_nhap_voi, db, vai_tro):
    dang_nhap_voi("QUAN_LY")
    r = them(client, vai_tro=vai_tro, ho_ten="  Trần Thị Bình ")
    assert r.status_code == 201
    nd = r.json()
    assert (nd["vai_tro"], nd["trang_thai"], nd["ho_ten"]) == (vai_tro, "HOAT_DONG", "Trần Thị Bình")
    assert "mat_khau" not in nd and "mat_khau_bam" not in nd
    assert db.get(NguoiDung, nd["id"]).mat_khau_bam.startswith("$argon2")
    with client_rieng() as binh:
        assert dang_nhap(binh, "binh").json()["vai_tro"] == vai_tro


# AC2 – dữ liệu sai → 400, không lưu
@pytest.mark.parametrize(
    "doi",
    [
        {"mat_khau": "a" * 7},  # biên dưới - 1
        {"mat_khau": "a" * 201},  # biên trên + 1
        {"vai_tro": "TAI_XE"},  # tài xế tạo ở UC-04
        {"vai_tro": "ADMIN"},
        {"ten_dang_nhap": "   "},
        {"ho_ten": ""},
        {"ten_dang_nhap": None},
        {"la": 1},
    ],
)
def test_uc02_ac2_du_lieu_sai(client, dang_nhap_voi, db, doi):
    dang_nhap_voi("QUAN_LY")
    truoc = dem(db)
    assert them(client, **doi).status_code == 400
    assert dem(db) == truoc


@pytest.mark.parametrize("truong", ["ten_dang_nhap", "ho_ten", "mat_khau", "vai_tro"])
def test_uc02_ac2_thieu_truong(client, dang_nhap_voi, truong):
    dang_nhap_voi("QUAN_LY")
    assert client.post("/api/nguoi-dung", json={k: v for k, v in BINH.items() if k != truong}).status_code == 400


@pytest.mark.parametrize("do_dai", [8, 200])
def test_uc02_ac2_mat_khau_bien_duoc(client, dang_nhap_voi, do_dai):
    dang_nhap_voi("QUAN_LY")
    assert them(client, mat_khau="a" * do_dai).status_code == 201


# AC3 – trùng tên đăng nhập
def test_uc02_ac3_trung_ten_dang_nhap(client, dang_nhap_voi, tao_nguoi_dung, db):
    dang_nhap_voi("QUAN_LY")
    tao_nguoi_dung(ten="an", vai_tro="TAI_XE")
    truoc = dem(db)
    r = them(client, ten_dang_nhap="an")  # trùng cả tài khoản tài xế
    assert r.status_code == 409 and r.json()["ma"] == "TEN_DANG_NHAP_TRUNG"
    assert dem(db) == truoc

    binh_id = them(client).json()["id"]
    r = client.patch(f"/api/nguoi-dung/{binh_id}", json={"ten_dang_nhap": "an"})
    assert r.status_code == 409 and r.json()["ma"] == "TEN_DANG_NHAP_TRUNG"
    assert client.patch(f"/api/nguoi-dung/{binh_id}", json={"ten_dang_nhap": "binh"}).status_code == 200


# AC4 – danh sách
def test_uc02_ac4_danh_sach_loc_tim_phan_trang(client, dang_nhap_voi, tao_nguoi_dung):
    dang_nhap_voi("QUAN_LY")
    tao_nguoi_dung(ten="an", vai_tro="TAI_XE")
    tao_nguoi_dung(ten="cuong_100%", vai_tro="DIEU_PHOI", trang_thai="NGUNG")
    tao_nguoi_dung(ten="dung", vai_tro="KE_TOAN")

    r = client.get("/api/nguoi-dung").json()
    assert r["tong"] == 4  # quan_ly, an, cuong_100%, dung – có cả tài xế
    assert all("mat_khau_bam" not in d for d in r["du_lieu"])
    assert [d["ten_dang_nhap"] for d in client.get("/api/nguoi-dung?vai_tro=TAI_XE").json()["du_lieu"]] == ["an"]
    assert client.get("/api/nguoi-dung?trang_thai=NGUNG").json()["tong"] == 1
    assert client.get("/api/nguoi-dung?tim=100%25").json()["tong"] == 1  # "%" không khớp mọi dòng
    assert client.get("/api/nguoi-dung?tim=_").json()["tong"] == 2  # quan_ly, cuong_100%
    assert client.get("/api/nguoi-dung?tim=Người dun").json()["tong"] == 1  # theo họ tên
    trang2 = client.get("/api/nguoi-dung?trang=2&so_dong=3").json()
    assert (trang2["tong"], len(trang2["du_lieu"])) == (4, 1)
    assert client.get("/api/nguoi-dung?trang=9").json()["du_lieu"] == []
    assert client.get("/api/nguoi-dung?vai_tro=ADMIN").status_code == 400


# AC5 – sửa
def test_uc02_ac5_sua_va_doi_vai_tro_co_hieu_luc_ngay(client, dang_nhap_voi):
    dang_nhap_voi("QUAN_LY")
    binh_id = them(client, vai_tro="DIEU_PHOI").json()["id"]
    with client_rieng() as binh:
        dang_nhap(binh, "binh")
        assert binh.get("/api/tai-xe").status_code == 200  # Điều phối xem được tài xế

        r = client.patch(f"/api/nguoi-dung/{binh_id}", json={"ho_ten": "Bình Mới", "ten_dang_nhap": "binh2"})
        assert r.status_code == 200 and (r.json()["ho_ten"], r.json()["ten_dang_nhap"]) == ("Bình Mới", "binh2")
        r = client.patch(f"/api/nguoi-dung/{binh_id}", json={"vai_tro": "KE_TOAN"})
        assert r.status_code == 200 and r.json()["vai_tro"] == "KE_TOAN"
        assert binh.post("/api/xe", json={}).status_code == 403  # token cũ, vai trò mới
        assert dang_nhap(binh, "binh2").status_code == 200


@pytest.mark.parametrize(
    "than", [{"mat_khau": "matkhaumoi1"}, {"ho_ten": None}, {"vai_tro": None}, {"vai_tro": "TAI_XE"}]
)
def test_uc02_ac5_sua_sai(client, dang_nhap_voi, db, than):
    dang_nhap_voi("QUAN_LY")
    binh_id = them(client).json()["id"]
    assert client.patch(f"/api/nguoi-dung/{binh_id}", json=than).status_code == 400
    db.expire_all()
    assert db.get(NguoiDung, binh_id).vai_tro == "KE_TOAN"


# AC6 – khóa, mở, xóa bộ đếm khóa tạm
def test_uc02_ac6_khoa_co_hieu_luc_ngay_va_mo_lai(client, dang_nhap_voi, db):
    dang_nhap_voi("QUAN_LY")
    binh_id = them(client).json()["id"]
    with client_rieng() as binh:
        dang_nhap(binh, "binh")
        assert client.patch(f"/api/nguoi-dung/{binh_id}", json={"trang_thai": "NGUNG"}).status_code == 200
        assert binh.get("/api/auth/toi").status_code == 401
        assert dang_nhap(binh, "binh").status_code == 403

        # Đang bị khóa tạm vì sai mật khẩu, Quản lý mở lại thì đăng nhập được ngay
        nd = db.get(NguoiDung, binh_id)
        nd.so_lan_sai, nd.khoa_den = 3, datetime.now(UTC) + timedelta(minutes=10)
        db.commit()
        r = client.patch(f"/api/nguoi-dung/{binh_id}", json={"trang_thai": "HOAT_DONG"})
        assert r.status_code == 200 and r.json()["khoa_den"] is None
        db.expire_all()
        assert db.get(NguoiDung, binh_id).so_lan_sai == 0
        assert dang_nhap(binh, "binh").status_code == 200


def test_uc02_ac6_trang_thai_sai_va_khong_xoa(client, dang_nhap_voi, db):
    dang_nhap_voi("QUAN_LY")
    binh_id = them(client).json()["id"]
    assert client.patch(f"/api/nguoi-dung/{binh_id}", json={"trang_thai": "XOA"}).status_code == 400
    assert client.delete(f"/api/nguoi-dung/{binh_id}").status_code == 405
    assert db.get(NguoiDung, binh_id) is not None


# AC7 – đặt lại mật khẩu
@pytest.mark.parametrize("vai_tro", ["KE_TOAN", "TAI_XE"])
def test_uc02_ac7_dat_lai_mat_khau(client, dang_nhap_voi, tao_nguoi_dung, db, vai_tro):
    dang_nhap_voi("QUAN_LY")
    nd = tao_nguoi_dung(ten="binh", vai_tro=vai_tro)
    nd.so_lan_sai, nd.khoa_den = 0, datetime.now(UTC) + timedelta(minutes=10)
    db.commit()

    r = client.put(f"/api/nguoi-dung/{nd.id}/mat-khau", json={"mat_khau": "matkhaumoi1"})
    assert r.status_code == 204 and r.content == b""
    with client_rieng() as binh:
        assert dang_nhap(binh, "binh").status_code == 401  # mật khẩu cũ
        assert dang_nhap(binh, "binh", "matkhaumoi1").status_code == 200  # khóa tạm đã xóa


@pytest.mark.parametrize("than", [{"mat_khau": "a" * 7}, {}, {"mat_khau": "matkhaumoi1", "la": 1}])
def test_uc02_ac7_mat_khau_sai(client, dang_nhap_voi, tao_nguoi_dung, than):
    dang_nhap_voi("QUAN_LY")
    nd = tao_nguoi_dung(ten="binh", vai_tro="KE_TOAN")
    assert client.put(f"/api/nguoi-dung/{nd.id}/mat-khau", json=than).status_code == 400
    with client_rieng() as binh:
        assert dang_nhap(binh, "binh").status_code == 200  # mật khẩu cũ vẫn dùng được


# AC8 – tài khoản tài xế
def test_uc02_ac8_tai_khoan_tai_xe(client, dang_nhap_voi, tao_nguoi_dung, db):
    dang_nhap_voi("QUAN_LY")
    an = tao_nguoi_dung(ten="an", vai_tro="TAI_XE")
    for than in [{"vai_tro": "DIEU_PHOI"}, {"trang_thai": "NGUNG"}]:
        r = client.patch(f"/api/nguoi-dung/{an.id}", json=than)
        assert r.status_code == 409 and r.json()["ma"] == "TAI_KHOAN_TAI_XE"
    db.expire_all()
    assert (an.vai_tro, an.trang_thai) == ("TAI_XE", "HOAT_DONG")
    r = client.patch(f"/api/nguoi-dung/{an.id}", json={"ten_dang_nhap": "an2", "ho_ten": "Nguyễn Văn An"})
    assert r.status_code == 200 and r.json()["ten_dang_nhap"] == "an2"


# AC9 – không tự khóa mình, luôn còn một Quản lý
@pytest.mark.parametrize("than", [{"vai_tro": "DIEU_PHOI"}, {"trang_thai": "NGUNG"}])
def test_uc02_ac9_khong_tu_doi_quyen(client, dang_nhap_voi, db, than):
    ql = dang_nhap_voi("QUAN_LY")
    r = client.patch(f"/api/nguoi-dung/{ql.id}", json=than)
    assert r.status_code == 409 and r.json()["ma"] == "KHONG_TU_DOI_QUYEN"
    db.expire_all()
    assert (ql.vai_tro, ql.trang_thai) == ("QUAN_LY", "HOAT_DONG")
    assert client.patch(f"/api/nguoi-dung/{ql.id}", json={"ho_ten": "Tên mới", "vai_tro": "QUAN_LY"}).status_code == 200


def test_uc02_ac9_khoa_quan_ly_khac(client, dang_nhap_voi, tao_nguoi_dung):
    dang_nhap_voi("QUAN_LY")
    ql2 = tao_nguoi_dung(ten="ql2", vai_tro="QUAN_LY")
    assert client.patch(f"/api/nguoi-dung/{ql2.id}", json={"trang_thai": "NGUNG"}).status_code == 200


def test_uc02_ac9_quan_ly_cuoi(db, tao_nguoi_dung):
    # Gọi thẳng service: qua API thì người gọi luôn là một Quản lý khác đang hoạt động
    ql = tao_nguoi_dung(ten="ql", vai_tro="QUAN_LY")
    ke_toan = tao_nguoi_dung(ten="kt", vai_tro="KE_TOAN")
    with pytest.raises(LoiNghiepVu) as loi:
        service.sua(db, ql.id, NguoiDungSua(trang_thai="NGUNG"), ke_toan)
    assert loi.value.ma == "QUAN_LY_CUOI" and loi.value.status_code == 409


def test_uc02_ac9_hai_quan_ly_khoa_nhau_cung_luc(dang_nhap_voi, tao_nguoi_dung, db):
    a = tao_nguoi_dung(ten="qla", vai_tro="QUAN_LY")
    b = tao_nguoi_dung(ten="qlb", vai_tro="QUAN_LY")
    cho = Barrier(2)

    def khoa(ten, muc_tieu):
        with client_rieng() as c:
            dang_nhap(c, ten)
            cho.wait()
            return c.patch(f"/api/nguoi-dung/{muc_tieu}", json={"trang_thai": "NGUNG"}).status_code

    with ThreadPoolExecutor(2) as ex:
        ket_qua = sorted(ex.map(khoa, ["qla", "qlb"], [b.id, a.id]))
    # Người sau: 409 (Quản lý cuối) nếu đã qua kiểm đăng nhập, hoặc 401 nếu bị khóa trước khi kiểm
    assert ket_qua[0] == 200 and ket_qua[1] in (401, 409)
    db.expire_all()
    con = db.scalar(select(func.count()).where(NguoiDung.vai_tro == "QUAN_LY", NguoiDung.trang_thai == "HOAT_DONG"))
    assert con == 1


# AC10 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "KE_TOAN", "TAI_XE"])
def test_uc02_ac10_chi_quan_ly(client, dang_nhap_voi, tao_nguoi_dung, db, vai_tro):
    nd = tao_nguoi_dung(ten="binh", vai_tro="KE_TOAN")
    dang_nhap_voi(vai_tro)
    truoc = dem(db)
    assert client.get("/api/nguoi-dung").status_code == 403
    assert them(client, ten_dang_nhap="moi").status_code == 403
    assert client.patch(f"/api/nguoi-dung/{nd.id}", json={"vai_tro": "QUAN_LY"}).status_code == 403
    assert client.put(f"/api/nguoi-dung/{nd.id}/mat-khau", json={"mat_khau": "matkhaumoi1"}).status_code == 403
    db.expire_all()
    assert (dem(db), nd.vai_tro) == (truoc, "KE_TOAN")


def test_uc02_ac10_chua_dang_nhap_va_khong_ton_tai(client, dang_nhap_voi):
    assert client.get("/api/nguoi-dung").status_code == 401
    assert them(client).status_code == 401
    assert client.patch("/api/nguoi-dung/1", json={"ho_ten": "X"}).status_code == 401
    assert client.put("/api/nguoi-dung/1/mat-khau", json={"mat_khau": "matkhaumoi1"}).status_code == 401
    dang_nhap_voi("QUAN_LY")
    assert client.patch("/api/nguoi-dung/999", json={"ho_ten": "X"}).status_code == 404
    assert client.put("/api/nguoi-dung/999/mat-khau", json={"mat_khau": "matkhaumoi1"}).status_code == 404
