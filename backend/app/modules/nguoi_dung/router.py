from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.nguoi_dung import service
from app.modules.nguoi_dung.schemas import MatKhauVao, NguoiDungRa, NguoiDungSua, NguoiDungVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/nguoi-dung", tags=["nguoi-dung"])
Db = Annotated[Session, Depends(get_db)]
QuanLy = Annotated[NguoiDung, Depends(can_vai_tro("QUAN_LY"))]  # chỉ Quản lý (BR-57)


@router.get("", response_model=DanhSach[NguoiDungRa])
def danh_sach(
    db: Db,
    _: QuanLy,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    vai_tro: Literal["QUAN_LY", "DIEU_PHOI", "TAI_XE", "KE_TOAN"] | None = None,
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, vai_tro, trang_thai, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.post("", response_model=NguoiDungRa, status_code=201)
def tao(vao: NguoiDungVao, db: Db, _: QuanLy):
    return service.tao(db, vao)


@router.patch("/{nd_id}", response_model=NguoiDungRa)
def sua(nd_id: int, vao: NguoiDungSua, db: Db, ql: QuanLy):
    return service.sua(db, nd_id, vao, ql)


@router.put("/{nd_id}/mat-khau", status_code=204)
def dat_lai_mat_khau(nd_id: int, vao: MatKhauVao, db: Db, _: QuanLy):
    service.dat_lai_mat_khau(db, nd_id, vao.mat_khau)
