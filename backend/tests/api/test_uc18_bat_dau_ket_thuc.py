from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app import luu_tru
from app.auth.bao_mat import bam_mat_khau
from app.models import (
    Chuyen,
    DonHang,
    Ghep,
    KhachHang,
    LichSuTrangThai,
    NguoiDung,
    Nut,
    TaiXe,
    Tep,
    Tuyen,
    TuyenNut,
    Xe,
)
from app.thoi_gian import GIO_VN, hom_nay_vn

HAN_XA = date(2031, 12, 31)
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 1000
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 1000


@pytest.fixture(autouse=True)
def thu_muc_tam(tmp_path, monkeypatch):
    """Ảnh test ghi vào thư mục tạm, không vào backend/uploads."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    return tmp_path


def hom_nay(gio: int, phut: int = 0, them_ngay: int = 0) -> datetime:
    return datetime.combine(hom_nay_vn() + timedelta(days=them_ngay), time(gio, phut), GIO_VN)


@pytest.fixture
def kb(db):
    """Kịch bản mục 11 rút gọn: X1 (km 120.000), tài xế An hạng C, chuyến C01 hôm nay 23:00 đã chốt, 2 đơn."""
    nut = [Nut(ten=t, tinh=t, loai="TINH") for t in ("TP.HCM", "Cần Thơ")]
    t01 = Tuyen(ma="T01", ten="TP.HCM – Cần Thơ", dm_dau=1, dm_cau_duong=1, dm_boc_xep=1, dm_luong_tai_xe=600000)
    x1 = Xe(
        bien_so="51C-111.11",
        tai_trong_kg=5000,
        the_tich_m3=20,
        ktt_toan_bo_kg=9500,
        han_dang_kiem=HAN_XA,
        han_bao_hiem=HAN_XA,
        km_dong_ho=120000,
    )
    dp = NguoiDung(ten_dang_nhap="dp", ho_ten="Điều phối", vai_tro="DIEU_PHOI", mat_khau_bam="-")
    kh = KhachHang(ten="Cty A", sdt="0901116789")
    db.add_all([*nut, t01, x1, dp, kh])
    db.flush()
    for i, (n, phut) in enumerate(zip(nut, (0, 270), strict=True), 1):
        db.add(TuyenNut(tuyen_id=t01.id, thu_tu=i, nut_id=n.id, phut_tu_diem_dau=phut, km_tu_diem_dau=phut))

    def tai_xe(ten, hang="C"):
        nd = NguoiDung(ten_dang_nhap=ten, ho_ten=ten.title(), vai_tro="TAI_XE", mat_khau_bam=bam_mat_khau("matkhau123"))
        db.add(nd)
        db.flush()
        tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=f"GPLX{nd.id}000", hang_gplx=hang, han_gplx=HAN_XA, sdt="0909000000")
        db.add(tx)
        db.flush()
        return tx

    so = iter(range(1, 100))

    def don(trang_thai="DA_GHEP"):
        i = next(so)
        d = DonHang(
            ma_don=f"DH-{i:04d}",
            khach_hang_id=kh.id,
            kg=Decimal(100),
            m3=Decimal(1),
            so_kien=1,
            nut_lay_id=nut[0].id,
            dia_chi_lay="Lấy",
            sdt_lay="0901116789",
            nut_giao_id=nut[1].id,
            dia_chi_giao="Giao",
            nguoi_nhan="Chị Lan",
            sdt_nhan="0907778888",
            han_giao=hom_nay(23, them_ngay=2),
            don_gia_chot=1000,
            cuoc_toi_thieu_chot=50000,
            he_so_quy_doi_chot=333,
            lam_tron_chot=1000,
            kl_tinh_cuoc=Decimal(100),
            cuoc_tinh=100000,
            trang_thai=trang_thai,
        )
        db.add(d)
        db.flush()
        return d

    def chuyen(tx, trang_thai="DA_CHOT", khoi_hanh=None, ds=(), **them):
        kh_ = khoi_hanh or hom_nay(23)
        c = Chuyen(
            ma_chuyen=f"CH-{next(so):02d}",
            tuyen_id=t01.id,
            xe_id=x1.id,
            tai_xe_id=tx.id,
            khoi_hanh_du_kien=kh_,
            ket_thuc_du_kien=kh_ + timedelta(hours=7),  # 06:00 ngày mai: ngày so hạn giấy tờ
            dieu_phoi_id=dp.id,
            trang_thai=trang_thai,
            **them,
        )
        db.add(c)
        db.flush()
        for d in ds:
            db.add(Ghep(chuyen_id=c.id, don_hang_id=d.id))
        db.commit()
        return c

    an = tai_xe("an")
    d1, d2 = don(), don()
    c01 = chuyen(an, ds=(d1, d2))
    db.commit()
    return {"an": an, "binh": tai_xe("binh", "B"), "x1": x1, "d1": d1, "d2": d2, "c01": c01, "chuyen": chuyen}


def dang_nhap(client, ten="an"):
    assert client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": "matkhau123"}).status_code == 200


def bat_dau(client, chuyen_id, km=120000, anh=JPEG, ten_file="dong-ho.jpg"):
    files = {"anh_dong_ho": (ten_file, anh, "image/jpeg")} if anh is not None else None
    return client.post(f"/api/toi/chuyen/{chuyen_id}/bat-dau", data={"km_bat_dau": km}, files=files)


def ket_thuc(client, chuyen_id, km=120178, anh=JPEG):
    files = {"anh_dong_ho": ("dong-ho.jpg", anh, "image/jpeg")}
    return client.post(f"/api/toi/chuyen/{chuyen_id}/ket-thuc", data={"km_ket_thuc": km}, files=files)


def dem(db, bang, *dk) -> int:
    return db.scalar(select(func.count()).select_from(bang).where(*dk))


def lai(db, obj):
    db.expire_all()
    return db.get(type(obj), obj.id)


def dat_trang_thai_don(db, *ds_tt):
    """Giả lập UC-19, 20 đã quét: đặt thẳng trạng thái đơn."""
    db.expire_all()
    for d, tt in ds_tt:
        db.get(DonHang, d.id).trang_thai = tt
    db.commit()


# AC1 – bắt đầu hợp lệ
def test_uc18_ac1_bat_dau_hop_le(client, kb, db, thu_muc_tam):
    dang_nhap(client)
    truoc = datetime.now(GIO_VN)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 200, r.text
    assert r.json()["trang_thai"] == "DANG_CHAY"
    c = lai(db, kb["c01"])
    assert (c.trang_thai, c.km_bat_dau) == ("DANG_CHAY", 120000)
    assert truoc - timedelta(seconds=1) <= c.khoi_hanh_thuc_te <= datetime.now(GIO_VN)  # giờ máy chủ
    tep = db.scalars(select(Tep).where(Tep.chuyen_id == c.id)).all()
    assert [(t.loai, t.kich_thuoc) for t in tep] == [("ANH_KM_BAT_DAU", len(JPEG))]
    assert (thu_muc_tam / tep[0].duong_dan).read_bytes() == JPEG
    ls = db.scalars(select(LichSuTrangThai).where(LichSuTrangThai.doi_tuong_id == c.id)).all()
    assert [(x.doi_tuong, x.tu, x.sang, x.nguoi) for x in ls] == [
        ("CHUYEN", "DA_CHOT", "DANG_CHAY", kb["an"].nguoi_dung_id)
    ]
    assert {lai(db, d).trang_thai for d in (kb["d1"], kb["d2"])} == {"DA_GHEP"}


# AC2 – đúng ngày khởi hành
def test_uc18_ac2_som_gio_cung_ngay_duoc(client, kb):
    c = kb["chuyen"](kb["an"], khoi_hanh=hom_nay(23, 59))
    dang_nhap(client)
    assert bat_dau(client, c.id).status_code == 200


@pytest.mark.parametrize("them_ngay", [1, -1])
def test_uc18_ac2_khac_ngay_bi_chan(client, kb, db, them_ngay):
    c = kb["chuyen"](kb["an"], khoi_hanh=hom_nay(0, 30, them_ngay=them_ngay))
    dang_nhap(client)
    r = bat_dau(client, c.id)
    assert r.status_code == 422 and r.json()["ma"] == "BR-26"
    assert lai(db, c).trang_thai == "DA_CHOT"


# AC3 – kiểm lại giấy tờ BR-11…15
def _ngay_kt(kb) -> date:
    return kb["c01"].ket_thuc_du_kien.astimezone(GIO_VN).date()


@pytest.mark.parametrize(
    ("doi", "ma"),
    [
        (lambda kb, db: setattr(lai(db, kb["x1"]), "trang_thai", "NGUNG"), "BR-11"),
        (lambda kb, db: setattr(lai(db, kb["x1"]), "han_dang_kiem", _ngay_kt(kb) - timedelta(days=1)), "BR-12"),
        (lambda kb, db: setattr(lai(db, kb["x1"]), "han_bao_hiem", _ngay_kt(kb) - timedelta(days=1)), "BR-13"),
        (lambda kb, db: setattr(lai(db, kb["an"]), "hang_gplx", "C1"), "BR-14"),
        (lambda kb, db: setattr(lai(db, kb["an"]), "han_gplx", _ngay_kt(kb) - timedelta(days=1)), "BR-15"),
    ],
)
def test_uc18_ac3_giay_to_het_han_bi_chan(client, kb, db, doi, ma):
    doi(kb, db)
    db.commit()
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 422 and r.json()["ma"] == ma
    assert [v["ma"] for v in r.json()["chi_tiet"]] == [ma]
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"


def test_uc18_ac3_nhieu_vi_pham_va_bien(client, kb, db):
    x1 = lai(db, kb["x1"])
    x1.han_dang_kiem = x1.han_bao_hiem = _ngay_kt(kb)  # biên: đúng bằng ngày kết thúc vẫn đạt
    lai(db, kb["an"]).han_gplx = _ngay_kt(kb)
    db.commit()
    dang_nhap(client)
    assert bat_dau(client, kb["c01"].id).status_code == 200

    c = kb["chuyen"](kb["an"], khoi_hanh=hom_nay(23, 30))
    x1 = lai(db, kb["x1"])
    x1.trang_thai, x1.han_bao_hiem = "NGUNG", _ngay_kt(kb) - timedelta(days=1)
    db.get(Chuyen, kb["c01"].id).trang_thai = "HOAN_THANH"  # kết thúc c01 để không bị chặn BR-26 (AC12) trước giấy tờ
    db.commit()
    r = bat_dau(client, c.id, km=120000)
    assert r.status_code == 422 and [v["ma"] for v in r.json()["chi_tiet"]] == ["BR-11", "BR-13"]


# AC4 – km bắt đầu không nhỏ hơn km sàn
def test_uc18_ac4_km_san_la_km_dong_ho(client, kb, db):
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id, km=119999)
    assert r.status_code == 422 and r.json()["ma"] == "BR-70"
    assert dem(db, Tep) == 0
    assert bat_dau(client, kb["c01"].id, km=120000).status_code == 200


def test_uc18_ac4_chuyen_truoc_su_co_khong_km_cuoi(client, kb, db):
    kb["chuyen"](
        kb["an"], "HOAN_THANH", hom_nay(5, them_ngay=-3), km_bat_dau=120500, ket_thuc_bat_thuong=True
    )  # kết thúc do sự cố, không có km cuối: km_dong_ho xe vẫn 120.000
    dang_nhap(client)
    assert bat_dau(client, kb["c01"].id, km=120499).json()["ma"] == "BR-70"
    assert bat_dau(client, kb["c01"].id, km=120500).status_code == 200


# AC5 – kiểm ảnh
@pytest.mark.parametrize(
    ("anh", "ma_http", "ma"),
    [
        (b"day khong phai anh, chi la chu", 400, "ANH_SAI_LOAI"),
        (b"GIF89a" + b"0" * 100, 400, "ANH_SAI_LOAI"),
        (b"", 400, "ANH_RONG"),
        (b"\xff\xd8\xff" + b"0" * (luu_tru.KICH_THUOC_TOI_DA - 2), 413, "ANH_QUA_LON"),  # 500 KB + 1 byte
    ],
    ids=["chu", "gif", "rong", "qua-500kb"],  # bytes dài làm tên ca thì Windows báo lỗi biến môi trường
)
def test_uc18_ac5_anh_sai_bi_chan(client, kb, db, thu_muc_tam, anh, ma_http, ma):
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id, anh=anh)
    assert r.status_code == ma_http and r.json()["ma"] == ma
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"
    assert dem(db, Tep) == 0 and list(thu_muc_tam.iterdir()) == []


def test_uc18_ac5_thieu_anh(client, kb, db):
    dang_nhap(client)
    assert bat_dau(client, kb["c01"].id, anh=None).status_code == 400
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"


def test_uc18_ac5_anh_bien_png_va_ten_do_may_chu_dat(client, kb, db, thu_muc_tam):
    dung_500kb = b"\xff\xd8\xff" + b"0" * (luu_tru.KICH_THUOC_TOI_DA - 3)
    dang_nhap(client)
    assert bat_dau(client, kb["c01"].id, anh=dung_500kb, ten_file="../../x.jpg").status_code == 200
    ten = db.scalar(select(Tep.duong_dan))
    assert ten.endswith(".jpg") and len(ten) == 36 and "x" not in ten.removesuffix(".jpg")  # uuid hex + .jpg
    assert [p.name for p in thu_muc_tam.iterdir()] == [ten]

    c = kb["chuyen"](kb["an"], khoi_hanh=hom_nay(23, 30))
    lai(db, kb["c01"]).trang_thai = "HOAN_THANH"
    db.commit()
    assert bat_dau(client, c.id, anh=PNG, ten_file="anh.jpg").status_code == 200
    assert db.scalar(select(Tep.duong_dan).where(Tep.chuyen_id == c.id)).endswith(".png")  # theo nội dung thật


def test_uc18_ac5_loi_csdl_thi_xoa_file(client, kb, db, thu_muc_tam, monkeypatch):
    from app.modules.toi import service

    def hong(*a, **k):
        raise RuntimeError("CSDL lỗi")

    monkeypatch.setattr(service, "LichSuTrangThai", hong)
    dang_nhap(client)
    with pytest.raises(RuntimeError):
        bat_dau(client, kb["c01"].id)
    assert list(thu_muc_tam.iterdir()) == []
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"


# AC6 – kết thúc hợp lệ
def test_uc18_ac6_ket_thuc_hop_le(client, kb, db, thu_muc_tam):
    dang_nhap(client)
    assert bat_dau(client, kb["c01"].id).status_code == 200
    dat_trang_thai_don(db, (kb["d1"], "DA_GIAO"), (kb["d2"], "THAT_BAI"))
    r = ket_thuc(client, kb["c01"].id, km=120178)
    assert r.status_code == 200, r.text
    c = lai(db, kb["c01"])
    assert (c.trang_thai, c.km_ket_thuc) == ("HOAN_THANH", 120178)
    assert c.ket_thuc_thuc_te is not None
    assert lai(db, kb["x1"]).km_dong_ho == 120178
    assert sorted(db.scalars(select(Tep.loai).where(Tep.chuyen_id == c.id))) == ["ANH_KM_BAT_DAU", "ANH_KM_KET_THUC"]
    assert len(list(thu_muc_tam.iterdir())) == 2
    ls = db.scalars(
        select(LichSuTrangThai.sang).where(LichSuTrangThai.doi_tuong_id == c.id).order_by(LichSuTrangThai.id)
    )
    assert list(ls) == ["DANG_CHAY", "HOAN_THANH"]
    g = {x.don_hang_id: x for x in db.scalars(select(Ghep).where(Ghep.chuyen_id == c.id))}
    assert (g[kb["d1"].id].hieu_luc, g[kb["d1"].id].ket_qua) == (True, "DA_GIAO")
    assert (g[kb["d2"].id].hieu_luc, g[kb["d2"].id].ket_qua) == (False, "THAT_BAI")  # BR-36
    # Lịch sử UC-17 vẫn thấy cả hai đơn
    assert {p["ma_don"] for p in r.json()["lich_trinh"]} == {kb["d1"].ma_don, kb["d2"].ma_don}


# AC7 – còn đơn chưa xong; chạy rỗng
@pytest.mark.parametrize("con", ["DA_GHEP", "DA_LAY"])
def test_uc18_ac7_con_don_chua_xong(client, kb, db, con):
    dang_nhap(client)
    bat_dau(client, kb["c01"].id)
    dat_trang_thai_don(db, (kb["d1"], "DA_GIAO"), (kb["d2"], con))
    r = ket_thuc(client, kb["c01"].id)
    assert r.status_code == 422 and r.json()["ma"] == "BR-28"
    assert [v["ma_don"] for v in r.json()["chi_tiet"]] == [kb["d2"].ma_don]
    assert lai(db, kb["c01"]).trang_thai == "DANG_CHAY"
    assert lai(db, kb["x1"]).km_dong_ho == 120000


def test_uc18_ac7_chay_rong_ket_thuc_duoc(client, kb, db):
    lai(db, kb["c01"]).trang_thai = "HOAN_THANH"
    rong = kb["chuyen"](kb["an"], khoi_hanh=hom_nay(23, 30))
    dang_nhap(client)
    assert bat_dau(client, rong.id).status_code == 200
    assert ket_thuc(client, rong.id, km=120001).status_code == 200


# AC8 – km kết thúc lớn hơn km bắt đầu
def test_uc18_ac8_km_ket_thuc(client, kb, db):
    dang_nhap(client)
    bat_dau(client, kb["c01"].id, km=120000)
    dat_trang_thai_don(db, (kb["d1"], "DA_GIAO"), (kb["d2"], "DA_GIAO"))
    r = ket_thuc(client, kb["c01"].id, km=120000)
    assert r.status_code == 422 and r.json()["ma"] == "BR-70"
    assert ket_thuc(client, kb["c01"].id, km=120001).status_code == 200


# AC9 – sai trạng thái, bấm hai lần
@pytest.mark.parametrize("tt", ["DANG_CHAY", "HOAN_THANH"])
def test_uc18_ac9_bat_dau_sai_trang_thai(client, kb, db, tt):
    lai(db, kb["c01"]).trang_thai = tt
    db.commit()
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 409 and r.json()["ma"] == "SAI_TRANG_THAI"
    assert dem(db, Tep) == 0


def test_uc18_ac9_ket_thuc_chuyen_chua_chay_va_bam_hai_lan(client, kb, db):
    dang_nhap(client)
    assert ket_thuc(client, kb["c01"].id).status_code == 409
    assert bat_dau(client, kb["c01"].id).status_code == 200
    assert bat_dau(client, kb["c01"].id).status_code == 409
    assert dem(db, Tep) == 1


# AC10 – phân quyền
def test_uc18_ac10_chuyen_khong_phai_cua_minh(client, kb, db, thu_muc_tam):
    lap = kb["chuyen"](kb["an"], "LAP", hom_nay(23, 30))
    dang_nhap(client, "binh")
    for i in (kb["c01"].id, lap.id, 99999):
        assert bat_dau(client, i).status_code == 404
        assert ket_thuc(client, i).status_code == 404
    dang_nhap(client, "an")
    assert bat_dau(client, lap.id).status_code == 404
    assert dem(db, Tep) == 0 and list(thu_muc_tam.iterdir()) == []


@pytest.mark.parametrize("vai_tro", ["DIEU_PHOI", "QUAN_LY", "KE_TOAN"])
def test_uc18_ac10_vai_tro_khac(client, kb, dang_nhap_voi, vai_tro):
    dang_nhap_voi(vai_tro)
    assert bat_dau(client, kb["c01"].id).status_code == 403
    assert ket_thuc(client, kb["c01"].id).status_code == 403


def test_uc18_ac10_chua_dang_nhap(client, kb):
    assert bat_dau(client, kb["c01"].id).status_code == 401
    assert ket_thuc(client, kb["c01"].id).status_code == 401


# AC12 – xe hoặc tài xế đang có chuyến khác DANG_CHAY (BR-26)
def test_uc18_ac12_xe_dang_chay_chuyen_khac(client, kb, db, thu_muc_tam):
    dang_chay = kb["chuyen"](kb["binh"], "DANG_CHAY", hom_nay(6))
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 409 and r.json()["ma"] == "BR-26"
    assert dang_chay.ma_chuyen in r.json()["thong_diep"]
    assert kb["x1"].bien_so in r.json()["thong_diep"]
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"
    assert dem(db, Tep) == 0 and list(thu_muc_tam.iterdir()) == []


@pytest.mark.parametrize("tt", ["HOAN_THANH", "HUY"])
def test_uc18_ac12_chuyen_khac_da_xong_hoac_huy_duoc(client, kb, tt):
    kb["chuyen"](kb["binh"], tt, hom_nay(6))
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 200, r.text
    assert r.json()["trang_thai"] == "DANG_CHAY"


def test_uc18_ac12_tai_xe_dang_chay_xe_khac(client, kb, db, thu_muc_tam):
    x2 = Xe(
        bien_so="51C-222.22",
        tai_trong_kg=5000,
        the_tich_m3=20,
        ktt_toan_bo_kg=9500,
        han_dang_kiem=HAN_XA,
        han_bao_hiem=HAN_XA,
        km_dong_ho=50000,
    )
    db.add(x2)
    db.flush()
    dang_chay = Chuyen(
        ma_chuyen="CH-99",
        tuyen_id=kb["c01"].tuyen_id,
        xe_id=x2.id,
        tai_xe_id=kb["an"].id,
        khoi_hanh_du_kien=hom_nay(6),
        ket_thuc_du_kien=hom_nay(13),
        dieu_phoi_id=kb["c01"].dieu_phoi_id,
        trang_thai="DANG_CHAY",
    )
    db.add(dang_chay)
    db.commit()
    dang_nhap(client)
    r = bat_dau(client, kb["c01"].id)
    assert r.status_code == 409 and r.json()["ma"] == "BR-26"
    assert dang_chay.ma_chuyen in r.json()["thong_diep"]
    assert "Bạn đang chạy chuyến" in r.json()["thong_diep"]
    assert lai(db, kb["c01"]).trang_thai == "DA_CHOT"
    assert dem(db, Tep) == 0 and list(thu_muc_tam.iterdir()) == []
