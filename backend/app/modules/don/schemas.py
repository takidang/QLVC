from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.kieu import ChuBatBuoc, SoDienThoai

SoKg = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
SoKhoi = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]
DiaChi = Annotated[ChuBatBuoc, Field(max_length=300)]
Ten = Annotated[ChuBatBuoc, Field(max_length=100)]
ViDo = Annotated[Decimal, Field(ge=-90, le=90, max_digits=9, decimal_places=6)]
KinhDo = Annotated[Decimal, Field(ge=-180, le=180, max_digits=9, decimal_places=6)]
TrangThaiDon = Literal["CHO_GHEP", "DA_GHEP", "DA_LAY", "DA_GIAO", "THAT_BAI", "TRA_HANG", "HUY"]  # ST-O


class TinhCuocVao(BaseModel):
    nut_lay_id: int
    nut_giao_id: int
    kg: SoKg
    m3: SoKhoi


class TinhCuocRa(BaseModel):
    kl_quy_doi: Decimal
    kl_tinh_cuoc: Decimal
    don_gia_kg: int
    cuoc_toi_thieu: int
    cuoc: int


class DonVao(BaseModel):
    # Thời gian phải có múi giờ (AwareDatetime): thiếu múi giờ → 400 (quyết định UC-08 số 2)
    model_config = ConfigDict(extra="forbid")

    khach_hang_id: int
    mo_ta: Annotated[str, Field(max_length=300)] | None = None
    kg: SoKg
    m3: SoKhoi
    so_kien: Annotated[int, Field(ge=1)]

    nut_lay_id: int
    dia_chi_lay: DiaChi
    lat_lay: ViDo | None = None
    lng_lay: KinhDo | None = None
    nguoi_lien_he_lay: Ten | None = None
    sdt_lay: SoDienThoai
    lay_tu: AwareDatetime | None = None
    lay_den: AwareDatetime | None = None

    nut_giao_id: int
    dia_chi_giao: DiaChi
    lat_giao: ViDo | None = None
    lng_giao: KinhDo | None = None
    nguoi_nhan: Ten
    sdt_nhan: SoDienThoai
    han_giao: AwareDatetime


class DonSua(BaseModel):
    """UC-10: gửi trường nào sửa trường đó. Không có khách, nút lấy / giao (quyết định 1): gửi lên → 400."""

    model_config = ConfigDict(extra="forbid")

    mo_ta: Annotated[str, Field(max_length=300)] | None = None
    kg: SoKg | None = None
    m3: SoKhoi | None = None
    so_kien: Annotated[int, Field(ge=1)] | None = None
    dia_chi_lay: DiaChi | None = None
    lat_lay: ViDo | None = None
    lng_lay: KinhDo | None = None
    nguoi_lien_he_lay: Ten | None = None
    sdt_lay: SoDienThoai | None = None
    lay_tu: AwareDatetime | None = None
    lay_den: AwareDatetime | None = None
    dia_chi_giao: DiaChi | None = None
    lat_giao: ViDo | None = None
    lng_giao: KinhDo | None = None
    nguoi_nhan: Ten | None = None
    sdt_nhan: SoDienThoai | None = None
    han_giao: AwareDatetime | None = None

    @model_validator(mode="after")
    def _kiem(self):
        if not self.model_fields_set:
            raise ValueError("Không có trường nào để sửa")
        # Chỉ cột cho phép trống mới nhận null (xóa khung giờ lấy, tọa độ, mô tả, người liên hệ)
        cam_null = {
            "kg",
            "m3",
            "so_kien",
            "dia_chi_lay",
            "sdt_lay",
            "dia_chi_giao",
            "nguoi_nhan",
            "sdt_nhan",
            "han_giao",
        }
        if sai := sorted(k for k in self.model_fields_set & cam_null if getattr(self, k) is None):
            raise ValueError("Không được để trống: " + ", ".join(sai))
        return self


class HuyDonVao(BaseModel):
    """UC-10: hủy đơn, lý do bắt buộc (BR-34), lưu vào lịch sử trạng thái (BR-30)."""

    model_config = ConfigDict(extra="forbid")

    ly_do: ChuBatBuoc = Field(max_length=300)


class GhepLaiVao(BaseModel):
    """UC-22: ghép lại đơn THAT_BAI; nơi giữ hàng bắt buộc khi đã lấy (BR-69), được đổi hạn giao."""

    model_config = ConfigDict(extra="forbid")

    han_giao: AwareDatetime | None = None
    nut_giu_id: int | None = None
    dia_chi_giu: DiaChi | None = None
    lat_giu: ViDo | None = None
    lng_giu: KinhDo | None = None


class TraHangVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ly_do: Annotated[ChuBatBuoc, Field(max_length=300)] | None = None


class DonRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ma_don: str
    khach_hang_id: int
    ten_khach: str
    mo_ta: str | None
    kg: Decimal
    m3: Decimal
    so_kien: int
    nut_lay_id: int
    tinh_lay: str
    dia_chi_lay: str
    nguoi_lien_he_lay: str | None
    sdt_lay: str
    lay_tu: datetime | None
    lay_den: datetime | None
    nut_giao_id: int
    tinh_giao: str
    dia_chi_giao: str
    nguoi_nhan: str
    sdt_nhan: str
    han_giao: datetime
    kl_tinh_cuoc: Decimal
    cuoc_tinh: int
    trang_thai: str
    tao_luc: datetime
    trang_thai_chuyen: str | None = None  # chỉ có ở danh sách: chuyến của đơn đang ghép (BR-33, 34)


class DonCanXuLyRa(DonRa):
    """UC-22 bước 1: đơn THAT_BAI kèm thông tin chọn cách xử lý (BR-36, 37)."""

    da_lay: bool
    so_lan_giao_tb_khach: int
    nguong: int  # CFG-04
    ly_do_cuoi: str | None
    cho_chuyen_xong: bool  # còn ghép hiệu lực: chuyến chưa kết thúc, chưa xử lý được
