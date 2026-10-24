import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config import Settings

# Test chạy trên CSDL riêng "<tên>_test" để không đụng dữ liệu dev. Đặt trước khi app đọc cấu hình.
_url = make_url(Settings().database_url)
TEST_URL = _url.set(database=f"{_url.database}_test")
os.environ["DATABASE_URL"] = TEST_URL.render_as_string(hide_password=False)

from app.auth.bao_mat import bam_mat_khau  # noqa: E402
from app.db import get_engine  # noqa: E402
from app.domain.cau_hinh import THAM_SO  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, NguoiDung  # noqa: E402


@pytest.fixture(scope="session")
def _csdl_test():
    may_chu = create_engine(_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with may_chu.connect() as c:
        if not c.scalar(text("SELECT 1 FROM pg_database WHERE datname = :d"), {"d": TEST_URL.database}):
            c.execute(text(f'CREATE DATABASE "{TEST_URL.database}"'))
    may_chu.dispose()

    engine = get_engine()
    with engine.begin() as c:
        Base.metadata.drop_all(c)
        c.execute(text("DROP TABLE IF EXISTS alembic_version"))
    # Dựng bảng bằng migration thật, để test cũng kiểm migration khớp models
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")
    # Giá trị CFG migration nạp phải khớp THAM_SO trong code (hai nơi ghi cùng một danh sách)
    with engine.connect() as c:
        da_nap = dict(c.execute(text("SELECT ma, gia_tri FROM cau_hinh")).all())
    assert da_nap == {ma: ts.mac_dinh for ma, ts in THAM_SO.items()}, "Migration CFG lệch app/domain/cau_hinh.py"
    return engine


@pytest.fixture
def db(_csdl_test):
    with Session(_csdl_test, expire_on_commit=False) as s:
        yield s
    with _csdl_test.begin() as c:
        bang = ", ".join(t.name for t in Base.metadata.sorted_tables)
        c.execute(text(f"TRUNCATE {bang} RESTART IDENTITY CASCADE"))
        # Migration nạp sẵn CFG mặc định; xóa bảng xong thì nạp lại để test sau vẫn có
        for ma, ts in THAM_SO.items():
            c.execute(text("INSERT INTO cau_hinh (ma, gia_tri) VALUES (:ma, :gt)"), {"ma": ma, "gt": ts.mac_dinh})


@pytest.fixture
def client(db):
    # https để trình khách gửi cookie Secure
    with TestClient(app, base_url="https://testserver") as c:
        yield c


@pytest.fixture
def tao_nguoi_dung(db):
    def tao(ten="dp1", vai_tro="DIEU_PHOI", mat_khau="matkhau123", trang_thai="HOAT_DONG") -> NguoiDung:
        nd = NguoiDung(
            ten_dang_nhap=ten,
            ho_ten=f"Người {ten}",
            vai_tro=vai_tro,
            trang_thai=trang_thai,
            mat_khau_bam=bam_mat_khau(mat_khau),
        )
        db.add(nd)
        db.commit()
        return nd

    return tao


@pytest.fixture
def dang_nhap_voi(client, tao_nguoi_dung):
    """Đăng nhập client bằng một vai trò, mỗi vai trò tạo một tài khoản. Dùng: dang_nhap_voi("KE_TOAN")."""
    da_tao: dict[str, NguoiDung] = {}

    def dang_nhap(vai_tro: str) -> NguoiDung:
        if vai_tro not in da_tao:
            da_tao[vai_tro] = tao_nguoi_dung(ten=vai_tro.lower(), vai_tro=vai_tro)
        r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": vai_tro.lower(), "mat_khau": "matkhau123"})
        assert r.status_code == 200
        return da_tao[vai_tro]

    return dang_nhap
