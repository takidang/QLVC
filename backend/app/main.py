from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.config import get_settings
from app.loi import LoiNghiepVu
from app.modules.danh_muc.bang_gia.router import router as bang_gia_router
from app.modules.danh_muc.cau_hinh.router import router as cau_hinh_router
from app.modules.danh_muc.khach_hang.router import router as khach_hang_router
from app.modules.danh_muc.nut.router import router as nut_router
from app.modules.danh_muc.tai_xe.router import router as tai_xe_router
from app.modules.danh_muc.tuyen.router import router as tuyen_router
from app.modules.danh_muc.xe.router import router as xe_router
from app.modules.don.router import router as don_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()  # thiếu JWT_SECRET / DATABASE_URL thì dừng ngay lúc khởi động (UC-01-AC2)
    yield


app = FastAPI(title="QLVC", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(xe_router)
app.include_router(tai_xe_router)
app.include_router(khach_hang_router)
app.include_router(bang_gia_router)
app.include_router(cau_hinh_router)
app.include_router(don_router)
app.include_router(nut_router)
app.include_router(tuyen_router)


# FastAPI mặc định trả 422 cho dữ liệu sai kiểu; 422 dành cho vi phạm BR (kien-truc.md mục 7).
@app.exception_handler(RequestValidationError)
async def loi_du_lieu(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Bỏ "input" (có thể là mật khẩu) và "ctx" (có thể chứa object không đổi sang JSON được)
    chi_tiet = [{k: e[k] for k in ("loc", "msg", "type")} for e in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={"ma": "DU_LIEU_KHONG_HOP_LE", "thong_diep": "Dữ liệu không hợp lệ", "chi_tiet": chi_tiet},
    )


@app.exception_handler(LoiNghiepVu)
async def loi_nghiep_vu(request: Request, exc: LoiNghiepVu) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"ma": exc.ma, "thong_diep": exc.thong_diep, "chi_tiet": exc.chi_tiet}
    )


@app.get("/api/health")
def health() -> dict:
    return {"trang_thai": "ok"}
