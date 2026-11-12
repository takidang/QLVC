from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import nguoi_dung_hien_tai
from app.db import get_db
from app.loi import LoiNghiepVu
from app.models import NguoiDung
from app.modules.tim_kiem import service

router = APIRouter(prefix="/api/tim", tags=["tim-kiem"])


def _chi_q(request: Request) -> None:
    la = set(request.query_params.keys()) - {"q"}
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {', '.join(sorted(la))}", 400)


# Mọi vai trò đăng nhập; mỗi người chỉ thấy nhóm mình được xem (UC-36 quyết định 3)
@router.get("", dependencies=[Depends(_chi_q)])
def tim(
    q: Annotated[str, Query(min_length=2, max_length=100)],
    nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)],
    db: Annotated[Session, Depends(get_db)],
):
    return service.tim(db, nd, q)
