"""Tiền và nhật ký: chi phí, tạm ứng, quyết toán, công nợ, lịch sử (so-do.md mục 7)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, luc_tao


class ChiPhi(Base):
    __tablename__ = "chi_phi"

    id: Mapped[int] = mapped_column(primary_key=True)
    chuyen_id: Mapped[int] = mapped_column(ForeignKey("chuyen.id"))
    loai: Mapped[str] = mapped_column(String(20))  # DAU|CAU_DUONG|BOC_XEP|PHAT_SINH
    so_tien_khai: Mapped[int]
    so_tien_duyet: Mapped[int | None]
    so_lit: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))  # chỉ loại DAU (BR-54)
    ghi_chu: Mapped[str] = mapped_column(String(500))
    trang_thai: Mapped[str] = mapped_column(String(20), default="CHO_DUYET")  # CHO_DUYET|DA_DUYET|TU_CHOI
    nguoi_tao: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    nguoi_duyet: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id"))
    tao_luc: Mapped[datetime] = luc_tao()


class TamUng(Base):
    __tablename__ = "tam_ung"

    id: Mapped[int] = mapped_column(primary_key=True)
    chuyen_id: Mapped[int] = mapped_column(ForeignKey("chuyen.id"))
    tai_xe_id: Mapped[int] = mapped_column(ForeignKey("tai_xe.id"))
    so_tien: Mapped[int]
    hinh_thuc: Mapped[str] = mapped_column(String(20))  # TIEN_MAT|CHUYEN_KHOAN
    trang_thai: Mapped[str] = mapped_column(String(20), default="HIEU_LUC")  # HIEU_LUC|DA_THU_HOI (BR-53)
    nguoi_tao: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    tao_luc: Mapped[datetime] = luc_tao()


class QuyetToan(Base):
    __tablename__ = "quyet_toan"

    id: Mapped[int] = mapped_column(primary_key=True)
    chuyen_id: Mapped[int] = mapped_column(ForeignKey("chuyen.id"), unique=True)  # khóa sổ (BR-29)
    doanh_thu: Mapped[int]  # BR-50
    tong_chi: Mapped[int]
    luong_tai_xe: Mapped[int]
    ly_do_luong_tay: Mapped[str | None] = mapped_column(String(300))  # BR-68
    lai: Mapped[int]  # BR-51
    chenh_lech_tam_ung: Mapped[int]  # BR-55
    xu_ly_chenh_lech: Mapped[str] = mapped_column(String(20))  # TAI_XE_DA_NOP|CONG_TY_DA_TRA|KHONG_CHENH
    hinh_thuc: Mapped[str | None] = mapped_column(String(20))
    luc_xu_ly: Mapped[datetime | None]
    ke_toan_id: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    luc: Mapped[datetime] = luc_tao()


class PhieuThu(Base):
    __tablename__ = "phieu_thu"

    id: Mapped[int] = mapped_column(primary_key=True)
    khach_hang_id: Mapped[int] = mapped_column(ForeignKey("khach_hang.id"))
    tong_tien: Mapped[int]
    ngay: Mapped[date]
    nguoi_tao: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))


class PhaiThu(Base):
    __tablename__ = "phai_thu"

    id: Mapped[int] = mapped_column(primary_key=True)
    don_hang_id: Mapped[int] = mapped_column(ForeignKey("don_hang.id"), unique=True)
    so_tien: Mapped[int]
    trang_thai_tt: Mapped[str] = mapped_column(String(20), default="CHUA_THU")  # CHUA_THU|DA_THU (BR-56)
    phieu_thu_id: Mapped[int | None] = mapped_column(ForeignKey("phieu_thu.id"))


class ChiPhiCoDinhXe(Base):
    __tablename__ = "chi_phi_co_dinh_xe"
    __table_args__ = (UniqueConstraint("xe_id", "thang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    xe_id: Mapped[int] = mapped_column(ForeignKey("xe.id"))
    thang: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    so_tien: Mapped[int]


class NhatKyTien(Base):
    """Chỉ thêm, không sửa xóa (BR-62)."""

    __tablename__ = "nhat_ky_tien"

    id: Mapped[int] = mapped_column(primary_key=True)
    bang: Mapped[str] = mapped_column(String(30))
    ban_ghi_id: Mapped[int]
    hanh_dong: Mapped[str] = mapped_column(String(20))  # TAO|SUA|DUYET|TU_CHOI|THU_HOI
    gia_tri_cu: Mapped[str | None] = mapped_column(String(500))
    gia_tri_moi: Mapped[str | None] = mapped_column(String(500))
    ly_do: Mapped[str | None] = mapped_column(String(300))
    nguoi: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    luc: Mapped[datetime] = luc_tao()


class LichSuTrangThai(Base):
    """Chỉ thêm, không sửa xóa (BR-30)."""

    __tablename__ = "lich_su_trang_thai"

    id: Mapped[int] = mapped_column(primary_key=True)
    doi_tuong: Mapped[str] = mapped_column(String(10))  # CHUYEN|DON
    doi_tuong_id: Mapped[int]
    tu: Mapped[str | None] = mapped_column(String(20))
    sang: Mapped[str] = mapped_column(String(20))
    ly_do: Mapped[str | None] = mapped_column(String(300))
    nguoi: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    luc: Mapped[datetime] = luc_tao()
