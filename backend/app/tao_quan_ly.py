"""Tạo tài khoản Quản lý đầu tiên: python -m app.tao_quan_ly (UC-01-AC11)."""

import sys
from getpass import getpass

from sqlalchemy.orm import sessionmaker

from app.auth.service import tao_quan_ly
from app.db import get_engine


def main() -> int:
    ten = input("Tên đăng nhập: ").strip()
    ho_ten = input("Họ tên: ").strip()
    mat_khau = getpass("Mật khẩu (ít nhất 8 ký tự, không hiện khi gõ): ")
    if mat_khau != getpass("Nhập lại mật khẩu: "):
        print("Hai lần nhập mật khẩu không khớp", file=sys.stderr)
        return 1
    with sessionmaker(get_engine())() as db:
        try:
            nd = tao_quan_ly(db, ten, ho_ten, mat_khau)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
    print(f"Đã tạo tài khoản Quản lý {nd.ten_dang_nhap!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
