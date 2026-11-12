from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.bao_mat import THOI_HAN_TOKEN, tao_token
from app.auth.phu_thuoc import nguoi_dung_hien_tai
from app.auth.schemas import DangNhapVao, DoiMatKhauVao, NguoiDungRa
from app.db import get_db
from app.models import NguoiDung

router = APIRouter(prefix="/api/auth", tags=["auth"])
COOKIE = {"key": "access_token", "httponly": True, "secure": True, "samesite": "strict", "path": "/"}


@router.post("/dang-nhap", response_model=NguoiDungRa)
def dang_nhap(vao: DangNhapVao, response: Response, db: Annotated[Session, Depends(get_db)]):
    bay_gio = datetime.now(UTC)
    nd = service.dang_nhap(db, vao.ten_dang_nhap, vao.mat_khau, bay_gio)
    response.set_cookie(value=tao_token(nd.id, bay_gio), max_age=int(THOI_HAN_TOKEN.total_seconds()), **COOKIE)
    return nd


# Không bắt buộc đăng nhập: token hết hạn vẫn đăng xuất được
@router.post("/dang-xuat", status_code=204)
def dang_xuat(response: Response):
    response.delete_cookie(**COOKIE)


@router.get("/toi", response_model=NguoiDungRa)
def toi(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)]):
    return nd


# UC-35: mọi vai trò đổi mật khẩu của chính mình
@router.put("/mat-khau", status_code=204)
def doi_mat_khau(
    vao: DoiMatKhauVao, nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)], db: Annotated[Session, Depends(get_db)]
):
    service.doi_mat_khau(db, nd.id, vao.mat_khau_cu, vao.mat_khau_moi, datetime.now(UTC))
