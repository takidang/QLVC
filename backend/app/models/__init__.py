"""Toàn bộ bảng theo ERD 0.5 (docs/so-do.md mục 5–7). Import ở đây để Alembic thấy đủ."""

from app.models.base import Base
from app.models.danh_muc import BangGia, CauHinh, KhachHang, LyDo, NguoiDung, Nut, TaiXe, Tuyen, TuyenNut, Xe
from app.models.tien import ChiPhi, ChiPhiCoDinhXe, LichSuTrangThai, NhatKyTien, PhaiThu, PhieuThu, QuyetToan, TamUng
from app.models.van_hanh import Chuyen, DonHang, Ghep, LuotQuet, SuCo, Tep

__all__ = [
    "Base",
    "BangGia",
    "CauHinh",
    "KhachHang",
    "LyDo",
    "NguoiDung",
    "Nut",
    "TaiXe",
    "Tuyen",
    "TuyenNut",
    "Xe",
    "ChiPhi",
    "ChiPhiCoDinhXe",
    "LichSuTrangThai",
    "NhatKyTien",
    "PhaiThu",
    "PhieuThu",
    "QuyetToan",
    "TamUng",
    "Chuyen",
    "DonHang",
    "Ghep",
    "LuotQuet",
    "SuCo",
    "Tep",
]
