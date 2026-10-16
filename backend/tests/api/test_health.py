from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, field_validator

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"trang_thai": "ok"}


def test_du_lieu_sai_kieu_tra_400_khong_phai_422():
    @app.get("/api/_test_kieu")
    def _test_kieu(n: int) -> dict:
        return {"n": n}

    r = client.get("/api/_test_kieu", params={"n": "abc"})
    assert r.status_code == 400
    assert r.json()["ma"] == "DU_LIEU_KHONG_HOP_LE"


def test_loi_400_khong_tra_lai_gia_tri_nguoi_dung_gui():
    class Vao(BaseModel):
        mat_khau: str = Field(max_length=10)
        sdt: str

        @field_validator("sdt")
        @classmethod
        def kiem_sdt(cls, v: str) -> str:
            raise ValueError("Số điện thoại không hợp lệ")  # validator tự viết: ctx chứa ValueError

    @app.post("/api/_test_bao_mat_loi")
    def _test_bao_mat_loi(vao: Vao) -> dict:
        return {}

    r = client.post("/api/_test_bao_mat_loi", json={"mat_khau": "BIMAT-" + "x" * 20, "sdt": "abc"})
    assert r.status_code == 400  # không thành 500 vì ctx không đổi sang JSON được
    assert "BIMAT" not in r.text
    assert all(set(e) == {"loc", "msg", "type"} for e in r.json()["chi_tiet"])
