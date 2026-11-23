"""Mục 2: Kiểm thử dữ liệu nhập bừa (fuzzing / boundary / XSS / SQLi / ngày tháng / tràn số) qua API."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import BaoCaoMuc, dang_nhap, iso_vn, now_vn, tom_tat


def main():
    bc = BaoCaoMuc(2, "Dữ liệu nhập bừa (API)")
    ql = dang_nhap("quanly")
    dp = dang_nhap("dieuphoi")
    kt = dang_nhap("ketoan")

    han_ok = iso_vn(now_vn() + timedelta(days=2))
    don_mau = {
        "khach_hang_id": 1,
        "mo_ta": "Hàng thử nhập bừa",
        "kg": "100.00",
        "m3": "1.00",
        "so_kien": 2,
        "nut_lay_id": 5,
        "dia_chi_lay": "10 Đường A, Cần Thơ",
        "sdt_lay": "0909111222",
        "nut_giao_id": 11,
        "dia_chi_giao": "20 Đường B, An Giang",
        "nguoi_nhan": "Anh Ba",
        "sdt_nhan": "0909333444",
        "han_giao": han_ok,
    }

    # --- A. Số âm, 0, số rất lớn (1e15, 1e19), số thập phân ở chỗ số nguyên ---
    bad_don_cases = [
        ("NB-01", "Tạo đơn kg âm (-10)", {**don_mau, "kg": "-10"}, (400, 422), "Vua", "BR-31"),
        ("NB-02", "Tạo đơn kg = 0", {**don_mau, "kg": "0"}, (400, 422), "Vua", "BR-31"),
        ("NB-03", "Tạo đơn m3 = 0", {**don_mau, "m3": "0"}, (400, 422), "Vua", "BR-31"),
        ("NB-04", "Tạo đơn so_kien = 0", {**don_mau, "so_kien": 0}, (400, 422), "Vua", "BR-31"),
        ("NB-05", "Tạo đơn so_kien âm (-5)", {**don_mau, "so_kien": -5}, (400, 422), "Vua", "BR-31"),
        ("NB-06", "Tạo đơn so_kien thập phân (1.5)", {**don_mau, "so_kien": 1.5}, (400, 422), "Vua", "BR-31"),
        ("NB-07", "Tạo đơn so_kien dạng float nguyên (2.0)", {**don_mau, "so_kien": 2.0}, (400, 422), "Nhe", "NFR-FUN-02"),
        ("NB-08", "Tạo đơn so_kien cực lớn (1e15 = 1000000000000000)", {**don_mau, "so_kien": 10**15}, (400, 422), "Vua", "BR-31"),
        ("NB-09", "Tạo đơn so_kien vượt BIGINT (10^19)", {**don_mau, "so_kien": 10**19}, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-10", "Tạo đơn m3=350000 -> kl_quy_doi vượt Numeric(10,2)", {**don_mau, "m3": "350000.00"}, (400, 422), "Nghiem trong", "BR-46, NFR-REL-01"),
        ("NB-11", "Tạo đơn kg cực lớn (1e15)", {**don_mau, "kg": "1000000000000000"}, (400, 422), "Vua", "BR-31"),
        ("NB-12", "Tạo đơn chuỗi rỗng ở dia_chi_lay", {**don_mau, "dia_chi_lay": "   "}, (400, 422), "Vua", "BR-31"),
        ("NB-13", "Tạo đơn mo_ta 10.000 ký tự", {**don_mau, "mo_ta": "A" * 10000}, (400, 422), "Vua", "Validation"),
        ("NB-14", "Tạo đơn dia_chi_lay 10.000 ký tự", {**don_mau, "dia_chi_lay": "B" * 10000}, (400, 422), "Vua", "Validation"),
        ("NB-15", "Tạo đơn ngày sai 30/02 (2026-02-30)", {**don_mau, "han_giao": "2026-02-30T10:00:00+07:00"}, (400, 422), "Vua", "BR-31"),
        ("NB-16", "Tạo đơn hạn giao năm 1900", {**don_mau, "han_giao": "1900-01-01T10:00:00+07:00"}, (400, 422), "Vua", "BR-31"),
        ("NB-17", "Tạo đơn hạn giao năm 3000", {**don_mau, "han_giao": "3000-01-01T10:00:00+07:00"}, (400, 422), "Vua", "BR-31"),
        ("NB-18", "Tạo đơn thiếu múi giờ ở han_giao", {**don_mau, "han_giao": "2026-12-01T10:00:00"}, (400, 422), "Vua", "api.md 1"),
        ("NB-19", "Tạo đơn điểm lấy == điểm giao (địa chỉ giống nhau)", {**don_mau, "dia_chi_giao": don_mau["dia_chi_lay"]}, (400, 422), "Vua", "BR-31"),
    ]
    for ma, ten, payload, exp, muc, br in bad_don_cases:
        st, data, _ = dp.raw("POST", "/api/don", payload)
        # Nếu trả 500 thì luôn nâng mức lên Nghiêm trọng
        muc_thuc = "Nghiem trong" if st >= 500 else muc
        bc.ghi(
            ma,
            ten,
            st in exp,
            tom_tat(st, data),
            f"HTTP {exp} kèm thông báo tiếng Việt, không 500, không lưu rác",
            f"POST /api/don body={str(payload)[:200]}",
            muc_thuc,
            br,
        )

    # --- B. Bảng giá, Xe, Chi phí cố định, Tuyến với số âm / 0 / 1e15 / thập phân / năm 1900 & 3000 ---
    sfx = uuid.uuid4().hex[:5].upper()
    other_bad = [
        ("NB-20", "Bảng giá don_gia_kg âm (-100)", ql, "POST", "/api/bang-gia", {"tinh_lay": f"T{sfx}", "tinh_giao": "B", "don_gia_kg": -100, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "2026-11-23"}, (400, 422), "Vua", "BR-48"),
        ("NB-21", "Bảng giá don_gia_kg thập phân (1200.5)", ql, "POST", "/api/bang-gia", {"tinh_lay": f"T{sfx}", "tinh_giao": "B", "don_gia_kg": 1200.5, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "2026-11-23"}, (400, 422), "Vua", "NFR-FUN-02"),
        ("NB-22", "Bảng giá don_gia_kg = 1e15 (1000000000000000)", ql, "POST", "/api/bang-gia", {"tinh_lay": f"T1E15_{sfx}", "tinh_giao": "B", "don_gia_kg": 10**15, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "2026-11-23"}, (400, 422), "Vua", "Validation"),
        ("NB-23", "Bảng giá don_gia_kg vượt BIGINT (10^19)", ql, "POST", "/api/bang-gia", {"tinh_lay": f"T1E19_{sfx}", "tinh_giao": "B", "don_gia_kg": 10**19, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "2026-11-23"}, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-24", "Bảng giá hieu_luc_tu năm 3000", ql, "POST", "/api/bang-gia", {"tinh_lay": f"T3000_{sfx}", "tinh_giao": "B", "don_gia_kg": 1200, "cuoc_toi_thieu": 50000, "hieu_luc_tu": "3000-01-01"}, (400, 422), "Vua", "Validation"),
        ("NB-25", "Xe tai_trong_kg = 1e15 & ktt_toan_bo_kg = 1e15", dp, "POST", "/api/xe", {"bien_so": f"99Z-{sfx}", "tai_trong_kg": 10**15, "the_tich_m3": "20.00", "ktt_toan_bo_kg": 10**15, "han_dang_kiem": "2027-12-31", "han_bao_hiem": "2027-12-31", "km_dong_ho": 0}, (400, 422), "Vua", "Validation"),
        ("NB-26", "Xe tai_trong_kg vượt BIGINT (10^19)", dp, "POST", "/api/xe", {"bien_so": f"99Y-{sfx}", "tai_trong_kg": 10**19, "the_tich_m3": "20.00", "ktt_toan_bo_kg": 10**19, "han_dang_kiem": "2027-12-31", "han_bao_hiem": "2027-12-31", "km_dong_ho": 0}, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-27", "Xe han_dang_kiem năm 1900 & han_bao_hiem năm 3000", dp, "POST", "/api/xe", {"bien_so": f"99D-{sfx}", "tai_trong_kg": 5000, "the_tich_m3": "20.00", "ktt_toan_bo_kg": 9000, "han_dang_kiem": "1900-01-01", "han_bao_hiem": "3000-01-01", "km_dong_ho": 0}, (400, 422), "Vua", "Validation"),
        ("NB-28", "Chi phí cố định xe so_tien = 1e15 (2026-01)", kt, "PUT", "/api/xe/4/chi-phi-co-dinh/2026-01", {"so_tien": 10**15}, (400, 422), "Vua", "Validation"),
        ("NB-29", "Chi phí cố định xe so_tien vượt BIGINT (10^19)", kt, "PUT", "/api/xe/4/chi-phi-co-dinh/2026-02", {"so_tien": 10**19}, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-30", "Chi phí cố định xe so_tien âm (-50000)", kt, "PUT", "/api/xe/4/chi-phi-co-dinh/2026-02", {"so_tien": -50000}, (400, 422), "Vua", "NFR-FUN-02"),
        ("NB-31", "Chi phí cố định xe tháng 0000-01", kt, "PUT", "/api/xe/4/chi-phi-co-dinh/0000-01", {"so_tien": 100000}, (400, 422), "Vua", "Validation"),
        ("NB-32", "Lập chuyến giờ khởi hành trong quá khứ", dp, "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": iso_vn(now_vn() - timedelta(hours=2)), "xe_id": 6, "tai_xe_id": 2}, (400, 422), "Vua", "BR-22"),
        ("NB-33", "Lập chuyến giờ khởi hành năm 1900", dp, "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": "1900-01-01T08:00:00+07:00", "xe_id": 6, "tai_xe_id": 2}, (400, 422), "Vua", "BR-22"),
        ("NB-34", "Lập chuyến giờ khởi hành ngày sai 2026-02-30", dp, "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": "2026-02-30T08:00:00+07:00", "xe_id": 6, "tai_xe_id": 2}, (400, 422), "Vua", "Validation"),
        ("NB-35", "Lập chuyến giờ khởi hành 9999-12-31T23:30:00+07:00 (tràn datetime)", dp, "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": "9999-12-31T23:30:00+07:00", "xe_id": 6, "tai_xe_id": 2}, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-36", "Báo cáo lãi lỗ tu=0000-01&den=0000-01", ql, "GET", "/api/bao-cao/lai-lo?tu=0000-01&den=0000-01", None, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-37", "Báo cáo lãi lỗ tu=9999-12&den=9999-12", ql, "GET", "/api/bao-cao/lai-lo?tu=9999-12&den=9999-12", None, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-38", "Báo cáo hiệu suất xe thang=0000-01", ql, "GET", "/api/bao-cao/hieu-suat-xe?thang=0000-01", None, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-39", "Báo cáo hiệu suất xe thang=9999-12", ql, "GET", "/api/bao-cao/hieu-suat-xe?thang=9999-12", None, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-40", "Phân trang trang=10^18 (tràn OFFSET BIGINT)", dp, "GET", "/api/don?trang=1000000000000000000", None, (400, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-41", "Path param ID vượt BIGINT GET /api/don/99999999999999999999", dp, "GET", "/api/don/99999999999999999999", None, (400, 404, 422), "Nghiem trong", "NFR-REL-01"),
        ("NB-42", "Tạm ứng số thập phân 100000.5", kt, "POST", "/api/chuyen/20/tam-ung", {"so_tien": 100000.5, "hinh_thuc": "TIEN_MAT"}, (400, 422), "Vua", "NFR-FUN-02"),
        ("NB-43", "Tạm ứng số float nguyên 100000.0", kt, "POST", "/api/chuyen/20/tam-ung", {"so_tien": 100000.0, "hinh_thuc": "TIEN_MAT"}, (400, 422), "Vua", "NFR-FUN-02"),
        ("NB-44", "Tạm ứng số âm -100000", kt, "POST", "/api/chuyen/20/tam-ung", {"so_tien": -100000, "hinh_thuc": "TIEN_MAT"}, (400, 422), "Vua", "BR-53"),
        ("NB-45", "Tạm ứng số 0", kt, "POST", "/api/chuyen/20/tam-ung", {"so_tien": 0, "hinh_thuc": "TIEN_MAT"}, (400, 422), "Vua", "BR-53"),
    ]
    for ma, ten, client, mth, path, body, exp, muc, br in other_bad:
        st, data, _ = client.raw(mth, path, body)
        muc_thuc = "Nghiem trong" if st >= 500 else muc
        bc.ghi(
            ma,
            ten,
            st in exp,
            tom_tat(st, data),
            f"HTTP {exp}, không 500, không lưu dữ liệu vô lý",
            f"{mth} {path}" + (f" body={body}" if body is not None else ""),
            muc_thuc,
            br,
        )

    # Trả chi phí cố định xe 4 tháng 2026-01 về 0 nếu NB-28 lỡ lưu 1e15 để không làm hỏng báo cáo lãi lỗ
    kt.raw("PUT", "/api/xe/4/chi-phi-co-dinh/2026-01", {"so_tien": 0})

    # --- C. SQL Injection & XSS & Emoji qua API ---
    sqli = "' OR 1=1 --"
    xss = "<script>alert(1)</script>"
    emoji = "Hàng dễ vỡ 🚚🔥💥"

    # C1. SQLi ở các ô tìm kiếm -> không được trả lỗi 500 và không được trả toàn bộ bảng
    for ma, path in [
        ("NB-46", "/api/don?tim=%27%20OR%201%3D1%20--"),
        ("NB-47", "/api/chuyen?tu_khoa=%27%20OR%201%3D1%20--"),
        ("NB-48", "/api/khach-hang?tim=%27%20OR%201%3D1%20--"),
        ("NB-49", "/api/tim?q=%27%20OR%201%3D1%20--"),
    ]:
        st, data, _ = dp.raw("GET", path)
        tong = data.get("tong", 0) if isinstance(data, dict) and "tong" in data else sum(
            (data.get(k, {}) or {}).get("tong", 0) for k in ("chuyen", "don", "xe", "tai_xe", "khach_hang")
        ) if isinstance(data, dict) else -1
        bc.ghi(ma, f"SQLi qua tìm kiếm GET {path}", st == 200 and tong == 0, f"HTTP {st}, tong={tong}", "HTTP 200, tong=0 (không bị SQLi)", f"GET {path}", "Nghiem trong", "OWASP SQLi")

    # C2. SQLi ở đăng nhập (dùng username lạ, không đụng tài khoản demo!)
    st, data, _ = dp.clone().raw("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": sqli, "mat_khau": sqli})
    bc.ghi("NB-50", "SQLi tại POST /api/auth/dang-nhap", st == 401, tom_tat(st, data), "HTTP 401 SAI_THONG_TIN", f"POST /api/auth/dang-nhap ten_dang_nhap={sqli!r}", "Nghiem trong", "OWASP SQLi")

    # C3. Emoji & XSS lưu vào khách hàng / đơn (kiểm tra API không 500; phần XSS không chạy sẽ kiểm tra tiếp ở mục 7 bằng Playwright)
    st_kh, d_kh, _ = dp.raw("POST", "/api/khach-hang", {"ten": f"Khách {xss} {emoji}", "sdt": "0919888777", "dia_chi": f"{xss} {sqli}"})
    bc.ghi(
        "NB-51",
        "Lưu tên khách hàng chứa XSS + Emoji + SQLi (kiểm không 500, chờ kiểm XSS ở UI)",
        st_kh in (201, 400, 422),
        tom_tat(st_kh, d_kh),
        "Không 500 (từ chối hoặc lưu an toàn, không chạy XSS trên giao diện)",
        f"POST /api/khach-hang ten='Khách {xss} {emoji}'",
        "Nghiem trong" if st_kh >= 500 else "Nhe",
        "OWASP XSS/SQLi",
    )

    # C4. Kiểm tra thông báo lỗi 400 có chi tiết tiếng Anh từ Pydantic hay tiếng Việt
    st_msg, d_msg, _ = dp.raw("POST", "/api/don", {**don_mau, "kg": "-5"})
    chi_tiet_msgs = [c.get("msg", "") for c in (d_msg or {}).get("chi_tiet", [])] if isinstance(d_msg, dict) else []
    co_tieng_anh = any("Input should be" in m or "Field required" in m or "String should have" in m for m in chi_tiet_msgs)
    bc.ghi(
        "NB-52",
        "Kiểm tra ngôn ngữ thông báo lỗi chi tiết khi nhập dữ liệu sai (kg=-5)",
        st_msg == 400 and not co_tieng_anh,
        f"HTTP {st_msg}: thong_diep={d_msg.get('thong_diep')!r}, chi_tiet.msg={chi_tiet_msgs}",
        "400/422 với thông báo chi tiết tiếng Việt (không lẫn tiếng Anh của Pydantic)",
        "POST /api/don với kg='-5'",
        "Nhe",
        "UX / Lỗi tiếng Việt",
    )

    bc.luu_json("ket_qua_02.json")


if __name__ == "__main__":
    main()
