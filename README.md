# Hệ thống quản lý vận tải cho doanh nghiệp vận tải hàng hóa nhỏ

Đồ án chuyên ngành CNPM – Nhóm 10

- Đặng Lê Tấn Tài
- Nguyễn Đỗ Tuấn Kiệt

Thời gian thực hiện: 12/10–20/12/2026

Hướng dẫn dùng Claude Code: xem `docs/SKILLS.md`

## Chạy lúc dev

Cần: Python 3.12, Node 24, Docker Desktop (cho PostgreSQL).

```bash
cp .env.example .env              # rồi điền giá trị
docker compose up -d db           # PostgreSQL

cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt   # Linux/macOS: .venv/bin/pip
.venv/Scripts/python -m pytest
.venv/Scripts/uvicorn app.main:app --reload         # http://localhost:8000/api/health

cd ../frontend
npm ci
npm run dev                       # http://localhost:5173, /api chuyển sang backend
```

Phiên bản package được ghim. Muốn cài hoặc nâng package thì hỏi nhóm trước (CLAUDE.md), rồi cập nhật `requirements*.txt` hoặc `package-lock.json`.
