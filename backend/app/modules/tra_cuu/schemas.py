from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TraCuuVao(BaseModel):
    """api.md 3.4: POST để số điện thoại không nằm trong URL và log truy cập."""

    model_config = ConfigDict(extra="forbid")

    ma_don: str = Field(min_length=1, max_length=20)
    sdt_4_so_cuoi: str = Field(pattern=r"^\d{4}$")


class Moc(BaseModel):
    trang_thai: str
    luc: datetime


class TraCuuRa(BaseModel):
    """Chỉ trạng thái và mốc thời gian (BR-59): không cước, GPS, SĐT, lý do, người thao tác."""

    ma_don: str
    trang_thai: str
    moc: list[Moc]
