#!/usr/bin/env python3
"""
04_phan_quyen_cheo_api_moi.py - Kiểm thử phân quyền chéo, IDOR, tham số lạ trên các API thêm sau:
1. Tìm chung: GET /api/tim?q=
2. Thông báo: GET /api/thong-bao
3. Tổng quan hôm nay: GET /api/tong-quan
4. Dự đoán trễ: GET /api/chuyen/{id}/du-doan-tre, GET /api/du-doan-tre?ngay=
5. Hồ sơ và ảnh đại diện: GET/PATCH/PUT /api/auth/ho-so, GET/PUT/DELETE /api/auth/anh-dai-dien
6. Đổi mật khẩu & phân quyền chéo quản trị mật khẩu + hiệu lực khóa tài khoản tức thì:
   PUT /api/auth/mat-khau, PUT /api/nguoi-dung/{id}/mat-khau, GET /api/tep/{id}/link

QUY TẮC AN TOÀN:
- KHÔNG đổi mật khẩu, KHÔNG khóa, KHÔNG sửa ảnh đại diện của các tài khoản gốc (quanly, dieuphoi, ketoan, taixe01..05).
- KHÔNG đăng nhập sai quá 4 lần trên tài khoản gốc. Mọi ca đổi mật khẩu / khóa / khóa tạm / đổi ảnh chỉ chạy trên tài khoản PHA- mới tạo.

Chạy độc lập: py -3.12 -I -X utf8 kiem-thu-kham-pha/04_phan_quyen_cheo_api_moi.py
"""

from __future__ import annotations

import json
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

BACKEND = "http://127.0.0.1:8000"
VN_TZ = timezone(timedelta(hours=7))
TAG = f"PHA-PQ-{int(time.time()) % 100000}-{random.randint(100, 999)}"

LOAI_TB_DP = {"GIAY_TO", "CHUYEN_TRE", "SU_CO_MO", "DON_SAP_QUA_HAN", "THIEU_GPS", "DON_THAT_BAI"}
LOAI_TB_KT = {"CHO_QUYET_TOAN", "CHI_PHI_CHO_DUYET", "TAM_UNG_TREO"}
LOAI_TB_TX = {"CHUYEN_DUOC_GIAO", "SU_CO_DA_DONG", "CHI_PHI_DA_XU_LY"}


def tao_png_1x1(mau: bytes = b"\x00\x11\x22\x33") -> bytes:
    def chunk(loai: bytes, du_lieu: bytes) -> bytes:
        crc = zlib.crc32(loai + du_lieu) & 0xFFFFFFFF
        return struct.pack(">I", len(du_lieu)) + loai + du_lieu + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(mau))
        + chunk(b"IEND", b"")
    )


PNG_A = tao_png_1x1(b"\x00\xff\x00\x00")
PNG_B = tao_png_1x1(b"\x00\x00\xff\x00")


class ApiClient:
    def __init__(self, base: str = BACKEND, token: str | None = None):
        self.base = base.rstrip("/")
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        multipart: tuple[dict[str, Any], list[tuple[str, str, bytes, str]]] | None = None,
        raw_bytes: bool = False,
        timeout: float = 20.0,
    ) -> tuple[int, Any, dict[str, str]]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Cookie"] = f"access_token={self.token}"
        data: bytes | None = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif multipart is not None:
            fields, files = multipart
            boundary = f"----PhaPQ{random.randint(100000, 999999)}"
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
                hdrs = {k.lower(): v for k, v in r.headers.items()}
                for sc in r.headers.get_all("Set-Cookie") or []:
                    m = re.search(r"access_token=([^;]+)", sc)
                    if m:
                        self.token = m.group(1)
                if raw_bytes:
                    return r.status, raw, hdrs
                return r.status, (json.loads(raw.decode("utf-8")) if raw else None), hdrs
        except urllib.error.HTTPError as e:
            raw = e.read()
            hdrs = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
            if raw_bytes:
                return e.code, raw, hdrs
            try:
                body = json.loads(raw.decode("utf-8")) if raw else None
            except Exception:
                body = raw.decode("utf-8", errors="replace")
            return e.code, body, hdrs

    def dang_nhap(self, ten: str, mk: str = "demo12345") -> dict[str, Any]:
        st, body, _ = self.request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": ten, "mat_khau": mk})
        if st != 200:
            raise RuntimeError(f"Đăng nhập {ten} lỗi {st}: {body}")
        return body


class KetQua:
    def __init__(self) -> None:
        self.ds: list[tuple[str, str, str]] = []

    def ghi(self, ma: str, dat: bool, ly_do: str) -> None:
        tt = "ĐẠT" if dat else "LỖI"
        self.ds.append((ma, tt, ly_do))
        print(f"[{tt}] {ma}: {ly_do}", flush=True)

    def tong_ket(self) -> int:
        dat = sum(1 for _, t, _ in self.ds if t == "ĐẠT")
        loi = sum(1 for _, t, _ in self.ds if t == "LỖI")
        print(f"\n=== TỔNG KẾT 04_phan_quyen_cheo_api_moi: tổng={len(self.ds)} | đạt={dat} | lỗi={loi} ===")
        return 1 if loi else 0


def main() -> int:
    kq = KetQua()
    print(f"=== Bắt đầu 04_phan_quyen_cheo_api_moi.py (TAG={TAG}) ===", flush=True)

    try:
        anon = ApiClient()
        ql = ApiClient()
        ql.dang_nhap("quanly")
        dp = ApiClient()
        dp.dang_nhap("dieuphoi")
        kt = ApiClient()
        kt.dang_nhap("ketoan")
        tx01 = ApiClient()
        tx01.dang_nhap("taixe01")

        # Tạo tài nguyên PHA- tách biệt: 1 khách, 2 xe, 2 tài xế (tx_a, tx_b), 2 tài khoản người dùng (dp_pha, dp_lock)
        now_vn = datetime.now(VN_TZ)
        nam_sau = (now_vn + timedelta(days=365)).strftime("%Y-%m-%d")
        hom_nay = now_vn.strftime("%Y-%m-%d")
        ngay_mai_iso = (now_vn + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
        mk_pha = "PhaPass123!"

        st, tuyen_res, _ = dp.request("GET", "/api/tuyen?trang_thai=HOAT_DONG&so_dong=20")
        assert st == 200 and tuyen_res["du_lieu"]
        tuyen_id = tuyen_res["du_lieu"][0]["id"]

        st, kh_pha, _ = dp.request(
            "POST",
            "/api/khach-hang",
            {"ten": f"{TAG} KhachBimat", "sdt": f"094{random.randint(1000000, 9999999)}"},
        )
        assert st == 201

        bs_a = f"51Q-{random.randint(10000, 99999)}"
        bs_b = f"51R-{random.randint(10000, 99999)}"
        xe_a = dp.request(
            "POST",
            "/api/xe",
            {
                "bien_so": bs_a,
                "tai_trong_kg": 5000,
                "the_tich_m3": "20.00",
                "ktt_toan_bo_kg": 8000,
                "han_dang_kiem": nam_sau,
                "han_bao_hiem": nam_sau,
                "km_dong_ho": 1000,
            },
        )[1]
        xe_b = dp.request(
            "POST",
            "/api/xe",
            {
                "bien_so": bs_b,
                "tai_trong_kg": 5000,
                "the_tich_m3": "20.00",
                "ktt_toan_bo_kg": 8000,
                "han_dang_kiem": nam_sau,
                "han_bao_hiem": nam_sau,
                "km_dong_ho": 1000,
            },
        )[1]

        u_txa = f"PHA-txa-{random.randint(10000, 99999)}"
        u_txb = f"PHA-txb-{random.randint(10000, 99999)}"
        tx_a = dp.request(
            "POST",
            "/api/tai-xe",
            {
                "ten_dang_nhap": u_txa,
                "mat_khau": mk_pha,
                "ho_ten": f"{TAG} TaiXeAlpha",
                "so_gplx": f"PQA{random.randint(1000000, 9999999)}",
                "hang_gplx": "C",
                "han_gplx": nam_sau,
                "sdt": f"095{random.randint(1000000, 9999999)}",
            },
        )[1]
        tx_b = dp.request(
            "POST",
            "/api/tai-xe",
            {
                "ten_dang_nhap": u_txb,
                "mat_khau": mk_pha,
                "ho_ten": f"{TAG} TaiXeBeta",
                "so_gplx": f"PQB{random.randint(1000000, 9999999)}",
                "hang_gplx": "C",
                "han_gplx": nam_sau,
                "sdt": f"096{random.randint(1000000, 9999999)}",
            },
        )[1]
        cli_txa = ApiClient()
        cli_txa.dang_nhap(u_txa, mk_pha)
        cli_txb = ApiClient()
        cli_txb.dang_nhap(u_txb, mk_pha)

        # Chuyến của tx_a: 1 chuyến LAP (tài xế không được thấy), 1 chuyến HUY (không thấy), 1 chuyến DA_CHOT (thấy)
        c_a_lap = dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": tuyen_id, "khoi_hanh_du_kien": ngay_mai_iso, "xe_id": xe_a["id"], "tai_xe_id": tx_a["id"]},
        )[1]
        kh_ngay2 = (now_vn + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
        c_a_huy = dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": tuyen_id, "khoi_hanh_du_kien": kh_ngay2, "xe_id": xe_a["id"], "tai_xe_id": tx_a["id"]},
        )[1]
        dp.request("POST", f"/api/chuyen/{c_a_huy['id']}/huy", {"ly_do": "PHA hủy kiểm quyền"})

        # Chuyến của tx_b ở trạng thái DA_CHOT ngày mai -> sinh thông báo CHUYEN_DUOC_GIAO cho tx_b, KHÔNG ĐƯỢC lộ cho tx_a!
        c_b_chot = dp.request(
            "POST",
            "/api/chuyen",
            {"tuyen_id": tuyen_id, "khoi_hanh_du_kien": ngay_mai_iso, "xe_id": xe_b["id"], "tai_xe_id": tx_b["id"]},
        )[1]
        dp.request("POST", f"/api/chuyen/{c_b_chot['id']}/chot", {"xac_nhan_chay_rong": True})

        # Tài khoản người dùng PHA- dùng cho đổi MK, ảnh đại diện, khóa phiên
        u_dp1 = f"PHA-u1-{random.randint(10000, 99999)}"
        u_lock = f"PHA-lk-{random.randint(10000, 99999)}"
        nd_u1 = ql.request(
            "POST",
            "/api/nguoi-dung",
            {"ten_dang_nhap": u_dp1, "ho_ten": f"{TAG} UserTest1", "vai_tro": "DIEU_PHOI", "mat_khau": mk_pha},
        )[1]
        ql.request(
            "POST",
            "/api/nguoi-dung",
            {"ten_dang_nhap": u_lock, "ho_ten": f"{TAG} UserLockTest", "vai_tro": "KE_TOAN", "mat_khau": mk_pha},
        )
        cli_u1 = ApiClient()
        cli_u1.dang_nhap(u_dp1, mk_pha)
        cli_lock = ApiClient()
        cli_lock.dang_nhap(u_lock, mk_pha)
    except Exception as e:
        print(f"[LỖI] Chuẩn bị dữ liệu thất bại: {e}")
        traceback.print_exc()
        return 1

    # =========================================================================
    # NHÓM 1: TÌM CHUNG (GET /api/tim?q=)
    # =========================================================================
    st, _, _ = anon.request("GET", "/api/tim?q=CH")
    kq.ghi("PQ-01_tim_an_danh_401", st == 401, f"status={st}")

    # Kế toán tìm đúng biển số xe & tên tài xế PHA- -> xe và tai_xe PHẢI rỗng!
    st_xe, b_xe, _ = kt.request("GET", f"/api/tim?q={urllib.parse.quote(bs_a)}")
    st_tx, b_tx, _ = kt.request("GET", f"/api/tim?q={urllib.parse.quote('TaiXeAlpha')}")
    kq.ghi(
        "PQ-02_tim_ketoan_khong_lo_xe_va_taixe",
        st_xe == 200
        and st_tx == 200
        and b_xe["xe"] == {"tong": 0, "ds": []}
        and b_tx["tai_xe"] == {"tong": 0, "ds": []},
        f"kt_xe={b_xe['xe']}, kt_taixe={b_tx['tai_xe']}",
    )

    # Tài xế A tìm đúng mã chuyến của B, tìm đúng chuyến LAP & HUY của chính A, tìm tên khách/biển số -> không được lộ!
    st1, r_b, _ = cli_txa.request("GET", f"/api/tim?q={urllib.parse.quote(c_b_chot['ma_chuyen'])}")
    st2, r_lap, _ = cli_txa.request("GET", f"/api/tim?q={urllib.parse.quote(c_a_lap['ma_chuyen'])}")
    st3, r_huy, _ = cli_txa.request("GET", f"/api/tim?q={urllib.parse.quote(c_a_huy['ma_chuyen'])}")
    st4, r_kh, _ = cli_txa.request("GET", f"/api/tim?q={urllib.parse.quote('KhachBimat')}")
    kq.ghi(
        "PQ-03_tim_taixe_khong_lo_chuyen_nguoi_khac_LAP_HUY_khach",
        st1 == 200
        and r_b["chuyen"]["tong"] == 0
        and r_lap["chuyen"]["tong"] == 0
        and r_huy["chuyen"]["tong"] == 0
        and r_kh["khach_hang"] == {"tong": 0, "ds": []}
        and r_kh["don"] == {"tong": 0, "ds": []}
        and r_kh["xe"] == {"tong": 0, "ds": []}
        and r_kh["tai_xe"] == {"tong": 0, "ds": []},
        f"chuyen_B={r_b['chuyen']['tong']}, LAP={r_lap['chuyen']['tong']}, HUY={r_huy['chuyen']['tong']}, kh={r_kh['khach_hang']}",
    )

    # Tài xế B tìm đúng mã chuyến DA_CHOT của chính mình -> phải thấy
    st_ok, r_ok, _ = cli_txb.request("GET", f"/api/tim?q={urllib.parse.quote(c_b_chot['ma_chuyen'])}")
    kq.ghi(
        "PQ-04_tim_taixe_thay_chuyen_DA_CHOT_cua_minh",
        st_ok == 200 and r_ok["chuyen"]["tong"] == 1 and r_ok["chuyen"]["ds"][0]["id"] == c_b_chot["id"],
        f"status={st_ok}, chuyen={r_ok['chuyen']}",
    )

    # Tham số lạ, q ngắn, wildcard %/_
    st_la, _, _ = dp.request("GET", "/api/tim?q=CH&vai_tro=QUAN_LY")
    st_ngan, _, _ = dp.request("GET", "/api/tim?q=%20a%20")
    st_wc, b_wc, _ = dp.request("GET", "/api/tim?q=%25%25")
    kq.ghi(
        "PQ-05_tim_tham_so_la_q_ngan_wildcard",
        st_la == 400 and st_ngan == 400 and st_wc == 200 and b_wc["chuyen"]["tong"] == 0,
        f"tham_so_la={st_la}, q_ngan={st_ngan}, wildcard_tong_chuyen={b_wc['chuyen']['tong'] if isinstance(b_wc, dict) else b_wc}",
    )

    # =========================================================================
    # NHÓM 2: THÔNG BÁO (GET /api/thong-bao)
    # =========================================================================
    st_an, _, _ = anon.request("GET", "/api/thong-bao")
    st_la, _, _ = tx01.request("GET", "/api/thong-bao?vai_tro=QUAN_LY")
    kq.ghi("PQ-06_thong_bao_an_danh_va_tham_so_la", st_an == 401 and st_la == 400, f"anon={st_an}, tham_so_la={st_la}")

    _, tb_ql, _ = ql.request("GET", "/api/thong-bao")
    _, tb_dp, _ = dp.request("GET", "/api/thong-bao")
    _, tb_kt, _ = kt.request("GET", "/api/thong-bao")
    _, tb_txa, _ = cli_txa.request("GET", "/api/thong-bao")
    _, tb_txb, _ = cli_txb.request("GET", "/api/thong-bao")

    loai_ql = {x["loai"] for x in tb_ql["thong_bao"]}
    loai_dp = {x["loai"] for x in tb_dp["thong_bao"]}
    loai_kt = {x["loai"] for x in tb_kt["thong_bao"]}
    loai_txa = {x["loai"] for x in tb_txa["thong_bao"]}
    loai_txb = {x["loai"] for x in tb_txb["thong_bao"]}
    ids_txa = {x["doi_tuong"]["id"] for x in tb_txa["thong_bao"]}
    ids_txb = {x["doi_tuong"]["id"] for x in tb_txb["thong_bao"]}

    kq.ghi(
        "PQ-07_thong_bao_tach_vai_tro_va_chong_IDOR_taixe",
        loai_ql.issubset(LOAI_TB_DP)
        and loai_dp.issubset(LOAI_TB_DP)
        and loai_kt.issubset(LOAI_TB_KT)
        and loai_txa.issubset(LOAI_TB_TX)
        and loai_txb.issubset(LOAI_TB_TX)
        and (c_b_chot["id"] in ids_txb)
        and (c_b_chot["id"] not in ids_txa),
        f"ql={loai_ql}, kt={loai_kt}, txa_ids={ids_txa}, txb_has_cb={c_b_chot['id'] in ids_txb}",
    )

    # =========================================================================
    # NHÓM 3: TỔNG QUAN HÔM NAY (GET /api/tong-quan)
    # =========================================================================
    st_an, _, _ = anon.request("GET", "/api/tong-quan")
    st_ql, _, _ = ql.request("GET", f"/api/tong-quan?ngay={hom_nay}")
    st_dp, _, _ = dp.request("GET", "/api/tong-quan")
    st_kt, _, _ = kt.request("GET", "/api/tong-quan")
    st_tx1, _, _ = tx01.request("GET", "/api/tong-quan")
    st_txa, _, _ = cli_txa.request("GET", f"/api/tong-quan?ngay={hom_nay}")
    st_la, _, _ = dp.request("GET", f"/api/tong-quan?ngay={hom_nay}&vai_tro=QUAN_LY")
    st_bad, _, _ = dp.request("GET", "/api/tong-quan?ngay=2026-99-99")
    kq.ghi(
        "PQ-08_tong_quan_phan_quyen_va_tham_so",
        st_an == 401
        and st_ql == 200
        and st_dp == 200
        and st_kt == 200
        and st_tx1 == 403
        and st_txa == 403
        and st_la == 400
        and st_bad == 400,
        f"anon={st_an}, ql={st_ql}, dp={st_dp}, kt={st_kt}, tx01={st_tx1}, txa={st_txa}, la={st_la}, bad={st_bad}",
    )

    # =========================================================================
    # NHÓM 4: DỰ ĐOÁN TRỄ (GET /api/chuyen/{id}/du-doan-tre & /api/du-doan-tre)
    # =========================================================================
    cid_test = c_b_chot["id"]
    st_an1, _, _ = anon.request("GET", f"/api/chuyen/{cid_test}/du-doan-tre")
    st_an2, _, _ = anon.request("GET", f"/api/du-doan-tre?ngay={hom_nay}")
    st_ql1, _, _ = ql.request("GET", f"/api/chuyen/{cid_test}/du-doan-tre")
    st_dp2, _, _ = dp.request("GET", f"/api/du-doan-tre?ngay={hom_nay}")
    st_kt1, _, _ = kt.request("GET", f"/api/chuyen/{cid_test}/du-doan-tre")
    st_kt2, _, _ = kt.request("GET", f"/api/du-doan-tre?ngay={hom_nay}")
    st_tx1, _, _ = cli_txb.request("GET", f"/api/chuyen/{cid_test}/du-doan-tre")  # chuyến của chính tx_b -> vẫn 403!
    st_tx2, _, _ = cli_txb.request("GET", f"/api/du-doan-tre?ngay={hom_nay}")
    st_huy, b_huy, _ = dp.request("GET", f"/api/chuyen/{c_a_huy['id']}/du-doan-tre")
    kq.ghi(
        "PQ-09_du_doan_tre_phan_quyen_cheo",
        st_an1 == 401
        and st_an2 == 401
        and st_ql1 == 200
        and st_dp2 == 200
        and st_kt1 == 403
        and st_kt2 == 403
        and st_tx1 == 403
        and st_tx2 == 403
        and st_huy == 200
        and b_huy.get("co_du_doan") is False,
        f"anon=({st_an1},{st_an2}), ql={st_ql1}, dp={st_dp2}, kt=({st_kt1},{st_kt2}), tx=({st_tx1},{st_tx2}), huy={b_huy}",
    )

    # Kiểm tra tham số thừa trên /api/du-doan-tre (so với chuẩn kiểm tham số lạ ở tong-quan / tim / thong-bao)
    st_thieu, _, _ = dp.request("GET", "/api/du-doan-tre")
    st_la_dd, _, _ = dp.request("GET", f"/api/du-doan-tre?ngay={hom_nay}&tham_so_la=1")
    kq.ghi(
        "PQ-10_du_doan_tre_thieu_ngay_va_tham_so_la",
        st_thieu == 400 and st_la_dd == 400,
        f"thieu_ngay={st_thieu} (mong 400), tham_so_la={st_la_dd} (ghi nhận: nếu 200 tức router goi_y bỏ qua tham số lạ)",
    )

    # =========================================================================
    # NHÓM 5: HỒ SƠ VÀ ẢNH ĐẠI DIỆN (/api/auth/ho-so, /api/auth/anh-dai-dien)
    # =========================================================================
    st_hs_an, _, _ = anon.request("GET", "/api/auth/ho-so")
    st_av_an, _, _ = anon.request("GET", "/api/auth/anh-dai-dien")
    st_av_put_an, _, _ = anon.request(
        "PUT", "/api/auth/anh-dai-dien", multipart=({}, [("anh", "a.png", PNG_A, "image/png")])
    )
    st_av_del_an, _, _ = anon.request("DELETE", "/api/auth/anh-dai-dien")
    kq.ghi(
        "PQ-11_ho_so_va_anh_an_danh_401",
        all(s == 401 for s in (st_hs_an, st_av_an, st_av_put_an, st_av_del_an)),
        f"codes=({st_hs_an},{st_av_an},{st_av_put_an},{st_av_del_an})",
    )

    # Hồ sơ chỉ xem: 405 với PATCH/PUT/POST/DELETE; không lộ mat_khau_bam hay anh_dai_dien; không IDOR qua query ?id=1
    st_hs_u1, hs_u1, _ = cli_u1.request("GET", "/api/auth/ho-so?id=1&nguoi_dung_id=1")
    st_hs_tx, hs_tx, _ = cli_txa.request("GET", "/api/auth/ho-so?id=1")
    st_405 = [
        cli_u1.request(m, "/api/auth/ho-so", {"ho_ten": "Hack", "vai_tro": "QUAN_LY"})[0]
        for m in ("PATCH", "PUT", "POST", "DELETE")
    ]
    nhay_cam = {"mat_khau", "mat_khau_bam", "anh_dai_dien"}
    khong_lo = not (nhay_cam & set(hs_u1.keys())) and not (nhay_cam & set(hs_tx.keys()))
    kq.ghi(
        "PQ-12_ho_so_chi_xem_405_va_khong_IDOR",
        st_hs_u1 == 200
        and hs_u1["ten_dang_nhap"] == u_dp1
        and hs_u1["tai_xe"] is None
        and st_hs_tx == 200
        and hs_tx["ten_dang_nhap"] == u_txa
        and hs_tx["tai_xe"] is not None
        and all(s == 405 for s in st_405)
        and khong_lo,
        f"u1={hs_u1.get('ten_dang_nhap')}, tx={hs_tx.get('ten_dang_nhap')}, methods_405={st_405}, khong_lo={khong_lo}",
    )

    # Ảnh đại diện trên tài khoản PHA- (cli_u1 upload; cli_txa không đọc được; kiểm tra header bảo mật & file sai)
    st_up, b_up, _ = cli_u1.request(
        "PUT",
        "/api/auth/anh-dai-dien",
        multipart=({"nguoi_dung_id": "1", "vai_tro": "QUAN_LY"}, [("anh", "../../hack.png", PNG_A, "image/png")]),
    )
    st_get_u1, raw_u1, hdr_u1 = cli_u1.request("GET", "/api/auth/anh-dai-dien", raw_bytes=True)
    # Tài khoản PHA- khác thử đọc ảnh (kể cả truyền ?id= / ?nguoi_dung_id= của u1) -> phải 404 (chưa có ảnh của chính mình)
    st_get_cheo, _, _ = cli_txa.request("GET", f"/api/auth/anh-dai-dien?nguoi_dung_id={nd_u1['id']}&id={nd_u1['id']}")
    # Kiểm tra user #1 (quanly) không bị đổi vai trò / ảnh do trường lạ
    _, hs_ql_sau, _ = ql.request("GET", "/api/auth/ho-so")

    # Upload ảnh giả (SVG đổi đuôi .png), rỗng, và > 500KB
    st_svg, _, _ = cli_u1.request(
        "PUT", "/api/auth/anh-dai-dien", multipart=({}, [("anh", "x.png", b"<svg onload=alert(1)></svg>", "image/png")])
    )
    st_rong, _, _ = cli_u1.request(
        "PUT", "/api/auth/anh-dai-dien", multipart=({}, [("anh", "empty.png", b"", "image/png")])
    )
    st_lon, _, _ = cli_u1.request(
        "PUT", "/api/auth/anh-dai-dien", multipart=({}, [("anh", "big.png", PNG_B + b"0" * (500 * 1024), "image/png")])
    )

    # Xóa ảnh 2 lần đều 204, rồi GET -> 404
    st_del1, _, _ = cli_u1.request("DELETE", "/api/auth/anh-dai-dien")
    st_del2, _, _ = cli_u1.request("DELETE", "/api/auth/anh-dai-dien")
    st_get_sau, _, _ = cli_u1.request("GET", "/api/auth/anh-dai-dien")

    kq.ghi(
        "PQ-13_anh_dai_dien_upload_header_IDOR_va_xoa",
        st_up == 200
        and b_up.get("co_anh_dai_dien") is True
        and b_up.get("vai_tro") == "DIEU_PHOI"
        and st_get_u1 == 200
        and raw_u1 == PNG_A
        and hdr_u1.get("x-content-type-options") == "nosniff"
        and "private" in hdr_u1.get("cache-control", "")
        and st_get_cheo == 404
        and hs_ql_sau["vai_tro"] == "QUAN_LY"
        and st_svg == 400
        and st_rong == 400
        and st_lon == 413
        and st_del1 == 204
        and st_del2 == 204
        and st_get_sau == 404,
        f"up={st_up}, get={st_get_u1}(bytes_ok={raw_u1 == PNG_A}, nosniff={hdr_u1.get('x-content-type-options')}), "
        f"cheo={st_get_cheo}, bad=({st_svg},{st_rong},{st_lon}), del=({st_del1},{st_del2},{st_get_sau})",
    )

    # =========================================================================
    # NHÓM 6: ĐỔI MẬT KHẨU (PUT /api/auth/mat-khau), PHÂN QUYỀN CHÉO NGƯỜI DÙNG & KHÓA TỨC THÌ
    # =========================================================================
    st_mk_an, _, _ = anon.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": "a", "mat_khau_moi": "12345678"})
    # Trường thừa (thử đổi hộ người khác bằng nguoi_dung_id / id) -> 400
    st_mk_la, _, _ = cli_u1.request(
        "PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_pha, "mat_khau_moi": "PhaMoi123!", "nguoi_dung_id": 1}
    )
    # Mật khẩu trùng cũ -> 422 MAT_KHAU_TRUNG; ngắn < 8 -> 400
    st_mk_trung, b_trung, _ = cli_u1.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_pha, "mat_khau_moi": mk_pha})
    st_mk_ngan, _, _ = cli_u1.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_pha, "mat_khau_moi": "1234567"})
    # Sai mật khẩu cũ (chỉ 1 lần trên tài khoản PHA-) -> 422 SAI_MAT_KHAU_CU (KHÔNG phải 401!)
    st_mk_sai, b_sai, _ = cli_u1.request(
        "PUT", "/api/auth/mat-khau", {"mat_khau_cu": "SaiMatKhau!", "mat_khau_moi": "PhaMoi123!"}
    )
    # Đổi mật khẩu thành công -> 204; phiên cũ còn dùng được; đăng nhập lại bằng MK cũ 401, MK mới 200
    mk_moi = "PhaMoi999!"
    st_mk_ok, _, _ = cli_u1.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_pha, "mat_khau_moi": mk_moi})
    st_toi_cu, _, _ = cli_u1.request("GET", "/api/auth/toi")
    st_dn_cu, _, _ = ApiClient().request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": u_dp1, "mat_khau": mk_pha})
    st_dn_moi, _, _ = ApiClient().request("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": u_dp1, "mat_khau": mk_moi})
    kq.ghi(
        "PQ-14_doi_mat_khau_chinh_minh_va_chan_truong_la",
        st_mk_an == 401
        and st_mk_la == 400
        and st_mk_trung == 422
        and b_trung.get("ma") == "MAT_KHAU_TRUNG"
        and st_mk_ngan == 400
        and st_mk_sai == 422
        and b_sai.get("ma") == "SAI_MAT_KHAU_CU"
        and st_mk_ok == 204
        and st_toi_cu == 200
        and st_dn_cu == 401
        and st_dn_moi == 200,
        f"an={st_mk_an}, la={st_mk_la}, trung={st_mk_trung}, ngan={st_mk_ngan}, sai={st_mk_sai}, ok={st_mk_ok}, toi={st_toi_cu}, dnCu={st_dn_cu}, dnMoi={st_dn_moi}",
    )

    # PQ-15: Sai mật khẩu cũ 5 lần qua PUT /api/auth/mat-khau trên tài khoản PHA-lock riêng -> khóa tạm 429 cả đổi MK lẫn đăng nhập
    cac_sai = [
        cli_lock.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": f"Sai-{i}-xxx", "mat_khau_moi": "PhaMoi888!"})[0]
        for i in range(5)
    ]
    st_lan6, b_lan6, _ = cli_lock.request(
        "PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_pha, "mat_khau_moi": "PhaMoi888!"}
    )
    st_dn_khoa, b_dn_khoa, _ = ApiClient().request(
        "POST", "/api/auth/dang-nhap", {"ten_dang_nhap": u_lock, "mat_khau": mk_pha}
    )
    kq.ghi(
        "PQ-15_khoa_tam_khi_do_mat_khau_cu_tai_khoan_PHA",
        cac_sai == [422, 422, 422, 422, 422]
        and st_lan6 == 429
        and b_lan6.get("ma") == "KHOA_TAM"
        and st_dn_khoa == 429
        and b_dn_khoa.get("ma") == "KHOA_TAM",
        f"5_lan={cac_sai}, lan6={st_lan6}({b_lan6.get('ma') if isinstance(b_lan6, dict) else b_lan6}), dn_khi_khoa={st_dn_khoa}",
    )

    # PQ-16: Phân quyền chéo quản trị người dùng & đặt lại mật khẩu hộ + link ảnh chi phí
    cheo_nd = []
    for ten_vt, cli in [("DP", dp), ("KT", kt), ("TX", tx01)]:
        s1 = cli.request("GET", "/api/nguoi-dung")[0]
        s2 = cli.request("PATCH", f"/api/nguoi-dung/{nd_u1['id']}", {"ho_ten": "Hack"})[0]
        s3 = cli.request("PUT", f"/api/nguoi-dung/{nd_u1['id']}/mat-khau", {"mat_khau": "HackPass123!"})[0]
        cheo_nd.append((ten_vt, s1, s2, s3))
    tat_ca_403 = all(s1 == 403 and s2 == 403 and s3 == 403 for _, s1, s2, s3 in cheo_nd)
    # Kiểm tra /api/tep/1/link bị chặn với DP, TX, ẩn danh
    s_tep_an = anon.request("GET", "/api/tep/1/link")[0]
    s_tep_dp = dp.request("GET", "/api/tep/1/link")[0]
    s_tep_tx = tx01.request("GET", "/api/tep/1/link")[0]
    kq.ghi(
        "PQ-16_phan_quyen_cheo_nguoi_dung_va_tep_link",
        tat_ca_403 and s_tep_an == 401 and s_tep_dp == 403 and s_tep_tx == 403,
        f"nguoi_dung={cheo_nd}, tep_link=(an={s_tep_an},dp={s_tep_dp},tx={s_tep_tx})",
    )

    # PQ-17: Quản lý khóa tài khoản PHA- u1 -> cookie cũ lập tức bị 401 trên mọi API mới!
    st_k, _, _ = ql.request("PATCH", f"/api/nguoi-dung/{nd_u1['id']}", {"trang_thai": "NGUNG"})
    sau_khoa = {
        "tim": cli_u1.request("GET", "/api/tim?q=CH")[0],
        "thong_bao": cli_u1.request("GET", "/api/thong-bao")[0],
        "tong_quan": cli_u1.request("GET", "/api/tong-quan")[0],
        "du_doan": cli_u1.request("GET", f"/api/du-doan-tre?ngay={hom_nay}")[0],
        "ho_so": cli_u1.request("GET", "/api/auth/ho-so")[0],
        "anh": cli_u1.request("GET", "/api/auth/anh-dai-dien")[0],
        "mat_khau": cli_u1.request("PUT", "/api/auth/mat-khau", {"mat_khau_cu": mk_moi, "mat_khau_moi": "PhaMoi777!"})[0],
    }
    kq.ghi(
        "PQ-17_khoa_tai_khoan_vo_hieu_cookie_ngay_tren_moi_api_moi",
        st_k == 200 and all(v == 401 for v in sau_khoa.values()),
        f"khoa={st_k}, ket_qua_cookie_cu={sau_khoa}",
    )

    return kq.tong_ket()


if __name__ == "__main__":
    sys.exit(main())
