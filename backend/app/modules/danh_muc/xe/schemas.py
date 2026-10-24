from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

BienSo = Annotated[str, Field(min_length=1, max_length=20)]
SoKgDuong = Annotated[int, Field(gt=0)]
TheTich = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]
DinhMucLit = Annotated[Decimal, Field(ge=0, max_digits=5, decimal_places=2)]


def chuan_hoa_bien_so(v: str | None) -> str | None:
    if v is None:  # XeSua gửi null: để khong_xoa_truong_bat_buoc báo lỗi
        return v
    v = v.strip().upper()
    if not v:
        raise ValueError("Biển số không được để trống")
    return v


class XeVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bien_so: BienSo
    tai_trong_kg: SoKgDuong
    the_tich_m3: TheTich
    ktt_toan_bo_kg: SoKgDuong
    han_dang_kiem: date
    han_bao_hiem: date
    dinh_muc_lit_100km: DinhMucLit | None = None
    km_dong_ho: Annotated[int, Field(ge=0)] = 0

    chuan_hoa = field_validator("bien_so")(chuan_hoa_bien_so)


class XeSua(BaseModel):
    """Không có km_dong_ho: km chỉ nhập lúc tạo, sau đó đổi qua chuyến (BR-70). Gửi lên → 400."""

    model_config = ConfigDict(extra="forbid")

    bien_so: BienSo | None = None
    tai_trong_kg: SoKgDuong | None = None
    the_tich_m3: TheTich | None = None
    ktt_toan_bo_kg: SoKgDuong | None = None
    han_dang_kiem: date | None = None
    han_bao_hiem: date | None = None
    dinh_muc_lit_100km: DinhMucLit | None = None
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None  # BR-11

    chuan_hoa = field_validator("bien_so")(chuan_hoa_bien_so)

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        # Gửi null cho trường bắt buộc → 400, không để CSDL báo lỗi 500
        for truong in self.model_fields_set - {"dinh_muc_lit_100km"}:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class XeRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bien_so: str
    tai_trong_kg: int
    the_tich_m3: Decimal
    ktt_toan_bo_kg: int
    han_dang_kiem: date
    han_bao_hiem: date
    dinh_muc_lit_100km: Decimal | None
    km_dong_ho: int
    trang_thai: str


class ChiPhiCoDinhVao(BaseModel):
    so_tien: Annotated[int, Field(ge=0)]


class ChiPhiCoDinhRa(BaseModel):
    xe_id: int
    thang: str
    so_tien: int | None  # None: chưa nhập
