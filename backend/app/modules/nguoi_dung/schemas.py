from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.danh_muc.tai_xe.schemas import HoTen, MatKhau, TenDangNhap

# Tài xế tạo, đổi vai trò, khóa/mở ở UC-04 để hồ sơ tài xế và tài khoản luôn cùng trạng thái (chốt 30/10)
VaiTro = Literal["QUAN_LY", "DIEU_PHOI", "KE_TOAN"]


class NguoiDungVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten_dang_nhap: TenDangNhap
    ho_ten: HoTen
    mat_khau: MatKhau
    vai_tro: VaiTro


class NguoiDungSua(BaseModel):
    """Không có mật khẩu: đặt lại ở PUT /{id}/mat-khau. Gửi lên → 400."""

    model_config = ConfigDict(extra="forbid")

    ten_dang_nhap: TenDangNhap | None = None
    ho_ten: HoTen | None = None
    vai_tro: VaiTro | None = None
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None  # BR-60

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        for truong in self.model_fields_set:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class MatKhauVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mat_khau: MatKhau


class NguoiDungRa(BaseModel):
    """Không bao giờ có mật khẩu hay mật khẩu băm (UC-02-AC1)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: str
    trang_thai: str
    khoa_den: datetime | None  # khóa tạm do sai mật khẩu (NFR-SEC-05)
