"""Tham số cấu hình CFG-xx (nghiep-vu.md mục 3): tên, đơn vị, giá trị mặc định, cách kiểm. Hàm thuần."""

import re
from collections.abc import Callable
from dataclasses import dataclass


def _so_nguyen(nho_nhat: int) -> Callable[[str], str]:
    def kiem(v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"\d+", v) or int(v) < nho_nhat:
            raise ValueError(f"Phải là số nguyên ≥ {nho_nhat}")
        return str(int(v))

    return kiem


def _gio_lai(v: str) -> str:
    """CFG-07: giờ lái tối đa ngày/tuần/liên tục, ví dụ 10/48/4."""
    phan = [p.strip() for p in v.split("/")]
    if len(phan) != 3 or not all(re.fullmatch(r"\d+", p) and int(p) > 0 for p in phan):
        raise ValueError("Phải có dạng ngày/tuần/liên tục, ba số nguyên > 0, ví dụ 10/48/4")
    return "/".join(str(int(p)) for p in phan)


@dataclass(frozen=True)
class ThamSo:
    ten: str
    don_vi: str
    mac_dinh: str
    kiem: Callable[[str], str]


# Giữ khớp với giá trị nạp trong migration 177fdcb334df (migration không import code app)
THAM_SO: dict[str, ThamSo] = {
    "CFG-01": ThamSo("Hệ số quy đổi thể tích", "kg/m³", "333", _so_nguyen(1)),
    "CFG-02": ThamSo("Cảnh báo giấy tờ sắp hết hạn trước", "ngày", "30", _so_nguyen(0)),
    "CFG-04": ThamSo("Số lần giao thất bại (phía khách) trước khi chỉ còn trả hàng", "lần", "3", _so_nguyen(1)),
    "CFG-05": ThamSo("Thời gian đệm sau chuyến", "phút", "60", _so_nguyen(0)),
    "CFG-06": ThamSo("Làm tròn cước lên bội số", "đồng", "1000", _so_nguyen(1)),
    "CFG-07": ThamSo("Giờ lái tối đa ngày/tuần/liên tục", "giờ", "10/48/4", _gio_lai),
    "CFG-08": ThamSo("Phút dừng mỗi điểm", "phút", "20", _so_nguyen(0)),
    "CFG-09": ThamSo("Ngưỡng trễ so với ETA để gắn cờ trễ", "phút", "15", _so_nguyen(0)),
    "CFG-10": ThamSo("Cảnh báo đơn chờ ghép khi còn dưới (tới hạn giao)", "giờ", "24", _so_nguyen(0)),
}
