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
DATABASE_URL=postgresql+psycopg://qlvc:<mật khẩu ở trên>@127.0.0.1:5432/qlvc
JWT_SECRET=<chuỗi ngẫu nhiên, xem dưới>
LUU_TRU=local
```

Ghi `127.0.0.1`, **không ghi `localhost`**: trên Windows `localhost` thử IPv6 trước nên mỗi lần kết nối CSDL bị treo vài giây tới cả phút.

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

Mở http://localhost:8000/api/health → `{"trang_thai":"ok"}`.

Tài khoản để thử: `.venv\Scripts\python -m app.tai_khoan_demo` tạo (hoặc đặt lại mật khẩu, mở khóa) `quanly`, `dieuphoi`, `ketoan`, `taixe`, mật khẩu chung **`demo12345`**. Quên mật khẩu thì chạy lại lệnh này. Bản demo (`APP_ENV=demo`) phải truyền mật khẩu riêng: `python -m app.tai_khoan_demo <mật khẩu>`.

Trong VS Code chọn interpreter `backend\.venv` để có gợi ý code.

## 6. Frontend (cửa sổ PowerShell khác)

```powershell
cd frontend
npm ci                                  # dùng npm ci, không dùng npm install
npm run dev
```

Mở http://127.0.0.1:5173 thấy dòng "QLVC – Hệ thống quản lý vận tải".

## 7. Kiểm tra lần cuối

```powershell
cd backend;  .venv\Scripts\ruff check .;  .venv\Scripts\python -m pytest
cd ..\frontend;  npm run lint;  npm run build
```

Cả bốn lệnh không báo lỗi là xong. Ghi vào nhật ký của mình trong `docs/TIEN-DO.md`.

## 8. Dữ liệu demo (máy chạy demo – máy Kiệt)

Cần đã cài `requirements-dev.txt` (mục 5): lệnh nạp gọi API qua `TestClient`, dùng gói `httpx` có trong đó.

Demo dùng một CSDL **riêng, sạch** tên `qlvc_demo`, không đụng CSDL dev. Chuyển qua lại chỉ bằng cách đổi **tên CSDL ở cuối `DATABASE_URL`** trong `.env` (tự sửa, không gửi `.env` cho ai).

**Chuẩn bị (một lần, trước ngày demo):**

```powershell
git switch dev; git pull
docker compose up -d db
docker compose exec db sh -c 'createdb -U "$POSTGRES_USER" qlvc_demo'
# Sửa .env: DATABASE_URL=...:5432/<tên cũ>  →  ...:5432/qlvc_demo
cd backend
.venv\Scripts\alembic upgrade head
.venv\Scripts\python -m seed.demo          # tạo danh mục + 7 ngày trước + hôm nay, khoảng 1 phút
```

**Sáng ngày demo** (chạy trong khoảng **7:00–18:00**, vì chuyến hôm nay tính quanh giờ chạy lệnh):

```powershell
cd backend
.venv\Scripts\python -m seed.demo --ngay-moi   # thêm chuyến hôm nay: đang chạy (trễ, sự cố), vừa xong, đã quyết toán, sắp đi
.venv\Scripts\uvicorn app.main:app             # không cần --reload khi demo
```

Cửa sổ khác: `cd frontend; npm run dev`. Đăng nhập `dieuphoi`, `ketoan`, `quanly`, `taixe` (hoặc `taixe01`…`taixe05`), mật khẩu `demo12345`.

- Lệnh **không xóa** gì. CSDL đã có chuyến mà chạy không có `--ngay-moi` → dừng, báo dùng `--ngay-moi`. Hôm nay đã có chuyến → `--ngay-moi` cũng dừng.
- Muốn làm lại từ đầu: `docker compose exec db sh -c 'dropdb -U "$POSTGRES_USER" qlvc_demo && createdb -U "$POSTGRES_USER" qlvc_demo'`, rồi chạy lại phần chuẩn bị (từ `alembic upgrade head`).
- Bản đồ dùng nền OpenStreetMap: máy demo cần mạng.

**Sau demo:** đổi `DATABASE_URL` về tên CSDL dev cũ. CSDL `qlvc_demo` để nguyên cho lần demo sau.

## Lỗi hay gặp

| Lỗi | Cách xử lý |
|---|---|
| `python` mở Microsoft Store | Cài lại Python, tick **Add to PATH**; hoặc tắt "App execution aliases" cho python trong Settings |
| `docker: command not found` / không kết nối được | Chưa mở Docker Desktop, hoặc chưa khởi động lại máy sau khi cài WSL |
| `docker compose` báo thiếu `POSTGRES_PASSWORD` | Chưa tạo `.env` ở thư mục gốc `QLVC` (không phải trong `backend/`) |
| Cổng 5432 đã bị dùng | Máy đã cài PostgreSQL khác: tắt service đó, hoặc báo nhóm để đổi cổng |
| `npm ci` lỗi phiên bản | Kiểm tra `node --version` là v24 |
| Không cài được package | Đúng: phiên bản đã ghim, muốn thêm package thì hỏi nhóm trước (CLAUDE.md) |
