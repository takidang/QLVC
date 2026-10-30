from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict

TrangThaiChuyen = Literal["LAP", "DA_CHOT", "DANG_CHAY", "HOAN_THANH", "DA_QUYET_TOAN", "HUY"]  # ST-T


class ChuyenVao(BaseModel):
    # Giờ phải có múi giờ, thiếu → 400 (như UC-08)
    model_config = ConfigDict(extra="forbid")

    tuyen_id: int
    khoi_hanh_du_kien: AwareDatetime
    xe_id: int
    tai_xe_id: int


class ChuyenRa(BaseModel):
    id: int
    ma_chuyen: str
    tuyen_id: int
    ma_tuyen: str
    ten_tuyen: str
    xe_id: int
    bien_so: str
    tai_xe_id: int
    ten_tai_xe: str
    khoi_hanh_du_kien: datetime
    ket_thuc_du_kien: datetime
    trang_thai: str


class LyDo(BaseModel):
    ma: str
    thong_diep: str


class XeKhaDung(BaseModel):
    id: int
    bien_so: str
    tai_trong_kg: int
    the_tich_m3: Decimal
    ktt_toan_bo_kg: int
    kha_dung: bool
    ly_do: list[LyDo]


class TaiXeKhaDung(BaseModel):
    id: int
    ho_ten: str
    hang_gplx: str
    han_gplx: date
    kha_dung: bool
    ly_do: list[LyDo]
