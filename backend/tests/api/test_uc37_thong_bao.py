# ruff: noqa: F811  (kb, dang_chay là fixture nhập từ test UC-13, UC-32, dùng làm tham số)
from datetime import UTC, datetime, time, timedelta

import pytest

from app.auth.bao_mat import bam_mat_khau
from app.models import (
    ChiPhi,
    Chuyen,
    DonHang,
    LichSuTrangThai,
    LuotQuet,
    NguoiDung,
    NhatKyTien,
    SuCo,
    TaiXe,
    TamUng,
    Xe,
)
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.modules.thong_bao import service
from app.thoi_gian import GIO_VN, hom_nay_vn
from tests.api.test_uc13_ghep_don import kb, luc  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import sua
from tests.api.test_uc32_theo_doi_chuyen import dang_chay, ghep_cua, quet  # noqa: F401 (dang_chay là fixture)

TRUONG = {"loai", "muc_do", "tieu_de", "noi_dung", "doi_tuong", "luc"}
LOAI_DP = {"GIAY_TO", "CHUYEN_TRE", "SU_CO_MO", "DON_SAP_QUA_HAN", "THIEU_GPS", "DON_THAT_BAI"}
LOAI_KT = {"CHO_QUYET_TOAN", "CHI_PHI_CHO_DUYET", "TAM_UNG_TREO"}
LOAI_TX = {"CHUYEN_DUOC_GIAO", "SU_CO_DA_DONG", "CHI_PHI_DA_XU_LY"}


def xem(client) -> list[dict]:
    r = client.get("/api/thong-bao")
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["so_luong"] == len(j["thong_bao"])
    return j["thong_bao"]


def cua(ds, loai) -> list[dict]:
    return [t for t in ds if t["loai"] == loai]


def gio(s: str) -> datetime:
    return datetime.fromisoformat(s)


def dang_nhap_an(client, db, kb):
    """Tài xế An của kịch bản UC-13 chưa có mật khẩu: đặt rồi đăng nhập."""
    db.get(NguoiDung, db.get(TaiXe, kb["an"]).nguoi_dung_id).mat_khau_bam = bam_mat_khau("matkhau123")
    db.commit()
    assert client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "an", "mat_khau": "matkhau123"}).status_code == 200


@pytest.fixture
def du_dp(db, kb, dang_chay):
    """Đủ 6 loại thông báo của Điều phối trên C01 đang chạy."""
    c01, dp = dang_chay["c01"], dang_chay["dp"]
    quet(db, kb, c01, "d4", "LAY", tre_phut=25, trang_thai_moi="DA_LAY")  # chuyến trễ
    g1 = ghep_cua(db, c01, kb["d1"])
    db.add(LuotQuet(ghep_id=g1.id, tai_xe_id=kb["an"], loai="LAY", thoi_gian=luc(7, 30), thieu_gps=True))
    db.get(DonHang, kb["d1"]).trang_thai = "DA_LAY"
    sc = SuCo(chuyen_id=c01, tai_xe_id=kb["an"], loai="HONG_XE", ghi_chu="Đèn nhiệt độ máy", luc=luc(7))
    db.add(sc)
    db.get(Xe, kb["x4"]).han_dang_kiem = hom_nay_vn() + timedelta(days=5)  # giấy tờ sắp hết hạn
    han = datetime.now(UTC) + timedelta(hours=2)
    db.get(DonHang, kb["d8"]).han_giao = han  # chờ ghép, sắp quá hạn
    db.get(DonHang, kb["d6"]).trang_thai = "THAT_BAI"  # thất bại, không còn ghép → sẵn sàng xử lý
    db.add(
        LichSuTrangThai(
            doi_tuong="DON",
            doi_tuong_id=kb["d6"],
            tu="DA_LAY",
            sang="THAT_BAI",
            ly_do="Người nhận vắng",
            nguoi=dp.id,
            luc=luc(8),
        )
    )
    db.commit()
    return {"c01": c01, "su_co": sc.id, "han_d8": han}


# AC1 – Điều phối: bảng cảnh báo + đơn thất bại; luc đúng mốc sự việc
def test_uc37_ac1_dieu_phoi(client, db, kb, du_dp):
    ds = xem(client)
    assert {t["loai"] for t in ds} == LOAI_DP
    tre = cua(ds, "CHUYEN_TRE")
    assert len(tre) == 1 and tre[0]["doi_tuong"] == {"loai": "CHUYEN", "id": du_dp["c01"]}
    assert gio(tre[0]["luc"]) == luc(7, 30) and tre[0]["muc_do"] == "KHAN"  # lượt quét gần nhất
    su_co = cua(ds, "SU_CO_MO")[0]
    assert (su_co["noi_dung"], gio(su_co["luc"])) == ("Đèn nhiệt độ máy", luc(7))
    giay = [t for t in cua(ds, "GIAY_TO") if t["doi_tuong"] == {"loai": "XE", "id": kb["x4"]}]
    assert len(giay) == 1 and "còn 5 ngày" in giay[0]["tieu_de"] and giay[0]["muc_do"] == "CAN_LAM"
    assert gio(giay[0]["luc"]) == datetime.combine(hom_nay_vn(), time(), GIO_VN)  # nhắc lại mỗi ngày
    sap = cua(ds, "DON_SAP_QUA_HAN")
    gio_cho = int(cau_hinh.lay(db, "CFG-10"))
    assert sap[0]["doi_tuong"] == {"loai": "DON", "id": kb["d8"]}
    assert gio(sap[0]["luc"]) == du_dp["han_d8"] - timedelta(hours=gio_cho)  # lúc vào ngưỡng CFG-10
    assert cua(ds, "THIEU_GPS")[0]["doi_tuong"]["id"] == du_dp["c01"]
    tb = cua(ds, "DON_THAT_BAI")
    assert [t["doi_tuong"]["id"] for t in tb] == [kb["d6"]]
    assert (tb[0]["noi_dung"], gio(tb[0]["luc"])) == ("Người nhận vắng", luc(8))
    # Số thông báo khớp bảng cảnh báo UC-27 + đơn thất bại
    cb = client.get("/api/canh-bao").json()
    assert len(ds) == cb["so_viec"] + 1


@pytest.mark.parametrize(
    ("phut", "chu"),
    [
        (None, "trễ"),
        (0, "trễ"),
        (1, "trễ 1′"),
        (59, "trễ 59′"),  # biên: dưới 1 giờ ghi phút
        (60, "trễ 1 giờ"),  # biên: đúng 1 giờ
        (61, "trễ 1 giờ 1′"),
        (201, "trễ 3 giờ 21′"),
        (486, "trễ 8 giờ 6′"),
        (600, "trễ 10 giờ"),
    ],
)
def test_uc37_ac1_cach_ghi_do_tre(phut, chu):
    assert service._tre(phut) == chu


def test_uc37_ac1_tieu_de_chuyen_tre_doi_gio(client, db, kb, dang_chay):
    quet(db, kb, dang_chay["c01"], "d4", "LAY", tre_phut=486, trang_thai_moi="DA_LAY")
    tre = cua(xem(client), "CHUYEN_TRE")
    assert len(tre) == 1 and "trễ 8 giờ 6′" in tre[0]["tieu_de"] and "486" not in tre[0]["tieu_de"]


def test_uc37_ac1_don_that_bai_con_ghep_chua_bao(client, db, kb, dang_chay):
    # Đơn thất bại khi chuyến còn chạy (ghép còn hiệu lực) chưa xử lý được (BR-36): chưa thông báo
    quet(db, kb, dang_chay["c01"], "d2", "KHONG_LAY", trang_thai_moi="THAT_BAI")
    assert cua(xem(client), "DON_THAT_BAI") == []


def test_uc37_ac1_quan_ly_nhu_dieu_phoi(client, dang_nhap_voi, du_dp):
    dp = xem(client)
    dang_nhap_voi("QUAN_LY")
    assert xem(client) == dp


# AC2 – Kế toán: chuyến xong chưa quyết toán
@pytest.fixture
def xong(db, kb, dang_chay, dang_nhap_voi):
    c01 = dang_chay["c01"]
    kt = dang_nhap_voi("KE_TOAN")
    sua(db, Chuyen, c01, trang_thai="HOAN_THANH", ket_thuc_thuc_te=luc(11))
    for so, gio_ in ((500000, 9), (230000, 10)):
        db.add(ChiPhi(chuyen_id=c01, loai="DAU", so_tien_khai=so, ghi_chu="x", nguoi_tao=kt.id, tao_luc=luc(gio_)))
    db.add(
        ChiPhi(
            chuyen_id=c01,
            loai="BOC_XEP",
            so_tien_khai=1,
            ghi_chu="x",
            trang_thai="DA_DUYET",
            so_tien_duyet=1,
            nguoi_tao=kt.id,
        )
    )
    db.add(TamUng(chuyen_id=c01, tai_xe_id=kb["an"], so_tien=800000, hinh_thuc="TIEN_MAT", nguoi_tao=kt.id))
    db.add(
        TamUng(
            chuyen_id=c01,
            tai_xe_id=kb["an"],
            so_tien=99,
            hinh_thuc="TIEN_MAT",
            nguoi_tao=kt.id,
            trang_thai="DA_THU_HOI",
        )
    )
    db.commit()
    return c01


def test_uc37_ac2_ke_toan(client, db, xong):
    ds = xem(client)
    assert {t["loai"] for t in ds} == LOAI_KT
    assert all(t["doi_tuong"] == {"loai": "CHUYEN", "id": xong} for t in ds)
    cho = cua(ds, "CHO_QUYET_TOAN")[0]
    assert gio(cho["luc"]) == luc(11)
    chi = cua(ds, "CHI_PHI_CHO_DUYET")[0]
    assert "2 khoản" in chi["tieu_de"] and chi["noi_dung"] == "Tổng khai 730.000 đ"  # chỉ khoản chờ duyệt
    assert gio(chi["luc"]) == luc(10)  # khoản khai gần nhất
    assert "800.000 đ" in cua(ds, "TAM_UNG_TREO")[0]["tieu_de"]  # tạm ứng đã thu hồi không tính


def test_uc37_ac2_ket_thuc_su_co_nhac_nhap_luong(client, db, xong):
    sua(db, Chuyen, xong, ket_thuc_bat_thuong=True)
    assert "cần nhập lương" in cua(xem(client), "CHO_QUYET_TOAN")[0]["noi_dung"]


def test_uc37_ac2_da_quyet_toan_het_thong_bao(client, db, xong):
    sua(db, Chuyen, xong, trang_thai="DA_QUYET_TOAN")
    assert xem(client) == []


# AC3 – Tài xế: việc của chính mình
@pytest.fixture
def tx(client, db, kb, dang_chay, monkeypatch):
    """Giờ "bây giờ" là 05:00 ngày chạy (22/10/2030); An có C01 06:00 hôm nay."""
    monkeypatch.setattr(service, "bay_gio", lambda: luc(5))
    c01 = dang_chay["c01"]
    sua(db, Chuyen, c01, trang_thai="DA_CHOT")
    dp = dang_chay["dp"]
    db.add(
        LichSuTrangThai(
            doi_tuong="CHUYEN", doi_tuong_id=c01, tu="LAP", sang="DA_CHOT", nguoi=dp.id, luc=luc(20, ngay=21)
        )
    )

    def chuyen(tai_xe, ngay, trang_thai="DA_CHOT"):
        c = Chuyen(
            ma_chuyen=f"CH-T{tai_xe}{ngay}{trang_thai[:2]}",
            tuyen_id=kb["t01"],
            xe_id=kb["x4"],
            tai_xe_id=kb[tai_xe],
            khoi_hanh_du_kien=luc(8, ngay=ngay),
            ket_thuc_du_kien=luc(13, ngay=ngay),
            dieu_phoi_id=dp.id,
            trang_thai=trang_thai,
        )
        db.add(c)
        db.flush()
        return c.id

    mai = chuyen("an", 23)  # ngày mai: có
    chuyen("an", 24)  # ngày kia: không
    chuyen("an", 22, "LAP")  # chưa chốt: tài xế chưa thấy (UC-17)
    cua_dung = chuyen("dung", 22)  # của người khác

    def su_co(chuyen_id, tai_xe, trang_thai, luc_bao):
        db.add(
            SuCo(
                chuyen_id=chuyen_id,
                tai_xe_id=kb[tai_xe],
                loai="KET_XE",
                ghi_chu="x",
                trang_thai=trang_thai,
                cach_xu_ly="Đi đường tránh" if trang_thai == "DONG" else None,
                luc=luc_bao,
            )
        )

    su_co(c01, "an", "DONG", luc(4))  # có
    su_co(c01, "an", "DONG", luc(4, ngay=18))  # quá 3 ngày: không
    su_co(c01, "an", "MO", luc(4))  # chưa đóng: không
    su_co(cua_dung, "dung", "DONG", luc(4))  # của người khác: không

    def khoan(chuyen_id, khai, trang_thai, duyet, hanh_dong, luc_xu_ly, ly_do):
        cp = ChiPhi(
            chuyen_id=chuyen_id,
            loai="DAU",
            so_tien_khai=khai,
            so_tien_duyet=duyet,
            ghi_chu="x",
            trang_thai=trang_thai,
            nguoi_tao=dp.id,
        )
        db.add(cp)
        db.flush()
        db.add(
            NhatKyTien(bang="chi_phi", ban_ghi_id=cp.id, hanh_dong=hanh_dong, ly_do=ly_do, nguoi=dp.id, luc=luc_xu_ly)
        )

    khoan(c01, 500000, "TU_CHOI", None, "TU_CHOI", luc(3), "Không có hóa đơn")  # có
    khoan(c01, 400000, "DA_DUYET", 370000, "DUYET", luc(3, 30), "Hóa đơn ghi thiếu")  # có
    khoan(c01, 300000, "DA_DUYET", 300000, "DUYET", luc(3, 40), None)  # duyệt đúng số khai: không
    khoan(c01, 200000, "TU_CHOI", None, "TU_CHOI", luc(3, ngay=18), "cũ")  # quá 3 ngày: không
    khoan(cua_dung, 100000, "TU_CHOI", None, "TU_CHOI", luc(3), "của Dũng")  # của người khác: không
    db.commit()
    dang_nhap_an(client, db, kb)
    return {"c01": c01, "mai": mai}


def test_uc37_ac3_tai_xe(client, tx):
    ds = xem(client)
    assert {t["loai"] for t in ds} == LOAI_TX
    giao = cua(ds, "CHUYEN_DUOC_GIAO")
    assert {t["doi_tuong"]["id"] for t in giao} == {tx["c01"], tx["mai"]}
    assert gio([t for t in giao if t["doi_tuong"]["id"] == tx["c01"]][0]["luc"]) == luc(20, ngay=21)  # lúc chốt
    da_dong = cua(ds, "SU_CO_DA_DONG")
    assert len(da_dong) == 1 and da_dong[0]["noi_dung"] == "Đi đường tránh"
    chi = cua(ds, "CHI_PHI_DA_XU_LY")
    assert sorted(t["noi_dung"] for t in chi) == ["Hóa đơn ghi thiếu", "Không có hóa đơn"]
    assert any("bị từ chối" in t["tieu_de"] for t in chi)
    assert any("370.000 đ" in t["tieu_de"] and "400.000 đ" in t["tieu_de"] for t in chi)


def test_uc37_ac3_tu_choi_roi_duyet_chi_giu_lan_moi_nhat(client, db, tx):
    cp = db.query(ChiPhi).filter_by(so_tien_khai=500000).one()
    cp.trang_thai, cp.so_tien_duyet = "DA_DUYET", 450000
    db.add(
        NhatKyTien(
            bang="chi_phi", ban_ghi_id=cp.id, hanh_dong="DUYET", ly_do="Duyệt lại", nguoi=cp.nguoi_tao, luc=luc(4, 30)
        )
    )
    db.commit()
    chi = [t for t in cua(xem(client), "CHI_PHI_DA_XU_LY") if "500.000 đ" in t["tieu_de"]]
    assert len(chi) == 1 and chi[0]["noi_dung"] == "Duyệt lại"


def test_uc37_ac3_tai_xe_khong_ho_so(client, dang_nhap_voi):
    dang_nhap_voi("TAI_XE")  # tài khoản tài xế chưa có hồ sơ tài xế
    assert xem(client) == []


# AC4 – trường, thứ tự, quyền
def test_uc37_ac4_truong_va_thu_tu(client, du_dp):
    ds = xem(client)
    assert all(set(t) == TRUONG and t["muc_do"] in ("KHAN", "CAN_LAM", "THONG_TIN") for t in ds)
    luc_ds = [gio(t["luc"]) for t in ds]
    assert luc_ds == sorted(luc_ds, reverse=True)


def test_uc37_ac4_moi_vai_tro_chi_thay_loai_cua_minh(client, db, dang_nhap_voi, tx):
    assert {t["loai"] for t in xem(client)} <= LOAI_TX
    dang_nhap_voi("KE_TOAN")
    assert {t["loai"] for t in xem(client)} <= LOAI_KT
    dang_nhap_voi("DIEU_PHOI")
    assert {t["loai"] for t in xem(client)} <= LOAI_DP


def test_uc37_ac4_chua_dang_nhap_va_tham_so_la(client, dang_nhap_voi):
    assert client.get("/api/thong-bao").status_code == 401
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/thong-bao", params={"x": 1}).status_code == 400
