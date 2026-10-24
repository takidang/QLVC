from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.kieu import ChuBatBuoc

Tinh = Annotated[ChuBatBuoc, Field(max_length=50)]
DonGia = Annotated[int, Field(gt=0)]
CuocToiThieu = Annotated[int, Field(ge=0)]


class BangGiaVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tinh_lay: Tinh
    tinh_giao: Tinh
    don_gia_kg: DonGia
    cuoc_toi_thieu: CuocToiThieu
    hieu_luc_tu: date


class BangGiaSua(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tinh_lay: Tinh | None = None
    tinh_giao: Tinh | None = None
    don_gia_kg: DonGia | None = None
    cuoc_toi_thieu: CuocToiThieu | None = None
    hieu_luc_tu: date | None = None

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        # Mọi trường đều bắt buộc: gửi null → 400, không để CSDL báo lỗi 500
        for truong in self.model_fields_set:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class BangGiaRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tinh_lay: str
    tinh_giao: str
    don_gia_kg: int
    cuoc_toi_thieu: int
    hieu_luc_tu: date
    dang_ap_dung: bool = False
