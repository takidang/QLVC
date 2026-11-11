"""UC-27 bảng cảnh báo cho Điều phối: chỉ đọc, tính lại mỗi lần mở (không có "đã xem").

Năm nhóm: giấy tờ (BR-21), chuyến trễ / chồng lịch (BR-73, dùng lại cách tính UC-32), sự cố đang mở,
đơn chờ ghép sắp quá hạn (CFG-10), lượt quét thiếu GPS (BR-43).
"""

from datetime import timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Chuyen, DonHang, Ghep, KhachHang, LuotQuet, NguoiDung, Nut, SuCo, TaiXe, Xe
from app.modules.chuyen.theo_doi import _theo_doi
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.thoi_gian import GIO_VN, bay_gio

GIO_THIEU_GPS = 24  # chuyến kết thúc quá 24 giờ thì cảnh báo thiếu GPS không còn việc để làm (quyết định 5)


def _giay_to(db: Session, hom_nay, so_ngay: int) -> list[dict]:
    moc = hom_nay + timedelta(days=so_ngay)  # tính cả ngày thứ CFG-02 (BR-21)
    ra = []

    def them(doi_tuong, id_, ten, loai, han):
        ra.append(
            {
                "doi_tuong": doi_tuong,
                "id": id_,
                "ten": ten,
                "loai": loai,
                "han": han,
                "con_ngay": (han - hom_nay).days,
                "het_han": han < hom_nay,
            }
        )

    for x in db.scalars(
        select(Xe).where(Xe.trang_thai == "HOAT_DONG", or_(Xe.han_dang_kiem <= moc, Xe.han_bao_hiem <= moc))
    ):
        if x.han_dang_kiem <= moc:
            them("XE", x.id, x.bien_so, "DANG_KIEM", x.han_dang_kiem)
        if x.han_bao_hiem <= moc:
            them("XE", x.id, x.bien_so, "BAO_HIEM", x.han_bao_hiem)
    for tx, ten in db.execute(
        select(TaiXe, NguoiDung.ho_ten)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
        .where(TaiXe.trang_thai == "HOAT_DONG", TaiXe.han_gplx <= moc)
    ):
        them("TAI_XE", tx.id, ten, "GPLX", tx.han_gplx)
    return sorted(ra, key=lambda g: (g["han"], g["doi_tuong"], g["ten"]))  # hết hạn trước, rồi hạn gần trước


def _chuyen_tre(db: Session, nguong: int) -> list[dict]:
    ra = []
    for c, bien_so, ten in db.execute(
        select(Chuyen, Xe.bien_so, NguoiDung.ho_ten)
        .join(Xe, Xe.id == Chuyen.xe_id)
        .join(TaiXe, TaiXe.id == Chuyen.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
        .where(Chuyen.trang_thai == "DANG_CHAY")
        .order_by(Chuyen.khoi_hanh_du_kien, Chuyen.id)
    ):
        td = _theo_doi(db, c, nguong)  # cùng cách tính với bảng chuyến trong ngày (UC-32)
        if not {"TRE", "CHONG_LICH"} & set(td["co"]):
            continue
        da_quet = [p for p in td["diem"].values() if p["tre_phut"] is not None]
        gan_nhat = max(da_quet, key=lambda p: p["thuc_te"], default=None)
        ra.append(
            {
                "chuyen_id": c.id,
                "ma_chuyen": c.ma_chuyen,
                "bien_so": bien_so,
                "ten_tai_xe": ten,
                "tre_phut": gan_nhat["tre_phut"] if gan_nhat else None,  # lượt quét gần nhất, như BR-73
                "ket_thuc_dang_chay": td["ket_thuc_dang_chay"],
                "chong": td["chong"],
            }
        )
    return ra


def _su_co_mo(db: Session) -> list[dict]:
    dong = db.execute(
        select(SuCo, Chuyen.ma_chuyen, Xe.bien_so, NguoiDung.ho_ten)
        .join(Chuyen, Chuyen.id == SuCo.chuyen_id)
        .join(Xe, Xe.id == Chuyen.xe_id)
        .join(TaiXe, TaiXe.id == SuCo.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
        .where(SuCo.trang_thai == "MO")
        .order_by(SuCo.luc, SuCo.id)
    )
    return [
        {
            "su_co_id": sc.id,
            "chuyen_id": sc.chuyen_id,
            "ma_chuyen": ma,
            "bien_so": bien_so,
            "ten_tai_xe": ten,
            "loai": sc.loai,
            "ghi_chu": sc.ghi_chu,
            "luc": sc.luc,
        }
        for sc, ma, bien_so, ten in dong
    ]


def _don_sap_qua_han(db: Session, nay, so_gio: int) -> list[dict]:
    lay, giao = aliased(Nut), aliased(Nut)
    dong = db.execute(
        select(DonHang, KhachHang.ten, lay.tinh, giao.tinh)
        .join(KhachHang, KhachHang.id == DonHang.khach_hang_id)
        .join(lay, lay.id == DonHang.nut_lay_id)
        .join(giao, giao.id == DonHang.nut_giao_id)
        # "còn dưới" CFG-10 giờ: đúng bằng CFG-10 thì chưa báo; đã quá hạn vẫn hiện (quyết định 4)
        .where(DonHang.trang_thai == "CHO_GHEP", DonHang.han_giao < nay + timedelta(hours=so_gio))
        .order_by(DonHang.han_giao, DonHang.id)
    )
    return [
        {
            "don_id": d.id,
            "ma_don": d.ma_don,
            "ten_khach": ten_khach,
            "tinh_lay": tinh_lay,
            "tinh_giao": tinh_giao,
            "han_giao": d.han_giao,
            "con_phut": int((d.han_giao - nay).total_seconds() // 60),
            "qua_han": d.han_giao <= nay,
        }
        for d, ten_khach, tinh_lay, tinh_giao in dong
    ]


def _thieu_gps(db: Session, nay) -> list[dict]:
    dong = db.execute(
        select(Chuyen.id, Chuyen.ma_chuyen, NguoiDung.ho_ten, func.count(), func.max(LuotQuet.thoi_gian))
        .join(Ghep, Ghep.id == LuotQuet.ghep_id)
        .join(Chuyen, Chuyen.id == Ghep.chuyen_id)
        .join(TaiXe, TaiXe.id == Chuyen.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
        .where(
            LuotQuet.thieu_gps,
            or_(
                Chuyen.trang_thai == "DANG_CHAY",
                Chuyen.ket_thuc_thuc_te >= nay - timedelta(hours=GIO_THIEU_GPS),
            ),
        )
        .group_by(Chuyen.id, Chuyen.ma_chuyen, NguoiDung.ho_ten)
        .order_by(func.max(LuotQuet.thoi_gian).desc())
    )
    return [
        {"chuyen_id": i, "ma_chuyen": ma, "ten_tai_xe": ten, "so_luot": so, "luc_gan_nhat": luc}
        for i, ma, ten, so, luc in dong
    ]


def bang(db: Session) -> dict:
    nay = bay_gio()
    ch = {
        "ngay_bao_truoc": int(cau_hinh.lay(db, "CFG-02")),
        "nguong_tre_phut": int(cau_hinh.lay(db, "CFG-09")),
        "gio_cho_ghep": int(cau_hinh.lay(db, "CFG-10")),
    }
    nhom = {
        "giay_to": _giay_to(db, nay.astimezone(GIO_VN).date(), ch["ngay_bao_truoc"]),
        "chuyen_tre": _chuyen_tre(db, ch["nguong_tre_phut"]),
        "su_co_mo": _su_co_mo(db),
        "don_sap_qua_han": _don_sap_qua_han(db, nay, ch["gio_cho_ghep"]),
        "thieu_gps": _thieu_gps(db, nay),
    }
    return {"cau_hinh": ch, **nhom, "so_viec": sum(len(v) for v in nhom.values())}
