"""Mục 08: Phân quyền giao diện & quản lý phiên trên GIAO DIỆN PIXEL.

Kịch bản:
1. Đăng nhập taixe -> mở thẳng URL của quanly, dieuphoi, ketoan -> phải chuyển về /tai-xe/...
2. Đăng nhập dieuphoi -> mở thẳng URL của quanly, ketoan, taixe -> phải chuyển về /dieu-phoi/...
3. Đăng nhập ketoan -> mở thẳng URL của quanly, dieuphoi, taixe -> phải chuyển về /ke-toan/...
4. Đăng nhập quanly -> kiểm được vào /quan-ly/* & /dieu-phoi/*, bị chặn /ke-toan/* & /tai-xe/*,
   và trên /quan-ly/cong-no & /quan-ly/quyet-toan chỉ xem (ẩn nút ghi tiền)
5. Hết phiên (xóa cookie rồi bấm tiếp trên menu / tải lại) -> phải về /dang-nhap gọn, không màn trắng/crash
6. Đăng xuất qua Menu tài khoản rồi bấm nút Back trình duyệt -> KHÔNG được lộ trang cũ

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_08_phan_quyen_phien.py
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
    cho_yen,
    dang_nhap_nhanh,
    dang_nhap_ui,
    mo_trang_moi,
    tao_context_pixel,
)


def main() -> None:
    bc = BaoCaoScript(8, "Phân quyền giao diện, hết phiên (xóa cookie) & Đăng xuất rồi Back", "ket_qua_08.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # 8.1 Tài xế mở thẳng URL của các vai trò khác
            ctx_tx = tao_context_pixel(browser, viewport=VIEWPORT_MOBILE)
            pg_tx, mon_tx = mo_trang_moi(ctx_tx)
            try:
                dang_nhap_nhanh(ctx_tx, pg_tx, "taixe")

                def test_taixe_trai_quyen():
                    mon_tx.reset()
                    urls_cam = [
                        "/quan-ly/tong-quan",
                        "/quan-ly/nguoi-dung",
                        "/quan-ly/bang-gia",
                        "/quan-ly/cau-hinh",
                        "/dieu-phoi/don",
                        "/dieu-phoi/chuyen",
                        "/dieu-phoi/xe",
                        "/ke-toan/tam-ung",
                        "/ke-toan/quyet-toan",
                        "/ke-toan/cong-no",
                    ]
                    lot = []
                    for u in urls_cam:
                        pg_tx.goto(f"{BASE_FE}{u}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(pg_tx, ms=250, network_timeout=3000)
                        if "/tai-xe" not in pg_tx.url:
                            lot.append((u, pg_tx.url.replace(BASE_FE, "")))
                    if lot or mon_tx.page_errors:
                        return False, f"Lọt URL trái quyền={lot}, pageerror={mon_tx.page_errors[:2]}", "Nghiêm trọng"
                    return True, f"Cả {len(urls_cam)} URL vai trò khác đều chuyển hướng về /tai-xe/...", ""

                bc.chay_ca(
                    "PQ01_TAIXE_URL_KHAC",
                    "Tài xế mở thẳng 10 URL của Quản lý / Điều phối / Kế toán",
                    test_taixe_trai_quyen,
                    page=pg_tx,
                    muc="Nghiêm trọng",
                    tai_hien="Đăng nhập taixe -> mở thẳng /quan-ly/*, /dieu-phoi/*, /ke-toan/*",
                    mong_doi="Mọi URL vai trò khác đều redirect về /tai-xe/chuyen, không lộ dữ liệu",
                )
            finally:
                ctx_tx.close()

            # 8.2 Điều phối mở thẳng URL của Quản lý / Kế toán / Tài xế
            ctx_dp = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_dp, mon_dp = mo_trang_moi(ctx_dp)
            try:
                dang_nhap_nhanh(ctx_dp, pg_dp, "dieuphoi")

                def test_dieuphoi_trai_quyen():
                    mon_dp.reset()
                    urls_cam = [
                        "/quan-ly/tong-quan",
                        "/quan-ly/nguoi-dung",
                        "/quan-ly/bang-gia",
                        "/quan-ly/cau-hinh",
                        "/ke-toan/tam-ung",
                        "/ke-toan/quyet-toan",
                        "/ke-toan/cong-no",
                        "/ke-toan/chi-phi-xe",
                        "/tai-xe/chuyen",
                    ]
                    lot = []
                    for u in urls_cam:
                        pg_dp.goto(f"{BASE_FE}{u}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(pg_dp, ms=250, network_timeout=3000)
                        if "/dieu-phoi" not in pg_dp.url:
                            lot.append((u, pg_dp.url.replace(BASE_FE, "")))
                    if lot or mon_dp.page_errors:
                        return False, f"Lọt URL trái quyền={lot}, pageerror={mon_dp.page_errors[:2]}", "Nghiêm trọng"
                    return True, f"Cả {len(urls_cam)} URL trái quyền đều redirect về /dieu-phoi/...", ""

                bc.chay_ca(
                    "PQ02_DIEUPHOI_URL_KHAC",
                    "Điều phối mở thẳng 9 URL của Quản lý / Kế toán / Tài xế",
                    test_dieuphoi_trai_quyen,
                    page=pg_dp,
                    muc="Nghiêm trọng",
                    tai_hien="Đăng nhập dieuphoi -> mở thẳng /quan-ly/*, /ke-toan/*, /tai-xe/chuyen",
                    mong_doi="Mọi URL trái quyền đều redirect về /dieu-phoi/chuyen",
                )
            finally:
                ctx_dp.close()

            # 8.3 Kế toán mở thẳng URL của Quản lý / Điều phối / Tài xế
            ctx_kt = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_kt, mon_kt = mo_trang_moi(ctx_kt)
            try:
                dang_nhap_nhanh(ctx_kt, pg_kt, "ketoan")

                def test_ketoan_trai_quyen():
                    mon_kt.reset()
                    urls_cam = [
                        "/quan-ly/nguoi-dung",
                        "/quan-ly/bang-gia",
                        "/quan-ly/cau-hinh",
                        "/dieu-phoi/don",
                        "/dieu-phoi/chuyen",
                        "/dieu-phoi/xe",
                        "/tai-xe/chuyen",
                    ]
                    lot = []
                    for u in urls_cam:
                        pg_kt.goto(f"{BASE_FE}{u}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(pg_kt, ms=250, network_timeout=3000)
                        if "/ke-toan" not in pg_kt.url:
                            lot.append((u, pg_kt.url.replace(BASE_FE, "")))
                    if lot or mon_kt.page_errors:
                        return False, f"Lọt URL trái quyền={lot}, pageerror={mon_kt.page_errors[:2]}", "Nghiêm trọng"
                    return True, f"Cả {len(urls_cam)} URL trái quyền đều redirect về /ke-toan/...", ""

                bc.chay_ca(
                    "PQ03_KETOAN_URL_KHAC",
                    "Kế toán mở thẳng 7 URL của Quản lý / Điều phối / Tài xế",
                    test_ketoan_trai_quyen,
                    page=pg_kt,
                    muc="Nghiêm trọng",
                    tai_hien="Đăng nhập ketoan -> mở thẳng /quan-ly/*, /dieu-phoi/*, /tai-xe/chuyen",
                    mong_doi="Mọi URL trái quyền đều redirect về /ke-toan/tong-quan",
                )
            finally:
                ctx_kt.close()

            # 8.4 Quản lý: bị chặn /ke-toan/* và /tai-xe/*, đồng thời /quan-ly/cong-no & /quan-ly/quyet-toan chỉ xem
            ctx_ql = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_ql, mon_ql = mo_trang_moi(ctx_ql)
            try:
                dang_nhap_nhanh(ctx_ql, pg_ql, "quanly")

                def test_quanly_quyen():
                    mon_ql.reset()
                    lot = []
                    for u in ["/ke-toan/tam-ung", "/ke-toan/quyet-toan", "/ke-toan/cong-no", "/tai-xe/chuyen"]:
                        pg_ql.goto(f"{BASE_FE}{u}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(pg_ql, ms=250, network_timeout=3000)
                        if "/quan-ly" not in pg_ql.url:
                            lot.append((u, pg_ql.url.replace(BASE_FE, "")))

                    # Kiểm chỉ xem trên /quan-ly/cong-no
                    pg_ql.goto(f"{BASE_FE}/quan-ly/cong-no", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_ql, ms=400)
                    nut_ghi_cn = pg_ql.locator('button:has-text("Đánh dấu đã thu")').count()

                    # Kiểm chỉ xem trên /quan-ly/quyet-toan
                    pg_ql.goto(f"{BASE_FE}/quan-ly/quyet-toan", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_ql, ms=400)
                    if pg_ql.locator(".qt-ds ul button").count() > 0:
                        pg_ql.locator(".qt-ds ul button").first.click()
                        cho_yen(pg_ql, ms=400)
                    nut_ghi_qt = pg_ql.locator('button:has-text("Quyết toán")').count()

                    van_de = []
                    if lot:
                        van_de.append(f"Quản lý lọt sang trang ngoài quyền: {lot}")
                    if nut_ghi_cn > 0:
                        van_de.append("Quản lý thấy nút 'Đánh dấu đã thu' ở /quan-ly/cong-no (phải chỉ xem)")
                    if nut_ghi_qt > 0:
                        van_de.append("Quản lý thấy nút 'Quyết toán' ở /quan-ly/quyet-toan (phải chỉ xem)")
                    return (
                        not van_de and not mon_ql.page_errors,
                        " | ".join(van_de) if van_de else "Quản lý bị chặn /ke-toan/*, /tai-xe/* và chỉ xem Công nợ/Quyết toán",
                        "Nghiêm trọng",
                    )

                bc.chay_ca(
                    "PQ04_QUANLY_CHIXEM",
                    "Quản lý bị chặn /ke-toan/* & /tai-xe/*, và chỉ xem ở /quan-ly/cong-no, /quyet-toan",
                    test_quanly_quyen,
                    page=pg_ql,
                    muc="Nghiêm trọng",
                    tai_hien="Đăng nhập quanly -> mở /ke-toan/*, /tai-xe/* -> kiểm nút ghi ở /quan-ly/cong-no & /quyet-toan",
                    mong_doi="Chặn /ke-toan/* và /tai-xe/*, ẩn toàn bộ nút ghi tiền ở Công nợ & Quyết toán",
                )
            finally:
                ctx_ql.close()

            # 8.5 Hết phiên: xóa cookie rồi bấm tiếp trên menu (SPA) VÀ tải lại trang
            ctx_het = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_het, mon_het = mo_trang_moi(ctx_het)
            try:
                dang_nhap_ui(pg_het, "dieuphoi")

                def test_het_phien_xoa_cookie():
                    mon_het.reset()
                    pg_het.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_het, ms=400)
                    # Xóa sạch cookie phiên
                    ctx_het.clear_cookies()
                    # Bấm tiếp sang mục Đơn hàng trên menu trái (SPA navigation sau khi cookie đã hết hạn)
                    link_don = pg_het.locator('aside.canh nav a[href="/dieu-phoi/don"]').first
                    if link_don.count() > 0:
                        link_don.click()
                    else:
                        pg_het.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_het, ms=900, network_timeout=4000)
                    url_sau_bam = pg_het.url.replace(BASE_FE, "")
                    ve_dn_khi_bam = "/dang-nhap" in url_sau_bam

                    # Thử F5 (reload) sau khi hết cookie -> chắc chắn phải về /dang-nhap
                    pg_het.reload(wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_het, ms=600, network_timeout=4000)
                    url_sau_f5 = pg_het.url.replace(BASE_FE, "")
                    ve_dn_sau_f5 = "/dang-nhap" in url_sau_f5

                    van_de = []
                    if not ve_dn_khi_bam:
                        van_de.append(
                            f"Hết cookie nhưng bấm menu tiếp KHÔNG tự đưa về /dang-nhap (vẫn kẹt ở {url_sau_bam}, chỉ báo lỗi/trống)"
                        )
                    if not ve_dn_sau_f5:
                        van_de.append(f"Sau khi F5 khi không có cookie vẫn không về /dang-nhap ({url_sau_f5})")
                    if mon_het.page_errors:
                        van_de.append(f"pageerror={mon_het.page_errors[:2]}")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else "Hết cookie bấm menu & F5 đều tự chuyển gọn về /dang-nhap",
                        "Vừa" if ve_dn_sau_f5 else "Nghiêm trọng",
                    )

                bc.chay_ca(
                    "PQ05_HET_PHIEN_COOKIE",
                    "Hết phiên (xóa cookie) rồi bấm menu tiếp và F5: phải tự về /dang-nhap gọn",
                    test_het_phien_xoa_cookie,
                    page=pg_het,
                    tai_hien="Đăng nhập dieuphoi -> clear_cookies() -> bấm menu sang /dieu-phoi/don -> F5",
                    mong_doi="Nhận 401 thì chuyển gọn về /dang-nhap, không kẹt trang cũ/màn trống",
                )
            finally:
                ctx_het.close()

            # 8.6 Đăng xuất rồi bấm Back -> không được lộ trang cũ
            ctx_dx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            pg_dx, mon_dx = mo_trang_moi(ctx_dx)
            try:
                dang_nhap_ui(pg_dx, "dieuphoi")

                def test_dang_xuat_roi_back():
                    mon_dx.reset()
                    pg_dx.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_dx, ms=350)
                    pg_dx.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(pg_dx, ms=350)

                    # Mở Menu tài khoản -> bấm Đăng xuất
                    pg_dx.locator("details.menu-tk summary").first.click()
                    pg_dx.locator('details.menu-tk button:has-text("Đăng xuất")').first.click()
                    pg_dx.wait_for_url(lambda u: "/dang-nhap" in u, timeout=10000)
                    cho_yen(pg_dx, ms=400)

                    # Bấm Back 2 lần liên tiếp
                    lo_trang = []
                    for lan in (1, 2):
                        pg_dx.go_back(wait_until="domcontentloaded", timeout=10000)
                        cho_yen(pg_dx, ms=400, network_timeout=3000)
                        u = pg_dx.url.replace(BASE_FE, "")
                        co_bang = pg_dx.locator("table").count()
                        if "/dang-nhap" not in u or co_bang > 0:
                            lo_trang.append(f"Back #{lan}: url={u}, tables={co_bang}")
                    if lo_trang or mon_dx.page_errors:
                        return False, f"Đăng xuất xong bấm Back bị lộ trang cũ: {lo_trang}, pageerror={mon_dx.page_errors[:2]}", "Nghiêm trọng"
                    return True, "Đăng xuất rồi bấm Back 2 lần đều ở lại /dang-nhap, không lộ dữ liệu cũ", ""

                bc.chay_ca(
                    "PQ06_DANG_XUAT_BACK",
                    "Đăng xuất rồi bấm nút Back trình duyệt: không lộ trang nội bộ cũ",
                    test_dang_xuat_roi_back,
                    page=pg_dx,
                    muc="Nghiêm trọng",
                    tai_hien="Đăng nhập -> mở Chuyến -> mở Đơn -> Đăng xuất -> bấm Back 2 lần",
                    mong_doi="Giữ ở /dang-nhap, không hiện lại bảng đơn hàng hay chuyến cũ",
                )
            finally:
                ctx_dx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
