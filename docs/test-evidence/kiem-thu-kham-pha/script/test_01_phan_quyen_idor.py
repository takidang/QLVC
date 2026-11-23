"""Mục 1: Kiểm thử phân quyền (RBAC) & IDOR qua API + khóa tài khoản thử nghiệm."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import (
    MIN_JPG,
    MIN_PNG,
    ApiClient,
    BaoCaoMuc,
    dang_nhap,
    iso_vn,
    now_vn,
    tom_tat,
)


def main():
    bc = BaoCaoMuc(1, "Phân quyền / IDOR qua API")
    ql = dang_nhap("quanly")
    dp = dang_nhap("dieuphoi")
    kt = dang_nhap("ketoan")
    tx = dang_nhap("taixe")
    anon = ApiClient()

    # Lấy dữ liệu thật đang có để test phân quyền / IDOR
    _, ds_chuyen, _ = dp.raw("GET", "/api/chuyen?so_dong=50")
    chuyen_all = ds_chuyen["du_lieu"]
    chuyen_khac_chay = next((c for c in chuyen_all if c["tai_xe_id"] != 1 and c["trang_thai"] == "DANG_CHAY"), None)
    chuyen_khac_chot = next((c for c in chuyen_all if c["tai_xe_id"] != 1 and c["trang_thai"] == "DA_CHOT"), None)
    chuyen_khac_ht = next((c for c in chuyen_all if c["tai_xe_id"] != 1 and c["trang_thai"] == "HOAN_THANH"), None)
    chuyen_khac_lap = next((c for c in chuyen_all if c["tai_xe_id"] != 1 and c["trang_thai"] == "LAP"), None)
    chuyen_khac_huy = next((c for c in chuyen_all if c["tai_xe_id"] != 1 and c["trang_thai"] == "HUY"), None)
    chuyen_qt = next((c for c in chuyen_all if c["trang_thai"] == "DA_QUYET_TOAN"), None)

    # Lấy 1 đơn nằm trên chuyến đang chạy của tài xế khác để test quét IDOR
    don_cua_tx_khac = None
    if chuyen_khac_chay:
        _, ct_chay, _ = dp.raw("GET", f"/api/chuyen/{chuyen_khac_chay['id']}")
        if ct_chay and ct_chay.get("don"):
            don_cua_tx_khac = ct_chay["don"][0]["ma_don"]

    # Lấy 1 tep_id nếu có (từ bảng quyết toán)
    tep_id_mau = None
    if chuyen_khac_ht:
        _, qt_ht, _ = kt.raw("GET", f"/api/chuyen/{chuyen_khac_ht['id']}/quyet-toan")
        for k in (qt_ht or {}).get("khoan", []):
            if k.get("anh"):
                tep_id_mau = k["anh"][0]
                break

    # 1A. Chưa đăng nhập gọi API yêu cầu đăng nhập
    for ma, path in [
        ("PQ-01", "/api/auth/toi"),
        ("PQ-02", "/api/don"),
        ("PQ-03", "/api/chuyen"),
        ("PQ-04", "/api/nguoi-dung"),
    ]:
        st, data, _ = anon.raw("GET", path)
        bc.ghi(ma, f"Chưa đăng nhập gọi GET {path}", st == 401, tom_tat(st, data), "HTTP 401", f"GET {path} (không cookie)", "Nghiem trong", "BR-57")

    # 1B. Ma trận phân quyền chéo vai trò
    cases_rbac = [
        # Tài xế gọi API của Điều phối / Kế toán / Quản lý
        ("PQ-05", "taixe", tx, "GET", "/api/don", None, (403,)),
        ("PQ-06", "taixe", tx, "POST", "/api/don", {}, (403,)),
        ("PQ-07", "taixe", tx, "GET", "/api/chuyen", None, (403,)),
        ("PQ-08", "taixe", tx, "GET", f"/api/chuyen/{chuyen_khac_ht['id']}/quyet-toan", None, (403,)),
        ("PQ-09", "taixe", tx, "POST", f"/api/chuyen/{chuyen_khac_ht['id']}/quyet-toan", {}, (403,)),
        ("PQ-10", "taixe", tx, "GET", "/api/tam-ung", None, (403,)),
        ("PQ-11", "taixe", tx, "POST", f"/api/chuyen/{chuyen_khac_chot['id']}/tam-ung", {"so_tien": 100000, "hinh_thuc": "TIEN_MAT"}, (403,)),
        ("PQ-12", "taixe", tx, "GET", "/api/phai-thu", None, (403,)),
        ("PQ-13", "taixe", tx, "GET", "/api/nguoi-dung", None, (403,)),
        ("PQ-14", "taixe", tx, "GET", "/api/bang-gia", None, (403,)),
        ("PQ-15", "taixe", tx, "GET", "/api/cau-hinh", None, (403,)),
        ("PQ-16", "taixe", tx, "GET", "/api/bao-cao/lai-lo", None, (403,)),
        ("PQ-17", "taixe", tx, "GET", "/api/bao-cao/hieu-suat-xe", None, (403,)),
        ("PQ-18", "taixe", tx, "GET", "/api/tong-quan", None, (403,)),
        ("PQ-19", "taixe", tx, "GET", "/api/canh-bao", None, (403,)),
        ("PQ-20", "taixe", tx, "GET", "/api/xe", None, (403,)),
        ("PQ-21", "taixe", tx, "GET", "/api/tai-xe", None, (403,)),
        # Điều phối gọi API của Kế toán / Quản lý / Tài xế
        ("PQ-22", "dieuphoi", dp, "POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [1], "ngay": "2026-11-23"}, (403,)),
        ("PQ-23", "dieuphoi", dp, "GET", "/api/phai-thu", None, (403,)),
        ("PQ-24", "dieuphoi", dp, "GET", "/api/bang-gia", None, (403,)),
        ("PQ-25", "dieuphoi", dp, "POST", "/api/bang-gia", {"tinh_lay": "A", "tinh_giao": "B", "don_gia_kg": 1000, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "2026-11-23"}, (403,)),
        ("PQ-26", "dieuphoi", dp, "GET", "/api/nguoi-dung", None, (403,)),
        ("PQ-27", "dieuphoi", dp, "GET", "/api/cau-hinh", None, (403,)),
        ("PQ-28", "dieuphoi", dp, "PUT", "/api/cau-hinh/CFG-01", {"gia_tri": "333"}, (403,)),
        ("PQ-29", "dieuphoi", dp, "GET", "/api/tam-ung", None, (403,)),
        ("PQ-30", "dieuphoi", dp, "GET", f"/api/chuyen/{chuyen_khac_ht['id']}/quyet-toan", None, (403,)),
        ("PQ-31", "dieuphoi", dp, "GET", "/api/bao-cao/hieu-suat-xe", None, (403,)),
        ("PQ-32", "dieuphoi", dp, "PUT", "/api/xe/1/chi-phi-co-dinh/2026-11", {"so_tien": 1000000}, (403,)),
        ("PQ-33", "dieuphoi", dp, "GET", "/api/toi/chuyen", None, (403,)),
        # Kế toán gọi API của Quản lý / Điều phối (ghi) / Tài xế
        ("PQ-34", "ketoan", kt, "GET", "/api/nguoi-dung", None, (403,)),
        ("PQ-35", "ketoan", kt, "GET", "/api/bang-gia", None, (403,)),
        ("PQ-36", "ketoan", kt, "GET", "/api/cau-hinh", None, (403,)),
        ("PQ-37", "ketoan", kt, "POST", "/api/don", {}, (403,)),
        ("PQ-38", "ketoan", kt, "POST", "/api/chuyen", {}, (403,)),
        ("PQ-39", "ketoan", kt, "POST", f"/api/chuyen/{chuyen_khac_lap['id']}/chot", {}, (403,)),
        ("PQ-40", "ketoan", kt, "GET", "/api/canh-bao", None, (403,)),
        ("PQ-41", "ketoan", kt, "GET", "/api/du-doan-tre?ngay=2026-11-23", None, (403,)),
        ("PQ-42", "ketoan", kt, "GET", "/api/toi/chuyen", None, (403,)),
        ("PQ-43", "ketoan", kt, "GET", "/api/nut", None, (403,)),
        ("PQ-44", "ketoan", kt, "GET", "/api/tuyen", None, (403,)),
        # Kế toán gọi GET /api/tai-xe (docs/api.md ghi vai trò DP, nhưng code cho cả KE_TOAN xem)
        ("PQ-45", "ketoan", kt, "GET", "/api/tai-xe", None, (403,)),
        # Quản lý gọi API ghi tiền của Kế toán & API của Tài xế (theo security-rules: Quản lý chỉ xem tiền)
        ("PQ-46", "quanly", ql, "POST", f"/api/chuyen/{chuyen_khac_chot['id']}/tam-ung", {"so_tien": 100000, "hinh_thuc": "TIEN_MAT"}, (403,)),
        ("PQ-47", "quanly", ql, "POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [1], "ngay": "2026-11-23"}, (403,)),
        ("PQ-48", "quanly", ql, "POST", f"/api/chuyen/{chuyen_khac_ht['id']}/quyet-toan", {}, (403,)),
        ("PQ-49", "quanly", ql, "PUT", "/api/xe/1/chi-phi-co-dinh/2026-11", {"so_tien": 1000000}, (403,)),
        ("PQ-50", "quanly", ql, "GET", "/api/toi/chuyen", None, (403,)),
    ]

    for ma, role, client, method, path, body, expected in cases_rbac:
        st, data, _ = client.raw(method, path, body)
        ok = st in expected
        muc = "Nghiem trong" if (not ok and st < 300 and ma != "PQ-45") else "Nhe"
        if ma == "PQ-45" and st == 200:
            bc.ghi(
                ma,
                f"{role} gọi {method} {path} (đối chiếu docs/api.md)",
                False,
                f"HTTP 200 (trả về {len(data.get('du_lieu', []))} tài xế gồm SĐT, số GPLX)",
                "docs/api.md mục 2.2 ghi GET /api/tai-xe chỉ cho vai trò DP (nhưng router mở thêm KE_TOAN)",
                f"Đăng nhập ketoan -> GET /api/tai-xe",
                "Nhe",
                "BR-57 / docs/api.md",
            )
            continue
        bc.ghi(
            ma,
            f"{role} gọi {method} {path}",
            ok,
            tom_tat(st, data),
            f"HTTP {expected}",
            f"Đăng nhập {role} -> {method} {path}",
            muc,
            "BR-57",
        )

    # 1C. Kiểm tra quyền PATCH/PUT /api/auth/ho-so (UC-39 yêu cầu 405)
    st, data, _ = tx.raw("PATCH", "/api/auth/ho-so", {"ho_ten": "Hack"})
    bc.ghi("PQ-51", "taixe gọi PATCH /api/auth/ho-so (hồ sơ chỉ xem)", st == 405, tom_tat(st, data), "HTTP 405", "Đăng nhập taixe -> PATCH /api/auth/ho-so", "Vua", "UC-39")

    # 1D. IDOR: Tài xế truy cập chuyến / quét / chi phí / sự cố KHÔNG phải của mình
    # Tạo thêm 1 tài xế mới + 1 chuyến DANG_CHAY cho tài xế mới và tạo 1 khoản chi phí để test IDOR sửa/xóa chi phí
    suffix = uuid.uuid4().hex[:6]
    tx2_user = f"txidor_{suffix}"
    st_tx2, d_tx2, _ = dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": tx2_user,
            "ho_ten": f"Tài xế IDOR {suffix}",
            "mat_khau": "demo12345",
            "so_gplx": f"IDOR{suffix.upper()}01",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0988776655",
        },
    )
    assert st_tx2 == 201, f"Tao tai xe IDOR fail: {st_tx2} {d_tx2}"
    tx2_id = d_tx2["id"]
    tx2 = dang_nhap(tx2_user, "demo12345")

    # Tìm xe rảnh hôm nay để lập chuyến cho tx2, chốt, bắt đầu -> tạo 1 chi phí của tx2
    kh_hom_nay = iso_vn(now_vn() + timedelta(minutes=20))
    _, xe_kd, _ = dp.raw("GET", f"/api/chuyen/xe-kha-dung?tuyen_id=5&khoi_hanh={kh_hom_nay.replace('+', '%2B')}")
    xe_free = next((x for x in xe_kd if x["kha_dung"]), None)
    cp_tx2_id = None
    chuyen_tx2_id = None
    if xe_free:
        st_c, d_c, _ = dp.raw(
            "POST",
            "/api/chuyen",
            {"tuyen_id": 5, "khoi_hanh_du_kien": kh_hom_nay, "xe_id": xe_free["id"], "tai_xe_id": tx2_id},
        )
        assert st_c == 201, f"Tao chuyen tx2 fail: {st_c} {d_c}"
        chuyen_tx2_id = d_c["id"]
        st_chot, d_chot, _ = dp.raw("POST", f"/api/chuyen/{chuyen_tx2_id}/chot", {"xac_nhan_chay_rong": True})
        assert st_chot == 200, f"Chot chuyen tx2 fail: {st_chot} {d_chot}"
        # Lấy km sàn của xe
        _, d_xe, _ = dp.raw("GET", f"/api/xe/{xe_free['id']}")
        km_bd = d_xe["km_dong_ho"] + 10
        st_bd, d_bd, _ = tx2.multipart(
            "POST",
            f"/api/toi/chuyen/{chuyen_tx2_id}/bat-dau",
            {"km_bat_dau": str(km_bd)},
            [("anh_dong_ho", "km.jpg", MIN_JPG, "image/jpeg")],
        )
        assert st_bd == 200, f"Bat dau chuyen tx2 fail: {st_bd} {d_bd}"
        st_cp, d_cp, _ = tx2.multipart(
            "POST",
            f"/api/toi/chuyen/{chuyen_tx2_id}/chi-phi",
            {"loai": "CAU_DUONG", "so_tien": "50000", "ghi_chu": "Phí cầu đường tx2"},
            [("anh", "hd.jpg", MIN_JPG, "image/jpeg")],
        )
        assert st_cp == 201, f"Tao chi phi tx2 fail: {st_cp} {d_cp}"
        cp_tx2_id = d_cp["id"]

    # Chạy các ca IDOR bằng tài khoản `taixe` (tai_xe_id=1) nhắm vào chuyến & chi phí của tài xế khác
    idor_checks = [
        ("IDOR-01", "taixe xem chuyến DANG_CHAY của người khác", "GET", f"/api/toi/chuyen/{chuyen_khac_chay['id']}", None, None, (403, 404)),
        ("IDOR-02", "taixe xem chuyến DA_CHOT của người khác", "GET", f"/api/toi/chuyen/{chuyen_khac_chot['id']}", None, None, (403, 404)),
        ("IDOR-03", "taixe xem chuyến LAP của người khác", "GET", f"/api/toi/chuyen/{chuyen_khac_lap['id']}", None, None, (403, 404)),
        ("IDOR-04", "taixe xem chuyến HUY của người khác", "GET", f"/api/toi/chuyen/{chuyen_khac_huy['id']}", None, None, (403, 404)),
        ("IDOR-05", "taixe xem chi phí chuyến người khác", "GET", f"/api/toi/chuyen/{chuyen_tx2_id}/chi-phi", None, None, (403, 404)),
        ("IDOR-06", "taixe xem sự cố chuyến người khác", "GET", f"/api/toi/chuyen/{chuyen_tx2_id}/su-co", None, None, (403, 404)),
        ("IDOR-07", "taixe sửa chi phí của tài xế khác", "PATCH", f"/api/toi/chi-phi/{cp_tx2_id}", {"so_tien": 99000}, None, (403, 404)),
        ("IDOR-08", "taixe xóa chi phí của tài xế khác", "DELETE", f"/api/toi/chi-phi/{cp_tx2_id}", None, None, (403, 404)),
    ]
    for ma, ten, mth, path, jbody, _, exp in idor_checks:
        st, data, _ = tx.raw(mth, path, jbody)
        bc.ghi(ma, ten, st in exp, tom_tat(st, data), f"HTTP {exp}, không lộ dữ liệu", f"Đăng nhập taixe -> {mth} {path}", "Nghiem trong", "BR-58")

    # IDOR multipart: bắt đầu, kết thúc, thêm chi phí, báo sự cố, quét trên chuyến người khác
    st, data, _ = tx.multipart("POST", f"/api/toi/chuyen/{chuyen_khac_chot['id']}/bat-dau", {"km_bat_dau": "500000"}, [("anh_dong_ho", "a.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("IDOR-09", "taixe bắt đầu chuyến DA_CHOT của người khác", st in (403, 404), tom_tat(st, data), "HTTP 403/404", f"taixe POST /api/toi/chuyen/{chuyen_khac_chot['id']}/bat-dau", "Nghiem trong", "BR-26, BR-58")

    st, data, _ = tx.multipart("POST", f"/api/toi/chuyen/{chuyen_tx2_id}/ket-thuc", {"km_ket_thuc": "900000"}, [("anh_dong_ho", "a.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("IDOR-10", "taixe kết thúc chuyến DANG_CHAY của người khác", st in (403, 404), tom_tat(st, data), "HTTP 403/404", f"taixe POST /api/toi/chuyen/{chuyen_tx2_id}/ket-thuc", "Nghiem trong", "BR-28, BR-58")

    st, data, _ = tx.multipart("POST", f"/api/toi/chuyen/{chuyen_tx2_id}/chi-phi", {"loai": "CAU_DUONG", "so_tien": "10000", "ghi_chu": "IDOR"}, [("anh", "a.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("IDOR-11", "taixe ghi chi phí vào chuyến người khác", st in (403, 404), tom_tat(st, data), "HTTP 403/404", f"taixe POST /api/toi/chuyen/{chuyen_tx2_id}/chi-phi", "Nghiem trong", "BR-54, BR-58")

    st, data, _ = tx.multipart("POST", f"/api/toi/chuyen/{chuyen_tx2_id}/su-co", {"loai": "KHAC", "ghi_chu": "IDOR sự cố"})
    bc.ghi("IDOR-12", "taixe báo sự cố trên chuyến người khác", st in (403, 404), tom_tat(st, data), "HTTP 403/404", f"taixe POST /api/toi/chuyen/{chuyen_tx2_id}/su-co", "Nghiem trong", "BR-58")

    if don_cua_tx_khac:
        st, data, _ = tx.multipart("POST", "/api/toi/quet", {"ma_don": don_cua_tx_khac, "loai": "LAY"})
        bc.ghi("IDOR-13", f"taixe quét lấy đơn {don_cua_tx_khac} của chuyến tài xế khác", st in (403, 404), tom_tat(st, data), "HTTP 403 BR-38", f"taixe POST /api/toi/quet ma_don={don_cua_tx_khac} loai=LAY", "Nghiem trong", "BR-38, BR-58")

    # IDOR tìm kiếm chung: taixe gọi /api/tim không được lộ chuyến người khác / đơn / khách / xe / tài xế
    st, data, _ = tx.raw("GET", "/api/tim?q=CH-26")
    lo_chuyen = [c for c in (data or {}).get("chuyen", {}).get("ds", []) if c["ten_tai_xe"] != "Tài xế Demo"]
    lo_khac = any((data or {}).get(k, {}).get("tong", 0) > 0 for k in ("don", "xe", "tai_xe", "khach_hang"))
    bc.ghi(
        "IDOR-14",
        "taixe tìm kiếm chung /api/tim?q=CH-26 không lộ chuyến người khác hoặc danh mục",
        st == 200 and not lo_chuyen and not lo_khac,
        f"HTTP {st}: chuyen.tong={data['chuyen']['tong']}, lo_chuyen={len(lo_chuyen)}, lo_khac={lo_khac}",
        "Chỉ trả chuyến của Tài xế Demo, các nhóm khác tong=0",
        "Đăng nhập taixe -> GET /api/tim?q=CH-26",
        "Nghiem trong",
        "BR-58, UC-36",
    )

    # Kiểm tra /api/tep/{id}/link với taixe và dieuphoi
    if tep_id_mau:
        st, data, _ = tx.raw("GET", f"/api/tep/{tep_id_mau}/link")
        bc.ghi("IDOR-15", f"taixe lấy link ảnh chi phí chuyến khác (tep_id={tep_id_mau})", st == 403, tom_tat(st, data), "HTTP 403", f"taixe GET /api/tep/{tep_id_mau}/link", "Nghiem trong", "BR-58, NFR-SEC-04")
        st, data, _ = dp.raw("GET", f"/api/tep/{tep_id_mau}/link")
        bc.ghi("IDOR-16", f"dieuphoi lấy link ảnh chi phí (tep_id={tep_id_mau})", st == 403, tom_tat(st, data), "HTTP 403 (hoặc theo api.md DP có quyền xem ảnh)", f"dieuphoi GET /api/tep/{tep_id_mau}/link", "Nhe", "BR-57")

    # Kết thúc chuyến test của tx2 để giải phóng xe cho các bài test sau
    if chuyen_tx2_id:
        _, d_xe2, _ = dp.raw("GET", f"/api/xe/{xe_free['id']}")
        tx2.multipart("POST", f"/api/toi/chuyen/{chuyen_tx2_id}/ket-thuc", {"km_ket_thuc": str(d_xe2["km_dong_ho"] + 25)}, [("anh_dong_ho", "km2.jpg", MIN_JPG, "image/jpeg")])

    # 1E. Kiểm tra khóa tạm 15 phút khi đăng nhập sai 5 lần trên tài khoản MỚI tạo bằng quanly
    u_lock = f"khoa_{suffix}"
    st_u, d_u, _ = ql.raw("POST", "/api/nguoi-dung", {"ten_dang_nhap": u_lock, "ho_ten": "Thử khóa tạm", "mat_khau": "demo12345", "vai_tro": "DIEU_PHOI"})
    assert st_u == 201, f"Tao user khoa fail: {st_u} {d_u}"
    c_tmp = ApiClient()
    statuses = []
    for _ in range(5):
        st_l, _ = c_tmp.login(u_lock, "sai_mat_khau")
        statuses.append(st_l)
    st_6, d_6 = c_tmp.login(u_lock, "demo12345")
    bc.ghi(
        "PQ-52",
        f"Tài khoản mới {u_lock}: sai 5 lần liên tiếp -> lần 6 đúng mật khẩu vẫn bị khóa 429",
        statuses == [401, 401, 401, 401, 401] and st_6 == 429,
        f"5 lần sai={statuses}; lần 6 đúng -> {tom_tat(st_6, d_6)}",
        "5 lần sai 401, lần 6 trả 429 KHOA_TAM",
        f"POST /api/nguoi-dung tạo {u_lock} -> POST /api/auth/dang-nhap sai 5 lần -> thử đăng nhập đúng",
        "Vua",
        "NFR-SEC-05",
    )

    bc.luu_json("ket_qua_01.json")


if __name__ == "__main__":
    main()
