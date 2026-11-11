# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import DonHang, LichSuTrangThai
from app.modules.tra_cuu import service
from tests.api.test_uc13_ghep_don import kb, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import sua


@pytest.fixture(autouse=True)
def _xoa_dem():
    service._sai.clear()
    yield
    service._sai.clear()


@pytest.fixture
def d1(db, kb):
    """Đ1 theo TC-BR59: SĐT lấy 0909123456, nhận 0909555666; đã ghép rồi lấy hàng."""
    sua(db, DonHang, kb["d1"], sdt_lay="0909123456", sdt_nhan="0909555666", trang_thai="DA_LAY")
    # Dòng tạo đơn (tu=None) không thành mốc thứ hai: mốc tạo lấy từ tao_luc
    for tu, sang, gio, ly_do in (
        (None, "CHO_GHEP", 4, None),
        ("CHO_GHEP", "DA_GHEP", 5, None),
        ("DA_GHEP", "DA_LAY", 6, "Sự cố xe: nội bộ"),
    ):
        db.add(
            LichSuTrangThai(
                doi_tuong="DON", doi_tuong_id=kb["d1"], tu=tu, sang=sang, ly_do=ly_do, nguoi=1, luc=luc(gio)
            )
        )
    db.commit()
    return db.get(DonHang, kb["d1"])


def tra(client, ma_don, so):
    return client.post("/api/tra-cuu", json={"ma_don": ma_don, "sdt_4_so_cuoi": so})


# AC1 – mã + 4 số cuối SĐT lấy hoặc nhận (TC-BR59-01)
@pytest.mark.parametrize("so", ["3456", "5666"])
def test_uc28_ac1_tra_cuu_dung(client, d1, so):
    r = tra(client, "DH-0001", so)
    assert r.status_code == 200, r.text
    j = r.json()
    assert (j["ma_don"], j["trang_thai"]) == ("DH-0001", "DA_LAY")
    assert [m["trang_thai"] for m in j["moc"]] == ["CHO_GHEP", "DA_GHEP", "DA_LAY"]


# AC2 – chỉ trạng thái và mốc, không lộ thông tin khác (BR-59)
def test_uc28_ac2_khong_lo_thong_tin(client, d1):
    j = tra(client, "DH-0001", "3456").json()
    assert set(j) == {"ma_don", "trang_thai", "moc"}
    assert all(set(m) == {"trang_thai", "luc"} for m in j["moc"])
    assert "Sự cố" not in str(j) and "0909" not in str(j)


# AC3 – sai số, sai mã: cùng 404 (TC-BR59-02)
def test_uc28_ac3_sai_cung_thong_bao(client, d1):
    a, b = tra(client, "DH-0001", "0000"), tra(client, "DH-9999", "3456")
    assert a.status_code == b.status_code == 404
    assert a.json()["thong_diep"] == b.json()["thong_diep"] == "Không tìm thấy đơn"
    assert tra(client, "DH-0001", "9123").status_code == 404  # phải là 4 số **cuối**


# AC4 – dữ liệu sai
@pytest.mark.parametrize(
    "body",
    [
        {"ma_don": "DH-0001"},
        {"ma_don": "DH-0001", "sdt_4_so_cuoi": "345"},
        {"ma_don": "DH-0001", "sdt_4_so_cuoi": "34a6"},
        {"ma_don": "DH-0001", "sdt_4_so_cuoi": "%456"},
        {"ma_don": "D" * 21, "sdt_4_so_cuoi": "3456"},
        {"ma_don": "DH-0001", "sdt_4_so_cuoi": "3456", "x": 1},
    ],
)
def test_uc28_ac4_du_lieu_sai(client, d1, body):
    assert client.post("/api/tra-cuu", json=body).status_code == 400


# AC5 – 10 lần sai / phút / IP, lần 11 bị chặn kể cả đúng (TC-BR59-03)
def test_uc28_ac5_gioi_han_tan_suat(client, d1, monkeypatch):
    gio = [1000.0]
    monkeypatch.setattr(service, "_gio", lambda: gio[0])
    for _ in range(10):
        assert tra(client, "DH-0001", "0000").status_code == 404
    r = tra(client, "DH-0001", "3456")
    assert (r.status_code, r.json()["ma"]) == (429, "QUA_TAN_SUAT")
    with TestClient(app, base_url="https://testserver", client=("10.0.0.2", 5000)) as khac:
        assert tra(khac, "DH-0001", "3456").status_code == 200  # IP khác không bị ảnh hưởng
    gio[0] += 60  # qua cửa sổ 1 phút
    assert tra(client, "DH-0001", "3456").status_code == 200


def test_uc28_ac5_tra_dung_khong_tinh_sai(client, d1):
    for _ in range(12):
        assert tra(client, "DH-0001", "3456").status_code == 200


# AC6 – không cần đăng nhập; mã viết thường, có khoảng trắng
def test_uc28_ac6_khong_dang_nhap_ma_tu_do(client, d1):
    assert tra(client, "  dh-0001 ", "5666").status_code == 200
