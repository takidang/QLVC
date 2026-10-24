from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.kieu import ChuBatBuoc, SoDienThoai

SoKg = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
SoKhoi = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]
DiaChi = Annotated[ChuBatBuoc, Field(max_length=300)]
Ten = Annotated[ChuBatBuoc, Field(max_length=100)]
ViDo = Annotated[Decimal, Field(ge=-90, le=90, max_digits=9, decimal_places=6)]
KinhDo = Annotated[Decimal, Field(ge=-180, le=180, max_digits=9, decimal_places=6)]
TrangThaiDon = Literal["CHO_GHEP", "DA_GHEP", "DA_LAY", "DA_GIAO", "THAT_BAI", "TRA_HANG", "HUY"]  # ST-O


class TinhCuocVao(BaseModel):
    nut_lay_id: int
    nut_giao_id: int
    kg: SoKg
    m3: SoKhoi


class TinhCuocRa(BaseModel):
    kl_quy_doi: Decimal
    kl_tinh_cuoc: Decimal
    don_gia_kg: int
    cuoc_toi_thieu: int
    cuoc: int


class DonVao(BaseModel):
    # Thời gian phải có múi giờ (AwareDatetime): thiếu múi giờ → 400 (quyết định UC-08 số 2)
    model_config = ConfigDict(extra="forbid")

    khach_hang_id: int
    mo_ta: Annotated[str, Field(max_length=300)] | None = None
    kg: SoKg
    m3: SoKhoi
    so_kien: Annotated[int, Field(ge=1)]

    nut_lay_id: int
    dia_chi_lay: DiaChi
    lat_lay: ViDo | None = None
    lng_lay: KinhDo | None = None
    nguoi_lien_he_lay: Ten | None = None
    sdt_lay: SoDienThoai
    lay_tu: AwareDatetime | None = None
    lay_den: AwareDatetime | None = None

    nut_giao_id: int
    dia_chi_giao: DiaChi
    lat_giao: ViDo | None = None
    lng_giao: KinhDo | None = None
    nguoi_nhan: Ten
    sdt_nhan: SoDienThoai
    han_giao: AwareDatetime


class DonRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ma_don: str
    khach_hang_id: int
    ten_khach: str
    mo_ta: str | None
    kg: Decimal
    m3: Decimal
    so_kien: int
    nut_lay_id: int
    tinh_lay: str
    dia_chi_lay: str
    sdt_lay: str
    lay_tu: datetime | None
    lay_den: datetime | None
    nut_giao_id: int
    tinh_giao: str
    dia_chi_giao: str
    nguoi_nhan: str
    sdt_nhan: str
    han_giao: datetime
    kl_tinh_cuoc: Decimal
    cuoc_tinh: int
    trang_thai: str
    tao_luc: datetime
