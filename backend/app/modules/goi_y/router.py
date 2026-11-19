from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.modules.goi_y import service
from app.modules.goi_y.schemas import DuDoanTreRa

router = APIRouter(prefix="/api/chuyen", tags=["goi-y"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối xem gợi ý (Quản lý kế thừa); Kế toán, Tài xế không (UC-30-AC6)
DIEU_PHOI = Depends(can_vai_tro("DIEU_PHOI"))


@router.get("/{chuyen_id}/du-doan-tre", response_model=DuDoanTreRa, dependencies=[DIEU_PHOI])
def du_doan_tre(chuyen_id: int, db: Db):
    return service.du_doan_tre(db, chuyen_id)
