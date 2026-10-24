from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.kieu import ChuBatBuoc, SoDienThoai

Ten = Annotated[ChuBatBuoc, Field(max_length=200)]
DiaChi = Annotated[str, Field(max_length=300)]
# Mã số thuế doanh nghiệp: 10 số, hoặc 10 số + "-" + 3 số (chi nhánh)
MaSoThue = Annotated[str, Field(pattern=r"^\d{10}(-\d{3})?$")]


class KhachHangVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten: Ten
    sdt: SoDienThoai
    dia_chi: DiaChi | None = None
    ma_so_thue: MaSoThue | None = None


class KhachHangSua(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten: Ten | None = None
    sdt: SoDienThoai | None = None
    dia_chi: DiaChi | None = None
    ma_so_thue: MaSoThue | None = None
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None  # BR-60

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        # Gửi null cho trường bắt buộc → 400, không để CSDL báo lỗi 500
        for truong in self.model_fields_set & {"ten", "sdt", "trang_thai"}:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class KhachHangRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ten: str
    sdt: str
    dia_chi: str | None
    ma_so_thue: str | None
    trang_thai: str
