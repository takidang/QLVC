import pytest
from pydantic import ValidationError

from app.auth.bao_mat import bam_mat_khau, dung_mat_khau
from app.config import Settings


def test_uc01_ac1_mat_khau_luu_dang_bam_argon2():
    bam = bam_mat_khau("matkhau123")
    assert bam.startswith("$argon2")
    assert "matkhau123" not in bam
    assert dung_mat_khau(bam, "matkhau123")
    assert not dung_mat_khau(bam, "matkhau124")  # sai một ký tự


@pytest.mark.parametrize("thieu", ["DATABASE_URL", "JWT_SECRET"])
def test_uc01_ac2_thieu_bien_moi_truong_thi_khong_khoi_dong(monkeypatch, thieu):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@127.0.0.1/db")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.delenv(thieu)
    with pytest.raises(ValidationError, match=thieu.lower()):
        Settings(_env_file=None)


def test_uc01_ac2_jwt_secret_qua_ngan_bi_tu_choi(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@127.0.0.1/db")
    monkeypatch.setenv("JWT_SECRET", "x" * 31)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
