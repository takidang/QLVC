from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.danh_muc.cau_hinh import service

router = APIRouter(prefix="/api/cau-hinh", tags=["cau-hinh"])
Db = Annotated[Session, Depends(get_db)]
QUAN_LY = can_vai_tro("QUAN_LY")


class ThamSoRa(BaseModel):
    ma: str
    ten: str
    don_vi: str
    gia_tri: str
    nguoi_sua: str | None
    luc: datetime | None


class ThamSoVao(BaseModel):
    gia_tri: str = Field(min_length=1, max_length=50)


@router.get("", response_model=list[ThamSoRa], dependencies=[Depends(QUAN_LY)])
def danh_sach(db: Db):
    return service.danh_sach(db)


@router.put("/{ma}", response_model=list[ThamSoRa])
def sua(ma: str, vao: ThamSoVao, db: Db, nd: Annotated[NguoiDung, Depends(QUAN_LY)]):
    service.sua(db, ma, vao.gia_tri, nd)
    return service.danh_sach(db)
