from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.kieu import ChuBatBuoc

HinhThuc = Literal["TIEN_MAT", "CHUYEN_KHOAN"]
TrangThaiTamUng = Literal["HIEU_LUC", "DA_THU_HOI"]  # BR-53
# Số nguyên đồng (NFR-FUN-02); trần chặn số vô lý vì bảng không có ràng buộc (UC-23 quyết định 8)
SoTien = Annotated[int, Field(ge=1, le=1_000_000_000_000, strict=True)]
LyDo = Annotated[ChuBatBuoc, Field(max_length=300)]


class TamUngVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    so_tien: SoTien
    hinh_thuc: HinhThuc


class TamUngSua(BaseModel):
    model_config = ConfigDict(extra="forbid")

    so_tien: SoTien
    hinh_thuc: HinhThuc | None = None  # bỏ trống: giữ hình thức cũ
    ly_do: LyDo  # sửa bắt buộc lý do (UC-23 3a)


class ThuHoiVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ly_do: LyDo | None = None  # bỏ trống: nhật ký ghi câu mặc định (quyết định 5)


class TamUngRa(BaseModel):
    id: int
    chuyen_id: int
    ma_chuyen: str
    tai_xe_id: int
    ten_tai_xe: str
    so_tien: int
    hinh_thuc: HinhThuc
    trang_thai: TrangThaiTamUng
    tao_luc: datetime


class TamUngChuyen(BaseModel):
    """Màn hình cấp: định mức đã chốt, đã cấp còn hiệu lực, số gợi ý còn được cấp (UC-23 bước 1)."""

    chuyen_id: int
    ma_chuyen: str
    trang_thai_chuyen: str
    dinh_muc: int
    tong_hieu_luc: int
    con_duoc_cap: int
    khoan: list[TamUngRa]
