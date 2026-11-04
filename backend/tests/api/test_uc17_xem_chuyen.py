from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from app.auth.bao_mat import bam_mat_khau
from app.models import Chuyen, DonHang, Ghep, KhachHang, NguoiDung, Nut, TaiXe, Tuyen, TuyenNut, Xe
from app.thoi_gian import GIO_VN

HAN_XA = date(2031, 12, 31)
TIEN = {"cuoc_tinh", "don_gia_chot", "cuoc_toi_thieu_chot", "lai_du_kien", "dm_dau_chot", "dm_cau_duong_chot"}


def luc(gio: int, phut: int = 0, ngay: int = 22) -> datetime:
    return datetime(2030, 10, ngay, gio, phut, tzinfo=GIO_VN)


@pytest.fixture
def kb(db):
    """Kịch bản mục 11: tuyến T01, xe X1, tài xế An và Bình, đơn Đ1, Đ2, Đ4; chuyến đặt trạng thái thẳng vào CSDL."""
    ten_nut = ("TP.HCM", "Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ")
    nut = {t: Nut(ten=t, tinh=t, loai="TINH") for t in ten_nut}
    db.add_all(nut.values())
    t01 = Tuyen(
        ma="T01", ten="TP.HCM – Cần Thơ", dm_dau=550000, dm_cau_duong=200000, dm_boc_xep=250000, dm_luong_tai_xe=600000
    )
    x1 = Xe(
        bien_so="51C-111.11",
        tai_trong_kg=5000,
        the_tich_m3=20,
        ktt_toan_bo_kg=9500,
        han_dang_kiem=HAN_XA,
        han_bao_hiem=HAN_XA,
    )
    dp = NguoiDung(ten_dang_nhap="dp", ho_ten="Điều phối", vai_tro="DIEU_PHOI", mat_khau_bam="-")
    kh = KhachHang(ten="Cty A", sdt="0901116789")
    db.add_all([t01, x1, dp, kh])
    db.flush()
    for i, (t, phut) in enumerate(zip(ten_nut, (0, 60, 120, 210, 270), strict=True), 1):
        db.add(TuyenNut(tuyen_id=t01.id, thu_tu=i, nut_id=nut[t].id, phut_tu_diem_dau=phut, km_tu_diem_dau=phut))

    def tai_xe(ten):
        nd = NguoiDung(ten_dang_nhap=ten, ho_ten=ten.title(), vai_tro="TAI_XE", mat_khau_bam=bam_mat_khau("matkhau123"))
        db.add(nd)
        db.flush()
        tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=f"GPLX{nd.id}000", hang_gplx="C", han_gplx=HAN_XA, sdt="0909000000")
        db.add(tx)
        db.flush()
        return tx

    def don(so, lay, giao, kg, m3, han, khung=(None, None), trang_thai="DA_GHEP"):
        d = DonHang(
            ma_don=f"DH-{so:04d}",
            khach_hang_id=kh.id,
            mo_ta=f"Hàng {so}",
            kg=Decimal(kg),
            m3=Decimal(m3),
            so_kien=2,
            nut_lay_id=nut[lay].id,
            dia_chi_lay=f"Lấy {so}",
            nguoi_lien_he_lay="Anh Hùng",
            sdt_lay="0901116789",
            lay_tu=khung[0],
            lay_den=khung[1],
            nut_giao_id=nut[giao].id,
            dia_chi_giao=f"Giao {so}",
            nguoi_nhan="Chị Lan",
            sdt_nhan="0907778888",
            han_giao=han,
            don_gia_chot=1000,
            cuoc_toi_thieu_chot=50000,
            he_so_quy_doi_chot=333,
            lam_tron_chot=1000,
            kl_tinh_cuoc=Decimal(kg),
            cuoc_tinh=1234000,
            trang_thai=trang_thai,
        )
        db.add(d)
        db.flush()
        return d

    an, binh = tai_xe("an"), tai_xe("binh")
    so_chuyen = iter(range(1, 100))

    def chuyen(tx, trang_thai, gio=6, ngay=22, *ds, **ghep_them):  # ghep_them: hieu_luc, ket_qua
        c = Chuyen(
            ma_chuyen=f"CH-{next(so_chuyen):02d}",
            tuyen_id=t01.id,
            xe_id=x1.id,
            tai_xe_id=tx.id,
            khoi_hanh_du_kien=luc(gio, ngay=ngay),
            ket_thuc_du_kien=luc(gio, ngay=ngay) + timedelta(hours=7),
            dieu_phoi_id=dp.id,
            trang_thai=trang_thai,
            luong_tai_xe_chot=600000 if trang_thai != "LAP" else None,
        )
        db.add(c)
        db.flush()
        for d in ds:
            db.add(Ghep(chuyen_id=c.id, don_hang_id=d.id, **ghep_them))
        db.flush()
        return c

    d1 = don(1, "TP.HCM", "Cần Thơ", 1800, 6, luc(14))
    d2 = don(2, "Long An", "Cần Thơ", 1200, 3, luc(12), (luc(6, 30), luc(9)))
    d4 = don(4, "TP.HCM", "Tiền Giang", 800, 2, luc(18))
    ds = {
        "an": an,
        "binh": binh,
        "d1": d1,
        "d2": d2,
        "d4": d4,
        "c01": chuyen(an, "DA_CHOT", 6, 22, d1, d2, d4),
    }
    db.commit()

    def luu(tao):
        def ham(*a, **k):
            x = tao(*a, **k)
            db.commit()
            return x

        return ham

    return ds | {"chuyen": luu(chuyen), "don": luu(don)}


def gio(s: str) -> str:
    """Giờ:phút theo giờ Việt Nam của một mốc máy chủ trả về (máy chủ trả UTC)."""
    return datetime.fromisoformat(s).astimezone(GIO_VN).strftime("%H:%M")


def dang_nhap_tai_xe(client, ten="an"):
    assert client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": "matkhau123"}).status_code == 200


def ma_chuyen(r) -> list[str]:
    return [c["ma_chuyen"] for c in r.json()["du_lieu"]]


def co_khoa_tien(o) -> set[str]:
    """Mọi khóa tiền xuất hiện ở bất kỳ cấp nào trong JSON."""
    if isinstance(o, dict):
        return (TIEN & o.keys()) | set().union(*(co_khoa_tien(v) for v in o.values()))
    if isinstance(o, list):
        return set().union(*(co_khoa_tien(v) for v in o))
    return set()


# AC1 – chỉ chuyến của mình
def test_uc17_ac1_chi_thay_chuyen_cua_minh(client, kb):
    c_an2 = kb["chuyen"](kb["an"], "DANG_CHAY", 6, 21)
    c_binh = kb["chuyen"](kb["binh"], "DA_CHOT", 8)
    dang_nhap_tai_xe(client, "an")
    r = client.get("/api/toi/chuyen")
    assert r.status_code == 200
    assert sorted(ma_chuyen(r)) == sorted([kb["c01"].ma_chuyen, c_an2.ma_chuyen])
    assert c_binh.ma_chuyen not in ma_chuyen(r)


# AC2 – nhóm cần làm / đã xong, không thấy LAP, HUY
def test_uc17_ac2_nhom_va_thu_tu(client, kb):
    chuyen = kb["chuyen"]
    sap = chuyen(kb["an"], "DA_CHOT", 5, 22)  # sớm hơn c01 (06:00 cùng ngày)
    chay = chuyen(kb["an"], "DANG_CHAY", 6, 23)  # khởi hành muộn nhất nhưng đang chạy → lên đầu
    xong_cu = chuyen(kb["an"], "HOAN_THANH", 6, 10)
    xong_moi = chuyen(kb["an"], "DA_QUYET_TOAN", 6, 15)
    lap = chuyen(kb["an"], "LAP", 6, 24)
    huy = chuyen(kb["an"], "HUY", 6, 25)
    dang_nhap_tai_xe(client)

    can_lam = ma_chuyen(client.get("/api/toi/chuyen"))
    assert can_lam == [chay.ma_chuyen, sap.ma_chuyen, kb["c01"].ma_chuyen]
    assert ma_chuyen(client.get("/api/toi/chuyen?nhom=can_lam")) == can_lam
    assert ma_chuyen(client.get("/api/toi/chuyen?nhom=da_xong")) == [xong_moi.ma_chuyen, xong_cu.ma_chuyen]
    tat_ca = can_lam + ma_chuyen(client.get("/api/toi/chuyen?nhom=da_xong"))
    assert lap.ma_chuyen not in tat_ca and huy.ma_chuyen not in tat_ca
    assert client.get("/api/toi/chuyen?nhom=huy").status_code == 400


# AC3 – nội dung dòng, phân trang, rỗng
def test_uc17_ac3_dong_va_phan_trang(client, kb):
    for ngay in (23, 24):
        kb["chuyen"](kb["an"], "DA_CHOT", 6, ngay)
    dang_nhap_tai_xe(client)
    dong = client.get("/api/toi/chuyen").json()["du_lieu"][0]
    assert dong["ma_chuyen"] == kb["c01"].ma_chuyen
    gia_tri = (dong["ma_tuyen"], dong["bien_so"], dong["trang_thai"], dong["so_don"])
    assert gia_tri == ("T01", "51C-111.11", "DA_CHOT", 3)
    assert datetime.fromisoformat(dong["khoi_hanh_du_kien"]) == luc(6) and dong["ket_thuc_du_kien"]
    assert not co_khoa_tien(dong) and "luong_tai_xe_chot" not in dong
    trang2 = client.get("/api/toi/chuyen?trang=2&so_dong=2").json()
    assert (trang2["tong"], len(trang2["du_lieu"])) == (3, 1)


def test_uc17_ac3_chua_co_chuyen(client, kb):
    dang_nhap_tai_xe(client, "binh")
    assert client.get("/api/toi/chuyen").json() == {"du_lieu": [], "tong": 0}


# AC4 – lịch trình BR-63, giờ kịch bản mục 11, thông tin đơn
def test_uc17_ac4_lich_trinh_theo_kich_ban(client, kb):
    dang_nhap_tai_xe(client)
    r = client.get(f"/api/toi/chuyen/{kb['c01'].id}")
    assert r.status_code == 200
    lt = r.json()["lich_trinh"]
    assert [(p["viec"], p["ma_don"]) for p in lt] == [
        ("LAY", "DH-0001"),
        ("LAY", "DH-0004"),
        ("LAY", "DH-0002"),
        ("GIAO", "DH-0004"),
        ("GIAO", "DH-0002"),  # hạn 12:00 sớm hơn Đ1 14:00 nên giao trước (BR-63)
        ("GIAO", "DH-0001"),
    ]
    assert [gio(p["eta"]) for p in lt] == ["06:00", "06:20", "07:40", "09:00", "11:50", "12:10"]
    assert [p["nut"] for p in lt] == ["TP.HCM", "TP.HCM", "Long An", "Tiền Giang", "Cần Thơ", "Cần Thơ"]

    lay_d2, giao_d2 = lt[2], lt[4]
    assert (lay_d2["dia_chi"], lay_d2["nguoi_lien_he"], lay_d2["sdt"]) == ("Lấy 2", "Anh Hùng", "0901116789")
    assert (giao_d2["dia_chi"], giao_d2["nguoi_lien_he"], giao_d2["sdt"]) == ("Giao 2", "Chị Lan", "0907778888")
    assert gio(lay_d2["lay_tu"]) == "06:30" and gio(lay_d2["lay_den"]) == "09:00"
    assert gio(giao_d2["han_giao"]) == "12:00"
    assert (lay_d2["ten_khach"], lay_d2["mo_ta"], lay_d2["kg"], lay_d2["m3"], lay_d2["so_kien"]) == (
        "Cty A",
        "Hàng 2",
        "1200.00",
        "3.00",
        2,
    )
    assert lay_d2["trang_thai_don"] == "DA_GHEP"


# AC5 – ETA kế hoạch đã lưu lúc chốt được ưu tiên
def test_uc17_ac5_dung_eta_ke_hoach_da_luu(client, kb, db):
    g = db.query(Ghep).filter_by(chuyen_id=kb["c01"].id, don_hang_id=kb["d1"].id).one()
    g.eta_lay_ke_hoach, g.eta_giao_ke_hoach = luc(6, 5), luc(12, 45)
    db.commit()
    dang_nhap_tai_xe(client)
    lt = client.get(f"/api/toi/chuyen/{kb['c01'].id}").json()["lich_trinh"]
    eta = {(p["viec"], p["ma_don"]): gio(p["eta"]) for p in lt}
    assert eta[("LAY", "DH-0001")] == "06:05" and eta[("GIAO", "DH-0001")] == "12:45"  # giờ đã lưu
    assert eta[("GIAO", "DH-0002")] == "11:50"  # cột rỗng: tính theo lịch trình


# AC6 – chỉ có lương, không lộ tiền khác
def test_uc17_ac6_chi_co_luong(client, kb):
    dang_nhap_tai_xe(client)
    ct = client.get(f"/api/toi/chuyen/{kb['c01'].id}").json()
    assert ct["luong_tai_xe_chot"] == 600000
    assert co_khoa_tien(ct) == set()
    assert "1234000" not in str(ct)  # cước của đơn không lọt ra dưới tên khác


# AC7 – chạy rỗng; đơn thất bại đã gỡ hiệu lực vẫn hiện
def test_uc17_ac7_chay_rong(client, kb):
    rong = kb["chuyen"](kb["an"], "DA_CHOT", 6, 25)
    dang_nhap_tai_xe(client)
    r = client.get(f"/api/toi/chuyen/{rong.id}")
    assert r.status_code == 200 and r.json()["lich_trinh"] == [] and r.json()["so_don"] == 0


def test_uc17_ac7_don_that_bai_van_hien(client, kb, db):
    d9 = kb["don"](9, "TP.HCM", "Tiền Giang", 100, 1, luc(18, ngay=20), trang_thai="THAT_BAI")
    d10 = kb["don"](10, "TP.HCM", "Tiền Giang", 100, 1, luc(18, ngay=20), trang_thai="CHO_GHEP")
    xong = kb["chuyen"](kb["an"], "HOAN_THANH", 6, 20, d9, hieu_luc=False, ket_qua="THAT_BAI")  # BR-36
    db.add(Ghep(chuyen_id=xong.id, don_hang_id=d10.id, hieu_luc=False))  # từng ghép rồi bị gỡ: không hiện
    db.commit()
    dang_nhap_tai_xe(client)
    ct = client.get(f"/api/toi/chuyen/{xong.id}").json()
    assert {p["ma_don"] for p in ct["lich_trinh"]} == {"DH-0009"}
    assert {p["trang_thai_don"] for p in ct["lich_trinh"]} == {"THAT_BAI"}
    assert ct["so_don"] == 1
    assert client.get("/api/toi/chuyen?nhom=da_xong").json()["du_lieu"][0]["so_don"] == 1


# AC8 – cùng một 404 cho chuyến người khác, LAP, HUY, id không có
def test_uc17_ac8_cung_mot_404(client, kb):
    c_binh = kb["chuyen"](kb["binh"], "DANG_CHAY", 8)
    lap = kb["chuyen"](kb["an"], "LAP", 6, 26)
    huy = kb["chuyen"](kb["an"], "HUY", 6, 27)
    dang_nhap_tai_xe(client)
    loi = [client.get(f"/api/toi/chuyen/{i}") for i in (c_binh.id, lap.id, huy.id, 99999)]
    assert {r.status_code for r in loi} == {404}
    assert len({(r.json()["ma"], r.json()["thong_diep"]) for r in loi}) == 1


# AC9 – phân quyền
@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "QUAN_LY", "KE_TOAN"])
def test_uc17_ac9_vai_tro_khac_bi_chan(client, kb, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/toi/chuyen").status_code == 403
    assert client.get(f"/api/toi/chuyen/{kb['c01'].id}").status_code == 403


def test_uc17_ac9_chua_dang_nhap_va_tai_xe_bi_ngung(client, kb, db):
    assert client.get("/api/toi/chuyen").status_code == 401
    assert client.get(f"/api/toi/chuyen/{kb['c01'].id}").status_code == 401
    dang_nhap_tai_xe(client)
    db.get(NguoiDung, kb["an"].nguoi_dung_id).trang_thai = "NGUNG"  # UC-04 ngừng tài xế khóa tài khoản
    db.commit()
    assert client.get("/api/toi/chuyen").status_code == 401
