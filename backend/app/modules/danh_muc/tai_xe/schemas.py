import re
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.kieu import ChuBatBuoc, SoDienThoai

HangGplx = Literal["B", "C1", "C"]  # BR-14
TenDangNhap = Annotated[ChuBatBuoc, Field(max_length=50)]
HoTen = Annotated[ChuBatBuoc, Field(max_length=100)]
MatKhau = Annotated[str, Field(min_length=8, max_length=200)]  # UC-04-AC2: 7 ký tự bị chặn, 8 được


def chuan_hoa_so_gplx(v: str | None) -> str | None:
    """Bỏ mọi khoảng trắng, viết hoa; 6–20 chữ/số để nhập được cả bằng mẫu cũ (chốt 25/10, UC-04)."""
    if v is None:  # TaiXeSua gửi null: để khong_xoa_truong_bat_buoc báo lỗi
        return v
    v = re.sub(r"\s", "", v).upper()
    if not re.fullmatch(r"[A-Z0-9]{6,20}", v):
        raise ValueError("Số GPLX gồm 6–20 chữ cái hoặc chữ số")
    return v


def chuan_hoa_hang(v: object) -> object:
    """Gõ thường "c1" vẫn nhận thành "C1" (chốt 25/10, UC-04)."""
    return v.strip().upper() if isinstance(v, str) else v


class TaiXeVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten_dang_nhap: TenDangNhap
    ho_ten: HoTen
    mat_khau: MatKhau
    so_gplx: str
    hang_gplx: HangGplx
    han_gplx: date
    sdt: SoDienThoai

    chuan_hoa_gplx = field_validator("so_gplx")(chuan_hoa_so_gplx)
    chuan_hoa_hang_gplx = field_validator("hang_gplx", mode="before")(chuan_hoa_hang)


class TaiXeSua(BaseModel):
    """Không có tên đăng nhập, mật khẩu: đổi ở UC-02 (chốt 25/10). Gửi lên → 400."""

    model_config = ConfigDict(extra="forbid")

    ho_ten: HoTen | None = None
    so_gplx: str | None = None
    hang_gplx: HangGplx | None = None
    han_gplx: date | None = None
    sdt: SoDienThoai | None = None
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None  # BR-60

    chuan_hoa_gplx = field_validator("so_gplx")(chuan_hoa_so_gplx)
    chuan_hoa_hang_gplx = field_validator("hang_gplx", mode="before")(chuan_hoa_hang)

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        # Mọi trường đều bắt buộc: gửi null → 400, không để CSDL báo lỗi 500
        for truong in self.model_fields_set:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class TaiXeRa(BaseModel):
    """Không bao giờ có mật khẩu hay mật khẩu băm (UC-04-AC1)."""

    id: int
    ten_dang_nhap: str
    ho_ten: str
    so_gplx: str
    hang_gplx: str
    han_gplx: date
    sdt: str
    trang_thai: str
