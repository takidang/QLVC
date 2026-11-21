# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
import pytest
from sqlalchemy import select

from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, LyDo, NhatKyTien, Nut
from app.modules.don import that_bai
from tests.api.test_uc13_ghep_don import ghep, kb, lap, luc, so_ghep, trang_thai  # noqa: F401 (kb là fixture)
from tests.api.test_uc15_chot_chuyen import sua


@pytest.fixture
def tb(db, client, dang_nhap_voi, kb):
    """Đơn THAT_BAI sau chuyến C01 đã kết thúc: Đ1 đã lấy, giao thất bại; Đ4 không lấy được (kịch bản mục 11)."""
    dp = dang_nhap_voi("DIEU_PHOI")
    c01 = lap(client, kb)
    ly_do = {
        "vang": LyDo(ten="Người nhận vắng", ap_dung="GIAO", phia="KHACH"),
        "hong_xe": LyDo(ten="Xe hỏng", ap_dung="GIAO", phia="SU_CO_XE"),
        "khong_lay": LyDo(ten="Khách chưa chuẩn bị hàng", ap_dung="LAY", phia="KHACH"),
    }
    db.add_all(ly_do.values())
    db.flush()

    def that_bai_sau_chuyen(don, *luot):
        g = Ghep(chuyen_id=c01, don_hang_id=kb[don], hieu_luc=False, ket_qua="THAT_BAI")  # BR-36: chuyến đã xong
        db.add(g)
        db.flush()
        for loai, ld in luot:
            db.add(LuotQuet(ghep_id=g.id, tai_xe_id=kb["an"], loai=loai, ly_do_id=ly_do[ld].id if ld else None))
        db.get(DonHang, kb[don]).trang_thai = "THAT_BAI"
        return g

    that_bai_sau_chuyen("d1", ("LAY", None), ("GIAO_THAT_BAI", "vang"))
    that_bai_sau_chuyen("d4", ("KHONG_LAY", "khong_lay"))
    db.get(Chuyen, c01).trang_thai = "HOAN_THANH"
    db.commit()
    return {"dp": dp, "c01": c01, "ly_do": {k: v.id for k, v in ly_do.items()}, "them": that_bai_sau_chuyen}


def ghep_lai(client, don_id, **gt):
    return client.post(f"/api/don/{don_id}/ghep-lai", json=gt)


def tra_hang(client, don_id, **gt):
    return client.post(f"/api/don/{don_id}/tra-hang", json=gt or None)


def huy(client, don_id, ly_do="khách không gửi nữa"):
    return client.post(f"/api/don/{don_id}/huy", json={"ly_do": ly_do})


def noi_giu(db, ten="Cần Thơ", han=None) -> dict:
    nut = db.scalar(select(Nut.id).where(Nut.ten == ten))
    return {"nut_giu_id": nut, "dia_chi_giu": f"Kho {ten}"} | ({"han_giao": han.isoformat()} if han else {})


def don(db, don_id) -> DonHang:
    db.expire_all()
    return db.get(DonHang, don_id)


# AC1 – ghép lại đơn đã lấy, nơi giữ hàng, cước giữ nguyên
def test_uc22_ac1_ghep_lai_don_da_lay(client, db, kb, tb):
    r = ghep_lai(client, kb["d1"], **noi_giu(db, han=luc(17, ngay=23)))  # TC-BR69-01
    assert r.status_code == 200, r.text
    d = don(db, kb["d1"])
    assert (d.trang_thai, d.cuoc_tinh, d.han_giao) == ("CHO_GHEP", 2997000, luc(17, ngay=23))
    assert (d.nut_giu_id, d.dia_chi_giu) == (db.scalar(select(Nut.id).where(Nut.ten == "Cần Thơ")), "Kho Cần Thơ")
    assert db.scalar(select(NhatKyTien.id).where(NhatKyTien.ban_ghi_id == d.id)) is None


# AC2 – nơi giữ hàng
def test_uc22_ac2_thieu_noi_giu_hang(client, db, kb, tb):
    r = ghep_lai(client, kb["d1"])  # TC-BR69-02
    assert (r.status_code, r.json()["ma"]) == (422, "BR-69")
    assert trang_thai(db, kb["d1"]) == "THAT_BAI"
    r = ghep_lai(client, kb["d1"], nut_giu_id=noi_giu(db)["nut_giu_id"])  # thiếu địa chỉ
    assert r.json()["ma"] == "BR-69"


def test_uc22_ac2_don_chua_lay_khong_co_noi_giu(client, db, kb, tb):
    r = ghep_lai(client, kb["d4"], **noi_giu(db))
    assert (r.status_code, r.json()["ma"]) == (422, "BR-69")
    assert ghep_lai(client, kb["d4"]).status_code == 200
    d = don(db, kb["d4"])
    assert (d.trang_thai, d.nut_giu_id) == ("CHO_GHEP", None)


# AC3 – BR-37 chỉ đếm giao thất bại phía khách
def test_uc22_ac3_dat_nguong_chi_con_tra_hang(client, db, kb, tb):
    tb["them"]("d1", ("GIAO_THAT_BAI", "vang"), ("GIAO_THAT_BAI", "vang"))  # tổng 3 lần phía khách
    db.commit()
    r = ghep_lai(client, kb["d1"], **noi_giu(db))  # TC-BR37-01
    assert (r.status_code, r.json()["ma"]) == (422, "BR-37")
    assert tra_hang(client, kb["d1"]).status_code == 200


def test_uc22_ac3_su_co_xe_khong_tinh(client, db, kb, tb):
    tb["them"]("d1", ("GIAO_THAT_BAI", "vang"), ("GIAO_THAT_BAI", "hong_xe"))  # 2 phía khách + 1 sự cố xe
    db.commit()
    assert that_bai.so_lan_giao_tb_khach(db, kb["d1"]) == 2
    assert ghep_lai(client, kb["d1"], **noi_giu(db)).status_code == 200  # TC-BR37-02


def test_uc22_ac3_that_bai_khi_lay_khong_tinh(client, db, kb, tb):
    tb["them"]("d4", ("KHONG_LAY", "khong_lay"), ("KHONG_LAY", "khong_lay"))  # 3 lần không lấy được
    db.commit()
    assert ghep_lai(client, kb["d4"]).status_code == 200  # TC-BR37-03


# AC4 – ghép vào chuyến mới: lấy tại nơi giữ hàng
def test_uc22_ac4_lich_trinh_lay_tai_noi_giu(client, db, kb, tb):
    assert ghep_lai(client, kb["d1"], **noi_giu(db, "Vĩnh Long", han=luc(14, ngay=23))).status_code == 200
    sua(db, DonHang, kb["d1"], han_giao=luc(14))  # để ghép được vào chuyến ngày 22 trong kịch bản
    c02 = lap(client, kb, gio=8, xe="x4", tai_xe="dung")
    r = ghep(client, c02, kb["d1"])
    assert r.status_code == 200, r.text
    lich = {(p["viec"], p["nut"]) for p in r.json()["lich_trinh"] if p["don_id"] == kb["d1"]}
    assert lich == {("LAY", "Vĩnh Long"), ("GIAO", "Cần Thơ")}


# AC5 – hạn giao mới
def test_uc22_ac5_han_giao_moi(client, db, kb, tb, monkeypatch):
    monkeypatch.setattr(that_bai, "bay_gio", lambda: luc(9, ngay=23))
    r = ghep_lai(client, kb["d1"], **noi_giu(db, han=luc(9, ngay=23)))
    assert (r.status_code, r.json()["ma"]) == (422, "BR-31")
    assert ghep_lai(client, kb["d1"], **noi_giu(db, han=luc(9, 1, ngay=23))).status_code == 200  # biên


# AC6 – trả hàng
def test_uc22_ac6_tra_hang(client, db, kb, tb):
    assert tra_hang(client, kb["d1"]).json()["trang_thai"] == "TRA_HANG"  # TC-BR36-02
    r = tra_hang(client, kb["d4"])  # TC-BR36-03
    assert (r.status_code, r.json()["ma"]) == (422, "BR-36")
    assert trang_thai(db, kb["d4"]) == "THAT_BAI"


# AC7 – hủy
def test_uc22_ac7_huy(client, db, kb, tb):
    r = huy(client, kb["d1"])  # TC-BR34-04
    assert (r.status_code, r.json()["ma"]) == (422, "BR-34")
    assert trang_thai(db, kb["d1"]) == "THAT_BAI"
    assert huy(client, kb["d4"]).json()["trang_thai"] == "HUY"  # TC-BR34-02


# AC8 – chỉ khi chuyến đã kết thúc, đúng trạng thái
def test_uc22_ac8_chuyen_chua_ket_thuc(client, db, kb, tb):
    g = db.scalar(select(Ghep).where(Ghep.don_hang_id == kb["d1"]))
    g.hieu_luc = True  # chuyến còn chạy: ghép chưa hết hiệu lực
    db.commit()
    for r in (ghep_lai(client, kb["d1"], **noi_giu(db)), tra_hang(client, kb["d1"])):
        assert (r.status_code, r.json()["ma"]) == (409, "BR-36")
    assert trang_thai(db, kb["d1"]) == "THAT_BAI"


def test_uc22_ac8_sai_trang_thai(client, db, kb, tb):
    for r in (ghep_lai(client, kb["d8"]), tra_hang(client, kb["d8"])):  # Đ8 CHO_GHEP
        assert (r.status_code, r.json()["ma"]) == (409, "BR-36")
    assert ghep_lai(client, 999999).status_code == 404


# AC9 – lịch sử
def test_uc22_ac9_lich_su(client, db, kb, tb):
    ghep_lai(client, kb["d1"], **noi_giu(db))
    tra_hang(client, kb["d4"])  # bị chặn, không ghi
    huy(client, kb["d4"], "khách hủy")
    ls = db.execute(
        select(LichSuTrangThai.doi_tuong_id, LichSuTrangThai.tu, LichSuTrangThai.sang, LichSuTrangThai.ly_do)
        .where(LichSuTrangThai.tu == "THAT_BAI", LichSuTrangThai.nguoi == tb["dp"].id)
        .order_by(LichSuTrangThai.id)
    ).all()
    assert ls == [
        (kb["d1"], "THAT_BAI", "CHO_GHEP", "Ghép lại, giữ hàng tại Cần Thơ"),
        (kb["d4"], "THAT_BAI", "HUY", "khách hủy"),
    ]


# AC10 – danh sách cần xử lý
def test_uc22_ac10_danh_sach_can_xu_ly(client, db, kb, tb):
    ds = {d["id"]: d for d in client.get("/api/don/can-xu-ly").json()}
    assert set(ds) == {kb["d1"], kb["d4"]}
    d1, d4 = ds[kb["d1"]], ds[kb["d4"]]
    assert (d1["da_lay"], d1["so_lan_giao_tb_khach"], d1["nguong"], d1["ly_do_cuoi"]) == (
        True,
        1,
        3,
        "Người nhận vắng",
    )
    assert (d4["da_lay"], d4["so_lan_giao_tb_khach"], d4["ly_do_cuoi"]) == (False, 0, "Khách chưa chuẩn bị hàng")
    assert not d1["cho_chuyen_xong"]


# AC10 – đơn thất bại do kết thúc sự cố (BR-68): lý do gần nhất lấy từ lịch sử, không để trống
def test_uc22_ac10_ly_do_ket_thuc_su_co(client, db, kb, tb):
    sua(db, DonHang, kb["d2"], trang_thai="DA_GHEP")
    db.add(Ghep(chuyen_id=tb["c01"], don_hang_id=kb["d2"], hieu_luc=True))
    sua(db, Chuyen, tb["c01"], trang_thai="DANG_CHAY")
    assert client.post(f"/api/chuyen/{tb['c01']}/ket-thuc-su-co", json={"ly_do": "hỏng hộp số"}).status_code == 200
    ds = {d["id"]: d for d in client.get("/api/don/can-xu-ly").json()}
    assert ds[kb["d2"]]["ly_do_cuoi"] == "Sự cố xe: hỏng hộp số"
    assert ds[kb["d1"]]["ly_do_cuoi"] == "Người nhận vắng"  # không có lịch sử thì lấy từ lượt quét


# AC11 – phân quyền
@pytest.mark.parametrize(("vai_tro", "ma"), [("DIEU_PHOI", 200), ("QUAN_LY", 200), ("KE_TOAN", 403), ("TAI_XE", 403)])
def test_uc22_ac11_phan_quyen(client, dang_nhap_voi, db, kb, tb, vai_tro, ma):
    dang_nhap_voi(vai_tro)
    assert client.get("/api/don/can-xu-ly").status_code == ma
    assert tra_hang(client, kb["d1"]).status_code == ma
    assert ghep_lai(client, kb["d4"]).status_code == ma
    assert (trang_thai(db, kb["d1"]), trang_thai(db, kb["d4"])) == (
        ("TRA_HANG", "CHO_GHEP") if ma == 200 else ("THAT_BAI", "THAT_BAI")
    )


def test_uc22_ac11_chua_dang_nhap(client, db, kb, tb):
    client.cookies.clear()
    assert client.get("/api/don/can-xu-ly").status_code == 401
    assert ghep_lai(client, kb["d4"]).status_code == 401
    assert tra_hang(client, kb["d1"]).status_code == 401


def test_uc22_ac1_bo_khung_gio_lay_cu_khi_da_lay(client, db, kb, tb):
    tb["them"]("d2", ("LAY", None), ("GIAO_THAT_BAI", "vang"))  # Đ2 có khung lấy 06:30–09:00
    db.commit()
    assert ghep_lai(client, kb["d2"], **noi_giu(db)).status_code == 200
    d = don(db, kb["d2"])
    assert (d.lay_tu, d.lay_den) == (None, None)  # hàng đã ở kho, không còn hẹn lấy với khách
