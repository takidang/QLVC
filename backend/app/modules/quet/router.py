from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.loi import LoiNghiepVu
from app.luu_tru import KICH_THUOC_TOI_DA
from app.models import NguoiDung
from app.modules.quet import service
from app.modules.quet.schemas import LoaiQuet, QuetRa

# Cùng tiền tố trang tài xế (api.md 3.2) nhưng tách module, không đụng toi/ (UC-17, 18)
router = APIRouter(prefix="/api/toi", tags=["quet"])
TRUONG = {"ma_don", "loai", "lat", "lng", "do_chinh_xac_m", "anh", "ly_do_id", "chu_ky", "ten_nguoi_nhan"}
SO_ANH_TOI_DA = 5  # review PR #15: chặn gửi hàng loạt ảnh làm đầy ổ đĩa (security-rules)


async def _khong_truong_la(request: Request) -> None:
    # Form mặc định bỏ qua trường lạ; giờ quét do máy chủ ghi nên gửi thoi_gian (hay trường lạ khác) → 400 (TC-BR43-02)
    la = set((await request.form()).keys()) - TRUONG
    if la:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Trường không hợp lệ: {', '.join(sorted(la))}", 400)


@router.post("/quet", response_model=QuetRa, dependencies=[Depends(_khong_truong_la)])
def quet(
    db: Annotated[Session, Depends(get_db)],
    nd: Annotated[NguoiDung, Depends(can_vai_tro("TAI_XE"))],  # chỉ tài xế (BR-57)
    ma_don: Annotated[str, Form(min_length=1, max_length=50)],
    loai: Annotated[LoaiQuet, Form()],
    lat: Annotated[Decimal | None, Form(ge=-90, le=90)] = None,
    lng: Annotated[Decimal | None, Form(ge=-180, le=180)] = None,
    # Cột Numeric(8, 1): trần 9.999.999,95 làm tròn lên 10.000.000 → lỗi CSDL; 1.000 km sai số đã là vô nghĩa
    do_chinh_xac_m: Annotated[Decimal | None, Form(ge=0, lt=1_000_000)] = None,
    anh: Annotated[list[UploadFile] | None, File()] = None,
    ly_do_id: Annotated[int | None, Form()] = None,
    chu_ky: Annotated[UploadFile | None, File()] = None,  # UC-20: ảnh PNG người nhận ký (BR-41)
    ten_nguoi_nhan: Annotated[str | None, Form(max_length=100)] = None,
):
    if (lat is None) != (lng is None):  # quyết định 5: gửi một nửa tọa độ là lỗi, không phải thiếu GPS
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Cần gửi đủ cả vĩ độ và kinh độ", 400)
    if len(anh or []) > SO_ANH_TOI_DA:
        raise LoiNghiepVu("QUA_NHIEU_ANH", f"Tối đa {SO_ANH_TOI_DA} ảnh mỗi lần quét", 400)
    gps = (lat, lng, do_chinh_xac_m) if lat is not None else None
    # Đọc tối đa giới hạn + 1 byte mỗi ảnh: đủ để biết ảnh quá lớn mà không nạp cả file lớn vào bộ nhớ
    du_lieu = [a.file.read(KICH_THUOC_TOI_DA + 1) for a in anh or []]
    ky = chu_ky.file.read(KICH_THUOC_TOI_DA + 1) if chu_ky else None
    return service.quet(db, nd, ma_don, loai, gps, du_lieu, ly_do_id, ky, ten_nguoi_nhan)
