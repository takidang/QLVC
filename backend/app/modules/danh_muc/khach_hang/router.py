from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.modules.danh_muc.khach_hang import service
from app.modules.danh_muc.khach_hang.schemas import KhachHangRa, KhachHangSua, KhachHangVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/khach-hang", tags=["khach-hang"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối (Quản lý kế thừa) thêm, sửa; Kế toán chỉ xem để theo dõi công nợ (UC-25)
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
SUA = Depends(can_vai_tro("DIEU_PHOI"))


@router.get("", response_model=DanhSach[KhachHangRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.post("", response_model=KhachHangRa, status_code=201, dependencies=[SUA])
def tao(vao: KhachHangVao, db: Db):
    return service.tao(db, vao)


@router.get("/{kh_id}", response_model=KhachHangRa, dependencies=[XEM])
def chi_tiet(kh_id: int, db: Db):
    return service.lay(db, kh_id)


@router.patch("/{kh_id}", response_model=KhachHangRa, dependencies=[SUA])
def sua(kh_id: int, vao: KhachHangSua, db: Db):
    return service.sua(db, kh_id, vao)
