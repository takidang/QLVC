from fastapi.testclient import TestClient

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
