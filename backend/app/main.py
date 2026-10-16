from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.config import get_settings
from app.loi import LoiNghiepVu


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()  # thiếu JWT_SECRET / DATABASE_URL thì dừng ngay lúc khởi động (UC-01-AC2)
    yield


app = FastAPI(title="QLVC", lifespan=lifespan)
app.include_router(auth_router)


# FastAPI mặc định trả 422 cho dữ liệu sai kiểu; 422 dành cho vi phạm BR (kien-truc.md mục 7).
@app.exception_handler(RequestValidationError)
async def loi_du_lieu(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"ma": "DU_LIEU_KHONG_HOP_LE", "thong_diep": "Dữ liệu không hợp lệ", "chi_tiet": exc.errors()},
    )


@app.exception_handler(LoiNghiepVu)
async def loi_nghiep_vu(request: Request, exc: LoiNghiepVu) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"ma": exc.ma, "thong_diep": exc.thong_diep, "chi_tiet": exc.chi_tiet}
    )


@app.get("/api/health")
def health() -> dict:
    return {"trang_thai": "ok"}
