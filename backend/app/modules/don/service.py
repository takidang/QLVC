import secrets
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from app.domain.cuoc import kiem_br31_don_hop_le, kl_quy_doi, kl_tinh_cuoc, tinh_cuoc
from app.loi import LoiNghiepVu
from app.models import Chuyen, DonHang, Ghep, KhachHang, LichSuTrangThai, NguoiDung, Nut
from app.modules.danh_muc.bang_gia.service import tra_gia
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.modules.don.schemas import DonVao
from app.phan_trang import PhanTrang
from app.thoi_gian import bay_gio, hom_nay_vn

# Bỏ 0, O, 1, I để đọc mã qua điện thoại không nhầm (quyết định UC-08 số 1)
KY_TU_MA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def sinh_ma_don() -> str:
    return "DH-" + "".join(secrets.choice(KY_TU_MA) for _ in range(6))


@dataclass
class BaoGia:
    kl_quy_doi: Decimal
    kl_tinh_cuoc: Decimal
    don_gia_kg: int
    cuoc_toi_thieu: int
    he_so: int
    buoc: int
    cuoc: int


def _nut(db: Session, nut_id: int) -> Nut:
    nut = db.get(Nut, nut_id)
    if nut is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", f"Không tìm thấy nút {nut_id}", 404)
    return nut


def bao_gia(db: Session, nut_lay_id: int, nut_giao_id: int, kg: Decimal, m3: Decimal) -> BaoGia:
    """Tính cước theo giá đang hiệu lực hôm nay của cặp tỉnh và CFG hiện hành (BR-46…48)."""
    lay, giao = _nut(db, nut_lay_id), _nut(db, nut_giao_id)
    bg = tra_gia(db, lay.tinh, giao.tinh, hom_nay_vn())
    if bg is None:
        raise LoiNghiepVu("BR-48", f"Chưa có bảng giá {lay.tinh} → {giao.tinh}, không tạo được đơn")
    he_so, buoc = int(cau_hinh.lay(db, "CFG-01")), int(cau_hinh.lay(db, "CFG-06"))
    kl_qd = kl_quy_doi(m3, he_so)
    kl_tc = kl_tinh_cuoc(kg, kl_qd)
    return BaoGia(
        kl_qd,
        kl_tc,
        bg.don_gia_kg,
        bg.cuoc_toi_thieu,
        he_so,
        buoc,
        tinh_cuoc(kl_tc, bg.don_gia_kg, bg.cuoc_toi_thieu, buoc),
    )


def tao(db: Session, vao: DonVao, nguoi: NguoiDung) -> DonHang:
    kh = db.get(KhachHang, vao.khach_hang_id)
    if kh is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy khách hàng", 404)
    if kh.trang_thai != "HOAT_DONG":
        raise LoiNghiepVu("KHACH_NGUNG", f"Khách hàng {kh.ten} đã ngừng, không tạo đơn được")
    kiem_br31_don_hop_le(vao.dia_chi_lay, vao.dia_chi_giao, vao.lay_tu, vao.lay_den, vao.han_giao, bay_gio())
    bg = bao_gia(db, vao.nut_lay_id, vao.nut_giao_id, vao.kg, vao.m3)

    for _ in range(3):  # mã ngẫu nhiên trùng (rất hiếm) thì sinh lại
        don = DonHang(
            **vao.model_dump(),
            ma_don=sinh_ma_don(),
            # Chốt cước và bản sao giá ngay lúc tạo (BR-32): đổi bảng giá hay CFG sau đó không ảnh hưởng
            don_gia_chot=bg.don_gia_kg,
            cuoc_toi_thieu_chot=bg.cuoc_toi_thieu,
            he_so_quy_doi_chot=bg.he_so,
            lam_tron_chot=bg.buoc,
            kl_tinh_cuoc=bg.kl_tinh_cuoc,
            cuoc_tinh=bg.cuoc,
        )
        db.add(don)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            continue
        db.add(LichSuTrangThai(doi_tuong="DON", doi_tuong_id=don.id, tu=None, sang=don.trang_thai, nguoi=nguoi.id))
        db.commit()
        return don
    raise LoiNghiepVu("LOI_MA_DON", "Không sinh được mã đơn, vui lòng thử lại", 409)


NutLay, NutGiao = aliased(Nut), aliased(Nut)
_CHON = (DonHang, KhachHang.ten, NutLay.tinh, NutGiao.tinh)


def ra_don(dong) -> dict:
    don, ten_khach, tinh_lay, tinh_giao = dong
    return {
        **{c: getattr(don, c) for c in DonHang.__mapper__.columns.keys()},
        "ten_khach": ten_khach,
        "tinh_lay": tinh_lay,
        "tinh_giao": tinh_giao,
    }


def truy_van_don():
    return (
        select(*_CHON)
        .join(KhachHang, KhachHang.id == DonHang.khach_hang_id)
        .join(NutLay, NutLay.id == DonHang.nut_lay_id)
        .join(NutGiao, NutGiao.id == DonHang.nut_giao_id)
    )


def lay(db: Session, don_id: int) -> dict:
    dong = db.execute(truy_van_don().where(DonHang.id == don_id)).first()
    if dong is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy đơn hàng", 404)
    return ra_don(dong)


def danh_sach(
    db: Session, pt: PhanTrang, trang_thai: str | None, khach_hang_id: int | None, tim: str | None
) -> tuple[list[dict], int]:
    loc = truy_van_don()
    if trang_thai:
        loc = loc.where(DonHang.trang_thai == trang_thai)
    if khach_hang_id:
        loc = loc.where(DonHang.khach_hang_id == khach_hang_id)
    if tim and (tim := tim.strip()):
        loc = loc.where(DonHang.ma_don.icontains(tim, autoescape=True))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    ra = [
        ra_don(d)
        for d in db.execute(loc.order_by(DonHang.tao_luc.desc(), DonHang.id.desc()).offset(pt.bo_qua).limit(pt.so_dong))
    ]
    # Trạng thái chuyến của đơn đang ghép: giao diện ẩn Sửa / Hủy khi chuyến không còn Đang lập (BR-33, 34)
    chuyen = dict(
        db.execute(
            select(Ghep.don_hang_id, Chuyen.trang_thai)
            .join(Chuyen, Chuyen.id == Ghep.chuyen_id)
            .where(Ghep.hieu_luc, Ghep.don_hang_id.in_([d["id"] for d in ra]))
        ).all()
    )
    for d in ra:
        d["trang_thai_chuyen"] = chuyen.get(d["id"])
    return ra, tong
