"""Tiện ích dùng chung cho bộ kiểm thử khám phá GIAO DIỆN PIXEL (Phiếu 35).

Chạy bằng: py -3.12 -I -X utf8 <script.py>
Chỉ dùng thư viện chuẩn Python 3.12 + playwright.sync_api (KHÔNG dùng httpx / .venv).
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import time
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

BASE_FE = "http://127.0.0.1:5173"
BASE_API = "http://127.0.0.1:8000"
VN_TZ = timezone(timedelta(hours=7))

DIR_GOC = os.path.dirname(os.path.abspath(__file__))
DIR_ANH = os.path.join(DIR_GOC, "anh")
os.makedirs(DIR_ANH, exist_ok=True)

VIEWPORT_DESKTOP = {"width": 1440, "height": 900}
VIEWPORT_TABLET = {"width": 1100, "height": 800}
VIEWPORT_MOBILE = {"width": 390, "height": 844}

# JPEG và PNG tối thiểu hợp lệ (1x1 pixel) để thử upload ảnh không cần file ngoài
MIN_JPG = bytes.fromhex(
    "ffd8ffe000104a46494600010101004800480000ffdb004300030202030202030303030403030405"
    "0805050404050a070706080c0a0c0c0b0a0b0b0d0e12100d0e110e0b0b1016101113141515150c0f"
    "171816141812141514ffc0000b080001000101011100ffc400140001000000000000000000000000"
    "00000009ffc40014100100000000000000000000000000000000ffda0008010100003f00d2cf20ffd9"
)
MIN_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415408d763f8ffff3f0005fe02fea7d6a5400000000049454e44ae426082"
)

XSS_SCRIPT = "<script>window.__xss=1;alert(1)</script>"
XSS_IMG = '<img src=x onerror="window.__xss=1;alert(1)">'
SQLI_PAYLOAD = "' OR 1=1 --"
EMOJI_PAYLOAD = "PHA-🚚🔥💥🧪中文العربية"


def now_vn() -> datetime:
    return datetime.now(VN_TZ)


def iso_vn(dt: datetime) -> str:
    return dt.astimezone(VN_TZ).isoformat(timespec="seconds")


def ma_ngau_nhien(do_dai: int = 5) -> str:
    return uuid.uuid4().hex[:do_dai].upper()


def slug_an_toan(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_")
    return s[:70] or "anh"


# =============================================================================
# Báo cáo kết quả cho từng script
# =============================================================================
@dataclass
class KetQuaCa:
    ma: str
    ten: str
    dat: bool
    ly_do: str
    muc: str = ""  # Nghiêm trọng | Vừa | Nhẹ
    anh: str = ""
    tai_hien: str = ""
    mong_doi: str = ""


class BaoCaoScript:
    def __init__(self, ma_muc: int, ten_muc: str, ten_file_kq: str):
        self.ma_muc = ma_muc
        self.ten_muc = ten_muc
        self.ten_file_kq = ten_file_kq
        self.ca: list[KetQuaCa] = []
        self.bat_dau = time.time()
        print(f"\n{'=' * 76}")
        print(f"MỤC {ma_muc:02d}: {ten_muc}")
        print(f"{'=' * 76}")

    def ghi(
        self,
        ma: str,
        ten: str,
        dat: bool,
        ly_do: str,
        muc: str = "Vừa",
        anh: str = "",
        tai_hien: str = "",
        mong_doi: str = "",
    ) -> KetQuaCa:
        item = KetQuaCa(
            ma=ma,
            ten=ten,
            dat=dat,
            ly_do=ly_do,
            muc="" if dat else muc,
            anh=anh,
            tai_hien=tai_hien,
            mong_doi=mong_doi,
        )
        self.ca.append(item)
        nhan = "ĐẠT" if dat else f"LỖI ({muc})"
        phu_anh = f" | ảnh: {anh}" if (not dat and anh) else ""
        print(f"[{nhan}] {ma} - {ten}: {ly_do[:260]}{phu_anh}", flush=True)
        return item

    def chay_ca(
        self,
        ma: str,
        ten: str,
        fn: Callable[[], tuple[bool, str, str] | tuple[bool, str]],
        page: Page | None = None,
        muc: str = "Vừa",
        tai_hien: str = "",
        mong_doi: str = "",
        chup_khi_loi: bool = True,
    ) -> KetQuaCa:
        """Chạy 1 ca kiểm thử trong try/except để lỗi không làm dừng cả bộ."""
        try:
            kq = fn()
            if len(kq) == 3:
                dat, ly_do, muc_rieng = kq
                muc_dung = muc_rieng or muc
            else:
                dat, ly_do = kq
                muc_dung = muc
            anh = ""
            if not dat and chup_khi_loi and page is not None:
                anh = chup_anh(page, f"m{self.ma_muc:02d}_{ma}")
            return self.ghi(ma, ten, dat, ly_do, muc=muc_dung, anh=anh, tai_hien=tai_hien, mong_doi=mong_doi)
        except Exception as exc:
            anh = chup_anh(page, f"m{self.ma_muc:02d}_{ma}_exc") if (chup_khi_loi and page is not None) else ""
            tb_dong = traceback.format_exc().strip().splitlines()[-1]
            return self.ghi(
                ma,
                ten,
                False,
                f"Ngoại lệ khi chạy ca: {type(exc).__name__}: {exc} ({tb_dong})",
                muc=muc,
                anh=anh,
                tai_hien=tai_hien,
                mong_doi=mong_doi,
            )

    def ket_thuc(self) -> dict[str, Any]:
        thoi_gian = round(time.time() - self.bat_dau, 1)
        tong = len(self.ca)
        dat = sum(1 for c in self.ca if c.dat)
        loi = tong - dat
        du_lieu = {
            "muc": self.ma_muc,
            "ten_muc": self.ten_muc,
            "tong": tong,
            "dat": dat,
            "loi": loi,
            "thoi_gian_giay": thoi_gian,
            "ca": [asdict(c) for c in self.ca],
        }
        duong_dan = os.path.join(DIR_GOC, self.ten_file_kq)
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        print(f"\n==> TỔNG KẾT MỤC {self.ma_muc:02d} ({self.ten_muc}): {tong} ca | ĐẠT: {dat} | LỖI: {loi} | {thoi_gian}s")
        print(f"    Đã lưu JSON: {duong_dan}")
        return du_lieu


# =============================================================================
# Theo dõi trang an toàn (không bao giờ dùng remove_listener với lambda ẩn danh)
# =============================================================================
class BoTheoDoi:
    """Gắn listener một lần duy nhất lên Page, đổi hành vi dialog bằng thuộc tính."""

    def __init__(self, page: Page, che_do_dialog: str = "dismiss"):
        self.page = page
        self.che_do_dialog = che_do_dialog  # "dismiss" | "accept"
        self.console_errors: list[str] = []
        self.page_errors: list[str] = []
        self.http_5xx: list[str] = []
        self.http_4xx: list[str] = []
        self.dialogs: list[str] = []
        self.requests: list[tuple[str, str]] = []
        self.ghi_requests = False

        page.on("console", self._on_console)
        page.on("pageerror", self._on_pageerror)
        page.on("response", self._on_response)
        page.on("dialog", self._on_dialog)
        page.on("request", self._on_request)

    def _on_console(self, msg) -> None:
        try:
            if msg.type == "error":
                self.console_errors.append(msg.text)
        except Exception:
            pass

    def _on_pageerror(self, err) -> None:
        try:
            self.page_errors.append(str(err))
        except Exception:
            pass

    def _on_response(self, resp) -> None:
        try:
            st = resp.status
            if st >= 500:
                self.http_5xx.append(f"{st} {resp.request.method} {resp.url}")
            elif st >= 400:
                self.http_4xx.append(f"{st} {resp.request.method} {resp.url}")
        except Exception:
            pass

    def _on_dialog(self, dialog) -> None:
        try:
            self.dialogs.append(f"{dialog.type}: {dialog.message}")
            if self.che_do_dialog == "accept":
                dialog.accept()
            else:
                dialog.dismiss()
        except Exception:
            pass

    def _on_request(self, req) -> None:
        try:
            if self.ghi_requests:
                self.requests.append((req.method, req.url))
        except Exception:
            pass

    def reset(self) -> None:
        self.console_errors.clear()
        self.page_errors.clear()
        self.http_5xx.clear()
        self.http_4xx.clear()
        self.dialogs.clear()
        self.requests.clear()

    def loi_console_that(self, bo_qua_401: bool = True) -> list[str]:
        kq = []
        for e in self.console_errors:
            if bo_qua_401 and ("status of 401" in e or "401 (Unauthorized)" in e):
                continue
            kq.append(e)
        return kq

    def kiem_xss(self) -> tuple[bool, str]:
        xss_val = 0
        try:
            xss_val = self.page.evaluate("() => window.__xss || 0")
        except Exception:
            xss_val = 0
        alert_dialogs = [d for d in self.dialogs if d.startswith("alert:")]
        bi_xss = bool(xss_val) or len(alert_dialogs) > 0
        return bi_xss, f"window.__xss={xss_val}, alert_dialogs={alert_dialogs}"


# =============================================================================
# Quản lý BrowserContext Pixel, đăng nhập, chụp ảnh, chờ ổn định
# =============================================================================
def chup_anh(page: Page, ten: str) -> str:
    ten_file = f"{slug_an_toan(ten)}.png"
    duong_dan = os.path.join(DIR_ANH, ten_file)
    try:
        if not page.is_closed():
            page.screenshot(path=duong_dan, full_page=False, timeout=8000)
            return f"anh/{ten_file}"
    except Exception:
        pass
    return ""


def tao_context_pixel(
    browser: Browser,
    viewport: dict[str, int] | None = None,
    co_dinh_pixel: bool = True,
    che_do: str = "sang",
    reduced_motion: str | None = None,
    extra_init_js: str = "",
) -> BrowserContext:
    """Tạo context đã bật phong cách Pixel + chế độ sáng TRƯỚC khi mở trang."""
    kwargs: dict[str, Any] = {
        "viewport": viewport or VIEWPORT_DESKTOP,
        "locale": "vi-VN",
        "timezone_id": "Asia/Ho_Chi_Minh",
    }
    if reduced_motion is not None:
        kwargs["reduced_motion"] = reduced_motion
    ctx = browser.new_context(**kwargs)
    if co_dinh_pixel:
        init_js = f"""
            window.__xss = 0;
            try {{
                localStorage.setItem('qlvc-phong-cach', 'pixel');
                localStorage.setItem('qlvc-che-do', '{che_do}');
            }} catch (e) {{}}
            {extra_init_js}
        """
    else:
        # Chỉ đặt lần đầu trong phiên để test đổi Pixel <-> Hiện tại không bị ghi đè khi reload
        init_js = f"""
            window.__xss = 0;
            try {{
                if (!sessionStorage.getItem('__pha_init_pixel')) {{
                    localStorage.setItem('qlvc-phong-cach', 'pixel');
                    localStorage.setItem('qlvc-che-do', '{che_do}');
                    sessionStorage.setItem('__pha_init_pixel', '1');
                }}
            }} catch (e) {{}}
            {extra_init_js}
        """
    ctx.add_init_script(init_js)
    return ctx


def mo_trang_moi(
    ctx: BrowserContext,
    timeout_ms: int = 12000,
    che_do_dialog: str = "dismiss",
) -> tuple[Page, BoTheoDoi]:
    page = ctx.new_page()
    page.set_default_timeout(timeout_ms)
    page.set_default_navigation_timeout(max(timeout_ms, 15000))
    mon = BoTheoDoi(page, che_do_dialog=che_do_dialog)
    return page, mon


def cho_yen(page: Page, ms: int = 450, network_timeout: int = 5000) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=network_timeout)
    except PlaywrightTimeoutError:
        pass
    except Exception:
        pass
    if ms > 0:
        page.wait_for_timeout(ms)


def mo_khung_dang_nhap_pixel(page: Page, timeout_ms: int = 8000) -> None:
    """Ở giao diện Pixel, /dang-nhap có nút .dn-bam-logo để mở khung nhập."""
    o_user = page.locator('input[autocomplete="username"]')
    if o_user.count() > 0 and o_user.first.is_visible():
        return
    logo = page.locator(".dn-bam-logo")
    try:
        logo.first.wait_for(state="visible", timeout=min(timeout_ms, 4000))
        logo.first.click(timeout=4000)
        o_user.first.wait_for(state="visible", timeout=timeout_ms)
        return
    except Exception:
        # Dự phòng nếu màn đăng nhập hiện thẳng form (không có .dn-bam-logo)
        o_user.first.wait_for(state="visible", timeout=timeout_ms)


def dang_nhap_ui(page: Page, user: str, pw: str = "demo12345", timeout_ms: int = 15000) -> None:
    page.goto(f"{BASE_FE}/dang-nhap", wait_until="domcontentloaded", timeout=timeout_ms)
    cho_yen(page, ms=300, network_timeout=4000)
    if "/dang-nhap" not in page.url:
        return
    mo_khung_dang_nhap_pixel(page, timeout_ms=8000)
    page.locator('input[autocomplete="username"]').first.fill(user)
    page.locator('input[autocomplete="current-password"]').first.fill(pw)
    page.locator('button:has-text("Đăng nhập")').first.click()
    page.wait_for_url(lambda u: "/dang-nhap" not in u, timeout=timeout_ms)
    cho_yen(page, ms=450, network_timeout=5000)


def dang_nhap_nhanh(ctx: BrowserContext, page: Page, user: str, pw: str = "demo12345") -> None:
    """Đăng nhập bằng POST /api/auth/dang-nhap qua ctx.request (set cookie httponly), dự phòng UI."""
    try:
        resp = ctx.request.post(
            f"{BASE_FE}/api/auth/dang-nhap",
            data={"ten_dang_nhap": user, "mat_khau": pw},
            timeout=10000,
        )
        if resp.status == 200:
            page.goto(f"{BASE_FE}/", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_url(lambda u: "/dang-nhap" not in u, timeout=10000)
            cho_yen(page, ms=450, network_timeout=5000)
            return
    except Exception:
        pass
    dang_nhap_ui(page, user, pw)


# =============================================================================
# Kiểm tra bố cục DOM dùng chung (tràn ngang, chữ/nút bị cắt, phần tử đè nhau)
# =============================================================================
JS_KIEM_BO_CUC = """() => {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const doc = document.documentElement;
  const body = document.body;
  const sw = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);

  const mainEl = document.querySelector('main.trang') || document.querySelector('main') || body;
  const mainText = (mainEl ? mainEl.innerText : '').trim();

  const anCuonNgang = (el) => {
    let p = el.parentElement;
    while (p && p !== document.body) {
      const ps = getComputedStyle(p);
      if ((ps.overflowX === 'auto' || ps.overflowX === 'scroll') && p.clientWidth <= vw + 4) {
        return true;
      }
      p = p.parentElement;
    }
    return false;
  };

  const hienThi = (el) => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.05) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    if (el.classList.contains('an-chu')) return false;
    if (r.width <= 2 && r.height <= 2 && st.overflow === 'hidden') return false;
    return true;
  };

  const tranViewport = [];
  const biCat = [];
  const anhLoi = [];

  for (const img of document.querySelectorAll('img')) {
    if (!hienThi(img)) continue;
    if (!img.complete || img.naturalWidth === 0) {
      anhLoi.push((img.getAttribute('src') || '').slice(0, 60));
    }
  }

  for (const el of document.querySelectorAll('h1,h2,h3,button,a,input,select,label,.nhan,.bien,table,section,aside,header,nav')) {
    if (!hienThi(el)) continue;
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);

    if (r.right > vw + 3 && !anCuonNgang(el) && st.overflowX !== 'auto' && st.overflowX !== 'scroll') {
      tranViewport.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().slice(0, 40),
        txt: (el.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 35),
        right: Math.round(r.right),
        vw,
      });
    }

    // Kiểm chữ/nút bị cắt trong chính khung của nó (overflow hidden/clip mà scrollWidth > clientWidth)
    if (['BUTTON', 'A', 'H1', 'H2', 'H3'].includes(el.tagName)) {
      const ovX = st.overflowX;
      if ((ovX === 'hidden' || ovX === 'clip') && el.clientWidth > 10 && el.scrollWidth > el.clientWidth + 4) {
        const txt = (el.innerText || '').trim().replace(/\\s+/g, ' ');
        if (txt.length > 0 && st.textOverflow !== 'ellipsis') {
          biCat.push({
            tag: el.tagName.toLowerCase(),
            cls: (el.className || '').toString().slice(0, 35),
            txt: txt.slice(0, 35),
            sw: el.scrollWidth,
            cw: el.clientWidth,
          });
        }
      }
    }
  }

  // Kiểm chồng lấn giữa các phần tử tương tác & tiêu đề hiển thị trong viewport
  const muc = [];
  for (const el of document.querySelectorAll('h1,h2,button,a,input,select')) {
    if (!hienThi(el)) continue;
    if (el.closest('svg')) continue;
    if (el.closest('[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    if (r.bottom < 0 || r.top > vh + 400) continue;
    // Bỏ qua phần tử trong hộp ẩn hoặc ngoài khung cuộn
    muc.push({ el, r, txt: (el.innerText || el.getAttribute('aria-label') || el.tagName).trim().replace(/\\s+/g, ' ').slice(0, 30) });
  }
  const chongNhau = [];
  for (let i = 0; i < muc.length && chongNhau.length < 6; i++) {
    for (let j = i + 1; j < muc.length && chongNhau.length < 6; j++) {
      const a = muc[i], b = muc[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      // Bỏ qua nếu 1 phần tử nằm trong lớp nổi cố định/sticky/popover đè lên nền (menu, hộp thoại, chuông)
      const inFloatA = !!a.el.closest('.hop-thoai,.nen-mo,.chuong-hop,.menu-tk-hop,.tim-hop,[role="dialog"],.canh,header.dau');
      const inFloatB = !!b.el.closest('.hop-thoai,.nen-mo,.chuong-hop,.menu-tk-hop,.tim-hop,[role="dialog"],.canh,header.dau');
      if (inFloatA !== inFloatB) continue;
      const ix = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const iy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ix > 4 && iy > 4) {
        const area = ix * iy;
        const minArea = Math.min(a.r.width * a.r.height, b.r.width * b.r.height);
        if (minArea > 0 && area / minArea > 0.25) {
          chongNhau.push({
            a: `${a.el.tagName.toLowerCase()}(${a.txt})`,
            b: `${b.el.tagName.toLowerCase()}(${b.txt})`,
            tyLe: Math.round((area / minArea) * 100),
          });
        }
      }
    }
  }

  // Kiểm skeleton .px-tai và độ mờ main.trang > *
  const pxTai = document.querySelectorAll('.px-tai').length;
  const mainChildren = Array.from(document.querySelectorAll('main.trang > *')).map((el) => {
    const st = getComputedStyle(el);
    return { opacity: parseFloat(st.opacity), filter: st.filter };
  });

  return {
    vw,
    vh,
    sw,
    cuonNgang: sw > vw + 2,
    mainTextLen: mainText.length,
    mainTextMau: mainText.slice(0, 80),
    tranViewport: tranViewport.slice(0, 6),
    biCat: biCat.slice(0, 6),
    chongNhau,
    anhLoi: anhLoi.slice(0, 5),
    pxTai,
    mainChildren,
    phongCach: document.documentElement.dataset.phongCach || localStorage.getItem('qlvc-phong-cach') || '',
  };
}"""


def kiem_bo_cuc_trang(page: Page) -> dict[str, Any]:
    return page.evaluate(JS_KIEM_BO_CUC)


def cho_noi_dung_khong_trang(page: Page, timeout_s: float = 4.0) -> tuple[bool, int, str]:
    """Chờ tối đa timeout_s để vùng nội dung có chữ thật (không phải màn trắng hay kẹt 'Đang tải…')."""
    han = time.time() + timeout_s
    last_len = 0
    last_txt = ""
    while time.time() < han:
        try:
            info = page.evaluate(
                """() => {
                    const m = document.querySelector('main.trang') || document.querySelector('main') || document.body;
                    const t = (m ? m.innerText : '').trim();
                    return { len: t.length, txt: t.slice(0, 100) };
                }"""
            )
            last_len = info["len"]
            last_txt = info["txt"]
            if last_len >= 15 and last_txt not in ("Đang tải…", "Đang tải..."):
                return True, last_len, last_txt
        except Exception:
            pass
        page.wait_for_timeout(200)
    return False, last_len, last_txt


# =============================================================================
# API Client mỏng dùng urllib (cho chuẩn bị dữ liệu PHA- và kiểm chứng backend)
# =============================================================================
def encode_multipart(
    fields: dict[str, Any] | list[tuple[str, Any]],
    files: list[tuple[str, str, bytes, str]],
) -> tuple[bytes, str]:
    boundary = f"----QLVCPixelPha{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    items = fields.items() if isinstance(fields, dict) else fields
    for k, v in items:
        if v is None:
            continue
        chunks.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8")
        )
    for field_name, filename, content, content_type in files:
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
            + content
            + b"\r\n"
        )
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class ApiClient:
    """HTTP client mỏng dùng urllib (qua proxy BASE_FE hoặc trực tiếp BASE_API)."""

    def __init__(self, base_url: str = BASE_FE, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def raw(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        raw_body: bytes | None = None,
        content_type: str | None = None,
        timeout: int = 15,
    ) -> tuple[int, Any, dict[str, str]]:
        url = f"{self.base_url}{path}"
        headers: dict[str, str] = {}
        if self.token:
            headers["Cookie"] = f"access_token={self.token}"
        body: bytes | None = None
        if json_body is not None:
            body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif raw_body is not None:
            body = raw_body
            if content_type:
                headers["Content-Type"] = content_type
        req = Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urlopen(req, timeout=timeout) as resp:
                status = resp.status
                resp_headers = dict(resp.headers.items())
                raw_text = resp.read()
        except HTTPError as e:
            status = e.code
            resp_headers = dict(e.headers.items()) if e.headers else {}
            raw_text = e.read()
        except URLError as e:
            return 0, f"URLError: {e}", {}
        text = raw_text.decode("utf-8", errors="replace")
        try:
            parsed = json.loads(text) if text else None
        except Exception:
            parsed = text
        return status, parsed, resp_headers

    def multipart(
        self,
        method: str,
        path: str,
        fields: dict[str, Any] | list[tuple[str, Any]] | None = None,
        files: list[tuple[str, str, bytes, str]] | None = None,
    ) -> tuple[int, Any, dict[str, str]]:
        body, ctype = encode_multipart(fields or {}, files or [])
        return self.raw(method, path, raw_body=body, content_type=ctype)

    def login(self, ten_dang_nhap: str, mat_khau: str = "demo12345") -> tuple[int, Any]:
        st, data, headers = self.raw(
            "POST",
            "/api/auth/dang-nhap",
            {"ten_dang_nhap": ten_dang_nhap, "mat_khau": mat_khau},
        )
        for k, v in headers.items():
            if k.lower() == "set-cookie":
                m = re.search(r"access_token=([^;]+)", v)
                if m:
                    self.token = m.group(1)
        return st, data


def dang_nhap_api(user: str, pw: str = "demo12345") -> ApiClient:
    c = ApiClient(BASE_FE)
    st, data = c.login(user, pw)
    if st != 200 or not c.token:
        c = ApiClient(BASE_API)
        st, data = c.login(user, pw)
    if st != 200 or not c.token:
        raise RuntimeError(f"Đăng nhập API {user} thất bại: HTTP {st} {data}")
    return c


def tim_cap_nut_co_gia(api_dp: ApiClient, tuyen: dict[str, Any] | None = None) -> tuple[int, int] | None:
    """Tìm cặp (nut_lay_id, nut_giao_id) đúng chiều tuyến và có bảng giá hợp lệ."""
    ds_tuyen = [tuyen] if tuyen else []
    if not ds_tuyen:
        st, r, _ = api_dp.raw("GET", "/api/tuyen?trang_thai=HOAT_DONG&so_dong=50")
        if st == 200 and isinstance(r, dict):
            ds_tuyen = r.get("du_lieu", [])
    for t in ds_tuyen:
        nuts = t.get("nut") or []
        for i in range(len(nuts)):
            for j in range(i + 1, len(nuts)):
                n1, n2 = nuts[i]["nut_id"], nuts[j]["nut_id"]
                st, _, _ = api_dp.raw(
                    "POST",
                    "/api/don/tinh-cuoc",
                    {"nut_lay_id": n1, "nut_giao_id": n2, "kg": "100", "m3": "1"},
                )
                if st == 200:
                    return int(n1), int(n2)
    return None


def lay_khach_hang_dau(api_dp: ApiClient) -> int | None:
    st, r, _ = api_dp.raw("GET", "/api/khach-hang?trang_thai=HOAT_DONG&so_dong=10")
    if st == 200 and isinstance(r, dict) and r.get("du_lieu"):
        return int(r["du_lieu"][0]["id"])
    return None


def lay_chuyen_mau(api_dp: ApiClient, trang_thai: str | None = None) -> dict[str, Any] | None:
    qs = f"trang_thai={trang_thai}&so_dong=10" if trang_thai else "so_dong=10"
    st, r, _ = api_dp.raw("GET", f"/api/chuyen?{qs}")
    if st == 200 and isinstance(r, dict) and r.get("du_lieu"):
        return r["du_lieu"][0]
    return None


def lay_don_mau(api_dp: ApiClient) -> dict[str, Any] | None:
    st, r, _ = api_dp.raw("GET", "/api/don?so_dong=10")
    if st == 200 and isinstance(r, dict) and r.get("du_lieu"):
        return r["du_lieu"][0]
    return None


def tao_don_pha(
    api_dp: ApiClient,
    khach_id: int,
    nut_lay_id: int,
    nut_giao_id: int,
    kg: str = "100.00",
    m3: str = "1.00",
    so_kien: int = 2,
    nhan: str = "PHA",
    han_gio_them: int = 72,
) -> dict[str, Any]:
    sfx = ma_ngau_nhien(5)
    st, d, _ = api_dp.raw(
        "POST",
        "/api/don",
        {
            "khach_hang_id": khach_id,
            "mo_ta": f"PHA-{nhan}-{sfx}",
            "kg": kg,
            "m3": m3,
            "so_kien": so_kien,
            "nut_lay_id": nut_lay_id,
            "dia_chi_lay": f"10 Đường PHA {sfx}",
            "sdt_lay": "0909111222",
            "nut_giao_id": nut_giao_id,
            "dia_chi_giao": f"20 Đường PHA {sfx}",
            "nguoi_nhan": f"PHA-Nhan-{sfx}",
            "sdt_nhan": "0909333444",
            "han_giao": iso_vn(now_vn() + timedelta(hours=han_gio_them)),
        },
    )
    if st not in (200, 201) or not isinstance(d, dict) or "id" not in d:
        raise RuntimeError(f"Tạo đơn PHA thất bại: HTTP {st} {d}")
    return d


def tao_chuyen_lap_pha(
    api_dp: ApiClient,
    tai_trong_kg: int = 2000,
    the_tich_m3: str = "10.00",
    gio_them: int = 4,
) -> tuple[dict[str, Any], dict[str, Any], tuple[int, int]]:
    """Tạo xe PHA-, tài xế PHA- và chuyến LAP sạch để kiểm thử không ảnh hưởng dữ liệu sẵn."""
    sfx = ma_ngau_nhien(5)
    st_t, r_t, _ = api_dp.raw("GET", "/api/tuyen?trang_thai=HOAT_DONG&so_dong=50")
    if st_t != 200 or not isinstance(r_t, dict) or not r_t.get("du_lieu"):
        raise RuntimeError(f"Không có tuyến hoạt động: HTTP {st_t} {r_t}")

    tuyen_chon = None
    cap_nut = None
    for t in r_t["du_lieu"]:
        cap = tim_cap_nut_co_gia(api_dp, t)
        if cap:
            tuyen_chon = t
            cap_nut = cap
            break
    if not tuyen_chon or not cap_nut:
        raise RuntimeError("Không tìm thấy tuyến có cặp nút hợp lệ trong bảng giá")

    st_xe, d_xe, _ = api_dp.raw(
        "POST",
        "/api/xe",
        {
            "bien_so": f"PHA-{sfx}",
            "tai_trong_kg": tai_trong_kg,
            "the_tich_m3": the_tich_m3,
            "ktt_toan_bo_kg": max(tai_trong_kg + 2500, 8000),
            "han_dang_kiem": "2029-12-31",
            "han_bao_hiem": "2029-12-31",
            "km_dong_ho": 1000,
        },
    )
    if st_xe not in (200, 201) or not isinstance(d_xe, dict):
        raise RuntimeError(f"Tạo xe PHA thất bại: HTTP {st_xe} {d_xe}")

    st_tx, d_tx, _ = api_dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": f"pha_tx_{sfx.lower()}",
            "ho_ten": f"PHA-Tài xế {sfx}",
            "mat_khau": "demo12345",
            "so_gplx": f"PHA{sfx}0123",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0912345678",
        },
    )
    if st_tx not in (200, 201) or not isinstance(d_tx, dict):
        raise RuntimeError(f"Tạo tài xế PHA thất bại: HTTP {st_tx} {d_tx}")

    st_ch, d_ch, _ = api_dp.raw(
        "POST",
        "/api/chuyen",
        {
            "tuyen_id": tuyen_chon["id"],
            "khoi_hanh_du_kien": iso_vn(now_vn() + timedelta(hours=gio_them)),
            "xe_id": d_xe["id"],
            "tai_xe_id": d_tx["id"],
        },
    )
    if st_ch not in (200, 201) or not isinstance(d_ch, dict):
        raise RuntimeError(f"Lập chuyến PHA thất bại: HTTP {st_ch} {d_ch}")
    return d_ch, tuyen_chon, cap_nut


def tao_tai_khoan_pha(api_ql: ApiClient, vai_tro: str = "DIEU_PHOI", mat_khau: str = "demo12345") -> tuple[str, str, int]:
    """Tạo tài khoản PHA- riêng để thử đổi mật khẩu / đăng nhập sai mà không khóa tài khoản demo."""
    sfx = ma_ngau_nhien(6).lower()
    user = f"pha_{sfx}"
    st, d, _ = api_ql.raw(
        "POST",
        "/api/nguoi-dung",
        {
            "ten_dang_nhap": user,
            "ho_ten": f"PHA-NguoiDung-{sfx.upper()}",
            "mat_khau": mat_khau,
            "vai_tro": vai_tro,
        },
    )
    if st not in (200, 201) or not isinstance(d, dict) or "id" not in d:
        raise RuntimeError(f"Tạo tài khoản PHA thất bại: HTTP {st} {d}")
    return user, mat_khau, int(d["id"])
