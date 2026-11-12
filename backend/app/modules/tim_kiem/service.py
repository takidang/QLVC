"""UC-36 tìm kiếm chung: một từ khóa, kết quả gộp theo nhóm, mỗi nhóm tối đa 5 dòng và tổng số khớp."""

import unicodedata

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import Chuyen, KhachHang, NguoiDung, TaiXe, Xe
from app.modules.chuyen import service as chuyen_service
from app.modules.don import service as don_service
from app.modules.toi.service import THAY_DUOC

TOI_DA = 5
NHOM = ("chuyen", "don", "xe", "tai_xe", "khach_hang")
# Nhóm xem được theo vai trò (quyền xem hiện có của từng module); Quản lý kế thừa Điều phối
XEM_DUOC = {
    "QUAN_LY": NHOM,
    "DIEU_PHOI": NHOM,
    "KE_TOAN": ("chuyen", "don", "khach_hang"),
    "TAI_XE": ("chuyen",),
}


def _nhom(db: Session, loc, cot, ra) -> dict:
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    return {"tong": tong, "ds": [ra(d) for d in db.execute(loc.order_by(*cot).limit(TOI_DA))]}


def _chuyen(db: Session, nd: NguoiDung, q: str) -> dict:
    loc = chuyen_service.truy_van_chuyen().where(
        or_(
            Chuyen.ma_chuyen.icontains(q, autoescape=True),
            Xe.bien_so.icontains(q, autoescape=True),
            NguoiDung.ho_ten.icontains(q, autoescape=True),
        )
    )
    if nd.vai_tro == "TAI_XE":  # chuyến của mình, trạng thái được xem như UC-17 (BR-58)
        tx = db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id))
        loc = loc.where(Chuyen.tai_xe_id == tx, Chuyen.trang_thai.in_(THAY_DUOC))
    return _nhom(
        db,
        loc,
        (Chuyen.khoi_hanh_du_kien.desc(), Chuyen.id.desc()),
        lambda d: {
            "id": d[0].id,
            "ma_chuyen": d[0].ma_chuyen,
            "trang_thai": d[0].trang_thai,
            "bien_so": d[3],
            "ten_tai_xe": d[4],
            "khoi_hanh_du_kien": d[0].khoi_hanh_du_kien,
        },
    )


def _don(db: Session, q: str) -> dict:
    d0 = don_service.DonHang
    loc = don_service.truy_van_don().where(
        or_(d0.ma_don.icontains(q, autoescape=True), don_service.KhachHang.ten.icontains(q, autoescape=True))
    )
    return _nhom(
        db,
        loc,
        (d0.tao_luc.desc(), d0.id.desc()),
        lambda d: {
            "id": d[0].id,
            "ma_don": d[0].ma_don,
            "trang_thai": d[0].trang_thai,
            "ten_khach": d[1],
            "tinh_lay": d[2],
            "tinh_giao": d[3],
        },
    )


def _xe(db: Session, q: str) -> dict:
    loc = select(Xe).where(Xe.bien_so.icontains(q, autoescape=True))
    return _nhom(
        db,
        loc,
        (Xe.bien_so,),
        lambda d: {"id": d[0].id, "bien_so": d[0].bien_so, "trang_thai": d[0].trang_thai},
    )


def _tai_xe(db: Session, q: str) -> dict:
    loc = (
        select(TaiXe, NguoiDung.ho_ten)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
        .where(NguoiDung.ho_ten.icontains(q, autoescape=True))
    )
    return _nhom(
        db,
        loc,
        (NguoiDung.ho_ten,),
        lambda d: {"id": d[0].id, "ho_ten": d[1], "trang_thai": d[0].trang_thai},
    )


def _khach(db: Session, q: str) -> dict:
    loc = select(KhachHang).where(
        or_(KhachHang.ten.icontains(q, autoescape=True), KhachHang.sdt.icontains(q, autoescape=True))
    )
    return _nhom(
        db,
        loc,
        (KhachHang.ten,),
        lambda d: {"id": d[0].id, "ten": d[0].ten, "sdt": d[0].sdt},
    )


def tim(db: Session, nd: NguoiDung, q: str) -> dict:
    q = unicodedata.normalize("NFC", q).strip()  # NFC: "bình" gõ kiểu tổ hợp vẫn khớp tên lưu dựng sẵn
    if len(q) < 2:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Từ khóa cần ít nhất 2 ký tự", 400)
    xem = XEM_DUOC[nd.vai_tro]
    cach = {
        "chuyen": lambda: _chuyen(db, nd, q),
        "don": lambda: _don(db, q),
        "xe": lambda: _xe(db, q),
        "tai_xe": lambda: _tai_xe(db, q),
        "khach_hang": lambda: _khach(db, q),
    }
    # Luôn đủ 5 khóa: nhóm không được xem trả rỗng, giao diện không phải đoán
    return {"q": q} | {n: cach[n]() if n in xem else {"tong": 0, "ds": []} for n in NHOM}
