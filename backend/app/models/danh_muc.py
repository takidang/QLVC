"""Danh mục: người dùng, tài xế, xe, nút, tuyến, khách, bảng giá, cấu hình, lý do (so-do.md mục 5, 6)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

ToaDo = Numeric(9, 6)


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten_dang_nhap: Mapped[str] = mapped_column(String(50), unique=True)
    mat_khau_bam: Mapped[str] = mapped_column(String(200))
    ho_ten: Mapped[str] = mapped_column(String(100))
    vai_tro: Mapped[str] = mapped_column(String(20))  # QUAN_LY|DIEU_PHOI|TAI_XE|KE_TOAN
    trang_thai: Mapped[str] = mapped_column(String(20), default="HOAT_DONG")  # HOAT_DONG|NGUNG
    so_lan_sai: Mapped[int] = mapped_column(default=0)  # NFR-SEC-05
    khoa_den: Mapped[datetime | None]
    anh_dai_dien: Mapped[str | None] = mapped_column(String(60))  # UC-39: tên file do máy chủ sinh

    @property
    def co_anh_dai_dien(self) -> bool:
        return bool(self.anh_dai_dien)


class TaiXe(Base):
    __tablename__ = "tai_xe"

    id: Mapped[int] = mapped_column(primary_key=True)
    nguoi_dung_id: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"), unique=True)
    so_gplx: Mapped[str] = mapped_column(String(20), unique=True)
    hang_gplx: Mapped[str] = mapped_column(String(5))  # B|C1|C (BR-14)
    han_gplx: Mapped[date]  # BR-15
    sdt: Mapped[str] = mapped_column(String(15))
    trang_thai: Mapped[str] = mapped_column(String(20), default="HOAT_DONG")


class Xe(Base):
    __tablename__ = "xe"

    id: Mapped[int] = mapped_column(primary_key=True)
    bien_so: Mapped[str] = mapped_column(String(20), unique=True)
    tai_trong_kg: Mapped[int]  # BR-01
    the_tich_m3: Mapped[Decimal] = mapped_column(Numeric(8, 2))  # BR-02
    ktt_toan_bo_kg: Mapped[int]  # BR-14
    han_dang_kiem: Mapped[date]  # BR-12
    han_bao_hiem: Mapped[date]  # BR-13
    dinh_muc_lit_100km: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    km_dong_ho: Mapped[int] = mapped_column(default=0)  # BR-70
    trang_thai: Mapped[str] = mapped_column(String(20), default="HOAT_DONG")


class Nut(Base):
    __tablename__ = "nut"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten: Mapped[str] = mapped_column(String(100))
    tinh: Mapped[str] = mapped_column(String(50))  # tra bảng giá
    loai: Mapped[str] = mapped_column(String(10))  # TINH|KHO
    lat: Mapped[Decimal | None] = mapped_column(ToaDo)
    lng: Mapped[Decimal | None] = mapped_column(ToaDo)


class Tuyen(Base):
    __tablename__ = "tuyen"

    id: Mapped[int] = mapped_column(primary_key=True)
    ma: Mapped[str] = mapped_column(String(20), unique=True)
    ten: Mapped[str] = mapped_column(String(100))
    dm_dau: Mapped[int]
    dm_cau_duong: Mapped[int]
    dm_boc_xep: Mapped[int]
    dm_luong_tai_xe: Mapped[int]  # lương khoán mỗi chuyến
    trang_thai: Mapped[str] = mapped_column(String(20), default="HOAT_DONG")


class TuyenNut(Base):
    __tablename__ = "tuyen_nut"

    tuyen_id: Mapped[int] = mapped_column(ForeignKey("tuyen.id"), primary_key=True)
    thu_tu: Mapped[int] = mapped_column(primary_key=True)
    nut_id: Mapped[int] = mapped_column(ForeignKey("nut.id"))
    phut_tu_diem_dau: Mapped[int]  # BR-63, 66
    km_tu_diem_dau: Mapped[int]
    la_diem_nghi: Mapped[bool] = mapped_column(default=False)  # BR-20


class KhachHang(Base):
    __tablename__ = "khach_hang"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten: Mapped[str] = mapped_column(String(200))
    sdt: Mapped[str] = mapped_column(String(15))
    dia_chi: Mapped[str | None] = mapped_column(String(300))
    ma_so_thue: Mapped[str | None] = mapped_column(String(20))
    trang_thai: Mapped[str] = mapped_column(String(20), default="HOAT_DONG")


class BangGia(Base):
    __tablename__ = "bang_gia"

    id: Mapped[int] = mapped_column(primary_key=True)
    tinh_lay: Mapped[str] = mapped_column(String(50))
    tinh_giao: Mapped[str] = mapped_column(String(50))
    don_gia_kg: Mapped[int]
    cuoc_toi_thieu: Mapped[int]
    hieu_luc_tu: Mapped[date]


# Một cặp tỉnh (không phân biệt hoa thường) chỉ có một mức giá mỗi ngày hiệu lực (UC-07-AC2)
Index(
    "uq_bang_gia_cap_tinh_ngay",
    func.lower(BangGia.tinh_lay),
    func.lower(BangGia.tinh_giao),
    BangGia.hieu_luc_tu,
    unique=True,
)


class CauHinh(Base):
    __tablename__ = "cau_hinh"

    ma: Mapped[str] = mapped_column(String(10), primary_key=True)  # CFG-xx
    gia_tri: Mapped[str] = mapped_column(String(50))
    nguoi_sua: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id"))
    luc: Mapped[datetime | None]


class LyDo(Base):
    __tablename__ = "ly_do"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten: Mapped[str] = mapped_column(String(100))
    ap_dung: Mapped[str] = mapped_column(String(10))  # LAY|GIAO
    phia: Mapped[str] = mapped_column(String(10))  # KHACH|SU_CO_XE (BR-37)
