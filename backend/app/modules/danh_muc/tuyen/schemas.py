from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.kieu import ChuBatBuoc

Tien = Annotated[int, Field(ge=0)]
SoKhongAm = Annotated[int, Field(ge=0)]


class NutTuyenVao(BaseModel):
    nut_id: int
    phut_tu_diem_dau: SoKhongAm
    km_tu_diem_dau: SoKhongAm
    la_diem_nghi: bool = False


class TuyenVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ma: Annotated[ChuBatBuoc, Field(max_length=20)]
    ten: Annotated[ChuBatBuoc, Field(max_length=100)]
    dm_dau: Tien
    dm_cau_duong: Tien
    dm_boc_xep: Tien
    dm_luong_tai_xe: Tien  # lương khoán mỗi chuyến
    nut: list[NutTuyenVao]


class TuyenSua(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten: Annotated[ChuBatBuoc, Field(max_length=100)] | None = None
    dm_dau: Tien | None = None
    dm_cau_duong: Tien | None = None
    dm_boc_xep: Tien | None = None
    dm_luong_tai_xe: Tien | None = None
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None  # BR-60
    nut: list[NutTuyenVao] | None = None

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        for truong in self.model_fields_set:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class NutTuyenRa(BaseModel):
    thu_tu: int
    nut_id: int
    ten: str
    tinh: str
    phut_tu_diem_dau: int
    km_tu_diem_dau: int
    la_diem_nghi: bool


class TuyenRa(BaseModel):
    id: int
    ma: str
    ten: str
    dm_dau: int
    dm_cau_duong: int
    dm_boc_xep: int
    dm_luong_tai_xe: int
    trang_thai: str
    nut: list[NutTuyenRa]
    tong_phut: int
    tong_km: int
    canh_bao: list[str]  # BR-20, chỉ cảnh báo
