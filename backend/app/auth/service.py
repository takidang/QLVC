import logging
import math
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import luu_tru
from app.auth.bao_mat import bam_mat_khau, dung_mat_khau
from app.loi import LoiNghiepVu
from app.models import NguoiDung, TaiXe

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


def doi_mat_khau(db: Session, nd_id: int, cu: str, moi: str, bay_gio: datetime) -> None:
    """UC-35. Sai mật khẩu cũ tính như đăng nhập sai (cùng bộ đếm, cùng khóa 15 phút) để không dò mật khẩu qua đây."""
    nd = db.scalar(select(NguoiDung).where(NguoiDung.id == nd_id).with_for_update())
    if nd.khoa_den and nd.khoa_den > bay_gio:
        phut = math.ceil((nd.khoa_den - bay_gio).total_seconds() / 60)
        raise LoiNghiepVu("KHOA_TAM", f"Sai mật khẩu quá {SO_LAN_SAI_TOI_DA} lần, thử lại sau {phut} phút", 429)
    if not dung_mat_khau(nd.mat_khau_bam, cu):
        nd.so_lan_sai += 1
        if nd.so_lan_sai >= SO_LAN_SAI_TOI_DA:
            nd.so_lan_sai, nd.khoa_den = 0, bay_gio + THOI_GIAN_KHOA
        db.commit()
        # 422, không phải 401: giao diện không nhầm là phiên hết hạn
        raise LoiNghiepVu("SAI_MAT_KHAU_CU", "Mật khẩu hiện tại không đúng", 422)
    if cu == moi:
        raise LoiNghiepVu("MAT_KHAU_TRUNG", "Mật khẩu mới phải khác mật khẩu hiện tại", 422)
    # Phiên đang dùng vẫn còn hạn (JWT không có phiên bản – UC-02 quyết định 5)
    nd.mat_khau_bam, nd.so_lan_sai, nd.khoa_den = bam_mat_khau(moi), 0, None
    db.commit()


def tao_quan_ly(db: Session, ten_dang_nhap: str, ho_ten: str, mat_khau: str) -> NguoiDung:
    if len(mat_khau) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
    if db.scalar(select(NguoiDung.id).where(NguoiDung.ten_dang_nhap == ten_dang_nhap)):
        raise ValueError(f"Tên đăng nhập {ten_dang_nhap!r} đã tồn tại")
    nd = NguoiDung(ten_dang_nhap=ten_dang_nhap, ho_ten=ho_ten, vai_tro="QUAN_LY", mat_khau_bam=bam_mat_khau(mat_khau))
    db.add(nd)
    db.commit()
    return nd


def ho_so(db: Session, nd: NguoiDung) -> dict:
    """UC-39-AC1: hồ sơ cá nhân của chính người gọi; tài xế kèm 4 trường GPLX / SĐT."""
    tx = db.scalar(select(TaiXe).where(TaiXe.nguoi_dung_id == nd.id)) if nd.vai_tro == "TAI_XE" else None
    return {
        "id": nd.id,
        "ten_dang_nhap": nd.ten_dang_nhap,
        "ho_ten": nd.ho_ten,
        "vai_tro": nd.vai_tro,
        "trang_thai": nd.trang_thai,
        "co_anh_dai_dien": bool(nd.anh_dai_dien),
        "tai_xe": tx,
    }


def doi_anh_dai_dien(db: Session, nd_id: int, du_lieu: bytes) -> dict:
    """UC-39-AC2, AC3: kiểm byte đầu & cỡ → lưu tên hex → ghi cột → commit → sau commit xóa ảnh cũ."""
    duoi = luu_tru.kiem_anh(du_lieu)
    nd = db.scalar(select(NguoiDung).where(NguoiDung.id == nd_id).with_for_update())
    cu = nd.anh_dai_dien
    ten_moi = luu_tru.luu(du_lieu, duoi)
    try:
        nd.anh_dai_dien = ten_moi
        db.commit()
    except Exception:
        db.rollback()
        try:
            luu_tru.xoa(ten_moi)
        except Exception as err:
            logging.getLogger(__name__).warning("Không xóa được ảnh đại diện mới sau rollback (%s)", type(err).__name__)
        raise
    if cu:
        try:
            luu_tru.xoa(cu)
        except Exception as err:
            # Lỗi xóa file cũ chỉ log, không làm hỏng yêu cầu đã commit (UC-39)
            logging.getLogger(__name__).warning(
                "Không xóa được ảnh đại diện cũ của người dùng %s (%s)", nd.id, type(err).__name__
            )
    return ho_so(db, nd)


def xoa_anh_dai_dien(db: Session, nd_id: int) -> None:
    """UC-39-AC3: xóa ảnh đại diện của chính mình; chưa có ảnh vẫn trả 204."""
    nd = db.scalar(select(NguoiDung).where(NguoiDung.id == nd_id).with_for_update())
    cu = nd.anh_dai_dien
    if not cu:
        return
    nd.anh_dai_dien = None
    db.commit()
    try:
        luu_tru.xoa(cu)
    except Exception as err:
        logging.getLogger(__name__).warning(
            "Không xóa được ảnh đại diện cũ của người dùng %s (%s)", nd.id, type(err).__name__
        )


def doc_anh_dai_dien(nd: NguoiDung) -> tuple[bytes, str]:
    """UC-39-AC4: đọc ảnh đại diện của chính người gọi kèm Content-Type theo đuôi đã kiểm."""
    if not nd.anh_dai_dien:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Chưa có ảnh đại diện", 404)
    try:
        noi_dung = luu_tru.doc(nd.anh_dai_dien)
    except (FileNotFoundError, ValueError) as err:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy ảnh đại diện", 404) from err
    return noi_dung, luu_tru.LOAI_ANH[Path(nd.anh_dai_dien).suffix]
