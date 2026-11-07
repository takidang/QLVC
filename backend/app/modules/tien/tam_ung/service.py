"""UC-23 tạm ứng: Kế toán cấp, sửa, thu hồi; tổng còn hiệu lực không vượt định mức đã chốt (BR-53).

Mọi lần ghi khóa dòng chuyến trước (kien-truc.md mục 6): hai lần cấp cùng chuyến, hoặc cấp và mở chốt / hủy
chạy lần lượt, nên tổng luôn được kiểm trên số mới nhất.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import Chuyen, NguoiDung, NhatKyTien, TaiXe, TamUng
from app.phan_trang import PhanTrang

CAP_DUOC = ("DA_CHOT", "DANG_CHAY")  # BR-53
SUA_DUOC = (*CAP_DUOC, "HOAN_THANH")  # sửa, thu hồi tới khi quyết toán (UC-23 quyết định 3)
TEN_TRANG_THAI = {"LAP": "đang lập", "HOAN_THANH": "đã hoàn thành", "DA_QUYET_TOAN": "đã quyết toán", "HUY": "đã hủy"}
THU_HOI_MAC_DINH = "Tài xế đã nộp lại tạm ứng"


def _tien(so: int) -> str:
    return f"{so:,}".replace(",", ".") + " đ"


def _khoa_chuyen(db: Session, chuyen_id: int) -> Chuyen:
    c = db.get(Chuyen, chuyen_id, with_for_update=True, populate_existing=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return c


def _dinh_muc(c: Chuyen) -> int:
    """Định mức chi phí đã chốt (dầu + cầu đường + bốc xếp, BR-53, 71); chuyến chưa chốt là 0."""
    return (c.dm_dau_chot or 0) + (c.dm_cau_duong_chot or 0) + (c.dm_boc_xep_chot or 0)


def _tong_hieu_luc(db: Session, chuyen_id: int, tru_id: int | None = None) -> int:
    q = select(func.coalesce(func.sum(TamUng.so_tien), 0)).where(
        TamUng.chuyen_id == chuyen_id, TamUng.trang_thai == "HIEU_LUC"
    )
    if tru_id is not None:
        q = q.where(TamUng.id != tru_id)
    return int(db.scalar(q))  # sum của BIGINT trên PostgreSQL ra Decimal


def _kiem_br53(db: Session, c: Chuyen, so_tien: int, tru_id: int | None = None) -> None:
    dm, da_cap = _dinh_muc(c), _tong_hieu_luc(db, c.id, tru_id)
    if da_cap + so_tien > dm:
        con = max(dm - da_cap, 0)
        raise LoiNghiepVu(
            "BR-53",
            f"Tổng tạm ứng {_tien(da_cap + so_tien)} vượt định mức đã chốt {_tien(dm)} của chuyến {c.ma_chuyen}; "
            f"còn được cấp {_tien(con)}",
            422,
            chi_tiet=[{"ma": "BR-53", "dinh_muc": dm, "tong_hieu_luc": da_cap, "con_duoc_cap": con}],
        )


def _ghi_nhat_ky(db: Session, tu: TamUng, hanh_dong: str, cu: str | None, moi: str, ly_do: str, nd: NguoiDung):
    # Nhật ký tiền chỉ thêm, không sửa xóa (BR-62)
    db.add(
        NhatKyTien(
            bang="tam_ung",
            ban_ghi_id=tu.id,
            hanh_dong=hanh_dong,
            gia_tri_cu=cu,
            gia_tri_moi=moi,
            ly_do=ly_do,
            nguoi=nd.id,
        )
    )


def _gia_tri(tu: TamUng) -> str:
    return f"{tu.so_tien} {tu.hinh_thuc}"  # quyết định 7


def _truy_van():
    return (
        select(TamUng, Chuyen.ma_chuyen, NguoiDung.ho_ten)
        .join(Chuyen, Chuyen.id == TamUng.chuyen_id)
        .join(TaiXe, TaiXe.id == TamUng.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
    )


def _ra(dong) -> dict:
    tu, ma_chuyen, ten = dong
    return {
        "id": tu.id,
        "chuyen_id": tu.chuyen_id,
        "ma_chuyen": ma_chuyen,
        "tai_xe_id": tu.tai_xe_id,
        "ten_tai_xe": ten,
        "so_tien": tu.so_tien,
        "hinh_thuc": tu.hinh_thuc,
        "trang_thai": tu.trang_thai,
        "tao_luc": tu.tao_luc,
    }


def _lay_ra(db: Session, tam_ung_id: int) -> dict:
    return _ra(db.execute(_truy_van().where(TamUng.id == tam_ung_id)).one())


def cap(db: Session, chuyen_id: int, so_tien: int, hinh_thuc: str, nd: NguoiDung) -> dict:
    c = _khoa_chuyen(db, chuyen_id)
    if c.trang_thai not in CAP_DUOC:
        raise LoiNghiepVu(
            "BR-53",
            f"Chuyến {c.ma_chuyen} {TEN_TRANG_THAI.get(c.trang_thai, c.trang_thai)}, "
            "chỉ cấp tạm ứng khi chuyến đã chốt hoặc đang chạy",
            409,
        )
    _kiem_br53(db, c, so_tien)
    tu = TamUng(chuyen_id=c.id, tai_xe_id=c.tai_xe_id, so_tien=so_tien, hinh_thuc=hinh_thuc, nguoi_tao=nd.id)
    db.add(tu)
    db.flush()
    _ghi_nhat_ky(db, tu, "TAO", None, _gia_tri(tu), f"Cấp tạm ứng chuyến {c.ma_chuyen}", nd)
    db.commit()
    return _lay_ra(db, tu.id)


def _khoa_khoan(db: Session, tam_ung_id: int, viec: str) -> tuple[TamUng, Chuyen]:
    """Khóa chuyến rồi khoản (thứ tự kien-truc.md mục 6); chỉ khoản còn hiệu lực của chuyến chưa quyết toán."""
    chuyen_id = db.scalar(select(TamUng.chuyen_id).where(TamUng.id == tam_ung_id))
    if chuyen_id is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khoản tạm ứng", 404)
    c = _khoa_chuyen(db, chuyen_id)
    tu = db.get(TamUng, tam_ung_id, with_for_update=True, populate_existing=True)
    if c.trang_thai == "DA_QUYET_TOAN":
        raise LoiNghiepVu("BR-29", f"Chuyến {c.ma_chuyen} đã quyết toán, không {viec} tạm ứng được", 409)
    if c.trang_thai not in SUA_DUOC:
        raise LoiNghiepVu(
            "BR-53", f"Chuyến {c.ma_chuyen} {TEN_TRANG_THAI.get(c.trang_thai, c.trang_thai)}, không {viec} được", 409
        )
    if tu.trang_thai != "HIEU_LUC":
        raise LoiNghiepVu("BR-53", f"Khoản tạm ứng đã thu hồi, không {viec} được", 409)
    return tu, c


def sua(db: Session, tam_ung_id: int, so_tien: int, hinh_thuc: str | None, ly_do: str, nd: NguoiDung) -> dict:
    tu, c = _khoa_khoan(db, tam_ung_id, "sửa")
    hinh_thuc = hinh_thuc or tu.hinh_thuc
    if (so_tien, hinh_thuc) == (tu.so_tien, tu.hinh_thuc):
        raise LoiNghiepVu("KHONG_CO_THAY_DOI", "Số tiền và hình thức giữ nguyên, không có gì để sửa", 400)
    _kiem_br53(db, c, so_tien, tru_id=tu.id)  # kiểm lại ở mọi lần sửa (BR-53)
    cu = _gia_tri(tu)
    tu.so_tien, tu.hinh_thuc = so_tien, hinh_thuc
    _ghi_nhat_ky(db, tu, "SUA", cu, _gia_tri(tu), ly_do, nd)
    db.commit()
    return _lay_ra(db, tu.id)


def thu_hoi(db: Session, tam_ung_id: int, ly_do: str | None, nd: NguoiDung) -> dict:
    tu, _ = _khoa_khoan(db, tam_ung_id, "thu hồi")
    tu.trang_thai = "DA_THU_HOI"  # BR-24, 25: sau đó Điều phối mở chốt / hủy được
    _ghi_nhat_ky(db, tu, "THU_HOI", "HIEU_LUC", "DA_THU_HOI", ly_do or THU_HOI_MAC_DINH, nd)
    db.commit()
    return _lay_ra(db, tu.id)


def theo_chuyen(db: Session, chuyen_id: int) -> dict:
    c = db.get(Chuyen, chuyen_id)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    dm, da_cap = _dinh_muc(c), _tong_hieu_luc(db, c.id)
    khoan = db.execute(_truy_van().where(TamUng.chuyen_id == c.id).order_by(TamUng.id)).all()
    return {
        "chuyen_id": c.id,
        "ma_chuyen": c.ma_chuyen,
        "trang_thai_chuyen": c.trang_thai,
        "dinh_muc": dm,
        "tong_hieu_luc": da_cap,
        "con_duoc_cap": max(dm - da_cap, 0),
        "khoan": [_ra(k) for k in khoan],
    }


def danh_sach(
    db: Session, pt: PhanTrang, trang_thai: str | None, chuyen_id: int | None, tai_xe_id: int | None
) -> tuple[list[dict], int]:
    loc = [
        dk
        for dk, co in (
            (TamUng.trang_thai == trang_thai, trang_thai),
            (TamUng.chuyen_id == chuyen_id, chuyen_id),
            (TamUng.tai_xe_id == tai_xe_id, tai_xe_id),
        )
        if co is not None
    ]
    tong = db.scalar(select(func.count()).select_from(TamUng).where(*loc))
    dong = db.execute(_truy_van().where(*loc).order_by(TamUng.id.desc()).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return [_ra(d) for d in dong], tong
