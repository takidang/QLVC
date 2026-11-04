from typing import Literal

from pydantic import BaseModel

# UC-19 làm LAY, KHONG_LAY; GIAO, GIAO_THAT_BAI thêm ở UC-20 (api.md 3.2), gửi bây giờ → 400
LoaiQuet = Literal["LAY", "KHONG_LAY"]


class QuetRa(BaseModel):
    ma_don: str
    trang_thai: str
    canh_bao: list[str]  # THIEU_GPS (BR-43); UC-20 thêm GIAO_TRE (BR-72)
    lap_lai: bool  # BR-45: đơn đã có kết quả từ trước, không tạo bản ghi mới
