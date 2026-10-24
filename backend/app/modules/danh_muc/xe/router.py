from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.danh_muc.xe import service
from app.modules.danh_muc.xe.schemas import ChiPhiCoDinhRa, ChiPhiCoDinhVao, XeRa, XeSua, XeVao
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/xe", tags=["xe"])
Db = Annotated[Session, Depends(get_db)]
Thang = Annotated[str, Path(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]  # YYYY-MM

# Điều phối (Quản lý kế thừa) thêm, sửa; Kế toán chỉ xem để chọn xe nhập chi phí cố định
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
SUA = Depends(can_vai_tro("DIEU_PHOI"))
KE_TOAN = can_vai_tro("KE_TOAN")


@router.get("", response_model=DanhSach[XeRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: Literal["HOAT_DONG", "NGUNG"] | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.post("", response_model=XeRa, status_code=201, dependencies=[SUA])
def tao(vao: XeVao, db: Db):
    return service.tao(db, vao)


@router.get("/{xe_id}", response_model=XeRa, dependencies=[XEM])
def chi_tiet(xe_id: int, db: Db):
    return service.lay(db, xe_id)


@router.patch("/{xe_id}", response_model=XeRa, dependencies=[SUA])
def sua(xe_id: int, vao: XeSua, db: Db):
    return service.sua(db, xe_id, vao)


@router.get("/{xe_id}/chi-phi-co-dinh/{thang}", response_model=ChiPhiCoDinhRa, dependencies=[Depends(KE_TOAN)])
def xem_chi_phi_co_dinh(xe_id: int, thang: Thang, db: Db):
    return {"xe_id": xe_id, "thang": thang, "so_tien": service.lay_chi_phi_co_dinh(db, xe_id, thang)}


@router.put("/{xe_id}/chi-phi-co-dinh/{thang}", response_model=ChiPhiCoDinhRa)
def dat_chi_phi_co_dinh(
    xe_id: int, thang: Thang, vao: ChiPhiCoDinhVao, db: Db, nd: Annotated[NguoiDung, Depends(KE_TOAN)]
):
    return {"xe_id": xe_id, "thang": thang, "so_tien": service.dat_chi_phi_co_dinh(db, xe_id, thang, vao.so_tien, nd)}
