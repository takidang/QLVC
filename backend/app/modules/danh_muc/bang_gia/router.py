from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.modules.danh_muc.bang_gia import service
from app.modules.danh_muc.bang_gia.schemas import BangGiaRa, BangGiaSua, BangGiaVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/bang-gia", tags=["bang-gia"], dependencies=[Depends(can_vai_tro("QUAN_LY"))])
Db = Annotated[Session, Depends(get_db)]


def _ra(bg, dang_ap_dung: set[int]) -> BangGiaRa:
    return BangGiaRa.model_validate(bg).model_copy(update={"dang_ap_dung": bg.id in dang_ap_dung})


# Đường dẫn cố định đặt trước đường dẫn có {id} (api.md mục 1)
@router.get("/ten-tinh", response_model=list[str])
def ten_tinh(db: Db):
    return service.ten_tinh_da_dung(db)


@router.get("", response_model=DanhSach[BangGiaRa])
def danh_sach(db: Db, pt: Annotated[PhanTrang, Depends(phan_trang)], tim: str | None = None):
    du_lieu, tong = service.danh_sach(db, pt, tim)
    ap_dung = service.id_dang_ap_dung(db)
    return {"du_lieu": [_ra(bg, ap_dung) for bg in du_lieu], "tong": tong}


@router.post("", response_model=BangGiaRa, status_code=201)
def tao(vao: BangGiaVao, db: Db):
    return _ra(service.tao(db, vao), service.id_dang_ap_dung(db))


@router.patch("/{bg_id}", response_model=BangGiaRa)
def sua(bg_id: int, vao: BangGiaSua, db: Db):
    return _ra(service.sua(db, bg_id, vao), service.id_dang_ap_dung(db))
