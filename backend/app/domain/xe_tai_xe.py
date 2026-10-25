"""Quy tắc xe, tài xế (nghiep-vu.md nhóm B). Hàm thuần: không chạm CSDL, test được không cần DB."""

from app.loi import LoiNghiepVu


def kiem_br14_khoi_luong_toan_bo(tai_trong_kg: int, ktt_toan_bo_kg: int) -> None:
    """Khối lượng toàn bộ theo thiết kế gồm cả xe và hàng nên không nhỏ hơn tải trọng (chốt 24/10, UC-03-AC3).

    Nhập nhầm hai số này làm sai kiểm hạng bằng lái ở BR-14.
    """
    if ktt_toan_bo_kg < tai_trong_kg:
        raise LoiNghiepVu(
            "BR-14",
            f"Khối lượng toàn bộ ({ktt_toan_bo_kg} kg) không được nhỏ hơn tải trọng ({tai_trong_kg} kg)",
        )


# Thứ bậc hạng GPLX: hạng cao lái được xe của hạng thấp (C ⊇ C1 ⊇ B)
_BAC_GPLX = {"B": 1, "C1": 2, "C": 3}


def hang_gplx_toi_thieu(ktt_toan_bo_kg: int) -> str:
    """Hạng GPLX thấp nhất được lái xe có khối lượng toàn bộ theo thiết kế này (BR-14, Điều 57 Luật TTATGT 2024)."""
    if ktt_toan_bo_kg <= 3500:
        return "B"
    if ktt_toan_bo_kg <= 7500:
        return "C1"
    return "C"


def kiem_br14_hang_gplx(hang_gplx: str, ktt_toan_bo_kg: int) -> None:
    """Tài xế hạng `hang_gplx` có lái được xe này không (UC-04-AC4; UC-11, 12 gọi khi lập/đổi chuyến)."""
    can = hang_gplx_toi_thieu(ktt_toan_bo_kg)
    if _BAC_GPLX[hang_gplx] < _BAC_GPLX[can]:
        raise LoiNghiepVu(
            "BR-14",
            f"Xe khối lượng toàn bộ {ktt_toan_bo_kg} kg cần GPLX hạng {can} trở lên, tài xế có hạng {hang_gplx}",
        )
