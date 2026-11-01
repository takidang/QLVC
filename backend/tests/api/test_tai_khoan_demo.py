from sqlalchemy import select

from app.auth.bao_mat import dung_mat_khau
from app.models import NguoiDung, TaiXe
from app.tai_khoan_demo import MAT_KHAU_DEV, tao_tai_khoan_demo


def test_tao_du_bon_vai_tro_va_dang_nhap_duoc(client, db):
    tao_tai_khoan_demo(db, MAT_KHAU_DEV)
    vai_tro = dict(db.execute(select(NguoiDung.ten_dang_nhap, NguoiDung.vai_tro)).all())
    assert vai_tro == {"quanly": "QUAN_LY", "dieuphoi": "DIEU_PHOI", "ketoan": "KE_TOAN", "taixe": "TAI_XE"}
    assert db.scalar(select(TaiXe).join(NguoiDung).where(NguoiDung.ten_dang_nhap == "taixe")) is not None
    r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": "dieuphoi", "mat_khau": MAT_KHAU_DEV})
    assert r.status_code == 200, r.text


def test_chay_lai_thi_dat_lai_mat_khau_va_mo_khoa(db):
    tao_tai_khoan_demo(db, MAT_KHAU_DEV)
    ql = db.scalar(select(NguoiDung).where(NguoiDung.ten_dang_nhap == "quanly"))
    ql.trang_thai, ql.so_lan_sai = "NGUNG", 3
    db.commit()

    tao_tai_khoan_demo(db, "matkhaumoi1")
    db.refresh(ql)
    assert (ql.trang_thai, ql.so_lan_sai, ql.khoa_den) == ("HOAT_DONG", 0, None)
    assert dung_mat_khau(ql.mat_khau_bam, "matkhaumoi1")
    assert db.scalar(select(TaiXe.id).where(TaiXe.so_gplx == "DEMO000001")) is not None
    assert len(db.scalars(select(TaiXe)).all()) == 1  # không tạo trùng hồ sơ tài xế
