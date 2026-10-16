import math
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.bao_mat import bam_mat_khau, dung_mat_khau
from app.loi import LoiNghiepVu
from app.models import NguoiDung

SO_LAN_SAI_TOI_DA = 5  # NFR-SEC-05, kien-truc.md mục 5
THOI_GIAN_KHOA = timedelta(minutes=15)
# Băm giả để thời gian trả lời khi sai tên đăng nhập gần bằng khi sai mật khẩu
_BAM_GIA = bam_mat_khau("khong-ton-tai")


def _sai_thong_tin() -> LoiNghiepVu:
    return LoiNghiepVu("SAI_THONG_TIN", "Sai tên đăng nhập hoặc mật khẩu", 401)


def dang_nhap(db: Session, ten_dang_nhap: str, mat_khau: str, bay_gio: datetime) -> NguoiDung:
    # Khóa dòng để hai lần sai đồng thời không làm lệch bộ đếm
    nd = db.scalar(select(NguoiDung).where(NguoiDung.ten_dang_nhap == ten_dang_nhap).with_for_update())
    if nd is None:
        dung_mat_khau(_BAM_GIA, mat_khau)
        raise _sai_thong_tin()

    if nd.khoa_den and nd.khoa_den > bay_gio:
        phut = math.ceil((nd.khoa_den - bay_gio).total_seconds() / 60)
        raise LoiNghiepVu("KHOA_TAM", f"Sai mật khẩu quá {SO_LAN_SAI_TOI_DA} lần, thử lại sau {phut} phút", 429)

    if not dung_mat_khau(nd.mat_khau_bam, mat_khau):
        nd.so_lan_sai += 1
        if nd.so_lan_sai >= SO_LAN_SAI_TOI_DA:
            nd.so_lan_sai, nd.khoa_den = 0, bay_gio + THOI_GIAN_KHOA
        db.commit()
        raise _sai_thong_tin()

    nd.so_lan_sai, nd.khoa_den = 0, None
    db.commit()
    if nd.trang_thai != "HOAT_DONG":  # BR-60
        raise LoiNghiepVu("TAI_KHOAN_KHOA", "Tài khoản đã bị khóa", 403)
    return nd


def tao_quan_ly(db: Session, ten_dang_nhap: str, ho_ten: str, mat_khau: str) -> NguoiDung:
    if len(mat_khau) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
    if db.scalar(select(NguoiDung.id).where(NguoiDung.ten_dang_nhap == ten_dang_nhap)):
        raise ValueError(f"Tên đăng nhập {ten_dang_nhap!r} đã tồn tại")
    nd = NguoiDung(ten_dang_nhap=ten_dang_nhap, ho_ten=ho_ten, vai_tro="QUAN_LY", mat_khau_bam=bam_mat_khau(mat_khau))
    db.add(nd)
    db.commit()
    return nd
