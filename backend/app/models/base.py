from datetime import datetime

from sqlalchemy import BigInteger, DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, mapped_column

# Đặt tên ràng buộc cố định để migration Alembic ổn định giữa các máy
NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)
    # Tiền là số nguyên đồng, lưu bigint (NFR-FUN-02)
    type_annotation_map = {int: BigInteger, datetime: DateTime(timezone=True)}


def luc_tao():
    """Cột thời điểm do máy chủ CSDL ghi, client không gửi được."""
    return mapped_column(server_default=func.now())
