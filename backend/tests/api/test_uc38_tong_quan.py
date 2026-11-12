# ruff: noqa: F811  (kb, dang_chay là fixture nhập từ test UC-13, UC-32, dùng làm tham số)
import pytest
from sqlalchemy import select

from app.models import Chuyen, Ghep
from app.thoi_gian import hom_nay_vn
from tests.api.test_uc13_ghep_don import NGAY, kb, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import sua
from tests.api.test_uc32_theo_doi_chuyen import chuyen_ke_tiep, dang_chay, ghep_cua, quet  # noqa: F401

TRANG_THAI = {"LAP", "DA_CHOT", "DANG_CHAY", "HOAN_THANH", "DA_QUYET_TOAN", "HUY"}


def xem(client, ngay=None) -> dict:
    ngay = ngay or NGAY.isoformat()
    r = client.get("/api/tong-quan", params={"ngay": ngay})
    assert r.status_code == 200, r.text
    return r.json()


def dat_ket_qua(db, c01, kb, don, ket_qua):
    g = ghep_cua(db, c01, kb[don])
    g.ket_qua = ket_qua  # như dịch vụ quét ghi trên chính chuyến này
    db.commit()


def doi_gio(db, ma, **gt):
    sua(db, Chuyen, db.scalar(select(Chuyen.id).where(Chuyen.ma_chuyen == ma)), **gt)


# AC1 – chuyến theo trạng thái, chỉ trong ngày
def test_uc38_ac1_chuyen_theo_trang_thai(client, db, kb, dang_chay):
    dp = dang_chay["dp"]
    for gio, tt in ((12, "HUY"), (13, "LAP"), (14, "HOAN_THANH"), (15, "DA_QUYET_TOAN"), (16, "DA_CHOT")):
        chuyen_ke_tiep(db, kb, dp, gio, trang_thai=tt)
    j = xem(client)["chuyen"]
    assert set(j["theo_trang_thai"]) == TRANG_THAI  # luôn đủ 6 khóa
    assert j["theo_trang_thai"] == {
        "LAP": 1,
        "DA_CHOT": 1,
        "DANG_CHAY": 1,
        "HOAN_THANH": 1,
        "DA_QUYET_TOAN": 1,
        "HUY": 1,
    }
    assert j["tong"] == 6 == sum(j["theo_trang_thai"].values())


def test_uc38_ac1_bien_ngay(client, db, kb, dang_chay):
    dp = dang_chay["dp"]
    chuyen_ke_tiep(db, kb, dp, 0, trang_thai="LAP")  # 00:00 hôm đó: tính
    chuyen_ke_tiep(db, kb, dp, 1, trang_thai="LAP")  # sẽ dời sang 00:00 hôm sau: không tính
    chuyen_ke_tiep(db, kb, dp, 2, trang_thai="LAP")  # sẽ dời sang 23:59 ngày 21: không tính
    doi_gio(db, "CH-C00-10", khoi_hanh_du_kien=luc(0, ngay=23))
    doi_gio(db, "CH-C00-20", khoi_hanh_du_kien=luc(23, 59, ngay=21))
    j = xem(client)["chuyen"]
    assert j["theo_trang_thai"]["LAP"] == 1 and j["tong"] == 2  # C01 + chuyến 00:00
    assert xem(client, "2030-10-23")["chuyen"]["tong"] == 1  # 00:00 hôm sau thuộc ngày hôm sau
    assert xem(client, "2030-10-21")["chuyen"]["tong"] == 1  # 23:59 hôm trước thuộc ngày hôm trước
    assert xem(client, "2030-10-25")["chuyen"] == {"tong": 0, "theo_trang_thai": dict.fromkeys(TRANG_THAI, 0)}


# AC2 – đơn giao, thất bại, còn lại; không tính chuyến hủy và đơn đã gỡ
def test_uc38_ac2_don(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    dat_ket_qua(db, c01, kb, "d4", "DA_GIAO")
    dat_ket_qua(db, c01, kb, "d1", "THAT_BAI")
    j = xem(client)["don"]
    assert j == {"tong": 3, "da_giao": 1, "that_bai": 1, "con_lai": 1, "kg_da_cho": 800.0}  # d4 = 800 kg


def test_uc38_ac2_khong_tinh_chuyen_huy_va_don_da_go(client, db, kb, dang_chay):
    c01, dp = dang_chay["c01"], dang_chay["dp"]
    ma = chuyen_ke_tiep(db, kb, dp, 12, trang_thai="HUY")
    huy = db.scalar(select(Chuyen.id).where(Chuyen.ma_chuyen == ma))
    db.add(Ghep(chuyen_id=huy, don_hang_id=kb["d5"], hieu_luc=True))  # dù còn ghép, chuyến hủy không tính (AC2)
    g2 = Ghep(chuyen_id=c01, don_hang_id=kb["d6"], hieu_luc=False)  # đơn đã gỡ khỏi C01, chưa có kết quả
    db.add(g2)
    db.commit()
    j = xem(client)
    assert j["don"]["tong"] == 3 and j["chuyen"]["theo_trang_thai"]["HUY"] == 1
    assert j["doanh_thu_du_kien"] == 5237000


# AC3 – tỉ lệ đúng giờ, biên ngưỡng CFG-09 (15 phút)
def test_uc38_ac3_dung_gio_bien(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    j = xem(client)["dung_gio"]
    assert j == {"nguong_tre_phut": 15, "da_quet": 0, "dung_gio": 0, "ty_le": None}  # chưa quét
    quet(db, kb, c01, "d4", "LAY", tre_phut=5, trang_thai_moi="DA_LAY")
    quet(db, kb, c01, "d2", "LAY", tre_phut=15, trang_thai_moi="DA_LAY")  # đúng bằng ngưỡng: đúng giờ
    quet(db, kb, c01, "d1", "LAY", tre_phut=16, trang_thai_moi="DA_LAY")  # ngưỡng + 1: trễ
    quet(db, kb, c01, "d4", "GIAO", tre_phut=-4, trang_thai_moi="DA_GIAO")  # sớm: đúng giờ
    j = xem(client)["dung_gio"]
    assert (j["da_quet"], j["dung_gio"], j["ty_le"]) == (4, 3, 0.75)


def test_uc38_ac3_khong_quet_khong_tinh(client, db, kb, dang_chay):
    # Không lấy được thì điểm giao bị bỏ (không có lượt quét giao): không vào mẫu số
    c01 = dang_chay["c01"]
    quet(db, kb, c01, "d2", "KHONG_LAY", tre_phut=0, trang_thai_moi="THAT_BAI")
    j = xem(client)["dung_gio"]
    assert (j["da_quet"], j["dung_gio"], j["ty_le"]) == (1, 1, 1.0)


# AC4 – doanh thu dự kiến
def test_uc38_ac4_doanh_thu(client, db, kb, dang_chay):
    c01 = dang_chay["c01"]
    assert xem(client)["doanh_thu_du_kien"] == 2997000 + 1440000 + 800000  # d1 + d2 + d4
    dat_ket_qua(db, c01, kb, "d1", "THAT_BAI")  # đơn thất bại vẫn nằm trong doanh thu dự kiến
    assert xem(client)["doanh_thu_du_kien"] == 5237000
    assert xem(client, "2030-10-25")["doanh_thu_du_kien"] == 0


# AC5 – quyền, dữ liệu sai, mặc định hôm nay
@pytest.mark.parametrize(("vai_tro", "ma"), [("QUAN_LY", 200), ("DIEU_PHOI", 200), ("KE_TOAN", 200), ("TAI_XE", 403)])
def test_uc38_ac5_phan_quyen(client, dang_nhap_voi, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/tong-quan").status_code == ma


def test_uc38_ac5_chua_dang_nhap(client):
    assert client.get("/api/tong-quan").status_code == 401


@pytest.mark.parametrize("ngay", ["abc", "2030-13-45", "22/10/2030", "2030-10-22T10:00"])
def test_uc38_ac5_ngay_sai(client, dang_nhap_voi, ngay):
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/tong-quan", params={"ngay": ngay}).status_code == 400


def test_uc38_ac5_tham_so_la_va_mac_dinh_hom_nay(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/tong-quan", params={"x": 1}).status_code == 400
    j = client.get("/api/tong-quan").json()
    assert j["ngay"] == hom_nay_vn().isoformat() and j["chuyen"]["tong"] == 0 and j["dung_gio"]["ty_le"] is None
