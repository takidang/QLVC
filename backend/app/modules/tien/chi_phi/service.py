"""UC-21 ghi chi phí: tài xế ghi khoản đã chi (BR-54), sửa / xóa khoản của mình khi còn chờ duyệt.

Duyệt, từ chối là của Kế toán ở UC-24. Khóa chuyến dùng chung (`FOR SHARE`, kien-truc.md mục 6): quyết toán
khóa riêng dòng chuyến nên phải đợi các lượt ghi chi phí đang chạy, và ngược lại.
"""

import unicodedata
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import luu_tru
from app.loi import LoiNghiepVu
from app.models import ChiPhi, Chuyen, NguoiDung, NhatKyTien, TaiXe, TamUng, Tep

# Đang chạy hoặc đã về mà chưa quyết toán (tiền điều kiện UC-21, BR-54); LAP, HUY tài xế không thấy → 404 như UC-17
GHI_DUOC = ("DANG_CHAY", "HOAN_THANH")
TAI_XE_THAY = ("DA_CHOT", *GHI_DUOC, "DA_QUYET_TOAN")
LY_DO_SUA = "Tài xế sửa khoản chờ duyệt"
LY_DO_XOA = "Tài xế xóa khoản chờ duyệt"


def _chuyen_cua_toi(db: Session, nd: NguoiDung, chuyen_id: int, khoa: bool = False) -> Chuyen:
    c = db.get(Chuyen, chuyen_id, with_for_update={"read": True} if khoa else None, populate_existing=khoa)
    tai_xe_id = db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id))
    # Chuyến người khác, LAP / HUY, id không có: cùng một 404, không lộ chuyến có tồn tại (BR-58, IDOR)
    if c is None or c.tai_xe_id != tai_xe_id or c.trang_thai not in TAI_XE_THAY:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return c


def _kiem_ghi_duoc(c: Chuyen, viec: str) -> None:
    if c.trang_thai == "DA_QUYET_TOAN":
        raise LoiNghiepVu("BR-29", f"Chuyến {c.ma_chuyen} đã quyết toán, không {viec} chi phí được", 409)
    if c.trang_thai not in GHI_DUOC:
        raise LoiNghiepVu("BR-54", f"Chuyến {c.ma_chuyen} chưa chạy, chưa {viec} chi phí được", 409)


def _kiem_br54(loai: str, so_lit: Decimal | None, ghi_chu: str, co_anh: bool) -> None:
    # Hình dạng sai → 400 (TC-BR54-03); thiếu nội dung bắt buộc → 422 BR-54 (UC-21 quyết định 4)
    if loai == "DAU" and so_lit is None:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Khoản dầu cần số lít", 400)
    if loai != "DAU" and so_lit is not None:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Chỉ khoản dầu mới ghi số lít", 400)
    thieu = [ten for ten, co in (("ghi chú", ghi_chu), ("ảnh chứng từ", co_anh)) if not co]
    if thieu:
        raise LoiNghiepVu("BR-54", f"Chi phí cần có {', '.join(thieu)}", 422)


def _chuan(ghi_chu: str | None) -> str:
    return unicodedata.normalize("NFC", ghi_chu or "").strip()


def _gia_tri(cp: ChiPhi) -> str:
    return f"{cp.so_tien_khai} {cp.loai}" + (f" {cp.so_lit:.2f}" if cp.so_lit is not None else "")  # quyết định 8


def _ghi_nhat_ky(db: Session, cp: ChiPhi, hanh_dong: str, cu: str | None, moi: str | None, ly_do: str, nd):
    # Nhật ký tiền chỉ thêm, không sửa xóa (BR-62); dòng XOA giữ lại khi khoản đã bị xóa
    db.add(
        NhatKyTien(
            bang="chi_phi",
            ban_ghi_id=cp.id,
            hanh_dong=hanh_dong,
            gia_tri_cu=cu,
            gia_tri_moi=moi,
            ly_do=ly_do,
            nguoi=nd.id,
        )
    )


def _so_anh(db: Session, chi_phi_ids: list[int]) -> dict[int, int]:
    dong = db.execute(
        select(Tep.chi_phi_id, func.count()).where(Tep.chi_phi_id.in_(chi_phi_ids)).group_by(Tep.chi_phi_id)
    )
    return dict(dong.all())


def _ra(cp: ChiPhi, so_anh: int) -> dict:
    return {
        "id": cp.id,
        "chuyen_id": cp.chuyen_id,
        "loai": cp.loai,
        "so_tien_khai": cp.so_tien_khai,
        "so_tien_duyet": cp.so_tien_duyet,
        "so_lit": cp.so_lit,
        "ghi_chu": cp.ghi_chu,
        "trang_thai": cp.trang_thai,
        "so_anh": so_anh,
        "tao_luc": cp.tao_luc,
    }


def ghi(
    db: Session,
    nd: NguoiDung,
    chuyen_id: int,
    loai: str,
    so_tien: int,
    so_lit: Decimal | None,
    ghi_chu: str | None,
    anh: list[bytes],
) -> dict:
    c = _chuyen_cua_toi(db, nd, chuyen_id, khoa=True)
    _kiem_ghi_duoc(c, "ghi")
    ghi_chu = _chuan(ghi_chu)
    _kiem_br54(loai, so_lit, ghi_chu, bool(anh))
    duoi = [luu_tru.kiem_anh(a) for a in anh]  # sai loại 400, quá 500 KB 413, trước khi ghi gì

    da_ghi: list[str] = []
    try:
        cp = ChiPhi(chuyen_id=c.id, loai=loai, so_tien_khai=so_tien, so_lit=so_lit, ghi_chu=ghi_chu, nguoi_tao=nd.id)
        db.add(cp)
        db.flush()
        for du_lieu, du in zip(anh, duoi, strict=True):
            da_ghi.append(luu_tru.luu(du_lieu, du))
            db.add(Tep(chi_phi_id=cp.id, loai="ANH", duong_dan=da_ghi[-1], kich_thuoc=len(du_lieu)))
        _ghi_nhat_ky(db, cp, "TAO", None, _gia_tri(cp), f"Tài xế ghi chi phí chuyến {c.ma_chuyen}", nd)
        db.commit()
    except Exception:
        db.rollback()
        for ten in da_ghi:  # không để ảnh mồ côi khi CSDL lỗi (NFR-REL-01)
            luu_tru.xoa(ten)
        raise
    return _ra(cp, len(anh))


def _khoan_cua_toi(db: Session, nd: NguoiDung, chi_phi_id: int, viec: str) -> ChiPhi:
    """Khóa chuyến rồi khoản; chỉ khoản mình tạo, còn chờ duyệt, chuyến chưa quyết toán."""
    chuyen_id = db.scalar(select(ChiPhi.chuyen_id).where(ChiPhi.id == chi_phi_id, ChiPhi.nguoi_tao == nd.id))
    if chuyen_id is None:  # khoản của tài xế khác hay không có: cùng 404 (BR-58)
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khoản chi phí", 404)
    c = _chuyen_cua_toi(db, nd, chuyen_id, khoa=True)
    cp = db.get(ChiPhi, chi_phi_id, with_for_update=True, populate_existing=True)
    if cp is None:  # request song song đã xóa khoản trong lúc đợi khóa chuyến
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khoản chi phí", 404)
    _kiem_ghi_duoc(c, viec)
    if cp.trang_thai != "CHO_DUYET":
        raise LoiNghiepVu("BR-54", f"Khoản đã được Kế toán xử lý, không {viec} được", 409)
    return cp


def sua(db: Session, nd: NguoiDung, chi_phi_id: int, thay: dict) -> dict:
    cp = _khoan_cua_toi(db, nd, chi_phi_id, "sửa")
    moi = {
        "loai": thay.get("loai") or cp.loai,
        "so_tien_khai": thay.get("so_tien") or cp.so_tien_khai,
        "so_lit": thay["so_lit"] if "so_lit" in thay else cp.so_lit,
        "ghi_chu": _chuan(thay["ghi_chu"]) if "ghi_chu" in thay else cp.ghi_chu,
    }
    _kiem_br54(moi["loai"], moi["so_lit"], moi["ghi_chu"], True)  # sửa không đổi ảnh (quyết định 6)
    if all(getattr(cp, k) == v for k, v in moi.items()):
        raise LoiNghiepVu("KHONG_CO_THAY_DOI", "Không có gì thay đổi", 400)
    cu = _gia_tri(cp)
    for k, v in moi.items():
        setattr(cp, k, v)
    _ghi_nhat_ky(db, cp, "SUA", cu, _gia_tri(cp), LY_DO_SUA, nd)
    db.commit()
    return _ra(cp, _so_anh(db, [cp.id]).get(cp.id, 0))


def xoa(db: Session, nd: NguoiDung, chi_phi_id: int) -> None:
    cp = _khoan_cua_toi(db, nd, chi_phi_id, "xóa")
    tep = list(db.scalars(select(Tep.duong_dan).where(Tep.chi_phi_id == cp.id)))
    _ghi_nhat_ky(db, cp, "XOA", _gia_tri(cp), None, LY_DO_XOA, nd)
    db.execute(delete(Tep).where(Tep.chi_phi_id == cp.id))
    db.delete(cp)
    db.commit()
    for ten in tep:  # xóa file sau khi CSDL đã xong: lỗi giữa chừng thì ảnh vẫn còn cho khoản còn đó
        luu_tru.xoa(ten)


def theo_chuyen(db: Session, nd: NguoiDung, chuyen_id: int) -> dict:
    c = _chuyen_cua_toi(db, nd, chuyen_id)
    khoan = list(db.scalars(select(ChiPhi).where(ChiPhi.chuyen_id == c.id).order_by(ChiPhi.id)))
    so_anh = _so_anh(db, [k.id for k in khoan])
    tam_ung = db.scalar(
        select(func.coalesce(func.sum(TamUng.so_tien), 0)).where(
            TamUng.chuyen_id == c.id, TamUng.trang_thai == "HIEU_LUC"
        )
    )
    return {
        "chuyen_id": c.id,
        "tam_ung_da_nhan": int(tam_ung),  # sum BIGINT trên PostgreSQL ra Decimal
        "tong_da_khai": sum(k.so_tien_khai for k in khoan if k.trang_thai != "TU_CHOI"),
        "khoan": [_ra(k, so_anh.get(k.id, 0)) for k in khoan],
    }
