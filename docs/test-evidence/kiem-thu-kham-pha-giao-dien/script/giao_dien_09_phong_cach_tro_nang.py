"""Mục 09: Đổi phong cách & Trợ năng (Accessibility) trên GIAO DIỆN PIXEL.

Kịch bản:
1. Đổi phong cách Pixel <-> Hiện tại giữa chừng trong /cai-dat (có nháy/vỡ bố cục không)
2. Bật prefers-reduced-motion (emulate_media), thuộc tính data-giam-chuyen-dong='bat'
   và data-hieu-ung-pixel='tat': kiểm tra hiệu ứng có thật sự tắt không
3. Phóng chữ 200% và zoom 150%: bố cục có vỡ/tràn/chồng không
4. Tab qua toàn trang: kiểm tra mọi nút/liên kết/ô nhập có viền focus nhìn thấy được không
5. Đo tương phản màu nút và tem (WCAG 2.1 đơn giản: ≥ 4.5:1 chữ thường, ≥ 3.0:1 chữ lớn)

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_09_phong_cach_tro_nang.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    VIEWPORT_DESKTOP,
    BaoCaoScript,
    cho_yen,
    dang_nhap_nhanh,
    kiem_bo_cuc_trang,
    mo_trang_moi,
    tao_context_pixel,
)

JS_DO_WCAG_CONTRAST = """() => {
  const parseRgb = (str) => {
    if (!str) return null;
    const m = str.match(/rgba?\\(\\s*([\\d.]+)[,\\s]+([\\d.]+)[,\\s]+([\\d.]+)(?:[,/\\s]+([\\d.]+))?\\s*\\)/i);
    if (!m) return null;
    return { r: Number(m[1]), g: Number(m[2]), b: Number(m[3]), a: m[4] === undefined ? 1 : Number(m[4]) };
  };
  const blend = (fg, bg) => {
    const a = fg.a;
    return {
      r: fg.r * a + bg.r * (1 - a),
      g: fg.g * a + bg.g * (1 - a),
      b: fg.b * a + bg.b * (1 - a),
      a: 1,
    };
  };
  const getBg = (el) => {
    const layers = [];
    let cur = el;
    while (cur && cur.nodeType === 1) {
      const c = parseRgb(getComputedStyle(cur).backgroundColor);
      if (c && c.a > 0) layers.push(c);
      if (c && c.a >= 0.99) break;
      cur = cur.parentElement;
    }
    let acc = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = layers.length - 1; i >= 0; i--) {
      acc = blend(layers[i], acc);
    }
    return acc;
  };
  const lum = ({ r, g, b }) => {
    const c = [r, g, b].map((v) => {
      const s = v / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const ratio = (c1, c2) => {
    const l1 = lum(c1), l2 = lum(c2);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };

  const khongDat = [];
  let tongDo = 0;
  for (const el of document.querySelectorAll('button, .nhan, .bien, [class*="tem"], [class*="badge"]')) {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.2) continue;
    if (el.disabled) continue; // WCAG miễn nút disabled
    const r = el.getBoundingClientRect();
    if (r.width < 12 || r.height < 12) continue;
    const txt = (el.innerText || '').trim().replace(/\\s+/g, ' ');
    if (!txt) continue;
    const fg = parseRgb(st.color);
    const bg = getBg(el);
    if (!fg) continue;
    const fgEff = fg.a < 1 ? blend(fg, bg) : fg;
    const cr = ratio(fgEff, bg);
    const fs = parseFloat(st.fontSize) || 14;
    const fw = parseInt(st.fontWeight, 10) || 400;
    const lon = fs >= 24 || (fs >= 18.66 && fw >= 700);
    const nguong = lon ? 3.0 : 4.5;
    tongDo += 1;
    if (cr < nguong) {
      khongDat.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().slice(0, 35),
        txt: txt.slice(0, 30),
        ratio: Math.round(cr * 100) / 100,
        nguong,
        fg: st.color,
        bg: `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})`,
      });
    }
  }
  return { tongDo, soLoi: khongDat.length, khongDat: khongDat.slice(0, 12) };
}"""


def dem_hieu_ung_chay(page: Page) -> dict:
    return page.evaluate(
        """() => {
            const anims = document.getAnimations ? document.getAnimations() : [];
            const dangChay = [];
            for (const a of anims) {
                if (a.playState !== 'running') continue;
                const timing = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
                const dur = Number(timing.duration) || 0;
                const iters = timing.iterations;
                if (dur > 10 || iters === Infinity) {
                    dangChay.push({
                        name: a.animationName || a.transitionProperty || 'waapi',
                        dur,
                        infinite: iters === Infinity,
                    });
                }
            }
            const ds = document.documentElement.dataset;
            return {
                tongAnim: anims.length,
                soDangChay: dangChay.length,
                mauDangChay: dangChay.slice(0, 6),
                giamChuyenDong: ds.giamChuyenDong || '',
                hieuUngPixel: ds.hieuUngPixel || '',
                phongCach: ds.phongCach || localStorage.getItem('qlvc-phong-cach') || '',
            };
        }"""
    )


def main() -> None:
    bc = BaoCaoScript(9, "Đổi phong cách Pixel ↔ Hiện tại & Trợ năng (reduced motion, zoom, Tab focus, WCAG)", "ket_qua_09.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =================================================================
            # 9.1 Đổi phong cách Pixel <-> Hiện tại giữa chừng trong Cài đặt
            # =================================================================
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP, co_dinh_pixel=False)
            page, mon = mo_trang_moi(ctx)
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")

                def test_doi_phong_cach():
                    mon.reset()
                    page.goto(f"{BASE_FE}/cai-dat", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    btn_pixel = page.locator('button:has-text("Pixel")').first
                    btn_hientai = page.locator('button:has-text("Hiện tại")').first
                    if btn_pixel.count() == 0 or btn_hientai.count() == 0:
                        return False, "Không tìm thấy cặp nút đổi phong cách 'Pixel' / 'Hiện tại' trên trang /cai-dat", "Vừa"

                    van_de = []
                    for luot in range(2):
                        btn_hientai.click()
                        page.wait_for_timeout(300)
                        ls_ht = page.evaluate("() => localStorage.getItem('qlvc-phong-cach') || ''")
                        bc_ht = kiem_bo_cuc_trang(page)
                        if ls_ht == "pixel":
                            van_de.append(f"Lượt {luot + 1}: bấm 'Hiện tại' nhưng qlvc-phong-cach vẫn là 'pixel'")
                        if bc_ht["cuonNgang"] or bc_ht["chongNhau"]:
                            van_de.append(f"Vỡ bố cục khi đổi sang Hiện tại: cuonNgang={bc_ht['cuonNgang']}, chong={bc_ht['chongNhau'][:2]}")

                        btn_pixel.click()
                        page.wait_for_timeout(300)
                        ls_px = page.evaluate("() => localStorage.getItem('qlvc-phong-cach') || ''")
                        bc_px = kiem_bo_cuc_trang(page)
                        if ls_px != "pixel":
                            van_de.append(f"Lượt {luot + 1}: bấm 'Pixel' nhưng qlvc-phong-cach={ls_px!r}")
                        if bc_px["cuonNgang"] or bc_px["chongNhau"]:
                            van_de.append(f"Vỡ bố cục khi đổi lại Pixel: cuonNgang={bc_px['cuonNgang']}, chong={bc_px['chongNhau'][:2]}")

                    # Chuyển sang trang Chuyến sau khi đổi lại Pixel để kiểm không kẹt vỡ
                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=450)
                    bc_ch = kiem_bo_cuc_trang(page)
                    if bc_ch["cuonNgang"] or mon.page_errors:
                        van_de.append(f"Sau đổi phong cách mở /chuyen lỗi: cuonNgang={bc_ch['cuonNgang']}, pageerror={mon.page_errors[:2]}")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else "Đổi qua lại Pixel ↔ Hiện tại 2 vòng êm, lưu đúng localStorage, không vỡ bố cục",
                        "Vừa",
                    )

                bc.chay_ca(
                    "TN01_DOI_PHONG_CACH",
                    "Đổi phong cách Pixel ↔ Hiện tại giữa chừng trong /cai-dat",
                    test_doi_phong_cach,
                    page=page,
                    tai_hien="Mở /cai-dat -> bấm Hiện tại -> Pixel lặp 2 vòng -> chuyển sang /dieu-phoi/chuyen",
                    mong_doi="Đổi ngay lập tức, không nháy lỗi/vỡ bố cục, không pageerror",
                )

                # 9.2 prefers-reduced-motion: reduce
                def test_reduced_motion():
                    mon.reset()
                    page.emulate_media(reduced_motion="reduce")
                    try:
                        page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(page, ms=500)
                        k1 = dem_hieu_ung_chay(page)
                        page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(120)
                        k2 = dem_hieu_ung_chay(page)
                    finally:
                        page.emulate_media(reduced_motion="no-preference")

                    if k1["soDangChay"] > 0 or k2["soDangChay"] > 0:
                        return (
                            False,
                            f"Bật prefers-reduced-motion: reduce nhưng vẫn còn animation đang chạy: chuyen={k1['mauDangChay']}, don={k2['mauDangChay']}",
                            "Vừa",
                        )
                    return True, "prefers-reduced-motion: reduce tắt sạch animation đang chạy trên Chuyến & Đơn", ""

                bc.chay_ca(
                    "TN02_REDUCED_MOTION",
                    "Bật prefers-reduced-motion: reduce -> kiểm tra hiệu ứng có thật sự tắt",
                    test_reduced_motion,
                    page=page,
                    tai_hien="emulate_media(reduced_motion='reduce') -> mở /dieu-phoi/chuyen và /dieu-phoi/don -> đo document.getAnimations()",
                    mong_doi="Không còn CSS animation/transition dài > 10ms hay vô hạn đang chạy",
                )

                # 9.3 Thuộc tính data-giam-chuyen-dong='bat' và data-hieu-ung-pixel='tat'
                def test_data_attrs():
                    mon.reset()
                    page.goto(f"{BASE_FE}/cai-dat", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=350)
                    # Thử bật qua nút UI trên /cai-dat nếu có, đồng thời đặt dataset + localStorage đúng tên yêu cầu
                    page.evaluate(
                        """() => {
                            localStorage.setItem('qlvc-giam-chuyen-dong', 'bat');
                            localStorage.setItem('qlvc-hieu-ung-pixel', 'tat');
                            document.documentElement.dataset.giamChuyenDong = 'bat';
                            document.documentElement.dataset.hieuUngPixel = 'tat';
                        }"""
                    )
                    # Bấm menu chuyển sang Đơn hàng (không reload) để kiểm tra CSS áp trực tiếp
                    link_don = page.locator('aside.canh nav a[href="/dieu-phoi/don"]').first
                    if link_don.count() > 0:
                        link_don.click()
                    else:
                        page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(120)
                    k_giua = dem_hieu_ung_chay(page)
                    cho_yen(page, ms=400)
                    k_sau = dem_hieu_ung_chay(page)
                    # Dọn lại cài đặt cho các ca sau
                    page.evaluate(
                        """() => {
                            localStorage.removeItem('qlvc-giam-chuyen-dong');
                            localStorage.removeItem('qlvc-hieu-ung-pixel');
                            delete document.documentElement.dataset.giamChuyenDong;
                            delete document.documentElement.dataset.hieuUngPixel;
                        }"""
                    )
                    if k_giua["soDangChay"] > 0 or k_sau["soDangChay"] > 0:
                        return (
                            False,
                            f"Đã đặt data-giam-chuyen-dong='bat' & data-hieu-ung-pixel='tat' nhưng vẫn có animation chạy: {k_giua['mauDangChay'] or k_sau['mauDangChay']}",
                            "Vừa",
                        )
                    return True, "data-giam-chuyen-dong='bat' & data-hieu-ung-pixel='tat' tắt sạch hiệu ứng", ""

                bc.chay_ca(
                    "TN03_DATA_TAT_HIEU_UNG",
                    "Thuộc tính data-giam-chuyen-dong='bat' & data-hieu-ung-pixel='tat': hiệu ứng có tắt thật không",
                    test_data_attrs,
                    page=page,
                    tai_hien="Đặt data-giam-chuyen-dong='bat' & data-hieu-ung-pixel='tat' -> chuyển sang /dieu-phoi/don -> đo getAnimations()",
                    mong_doi="Tất cả hiệu ứng chuyển động / hiệu ứng pixel tắt hoàn toàn",
                )

                # 9.4 Phóng chữ 200% và zoom 150%
                def test_phong_chu_200_va_zoom_150():
                    mon.reset()
                    van_de = []
                    for che_do, js_ap in [
                        ("font-size 200%", "() => { document.documentElement.style.zoom = ''; document.documentElement.style.fontSize = '200%'; }"),
                        ("zoom 150%", "() => { document.documentElement.style.fontSize = ''; document.documentElement.style.zoom = '1.5'; }"),
                    ]:
                        for path in ["/dieu-phoi/chuyen", "/dieu-phoi/don", "/cai-dat"]:
                            page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
                            cho_yen(page, ms=350)
                            page.evaluate(js_ap)
                            page.wait_for_timeout(250)
                            m = kiem_bo_cuc_trang(page)
                            if m["cuonNgang"] or m["tranViewport"] or m["chongNhau"]:
                                van_de.append(
                                    f"[{che_do}][{path}] cuonNgang={m['cuonNgang']}(sw={m['sw']}/vw={m['vw']}), tran={len(m['tranViewport'])}, chong={len(m['chongNhau'])}"
                                )
                    page.evaluate("() => { document.documentElement.style.fontSize = ''; document.documentElement.style.zoom = ''; }")
                    if van_de:
                        return False, " | ".join(van_de[:4]), "Vừa"
                    return True, "Phóng chữ 200% và zoom 150% trên Chuyến, Đơn, Cài đặt không vỡ bố cục", ""

                bc.chay_ca(
                    "TN04_FONT200_ZOOM150",
                    "Phóng chữ 200% và zoom 150% trên 3 trang (Chuyến, Đơn, Cài đặt)",
                    test_phong_chu_200_va_zoom_150,
                    page=page,
                    tai_hien="Áp font-size: 200% rồi zoom: 1.5 ở 1440×900 trên /chuyen, /don, /cai-dat",
                    mong_doi="Không cuộn ngang vỡ khung, không tràn viewport, không chồng phần tử",
                )

                # 9.5 Tab qua toàn trang: kiểm viền focus trên mọi nút/liên kết
                def test_tab_focus_ring():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.evaluate("() => { if (document.activeElement) document.activeElement.blur(); }")
                    thieu_focus = []
                    da_kiem = 0
                    seen = set()
                    for _ in range(35):
                        page.keyboard.press("Tab")
                        info = page.evaluate(
                            """() => {
                                const el = document.activeElement;
                                if (!el || el === document.body) return null;
                                const tag = el.tagName.toLowerCase();
                                if (!['a', 'button', 'input', 'select', 'summary'].includes(tag)) return null;
                                const st = getComputedStyle(el);
                                const ow = parseFloat(st.outlineWidth) || 0;
                                const coOutline = st.outlineStyle !== 'none' && ow >= 1;
                                const coShadow = st.boxShadow && st.boxShadow !== 'none';
                                const idKey = `${tag}|${(el.className || '').toString().slice(0,25)}|${(el.innerText || el.getAttribute('aria-label') || '').trim().slice(0,25)}`;
                                return { idKey, coOutline, coShadow, outline: `${st.outlineWidth} ${st.outlineStyle} ${st.outlineColor}`, shadow: st.boxShadow.slice(0, 40) };
                            }"""
                        )
                        if not info or info["idKey"] in seen:
                            continue
                        seen.add(info["idKey"])
                        da_kiem += 1
                        if not info["coOutline"] and not info["coShadow"]:
                            thieu_focus.append(info["idKey"])
                    if thieu_focus:
                        return (
                            False,
                            f"{len(thieu_focus)}/{da_kiem} phần tử không có viền focus (outline/box-shadow) khi Tab: {thieu_focus[:6]}",
                            "Vừa",
                        )
                    return True, f"Đã Tab qua {da_kiem} nút/link/ô nhập: tất cả đều có viền focus nhìn thấy được", ""

                bc.chay_ca(
                    "TN05_TAB_FOCUS_RING",
                    "Tab qua toàn trang /dieu-phoi/don: kiểm viền focus ở mọi nút/liên kết",
                    test_tab_focus_ring,
                    page=page,
                    tai_hien="Mở /dieu-phoi/don -> nhấn Tab 35 lần -> đo outline & box-shadow của activeElement",
                    mong_doi="Mọi nút/liên kết đều hiện viền focus rõ ràng khi điều hướng bàn phím",
                )

                # 9.6 Đo tương phản màu WCAG trên nút và tem
                def test_tuong_phan_wcag():
                    mon.reset()
                    tat_ca_loi = []
                    tong_do = 0
                    for path in ["/dieu-phoi/chuyen", "/dieu-phoi/don", "/cai-dat"]:
                        page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
                        cho_yen(page, ms=450)
                        kq = page.evaluate(JS_DO_WCAG_CONTRAST)
                        tong_do += kq["tongDo"]
                        for item in kq["khongDat"]:
                            tat_ca_loi.append(f"{path}: {item['tag']}({item['txt']}) ratio={item['ratio']}<{item['nguong']} [{item['fg']} trên {item['bg']}]")
                    if tat_ca_loi:
                        return (
                            False,
                            f"{len(tat_ca_loi)}/{tong_do} nút/tem dưới ngưỡng tương phản WCAG: " + " ; ".join(tat_ca_loi[:5]),
                            "Nhẹ",
                        )
                    return True, f"Tất cả {tong_do} nút/tem trên 3 trang đều đạt ngưỡng tương phản WCAG", ""

                bc.chay_ca(
                    "TN06_TUONG_PHAN_WCAG",
                    "Đo tương phản màu WCAG trên nút & tem (.nhan, .bien, button)",
                    test_tuong_phan_wcag,
                    page=page,
                    muc="Nhẹ",
                    tai_hien="Mở /dieu-phoi/chuyen, /dieu-phoi/don, /cai-dat -> tính contrast ratio chữ/nền từng nút & tem",
                    mong_doi="Mọi nút và tem đạt tỷ lệ tương phản ≥ 4.5:1 (chữ thường) hoặc ≥ 3.0:1 (chữ lớn)",
                )
            finally:
                ctx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
