from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.modules.bao_cao import service
from app.thoi_gian import hom_nay_vn

router = APIRouter(prefix="/api/bao-cao", tags=["bao-cao"])
THANG = r"^\d{4}-(0[1-9]|1[0-2])$"
TRUONG = {"theo", "tu", "den"}


def _khong_tham_so_la(request: Request) -> None:
    la = set(request.query_params.keys()) - TRUONG
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {', '.join(sorted(la))}", 400)


# Quản lý, Kế toán xem; Điều phối xem theo api.md (UC-26 quyết định 5); Tài xế không (BR-57)
@router.get(
    "/lai-lo",
    dependencies=[Depends(can_vai_tro("QUAN_LY", "KE_TOAN", "DIEU_PHOI")), Depends(_khong_tham_so_la)],
)
def lai_lo(
    db: Annotated[Session, Depends(get_db)],
    theo: Literal["chuyen", "xe", "thang"] = "thang",
    tu: Annotated[str | None, Query(pattern=THANG)] = None,
    den: Annotated[str | None, Query(pattern=THANG)] = None,
):
    nay = hom_nay_vn().strftime("%Y-%m")
    return service.lai_lo(db, theo, tu or nay, den or tu or nay)
