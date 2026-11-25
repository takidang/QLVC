# ruff: noqa: F811  (kb là fixture nhập từ test UC-17, dùng làm tham số)
"""UC-24 Quyết toán. C01 theo kịch bản nghiep-vu.md mục 11 bước 7: Đ2, Đ4 giao, Đ1 thất bại; dầu 26 lít 520.000,
cầu đường 230.000, bốc xếp 300.000; tạm ứng 1.000.000; lương chốt 600.000; 178 km, xe 15 lít/100 km."""

import json
import time
from datetime import timedelta
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import func, select, update

from app import luu_tru
from app.models import ChiPhi, Chuyen, Ghep, LichSuTrangThai, NhatKyTien, QuyetToan, TamUng, Tep, Xe
from app.thoi_gian import bay_gio
from tests.api.test_uc17_xem_chuyen import kb  # noqa: F401 (kb là fixture)

JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
CONG_TY_TRA = {"xu_ly_chenh_lech": "CONG_TY_DA_TRA", "hinh_thuc": "TIEN_MAT"}


@pytest.fixture
def qt(db, kb, client, dang_nhap_voi, tmp_path, monkeypatch):
    """C01 HOAN_THANH với 3 khoản chờ duyệt (mỗi khoản 1 ảnh); client đăng nhập Kế toán."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    kt = dang_nhap_voi("KE_TOAN")
    c = kb["c01"]
    c.trang_thai, c.km_bat_dau, c.km_ket_thuc = "HOAN_THANH", 1000, 1178
    c.dm_dau_chot, c.dm_cau_duong_chot, c.dm_boc_xep_chot = 550000, 200000, 250000
    db.get(Xe, c.xe_id).dinh_muc_lit_100km = Decimal(15)
    for d, cuoc, kq in ((kb["d1"], 2997000, "THAT_BAI"), (kb["d2"], 1440000, "DA_GIAO"), (kb["d4"], 800000, "DA_GIAO")):
        d.cuoc_tinh = cuoc
        db.execute(update(Ghep).where(Ghep.chuyen_id == c.id, Ghep.don_hang_id == d.id).values(ket_qua=kq))
    db.add(TamUng(chuyen_id=c.id, tai_xe_id=kb["an"].id, so_tien=1000000, hinh_thuc="TIEN_MAT", nguoi_tao=kt.id))
    khoan = {}
    for ten, loai, so, lit, anh in (
        ("dau", "DAU", 520000, Decimal(26), PNG),
        ("cau", "CAU_DUONG", 230000, None, JPG),
        ("boc", "BOC_XEP", 300000, None, JPG),
    ):
        cp = ChiPhi(
            chuyen_id=c.id, loai=loai, so_tien_khai=so, so_lit=lit, ghi_chu=ten, nguoi_tao=kb["an"].nguoi_dung_id
        )
        db.add(cp)
        db.flush()
        tep_ten = luu_tru.luu(anh, ".png" if anh == PNG else ".jpg")
        db.add(Tep(chi_phi_id=cp.id, loai="ANH", duong_dan=tep_ten, kich_thuoc=len(anh)))
        khoan[ten] = cp.id
    db.commit()
    return kb | {"id": c.id, "kt": kt, "k": khoan, "dang_nhap_voi": dang_nhap_voi}


def duyet(client, cp_id, so, ly_do=None, **them):
    return client.post(f"/api/chi-phi/{cp_id}/duyet", json={"so_tien_duyet": so, "ly_do": ly_do, **them})


def tu_choi(client, cp_id, ly_do="Không có hóa đơn"):
    return client.post(f"/api/chi-phi/{cp_id}/tu-choi", json={"ly_do": ly_do})


def duyet_het(client, qt):
    for ten, so in (("dau", 520000), ("cau", 230000), ("boc", 300000)):
        assert duyet(client, qt["k"][ten], so).status_code == 200


def quyet_toan(client, chuyen_id, **body):
    return client.post(f"/api/chuyen/{chuyen_id}/quyet-toan", json=body)


def gio(phut=0) -> str:
    return (bay_gio() + timedelta(minutes=phut)).isoformat()


def ma(r) -> tuple[int, str | None]:
    return r.status_code, r.json().get("ma")


def chi_phi(db, cp_id) -> ChiPhi:
    db.expire_all()
    return db.get(ChiPhi, cp_id)


def nhat_ky(db, bang, ban_ghi_id) -> list[NhatKyTien]:
    db.expire_all()
    return list(
        db.scalars(
            select(NhatKyTien)
            .where(NhatKyTien.bang == bang, NhatKyTien.ban_ghi_id == ban_ghi_id)
            .order_by(NhatKyTien.id)
        )
    )


def trang_thai(db, chuyen_id) -> str:
    db.expire_all()
    return db.get(Chuyen, chuyen_id).trang_thai


def dat_chuyen(db, chuyen_id, tt, **them):
    c = db.get(Chuyen, chuyen_id)
    c.trang_thai = tt
    for k, v in them.items():
        setattr(c, k, v)
    db.commit()


# AC1 – duyệt, điều chỉnh có lý do, biên số duyệt
def test_uc24_ac1_duyet_dung_so_khai(client, db, qt):
    r = duyet(client, qt["k"]["dau"], 520000)
    assert r.status_code == 200, r.text
    assert (r.json()["trang_thai"], r.json()["so_tien_duyet"], len(r.json()["anh"])) == ("DA_DUYET", 520000, 1)
    cp = chi_phi(db, qt["k"]["dau"])
    assert (cp.trang_thai, cp.so_tien_duyet, cp.nguoi_duyet) == ("DA_DUYET", 520000, qt["kt"].id)
    (nk,) = nhat_ky(db, "chi_phi", cp.id)
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.nguoi) == (
        "DUYET",
        "CHO_DUYET 520000",
        "DA_DUYET 520000",
        qt["kt"].id,
    )


def test_uc24_ac1_dieu_chinh_can_ly_do(client, db, qt):
    assert ma(duyet(client, qt["k"]["dau"], 500000)) == (422, "BR-55")
    assert ma(duyet(client, qt["k"]["dau"], 500000, ly_do="   ")) == (400, "DU_LIEU_KHONG_HOP_LE")
    assert chi_phi(db, qt["k"]["dau"]).trang_thai == "CHO_DUYET"
    r = duyet(client, qt["k"]["dau"], 500000, ly_do="Hóa đơn ghi 500.000")
    assert r.status_code == 200 and r.json()["so_tien_duyet"] == 500000
    (nk,) = nhat_ky(db, "chi_phi", qt["k"]["dau"])
    assert (nk.gia_tri_moi, nk.ly_do) == ("DA_DUYET 500000", "Hóa đơn ghi 500.000")


@pytest.mark.parametrize(
    ("so", "kq"),
    [(520000, (200, None)), (520001, (422, "BR-55")), (1, (200, None)), (0, (400, "DU_LIEU_KHONG_HOP_LE"))],
)
def test_uc24_ac1_bien_so_duyet(client, db, qt, so, kq):
    r = duyet(client, qt["k"]["dau"], so, ly_do="Điều chỉnh")
    assert (r.status_code, r.json().get("ma")) == kq
    assert chi_phi(db, qt["k"]["dau"]).trang_thai == ("DA_DUYET" if kq[0] == 200 else "CHO_DUYET")


@pytest.mark.parametrize("body", [{"so_tien_duyet": "520000"}, {"so_tien_duyet": 520000, "trang_thai": "DA_DUYET"}, {}])
def test_uc24_ac1_du_lieu_sai(client, qt, body):
    assert ma(client.post(f"/api/chi-phi/{qt['k']['dau']}/duyet", json=body)) == (400, "DU_LIEU_KHONG_HOP_LE")


# AC2 – từ chối, đổi quyết định
def test_uc24_ac2_tu_choi(client, db, qt):
    assert ma(client.post(f"/api/chi-phi/{qt['k']['boc']}/tu-choi", json={})) == (400, "DU_LIEU_KHONG_HOP_LE")
    r = tu_choi(client, qt["k"]["boc"])
    assert r.status_code == 200 and (r.json()["trang_thai"], r.json()["so_tien_duyet"]) == ("TU_CHOI", None)
    (nk,) = nhat_ky(db, "chi_phi", qt["k"]["boc"])
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.ly_do) == (
        "TU_CHOI",
        "CHO_DUYET 300000",
        "TU_CHOI",
        "Không có hóa đơn",
    )


def test_uc24_ac2_doi_quyet_dinh(client, db, qt):
    k = qt["k"]["cau"]
    assert duyet(client, k, 230000).status_code == 200
    assert ma(duyet(client, k, 230000)) == (400, "KHONG_CO_THAY_DOI")
    assert duyet(client, k, 200000, ly_do="Một vé không hợp lệ").status_code == 200
    assert tu_choi(client, k).status_code == 200
    assert ma(tu_choi(client, k)) == (400, "KHONG_CO_THAY_DOI")
    assert duyet(client, k, 230000).status_code == 200
    assert [(n.hanh_dong, n.gia_tri_cu, n.gia_tri_moi) for n in nhat_ky(db, "chi_phi", k)] == [
        ("DUYET", "CHO_DUYET 230000", "DA_DUYET 230000"),
        ("DUYET", "DA_DUYET 230000", "DA_DUYET 200000"),
        ("TU_CHOI", "DA_DUYET 200000", "TU_CHOI"),
        ("DUYET", "TU_CHOI 230000", "DA_DUYET 230000"),
    ]


# AC3 – trạng thái chuyến khi duyệt
@pytest.mark.parametrize(("tt", "kq"), [("DANG_CHAY", (409, "BR-55")), ("DA_QUYET_TOAN", (409, "BR-29"))])
def test_uc24_ac3_duyet_sai_trang_thai(client, db, qt, tt, kq):
    dat_chuyen(db, qt["id"], tt)
    assert ma(duyet(client, qt["k"]["dau"], 520000)) == kq
    assert ma(tu_choi(client, qt["k"]["dau"])) == kq
    cp = chi_phi(db, qt["k"]["dau"])
    assert (cp.trang_thai, cp.so_tien_duyet) == ("CHO_DUYET", None) and nhat_ky(db, "chi_phi", cp.id) == []


def test_uc24_ac3_khoan_khong_co(client, qt):
    assert ma(duyet(client, 999999, 1)) == (404, "KHONG_TIM_THAY")
    assert ma(tu_choi(client, 999999)) == (404, "KHONG_TIM_THAY")


# AC4 – doanh thu chỉ đơn giao thành công trên chuyến này (TC-BR50-01, 02)
def test_uc24_ac4_doanh_thu_c01(client, qt):
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert j["doanh_thu"] == 2240000
    assert [(d["ma_don"], d["cuoc"]) for d in j["don_giao"]] == [("DH-0002", 1440000), ("DH-0004", 800000)]
    assert [(d["ma_don"], d["cuoc"]) for d in j["don_that_bai"]] == [("DH-0001", 2997000)]


def test_uc24_ac4_don_giao_lai_tinh_cho_chuyen_sau(client, db, qt):
    db.execute(update(Ghep).where(Ghep.chuyen_id == qt["id"], Ghep.don_hang_id == qt["d1"].id).values(hieu_luc=False))
    db.commit()
    c05 = qt["chuyen"](qt["binh"], "HOAN_THANH", 6, 23, qt["d1"], ket_qua="DA_GIAO")
    j = client.get(f"/api/chuyen/{c05.id}/quyet-toan").json()
    assert (j["doanh_thu"], [d["ma_don"] for d in j["don_giao"]]) == (2997000, ["DH-0001"])
    assert client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()["doanh_thu"] == 2240000


# AC5 – lãi (TC-BR51-01, 02); khoản từ chối không tính
def test_uc24_ac5_lai_c01(client, qt):
    duyet_het(client, qt)
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["tong_chi"], j["luong_tai_xe"], j["lai"]) == (1050000, 600000, 590000)


def test_uc24_ac5_tu_choi_khong_tinh(client, qt):
    duyet(client, qt["k"]["dau"], 520000)
    duyet(client, qt["k"]["cau"], 230000)
    tu_choi(client, qt["k"]["boc"])
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["tong_chi"], j["lai"], j["chenh_lech_tam_ung"]) == (750000, 890000, 250000)


def test_uc24_ac5_lai_luong_tay(client, db, qt):
    dat_chuyen(db, qt["id"], "HOAN_THANH", ket_thuc_bat_thuong=True, ly_do_ket_thuc="Hỏng hộp số")
    duyet_het(client, qt)
    r = quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio(), luong_tay=300000, ly_do_luong_tay="Chạy nửa tuyến")
    assert r.status_code == 200, r.text
    assert (r.json()["luong_tai_xe"], r.json()["lai"]) == (300000, 890000)


# AC6 – bảng định mức – thực tế, dầu tham khảo, lý do lệch
def test_uc24_ac6_bang_quyet_toan(client, qt):
    duyet_het(client, qt)
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert [(x["loai"], x["dinh_muc"], x["thuc_te"], x["chenh_lech"]) for x in j["chi_theo_loai"]] == [
        ("DAU", 550000, 520000, -30000),
        ("CAU_DUONG", 200000, 230000, 30000),
        ("BOC_XEP", 250000, 300000, 50000),
        ("PHAT_SINH", 0, 0, 0),
    ]
    assert (j["dinh_muc"], j["tong_chi"], j["tong_chi"] - j["dinh_muc"]) == (1000000, 1050000, 50000)
    assert (j["km"], Decimal(j["dau_tham_khao_lit"]), Decimal(j["dau_thuc_te_lit"])) == (
        178,
        Decimal("26.7"),
        Decimal(26),
    )
    assert (j["tong_tam_ung_hieu_luc"], j["chenh_lech_tam_ung"], j["xu_ly_goi_y"]) == (
        1000000,
        -50000,
        "CONG_TY_DA_TRA",
    )
    assert (j["so_cho_duyet"], j["luong_chot"], j["can_luong_tay"]) == (0, 600000, False)
    # Dự kiến: 2.240.000 + 2.997.000 − 1.000.000 − 600.000; lý do lệch cộng lại đúng bằng lãi − lãi dự kiến
    assert j["lai_du_kien"] == 3637000
    assert sum(x["so_tien"] for x in j["ly_do_lech"]) == j["lai"] - j["lai_du_kien"]
    assert j["ly_do_lech"][0] == {"mo_ta": "Đơn DH-0001 giao thất bại", "so_tien": -2997000}
    assert {"mo_ta": "Bốc xếp vượt định mức", "so_tien": -50000} in j["ly_do_lech"]
    assert {"mo_ta": "Dầu dưới định mức", "so_tien": 30000} in j["ly_do_lech"]


def test_uc24_ac6_cho_duyet_va_thieu_km(client, db, qt):
    dat_chuyen(db, qt["id"], "HOAN_THANH", km_ket_thuc=None)
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["km"], j["dau_tham_khao_lit"], j["so_cho_duyet"], j["tong_chi"]) == (None, None, 3, 0)
    assert [len(k["anh"]) for k in j["khoan"]] == [1, 1, 1]


@pytest.mark.parametrize("tt", ["LAP", "DA_CHOT", "DANG_CHAY", "HUY"])
def test_uc24_ac6_chua_hoan_thanh(client, db, qt, tt):
    dat_chuyen(db, qt["id"], tt)
    assert ma(client.get(f"/api/chuyen/{qt['id']}/quyet-toan")) == (409, "BR-55")


def test_uc24_ac6_khong_co_chuyen(client, qt):
    assert ma(client.get("/api/chuyen/999999/quyet-toan")) == (404, "KHONG_TIM_THAY")


# AC7 – quyết toán C01 (TC-BR55-01)
def test_uc24_ac7_quyet_toan_c01(client, db, qt):
    duyet_het(client, qt)
    luc = gio(-60)
    r = quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=luc)
    assert r.status_code == 200, r.text
    assert r.json() == {
        "chuyen_id": qt["id"],
        "doanh_thu": 2240000,
        "tong_chi": 1050000,
        "luong_tai_xe": 600000,
        "lai": 590000,
        "tong_tam_ung_hieu_luc": 1000000,
        "chenh_lech_tam_ung": -50000,
        "xu_ly_chenh_lech": "CONG_TY_DA_TRA",
    }
    assert trang_thai(db, qt["id"]) == "DA_QUYET_TOAN"
    q = db.scalar(select(QuyetToan).where(QuyetToan.chuyen_id == qt["id"]))
    assert (q.lai, q.chenh_lech_tam_ung, q.hinh_thuc, q.ke_toan_id, q.ly_do_luong_tay) == (
        590000,
        -50000,
        "TIEN_MAT",
        qt["kt"].id,
        None,
    )
    ls = db.scalar(select(LichSuTrangThai).where(LichSuTrangThai.sang == "DA_QUYET_TOAN"))
    assert (ls.doi_tuong_id, ls.tu, ls.nguoi) == (qt["id"], "HOAN_THANH", qt["kt"].id)
    (nk,) = nhat_ky(db, "quyet_toan", q.id)
    assert nk.hanh_dong == "QUYET_TOAN" and json.loads(nk.gia_tri_moi)["lai"] == 590000
    # Sau khi khóa, bảng trả số đã lưu kèm cách xử lý
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["trang_thai"], j["lai"], j["xu_ly_chenh_lech"], j["hinh_thuc"]) == (
        "DA_QUYET_TOAN",
        590000,
        "CONG_TY_DA_TRA",
        "TIEN_MAT",
    )


# AC8 – còn chờ duyệt, sai trạng thái (TC-BR55-02, 05)
def test_uc24_ac8_con_cho_duyet(client, db, qt):
    duyet(client, qt["k"]["dau"], 520000)
    duyet(client, qt["k"]["cau"], 230000)
    r = quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())
    assert ma(r) == (409, "BR-55") and r.json()["chi_tiet"][0]["chi_phi_ids"] == [qt["k"]["boc"]]
    assert trang_thai(db, qt["id"]) == "HOAN_THANH"
    assert db.scalar(select(func.count()).select_from(QuyetToan)) == 0


@pytest.mark.parametrize(
    ("tt", "kq"), [("DANG_CHAY", (409, "BR-55")), ("DA_CHOT", (409, "BR-55")), ("DA_QUYET_TOAN", (409, "BR-29"))]
)
def test_uc24_ac8_sai_trang_thai(client, db, qt, tt, kq):
    duyet_het(client, qt)
    dat_chuyen(db, qt["id"], tt)
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())) == kq
    assert trang_thai(db, qt["id"]) == tt


def test_uc24_ac8_khong_co_chuyen(client, qt):
    assert ma(quyet_toan(client, 999999, **CONG_TY_TRA, luc_xu_ly=gio())) == (404, "KHONG_TIM_THAY")


# AC9 – cách xử lý chênh lệch (TC-BR55-03, 04)
@pytest.mark.parametrize(
    "body",
    [
        {},  # thiếu cách xử lý (TC-BR55-03)
        {"xu_ly_chenh_lech": "TAI_XE_DA_NOP", "hinh_thuc": "TIEN_MAT"},  # sai dấu (TC-BR55-04)
        {"xu_ly_chenh_lech": "KHONG_CHENH"},
        {"xu_ly_chenh_lech": "CONG_TY_DA_TRA"},  # thiếu hình thức, giờ
        {"xu_ly_chenh_lech": "CONG_TY_DA_TRA", "hinh_thuc": "TIEN_MAT"},  # thiếu giờ
        {"xu_ly_chenh_lech": "CONG_TY_DA_TRA", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": "tuong_lai"},
    ],
)
def test_uc24_ac9_xu_ly_sai(client, db, qt, body):
    duyet_het(client, qt)
    if body.get("luc_xu_ly") == "tuong_lai":
        body["luc_xu_ly"] = gio(10)
    elif "hinh_thuc" in body and "TAI_XE" in body["xu_ly_chenh_lech"]:
        body["luc_xu_ly"] = gio()
    assert ma(quyet_toan(client, qt["id"], **body)) == (422, "BR-55")
    assert trang_thai(db, qt["id"]) == "HOAN_THANH"


@pytest.mark.parametrize("body", [{"luc_xu_ly": "2026-11-10T09:00:00"}, {"hinh_thuc": "THE"}, {"lai": 1}])
def test_uc24_ac9_du_lieu_sai(client, qt, body):
    duyet_het(client, qt)
    r = quyet_toan(client, qt["id"], **{**CONG_TY_TRA, "luc_xu_ly": gio(), **body})
    assert ma(r) == (400, "DU_LIEU_KHONG_HOP_LE")


def test_uc24_ac9_duong_tai_xe_nop(client, db, qt):
    duyet(client, qt["k"]["dau"], 400000, ly_do="Hóa đơn 400.000")
    duyet(client, qt["k"]["cau"], 230000)
    tu_choi(client, qt["k"]["boc"])  # chi 630.000, tạm ứng 1.000.000 → tài xế nộp lại 370.000
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())) == (422, "BR-55")
    r = quyet_toan(client, qt["id"], xu_ly_chenh_lech="TAI_XE_DA_NOP", hinh_thuc="CHUYEN_KHOAN", luc_xu_ly=gio(4))
    assert r.status_code == 200 and r.json()["chenh_lech_tam_ung"] == 370000


def test_uc24_ac9_chenh_bang_0(client, db, qt):
    # Biên: tạm ứng = chi đã duyệt → chỉ nhận KHONG_CHENH, hình thức và giờ bỏ qua
    duyet(client, qt["k"]["dau"], 470000, ly_do="Hóa đơn 470.000")
    duyet(client, qt["k"]["cau"], 230000)
    duyet(client, qt["k"]["boc"], 300000)
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())) == (422, "BR-55")
    r = quyet_toan(client, qt["id"], xu_ly_chenh_lech="KHONG_CHENH", hinh_thuc="TIEN_MAT", luc_xu_ly=gio())
    assert r.status_code == 200 and r.json()["chenh_lech_tam_ung"] == 0
    q = db.scalar(select(QuyetToan))
    assert (q.xu_ly_chenh_lech, q.hinh_thuc, q.luc_xu_ly) == ("KHONG_CHENH", None, None)


# AC10 – lương tay khi kết thúc do sự cố (BR-68)
@pytest.mark.parametrize(
    "them",
    [{}, {"luong_tay": 300000}, {"ly_do_luong_tay": "Chạy nửa tuyến"}, {"luong_tay": 300000, "ly_do_luong_tay": ""}],
)
def test_uc24_ac10_thieu_luong_tay(client, db, qt, them):
    dat_chuyen(db, qt["id"], "HOAN_THANH", ket_thuc_bat_thuong=True)
    duyet_het(client, qt)
    code = (400, "DU_LIEU_KHONG_HOP_LE") if them.get("ly_do_luong_tay") == "" else (422, "BR-68")
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio(), **them)) == code
    assert trang_thai(db, qt["id"]) == "HOAN_THANH"


def test_uc24_ac10_luong_tay_0(client, db, qt):
    dat_chuyen(db, qt["id"], "HOAN_THANH", ket_thuc_bat_thuong=True)
    assert client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()["can_luong_tay"] is True
    duyet_het(client, qt)
    r = quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio(), luong_tay=0, ly_do_luong_tay="Hỏng ngay đầu")
    assert r.status_code == 200 and (r.json()["luong_tai_xe"], r.json()["lai"]) == (0, 1190000)
    q = db.scalar(select(QuyetToan))
    assert (q.luong_tai_xe, q.ly_do_luong_tay) == (0, "Hỏng ngay đầu")
    (nk,) = nhat_ky(db, "chuyen", qt["id"])
    assert (nk.hanh_dong, nk.gia_tri_cu, nk.gia_tri_moi, nk.ly_do) == ("LUONG_TAY", "600000", "0", "Hỏng ngay đầu")
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["luong_tai_xe"], j["ly_do_luong_tay"]) == (0, "Hỏng ngay đầu")


def test_uc24_ac10_chuyen_binh_thuong_bo_qua_luong_tay(client, db, qt):
    duyet_het(client, qt)
    r = quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio(), luong_tay=1, ly_do_luong_tay="x")
    assert r.status_code == 200 and r.json()["luong_tai_xe"] == 600000
    assert nhat_ky(db, "chuyen", qt["id"]) == []


# AC11 – sau quyết toán mọi lượt ghi tiền 409 BR-29
def test_uc24_ac11_khoa_sau_quyet_toan(client, db, qt, dang_nhap_voi):
    duyet_het(client, qt)
    assert quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio()).status_code == 200
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())) == (409, "BR-29")
    assert db.scalar(select(func.count()).select_from(QuyetToan)) == 1
    assert ma(duyet(client, qt["k"]["dau"], 500000, ly_do="x")) == (409, "BR-29")
    assert ma(tu_choi(client, qt["k"]["dau"])) == (409, "BR-29")
    tu_id = db.scalar(select(TamUng.id))
    assert ma(client.post(f"/api/chuyen/{qt['id']}/tam-ung", json={"so_tien": 1, "hinh_thuc": "TIEN_MAT"}))[0] == 409
    assert ma(client.patch(f"/api/tam-ung/{tu_id}", json={"so_tien": 900000, "ly_do": "x"})) == (409, "BR-29")
    assert ma(client.post(f"/api/tam-ung/{tu_id}/thu-hoi", json={})) == (409, "BR-29")
    # Tài xế An
    assert client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "an", "mat_khau": "matkhau123"}).status_code == 200
    r = client.post(
        f"/api/toi/chuyen/{qt['id']}/chi-phi",
        data={"loai": "PHAT_SINH", "so_tien": "1000", "ghi_chu": "x"},
        files=[("anh", ("a.jpg", JPG, "image/jpeg"))],
    )
    assert ma(r) == (409, "BR-29")
    assert ma(client.delete(f"/api/toi/chi-phi/{qt['k']['dau']}")) == (409, "BR-29")
    assert chi_phi(db, qt["k"]["dau"]).so_tien_duyet == 520000


# AC12 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "TAI_XE", "QUAN_LY"])
def test_uc24_ac12_ghi_bi_cam(client, db, qt, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert ma(duyet(client, qt["k"]["dau"], 520000)) == (403, "KHONG_DU_QUYEN")
    assert ma(tu_choi(client, qt["k"]["dau"])) == (403, "KHONG_DU_QUYEN")
    assert ma(quyet_toan(client, qt["id"], **CONG_TY_TRA, luc_xu_ly=gio())) == (403, "KHONG_DU_QUYEN")
    xem = client.get(f"/api/chuyen/{qt['id']}/quyet-toan")
    assert xem.status_code == (200 if vai_tro == "QUAN_LY" else 403)
    assert chi_phi(db, qt["k"]["dau"]).trang_thai == "CHO_DUYET" and trang_thai(db, qt["id"]) == "HOAN_THANH"


def test_uc24_ac12_chua_dang_nhap(client, qt):
    client.cookies.clear()
    assert duyet(client, qt["k"]["dau"], 520000).status_code == 401
    assert client.get(f"/api/chuyen/{qt['id']}/quyet-toan").status_code == 401
    assert quyet_toan(client, qt["id"]).status_code == 401


# AC13 – ảnh chứng từ qua link có hạn (NFR-SEC-04)
def _tep(db, cp_id) -> int:
    return db.scalar(select(Tep.id).where(Tep.chi_phi_id == cp_id))


@pytest.mark.parametrize("vai_tro", ["KE_TOAN", "QUAN_LY"])
def test_uc24_ac13_xem_anh(client, db, qt, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    r = client.get(f"/api/tep/{_tep(db, qt['k']['dau'])}/link")
    assert r.status_code == 200
    client.cookies.clear()  # link tự mang quyền, không cần cookie
    a = client.get(r.json()["url"])
    assert a.status_code == 200 and a.content == PNG
    assert (a.headers["content-type"], a.headers["x-content-type-options"]) == ("image/png", "nosniff")


@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "TAI_XE"])
def test_uc24_ac13_vai_tro_khac(client, db, qt, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert ma(client.get(f"/api/tep/{_tep(db, qt['k']['dau'])}/link")) == (403, "KHONG_DU_QUYEN")


def test_uc24_ac13_link_het_han_sai_chu_ky(client, db, qt, monkeypatch):
    tep_id = _tep(db, qt["k"]["dau"])
    url = client.get(f"/api/tep/{tep_id}/link").json()["url"]
    q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    assert ma(client.get(f"/api/tep/{tep_id}/anh", params={**q, "ky": "0" * 64})) == (403, "KHONG_DU_QUYEN")
    assert ma(client.get(f"/api/tep/{tep_id}/anh", params={**q, "het": int(q["het"]) + 60})) == (403, "KHONG_DU_QUYEN")
    assert ma(client.get(f"/api/tep/{tep_id}/anh", params={**q, "ky": "ạ"})) == (403, "KHONG_DU_QUYEN")
    tep_khac = _tep(db, qt["k"]["cau"])  # chữ ký của tệp này không mở được tệp khác
    assert ma(client.get(f"/api/tep/{tep_khac}/anh", params=q)) == (403, "KHONG_DU_QUYEN")
    that = time.time
    monkeypatch.setattr(time, "time", lambda: that() + 301)
    assert ma(client.get(url)) == (403, "KHONG_DU_QUYEN")


def test_uc24_ac13_tep_khong_co_hoac_khong_phai_chi_phi(client, db, qt):
    assert ma(client.get("/api/tep/999999/link")) == (404, "KHONG_TIM_THAY")
    t = Tep(chuyen_id=qt["id"], loai="ANH_KM_BAT_DAU", duong_dan="x.jpg", kich_thuoc=1)
    db.add(t)
    db.commit()
    assert ma(client.get(f"/api/tep/{t.id}/link")) == (403, "KHONG_DU_QUYEN")


def test_uc24_ac9_tam_ung_da_thu_hoi_khong_tinh(client, db, qt):
    db.add(
        TamUng(
            chuyen_id=qt["id"],
            tai_xe_id=qt["an"].id,
            so_tien=500000,
            hinh_thuc="TIEN_MAT",
            trang_thai="DA_THU_HOI",
            nguoi_tao=qt["kt"].id,
        )
    )
    db.commit()
    duyet_het(client, qt)
    j = client.get(f"/api/chuyen/{qt['id']}/quyet-toan").json()
    assert (j["tong_tam_ung_hieu_luc"], j["chenh_lech_tam_ung"]) == (1000000, -50000)


# Kiểm thử khám phá 23/11: tài xế xóa khoản trong lúc Kế toán đang đợi khóa để duyệt → 404, không 500
def test_uc24_duyet_khoan_vua_bi_xoa(client, db, qt):
    import threading

    from fastapi.testclient import TestClient
    from sqlalchemy import delete
    from sqlalchemy.orm import Session

    from app.db import get_engine
    from app.main import app

    cp = qt["k"]["cau"]
    s = Session(get_engine())
    s.get(Chuyen, qt["id"], with_for_update=True)  # như lần xóa của tài xế đang giữ dòng chuyến
    ket_qua: list = []

    def gui():
        with TestClient(app, base_url="https://testserver") as c:
            assert (
                c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "ke_toan", "mat_khau": "matkhau123"}).status_code
                == 200
            )
            ket_qua.append(duyet(c, cp, 230000))

    try:
        t = threading.Thread(target=gui)
        t.start()
        t.join(1.5)
        assert t.is_alive()
        s.execute(delete(Tep).where(Tep.chi_phi_id == cp))
        s.execute(delete(ChiPhi).where(ChiPhi.id == cp))
        s.commit()
    finally:
        s.close()
    t.join()
    assert ma(ket_qua[0]) == (404, "KHONG_TIM_THAY")
