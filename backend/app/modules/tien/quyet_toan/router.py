from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.tien.quyet_toan import service
from app.modules.tien.quyet_toan.schemas import (
    BangQuyetToan,
    DuyetVao,
    KhoanChiRa,
    QuyetToanRa,
    QuyetToanVao,
    TuChoiVao,
)

router = APIRouter(tags=["quyet-toan"])
Db = Annotated[Session, Depends(get_db)]
# Kế toán ghi; Quản lý chỉ xem (nghiep-vu.md mục 8, quyết định 8). Điều phối, Tài xế không thấy (BR-57)
KeToan = Annotated[NguoiDung, Depends(can_vai_tro("KE_TOAN"))]
XEM = Depends(can_vai_tro("KE_TOAN", "QUAN_LY"))


@router.post("/api/chi-phi/{chi_phi_id}/duyet", response_model=KhoanChiRa)
def duyet(chi_phi_id: int, vao: DuyetVao, db: Db, nd: KeToan):
    return service.duyet(db, chi_phi_id, vao.so_tien_duyet, vao.ly_do, nd)


@router.post("/api/chi-phi/{chi_phi_id}/tu-choi", response_model=KhoanChiRa)
def tu_choi(chi_phi_id: int, vao: TuChoiVao, db: Db, nd: KeToan):
    return service.tu_choi(db, chi_phi_id, vao.ly_do, nd)


@router.get("/api/chuyen/{chuyen_id}/quyet-toan", response_model=BangQuyetToan, dependencies=[XEM])
def bang(chuyen_id: int, db: Db):
    return service.bang(db, chuyen_id)


@router.post("/api/chuyen/{chuyen_id}/quyet-toan", response_model=QuyetToanRa)
def quyet_toan(chuyen_id: int, vao: QuyetToanVao, db: Db, nd: KeToan):
    return service.quyet_toan(db, chuyen_id, vao, nd)
