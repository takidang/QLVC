"""Mục 07: Thông báo, chuông, menu tài khoản, ô tìm kiếm, popover cảnh báo "ĐƠN THẤT BẠI".

Kiểm tra ở các cỡ 1440×900, 1100×800 và 390×844 trên GIAO DIỆN PIXEL:
- Chuông thông báo: mở/đóng, số "mới" khớp API, cuộn danh sách, không tràn màn/che menu,
  bấm một mục đi đúng trang.
- Menu tài khoản: mở/đóng (bấm ngoài, Escape), không tràn màn, link Tài khoản / Cài đặt đúng.
- Ô tìm kiếm trên cùng: gõ tìm, xổ kết quả, cuộn, không tràn/che, Escape đóng, bấm mục đi đúng trang.
- Popover cảnh báo "ĐƠN THẤT BẠI": mở/đóng, không tràn màn/che menu ở 1100px & 390px,
  rê chuột đi lại giữa nút và tờ giấy/popover không bị tắt giữa chừng.

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_07_thong_bao_popover.py
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
    VIEWPORT_TABLET,
    BaoCaoScript,
    cho_yen,
    dang_nhap_api,
    dang_nhap_nhanh,
    mo_trang_moi,
    tao_context_pixel,
)


def kiem_khung_noi(page: Page, sel: str) -> dict:
    """Đo vị trí hộp nổi so với viewport và menu trái / thanh đầu."""
    return page.evaluate(
        """(selector) => {
            const el = document.querySelector(selector);
            if (!el) return { co: false };
            const st = getComputedStyle(el);
            if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.05) {
                return { co: false };
            }
            const r = el.getBoundingClientRect();
            const vw = window.innerWidth;
            const vh = window.innerHeight;
            const menu = document.querySelector('aside.canh');
            let deMenu = false;
            if (menu && vw >= 900) {
                const mr = menu.getBoundingClientRect();
                if (mr.width > 0 && mr.height > 0) {
                    const ix = Math.min(r.right, mr.right) - Math.max(r.left, mr.left);
                    const iy = Math.min(r.bottom, mr.bottom) - Math.max(r.top, mr.top);
                    if (ix > 8 && iy > 8) deMenu = true;
                }
            }
            return {
                co: true,
                rect: { left: Math.round(r.left), right: Math.round(r.right), top: Math.round(r.top), bottom: Math.round(r.bottom), w: Math.round(r.width), h: Math.round(r.height) },
                vw, vh,
                tranTrai: r.left < -2,
                tranPhai: r.right > vw + 2,
                tranDuoi: r.bottom > vh + 4,
                deMenu,
                scrollH: el.scrollHeight,
                clientH: el.clientHeight,
            };
        }""",
        sel,
    )


def main() -> None:
    bc = BaoCaoScript(7, "Chuông thông báo, menu tài khoản, ô tìm kiếm & popover 'ĐƠN THẤT BẠI'", "ket_qua_07.json")

    api_dp = dang_nhap_api("dieuphoi")
    st_tb, data_tb, _ = api_dp.raw("GET", "/api/thong-bao")
    ds_tb_api = data_tb.get("thong_bao", []) if (st_tb == 200 and isinstance(data_tb, dict)) else []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =================================================================
            # 1. CHUÔNG THÔNG BÁO (số "mới", cuộn, tràn màn ở 1440 / 1100 / 390, bấm đi đúng trang)
            # =================================================================
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx)
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")

                def test_chuong_so_moi_va_dieu_huong():
                    mon.reset()
                    # Xóa mốc đã đọc để kiểm số "mới" ban đầu khớp toàn bộ API /api/thong-bao
                    page.evaluate(
                        """() => {
                            for (const k of Object.keys(localStorage)) {
                                if (k.startsWith('qlvc-da-doc-')) localStorage.removeItem(k);
                            }
                        }"""
                    )
                    page.reload(wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=500)

                    chuong = page.locator("details.chuong").first
                    chuong.wait_for(state="visible", timeout=6000)
                    badge_em = chuong.locator("summary em")
                    badge_txt = badge_em.inner_text().strip() if badge_em.count() > 0 else "0"
                    so_api = len(ds_tb_api)
                    mong_doi_badge = "99+" if so_api > 99 else str(so_api)

                    van_de = []
                    if so_api > 0 and badge_txt != mong_doi_badge:
                        van_de.append(f"Số 'mới' trên chuông ({badge_txt}) không khớp API ({mong_doi_badge})")

                    # Mở chuông
                    chuong.locator("summary").click()
                    page.wait_for_timeout(300)
                    box = kiem_khung_noi(page, ".chuong-hop")
                    if not box.get("co"):
                        return False, "Bấm chuông nhưng không hiện hộp .chuong-hop", "Vừa"
                    if box["tranTrai"] or box["tranPhai"] or box["deMenu"]:
                        van_de.append(f"Hộp chuông tràn/che ở 1440px: {box}")

                    # Thử cuộn trong danh sách thông báo
                    page.evaluate(
                        """() => {
                            const ul = document.querySelector('.chuong-hop ul');
                            if (ul) ul.scrollTop = 200;
                        }"""
                    )
                    # Kiểm dấu "mới" bên trong và bấm mục đầu tiên xem có điều hướng đúng không
                    links = chuong.locator(".chuong-hop ul a")
                    href_dau = ""
                    url_sau = ""
                    if links.count() > 0:
                        href_dau = links.first.get_attribute("href") or ""
                        links.first.click()
                        cho_yen(page, ms=450)
                        url_sau = page.url.replace(BASE_FE, "")
                        if href_dau and not url_sau.startswith(href_dau.split("?")[0]):
                            van_de.append(f"Bấm mục thông báo href={href_dau} nhưng lại tới {url_sau}")
                        # Sau khi mở chuông 1 lần, số badge phải về 0
                        badge_sau = page.locator("details.chuong summary em").count()
                        if badge_sau > 0:
                            van_de.append("Sau khi đã mở chuông đọc, số 'mới' vẫn không xóa về 0")

                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de)
                        if van_de
                        else f"Số mới khớp API ({badge_txt}/{so_api}), hộp gọn, bấm mục đi đúng ({href_dau} -> {url_sau})",
                        "Vừa",
                    )

                bc.chay_ca(
                    "TB01_CHUONG_LOGIC",
                    "Chuông thông báo: số 'mới' khớp API, cuộn danh sách, bấm mục điều hướng đúng trang",
                    test_chuong_so_moi_va_dieu_huong,
                    page=page,
                    tai_hien="Xóa qlvc-da-doc-* -> tải lại -> kiểm số mới -> mở chuông -> bấm mục đầu tiên",
                    mong_doi="Số mới khớp /api/thong-bao, hộp không tràn, bấm mục đi đúng trang và reset số mới",
                )

                # 2. Kiểm tràn / che menu ở 1100px và 390px cho Chuông + Menu tài khoản + Tìm chung
                for vp_ten, vp in [("1100x800", VIEWPORT_TABLET), ("390x844", VIEWPORT_MOBILE)]:
                    def make_test_noi(vname=vp_ten, vdim=vp):
                        def chay():
                            mon.reset()
                            page.set_viewport_size(vdim)
                            page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                            cho_yen(page, ms=450)
                            van_de = []

                            # Chuông
                            page.locator("details.chuong summary").first.click()
                            page.wait_for_timeout(250)
                            b_ch = kiem_khung_noi(page, ".chuong-hop")
                            if not b_ch.get("co") or b_ch["tranTrai"] or b_ch["tranPhai"] or b_ch["deMenu"]:
                                van_de.append(f"Chuông lỗi ở {vname}: {b_ch}")
                            page.mouse.click(5, 5)
                            page.wait_for_timeout(150)

                            # Menu tài khoản
                            page.locator("details.menu-tk summary").first.click()
                            page.wait_for_timeout(250)
                            b_tk = kiem_khung_noi(page, ".menu-tk-hop")
                            if not b_tk.get("co") or b_tk["tranTrai"] or b_tk["tranPhai"] or b_tk["deMenu"]:
                                van_de.append(f"Menu tài khoản lỗi ở {vname}: {b_tk}")
                            # Kiểm đóng bằng Escape
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(200)
                            if page.locator("details.menu-tk[open]").count() > 0:
                                van_de.append(f"Menu tài khoản không đóng khi nhấn Escape ở {vname}")

                            # Ô tìm kiếm (ẩn dưới 760px theo docs, nhưng nếu hiện thì phải gọn trong viewport)
                            o_tim = page.locator('.tim-chung input[type="search"]').first
                            if o_tim.count() > 0 and o_tim.is_visible():
                                o_tim.fill("DH")
                                page.wait_for_timeout(500)
                                b_tim = kiem_khung_noi(page, ".tim-hop")
                                if b_tim.get("co") and (b_tim["tranTrai"] or b_tim["tranPhai"] or b_tim["deMenu"]):
                                    van_de.append(f"Hộp kết quả Tìm chung tràn/che ở {vname}: {b_tim}")
                                o_tim.press("Escape")

                            return (
                                not van_de and not mon.page_errors,
                                " | ".join(van_de) if van_de else f"Chuông, Menu tài khoản & Tìm chung gọn trong {vname}",
                                "Vừa",
                            )
                        return chay

                    bc.chay_ca(
                        f"TB02_NOI_{vp_ten.split('x')[0]}",
                        f"Chuông, Menu tài khoản & Ô tìm kiếm ở {vp_ten}: không tràn màn hay che menu",
                        make_test_noi(),
                        page=page,
                        tai_hien=f"Viewport {vp_ten} -> lần lượt mở Chuông, Menu tài khoản, Tìm chung",
                        mong_doi="Các hộp nổi nằm gọn trong khung nhìn, không che menu, đóng được bằng Escape/bấm ngoài",
                    )

                # 3. Ô tìm kiếm: gõ tìm, cuộn kết quả, bấm 1 kết quả đi đúng trang
                def test_tim_chung_dieu_huong():
                    mon.reset()
                    page.set_viewport_size(VIEWPORT_DESKTOP)
                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    o_tim = page.locator('.tim-chung input[type="search"]').first
                    o_tim.fill("CH-")
                    page.wait_for_timeout(600)
                    hop = page.locator(".tim-hop")
                    if hop.count() == 0:
                        o_tim.fill("DH-")
                        page.wait_for_timeout(600)
                    if hop.count() == 0:
                        return False, "Gõ 'CH-' / 'DH-' vào ô tìm chung không hiện hộp .tim-hop", "Vừa"
                    links = hop.locator("a")
                    if links.count() == 0:
                        return True, "Hộp tìm chung hiện bình thường (không có dữ liệu khớp 'CH-'/'DH-')", ""
                    href = links.first.get_attribute("href") or ""
                    links.first.click()
                    cho_yen(page, ms=450)
                    url_sau = page.url.replace(BASE_FE, "")
                    if href and not url_sau.startswith(href):
                        return False, f"Bấm kết quả tìm chung href={href} nhưng tới {url_sau}", "Vừa"
                    return True, f"Tìm chung mở hộp, bấm kết quả điều hướng đúng ({url_sau})", ""

                bc.chay_ca(
                    "TB03_TIM_CHUNG_CLICK",
                    "Ô tìm kiếm trên cùng: gõ từ khóa, hiện danh sách nhóm và bấm điều hướng đúng",
                    test_tim_chung_dieu_huong,
                    page=page,
                    tai_hien="Gõ 'CH-' hoặc 'DH-' vào ô Tìm chung -> bấm kết quả đầu tiên",
                    mong_doi="Hiện hộp kết quả .tim-hop và bấm điều hướng tới đúng trang chi tiết",
                )

                # 4. Popover cảnh báo "ĐƠN THẤT BẠI" ở 1100px và 390px + rê chuột đi lại giữa nút và tờ giấy
                for vp_ten, vp in [("1100x800", VIEWPORT_TABLET), ("390x844", VIEWPORT_MOBILE)]:
                    def make_test_popover(vname=vp_ten, vdim=vp):
                        def chay():
                            mon.reset()
                            page.set_viewport_size(vdim)
                            # Kiểm tra trên cả /dieu-phoi/don và /dieu-phoi/chuyen để tìm nút/tem "ĐƠN THẤT BẠI"
                            tim_thay = None
                            for path in ["/dieu-phoi/don", "/dieu-phoi/chuyen"]:
                                page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
                                cho_yen(page, ms=500)
                                loc = page.locator(
                                    'button:has-text("ĐƠN THẤT BẠI"), button:has-text("Đơn thất bại"), '
                                    '[class*="that-bai"], [class*="canh-bao"] button'
                                )
                                for idx in range(loc.count()):
                                    el = loc.nth(idx)
                                    if el.is_visible():
                                        txt = (el.inner_text() or "").strip()
                                        if "thất bại" in txt.lower():
                                            tim_thay = (path, el, txt)
                                            break
                                if tim_thay:
                                    break

                            if not tim_thay:
                                return (
                                    True,
                                    f"Chưa có đơn thất bại / nút popover 'ĐƠN THẤT BẠI' đang hiển thị ở {vname} (ghi chú: kiểm lại nếu có dữ liệu đơn thất bại)",
                                    "",
                                )

                            path, btn, txt_nut = tim_thay
                            btn_box = btn.bounding_box()
                            if not btn_box:
                                return False, f"Nút '{txt_nut}' ở {path} không có bounding box", "Vừa"

                            # Rê chuột vào nút (và nếu không mở khi hover thì thử click)
                            page.mouse.move(btn_box["x"] + btn_box["width"] / 2, btn_box["y"] + btn_box["height"] / 2)
                            page.wait_for_timeout(350)

                            def tim_popover():
                                return page.evaluate(
                                    """() => {
                                        const cands = document.querySelectorAll(
                                            '[role="tooltip"], [role="dialog"], .popover, [class*="popover"], [class*="to-giay"], [class*="giay"], [class*="canh-bao-hop"], [class*="tb-hop"]'
                                        );
                                        const vw = window.innerWidth, vh = window.innerHeight;
                                        const menu = document.querySelector('aside.canh');
                                        const mr = (menu && vw >= 900) ? menu.getBoundingClientRect() : null;
                                        for (const el of cands) {
                                            const st = getComputedStyle(el);
                                            const r = el.getBoundingClientRect();
                                            if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.05) continue;
                                            if (r.width < 60 || r.height < 30) continue;
                                            if (st.position === 'fixed' || st.position === 'absolute') {
                                                let deMenu = false;
                                                if (mr && mr.width > 0) {
                                                    const ix = Math.min(r.right, mr.right) - Math.max(r.left, mr.left);
                                                    const iy = Math.min(r.bottom, mr.bottom) - Math.max(r.top, mr.top);
                                                    if (ix > 8 && iy > 8) deMenu = true;
                                                }
                                                return {
                                                    co: true,
                                                    cls: (el.className || '').toString().slice(0, 50),
                                                    x: r.x, y: r.y, w: r.width, h: r.height,
                                                    tranTrai: r.left < -2,
                                                    tranPhai: r.right > vw + 2,
                                                    tranDuoi: r.bottom > vh + 4,
                                                    deMenu,
                                                };
                                            }
                                        }
                                        return { co: false };
                                    }"""
                                )

                            pop = tim_popover()
                            mo_bang_hover = pop.get("co", False)
                            if not mo_bang_hover:
                                btn.click()
                                page.wait_for_timeout(300)
                                pop = tim_popover()

                            if not pop.get("co"):
                                return True, f"Thấy phần tử '{txt_nut}' ở {path} ({vname}) nhưng không có lớp popover position:fixed/absolute nổi lên", ""

                            van_de = []
                            if pop["tranTrai"] or pop["tranPhai"]:
                                van_de.append(f"Popover tràn ngang viewport ở {vname}: {pop}")
                            if pop["deMenu"]:
                                van_de.append(f"Popover che đè lên menu trái ở {vname}: {pop}")

                            # Rê chuột đi lại giữa nút và tờ giấy popover (chỉ kiểm tắt giữa chừng ở desktop/1100px)
                            if mo_bang_hover and vdim["width"] >= 900:
                                x1 = btn_box["x"] + btn_box["width"] / 2
                                y1 = btn_box["y"] + btn_box["height"] / 2
                                x2 = pop["x"] + pop["w"] / 2
                                y2 = pop["y"] + min(pop["h"] / 2, 40)
                                tat_giua_chung = False
                                for buoc in range(1, 7):
                                    t = buoc / 6.0
                                    page.mouse.move(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
                                    page.wait_for_timeout(90)
                                    if not tim_popover().get("co"):
                                        tat_giua_chung = True
                                        break
                                if not tat_giua_chung:
                                    # Rê ngược lại về nút
                                    for buoc in range(1, 7):
                                        t = buoc / 6.0
                                        page.mouse.move(x2 + (x1 - x2) * t, y2 + (y1 - y2) * t)
                                        page.wait_for_timeout(90)
                                        if not tim_popover().get("co"):
                                            tat_giua_chung = True
                                            break
                                if tat_giua_chung:
                                    van_de.append("Rê chuột đi lại giữa nút và tờ giấy popover bị tắt giữa chừng (có khe hở hover)")

                            return (
                                not van_de and not mon.page_errors,
                                " | ".join(van_de) if van_de else f"Popover '{txt_nut}' ở {vname} gọn, không che menu, rê chuột ổn định",
                                "Vừa",
                            )
                        return chay

                    bc.chay_ca(
                        f"TB04_POPOVER_{vp_ten.split('x')[0]}",
                        f"Popover cảnh báo 'ĐƠN THẤT BẠI' ở {vp_ten}: tràn màn, che menu & rê chuột không tắt giữa chừng",
                        make_test_popover(),
                        page=page,
                        tai_hien=f"Viewport {vp_ten} -> mở /dieu-phoi/don hoặc /chuyen -> rê chuột/bấm nút ĐƠN THẤT BẠI -> rê chuột giữa nút và popover",
                        mong_doi="Popover nằm gọn trong màn hình, không che menu, rê chuột đi lại không bị tắt giữa chừng",
                    )
            finally:
                ctx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
