"""Mục 05: Chuyển trang và tải trên GIAO DIỆN PIXEL.

Các kịch bản:
1. Đổi trang liên tục thật nhanh qua menu trái (20 lần)
2. Back / Forward liên tiếp nhiều lần
3. F5 (reload) giữa chừng khi API đang tải chậm
4. Mạng chậm (page.route thêm trễ 2–3 s cho /api/**):
   - Kiểm tra màn trắng
   - Kiểm tra hiệu ứng mờ-hiện dần (main.trang > * chạy px-hien-mo 300ms):
     có bị kẹt độ mờ thấp, nhấp nháy chạy 2 lần, hay bị filter: blur mãi không
   - Kiểm tra khung xương tải .px-tai có tự biến mất sau khi dữ liệu về không
5. Mạng lỗi (abort 30% request /api/**):
   - Không màn trắng, không pageerror, .px-tai không kẹt mãi

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_05_chuyen_trang_tai.py
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    VIEWPORT_DESKTOP,
    BaoCaoScript,
    cho_noi_dung_khong_trang,
    cho_yen,
    dang_nhap_nhanh,
    mo_trang_moi,
    tao_context_pixel,
)

JS_THEO_DOI_ANIM = """() => {
  window.__phaAnimEvents = [];
  if (!window.__phaAnimBound) {
    window.__phaAnimBound = true;
    document.addEventListener('animationstart', (e) => {
      if (e.target && e.target.closest && e.target.closest('main.trang')) {
        window.__phaAnimEvents.push({
          t: Date.now(),
          name: e.animationName || '',
          tag: e.target.tagName.toLowerCase(),
          cls: (e.target.className || '').toString().slice(0, 40),
        });
      }
    }, true);
  }
}"""


def kiem_trang_thai_hien_mo(page: Page) -> dict:
    return page.evaluate(
        """() => {
            const kids = Array.from(document.querySelectorAll('main.trang > *')).map(el => {
                const st = getComputedStyle(el);
                return {
                    tag: el.tagName.toLowerCase(),
                    cls: (el.className || '').toString().slice(0, 40),
                    opacity: parseFloat(st.opacity),
                    filter: st.filter || 'none',
                    anim: st.animationName || 'none',
                };
            });
            const pxTai = Array.from(document.querySelectorAll('.px-tai')).filter(el => {
                const st = getComputedStyle(el);
                const r = el.getBoundingClientRect();
                return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 0 && r.height > 0;
            }).length;
            const mainEl = document.querySelector('main.trang');
            const textLen = (mainEl ? mainEl.innerText : '').trim().length;
            return {
                kids,
                ketMo: kids.some(k => k.opacity < 0.98),
                ketNhoe: kids.some(k => k.filter !== 'none' && k.filter.includes('blur')),
                pxTai,
                textLen,
                animEvents: (window.__phaAnimEvents || []).slice(-20),
            };
        }"""
    )


def main() -> None:
    bc = BaoCaoScript(5, "Chuyển trang, tải chậm/lỗi, hiệu ứng px-hien-mo & khung xương .px-tai", "ket_qua_05.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx)
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")
                page.evaluate(JS_THEO_DOI_ANIM)

                # 5.1 Đổi trang liên tục thật nhanh qua menu trái 20 lần
                def test_doi_trang_20_lan():
                    mon.reset()
                    links = page.locator("aside.canh nav a")
                    so_link = links.count()
                    if so_link < 2:
                        return False, f"Không tìm thấy đủ mục menu trái (count={so_link})", "Vừa"
                    for i in range(20):
                        links.nth(i % so_link).click(timeout=4000)
                        page.wait_for_timeout(80)
                    co_nd, text_len, mau = cho_noi_dung_khong_trang(page, timeout_s=4.5)
                    cho_yen(page, ms=600, network_timeout=5000)
                    st = kiem_trang_thai_hien_mo(page)
                    van_de = []
                    if not co_nd:
                        van_de.append(f"Màn trắng sau 20 lần đổi menu (len={text_len}, mẫu={mau!r})")
                    if mon.page_errors:
                        van_de.append(f"pageerror={mon.page_errors[:2]}")
                    if mon.http_5xx:
                        van_de.append(f"5xx={mon.http_5xx[:2]}")
                    if st["ketMo"]:
                        van_de.append(f"Kẹt độ mờ thấp sau 600ms: {st['kids']}")
                    if st["ketNhoe"]:
                        van_de.append(f"Kẹt filter blur (nhòe chữ mãi): {st['kids']}")
                    if st["pxTai"] > 0:
                        van_de.append(f"Khung xương .px-tai bị kẹt ({st['pxTai']})")
                    muc = "Nghiêm trọng" if (not co_nd or mon.page_errors or mon.http_5xx) else "Vừa"
                    return (
                        not van_de,
                        " | ".join(van_de)
                        if van_de
                        else f"20 lần bấm menu liên tục OK (url={page.url.replace(BASE_FE, '')}, text={text_len}, opacity/blur sạch)",
                        muc,
                    )

                bc.chay_ca(
                    "CT01_DOI_MENU_20_LAN",
                    "Đổi trang liên tục thật nhanh qua menu trái 20 lần",
                    test_doi_trang_20_lan,
                    page=page,
                    tai_hien="Bấm liên tục 20 lần qua các mục menu trái (cách nhau 80ms)",
                    mong_doi="Không màn trắng, không pageerror/5xx, không kẹt mờ/nhòe hay .px-tai",
                )

                # 5.2 Back / Forward liên tiếp
                def test_back_forward():
                    mon.reset()
                    routes = [
                        "/dieu-phoi/chuyen",
                        "/dieu-phoi/don",
                        "/dieu-phoi/xe",
                        "/dieu-phoi/tai-xe",
                        "/dieu-phoi/khach-hang",
                        "/dieu-phoi/tuyen",
                    ]
                    for r in routes:
                        page.goto(f"{BASE_FE}{r}", wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(200)
                    for _ in range(5):
                        page.go_back(wait_until="domcontentloaded", timeout=10000)
                        page.wait_for_timeout(150)
                    for _ in range(5):
                        page.go_forward(wait_until="domcontentloaded", timeout=10000)
                        page.wait_for_timeout(150)
                    co_nd, text_len, mau = cho_noi_dung_khong_trang(page, timeout_s=4.0)
                    cho_yen(page, ms=500)
                    st = kiem_trang_thai_hien_mo(page)
                    van_de = []
                    if not co_nd:
                        van_de.append(f"Màn trắng sau Back/Forward (len={text_len}, mẫu={mau!r})")
                    if mon.page_errors or mon.http_5xx:
                        van_de.append(f"pageerror={mon.page_errors[:2]}, 5xx={mon.http_5xx[:2]}")
                    if st["ketMo"] or st["ketNhoe"]:
                        van_de.append(f"Kẹt mờ/nhòe sau Back/Forward: {st['kids']}")
                    if st["pxTai"] > 0:
                        van_de.append(f"Kẹt .px-tai ({st['pxTai']})")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else f"5× Back + 5× Forward OK (cuối={page.url.replace(BASE_FE, '')})",
                        "Nghiêm trọng" if (not co_nd or mon.page_errors) else "Vừa",
                    )

                bc.chay_ca(
                    "CT02_BACK_FORWARD",
                    "Back 5 lần rồi Forward 5 lần liên tiếp",
                    test_back_forward,
                    page=page,
                    tai_hien="Mở 6 trang liên tiếp -> bấm Back 5 lần -> bấm Forward 5 lần",
                    mong_doi="Hiển thị đúng trang cuối, không màn trắng, không kẹt px-hien-mo / .px-tai",
                )

                # 5.3 F5 giữa chừng khi API đang tải
                def test_f5_giua_chung():
                    mon.reset()
                    tre_bat = {"on": True}

                    def route_cham(route):
                        try:
                            if tre_bat["on"]:
                                page.wait_for_timeout(1500)
                            route.continue_()
                        except Exception:
                            pass

                    page.route("**/api/**", route_cham)
                    try:
                        page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(300)
                        # Tắt trễ rồi F5 ngay giữa lúc request đầu còn đang treo
                        tre_bat["on"] = False
                        page.reload(wait_until="domcontentloaded", timeout=15000)
                        co_nd, text_len, mau = cho_noi_dung_khong_trang(page, timeout_s=4.5)
                        cho_yen(page, ms=500)
                        st = kiem_trang_thai_hien_mo(page)
                    finally:
                        page.unroute("**/api/**", route_cham)

                    van_de = []
                    if not co_nd:
                        van_de.append(f"Màn trắng sau F5 giữa chừng (len={text_len}, mẫu={mau!r})")
                    if mon.page_errors or mon.http_5xx:
                        van_de.append(f"pageerror={mon.page_errors[:2]}, 5xx={mon.http_5xx[:2]}")
                    if st["ketMo"] or st["ketNhoe"] or st["pxTai"] > 0:
                        van_de.append(f"Kẹt hiệu ứng/skeleton sau F5: {st}")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else f"F5 giữa lúc API đang tải phục hồi sạch (text={text_len})",
                        "Nghiêm trọng" if (not co_nd or mon.page_errors) else "Vừa",
                    )

                bc.chay_ca(
                    "CT03_F5_GIUA_CHUNG",
                    "F5 (reload) giữa chừng khi API đang tải chậm",
                    test_f5_giua_chung,
                    page=page,
                    tai_hien="Làm trễ /api/** 1.5s -> mở /dieu-phoi/don -> sau 300ms bấm F5",
                    mong_doi="Trang tải lại sạch, không màn trắng, không kẹt mờ/nhòe hay .px-tai",
                )

                # 5.4 Mạng chậm (trễ 2.2s cho /api/**): kiểm px-hien-mo nhấp nháy 2 lần / kẹt mờ / .px-tai kẹt
                def test_mang_cham():
                    mon.reset()

                    def route_cham_2s(route):
                        try:
                            page.wait_for_timeout(2200)
                            route.continue_()
                        except Exception:
                            pass

                    page.route("**/api/**", route_cham_2s)
                    try:
                        page.evaluate(JS_THEO_DOI_ANIM)
                        page.evaluate("() => { window.__phaAnimEvents = []; }")
                        # Bấm menu chuyển sang Đơn hàng trong điều kiện mạng chậm 2.2s
                        link_don = page.locator('aside.canh nav a[href="/dieu-phoi/don"]').first
                        if link_don.count() > 0:
                            link_don.click()
                        else:
                            page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)

                        # Đo ở mốc 600ms (trong lúc API chưa về)
                        page.wait_for_timeout(600)
                        giua = kiem_trang_thai_hien_mo(page)
                        # Chờ API về xong (tối đa 6s)
                        cho_yen(page, ms=700, network_timeout=6500)
                        cuoi = kiem_trang_thai_hien_mo(page)
                    finally:
                        page.unroute("**/api/**", route_cham_2s)

                    hien_mo_ev = [e for e in cuoi["animEvents"] if "hien-mo" in e["name"].lower() or "px-" in e["name"].lower()]
                    van_de = []
                    if cuoi["textLen"] < 20:
                        van_de.append(f"Màn trắng sau khi API chậm 2.2s trả về (textLen={cuoi['textLen']})")
                    if mon.page_errors or mon.http_5xx:
                        van_de.append(f"pageerror={mon.page_errors[:2]}, 5xx={mon.http_5xx[:2]}")
                    if cuoi["ketMo"]:
                        van_de.append(f"Kẹt opacity thấp sau tải chậm: {cuoi['kids']}")
                    if cuoi["ketNhoe"]:
                        van_de.append(f"Kẹt filter blur sau tải chậm: {cuoi['kids']}")
                    if cuoi["pxTai"] > 0:
                        van_de.append(f"Khung xương .px-tai kẹt mãi sau khi API về ({cuoi['pxTai']})")
                    # Phát hiện px-hien-mo chạy >= 2 lần trên cùng 1 lượt chuyển trang (nhấp nháy 2 lần)
                    so_hien_mo = sum(1 for e in hien_mo_ev if "hien-mo" in e["name"].lower())
                    if so_hien_mo >= 2:
                        van_de.append(f"Hiệu ứng px-hien-mo chạy lặp {so_hien_mo} lần (nhấp nháy hai lần): {hien_mo_ev}")
                    return (
                        not van_de,
                        " | ".join(van_de)
                        if van_de
                        else f"Mạng trễ 2.2s OK (giữa tải .px-tai={giua['pxTai']}, sau tải .px-tai={cuoi['pxTai']}, px-hien-mo={so_hien_mo} lần)",
                        "Vừa",
                    )

                bc.chay_ca(
                    "CT04_MANG_CHAM_2S",
                    "Mạng chậm (trễ 2.2s /api/**): kiểm px-hien-mo không kẹt mờ/nhòe/nháy 2 lần & .px-tai tắt",
                    test_mang_cham,
                    page=page,
                    tai_hien="Chặn /api/** trễ 2.2s -> bấm menu sang /dieu-phoi/don -> theo dõi animationstart & .px-tai",
                    mong_doi="Không kẹt độ mờ/blur, px-hien-mo không nháy 2 lần, .px-tai tự tắt khi dữ liệu về",
                )

                # 5.5 Mạng lỗi: abort 30% request /api/**
                def test_mang_loi_30():
                    mon.reset()
                    dem = {"n": 0, "aborted": 0}

                    def route_abort_30(route):
                        dem["n"] += 1
                        # Bỏ qua /api/auth/toi để không bị đá ra /dang-nhap ngẫu nhiên, abort 1 trong mỗi 3 request còn lại
                        if "/api/auth/toi" not in route.request.url and dem["n"] % 3 == 0:
                            dem["aborted"] += 1
                            try:
                                route.abort("failed")
                            except Exception:
                                pass
                            return
                        try:
                            route.continue_()
                        except Exception:
                            pass

                    page.route("**/api/**", route_abort_30)
                    van_de = []
                    try:
                        for path in ["/dieu-phoi/chuyen", "/dieu-phoi/don", "/dieu-phoi/xe", "/dieu-phoi/khach-hang"]:
                            page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
                            co_nd, text_len, _ = cho_noi_dung_khong_trang(page, timeout_s=4.0)
                            cho_yen(page, ms=500, network_timeout=4000)
                            st = kiem_trang_thai_hien_mo(page)
                            if not co_nd:
                                van_de.append(f"{path}: màn trắng khi abort 30%")
                            if st["pxTai"] > 0:
                                van_de.append(f"{path}: kẹt {st['pxTai']} .px-tai khi request lỗi")
                            if st["ketMo"] or st["ketNhoe"]:
                                van_de.append(f"{path}: kẹt mờ/nhòe khi request lỗi")
                    finally:
                        page.unroute("**/api/**", route_abort_30)

                    if mon.page_errors:
                        van_de.append(f"pageerror khi mạng lỗi: {mon.page_errors[:2]}")
                    muc = "Nghiêm trọng" if (mon.page_errors or any("màn trắng" in x for x in van_de)) else "Vừa"
                    return (
                        not van_de,
                        " | ".join(van_de)
                        if van_de
                        else f"Đã abort {dem['aborted']}/{dem['n']} request trên 4 trang: không màn trắng, không pageerror, không kẹt .px-tai",
                        muc,
                    )

                bc.chay_ca(
                    "CT05_MANG_LOI_30",
                    "Mạng lỗi (abort 30% request /api/**) trên 4 trang: không màn trắng, không kẹt .px-tai",
                    test_mang_loi_30,
                    page=page,
                    tai_hien="Abort 1/3 số request /api/** -> lần lượt mở 4 trang Chuyến, Đơn, Xe, Khách hàng",
                    mong_doi="Hiện báo lỗi thân thiện hoặc nội dung còn lại, không màn trắng/pageerror, .px-tai không kẹt mãi",
                )
            finally:
                ctx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
