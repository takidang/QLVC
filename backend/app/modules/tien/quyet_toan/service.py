"""UC-24 quyết toán: Kế toán duyệt / điều chỉnh / từ chối từng khoản chi, rồi khóa sổ chuyến (BR-29, 50, 51, 55, 68).

Khóa (kien-truc.md mục 6): duyệt / từ chối khóa chung dòng chuyến (`FOR SHARE`, như tài xế ghi chi phí) rồi khóa
riêng khoản; quyết toán khóa riêng dòng chuyến nên đợi mọi lượt duyệt / ghi chi phí đang chạy, và ngược lại.
"""

import json
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.loi import LoiNghiepVu
from app.models import (
    ChiPhi,
    Chuyen,
    DonHang,
    Ghep,
    KhachHang,
    LichSuTrangThai,
    NguoiDung,
    NhatKyTien,
    QuyetToan,
    TaiXe,
    TamUng,
    Tep,
    Tuyen,
    Xe,
)
from app.thoi_gian import bay_gio

LOAI_CHI = ("DAU", "CAU_DUONG", "BOC_XEP", "PHAT_SINH")
TEN_LOAI = {"DAU": "Dầu", "CAU_DUONG": "Cầu đường", "BOC_XEP": "Bốc xếp", "PHAT_SINH": "Phát sinh"}
XEM_DUOC = ("HOAN_THANH", "DA_QUYET_TOAN")
TEN_XU_LY = {
    "TAI_XE_DA_NOP": "tài xế đã nộp lại",
    "CONG_TY_DA_TRA": "công ty đã trả thêm",
    "KHONG_CHENH": "không chênh",
}
LECH_GIO = timedelta(minutes=5)  # giờ máy Kế toán nhanh hơn máy chủ vài phút vẫn nhận "bây giờ"


def _tien(so: int) -> str:
    return f"{so:,}".replace(",", ".") + " đ"


def _kiem_hoan_thanh(c: Chuyen, viec: str) -> None:
    if c.trang_thai == "DA_QUYET_TOAN":
        raise LoiNghiepVu("BR-29", f"Chuyến {c.ma_chuyen} đã quyết toán, không {viec} được", 409)
    if c.trang_thai != "HOAN_THANH":
        raise LoiNghiepVu("BR-55", f"Chuyến {c.ma_chuyen} chưa hoàn thành, chưa {viec} được", 409)


def _nhat_ky(db: Session, bang: str, ban_ghi_id: int, hanh_dong: str, cu, moi, ly_do, nd: NguoiDung) -> None:
    # Nhật ký tiền chỉ thêm, không sửa xóa (BR-62)
    db.add(
        NhatKyTien(
            bang=bang,
            ban_ghi_id=ban_ghi_id,
            hanh_dong=hanh_dong,
            gia_tri_cu=cu,
            gia_tri_moi=moi,
            ly_do=ly_do,
            nguoi=nd.id,
        )
    )


def _anh(db: Session, chi_phi_ids: list[int]) -> dict[int, list[int]]:
    ra: dict[int, list[int]] = {}
    for cp_id, tep_id in db.execute(
        select(Tep.chi_phi_id, Tep.id).where(Tep.chi_phi_id.in_(chi_phi_ids)).order_by(Tep.id)
    ):
        ra.setdefault(cp_id, []).append(tep_id)
    return ra


def _khoan_ra(cp: ChiPhi, anh: list[int]) -> dict:
    return {
        "id": cp.id,
        "loai": cp.loai,
        "so_tien_khai": cp.so_tien_khai,
        "so_tien_duyet": cp.so_tien_duyet,
        "so_lit": cp.so_lit,
        "ghi_chu": cp.ghi_chu,
        "trang_thai": cp.trang_thai,
        "anh": anh,
        "tao_luc": cp.tao_luc,
    }


def _gia_tri(cp: ChiPhi) -> str:
    return f"{cp.trang_thai} {cp.so_tien_duyet if cp.so_tien_duyet is not None else cp.so_tien_khai}"


# ---------- Duyệt / từ chối từng khoản (bước 2) ----------


def _khoa_khoan(db: Session, chi_phi_id: int, viec: str) -> ChiPhi:
    chuyen_id = db.scalar(select(ChiPhi.chuyen_id).where(ChiPhi.id == chi_phi_id))
    if chuyen_id is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khoản chi phí", 404)
    c = db.get(Chuyen, chuyen_id, with_for_update={"read": True}, populate_existing=True)
    _kiem_hoan_thanh(c, viec)  # chỉ duyệt khi đã hoàn thành (quyết định 2)
    return db.get(ChiPhi, chi_phi_id, with_for_update=True, populate_existing=True)


def duyet(db: Session, chi_phi_id: int, so_tien_duyet: int, ly_do: str | None, nd: NguoiDung) -> dict:
    cp = _khoa_khoan(db, chi_phi_id, "duyệt chi phí")
    if so_tien_duyet > cp.so_tien_khai:  # chỉ được giảm (quyết định 3)
        raise LoiNghiepVu("BR-55", f"Số duyệt không được lớn hơn số tài xế khai {_tien(cp.so_tien_khai)}", 422)
    if so_tien_duyet != cp.so_tien_khai and not ly_do:
        raise LoiNghiepVu("BR-55", "Điều chỉnh số tiền cần ghi lý do", 422)
    if cp.trang_thai == "DA_DUYET" and cp.so_tien_duyet == so_tien_duyet:
        raise LoiNghiepVu("KHONG_CO_THAY_DOI", "Khoản đã được duyệt đúng số này", 400)
    cu = _gia_tri(cp)
    cp.trang_thai, cp.so_tien_duyet, cp.nguoi_duyet = "DA_DUYET", so_tien_duyet, nd.id
    _nhat_ky(db, "chi_phi", cp.id, "DUYET", cu, _gia_tri(cp), ly_do or "Duyệt đúng số khai", nd)
    db.commit()
    return _khoan_ra(cp, _anh(db, [cp.id]).get(cp.id, []))


def tu_choi(db: Session, chi_phi_id: int, ly_do: str, nd: NguoiDung) -> dict:
    cp = _khoa_khoan(db, chi_phi_id, "từ chối chi phí")
    if cp.trang_thai == "TU_CHOI":
        raise LoiNghiepVu("KHONG_CO_THAY_DOI", "Khoản đã bị từ chối", 400)
    cu = _gia_tri(cp)
    cp.trang_thai, cp.so_tien_duyet, cp.nguoi_duyet = "TU_CHOI", None, nd.id
    _nhat_ky(db, "chi_phi", cp.id, "TU_CHOI", cu, "TU_CHOI", ly_do, nd)
    db.commit()
    return _khoan_ra(cp, _anh(db, [cp.id]).get(cp.id, []))


# ---------- Bảng quyết toán (bước 1, 3) ----------


def _don(db: Session, chuyen_id: int, ket_qua: str) -> list[dict]:
    dong = db.execute(
        select(DonHang.id, DonHang.ma_don, KhachHang.ten, DonHang.cuoc_tinh)
        .join(Ghep, Ghep.don_hang_id == DonHang.id)
        .join(KhachHang, KhachHang.id == DonHang.khach_hang_id)
        .where(Ghep.chuyen_id == chuyen_id, Ghep.ket_qua == ket_qua)
        .order_by(DonHang.ma_don)
    )
    return [{"id": i, "ma_don": m, "ten_khach": k, "cuoc": cuoc} for i, m, k, cuoc in dong]


def _tinh(db: Session, c: Chuyen, luong_tay: int | None = None) -> dict:
    """Mọi con số của quyết toán; dùng cho cả xem (GET) và khóa sổ (POST) để hai bên luôn khớp."""
    xe, tuyen = db.get(Xe, c.xe_id), db.get(Tuyen, c.tuyen_id)
    ten_tai_xe = db.scalar(
        select(NguoiDung.ho_ten).join(TaiXe, TaiXe.nguoi_dung_id == NguoiDung.id).where(TaiXe.id == c.tai_xe_id)
    )
    don_giao, don_that_bai = _don(db, c.id, "DA_GIAO"), _don(db, c.id, "THAT_BAI")
    doanh_thu = sum(d["cuoc"] for d in don_giao)  # BR-50: chỉ đơn giao thành công trên chuyến này

    khoan = list(db.scalars(select(ChiPhi).where(ChiPhi.chuyen_id == c.id).order_by(ChiPhi.id)))
    anh = _anh(db, [k.id for k in khoan])
    duyet = [k for k in khoan if k.trang_thai == "DA_DUYET"]
    dm = {"DAU": c.dm_dau_chot or 0, "CAU_DUONG": c.dm_cau_duong_chot or 0, "BOC_XEP": c.dm_boc_xep_chot or 0}
    theo_loai = []
    for loai in LOAI_CHI:
        thuc_te = sum(k.so_tien_duyet for k in duyet if k.loai == loai)
        theo_loai.append(
            {"loai": loai, "dinh_muc": dm.get(loai, 0), "thuc_te": thuc_te, "chenh_lech": thuc_te - dm.get(loai, 0)}
        )
    tong_chi = sum(k.so_tien_duyet for k in duyet)
    dinh_muc = sum(dm.values())

    km = c.km_ket_thuc - c.km_bat_dau if c.km_bat_dau is not None and c.km_ket_thuc is not None else None
    dau_tk = (
        (Decimal(km) * xe.dinh_muc_lit_100km / 100).quantize(Decimal("0.01"))
        if km is not None and xe.dinh_muc_lit_100km is not None
        else None
    )

    luong_chot = c.luong_tai_xe_chot or 0
    luong = luong_tay if luong_tay is not None else luong_chot  # BR-71, hoặc nhập tay BR-68
    tam_ung = int(
        db.scalar(
            select(func.coalesce(func.sum(TamUng.so_tien), 0)).where(
                TamUng.chuyen_id == c.id, TamUng.trang_thai == "HIEU_LUC"
            )
        )
    )
    chenh = tam_ung - tong_chi  # BR-55: dương tài xế nộp lại, âm công ty trả thêm
    lai = doanh_thu - tong_chi - luong  # BR-51
    lai_du_kien = doanh_thu + sum(d["cuoc"] for d in don_that_bai) - dinh_muc - luong_chot

    ly_do_lech = [{"mo_ta": f"Đơn {d['ma_don']} giao thất bại", "so_tien": -d["cuoc"]} for d in don_that_bai]
    for x in theo_loai:
        if x["chenh_lech"]:
            vuot = x["chenh_lech"] > 0
            ly_do_lech.append(
                {
                    "mo_ta": f"{TEN_LOAI[x['loai']]} {'vượt' if vuot else 'dưới'} định mức",
                    "so_tien": -x["chenh_lech"],
                }
            )
    if luong != luong_chot:
        ly_do_lech.append({"mo_ta": "Lương nhập tay khác lương đã chốt", "so_tien": luong_chot - luong})

    return {
        "chuyen_id": c.id,
        "ma_chuyen": c.ma_chuyen,
        "trang_thai": c.trang_thai,
        "bien_so": xe.bien_so,
        "ten_tai_xe": ten_tai_xe,
        "ten_tuyen": tuyen.ten,
        "ket_thuc_bat_thuong": c.ket_thuc_bat_thuong,
        "ly_do_ket_thuc": c.ly_do_ket_thuc,
        "don_giao": don_giao,
        "don_that_bai": don_that_bai,
        "doanh_thu": doanh_thu,
        "chi_theo_loai": theo_loai,
        "dinh_muc": dinh_muc,
        "tong_chi": tong_chi,
        "km": km,
        "dau_tham_khao_lit": dau_tk,
        "dau_thuc_te_lit": sum((k.so_lit or Decimal(0) for k in duyet if k.loai == "DAU"), Decimal(0)),
        "khoan": [_khoan_ra(k, anh.get(k.id, [])) for k in khoan],
        "so_cho_duyet": sum(k.trang_thai == "CHO_DUYET" for k in khoan),
        "luong_chot": luong_chot,
        "luong_tai_xe": luong,
        "can_luong_tay": c.ket_thuc_bat_thuong,
        "tong_tam_ung_hieu_luc": tam_ung,
        "chenh_lech_tam_ung": chenh,
        "xu_ly_goi_y": "TAI_XE_DA_NOP" if chenh > 0 else "CONG_TY_DA_TRA" if chenh < 0 else "KHONG_CHENH",
        "lai": lai,
        "lai_du_kien": lai_du_kien,
        "ly_do_lech": ly_do_lech,
    }


def bang(db: Session, chuyen_id: int) -> dict:
    c = db.get(Chuyen, chuyen_id)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    if c.trang_thai not in XEM_DUOC:
        raise LoiNghiepVu("BR-55", f"Chuyến {c.ma_chuyen} chưa hoàn thành, chưa có bảng quyết toán", 409)
    qt = db.scalar(select(QuyetToan).where(QuyetToan.chuyen_id == c.id))
    ra = _tinh(db, c, qt.luong_tai_xe if qt and qt.ly_do_luong_tay else None)
    ra |= {
        "ly_do_luong_tay": qt.ly_do_luong_tay if qt else None,
        "xu_ly_chenh_lech": qt.xu_ly_chenh_lech if qt else None,
        "hinh_thuc": qt.hinh_thuc if qt else None,
        "luc_xu_ly": qt.luc_xu_ly if qt else None,
        "luc_quyet_toan": qt.luc if qt else None,
    }
    return ra


# ---------- Khóa sổ (bước 4, 5) ----------


def quyet_toan(db: Session, chuyen_id: int, vao, nd: NguoiDung) -> dict:
    c = db.get(Chuyen, chuyen_id, with_for_update=True, populate_existing=True)
    if c is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy chuyến", 404)
    _kiem_hoan_thanh(c, "quyết toán")
    cho = list(
        db.scalars(
            select(ChiPhi.id).where(ChiPhi.chuyen_id == c.id, ChiPhi.trang_thai == "CHO_DUYET").order_by(ChiPhi.id)
        )
    )
    if cho:
        raise LoiNghiepVu(
            "BR-55", f"Còn {len(cho)} khoản chi chờ duyệt", 409, chi_tiet=[{"ma": "BR-55", "chi_phi_ids": cho}]
        )

    if c.ket_thuc_bat_thuong:  # BR-68
        if vao.luong_tay is None or not vao.ly_do_luong_tay:
            raise LoiNghiepVu("BR-68", "Chuyến kết thúc do sự cố: cần nhập lương tài xế và lý do", 422)
        luong_tay, ly_do_luong = vao.luong_tay, vao.ly_do_luong_tay
    else:  # chuyến bình thường: bỏ qua lương tay, dùng lương đã chốt (api.md 3.3)
        luong_tay, ly_do_luong = None, None

    t = _tinh(db, c, luong_tay)
    chenh, can = t["chenh_lech_tam_ung"], t["xu_ly_goi_y"]
    if vao.xu_ly_chenh_lech != can:
        raise LoiNghiepVu(
            "BR-55",
            "Chênh lệch tạm ứng "
            + (f"{_tien(abs(chenh))}: cần ghi " if chenh else "bằng 0: cần ghi ")
            + TEN_XU_LY[can],
            422,
            chi_tiet=[{"ma": "BR-55", "chenh_lech_tam_ung": chenh, "xu_ly_chenh_lech": can}],
        )
    if chenh:
        if vao.hinh_thuc is None or vao.luc_xu_ly is None:
            raise LoiNghiepVu("BR-55", "Cần ghi hình thức và thời điểm xử lý chênh lệch", 422)
        if vao.luc_xu_ly > bay_gio() + LECH_GIO:
            raise LoiNghiepVu("BR-55", "Thời điểm xử lý chênh lệch không được ở tương lai", 422)
        hinh_thuc, luc_xu_ly = vao.hinh_thuc, vao.luc_xu_ly
    else:  # quyết định 6
        hinh_thuc, luc_xu_ly = None, None

    qt = QuyetToan(
        chuyen_id=c.id,
        doanh_thu=t["doanh_thu"],
        tong_chi=t["tong_chi"],
        luong_tai_xe=t["luong_tai_xe"],
        ly_do_luong_tay=ly_do_luong,
        lai=t["lai"],
        chenh_lech_tam_ung=chenh,
        xu_ly_chenh_lech=can,
        hinh_thuc=hinh_thuc,
        luc_xu_ly=luc_xu_ly,
        ke_toan_id=nd.id,
    )
    db.add(qt)
    db.flush()
    db.add(LichSuTrangThai(doi_tuong="CHUYEN", doi_tuong_id=c.id, tu=c.trang_thai, sang="DA_QUYET_TOAN", nguoi=nd.id))
    c.trang_thai = "DA_QUYET_TOAN"  # BR-29: từ đây mọi lượt ghi tiền của chuyến trả 409
    so = {k: t[k] for k in ("doanh_thu", "tong_chi", "luong_tai_xe", "lai", "chenh_lech_tam_ung")}
    _nhat_ky(
        db,
        "quyet_toan",
        qt.id,
        "QUYET_TOAN",
        None,
        json.dumps(so | {"xu_ly_chenh_lech": can, "hinh_thuc": hinh_thuc}),
        f"Quyết toán chuyến {c.ma_chuyen}",
        nd,
    )
    if luong_tay is not None:
        _nhat_ky(db, "chuyen", c.id, "LUONG_TAY", str(t["luong_chot"]), str(luong_tay), ly_do_luong, nd)
    db.commit()
    return so | {"chuyen_id": c.id, "tong_tam_ung_hieu_luc": t["tong_tam_ung_hieu_luc"], "xu_ly_chenh_lech": can}
