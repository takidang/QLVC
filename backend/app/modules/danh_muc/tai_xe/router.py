from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.modules.danh_muc.tai_xe import service
from app.modules.danh_muc.tai_xe.schemas import TaiXeRa, TaiXeSua, TaiXeVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/tai-xe", tags=["tai-xe"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối (Quản lý kế thừa) thêm, sửa; Kế toán chỉ xem để cấp tạm ứng theo tài xế
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
SUA = Depends(can_vai_tro("DIEU_PHOI"))


@router.get("", response_model=DanhSach[TaiXeRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.post("", response_model=TaiXeRa, status_code=201, dependencies=[SUA])
def tao(vao: TaiXeVao, db: Db):
    return service.tao(db, vao)


@router.get("/{tx_id}", response_model=TaiXeRa, dependencies=[XEM])
def chi_tiet(tx_id: int, db: Db):
    return service.lay(db, tx_id)


@router.patch("/{tx_id}", response_model=TaiXeRa, dependencies=[SUA])
def sua(tx_id: int, vao: TaiXeSua, db: Db):
    return service.sua(db, tx_id, vao)
