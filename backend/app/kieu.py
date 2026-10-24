"""Kiểu dữ liệu dùng chung cho schema: dùng lại ở khách hàng, đơn hàng, tài xế."""

import re
import unicodedata
from typing import Annotated

from pydantic import AfterValidator


def chuan_hoa_sdt(v: str | None) -> str | None:
    """Bỏ khoảng trắng, dấu chấm, gạch; +84 → 0; phải là 0 + 9 hoặc 10 chữ số (BR-59 dùng 4 số cuối)."""
    if v is None:  # schema sửa gửi null: để kiểm trường bắt buộc báo lỗi
        return v
    so = re.sub(r"[\s.\-()]", "", v)
    if so.startswith("+84"):
        so = "0" + so[3:]
    if not re.fullmatch(r"0\d{9,10}", so):
        raise ValueError("Số điện thoại phải gồm 10 hoặc 11 chữ số, bắt đầu bằng 0")
    return so


def chuan_hoa_chu(v: str | None) -> str | None:
    """Bỏ khoảng trắng đầu cuối; đưa về Unicode dựng sẵn (NFC); chuỗi rỗng sau khi bỏ thì báo lỗi.

    NFC: "Cần Thơ" gõ kiểu tổ hợp (Unikey tổ hợp, macOS) và kiểu dựng sẵn thành cùng một chuỗi,
    để tra giá theo tỉnh (BR-48), chặn trùng và so địa chỉ (BR-31) không lọt.
    """
    if v is None:
        return v
    v = unicodedata.normalize("NFC", v).strip()
    if not v:
        raise ValueError("Không được để trống")
    return v


SoDienThoai = Annotated[str, AfterValidator(chuan_hoa_sdt)]
ChuBatBuoc = Annotated[str, AfterValidator(chuan_hoa_chu)]
