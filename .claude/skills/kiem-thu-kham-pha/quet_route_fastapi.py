"""Liệt kê route: có cần đăng nhập không, giới hạn vai trò nào."""
import sys
sys.path.insert(0, ".")
from fastapi.routing import APIRoute
from app.main import app


def duyet(dep, out):
    fn = dep.call
    name = getattr(fn, "__qualname__", repr(fn))
    clo = getattr(fn, "__closure__", None)
    if "can_vai_tro" in name and clo:
        for c in clo:
            v = c.cell_contents
            if isinstance(v, (tuple, frozenset, set)):
                out.add("vai_tro=" + ",".join(sorted(v)))
    if "nguoi_dung_hien_tai" in name:
        out.add("dang_nhap")
    for d in dep.dependencies:
        duyet(d, out)


def tat_ca(routes):
    for r in routes:
        if hasattr(r, "original_router"):
            yield from tat_ca(r.original_router.routes)
        elif isinstance(r, APIRoute):
            yield r


for r in tat_ca(app.routes):
    out = set()
    duyet(r.dependant, out)
    vt = sorted(x for x in out if x.startswith("vai_tro"))
    nhan = " | ".join(vt) if vt else ("CHI DANG NHAP" if out else "KHONG CAN DANG NHAP")
    print(f"{','.join(sorted(r.methods)):7} {r.path:60} {nhan}")
