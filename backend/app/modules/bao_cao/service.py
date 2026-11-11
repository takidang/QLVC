"""UC-26 báo cáo lãi lỗ: chỉ đọc số đã khóa trong QUYET_TOAN (BR-29, 51), không tính lại.

Theo xe, theo tháng thì trừ chi phí cố định hằng tháng của xe (nghiep-vu.md bảng chỉ số "Lãi xe theo tháng").
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import ChiPhiCoDinhXe, Chuyen, QuyetToan, Tuyen, Xe
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
