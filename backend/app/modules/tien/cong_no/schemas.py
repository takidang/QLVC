import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictInt


def _chi_ngay(v: object) -> object:
    # Ngày thu chỉ là ngày "YYYY-MM-DD"; gửi kèm giờ, số… thì báo sai dạng (400) thay vì tự cắt giờ
    if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        raise ValueError("Ngày thu phải có dạng YYYY-MM-DD")
    return v


TrangThaiTT = Literal["CHUA_THU", "DA_THU"]  # trạng thái thanh toán, tách khỏi vòng đời đơn (BR-56)


class DaThuVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phai_thu_ids: Annotated[list[StrictInt], Field(min_length=1, max_length=100)]
    ngay: Annotated[date, BeforeValidator(_chi_ngay)]


class PhaiThuRa(BaseModel):
    id: int
    don_hang_id: int
    ma_don: str
    khach_hang_id: int
    ten_khach: str
    ngay_giao: datetime | None
    so_tien: int
    trang_thai_tt: TrangThaiTT
    phieu_thu_id: int | None
    ngay_thu: date | None


class DanhSachPhaiThu(BaseModel):
    du_lieu: list[PhaiThuRa]
    tong: int
    tong_tien: int  # Σ số tiền của bộ lọc


class NoTheoKhach(BaseModel):
    khach_hang_id: int
    ten_khach: str
    so_khoan: int
    tong_no: int


class PhieuThuRa(BaseModel):
    phieu_thu_id: int
    khach_hang_id: int
    tong_tien: int
    ngay: date
    so_khoan: int
