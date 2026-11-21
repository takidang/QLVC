from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.modules.chuyen.schemas import ChuyenRa


class ChuyenCuaToi(ChuyenRa):
    """Một dòng "Chuyến của tôi" (UC-17). Không có trường tiền."""

    so_don: int


class DiemCuaToi(BaseModel):
    """Một điểm dừng kèm đơn ở điểm đó: đủ để tài xế tìm đường, gọi điện, kiểm hàng. Không có cước (UC-17 số 3)."""

    thu_tu: int
    nut: str
    viec: Literal["LAY", "GIAO"]
    eta: datetime
    don_id: int
    ma_don: str
    ten_khach: str
    mo_ta: str | None
    kg: Decimal
    m3: Decimal
    so_kien: int
    trang_thai_don: str
    da_lay: bool  # đã quét lấy trong chuyến này (nhãn điểm Lấy khi đơn giao thất bại)
    dia_chi: str
    nguoi_lien_he: str | None
    sdt: str
    lay_tu: datetime | None
    lay_den: datetime | None
    han_giao: datetime


class ChuyenCuaToiChiTiet(ChuyenCuaToi):
    luong_tai_xe_chot: int | None  # BR-71: lương khoán đã chốt của chính tài xế
    lich_trinh: list[DiemCuaToi]
