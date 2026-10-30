from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.chuyen import service
from app.modules.chuyen.schemas import (
    ChuyenChiTiet,
    ChuyenRa,
    ChuyenVao,
    GhepVao,
    TaiXeKhaDung,
    TrangThaiChuyen,
    XeKhaDung,
)
from app.modules.don.schemas import DonRa
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/chuyen", tags=["chuyen"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối (Quản lý kế thừa) lập chuyến; Kế toán chỉ xem chuyến
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
DIEU_PHOI = can_vai_tro("DIEU_PHOI")


# Đường dẫn cố định đặt trước đường dẫn có {id} (api.md mục 1)
@router.get("/xe-kha-dung", response_model=list[XeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def xe_kha_dung(tuyen_id: int, khoi_hanh: AwareDatetime, db: Db):
    return service.xe_kha_dung(db, tuyen_id, khoi_hanh)


@router.get("/tai-xe-kha-dung", response_model=list[TaiXeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def tai_xe_kha_dung(tuyen_id: int, khoi_hanh: AwareDatetime, db: Db, xe_id: int | None = None):
    return service.tai_xe_kha_dung(db, tuyen_id, khoi_hanh, xe_id)


@router.post("", response_model=ChuyenRa, status_code=201)
def tao(vao: ChuyenVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.lay(db, service.tao(db, vao, nd))


@router.get("", response_model=DanhSach[ChuyenRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: TrangThaiChuyen | None = None,
    ngay: date | None = None,
    tuyen_id: int | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, ngay, tuyen_id)
    return {"du_lieu": du_lieu, "tong": tong}


@router.get("/{chuyen_id}", response_model=ChuyenChiTiet, dependencies=[XEM])
def chi_tiet(chuyen_id: int, db: Db):
    return service.chi_tiet(db, chuyen_id)


@router.get("/{chuyen_id}/don-phu-hop", response_model=list[DonRa], dependencies=[Depends(DIEU_PHOI)])
def don_phu_hop(chuyen_id: int, db: Db):
    return service.don_phu_hop(db, chuyen_id)


@router.post("/{chuyen_id}/ghep", response_model=ChuyenChiTiet)
def ghep(chuyen_id: int, vao: GhepVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.ghep(db, chuyen_id, vao.don_ids, nd)


@router.post("/{chuyen_id}/go", response_model=ChuyenChiTiet)
def go(chuyen_id: int, vao: GhepVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.go(db, chuyen_id, vao.don_ids, nd)
