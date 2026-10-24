from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.modules.danh_muc.tuyen import service
from app.modules.danh_muc.tuyen.schemas import TuyenRa, TuyenSua, TuyenVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/tuyen", tags=["tuyen"], dependencies=[Depends(can_vai_tro("DIEU_PHOI"))])
Db = Annotated[Session, Depends(get_db)]


@router.get("", response_model=DanhSach[TuyenRa])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.post("", response_model=TuyenRa, status_code=201)
def tao(vao: TuyenVao, db: Db):
    return service.lay(db, service.tao(db, vao))


@router.get("/{tuyen_id}", response_model=TuyenRa)
def chi_tiet(tuyen_id: int, db: Db):
    return service.lay(db, tuyen_id)


@router.patch("/{tuyen_id}", response_model=TuyenRa)
def sua(tuyen_id: int, vao: TuyenSua, db: Db):
    service.sua(db, tuyen_id, vao)
    return service.lay(db, tuyen_id)
