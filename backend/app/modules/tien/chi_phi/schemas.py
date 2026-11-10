from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

LoaiChi = Literal["DAU", "CAU_DUONG", "BOC_XEP", "PHAT_SINH"]
TrangThaiChi = Literal["CHO_DUYET", "DA_DUYET", "TU_CHOI"]
# Số nguyên đồng (NFR-FUN-02), trần chặn số vô lý; số lít theo cột Numeric(8, 2)
SoTien = Annotated[int, Field(ge=1, le=1_000_000_000_000)]
SoLit = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]


class ChiPhiSua(BaseModel):
    """Tài xế sửa khoản chờ duyệt; trường không gửi thì giữ. `so_lit: null` để bỏ số lít khi đổi khỏi dầu."""

    model_config = ConfigDict(extra="forbid")

    loai: LoaiChi | None = None
    so_tien: Annotated[int, Field(ge=1, le=1_000_000_000_000, strict=True)] | None = None
    so_lit: SoLit | None = None
    ghi_chu: Annotated[str, Field(max_length=500)] | None = None


class ChiPhiRa(BaseModel):
    id: int
    chuyen_id: int
    loai: LoaiChi
    so_tien_khai: int
    so_tien_duyet: int | None
    so_lit: Decimal | None
    ghi_chu: str
    trang_thai: TrangThaiChi
    so_anh: int
    tao_luc: datetime


class ChiPhiChuyen(BaseModel):
    chuyen_id: int
    tam_ung_da_nhan: int  # tạm ứng HIEU_LUC của chuyến (UC-23 quyết định 9)
    tong_da_khai: int  # các khoản chưa bị từ chối
    khoan: list[ChiPhiRa]
