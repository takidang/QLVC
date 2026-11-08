# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import threading
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Chuyen, DonHang, LichSuTrangThai, NhatKyTien
from app.modules.don import sua_huy
from tests.api.test_uc13_ghep_don import ghep, kb, luc, so_ghep, trang_thai  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import chot, chuyen, lap_c01, sua


def sua_don(client, don_id, **gt):
    return client.patch(f"/api/don/{don_id}", json=gt)


def huy(client, don_id, ly_do="khách hủy", **them):
    return client.post(f"/api/don/{don_id}/huy", json={"ly_do": ly_do, **them} if ly_do is not None else {})


def don(db, don_id) -> DonHang:
    db.expire_all()
    return db.get(DonHang, don_id)


def nhat_ky_tien(db, don_id) -> list[tuple]:
    return db.execute(
        select(NhatKyTien.hanh_dong, NhatKyTien.gia_tri_cu, NhatKyTien.gia_tri_moi, NhatKyTien.nguoi).where(
            NhatKyTien.bang == "don_hang", NhatKyTien.ban_ghi_id == don_id
        )
    ).all()


def ma_vi_pham(r) -> set[tuple[int | None, str]]:
    return {(v["don_id"], v["ma"]) for v in r.json()["chi_tiet"]}


# AC1 – cước tính lại từ bản sao giá trên đơn, ghi nhật ký tiền
def test_uc10_ac1_sua_kg_tinh_lai_cuoc_tu_ban_sao(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    # Kịch bản không có bảng giá nào: nếu code đọc bảng giá hiện tại thay vì bản sao 1.000 trên đơn thì lỗi (TC-BR33-01)
    r = sua_don(client, kb["d4"], kg="900")
    assert r.status_code == 200, r.text
    assert (r.json()["cuoc_tinh"], Decimal(r.json()["kl_tinh_cuoc"])) == (900000, Decimal(900))
    assert nhat_ky_tien(db, kb["d4"]) == [("SUA", "800000", "900000", dp.id)]


# AC2 – KL quy đổi; sửa không đổi cước thì không ghi nhật ký tiền
def test_uc10_ac2_m3_quy_doi_va_khong_doi_cuoc(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    assert sua_don(client, kb["d4"], sdt_nhan="0912345678").json()["cuoc_tinh"] == 800000
    assert nhat_ky_tien(db, kb["d4"]) == []
    r = sua_don(client, kb["d4"], m3="3")  # 3 × 333 = 999 kg > 800 kg thực
    assert r.json()["cuoc_tinh"] == 999000
    assert len(nhat_ky_tien(db, kb["d4"])) == 1


# AC3 – BR-31 khi sửa
@pytest.mark.parametrize("gt", [{"kg": "0"}, {"m3": "0"}, {"so_kien": 0}])
def test_uc10_ac3_so_luong_khong_hop_le(client, dang_nhap_voi, db, kb, gt):
    dang_nhap_voi("DIEU_PHOI")
    assert sua_don(client, kb["d4"], **gt).status_code == 400
    assert don(db, kb["d4"]).kg == 800


def test_uc10_ac3_khung_lay_va_han_giao(client, dang_nhap_voi, db, kb, monkeypatch):
    dang_nhap_voi("DIEU_PHOI")
    monkeypatch.setattr(sua_huy, "bay_gio", lambda: luc(5))
    r = sua_don(client, kb["d4"], lay_tu=luc(9).isoformat(), lay_den=luc(6, 30).isoformat())
    assert (r.status_code, r.json()["ma"]) == (422, "BR-31")
    assert (sua_don(client, kb["d4"], han_giao=luc(5).isoformat()).json()["ma"]) == "BR-31"  # = lúc sửa
    assert sua_don(client, kb["d4"], han_giao=luc(5, 1).isoformat()).status_code == 200  # sau 1 phút: biên
    assert sua_don(client, 999999, kg="1").status_code == 404


def test_uc10_ac3_han_giao_khong_doi_thi_khong_bat_sau_luc_sua(client, dang_nhap_voi, db, kb, monkeypatch):
    dang_nhap_voi("DIEU_PHOI")
    monkeypatch.setattr(sua_huy, "bay_gio", lambda: luc(19))  # đã qua hạn giao 18:00 của Đ4
    assert sua_don(client, kb["d4"], sdt_nhan="0912345678").status_code == 200


# AC4 – đơn đang ghép: kiểm lại cả chuyến (BR-67)
def test_uc10_ac4_han_giao_don_dang_ghep(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    lap_c01(client, kb, "d1", "d2", "d4")  # ETA giao Đ2 11:50
    r = sua_don(client, kb["d2"], han_giao=luc(11, 49).isoformat())
    assert (r.status_code, r.json()["ma"]) == (422, "VI_PHAM_SUA")
    assert (kb["d2"], "BR-06") in ma_vi_pham(r)
    assert don(db, kb["d2"]).han_giao == luc(12)
    assert sua_don(client, kb["d2"], han_giao=luc(11, 50).isoformat()).status_code == 200  # biên


def test_uc10_ac4_tai_trong_don_dang_ghep(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    lap_c01(client, kb, "d1", "d2", "d4")  # 1.800 + 1.200 + 800 = 3.800 / 5.000 kg
    r = sua_don(client, kb["d1"], kg="3001")
    assert (r.status_code, r.json()["ma"]) == (422, "VI_PHAM_SUA")
    assert "BR-01" in {m for _, m in ma_vi_pham(r)}
    assert don(db, kb["d1"]).cuoc_tinh == 2997000
    assert sua_don(client, kb["d1"], kg="3000").status_code == 200  # tổng đúng 5.000: biên


# AC5 – trạng thái sai
def test_uc10_ac5_trang_thai_khong_sua_duoc(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    sua(db, DonHang, kb["d8"], trang_thai="DA_LAY")
    r = sua_don(client, kb["d8"], kg="400")  # TC-BR33-02
    assert (r.status_code, r.json()["ma"]) == (409, "BR-33")
    assert don(db, kb["d8"]).kg == 300

    c01 = lap_c01(client, kb, "d1", "d4")
    assert chot(client, c01).status_code == 200
    r = sua_don(client, kb["d4"], kg="900")
    assert (r.status_code, r.json()["ma"]) == (409, "BR-33")


# AC6 – trường không cho sửa, trường lạ, body rỗng, null ở cột bắt buộc
@pytest.mark.parametrize("gt", [{"nut_giao_id": 1}, {"khach_hang_id": 1}, {"xoa_luon": True}, {}, {"kg": None}])
def test_uc10_ac6_truong_khong_hop_le(client, dang_nhap_voi, db, kb, gt):
    dang_nhap_voi("DIEU_PHOI")
    assert client.patch(f"/api/don/{kb['d4']}", json=gt).status_code == 400


def test_uc10_ac6_xoa_khung_lay_bang_null(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    r = sua_don(client, kb["d2"], lay_tu=None, lay_den=None)
    assert r.status_code == 200, r.text
    assert (r.json()["lay_tu"], r.json()["lay_den"]) == (None, None)


# AC7 – hủy đơn chờ ghép, lý do
def test_uc10_ac7_huy_don_cho_ghep(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    r = huy(client, kb["d8"], "  khách hủy  ")
    assert (r.status_code, r.json()["trang_thai"]) == (200, "HUY")
    ls = db.execute(
        select(LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.ly_do, LichSuTrangThai.nguoi).where(
            LichSuTrangThai.doi_tuong == "DON", LichSuTrangThai.doi_tuong_id == kb["d8"]
        )
    ).all()
    assert ls == [("CHO_GHEP", "HUY", "khách hủy", dp.id)]  # TC-BR34-01


@pytest.mark.parametrize(("ly_do", "ma"), [(None, 400), ("", 400), ("   ", 400), ("x" * 301, 400), ("x" * 300, 200)])
def test_uc10_ac7_ly_do(client, dang_nhap_voi, db, kb, ly_do, ma):
    dang_nhap_voi("DIEU_PHOI")
    assert huy(client, kb["d8"], ly_do).status_code == ma
    assert trang_thai(db, kb["d8"]) == ("HUY" if ma == 200 else "CHO_GHEP")


# AC8 – hủy đơn đang ghép: tự gỡ khỏi chuyến
def test_uc10_ac8_huy_don_dang_ghep(client, dang_nhap_voi, db, kb):
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d2", "d4")
    assert huy(client, kb["d4"]).status_code == 200
    assert trang_thai(db, kb["d4"]) == "HUY"
    assert so_ghep(db, don_hang_id=kb["d4"], hieu_luc=True) == 0
    lich = client.get(f"/api/chuyen/{c01}").json()["lich_trinh"]
    assert kb["d4"] not in {p["don_id"] for p in lich} and len(lich) == 4
    ls = db.execute(
        select(LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.ly_do)
        .where(
            LichSuTrangThai.doi_tuong == "DON",
            LichSuTrangThai.doi_tuong_id == kb["d4"],
            LichSuTrangThai.nguoi == dp.id,
            LichSuTrangThai.sang.in_(("CHO_GHEP", "HUY")),
        )
        .order_by(LichSuTrangThai.id)
    ).all()
    assert ls == [("DA_GHEP", "CHO_GHEP", "khách hủy"), ("CHO_GHEP", "HUY", "khách hủy")]


def test_uc10_ac8_chuyen_da_chot(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1", "d4")
    chot(client, c01)
    r = huy(client, kb["d4"])
    assert (r.status_code, r.json()["ma"]) == (409, "BR-34")
    assert trang_thai(db, kb["d4"]) == "DA_GHEP"
    assert chuyen(db, c01).trang_thai == "DA_CHOT"


# AC9 – hủy sai trạng thái
@pytest.mark.parametrize("tt", ["DA_LAY", "DA_GIAO", "THAT_BAI", "TRA_HANG"])
def test_uc10_ac9_trang_thai_khong_huy_duoc(client, dang_nhap_voi, db, kb, tt):
    dang_nhap_voi("DIEU_PHOI")
    sua(db, DonHang, kb["d8"], trang_thai=tt)
    r = huy(client, kb["d8"])  # TC-BR34-03 (DA_LAY); THAT_BAI để UC-22
    assert (r.status_code, r.json()["ma"]) == (409, "BR-34")
    assert trang_thai(db, kb["d8"]) == tt


def test_uc10_ac9_huy_lan_hai(client, dang_nhap_voi, kb):
    dang_nhap_voi("DIEU_PHOI")
    assert huy(client, kb["d8"]).status_code == 200
    assert huy(client, kb["d8"]).status_code == 409
    assert huy(client, 999999).status_code == 404


# AC10 – hủy và ghép cùng một đơn cùng lúc
def test_uc10_ac10_huy_va_ghep_dong_thoi(client, dang_nhap_voi, db, kb):
    dang_nhap_voi("DIEU_PHOI")
    c01 = lap_c01(client, kb, "d1")
    ket_qua: dict = {}
    cho = threading.Barrier(2)

    def gui(viec):
        with TestClient(app, base_url="https://testserver") as c:
            c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieu_phoi", "mat_khau": "matkhau123"})
            cho.wait()
            ket_qua[viec] = huy(c, kb["d4"]) if viec == "huy" else ghep(c, c01, kb["d4"])

    luong = [threading.Thread(target=gui, args=(v,)) for v in ("huy", "ghep")]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert ket_qua["huy"].status_code == 200, ket_qua["huy"].text
    assert ket_qua["ghep"].status_code in (200, 409)
    # Dù ai chạy trước: đơn đã hủy không còn ghép hiệu lực nào
    assert trang_thai(db, kb["d4"]) == "HUY"
    assert so_ghep(db, don_hang_id=kb["d4"], hieu_luc=True) == 0
    db.expire_all()
    assert db.get(Chuyen, c01).trang_thai == "LAP"


# AC11 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc10_ac11_phan_quyen(client, dang_nhap_voi, db, kb, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert sua_don(client, kb["d4"], kg="900").status_code == ma
    assert huy(client, kb["d8"]).status_code == ma
    assert (don(db, kb["d4"]).kg, trang_thai(db, kb["d8"])) == (
        (Decimal(900), "HUY") if ma == 200 else (Decimal(800), "CHO_GHEP")
    )


def test_uc10_ac11_chua_dang_nhap(client, kb):
    assert sua_don(client, kb["d4"], kg="900").status_code == 401
    assert huy(client, kb["d8"]).status_code == 401
