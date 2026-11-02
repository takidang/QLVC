"""Tạo sẵn (hoặc đặt lại) một tài khoản cho mỗi vai trò để thử, demo: python -m app.tai_khoan_demo.

Chạy lại bao nhiêu lần cũng được: tài khoản đã có thì đặt lại mật khẩu, mở khóa.
Máy dev dùng mật khẩu chung MAT_KHAU_DEV; bản demo (APP_ENV=demo) bắt buộc truyền mật khẩu riêng.
"""

import sys
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.auth.bao_mat import bam_mat_khau
from app.config import get_settings
from app.db import get_engine
from app.models import NguoiDung, TaiXe

MAT_KHAU_DEV = "demo12345"
TAI_KHOAN = [
    ("quanly", "Quản lý Demo", "QUAN_LY"),
    ("dieuphoi", "Điều phối Demo", "DIEU_PHOI"),
    ("ketoan", "Kế toán Demo", "KE_TOAN"),
    ("taixe", "Tài xế Demo", "TAI_XE"),
]


def tao_tai_khoan_demo(db: Session, mat_khau: str) -> list[str]:
    if len(mat_khau) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
    bam = bam_mat_khau(mat_khau)
    for ten, ho_ten, vai_tro in TAI_KHOAN:
        nd = db.scalar(select(NguoiDung).where(NguoiDung.ten_dang_nhap == ten))
        if nd is None:
            nd = NguoiDung(ten_dang_nhap=ten, ho_ten=ho_ten, vai_tro=vai_tro)
            db.add(nd)
        nd.mat_khau_bam, nd.trang_thai, nd.so_lan_sai, nd.khoa_den = bam, "HOAT_DONG", 0, None
        db.flush()
        # Tài khoản tài xế phải kèm hồ sơ tài xế (UC-04)
        if vai_tro == "TAI_XE" and not db.scalar(select(TaiXe.id).where(TaiXe.nguoi_dung_id == nd.id)):
            hs = dict(so_gplx="DEMO000001", hang_gplx="C", han_gplx=date(2035, 12, 31), sdt="0900000000")
            db.add(TaiXe(nguoi_dung_id=nd.id, **hs))
    db.commit()
    return [ten for ten, _, _ in TAI_KHOAN]


def main(argv: list[str]) -> int:
    if argv:
        mat_khau = argv[0]
    elif get_settings().app_env == "dev":
        mat_khau = MAT_KHAU_DEV
    else:
        print("Bản demo phải truyền mật khẩu: python -m app.tai_khoan_demo <mật khẩu>", file=sys.stderr)
        return 1
    with sessionmaker(get_engine())() as db:
        try:
            ds = tao_tai_khoan_demo(db, mat_khau)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
    print(f"Đã tạo/đặt lại: {', '.join(ds)}" + (f" (mật khẩu {MAT_KHAU_DEV})" if not argv else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
