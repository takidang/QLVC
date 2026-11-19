from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.modules.danh_muc.tai_xe.schemas import MatKhau


class DangNhapVao(BaseModel):
    ten_dang_nhap: str = Field(min_length=1, max_length=50)
    mat_khau: str = Field(min_length=1, max_length=200)


class NguoiDungRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ho_ten: str
    vai_tro: str
    co_anh_dai_dien: bool


class TaiXeHoSoRa(BaseModel):
    """Thông tin tài xế chỉ xem trong hồ sơ cá nhân (UC-39-AC1)."""

    model_config = ConfigDict(from_attributes=True)

    sdt: str
    so_gplx: str
    hang_gplx: str
    han_gplx: date


class HoSoRa(BaseModel):
    """UC-39: hồ sơ cá nhân của chính người đang đăng nhập; không lộ mật khẩu hay tên file ảnh."""

    id: int
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: str
    trang_thai: str
    co_anh_dai_dien: bool
    tai_xe: TaiXeHoSoRa | None = None


class DoiMatKhauVao(BaseModel):
    """UC-35: người dùng tự đổi mật khẩu; chỉ của chính mình (không nhận id)."""

    model_config = ConfigDict(extra="forbid")

    mat_khau_cu: str = Field(min_length=1, max_length=200)
    mat_khau_moi: MatKhau
