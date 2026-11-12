"""UC-37 thông báo theo vai trò: tính lại mỗi lần mở từ dữ liệu sẵn có, không lưu (quyết định 1).

`luc` là lúc sự việc xảy ra để giao diện so với mốc lần xem cuối ("đã đọc" lưu trên trình duyệt).
"""

from datetime import datetime, time, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import ChiPhi, Chuyen, Ghep, LichSuTrangThai, LuotQuet, NguoiDung, NhatKyTien, SuCo, TaiXe, TamUng
from app.modules.canh_bao import service as canh_bao
from app.modules.don import that_bai
from app.thoi_gian import GIO_VN, bay_gio

KHAN, CAN_LAM, THONG_TIN = "KHAN", "CAN_LAM", "THONG_TIN"
GAN_DAY = timedelta(days=3)  # tài xế: sự cố đã đóng, khoản chi đã xử lý gần đây (quyết định 4)
TEN_GIAY_TO = {"DANG_KIEM": "đăng kiểm", "BAO_HIEM": "bảo hiểm", "GPLX": "GPLX"}
TEN_SU_CO = {"HONG_XE": "hỏng xe", "TAI_NAN": "tai nạn", "KET_XE": "kẹt xe", "THOI_TIET": "thời tiết", "KHAC": "khác"}


def _tb(loai, muc_do, tieu_de, noi_dung, doi_tuong, id_, luc) -> dict:
    return {
        "loai": loai,
        "muc_do": muc_do,
        "tieu_de": tieu_de,
        "noi_dung": noi_dung,
        "doi_tuong": {"loai": doi_tuong, "id": id_},
        "luc": luc,
    }


def _tien(so: int) -> str:
    return f"{so:,}".replace(",", ".") + " đ"


def _gio(luc: datetime) -> str:
    return luc.astimezone(GIO_VN).strftime("%H:%M %d/%m")


def _dau_ngay(nay: datetime) -> datetime:
    return datetime.combine(nay.astimezone(GIO_VN).date(), time(), GIO_VN)


def _lich_su_moi_nhat(db: Session, doi_tuong: str, ids: list[int], sang: str) -> dict[int, datetime]:
    if not ids:
        return {}
    return dict(
        db.execute(
            select(LichSuTrangThai.doi_tuong_id, func.max(LichSuTrangThai.luc))
            .where(
                LichSuTrangThai.doi_tuong == doi_tuong,
                LichSuTrangThai.doi_tuong_id.in_(ids),
                LichSuTrangThai.sang == sang,
            )
            .group_by(LichSuTrangThai.doi_tuong_id)
        ).all()
    )


# ---------- Điều phối, Quản lý: bảng cảnh báo UC-27 + đơn thất bại UC-22 ----------


def _dieu_phoi(db: Session, nay: datetime) -> list[dict]:
    cb = canh_bao.bang(db)
    ra = []
    for g in cb["giay_to"]:
        tinh = "đã hết hạn" if g["het_han"] else f"còn {g['con_ngay']} ngày"
        ra.append(
            _tb(
                "GIAY_TO",
                KHAN if g["het_han"] else CAN_LAM,
                f"{g['ten']}: {TEN_GIAY_TO[g['loai']]} {tinh}",
                f"Hạn {g['han']:%d/%m/%Y}",
                g["doi_tuong"],
                g["id"],
                _dau_ngay(nay),  # không có mốc sự việc: nhắc lại mỗi ngày (quyết định 3)
            )
        )

    tre_ids = [c["chuyen_id"] for c in cb["chuyen_tre"]]
    quet_cuoi = {}
    if tre_ids:
        quet_cuoi = dict(
            db.execute(
                select(Ghep.chuyen_id, func.max(LuotQuet.thoi_gian))
                .join(Ghep, Ghep.id == LuotQuet.ghep_id)
                .where(Ghep.chuyen_id.in_(tre_ids))
                .group_by(Ghep.chuyen_id)
            ).all()
        )
    for c in cb["chuyen_tre"]:
        tre = f"trễ {c['tre_phut']}′" if c["tre_phut"] is not None else "trễ"
        chong = f", chồng lên {', '.join(c['chong'])}" if c["chong"] else ""
        ra.append(
            _tb(
                "CHUYEN_TRE",
                KHAN,
                f"Chuyến {c['ma_chuyen']} {tre}{chong}",
                f"{c['bien_so']} · {c['ten_tai_xe']} · dự kiến xong {_gio(c['ket_thuc_dang_chay'])}",
                "CHUYEN",
                c["chuyen_id"],
                quet_cuoi.get(c["chuyen_id"], nay),
            )
        )

    for s in cb["su_co_mo"]:
        ra.append(
            _tb(
                "SU_CO_MO",
                KHAN,
                f"Sự cố {TEN_SU_CO.get(s['loai'], s['loai'])} – chuyến {s['ma_chuyen']}",
                s["ghi_chu"],
                "CHUYEN",
                s["chuyen_id"],
                s["luc"],
            )
        )

    gio_cho = timedelta(hours=cb["cau_hinh"]["gio_cho_ghep"])
    for d in cb["don_sap_qua_han"]:
        ra.append(
            _tb(
                "DON_SAP_QUA_HAN",
                KHAN if d["qua_han"] else CAN_LAM,
                f"Đơn {d['ma_don']} chưa ghép, {'đã quá hạn giao' if d['qua_han'] else 'sắp tới hạn giao'}",
                f"{d['ten_khach']} · {d['tinh_lay']} → {d['tinh_giao']} · hạn {_gio(d['han_giao'])}",
                "DON",
                d["don_id"],
                d["han_giao"] - gio_cho,  # lúc đơn bắt đầu vào ngưỡng CFG-10
            )
        )

    for t in cb["thieu_gps"]:
        ra.append(
            _tb(
                "THIEU_GPS",
                THONG_TIN,
                f"Chuyến {t['ma_chuyen']}: {t['so_luot']} lượt quét thiếu GPS",
                t["ten_tai_xe"],
                "CHUYEN",
                t["chuyen_id"],
                t["luc_gan_nhat"],
            )
        )

    don_tb = [d for d in that_bai.can_xu_ly(db) if not d["cho_chuyen_xong"]]  # sẵn sàng xử lý (BR-36)
    luc_tb = _lich_su_moi_nhat(db, "DON", [d["id"] for d in don_tb], "THAT_BAI")
    for d in don_tb:
        ra.append(
            _tb(
                "DON_THAT_BAI",
                CAN_LAM,
                f"Đơn {d['ma_don']} thất bại, cần ghép lại / trả hàng / hủy",
                d["ly_do_cuoi"],
                "DON",
                d["id"],
                luc_tb.get(d["id"], d["tao_luc"]),
            )
        )
    return ra


# ---------- Kế toán: chuyến xong chưa quyết toán (UC-24) ----------


def _ke_toan(db: Session) -> list[dict]:
    ds = list(db.scalars(select(Chuyen).where(Chuyen.trang_thai == "HOAN_THANH").order_by(Chuyen.id)))
    ids = [c.id for c in ds]
    cho = {
        cid: (so, tong, luc)
        for cid, so, tong, luc in db.execute(
            select(ChiPhi.chuyen_id, func.count(), func.sum(ChiPhi.so_tien_khai), func.max(ChiPhi.tao_luc))
            .where(ChiPhi.chuyen_id.in_(ids), ChiPhi.trang_thai == "CHO_DUYET")
            .group_by(ChiPhi.chuyen_id)
        )
    }
    tam_ung = dict(
        db.execute(
            select(TamUng.chuyen_id, func.sum(TamUng.so_tien))
            .where(TamUng.chuyen_id.in_(ids), TamUng.trang_thai == "HIEU_LUC")
            .group_by(TamUng.chuyen_id)
        ).all()
    )
    ra = []
    for c in ds:
        xong = c.ket_thuc_thuc_te or c.ket_thuc_du_kien
        su_co = " · kết thúc do sự cố, cần nhập lương" if c.ket_thuc_bat_thuong else ""
        ra.append(
            _tb(
                "CHO_QUYET_TOAN",
                CAN_LAM,
                f"Chuyến {c.ma_chuyen} chờ quyết toán",
                f"Kết thúc {_gio(xong)}{su_co}",
                "CHUYEN",
                c.id,
                xong,
            )
        )
        if c.id in cho:
            so, tong, luc = cho[c.id]
            ra.append(
                _tb(
                    "CHI_PHI_CHO_DUYET",
                    CAN_LAM,
                    f"Chuyến {c.ma_chuyen}: {so} khoản chi chờ duyệt",
                    f"Tổng khai {_tien(int(tong))}",
                    "CHUYEN",
                    c.id,
                    luc,
                )
            )
        if tam_ung.get(c.id):
            ra.append(
                _tb(
                    "TAM_UNG_TREO",
                    THONG_TIN,
                    f"Tạm ứng {_tien(int(tam_ung[c.id]))} của chuyến {c.ma_chuyen} chưa quyết toán",
                    None,
                    "CHUYEN",
                    c.id,
                    xong,
                )
            )
    return ra


# ---------- Tài xế: việc của chính mình (BR-58) ----------


def _tai_xe(db: Session, nd: NguoiDung, nay: datetime) -> list[dict]:
    tx = db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id))
    if tx is None:
        return []
    hom_nay = _dau_ngay(nay)
    ra = []

    sap_chay = list(
        db.scalars(
            select(Chuyen)
            .where(
                Chuyen.tai_xe_id == tx,
                Chuyen.trang_thai == "DA_CHOT",
                Chuyen.khoi_hanh_du_kien >= hom_nay,
                Chuyen.khoi_hanh_du_kien < hom_nay + timedelta(days=2),  # hôm nay và ngày mai
            )
            .order_by(Chuyen.khoi_hanh_du_kien)
        )
    )
    luc_chot = _lich_su_moi_nhat(db, "CHUYEN", [c.id for c in sap_chay], "DA_CHOT")
    for c in sap_chay:
        ra.append(
            _tb(
                "CHUYEN_DUOC_GIAO",
                CAN_LAM,
                f"Chuyến {c.ma_chuyen} khởi hành {_gio(c.khoi_hanh_du_kien)}",
                "Chuyến đã chốt, nhớ chụp đồng hồ km khi bắt đầu",
                "CHUYEN",
                c.id,
                luc_chot.get(c.id, c.khoi_hanh_du_kien),
            )
        )

    for s, ma in db.execute(
        select(SuCo, Chuyen.ma_chuyen)
        .join(Chuyen, Chuyen.id == SuCo.chuyen_id)
        .where(SuCo.tai_xe_id == tx, SuCo.trang_thai == "DONG", SuCo.luc >= nay - GAN_DAY)
    ):
        ra.append(
            _tb(
                "SU_CO_DA_DONG",
                THONG_TIN,
                f"Sự cố {TEN_SU_CO.get(s.loai, s.loai)} – chuyến {ma} đã được xử lý",
                s.cach_xu_ly,
                "CHUYEN",
                s.chuyen_id,
                s.luc,
            )
        )

    # Khoản chi bị từ chối hoặc duyệt khác số khai; lúc và lý do lấy từ nhật ký tiền (BR-62), lần mới nhất
    moi_nhat: dict[int, tuple] = {}
    for cp, ma, luc, ly_do in db.execute(
        select(ChiPhi, Chuyen.ma_chuyen, NhatKyTien.luc, NhatKyTien.ly_do)
        .join(Chuyen, Chuyen.id == ChiPhi.chuyen_id)
        .join(NhatKyTien, (NhatKyTien.bang == "chi_phi") & (NhatKyTien.ban_ghi_id == ChiPhi.id))
        .where(
            Chuyen.tai_xe_id == tx,
            NhatKyTien.hanh_dong.in_(("DUYET", "TU_CHOI")),
            NhatKyTien.luc >= nay - GAN_DAY,
            or_(ChiPhi.trang_thai == "TU_CHOI", ChiPhi.so_tien_duyet != ChiPhi.so_tien_khai),
        )
        .order_by(NhatKyTien.id)
    ):
        moi_nhat[cp.id] = (cp, ma, luc, ly_do)
    for cp, ma, luc, ly_do in moi_nhat.values():
        if cp.trang_thai == "TU_CHOI":
            tieu_de = f"Khoản chi {_tien(cp.so_tien_khai)} – chuyến {ma} bị từ chối"
        else:
            tieu_de = f"Khoản chi chuyến {ma} được duyệt {_tien(cp.so_tien_duyet)} (khai {_tien(cp.so_tien_khai)})"
        ra.append(_tb("CHI_PHI_DA_XU_LY", THONG_TIN, tieu_de, ly_do, "CHUYEN", cp.chuyen_id, luc))
    return ra


def thong_bao(db: Session, nd: NguoiDung) -> dict:
    nay = bay_gio()
    if nd.vai_tro in ("DIEU_PHOI", "QUAN_LY"):  # Quản lý kế thừa Điều phối
        ra = _dieu_phoi(db, nay)
    elif nd.vai_tro == "KE_TOAN":
        ra = _ke_toan(db)
    else:
        ra = _tai_xe(db, nd, nay)
    ra.sort(key=lambda t: t["luc"], reverse=True)
    return {"so_luong": len(ra), "thong_bao": ra}
