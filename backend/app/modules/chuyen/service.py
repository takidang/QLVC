from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.chuyen import (
    LichChuyen,
    TaiXeXet,
    XeXet,
    ket_thuc_chay_rong,
    xet_gio_lai,
    xet_tai_xe,
    xet_trung_lich,
    xet_xe,
)
from app.loi import LoiNghiepVu
from app.models import Chuyen, LichSuTrangThai, NguoiDung, TaiXe, Tuyen, TuyenNut, Xe
from app.modules.chuyen.schemas import ChuyenVao
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.phan_trang import PhanTrang
from app.thoi_gian import GIO_VN, bay_gio

# Giờ lái của một chuyến = phút nút cuối của tuyến (BR-65)
_PHUT_TUYEN = (
    select(TuyenNut.tuyen_id, func.max(TuyenNut.phut_tu_diem_dau).label("phut")).group_by(TuyenNut.tuyen_id).subquery()
)


@dataclass
class KhungChuyen:
    """Chuyến định lập: tuyến, giờ, kết thúc dự kiến khi chưa có đơn, và giới hạn từ CFG."""

    tuyen: Tuyen
    phut_lai: int
    khoi_hanh: datetime
    ket_thuc: datetime
    gio_ngay: int
    gio_tuan: int

    @property
    def ngay_ket_thuc(self) -> date:
        # Ngày so hạn giấy tờ (BR-12, 13, 15) theo giờ Việt Nam (quyết định UC-11 số 1)
        return self.ket_thuc.astimezone(GIO_VN).date()


def _khung(db: Session, tuyen_id: int, khoi_hanh: datetime) -> KhungChuyen:
    tuyen = db.get(Tuyen, tuyen_id)
    if tuyen is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tuyến", 404)
    phut = db.scalar(select(_PHUT_TUYEN.c.phut).where(_PHUT_TUYEN.c.tuyen_id == tuyen_id)) or 0
    ngay, tuan, _ = (int(x) for x in cau_hinh.lay(db, "CFG-07").split("/"))
    dem = int(cau_hinh.lay(db, "CFG-05"))
    return KhungChuyen(tuyen, phut, khoi_hanh, ket_thuc_chay_rong(khoi_hanh, phut, dem), ngay, tuan)


def _lich(db: Session, cot, ids: list[int], k: KhungChuyen) -> dict[int, list[LichChuyen]]:
    """Chuyến khác HUY của các xe / tài xế này, chạm tới các tuần mà chuyến mới chạm (đủ cho BR-16…19)."""
    dau = k.khoi_hanh.astimezone(GIO_VN).date()
    tu = datetime.combine(dau - timedelta(days=dau.weekday()), time(), GIO_VN)
    cuoi = max(k.ket_thuc, k.khoi_hanh + timedelta(minutes=k.phut_lai)).astimezone(GIO_VN).date()
    den = datetime.combine(cuoi + timedelta(days=7 - cuoi.weekday()), time(), GIO_VN)
    dong = db.execute(
        select(cot, Chuyen.ma_chuyen, Chuyen.khoi_hanh_du_kien, Chuyen.ket_thuc_du_kien, _PHUT_TUYEN.c.phut)
        .join(_PHUT_TUYEN, _PHUT_TUYEN.c.tuyen_id == Chuyen.tuyen_id)
        .where(
            cot.in_(ids),
            Chuyen.trang_thai != "HUY",
            Chuyen.khoi_hanh_du_kien < den,
            Chuyen.ket_thuc_du_kien > tu,
        )
    ).all()
    ket_qua: dict[int, list[LichChuyen]] = {i: [] for i in ids}
    for id_, ma, kh, kt, phut in dong:
        ket_qua[id_].append(LichChuyen(ma, kh, kt, phut))
    return ket_qua


def _xet_xe(db: Session, k: KhungChuyen, ds: list[Xe]) -> dict[int, list[dict]]:
    lich = _lich(db, Chuyen.xe_id, [x.id for x in ds], k)
    return {
        x.id: xet_xe(XeXet(x.bien_so, x.trang_thai, x.han_dang_kiem, x.han_bao_hiem), k.ngay_ket_thuc)
        + xet_trung_lich("BR-16", f"Xe {x.bien_so}", k.khoi_hanh, k.ket_thuc, lich[x.id])
        for x in ds
    }


def _xet_tai_xe(db: Session, k: KhungChuyen, ds: list[tuple[TaiXe, str]], ktt_xe: int | None) -> dict[int, list[dict]]:
    lich = _lich(db, Chuyen.tai_xe_id, [tx.id for tx, _ in ds], k)
    return {
        tx.id: xet_tai_xe(TaiXeXet(ten, tx.trang_thai, tx.hang_gplx, tx.han_gplx), k.ngay_ket_thuc, ktt_xe)
        + xet_trung_lich("BR-17", f"Tài xế {ten}", k.khoi_hanh, k.ket_thuc, lich[tx.id])
        + xet_gio_lai(f"Tài xế {ten}", k.khoi_hanh, k.phut_lai, lich[tx.id], k.gio_ngay, k.gio_tuan)
        for tx, ten in ds
    }


def xe_kha_dung(db: Session, tuyen_id: int, khoi_hanh: datetime) -> list[dict]:
    k = _khung(db, tuyen_id, khoi_hanh)
    ds = list(db.scalars(select(Xe).order_by(Xe.bien_so)))
    vp = _xet_xe(db, k, ds)
    ket_qua = [
        {
            **{c: getattr(x, c) for c in ("id", "bien_so", "tai_trong_kg", "the_tich_m3", "ktt_toan_bo_kg")},
            "kha_dung": not vp[x.id],
            "ly_do": vp[x.id],
        }
        for x in ds
    ]
    return sorted(ket_qua, key=lambda x: not x["kha_dung"])  # khả dụng trước, giữ thứ tự biển số


def tai_xe_kha_dung(db: Session, tuyen_id: int, khoi_hanh: datetime, xe_id: int | None) -> list[dict]:
    k = _khung(db, tuyen_id, khoi_hanh)
    ktt = None
    if xe_id is not None:  # có xe thì lọc thêm BR-14 (quyết định UC-11 số 6)
        xe = db.get(Xe, xe_id)
        if xe is None:
            raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy xe", 404)
        ktt = xe.ktt_toan_bo_kg
    ds = list(db.execute(select(TaiXe, NguoiDung.ho_ten).join(NguoiDung).order_by(NguoiDung.ho_ten)).all())
    vp = _xet_tai_xe(db, k, ds, ktt)
    ket_qua = [
        {
            "id": tx.id,
            "ho_ten": ten,
            "hang_gplx": tx.hang_gplx,
            "han_gplx": tx.han_gplx,
            "kha_dung": not vp[tx.id],
            "ly_do": vp[tx.id],
        }
        for tx, ten in ds
    ]
    return sorted(ket_qua, key=lambda x: not x["kha_dung"])


def tao(db: Session, vao: ChuyenVao, nguoi: NguoiDung) -> int:
    k = _khung(db, vao.tuyen_id, vao.khoi_hanh_du_kien)
    if k.tuyen.trang_thai != "HOAT_DONG":
        raise LoiNghiepVu("TUYEN_NGUNG", f"Tuyến {k.tuyen.ma} đã ngừng, không lập chuyến được")
    if k.khoi_hanh <= bay_gio():
        raise LoiNghiepVu("KHOI_HANH_DA_QUA", "Giờ khởi hành đã qua, không lập chuyến được")
    # Khóa dòng xe rồi tài xế (thứ tự cố định): người lập sau phải đợi, rồi thấy chuyến vừa lập (BR-16, 17)
    xe = db.get(Xe, vao.xe_id, with_for_update=True)
    if xe is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy xe", 404)
    tx = db.get(TaiXe, vao.tai_xe_id, with_for_update=True)
    if tx is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tài xế", 404)
    ten = db.get(NguoiDung, tx.nguoi_dung_id).ho_ten

    vp = _xet_xe(db, k, [xe])[xe.id] + _xet_tai_xe(db, k, [(tx, ten)], xe.ktt_toan_bo_kg)[tx.id]
    if vp:
        # Báo mọi vi phạm một lần, mã là BR đầu tiên (quyết định UC-11 số 4)
        raise LoiNghiepVu(vp[0]["ma"], "Không lập được chuyến", chi_tiet=vp)

    # Mã CH-yyMMdd-NN theo ngày khởi hành; khóa theo ngày để hai người lập cùng lúc không trùng số
    ngay = k.khoi_hanh.astimezone(GIO_VN).strftime("%y%m%d")
    db.execute(select(func.pg_advisory_xact_lock(int(ngay))))
    so = db.scalar(select(func.count()).where(Chuyen.ma_chuyen.startswith(f"CH-{ngay}-")))
    chuyen = Chuyen(
        ma_chuyen=f"CH-{ngay}-{so + 1:02d}",
        tuyen_id=k.tuyen.id,
        xe_id=xe.id,
        tai_xe_id=tx.id,
        khoi_hanh_du_kien=k.khoi_hanh,
        ket_thuc_du_kien=k.ket_thuc,
        dieu_phoi_id=nguoi.id,
    )
    db.add(chuyen)
    db.flush()
    db.add(LichSuTrangThai(doi_tuong="CHUYEN", doi_tuong_id=chuyen.id, tu=None, sang="LAP", nguoi=nguoi.id))
    db.commit()
    return chuyen.id


_CHON = (Chuyen, Tuyen.ma, Tuyen.ten, Xe.bien_so, NguoiDung.ho_ten)


def _truy_van():
    return (
        select(*_CHON)
        .join(Tuyen, Tuyen.id == Chuyen.tuyen_id)
        .join(Xe, Xe.id == Chuyen.xe_id)
        .join(TaiXe, TaiXe.id == Chuyen.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
    )


def _ra(dong) -> dict:
    c, ma_tuyen, ten_tuyen, bien_so, ten_tai_xe = dong
    return {
        **{
            k: getattr(c, k)
            for k in (
                "id",
                "ma_chuyen",
                "tuyen_id",
                "xe_id",
                "tai_xe_id",
                "khoi_hanh_du_kien",
                "ket_thuc_du_kien",
                "trang_thai",
            )
        },
        "ma_tuyen": ma_tuyen,
        "ten_tuyen": ten_tuyen,
        "bien_so": bien_so,
        "ten_tai_xe": ten_tai_xe,
    }


def lay(db: Session, chuyen_id: int) -> dict:
    dong = db.execute(_truy_van().where(Chuyen.id == chuyen_id)).first()
    if dong is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return _ra(dong)


def danh_sach(
    db: Session, pt: PhanTrang, trang_thai: str | None, ngay: date | None, tuyen_id: int | None
) -> tuple[list[dict], int]:
    loc = _truy_van()
    if trang_thai:
        loc = loc.where(Chuyen.trang_thai == trang_thai)
    if ngay:  # ngày khởi hành theo giờ Việt Nam
        dau = datetime.combine(ngay, time(), GIO_VN)
        loc = loc.where(Chuyen.khoi_hanh_du_kien >= dau, Chuyen.khoi_hanh_du_kien < dau + timedelta(days=1))
    if tuyen_id:
        loc = loc.where(Chuyen.tuyen_id == tuyen_id)
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    dong = db.execute(
        loc.order_by(Chuyen.khoi_hanh_du_kien.desc(), Chuyen.id.desc()).offset(pt.bo_qua).limit(pt.so_dong)
    )
    return [_ra(d) for d in dong], tong
