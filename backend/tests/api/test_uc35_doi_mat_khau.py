from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.auth import service
from app.auth.bao_mat import dung_mat_khau
from app.models import NguoiDung

CU, MOI = "matkhau123", "matkhaumoi456"


def doi(client, cu=CU, moi=MOI, **them):
    return client.put("/api/auth/mat-khau", json={"mat_khau_cu": cu, "mat_khau_moi": moi, **them})


def dang_nhap(client, ten, mat_khau):
    return client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": mat_khau})


def nd(db, ten) -> NguoiDung:
    db.expire_all()
    return db.scalar(select(NguoiDung).where(NguoiDung.ten_dang_nhap == ten))


# AC1 – đổi đúng
def test_uc35_ac1_doi_dung(client, db, dang_nhap_voi):
    tai = dang_nhap_voi("KE_TOAN")
    tai.so_lan_sai = 3  # đang có vài lần sai
    db.commit()
    assert doi(client).status_code == 204
    assert dung_mat_khau(nd(db, "ke_toan").mat_khau_bam, MOI) and nd(db, "ke_toan").so_lan_sai == 0
    assert dang_nhap(client, "ke_toan", CU).status_code == 401
    assert dang_nhap(client, "ke_toan", MOI).status_code == 200


# AC2 – sai mật khẩu cũ: 422, không đổi, tính như đăng nhập sai, khóa sau 5 lần
def test_uc35_ac2_sai_mat_khau_cu_khoa_sau_5_lan(client, db, dang_nhap_voi):
    dang_nhap_voi("TAI_XE")
    for i in range(4):
        r = doi(client, cu="sai-mat-khau")
        assert (r.status_code, r.json()["ma"]) == (422, "SAI_MAT_KHAU_CU"), i
    assert nd(db, "tai_xe").so_lan_sai == 4 and dung_mat_khau(nd(db, "tai_xe").mat_khau_bam, CU)
    assert doi(client, cu="sai-mat-khau").status_code == 422  # lần 5: sai và bị khóa
    assert nd(db, "tai_xe").khoa_den is not None
    r = doi(client)  # đúng mật khẩu nhưng đang khóa
    assert (r.status_code, r.json()["ma"]) == (429, "KHOA_TAM")
    assert dang_nhap(client, "tai_xe", CU).status_code == 429  # đăng nhập cũng bị khóa (dùng chung bộ đếm)
    assert dung_mat_khau(nd(db, "tai_xe").mat_khau_bam, CU)


def test_uc35_ac2_het_khoa_doi_duoc(client, db, dang_nhap_voi):
    dang_nhap_voi("TAI_XE")
    n = nd(db, "tai_xe")
    n.khoa_den = datetime.now(UTC) - timedelta(minutes=1)  # đã hết 15 phút
    db.commit()
    assert doi(client).status_code == 204


def test_uc35_ac2_tre_gio_dung_bo_dem_service(db, tao_nguoi_dung):
    n = tao_nguoi_dung(ten="x1")
    gio = datetime(2030, 1, 1, tzinfo=UTC)
    for _ in range(service.SO_LAN_SAI_TOI_DA):
        with pytest.raises(Exception, match="Mật khẩu hiện tại"):
            service.doi_mat_khau(db, n.id, "sai", MOI, gio)
    assert nd(db, "x1").khoa_den == gio + service.THOI_GIAN_KHOA


# AC3 – dữ liệu sai
def test_uc35_ac3_trung_mat_khau_cu(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    r = doi(client, moi=CU)
    assert (r.status_code, r.json()["ma"]) == (422, "MAT_KHAU_TRUNG")


@pytest.mark.parametrize(
    "body",
    [
        {"mat_khau_cu": CU},  # thiếu mới
        {"mat_khau_moi": MOI},  # thiếu cũ
        {"mat_khau_cu": CU, "mat_khau_moi": "1234567"},  # 7 ký tự
        {"mat_khau_cu": CU, "mat_khau_moi": "x" * 201},
        {"mat_khau_cu": CU, "mat_khau_moi": MOI, "id": 1},  # trường lạ (không đổi của người khác)
    ],
)
def test_uc35_ac3_du_lieu_sai(client, db, dang_nhap_voi, body):
    dang_nhap_voi("DIEU_PHOI")
    assert client.put("/api/auth/mat-khau", json=body).status_code == 400
    assert dung_mat_khau(nd(db, "dieu_phoi").mat_khau_bam, CU)


def test_uc35_ac3_bien_8_ky_tu(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert doi(client, moi="12345678").status_code == 204  # đúng 8 ký tự: được


# AC4 – mọi vai trò; chưa đăng nhập; chỉ của chính mình
@pytest.mark.parametrize("vai_tro", ["QUAN_LY", "DIEU_PHOI", "KE_TOAN", "TAI_XE"])
def test_uc35_ac4_moi_vai_tro(client, db, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert doi(client).status_code == 204


def test_uc35_ac4_chua_dang_nhap(client):
    assert doi(client).status_code == 401


def test_uc35_ac4_khong_dung_den_nguoi_khac(client, db, dang_nhap_voi, tao_nguoi_dung):
    khac = tao_nguoi_dung(ten="nguoi_khac", vai_tro="KE_TOAN")
    dang_nhap_voi("DIEU_PHOI")
    assert doi(client).status_code == 204
    assert dung_mat_khau(nd(db, "nguoi_khac").mat_khau_bam, CU) and khac.so_lan_sai == 0
