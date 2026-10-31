"""Trang tài xế (UC-17): chuyến được giao, lịch trình. Chỉ đọc; tài xế chỉ thấy chuyến của mình (BR-58)."""

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.domain.lich_trinh import lich_trinh
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, NguoiDung, TaiXe
from app.modules.chuyen.service import _don_ghep, _ngu_canh, _ra, _truy_van
from app.modules.don.service import truy_van_don
from app.phan_trang import PhanTrang

# Từ DA_CHOT trở đi; LAP (Điều phối còn sửa) và HUY không bao giờ hiện (quyết định UC-17 số 1)
NHOM = {"can_lam": ("DA_CHOT", "DANG_CHAY"), "da_xong": ("HOAN_THANH", "DA_QUYET_TOAN")}
THAY_DUOC = NHOM["can_lam"] + NHOM["da_xong"]

# Đơn của chuyến: ghép hiệu lực, cộng đơn đã có kết quả (đơn thất bại bị gỡ hiệu lực khi kết thúc, BR-36)
_DON_CUA_CHUYEN = or_(Ghep.hieu_luc, Ghep.ket_qua.is_not(None))


def _tai_xe_id(db: Session, nd: NguoiDung) -> int | None:
    return db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id))


def danh_sach(db: Session, nd: NguoiDung, nhom: str, pt: PhanTrang) -> tuple[list[dict], int]:
    so_don = (
        select(func.count()).where(Ghep.chuyen_id == Chuyen.id, _DON_CUA_CHUYEN).correlate(Chuyen).scalar_subquery()
    )
    loc = _truy_van().where(Chuyen.tai_xe_id == _tai_xe_id(db, nd), Chuyen.trang_thai.in_(NHOM[nhom]))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    if nhom == "can_lam":  # chuyến đang chạy lên đầu, rồi chuyến sắp chạy sớm trước
        thu_tu = (case((Chuyen.trang_thai == "DANG_CHAY", 0), else_=1), Chuyen.khoi_hanh_du_kien, Chuyen.id)
    else:
        thu_tu = (Chuyen.khoi_hanh_du_kien.desc(), Chuyen.id.desc())
    dong = db.execute(loc.add_columns(so_don).order_by(*thu_tu).offset(pt.bo_qua).limit(pt.so_dong))
    return [_ra(d[:-1]) | {"so_don": d[-1]} for d in dong], tong


def chi_tiet(db: Session, nd: NguoiDung, chuyen_id: int) -> dict:
    c = db.get(Chuyen, chuyen_id)
    # Chuyến người khác, chuyến LAP/HUY, id không có: cùng một 404, không lộ chuyến có tồn tại (BR-58, IDOR)
    if c is None or c.tai_xe_id != _tai_xe_id(db, nd) or c.trang_thai not in THAY_DUOC:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)

    dong = db.execute(
        truy_van_don()
        .add_columns(Ghep.eta_lay_ke_hoach, Ghep.eta_giao_ke_hoach)
        .join(Ghep, Ghep.don_hang_id == DonHang.id)
        .where(Ghep.chuyen_id == chuyen_id, _DON_CUA_CHUYEN)
        .order_by(DonHang.id)
    ).all()
    don = {d.id: d for d, *_ in dong}
    ten_khach = {d.id: k for d, k, *_ in dong}
    # Giờ dự kiến: ETA kế hoạch lưu lúc chốt (BR-71); chưa lưu thì tính theo lịch trình hiện tại (quyết định số 4)
    eta_kh = {(d.id, "LAY"): lay for d, *_, lay, _ in dong} | {(d.id, "GIAO"): giao for d, *_, giao in dong}
    nc = _ngu_canh(db, c)
    diem = lich_trinh(c.khoi_hanh_du_kien, nc.thu_tu, nc.phut, [_don_ghep(d) for d in don.values()], nc.cfg08)

    def ra_diem(i: int, p) -> dict:
        d = don[p.don.id]
        lay = p.viec == "LAY"
        return {
            "thu_tu": i,
            "nut": nc.ten_nut[p.nut],
            "viec": p.viec,
            "eta": eta_kh[(d.id, p.viec)] or p.eta,
            "don_id": d.id,
            "ma_don": d.ma_don,
            "ten_khach": ten_khach[d.id],
            "mo_ta": d.mo_ta,
            "kg": d.kg,
            "m3": d.m3,
            "so_kien": d.so_kien,
            "trang_thai_don": d.trang_thai,
            # Đơn ghép lại sau khi đã lấy: lấy ở nơi đang giữ hàng (BR-69)
            "dia_chi": (d.dia_chi_giu or d.dia_chi_lay) if lay else d.dia_chi_giao,
            "nguoi_lien_he": d.nguoi_lien_he_lay if lay else d.nguoi_nhan,
            "sdt": d.sdt_lay if lay else d.sdt_nhan,
            "lay_tu": d.lay_tu,
            "lay_den": d.lay_den,
            "han_giao": d.han_giao,
        }

    goc = _ra(db.execute(_truy_van().where(Chuyen.id == chuyen_id)).one())
    return goc | {
        "so_don": len(don),
        "luong_tai_xe_chot": c.luong_tai_xe_chot,
        "lich_trinh": [ra_diem(i, p) for i, p in enumerate(diem, start=1)],
    }
