"""Tiện ích dùng chung cho bộ kiểm thử khám phá QLVC (không cần cài gói ngoài)."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_API = "http://127.0.0.1:8000"
BASE_FE = "http://127.0.0.1:5173"
VN_TZ = timezone(timedelta(hours=7))

# JPEG tối thiểu hợp lệ (1x1 pixel trắng) và PNG tối thiểu hợp lệ (1x1 pixel)
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


@dataclass
class KetQuaCa:
    ma: str
    ten: str
    dat: bool
    muc: str = ""  # Nghiem trong | Vua | Nhe (khi dat=False)
    tai_hien: str = ""
    thuc_te: str = ""
    mong_doi: str = ""
    br: str = ""


class BaoCaoMuc:
    def __init__(self, muc_so: int, ten_muc: str):
        self.muc_so = muc_so
        self.ten_muc = ten_muc
        self.ca: list[KetQuaCa] = []

    def ghi(
        self,
        ma: str,
        ten: str,
        dat: bool,
        thuc_te: str,
        mong_doi: str,
        tai_hien: str = "",
        muc: str = "Vua",
        br: str = "",
    ) -> KetQuaCa:
        item = KetQuaCa(
            ma=ma,
            ten=ten,
            dat=dat,
            muc="" if dat else muc,
            tai_hien=tai_hien,
            thuc_te=thuc_te,
            mong_doi=mong_doi,
            br=br,
        )
        self.ca.append(item)
        icon = "DAT" if dat else f"LOI[{muc}]"
        print(f"  [{icon}] {ma}: {ten} -> {thuc_te[:160]}")
        return item

    def luu_json(self, ten_file: str) -> None:
        duong_dan = os.path.join(os.path.dirname(__file__), ten_file)
        tong = len(self.ca)
        dat = sum(1 for c in self.ca if c.dat)
        loi = tong - dat
        data = {
            "muc_so": self.muc_so,
            "ten_muc": self.ten_muc,
            "tong": tong,
            "dat": dat,
            "loi": loi,
            "ca": [asdict(c) for c in self.ca],
        }
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n==> Mục {self.muc_so} ({self.ten_muc}): {tong} ca | Đạt: {dat} | Lỗi: {loi}")


def encode_multipart(fields: dict[str, Any] | list[tuple[str, Any]], files: list[tuple[str, str, bytes, str]]) -> tuple[bytes, str]:
    boundary = f"----QLVCTest{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    items = fields.items() if isinstance(fields, dict) else fields
    for k, v in items:
        if v is None:
            continue
        chunks.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8")
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
    """HTTP client mỏng dùng urllib, an toàn đa luồng khi truyền sẵn token."""

    def __init__(self, base_url: str = BASE_API, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def clone(self) -> "ApiClient":
        return ApiClient(self.base_url, self.token)

    def raw(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        raw_body: bytes | None = None,
        content_type: str | None = None,
        extra_headers: dict[str, str] | None = None,
        timeout: int = 20,
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
        if extra_headers:
            headers.update(extra_headers)
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
        extra_headers: dict[str, str] | None = None,
    ) -> tuple[int, Any, dict[str, str]]:
        body, ctype = encode_multipart(fields or {}, files or [])
        return self.raw(method, path, raw_body=body, content_type=ctype, extra_headers=extra_headers)

    def login(self, ten_dang_nhap: str, mat_khau: str = "demo12345") -> tuple[int, Any]:
        st, data, headers = self.raw("POST", "/api/auth/dang-nhap", {"ten_dang_nhap": ten_dang_nhap, "mat_khau": mat_khau})
        for k, v in headers.items():
            if k.lower() == "set-cookie":
                m = re.search(r"access_token=([^;]+)", v)
                if m:
                    self.token = m.group(1)
        return st, data


def dang_nhap(user: str, pw: str = "demo12345") -> ApiClient:
    c = ApiClient()
    st, data = c.login(user, pw)
    assert st == 200 and c.token, f"Dang nhap {user} that bai: {st} {data}"
    return c


def now_vn() -> datetime:
    return datetime.now(VN_TZ)


def iso_vn(dt: datetime) -> str:
    return dt.astimezone(VN_TZ).isoformat(timespec="seconds")


def tom_tat(status: int, data: Any) -> str:
    s = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
    if len(s) > 220:
        s = s[:220] + "…"
    return f"HTTP {status}: {s}"
