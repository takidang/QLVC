"""Mục 02: Form nhập bừa qua giao diện PIXEL.

Thử dữ liệu độc hại / biên trên các form:
- Tạo đơn, Lập chuyến, Thêm/Sửa xe, tài xế, khách hàng, nút, tuyến, bảng giá,
  tạm ứng, chi phí, sự cố, đổi mật khẩu (trên tài khoản PHA- mới), ô tìm kiếm trên cùng.
Bộ giá trị: số âm, 0, 1e15, 10^19, thập phân ở ô nguyên, rỗng, 10.000 ký tự,
emoji, <script>alert(1)</script>, <img src=x onerror=alert(1)>, ' OR 1=1 --,
ngày 30/02, năm 0, 1900, 3000.

Kiểm:
- Thông báo lỗi tiếng Việt ngay ô nhập (không 500, không màn trắng, không crash)
- XSS không chạy (nghe dialog & kiểm window.__xss)
- Dữ liệu rác không lưu
- Chữ báo lỗi không bị tràn khung / bị che

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_02_form_nhap_bua.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Locator, Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    EMOJI_PAYLOAD,
    MIN_JPG,
    SQLI_PAYLOAD,
    VIEWPORT_DESKTOP,
    XSS_IMG,
    XSS_SCRIPT,
    BaoCaoScript,
    BoTheoDoi,
    cho_yen,
    dang_nhap_api,
    dang_nhap_nhanh,
    lay_khach_hang_dau,
    ma_ngau_nhien,
    mo_trang_moi,
    tao_context_pixel,
    tao_tai_khoan_pha,
    tim_cap_nut_co_gia,
)

CHUOI_10K = "PHA-" + ("A" * 9996)


def dien_an_toan(loc: Locator, gia_tri: str) -> None:
    """Điền giá trị vào ô nhập kể cả ngày bất hợp lệ hoặc vượt maxLength để thử sức bền."""
    try:
        loc.fill(gia_tri, timeout=4000)
    except Exception:
        # Một số ô type=date / datetime-local từ chối fill ngày sai chuẩn (vd 2026-02-30) -> gán qua DOM để thử phản ứng
        try:
            loc.evaluate(
                """(el, v) => {
                    const proto = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
                    if (proto && proto.set) proto.set.call(el, v);
                    else el.value = v;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }""",
                gia_tri,
            )
        except Exception:
            pass


def kiem_thong_bao_loi_va_tran(page: Page, scope_sel: str = "form.hop-thoai") -> dict:
    """Đọc các thông báo lỗi trong form/trang và kiểm tra chữ lỗi có bị tràn khung/bị che không."""
    return page.evaluate(
        """(sel) => {
            const root = document.querySelector(sel) || document.querySelector('main.trang') || document.body;
            const rootRect = root.getBoundingClientRect();
            const loiEls = Array.from(root.querySelectorAll('.loi, [role="alert"], [aria-invalid="true"]'));
            const cauLoi = [];
            const loiTran = [];
            for (const el of loiEls) {
                const st = getComputedStyle(el);
                if (st.display === 'none' || st.visibility === 'hidden') continue;
                const txt = (el.innerText || '').trim();
                if (txt) cauLoi.push(txt.slice(0, 120));
                const r = el.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) {
                    if (r.right > window.innerWidth + 2 || r.right > rootRect.right + 8) {
                        loiTran.push({ txt: txt.slice(0, 50), right: Math.round(r.right), rootRight: Math.round(rootRect.right) });
                    }
                    if ((st.overflowX === 'hidden' || st.overflowX === 'clip') && el.scrollWidth > el.clientWidth + 4) {
                        loiTran.push({ txt: txt.slice(0, 50), cat: true, sw: el.scrollWidth, cw: el.clientWidth });
                    }
                }
            }
            // Kiểm tra HTML5 validationMessage nếu trình duyệt chặn submit trước khi gọi API
            const invalidInputs = Array.from(root.querySelectorAll('input:invalid, select:invalid')).map(el => ({
                name: el.getAttribute('name') || el.getAttribute('aria-label') || el.type,
                msg: el.validationMessage || ''
            }));
            return {
                conMo: !!document.querySelector(sel),
                cauLoi,
                loiTran,
                invalidInputs: invalidInputs.slice(0, 4),
            };
        }""",
        scope_sel,
    )


def dong_hop_thoai_neu_mo(page: Page) -> None:
    try:
        form = page.locator("form.hop-thoai")
        if form.count() > 0 and form.first.is_visible():
            for nhan in ("Hủy", "Thôi", "Đóng"):
                btn = form.first.locator(f'button[type="button"]:has-text("{nhan}")')
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click(timeout=3000)
                    page.wait_for_timeout(200)
                    return
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
    except Exception:
        pass


def danh_gia_an_toan_form(
    mon: BoTheoDoi,
    info: dict,
    yeu_cau_chan: bool = True,
    yeu_cau_loi_vn: bool = False,
) -> tuple[bool, str, str]:
    bi_xss, xss_txt = mon.kiem_xss()
    if bi_xss:
        return False, f"PHÁT HIỆN XSS THỰC THI! {xss_txt}", "Nghiêm trọng"
    if mon.http_5xx:
        return False, f"Máy chủ trả 5xx: {mon.http_5xx[:2]}", "Nghiêm trọng"
    if mon.page_errors:
        return False, f"Lỗi JS pageerror: {mon.page_errors[:2]}", "Nghiêm trọng"
    van_de = []
    if info.get("loiTran"):
        van_de.append(f"Chữ lỗi bị tràn/cắt: {info['loiTran'][:2]}")
    if yeu_cau_chan and not info.get("conMo") and not info.get("cauLoi") and not info.get("invalidInputs"):
        van_de.append("Form tự đóng / lưu dữ liệu rác không báo lỗi")
    if yeu_cau_loi_vn and not info.get("cauLoi"):
        # Nếu chỉ có HTML5 native tooltip (có thể là tiếng Anh trên Chromium), ghi nhận rõ
        if info.get("invalidInputs"):
            msgs = [x["msg"] for x in info["invalidInputs"] if x["msg"]]
            # Kiểm tra có phải tiếng Anh mặc định không
            tieng_anh = any(
                w in m.lower() for m in msgs for w in ("please", "value must", "select an item", "fill out")
            )
            if tieng_anh:
                van_de.append(f"Chỉ hiện validation mặc định tiếng Anh thay vì lỗi tiếng Việt ngay ô nhập: {msgs[:2]}")
        else:
            van_de.append("Không thấy thông báo lỗi tiếng Việt hiển thị")
    if van_de:
        return False, " | ".join(van_de), "Vừa"
    return (
        True,
        f"Chặn an toàn, không XSS/5xx (lỗi UI={info['cauLoi'][:2]}, html5={len(info['invalidInputs'])})",
        "",
    )


def main() -> None:
    bc = BaoCaoScript(2, "Form nhập bừa qua giao diện Pixel (12+ form, XSS/SQLi/biên/ngày)", "ket_qua_02.json")

    api_dp = dang_nhap_api("dieuphoi")
    api_ql = dang_nhap_api("quanly")
    khach_id = lay_khach_hang_dau(api_dp)
    cap_nut = tim_cap_nut_co_gia(api_dp)

    # Tạo tài khoản PHA- riêng để thử Đổi mật khẩu (tuyệt đối không đổi mật khẩu demo12345 của 4 tài khoản chính)
    user_mk, pw_mk, _ = tao_tai_khoan_pha(api_ql, vai_tro="DIEU_PHOI")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =================================================================
            # A. VAI TRÒ ĐIỀU PHỐI: Tạo đơn, Lập chuyến, Xe, Tài xế, Khách hàng, Nút, Tuyến, Tìm chung
            # =================================================================
            ctx_dp = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx_dp)
            try:
                dang_nhap_nhanh(ctx_dp, page, "dieuphoi")

                # 1. Ô tìm kiếm trên cùng (TimChung)
                def test_tim_chung():
                    mon.reset()
                    o_tim = page.locator('.tim-chung input[type="search"], input[aria-label="Tìm chung"]').first
                    o_tim.wait_for(state="visible", timeout=6000)
                    payloads = ["", "a", XSS_SCRIPT, XSS_IMG, SQLI_PAYLOAD, EMOJI_PAYLOAD, CHUOI_10K[:2000]]
                    for pl in payloads:
                        dien_an_toan(o_tim, pl)
                        page.wait_for_timeout(350)
                    o_tim.press("Escape")
                    bi_xss, xss_txt = mon.kiem_xss()
                    if bi_xss:
                        return False, f"XSS ở ô tìm chung: {xss_txt}", "Nghiêm trọng"
                    if mon.http_5xx or mon.page_errors:
                        return False, f"5xx={mon.http_5xx[:2]}, pageerror={mon.page_errors[:2]}", "Nghiêm trọng"
                    return True, f"Đã thử {len(payloads)} payload ở Tìm chung: không 5xx/XSS/crash", ""

                bc.chay_ca(
                    "F01_TIM_CHUNG",
                    "Ô tìm kiếm trên cùng: rỗng, 1 ký tự, 2000 ký tự, emoji, XSS, SQLi",
                    test_tim_chung,
                    page=page,
                    tai_hien="Gõ lần lượt rỗng, XSS, SQLi, emoji, chuỗi dài vào ô Tìm chung trên thanh đầu",
                    mong_doi="Không 500, không màn trắng, không thực thi XSS",
                )

                # 2. Form Tạo đơn: số âm, 0, thập phân ở ô nguyên, 1e15, 10^19, ngày 30/02, 1900, 3000, XSS/SQLi/10k
                def test_tao_don_bien():
                    mon.reset()
                    _, truoc, _ = api_dp.raw("GET", "/api/don?so_dong=1")
                    tong_truoc = truoc["tong"] if isinstance(truoc, dict) else 0
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Tạo đơn")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)

                    # Thử submit rỗng
                    form.locator('button:has-text("Lưu đơn")').click(force=True)
                    page.wait_for_timeout(300)

                    # Điền các giá trị biên xấu
                    if khach_id:
                        form.locator("select").nth(0).select_option(str(khach_id))
                    if cap_nut:
                        form.locator("select").nth(1).select_option(str(cap_nut[0]))
                        form.locator("select").nth(2).select_option(str(cap_nut[1]))

                    nums = form.locator('input[type="number"]')
                    # kg âm, m3 = 0, so_kien = 1.5 (thập phân ở ô nguyên)
                    dien_an_toan(nums.nth(0), "-50")
                    dien_an_toan(nums.nth(1), "0")
                    dien_an_toan(nums.nth(2), "1.5")
                    dien_an_toan(form.locator("label", has_text="Mô tả hàng").locator("input"), XSS_SCRIPT)
                    dien_an_toan(form.locator("label", has_text="Địa chỉ lấy").locator("input"), XSS_IMG)
                    dien_an_toan(form.locator("label", has_text="SĐT lấy").locator("input"), SQLI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="Địa chỉ giao").locator("input"), CHUOI_10K[:1000])
                    dien_an_toan(form.locator("label", has_text="Người nhận").locator("input"), EMOJI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="SĐT nhận").locator("input"), "abc")
                    dien_an_toan(form.locator("label", has_text="Hạn giao").locator("input"), "1900-01-01T10:00")
                    form.locator('button:has-text("Lưu đơn")').click(force=True)
                    page.wait_for_timeout(600)

                    # Thử thêm số cực lớn 1e15 / 10^19 và ngày 30/02, năm 0000, năm 3000 (với kg/m3 hợp lệ để nút Lưu mở)
                    dien_an_toan(nums.nth(0), "100")
                    dien_an_toan(nums.nth(1), "1")
                    dien_an_toan(nums.nth(2), "10000000000000000000")  # 10^19
                    page.wait_for_timeout(500)
                    for ngay_xau in ("2026-02-30T10:00", "0000-01-01T10:00", "1900-01-01T10:00", "3000-01-01T10:00"):
                        dien_an_toan(form.locator("label", has_text="Hạn giao").locator("input"), ngay_xau)
                        btn_luu = form.locator('button:has-text("Lưu đơn")')
                        if btn_luu.is_enabled():
                            btn_luu.click()
                            page.wait_for_timeout(500)

                    info = kiem_thong_bao_loi_va_tran(page)
                    _, sau, _ = api_dp.raw("GET", "/api/don?so_dong=1")
                    tong_sau = sau["tong"] if isinstance(sau, dict) else 0
                    dong_hop_thoai_neu_mo(page)

                    ok, ly_do, muc = danh_gia_an_toan_form(mon, info, yeu_cau_chan=True)
                    if tong_sau > tong_truoc:
                        return False, f"DỮ LIỆU RÁC ĐÃ ĐƯỢC LƯU! tong đơn tăng {tong_truoc} -> {tong_sau} | {ly_do}", "Nghiêm trọng"
                    return ok, f"Đơn không tăng ({tong_truoc}->{tong_sau}) | {ly_do}", muc

                bc.chay_ca(
                    "F02_TAO_DON",
                    "Form Tạo đơn: số âm, 0, thập phân ở số kiện, 10^19, ngày 30/02/0/1900/3000, XSS/SQLi/10k",
                    test_tao_don_bien,
                    page=page,
                    tai_hien="Mở /dieu-phoi/don -> Tạo đơn -> nhập số âm/0/1.5/10^19/ngày xấu/XSS -> bấm Lưu đơn",
                    mong_doi="Chặn bằng thông báo lỗi tiếng Việt, không 500, không XSS, không lưu đơn rác",
                )

                # 3. Form Lập chuyến: rỗng, năm 0000, 1900, 3000
                def test_lap_chuyen_bien():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Lập chuyến")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    sel_tuyen = form.locator("select").first
                    if sel_tuyen.locator("option").count() > 1:
                        sel_tuyen.select_option(index=1)
                    o_gio = form.locator('input[type="datetime-local"]').first
                    for ngay_xau in ("", "2026-02-30T08:00", "0000-01-01T08:00", "1900-01-01T08:00", "3000-01-01T08:00"):
                        dien_an_toan(o_gio, ngay_xau)
                        page.wait_for_timeout(350)
                    info = kiem_thong_bao_loi_va_tran(page)
                    dong_hop_thoai_neu_mo(page)
                    return danh_gia_an_toan_form(mon, info, yeu_cau_chan=True)

                bc.chay_ca(
                    "F03_LAP_CHUYEN",
                    "Form Lập chuyến: giờ khởi hành rỗng, 30/02, năm 0, 1900, 3000",
                    test_lap_chuyen_bien,
                    page=page,
                    tai_hien="Mở /dieu-phoi/chuyen -> Lập chuyến -> chọn tuyến -> nhập các ngày biên",
                    mong_doi="Không 500, không crash khi hỏi xe/tài xế khả dụng, chặn ngày bất hợp lệ",
                )

                # 4. Form Thêm xe: số âm, 0, 1e15, 10^19, thập phân ở kg, ngày 1900/3000, XSS/SQLi/10k
                def test_them_xe():
                    mon.reset()
                    _, truoc, _ = api_dp.raw("GET", "/api/xe?so_dong=1")
                    tong_truoc = truoc["tong"] if isinstance(truoc, dict) else 0
                    page.goto(f"{BASE_FE}/dieu-phoi/xe", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Thêm xe")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)

                    # Rỗng
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(200)

                    # XSS + số âm + thập phân ở ô nguyên + 10^19 + ngày xấu
                    dien_an_toan(form.locator("label", has_text="Biển số").locator("input"), XSS_SCRIPT)
                    dien_an_toan(form.locator("label", has_text="Tải trọng").locator("input"), "-100")
                    dien_an_toan(form.locator("label", has_text="Khối lượng toàn bộ").locator("input"), "10000000000000000000")
                    dien_an_toan(form.locator("label", has_text="Thể tích").locator("input"), "0")
                    dien_an_toan(form.locator("label", has_text="Định mức dầu").locator("input"), "-5.5")
                    dien_an_toan(form.locator("label", has_text="Hạn đăng kiểm").locator("input"), "1900-01-01")
                    dien_an_toan(form.locator("label", has_text="Hạn bảo hiểm").locator("input"), "3000-01-01")
                    dien_an_toan(form.locator("label", has_text="Km đồng hồ").locator("input"), "12.5")
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(600)

                    # Gỡ novalidate tạm chỉ để kiểm phản hồi backend + hiển thị lỗi UI khi gửi 1e15 / XSS
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    dien_an_toan(form.locator("label", has_text="Tải trọng").locator("input"), "1000000000000000")
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(700)

                    info = kiem_thong_bao_loi_va_tran(page)
                    _, sau, _ = api_dp.raw("GET", "/api/xe?so_dong=1")
                    tong_sau = sau["tong"] if isinstance(sau, dict) else 0
                    dong_hop_thoai_neu_mo(page)
                    ok, ly_do, muc = danh_gia_an_toan_form(mon, info, yeu_cau_chan=True)
                    if tong_sau > tong_truoc:
                        return False, f"Lưu được xe rác! tong xe {tong_truoc}->{tong_sau} | {ly_do}", "Nghiêm trọng"
                    return ok, f"Số xe không đổi ({tong_truoc}) | {ly_do}", muc

                bc.chay_ca(
                    "F04_THEM_XE",
                    "Form Thêm xe: biển số XSS, tải âm/1e15/10^19, km thập phân, ngày 1900/3000",
                    test_them_xe,
                    page=page,
                    tai_hien="Mở /dieu-phoi/xe -> Thêm xe -> nhập dữ liệu biên/XSS -> Lưu",
                    mong_doi="Báo lỗi tiếng Việt ngay ô nhập, không 500, không XSS, không lưu xe rác",
                )

                # 5. Form Thêm tài xế: rỗng, XSS, SQLi, emoji, 10k, ngày GPLX 1900/3000
                def test_them_tai_xe():
                    mon.reset()
                    _, truoc, _ = api_dp.raw("GET", "/api/tai-xe?so_dong=1")
                    tong_truoc = truoc["tong"] if isinstance(truoc, dict) else 0
                    page.goto(f"{BASE_FE}/dieu-phoi/tai-xe", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Thêm tài xế")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    dien_an_toan(form.locator("label", has_text="Họ tên").locator("input"), XSS_IMG + EMOJI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="Tên đăng nhập").locator("input"), SQLI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="Mật khẩu").locator("input"), "123")
                    dien_an_toan(form.locator("label", has_text="Số GPLX").locator("input"), "12")
                    dien_an_toan(form.locator("label", has_text="Hạn GPLX").locator("input"), "1900-01-01")
                    dien_an_toan(form.locator("label", has_text="Số điện thoại").locator("input"), "khongphaisdt")
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(700)
                    info = kiem_thong_bao_loi_va_tran(page)
                    _, sau, _ = api_dp.raw("GET", "/api/tai-xe?so_dong=1")
                    tong_sau = sau["tong"] if isinstance(sau, dict) else 0
                    dong_hop_thoai_neu_mo(page)
                    ok, ly_do, muc = danh_gia_an_toan_form(mon, info, yeu_cau_chan=True, yeu_cau_loi_vn=True)
                    if tong_sau > tong_truoc:
                        return False, f"Lưu được tài xế rác! {tong_truoc}->{tong_sau} | {ly_do}", "Nghiêm trọng"
                    return ok, f"Số tài xế không đổi ({tong_truoc}) | {ly_do}", muc

                bc.chay_ca(
                    "F05_THEM_TAI_XE",
                    "Form Thêm tài xế: XSS/emoji, SQLi username, mật khẩu < 8, SĐT chữ, ngày 1900",
                    test_them_tai_xe,
                    page=page,
                    tai_hien="Mở /dieu-phoi/tai-xe -> Thêm tài xế -> nhập XSS/SQLi/SĐT sai -> Lưu",
                    mong_doi="Hiện lỗi tiếng Việt ngay ô nhập, không 500, không XSS, không lưu dữ liệu rác",
                )

                # 6. Form Thêm khách hàng: rỗng, 10.000 ký tự, XSS, SQLi, emoji
                def test_them_khach():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/khach-hang", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Thêm khách hàng")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    # Lần 1: 10.000 ký tự + SĐT sai -> phải bị chặn
                    dien_an_toan(form.locator("label", has_text="Tên khách hàng").locator("input"), CHUOI_10K)
                    dien_an_toan(form.locator("label", has_text="Số điện thoại").locator("input"), SQLI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="Mã số thuế").locator("input"), XSS_SCRIPT)
                    dien_an_toan(form.locator("label", has_text="Địa chỉ").locator("input"), XSS_IMG)
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(700)
                    info = kiem_thong_bao_loi_va_tran(page)
                    dong_hop_thoai_neu_mo(page)
                    return danh_gia_an_toan_form(mon, info, yeu_cau_chan=True, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F06_THEM_KHACH",
                    "Form Thêm khách hàng: 10.000 ký tự, SĐT SQLi, MST/địa chỉ XSS",
                    test_them_khach,
                    page=page,
                    tai_hien="Mở /dieu-phoi/khach-hang -> Thêm khách hàng -> nhập 10k ký tự + SQLi + XSS -> Lưu",
                    mong_doi="Báo lỗi tiếng Việt ngay ô nhập, không tràn lỗi, không 500, không XSS",
                )

                # 7. Form Thêm nút: tọa độ rác, tên 10k, XSS, SQLi
                def test_them_nut():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/nut", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Thêm nút")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    dien_an_toan(form.locator("label", has_text="Tên nút").locator("input"), CHUOI_10K)
                    dien_an_toan(form.locator("label", has_text="Tỉnh").locator("input"), XSS_SCRIPT)
                    dien_an_toan(form.locator("label", has_text="Vĩ độ").locator("input"), "999999")
                    dien_an_toan(form.locator("label", has_text="Kinh độ").locator("input"), "-999999")
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(700)
                    info = kiem_thong_bao_loi_va_tran(page)
                    dong_hop_thoai_neu_mo(page)
                    return danh_gia_an_toan_form(mon, info, yeu_cau_chan=True, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F07_THEM_NUT",
                    "Form Thêm nút: tên 10.000 ký tự, tỉnh XSS, tọa độ vượt chuẩn (±999999)",
                    test_them_nut,
                    page=page,
                    tai_hien="Mở /dieu-phoi/nut -> Thêm nút -> nhập 10k + XSS + vĩ độ 999999 -> Lưu",
                    mong_doi="Báo lỗi tiếng Việt, không 500, không XSS, không lưu dữ liệu rác",
                )

                # 8. Form Thêm tuyến: định mức âm, 10^19, phút > 600 (BR-66), tên XSS
                def test_them_tuyen():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/tuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    page.locator('button:has-text("Thêm tuyến")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    dien_an_toan(form.locator("label", has_text="Mã tuyến").locator("input"), f"PHA-{ma_ngau_nhien(4)}")
                    dien_an_toan(form.locator("label", has_text="Tên tuyến").locator("input"), XSS_IMG)
                    dien_an_toan(form.locator("label", has_text="Định mức dầu").locator("input"), "-10000")
                    dien_an_toan(form.locator("label", has_text="Định mức cầu đường").locator("input"), "10000000000000000000")
                    dien_an_toan(form.locator("label", has_text="Định mức bốc xếp").locator("input"), "12.5")
                    dien_an_toan(form.locator("label", has_text="Lương khoán").locator("input"), "-500")
                    sel = form.locator("table select").first
                    if sel.locator("option").count() > 1:
                        sel.select_option(index=1)
                    dien_an_toan(form.locator('input[aria-label="Phút nút 1"]'), "9999")
                    form.locator('button:has-text("Lưu")').click()
                    page.wait_for_timeout(700)
                    info = kiem_thong_bao_loi_va_tran(page)
                    dong_hop_thoai_neu_mo(page)
                    return danh_gia_an_toan_form(mon, info, yeu_cau_chan=True, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F08_THEM_TUYEN",
                    "Form Thêm tuyến: định mức âm/10^19/thập phân, phút 9999, tên XSS",
                    test_them_tuyen,
                    page=page,
                    tai_hien="Mở /dieu-phoi/tuyen -> Thêm tuyến -> nhập định mức âm/10^19/thập phân + XSS -> Lưu",
                    mong_doi="Báo lỗi tiếng Việt, không 500, không XSS, không lưu tuyến rác",
                )
            finally:
                ctx_dp.close()

            # =================================================================
            # B. VAI TRÒ QUẢN LÝ: Bảng giá
            # =================================================================
            ctx_ql = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page_ql, mon_ql = mo_trang_moi(ctx_ql)
            try:
                dang_nhap_nhanh(ctx_ql, page_ql, "quanly")

                def test_bang_gia():
                    mon_ql.reset()
                    page_ql.goto(f"{BASE_FE}/quan-ly/bang-gia", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_ql, ms=400)
                    page_ql.locator('button:has-text("Thêm mức giá")').first.click()
                    form = page_ql.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=6000)
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    dien_an_toan(form.locator("label", has_text="Tỉnh lấy").locator("input"), XSS_SCRIPT)
                    dien_an_toan(form.locator("label", has_text="Tỉnh giao").locator("input"), SQLI_PAYLOAD)
                    dien_an_toan(form.locator("label", has_text="Đơn giá").locator("input"), "-500")
                    dien_an_toan(form.locator("label", has_text="Cước tối thiểu").locator("input"), "10000000000000000000")
                    dien_an_toan(form.locator("label", has_text="Hiệu lực từ ngày").locator("input"), "1900-01-01")
                    form.locator('button:has-text("Lưu")').click()
                    page_ql.wait_for_timeout(700)
                    info = kiem_thong_bao_loi_va_tran(page_ql)
                    dong_hop_thoai_neu_mo(page_ql)
                    return danh_gia_an_toan_form(mon_ql, info, yeu_cau_chan=True, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F09_BANG_GIA",
                    "Form Bảng giá: đơn giá âm, cước tối thiểu 10^19, tỉnh XSS/SQLi, ngày 1900",
                    test_bang_gia,
                    page=page_ql,
                    tai_hien="Đăng nhập quanly -> /quan-ly/bang-gia -> Thêm mức giá -> nhập biên/XSS -> Lưu",
                    mong_doi="Báo lỗi tiếng Việt ngay ô nhập, không 500, không XSS",
                )
            finally:
                ctx_ql.close()

            # =================================================================
            # C. VAI TRÒ KẾ TOÁN: Tạm ứng
            # =================================================================
            ctx_kt = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page_kt, mon_kt = mo_trang_moi(ctx_kt)
            try:
                dang_nhap_nhanh(ctx_kt, page_kt, "ketoan")

                def test_tam_ung():
                    mon_kt.reset()
                    page_kt.goto(f"{BASE_FE}/ke-toan/tam-ung", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_kt, ms=500)
                    sel = page_kt.locator("select").first
                    if sel.locator("option").count() <= 1:
                        return True, "Không có chuyến DA_CHOT/DANG_CHAY để mở form cấp tạm ứng (bỏ qua an toàn)", ""
                    # Tìm chuyến có form cấp tạm ứng (DA_CHOT / DANG_CHAY)
                    da_chon = False
                    for idx in range(1, min(sel.locator("option").count(), 10)):
                        sel.select_option(index=idx)
                        page_kt.wait_for_timeout(400)
                        if page_kt.locator('button:has-text("Cấp tạm ứng")').count() > 0:
                            da_chon = True
                            break
                    if not da_chon:
                        return True, "Các chuyến hiện có đều ở HOAN_THANH (chỉ sửa/thu hồi, không có form cấp mới)", ""

                    form = page_kt.locator("form.o-nhap").first
                    form.evaluate("f => f.setAttribute('novalidate', '')")
                    o_tien = form.locator('input[type="number"]').first
                    for gt in ("", "-100000", "0", "100.5", "1000000000000000", "10000000000000000000"):
                        dien_an_toan(o_tien, gt)
                        form.locator('button:has-text("Cấp tạm ứng")').click()
                        page_kt.wait_for_timeout(450)
                    info = kiem_thong_bao_loi_va_tran(page_kt, scope_sel="main.trang")
                    return danh_gia_an_toan_form(mon_kt, info, yeu_cau_chan=False, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F10_TAM_UNG",
                    "Form Tạm ứng: rỗng, số âm, 0, thập phân 100.5, 1e15, 10^19",
                    test_tam_ung,
                    page=page_kt,
                    tai_hien="Đăng nhập ketoan -> /ke-toan/tam-ung -> chọn chuyến -> nhập các số tiền bất hợp lệ -> Cấp tạm ứng",
                    mong_doi="Hiện lỗi tiếng Việt, không 500, không cấp tạm ứng rác",
                )
            finally:
                ctx_kt.close()

            # =================================================================
            # D. VAI TRÒ TÀI XẾ: Chi phí & Sự cố
            # =================================================================
            ctx_tx = tao_context_pixel(browser, viewport={"width": 390, "height": 844})
            page_tx, mon_tx = mo_trang_moi(ctx_tx)
            try:
                api_tx = dang_nhap_api("taixe")
                st_c, r_c, _ = api_tx.raw("GET", "/api/toi/chuyen?nhom=can_lam&so_dong=10")
                ch_chay = None
                if st_c == 200 and isinstance(r_c, dict):
                    for item in r_c.get("du_lieu", []):
                        if item.get("trang_thai") == "DANG_CHAY":
                            ch_chay = item
                            break
                dang_nhap_nhanh(ctx_tx, page_tx, "taixe")

                def test_chi_phi_su_co():
                    if not ch_chay:
                        return True, "Tài xế demo chưa có chuyến DANG_CHAY sẵn (không thay đổi chuyến có sẵn)", ""
                    mon_tx.reset()
                    page_tx.goto(f"{BASE_FE}/tai-xe/chuyen/{ch_chay['id']}", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_tx, ms=500)

                    # Form Chi phí
                    btn_cp = page_tx.locator('button:has-text("Ghi chi phí")').first
                    if btn_cp.count() > 0:
                        form_cp = btn_cp.locator("xpath=ancestor::form").first
                        form_cp.evaluate("f => f.setAttribute('novalidate', '')")
                        nums = form_cp.locator('input[type="number"]')
                        dien_an_toan(nums.nth(0), "-50000")
                        if nums.count() > 1:
                            dien_an_toan(nums.nth(1), "-10")
                        dien_an_toan(form_cp.locator("label", has_text="Ghi chú").locator("input"), XSS_SCRIPT)
                        btn_cp.click()
                        page_tx.wait_for_timeout(500)
                        dien_an_toan(nums.nth(0), "10000000000000000000")
                        btn_cp.click()
                        page_tx.wait_for_timeout(500)

                    # Form Sự cố (gửi ghi chú rỗng, sau đó không gửi dữ liệu hợp lệ để khỏi làm bẩn chuyến sẵn)
                    btn_sc = page_tx.locator('button:has-text("Báo sự cố")').first
                    if btn_sc.count() > 0:
                        form_sc = btn_sc.locator("xpath=ancestor::form").first
                        dien_an_toan(form_sc.locator("label", has_text="Ghi chú").locator("input"), "   ")
                        btn_sc.click()
                        page_tx.wait_for_timeout(400)

                    info = kiem_thong_bao_loi_va_tran(page_tx, scope_sel="main.trang")
                    return danh_gia_an_toan_form(mon_tx, info, yeu_cau_chan=False, yeu_cau_loi_vn=True)

                bc.chay_ca(
                    "F11_CHI_PHI_SU_CO",
                    "Form Chi phí & Sự cố (tài xế): số âm, 10^19, XSS, ghi chú rỗng",
                    test_chi_phi_su_co,
                    page=page_tx,
                    tai_hien="Đăng nhập taixe -> mở chuyến DANG_CHAY -> nhập số âm/10^19/XSS vào Chi phí & rỗng vào Sự cố",
                    mong_doi="Hiện thông báo lỗi tiếng Việt, không 500, không XSS",
                )
            finally:
                ctx_tx.close()

            # =================================================================
            # E. FORM ĐỔI MẬT KHẨU (trên tài khoản PHA- riêng)
            # =================================================================
            ctx_mk = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page_mk, mon_mk = mo_trang_moi(ctx_mk)
            try:
                dang_nhap_nhanh(ctx_mk, page_mk, user_mk, pw_mk)

                def test_doi_mk():
                    mon_mk.reset()
                    page_mk.goto(f"{BASE_FE}/tai-khoan", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_mk, ms=400)
                    form = page_mk.locator("form.tk-mk").first
                    form.wait_for(state="visible", timeout=6000)
                    o_cu = form.locator("label", has_text="Mật khẩu hiện tại").locator("input")
                    o_moi = form.locator("label", has_text="Mật khẩu mới").first.locator("input")
                    o_lai = form.locator("label", has_text="Nhập lại mật khẩu mới").locator("input")
                    btn = form.locator('button:has-text("Đổi mật khẩu")')

                    cac_ca = [
                        (pw_mk, "123", "123"),  # ngắn < 8
                        (pw_mk, "abcdefgh1", "abcdefgh2"),  # không khớp
                        (pw_mk, "A" * 250, "A" * 250),  # > 200 ký tự
                        (pw_mk, pw_mk, pw_mk),  # trùng mật khẩu cũ
                        (pw_mk, XSS_SCRIPT, XSS_SCRIPT),  # XSS (nếu lưu được thì đổi lại, không để alert)
                    ]
                    loi_thay = []
                    for cu, moi, lai in cac_ca[:4]:
                        dien_an_toan(o_cu, cu)
                        dien_an_toan(o_moi, moi)
                        dien_an_toan(o_lai, lai)
                        if btn.is_enabled():
                            btn.click()
                            page_mk.wait_for_timeout(450)
                            t = form.locator('[role="alert"]').inner_text() if form.locator('[role="alert"]').count() else ""
                            loi_thay.append(t)

                    info = kiem_thong_bao_loi_va_tran(page_mk, scope_sel="form.tk-mk")
                    ok, ly_do, muc = danh_gia_an_toan_form(mon_mk, info, yeu_cau_chan=False, yeu_cau_loi_vn=True)
                    return ok, f"Các lỗi đã hiện={loi_thay[:3]} | {ly_do}", muc

                bc.chay_ca(
                    "F12_DOI_MAT_KHAU",
                    f"Form Đổi mật khẩu (tài khoản {user_mk}): ngắn < 8, không khớp, > 200 ký tự, trùng cũ",
                    test_doi_mk,
                    page=page_mk,
                    tai_hien=f"Đăng nhập {user_mk} -> /tai-khoan -> thử các mật khẩu không hợp lệ",
                    mong_doi="Hiện lỗi tiếng Việt rõ ràng ngay trong form, không 500, không XSS",
                )
            finally:
                ctx_mk.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
