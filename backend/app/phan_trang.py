"""Phân trang dùng chung cho mọi danh sách (api.md mục 1: ?trang=&so_dong= → {du_lieu, tong})."""

from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class PhanTrang(BaseModel):
    trang: int
    so_dong: int

    @property
    def bo_qua(self) -> int:
        return (self.trang - 1) * self.so_dong


def phan_trang(trang: Annotated[int, Query(ge=1)] = 1, so_dong: Annotated[int, Query(ge=1, le=100)] = 20) -> PhanTrang:
    return PhanTrang(trang=trang, so_dong=so_dong)


class DanhSach[T](BaseModel):
    du_lieu: list[T]
    tong: int
