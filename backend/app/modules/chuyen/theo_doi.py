"""UC-32 theo dõi chuyến: tiến độ, cờ, độ trễ so ETA kế hoạch, chồng lịch khi đang chạy (BR-73), dòng thời gian,
kết thúc do sự cố (BR-68), đóng sự cố. Tách khỏi `service.py` để phần lập / ghép / chốt giữ gọn.
"""

from datetime import timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, LichSuTrangThai, LuotQuet, NguoiDung, SuCo, TamUng, Xe
from app.modules.chuyen import service
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.thoi_gian import bay_gio

PHIA = {"LAY": "LAY", "KHONG_LAY": "LAY", "GIAO": "GIAO", "GIAO_THAT_BAI": "GIAO"}  # lượt quét thuộc điểm nào
# Dòng thời gian hiện chữ, không hiện mã
TEN_TRANG_THAI = {
    "LAP": "Đang lập",
    "DA_CHOT": "Đã chốt",
    "DANG_CHAY": "Đang chạy",
    "HOAN_THANH": "Hoàn thành",
    "DA_QUYET_TOAN": "Đã quyết toán",
    "HUY": "Hủy",
    "CHO_GHEP": "Chờ ghép",
    "DA_GHEP": "Đã ghép",
    "DA_LAY": "Đã lấy",
    "DA_GIAO": "Đã giao",
    "THAT_BAI": "Thất bại",
    "TRA_HANG": "Trả hàng",
}
TEN_QUET = {"LAY": "Quét lấy", "KHONG_LAY": "Không lấy được", "GIAO": "Giao", "GIAO_THAT_BAI": "Giao không được"}


def _ghep(db: Session, chuyen_id: int) -> list[tuple[Ghep, DonHang]]:
    """Ghép của chuyến: còn hiệu lực, hoặc đã có kết quả (đơn thất bại của chuyến đã kết thúc vẫn tính)."""
    return db.execute(
        select(Ghep, DonHang)
        .join(DonHang, DonHang.id == Ghep.don_hang_id)
        .where(Ghep.chuyen_id == chuyen_id, or_(Ghep.hieu_luc, Ghep.ket_qua.is_not(None)))
    ).all()


def _diem(db: Session, ghep: list[tuple[Ghep, DonHang]]) -> dict[tuple[int, str], dict]:
    """(don_id, LAY|GIAO) → ETA kế hoạch, giờ quét đầu tiên, kết quả, số phút trễ."""
    quet: dict[tuple[int, str], LuotQuet] = {}
    if ghep:
        theo_ghep = {g.id: d.id for g, d in ghep}
        for lq in db.scalars(
            select(LuotQuet).where(LuotQuet.ghep_id.in_(theo_ghep)).order_by(LuotQuet.thoi_gian, LuotQuet.id)
        ):
            quet.setdefault((theo_ghep[lq.ghep_id], PHIA[lq.loai]), lq)
    ra = {}
    for g, d in ghep:
        for viec, eta in (("LAY", g.eta_lay_ke_hoach), ("GIAO", g.eta_giao_ke_hoach)):
            lq = quet.get((d.id, viec))
            tre = int((lq.thoi_gian - eta).total_seconds() // 60) if lq and eta else None
            ra[(d.id, viec)] = {
                "eta_ke_hoach": eta,
                "thuc_te": lq.thoi_gian if lq else None,
                "ket_qua": lq.loai if lq else None,
                "tre_phut": tre,
            }
        if ra[(d.id, "LAY")]["ket_qua"] == "KHONG_LAY":
            ra[(d.id, "GIAO")]["ket_qua"] = "BO"  # không lấy được thì không còn điểm giao để làm
    return ra


def _theo_doi(db: Session, c: Chuyen, nguong: int) -> dict:
    ghep = _ghep(db, c.id)
    diem = _diem(db, ghep)
    xong = sum(1 for p in diem.values() if p["ket_qua"])
    tre = [p for p in diem.values() if p["tre_phut"] is not None]
    co = []
    if any(p["tre_phut"] > nguong for p in tre):
        co.append("TRE")
    if db.scalar(select(func.count()).select_from(SuCo).where(SuCo.chuyen_id == c.id, SuCo.trang_thai == "MO")):
        co.append("SU_CO")
    if any(d.trang_thai == "THAT_BAI" or g.ket_qua == "THAT_BAI" for g, d in ghep):
        co.append("THAT_BAI")
    if c.trang_thai == "HOAN_THANH":
        co.append("CHUA_QUYET_TOAN")

    gan_nhat = max(tre, key=lambda p: p["thuc_te"], default=None)  # lượt quét gần nhất (BR-73)
    # BR-73: kết thúc dự kiến khi đang chạy = kết thúc dự kiến + max(0, độ trễ lượt quét gần nhất)
    ket_thuc_dang_chay, chong = None, []
    if c.trang_thai == "DANG_CHAY":
        ket_thuc_dang_chay = c.ket_thuc_du_kien + timedelta(minutes=max(0, gan_nhat["tre_phut"] if gan_nhat else 0))
        chong = list(
            db.scalars(
                select(Chuyen.ma_chuyen)
                .where(
                    or_(Chuyen.xe_id == c.xe_id, Chuyen.tai_xe_id == c.tai_xe_id),
                    Chuyen.id != c.id,
                    Chuyen.trang_thai != "HUY",
                    Chuyen.khoi_hanh_du_kien >= c.khoi_hanh_du_kien,
                    Chuyen.khoi_hanh_du_kien < ket_thuc_dang_chay,
                )
                .order_by(Chuyen.khoi_hanh_du_kien)
            )
        )
        if chong:
            co.append("CHONG_LICH")
    return {
        "diem": diem,
        "tre_phut": gan_nhat["tre_phut"] if gan_nhat else None,  # lượt quét gần nhất, âm là sớm (BR-73)
        "xong": xong,
        "tong": len(diem),
        "co": co,
        "chong": chong,
        "ket_thuc_dang_chay": ket_thuc_dang_chay,
    }


def _trang_thai_diem(c: Chuyen, ct: dict, diem: dict) -> list[str]:
    """Trạng thái từng điểm dừng theo thứ tự lịch trình (UC-32-AC12)."""
    don_tb = {d["id"] for d in ct["don"] if d["trang_thai"] == "THAT_BAI"}
    dang_toi = c.trang_thai == "DANG_CHAY"
    ra = []
    for p in ct["lich_trinh"]:
        kq = diem.get((p["don_id"], p["viec"]), {}).get("ket_qua")
        if kq in ("LAY", "GIAO"):
            ra.append("XONG")
        elif kq or p["don_id"] in don_tb:  # KHONG_LAY, GIAO_THAT_BAI, BO; hoặc thất bại do kết thúc sự cố
            ra.append("THAT_BAI")
        elif dang_toi:
            ra.append("DANG_TOI")
            dang_toi = False
        else:
            ra.append("CHUA")
    return ra


def _vi_tri(db: Session, c: Chuyen, ct: dict) -> dict | None:
    """Lượt quét mới nhất có GPS (UC-32-AC14); không theo dõi liên tục, chỉ là vị trí lúc quét."""
    dong = db.execute(
        select(LuotQuet, Ghep.don_hang_id)
        .join(Ghep, Ghep.id == LuotQuet.ghep_id)
        .where(Ghep.chuyen_id == c.id, LuotQuet.lat.is_not(None), LuotQuet.lng.is_not(None))
        .order_by(LuotQuet.thoi_gian.desc(), LuotQuet.id.desc())
        .limit(1)
    ).first()
    if dong is None:
        return None
    lq, don_id = dong
    nut = next((p["nut"] for p in ct["lich_trinh"] if (p["don_id"], p["viec"]) == (don_id, PHIA[lq.loai])), None)
    return {"lat": lq.lat, "lng": lq.lng, "luc": lq.thoi_gian, "nut": nut}


def bang_ngay(db: Session, ds: list[dict]) -> list[dict]:
    """Thêm `theo_doi` cho từng dòng của bảng chuyến trong ngày (UC-32 bước 1)."""
    nguong = int(cau_hinh.lay(db, "CFG-09"))
    for x in ds:
        c = db.get(Chuyen, x["id"])
        td = _theo_doi(db, c, nguong)
        ct = service.chi_tiet(db, c.id)
        x["theo_doi"] = {
            "xong": td["xong"],
            "tong": td["tong"],
            "ty_le_lap_day": ct["ty_le_lap_day"],
            "co": td["co"],
            "chong": td["chong"],
            "diem": _trang_thai_diem(c, ct, td["diem"]),
            "tre_phut": td["tre_phut"],
            "vi_tri": _vi_tri(db, c, ct),
        }
    return ds


def _dong_thoi_gian(db: Session, c: Chuyen, ghep: list[tuple[Ghep, DonHang]]) -> list[dict]:
    ma = {d.id: d.ma_don for _, d in ghep}
    ten = dict(db.execute(select(NguoiDung.id, NguoiDung.ho_ten)).all())
    su_kien = []
    ls = db.scalars(
        select(LichSuTrangThai).where(
            or_(
                (LichSuTrangThai.doi_tuong == "CHUYEN") & (LichSuTrangThai.doi_tuong_id == c.id),
                (LichSuTrangThai.doi_tuong == "DON") & LichSuTrangThai.doi_tuong_id.in_(ma),
            )
        )
    )
    for x in ls:
        doi_tuong = f"Chuyến {c.ma_chuyen}" if x.doi_tuong == "CHUYEN" else f"Đơn {ma[x.doi_tuong_id]}"
        tu = TEN_TRANG_THAI.get(x.tu, x.tu) if x.tu else "Mới"
        cau = f"{doi_tuong}: {tu} → {TEN_TRANG_THAI.get(x.sang, x.sang)}" + (f" ({x.ly_do})" if x.ly_do else "")
        su_kien.append({"luc": x.luc, "loai": "TRANG_THAI", "noi_dung": cau, "nguoi": ten.get(x.nguoi)})
    theo_ghep = {g.id: d.ma_don for g, d in ghep}
    if theo_ghep:
        for lq in db.scalars(select(LuotQuet).where(LuotQuet.ghep_id.in_(theo_ghep))):
            gps = " · thiếu GPS" if lq.thieu_gps else ""
            cau = f"{TEN_QUET[lq.loai]} đơn {theo_ghep[lq.ghep_id]}{gps}"
            su_kien.append({"luc": lq.thoi_gian, "loai": "QUET", "noi_dung": cau})
    for sc in db.scalars(select(SuCo).where(SuCo.chuyen_id == c.id)):
        cau = f"Sự cố {sc.loai}" + (f": {sc.ghi_chu}" if sc.ghi_chu else "")
        su_kien.append({"luc": sc.luc, "loai": "SU_CO", "noi_dung": cau})
    return sorted(su_kien, key=lambda s: s["luc"])


def chi_tiet(db: Session, chuyen_id: int) -> dict:
    """Chi tiết chuyến cho Điều phối / Kế toán (UC-32 bước 2): thêm giờ quét, trễ, dòng thời gian, tiền, sự cố."""
    ct = service.chi_tiet(db, chuyen_id)
    c = db.get(Chuyen, chuyen_id)
    td = _theo_doi(db, c, int(cau_hinh.lay(db, "CFG-09")))
    for p in ct["lich_trinh"]:
        p |= td["diem"].get((p["don_id"], p["viec"]), {})
    # Định mức, lương lấy như lãi dự kiến: đã chốt thì số đã chốt, đang lập thì theo tuyến (BR-52, 71)
    if c.dm_dau_chot is not None:
        dm, luong = c.dm_dau_chot + c.dm_cau_duong_chot + c.dm_boc_xep_chot, c.luong_tai_xe_chot
    else:
        t = service.ngu_canh(db, c).tuyen
        dm, luong = t.dm_dau + t.dm_cau_duong + t.dm_boc_xep, t.dm_luong_tai_xe
    tam_ung = db.scalar(
        select(func.coalesce(func.sum(TamUng.so_tien), 0)).where(
            TamUng.chuyen_id == c.id, TamUng.trang_thai == "HIEU_LUC"
        )
    )
    su_co = db.scalars(select(SuCo).where(SuCo.chuyen_id == c.id).order_by(SuCo.id)).all()
    return ct | {
        "co": td["co"],
        "chong": td["chong"],
        "ket_thuc_dang_chay": td["ket_thuc_dang_chay"],
        "ket_thuc_bat_thuong": c.ket_thuc_bat_thuong,
        "ly_do_ket_thuc": c.ly_do_ket_thuc,
        "km_bat_dau": c.km_bat_dau,
        "km_ket_thuc": c.km_ket_thuc,
        "dong_thoi_gian": _dong_thoi_gian(db, c, _ghep(db, c.id)),
        "tien": {
            "dinh_muc": dm,
            "luong": luong,
            "tam_ung_hieu_luc": int(tam_ung),
            "doanh_thu": sum(d["cuoc_tinh"] for d in ct["don"]),
        },
        "su_co": [
            {
                "id": s.id,
                "loai": s.loai,
                "ghi_chu": s.ghi_chu,
                "trang_thai": s.trang_thai,
                "cach_xu_ly": s.cach_xu_ly,
                "luc": s.luc,
            }
            for s in su_co
        ],
    }


def ket_thuc_su_co(db: Session, chuyen_id: int, ly_do: str, km: int | None, nguoi: NguoiDung) -> dict:
    """BR-68: chuyến DANG_CHAY kết thúc do sự cố; đơn chưa giao → THAT_BAI, giải phóng xe và tài xế."""
    c = db.get(Chuyen, chuyen_id, with_for_update=True, populate_existing=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai != "DANG_CHAY":
        raise LoiNghiepVu("BR-68", f"Chuyến {c.ma_chuyen} không đang chạy, không kết thúc do sự cố được", 409)
    xe = db.get(Xe, c.xe_id, with_for_update=True)
    if km is not None and c.km_bat_dau is not None and km <= c.km_bat_dau:
        raise LoiNghiepVu("BR-70", f"Km kết thúc {km:,} phải lớn hơn km bắt đầu {c.km_bat_dau:,}")
    ghep = db.execute(
        select(Ghep, DonHang)
        .join(DonHang, DonHang.id == Ghep.don_hang_id)
        .where(Ghep.chuyen_id == c.id, Ghep.hieu_luc)
        .order_by(DonHang.id)
        .with_for_update(of=DonHang)
    ).all()
    con = [d for _, d in ghep if d.trang_thai in ("DA_GHEP", "DA_LAY")]
    service._doi_trang_thai(db, con, "THAT_BAI", nguoi, f"Sự cố xe: {ly_do}")
    for g, d in ghep:
        g.ket_qua = g.ket_qua or d.trang_thai
        if d.trang_thai == "THAT_BAI":
            g.hieu_luc = False  # BR-36: Điều phối ghép lại / trả hàng / hủy
    luc = bay_gio()
    if km is not None:
        c.km_ket_thuc, xe.km_dong_ho = km, km  # BR-70
    c.ket_thuc_bat_thuong, c.ly_do_ket_thuc, c.ket_thuc_thuc_te = True, ly_do, luc
    c.ket_thuc_du_kien = max(luc, c.khoi_hanh_du_kien)  # khoảng chiếm dừng ở giờ kết thúc thực tế (BR-68)
    service._doi_trang_thai_chuyen(db, c, "HOAN_THANH", nguoi, f"Kết thúc do sự cố: {ly_do}")
    db.commit()
    return chi_tiet(db, c.id)


def dong_su_co(db: Session, su_co_id: int, cach_xu_ly: str) -> dict:
    sc = db.get(SuCo, su_co_id, with_for_update=True)
    if sc is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy sự cố", 404)
    if sc.trang_thai != "MO":
        raise LoiNghiepVu("SU_CO_DA_DONG", "Sự cố đã đóng", 409)
    sc.trang_thai, sc.cach_xu_ly = "DONG", cach_xu_ly
    db.commit()
    return {
        "id": sc.id,
        "loai": sc.loai,
        "ghi_chu": sc.ghi_chu,
        "trang_thai": sc.trang_thai,
        "cach_xu_ly": sc.cach_xu_ly,
        "luc": sc.luc,
    }
