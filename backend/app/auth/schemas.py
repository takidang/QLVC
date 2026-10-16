from pydantic import BaseModel, ConfigDict, Field


class DangNhapVao(BaseModel):
    ten_dang_nhap: str = Field(min_length=1, max_length=50)
    mat_khau: str = Field(min_length=1, max_length=200)


class NguoiDungRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ho_ten: str
    vai_tro: str
