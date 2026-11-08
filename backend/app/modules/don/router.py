from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.don import service, sua_huy
from app.modules.don.schemas import DonRa, DonSua, DonVao, HuyDonVao, TinhCuocRa, TinhCuocVao, TrangThaiDon
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/don", tags=["don"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối (Quản lý kế thừa) tạo đơn; Kế toán chỉ xem
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
DIEU_PHOI = can_vai_tro("DIEU_PHOI")


# Đường dẫn cố định đặt trước đường dẫn có {id} (api.md mục 1)
@router.post("/tinh-cuoc", response_model=TinhCuocRa, dependencies=[Depends(DIEU_PHOI)])
def tinh_cuoc(vao: TinhCuocVao, db: Db):
    return asdict(service.bao_gia(db, vao.nut_lay_id, vao.nut_giao_id, vao.kg, vao.m3))


@router.post("", response_model=DonRa, status_code=201)
def tao(vao: DonVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.lay(db, service.tao(db, vao, nd).id)


@router.get("", response_model=DanhSach[DonRa], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: TrangThaiDon | None = None,
    khach_hang_id: int | None = None,
    tim: str | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, khach_hang_id, tim)
    return {"du_lieu": du_lieu, "tong": tong}


@router.get("/{don_id}", response_model=DonRa, dependencies=[XEM])
def chi_tiet(don_id: int, db: Db):
    return service.lay(db, don_id)


@router.patch("/{don_id}", response_model=DonRa)
def sua(don_id: int, vao: DonSua, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return sua_huy.sua(db, don_id, vao, nd)


@router.post("/{don_id}/huy", response_model=DonRa)
def huy(don_id: int, vao: HuyDonVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return sua_huy.huy(db, don_id, vao.ly_do, nd)
