from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.config import get_settings

THOI_HAN_TOKEN = timedelta(hours=8)  # NFR-SEC-01
_ph = PasswordHasher()


def bam_mat_khau(mat_khau: str) -> str:
    return _ph.hash(mat_khau)


def dung_mat_khau(mat_khau_bam: str, mat_khau: str) -> bool:
    try:
        return _ph.verify(mat_khau_bam, mat_khau)
    except VerificationError:
        return False


def tao_token(nguoi_dung_id: int, bay_gio: datetime) -> str:
    payload = {"sub": str(nguoi_dung_id), "iat": bay_gio, "exp": bay_gio + THOI_HAN_TOKEN}
    return jwt.encode(payload, get_settings().jwt_secret, algorithm="HS256")


def doc_token(token: str) -> int | None:
    """Trả id người dùng, hoặc None nếu token sai chữ ký, sai thuật toán, hết hạn."""
    try:
        # Chỉ nhận HS256: chặn token "alg: none" và tráo thuật toán
        payload = jwt.decode(
            token, get_settings().jwt_secret, algorithms=["HS256"], options={"require": ["exp", "sub"]}
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
