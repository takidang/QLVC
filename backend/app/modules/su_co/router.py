from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.luu_tru import KICH_THUOC_TOI_DA
from app.models import NguoiDung
from app.modules.su_co import service
from app.modules.su_co.schemas import LoaiSuCo, SuCoRa

# Trang tài xế (api.md 2.5); Điều phối đóng sự cố ở /api/su-co/{id}/dong (UC-32)
router = APIRouter(prefix="/api/toi", tags=["su-co"])
Db = Annotated[Session, Depends(get_db)]
TaiXe = Annotated[NguoiDung, Depends(can_vai_tro("TAI_XE"))]  # chỉ tài xế (BR-57)
TRUONG = {"loai", "ghi_chu", "anh"}
SO_ANH_TOI_DA = 5


async def _khong_truong_la(request: Request) -> None:
    # Form mặc định bỏ qua trường lạ: gửi trạng thái, tài xế… → 400 (như UC-19, 21)
    la = set((await request.form()).keys()) - TRUONG
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Trường không hợp lệ: {', '.join(sorted(la))}", 400)


@router.get("/chuyen/{chuyen_id}/su-co", response_model=list[SuCoRa])
def theo_chuyen(chuyen_id: int, db: Db, nd: TaiXe):
    return service.theo_chuyen(db, nd, chuyen_id)


@router.post(
    "/chuyen/{chuyen_id}/su-co",
    response_model=SuCoRa,
    status_code=201,
    dependencies=[Depends(_khong_truong_la)],
)
def bao(
    chuyen_id: int,
    db: Db,
    nd: TaiXe,
    loai: Annotated[LoaiSuCo, Form()],
    ghi_chu: Annotated[str | None, Form(max_length=500)] = None,
    anh: Annotated[list[UploadFile] | None, File()] = None,
):
    if len(anh or []) > SO_ANH_TOI_DA:
        raise LoiNghiepVu("QUA_NHIEU_ANH", f"Tối đa {SO_ANH_TOI_DA} ảnh", 400)
    # Đọc tối đa giới hạn + 1 byte: đủ biết ảnh quá lớn mà không nạp cả file lớn vào bộ nhớ
    du_lieu = [a.file.read(KICH_THUOC_TOI_DA + 1) for a in anh or []]
    return service.bao(db, nd, chuyen_id, loai, ghi_chu, du_lieu)
