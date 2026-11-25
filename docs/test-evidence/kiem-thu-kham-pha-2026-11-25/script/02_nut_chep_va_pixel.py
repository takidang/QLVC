#!/usr/bin/env python3
"""
02_nut_chep_va_pixel.py - Kiểm thử NutChep.tsx và giao diện Pixel (qlvc-phong-cach=pixel)
ở 3 cỡ màn hình: 1440x900, 1024x768, 390x844.

Kiểm tra:
- Phần A: NutChep ở cả 4 vị trí (Tài xế, Khách hàng, Chi tiết chuyến/KhoiXe, Chuyến của tôi/Tài xế)
  ở phong cách Thường và Pixel: chép thành công + toast, lỗi clipboard + toast lỗi,
  stopPropagation (không kích hoạt dòng/link cha), kích thước & không bị che.
- Phần B: Quét tất cả các trang theo từng vai trò ở chế độ Pixel tại 1440 px, 1024 px, 390 px:
  màn trắng, lỗi console/pageerror/API 5xx, cuộn ngang trang, chữ tràn thực, nút chính bị che.
- Phần C: 7 hộp thoại dài trong Pixel ở 1440 px, 1024 px, 390 px: cuộn tới nút Lưu và bấm được
  (không bị cắt/che bởi thanh menu đáy hay tràn ngang).

Chạy độc lập: py -3.12 -I -X utf8 kiem-thu-kham-pha/02_nut_chep_va_pixel.py
"""

from __future__ import annotations

import json
import re
import sys
import traceback
import urllib.error
import urllib.request
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

FRONTEND = "http://127.0.0.1:5173"
BACKEND = "http://127.0.0.1:8000"
VIEWPORTS = [
    ("1440", {"width": 1440, "height": 900}),
    ("1024", {"width": 1024, "height": 768}),
    ("390", {"width": 390, "height": 844}),
]


class ApiClient:
    def __init__(self, base: str = BACKEND):
        self.base = base.rstrip("/")
        self.token: str | None = None

    def request(self, method: str, path: str, json_body: Any = None) -> tuple[int, Any]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Cookie"] = f"access_token={self.token}"
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(f"{self.base}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read()
                for sc in r.headers.get_all("Set-Cookie") or []:
                    m = re.search(r"access_token=([^;]+)", sc)
                    if m:
                        self.token = m.group(1)
                return r.status, json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                body = json.loads(raw.decode("utf-8")) if raw else None
            except Exception:
                body = raw.decode("utf-8", errors="replace")
            return e.code, body

    def dang_nhap(self, u: str, p: str = "demo12345") -> None:
        st, body = self.request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": u, "mat_khau": p})
        if st != 200:
            raise RuntimeError(f"Đăng nhập {u} lỗi {st}: {body}")


class KetQua:
    def __init__(self) -> None:
        self.ds: list[tuple[str, str, str]] = []

    def ghi(self, ma: str, dat: bool, ly_do: str) -> None:
        tt = "ĐẠT" if dat else "LỖI"
        self.ds.append((ma, tt, ly_do))
        print(f"[{tt}] {ma}: {ly_do}", flush=True)

    def bo_qua(self, ma: str, ly_do: str) -> None:
        self.ds.append((ma, "BO_QUA", ly_do))
        print(f"[BỎ QUA] {ma}: {ly_do}", flush=True)

    def tong_ket(self) -> int:
        dat = sum(1 for _, t, _ in self.ds if t == "ĐẠT")
        loi = sum(1 for _, t, _ in self.ds if t == "LỖI")
        bq = sum(1 for _, t, _ in self.ds if t == "BO_QUA")
        print(f"\n=== TỔNG KẾT 02_nut_chep_va_pixel: tổng={len(self.ds)} | đạt={dat} | lỗi={loi} | bỏ qua={bq} ===")
        return 1 if loi else 0


CLIPBOARD_HOOK = r"""
(() => {
  window.__phaCopied = [];
  window.__phaClipFail = false;
  const fakeClip = {
    writeText: async (text) => {
      if (window.__phaClipFail) throw new Error('Clipboard bị từ chối');
      window.__phaCopied.push(String(text));
    },
  };
  try {
    Object.defineProperty(navigator, 'clipboard', {
      value: fakeClip,
      configurable: true,
    });
  } catch (_) {}
})();
"""


def lay_id_mau() -> dict[str, Any]:
    """Đọc ID chuyến/đơn có sẵn trong CSDL thử (chỉ đọc, không sửa gì)."""
    dp = ApiClient()
    dp.dang_nhap("dieuphoi")
    st, ch = dp.request("GET", "/api/chuyen?so_dong=10")
    cid = ch["du_lieu"][0]["id"] if st == 200 and ch["du_lieu"] else None
    st, don = dp.request("GET", "/api/don?so_dong=10")
    did = don["du_lieu"][0]["id"] if st == 200 and don["du_lieu"] else None

    # Tìm tài xế mẫu nào có chuyến can_lam (có điểm chưa xong để thấy NutChep trên thẻ điểm dừng)
    tx_user = "taixe01"
    tx_cid = None
    for u in ["taixe01", "taixe02", "taixe03", "taixe04", "taixe05"]:
        tx = ApiClient()
        try:
            tx.dang_nhap(u)
        except Exception:
            continue
        st, r = tx.request("GET", "/api/toi/chuyen?nhom=can_lam&so_dong=10")
        if st == 200 and r["du_lieu"]:
            for c in r["du_lieu"]:
                if c.get("so_don", 0) > 0:
                    tx_user, tx_cid = u, c["id"]
                    break
        if tx_cid:
            break
    if not tx_cid:
        tx = ApiClient()
        tx.dang_nhap("taixe01")
        st, r = tx.request("GET", "/api/toi/chuyen?nhom=da_xong&so_dong=5")
        if st == 200 and r["du_lieu"]:
            tx_cid = r["du_lieu"][0]["id"]
    return {"cid": cid, "did": did, "tx_user": tx_user, "tx_cid": tx_cid}


def tao_phien(
    browser: Browser,
    viewport: dict[str, int],
    pixel: bool,
    tai_khoan: str | None = None,
) -> tuple[BrowserContext, Page, list[str], list[str], list[str]]:
    ctx = browser.new_context(viewport=viewport)
    if pixel:
        ctx.add_init_script("localStorage.setItem('qlvc-phong-cach', 'pixel');")
    else:
        ctx.add_init_script("localStorage.removeItem('qlvc-phong-cach');")
    ctx.add_init_script(CLIPBOARD_HOOK)
    page = ctx.new_page()
    console_errs: list[str] = []
    page_errs: list[str] = []
    api_5xx: list[str] = []

    page.on("console", lambda m: console_errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errs.append(str(e)))
    page.on(
        "response",
        lambda r: api_5xx.append(f"{r.status} {r.url}")
        if "/api/" in r.url and r.status >= 500
        else None,
    )

    page.goto(f"{FRONTEND}/dang-nhap", wait_until="domcontentloaded")
    if tai_khoan:
        st = page.evaluate(
            """async (u) => {
              const r = await fetch('/api/auth/dang-nhap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ ten_dang_nhap: u, mat_khau: 'demo12345' }),
              });
              return r.status;
            }""",
            tai_khoan,
        )
        if st != 200:
            raise RuntimeError(f"Đăng nhập {tai_khoan} thất bại: {st}")
    return ctx, page, console_errs, page_errs, api_5xx


def kiem_tra_nut_chep_tren_trang(
    page: Page,
    kq: KetQua,
    ma: str,
    url: str,
    console_errs: list[str],
    page_errs: list[str],
) -> None:
    console_errs.clear()
    page_errs.clear()
    page.goto(f"{FRONTEND}{url}", wait_until="networkidle")
    page.wait_for_timeout(600)
    nut = page.locator("button.nut-chep").first
    if nut.count() == 0:
        kq.bo_qua(ma, f"Trang {url} không có button.nut-chep hiển thị (có thể bảng rỗng hoặc điểm đã xong)")
        return
    try:
        nut.wait_for(state="visible", timeout=5000)
    except Exception:
        kq.bo_qua(ma, f"Trang {url} có button.nut-chep nhưng không hiển thị")
        return

    nut.scroll_into_view_if_needed()
    page.wait_for_timeout(150)

    # Kiểm tra kích thước, viền, và không bị phần tử khác che (elementFromPoint)
    info = nut.evaluate(
        """(el) => {
          const r = el.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const topEl = document.elementFromPoint(cx, cy);
          const cs = getComputedStyle(el);
          return {
            w: Math.round(r.width),
            h: Math.round(r.height),
            aria: el.getAttribute('aria-label') || '',
            hitOk: !!topEl && (topEl === el || el.contains(topEl)),
            topTag: topEl ? `${topEl.tagName}.${topEl.className}` : 'null',
            borderWidth: cs.borderTopWidth,
            borderColor: cs.borderTopColor,
          };
        }"""
    )

    url_truoc = page.url
    # 1. Test chép thành công
    page.evaluate("() => { window.__phaCopied = []; window.__phaClipFail = false; }")
    nut.click()
    page.wait_for_timeout(350)
    copied = page.evaluate("() => window.__phaCopied")
    url_sau = page.url
    toast_ok = page.locator("[data-sonner-toast]").filter(has_text="Đã chép").count() > 0

    # 2. Test fallback khi clipboard bị từ chối
    page.evaluate("() => { window.__phaClipFail = true; }")
    nut.click()
    page.wait_for_timeout(350)
    toast_loi = page.locator("[data-sonner-toast]").filter(has_text="Không chép được").count() > 0

    dat = (
        info["w"] >= 24
        and info["h"] >= 24
        and info["hitOk"]
        and len(copied) == 1
        and copied[0] in info["aria"]
        and toast_ok
        and toast_loi
        and (url_truoc == url_sau)
        and not console_errs
        and not page_errs
    )
    kq.ghi(
        ma,
        dat,
        f"size={info['w']}x{info['h']}, hitOk={info['hitOk']} ({info['topTag']}), "
        f"copied={copied}, toast_ok={toast_ok}, toast_loi={toast_loi}, "
        f"khong_nhay_trang={url_truoc == url_sau}, border={info['borderWidth']} {info['borderColor']}, "
        f"errs={len(console_errs) + len(page_errs)}",
    )


AUDIT_PIXEL_JS = r"""
() => {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const root = document.documentElement;
  const main = document.querySelector('main');
  const textLen = (document.body.innerText || '').trim().length;
  const mainOpacity = main ? parseFloat(getComputedStyle(main).opacity) : 1;
  const cuonNgangPx = Math.round(root.scrollWidth - vw);

  const laAn = (el) => {
    if (!el || !(el instanceof HTMLElement)) return true;
    if (el.closest('details:not([open])')) return true;
    if (el.closest('[hidden], .an-chu, .giu-cho, [aria-hidden="true"]')) return true;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return true;
    const r = el.getBoundingClientRect();
    return r.width < 1 || r.height < 1;
  };

  // 1. Kiểm tra chữ bị tràn khỏi khung (bỏ qua input/textarea và phần tử nằm trong khung cuộn ngang .bang-khung/.lich-gio)
  const chuTran = [];
  const cands = document.querySelectorAll('main h1, main h2, main h3, main button, main .nhan, main .bien');
  for (const el of cands) {
    if (laAn(el)) continue;
    if (el.closest('.bang-khung, .lich-gio, .vien-thuoc')) continue;
    const cs = getComputedStyle(el);
    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue;
    if (el.scrollWidth > el.clientWidth + 3) {
      chuTran.push(`${el.tagName}(${(el.textContent || '').trim().slice(0, 25)}): ${el.scrollWidth}>${el.clientWidth}`);
      if (chuTran.length >= 5) break;
    }
  }

  // 2. Kiểm tra nút hiển thị bị phần tử khác che không bấm được (tối đa 12 nút đầu trong main)
  const nutBiChe = [];
  const btns = Array.from(document.querySelectorAll('main button:enabled')).filter((b) => !laAn(b));
  for (const b of btns.slice(0, 12)) {
    b.scrollIntoView({ block: 'center', inline: 'nearest' });
    const r = b.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    const cx = Math.min(Math.max(r.left + r.width / 2, 1), vw - 1);
    const cy = Math.min(Math.max(r.top + r.height / 2, 1), vh - 1);
    const topEl = document.elementFromPoint(cx, cy);
    if (topEl && topEl !== b && !b.contains(topEl) && !topEl.contains(b)) {
      nutBiChe.push(
        `btn(${(b.textContent || b.getAttribute('aria-label') || '').trim().slice(0, 22)}) bi che boi ${topEl.tagName}.${String(topEl.className || '').slice(0, 30)}`
      );
      if (nutBiChe.length >= 4) break;
    }
  }
  window.scrollTo(0, 0);

  return {
    phongCach: root.dataset.phongCach || '',
    textLen,
    mainOpacity,
    cuonNgangPx,
    chuTran,
    nutBiChe,
  };
}
"""


def quet_trang_pixel(
    page: Page,
    kq: KetQua,
    ma: str,
    url: str,
    console_errs: list[str],
    page_errs: list[str],
    api_5xx: list[str],
) -> None:
    console_errs.clear()
    page_errs.clear()
    api_5xx.clear()
    page.goto(f"{FRONTEND}{url}", wait_until="networkidle")
    # Chờ hiệu ứng tải tối đa ~1.7s (data-px-cho timeout 1.5s)
    page.wait_for_timeout(1700)
    res = page.evaluate(AUDIT_PIXEL_JS)
    man_trang = res["textLen"] < 20 or res["mainOpacity"] < 0.5
    dat = (
        res["phongCach"] == "pixel"
        and not man_trang
        and res["cuonNgangPx"] <= 1
        and not res["chuTran"]
        and not res["nutBiChe"]
        and not console_errs
        and not page_errs
        and not api_5xx
    )
    ly_do = (
        f"textLen={res['textLen']}, opacity={res['mainOpacity']}, cuonNgang={res['cuonNgangPx']}px, "
        f"chuTran={res['chuTran']}, nutBiChe={res['nutBiChe']}, "
        f"consoleErr={console_errs[:2]}, pageErr={page_errs[:2]}, api5xx={api_5xx[:2]}"
    )
    kq.ghi(ma, dat, ly_do)


def kiem_hop_thoai_pixel(
    page: Page,
    kq: KetQua,
    ma: str,
    url: str,
    ten_nut_mo: str,
    ten_nut_luu: str,
    them_nut_tuyen: bool = False,
) -> None:
    page.goto(f"{FRONTEND}{url}", wait_until="networkidle")
    page.wait_for_timeout(600)
    nut_mo = page.get_by_role("button", name=ten_nut_mo).first
    if nut_mo.count() == 0:
        kq.bo_qua(ma, f"Không tìm thấy nút {ten_nut_mo!r} ở {url}")
        return
    nut_mo.click()
    hop = page.locator(".nen-mo .hop-thoai").last
    hop.wait_for(state="visible", timeout=5000)

    if them_nut_tuyen:
        # Thêm 3 dòng nút để kiểm tra cuộn hộp thoại dài trên màn hình hẹp 390px
        nut_them = hop.get_by_role("button", name="+ Thêm nút")
        for _ in range(3):
            if nut_them.is_visible():
                nut_them.click()
        page.wait_for_timeout(150)

    res = page.evaluate(
        """(tenLuu) => {
          const vw = window.innerWidth;
          const vh = window.innerHeight;
          const hop = Array.from(document.querySelectorAll('.nen-mo .hop-thoai')).pop();
          if (!hop) return { ok: false, lyDo: 'Khong thay .hop-thoai' };
          const hr = hop.getBoundingClientRect();
          const tranNgang = hr.left < -2 || hr.right > vw + 2;
          // Cuộn hộp thoại xuống đáy
          hop.scrollTop = hop.scrollHeight;
          const btns = Array.from(hop.querySelectorAll('button'));
          const luu = btns.find((b) => (b.textContent || '').trim() === tenLuu) || btns[btns.length - 1];
          if (!luu) return { ok: false, lyDo: 'Khong thay nut luu' };
          luu.scrollIntoView({ block: 'nearest' });
          const br = luu.getBoundingClientRect();
          const trongKhung = br.top >= 0 && br.bottom <= vh + 1 && br.left >= 0 && br.right <= vw + 1;
          const cx = Math.min(Math.max(br.left + br.width / 2, 1), vw - 1);
          const cy = Math.min(Math.max(br.top + br.height / 2, 1), vh - 1);
          const topEl = document.elementFromPoint(cx, cy);
          const bamDuoc = !!topEl && (topEl === luu || luu.contains(topEl));
          return {
            ok: !tranNgang && trongKhung && bamDuoc,
            tranNgang,
            hopRect: [Math.round(hr.left), Math.round(hr.right), vw],
            scrollH: Math.round(hop.scrollHeight),
            clientH: Math.round(hop.clientHeight),
            scrollTop: Math.round(hop.scrollTop),
            luuRect: [Math.round(br.top), Math.round(br.bottom), vh],
            trongKhung,
            bamDuoc,
            topTag: topEl ? `${topEl.tagName}.${String(topEl.className || '').slice(0, 30)}` : 'null',
          };
        }""",
        ten_nut_luu,
    )
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    kq.ghi(
        ma,
        bool(res.get("ok")),
        f"tranNgang={res.get('tranNgang')} hop={res.get('hopRect')}, "
        f"scroll={res.get('scrollTop')}/{res.get('scrollH')}(ch={res.get('clientH')}), "
        f"luu={res.get('luuRect')}, trongKhung={res.get('trongKhung')}, bamDuoc={res.get('bamDuoc')} ({res.get('topTag')})",
    )


def main() -> int:
    kq = KetQua()
    print("=== Bắt đầu 02_nut_chep_va_pixel.py ===", flush=True)
    try:
        mau = lay_id_mau()
    except Exception as e:
        print(f"[LỖI] Không đọc được dữ liệu mẫu từ API: {e}")
        traceback.print_exc()
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =================================================================
            # PHẦN A: NutChep.tsx ở cả Thường và Pixel, 1440px và 390px
            # =================================================================
            for pixel in (False, True):
                ten_pc = "pixel" if pixel else "thuong"
                for ten_vp, vp in [("1440", VIEWPORTS[0][1]), ("390", VIEWPORTS[2][1])]:
                    ctx, page, c_err, p_err, _ = tao_phien(browser, vp, pixel=pixel, tai_khoan="dieuphoi")
                    try:
                        kiem_tra_nut_chep_tren_trang(
                            page, kq, f"NC_taixe_{ten_pc}_{ten_vp}", "/dieu-phoi/tai-xe", c_err, p_err
                        )
                        kiem_tra_nut_chep_tren_trang(
                            page, kq, f"NC_khach_{ten_pc}_{ten_vp}", "/dieu-phoi/khach-hang", c_err, p_err
                        )
                        if mau["cid"]:
                            kiem_tra_nut_chep_tren_trang(
                                page,
                                kq,
                                f"NC_khoixe_{ten_pc}_{ten_vp}",
                                f"/dieu-phoi/chuyen/{mau['cid']}",
                                c_err,
                                p_err,
                            )
                    finally:
                        ctx.close()

                    if mau["tx_cid"]:
                        ctx, page, c_err, p_err, _ = tao_phien(
                            browser, vp, pixel=pixel, tai_khoan=mau["tx_user"]
                        )
                        try:
                            kiem_tra_nut_chep_tren_trang(
                                page,
                                kq,
                                f"NC_chuyen_tx_{ten_pc}_{ten_vp}",
                                f"/tai-xe/chuyen/{mau['tx_cid']}",
                                c_err,
                                p_err,
                            )
                        finally:
                            ctx.close()

            # =================================================================
            # PHẦN B: Quét toàn bộ trang ở giao diện Pixel x 3 cỡ (1440, 1024, 390)
            # =================================================================
            for ten_vp, vp in VIEWPORTS:
                # 1. Trang công khai (/dang-nhap máy in phiếu Pixel, /tra-cuu)
                ctx, page, c_err, p_err, a5 = tao_phien(browser, vp, pixel=True, tai_khoan=None)
                try:
                    page.goto(f"{FRONTEND}/dang-nhap", wait_until="networkidle")
                    page.wait_for_timeout(500)
                    # Bấm logo để in phiếu đăng nhập Pixel
                    nut_logo = page.locator("button.dn-bam-logo")
                    if nut_logo.count() > 0 and nut_logo.is_visible():
                        nut_logo.click()
                        page.wait_for_timeout(700)
                    res_dn = page.evaluate(AUDIT_PIXEL_JS)
                    co_form_nv = page.locator("form.dn-phieu").is_visible()
                    kq.ghi(
                        f"PX_dang_nhap_{ten_vp}",
                        co_form_nv
                        and res_dn["cuonNgangPx"] <= 1
                        and not c_err
                        and not p_err
                        and not a5,
                        f"co_form_nv={co_form_nv}, cuonNgang={res_dn['cuonNgangPx']}px, errs={c_err + p_err}",
                    )
                    quet_trang_pixel(page, kq, f"PX_tra_cuu_{ten_vp}", "/tra-cuu", c_err, p_err, a5)
                finally:
                    ctx.close()

                # 2. Quản lý
                ctx, page, c_err, p_err, a5 = tao_phien(browser, vp, pixel=True, tai_khoan="quanly")
                try:
                    for ten_r, r in [
                        ("ql_tong_quan", "/quan-ly/tong-quan"),
                        ("ql_nguoi_dung", "/quan-ly/nguoi-dung"),
                        ("ql_bang_gia", "/quan-ly/bang-gia"),
                        ("ql_cau_hinh", "/quan-ly/cau-hinh"),
                        ("ql_cong_no", "/quan-ly/cong-no"),
                        ("ql_quyet_toan", "/quan-ly/quyet-toan"),
                        ("ql_tai_khoan", "/tai-khoan"),
                        ("ql_cai_dat", "/cai-dat"),
                    ]:
                        quet_trang_pixel(page, kq, f"PX_{ten_r}_{ten_vp}", r, c_err, p_err, a5)
                finally:
                    ctx.close()

                # 3. Điều phối
                ctx, page, c_err, p_err, a5 = tao_phien(browser, vp, pixel=True, tai_khoan="dieuphoi")
                try:
                    ds_dp = [
                        ("dp_chuyen", "/dieu-phoi/chuyen"),
                        ("dp_don", "/dieu-phoi/don"),
                        ("dp_xe", "/dieu-phoi/xe"),
                        ("dp_tai_xe", "/dieu-phoi/tai-xe"),
                        ("dp_khach_hang", "/dieu-phoi/khach-hang"),
                        ("dp_nut", "/dieu-phoi/nut"),
                        ("dp_tuyen", "/dieu-phoi/tuyen"),
                    ]
                    if mau["cid"]:
                        ds_dp.append(("dp_chuyen_ct", f"/dieu-phoi/chuyen/{mau['cid']}"))
                    if mau["did"]:
                        ds_dp.append(("dp_phieu_don", f"/dieu-phoi/don/{mau['did']}/phieu"))
                    for ten_r, r in ds_dp:
                        quet_trang_pixel(page, kq, f"PX_{ten_r}_{ten_vp}", r, c_err, p_err, a5)
                finally:
                    ctx.close()

                # 4. Kế toán
                ctx, page, c_err, p_err, a5 = tao_phien(browser, vp, pixel=True, tai_khoan="ketoan")
                try:
                    for ten_r, r in [
                        ("kt_tong_quan", "/ke-toan/tong-quan"),
                        ("kt_chi_phi_xe", "/ke-toan/chi-phi-xe"),
                        ("kt_cong_no", "/ke-toan/cong-no"),
                        ("kt_quyet_toan", "/ke-toan/quyet-toan"),
                        ("kt_tam_ung", "/ke-toan/tam-ung"),
                    ]:
                        quet_trang_pixel(page, kq, f"PX_{ten_r}_{ten_vp}", r, c_err, p_err, a5)
                finally:
                    ctx.close()

                # 5. Tài xế
                ctx, page, c_err, p_err, a5 = tao_phien(
                    browser, vp, pixel=True, tai_khoan=mau["tx_user"]
                )
                try:
                    quet_trang_pixel(page, kq, f"PX_tx_chuyen_{ten_vp}", "/tai-xe/chuyen", c_err, p_err, a5)
                    if mau["tx_cid"]:
                        quet_trang_pixel(
                            page,
                            kq,
                            f"PX_tx_chuyen_ct_{ten_vp}",
                            f"/tai-xe/chuyen/{mau['tx_cid']}",
                            c_err,
                            p_err,
                            a5,
                        )
                    quet_trang_pixel(page, kq, f"PX_tx_tai_khoan_{ten_vp}", "/tai-khoan", c_err, p_err, a5)
                finally:
                    ctx.close()

            # =================================================================
            # PHẦN C: Hộp thoại trong Pixel x 3 cỡ (cuộn tới nút Lưu & bấm được)
            # =================================================================
            for ten_vp, vp in VIEWPORTS:
                ctx, page, _, _, _ = tao_phien(browser, vp, pixel=True, tai_khoan="dieuphoi")
                try:
                    kiem_hop_thoai_pixel(
                        page,
                        kq,
                        f"PX_HD_them_tuyen_{ten_vp}",
                        "/dieu-phoi/tuyen",
                        "Thêm tuyến",
                        "Lưu",
                        them_nut_tuyen=True,
                    )
                    kiem_hop_thoai_pixel(
                        page, kq, f"PX_HD_tao_don_{ten_vp}", "/dieu-phoi/don", "Tạo đơn", "Lưu đơn"
                    )
                    kiem_hop_thoai_pixel(
                        page,
                        kq,
                        f"PX_HD_lap_chuyen_{ten_vp}",
                        "/dieu-phoi/chuyen",
                        "Lập chuyến",
                        "Lập chuyến",
                    )
                    kiem_hop_thoai_pixel(
                        page, kq, f"PX_HD_them_xe_{ten_vp}", "/dieu-phoi/xe", "Thêm xe", "Lưu"
                    )
                    kiem_hop_thoai_pixel(
                        page,
                        kq,
                        f"PX_HD_them_tai_xe_{ten_vp}",
                        "/dieu-phoi/tai-xe",
                        "Thêm tài xế",
                        "Lưu",
                    )
                    kiem_hop_thoai_pixel(
                        page,
                        kq,
                        f"PX_HD_them_khach_{ten_vp}",
                        "/dieu-phoi/khach-hang",
                        "Thêm khách hàng",
                        "Lưu",
                    )
                finally:
                    ctx.close()

                ctx, page, _, _, _ = tao_phien(browser, vp, pixel=True, tai_khoan="quanly")
                try:
                    kiem_hop_thoai_pixel(
                        page,
                        kq,
                        f"PX_HD_them_nguoi_dung_{ten_vp}",
                        "/quan-ly/nguoi-dung",
                        "Thêm người dùng",
                        "Lưu",
                    )
                finally:
                    ctx.close()
        finally:
            browser.close()

    return kq.tong_ket()


if __name__ == "__main__":
    sys.exit(main())
