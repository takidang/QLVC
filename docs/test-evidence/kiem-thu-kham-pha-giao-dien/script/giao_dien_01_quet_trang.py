"""Mục 01: Quét mọi trang × 4 vai trò × 2 cỡ (1440×900 và 390×844) trên GIAO DIỆN PIXEL.

Kiểm tra từng route chính (từ App.tsx + menu trái thực tế):
- Màn trắng (vùng nội dung trống sau 4 s)
- pageerror, console.error, HTTP 5xx
- Thanh cuộn ngang bất thường
- Chữ/nút tràn khỏi khung hoặc bị cắt
- Phần tử chồng lên nhau, ảnh hỏng
Chụp ảnh vào kiem-thu-kham-pha/anh/ mỗi khi có lỗi.

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_01_quet_trang.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    VIEWPORT_DESKTOP,
    VIEWPORT_MOBILE,
    BaoCaoScript,
    cho_noi_dung_khong_trang,
    cho_yen,
    chup_anh,
    dang_nhap_api,
    dang_nhap_nhanh,
    dang_nhap_ui,
    kiem_bo_cuc_trang,
    lay_chuyen_mau,
    lay_don_mau,
    mo_khung_dang_nhap_pixel,
    mo_trang_moi,
    slug_an_toan,
    tao_context_pixel,
)


def lay_route_menu_trai(page) -> list[str]:
    try:
        hrefs = page.evaluate(
            """() => Array.from(document.querySelectorAll('aside.canh nav a[href], nav a[href]'))
                .map(a => a.getAttribute('href') || '')
                .filter(h => h.startsWith('/') && !h.startsWith('/dang-nhap'))"""
        )
        seen: list[str] = []
        for h in hrefs:
            if h not in seen:
                seen.append(h)
        return seen
    except Exception:
        return []


def quet_mot_trang(bc: BaoCaoScript, page, mon, ma: str, role: str, vp_ten: str, path: str) -> None:
    def chay():
        mon.reset()
        page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
        co_noi_dung, text_len, text_mau = cho_noi_dung_khong_trang(page, timeout_s=4.0)
        cho_yen(page, ms=400, network_timeout=4000)
        m = kiem_bo_cuc_trang(page)

        van_de: list[str] = []
        muc = "Nhẹ"

        if not co_noi_dung:
            van_de.append(f"Màn trắng/trống sau 4s (len={text_len}, mẫu={text_mau!r})")
            muc = "Nghiêm trọng"
        if mon.page_errors:
            van_de.append(f"pageerror={mon.page_errors[:2]}")
            muc = "Nghiêm trọng"
        if mon.http_5xx:
            van_de.append(f"HTTP 5xx={mon.http_5xx[:2]}")
            muc = "Nghiêm trọng"
        console_err = mon.loi_console_that(bo_qua_401=True)
        if console_err:
            van_de.append(f"console.error={console_err[:2]}")
            if muc == "Nhẹ":
                muc = "Vừa"
        if m["cuonNgang"]:
            van_de.append(f"Cuộn ngang sw={m['sw']}>vw={m['vw']}")
            if muc == "Nhẹ":
                muc = "Vừa"
        if m["tranViewport"]:
            van_de.append(f"Tràn khung={m['tranViewport'][:2]}")
            if muc == "Nhẹ":
                muc = "Vừa"
        if m["biCat"]:
            van_de.append(f"Chữ/nút bị cắt={m['biCat'][:2]}")
        if m["chongNhau"]:
            van_de.append(f"Chồng phần tử={m['chongNhau'][:2]}")
            if muc == "Nhẹ":
                muc = "Vừa"
        if m["anhLoi"]:
            van_de.append(f"Ảnh lỗi={m['anhLoi'][:2]}")
        if m["pxTai"] > 0:
            van_de.append(f"Còn {m['pxTai']} khung xương .px-tai chưa tắt")
            if muc == "Nhẹ":
                muc = "Vừa"

        if van_de:
            return False, " | ".join(van_de), muc
        return True, f"OK (vw={m['vw']}, sw={m['sw']}, text={m['mainTextLen']} ký tự, phongCach={m['phongCach']})", ""

    bc.chay_ca(
        ma=ma,
        ten=f"[{role}][{vp_ten}] {path}",
        fn=chay,
        page=page,
        muc="Vừa",
        tai_hien=f"Bật Pixel sáng -> đăng nhập {role} ở {vp_ten} -> mở {path}",
        mong_doi="Không màn trắng, không pageerror/console.error/5xx, không cuộn ngang, không tràn/cắt/chồng phần tử",
    )


def main() -> None:
    bc = BaoCaoScript(1, "Quét mọi trang × 4 vai trò × 2 cỡ (1440×900 & 390×844)", "ket_qua_01.json")

    # Lấy ID chuyến/đơn có sẵn qua API để quét cả trang chi tiết
    chuyen_dp_id = None
    don_dp_id = None
    chuyen_tx_id = None
    try:
        api_dp = dang_nhap_api("dieuphoi")
        c = lay_chuyen_mau(api_dp)
        if c:
            chuyen_dp_id = c["id"]
        d = lay_don_mau(api_dp)
        if d:
            don_dp_id = d["id"]
    except Exception as exc:
        print(f"  [CẢNH BÁO] Không lấy được ID mẫu điều phối: {exc}")

    try:
        api_tx = dang_nhap_api("taixe")
        st, r, _ = api_tx.raw("GET", "/api/toi/chuyen?nhom=can_lam&so_dong=5")
        if st == 200 and isinstance(r, dict) and r.get("du_lieu"):
            chuyen_tx_id = r["du_lieu"][0]["id"]
        else:
            st, r, _ = api_tx.raw("GET", "/api/toi/chuyen?nhom=da_xong&so_dong=5")
            if st == 200 and isinstance(r, dict) and r.get("du_lieu"):
                chuyen_tx_id = r["du_lieu"][0]["id"]
    except Exception as exc:
        print(f"  [CẢNH BÁO] Không lấy được ID chuyến tài xế: {exc}")

    routes_co_dinh: dict[str, list[str]] = {
        "quanly": [
            "/quan-ly/tong-quan",
            "/quan-ly/nguoi-dung",
            "/quan-ly/bang-gia",
            "/quan-ly/cau-hinh",
            "/quan-ly/cong-no",
            "/quan-ly/quyet-toan",
            "/dieu-phoi/chuyen",
            "/dieu-phoi/don",
            "/dieu-phoi/xe",
            "/dieu-phoi/tai-xe",
            "/dieu-phoi/khach-hang",
            "/dieu-phoi/nut",
            "/dieu-phoi/tuyen",
            "/tai-khoan",
            "/cai-dat",
        ]
        + ([f"/dieu-phoi/chuyen/{chuyen_dp_id}"] if chuyen_dp_id else []),
        "dieuphoi": [
            "/dieu-phoi/chuyen",
            "/dieu-phoi/don",
            "/dieu-phoi/xe",
            "/dieu-phoi/tai-xe",
            "/dieu-phoi/khach-hang",
            "/dieu-phoi/nut",
            "/dieu-phoi/tuyen",
            "/tai-khoan",
            "/cai-dat",
        ]
        + ([f"/dieu-phoi/chuyen/{chuyen_dp_id}"] if chuyen_dp_id else [])
        + ([f"/dieu-phoi/don/{don_dp_id}/phieu"] if don_dp_id else []),
        "ketoan": [
            "/ke-toan/tong-quan",
            "/ke-toan/tam-ung",
            "/ke-toan/quyet-toan",
            "/ke-toan/cong-no",
            "/ke-toan/chi-phi-xe",
            "/tai-khoan",
            "/cai-dat",
        ],
        "taixe": [
            "/tai-xe/chuyen",
            "/tai-khoan",
            "/cai-dat",
        ]
        + ([f"/tai-xe/chuyen/{chuyen_tx_id}"] if chuyen_tx_id else []),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # 1. Trang công khai /dang-nhap (màn logo + mở khung form) và /tra-cuu ở 2 cỡ
            for vp_ten, vp in [("1440x900", VIEWPORT_DESKTOP), ("390x844", VIEWPORT_MOBILE)]:
                ctx = tao_context_pixel(browser, viewport=vp)
                page, mon = mo_trang_moi(ctx)
                try:
                    quet_mot_trang(bc, page, mon, f"PUB_DN_{vp_ten}", "khach", vp_ten, "/dang-nhap")

                    def kiem_form_dn():
                        mon.reset()
                        mo_khung_dang_nhap_pixel(page, timeout_ms=6000)
                        cho_yen(page, ms=350, network_timeout=3000)
                        m = kiem_bo_cuc_trang(page)
                        van_de = []
                        if mon.page_errors:
                            van_de.append(f"pageerror={mon.page_errors[:2]}")
                        if m["cuonNgang"]:
                            van_de.append(f"Cuộn ngang sw={m['sw']}>vw={m['vw']}")
                        if m["tranViewport"]:
                            van_de.append(f"Tràn khung={m['tranViewport'][:2]}")
                        if m["chongNhau"]:
                            van_de.append(f"Chồng phần tử={m['chongNhau'][:2]}")
                        return (not van_de), (" | ".join(van_de) if van_de else "Khung đăng nhập Pixel hiển thị gọn"), "Vừa"

                    bc.chay_ca(
                        f"PUB_DN_FORM_{vp_ten}",
                        f"[khach][{vp_ten}] /dang-nhap sau khi bấm .dn-bam-logo",
                        kiem_form_dn,
                        page=page,
                        tai_hien=f"Mở /dang-nhap ở {vp_ten} -> bấm .dn-bam-logo",
                        mong_doi="Form đăng nhập mở gọn, không tràn khung hay chồng phần tử",
                    )

                    quet_mot_trang(bc, page, mon, f"PUB_TC_{vp_ten}", "khach", vp_ten, "/tra-cuu")
                finally:
                    ctx.close()

            # 2. Thử đăng nhập bằng UI Pixel thật 1 lần cho dieuphoi để chắc chắn luồng .dn-bam-logo chạy
            ctx_dn = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_dn, mon_dn = mo_trang_moi(ctx_dn)
            try:
                def test_dn_ui():
                    dang_nhap_ui(pg_dn, "dieuphoi")
                    pc = pg_dn.evaluate(
                        "() => ({ ls: localStorage.getItem('qlvc-phong-cach'), attr: document.documentElement.dataset.phongCach || '' })"
                    )
                    ok = "/dieu-phoi" in pg_dn.url and not mon_dn.page_errors and pc["ls"] == "pixel"
                    return ok, f"url={pg_dn.url}, phongCach={pc}, pageerror={mon_dn.page_errors}", "Nghiêm trọng"

                bc.chay_ca(
                    "LOGIN_PIXEL_UI",
                    "Đăng nhập dieuphoi qua giao diện Pixel (.dn-bam-logo -> điền -> Đăng nhập)",
                    test_dn_ui,
                    page=pg_dn,
                    tai_hien="Mở /dang-nhap -> bấm .dn-bam-logo -> điền dieuphoi/demo12345 -> Đăng nhập",
                    mong_doi="Đăng nhập thành công vào /dieu-phoi/chuyen với phong cách Pixel",
                )
            finally:
                ctx_dn.close()

            # 3. Quét toàn bộ route × 4 vai trò × 2 cỡ màn hình
            for role, ds_route in routes_co_dinh.items():
                for vp_ten, vp in [("1440x900", VIEWPORT_DESKTOP), ("390x844", VIEWPORT_MOBILE)]:
                    ctx = tao_context_pixel(browser, viewport=vp)
                    page, mon = mo_trang_moi(ctx)
                    try:
                        dang_nhap_nhanh(ctx, page, role)
                        # Hợp nhất thêm các link thấy trên menu trái thực tế (phòng có route mới ở nhánh Pixel)
                        menu_routes = lay_route_menu_trai(page)
                        tat_ca = list(ds_route)
                        for mr in menu_routes:
                            if mr not in tat_ca:
                                tat_ca.append(mr)
                        for idx, path in enumerate(tat_ca, 1):
                            ma = f"{role.upper()[:2]}_{vp_ten.split('x')[0]}_{idx:02d}_{slug_an_toan(path)[:18]}"
                            quet_mot_trang(bc, page, mon, ma, role, vp_ten, path)
                    except Exception as exc:
                        anh = chup_anh(page, f"m01_{role}_{vp_ten}_setup_err")
                        bc.ghi(
                            f"{role.upper()[:2]}_{vp_ten}_INIT",
                            f"Khởi tạo phiên {role} ở {vp_ten}",
                            False,
                            f"Không đăng nhập/quét được: {exc}",
                            muc="Nghiêm trọng",
                            anh=anh,
                        )
                    finally:
                        ctx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
