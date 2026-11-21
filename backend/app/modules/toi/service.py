"""Trang tài xế: chuyến được giao, lịch trình (UC-17); bắt đầu / kết thúc chuyến (UC-18). Chỉ chuyến của mình."""

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app import luu_tru
from app.domain.chuyen import TaiXeXet, XeXet, xet_tai_xe, xet_xe
from app.domain.lich_trinh import lich_trinh
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, NguoiDung, TaiXe, Tep, Xe
from app.modules.chuyen.service import don_ghep, ngu_canh, ra_chuyen, truy_van_chuyen
from app.modules.don.service import truy_van_don
from app.phan_trang import PhanTrang
from app.thoi_gian import GIO_VN, bay_gio, hom_nay_vn

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
    loc = truy_van_chuyen().where(Chuyen.tai_xe_id == _tai_xe_id(db, nd), Chuyen.trang_thai.in_(NHOM[nhom]))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    if nhom == "can_lam":  # chuyến đang chạy lên đầu, rồi chuyến sắp chạy sớm trước
        thu_tu = (case((Chuyen.trang_thai == "DANG_CHAY", 0), else_=1), Chuyen.khoi_hanh_du_kien, Chuyen.id)
    else:
        thu_tu = (Chuyen.khoi_hanh_du_kien.desc(), Chuyen.id.desc())
    dong = db.execute(loc.add_columns(so_don).order_by(*thu_tu).offset(pt.bo_qua).limit(pt.so_dong))
    return [ra_chuyen(d[:-1]) | {"so_don": d[-1]} for d in dong], tong


def _chuyen_cua_toi(db: Session, nd: NguoiDung, chuyen_id: int, khoa: bool = False) -> Chuyen:
    c = db.get(Chuyen, chuyen_id, with_for_update=khoa)
    # Chuyến người khác, chuyến LAP/HUY, id không có: cùng một 404, không lộ chuyến có tồn tại (BR-58, IDOR)
    if c is None or c.tai_xe_id != _tai_xe_id(db, nd) or c.trang_thai not in THAY_DUOC:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return c


def chi_tiet(db: Session, nd: NguoiDung, chuyen_id: int) -> dict:
    c = _chuyen_cua_toi(db, nd, chuyen_id)

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
    # Đơn đã quét lấy trong chính chuyến này: điểm Lấy của đơn giao thất bại vẫn là "Đã lấy" (góp ý #21).
    # Đếm theo chuyến, không theo đơn: đơn ghép lại (BR-69) có thể đã lấy ở chuyến trước
    da_lay = set(
        db.scalars(
            select(Ghep.don_hang_id)
            .join(LuotQuet, LuotQuet.ghep_id == Ghep.id)
            .where(Ghep.chuyen_id == chuyen_id, LuotQuet.loai == "LAY")
        )
    )
    nc = ngu_canh(db, c)
    diem = lich_trinh(c.khoi_hanh_du_kien, nc.thu_tu, nc.phut, [don_ghep(d) for d in don.values()], nc.cfg08)

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
            "da_lay": d.id in da_lay,
            # Đơn ghép lại sau khi đã lấy: lấy ở nơi đang giữ hàng (BR-69)
            "dia_chi": (d.dia_chi_giu or d.dia_chi_lay) if lay else d.dia_chi_giao,
            "nguoi_lien_he": d.nguoi_lien_he_lay if lay else d.nguoi_nhan,
            "sdt": d.sdt_lay if lay else d.sdt_nhan,
            "lay_tu": d.lay_tu,
            "lay_den": d.lay_den,
            "han_giao": d.han_giao,
        }

    goc = ra_chuyen(db.execute(truy_van_chuyen().where(Chuyen.id == chuyen_id)).one())
    return goc | {
        "so_don": len(don),
        "luong_tai_xe_chot": c.luong_tai_xe_chot,
        "lich_trinh": [ra_diem(i, p) for i, p in enumerate(diem, start=1)],
    }


# ---------- UC-18: bắt đầu / kết thúc chuyến ----------


def _can_trang_thai(c: Chuyen, can: str, viec: str) -> None:
    if c.trang_thai != can:
        raise LoiNghiepVu("SAI_TRANG_THAI", f"Chuyến {c.ma_chuyen} đang {c.trang_thai}, không {viec} được", 409)


def _chuyen_trang_thai(db: Session, c: Chuyen, nd: NguoiDung, sang: str, anh: bytes, duoi: str, loai: str) -> None:
    """Ghi ảnh đồng hồ và đổi trạng thái trong cùng giao dịch; CSDL lỗi thì xóa file vừa ghi (không để ảnh mồ côi)."""
    ten = luu_tru.luu(anh, duoi)
    try:
        db.add(Tep(chuyen_id=c.id, loai=loai, duong_dan=ten, kich_thuoc=len(anh)))
        db.add(LichSuTrangThai(doi_tuong="CHUYEN", doi_tuong_id=c.id, tu=c.trang_thai, sang=sang, nguoi=nd.id))
        c.trang_thai = sang
        db.commit()
    except Exception:
        db.rollback()
        luu_tru.xoa(ten)
        raise


def bat_dau(db: Session, nd: NguoiDung, chuyen_id: int, km: int, anh: bytes) -> None:
    duoi = luu_tru.kiem_anh(anh)
    c = _chuyen_cua_toi(db, nd, chuyen_id, khoa=True)  # bấm hai lần: lần sau đợi rồi thấy DANG_CHAY → 409
    _can_trang_thai(c, "DA_CHOT", "bắt đầu")
    if c.khoi_hanh_du_kien.astimezone(GIO_VN).date() != hom_nay_vn():  # sớm giờ trong cùng ngày vẫn được
        ngay = c.khoi_hanh_du_kien.astimezone(GIO_VN).strftime("%d/%m/%Y")
        raise LoiNghiepVu("BR-26", f"Chuyến {c.ma_chuyen} chạy ngày {ngay}, chỉ bắt đầu được trong ngày đó")

    xe = db.get(Xe, c.xe_id, with_for_update=True)
    tx = db.get(TaiXe, c.tai_xe_id, with_for_update=True)
    # BR-26: xe và tài xế không có chuyến khác đang chạy (chuyến trước chạy trễ phải kết thúc trước)
    dang_chay = db.scalar(
        select(Chuyen)
        .where(
            Chuyen.id != c.id,
            Chuyen.trang_thai == "DANG_CHAY",
            or_(Chuyen.xe_id == c.xe_id, Chuyen.tai_xe_id == c.tai_xe_id),
        )
        .limit(1)
    )
    if dang_chay is not None:
        if dang_chay.xe_id == c.xe_id:
            tb = f"Xe {xe.bien_so} đang chạy chuyến {dang_chay.ma_chuyen}, chờ chuyến đó kết thúc rồi bắt đầu"
        else:
            tb = f"Bạn đang chạy chuyến {dang_chay.ma_chuyen}, kết thúc chuyến đó trước"
        raise LoiNghiepVu("BR-26", tb, 409)

    # Giấy tờ có thể hết hạn sau lúc lập chuyến: kiểm lại BR-11…15 bằng đúng hàm của UC-11
    ngay_ket_thuc = c.ket_thuc_du_kien.astimezone(GIO_VN).date()
    vp = xet_xe(XeXet(xe.bien_so, xe.trang_thai, xe.han_dang_kiem, xe.han_bao_hiem), ngay_ket_thuc) + xet_tai_xe(
        TaiXeXet(nd.ho_ten, tx.trang_thai, tx.hang_gplx, tx.han_gplx), ngay_ket_thuc, xe.ktt_toan_bo_kg
    )
    if vp:
        raise LoiNghiepVu(vp[0]["ma"], "Không bắt đầu được chuyến, báo Điều phối", chi_tiet=vp)

    # BR-70: km chỉ tăng. Sàn = km đồng hồ của xe (cập nhật mỗi lần kết thúc) và km bắt đầu các chuyến trước
    # (chuyến kết thúc do sự cố không có km cuối – quyết định UC-18 số 3)
    km_truoc = db.scalar(select(func.max(Chuyen.km_bat_dau)).where(Chuyen.xe_id == xe.id, Chuyen.id != c.id))
    san = max(xe.km_dong_ho, km_truoc or 0)
    if km < san:
        raise LoiNghiepVu("BR-70", f"Km bắt đầu {km:,} nhỏ hơn km đã ghi của xe {xe.bien_so} ({san:,})")

    c.km_bat_dau, c.khoi_hanh_thuc_te = km, bay_gio()  # giờ máy chủ, không nhận giờ từ điện thoại
    _chuyen_trang_thai(db, c, nd, "DANG_CHAY", anh, duoi, "ANH_KM_BAT_DAU")


def ket_thuc(db: Session, nd: NguoiDung, chuyen_id: int, km: int, anh: bytes) -> None:
    duoi = luu_tru.kiem_anh(anh)
    c = _chuyen_cua_toi(db, nd, chuyen_id, khoa=True)
    _can_trang_thai(c, "DANG_CHAY", "kết thúc")

    ghep = db.execute(
        select(Ghep, DonHang.ma_don, DonHang.trang_thai)
        .join(DonHang, DonHang.id == Ghep.don_hang_id)
        .where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)
        .order_by(DonHang.ma_don)
    ).all()
    con = [ma for _, ma, tt in ghep if tt not in ("DA_GIAO", "THAT_BAI")]
    if con:
        raise LoiNghiepVu(
            "BR-28",
            f"Còn {len(con)} đơn chưa giao hoặc báo thất bại: {', '.join(con)}",
            chi_tiet=[{"ma": "BR-28", "thong_diep": f"Đơn {ma} chưa có kết quả", "ma_don": ma} for ma in con],
        )
    if c.km_bat_dau is not None and km <= c.km_bat_dau:
        raise LoiNghiepVu("BR-70", f"Km kết thúc {km:,} phải lớn hơn km bắt đầu {c.km_bat_dau:,}")

    for g, _, tt in ghep:
        g.ket_qua = g.ket_qua or tt  # để lịch sử chuyến còn thấy đơn thất bại (quyết định UC-18 số 4)
        if tt == "THAT_BAI":
            g.hieu_luc = False  # BR-36: Điều phối ghép lại / trả hàng / hủy
    db.get(Xe, c.xe_id, with_for_update=True).km_dong_ho = km  # BR-70
    c.km_ket_thuc, c.ket_thuc_thuc_te = km, bay_gio()
    _chuyen_trang_thai(db, c, nd, "HOAN_THANH", anh, duoi, "ANH_KM_KET_THUC")
