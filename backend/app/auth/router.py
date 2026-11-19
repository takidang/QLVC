from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.bao_mat import THOI_HAN_TOKEN, tao_token
from app.auth.phu_thuoc import nguoi_dung_hien_tai
from app.auth.schemas import DangNhapVao, DoiMatKhauVao, HoSoRa, NguoiDungRa
from app.db import get_db
from app.luu_tru import KICH_THUOC_TOI_DA
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


# UC-39: hồ sơ cá nhân chỉ xem; không có PATCH/PUT /ho-so (AC5: 405)
@router.get("/ho-so", response_model=HoSoRa)
def ho_so(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)], db: Annotated[Session, Depends(get_db)]):
    return service.ho_so(db, nd)


@router.put("/anh-dai-dien", response_model=HoSoRa)
def doi_anh_dai_dien(
    anh: Annotated[UploadFile, File()],
    nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)],
    db: Annotated[Session, Depends(get_db)],
):
    # Đọc tối đa giới hạn + 1 byte: đủ biết ảnh quá lớn mà không nạp cả file lớn vào bộ nhớ
    du_lieu = anh.file.read(KICH_THUOC_TOI_DA + 1)
    return service.doi_anh_dai_dien(db, nd.id, du_lieu)


@router.delete("/anh-dai-dien", status_code=204)
def xoa_anh_dai_dien(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)], db: Annotated[Session, Depends(get_db)]):
    service.xoa_anh_dai_dien(db, nd.id)


@router.get("/anh-dai-dien")
def anh_dai_dien(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)]) -> Response:
    noi_dung, loai = service.doc_anh_dai_dien(nd)
    return Response(
        content=noi_dung,
        media_type=loai,
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-cache"},
    )
