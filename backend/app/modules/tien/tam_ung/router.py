from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.tien.tam_ung import service
from app.modules.tien.tam_ung.schemas import TamUngChuyen, TamUngRa, TamUngSua, TamUngVao, ThuHoiVao, TrangThaiTamUng
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(tags=["tam-ung"])
Db = Annotated[Session, Depends(get_db)]
# Kế toán ghi; Quản lý chỉ xem (security-rules: dữ liệu tiền). Điều phối, Tài xế không thấy (BR-57)
KeToan = Annotated[NguoiDung, Depends(can_vai_tro("KE_TOAN"))]
XEM = Depends(can_vai_tro("KE_TOAN", "QUAN_LY"))


@router.get("/api/chuyen/{chuyen_id}/tam-ung", response_model=TamUngChuyen, dependencies=[XEM])
def theo_chuyen(chuyen_id: int, db: Db):
    return service.theo_chuyen(db, chuyen_id)


@router.post("/api/chuyen/{chuyen_id}/tam-ung", response_model=TamUngRa, status_code=201)
def cap(chuyen_id: int, vao: TamUngVao, db: Db, nd: KeToan):
    return service.cap(db, chuyen_id, vao.so_tien, vao.hinh_thuc, nd)


@router.get("/api/tam-ung", response_model=DanhSach[TamUngRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: TrangThaiTamUng | None = None,
    chuyen_id: int | None = None,
    tai_xe_id: int | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, chuyen_id, tai_xe_id)
    return {"du_lieu": du_lieu, "tong": tong}


@router.patch("/api/tam-ung/{tam_ung_id}", response_model=TamUngRa)
def sua(tam_ung_id: int, vao: TamUngSua, db: Db, nd: KeToan):
    return service.sua(db, tam_ung_id, vao.so_tien, vao.hinh_thuc, vao.ly_do, nd)


@router.post("/api/tam-ung/{tam_ung_id}/thu-hoi", response_model=TamUngRa)
def thu_hoi(tam_ung_id: int, db: Db, nd: KeToan, vao: Annotated[ThuHoiVao | None, Body()] = None):
    return service.thu_hoi(db, tam_ung_id, vao.ly_do if vao else None, nd)
