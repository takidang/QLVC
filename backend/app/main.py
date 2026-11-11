from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.config import get_settings
from app.loi import LoiNghiepVu
from app.modules.bao_cao.router import router as bao_cao_router
from app.modules.chuyen.router import router as chuyen_router
from app.modules.chuyen.router import router_su_co as su_co_router
from app.modules.danh_muc.bang_gia.router import router as bang_gia_router
from app.modules.danh_muc.cau_hinh.router import router as cau_hinh_router
from app.modules.danh_muc.khach_hang.router import router as khach_hang_router
from app.modules.danh_muc.ly_do.router import router as ly_do_router
from app.modules.danh_muc.nut.router import router as nut_router
from app.modules.danh_muc.tai_xe.router import router as tai_xe_router
from app.modules.danh_muc.tuyen.router import router as tuyen_router
from app.modules.danh_muc.xe.router import router as xe_router
from app.modules.don.router import router as don_router
from app.modules.nguoi_dung.router import router as nguoi_dung_router
from app.modules.quet.router import router as quet_router
from app.modules.su_co.router import router as bao_su_co_router
from app.modules.tep.router import router as tep_router
from app.modules.tien.chi_phi.router import router as chi_phi_router
from app.modules.tien.cong_no.router import router as cong_no_router
from app.modules.tien.quyet_toan.router import router as quyet_toan_router
from app.modules.tien.tam_ung.router import router as tam_ung_router
from app.modules.toi.router import router as toi_router
from app.modules.tra_cuu.router import router as tra_cuu_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()  # thiếu JWT_SECRET / DATABASE_URL thì dừng ngay lúc khởi động (UC-01-AC2)
    yield


app = FastAPI(title="QLVC", lifespan=lifespan)
# Xếp theo chữ cái: thêm router mới chèn đúng chỗ, hai người thêm cùng lúc ít khi đụng nhau (docs/nhanh-git.md mục 4)
app.include_router(auth_router)
app.include_router(bang_gia_router)
app.include_router(bao_cao_router)
app.include_router(bao_su_co_router)
app.include_router(cau_hinh_router)
app.include_router(chi_phi_router)
app.include_router(chuyen_router)
app.include_router(cong_no_router)
app.include_router(don_router)
app.include_router(khach_hang_router)
app.include_router(ly_do_router)
app.include_router(nguoi_dung_router)
app.include_router(nut_router)
app.include_router(quet_router)
app.include_router(quyet_toan_router)
app.include_router(su_co_router)
app.include_router(tai_xe_router)
app.include_router(tam_ung_router)
app.include_router(tep_router)
app.include_router(toi_router)
app.include_router(tra_cuu_router)
app.include_router(tuyen_router)
app.include_router(xe_router)


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
