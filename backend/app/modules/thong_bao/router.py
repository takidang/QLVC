from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import nguoi_dung_hien_tai
from app.db import get_db
from app.loi import LoiNghiepVu
from app.models import NguoiDung
from app.modules.thong_bao import service

router = APIRouter(prefix="/api/thong-bao", tags=["thong-bao"])


def _khong_tham_so(request: Request) -> None:
    if request.query_params:
        la = ", ".join(sorted(request.query_params.keys()))
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {la}", 400)


# Mọi vai trò đăng nhập; mỗi người chỉ thấy thông báo của vai trò mình (UC-37)
@router.get("", dependencies=[Depends(_khong_tham_so)])
def thong_bao(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)], db: Annotated[Session, Depends(get_db)]):
    return service.thong_bao(db, nd)
