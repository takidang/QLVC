from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.tien.cong_no import service
from app.modules.tien.cong_no.schemas import DanhSachPhaiThu, DaThuVao, NoTheoKhach, PhieuThuRa, TrangThaiTT
from app.phan_trang import PhanTrang, phan_trang

router = APIRouter(prefix="/api/phai-thu", tags=["cong-no"])
Db = Annotated[Session, Depends(get_db)]
# Kế toán ghi; Quản lý chỉ xem (nghiep-vu.md mục 6). Điều phối, Tài xế không thấy (BR-57)
XEM = Depends(can_vai_tro("KE_TOAN", "QUAN_LY"))
KeToan = Annotated[NguoiDung, Depends(can_vai_tro("KE_TOAN"))]


@router.get("", response_model=DanhSachPhaiThu, dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai_tt: TrangThaiTT | None = None,
    khach_hang_id: int | None = None,
):
    du_lieu, tong, tong_tien = service.danh_sach(db, pt, trang_thai_tt, khach_hang_id)
    return {"du_lieu": du_lieu, "tong": tong, "tong_tien": tong_tien}


@router.get("/theo-khach", response_model=list[NoTheoKhach], dependencies=[XEM])
def theo_khach(db: Db):
    return service.theo_khach(db)


@router.post("/da-thu", response_model=PhieuThuRa)
def da_thu(vao: DaThuVao, db: Db, nd: KeToan):
    return service.da_thu(db, vao.phai_thu_ids, vao.ngay, nd)
