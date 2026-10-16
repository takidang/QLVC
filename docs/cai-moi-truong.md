# Cài môi trường dev (Windows)

> Dành cho cả Tài và Kiệt. Làm một lần trên mỗi máy, khoảng 1 giờ (phần lớn là chờ tải). Xong bước 7 là chạy được backend, frontend và CSDL.
> Nhờ Claude Code kiểm từng bước: "kiểm tra giúp mình đã cài xong bước X trong docs/cai-moi-truong.md chưa".

## 1. Phần mềm cần cài

| Phần mềm | Phiên bản | Tải ở đâu | Kiểm tra (mở PowerShell mới) |
|---|---|---|---|
| Git | bản mới | git-scm.com | `git --version` |
| Python | **3.12** (không dùng 3.13 trở lên cho tới khi nhóm thống nhất) | python.org – lúc cài tick **Add python.exe to PATH** | `python --version` |
| Node.js | **24 LTS** | nodejs.org | `node --version` → `v24.x` |
| WSL 2 | — | PowerShell **Run as Administrator**: `wsl --install`, rồi **khởi động lại máy** | `wsl --status` |
| Docker Desktop | bản mới | docker.com – cài **sau** WSL, chọn **Use WSL 2** | Mở Docker Desktop, thấy **Engine running**; `docker --version` |
| VS Code + Claude Code | — | code.visualstudio.com | — |

Docker Desktop miễn phí cho cá nhân và học tập. Nó tốn khoảng 2 GB RAM khi chạy, không code thì tắt đi. **Mỗi lần code phải mở Docker Desktop trước** thì CSDL mới chạy.

## 2. Lấy code

```powershell
git clone https://github.com/takidang/QLVC.git
cd QLVC
```

Mở thư mục `QLVC` bằng VS Code, mở Claude Code, chọn **Trust**. Tạo file `CLAUDE.local.md` có một dòng `Người dùng máy này: <tên>` (file này không lên git).

## 3. Tạo file `.env`

Chép `.env.example` thành `.env` (cùng thư mục), điền giá trị **cho máy mình**. Mật khẩu dev đặt tùy ý, không dùng lại mật khẩu thật nào, và **không bao giờ commit `.env`**.

```
APP_ENV=dev
POSTGRES_USER=qlvc
POSTGRES_PASSWORD=<tự đặt>
POSTGRES_DB=qlvc
DATABASE_URL=postgresql+psycopg://qlvc:<mật khẩu ở trên>@localhost:5432/qlvc
JWT_SECRET=<chuỗi ngẫu nhiên, xem dưới>
LUU_TRU=local
```

Sinh `JWT_SECRET`: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Ba biến `SUPABASE_*` để trống (chỉ dùng ở bản demo).

## 4. Chạy CSDL

```powershell
docker compose up -d db      # lần đầu tải PostgreSQL 16, mất vài phút
docker compose ps            # thấy service db trạng thái running
```

Tắt: `docker compose stop`. Dữ liệu vẫn giữ trong volume `pgdata`.

## 5. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest          # phải thấy "passed"
.venv\Scripts\uvicorn app.main:app --reload
```

Mở http://localhost:8000/api/health → `{"trang_thai":"ok"}`. Trong VS Code chọn interpreter `backend\.venv` để có gợi ý code.

## 6. Frontend (cửa sổ PowerShell khác)

```powershell
cd frontend
npm ci                                  # dùng npm ci, không dùng npm install
npm run dev
```

Mở http://localhost:5173 thấy dòng "QLVC – Hệ thống quản lý vận tải".

## 7. Kiểm tra lần cuối

```powershell
cd backend;  .venv\Scripts\ruff check .;  .venv\Scripts\python -m pytest
cd ..\frontend;  npm run lint;  npm run build
```

Cả bốn lệnh không báo lỗi là xong. Ghi vào nhật ký của mình trong `docs/TIEN-DO.md`.

## Lỗi hay gặp

| Lỗi | Cách xử lý |
|---|---|
| `python` mở Microsoft Store | Cài lại Python, tick **Add to PATH**; hoặc tắt "App execution aliases" cho python trong Settings |
| `docker: command not found` / không kết nối được | Chưa mở Docker Desktop, hoặc chưa khởi động lại máy sau khi cài WSL |
| `docker compose` báo thiếu `POSTGRES_PASSWORD` | Chưa tạo `.env` ở thư mục gốc `QLVC` (không phải trong `backend/`) |
| Cổng 5432 đã bị dùng | Máy đã cài PostgreSQL khác: tắt service đó, hoặc báo nhóm để đổi cổng |
| `npm ci` lỗi phiên bản | Kiểm tra `node --version` là v24 |
| Không cài được package | Đúng: phiên bản đã ghim, muốn thêm package thì hỏi nhóm trước (CLAUDE.md) |
