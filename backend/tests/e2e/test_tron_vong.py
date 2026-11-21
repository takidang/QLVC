# ruff: noqa: F811  (kb là fixture nhập từ test UC-13, dùng làm tham số)
"""E2E chạy trọn vòng (story E2E-tron-vong): tạo đơn → lập, ghép, chốt → tạm ứng → tài xế quét lấy, giao,
giao không được, chi phí, kết thúc → duyệt chi phí, quyết toán, thu nợ → báo cáo lãi lỗ.

Danh mục (nút, tuyến T01, xe, tài xế, khách) lấy từ fixture `kb` của UC-13; từ đơn trở đi gọi API thật,
mỗi vai trò một client đăng nhập riêng. Ảnh ghi vào thư mục tạm như test UC-19.
"""

from contextlib import ExitStack
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import luu_tru
from app.auth.bao_mat import bam_mat_khau
from app.main import app
from app.models import BangGia, KhachHang, NguoiDung, TaiXe
from app.thoi_gian import GIO_VN
from tests.api.test_uc13_ghep_don import kb  # noqa: F401 (kb là fixture)
from tests.api.test_uc19_quet_lay import GPS, JPG, LY_DO_GIAO, PNG

MK = "matkhau123"
# T01 trong kb: lương 600.000; định mức = dầu 550.000 + cầu đường 200.000 + bốc xếp 250.000
LUONG_T01, DINH_MUC_T01 = 600_000, 1_000_000
TAM_UNG = 800_000
DAU_KHAI, DAU_DUYET = 600_000, 580_000
CAU_DUONG = 200_000
CUOC_A = 2_997_000  # 1.800 kg, 6 m³ → quy đổi 6 × 333 = 1.998 kg × 1.500 đ (kịch bản mục 11, Đ1)
CUOC_B = 800_000  # 800 kg, 2 m³ → 800 kg × 1.000 đ


def kiem(r, ma: int, buoc: str) -> dict:
    assert r.status_code == ma, f"{buoc}: mong {ma}, nhận {r.status_code} {r.text}"
    return r.json() if r.content else {}


def loi(r, ma: int, ma_loi: str, buoc: str) -> None:
    assert (r.status_code, r.json().get("ma")) == (ma, ma_loi), f"{buoc}: {r.status_code} {r.text}"


@pytest.fixture
def vong(db, kb, tao_nguoi_dung, tmp_path, monkeypatch):
    """Danh mục từ kb + bảng giá, tài khoản 4 vai trò; trả các client đã đăng nhập."""
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    hom_qua = datetime.now(GIO_VN).date() - timedelta(days=30)  # ngày theo giờ VN, không theo giờ máy (CI chạy UTC)
    for lay, giao, gia in (("TP.HCM", "Cần Thơ", 1500), ("TP.HCM", "Tiền Giang", 1000)):
        db.add(BangGia(tinh_lay=lay, tinh_giao=giao, don_gia_kg=gia, cuoc_toi_thieu=50000, hieu_luc_tu=hom_qua))
    for tx in (kb["an"], kb["dung"]):  # tài xế của kb chưa có mật khẩu
        nd = db.get(NguoiDung, db.get(TaiXe, tx).nguoi_dung_id)
        nd.mat_khau_bam = bam_mat_khau(MK)
    db.commit()
    tao_nguoi_dung(ten="dp", vai_tro="DIEU_PHOI")
    tao_nguoi_dung(ten="kt", vai_tro="KE_TOAN")
    tao_nguoi_dung(ten="ql", vai_tro="QUAN_LY")
    ten_tx = {k: db.get(NguoiDung, db.get(TaiXe, kb[k]).nguoi_dung_id).ten_dang_nhap for k in ("an", "dung")}

    with ExitStack() as st:
        may = {}
        for vai, ten in (("dp", "dp"), ("kt", "kt"), ("ql", "ql"), ("an", ten_tx["an"]), ("dung", ten_tx["dung"])):
            c = st.enter_context(TestClient(app, base_url="https://testserver"))
            kiem(c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": MK}), 200, f"đăng nhập {vai}")
            may[vai] = c
        kh = db.scalar(select(KhachHang.id).where(KhachHang.ten == "Cty A"))
        nut = {r["ten"]: r["id"] for r in may["dp"].get("/api/nut?so_dong=100").json()["du_lieu"]}
        yield {"may": may, "kb": kb, "kh": kh, "nut": nut}


def tao_don(dp, v, giao, kg, m3, han) -> dict:
    return kiem(
        dp.post(
            "/api/don",
            json={
                "khach_hang_id": v["kh"],
                "mo_ta": "Hàng E2E",
                "kg": kg,
                "m3": m3,
                "so_kien": 4,
                "nut_lay_id": v["nut"]["TP.HCM"],
                "dia_chi_lay": "12 Nguyễn Huệ, Q.1",
                "sdt_lay": "0901116789",
                "nut_giao_id": v["nut"][giao],
                "dia_chi_giao": f"5 Đường số 1, {giao}",
                "nguoi_nhan": "Chị Lan",
                "sdt_nhan": "0907778888",
                "han_giao": han.isoformat(),
            },
        ),
        201,
        f"bước 1: tạo đơn đi {giao}",
    )


def trang_thai_don(dp, don_id) -> str:
    return kiem(dp.get(f"/api/don/{don_id}"), 200, "xem đơn")["trang_thai"]


def trang_thai_chuyen(dp, cid) -> str:
    return kiem(dp.get(f"/api/chuyen/{cid}"), 200, "xem chuyến")["trang_thai"]


def quet(tx, ma, loai, **them):
    files = [("anh", ("a.jpg", JPG, "image/jpeg"))]
    if loai == "GIAO":
        files.append(("chu_ky", ("ky.png", PNG, "image/png")))
    return tx.post("/api/toi/quet", data={"ma_don": ma, "loai": loai, **GPS, **them}, files=files)


def anh_dong_ho():
    return {"anh_dong_ho": ("km.jpg", JPG, "image/jpeg")}


def test_e2e_tron_vong(vong):
    m = vong["may"]
    dp, kt, ql, an, dung = m["dp"], m["kt"], m["ql"], m["an"], m["dung"]
    kb = vong["kb"]

    # BR-26: tài xế chỉ bắt đầu được trong ngày khởi hành (giờ VN). CI chạy giờ UTC: gần nửa đêm VN thì bỏ qua.
    nay = datetime.now(GIO_VN)
    khoi_hanh = (nay + timedelta(minutes=10)).replace(second=0, microsecond=0)
    if khoi_hanh.date() != nay.date():
        pytest.skip(f"Giờ VN {nay:%H:%M}: khởi hành sẽ sang ngày sau, BR-26 chặn bắt đầu chuyến")

    # Bước 1 – Điều phối tạo 2 đơn; cước chốt theo bảng giá lúc tạo (AC3)
    han = nay + timedelta(days=1)
    a = tao_don(dp, vong, "Cần Thơ", "1800", "6", han)
    b = tao_don(dp, vong, "Tiền Giang", "800", "2", han)
    assert (a["cuoc_tinh"], b["cuoc_tinh"]) == (CUOC_A, CUOC_B), "bước 1: cước chốt"
    assert trang_thai_don(dp, a["id"]) == trang_thai_don(dp, b["id"]) == "CHO_GHEP", "bước 1: đơn chờ ghép"

    # Bước 2 – lập chuyến T01, xe X1, tài xế An
    c = kiem(
        dp.post(
            "/api/chuyen",
            json={
                "tuyen_id": kb["t01"],
                "khoi_hanh_du_kien": khoi_hanh.isoformat(),
                "xe_id": kb["x1"],
                "tai_xe_id": kb["an"],
            },
        ),
        201,
        "bước 2: lập chuyến",
    )
    cid = c["id"]
    assert trang_thai_chuyen(dp, cid) == "LAP", "bước 2: chuyến LAP"

    # Bước 3 – ghép 2 đơn
    kiem(dp.post(f"/api/chuyen/{cid}/ghep", json={"don_ids": [a["id"], b["id"]]}), 200, "bước 3: ghép")
    assert trang_thai_don(dp, a["id"]) == trang_thai_don(dp, b["id"]) == "DA_GHEP", "bước 3: đơn đã ghép"

    # Bước 4 – chốt
    kiem(dp.post(f"/api/chuyen/{cid}/chot", json={}), 200, "bước 4: chốt")
    assert trang_thai_chuyen(dp, cid) == "DA_CHOT", "bước 4: chuyến DA_CHOT"

    # Bước 5 – Kế toán cấp tạm ứng ≤ định mức (BR-53)
    tu = kiem(kt.get(f"/api/chuyen/{cid}/tam-ung"), 200, "bước 5: xem tạm ứng")
    assert tu["dinh_muc"] == DINH_MUC_T01, "bước 5: định mức chốt"
    loi(
        kt.post(f"/api/chuyen/{cid}/tam-ung", json={"so_tien": DINH_MUC_T01 + 1, "hinh_thuc": "TIEN_MAT"}),
        422,
        "BR-53",
        "bước 5: vượt định mức",
    )
    kiem(kt.post(f"/api/chuyen/{cid}/tam-ung", json={"so_tien": TAM_UNG, "hinh_thuc": "TIEN_MAT"}), 201, "bước 5")

    # Bước 6 – Tài xế An bắt đầu chuyến; tài xế khác không thấy chuyến (BR-58, 404 chống IDOR)
    loi(dung.get(f"/api/toi/chuyen/{cid}"), 404, "KHONG_TIM_THAY", "bước 6: tài xế khác xem chuyến")
    lt = kiem(an.get(f"/api/toi/chuyen/{cid}"), 200, "bước 6: An xem chuyến")
    assert lt["ma_chuyen"] == c["ma_chuyen"], "bước 6: An thấy đúng chuyến"
    km0 = 50_000
    kiem(an.post(f"/api/toi/chuyen/{cid}/bat-dau", data={"km_bat_dau": km0}, files=anh_dong_ho()), 200, "bước 6")
    assert trang_thai_chuyen(dp, cid) == "DANG_CHAY", "bước 6: chuyến DANG_CHAY"

    # Bước 7 – quét lấy 2 đơn; tài xế khác quét đơn của chuyến này → 403 BR-38
    loi(quet(dung, a["ma_don"], "LAY"), 403, "BR-38", "bước 7: tài xế khác quét")
    for d in (a, b):
        kiem(quet(an, d["ma_don"], "LAY"), 200, f"bước 7: lấy {d['ma_don']}")
        assert trang_thai_don(dp, d["id"]) == "DA_LAY", f"bước 7: {d['ma_don']} DA_LAY"

    # Bước 8 – chưa xong điểm thì chưa kết thúc được (BR-28)
    r = an.post(f"/api/toi/chuyen/{cid}/ket-thuc", data={"km_ket_thuc": km0 + 300}, files=anh_dong_ho())
    loi(r, 422, "BR-28", "bước 8: kết thúc sớm")
    assert {x["ma_don"] for x in r.json()["chi_tiet"]} == {a["ma_don"], b["ma_don"]}, "bước 8: đơn còn thiếu"

    # Bước 9 – B giao không được, lý do phía khách + ảnh (BR-42); A giao kèm ảnh, chữ ký, tên (BR-41)
    kiem(quet(an, b["ma_don"], "GIAO_THAT_BAI", ly_do_id=LY_DO_GIAO), 200, "bước 9: B giao không được")
    assert trang_thai_don(dp, b["id"]) == "THAT_BAI", "bước 9: B THAT_BAI"
    kiem(quet(an, a["ma_don"], "GIAO", ten_nguoi_nhan="Chị Lan"), 200, "bước 9: giao A")
    assert trang_thai_don(dp, a["id"]) == "DA_GIAO", "bước 9: A DA_GIAO"

    # Bước 10 – công nợ: A sinh đúng một khoản phải thu bằng cước, B không (BR-56)
    pt = kiem(kt.get("/api/phai-thu", params={"khach_hang_id": vong["kh"]}), 200, "bước 10")["du_lieu"]
    cua_vong = [p for p in pt if p["don_hang_id"] in (a["id"], b["id"])]
    assert [(p["don_hang_id"], p["so_tien"], p["trang_thai_tt"]) for p in cua_vong] == [
        (a["id"], CUOC_A, "CHUA_THU")
    ], "bước 10: phải thu"

    # Bước 11 – chi phí: dầu + cầu đường, mỗi khoản 1 ảnh
    for loai, tien, them in (("DAU", DAU_KHAI, {"so_lit": "40"}), ("CAU_DUONG", CAU_DUONG, {})):
        kiem(
            an.post(
                f"/api/toi/chuyen/{cid}/chi-phi",
                data={"loai": loai, "so_tien": tien, "ghi_chu": f"E2E {loai}", **them},
                files=[("anh", ("hd.jpg", JPG, "image/jpeg"))],
            ),
            201,
            f"bước 11: khai {loai}",
        )

    # Bước 12 – kết thúc chuyến
    r = an.post(f"/api/toi/chuyen/{cid}/ket-thuc", data={"km_ket_thuc": km0 + 300}, files=anh_dong_ho())
    kiem(r, 200, "bước 12: kết thúc")
    assert trang_thai_chuyen(dp, cid) == "HOAN_THANH", "bước 12: chuyến HOAN_THANH"

    # Bước 13 – Kế toán duyệt chi phí: dầu giảm tiền phải có lý do (BR-55), cầu đường duyệt đủ
    qt = kiem(kt.get(f"/api/chuyen/{cid}/quyet-toan"), 200, "bước 13: bảng quyết toán")
    khoan = {k["loai"]: k["id"] for k in qt["khoan"]}
    loi(kt.post(f"/api/chi-phi/{khoan['DAU']}/duyet", json={"so_tien_duyet": DAU_DUYET}), 422, "BR-55", "bước 13")
    kiem(
        kt.post(
            f"/api/chi-phi/{khoan['DAU']}/duyet", json={"so_tien_duyet": DAU_DUYET, "ly_do": "Hóa đơn ghi 580.000"}
        ),
        200,
        "bước 13: duyệt dầu",
    )
    kiem(kt.post(f"/api/chi-phi/{khoan['CAU_DUONG']}/duyet", json={"so_tien_duyet": CAU_DUONG}), 200, "bước 13")

    # Bước 14 – số tiền trên bảng quyết toán (AC3; nghiep-vu mục 11 bước 7)
    tong_chi = DAU_DUYET + CAU_DUONG
    chenh = TAM_UNG - tong_chi  # dương: tài xế nộp lại; âm: công ty trả thêm (BR-55)
    qt = kiem(kt.get(f"/api/chuyen/{cid}/quyet-toan"), 200, "bước 14")
    assert qt["doanh_thu"] == CUOC_A, "bước 14: doanh thu chỉ tính A (B thất bại)"
    assert qt["lai"] == CUOC_A - tong_chi - LUONG_T01, "bước 14: lãi = doanh thu − chi phí duyệt − lương"
    assert (qt["chenh_lech_tam_ung"], qt["xu_ly_goi_y"]) == (chenh, "TAI_XE_DA_NOP") == (20_000, "TAI_XE_DA_NOP"), (
        "bước 14: chênh lệch tạm ứng = tạm ứng − chi phí đã duyệt, dương thì tài xế nộp lại"
    )

    # Bước 15 – quyết toán; Tài xế gọi quyết toán → 403 (BR-57); sai dấu chênh lệch → bị chặn
    loi(an.post(f"/api/chuyen/{cid}/quyet-toan", json={}), 403, "KHONG_DU_QUYEN", "bước 15: tài xế quyết toán")
    luc_xu_ly = datetime.now(GIO_VN).isoformat()
    sai = {"xu_ly_chenh_lech": "CONG_TY_DA_TRA", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": luc_xu_ly}
    loi(kt.post(f"/api/chuyen/{cid}/quyet-toan", json=sai), 422, "BR-55", "bước 15: sai dấu chênh lệch")
    kq = kiem(
        kt.post(
            f"/api/chuyen/{cid}/quyet-toan",
            json={"xu_ly_chenh_lech": "TAI_XE_DA_NOP", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": luc_xu_ly},
        ),
        200,
        "bước 15: quyết toán",
    )
    assert (kq["doanh_thu"], kq["tong_chi"], kq["luong_tai_xe"], kq["lai"], kq["chenh_lech_tam_ung"]) == (
        CUOC_A,
        tong_chi,
        LUONG_T01,
        CUOC_A - tong_chi - LUONG_T01,
        chenh,
    ), "bước 15: số quyết toán"
    assert trang_thai_chuyen(dp, cid) == "DA_QUYET_TOAN", "bước 15: chuyến DA_QUYET_TOAN"

    # Bước 16 – khóa sổ: duyệt lại chi phí bị chặn (BR-29)
    loi(
        kt.post(f"/api/chi-phi/{khoan['CAU_DUONG']}/duyet", json={"so_tien_duyet": 100_000, "ly_do": "Sửa sau"}),
        409,
        "BR-29",
        "bước 16: sửa chi phí sau quyết toán",
    )

    # Bước 17 – báo cáo lãi lỗ theo chuyến của tháng này có chuyến với đúng lãi (UC-26)
    thang = khoi_hanh.strftime("%Y-%m")  # báo cáo tính tháng theo ngày khởi hành giờ VN
    bc = kiem(ql.get("/api/bao-cao/lai-lo", params={"theo": "chuyen", "tu": thang, "den": thang}), 200, "bước 17")
    dong = [d for d in bc["du_lieu"] if d["chuyen_id"] == cid]
    assert len(dong) == 1 and dong[0]["lai"] == CUOC_A - tong_chi - LUONG_T01, f"bước 17: {dong}"

    # Bước 18 – Kế toán thu nợ A: khoản sang DA_THU, có phiếu thu (BR-56)
    pt_a = cua_vong[0]["id"]
    thu = kiem(
        kt.post("/api/phai-thu/da-thu", json={"phai_thu_ids": [pt_a], "ngay": nay.date().isoformat()}),
        200,
        "bước 18: đánh dấu đã thu",
    )
    assert thu["tong_tien"] == CUOC_A and thu["phieu_thu_id"], "bước 18: phiếu thu"
    pt = kiem(kt.get("/api/phai-thu", params={"khach_hang_id": vong["kh"]}), 200, "bước 18")["du_lieu"]
    assert [(p["trang_thai_tt"], p["phieu_thu_id"]) for p in pt if p["id"] == pt_a] == [
        ("DA_THU", thu["phieu_thu_id"])
    ], "bước 18: khoản đã thu"
    assert trang_thai_don(dp, a["id"]) == "DA_GIAO", "bước 18: đơn giữ DA_GIAO"
