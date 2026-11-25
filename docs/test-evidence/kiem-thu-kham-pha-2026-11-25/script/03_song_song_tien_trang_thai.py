#!/usr/bin/env python3
"""
03_song_song_tien_trang_thai.py - Kiểm thử tiền và trạng thái song song (2-10 request đồng thời)
và các cặp hành động xung đột đồng thời:
- Tạm ứng: cấp song song (BR-53), thu hồi song song, sửa song song & sửa vs thu hồi
- Chi phí: duyệt song song, duyệt vs từ chối song song (không lặp ca xóa song song đã biết DA-BIET-1)
- Quyết toán: quyết toán song song (BR-29)
- Công nợ: ghi thu song song cùng danh sách & ghi thu chồng chéo [pt1,pt2] vs [pt2,pt3] (BR-56)
- Chuyến: chốt / mở chốt / hủy / bắt đầu / kết thúc song song; 2 chuyến cùng xe bắt đầu song song (BR-26)
- Quét & Sự cố: quét lấy / quét giao song song (BR-45, không trùng PhaiThu), LAY vs KHONG_LAY,
  GIAO vs GIAO_THAT_BAI, đóng sự cố song song
- Xung đột 2 hành động trái ngược cùng lúc:
  1) Mở chốt + Cấp tạm ứng (BR-24)
  2) Hủy chuyến + Cấp tạm ứng (BR-25)
  3) Quyết toán + Ghi chi phí mới (BR-29, BR-55)
  4) Quyết toán + Duyệt/Điều chỉnh chi phí (BR-29, BR-55)
  5) Hủy chuyến + Ghép đơn (BR-09, BR-25)
  6) Chốt chuyến + Sửa đơn đang ghép (BR-23, BR-33, kiểm deadlock)
  7) Kết thúc do sự cố + Quét giao cùng lúc (BR-68, BR-56)
  8) Hai chuyến cùng ghép 1 đơn CHO_GHEP cùng lúc (BR-07)

Chỉ dùng thư viện chuẩn Python (urllib, concurrent.futures, threading) - không cần httpx.
Chạy độc lập: py -3.12 -I -X utf8 kiem-thu-kham-pha/03_song_song_tien_trang_thai.py
"""

from __future__ import annotations

import json
import random
import re
import struct
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

BACKEND = "http://127.0.0.1:8000"
VN_TZ = timezone(timedelta(hours=7))
TAG = f"PHA-SS-{int(time.time()) % 100000}-{random.randint(100, 999)}"


def tao_png_1x1() -> bytes:
    def chunk(loai: bytes, du_lieu: bytes) -> bytes:
        crc = zlib.crc32(loai + du_lieu) & 0xFFFFFFFF
        return struct.pack(">I", len(du_lieu)) + loai + du_lieu + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"\x00\x00\xff\x00"))
        + chunk(b"IEND", b"")
    )


PNG = tao_png_1x1()


class ApiClient:
    """Thread-safe khi mỗi lời gọi dùng token đã đăng nhập (chỉ đọc self.token)."""

    def __init__(self, base: str = BACKEND, token: str | None = None):
        self.base = base.rstrip("/")
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        multipart: tuple[dict[str, Any], list[tuple[str, str, bytes, str]]] | None = None,
        timeout: float = 25.0,
    ) -> tuple[int, Any]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Cookie"] = f"access_token={self.token}"
        data: bytes | None = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif multipart is not None:
            fields, files = multipart
            boundary = f"----PhaSS{random.randint(100000, 999999)}"
            parts: list[bytes] = []
            for k, v in fields.items():
                if v is None:
                    continue
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{k}"\r\n\r\n'
                    f"{v}\r\n".encode("utf-8")
                )
            for fname, filename, content, ctype in files:
                parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{fname}"; filename="{filename}"\r\n'
                    f"Content-Type: {ctype}\r\n\r\n".encode("utf-8")
                    + content
                    + b"\r\n"
                )
            parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            data = b"".join(parts)
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        req = urllib.request.Request(f"{self.base}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
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
        except Exception as e:
            return 0, f"EXC: {type(e).__name__}: {e}"

    def dang_nhap(self, ten: str, mk: str = "demo12345") -> None:
        st, body = self.request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": ten, "mat_khau": mk})
        if st != 200:
            raise RuntimeError(f"Đăng nhập {ten} thất bại: {st} {body}")


def ban_dong_loat(cac_ham: list[Callable[[], tuple[int, Any]]]) -> list[tuple[int, Any]]:
    """Đồng bộ tất cả thread tại Barrier rồi phóng đồng thời."""
    barrier = threading.Barrier(len(cac_ham))

    def boc(fn: Callable[[], tuple[int, Any]]) -> tuple[int, Any]:
        try:
            barrier.wait(timeout=15)
        except threading.BrokenBarrierError:
            pass
        return fn()

    with ThreadPoolExecutor(max_workers=len(cac_ham)) as ex:
        futs = [ex.submit(boc, fn) for fn in cac_ham]
        return [f.result() for f in futs]


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
        print(f"\n=== TỔNG KẾT 03_song_song_tien_trang_thai: tổng={len(self.ds)} | đạt={dat} | lỗi={loi} | bỏ qua={bq} ===")
        return 1 if loi else 0


class MoiTruong:
    """Factory tạo tài nguyên PHA- riêng cho từng ca song song, tránh đụng lịch BR-16/17."""

    def __init__(self) -> None:
        self.ql = ApiClient()
        self.ql.dang_nhap("quanly")
        self.dp = ApiClient()
        self.dp.dang_nhap("dieuphoi")
        self.kt = ApiClient()
        self.kt.dang_nhap("ketoan")
        self.now_vn = datetime.now(VN_TZ)
        self.nam_sau = (self.now_vn + timedelta(days=365)).strftime("%Y-%m-%d")
        self.han_giao = (self.now_vn + timedelta(days=120)).isoformat(timespec="seconds")
        self._slot_ngay = 2

        st, tuyen_res = self.dp.request("GET", "/api/tuyen?trang_thai=HOAT_DONG&so_dong=100")
        assert st == 200 and tuyen_res["du_lieu"]
        st, nut_res = self.dp.request("GET", "/api/nut?so_dong=100")
        nut_map = {n["id"]: n for n in nut_res["du_lieu"]}
        st, bg_res = self.ql.request("GET", "/api/bang-gia?so_dong=100")
        cap_gia = {(b["tinh_lay"].strip().lower(), b["tinh_giao"].strip().lower()) for b in bg_res["du_lieu"]}

        self.tuyen = None
        self.nut_lay_id = None
        self.nut_giao_id = None
        for t in tuyen_res["du_lieu"]:
            dm = (t.get("dm_dau") or 0) + (t.get("dm_cau_duong") or 0) + (t.get("dm_boc_xep") or 0)
            ds_nut = t.get("nut") or []
            for i in range(len(ds_nut)):
                for j in range(i + 1, len(ds_nut)):
                    n1 = nut_map.get(ds_nut[i]["nut_id"])
                    n2 = nut_map.get(ds_nut[j]["nut_id"])
                    if n1 and n2 and (n1["tinh"].strip().lower(), n2["tinh"].strip().lower()) in cap_gia:
                        if dm >= 100000 or self.tuyen is None:
                            self.tuyen = t
                            self.nut_lay_id = n1["id"]
                            self.nut_giao_id = n2["id"]
                            if dm >= 100000:
                                break
                if self.tuyen and (
                    (self.tuyen.get("dm_dau") or 0)
                    + (self.tuyen.get("dm_cau_duong") or 0)
                    + (self.tuyen.get("dm_boc_xep") or 0)
                    >= 100000
                ):
                    break
        assert self.tuyen is not None, "Không tìm thấy tuyến khớp bảng giá"

        st, self.kh = self.dp.request(
            "POST",
            "/api/khach-hang",
            {"ten": f"{TAG} Khách song song", "sdt": f"092{random.randint(1000000, 9999999)}"},
        )
        assert st == 201, f"Tạo khách lỗi: {st} {self.kh}"

        st, ly_do = self.dp.request("GET", "/api/danh-muc/ly-do")
        self.ly_do_lay = next((x["id"] for x in ly_do if x["ap_dung"] == "LAY"), None)
        self.ly_do_giao = next((x["id"] for x in ly_do if x["ap_dung"] == "GIAO"), None)

    def tao_xe(self, km: int = 5000) -> dict[str, Any]:
        bs = f"51S-{random.randint(10000, 99999)}"
        st, xe = self.dp.request(
            "POST",
            "/api/xe",
            {
                "bien_so": bs,
                "tai_trong_kg": 5000,
                "the_tich_m3": "20.00",
                "ktt_toan_bo_kg": 8000,
                "han_dang_kiem": self.nam_sau,
                "han_bao_hiem": self.nam_sau,
                "dinh_muc_lit_100km": "18.00",
                "km_dong_ho": km,
            },
        )
        assert st == 201, f"Tạo xe lỗi: {st} {xe}"
        return xe

    def tao_tai_xe(self) -> tuple[dict[str, Any], ApiClient]:
        u = f"PHA-sstx-{random.randint(10000, 99999)}-{random.randint(10, 99)}"
        mk = "PhaTest123!"
        st, tx = self.dp.request(
            "POST",
            "/api/tai-xe",
            {
                "ten_dang_nhap": u,
                "mat_khau": mk,
                "ho_ten": f"{TAG} TX {u[-4:]}",
                "so_gplx": f"PHAS{random.randint(1000000, 9999999)}",
                "hang_gplx": "C",
                "han_gplx": self.nam_sau,
                "sdt": f"093{random.randint(1000000, 9999999)}",
            },
        )
        assert st == 201, f"Tạo tài xế lỗi: {st} {tx}"
        cli = ApiClient()
        cli.dang_nhap(u, mk)
        return tx, cli

    def tao_don(self, mo_ta: str, kg: str = "15.00", m3: str = "0.20") -> dict[str, Any]:
        st, d = self.dp.request(
            "POST",
            "/api/don",
            {
                "khach_hang_id": self.kh["id"],
                "mo_ta": f"{TAG} {mo_ta}",
                "kg": kg,
                "m3": m3,
                "so_kien": 1,
                "nut_lay_id": self.nut_lay_id,
                "dia_chi_lay": "Kho PHA lấy",
                "sdt_lay": "0901112222",
                "nut_giao_id": self.nut_giao_id,
                "dia_chi_giao": "Kho PHA giao",
                "nguoi_nhan": "Người nhận PHA",
                "sdt_nhan": "0903334444",
                "han_giao": self.han_giao,
            },
        )
        assert st == 201, f"Tạo đơn lỗi: {st} {d}"
        return d

    def lap_chuyen(self, xe_id: int, tx_id: int, hom_nay: bool = False, offset_phut: int = 2) -> dict[str, Any]:
        if hom_nay:
            kh = (datetime.now(VN_TZ) + timedelta(minutes=offset_phut)).isoformat(timespec="seconds")
        else:
            self._slot_ngay += 1
            kh = (self.now_vn + timedelta(days=self._slot_ngay)).replace(
                hour=8, minute=0, second=0, microsecond=0
            ).isoformat()
        st, c = self.dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": self.tuyen["id"], "khoi_hanh_du_kien": kh, "xe_id": xe_id, "tai_xe_id": tx_id},
        )
        assert st == 201, f"Lập chuyến lỗi: {st} {c}"
        return c

    def chot_chuyen(self, cid: int) -> None:
        st, r = self.dp.request(
            "POST", f"/api/chuyen/{cid}/chot", {"xac_nhan_chay_rong": True, "xac_nhan_lai_am": True}
        )
        assert st == 200, f"Chốt chuyến lỗi: {st} {r}"

    def bat_dau_chuyen(self, tx_cli: ApiClient, cid: int, km: int) -> None:
        st, r = tx_cli.request(
            "POST",
            f"/api/toi/chuyen/{cid}/bat-dau",
            multipart=({"km_bat_dau": str(km)}, [("anh_dong_ho", "km.png", PNG, "image/png")]),
        )
        assert st == 200, f"Bắt đầu chuyến lỗi: {st} {r}"


def dem_ma(ket_qua: list[tuple[int, Any]]) -> dict[int, int]:
    out: dict[int, int] = {}
    for st, _ in ket_qua:
        out[st] = out.get(st, 0) + 1
    return out


def khong_500(ket_qua: list[tuple[int, Any]]) -> bool:
    return all(st != 500 and st != 0 for st, _ in ket_qua)


def main() -> int:
    kq = KetQua()
    print(f"=== Bắt đầu 03_song_song_tien_trang_thai.py (TAG={TAG}) ===", flush=True)
    try:
        mt = MoiTruong()
    except Exception as e:
        print(f"[LỖI] Khởi tạo môi trường thất bại: {e}")
        traceback.print_exc()
        return 1

    # Dùng các xe/tài xế riêng cho từng nhóm để không chồng lịch
    xe1 = mt.tao_xe(5000)
    tx1, tx1_cli = mt.tao_tai_xe()

    # =========================================================================
    # 1. TẠM ỨNG SONG SONG: cấp 8 request (mỗi cái 60% định mức), thu hồi 6x, sửa vs thu hồi
    # =========================================================================
    c_tu = mt.lap_chuyen(xe1["id"], tx1["id"])
    mt.chot_chuyen(c_tu["id"])
    st, tu_info = mt.kt.request("GET", f"/api/chuyen/{c_tu['id']}/tam-ung")
    dm = tu_info["dinh_muc"]

    if dm >= 10000:
        moi_lan = int(dm * 0.6)
        res = ban_dong_loat(
            [
                (lambda: mt.kt.request("POST", f"/api/chuyen/{c_tu['id']}/tam-ung", {"so_tien": moi_lan, "hinh_thuc": "TIEN_MAT"}))
                for _ in range(8)
            ]
        )
        st2, tu_sau = mt.kt.request("GET", f"/api/chuyen/{c_tu['id']}/tam-ung")
        ok201 = sum(1 for s, _ in res if s == 201)
        kq.ghi(
            "SS-01_cap_tam_ung_8x_khong_vuot_dinh_muc",
            khong_500(res) and ok201 == 1 and tu_sau["tong_hieu_luc"] <= dm,
            f"codes={dem_ma(res)}, tong_hieu_luc={tu_sau['tong_hieu_luc']}/{dm}",
        )

        # SS-02: Thu hồi cùng 1 khoản tạm ứng 6x đồng thời -> đúng 1 lần 200, 5 lần 409
        tu_id = tu_sau["khoan"][0]["id"]
        res_th = ban_dong_loat(
            [(lambda tid=tu_id: mt.kt.request("POST", f"/api/tam-ung/{tid}/thu-hoi", {"ly_do": "PHA thu hồi"})) for _ in range(6)]
        )
        ok200 = sum(1 for s, _ in res_th if s == 200)
        kq.ghi(
            "SS-02_thu_hoi_tam_ung_6x",
            khong_500(res_th) and ok200 == 1 and sum(1 for s, _ in res_th if s == 409) == 5,
            f"codes={dem_ma(res_th)}",
        )

        # SS-03: Sửa tạm ứng 4x + Thu hồi 2x cùng lúc trên cùng khoản -> không 500, tổng <= định mức
        st, k_moi = mt.kt.request(
            "POST", f"/api/chuyen/{c_tu['id']}/tam-ung", {"so_tien": max(1000, dm // 4), "hinh_thuc": "TIEN_MAT"}
        )
        assert st == 201
        tid2 = k_moi["id"]
        ham_ss3 = [
            (lambda amt=max(2000, dm // 3) + i * 100: mt.kt.request("PATCH", f"/api/tam-ung/{tid2}", {"so_tien": amt, "ly_do": "PHA sửa"}))
            for i in range(4)
        ] + [
            (lambda: mt.kt.request("POST", f"/api/tam-ung/{tid2}/thu-hoi", {"ly_do": "PHA thu hồi xung đột"}))
            for _ in range(2)
        ]
        res_st = ban_dong_loat(ham_ss3)
        _, tu_sau3 = mt.kt.request("GET", f"/api/chuyen/{c_tu['id']}/tam-ung")
        kq.ghi(
            "SS-03_sua_va_thu_hoi_tam_ung_cung_luc",
            khong_500(res_st) and tu_sau3["tong_hieu_luc"] <= dm,
            f"codes={dem_ma(res_st)}, tong_hieu_luc={tu_sau3['tong_hieu_luc']}/{dm}",
        )
    else:
        kq.bo_qua("SS-01_cap_tam_ung_8x_khong_vuot_dinh_muc", f"Định mức tuyến quá nhỏ: {dm}")
        kq.bo_qua("SS-02_thu_hoi_tam_ung_6x", f"Định mức tuyến quá nhỏ: {dm}")
        kq.bo_qua("SS-03_sua_va_thu_hoi_tam_ung_cung_luc", f"Định mức tuyến quá nhỏ: {dm}")

    # =========================================================================
    # 2. CHỐT / MỞ CHỐT / HỦY CHUYẾN SONG SONG + XUNG ĐỘT MỞ CHỐT/HỦY + TẠM ỨNG + GHÉP ĐƠN
    # =========================================================================
    # SS-04: Chốt chuyến 6x song song -> đúng 1 lần 200, 5 lần 409
    c_chot = mt.lap_chuyen(xe1["id"], tx1["id"])
    res = ban_dong_loat(
        [(lambda: mt.dp.request("POST", f"/api/chuyen/{c_chot['id']}/chot", {"xac_nhan_chay_rong": True})) for _ in range(6)]
    )
    kq.ghi(
        "SS-04_chot_chuyen_6x",
        khong_500(res) and sum(1 for s, _ in res if s == 200) == 1 and sum(1 for s, _ in res if s == 409) == 5,
        f"codes={dem_ma(res)}",
    )

    # SS-05: Mở chốt chuyến 6x song song -> đúng 1 lần 200, 5 lần 409
    res = ban_dong_loat([(lambda: mt.dp.request("POST", f"/api/chuyen/{c_chot['id']}/mo-chot")) for _ in range(6)])
    kq.ghi(
        "SS-05_mo_chot_chuyen_6x",
        khong_500(res) and sum(1 for s, _ in res if s == 200) == 1 and sum(1 for s, _ in res if s == 409) == 5,
        f"codes={dem_ma(res)}",
    )

    # SS-06: Hủy chuyến 6x song song -> đúng 1 lần 200, 5 lần 409
    res = ban_dong_loat(
        [(lambda: mt.dp.request("POST", f"/api/chuyen/{c_chot['id']}/huy", {"ly_do": "PHA hủy 6x"})) for _ in range(6)]
    )
    kq.ghi(
        "SS-06_huy_chuyen_6x",
        khong_500(res) and sum(1 for s, _ in res if s == 200) == 1 and sum(1 for s, _ in res if s == 409) == 5,
        f"codes={dem_ma(res)}",
    )

    # SS-07 (XUNG ĐỘT): Mở chốt + Cấp tạm ứng đồng thời trên chuyến DA_CHOT (lặp 3 vòng để tăng xác suất đụng)
    vi_pham_br24 = False
    chi_tiet_07 = []
    for v in range(3):
        c_x = mt.lap_chuyen(xe1["id"], tx1["id"])
        mt.chot_chuyen(c_x["id"])
        r = ban_dong_loat(
            [
                lambda cid=c_x["id"]: mt.dp.request("POST", f"/api/chuyen/{cid}/mo-chot"),
                lambda cid=c_x["id"]: mt.kt.request("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 5000, "hinh_thuc": "TIEN_MAT"}),
                lambda cid=c_x["id"]: mt.dp.request("POST", f"/api/chuyen/{cid}/mo-chot"),
                lambda cid=c_x["id"]: mt.kt.request("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 5000, "hinh_thuc": "TIEN_MAT"}),
            ]
        )
        _, ct_x = mt.dp.request("GET", f"/api/chuyen/{c_x['id']}")
        _, tu_x = mt.kt.request("GET", f"/api/chuyen/{c_x['id']}/tam-ung")
        chi_tiet_07.append(f"v{v}:codes={dem_ma(r)},tt={ct_x['trang_thai']},tu={tu_x['tong_hieu_luc']}")
        if not khong_500(r) or (ct_x["trang_thai"] == "LAP" and tu_x["tong_hieu_luc"] > 0):
            vi_pham_br24 = True
    kq.ghi("SS-07_xung_dot_mo_chot_vs_cap_tam_ung", not vi_pham_br24, " | ".join(chi_tiet_07))

    # SS-08 (XUNG ĐỘT): Hủy chuyến + Cấp tạm ứng đồng thời trên chuyến DA_CHOT (BR-25)
    vi_pham_br25 = False
    chi_tiet_08 = []
    for v in range(3):
        c_x = mt.lap_chuyen(xe1["id"], tx1["id"])
        mt.chot_chuyen(c_x["id"])
        r = ban_dong_loat(
            [
                lambda cid=c_x["id"]: mt.dp.request("POST", f"/api/chuyen/{cid}/huy", {"ly_do": "PHA hủy xung đột"}),
                lambda cid=c_x["id"]: mt.kt.request("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 5000, "hinh_thuc": "TIEN_MAT"}),
            ]
        )
        _, ct_x = mt.dp.request("GET", f"/api/chuyen/{c_x['id']}")
        _, tu_x = mt.kt.request("GET", f"/api/chuyen/{c_x['id']}/tam-ung")
        chi_tiet_08.append(f"v{v}:codes={dem_ma(r)},tt={ct_x['trang_thai']},tu={tu_x['tong_hieu_luc']}")
        if not khong_500(r) or (ct_x["trang_thai"] == "HUY" and tu_x["tong_hieu_luc"] > 0):
            vi_pham_br25 = True
    kq.ghi("SS-08_xung_dot_huy_chuyen_vs_cap_tam_ung", not vi_pham_br25, " | ".join(chi_tiet_08))

    # SS-09 (XUNG ĐỘT): Hủy chuyến + Ghép đơn đồng thời trên chuyến LAP
    vi_pham_09 = False
    chi_tiet_09 = []
    for v in range(3):
        c_x = mt.lap_chuyen(xe1["id"], tx1["id"])
        d_x = mt.tao_don(f"Hủy vs Ghép {v}")
        r = ban_dong_loat(
            [
                lambda cid=c_x["id"]: mt.dp.request("POST", f"/api/chuyen/{cid}/huy", {"ly_do": "PHA hủy vs ghép"}),
                lambda cid=c_x["id"], did=d_x["id"]: mt.dp.request("POST", f"/api/chuyen/{cid}/ghep", {"don_ids": [did]}),
            ]
        )
        _, ct_x = mt.dp.request("GET", f"/api/chuyen/{c_x['id']}")
        _, don_x = mt.dp.request("GET", f"/api/don/{d_x['id']}")
        chi_tiet_09.append(f"v{v}:codes={dem_ma(r)},c={ct_x['trang_thai']},d={don_x['trang_thai']},soDon={len(ct_x['don'])}")
        # Chuyến HUY thì không được còn đơn DA_GHEP gắn vào!
        if not khong_500(r) or (ct_x["trang_thai"] == "HUY" and (don_x["trang_thai"] != "CHO_GHEP" or len(ct_x["don"]) > 0)):
            vi_pham_09 = True
    kq.ghi("SS-09_xung_dot_huy_chuyen_vs_ghep_don", not vi_pham_09, " | ".join(chi_tiet_09))

    # SS-10 (XUNG ĐỘT): Hai chuyến LAP cùng ghép 1 đơn CHO_GHEP đồng thời (BR-07)
    xe2 = mt.tao_xe(6000)
    tx2, tx2_cli = mt.tao_tai_xe()
    c_g1 = mt.lap_chuyen(xe1["id"], tx1["id"])
    c_g2 = mt.lap_chuyen(xe2["id"], tx2["id"])
    d_chung = mt.tao_don("Tranh ghép 2 chuyến")
    res_g = ban_dong_loat(
        [
            lambda: mt.dp.request("POST", f"/api/chuyen/{c_g1['id']}/ghep", {"don_ids": [d_chung["id"]]}),
            lambda: mt.dp.request("POST", f"/api/chuyen/{c_g2['id']}/ghep", {"don_ids": [d_chung["id"]]}),
        ]
    )
    ok_g = sum(1 for s, _ in res_g if s == 200)
    c409_g = sum(1 for s, _ in res_g if s == 409)
    kq.ghi("SS-10_hai_chuyen_cung_ghep_1_don", khong_500(res_g) and ok_g == 1 and c409_g == 1, f"codes={dem_ma(res_g)}")

    # SS-11 (XUNG ĐỘT): Chốt chuyến + Sửa đơn đang ghép đồng thời (kiểm deadlock & nhất quán BR-23/BR-33)
    c_cs = mt.lap_chuyen(xe1["id"], tx1["id"])
    d_cs = mt.tao_don("Chốt vs Sửa đơn", kg="10.00")
    st, _ = mt.dp.request("POST", f"/api/chuyen/{c_cs['id']}/ghep", {"don_ids": [d_cs["id"]]})
    assert st == 200
    res_cs = ban_dong_loat(
        [
            lambda: mt.dp.request("POST", f"/api/chuyen/{c_cs['id']}/chot", {"xac_nhan_lai_am": True}),
            lambda: mt.dp.request("PATCH", f"/api/don/{d_cs['id']}", {"kg": "20.00"}),
            lambda: mt.dp.request("PATCH", f"/api/don/{d_cs['id']}", {"kg": "25.00"}),
        ]
    )
    _, ct_cs = mt.dp.request("GET", f"/api/chuyen/{c_cs['id']}")
    kq.ghi(
        "SS-11_xung_dot_chot_chuyen_vs_sua_don",
        khong_500(res_cs) and ct_cs["trang_thai"] == "DA_CHOT",
        f"codes={dem_ma(res_cs)}, trang_thai_chuyen={ct_cs['trang_thai']}",
    )

    # =========================================================================
    # 3. VÒNG ĐỜI CHẠY HÔM NAY: Bắt đầu / Quét / Kết thúc / Sự cố / Chi phí / Quyết toán / Công nợ
    # =========================================================================
    now_vn = datetime.now(VN_TZ)
    if (now_vn + timedelta(minutes=10)).date() != now_vn.date():
        for ma in [
            "SS-12_bat_dau_chuyen_5x",
            "SS-13_quet_lay_6x_idempotent_va_xung_dot",
            "SS-14_quet_giao_6x_khong_trung_phai_thu",
            "SS-15_xung_dot_giao_vs_giao_that_bai",
            "SS-16_dong_su_co_5x",
            "SS-17_ket_thuc_chuyen_5x",
            "SS-18_duyet_chi_phi_6x_va_tu_choi",
            "SS-19_xung_dot_quyet_toan_vs_ghi_va_duyet_chi_phi",
            "SS-20_quyet_toan_6x",
            "SS-21_cong_no_da_thu_chong_cheo_nguoc_thu_tu",
            "SS-22_xung_dot_ket_thuc_su_co_vs_quet_giao",
            "SS-23_hai_chuyen_cung_xe_bat_dau_cung_luc",
        ]:
            kq.bo_qua(ma, "Gần nửa đêm VN, không lập được chuyến khởi hành hôm nay")
        return kq.tong_ket()

    xe3 = mt.tao_xe(7000)
    tx3, tx3_cli = mt.tao_tai_xe()
    c_run = mt.lap_chuyen(xe3["id"], tx3["id"], hom_nay=True, offset_phut=2)
    d_run1 = mt.tao_don("Đơn chạy 1 (giao)")
    d_run2 = mt.tao_don("Đơn chạy 2 (xung đột lấy)")
    d_run3 = mt.tao_don("Đơn chạy 3 (giao vs tb)")
    d_run4 = mt.tao_don("Đơn chạy 4 (công nợ 2)")
    d_run5 = mt.tao_don("Đơn chạy 5 (công nợ 3)")
    st, r = mt.dp.request(
        "POST", f"/api/chuyen/{c_run['id']}/ghep", {"don_ids": [d["id"] for d in (d_run1, d_run2, d_run3, d_run4, d_run5)]}
    )
    assert st == 200, f"Ghép đơn chạy lỗi: {st} {r}"
    mt.chot_chuyen(c_run["id"])

    # SS-12: Bắt đầu chuyến 5x song song -> đúng 1 lần 200, 4 lần 409
    res_bd = ban_dong_loat(
        [
            (
                lambda: tx3_cli.request(
                    "POST",
                    f"/api/toi/chuyen/{c_run['id']}/bat-dau",
                    multipart=({"km_bat_dau": "7100"}, [("anh_dong_ho", "km.png", PNG, "image/png")]),
                )
            )
            for _ in range(5)
        ]
    )
    kq.ghi(
        "SS-12_bat_dau_chuyen_5x",
        khong_500(res_bd) and sum(1 for s, _ in res_bd if s == 200) == 1 and sum(1 for s, _ in res_bd if s == 409) == 4,
        f"codes={dem_ma(res_bd)}",
    )

    # SS-13: Quét lấy 6x cùng đơn (BR-45: đúng 1 lap_lai=False, 5 lap_lai=True) + LAY vs KHONG_LAY
    res_ql = ban_dong_loat(
        [(lambda: tx3_cli.request("POST", "/api/toi/quet", multipart=({"ma_don": d_run1["ma_don"], "loai": "LAY"}, []))) for _ in range(6)]
    )
    so_moi = sum(1 for s, b in res_ql if s == 200 and isinstance(b, dict) and b.get("lap_lai") is False)
    so_lap = sum(1 for s, b in res_ql if s == 200 and isinstance(b, dict) and b.get("lap_lai") is True)

    res_lkl = ban_dong_loat(
        [
            lambda: tx3_cli.request("POST", "/api/toi/quet", multipart=({"ma_don": d_run2["ma_don"], "loai": "LAY"}, [])),
            lambda: tx3_cli.request(
                "POST",
                "/api/toi/quet",
                multipart=(
                    {"ma_don": d_run2["ma_don"], "loai": "KHONG_LAY", "ly_do_id": str(mt.ly_do_lay)},
                    [("anh", "kl.png", PNG, "image/png")],
                ),
            ),
        ]
    )
    kq.ghi(
        "SS-13_quet_lay_6x_idempotent_va_xung_dot",
        khong_500(res_ql)
        and khong_500(res_lkl)
        and so_moi == 1
        and so_lap == 5
        and sorted(s for s, _ in res_lkl) == [200, 409],
        f"lay6x=(moi={so_moi},lap={so_lap},codes={dem_ma(res_ql)}), lay_vs_khonglay={dem_ma(res_lkl)}",
    )

    # SS-14: Quét giao 6x cùng đơn d_run1 -> đúng 1 lap_lai=False, sinh ĐÚNG 1 khoản phải thu (BR-45, BR-56)
    res_qg = ban_dong_loat(
        [
            (
                lambda: tx3_cli.request(
                    "POST",
                    "/api/toi/quet",
                    multipart=(
                        {"ma_don": d_run1["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh PHA"},
                        [("anh", "p.png", PNG, "image/png"), ("chu_ky", "s.png", PNG, "image/png")],
                    ),
                )
            )
            for _ in range(6)
        ]
    )
    g_moi = sum(1 for s, b in res_qg if s == 200 and isinstance(b, dict) and b.get("lap_lai") is False)
    g_lap = sum(1 for s, b in res_qg if s == 200 and isinstance(b, dict) and b.get("lap_lai") is True)
    _, pt_ds = mt.kt.request("GET", f"/api/phai-thu?khach_hang_id={mt.kh['id']}&so_dong=100")
    pt_cua_d1 = [x for x in pt_ds["du_lieu"] if x["don_hang_id"] == d_run1["id"]]
    kq.ghi(
        "SS-14_quet_giao_6x_khong_trung_phai_thu",
        khong_500(res_qg) and g_moi == 1 and g_lap == 5 and len(pt_cua_d1) == 1,
        f"moi={g_moi}, lap={g_lap}, codes={dem_ma(res_qg)}, so_phai_thu={len(pt_cua_d1)}",
    )

    # SS-15: Quét GIAO vs GIAO_THAT_BAI cùng lúc trên d_run3 (lấy trước)
    st, _ = tx3_cli.request("POST", "/api/toi/quet", multipart=({"ma_don": d_run3["ma_don"], "loai": "LAY"}, []))
    assert st == 200
    res_gtb = ban_dong_loat(
        [
            lambda: tx3_cli.request(
                "POST",
                "/api/toi/quet",
                multipart=(
                    {"ma_don": d_run3["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh PHA 3"},
                    [("anh", "p.png", PNG, "image/png"), ("chu_ky", "s.png", PNG, "image/png")],
                ),
            ),
            lambda: tx3_cli.request(
                "POST",
                "/api/toi/quet",
                multipart=(
                    {"ma_don": d_run3["ma_don"], "loai": "GIAO_THAT_BAI", "ly_do_id": str(mt.ly_do_giao)},
                    [("anh", "tb.png", PNG, "image/png")],
                ),
            ),
        ]
    )
    kq.ghi(
        "SS-15_xung_dot_giao_vs_giao_that_bai",
        khong_500(res_gtb) and sorted(s for s, _ in res_gtb) == [200, 409],
        f"codes={dem_ma(res_gtb)}",
    )

    # Xử lý nốt d_run2 (nếu đã lấy -> giao), d_run4, d_run5 (lấy + giao để có 3 khoản phải thu cho SS-22)
    _, d2_tt = mt.dp.request("GET", f"/api/don/{d_run2['id']}")
    if d2_tt["trang_thai"] == "DA_LAY":
        tx3_cli.request(
            "POST",
            "/api/toi/quet",
            multipart=(
                {"ma_don": d_run2["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh PHA 2"},
                [("anh", "p.png", PNG, "image/png"), ("chu_ky", "s.png", PNG, "image/png")],
            ),
        )
    for d in (d_run4, d_run5):
        tx3_cli.request("POST", "/api/toi/quet", multipart=({"ma_don": d["ma_don"], "loai": "LAY"}, []))
        tx3_cli.request(
            "POST",
            "/api/toi/quet",
            multipart=(
                {"ma_don": d["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh PHA"},
                [("anh", "p.png", PNG, "image/png"), ("chu_ky", "s.png", PNG, "image/png")],
            ),
        )

    # SS-16: Báo sự cố rồi Đóng sự cố 5x song song -> đúng 1 lần 200, 4 lần 409
    st, sc = tx3_cli.request(
        "POST",
        f"/api/toi/chuyen/{c_run['id']}/su-co",
        multipart=({"loai": "KET_XE", "ghi_chu": f"{TAG} Kẹt xe thử"}, []),
    )
    assert st == 201, f"Báo sự cố lỗi: {st} {sc}"
    res_sc = ban_dong_loat(
        [(lambda: mt.dp.request("POST", f"/api/su-co/{sc['id']}/dong", {"cach_xu_ly": "Đã xử lý"})) for _ in range(5)]
    )
    kq.ghi(
        "SS-16_dong_su_co_5x",
        khong_500(res_sc) and sum(1 for s, _ in res_sc if s == 200) == 1 and sum(1 for s, _ in res_sc if s == 409) == 4,
        f"codes={dem_ma(res_sc)}",
    )

    # Ghi 2 khoản chi phí trước khi kết thúc để test duyệt/từ chối/quyết toán
    st, cp1 = tx3_cli.request(
        "POST",
        f"/api/toi/chuyen/{c_run['id']}/chi-phi",
        multipart=(
            {"loai": "CAU_DUONG", "so_tien": "100000", "ghi_chu": f"{TAG} CP1"},
            [("anh", "hd.png", PNG, "image/png")],
        ),
    )
    assert st == 201
    st, cp2 = tx3_cli.request(
        "POST",
        f"/api/toi/chuyen/{c_run['id']}/chi-phi",
        multipart=(
            {"loai": "BOC_XEP", "so_tien": "80000", "ghi_chu": f"{TAG} CP2"},
            [("anh", "hd.png", PNG, "image/png")],
        ),
    )
    assert st == 201

    # SS-17: Kết thúc chuyến 5x song song -> đúng 1 lần 200, 4 lần 409
    res_kt = ban_dong_loat(
        [
            (
                lambda: tx3_cli.request(
                    "POST",
                    f"/api/toi/chuyen/{c_run['id']}/ket-thuc",
                    multipart=({"km_ket_thuc": "7250"}, [("anh_dong_ho", "km2.png", PNG, "image/png")]),
                )
            )
            for _ in range(5)
        ]
    )
    kq.ghi(
        "SS-17_ket_thuc_chuyen_5x",
        khong_500(res_kt) and sum(1 for s, _ in res_kt if s == 200) == 1 and sum(1 for s, _ in res_kt if s == 409) == 4,
        f"codes={dem_ma(res_kt)}",
    )

    # SS-18: Duyệt chi phí 6x cùng số (1x 200, 5x 400 KHONG_CO_THAY_DOI) + Duyệt vs Từ chối trên cp2
    res_d1 = ban_dong_loat(
        [(lambda: mt.kt.request("POST", f"/api/chi-phi/{cp1['id']}/duyet", {"so_tien_duyet": 100000})) for _ in range(6)]
    )
    res_d2 = ban_dong_loat(
        [(lambda: mt.kt.request("POST", f"/api/chi-phi/{cp2['id']}/duyet", {"so_tien_duyet": 70000, "ly_do": "Giảm"})) for _ in range(3)]
        + [(lambda: mt.kt.request("POST", f"/api/chi-phi/{cp2['id']}/tu-choi", {"ly_do": "Từ chối"})) for _ in range(3)]
    )
    _, bang_qt = mt.kt.request("GET", f"/api/chuyen/{c_run['id']}/quyet-toan")
    cp2_sau = next(k for k in bang_qt["khoan"] if k["id"] == cp2["id"])
    nhat_quan_cp2 = (cp2_sau["trang_thai"] == "DA_DUYET" and cp2_sau["so_tien_duyet"] == 70000) or (
        cp2_sau["trang_thai"] == "TU_CHOI" and cp2_sau["so_tien_duyet"] is None
    )
    kq.ghi(
        "SS-18_duyet_chi_phi_6x_va_tu_choi",
        khong_500(res_d1)
        and khong_500(res_d2)
        and sum(1 for s, _ in res_d1 if s == 200) == 1
        and nhat_quan_cp2,
        f"duyet6x={dem_ma(res_d1)}, duyet_vs_tuchoi={dem_ma(res_d2)}, cp2_cuoi={cp2_sau['trang_thai']}/{cp2_sau['so_tien_duyet']}",
    )

    # SS-19 (XUNG ĐỘT): Quyết toán + Tài xế ghi chi phí mới đồng thời trên chuyến HOAN_THANH (BR-29, BR-55)
    # Kiểm bất biến: nếu chuyến đã lên DA_QUYET_TOAN, KHÔNG ĐƯỢC còn khoản chi CHO_DUYET nào!
    luc_xl = (datetime.now(VN_TZ) - timedelta(minutes=1)).isoformat(timespec="seconds")
    xu_ly = bang_qt["xu_ly_goi_y"]
    body_qt: dict[str, Any] = {"xu_ly_chenh_lech": xu_ly}
    if bang_qt["chenh_lech_tam_ung"] != 0:
        body_qt["hinh_thuc"] = "TIEN_MAT"
        body_qt["luc_xu_ly"] = luc_xl

    res_qt_cp = ban_dong_loat(
        [
            lambda: mt.kt.request("POST", f"/api/chuyen/{c_run['id']}/quyet-toan", body_qt),
            lambda: tx3_cli.request(
                "POST",
                f"/api/toi/chuyen/{c_run['id']}/chi-phi",
                multipart=(
                    {"loai": "PHAT_SINH", "so_tien": "30000", "ghi_chu": f"{TAG} CP chen QT"},
                    [("anh", "hd.png", PNG, "image/png")],
                ),
            ),
            lambda: mt.kt.request("POST", f"/api/chi-phi/{cp1['id']}/duyet", {"so_tien_duyet": 90000, "ly_do": "Sửa lúc QT"}),
        ]
    )
    _, bang_sau = mt.kt.request("GET", f"/api/chuyen/{c_run['id']}/quyet-toan")
    tong_duyet_thuc = sum(k["so_tien_duyet"] or 0 for k in bang_sau["khoan"] if k["trang_thai"] == "DA_DUYET")
    bat_bien_qt = (
        khong_500(res_qt_cp)
        and not (bang_sau["trang_thai"] == "DA_QUYET_TOAN" and bang_sau["so_cho_duyet"] > 0)
        and bang_sau["tong_chi"] == tong_duyet_thuc
    )
    kq.ghi(
        "SS-19_xung_dot_quyet_toan_vs_ghi_va_duyet_chi_phi",
        bat_bien_qt,
        f"codes={dem_ma(res_qt_cp)}, tt={bang_sau['trang_thai']}, cho_duyet={bang_sau['so_cho_duyet']}, tong_chi={bang_sau['tong_chi']} vs thuc={tong_duyet_thuc}",
    )

    # SS-20: Quyết toán 6x song song trên chuyến HOAN_THANH mới (kết thúc rỗng -> HOAN_THANH nhanh)
    xe4 = mt.tao_xe(8000)
    tx4, tx4_cli = mt.tao_tai_xe()
    c_qt6 = mt.lap_chuyen(xe4["id"], tx4["id"], hom_nay=True, offset_phut=2)
    mt.chot_chuyen(c_qt6["id"])
    mt.bat_dau_chuyen(tx4_cli, c_qt6["id"], 8050)
    st, _ = tx4_cli.request(
        "POST",
        f"/api/toi/chuyen/{c_qt6['id']}/ket-thuc",
        multipart=({"km_ket_thuc": "8100"}, [("anh_dong_ho", "km.png", PNG, "image/png")]),
    )
    assert st == 200
    res_qt6 = ban_dong_loat(
        [(lambda: mt.kt.request("POST", f"/api/chuyen/{c_qt6['id']}/quyet-toan", {"xu_ly_chenh_lech": "KHONG_CHENH"})) for _ in range(6)]
    )
    kq.ghi(
        "SS-20_quyet_toan_6x",
        khong_500(res_qt6) and sum(1 for s, _ in res_qt6 if s == 200) == 1 and sum(1 for s, _ in res_qt6 if s == 409) == 5,
        f"codes={dem_ma(res_qt6)}",
    )

    # SS-21: Ghi thu công nợ 6x cùng danh sách + chồng chéo [pt1, pt2] vs [pt2, pt3] (BR-56)
    _, pt_res = mt.kt.request("GET", f"/api/phai-thu?khach_hang_id={mt.kh['id']}&trang_thai_tt=CHUA_THU&so_dong=20")
    pt_ids = [x["id"] for x in pt_res["du_lieu"]]
    hom_nay_str = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    if len(pt_ids) >= 3:
        # Chồng chéo [pt0, pt1] vs [pt1, pt2] + ngược thứ tự [pt2, pt1] để test deadlock!
        res_cn_cc = ban_dong_loat(
            [
                lambda: mt.kt.request("POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [pt_ids[0], pt_ids[1]], "ngay": hom_nay_str}),
                lambda: mt.kt.request("POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [pt_ids[2], pt_ids[1]], "ngay": hom_nay_str}),
                lambda: mt.kt.request("POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [pt_ids[1], pt_ids[0]], "ngay": hom_nay_str}),
                lambda: mt.kt.request("POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [pt_ids[1]], "ngay": hom_nay_str}),
            ]
        )
        ok_cn = sum(1 for s, _ in res_cn_cc if s == 200)
        c409_cn = sum(1 for s, _ in res_cn_cc if s == 409)
        kq.ghi(
            "SS-21_cong_no_da_thu_chong_cheo_nguoc_thu_tu",
            khong_500(res_cn_cc) and ok_cn == 1 and c409_cn == 3,
            f"codes={dem_ma(res_cn_cc)} (pt_ids={pt_ids[:3]})",
        )
    else:
        kq.bo_qua("SS-21_cong_no_da_thu_chong_cheo_nguoc_thu_tu", f"Chỉ có {len(pt_ids)} khoản phải thu chưa thu")

    # SS-22 (XUNG ĐỘT): Kết thúc do sự cố (Điều phối) + Quét GIAO (Tài xế) đồng thời (BR-68, BR-56)
    xe5 = mt.tao_xe(9000)
    tx5, tx5_cli = mt.tao_tai_xe()
    c_sc = mt.lap_chuyen(xe5["id"], tx5["id"], hom_nay=True, offset_phut=2)
    d_sc = mt.tao_don("Sự cố vs Giao")
    st, _ = mt.dp.request("POST", f"/api/chuyen/{c_sc['id']}/ghep", {"don_ids": [d_sc["id"]]})
    assert st == 200
    mt.chot_chuyen(c_sc["id"])
    mt.bat_dau_chuyen(tx5_cli, c_sc["id"], 9050)
    st, _ = tx5_cli.request("POST", "/api/toi/quet", multipart=({"ma_don": d_sc["ma_don"], "loai": "LAY"}, []))
    assert st == 200

    res_sc_g = ban_dong_loat(
        [
            lambda: mt.dp.request(
                "POST", f"/api/chuyen/{c_sc['id']}/ket-thuc-su-co", {"ly_do": "PHA sự cố xung đột", "km_ket_thuc": 9100}
            ),
            lambda: tx5_cli.request(
                "POST",
                "/api/toi/quet",
                multipart=(
                    {"ma_don": d_sc["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh PHA SC"},
                    [("anh", "p.png", PNG, "image/png"), ("chu_ky", "s.png", PNG, "image/png")],
                ),
            ),
        ]
    )
    _, d_sc_sau = mt.dp.request("GET", f"/api/don/{d_sc['id']}")
    _, pt_sc = mt.kt.request("GET", f"/api/phai-thu?khach_hang_id={mt.kh['id']}&so_dong=100")
    pt_d_sc = [x for x in pt_sc["du_lieu"] if x["don_hang_id"] == d_sc["id"]]
    # Nếu đơn là THAT_BAI -> không được có PhaiThu; nếu là DA_GIAO -> đúng 1 PhaiThu
    nhat_quan_sc = (d_sc_sau["trang_thai"] == "THAT_BAI" and len(pt_d_sc) == 0) or (
        d_sc_sau["trang_thai"] == "DA_GIAO" and len(pt_d_sc) == 1
    )
    kq.ghi(
        "SS-22_xung_dot_ket_thuc_su_co_vs_quet_giao",
        khong_500(res_sc_g) and nhat_quan_sc,
        f"codes={dem_ma(res_sc_g)}, don={d_sc_sau['trang_thai']}, so_phai_thu={len(pt_d_sc)}",
    )

    # SS-23 (XUNG ĐỘT): Hai chuyến khác nhau của CÙNG 1 XE trong cùng ngày cùng bấm Bắt đầu (BR-26)
    xe6 = mt.tao_xe(9500)
    tx6a, tx6a_cli = mt.tao_tai_xe()
    tx6b, tx6b_cli = mt.tao_tai_xe()
    # Kiểm tra xem tuyến có đủ ngắn để lập 2 chuyến không chồng lịch trong cùng hôm nay không
    tong_phut = mt.tuyen.get("tong_phut", 600)
    kh1 = datetime.now(VN_TZ) + timedelta(minutes=2)
    kh2 = kh1 + timedelta(minutes=tong_phut + 90)
    if kh1.date() == kh2.date():
        st1, c6a = mt.dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": mt.tuyen["id"], "khoi_hanh_du_kien": kh1.isoformat(timespec="seconds"), "xe_id": xe6["id"], "tai_xe_id": tx6a["id"]},
        )
        st2, c6b = mt.dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": mt.tuyen["id"], "khoi_hanh_du_kien": kh2.isoformat(timespec="seconds"), "xe_id": xe6["id"], "tai_xe_id": tx6b["id"]},
        )
        if st1 == 201 and st2 == 201:
            mt.chot_chuyen(c6a["id"])
            mt.chot_chuyen(c6b["id"])
            res_2xe = ban_dong_loat(
                [
                    lambda: tx6a_cli.request(
                        "POST",
                        f"/api/toi/chuyen/{c6a['id']}/bat-dau",
                        multipart=({"km_bat_dau": "9510"}, [("anh_dong_ho", "k1.png", PNG, "image/png")]),
                    ),
                    lambda: tx6b_cli.request(
                        "POST",
                        f"/api/toi/chuyen/{c6b['id']}/bat-dau",
                        multipart=({"km_bat_dau": "9520"}, [("anh_dong_ho", "k2.png", PNG, "image/png")]),
                    ),
                ]
            )
            kq.ghi(
                "SS-23_hai_chuyen_cung_xe_bat_dau_cung_luc",
                khong_500(res_2xe) and sorted(s for s, _ in res_2xe) == [200, 409],
                f"codes={dem_ma(res_2xe)}",
            )
        else:
            kq.bo_qua("SS-23_hai_chuyen_cung_xe_bat_dau_cung_luc", f"Không lập được 2 chuyến cùng ngày: {st1}/{st2}")
    else:
        kq.bo_qua(
            "SS-23_hai_chuyen_cung_xe_bat_dau_cung_luc",
            f"Thời gian còn lại trong ngày không đủ xếp 2 chuyến cùng xe không chồng lịch (tong_phut={tong_phut})",
        )

    return kq.tong_ket()


if __name__ == "__main__":
    sys.exit(main())
