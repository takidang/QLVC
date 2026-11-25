---
name: kiem-thu-kham-pha
description: "Dùng khi người làm đồ án muốn kiểm tra bảo mật và 'phá thử' một web app trước khi demo, báo cáo hay phát hành: quét phụ thuộc, rà phân quyền từng endpoint, cho agent (agy) đóng vai kẻ phá gọi API và bấm giao diện, rồi tự xác minh từng lỗi, sửa lỗi thật kèm test. Gọi: 'phá thử', 'kiểm thử khám phá', 'quét bảo mật trước demo'."
---

# Kiểm thử khám phá + rà bảo mật trước demo

Mục tiêu: tìm lỗi mà test theo tiêu chí chấp nhận không bắt được (nhập bừa, gửi song song, gọi chéo quyền, file giả), xác minh bằng chạy thật, sửa lỗi thật có test. Làm được ở mọi dự án web có backend API.

## Quy ước của đồ án này (ghi đè phần chung bên dưới)
- **Khi nào:** trước mỗi mốc đưa lên `main`, sau khi gộp `dev` vào `test` (`docs/nhanh-git.md` mục 2). Không chạy ở từng PR. Còn dưới 2 ngày tới mốc thì chỉ ghi nhận, để sau mốc mới sửa (trừ lỗi nghiêm trọng, hai người cùng quyết).
- **Chạy ở đâu:** máy local, một CSDL thử riêng. Không chạy vào CSDL demo hay bản đã triển khai.
- **Sửa lỗi:** nhánh riêng từ `dev` → PR vào `dev` → gộp `dev` vào `test` lại, như mọi lỗi khác.
- **Báo cáo:** `docs/test-evidence/kiem-thu-kham-pha-<yyyy-mm-dd>/`. Repo công khai: không đưa `.env`, token, cookie, file dump CSDL, dữ liệu thật vào báo cáo hay script.
- Máy không có `agy` thì giao bước 2 cho agent Claude (khi người dùng bảo) với cùng phiếu.
- "Tài" trong phần dưới hiểu là người đang dùng máy.

## 0. Chuẩn bị (hỏi Tài nếu chưa rõ)
- Làm trên **nhánh riêng** tách từ nhánh tích hợp (vd `tai/kiem-tra-truoc-bao-cao`). Push lên nhánh đó được, **không mở PR / không gộp** khi sát ngày demo, trừ khi Tài bảo.
- Chạy app trên **CSDL dev**, không bao giờ CSDL demo/production: agent sẽ tạo nhiều dữ liệu rác.
- Đọc luật dự án: `CLAUDE.md`, quy tắc bảo mật (vd `docs/security-rules.md`), nghiệp vụ (BR).

## 1. Tự rà tĩnh (làm trước, rẻ, chính xác)
1. **Phụ thuộc**: `npm audit` (frontend); backend Python có `pip-audit` thì chạy, chưa có thì hỏi trước khi cài.
2. **Bảng phân quyền route**: FastAPI dùng `quet_route_fastapi.py` trong skill này (chạy từ thư mục backend bằng python của venv: `python -X utf8 <đường dẫn>/quet_route_fastapi.py`). In mỗi route: KHONG CAN DANG NHAP / CHI DANG NHAP / vai trò được phép. Soát: route không cần đăng nhập phải có lý do; route tiền chỉ đúng vai trò. Framework khác: grep decorator route + dependency auth, cùng ý.
   - FastAPI ≥ 0.14x lồng router thành `_IncludedRouter` (`.original_router.routes`); script đã xử lý.
3. **IDOR**: mọi service của vai trò "của tôi" (tài xế, khách…) phải lọc theo người đang đăng nhập; sai chủ trả 404 giống không tồn tại.
4. **Chống dò**: khoá đăng nhập sau N lần sai; endpoint công khai có giới hạn tần suất; thông báo lỗi chung không lộ dữ liệu tồn tại.
5. **Upload**: nhận diện theo byte đầu (không tin đuôi/Content-Type), tên do server sinh, giới hạn cỡ **khi đọc** (`read(MAX+1)`), giới hạn số file, phục vụ kèm `X-Content-Type-Options: nosniff`.
6. **Tiền / trạng thái song song**: kiểm có khoá dòng (`FOR UPDATE`) trước khi kiểm điều kiện; chú ý mẫu "đọc id trước, khoá sau" → sau khi khoá phải kiểm lại bản ghi còn tồn tại.
7. **Bí mật, cookie**: secret chỉ từ biến môi trường, không mặc định thật; cookie `httponly`, `secure`, `samesite`.

## 2. Cho agent phá thử (agy)
- Bật backend + frontend (dev DB), đặt lại tài khoản thử. Tạo worktree riêng: `git worktree add ../<repo>-agy-pha -b tai/agy-pha <nhánh>`.
- Phiếu: chép `phieu-mau.md` trong skill này, sửa URL, tài khoản, đường dẫn tài liệu. Phiếu **cấm sửa code**, chỉ viết script + báo cáo trong `kiem-thu-kham-pha/`.
- Gọi từ Bash (không PowerShell): `agy -p "$(cat phieu.md)" --model <model> --print-timeout 3300s`, chạy nền.
  - Claude trong agy hết lượt → Gemini (`gemini-4-neon-high`) làm được việc này vì chỉ đọc/thử, không sửa code.
  - **Headless agy tự từ chối lệnh shell** ("auto-denied") nên thường chỉ viết được script, không chạy được. Khi đó **mình đọc lướt script** (chỉ gọi localhost? không khoá tài khoản thật? không xoá dữ liệu ngoài dữ liệu tự tạo?) rồi tự chạy: `py -3.12 -I -X utf8 kiem-thu-kham-pha/chay_api.py > log`.
  - `-I` bỏ qua `PYTHONIOENCODING`: luôn thêm `-X utf8` khi in tiếng Việt trên Windows.

## 3. Xác minh và phân loại (bắt buộc: agent hay báo nhầm)
Với mỗi ca LỖI: tái hiện bằng tay (curl / script), đọc log backend tìm traceback (`grep -E "Error|Exception" be.log | sort | uniq -c`). Xếp vào:
| Loại | Xử lý |
|---|---|
| **Lỗi thật**: 500, race, lộ/sửa dữ liệu trái quyền | Sửa ngay trên nhánh, kèm test |
| **Nhập liệu lỏng**: nhận năm 3000, số 1e15 | Ghi lại, hỏi nhóm giới hạn nghiệp vụ; không tự đặt số |
| **Theo thiết kế**: vai trò X xem được Y vì nghiệp vụ cần | Đối chiếu tài liệu, ghi "không phải lỗi" + lý do |
| **Báo nhầm**: script sai, đánh dấu sai | Ghi rõ là báo nhầm |
| **Chỉ khi triển khai**: vd tin `X-Forwarded-For` sau proxy | Ghi vào việc của đợt triển khai |

Bẫy đã gặp: uvicorn mặc định tin `X-Forwarded-For` từ 127.0.0.1, và với `--forwarded-allow-ips="*"` lấy IP trái nhất (khách tự đặt) → giới hạn theo IP bị né. Sau proxy phải lấy IP proxy thêm vào (phải nhất) hoặc chỉ tin dải IP proxy.

## 4. Sửa lỗi thật
- Sửa nhỏ nhất đúng chỗ (ponytail). Lỗi tràn số/ngày từ CSDL: một exception handler chung (`DataError`, `OverflowError` → 400 mã riêng, thông báo tiếng Việt) + siết regex tham số (vd tháng chỉ năm 2000–2099).
- Race "đọc trước, khoá sau": sau `get(..., with_for_update=True)` kiểm `None` → 404.
- **Test cho từng lỗi**, và chứng minh test bắt được lỗi: `git stash push -- app/` → chạy test mới phải **hỏng** → `git stash pop` → phải **đạt**.
- Test song song (giữ khoá ở một Session, request khác trong thread): bọc `try/finally: s.close()`; nếu thread chết sớm mà không đóng session thì teardown `TRUNCATE` treo vô hạn. Response `httpx` không có `.ok` (dùng `status_code`). Treo thì xem `pg_stat_activity` (`idle in transaction`) và `pg_terminate_backend`.
- Chạy toàn bộ test suite + lint trước khi commit.

## 5. Kết quả
- Commit trên nhánh: code sửa + test + báo cáo `docs/test-evidence/kiem-thu-kham-pha/bao-cao.md` (bảng mục | số ca | đạt | lỗi thật | báo nhầm; mỗi lỗi: mức, tái hiện, thấy, mong đợi, đã sửa/để sau) + script của agent.
- Báo Tài ngắn: bao nhiêu ca, lỗi thật đã sửa, việc để sau (kèm lý do), nhánh nào, chưa gộp.
- Gỡ worktree của agent khi xong (`git worktree remove`; trước đó lưu file gitignore cần giữ).
