from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.toi import service
from app.modules.toi.schemas import ChuyenCuaToi, ChuyenCuaToiChiTiet
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/toi", tags=["toi"])
Db = Annotated[Session, Depends(get_db)]
TaiXeDangNhap = Annotated[NguoiDung, Depends(can_vai_tro("TAI_XE"))]  # chỉ tài xế (BR-57)


@router.get("/chuyen", response_model=DanhSach[ChuyenCuaToi])
def danh_sach(
    db: Db,
    nd: TaiXeDangNhap,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    nhom: Literal["can_lam", "da_xong"] = "can_lam",
):
    du_lieu, tong = service.danh_sach(db, nd, nhom, pt)
    return {"du_lieu": du_lieu, "tong": tong}


@router.get("/chuyen/{chuyen_id}", response_model=ChuyenCuaToiChiTiet)
def chi_tiet(chuyen_id: int, db: Db, nd: TaiXeDangNhap):
    return service.chi_tiet(db, nd, chuyen_id)
