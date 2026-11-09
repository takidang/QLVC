from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.luu_tru import KICH_THUOC_TOI_DA
from app.models import NguoiDung
from app.modules.tien.chi_phi import service
from app.modules.tien.chi_phi.schemas import ChiPhiChuyen, ChiPhiRa, ChiPhiSua, LoaiChi, SoLit, SoTien

# Trang tài xế (api.md 2.5); module tiền vì UC-24 duyệt cùng bảng
router = APIRouter(prefix="/api/toi", tags=["chi-phi"])
Db = Annotated[Session, Depends(get_db)]
TaiXe = Annotated[NguoiDung, Depends(can_vai_tro("TAI_XE"))]  # chỉ tài xế (BR-57)
TRUONG = {"loai", "so_tien", "so_lit", "ghi_chu", "anh"}
SO_ANH_TOI_DA = 5


async def _khong_truong_la(request: Request) -> None:
    # Form mặc định bỏ qua trường lạ (như quét mã UC-19): gửi trạng thái, người tạo… → 400
    la = set((await request.form()).keys()) - TRUONG
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Trường không hợp lệ: {', '.join(sorted(la))}", 400)


@router.get("/chuyen/{chuyen_id}/chi-phi", response_model=ChiPhiChuyen)
def theo_chuyen(chuyen_id: int, db: Db, nd: TaiXe):
    return service.theo_chuyen(db, nd, chuyen_id)


@router.post(
    "/chuyen/{chuyen_id}/chi-phi",
    response_model=ChiPhiRa,
    status_code=201,
    dependencies=[Depends(_khong_truong_la)],
)
def ghi(
    chuyen_id: int,
    db: Db,
    nd: TaiXe,
    loai: Annotated[LoaiChi, Form()],
    so_tien: Annotated[SoTien, Form()],
    so_lit: Annotated[SoLit | None, Form()] = None,
    ghi_chu: Annotated[str | None, Form(max_length=500)] = None,
    anh: Annotated[list[UploadFile] | None, File()] = None,
):
    if len(anh or []) > SO_ANH_TOI_DA:
        raise LoiNghiepVu("QUA_NHIEU_ANH", f"Tối đa {SO_ANH_TOI_DA} ảnh", 400)
    # Đọc tối đa giới hạn + 1 byte: đủ biết ảnh quá lớn mà không nạp cả file lớn vào bộ nhớ
    du_lieu = [a.file.read(KICH_THUOC_TOI_DA + 1) for a in anh or []]
    return service.ghi(db, nd, chuyen_id, loai, so_tien, so_lit, ghi_chu, du_lieu)


@router.patch("/chi-phi/{chi_phi_id}", response_model=ChiPhiRa)
def sua(chi_phi_id: int, vao: ChiPhiSua, db: Db, nd: TaiXe):
    return service.sua(db, nd, chi_phi_id, vao.model_dump(exclude_unset=True))


@router.delete("/chi-phi/{chi_phi_id}", status_code=204)
def xoa(chi_phi_id: int, db: Db, nd: TaiXe):
    service.xoa(db, nd, chi_phi_id)
    return Response(status_code=204)
