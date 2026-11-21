from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import LyDo

router = APIRouter(prefix="/api/danh-muc/ly-do", tags=["ly-do"])


class LyDoRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ten: str
    ap_dung: str
    phia: str  # KHACH|SU_CO_XE (BR-37)


# Danh mục chỉ đọc (nạp bằng migration), không có nghiệp vụ nên không tách service
@router.get("", response_model=list[LyDoRa], dependencies=[Depends(can_vai_tro("DIEU_PHOI", "TAI_XE"))])
def danh_sach(db: Annotated[Session, Depends(get_db)], ap_dung: Literal["LAY", "GIAO"] | None = None):
    loc = select(LyDo).order_by(LyDo.id)
    return db.scalars(loc.where(LyDo.ap_dung == ap_dung) if ap_dung else loc).all()
