from typing import Literal

from pydantic import BaseModel

# api.md 3.2: lấy (UC-19), giao (UC-20); hai loại thất bại đưa đơn về THAT_BAI
LoaiQuet = Literal["LAY", "KHONG_LAY", "GIAO", "GIAO_THAT_BAI"]


class QuetRa(BaseModel):
    ma_don: str
    trang_thai: str
    canh_bao: list[str]  # THIEU_GPS (BR-43), GIAO_TRE (BR-72)
    lap_lai: bool  # BR-45: đơn đã có kết quả từ trước, không tạo bản ghi mới
