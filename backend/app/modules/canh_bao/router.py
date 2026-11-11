from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.modules.canh_bao import service

router = APIRouter(prefix="/api/canh-bao", tags=["canh-bao"])


def _khong_tham_so(request: Request) -> None:
    if request.query_params:
        la = ", ".join(sorted(request.query_params.keys()))
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {la}", 400)


# Điều phối (Quản lý kế thừa); Kế toán, Tài xế không thấy (BR-57)
@router.get("", dependencies=[Depends(can_vai_tro("DIEU_PHOI")), Depends(_khong_tham_so)])
def bang(db: Annotated[Session, Depends(get_db)]):
    return service.bang(db)
