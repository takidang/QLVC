"""Báo cáo, chỉ đọc.

UC-26 lãi lỗ: số đã khóa trong QUYET_TOAN (BR-29, 51), không tính lại; theo xe, theo tháng thì trừ chi phí cố định
hằng tháng của xe (nghiep-vu.md bảng chỉ số "Lãi xe theo tháng").
UC-34 hiệu suất xe theo tháng: lấp đầy, chạy rỗng, km, dầu thực tế so với tham khảo.
"""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.lich_trinh import ty_le_lap_day
from app.loi import LoiNghiepVu
from app.models import ChiPhi, ChiPhiCoDinhXe, Chuyen, DonHang, Ghep, QuyetToan, Tuyen, Xe
from app.thoi_gian import GIO_VN

SO_THANG_TOI_DA = 12
COT = ("doanh_thu", "tong_chi", "luong_tai_xe")


def _so(thang: str) -> int:
    nam, t = map(int, thang.split("-"))
    return nam * 12 + t - 1


def _thang(so: int) -> str:
    return f"{so // 12:04d}-{so % 12 + 1:02d}"


def _dau_thang(so: int) -> datetime:
    return datetime(so // 12, so % 12 + 1, 1, tzinfo=GIO_VN)


def _cong(dong: dict, qt: QuyetToan) -> None:
    dong["so_chuyen"] += 1
    for k in COT:
        dong[k] += getattr(qt, k)
    dong["lai_chuyen"] += qt.lai


def _dong_trong(**khoa) -> dict:
    return khoa | {"so_chuyen": 0, **dict.fromkeys(COT, 0), "lai_chuyen": 0, "chi_phi_co_dinh": 0, "lai": 0}


def lai_lo(db: Session, theo: str, tu: str, den: str) -> dict:
    a, b = _so(tu), _so(den)
    if a > b:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", "Từ tháng phải trước hoặc bằng đến tháng", 400)
    if b - a + 1 > SO_THANG_TOI_DA:
        raise LoiNghiepVu("DU_LIEU_KHONG_HOP_LE", f"Chỉ xem tối đa {SO_THANG_TOI_DA} tháng một lần", 400)
    # Tháng của chuyến theo giờ khởi hành thực tế, giờ Việt Nam (chuyến đã quyết toán luôn có giờ này)
    trong_khoang = (Chuyen.khoi_hanh_thuc_te >= _dau_thang(a)) & (Chuyen.khoi_hanh_thuc_te < _dau_thang(b + 1))

    ds = db.execute(
        select(Chuyen, QuyetToan, Xe.bien_so, Tuyen.ten)
        .join(QuyetToan, QuyetToan.chuyen_id == Chuyen.id)
        .join(Xe, Xe.id == Chuyen.xe_id)
        .join(Tuyen, Tuyen.id == Chuyen.tuyen_id)
        .where(Chuyen.trang_thai == "DA_QUYET_TOAN", trong_khoang)
        .order_by(Chuyen.khoi_hanh_thuc_te.desc(), Chuyen.id.desc())
    ).all()
    cho = db.scalar(select(func.count()).select_from(Chuyen).where(Chuyen.trang_thai == "HOAN_THANH", trong_khoang))

    def thang_cua(c: Chuyen) -> str:
        return c.khoi_hanh_thuc_te.astimezone(GIO_VN).strftime("%Y-%m")

    ket = {"theo": theo, "tu": tu, "den": den, "so_chuyen_cho_quyet_toan": cho, "thieu_chi_phi_co_dinh": []}

    if theo == "chuyen":
        du_lieu = [
            {
                "chuyen_id": c.id,
                "ma_chuyen": c.ma_chuyen,
                "ngay": c.khoi_hanh_thuc_te.astimezone(GIO_VN).date(),
                "xe_id": c.xe_id,
                "bien_so": bien_so,
                "ten_tuyen": ten_tuyen,
                **{k: getattr(qt, k) for k in COT},
                "lai": qt.lai,
            }
            for c, qt, bien_so, ten_tuyen in ds
        ]
        tong = _dong_trong()
        for _, qt, _, _ in ds:
            _cong(tong, qt)
        tong["lai"] = tong["lai_chuyen"]
        return ket | {"du_lieu": du_lieu, "tong": tong}

    cac_thang = [_thang(s) for s in range(a, b + 1)]
    co_dinh = db.execute(
        select(ChiPhiCoDinhXe.xe_id, Xe.bien_so, ChiPhiCoDinhXe.thang, ChiPhiCoDinhXe.so_tien)
        .join(Xe, Xe.id == ChiPhiCoDinhXe.xe_id)
        .where(ChiPhiCoDinhXe.thang.in_(cac_thang))
    ).all()
    da_nhap = {(xe_id, thang) for xe_id, _, thang, _ in co_dinh}

    # Xe – tháng có chuyến mà chưa nhập chi phí cố định: tính 0 và báo (UC-26 quyết định 3)
    thieu = {}
    for c, _, bien_so, _ in ds:
        k = (c.xe_id, thang_cua(c))
        if k not in da_nhap:
            thieu[k] = {"xe_id": c.xe_id, "bien_so": bien_so, "thang": k[1]}
    ket["thieu_chi_phi_co_dinh"] = sorted(thieu.values(), key=lambda x: (x["thang"], x["bien_so"]))

    if theo == "xe":
        dong: dict = {}
        for c, qt, bien_so, _ in ds:
            _cong(dong.setdefault(c.xe_id, _dong_trong(xe_id=c.xe_id, bien_so=bien_so)), qt)
        for xe_id, bien_so, _, so_tien in co_dinh:  # xe không chạy mà có chi phí cố định vẫn có dòng (lỗ)
            dong.setdefault(xe_id, _dong_trong(xe_id=xe_id, bien_so=bien_so))["chi_phi_co_dinh"] += so_tien
        du_lieu = sorted(dong.values(), key=lambda x: x["bien_so"])
    else:
        dong = {t: _dong_trong(thang=t) for t in cac_thang}  # đủ mọi tháng, kể cả tháng trống (để vẽ biểu đồ)
        for c, qt, _, _ in ds:
            _cong(dong[thang_cua(c)], qt)
        for _, _, thang, so_tien in co_dinh:
            dong[thang]["chi_phi_co_dinh"] += so_tien
        du_lieu = list(dong.values())

    tong = _dong_trong()
    for d in du_lieu:
        d["lai"] = d["lai_chuyen"] - d["chi_phi_co_dinh"]
        for k in ("so_chuyen", *COT, "lai_chuyen", "chi_phi_co_dinh", "lai"):
            tong[k] += d[k]
    return ket | {"du_lieu": du_lieu, "tong": tong}


def hieu_suat_xe(db: Session, thang: str) -> dict:
    a = _so(thang)
    # Chuyến đã chạy xong (UC-34 quyết định 1), khởi hành thực tế trong tháng theo giờ VN như UC-26
    ds = list(
        db.scalars(
            select(Chuyen).where(
                Chuyen.trang_thai.in_(("HOAN_THANH", "DA_QUYET_TOAN")),
                Chuyen.khoi_hanh_thuc_te >= _dau_thang(a),
                Chuyen.khoi_hanh_thuc_te < _dau_thang(a + 1),
            )
        )
    )
    ids = [c.id for c in ds]
    # Hàng của chuyến như UC-13: ghép còn hiệu lực hoặc đã có kết quả (gồm đơn thất bại); đơn đã gỡ không tính
    hang = {
        cid: (kg, m3)
        for cid, kg, m3 in db.execute(
            select(Ghep.chuyen_id, func.sum(DonHang.kg), func.sum(DonHang.m3))
            .join(DonHang, DonHang.id == Ghep.don_hang_id)
            .where(Ghep.chuyen_id.in_(ids), or_(Ghep.hieu_luc, Ghep.ket_qua.is_not(None)))
            .group_by(Ghep.chuyen_id)
        )
    }
    lit = dict(
        db.execute(
            select(ChiPhi.chuyen_id, func.sum(ChiPhi.so_lit))
            .where(ChiPhi.chuyen_id.in_(ids), ChiPhi.loai == "DAU", ChiPhi.trang_thai == "DA_DUYET")
            .group_by(ChiPhi.chuyen_id)
        ).all()
    )
    xe_co_chuyen = {c.xe_id for c in ds}
    xe = {
        x.id: x for x in db.scalars(select(Xe).where(or_(Xe.id.in_(xe_co_chuyen), Xe.trang_thai == "HOAT_DONG")))
    }  # xe hoạt động không chạy vẫn có dòng; xe ngừng chỉ khi có chuyến (quyết định 4)

    theo_xe: dict[int, list[Chuyen]] = defaultdict(list)
    for c in ds:
        theo_xe[c.xe_id].append(c)
    lap_day_moi_chuyen: list[Decimal] = []
    du_lieu = []
    for x in sorted(xe.values(), key=lambda x: x.bien_so):
        cs = theo_xe.get(x.id, [])
        lap_day = []
        km = 0
        thuc_te = Decimal(0)
        for c in cs:
            kg, m3 = hang.get(c.id, (Decimal(0), Decimal(0)))
            lap_day.append(ty_le_lap_day(kg, m3, x.tai_trong_kg, x.the_tich_m3))  # chạy rỗng = 0
            if c.km_bat_dau is not None and c.km_ket_thuc is not None:  # BR-70: ghi lúc bắt đầu / kết thúc
                km += c.km_ket_thuc - c.km_bat_dau
            thuc_te += lit.get(c.id) or 0
        lap_day_moi_chuyen += lap_day
        tham_khao = (
            (Decimal(km) * x.dinh_muc_lit_100km / 100).quantize(Decimal("0.01"))
            if x.dinh_muc_lit_100km is not None
            else None
        )  # như dầu tham khảo của quyết toán (UC-24)
        du_lieu.append(
            {
                "xe_id": x.id,
                "bien_so": x.bien_so,
                "so_chuyen": len(cs),
                "so_chuyen_rong": sum(c.chay_rong for c in cs),
                "lap_day_tb": round(sum(lap_day) / len(lap_day), 4) if lap_day else None,
                "km": km,
                "dau_thuc_te_lit": thuc_te,
                "dau_tham_khao_lit": tham_khao,
                "chenh_lech_lit": thuc_te - tham_khao if tham_khao is not None else None,
                "so_chuyen_chua_quyet_toan": sum(c.trang_thai == "HOAN_THANH" for c in cs),
            }
        )

    def cong(k):
        return sum(d[k] for d in du_lieu)

    tham_khao_tong = [d["dau_tham_khao_lit"] for d in du_lieu if d["dau_tham_khao_lit"] is not None]
    tong = {k: cong(k) for k in ("so_chuyen", "so_chuyen_rong", "km", "dau_thuc_te_lit", "so_chuyen_chua_quyet_toan")}
    tong |= {
        # Trung bình trên mọi chuyến, không phải trung bình của các xe (AC4)
        "lap_day_tb": round(sum(lap_day_moi_chuyen) / len(lap_day_moi_chuyen), 4) if lap_day_moi_chuyen else None,
        "dau_tham_khao_lit": sum(tham_khao_tong, Decimal(0)) if tham_khao_tong else None,
    }
    return {"thang": thang, "du_lieu": du_lieu, "tong": tong}
