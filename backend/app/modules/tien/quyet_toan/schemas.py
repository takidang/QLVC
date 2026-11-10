from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.kieu import ChuBatBuoc

XuLyChenhLech = Literal["TAI_XE_DA_NOP", "CONG_TY_DA_TRA", "KHONG_CHENH"]  # BR-55
HinhThuc = Literal["TIEN_MAT", "CHUYEN_KHOAN"]
SoTien = Annotated[int, Field(ge=1, le=1_000_000_000_000, strict=True)]
LuongTay = Annotated[int, Field(ge=0, le=1_000_000_000_000, strict=True)]  # 0 được: xe hỏng đầu chuyến (quyết định 5)
LyDo = Annotated[ChuBatBuoc, Field(max_length=300)]


class DuyetVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    so_tien_duyet: SoTien
    ly_do: LyDo | None = None  # bắt buộc khi khác số khai (kiểm ở service → 422 BR-55)


class TuChoiVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ly_do: LyDo


class QuyetToanVao(BaseModel):
    """api.md 3.3: số tiền do máy chủ tính; Kế toán chỉ gửi phần ghi tay. Thiếu điều kiện → 422 ở service."""

    model_config = ConfigDict(extra="forbid")

    xu_ly_chenh_lech: XuLyChenhLech | None = None
    hinh_thuc: HinhThuc | None = None
    luc_xu_ly: AwareDatetime | None = None
    luong_tay: LuongTay | None = None
    ly_do_luong_tay: LyDo | None = None


class KhoanChiRa(BaseModel):
    id: int
    loai: str
    so_tien_khai: int
    so_tien_duyet: int | None
    so_lit: Decimal | None
    ghi_chu: str
    trang_thai: str
    anh: list[int]  # id tệp, xem qua GET /api/tep/{id}/link
    tao_luc: datetime


class DonRa(BaseModel):
    id: int
    ma_don: str
    ten_khach: str
    cuoc: int


class LoaiChiRa(BaseModel):
    loai: str
    dinh_muc: int
    thuc_te: int  # đã duyệt
    chenh_lech: int  # thực tế − định mức; dương là vượt


class LyDoLech(BaseModel):
    mo_ta: str
    so_tien: int  # ảnh hưởng tới lãi so với dự kiến: âm làm giảm lãi


class BangQuyetToan(BaseModel):
    chuyen_id: int
    ma_chuyen: str
    trang_thai: str
    bien_so: str
    ten_tai_xe: str
    ten_tuyen: str
    ket_thuc_bat_thuong: bool
    ly_do_ket_thuc: str | None
    don_giao: list[DonRa]
    don_that_bai: list[DonRa]
    doanh_thu: int
    chi_theo_loai: list[LoaiChiRa]
    dinh_muc: int
    tong_chi: int
    km: int | None
    dau_tham_khao_lit: Decimal | None
    dau_thuc_te_lit: Decimal
    khoan: list[KhoanChiRa]
    so_cho_duyet: int
    luong_chot: int
    luong_tai_xe: int
    can_luong_tay: bool
    ly_do_luong_tay: str | None
    tong_tam_ung_hieu_luc: int
    chenh_lech_tam_ung: int
    xu_ly_goi_y: XuLyChenhLech
    lai: int
    lai_du_kien: int
    ly_do_lech: list[LyDoLech]
    xu_ly_chenh_lech: XuLyChenhLech | None  # có khi đã quyết toán
    hinh_thuc: HinhThuc | None
    luc_xu_ly: datetime | None
    luc_quyet_toan: datetime | None


class QuyetToanRa(BaseModel):
    chuyen_id: int
    doanh_thu: int
    tong_chi: int
    luong_tai_xe: int
    lai: int
    tong_tam_ung_hieu_luc: int
    chenh_lech_tam_ung: int
    xu_ly_chenh_lech: XuLyChenhLech
