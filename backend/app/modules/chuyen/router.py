from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from app.auth.phu_thuoc import can_vai_tro
from app.db import get_db
from app.models import NguoiDung
from app.modules.chuyen import service, theo_doi
from app.modules.chuyen.schemas import (
    ChotVao,
    ChuyenChiTiet,
    ChuyenNgay,
    ChuyenRa,
    ChuyenVao,
    DongSuCoVao,
    GhepVao,
    HuyVao,
    KetThucSuCoVao,
    PhanCongVao,
    SuCoRa,
    TaiXeKhaDung,
    TrangThaiChuyen,
    XeKhaDung,
)
from app.modules.don.schemas import DonRa
from app.phan_trang import DanhSach, PhanTrang, phan_trang

router = APIRouter(prefix="/api/chuyen", tags=["chuyen"])
Db = Annotated[Session, Depends(get_db)]

# Điều phối (Quản lý kế thừa) lập chuyến; Kế toán chỉ xem chuyến
XEM = Depends(can_vai_tro("DIEU_PHOI", "KE_TOAN"))
DIEU_PHOI = can_vai_tro("DIEU_PHOI")


# Đường dẫn cố định đặt trước đường dẫn có {id} (api.md mục 1)
@router.get("/xe-kha-dung", response_model=list[XeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def xe_kha_dung(tuyen_id: int, khoi_hanh: AwareDatetime, db: Db):
    return service.xe_kha_dung(db, tuyen_id, khoi_hanh)


@router.get("/tai-xe-kha-dung", response_model=list[TaiXeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def tai_xe_kha_dung(tuyen_id: int, khoi_hanh: AwareDatetime, db: Db, xe_id: int | None = None):
    return service.tai_xe_kha_dung(db, tuyen_id, khoi_hanh, xe_id)


@router.post("", response_model=ChuyenRa, status_code=201)
def tao(vao: ChuyenVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.lay(db, service.tao(db, vao, nd))


@router.get("", response_model=DanhSach[ChuyenNgay], dependencies=[XEM])
def danh_sach(
    db: Db,
    pt: Annotated[PhanTrang, Depends(phan_trang)],
    trang_thai: TrangThaiChuyen | None = None,
    ngay: date | None = None,
    tuyen_id: int | None = None,
):
    du_lieu, tong = service.danh_sach(db, pt, trang_thai, ngay, tuyen_id)
    if ngay:  # bảng chuyến trong ngày: tiến độ, % đầy, cờ (UC-32)
        du_lieu = theo_doi.bang_ngay(db, du_lieu)
    return {"du_lieu": du_lieu, "tong": tong}


@router.get("/{chuyen_id}", response_model=ChuyenChiTiet, dependencies=[XEM])
def chi_tiet(chuyen_id: int, db: Db):
    return theo_doi.chi_tiet(db, chuyen_id)


@router.get("/{chuyen_id}/xe-kha-dung", response_model=list[XeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def xe_kha_dung_chuyen(chuyen_id: int, db: Db):
    return service.xe_kha_dung_chuyen(db, chuyen_id)


@router.get("/{chuyen_id}/tai-xe-kha-dung", response_model=list[TaiXeKhaDung], dependencies=[Depends(DIEU_PHOI)])
def tai_xe_kha_dung_chuyen(chuyen_id: int, db: Db, xe_id: int | None = None):
    return service.tai_xe_kha_dung_chuyen(db, chuyen_id, xe_id)


@router.put("/{chuyen_id}/phan-cong", response_model=ChuyenChiTiet, dependencies=[Depends(DIEU_PHOI)])
def phan_cong(chuyen_id: int, vao: PhanCongVao, db: Db):
    return service.phan_cong(db, chuyen_id, vao.xe_id, vao.tai_xe_id)


@router.get("/{chuyen_id}/don-phu-hop", response_model=list[DonRa], dependencies=[Depends(DIEU_PHOI)])
def don_phu_hop(chuyen_id: int, db: Db):
    return service.don_phu_hop(db, chuyen_id)


@router.post("/{chuyen_id}/ghep", response_model=ChuyenChiTiet)
def ghep(chuyen_id: int, vao: GhepVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.ghep(db, chuyen_id, vao.don_ids, nd)


@router.post("/{chuyen_id}/go", response_model=ChuyenChiTiet)
def go(chuyen_id: int, vao: GhepVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.go(db, chuyen_id, vao.don_ids, nd)


@router.post("/{chuyen_id}/chot", response_model=ChuyenChiTiet)
def chot(chuyen_id: int, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)], vao: ChotVao | None = None):
    vao = vao or ChotVao()
    return service.chot(db, chuyen_id, vao.xac_nhan_chay_rong, vao.xac_nhan_lai_am, nd)


@router.post("/{chuyen_id}/mo-chot", response_model=ChuyenChiTiet)
def mo_chot(chuyen_id: int, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.mo_chot(db, chuyen_id, nd)


@router.post("/{chuyen_id}/huy", response_model=ChuyenChiTiet)
def huy(chuyen_id: int, vao: HuyVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return service.huy(db, chuyen_id, vao.ly_do, nd)


@router.post("/{chuyen_id}/ket-thuc-su-co", response_model=ChuyenChiTiet)
def ket_thuc_su_co(chuyen_id: int, vao: KetThucSuCoVao, db: Db, nd: Annotated[NguoiDung, Depends(DIEU_PHOI)]):
    return theo_doi.ket_thuc_su_co(db, chuyen_id, vao.ly_do, vao.km_ket_thuc, nd)


# Sự cố do tài xế báo ở UC-33 (Kiệt); Điều phối đóng ở UC-32. Đặt trong module chuyến, không tạo module su_co
router_su_co = APIRouter(prefix="/api/su-co", tags=["su-co"])


@router_su_co.post("/{su_co_id}/dong", response_model=SuCoRa, dependencies=[Depends(DIEU_PHOI)])
def dong_su_co(su_co_id: int, vao: DongSuCoVao, db: Db):
    return theo_doi.dong_su_co(db, su_co_id, vao.cach_xu_ly)
