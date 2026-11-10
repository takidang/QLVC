"""Xem ảnh qua link có hạn 5 phút (NFR-SEC-04, kien-truc.md mục 7 bước 4).

UC-24 làm phần ảnh chứng từ chi phí cho Kế toán, Quản lý (quyết định 7); ảnh lượt quét, sự cố, đồng hồ để UC sau.
Link ký HMAC bằng JWT_SECRET (khóa riêng theo mục đích), nên mở ảnh không cần cookie: thẻ <img> dùng thẳng được.
"""

import hashlib
import hmac
import time
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import luu_tru
from app.auth.phu_thuoc import can_vai_tro
from app.config import get_settings
from app.db import get_db
from app.loi import LoiNghiepVu
from app.models import Tep

router = APIRouter(prefix="/api/tep", tags=["tep"])
Db = Annotated[Session, Depends(get_db)]
HAN_GIAY = 5 * 60
LOAI = {".jpg": "image/jpeg", ".png": "image/png"}  # đuôi do máy chủ đặt theo byte đầu file lúc lưu


def _ky(tep_id: int, het: int) -> str:
    khoa = hashlib.sha256(b"tep-link:" + get_settings().jwt_secret.encode()).digest()
    return hmac.new(khoa, f"{tep_id}.{het}".encode(), hashlib.sha256).hexdigest()


@router.get("/{tep_id}/link", dependencies=[Depends(can_vai_tro("KE_TOAN", "QUAN_LY"))])
def link(tep_id: int, db: Db) -> dict:
    tep = db.get(Tep, tep_id)
    if tep is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tệp", 404)
    if tep.chi_phi_id is None:
        raise LoiNghiepVu("KHONG_DU_QUYEN", "Bạn không có quyền xem tệp này", 403)
    het = int(time.time()) + HAN_GIAY
    return {"url": f"/api/tep/{tep_id}/anh?het={het}&ky={_ky(tep_id, het)}", "het_han": het}


@router.get("/{tep_id}/anh")
def anh(tep_id: int, het: int, ky: str, db: Db) -> FileResponse:
    if het < time.time() or not hmac.compare_digest(ky.encode(), _ky(tep_id, het).encode()):
        raise LoiNghiepVu("KHONG_DU_QUYEN", "Link xem ảnh đã hết hạn hoặc không hợp lệ", 403)
    tep = db.get(Tep, tep_id)
    duong_dan = luu_tru.THU_MUC / tep.duong_dan if tep else None
    if duong_dan is None or not duong_dan.is_file():
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tệp", 404)
    return FileResponse(
        duong_dan,
        media_type=LOAI.get(duong_dan.suffix, "application/octet-stream"),
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, max-age=300"},
    )
