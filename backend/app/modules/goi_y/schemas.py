from typing import Literal

from pydantic import BaseModel, Field


class YeuTo(BaseModel):
    ten: str
    huong: Literal["TANG", "GIAM"]


class DuDoanTreRa(BaseModel):
    # co_du_doan false: các trường còn lại để None (không có mô hình, mô hình hỏng, chuyến hủy – UC-30-AC4)
    co_du_doan: bool
    xac_suat: float | None = Field(default=None, ge=0, le=1)
    muc: Literal["THAP", "TRUNG_BINH", "CAO"] | None = None
    yeu_to: list[YeuTo] | None = None
    nguon: dict | None = None
