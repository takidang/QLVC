#!/usr/bin/env python3
"""
01_hop_xac_nhan.py - Kiểm thử khám phá Hộp xác nhận mới (xacNhanKho.ts, HopXacNhan.tsx, bayFocus.ts)
Thay thế window.confirm ở 10 chỗ + kiểm tra bấm đúp, Enter/Space/Esc dồn dập, Back/Forward,
đổi chuyến khi đang hỏi, hai hộp chồng nhau, mạng chậm (bọc window.fetch bằng add_init_script),
lỗi 4xx sau khi đồng ý, và xác minh đường đồng ý gửi đúng 1 yêu cầu với đúng dữ liệu đang hiện.

Chạy độc lập: py -3.12 -I -X utf8 kiem-thu-kham-pha/01_hop_xac_nhan.py
"""

from __future__ import annotations

import json
import os
import random
import re
import struct
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import zlib
from datetime import datetime, timedelta, timezone
from typing import Any

from playwright.sync_api import BrowserContext, Page, sync_playwright

FRONTEND = "http://127.0.0.1:5173"
BACKEND = "http://127.0.0.1:8000"
VN_TZ = timezone(timedelta(hours=7))
TAG = f"PHA-{int(time.time()) % 100000}-{random.randint(100, 999)}"


# ---------- Tiện ích chung ----------


def tao_png_1x1() -> bytes:
    """Sinh ảnh PNG 1x1 hợp lệ để upload (không cần file ngoài)."""
    def chunk(loai: bytes, du_lieu: bytes) -> bytes:
        crc = zlib.crc32(loai + du_lieu) & 0xFFFFFFFF
        return struct.pack(">I", len(du_lieu)) + loai + du_lieu + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\xff\x00\x00"
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


PNG_HOP_LE = tao_png_1x1()


class ApiClient:
    """Client HTTP dùng urllib, tự giữ cookie access_token (tránh urllib bỏ qua Secure cookie trên http://)."""

    def __init__(self, base: str = BACKEND):
        self.base = base.rstrip("/")
        self.token: str | None = None

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        h: dict[str, str] = {}
        if self.token:
            h["Cookie"] = f"access_token={self.token}"
        if extra:
            h.update(extra)
        return h

    def request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        multipart: tuple[dict[str, Any], list[tuple[str, str, bytes, str]]] | None = None,
        timeout: float = 20.0,
    ) -> tuple[int, Any, dict[str, str]]:
        url = f"{self.base}{path}"
        data: bytes | None = None
        extra_headers: dict[str, str] = {}

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            extra_headers["Content-Type"] = "application/json"
        elif multipart is not None:
            fields, files = multipart
            boundary = f"----PhaBoundary{random.randint(100000, 999999)}"
            parts: list[bytes] = []
            for k, v in fields.items():
                if v is None:
                    continue
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{k}"\r\n\r\n'
                    f"{v}\r\n".encode("utf-8")
                )
            for field_name, filename, content, ctype in files:
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                    f"Content-Type: {ctype}\r\n\r\n".encode("utf-8")
                    + content
                    + b"\r\n"
                )
            parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            data = b"".join(parts)
            extra_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        req = urllib.request.Request(url, data=data, headers=self._headers(extra_headers), method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                raw = resp.read()
                resp_headers = dict(resp.headers.items())
                set_cookies = resp.headers.get_all("Set-Cookie") or []
                for sc in set_cookies:
                    m = re.search(r"access_token=([^;]+)", sc)
                    if m:
                        self.token = m.group(1)
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read()
            resp_headers = dict(e.headers.items()) if e.headers else {}
        try:
            body = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            body = raw.decode("utf-8", errors="replace")
        return status, body, resp_headers

    def dang_nhap(self, ten: str, mk: str) -> dict[str, Any]:
        st, body, _ = self.request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": ten, "mat_khau": mk})
        if st != 200:
            raise RuntimeError(f"Đăng nhập {ten} thất bại: HTTP {st} {body}")
        return body


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
        print(f"\n=== TỔNG KẾT 01_hop_xac_nhan: tổng={len(self.ds)} | đạt={dat} | lỗi={loi} | bỏ qua={bq} ===")
        return 1 if loi else 0


# ---------- Dữ liệu thử PHA- ----------


def chuan_bi_du_lieu() -> dict[str, Any]:
    """Tạo bộ dữ liệu PHA- hoàn toàn độc lập để không đụng tài khoản/dữ liệu gốc."""
    ql = ApiClient()
    ql.dang_nhap("quanly", "demo12345")
    dp = ApiClient()
    dp.dang_nhap("dieuphoi", "demo12345")
    kt = ApiClient()
    kt.dang_nhap("ketoan", "demo12345")

    now_vn = datetime.now(VN_TZ)
    nam_sau = (now_vn + timedelta(days=365)).strftime("%Y-%m-%d")
    han_giao_iso = (now_vn + timedelta(days=2)).isoformat(timespec="seconds")

    # Chọn tuyến đang hoạt động có ít nhất 2 nút và có bảng giá giữa 2 nút đó
    st, tuyen_res, _ = dp.request("GET", "/api/tuyen?trang_thai=HOAT_DONG&so_dong=100")
    assert st == 200 and tuyen_res["du_lieu"], f"Không lấy được danh sách tuyến: {st} {tuyen_res}"
    st, nut_res, _ = dp.request("GET", "/api/nut?so_dong=100")
    nut_map = {n["id"]: n for n in nut_res["du_lieu"]}
    st, bg_res, _ = ql.request("GET", "/api/bang-gia?so_dong=100")
    cap_gia = {(b["tinh_lay"].strip().lower(), b["tinh_giao"].strip().lower()) for b in bg_res["du_lieu"]}

    tuyen_chon = None
    nut_lay_id = None
    nut_giao_id = None
    for t in tuyen_res["du_lieu"]:
        ds_nut = t.get("nut") or []
        for i in range(len(ds_nut)):
            for j in range(i + 1, len(ds_nut)):
                n1 = nut_map.get(ds_nut[i]["nut_id"])
                n2 = nut_map.get(ds_nut[j]["nut_id"])
                if n1 and n2 and (n1["tinh"].strip().lower(), n2["tinh"].strip().lower()) in cap_gia:
                    tuyen_chon = t
                    nut_lay_id = n1["id"]
                    nut_giao_id = n2["id"]
                    break
            if tuyen_chon:
                break
        if tuyen_chon:
            break
    if not tuyen_chon:
        raise RuntimeError("Không tìm thấy tuyến hoạt động có cặp nút khớp bảng giá")

    # Tạo khách hàng PHA-
    st, kh, _ = dp.request(
        "POST",
        "/api/khach-hang",
        {
            "ten": f"{TAG} Khách thử xác nhận",
            "sdt": f"090{random.randint(1000000, 9999999)}",
            "dia_chi": "123 Đường thử PHA",
        },
    )
    assert st == 201, f"Tạo khách hàng thất bại: {st} {kh}"

    # Tạo 3 xe PHA- riêng để không đụng lịch nhau (BR-16)
    xe_ds = []
    for idx in range(3):
        bs = f"51P-{random.randint(10000, 99999)}"
        st, xe, _ = dp.request(
            "POST",
            "/api/xe",
            {
                "bien_so": bs,
                "tai_trong_kg": 5000,
                "the_tich_m3": "20.00",
                "ktt_toan_bo_kg": 8000,
                "han_dang_kiem": nam_sau,
                "han_bao_hiem": nam_sau,
                "dinh_muc_lit_100km": "18.00",
                "km_dong_ho": 10000 + idx * 100,
            },
        )
        assert st == 201, f"Tạo xe {idx} thất bại: {st} {xe}"
        xe_ds.append(xe)

    # Tạo 3 tài xế PHA- riêng (1 để ngừng tài xế, 2 để chạy chuyến độc lập không đụng BR-17/BR-26)
    tx_ds = []
    mk_pha = "PhaTest123!"
    for idx in range(3):
        uname = f"PHA-tx-{random.randint(10000, 99999)}-{idx}"
        gplx = f"PHA{random.randint(10000000, 99999999)}"
        st, tx, _ = dp.request(
            "POST",
            "/api/tai-xe",
            {
                "ten_dang_nhap": uname,
                "mat_khau": mk_pha,
                "ho_ten": f"{TAG} Tài xế {idx}",
                "so_gplx": gplx,
                "hang_gplx": "C",
                "han_gplx": nam_sau,
                "sdt": f"091{random.randint(1000000, 9999999)}",
            },
        )
        assert st == 201, f"Tạo tài xế {idx} thất bại: {st} {tx}"
        tx["mat_khau"] = mk_pha
        tx_ds.append(tx)

    # Tạo 1 tài khoản người dùng PHA- (Điều phối) để test Khóa tài khoản
    nd_uname = f"PHA-dp-{random.randint(10000, 99999)}"
    st, nd_pha, _ = ql.request(
        "POST",
        "/api/nguoi-dung",
        {
            "ten_dang_nhap": nd_uname,
            "ho_ten": f"{TAG} Điều phối thử",
            "vai_tro": "DIEU_PHOI",
            "mat_khau": mk_pha,
        },
    )
    assert st == 201, f"Tạo người dùng PHA- thất bại: {st} {nd_pha}"

    # Hàm tạo đơn PHA-
    def tao_don(mo_ta: str, kg: str = "10.00", m3: str = "0.10") -> dict[str, Any]:
        st, d, _ = dp.request(
            "POST",
            "/api/don",
            {
                "khach_hang_id": kh["id"],
                "mo_ta": f"{TAG} {mo_ta}",
                "kg": kg,
                "m3": m3,
                "so_kien": 1,
                "nut_lay_id": nut_lay_id,
                "dia_chi_lay": "Kho PHA lấy",
                "nguoi_lien_he_lay": "Anh PHA",
                "sdt_lay": "0901234567",
                "nut_giao_id": nut_giao_id,
                "dia_chi_giao": "Kho PHA giao",
                "nguoi_nhan": "Chị PHA",
                "sdt_nhan": "0907654321",
                "han_giao": han_giao_iso,
            },
        )
        assert st == 201, f"Tạo đơn thất bại: {st} {d}"
        return d

    # Lập chuyến A (LAP, chạy rỗng -> chốt chuyến phải hỏi BR-23) & chuyến B (LAP, rỗng khác ngày để test đổi chuyến)
    kh_ngay_mai = (now_vn + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    st, chuyen_lap_a, _ = dp.request(
        "POST",
        "/api/chuyen",
        {
            "tuyen_id": tuyen_chon["id"],
            "khoi_hanh_du_kien": kh_ngay_mai.isoformat(),
            "xe_id": xe_ds[0]["id"],
            "tai_xe_id": tx_ds[0]["id"],
        },
    )
    assert st == 201, f"Lập chuyến A thất bại: {st} {chuyen_lap_a}"

    st, chuyen_lap_b, _ = dp.request(
        "POST",
        "/api/chuyen",
        {
            "tuyen_id": tuyen_chon["id"],
            "khoi_hanh_du_kien": (kh_ngay_mai + timedelta(hours=1)).isoformat(),
            "xe_id": xe_ds[1]["id"],
            "tai_xe_id": tx_ds[1]["id"],
        },
    )
    assert st == 201, f"Lập chuyến B thất bại: {st} {chuyen_lap_b}"

    # Lập chuyến C (DA_CHOT + cấp 2 khoản tạm ứng để test Thu hồi tạm ứng)
    st, chuyen_tu, _ = dp.request(
        "POST",
        "/api/chuyen",
        {
            "tuyen_id": tuyen_chon["id"],
            "khoi_hanh_du_kien": (kh_ngay_mai + timedelta(days=1)).isoformat(),
            "xe_id": xe_ds[0]["id"],
            "tai_xe_id": tx_ds[0]["id"],
        },
    )
    assert st == 201, f"Lập chuyến tạm ứng thất bại: {st} {chuyen_tu}"
    st, _, _ = dp.request("POST", f"/api/chuyen/{chuyen_tu['id']}/chot", {"xac_nhan_chay_rong": True})
    assert st == 200
    st, tu_info, _ = kt.request("GET", f"/api/chuyen/{chuyen_tu['id']}/tam-ung")
    dm = tu_info["dinh_muc"]
    tam_ung_khoan = None
    if dm >= 20000:
        st, tam_ung_khoan, _ = kt.request(
            "POST", f"/api/chuyen/{chuyen_tu['id']}/tam-ung", {"so_tien": 10000, "hinh_thuc": "TIEN_MAT"}
        )
        assert st == 201, f"Cấp tạm ứng thất bại: {st} {tam_ung_khoan}"

    # Chuyến D (khởi hành HÔM NAY để tài xế bắt đầu được -> test: Xác nhận giao, Xóa chi phí, Kết thúc do sự cố, Trả hàng, Công nợ, Quyết toán!)
    kh_hom_nay = now_vn + timedelta(minutes=2)
    chuyen_chay_tx = None
    don_giao_ui = None
    don_tra_hang = None
    chi_phi_xoa = None
    chuyen_qt = None
    phai_thu_cn = None
    chuyen_suco = None

    if kh_hom_nay.date() == now_vn.date():
        # --- Chuyến chạy 1 (xe_ds[1], tx_ds[1]): có 2 đơn -> lấy cả 2, giao 1 bằng API (sinh công nợ) + giữ 1 đơn DA_LAY để test Xác nhận giao qua UI + tạo 2 chi phí để test Xóa chi phí qua UI ---
        st, chuyen_chay_tx, _ = dp.request(
            "POST",
            "/api/chuyen",
            {
                "tuyen_id": tuyen_chon["id"],
                "khoi_hanh_du_kien": kh_hom_nay.isoformat(timespec="seconds"),
                "xe_id": xe_ds[1]["id"],
                "tai_xe_id": tx_ds[1]["id"],
            },
        )
        assert st == 201, f"Lập chuyến chạy TX thất bại: {st} {chuyen_chay_tx}"
        d1 = tao_don("Đơn giao qua UI")
        d2 = tao_don("Đơn sinh công nợ")
        st, _, _ = dp.request("POST", f"/api/chuyen/{chuyen_chay_tx['id']}/ghep", {"don_ids": [d1["id"], d2["id"]]})
        assert st == 200
        st, _, _ = dp.request(
            "POST",
            f"/api/chuyen/{chuyen_chay_tx['id']}/chot",
            {"xac_nhan_chay_rong": True, "xac_nhan_lai_am": True},
        )
        assert st == 200

        tx1 = ApiClient()
        tx1.dang_nhap(tx_ds[1]["ten_dang_nhap"], mk_pha)
        st, _, _ = tx1.request(
            "POST",
            f"/api/toi/chuyen/{chuyen_chay_tx['id']}/bat-dau",
            multipart=({"km_bat_dau": "10200"}, [("anh_dong_ho", "km.png", PNG_HOP_LE, "image/png")]),
        )
        assert st == 200, f"Bắt đầu chuyến TX thất bại: {st}"

        # Quét lấy cả d1 và d2
        for d in (d1, d2):
            st, r, _ = tx1.request("POST", "/api/toi/quet", multipart=({"ma_don": d["ma_don"], "loai": "LAY"}, []))
            assert st == 200, f"Quét lấy thất bại: {st} {r}"
        # Giao d2 bằng API để sinh Phải thu cho test Công nợ
        st, r, _ = tx1.request(
            "POST",
            "/api/toi/quet",
            multipart=(
                {"ma_don": d2["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Người nhận PHA"},
                [
                    ("anh", "pod.png", PNG_HOP_LE, "image/png"),
                    ("chu_ky", "sig.png", PNG_HOP_LE, "image/png"),
                ],
            ),
        )
        assert st == 200, f"Quét giao d2 thất bại: {st} {r}"
        don_giao_ui = d1

        # Tìm khoản phải thu của d2
        st, pt_res, _ = kt.request("GET", f"/api/phai-thu?khach_hang_id={kh['id']}&trang_thai_tt=CHUA_THU")
        if st == 200 and pt_res["du_lieu"]:
            phai_thu_cn = pt_res["du_lieu"][0]

        # Tạo 1 khoản chi phí cho tx1 để test Xóa chi phí qua UI
        st, chi_phi_xoa, _ = tx1.request(
            "POST",
            f"/api/toi/chuyen/{chuyen_chay_tx['id']}/chi-phi",
            multipart=(
                {"loai": "CAU_DUONG", "so_tien": "50000", "ghi_chu": f"{TAG} Chi phí xóa"},
                [("anh", "hd.png", PNG_HOP_LE, "image/png")],
            ),
        )
        assert st == 201, f"Ghi chi phí thất bại: {st} {chi_phi_xoa}"

        # --- Chuyến chạy 2 (xe_ds[2], tx_ds[2]): 1 đơn đã lấy -> Điều phối kết thúc do sự cố qua UI -> sinh luôn:
        #     (a) đơn THAT_BAI đã lấy để test Trả hàng qua UI
        #     (b) chuyến HOAN_THANH để test Quyết toán qua UI! ---
        st, chuyen_suco, _ = dp.request(
            "POST",
            "/api/chuyen",
            {
                "tuyen_id": tuyen_chon["id"],
                "khoi_hanh_du_kien": (kh_hom_nay + timedelta(minutes=1)).isoformat(timespec="seconds"),
                "xe_id": xe_ds[2]["id"],
                "tai_xe_id": tx_ds[2]["id"],
            },
        )
        assert st == 201, f"Lập chuyến sự cố thất bại: {st} {chuyen_suco}"
        d_sc = tao_don("Đơn sự cố để trả hàng")
        st, _, _ = dp.request("POST", f"/api/chuyen/{chuyen_suco['id']}/ghep", {"don_ids": [d_sc["id"]]})
        assert st == 200
        st, _, _ = dp.request(
            "POST",
            f"/api/chuyen/{chuyen_suco['id']}/chot",
            {"xac_nhan_chay_rong": True, "xac_nhan_lai_am": True},
        )
        assert st == 200
        tx2 = ApiClient()
        tx2.dang_nhap(tx_ds[2]["ten_dang_nhap"], mk_pha)
        st, _, _ = tx2.request(
            "POST",
            f"/api/toi/chuyen/{chuyen_suco['id']}/bat-dau",
            multipart=({"km_bat_dau": "10300"}, [("anh_dong_ho", "km.png", PNG_HOP_LE, "image/png")]),
        )
        assert st == 200
        st, _, _ = tx2.request("POST", "/api/toi/quet", multipart=({"ma_don": d_sc["ma_don"], "loai": "LAY"}, []))
        assert st == 200
        don_tra_hang = d_sc
        chuyen_qt = chuyen_suco  # sau khi kết thúc do sự cố, chuyến này thành HOAN_THANH -> quyết toán được!

    return {
        "kh": kh,
        "xe_ds": xe_ds,
        "tx_ds": tx_ds,
        "nd_pha": nd_pha,
        "chuyen_lap_a": chuyen_lap_a,
        "chuyen_lap_b": chuyen_lap_b,
        "chuyen_tu": chuyen_tu,
        "tam_ung_khoan": tam_ung_khoan,
        "chuyen_chay_tx": chuyen_chay_tx,
        "don_giao_ui": don_giao_ui,
        "chi_phi_xoa": chi_phi_xoa,
        "chuyen_suco": chuyen_suco,
        "don_tra_hang": don_tra_hang,
        "chuyen_qt": chuyen_qt,
        "phai_thu_cn": phai_thu_cn,
    }


# ---------- Tiện ích Playwright ----------

FETCH_HOOK_SCRIPT = r"""
(() => {
  window.__phaLogs = [];
  window.__phaDelays = [];  // [{pattern: RegExp|string, ms: number}]
  window.__phaFailOnce = []; // [{pattern: RegExp|string, status: number, body: object}]
  const origFetch = window.fetch.bind(window);
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : (input instanceof URL ? input.href : input.url);
    const method = (init && init.method) || (typeof input !== 'string' && input.method) || 'GET';
    let bodyText = null;
    if (init && typeof init.body === 'string') bodyText = init.body;
    const entry = { url, method: method.toUpperCase(), bodyText, t: Date.now() };
    window.__phaLogs.push(entry);

    for (const d of window.__phaDelays) {
      const re = d.pattern instanceof RegExp ? d.pattern : new RegExp(d.pattern);
      if (re.test(url) && (!d.method || d.method.toUpperCase() === entry.method)) {
        await new Promise((r) => setTimeout(r, d.ms));
      }
    }

    for (let i = 0; i < window.__phaFailOnce.length; i++) {
      const f = window.__phaFailOnce[i];
      const re = f.pattern instanceof RegExp ? f.pattern : new RegExp(f.pattern);
      if (re.test(url) && (!f.method || f.method.toUpperCase() === entry.method)) {
        window.__phaFailOnce.splice(i, 1);
        return new Response(JSON.stringify(f.body), {
          status: f.status,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }
    return origFetch(input, init);
  };
})();
"""


def mo_phien(browser, ten: str, mk: str = "demo12345") -> tuple[BrowserContext, Page, list[str], list[str]]:
    """Tạo context sạch, cài hook window.fetch qua add_init_script, đăng nhập và bắt dialog/pageerror."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(FETCH_HOOK_SCRIPT)
    page = ctx.new_page()
    dialogs: list[str] = []
    errors: list[str] = []

    def on_dialog(d):
        dialogs.append(f"{d.type}: {d.message}")
        d.dismiss()

    page.on("dialog", on_dialog)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

    page.goto(f"{FRONTEND}/dang-nhap", wait_until="domcontentloaded")
    ok = page.evaluate(
        """async ([u, p]) => {
          const r = await fetch('/api/auth/dang-nhap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ ten_dang_nhap: u, mat_khau: p }),
          });
          return r.status;
        }""",
        [ten, mk],
    )
    if ok != 200:
        raise RuntimeError(f"Đăng nhập trình duyệt {ten} thất bại: status={ok}")
    page.evaluate("() => { window.__phaLogs = []; }")
    return ctx, page, dialogs, errors


def xoa_log(page: Page) -> None:
    page.evaluate("() => { window.__phaLogs = []; window.__phaDelays = []; window.__phaFailOnce = []; }")


def lay_log(page: Page, pattern: str, method: str | None = None) -> list[dict[str, Any]]:
    logs = page.evaluate("() => window.__phaLogs || []")
    out = []
    for e in logs:
        if re.search(pattern, e["url"]) and (method is None or e["method"] == method.upper()):
            out.append(e)
    return out


def hop_xac_nhan(page: Page):
    return page.locator(".hop-thoai.xac-nhan[role='alertdialog']")


def main() -> int:
    kq = KetQua()
    print(f"=== Bắt đầu 01_hop_xac_nhan.py (TAG={TAG}) ===", flush=True)
    try:
        du = chuan_bi_du_lieu()
    except Exception as e:
        print(f"[LỖI] Chuẩn bị dữ liệu thất bại: {e}")
        traceback.print_exc()
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # =====================================================================
            # NHÓM 1: Điều phối — Chốt chuyến (BR-23), Focus, Esc/Enter/Space,
            # Back/Forward, Đổi chuyến khi đang hỏi / mạng chậm, Lỗi 4xx sau đồng ý
            # =====================================================================
            ctx, page, dialogs, errors = mo_phien(browser, "dieuphoi")
            try:
                cid_a = du["chuyen_lap_a"]["id"]
                cid_b = du["chuyen_lap_b"]["id"]

                # XN-01: Chốt chuyến rỗng -> hộp xác nhận thay window.confirm, focus ở "Thôi", Enter đóng không gửi lần 2
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_a}", wait_until="networkidle")
                page.get_by_role("button", name="Chốt chuyến").wait_for(timeout=10000)
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)

                focus_text = page.evaluate("() => document.activeElement?.textContent?.trim() || ''")
                # Kiểm tra bẫy focus: nhấn Tab 4 lần, activeElement luôn ở trong hộp xác nhận
                focus_trong = True
                for _ in range(4):
                    page.keyboard.press("Tab")
                    if not page.evaluate(
                        "() => !!document.querySelector('.hop-thoai.xac-nhan')?.contains(document.activeElement)"
                    ):
                        focus_trong = False
                # Đưa focus lại về "Thôi" rồi bấm Enter -> phải đóng và không gửi request chốt thứ 2
                hop_xac_nhan(page).get_by_role("button", name="Thôi").focus()
                page.keyboard.press("Enter")
                hop_xac_nhan(page).wait_for(state="hidden", timeout=3000)
                page.wait_for_timeout(300)
                req_chot = lay_log(page, rf"/api/chuyen/{cid_a}/chot", "POST")
                dat = (not dialogs) and (focus_text == "Thôi") and focus_trong and len(req_chot) == 1
                kq.ghi(
                    "XN-01_chot_focus_tab_enter_thoi",
                    dat,
                    f"dialogs={len(dialogs)}, focus_mac_dinh={focus_text!r}, bay_focus={focus_trong}, so_POST_chot={len(req_chot)}",
                )

                # XN-02: Enter/Space/Esc dồn dập khi hộp đang mở -> đóng gọn, không gửi chốt có xác nhận
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                for key in ["Escape", "Escape", "Enter", "Space", "Escape"]:
                    page.keyboard.press(key)
                page.wait_for_timeout(400)
                con_mo = hop_xac_nhan(page).is_visible()
                req_chot = lay_log(page, rf"/api/chuyen/{cid_a}/chot", "POST")
                da_gui_xac_nhan = any(r["bodyText"] and "true" in r["bodyText"] for r in req_chot)
                kq.ghi(
                    "XN-02_spam_esc_enter_space",
                    (not con_mo) and (not da_gui_xac_nhan) and (not dialogs),
                    f"con_mo={con_mo}, so_POST={len(req_chot)}, da_gui_xac_nhan={da_gui_xac_nhan}",
                )

                # XN-03: Back/Forward khi hộp đang mở -> tự đóng, không đồng ý, Forward không mở lại hộp cũ
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen", wait_until="networkidle")
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_a}", wait_until="networkidle")
                page.get_by_role("button", name="Chốt chuyến").wait_for(timeout=10000)
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                page.go_back(wait_until="domcontentloaded")
                page.wait_for_timeout(400)
                mo_sau_back = hop_xac_nhan(page).is_visible()
                page.go_forward(wait_until="domcontentloaded")
                page.wait_for_timeout(400)
                mo_sau_fwd = hop_xac_nhan(page).is_visible()
                req_chot = lay_log(page, rf"/api/chuyen/{cid_a}/chot", "POST")
                da_gui_xn = any(r["bodyText"] and "true" in r["bodyText"] for r in req_chot)
                kq.ghi(
                    "XN-03_back_forward_khi_hop_mo",
                    (not mo_sau_back) and (not mo_sau_fwd) and (not da_gui_xn),
                    f"mo_sau_back={mo_sau_back}, mo_sau_fwd={mo_sau_fwd}, da_gui_xac_nhan={da_gui_xn}",
                )

                # XN-04: Đổi chuyến trong lúc POST chốt chuyến đầu tiên bị mạng chậm -> hộp hỏi của chuyến A không hiện ở chuyến B
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_a}", wait_until="networkidle")
                page.get_by_role("button", name="Chốt chuyến").wait_for(timeout=10000)
                xoa_log(page)
                page.evaluate(
                    "([id]) => { window.__phaDelays.push({ pattern: `/api/chuyen/${id}/chot`, method: 'POST', ms: 1000 }); }",
                    [cid_a],
                )
                page.get_by_role("button", name="Chốt chuyến").click()
                page.wait_for_timeout(150)
                # Bấm chuyển sang chuyến B trong cột trái (hoặc điều hướng thẳng)
                nut_b = page.locator(".ct2-ds button", has_text=du["chuyen_lap_b"]["ma_chuyen"])
                if nut_b.count() > 0:
                    nut_b.first.click()
                else:
                    page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_b}", wait_until="domcontentloaded")
                page.wait_for_timeout(1400)
                mo_o_b = hop_xac_nhan(page).is_visible()
                ma_hien = page.locator(".ct-nhan .ma").text_content() or ""
                kq.ghi(
                    "XN-04_doi_chuyen_khi_cho_chot_mang_cham",
                    (not mo_o_b) and (du["chuyen_lap_b"]["ma_chuyen"] in ma_hien),
                    f"mo_hop_o_chuyen_B={mo_o_b}, ma_dang_hien={ma_hien.strip()!r}",
                )

                # XN-05: Lỗi 4xx sau khi bấm Đồng ý chốt -> đóng hộp, hiện lỗi, không kẹt disabled, mở lại được
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_a}", wait_until="networkidle")
                page.get_by_role("button", name="Chốt chuyến").wait_for(timeout=10000)
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                # Giả lập request thứ 2 (sau đồng ý) trả 409
                page.evaluate(
                    """([id]) => {
                      window.__phaFailOnce.push({
                        pattern: `/api/chuyen/${id}/chot`,
                        method: 'POST',
                        status: 409,
                        body: { ma: 'BR-09', thong_diep: 'Giả lập 409 sau khi đồng ý', chi_tiet: [] }
                      });
                    }""",
                    [cid_a],
                )
                hop_xac_nhan(page).get_by_role("button", name="Vẫn chốt").click()
                hop_xac_nhan(page).wait_for(state="hidden", timeout=4000)
                page.wait_for_timeout(400)
                co_loi = page.locator("[role='alert']").filter(has_text="Giả lập 409").count() > 0
                nut_chot = page.get_by_role("button", name="Chốt chuyến")
                khong_ket = nut_chot.is_visible() and nut_chot.is_enabled()
                kq.ghi(
                    "XN-05_loi_4xx_sau_dong_y_chot",
                    co_loi and khong_ket and (not errors),
                    f"co_loi_409={co_loi}, nut_san_sang={khong_ket}, errors={errors}",
                )

                # XN-06: Mạng chậm + bấm Đồng ý chốt thật -> đúng 1 request xác nhận kèm xac_nhan_chay_rong=true
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                page.evaluate(
                    "([id]) => { window.__phaDelays.push({ pattern: `/api/chuyen/${id}/chot`, method: 'POST', ms: 700 }); }",
                    [cid_a],
                )
                hop_xac_nhan(page).get_by_role("button", name="Vẫn chốt").click()
                page.wait_for_timeout(1200)
                reqs = [
                    r
                    for r in lay_log(page, rf"/api/chuyen/{cid_a}/chot", "POST")
                    if r["bodyText"] and "xac_nhan_chay_rong" in r["bodyText"] and "true" in r["bodyText"]
                ]
                da_chot = page.locator(".ct-nhan").filter(has_text="Đã chốt").count() > 0
                kq.ghi(
                    "XN-06_chot_chuyen_dong_y_1_request_dung_du_lieu",
                    len(reqs) == 1 and da_chot and (not dialogs),
                    f"so_POST_xac_nhan={len(reqs)}, da_chot_ui={da_chot}, body={reqs[0]['bodyText'] if reqs else None}",
                )

                # XN-07: Đổi chuyến sau khi bấm Đồng ý chốt (lúc request chốt đang chậm) -> không ghi đè chuyến B bằng A!
                # Lập nhanh chuyến A2 ở trạng thái LAP có lãi dương hoặc rỗng -> ta test trên chuyến B vừa có
                page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_b}", wait_until="networkidle")
                page.get_by_role("button", name="Chốt chuyến").wait_for(timeout=10000)
                xoa_log(page)
                page.get_by_role("button", name="Chốt chuyến").click()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                page.evaluate(
                    "([id]) => { window.__phaDelays.push({ pattern: `/api/chuyen/${id}/chot`, method: 'POST', ms: 1000 }); }",
                    [cid_b],
                )
                hop_xac_nhan(page).get_by_role("button", name="Vẫn chốt").click()
                page.wait_for_timeout(100)
                # Chuyển sang chuyến A ngay khi POST chốt của B đang bay
                nut_a = page.locator(".ct2-ds button", has_text=du["chuyen_lap_a"]["ma_chuyen"])
                if nut_a.count() > 0:
                    nut_a.first.click()
                    page.wait_for_timeout(1400)
                    ma_hien = page.locator(".ct-nhan .ma").text_content() or ""
                    khong_ghi_de = du["chuyen_lap_a"]["ma_chuyen"] in ma_hien
                    kq.ghi(
                        "XN-07_doi_chuyen_luc_request_chot_dang_bay",
                        khong_ghi_de,
                        f"mong_doi={du['chuyen_lap_a']['ma_chuyen']!r}, thuc_te_tren_man={ma_hien.strip()!r}",
                    )
                else:
                    kq.bo_qua("XN-07_doi_chuyen_luc_request_chot_dang_bay", "Không thấy chuyến A ở cột cùng ngày")

                # XN-08: Kết thúc do sự cố (BR-68) — hộp xác nhận, đúng 1 POST, đúng lý do & km
                if du["chuyen_suco"]:
                    cid_sc = du["chuyen_suco"]["id"]
                    page.goto(f"{FRONTEND}/dieu-phoi/chuyen/{cid_sc}", wait_until="networkidle")
                    page.get_by_role("button", name="Kết thúc do sự cố").click()
                    page.get_by_label("Lý do").fill(f"{TAG} Hỏng lốp thử XN")
                    page.get_by_label("Km cuối (nếu biết)").fill("10350")
                    xoa_log(page)
                    page.evaluate(
                        "([id]) => { window.__phaDelays.push({ pattern: `/api/chuyen/${id}/ket-thuc-su-co`, method: 'POST', ms: 600 }); }",
                        [cid_sc],
                    )
                    page.get_by_role("button", name="Kết thúc chuyến").click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    cau = hop_xac_nhan(page).locator(".xn-cau").text_content() or ""
                    hop_xac_nhan(page).get_by_role("button", name="Kết thúc chuyến").click()
                    page.wait_for_timeout(1200)
                    reqs = lay_log(page, rf"/api/chuyen/{cid_sc}/ket-thuc-su-co", "POST")
                    dung_payload = (
                        len(reqs) == 1
                        and f"{TAG} Hỏng lốp thử XN" in (reqs[0]["bodyText"] or "")
                        and "10350" in (reqs[0]["bodyText"] or "")
                    )
                    kq.ghi(
                        "XN-08_ket_thuc_su_co",
                        dung_payload and (not dialogs) and (du["chuyen_suco"]["ma_chuyen"] in cau),
                        f"so_POST={len(reqs)}, cau={cau!r}, body={reqs[0]['bodyText'] if reqs else None}",
                    )
                else:
                    kq.bo_qua("XN-08_ket_thuc_su_co", "Không tạo được chuyến chạy hôm nay (sát nửa đêm)")

                # XN-09: Trả hàng đơn thất bại đã lấy (DonDanhSach.tsx) — bấm đúp nút Trả hàng không tự đồng ý, đồng ý gửi đúng 1 POST
                if du["don_tra_hang"]:
                    ma_th = du["don_tra_hang"]["ma_don"]
                    did_th = du["don_tra_hang"]["id"]
                    page.goto(f"{FRONTEND}/dieu-phoi/don", wait_until="networkidle")
                    dong_th = page.locator("tr", has_text=ma_th).first
                    dong_th.wait_for(state="visible", timeout=10000)
                    xoa_log(page)
                    dong_th.get_by_role("button", name="Trả hàng").dblclick()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    page.wait_for_timeout(200)
                    req_truoc = lay_log(page, rf"/api/don/{did_th}/tra-hang", "POST")
                    # Bấm đồng ý với mạng chậm
                    page.evaluate(
                        "([id]) => { window.__phaDelays.push({ pattern: `/api/don/${id}/tra-hang`, method: 'POST', ms: 600 }); }",
                        [did_th],
                    )
                    hop_xac_nhan(page).get_by_role("button", name="Trả hàng").click()
                    page.wait_for_timeout(1100)
                    req_sau = lay_log(page, rf"/api/don/{did_th}/tra-hang", "POST")
                    kq.ghi(
                        "XN-09_tra_hang_dblclick_va_dong_y",
                        len(req_truoc) == 0 and len(req_sau) == 1 and (not dialogs),
                        f"req_sau_dblclick={len(req_truoc)}, req_sau_dong_y={len(req_sau)}",
                    )
                else:
                    kq.bo_qua("XN-09_tra_hang_dblclick_va_dong_y", "Không có đơn thất bại PHA- đã lấy")

                # XN-10: Ngừng tài xế PHA- (TaiXeDanhSach.tsx) — bấm đúp nút Ngừng, mạng chậm, đúng 1 PATCH
                tx_ngung = du["tx_ds"][0]
                page.goto(f"{FRONTEND}/dieu-phoi/tai-xe", wait_until="networkidle")
                page.get_by_placeholder("Tìm họ tên, số GPLX, SĐT").fill(tx_ngung["ho_ten"])
                dong_tx = page.locator("tbody tr", has_text=tx_ngung["ho_ten"]).first
                dong_tx.wait_for(state="visible", timeout=10000)
                xoa_log(page)
                dong_tx.get_by_role("button", name="Ngừng").dblclick()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                req_truoc = lay_log(page, rf"/api/tai-xe/{tx_ngung['id']}", "PATCH")
                page.evaluate(
                    "([id]) => { window.__phaDelays.push({ pattern: `/api/tai-xe/${id}`, method: 'PATCH', ms: 700 }); }",
                    [tx_ngung["id"]],
                )
                hop_xac_nhan(page).get_by_role("button", name="Ngừng").click()
                # Bấm lại nút Ngừng ngay lúc request PATCH đang bay (nút không disable -> kiểm tra dangDoi.current)
                if dong_tx.get_by_role("button", name="Ngừng").is_visible():
                    dong_tx.get_by_role("button", name="Ngừng").click()
                page.wait_for_timeout(1100)
                req_sau = lay_log(page, rf"/api/tai-xe/{tx_ngung['id']}", "PATCH")
                dung_body = len(req_sau) == 1 and '"NGUNG"' in (req_sau[0]["bodyText"] or "")
                kq.ghi(
                    "XN-10_ngung_tai_xe_dblclick_va_mang_cham",
                    len(req_truoc) == 0 and dung_body and (not dialogs),
                    f"req_sau_dblclick={len(req_truoc)}, so_PATCH={len(req_sau)}, body={req_sau[0]['bodyText'] if req_sau else None}",
                )
            finally:
                ctx.close()

            # =====================================================================
            # NHÓM 2: Quản lý — Khóa tài khoản PHA- + Hai hộp chồng nhau (.nen-mo)
            # =====================================================================
            ctx, page, dialogs, errors = mo_phien(browser, "quanly")
            try:
                nd_pha = du["nd_pha"]
                page.goto(f"{FRONTEND}/quan-ly/nguoi-dung", wait_until="networkidle")
                page.get_by_placeholder("Tìm tên đăng nhập, họ tên").fill(nd_pha["ten_dang_nhap"])
                dong_nd = page.locator("tbody tr", has_text=nd_pha["ten_dang_nhap"]).first
                dong_nd.wait_for(state="visible", timeout=10000)

                # XN-11: Khóa tài khoản PHA- — bấm đúp nút Khóa, đồng ý mạng chậm -> đúng 1 PATCH
                xoa_log(page)
                dong_nd.get_by_role("button", name="Khóa", exact=True).dblclick()
                hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                req_truoc = lay_log(page, rf"/api/nguoi-dung/{nd_pha['id']}", "PATCH")
                page.evaluate(
                    "([id]) => { window.__phaDelays.push({ pattern: `/api/nguoi-dung/${id}`, method: 'PATCH', ms: 700 }); }",
                    [nd_pha["id"]],
                )
                hop_xac_nhan(page).get_by_role("button", name="Khóa", exact=True).click()
                if dong_nd.get_by_role("button", name="Khóa", exact=True).is_visible():
                    dong_nd.get_by_role("button", name="Khóa", exact=True).click()
                page.wait_for_timeout(1100)
                req_sau = lay_log(page, rf"/api/nguoi-dung/{nd_pha['id']}", "PATCH")
                dung = len(req_truoc) == 0 and len(req_sau) == 1 and '"NGUNG"' in (req_sau[0]["bodyText"] or "")
                kq.ghi(
                    "XN-11_khoa_tai_khoan_pha",
                    dung and (not dialogs),
                    f"req_sau_dblclick={len(req_truoc)}, so_PATCH={len(req_sau)}, body={req_sau[0]['bodyText'] if req_sau else None}",
                )

                # XN-12: Hai hộp chồng nhau (.nen-mo modal + HopXacNhan portal):
                # Mở modal "Thêm người dùng", sau đó chèn giả lập 1 lớp mở hoặc kiểm tra thứ tự Esc trên 2 .nen-mo
                page.get_by_role("button", name="Thêm người dùng").click()
                page.locator(".hop-thoai").filter(has_text="Thêm người dùng").wait_for(state="visible", timeout=4000)
                # Mở thêm 1 hộp xác nhận trên cùng bằng cách click nút Khóa? Không được vì nền mờ che; ta mở lại nút Mở khóa rồi dùng Esc 2 lần trên 2 modal thật:
                # Cách tái hiện 2 hộp chồng nhau đúng DOM: mở modal Thêm người dùng, kích nút Khóa bằng DOM click (như shortcut/race) để mở HopXacNhan chồng lên modal
                # Mở khóa lại tài khoản PHA- qua API trước rồi reload không cần; dùng ngay nút Sửa của modal:
                page.evaluate(
                    """() => {
                      const b = document.querySelector('button.nguy-hiem');
                      if (b && b.textContent.trim() === 'Mở khóa') b.click();
                    }"""
                )
                page.wait_for_timeout(400)
                page.evaluate(
                    """() => {
                      const b = Array.from(document.querySelectorAll('button.nguy-hiem')).find(x => x.textContent.trim() === 'Khóa');
                      if (b) b.click();
                    }"""
                )
                page.wait_for_timeout(300)
                so_nen_truoc = page.locator(".nen-mo").count()
                if so_nen_truoc == 2:
                    # Esc lần 1: chỉ đóng HopXacNhan trên cùng, modal Thêm người dùng vẫn còn
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(200)
                    so_nen_sau_1 = page.locator(".nen-mo").count()
                    con_form = page.locator(".hop-thoai").filter(has_text="Thêm người dùng").is_visible()
                    # Esc lần 2: đóng luôn modal Thêm người dùng
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(200)
                    so_nen_sau_2 = page.locator(".nen-mo").count()
                    kq.ghi(
                        "XN-12_hai_hop_chong_nhau_esc_tung_lop",
                        so_nen_sau_1 == 1 and con_form and so_nen_sau_2 == 0,
                        f"nen_truoc={so_nen_truoc}, sau_esc1={so_nen_sau_1} (con_form={con_form}), sau_esc2={so_nen_sau_2}",
                    )
                else:
                    page.keyboard.press("Escape")
                    kq.bo_qua("XN-12_hai_hop_chong_nhau_esc_tung_lop", f"Không dựng được 2 .nen-mo chồng nhau (đếm={so_nen_truoc})")
            finally:
                ctx.close()

            # =====================================================================
            # NHÓM 3: Kế toán — Thu hồi tạm ứng, Ghi thu công nợ, Quyết toán
            # =====================================================================
            ctx, page, dialogs, errors = mo_phien(browser, "ketoan")
            try:
                # XN-13: Thu hồi tạm ứng (TamUng.tsx) — mạng chậm + đúng 1 POST
                if du["tam_ung_khoan"]:
                    tu_k = du["tam_ung_khoan"]
                    page.goto(f"{FRONTEND}/ke-toan/tam-ung", wait_until="networkidle")
                    page.locator("select").first.select_option(str(du["chuyen_tu"]["id"]))
                    page.get_by_role("button", name="Thu hồi").first.wait_for(state="visible", timeout=8000)
                    xoa_log(page)
                    page.get_by_role("button", name="Thu hồi").first.dblclick()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    req_truoc = lay_log(page, rf"/api/tam-ung/{tu_k['id']}/thu-hoi", "POST")
                    page.evaluate(
                        "([id]) => { window.__phaDelays.push({ pattern: `/api/tam-ung/${id}/thu-hoi`, method: 'POST', ms: 700 }); }",
                        [tu_k["id"]],
                    )
                    hop_xac_nhan(page).get_by_role("button", name="Thu hồi").click()
                    page.wait_for_timeout(1200)
                    req_sau = lay_log(page, rf"/api/tam-ung/{tu_k['id']}/thu-hoi", "POST")
                    kq.ghi(
                        "XN-13_thu_hoi_tam_ung",
                        len(req_truoc) == 0 and len(req_sau) == 1 and (not dialogs),
                        f"req_truoc={len(req_truoc)}, req_sau={len(req_sau)}",
                    )
                else:
                    kq.bo_qua("XN-13_thu_hoi_tam_ung", "Tuyến có định mức < 20.000 đ nên không cấp được tạm ứng")

                # XN-14: Ghi thu công nợ (CongNo.tsx) — kiểm tra đúng payload phai_thu_ids & ngay, đúng 1 POST
                if du["phai_thu_cn"]:
                    pt = du["phai_thu_cn"]
                    page.goto(f"{FRONTEND}/ke-toan/cong-no", wait_until="networkidle")
                    nut_kh = page.locator(".qt-ds button", has_text=du["kh"]["ten"]).first
                    nut_kh.wait_for(state="visible", timeout=10000)
                    nut_kh.click()
                    cb = page.get_by_label(f"Chọn {pt['ma_don']}")
                    cb.wait_for(state="visible", timeout=8000)
                    cb.check()
                    xoa_log(page)
                    page.evaluate(
                        "() => { window.__phaDelays.push({ pattern: '/api/phai-thu/da-thu', method: 'POST', ms: 700 }); }"
                    )
                    page.get_by_role("button", name="Đánh dấu đã thu").click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    cau = hop_xac_nhan(page).locator(".xn-cau").text_content() or ""
                    hop_xac_nhan(page).get_by_role("button", name="Đã thu").click()
                    page.wait_for_timeout(1200)
                    reqs = lay_log(page, r"/api/phai-thu/da-thu", "POST")
                    dung_id = len(reqs) == 1 and str(pt["id"]) in (reqs[0]["bodyText"] or "")
                    kq.ghi(
                        "XN-14_ghi_thu_cong_no",
                        dung_id and (du["kh"]["ten"] in cau) and (not dialogs),
                        f"so_POST={len(reqs)}, body={reqs[0]['bodyText'] if reqs else None}",
                    )
                else:
                    kq.bo_qua("XN-14_ghi_thu_cong_no", "Không có khoản phải thu PHA- chưa thu")

                # XN-15: Quyết toán (QuyetToan.tsx) — chuyến kết thúc sự cố cần lương tay, đúng 1 POST, lỗi 4xx trước rồi thành công
                if du["chuyen_qt"]:
                    cid_qt = du["chuyen_qt"]["id"]
                    ma_qt = du["chuyen_qt"]["ma_chuyen"]
                    page.goto(f"{FRONTEND}/ke-toan/quyet-toan", wait_until="networkidle")
                    nut_qt = page.locator(".qt-ds button", has_text=ma_qt).first
                    nut_qt.wait_for(state="visible", timeout=10000)
                    nut_qt.click()
                    page.get_by_label("Lương tài xế (đồng)").wait_for(state="visible", timeout=8000)
                    page.get_by_label("Lương tài xế (đồng)").fill("250000")
                    page.get_by_label("Lý do lương nhập tay").fill(f"{TAG} Lương sự cố")

                    # Thử lỗi 4xx sau khi đồng ý trước
                    xoa_log(page)
                    page.evaluate(
                        """([id]) => {
                          window.__phaFailOnce.push({
                            pattern: `/api/chuyen/${id}/quyet-toan`,
                            method: 'POST',
                            status: 422,
                            body: { ma: 'BR-55', thong_diep: 'Giả lập 422 quyết toán', chi_tiet: [] }
                          });
                        }""",
                        [cid_qt],
                    )
                    page.get_by_role("button", name="Quyết toán", exact=True).click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    hop_xac_nhan(page).get_by_role("button", name="Quyết toán", exact=True).click()
                    page.wait_for_timeout(500)
                    co_loi_qt = page.get_by_text("Giả lập 422 quyết toán").count() > 0

                    # Thử đồng ý thật với mạng chậm -> đúng 1 POST với lương tay 250000
                    xoa_log(page)
                    page.evaluate(
                        "([id]) => { window.__phaDelays.push({ pattern: `/api/chuyen/${id}/quyet-toan`, method: 'POST', ms: 700 }); }",
                        [cid_qt],
                    )
                    page.get_by_role("button", name="Quyết toán", exact=True).click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    hop_xac_nhan(page).get_by_role("button", name="Quyết toán", exact=True).click()
                    page.wait_for_timeout(1200)
                    reqs = lay_log(page, rf"/api/chuyen/{cid_qt}/quyet-toan", "POST")
                    dung = (
                        co_loi_qt
                        and len(reqs) == 1
                        and "250000" in (reqs[0]["bodyText"] or "")
                        and f"{TAG} Lương sự cố" in (reqs[0]["bodyText"] or "")
                    )
                    kq.ghi(
                        "XN-15_quyet_toan_4xx_va_dong_y",
                        dung and (not dialogs),
                        f"co_loi_422={co_loi_qt}, so_POST={len(reqs)}, body={reqs[0]['bodyText'] if reqs else None}",
                    )
                else:
                    kq.bo_qua("XN-15_quyet_toan_4xx_va_dong_y", "Không có chuyến hoàn thành PHA-")
            finally:
                ctx.close()

            # =====================================================================
            # NHÓM 4: Tài xế PHA- — Xóa chi phí & Xác nhận giao hàng
            # =====================================================================
            if du["chuyen_chay_tx"] and du["chi_phi_xoa"] and du["don_giao_ui"]:
                tx1 = du["tx_ds"][1]
                ctx, page, dialogs, errors = mo_phien(browser, tx1["ten_dang_nhap"], tx1["mat_khau"])
                try:
                    cid_tx = du["chuyen_chay_tx"]["id"]
                    cp_id = du["chi_phi_xoa"]["id"]
                    ma_giao = du["don_giao_ui"]["ma_don"]
                    page.goto(f"{FRONTEND}/tai-xe/chuyen/{cid_tx}", wait_until="networkidle")

                    # XN-16: Xóa chi phí (ChiPhi.tsx) — bấm đúp, mạng chậm, đúng 1 DELETE
                    dong_cp = page.locator(".ds-chi li", has_text=f"{TAG} Chi phí xóa").first
                    dong_cp.wait_for(state="visible", timeout=10000)
                    xoa_log(page)
                    dong_cp.get_by_role("button", name="Xóa").dblclick()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    req_truoc = lay_log(page, rf"/api/toi/chi-phi/{cp_id}", "DELETE")
                    page.evaluate(
                        "([id]) => { window.__phaDelays.push({ pattern: `/api/toi/chi-phi/${id}`, method: 'DELETE', ms: 700 }); }",
                        [cp_id],
                    )
                    hop_xac_nhan(page).get_by_role("button", name="Xóa").click()
                    if dong_cp.get_by_role("button", name="Xóa").is_visible():
                        dong_cp.get_by_role("button", name="Xóa").click()
                    page.wait_for_timeout(1200)
                    req_sau = lay_log(page, rf"/api/toi/chi-phi/{cp_id}", "DELETE")
                    kq.ghi(
                        "XN-16_xoa_chi_phi_dblclick_va_mang_cham",
                        len(req_truoc) == 0 and len(req_sau) == 1 and (not dialogs),
                        f"req_truoc={len(req_truoc)}, req_sau={len(req_sau)}",
                    )

                    # XN-17: Xác nhận giao hàng (GiaoHang.tsx) — đủ 4 điều kiện, bấm Thôi không gửi, đồng ý mạng chậm gửi đúng 1 POST
                    diem_giao = page.locator(f"#diem-GIAO-{du['don_giao_ui']['id']}")
                    diem_giao.wait_for(state="visible", timeout=8000)
                    diem_giao.get_by_role("button", name="Giao hàng").click()
                    diem_giao.get_by_placeholder("DH-…").fill(ma_giao)
                    diem_giao.get_by_role("button", name="Xác nhận mã").click()
                    diem_giao.locator("input[type='file']").set_input_files(
                        {"name": "pod.png", "mimeType": "image/png", "buffer": PNG_HOP_LE}
                    )
                    diem_giao.get_by_role("textbox", name="Tên người nhận").fill("Chị PHA Nhận")
                    # Ký 1 nét lên canvas chữ ký
                    cv = diem_giao.locator("canvas").first
                    box = cv.bounding_box()
                    assert box is not None
                    page.mouse.move(box["x"] + 20, box["y"] + 40)
                    page.mouse.down()
                    page.mouse.move(box["x"] + 120, box["y"] + 80, steps=5)
                    page.mouse.up()

                    # Bấm Xác nhận giao -> bấm Thôi -> không gửi POST /api/toi/quet
                    xoa_log(page)
                    diem_giao.get_by_role("button", name="Xác nhận giao").click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    cau_giao = hop_xac_nhan(page).locator(".xn-cau").text_content() or ""
                    hop_xac_nhan(page).get_by_role("button", name="Thôi").click()
                    hop_xac_nhan(page).wait_for(state="hidden", timeout=3000)
                    page.wait_for_timeout(300)
                    req_sau_thoi = lay_log(page, r"/api/toi/quet", "POST")

                    # Bấm lại Xác nhận giao -> đồng ý với mạng chậm -> đúng 1 POST /api/toi/quet
                    page.evaluate(
                        "() => { window.__phaDelays.push({ pattern: '/api/toi/quet', method: 'POST', ms: 700 }); }"
                    )
                    diem_giao.get_by_role("button", name="Xác nhận giao").click()
                    hop_xac_nhan(page).wait_for(state="visible", timeout=5000)
                    hop_xac_nhan(page).get_by_role("button", name="Đã giao").click()
                    page.wait_for_timeout(1500)
                    req_sau_dong_y = lay_log(page, r"/api/toi/quet", "POST")
                    kq.ghi(
                        "XN-17_xac_nhan_giao_thoi_va_dong_y",
                        len(req_sau_thoi) == 0
                        and len(req_sau_dong_y) == 1
                        and (ma_giao in cau_giao)
                        and ("Chị PHA Nhận" in cau_giao)
                        and (not dialogs),
                        f"req_thoi={len(req_sau_thoi)}, req_dong_y={len(req_sau_dong_y)}, cau={cau_giao!r}",
                    )
                finally:
                    ctx.close()
            else:
                kq.bo_qua("XN-16_xoa_chi_phi_dblclick_va_mang_cham", "Không có chuyến chạy PHA- hôm nay")
                kq.bo_qua("XN-17_xac_nhan_giao_thoi_va_dong_y", "Không có chuyến chạy PHA- hôm nay")
        finally:
            browser.close()

    return kq.tong_ket()


if __name__ == "__main__":
    sys.exit(main())
