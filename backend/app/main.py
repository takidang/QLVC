from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="QLVC")


# FastAPI mặc định trả 422 cho dữ liệu sai kiểu; 422 dành cho vi phạm BR (kien-truc.md mục 7).
@app.exception_handler(RequestValidationError)
async def loi_du_lieu(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"ma": "DU_LIEU_KHONG_HOP_LE", "thong_diep": "Dữ liệu không hợp lệ", "chi_tiet": exc.errors()},
    )


@app.get("/api/health")
def health() -> dict:
    return {"trang_thai": "ok"}
