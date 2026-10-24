"""Cước và tính hợp lệ của đơn (nghiep-vu.md mục 2.1, BR-31, 46–48). Hàm thuần, test không cần CSDL."""

import math
from datetime import datetime
from decimal import Decimal

from app.loi import LoiNghiepVu


def kl_quy_doi(m3: Decimal, he_so: int) -> Decimal:
    """BR-46: khối lượng quy đổi (kg) = m³ × CFG-01."""
    return m3 * he_so


def kl_tinh_cuoc(kg: Decimal, kl_qd: Decimal) -> Decimal:
    """BR-47: lấy số lớn hơn giữa kg thực và kg quy đổi."""
    return max(kg, kl_qd)


def tinh_cuoc(kl_tc: Decimal, don_gia_kg: int, cuoc_toi_thieu: int, buoc_lam_tron: int) -> int:
    """BR-48: max(cước tối thiểu, đơn giá × KL tính cước), làm tròn LÊN bội CFG-06."""
    tien = max(Decimal(cuoc_toi_thieu), don_gia_kg * kl_tc)
    return math.ceil(tien / buoc_lam_tron) * buoc_lam_tron


def _chu(v: str) -> str:
    return " ".join(v.split()).lower()


def kiem_br31_don_hop_le(
    dia_chi_lay: str,
    dia_chi_giao: str,
    lay_tu: datetime | None,
    lay_den: datetime | None,
    han_giao: datetime,
    bay_gio: datetime,
) -> None:
    """BR-31 phần giữa các trường (kg, m³, số kiện > 0 đã kiểm ở schema). Gom mọi vi phạm vào một lỗi."""
    vi_pham = []
    if _chu(dia_chi_lay) == _chu(dia_chi_giao):
        vi_pham.append("Địa chỉ lấy trùng địa chỉ giao")
    if han_giao <= bay_gio:
        vi_pham.append("Hạn giao phải sau thời điểm tạo đơn")
    if (lay_tu is None) != (lay_den is None):
        vi_pham.append("Khung giờ lấy phải có cả giờ bắt đầu và giờ kết thúc, hoặc để trống cả hai")
    elif lay_tu is not None:
        if lay_tu >= lay_den:
            vi_pham.append("Giờ bắt đầu lấy phải trước giờ kết thúc lấy")
        if han_giao <= lay_tu:
            vi_pham.append("Hạn giao phải sau giờ bắt đầu lấy")
    if vi_pham:
        chi_tiet = [{"ma": "BR-31", "thong_diep": v} for v in vi_pham]
        raise LoiNghiepVu("BR-31", "Đơn hàng không hợp lệ", chi_tiet=chi_tiet)
