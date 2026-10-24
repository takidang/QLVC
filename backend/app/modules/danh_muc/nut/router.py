"""Nút: tỉnh/thành hoặc kho trên tuyến (UC-05). Gọn nên schema và service để chung một file."""

from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.kieu import ChuBatBuoc
from app.loi import LoiNghiepVu
from app.models import DonHang, Nut
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/nut", tags=["nut"], dependencies=[Depends(can_vai_tro("DIEU_PHOI"))])
Db = Annotated[Session, Depends(get_db)]

Ten = Annotated[ChuBatBuoc, Field(max_length=100)]
Tinh = Annotated[ChuBatBuoc, Field(max_length=50)]
ViDo = Annotated[Decimal, Field(ge=-90, le=90, max_digits=9, decimal_places=6)]
KinhDo = Annotated[Decimal, Field(ge=-180, le=180, max_digits=9, decimal_places=6)]
Loai = Literal["TINH", "KHO"]


class NutVao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten: Ten
    tinh: Tinh  # dùng tra bảng giá (BR-48)
    loai: Loai
    lat: ViDo | None = None
    lng: KinhDo | None = None


class NutSua(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ten: Ten | None = None
    tinh: Tinh | None = None
    loai: Loai | None = None
    lat: ViDo | None = None
    lng: KinhDo | None = None

    @model_validator(mode="after")
    def khong_xoa_truong_bat_buoc(self):
        for truong in self.model_fields_set & {"ten", "tinh", "loai"}:
            if getattr(self, truong) is None:
                raise ValueError(f"{truong} không được để trống")
        return self


class NutRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ten: str
    tinh: str
    loai: str
    lat: Decimal | None
    lng: Decimal | None


def _lay(db: Session, nut_id: int) -> Nut:
    nut = db.get(Nut, nut_id, with_for_update=True)
    if nut is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy nút", 404)
    return nut


@router.get("", response_model=DanhSach[NutRa])
def danh_sach(db: Db, pt: Annotated[PhanTrang, Depends(phan_trang)], tim: str | None = None):
    loc = select(Nut)
    if tim and (tim := tim.strip()):
        loc = loc.where(or_(Nut.ten.icontains(tim, autoescape=True), Nut.tinh.icontains(tim, autoescape=True)))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    nut = db.scalars(loc.order_by(Nut.ten, Nut.id).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return {"du_lieu": nut, "tong": tong}


@router.post("", response_model=NutRa, status_code=201)
def tao(vao: NutVao, db: Db):
    nut = Nut(**vao.model_dump())
    db.add(nut)
    db.commit()
    return nut


@router.patch("/{nut_id}", response_model=NutRa)
def sua(nut_id: int, vao: NutSua, db: Db):
    nut = _lay(db, nut_id)
    thay_doi = vao.model_dump(exclude_unset=True)
    # Tỉnh dùng tra giá: nút đã có đơn thì không đổi tỉnh (quyết định UC-05 số 5)
    if "tinh" in thay_doi and thay_doi["tinh"] != nut.tinh:
        co_don = db.scalar(
            select(DonHang.id).where(or_(DonHang.nut_lay_id == nut_id, DonHang.nut_giao_id == nut_id)).limit(1)
        )
        if co_don:
            raise LoiNghiepVu("NUT_DA_CO_DON", f"Nút {nut.ten} đã có đơn, không đổi tỉnh được")
    for truong, gia_tri in thay_doi.items():
        setattr(nut, truong, gia_tri)
    db.commit()
    return nut
