"""Mục 04: Kiểm thử Hộp thoại (Modal/Dialog) trên GIAO DIỆN PIXEL.

Các kịch bản:
1. Mở rồi đóng bằng Escape, bấm ra ngoài (.nen-mo), nút Hủy/Thôi, nút × (nếu có)
2. Focus trap: Tab xoay vòng có thoát ra khỏi hộp thoại vào menu/nền không
3. Mở–đóng 10 lần liên tiếp rất nhanh (có kẹt lớp mờ hay lỗi JS không)
4. Cuộn nền khi hộp thoại đang mở (background scroll lock)
5. Hộp thoại trên 390×844 có bị cắt mất nút Lưu / không cuộn tới được không
6. Hai lớp nổi / hộp chồng nhau (ví dụ mở hộp thoại khi menu/chuông mở hoặc hộp lồng hộp)

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_04_hop_thoai.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    VIEWPORT_DESKTOP,
    VIEWPORT_MOBILE,
    BaoCaoScript,
    cho_yen,
    dang_nhap_nhanh,
    mo_trang_moi,
    tao_context_pixel,
)


def hop_thoai_dang_mo(page: Page) -> bool:
    return page.evaluate(
        """() => {
            const el = document.querySelector('form.hop-thoai, .hop-thoai, [role="dialog"]');
            if (!el) return false;
            const st = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 10 && r.height > 10;
        }"""
    )


def dong_hop_nhanh(page: Page) -> None:
    if not hop_thoai_dang_mo(page):
        return
    for sel in (
        '.hop-thoai button[type="button"]:has-text("Hủy")',
        '.hop-thoai button[type="button"]:has-text("Thôi")',
        '.hop-thoai button[type="button"]:has-text("Đóng")',
    ):
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            loc.first.click(timeout=2500)
            page.wait_for_timeout(150)
            return
    page.mouse.click(8, 8)
    page.wait_for_timeout(150)


def main() -> None:
    bc = BaoCaoScript(4, "Hộp thoại (Escape, bấm ngoài, focus trap, mở-đóng nhanh, cuộn nền, 390px, chồng hộp)", "ket_qua_04.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =================================================================
            # DESKTOP 1440x900
            # =================================================================
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx)
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")

                # 4.1 Escape đóng hộp thoại trên 3 màn (Đơn, Chuyến, Xe)
                def test_escape():
                    mon.reset()
                    khong_dong = []
                    for path, nut in [
                        ("/dieu-phoi/don", "Tạo đơn"),
                        ("/dieu-phoi/chuyen", "Lập chuyến"),
                        ("/dieu-phoi/xe", "Thêm xe"),
                    ]:
                        page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(page, ms=350)
                        page.locator(f'button:has-text("{nut}")').first.click()
                        page.locator(".hop-thoai").first.wait_for(state="visible", timeout=5000)
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(300)
                        if hop_thoai_dang_mo(page):
                            khong_dong.append(f"{nut} ({path})")
                            dong_hop_nhanh(page)
                    if khong_dong:
                        return False, f"Nhấn Escape KHÔNG đóng được hộp thoại: {khong_dong}", "Vừa"
                    return True, "Nhấn Escape đóng gọn cả 3 hộp thoại (Tạo đơn, Lập chuyến, Thêm xe)", ""

                bc.chay_ca(
                    "HT01_ESCAPE",
                    "Nhấn phím Escape đóng hộp thoại (Tạo đơn, Lập chuyến, Thêm xe)",
                    test_escape,
                    page=page,
                    tai_hien="Mở hộp thoại Tạo đơn / Lập chuyến / Thêm xe -> nhấn phím Escape",
                    mong_doi="Hộp thoại đóng ngay khi nhấn Escape",
                )

                # 4.2 Bấm ra ngoài (.nen-mo), nút Hủy, và kiểm nút ×
                def test_bam_ngoai_huy_x():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/xe", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=350)

                    # Bấm ngoài (.nen-mo ở góc trên trái 10,10)
                    page.locator('button:has-text("Thêm xe")').first.click()
                    page.locator(".hop-thoai").first.wait_for(state="visible", timeout=5000)
                    page.mouse.click(10, 10)
                    page.wait_for_timeout(300)
                    dong_ngoai = not hop_thoai_dang_mo(page)
                    if not dong_ngoai:
                        dong_hop_nhanh(page)

                    # Bấm nút Hủy
                    page.locator('button:has-text("Thêm xe")').first.click()
                    page.locator(".hop-thoai").first.wait_for(state="visible", timeout=5000)
                    page.locator('.hop-thoai button[type="button"]:has-text("Hủy")').first.click()
                    page.wait_for_timeout(300)
                    dong_huy = not hop_thoai_dang_mo(page)

                    # Kiểm có nút × đóng hộp thoại không
                    page.locator('button:has-text("Thêm xe")').first.click()
                    page.locator(".hop-thoai").first.wait_for(state="visible", timeout=5000)
                    nut_x = page.locator(
                        '.hop-thoai button:has-text("×"), .hop-thoai button:has-text("✕"), .hop-thoai button[aria-label*="Đóng"]'
                    )
                    co_nut_x = nut_x.count() > 0 and nut_x.first.is_visible()
                    dong_x = False
                    if co_nut_x:
                        nut_x.first.click()
                        page.wait_for_timeout(300)
                        dong_x = not hop_thoai_dang_mo(page)
                    else:
                        dong_hop_nhanh(page)

                    van_de = []
                    if not dong_ngoai:
                        van_de.append("Bấm ra ngoài (.nen-mo) không đóng hộp thoại")
                    if not dong_huy:
                        van_de.append("Bấm nút Hủy không đóng hộp thoại")
                    if co_nut_x and not dong_x:
                        van_de.append("Có nút × nhưng bấm không đóng hộp thoại")
                    return (
                        not van_de,
                        " | ".join(van_de)
                        if van_de
                        else f"Bấm ngoài={dong_ngoai}, Hủy={dong_huy}, nút ×={'có & đóng OK' if co_nut_x else 'không có nút × riêng'}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "HT02_NGOAI_HUY_X",
                    "Đóng hộp thoại bằng bấm ngoài, nút Hủy, và kiểm nút ×",
                    test_bam_ngoai_huy_x,
                    page=page,
                    tai_hien="Mở Thêm xe -> thử bấm góc (10,10) ngoài hộp, bấm Hủy, kiểm nút ×",
                    mong_doi="Các cách đóng đều đóng hộp thoại gọn gàng",
                )

                # 4.3 Focus trap: Tab xoay vòng có thoát ra khỏi hộp thoại không
                def test_focus_trap():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/khach-hang", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=350)
                    page.locator('button:has-text("Thêm khách hàng")').first.click()
                    page.locator(".hop-thoai").first.wait_for(state="visible", timeout=5000)
                    # Focus vào ô đầu tiên trong hộp thoại
                    page.locator(".hop-thoai input").first.focus()
                    thoat_ra = []
                    for buoc in range(20):
                        page.keyboard.press("Tab")
                        info = page.evaluate(
                            """() => {
                                const a = document.activeElement;
                                const hop = document.querySelector('.hop-thoai, [role="dialog"]');
                                if (!a || !hop) return { trong: false, moTa: 'null' };
                                return {
                                    trong: hop.contains(a),
                                    moTa: `${a.tagName.toLowerCase()}.${(a.className || '').toString().slice(0,25)}(${(a.innerText || a.getAttribute('aria-label') || '').trim().slice(0,25)})`
                                };
                            }"""
                        )
                        if not info["trong"]:
                            thoat_ra.append(f"Tab #{buoc + 1} -> {info['moTa']}")
                            if len(thoat_ra) >= 3:
                                break
                    dong_hop_nhanh(page)
                    if thoat_ra:
                        return False, f"KHÔNG CÓ FOCUS TRAP: nhấn Tab thoát khỏi hộp thoại ra nền: {thoat_ra}", "Vừa"
                    return True, "Tab 20 lần vẫn giữ focus gọn trong hộp thoại", ""

                bc.chay_ca(
                    "HT03_FOCUS_TRAP",
                    "Focus trap trong hộp thoại: nhấn Tab 20 lần không thoát ra nền",
                    test_focus_trap,
                    page=page,
                    tai_hien="Mở Thêm khách hàng -> focus ô đầu -> nhấn Tab liên tiếp 20 lần",
                    mong_doi="Focus xoay vòng bên trong hộp thoại, không nhảy sang menu trái/thanh trên",
                )

                # 4.4 Mở–đóng 10 lần liên tiếp rất nhanh
                def test_mo_dong_10_lan():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=350)
                    for i in range(10):
                        page.locator('button:has-text("Tạo đơn")').first.click(timeout=3000)
                        page.locator("form.hop-thoai").first.wait_for(state="visible", timeout=3000)
                        page.locator('form.hop-thoai button[type="button"]:has-text("Hủy")').first.click(timeout=3000)
                        page.wait_for_timeout(40)
                    page.wait_for_timeout(400)
                    con_mo = hop_thoai_dang_mo(page)
                    so_nen_mo = page.locator(".nen-mo").count()
                    van_de = []
                    if con_mo or so_nen_mo > 0:
                        van_de.append(f"Còn kẹt hộp thoại/lớp mờ sau 10 lần (con_mo={con_mo}, .nen-mo={so_nen_mo})")
                    if mon.page_errors:
                        van_de.append(f"pageerror={mon.page_errors[:2]}")
                    if mon.http_5xx:
                        van_de.append(f"5xx={mon.http_5xx[:2]}")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else "Mở–đóng 10 lần liên tiếp sạch sẽ, không kẹt .nen-mo, không lỗi JS",
                        "Vừa",
                    )

                bc.chay_ca(
                    "HT04_MO_DONG_10_LAN",
                    "Mở–đóng hộp thoại Tạo đơn 10 lần liên tiếp rất nhanh",
                    test_mo_dong_10_lan,
                    page=page,
                    tai_hien="Trên /dieu-phoi/don, bấm Tạo đơn -> Hủy lặp lại 10 lần liên tiếp",
                    mong_doi="Không kẹt lớp mờ .nen-mo, không lỗi console/JS/5xx",
                )

                # 4.5 Cuộn nền khi hộp thoại đang mở
                def test_cuon_nen():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    # Bảo đảm trang có thể cuộn (nếu trang ngắn hơn 900px thì thu chiều cao tạm)
                    co_the_cuon = page.evaluate("() => document.documentElement.scrollHeight > window.innerHeight + 50")
                    if not co_the_cuon:
                        page.set_viewport_size({"width": 1440, "height": 520})
                        page.wait_for_timeout(200)
                    page.evaluate("() => window.scrollTo(0, 0)")
                    page.locator('button:has-text("Tạo đơn")').first.click()
                    page.locator("form.hop-thoai").first.wait_for(state="visible", timeout=5000)
                    # Di chuột ra vùng lớp mờ bên trái hộp thoại rồi lăn chuột xuống
                    page.mouse.move(25, 250)
                    page.mouse.wheel(0, 800)
                    page.wait_for_timeout(350)
                    scroll_y = page.evaluate("() => Math.round(window.scrollY)")
                    body_overflow = page.evaluate("() => getComputedStyle(document.body).overflow")
                    dong_hop_nhanh(page)
                    page.set_viewport_size(VIEWPORT_DESKTOP)
                    if scroll_y > 10:
                        return (
                            False,
                            f"Nền phía sau vẫn cuộn được khi hộp thoại mở (window.scrollY={scroll_y}px, body.overflow={body_overflow})",
                            "Nhẹ",
                        )
                    return True, f"Nền không bị cuộn khi hộp mở (scrollY={scroll_y}, body.overflow={body_overflow})", ""

                bc.chay_ca(
                    "HT05_CUON_NEN",
                    "Kiểm khóa cuộn nền (background scroll) khi hộp thoại đang mở",
                    test_cuon_nen,
                    page=page,
                    tai_hien="Mở hộp thoại Tạo đơn -> đưa chuột ra vùng nền mờ -> cuộn bánh xe chuột xuống",
                    mong_doi="Trang nền phía sau không bị cuộn theo",
                )

                # 4.6 Hai lớp nổi / hai hộp chồng nhau (Menu tài khoản hoặc Chuông mở + mở Hộp thoại; hoặc Đơn thất bại -> Ghép lại + Hủy)
                def test_chong_hop():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    # Mở Chuông thông báo trước rồi bấm Tạo đơn -> kiểm xem Chuông có tự đóng hay đè lên trên hộp thoại không
                    chuong = page.locator("details.chuong summary").first
                    if chuong.count() > 0 and chuong.is_visible():
                        chuong.click()
                        page.wait_for_timeout(200)
                    page.locator('button:has-text("Tạo đơn")').first.click()
                    page.locator("form.hop-thoai").first.wait_for(state="visible", timeout=5000)
                    page.wait_for_timeout(250)
                    info = page.evaluate(
                        """() => {
                            const chuongMo = !!document.querySelector('details.chuong[open]');
                            const hop = document.querySelector('.nen-mo');
                            const chuongHop = document.querySelector('.chuong-hop');
                            const zHop = hop ? parseInt(getComputedStyle(hop).zIndex || '0', 10) : 0;
                            const zChuong = chuongHop ? parseInt(getComputedStyle(chuongHop).zIndex || '0', 10) : 0;
                            return { chuongMo, zHop, zChuong };
                        }"""
                    )
                    dong_hop_nhanh(page)
                    if info["chuongMo"] and info["zChuong"] >= info["zHop"]:
                        return False, f"Hộp chuông vẫn mở và đè lên trên hộp thoại: {info}", "Vừa"
                    return True, f"Kiểm chồng lớp Chuông + Hộp thoại OK ({info})", ""

                bc.chay_ca(
                    "HT06_CHONG_HOP",
                    "Hai lớp nổi chồng nhau: mở Chuông thông báo rồi mở hộp thoại Tạo đơn",
                    test_chong_hop,
                    page=page,
                    tai_hien="Bấm mở Chuông thông báo -> bấm Tạo đơn",
                    mong_doi="Chuông tự đóng hoặc nằm dưới lớp mờ hộp thoại, không đè che hộp thoại",
                )
            finally:
                ctx.close()

            # =================================================================
            # MOBILE 390x844: Kiểm hộp thoại có bị cắt mất nút Lưu không
            # =================================================================
            ctx_mb = tao_context_pixel(browser, viewport=VIEWPORT_MOBILE)
            page_mb, mon_mb = mo_trang_moi(ctx_mb)
            try:
                dang_nhap_nhanh(ctx_mb, page_mb, "dieuphoi")

                for idx, (path, nut_mo, nut_luu) in enumerate(
                    [
                        ("/dieu-phoi/don", "Tạo đơn", "Lưu đơn"),
                        ("/dieu-phoi/chuyen", "Lập chuyến", "Lập chuyến"),
                        ("/dieu-phoi/xe", "Thêm xe", "Lưu"),
                        ("/dieu-phoi/tuyen", "Thêm tuyến", "Lưu"),
                    ],
                    1,
                ):
                    def make_test_mobile(p_url=path, n_mo=nut_mo, n_luu=nut_luu):
                        def chay():
                            mon_mb.reset()
                            page_mb.goto(f"{BASE_FE}{p_url}", wait_until="domcontentloaded", timeout=15000)
                            cho_yen(page_mb, ms=400)
                            page_mb.locator(f'button:has-text("{n_mo}")').first.click()
                            form = page_mb.locator("form.hop-thoai").first
                            form.wait_for(state="visible", timeout=5000)
                            page_mb.wait_for_timeout(250)

                            # Cuộn hộp thoại xuống đáy (nếu nó có thể cuộn) rồi đo vị trí nút Lưu
                            kq = page_mb.evaluate(
                                """(tenNut) => {
                                    const nen = document.querySelector('.nen-mo');
                                    const hop = document.querySelector('form.hop-thoai');
                                    if (!hop) return { ok: false, lyDo: 'Không thấy form.hop-thoai' };
                                    // Cuộn cả .nen-mo lẫn form.hop-thoai xuống đáy
                                    if (nen) nen.scrollTop = nen.scrollHeight;
                                    hop.scrollTop = hop.scrollHeight;
                                    const btns = Array.from(hop.querySelectorAll('button')).filter(b => (b.innerText || '').includes(tenNut));
                                    const btn = btns[btns.length - 1];
                                    if (!btn) return { ok: false, lyDo: `Không tìm thấy nút "${tenNut}"` };
                                    btn.scrollIntoView({ block: 'nearest' });
                                    const r = btn.getBoundingClientRect();
                                    const hr = hop.getBoundingClientRect();
                                    const vw = window.innerWidth;
                                    const vh = window.innerHeight;
                                    const biCatDuoi = r.bottom > vh + 2;
                                    const biCatPhai = r.right > vw + 2;
                                    const hopTranNgang = hr.width > vw + 2 || hop.scrollWidth > hop.clientWidth + 6;
                                    return {
                                        ok: !biCatDuoi && !biCatPhai && !hopTranNgang,
                                        r: { top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right) },
                                        hr: { width: Math.round(hr.width), height: Math.round(hr.height) },
                                        vw, vh, biCatDuoi, biCatPhai, hopTranNgang,
                                    };
                                }""",
                                n_luu,
                            )
                            dong_hop_nhanh(page_mb)
                            if not kq.get("ok"):
                                return False, f"Hộp thoại '{n_mo}' ở 390px bị cắt/tràn: {kq}", "Vừa"
                            return True, f"Nút '{n_luu}' chạm được trong viewport 390×844 ({kq['r']})", ""
                        return chay

                    bc.chay_ca(
                        f"HT07_MOBILE_{idx}_{nut_mo[:6].upper()}",
                        f"Hộp thoại '{nut_mo}' ở 390×844: nút '{nut_luu}' không bị cắt",
                        make_test_mobile(),
                        page=page_mb,
                        tai_hien=f"Viewport 390×844 -> mở {path} -> bấm '{nut_mo}' -> cuộn tới nút '{nut_luu}'",
                        mong_doi=f"Hộp thoại vừa chiều ngang 390px, cuộn được tới nút '{nut_luu}' mà không bị cắt",
                    )
            finally:
                ctx_mb.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
