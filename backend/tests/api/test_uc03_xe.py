from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import NhatKyTien, Xe

X1 = {  # xe X1 trong kịch bản nghiep-vu.md mục 11
    "bien_so": "51C-111.11",
    "tai_trong_kg": 5000,
    "the_tich_m3": "20",
    "ktt_toan_bo_kg": 9500,
    "han_dang_kiem": "2026-11-30",
    "han_bao_hiem": "2027-06-30",
    "dinh_muc_lit_100km": "15",
    "km_dong_ho": 120000,
}


def xe_mau(**doi) -> Xe:
    """Xe X1 dựng thẳng trong CSDL (bỏ qua API) để chuẩn bị dữ liệu."""
    gia_tri = {**X1, "the_tich_m3": Decimal("20"), "dinh_muc_lit_100km": Decimal("15")}
    gia_tri |= {"han_dang_kiem": date(2026, 11, 30), "han_bao_hiem": date(2027, 6, 30)}
    return Xe(**(gia_tri | doi))


def them(client, **doi):
    return client.post("/api/xe", json={**X1, **doi})


# AC1 – thêm xe, chuẩn hóa biển số
def test_uc03_ac1_them_xe_hop_le(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    r = them(client, bien_so=" 51c-111.11 ")
    assert r.status_code == 201
    xe = r.json()
    assert xe["bien_so"] == "51C-111.11"
    assert xe["trang_thai"] == "HOAT_DONG"
    assert xe["km_dong_ho"] == 120000


# AC2 – dữ liệu sai bị chặn 400, kèm ca biên
@pytest.mark.parametrize(
    ("doi", "mong_doi"),
    [
        ({"tai_trong_kg": 0}, 400),
        ({"tai_trong_kg": 1, "ktt_toan_bo_kg": 1}, 201),  # biên được
        ({"ktt_toan_bo_kg": 0}, 400),
        ({"the_tich_m3": "0"}, 400),
        ({"the_tich_m3": "0.01"}, 201),  # biên được
        ({"km_dong_ho": -1}, 400),
        ({"km_dong_ho": 0}, 201),  # biên được
        ({"dinh_muc_lit_100km": "-1"}, 400),
        ({"bien_so": "   "}, 400),
        ({"han_dang_kiem": None}, 400),
        ({"han_bao_hiem": "khong-phai-ngay"}, 400),
    ],
)
def test_uc03_ac2_du_lieu_sai_bi_chan(client, dang_nhap_voi, db, doi, mong_doi):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client, **doi).status_code == mong_doi
    da_luu = db.scalar(select(Xe.id)) is not None
    assert da_luu == (mong_doi == 201)


def test_uc03_ac2_thieu_bien_so_bi_chan(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    vao = {k: v for k, v in X1.items() if k != "bien_so"}
    assert client.post("/api/xe", json=vao).status_code == 400


# AC3 – khối lượng toàn bộ ≥ tải trọng, kiểm cả khi sửa
def test_uc03_ac3_khoi_luong_toan_bo_khi_them_va_sua(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    r = them(client, tai_trong_kg=5000, ktt_toan_bo_kg=4999)
    assert r.status_code == 422
    assert r.json()["ma"] == "BR-14"
    xe_id = them(client).json()["id"]
    assert client.patch(f"/api/xe/{xe_id}", json={"ktt_toan_bo_kg": 4999}).status_code == 422
    assert client.patch(f"/api/xe/{xe_id}", json={"tai_trong_kg": 9501}).status_code == 422
    assert client.patch(f"/api/xe/{xe_id}", json={"tai_trong_kg": 9500}).status_code == 200  # biên


# AC4 – biển số trùng, kể cả khi lọt qua kiểm tra (hai người thêm cùng lúc)
def test_uc03_ac4_bien_so_trung(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert them(client).status_code == 201
    r = them(client, bien_so=" 51c-111.11", tai_trong_kg=1000, ktt_toan_bo_kg=2000)
    assert r.status_code == 409
    assert r.json()["ma"] == "BIEN_SO_TRUNG"
    assert client.get("/api/xe").json()["du_lieu"][0]["tai_trong_kg"] == 5000  # xe cũ không đổi


def test_uc03_ac4_rang_buoc_unique_o_csdl(client, dang_nhap_voi, db):
    # Giả lập người kia vừa lưu xong: bản ghi đã có trong CSDL, yêu cầu này phải nhận 409 chứ không 500
    db.add(xe_mau())
    db.commit()
    dang_nhap_voi("DIEU_PHOI")
    assert them(client).status_code == 409


# AC5 – danh sách: lọc, tìm, phân trang
def test_uc03_ac5_danh_sach_loc_tim_phan_trang(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    for bs in ("51C-111.11", "51C-222.22", "60C-333.33"):
        them(client, bien_so=bs)
    id_ngung = them(client, bien_so="51D-444.44").json()["id"]
    client.patch(f"/api/xe/{id_ngung}", json={"trang_thai": "NGUNG"})

    r = client.get("/api/xe", params={"tim": "51c", "trang_thai": "HOAT_DONG"}).json()
    assert r["tong"] == 2
    assert [x["bien_so"] for x in r["du_lieu"]] == ["51C-111.11", "51C-222.22"]

    trang2 = client.get("/api/xe", params={"trang": 2, "so_dong": 3}).json()
    assert trang2["tong"] == 4
    assert len(trang2["du_lieu"]) == 1
    ngoai = client.get("/api/xe", params={"trang": 9, "so_dong": 3}).json()
    assert ngoai == {"du_lieu": [], "tong": 4}
    assert client.get("/api/xe", params={"so_dong": 101}).status_code == 400


def test_uc03_ac5_tim_khong_hieu_ky_tu_dac_biet(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    them(client)
    assert client.get("/api/xe", params={"tim": "%"}).json()["tong"] == 0


# AC6 – sửa xe; km đồng hồ không sửa được
def test_uc03_ac6_sua_xe(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    xe_id = them(client).json()["id"]
    them(client, bien_so="51C-222.22")
    r = client.patch(f"/api/xe/{xe_id}", json={"han_dang_kiem": "2027-11-30", "bien_so": "51c-999.99"})
    assert r.status_code == 200
    assert r.json()["han_dang_kiem"] == "2027-11-30"
    assert r.json()["bien_so"] == "51C-999.99"

    assert client.patch(f"/api/xe/{xe_id}", json={"km_dong_ho": 1}).status_code == 400
    assert client.patch(f"/api/xe/{xe_id}", json={"tai_trong_kg": None}).status_code == 400
    assert client.patch(f"/api/xe/{xe_id}", json={"bien_so": "51C-222.22"}).status_code == 409
    xe = client.get(f"/api/xe/{xe_id}").json()
    assert xe["km_dong_ho"] == 120000
    assert xe["bien_so"] == "51C-999.99"


# AC7 – trạng thái, không có xóa
def test_uc03_ac7_doi_trang_thai_va_khong_xoa(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    xe_id = them(client).json()["id"]
    assert client.patch(f"/api/xe/{xe_id}", json={"trang_thai": "NGUNG"}).json()["trang_thai"] == "NGUNG"
    assert client.patch(f"/api/xe/{xe_id}", json={"trang_thai": "HOAT_DONG"}).json()["trang_thai"] == "HOAT_DONG"
    assert client.patch(f"/api/xe/{xe_id}", json={"trang_thai": "BAO_DUONG"}).status_code == 400
    assert client.delete(f"/api/xe/{xe_id}").status_code == 405


# AC8 – phân quyền
@pytest.mark.parametrize(
    ("vai_tro", "xem", "sua"),
    [("DIEU_PHOI", 200, 201), ("QUAN_LY", 200, 201), ("KE_TOAN", 200, 403), ("TAI_XE", 403, 403)],
)
def test_uc03_ac8_phan_quyen(client, dang_nhap_voi, db, vai_tro, xem, sua):
    db.add(xe_mau(bien_so="CO-SAN"))
    db.commit()
    xe_id = db.scalar(select(Xe.id))
    dang_nhap_voi(vai_tro)
    assert client.get("/api/xe").status_code == xem
    assert client.get(f"/api/xe/{xe_id}").status_code == xem
    assert them(client).status_code == sua
    assert client.patch(f"/api/xe/{xe_id}", json={"trang_thai": "NGUNG"}).status_code == (200 if sua == 201 else 403)


def test_uc03_ac8_chua_dang_nhap_va_khong_ton_tai(client, dang_nhap_voi):
    assert client.get("/api/xe").status_code == 401
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/xe/999").status_code == 404
    assert client.patch("/api/xe/999", json={"trang_thai": "NGUNG"}).status_code == 404


# AC9, AC10 – chi phí cố định tháng, nhật ký tiền
@pytest.fixture
def xe_id(db):
    xe = xe_mau()
    db.add(xe)
    db.commit()
    return xe.id


def test_uc03_ac9_ac10_ke_toan_nhap_chi_phi_co_dinh(client, dang_nhap_voi, db, xe_id):
    kt = dang_nhap_voi("KE_TOAN")
    url = f"/api/xe/{xe_id}/chi-phi-co-dinh/2026-10"
    assert client.get(url).json() == {"xe_id": xe_id, "thang": "2026-10", "so_tien": None}

    assert client.put(url, json={"so_tien": 9000000}).json()["so_tien"] == 9000000  # tạo
    assert client.put(url, json={"so_tien": 9500000}).json()["so_tien"] == 9500000  # sửa
    assert client.put(url, json={"so_tien": 9500000}).status_code == 200  # cùng số: không ghi nhật ký
    assert client.get(url).json()["so_tien"] == 9500000

    nhat_ky = db.scalars(select(NhatKyTien).order_by(NhatKyTien.id)).all()
    assert [(n.hanh_dong, n.gia_tri_cu, n.gia_tri_moi, n.nguoi) for n in nhat_ky] == [
        ("TAO", None, "9000000", kt.id),
        ("SUA", "9000000", "9500000", kt.id),
    ]


@pytest.mark.parametrize(
    ("thang", "so_tien", "mong_doi"),
    [
        ("2026-13", 1, 400),
        ("2026-1", 1, 400),
        ("10-2026", 1, 400),
        ("2026-12", -1, 400),
        ("2026-12", 0, 200),  # biên: 0 được
    ],
)
def test_uc03_ac9_du_lieu_sai(client, dang_nhap_voi, xe_id, thang, so_tien, mong_doi):
    dang_nhap_voi("KE_TOAN")
    assert client.put(f"/api/xe/{xe_id}/chi-phi-co-dinh/{thang}", json={"so_tien": so_tien}).status_code == mong_doi


@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "QUAN_LY", "TAI_XE"])
def test_uc03_ac9_chi_ke_toan_duoc_nhap(client, dang_nhap_voi, xe_id, vai_tro):
    dang_nhap_voi(vai_tro)
    url = f"/api/xe/{xe_id}/chi-phi-co-dinh/2026-10"
    assert client.put(url, json={"so_tien": 1}).status_code == 403
    assert client.get(url).status_code == 403


def test_uc03_ac9_xe_khong_ton_tai(client, dang_nhap_voi):
    dang_nhap_voi("KE_TOAN")
    assert client.put("/api/xe/999/chi-phi-co-dinh/2026-10", json={"so_tien": 1}).status_code == 404
