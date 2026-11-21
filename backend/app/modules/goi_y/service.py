"""Gợi ý AI (KT-08): chỉ đọc, không ghi CSDL; lỗi mô hình không làm hỏng lõi (UC-30-AC4, AC5)."""

import json
import logging
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import Chuyen, TuyenNut
from app.modules.goi_y.du_doan_tre import du_doan
from app.modules.goi_y.schemas import DuDoanTreRa
from app.thoi_gian import GIO_VN

log = logging.getLogger(__name__)

# File do ml/train_du_doan_tre.py xuất (đợt 2); test monkeypatch hằng này
DUONG_DAN_MO_HINH: Path = Path(__file__).with_name("mo_hinh_tre.json")


def dac_trung_chuyen(db: Session, c: Chuyen) -> dict[str, float]:
    km = db.scalar(select(func.max(TuyenNut.km_tu_diem_dau)).where(TuyenNut.tuyen_id == c.tuyen_id))
    if km is None:
        raise ValueError(f"Tuyến {c.tuyen_id} không có nút")
    khoi_hanh = c.khoi_hanh_du_kien.astimezone(GIO_VN)  # giờ, thứ theo giờ Việt Nam
    return {
        "km": float(km),
        "thoi_gian_gio": (c.ket_thuc_du_kien - c.khoi_hanh_du_kien).total_seconds() / 3600,
        "gio_khoi_hanh": float(khoi_hanh.hour),
        "thu_trong_tuan": float(khoi_hanh.weekday()),  # Thứ Hai = 0
    }


def du_doan_tre(db: Session, chuyen_id: int) -> DuDoanTreRa:
    c = db.get(Chuyen, chuyen_id)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai == "HUY":
        return DuDoanTreRa(co_du_doan=False)
    try:
        mo_hinh = json.loads(DUONG_DAN_MO_HINH.read_text(encoding="utf-8"))
        kq = du_doan(mo_hinh, dac_trung_chuyen(db, c))
        # Kiểm luôn kiểu trả về ở đây để lỗi định dạng (nguon không phải object…) cũng thành "không có gợi ý"
        return DuDoanTreRa(co_du_doan=True, nguon=mo_hinh["nguon"], **kq)
    except Exception as e:  # mọi lỗi mô hình: không để 500 (KT-08)
        log.warning("Không dự đoán được nguy cơ trễ chuyến %s: %r", chuyen_id, e)
        return DuDoanTreRa(co_du_doan=False)
