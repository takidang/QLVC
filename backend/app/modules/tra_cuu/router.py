from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.tra_cuu import service
from app.modules.tra_cuu.schemas import TraCuuRa, TraCuuVao

router = APIRouter(prefix="/api/tra-cuu", tags=["tra-cuu"])


@router.post("", response_model=TraCuuRa)
def tra_cuu(vao: TraCuuVao, request: Request, db: Annotated[Session, Depends(get_db)]):
    # Không đăng nhập (BR-59). IP lấy từ kết nối, không tin X-Forwarded-For (khách tự đặt được)
    ip = request.client.host if request.client else "?"
    return service.tra_cuu(db, ip, vao.ma_don, vao.sdt_4_so_cuoi)
