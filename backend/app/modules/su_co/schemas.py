from datetime import datetime
from typing import Literal

from pydantic import BaseModel

# UC-33 quyết định 2: danh sách cố định (cột loai là chuỗi, chưa có bảng danh mục)
LoaiSuCo = Literal["HONG_XE", "TAI_NAN", "KET_XE", "THOI_TIET", "KHAC"]


class SuCoRa(BaseModel):
    id: int
    chuyen_id: int
    loai: str  # đọc ra để chuỗi: dữ liệu cũ ngoài danh sách vẫn xem được
    ghi_chu: str | None  # sự cố cũ (trước UC-33) có thể trống
    trang_thai: Literal["MO", "DONG"]
    cach_xu_ly: str | None
    so_anh: int
    luc: datetime
