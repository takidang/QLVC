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


class DoiMatKhauVao(BaseModel):
    """UC-35: người dùng tự đổi mật khẩu; chỉ của chính mình (không nhận id)."""

    model_config = ConfigDict(extra="forbid")

    mat_khau_cu: str = Field(min_length=1, max_length=200)
    mat_khau_moi: MatKhau
