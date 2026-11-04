"""uc19 nap danh muc ly do

Revision ID: 2a4c8d5f38e7
Revises: 177fdcb334df
Create Date: 2026-11-04 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a4c8d5f38e7'
down_revision: Union[str, Sequence[str], None] = '177fdcb334df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Danh mục lý do lấy / giao không được (BR-42), phía cho BR-37 (story UC-19, quyết định 2).
# Ghi cứng ở đây, không import code app, để migration chạy được mãi về sau; khớp app/domain/ly_do.py (test so).
LY_DO = [
    ("Hàng chưa chuẩn bị xong", "LAY", "KHACH"),
    ("Không liên lạc được người gửi", "LAY", "KHACH"),
    ("Sai địa chỉ lấy hàng", "LAY", "KHACH"),
    ("Hàng khác mô tả (quá khổ, quá nặng)", "LAY", "KHACH"),
    ("Lý do khác", "LAY", "KHACH"),
    ("Xe hỏng / sự cố trên đường", "LAY", "SU_CO_XE"),
    ("Người nhận vắng", "GIAO", "KHACH"),
    ("Người nhận từ chối nhận", "GIAO", "KHACH"),
    ("Sai địa chỉ giao", "GIAO", "KHACH"),
    ("Lý do khác", "GIAO", "KHACH"),
    ("Hàng hư hỏng", "GIAO", "SU_CO_XE"),
    ("Xe hỏng / sự cố trên đường", "GIAO", "SU_CO_XE"),
]


def upgrade() -> None:
    """Upgrade schema."""
    ly_do = sa.table("ly_do", sa.column("ten", sa.String), sa.column("ap_dung", sa.String), sa.column("phia", sa.String))
    op.bulk_insert(ly_do, [{"ten": t, "ap_dung": a, "phia": p} for t, a, p in LY_DO])


def downgrade() -> None:
    """Downgrade schema."""
    # Chỉ xóa đúng các dòng đã nạp; lý do đã có lượt quét dùng thì khóa ngoại chặn (dữ liệu thật, không tự xóa)
    for t, a, p in LY_DO:
        op.execute(
            sa.text("DELETE FROM ly_do WHERE ten = :t AND ap_dung = :a AND phia = :p").bindparams(t=t, a=a, p=p)
        )
