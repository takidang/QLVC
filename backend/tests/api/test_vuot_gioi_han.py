# ruff: noqa: F811  (kb là fixture nhập từ test UC-11, dùng làm tham số)
"""Kiểm thử khám phá 23/11: số hay ngày vượt giới hạn trả 400 có thông báo, không 500 (NFR-USA-02)."""

import pytest

from tests.api.test_uc11_lap_chuyen import kb, lap  # noqa: F401 (kb là fixture)

QUA_BIGINT = 10**19


def ma(r) -> tuple[int, str | None]:
    return r.status_code, r.json().get("ma")


@pytest.mark.parametrize(
    "duong_dan",
    [f"/api/don/{QUA_BIGINT}", f"/api/don?trang={10**18}", f"/api/xe/{QUA_BIGINT}"],
)
def test_so_qua_cot_csdl(client, dang_nhap_voi, duong_dan):
    dang_nhap_voi("DIEU_PHOI")
    assert ma(client.get(duong_dan)) == (400, "VUOT_GIOI_HAN")


def test_tien_qua_cot_csdl(client, dang_nhap_voi, kb):
    dang_nhap_voi("KE_TOAN")
    r = client.put(f"/api/xe/{kb['x1']}/chi-phi-co-dinh/2026-01", json={"so_tien": QUA_BIGINT})
    assert ma(r) == (400, "VUOT_GIOI_HAN")


def test_khoi_hanh_tran_ngay(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    assert ma(lap(client, kb, khoi_hanh_du_kien="9999-12-31T23:30:00+07:00")) == (400, "VUOT_GIOI_HAN")


@pytest.mark.parametrize("thang", ["0000-01", "9999-12", "1999-12"])
def test_thang_ngoai_2000_2099(client, dang_nhap_voi, kb, thang):
    dang_nhap_voi("KE_TOAN")
    for duong_dan in (
        f"/api/bao-cao/hieu-suat-xe?thang={thang}",
        f"/api/bao-cao/lai-lo?tu={thang}&den={thang}",
        f"/api/xe/{kb['x1']}/chi-phi-co-dinh/{thang}",
    ):
        assert ma(client.get(duong_dan)) == (400, "DU_LIEU_KHONG_HOP_LE"), duong_dan
