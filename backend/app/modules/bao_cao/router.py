from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.modules.bao_cao import service
from app.thoi_gian import hom_nay_vn

router = APIRouter(prefix="/api/bao-cao", tags=["bao-cao"])
THANG = r"^20\d{2}-(0[1-9]|1[0-2])$"  # năm 2000–2099: năm 0 hay 9999 làm tràn datetime


def _chi_nhan(*truong: str):
    def kiem(request: Request) -> None:
        la = set(request.query_params.keys()) - set(truong)
        if la:
            raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Tham số không hợp lệ: {', '.join(sorted(la))}", 400)

    return kiem


# Quản lý, Kế toán xem; Điều phối xem theo api.md (UC-26 quyết định 5); Tài xế không (BR-57)
@router.get(
    "/lai-lo",
    dependencies=[Depends(can_vai_tro("QUAN_LY", "KE_TOAN", "DIEU_PHOI")), Depends(_chi_nhan("theo", "tu", "den"))],
)
def lai_lo(
    db: Annotated[Session, Depends(get_db)],
    theo: Literal["chuyen", "xe", "thang"] = "thang",
    tu: Annotated[str | None, Query(pattern=THANG)] = None,
    den: Annotated[str | None, Query(pattern=THANG)] = None,
):
    nay = hom_nay_vn().strftime("%Y-%m")
    return service.lai_lo(db, theo, tu or nay, den or tu or nay)


# Quản lý, Kế toán xem (api.md); Điều phối, Tài xế không (UC-34 quyết định 5)
@router.get(
    "/hieu-suat-xe",
    dependencies=[Depends(can_vai_tro("QUAN_LY", "KE_TOAN")), Depends(_chi_nhan("thang"))],
)
def hieu_suat_xe(
    db: Annotated[Session, Depends(get_db)],
    thang: Annotated[str | None, Query(pattern=THANG)] = None,
):
    return service.hieu_suat_xe(db, thang or hom_nay_vn().strftime("%Y-%m"))
