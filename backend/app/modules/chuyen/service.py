from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
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
from app.domain.lich_trinh import (
    DonGhep,
    ket_thuc_du_kien,
    lai_du_kien,
    lich_trinh,
    ty_le_lap_day,
    xet_ghep,
    xet_tai,
)
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, NguoiDung, Nut, TaiXe, TamUng, Tuyen, TuyenNut, Xe
from app.modules.chuyen.schemas import ChuyenVao
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.modules.don.service import ra_don, truy_van_don
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


def _lich(db: Session, cot, ids: list[int], k: KhungChuyen, bo: int | None) -> dict[int, list[LichChuyen]]:
    """Chuyến khác HUY của các xe / tài xế này, chạm tới các tuần mà chuyến mới chạm (đủ cho BR-16…19).

    `bo`: id chuyến đang xét lại (ghép đơn), không so với chính nó."""
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
            Chuyen.id != (bo or 0),
        )
    ).all()
    ket_qua: dict[int, list[LichChuyen]] = {i: [] for i in ids}
    for id_, ma, kh, kt, phut in dong:
        ket_qua[id_].append(LichChuyen(ma, kh, kt, phut))
    return ket_qua


def _xet_xe(db: Session, k: KhungChuyen, ds: list[Xe], bo: int | None = None) -> dict[int, list[dict]]:
    lich = _lich(db, Chuyen.xe_id, [x.id for x in ds], k, bo)
    return {
        x.id: xet_xe(XeXet(x.bien_so, x.trang_thai, x.han_dang_kiem, x.han_bao_hiem), k.ngay_ket_thuc)
        + xet_trung_lich("BR-16", f"Xe {x.bien_so}", k.khoi_hanh, k.ket_thuc, lich[x.id])
        for x in ds
    }


def _xet_tai_xe(
    db: Session, k: KhungChuyen, ds: list[tuple[TaiXe, str]], ktt_xe: int | None, bo: int | None = None
) -> dict[int, list[dict]]:
    lich = _lich(db, Chuyen.tai_xe_id, [tx.id for tx, _ in ds], k, bo)
    return {
        tx.id: xet_tai_xe(TaiXeXet(ten, tx.trang_thai, tx.hang_gplx, tx.han_gplx), k.ngay_ket_thuc, ktt_xe)
        + xet_trung_lich("BR-17", f"Tài xế {ten}", k.khoi_hanh, k.ket_thuc, lich[tx.id])
        + xet_gio_lai(f"Tài xế {ten}", k.khoi_hanh, k.phut_lai, lich[tx.id], k.gio_ngay, k.gio_tuan)
        for tx, ten in ds
    }


def xe_kha_dung(db: Session, tuyen_id: int, khoi_hanh: datetime) -> list[dict]:
    return _ds_xe(db, _khung(db, tuyen_id, khoi_hanh))


def _ds_xe(db: Session, k: KhungChuyen, bo: int | None = None, don: list[DonGhep] = ()) -> list[dict]:
    ds = list(db.scalars(select(Xe).order_by(Xe.bien_so)))
    vp = _xet_xe(db, k, ds, bo)
    for x in ds:  # chuyến đã có đơn: xe mới phải chở đủ hàng (BR-01, 02 theo BR-67)
        vp[x.id] += xet_tai(list(don), x.tai_trong_kg, x.the_tich_m3)
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
    return _ds_tai_xe(db, _khung(db, tuyen_id, khoi_hanh), xe_id)


def _ds_tai_xe(db: Session, k: KhungChuyen, xe_id: int | None, bo: int | None = None) -> list[dict]:
    ktt = None
    if xe_id is not None:  # có xe thì lọc thêm BR-14 (quyết định UC-11 số 6)
        xe = db.get(Xe, xe_id)
        if xe is None:
            raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy xe", 404)
        ktt = xe.ktt_toan_bo_kg
    ds = list(db.execute(select(TaiXe, NguoiDung.ho_ten).join(NguoiDung).order_by(NguoiDung.ho_ten)).all())
    vp = _xet_tai_xe(db, k, ds, ktt, bo)
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


def truy_van_chuyen():
    return (
        select(*_CHON)
        .join(Tuyen, Tuyen.id == Chuyen.tuyen_id)
        .join(Xe, Xe.id == Chuyen.xe_id)
        .join(TaiXe, TaiXe.id == Chuyen.tai_xe_id)
        .join(NguoiDung, NguoiDung.id == TaiXe.nguoi_dung_id)
    )


def ra_chuyen(dong) -> dict:
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
    dong = db.execute(truy_van_chuyen().where(Chuyen.id == chuyen_id)).first()
    if dong is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return ra_chuyen(dong)


def danh_sach(
    db: Session, pt: PhanTrang, trang_thai: str | None, ngay: date | None, tuyen_id: int | None
) -> tuple[list[dict], int]:
    loc = truy_van_chuyen()
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
    return [ra_chuyen(d) for d in dong], tong


# ---------- UC-13: ghép / gỡ đơn, chi tiết chuyến ----------


@dataclass
class NguCanh:
    """Những gì cần để tính lịch trình một chuyến: nút tuyến, xe, CFG."""

    chuyen: Chuyen
    tuyen: Tuyen
    xe: Xe
    thu_tu: dict[int, int]
    phut: dict[int, int]
    ten_nut: dict[int, str]
    cfg08: int
    cfg05: int

    @property
    def phut_tuyen(self) -> int:
        return max(self.phut.values(), default=0)


def ngu_canh(db: Session, chuyen: Chuyen, xe: Xe | None = None) -> NguCanh:
    nut = db.execute(
        select(TuyenNut.nut_id, TuyenNut.thu_tu, TuyenNut.phut_tu_diem_dau, Nut.ten)
        .join(Nut, Nut.id == TuyenNut.nut_id)
        .where(TuyenNut.tuyen_id == chuyen.tuyen_id)
    ).all()
    return NguCanh(
        chuyen,
        db.get(Tuyen, chuyen.tuyen_id),
        xe or db.get(Xe, chuyen.xe_id),
        {n: t for n, t, _, _ in nut},
        {n: p for n, _, p, _ in nut},
        {n: ten for n, _, _, ten in nut},
        int(cau_hinh.lay(db, "CFG-08")),
        int(cau_hinh.lay(db, "CFG-05")),
    )


def don_ghep(d: DonHang) -> DonGhep:
    # Đơn ghép lại sau khi đã lấy hàng: điểm lấy là nơi giữ hàng (BR-69)
    return DonGhep(
        d.id, d.ma_don, d.kg, d.m3, d.nut_giu_id or d.nut_lay_id, d.nut_giao_id, d.lay_tu, d.lay_den, d.han_giao
    )


def _dong_don_cua_chuyen(db: Session, chuyen_id: int) -> list:
    """Đơn của chuyến, dạng dòng của `truy_van_don` (có tên khách, tỉnh): ghép còn hiệu lực, hoặc đã có kết quả
    (đơn thất bại của chuyến đã kết thúc hết hiệu lực theo BR-36 nhưng vẫn thuộc chuyến – UC-32 quyết định 4)."""
    return db.execute(
        truy_van_don()
        .join(Ghep, Ghep.don_hang_id == DonHang.id)
        .where(Ghep.chuyen_id == chuyen_id, or_(Ghep.hieu_luc, Ghep.ket_qua.is_not(None)))
        .order_by(DonHang.id)
    ).all()


def chi_tiet(db: Session, chuyen_id: int) -> dict:
    """Tổng quan + thẻ Hàng (UC-13): tải, thể tích, % đầy, lịch trình BR-63, lãi dự kiến BR-52, đơn đang ghép."""
    goc = lay(db, chuyen_id)
    c = db.get(Chuyen, chuyen_id)
    nc = ngu_canh(db, c)
    dong = _dong_don_cua_chuyen(db, chuyen_id)
    don = [d for d, *_ in dong]
    diem = lich_trinh(c.khoi_hanh_du_kien, nc.thu_tu, nc.phut, [don_ghep(d) for d in don], nc.cfg08)
    kg, m3 = sum((d.kg for d in don), Decimal(0)), sum((d.m3 for d in don), Decimal(0))
    t = nc.tuyen
    # Khi LAP lấy định mức, lương từ tuyến; từ khi chốt lấy số đã chốt (BR-71)
    if c.dm_dau_chot is not None:
        dinh_muc, luong = c.dm_dau_chot + c.dm_cau_duong_chot + c.dm_boc_xep_chot, c.luong_tai_xe_chot
    else:
        dinh_muc, luong = t.dm_dau + t.dm_cau_duong + t.dm_boc_xep, t.dm_luong_tai_xe
    lai = lai_du_kien([d.cuoc_tinh for d in don], dinh_muc, luong)
    return goc | {
        "tai_trong": {"da_dung_kg": kg, "toi_da_kg": nc.xe.tai_trong_kg},
        "the_tich": {"da_dung_m3": m3, "toi_da_m3": nc.xe.the_tich_m3},
        "ty_le_lap_day": ty_le_lap_day(kg, m3, nc.xe.tai_trong_kg, nc.xe.the_tich_m3),
        "lich_trinh": [
            {
                "thu_tu": i,
                "nut": nc.ten_nut[d.nut],
                "viec": d.viec,
                "don_id": d.don.id,
                "ma_don": d.don.ma_don,
                "eta": d.eta,
            }
            for i, d in enumerate(diem, start=1)
        ],
        "lai_du_kien": lai,
        "canh_bao_lai_am": lai < 0,  # chỉ cảnh báo khi ghép; xác nhận ở lúc chốt (quyết định UC-13 số 6)
        "chay_rong": c.chay_rong,
        "don": [ra_don(d) for d in dong],
    }


_TEN_TRANG_THAI = {"LAP": "Đang lập", "DA_CHOT": "Đã chốt"}


def _khoa_chuyen(db: Session, chuyen_id: int, can: str = "LAP", viec: str = "thay đổi") -> tuple[Chuyen, Xe, TaiXe]:
    """Khóa chuyến rồi xe, tài xế (cùng thứ tự với lập chuyến) để hai thao tác trên một chuyến chạy lần lượt."""
    c = db.get(Chuyen, chuyen_id, with_for_update=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai != can:
        raise LoiNghiepVu(
            "BR-09", f"Chuyến {c.ma_chuyen} không ở trạng thái {_TEN_TRANG_THAI[can]}, không {viec} được", 409
        )
    return c, db.get(Xe, c.xe_id, with_for_update=True), db.get(TaiXe, c.tai_xe_id, with_for_update=True)


def _doi_trang_thai(db: Session, don: list[DonHang], sang: str, nguoi: NguoiDung, ly_do: str | None = None) -> None:
    for d in don:
        db.add(
            LichSuTrangThai(doi_tuong="DON", doi_tuong_id=d.id, tu=d.trang_thai, sang=sang, ly_do=ly_do, nguoi=nguoi.id)
        )
        d.trang_thai = sang


def ghep(db: Session, chuyen_id: int, don_ids: list[int], nguoi: NguoiDung) -> dict:
    c, xe, tx = _khoa_chuyen(db, chuyen_id)
    ids = set(don_ids)
    moi = list(db.scalars(select(DonHang).where(DonHang.id.in_(ids)).order_by(DonHang.id).with_for_update()))
    if thieu := sorted(ids - {d.id for d in moi}):
        raise LoiNghiepVu("KHONG_TIM_THAY", f"Không tìm thấy đơn {thieu}", 404)
    if sai := [d.ma_don for d in moi if d.trang_thai != "CHO_GHEP"]:
        raise LoiNghiepVu("BR-09", f"Đơn {', '.join(sai)} không ở trạng thái Chờ ghép (có thể vừa được ghép)", 409)

    cu = [d for d, *_ in _dong_don_cua_chuyen(db, c.id)]
    ket_thuc, vp = xet_ca_chuyen(db, c, xe, tx, cu + moi, ids)
    if vp:
        # Không ghép đơn nào trong lô (UC-13 ngoại lệ 3a)
        raise LoiNghiepVu("VI_PHAM_GHEP", "Có đơn vi phạm quy tắc ghép, chưa ghép đơn nào", chi_tiet=vp)

    db.add_all(Ghep(chuyen_id=c.id, don_hang_id=d.id) for d in moi)
    _doi_trang_thai(db, moi, "DA_GHEP", nguoi)
    c.ket_thuc_du_kien = ket_thuc  # để lập chuyến khác thấy đúng khoảng chiếm (quyết định UC-13 số 4)
    try:
        db.commit()
    except IntegrityError:  # lớp chặn cuối: chỉ mục unique một ghép hiệu lực mỗi đơn
        db.rollback()
        raise LoiNghiepVu("BR-07", "Đơn vừa được ghép vào chuyến khác, tải lại danh sách", 409) from None
    return chi_tiet(db, c.id)


def xet_ca_chuyen(
    db: Session, c: Chuyen, xe: Xe, tx: TaiXe, don: list[DonHang], moi: set[int]
) -> tuple[datetime, list[dict]]:
    """Kiểm cả chuyến với danh sách đơn `don` (BR-67): BR-01…06, giấy tờ theo ngày kết thúc mới, trùng lịch theo
    khoảng chiếm mới. Dùng cho ghép (UC-13) và sửa đơn đang ghép (UC-10). Trả (kết thúc dự kiến, vi phạm)."""
    nc = ngu_canh(db, c, xe)
    diem, vp = xet_ghep(
        [don_ghep(d) for d in don],
        moi,
        nc.thu_tu,
        nc.phut,
        c.khoi_hanh_du_kien,
        nc.cfg08,
        xe.tai_trong_kg,
        xe.the_tich_m3,
    )
    ket_thuc = ket_thuc_du_kien(c.khoi_hanh_du_kien, nc.phut_tuyen, diem, nc.cfg08, nc.cfg05)
    # Kết thúc dự kiến lùi: kiểm lại giấy tờ theo ngày kết thúc mới, trùng lịch theo khoảng chiếm mới (BR-67)
    k = replace(_khung(db, c.tuyen_id, c.khoi_hanh_du_kien), ket_thuc=ket_thuc)
    ten = db.get(NguoiDung, tx.nguoi_dung_id).ho_ten
    vp += [v for v in _xet_xe(db, k, [xe], c.id)[xe.id] if v["ma"] in ("BR-12", "BR-13", "BR-16")]
    vp += [v for v in _xet_tai_xe(db, k, [(tx, ten)], None, c.id)[tx.id] if v["ma"] in ("BR-15", "BR-17")]
    return ket_thuc, vp


def go(db: Session, chuyen_id: int, don_ids: list[int], nguoi: NguoiDung) -> dict:
    c, xe, _ = _khoa_chuyen(db, chuyen_id)
    ids = set(don_ids)
    cu = list(
        db.scalars(
            select(DonHang)
            .join(Ghep, Ghep.don_hang_id == DonHang.id)
            .where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)
            .order_by(DonHang.id)
            .with_for_update(of=DonHang)
        )
    )
    if la := sorted(ids - {d.id for d in cu}):
        raise LoiNghiepVu("DON_KHONG_THUOC_CHUYEN", f"Đơn {la} không đang ghép trong chuyến {c.ma_chuyen}")
    go_da_khoa(db, c, xe, cu, ids, nguoi)
    db.commit()
    return chi_tiet(db, c.id)


def go_da_khoa(
    db: Session,
    c: Chuyen,
    xe: Xe,
    cu: list[DonHang],
    ids: set[int],
    nguoi: NguoiDung,
    ly_do: str | None = None,
    ma_loi: str = "VI_PHAM_GO",
) -> None:
    """Gỡ `ids` khỏi chuyến đã khóa (`cu`: đơn đang ghép đã khóa); chưa commit. Dùng ở gỡ (UC-13), hủy đơn (UC-10)."""
    nc = ngu_canh(db, c, xe)
    # Gỡ làm ETA phía sau sớm lên, có thể rơi trước khung giờ lấy (ghi chú BR-67). Kết thúc chỉ sớm đi
    # nên không cần kiểm lại giấy tờ, trùng lịch.
    diem, vp = xet_ghep(
        [don_ghep(d) for d in cu if d.id not in ids],
        set(),
        nc.thu_tu,
        nc.phut,
        c.khoi_hanh_du_kien,
        nc.cfg08,
        xe.tai_trong_kg,
        xe.the_tich_m3,
    )
    if vp:
        raise LoiNghiepVu(ma_loi, "Gỡ đơn làm đơn khác vi phạm quy tắc, chưa gỡ đơn nào", chi_tiet=vp)

    db.execute(
        update(Ghep).where(Ghep.chuyen_id == c.id, Ghep.don_hang_id.in_(ids), Ghep.hieu_luc).values(hieu_luc=False)
    )
    _doi_trang_thai(db, [d for d in cu if d.id in ids], "CHO_GHEP", nguoi, ly_do)
    c.ket_thuc_du_kien = ket_thuc_du_kien(c.khoi_hanh_du_kien, nc.phut_tuyen, diem, nc.cfg08, nc.cfg05)


def don_phu_hop(db: Session, chuyen_id: int) -> list[dict]:
    """Đơn CHO_GHEP có điểm lấy (hoặc nơi giữ hàng) và điểm giao thuộc tuyến, đúng chiều (BR-03, 04)."""
    c = db.get(Chuyen, chuyen_id)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    nc = ngu_canh(db, c)
    nut_lay = func.coalesce(DonHang.nut_giu_id, DonHang.nut_lay_id)
    dong = db.execute(
        truy_van_don()
        .where(DonHang.trang_thai == "CHO_GHEP", nut_lay.in_(nc.thu_tu), DonHang.nut_giao_id.in_(nc.thu_tu))
        .order_by(DonHang.han_giao, DonHang.id)
        .limit(200)  # shortcut: 200 đơn hạn gần nhất, đủ cho nhà xe nhỏ; nhiều hơn thì thêm ô lọc
    ).all()
    return [ra_don(d) for d in dong if nc.thu_tu[d[0].nut_giu_id or d[0].nut_lay_id] <= nc.thu_tu[d[0].nut_giao_id]]


# ---------- UC-12: đổi xe, tài xế của chuyến LAP ----------


def _khung_cua(db: Session, c: Chuyen) -> KhungChuyen:
    """Khung của chuyến đã có: giữ kết thúc dự kiến đã tính theo đơn đang ghép (BR-64)."""
    return replace(_khung(db, c.tuyen_id, c.khoi_hanh_du_kien), ket_thuc=c.ket_thuc_du_kien)


def _don_dang_ghep(db: Session, chuyen_id: int) -> list[DonGhep]:
    return [don_ghep(d) for d, *_ in _dong_don_cua_chuyen(db, chuyen_id)]


def _chuyen(db: Session, chuyen_id: int) -> Chuyen:
    c = db.get(Chuyen, chuyen_id)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    return c


def xe_kha_dung_chuyen(db: Session, chuyen_id: int) -> list[dict]:
    c = _chuyen(db, chuyen_id)
    return _ds_xe(db, _khung_cua(db, c), c.id, _don_dang_ghep(db, c.id))


def tai_xe_kha_dung_chuyen(db: Session, chuyen_id: int, xe_id: int | None) -> list[dict]:
    c = _chuyen(db, chuyen_id)
    return _ds_tai_xe(db, _khung_cua(db, c), xe_id or c.xe_id, c.id)


def phan_cong(db: Session, chuyen_id: int, xe_id: int, tai_xe_id: int) -> dict:
    """UC-12: đổi xe và/hoặc tài xế khi chuyến LAP; kiểm lại BR-11…19 và tải, thể tích theo đơn đang ghép (BR-67)."""
    c = db.get(Chuyen, chuyen_id, with_for_update=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai != "LAP":
        raise LoiNghiepVu("BR-09", f"Chuyến {c.ma_chuyen} không ở trạng thái Đang lập, không đổi xe/tài xế được", 409)
    # Chỉ khóa xe, tài xế mới theo thứ tự xe → tài xế như lập chuyến (không khóa cái cũ: tránh khóa chéo)
    xe = db.get(Xe, xe_id, with_for_update=True)
    if xe is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy xe", 404)
    tx = db.get(TaiXe, tai_xe_id, with_for_update=True)
    if tx is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tài xế", 404)
    ten = db.get(NguoiDung, tx.nguoi_dung_id).ho_ten
    k = _khung_cua(db, c)
    vp = (
        _xet_xe(db, k, [xe], c.id)[xe.id]
        + xet_tai(_don_dang_ghep(db, c.id), xe.tai_trong_kg, xe.the_tich_m3)
        + _xet_tai_xe(db, k, [(tx, ten)], xe.ktt_toan_bo_kg, c.id)[tx.id]
    )
    if vp:
        raise LoiNghiepVu(vp[0]["ma"], "Không đổi được xe/tài xế", chi_tiet=vp)
    c.xe_id, c.tai_xe_id = xe.id, tx.id
    db.commit()
    return chi_tiet(db, c.id)


# ---------- UC-15: chốt / mở chốt ----------


def _doi_trang_thai_chuyen(db: Session, c: Chuyen, sang: str, nguoi: NguoiDung, ly_do: str | None = None) -> None:
    db.add(
        LichSuTrangThai(doi_tuong="CHUYEN", doi_tuong_id=c.id, tu=c.trang_thai, sang=sang, ly_do=ly_do, nguoi=nguoi.id)
    )
    c.trang_thai = sang


def chot(db: Session, chuyen_id: int, xac_nhan_chay_rong: bool, xac_nhan_lai_am: bool, nguoi: NguoiDung) -> dict:
    c, xe, tx = _khoa_chuyen(db, chuyen_id, viec="chốt")
    nc = ngu_canh(db, c, xe)
    ghep_hl = list(db.scalars(select(Ghep).where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)))
    don = list(db.scalars(select(DonHang).where(DonHang.id.in_([g.don_hang_id for g in ghep_hl]))))

    # Kiểm lại nhóm A cho mọi đơn đang ghép, nhóm B đủ BR-11…19 theo khoảng chiếm hiện tại (BR-23)
    diem, vp = xet_ghep(
        [don_ghep(d) for d in don],
        set(),
        nc.thu_tu,
        nc.phut,
        c.khoi_hanh_du_kien,
        nc.cfg08,
        xe.tai_trong_kg,
        xe.the_tich_m3,
    )
    k = replace(_khung(db, c.tuyen_id, c.khoi_hanh_du_kien), ket_thuc=c.ket_thuc_du_kien)
    ten = db.get(NguoiDung, tx.nguoi_dung_id).ho_ten
    vp += _xet_xe(db, k, [xe], c.id)[xe.id] + _xet_tai_xe(db, k, [(tx, ten)], xe.ktt_toan_bo_kg, c.id)[tx.id]
    if vp:
        raise LoiNghiepVu("VI_PHAM_CHOT", "Chuyến vi phạm quy tắc, chưa chốt", chi_tiet=vp)

    t = nc.tuyen
    if not don:
        if not xac_nhan_chay_rong:
            raise LoiNghiepVu("BR-23", "Chuyến chưa có đơn nào, cần xác nhận chạy rỗng")
    else:  # chuyến rỗng luôn lãi âm, xác nhận chạy rỗng là đủ (quyết định UC-15 số 2)
        lai = lai_du_kien([d.cuoc_tinh for d in don], t.dm_dau + t.dm_cau_duong + t.dm_boc_xep, t.dm_luong_tai_xe)
        if lai < 0 and not xac_nhan_lai_am:
            raise LoiNghiepVu("BR-52", f"Lãi dự kiến âm ({lai:,} đ), cần xác nhận".replace(",", "."))

    # Lưu định mức, lương của tuyến và ETA kế hoạch từng điểm (BR-71)
    c.dm_dau_chot, c.dm_cau_duong_chot, c.dm_boc_xep_chot = t.dm_dau, t.dm_cau_duong, t.dm_boc_xep
    c.luong_tai_xe_chot, c.chay_rong = t.dm_luong_tai_xe, not don
    eta = {(d.don.id, d.viec): d.eta for d in diem}
    for g in ghep_hl:
        g.eta_lay_ke_hoach, g.eta_giao_ke_hoach = eta[g.don_hang_id, "LAY"], eta[g.don_hang_id, "GIAO"]
    _doi_trang_thai_chuyen(db, c, "DA_CHOT", nguoi)
    db.commit()
    return chi_tiet(db, c.id)


def _con_tam_ung(db: Session, chuyen_id: int) -> bool:
    return (
        db.scalar(select(TamUng.id).where(TamUng.chuyen_id == chuyen_id, TamUng.trang_thai == "HIEU_LUC").limit(1))
        is not None
    )


def mo_chot(db: Session, chuyen_id: int, nguoi: NguoiDung) -> dict:
    c, _, _ = _khoa_chuyen(db, chuyen_id, can="DA_CHOT", viec="mở chốt")
    if _con_tam_ung(db, c.id):
        raise LoiNghiepVu("BR-24", "Chuyến còn tạm ứng chưa thu hồi, cần Kế toán thu hồi tạm ứng trước", 409)
    # Về LAP thì lãi dự kiến lấy lại từ tuyến; chốt lại lưu theo số mới (BR-52, 71; quyết định UC-15 số 4)
    c.dm_dau_chot = c.dm_cau_duong_chot = c.dm_boc_xep_chot = c.luong_tai_xe_chot = None
    c.chay_rong = False
    db.execute(
        update(Ghep).where(Ghep.chuyen_id == c.id, Ghep.hieu_luc).values(eta_lay_ke_hoach=None, eta_giao_ke_hoach=None)
    )
    _doi_trang_thai_chuyen(db, c, "LAP", nguoi)
    db.commit()
    return chi_tiet(db, c.id)


# ---------- UC-16: hủy chuyến ----------


def huy(db: Session, chuyen_id: int, ly_do: str, nguoi: NguoiDung) -> dict:
    # Khóa dòng chuyến như ghép/gỡ/chốt: hủy và các thao tác đó trên cùng chuyến chạy lần lượt
    c = db.get(Chuyen, chuyen_id, with_for_update=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai not in ("LAP", "DA_CHOT"):
        raise LoiNghiepVu("BR-25", f"Chuyến {c.ma_chuyen} đã chạy hoặc đã hủy, không hủy được", 409)
    if _con_tam_ung(db, c.id):
        raise LoiNghiepVu("BR-25", "Chuyến còn tạm ứng chưa thu hồi, cần Kế toán thu hồi tạm ứng trước", 409)

    don = list(
        db.scalars(
            select(DonHang)
            .join(Ghep, Ghep.don_hang_id == DonHang.id)
            .where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)
            .order_by(DonHang.id)
            .with_for_update(of=DonHang)
        )
    )
    db.execute(update(Ghep).where(Ghep.chuyen_id == c.id, Ghep.hieu_luc).values(hieu_luc=False))
    _doi_trang_thai(db, don, "CHO_GHEP", nguoi, ly_do)
    # Giữ số đã chốt làm dấu vết (quyết định UC-16 số 5); chuyến HUY không chiếm lịch (BR-16, 17)
    _doi_trang_thai_chuyen(db, c, "HUY", nguoi, ly_do)
    db.commit()
    return chi_tiet(db, c.id)
