from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.modules.tong_quan import service
from app.thoi_gian import hom_nay_vn

router = APIRouter(prefix="/api/tong-quan", tags=["tong-quan"])


def _chi_ngay(request: Request) -> None:
    la = set(request.query_params.keys()) - {"ngay"}
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {', '.join(sorted(la))}", 400)


# Quản lý, Điều phối, Kế toán xem; Tài xế không (BR-57)
@router.get(
    "",
    dependencies=[Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN")), Depends(_chi_ngay)],
)
def tong_quan(db: Annotated[Session, Depends(get_db)], ngay: date | None = None):
    return service.tong_quan(db, ngay or hom_nay_vn())
