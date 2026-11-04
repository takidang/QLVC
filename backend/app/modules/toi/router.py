from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.luu_tru import KICH_THUOC_TOI_DA
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


Km = Annotated[int, Form(ge=0, le=9_999_999)]


def _doc(anh: UploadFile) -> bytes:
    # Đọc tối đa giới hạn + 1 byte: đủ để biết ảnh quá lớn mà không nạp cả file lớn vào bộ nhớ
    return anh.file.read(KICH_THUOC_TOI_DA + 1)


@router.post("/chuyen/{chuyen_id}/bat-dau", response_model=ChuyenCuaToiChiTiet)
def bat_dau(chuyen_id: int, km_bat_dau: Km, anh_dong_ho: UploadFile, db: Db, nd: TaiXeDangNhap):
    service.bat_dau(db, nd, chuyen_id, km_bat_dau, _doc(anh_dong_ho))
    return service.chi_tiet(db, nd, chuyen_id)


@router.post("/chuyen/{chuyen_id}/ket-thuc", response_model=ChuyenCuaToiChiTiet)
def ket_thuc(chuyen_id: int, km_ket_thuc: Km, anh_dong_ho: UploadFile, db: Db, nd: TaiXeDangNhap):
    service.ket_thuc(db, nd, chuyen_id, km_ket_thuc, _doc(anh_dong_ho))
    return service.chi_tiet(db, nd, chuyen_id)
