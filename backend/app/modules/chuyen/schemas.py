from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.kieu import ChuBatBuoc
from app.modules.don.schemas import DonRa

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


class PhanCongVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    xe_id: int
    tai_xe_id: int


class GhepVao(BaseModel):
    # Chỉ nhận danh sách đơn: không có cách ghép một phần đơn (BR-08), trường lạ → 400
    model_config = ConfigDict(extra="forbid")

    don_ids: list[int] = Field(min_length=1)


class TaiTrong(BaseModel):
    da_dung_kg: Decimal
    toi_da_kg: int


class TheTich(BaseModel):
    da_dung_m3: Decimal
    toi_da_m3: Decimal


class DiemRa(BaseModel):
    thu_tu: int
    nut: str
    viec: Literal["LAY", "GIAO"]
    don_id: int
    ma_don: str
    eta: datetime


class ChuyenChiTiet(ChuyenRa):
    """Tổng quan + thẻ Hàng (UC-13); cũng là kết quả của ghép, gỡ (api.md mục 3.1)."""

    tai_trong: TaiTrong
    the_tich: TheTich
    ty_le_lap_day: Decimal
    lich_trinh: list[DiemRa]
    lai_du_kien: int
    canh_bao_lai_am: bool
    chay_rong: bool
    don: list[DonRa]


class HuyVao(BaseModel):
    """Hủy chuyến (UC-16): lý do bắt buộc (BR-25), lưu vào lịch sử trạng thái."""

    model_config = ConfigDict(extra="forbid")

    ly_do: ChuBatBuoc = Field(max_length=300)


class ChotVao(BaseModel):
    """Xác nhận khi chốt (UC-15): chuyến không có đơn (BR-23), lãi dự kiến âm (BR-52)."""

    model_config = ConfigDict(extra="forbid")

    xac_nhan_chay_rong: bool = False
    xac_nhan_lai_am: bool = False
