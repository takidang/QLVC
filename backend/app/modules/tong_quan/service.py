"""UC-38 tổng quan một ngày: chuyến theo trạng thái, đơn giao / thất bại, tỉ lệ đúng giờ, doanh thu dự kiến.

Chỉ đọc. Tính lại mỗi lần, dùng lại cách tính độ trễ của UC-32 (`theo_doi._ghep`, `_diem`) để khớp bảng chuyến.
"""

from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chuyen
from app.modules.chuyen import theo_doi
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.thoi_gian import GIO_VN

TRANG_THAI = ("LAP", "DA_CHOT", "DANG_CHAY", "HOAN_THANH", "DA_QUYET_TOAN", "HUY")


def tong_quan(db: Session, ngay: date) -> dict:
    dau = datetime.combine(ngay, time(), GIO_VN)  # một ngày theo giờ Việt Nam: [00:00, 00:00 hôm sau)
    ds = list(
        db.scalars(
            select(Chuyen).where(Chuyen.khoi_hanh_du_kien >= dau, Chuyen.khoi_hanh_du_kien < dau + timedelta(days=1))
        )
    )
    nguong = int(cau_hinh.lay(db, "CFG-09"))
    theo_trang_thai = {t: 0 for t in TRANG_THAI}
    don = {"tong": 0, "da_giao": 0, "that_bai": 0}
    kg_da_cho, doanh_thu = 0, 0
    da_quet = dung_gio = 0
    for c in ds:
        theo_trang_thai[c.trang_thai] += 1
        if c.trang_thai == "HUY":  # chuyến hủy không có hàng, không doanh thu
            continue
        ghep = theo_doi._ghep(db, c.id)
        for g, d in ghep:
            don["tong"] += 1
            doanh_thu += d.cuoc_tinh
            if g.ket_qua == "DA_GIAO":  # kết quả trên chính chuyến này (UC-32)
                don["da_giao"] += 1
                kg_da_cho += d.kg
            elif g.ket_qua == "THAT_BAI":
                don["that_bai"] += 1
        for diem in theo_doi._diem(db, ghep).values():
            if diem["tre_phut"] is not None:  # điểm đã quét
                da_quet += 1
                dung_gio += diem["tre_phut"] <= nguong  # sớm hoặc đúng bằng ngưỡng vẫn đúng giờ
    return {
        "ngay": ngay.isoformat(),
        "chuyen": {"tong": len(ds), "theo_trang_thai": theo_trang_thai},
        "don": don | {"con_lai": don["tong"] - don["da_giao"] - don["that_bai"], "kg_da_cho": float(kg_da_cho)},
        "dung_gio": {
            "nguong_tre_phut": nguong,
            "da_quet": da_quet,
            "dung_gio": dung_gio,
            "ty_le": round(dung_gio / da_quet, 4) if da_quet else None,
        },
        "doanh_thu_du_kien": doanh_thu,
    }
