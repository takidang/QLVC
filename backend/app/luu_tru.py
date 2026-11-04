"""Lưu ảnh, chữ ký (kien-truc.md KT-07, mục 9). Dùng chung cho UC-18…21, 33.

shortcut: chỉ ghi thư mục local (dev); Supabase Storage làm khi triển khai demo (`LUU_TRU=supabase`).
"""

import uuid
from pathlib import Path

from app.loi import LoiNghiepVu

KICH_THUOC_TOI_DA = 500 * 1024  # NFR-PER-03: trình duyệt nén trước, máy chủ vẫn chặn
THU_MUC = Path(__file__).resolve().parents[1] / "uploads"  # .gitignore: backend/uploads/
# Nhận diện theo vài byte đầu file, không tin đuôi tên hay Content-Type người dùng gửi (security-rules)
_DAU_FILE = {b"\xff\xd8\xff": ".jpg", b"\x89PNG\r\n\x1a\n": ".png"}


def kiem_anh(du_lieu: bytes) -> str:
    """Trả đuôi file theo loại thật; sai thì 400, lớn quá thì 413 (kien-truc.md mục 7)."""
    if not du_lieu:
        raise LoiNghiepVu("ANH_RONG", "Chưa có ảnh", 400)
    if len(du_lieu) > KICH_THUOC_TOI_DA:
        raise LoiNghiepVu("ANH_QUA_LON", "Ảnh lớn hơn 500 KB", 413)
    for dau, duoi in _DAU_FILE.items():
        if du_lieu.startswith(dau):
            return duoi
    raise LoiNghiepVu("ANH_SAI_LOAI", "Ảnh phải là JPEG hoặc PNG", 400)


def luu(du_lieu: bytes, duoi: str) -> str:
    """Ghi file với tên do máy chủ sinh; trả tên để lưu vào bảng TEP."""
    THU_MUC.mkdir(parents=True, exist_ok=True)
    ten = f"{uuid.uuid4().hex}{duoi}"
    (THU_MUC / ten).write_bytes(du_lieu)
    return ten


def xoa(ten: str) -> None:
    (THU_MUC / ten).unlink(missing_ok=True)
