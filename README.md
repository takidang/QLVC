# Hệ thống quản lý vận tải cho doanh nghiệp vận tải hàng hóa nhỏ

Đồ án chuyên ngành CNPM – Nhóm 8

- Đặng Lê Tấn Tài
- Nguyễn Đỗ Tuấn Kiệt

Thời gian thực hiện: 12/10–20/12/2026

Hướng dẫn dùng Claude Code: xem `docs/SKILLS.md`

## Giới thiệu

Web quản lý vận tải cho doanh nghiệp nhỏ, **chuyến xe là trung tâm**: điều phối ghép đơn hàng vào chuyến (kiểm tải trọng, giờ lái, giấy tờ), chốt chuyến, tài xế quét mã lấy và giao hàng trên điện thoại, kế toán duyệt chi phí rồi quyết toán khóa sổ, theo dõi công nợ và lãi lỗ. Bốn vai trò: Quản lý, Điều phối viên, Kế toán, Tài xế; khách tra cứu đơn không cần tài khoản.

Công nghệ: FastAPI (Python 3.12) + PostgreSQL 16 (Docker) + React/TypeScript (Vite).

| Thư mục | Nội dung |
|---|---|
| `backend/` | API, quy tắc nghiệp vụ, migration, lệnh nạp dữ liệu demo (`seed/`), test (1.000+ test) |
| `frontend/` | Giao diện web (máy tính và điện thoại 360 px cho tài xế) |
| `docs/` | Nghiệp vụ, use case, thiết kế, API, story từng chức năng, ảnh bằng chứng kiểm thử, báo cáo kiểm thử |

## Chạy bản demo

Cần: Docker Desktop (đang chạy), Python 3.12, Node.js 24. Từng bước cài đặt chi tiết: [docs/cai-moi-truong.md](docs/cai-moi-truong.md).

1. **Tạo file `.env`** ở thư mục gốc: chép từ `.env.example`, điền giá trị (xem mẫu ở `docs/cai-moi-truong.md` mục 3). Phải có `APP_ENV=dev`. Không đưa `.env` cho ai và không commit.
2. **Bật cơ sở dữ liệu** (PowerShell, thư mục gốc):

   ```powershell
   docker compose up -d db
   ```

3. **Cài và chạy backend** (cửa sổ PowerShell thứ nhất):

   ```powershell
   cd backend
   python -m venv .venv
   .venv\Scripts\pip install -r requirements-dev.txt
   .venv\Scripts\alembic upgrade head
   .venv\Scripts\python -m seed.demo
   .venv\Scripts\uvicorn app.main:app --port 8000
   ```

   `seed.demo` nạp sẵn xe, tài xế, khách, tuyến, bảng giá, 7 ngày chuyến đã quyết toán và chuyến hôm nay ở đủ trạng thái (đang chạy trễ, có sự cố, chờ quyết toán, đã chốt, đang lập, hủy). **Chạy trong khoảng 7:00–18:00** (giờ máy) để chuyến hôm nay không vắt qua nửa đêm. Ngoài giờ đó hoặc muốn nạp thêm ngày: xem `docs/cai-moi-truong.md` mục 8.

4. **Cài và chạy giao diện** (cửa sổ thứ hai):

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

5. Mở **http://127.0.0.1:5173**.

**Tài khoản demo** (mật khẩu chung `demo12345`):

| Tên đăng nhập | Vai trò | Thử gì |
|---|---|---|
| `dieuphoi` | Điều phối viên | Chuyến trong ngày, lập chuyến, ghép đơn, chốt, theo dõi trễ / sự cố |
| `ketoan` | Kế toán | Duyệt chi phí, quyết toán, công nợ, tạm ứng |
| `quanly` | Quản lý | Tổng quan, báo cáo lãi lỗ, hiệu suất xe, người dùng, bảng giá |
| `taixe`, `taixe04` (cũng có `taixe01`…`taixe05`) | Tài xế (`taixe` và `taixe04` có chuyến đang chạy hôm nay) | Dùng **điện thoại hoặc thu nhỏ cửa sổ 360 px**: bắt đầu, quét lấy, giao, chi phí, sự cố, kết thúc |

**Tra cứu đơn cho khách** (không cần đăng nhập): **http://127.0.0.1:5173/tra-cuu**. Lấy mã đơn ở trang Đơn hàng của Điều phối, nhập kèm 4 số cuối số điện thoại người gửi hoặc người nhận (xem trong hộp **Sửa** của đơn).

**Chạy test tự động** (backend, cần CSDL đang chạy): `cd backend; .venv\Scripts\python -m pytest`.

## Chạy lúc dev

Hướng dẫn cài từng bước trên Windows: [docs/cai-moi-truong.md](docs/cai-moi-truong.md).

Phiên bản package được ghim. Muốn cài hoặc nâng package thì hỏi nhóm trước (CLAUDE.md), rồi cập nhật `requirements*.txt` hoặc `package-lock.json`.
