from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth.bao_mat import doc_token
from app.db import get_db
from app.loi import LoiNghiepVu
from app.models import NguoiDung


def nguoi_dung_hien_tai(request: Request, db: Annotated[Session, Depends(get_db)]) -> NguoiDung:
    token = request.cookies.get("access_token")
    nd_id = doc_token(token) if token else None
    nd = db.get(NguoiDung, nd_id) if nd_id else None
    # Khóa tài khoản có hiệu lực ngay, không đợi token hết hạn (BR-60)
    if nd is None or nd.trang_thai != "HOAT_DONG":
        raise LoiNghiepVu("CHUA_DANG_NHAP", "Chưa đăng nhập hoặc phiên đã hết hạn", 401)
    return nd


def can_vai_tro(*vai_tro: str):
    """Phân quyền ở máy chủ (BR-57). Quản lý kế thừa quyền Điều phối (nghiep-vu.md mục 6)."""
    cho_phep = set(vai_tro) | ({"QUAN_LY"} if "DIEU_PHOI" in vai_tro else set())

    def kiem(nd: Annotated[NguoiDung, Depends(nguoi_dung_hien_tai)]) -> NguoiDung:
        if nd.vai_tro not in cho_phep:
            raise LoiNghiepVu("KHONG_DU_QUYEN", "Bạn không có quyền thực hiện thao tác này", 403)
        return nd

    return kiem
