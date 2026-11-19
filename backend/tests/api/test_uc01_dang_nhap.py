from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import tao_quan_ly as lenh_tao_quan_ly
from app.auth.bao_mat import dung_mat_khau, tao_token
from app.auth.phu_thuoc import can_vai_tro
from app.auth.service import tao_quan_ly
from app.config import get_settings
from app.main import app
from app.models import NguoiDung


# Hai endpoint chỉ dùng trong test để kiểm can_vai_tro (AC9)
@app.get("/api/_test/dieu-phoi")
def _chi_dieu_phoi(nd: Annotated[NguoiDung, Depends(can_vai_tro("DIEU_PHOI"))]):
    return {"ok": True}


@app.get("/api/_test/ke-toan")
def _chi_ke_toan(nd: Annotated[NguoiDung, Depends(can_vai_tro("KE_TOAN"))]):
    return {"ok": True}


def dang_nhap(client: TestClient, ten="dp1", mat_khau="matkhau123"):
    return client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": mat_khau})


def ky(payload: dict, khoa: str | None = None, alg="HS256") -> str:
    return jwt.encode(payload, khoa or get_settings().jwt_secret, algorithm=alg)


def test_uc01_ac3_dang_nhap_dung_dat_cookie_httponly(client, tao_nguoi_dung):
    nd = tao_nguoi_dung()
    r = dang_nhap(client)
    assert r.status_code == 200
    assert r.json() == {"id": nd.id, "ho_ten": nd.ho_ten, "vai_tro": "DIEU_PHOI", "co_anh_dai_dien": False}
    cookie = r.headers["set-cookie"]
    assert cookie.startswith("access_token=")
    for thuoc_tinh in ("HttpOnly", "Secure", "SameSite=strict", "Max-Age=28800", "Path=/"):
        assert thuoc_tinh in cookie
    assert r.cookies["access_token"] not in r.text  # token không nằm trong body


def test_uc01_ac4_sai_mat_khau_va_sai_ten_tra_cung_mot_loi(client, tao_nguoi_dung):
    tao_nguoi_dung()
    sai_mk = dang_nhap(client, mat_khau="sai")
    sai_ten = dang_nhap(client, ten="khong_co")
    assert sai_mk.status_code == sai_ten.status_code == 401
    assert sai_mk.json() == sai_ten.json()
    assert sai_mk.json()["thong_diep"] == "Sai tên đăng nhập hoặc mật khẩu"
    assert "set-cookie" not in sai_mk.headers


def test_uc01_ac5_tai_khoan_ngung(client, tao_nguoi_dung):
    tao_nguoi_dung(trang_thai="NGUNG")
    dung = dang_nhap(client)
    assert dung.status_code == 403
    assert dung.json()["ma"] == "TAI_KHOAN_KHOA"
    assert "set-cookie" not in dung.headers
    assert dang_nhap(client, mat_khau="sai").status_code == 401


def test_uc01_ac6_toi_voi_cookie_hop_le_va_khong_cookie(client, tao_nguoi_dung):
    nd = tao_nguoi_dung()
    assert client.get("/api/auth/toi").status_code == 401
    dang_nhap(client)
    r = client.get("/api/auth/toi")
    assert r.status_code == 200
    assert r.json()["id"] == nd.id


@pytest.mark.parametrize(
    ("tao", "mong_doi"),
    [
        (lambda id_, now: ky({"sub": str(id_), "exp": now + timedelta(seconds=30)}), 200),  # còn hạn, 30s cho CI chậm
        (lambda id_, now: ky({"sub": str(id_), "exp": now - timedelta(seconds=1)}), 401),  # quá 1 giây
        (lambda id_, now: tao_token(id_, now)[:-2] + "xx", 401),  # sửa chữ ký
        (lambda id_, now: ky({"sub": str(id_), "exp": now + timedelta(hours=1)}, khoa="k" * 40), 401),  # khóa khác
        (lambda id_, now: jwt.encode({"sub": str(id_), "exp": now + timedelta(hours=1)}, None, algorithm="none"), 401),
        (lambda id_, now: ky({"sub": str(id_)}), 401),  # thiếu exp
    ],
    ids=["con_han_30_giay", "qua_1_giay", "sua_chu_ky", "khoa_khac", "alg_none", "thieu_exp"],
)
def test_uc01_ac6_token_het_han_hoac_gia_bi_tu_choi(client, tao_nguoi_dung, tao, mong_doi):
    nd = tao_nguoi_dung()
    client.cookies.set("access_token", tao(nd.id, datetime.now(UTC)))
    assert client.get("/api/auth/toi").status_code == mong_doi


def test_uc01_ac7_khoa_tai_khoan_co_hieu_luc_ngay(client, tao_nguoi_dung, db):
    nd = tao_nguoi_dung()
    dang_nhap(client)
    assert client.get("/api/auth/toi").status_code == 200
    nd.trang_thai = "NGUNG"
    db.commit()
    assert client.get("/api/auth/toi").status_code == 401


def test_uc01_ac8_dang_xuat_xoa_cookie(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client)
    r = client.post("/api/auth/dang-xuat")
    assert r.status_code == 204
    assert 'access_token=""' in r.headers["set-cookie"] or "Max-Age=0" in r.headers["set-cookie"]
    assert client.get("/api/auth/toi").status_code == 401


@pytest.mark.parametrize(
    ("vai_tro", "duong_dan", "mong_doi"),
    [
        ("DIEU_PHOI", "/api/_test/dieu-phoi", 200),
        ("TAI_XE", "/api/_test/dieu-phoi", 403),
        ("KE_TOAN", "/api/_test/dieu-phoi", 403),
        ("QUAN_LY", "/api/_test/dieu-phoi", 200),  # Quản lý kế thừa Điều phối
        ("KE_TOAN", "/api/_test/ke-toan", 200),
        ("QUAN_LY", "/api/_test/ke-toan", 403),  # không kế thừa Kế toán
        ("DIEU_PHOI", "/api/_test/ke-toan", 403),
    ],
)
def test_uc01_ac9_can_vai_tro(client, tao_nguoi_dung, vai_tro, duong_dan, mong_doi):
    tao_nguoi_dung(ten="u1", vai_tro=vai_tro)
    dang_nhap(client, ten="u1")
    r = client.get(duong_dan)
    assert r.status_code == mong_doi
    if mong_doi == 403:
        assert r.json()["ma"] == "KHONG_DU_QUYEN"


def test_uc01_ac9_chua_dang_nhap_tra_401(client):
    assert client.get("/api/_test/dieu-phoi").status_code == 401


def test_uc01_ac10_sai_5_lan_thi_khoa_15_phut(client, tao_nguoi_dung, db):
    nd = tao_nguoi_dung()
    for _ in range(5):  # lần thứ 5 vẫn là 401 (biên)
        assert dang_nhap(client, mat_khau="sai").status_code == 401
    r = dang_nhap(client)  # lần 6, mật khẩu đúng vẫn bị chặn
    assert r.status_code == 429
    assert r.json()["ma"] == "KHOA_TAM"

    db.refresh(nd)
    assert nd.khoa_den - datetime.now(UTC) <= timedelta(minutes=15)
    nd.khoa_den = datetime.now(UTC) - timedelta(seconds=1)  # giả lập đã qua 15 phút
    db.commit()
    assert dang_nhap(client).status_code == 200


def test_uc01_ac10_dang_nhap_dung_thi_dem_lai(client, tao_nguoi_dung, db):
    nd = tao_nguoi_dung()
    for _ in range(4):
        dang_nhap(client, mat_khau="sai")
    assert dang_nhap(client).status_code == 200
    for _ in range(4):
        assert dang_nhap(client, mat_khau="sai").status_code == 401
    db.refresh(nd)
    assert nd.so_lan_sai == 4
    assert nd.khoa_den is None


def test_uc01_ac11_tao_quan_ly(db):
    nd = tao_quan_ly(db, "ql1", "Quản lý 1", "matkhau123")
    assert nd.vai_tro == "QUAN_LY"
    assert dung_mat_khau(nd.mat_khau_bam, "matkhau123")

    with pytest.raises(ValueError, match="đã tồn tại"):
        tao_quan_ly(db, "ql1", "Người khác", "khac12345")
    assert db.scalars(select(NguoiDung).where(NguoiDung.ten_dang_nhap == "ql1")).one().ho_ten == "Quản lý 1"

    with pytest.raises(ValueError, match="8 ký tự"):
        tao_quan_ly(db, "ql2", "Quản lý 2", "1234567")  # biên: 7 ký tự


def test_uc01_ac11_lenh_khong_in_mat_khau(db, monkeypatch, capsys):
    tra_loi = iter(["ql9", "Quản lý 9"])
    monkeypatch.setattr("builtins.input", lambda _: next(tra_loi))
    monkeypatch.setattr(lenh_tao_quan_ly, "getpass", lambda _: "bimat-12345")
    assert lenh_tao_quan_ly.main() == 0
    ra = capsys.readouterr()
    assert "bimat-12345" not in ra.out + ra.err
    assert db.scalar(select(NguoiDung.vai_tro).where(NguoiDung.ten_dang_nhap == "ql9")) == "QUAN_LY"
