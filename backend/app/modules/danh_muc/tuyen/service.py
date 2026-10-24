from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.tuyen import NutTuyen, canh_bao_br20, kiem_br66_thoi_gian_tuyen, kiem_cau_truc_tuyen
from app.loi import LoiNghiepVu
from app.models import Chuyen, Nut, Tuyen, TuyenNut
from app.modules.danh_muc.cau_hinh import service as cau_hinh
from app.modules.danh_muc.tuyen.schemas import NutTuyenVao, TuyenSua, TuyenVao
from app.phan_trang import PhanTrang


def _gio_lai(db: Session) -> tuple[int, int]:
    """CFG-07 ngày/tuần/liên tục → (giờ một ngày, giờ liên tục)."""
    ngay, _, lien_tuc = (int(x) for x in cau_hinh.lay(db, "CFG-07").split("/"))
    return ngay, lien_tuc


def _kiem_nut(db: Session, nut: list[NutTuyenVao]) -> list[NutTuyen]:
    ds = [NutTuyen(n.nut_id, n.phut_tu_diem_dau, n.km_tu_diem_dau, n.la_diem_nghi) for n in nut]
    kiem_cau_truc_tuyen(ds)
    co = set(db.scalars(select(Nut.id).where(Nut.id.in_([n.nut_id for n in ds]))))
    if thieu := [n.nut_id for n in ds if n.nut_id not in co]:
        raise LoiNghiepVu("KHONG_TIM_THAY", f"Không tìm thấy nút {thieu}", 404)
    kiem_br66_thoi_gian_tuyen(ds, _gio_lai(db)[0])
    return ds


def _ghi_nut(db: Session, tuyen_id: int, ds: list[NutTuyen]) -> None:
    db.execute(delete(TuyenNut).where(TuyenNut.tuyen_id == tuyen_id))
    db.add_all(
        TuyenNut(
            tuyen_id=tuyen_id,
            thu_tu=i,
            nut_id=n.nut_id,
            phut_tu_diem_dau=n.phut_tu_diem_dau,
            km_tu_diem_dau=n.km_tu_diem_dau,
            la_diem_nghi=n.la_diem_nghi,
        )
        for i, n in enumerate(ds, start=1)
    )


def _luu(db: Session, ma: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise LoiNghiepVu("MA_TUYEN_TRUNG", f"Mã tuyến {ma} đã có", 409) from None


def tao(db: Session, vao: TuyenVao) -> int:
    ds = _kiem_nut(db, vao.nut)
    tuyen = Tuyen(**vao.model_dump(exclude={"nut"}))
    db.add(tuyen)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise LoiNghiepVu("MA_TUYEN_TRUNG", f"Mã tuyến {vao.ma} đã có", 409) from None
    _ghi_nut(db, tuyen.id, ds)
    _luu(db, vao.ma)
    return tuyen.id


def sua(db: Session, tuyen_id: int, vao: TuyenSua) -> None:
    tuyen = db.get(Tuyen, tuyen_id, with_for_update=True)
    if tuyen is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tuyến", 404)
    thay_doi = vao.model_dump(exclude_unset=True, exclude={"nut"})
    if vao.nut is not None:
        # Đổi nút làm đổi ETA của chuyến đã lập (quyết định UC-05 số 4)
        co_chuyen = db.scalar(select(Chuyen.id).where(Chuyen.tuyen_id == tuyen_id, Chuyen.trang_thai != "HUY").limit(1))
        if co_chuyen:
            raise LoiNghiepVu(
                "TUYEN_DA_CO_CHUYEN", "Tuyến đã có chuyến, không đổi nút được; tạo tuyến mới và ngừng tuyến này", 409
            )
        _ghi_nut(db, tuyen_id, _kiem_nut(db, vao.nut))
    for truong, gia_tri in thay_doi.items():
        setattr(tuyen, truong, gia_tri)
    _luu(db, tuyen.ma)


def lay(db: Session, tuyen_id: int) -> dict:
    tuyen = db.get(Tuyen, tuyen_id)
    if tuyen is None:
        raise LoiNghiepVu("KHONG_TIM_THAY", "Không tìm thấy tuyến", 404)
    return _ra_nhieu(db, [tuyen])[0]


def danh_sach(db: Session, pt: PhanTrang, trang_thai: str | None, tim: str | None) -> tuple[list[dict], int]:
    loc = select(Tuyen)
    if trang_thai:
        loc = loc.where(Tuyen.trang_thai == trang_thai)
    if tim and (tim := tim.strip()):
        loc = loc.where(or_(Tuyen.ma.icontains(tim, autoescape=True), Tuyen.ten.icontains(tim, autoescape=True)))
    tong = db.scalar(select(func.count()).select_from(loc.subquery()))
    tuyen = db.scalars(loc.order_by(Tuyen.ma).offset(pt.bo_qua).limit(pt.so_dong)).all()
    return _ra_nhieu(db, list(tuyen)), tong


def _ra_nhieu(db: Session, ds_tuyen: list[Tuyen]) -> list[dict]:
    # Một truy vấn lấy nút của mọi tuyến trong trang, không truy vấn từng tuyến
    dong = db.execute(
        select(TuyenNut, Nut.ten, Nut.tinh)
        .join(Nut, Nut.id == TuyenNut.nut_id)
        .where(TuyenNut.tuyen_id.in_([t.id for t in ds_tuyen]))
        .order_by(TuyenNut.tuyen_id, TuyenNut.thu_tu)
    ).all()
    lien_tuc = _gio_lai(db)[1]
    ket_qua = []
    for t in ds_tuyen:
        cua_tuyen = [(tn, ten, tinh) for tn, ten, tinh in dong if tn.tuyen_id == t.id]
        nut = [
            {
                "thu_tu": tn.thu_tu,
                "nut_id": tn.nut_id,
                "ten": ten,
                "tinh": tinh,
                "phut_tu_diem_dau": tn.phut_tu_diem_dau,
                "km_tu_diem_dau": tn.km_tu_diem_dau,
                "la_diem_nghi": tn.la_diem_nghi,
            }
            for tn, ten, tinh in cua_tuyen
        ]
        ds = [NutTuyen(n["nut_id"], n["phut_tu_diem_dau"], n["km_tu_diem_dau"], n["la_diem_nghi"]) for n in nut]
        ket_qua.append(
            {
                c: getattr(t, c)
                for c in ("id", "ma", "ten", "dm_dau", "dm_cau_duong", "dm_boc_xep", "dm_luong_tai_xe", "trang_thai")
            }
            | {
                "nut": nut,
                "tong_phut": nut[-1]["phut_tu_diem_dau"] if nut else 0,
                "tong_km": nut[-1]["km_tu_diem_dau"] if nut else 0,
                "canh_bao": canh_bao_br20(ds, {n["nut_id"]: n["ten"] for n in nut}, lien_tuc) if ds else [],
            }
        )
    return ket_qua
