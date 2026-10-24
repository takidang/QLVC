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
