"""Story DEMO: lệnh nạp dữ liệu demo (seed/demo.py) trên CSDL test, ngày cố định để kết quả không đổi."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from app import luu_tru
from app.models import BangGia, ChiPhi, Chuyen, DonHang, KhachHang, NguoiDung, PhaiThu, QuyetToan, Tuyen, Xe
from app.thoi_gian import GIO_VN, bay_gio
from seed import demo, dong_ho

LUC = datetime(2030, 10, 22, 10, 0, tzinfo=GIO_VN)  # 10:00 sáng, trong khung 7h–18h


@pytest.fixture
def da_nap(db, monkeypatch, tmp_path):
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    demo.nap(bay_gio=LUC)
    return db


def dem(db, bang, *dk) -> int:
    db.expire_all()
    return db.scalar(select(func.count()).select_from(bang).where(*dk))


def may(ten):
    return demo._may(ten)


# AC1 – danh mục
def test_demo_ac1_danh_muc(da_nap):
    db = da_nap
    assert dem(db, NguoiDung, NguoiDung.vai_tro == "TAI_XE") >= 4
    assert {v for (v,) in db.execute(select(NguoiDung.vai_tro).distinct())} == {
        "QUAN_LY",
        "DIEU_PHOI",
        "KE_TOAN",
        "TAI_XE",
    }
    assert dem(db, Xe) >= 5 and dem(db, Tuyen) >= 2 and dem(db, KhachHang) >= 5 and dem(db, BangGia) >= 1
    assert dem(db, DonHang) >= 40
    for ten in ("quanly", "dieuphoi", "ketoan", "taixe", "taixe03"):
        may(ten)  # đăng nhập được bằng demo12345


# AC2 – hôm nay đủ trạng thái và cờ
def test_demo_ac2_hom_nay(da_nap):
    ds = may("dieuphoi").get("/api/chuyen", params={"ngay": LUC.date().isoformat(), "so_dong": 100}).json()["du_lieu"]
    assert {c["trang_thai"] for c in ds} == {"LAP", "DA_CHOT", "DANG_CHAY", "HOAN_THANH", "DA_QUYET_TOAN", "HUY"}
    co = {x for c in ds for x in c["theo_doi"]["co"]}
    assert {"TRE", "SU_CO", "THAT_BAI", "CHUA_QUYET_TOAN"} <= co
    dang_chay = [c["theo_doi"] for c in ds if c["trang_thai"] == "DANG_CHAY"]
    if "vi_tri" in dang_chay[0]:  # trường thêm ở UC-32-AC14 (PR #41)
        assert all(td["vi_tri"] for td in dang_chay)
    # Không có lượt quét nào sau giờ chạy lệnh
    for c in ds:
        for p in may("dieuphoi").get(f"/api/chuyen/{c['id']}").json()["lich_trinh"]:
            assert p.get("thuc_te") is None or datetime.fromisoformat(p["thuc_te"]) <= LUC


# AC3 – 7 ngày trước, việc chờ xử lý
def test_demo_ac3_ngay_truoc_va_viec_cho(da_nap):
    db = da_nap
    dau = datetime.combine(LUC.date(), datetime.min.time(), GIO_VN)
    assert dem(db, Chuyen, Chuyen.trang_thai == "DA_QUYET_TOAN", Chuyen.khoi_hanh_du_kien < dau) >= 14
    assert dem(db, Chuyen, Chuyen.khoi_hanh_du_kien < dau - timedelta(days=6)) >= 1
    assert len(may("dieuphoi").get("/api/don/can-xu-ly").json()) >= 2
    assert dem(db, ChiPhi, ChiPhi.trang_thai == "CHO_DUYET") >= 1
    assert dem(db, PhaiThu, PhaiThu.trang_thai_tt == "CHUA_THU") >= 1
    assert dem(db, PhaiThu, PhaiThu.trang_thai_tt == "DA_THU") >= 1


# AC4 – số liệu khớp nghiệp vụ
def test_demo_ac4_so_lieu_khop(da_nap):
    db = da_nap
    kt, dp = may("ketoan"), may("dieuphoi")
    for qt in db.scalars(select(QuyetToan)):
        bang = kt.get(f"/api/chuyen/{qt.chuyen_id}/quyet-toan").json()
        assert (bang["doanh_thu"], bang["tong_chi"], bang["lai"]) == (qt.doanh_thu, qt.tong_chi, qt.lai)
    with dong_ho.gia():  # bảng giá hiệu lực theo ngày nạp (2030), tra giá theo ngày đó
        dong_ho.dat(LUC)
        for d in db.scalars(select(DonHang).limit(10)):
            vao = {"nut_lay_id": d.nut_lay_id, "nut_giao_id": d.nut_giao_id, "kg": str(d.kg), "m3": str(d.m3)}
            assert dp.post("/api/don/tinh-cuoc", json=vao).json()["cuoc"] == d.cuoc_tinh


# AC5 – không nạp chồng; --ngay-moi
def test_demo_ac5_khong_nap_chong_va_ngay_moi(da_nap, monkeypatch, tmp_path):
    db = da_nap
    truoc = (dem(db, Chuyen), dem(db, Xe), dem(db, KhachHang), dem(db, Tuyen))
    with pytest.raises(demo.LoiNap, match="--ngay-moi"):
        demo.nap(bay_gio=LUC)
    with pytest.raises(demo.LoiNap, match="đã có"):
        demo.nap(ngay_moi=True, bay_gio=LUC)
    assert dem(db, Chuyen) == truoc[0]

    mai = LUC + timedelta(days=1)
    demo.nap(ngay_moi=True, bay_gio=mai)
    assert (dem(db, Xe), dem(db, KhachHang), dem(db, Tuyen)) == truoc[1:]
    ds = may("dieuphoi").get("/api/chuyen", params={"ngay": mai.date().isoformat()}).json()["du_lieu"]
    assert len(ds) == 7


def test_demo_chi_chay_o_dev(db, monkeypatch):
    """Không nạp trên bản demo (Render): mật khẩu demo12345 ai cũng biết (góp ý review #46)."""
    monkeypatch.setattr(demo, "get_settings", lambda: type("S", (), {"app_env": "demo"})())
    with pytest.raises(demo.LoiNap, match="APP_ENV=dev"):
        demo.nap(bay_gio=LUC)
    assert dem(db, Chuyen) == 0 and dem(db, NguoiDung) == 0


def test_demo_ngoai_khung_gio(db):
    with pytest.raises(demo.LoiNap, match="7:00–18:00"):
        demo.nap(bay_gio=LUC.replace(hour=5))
    assert dem(db, Chuyen) == 0


def test_demo_tra_lai_dong_ho(da_nap):
    """Sau khi nạp, service dùng lại giờ thật (đồng hồ giả không rò ra ngoài)."""
    from app.modules.chuyen import service

    assert service.bay_gio is bay_gio
    assert abs((bay_gio() - datetime.now(GIO_VN)).total_seconds()) < 5
