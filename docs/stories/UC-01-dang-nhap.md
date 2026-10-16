# UC-01: Đăng nhập / đăng xuất

- **Trạng thái:** Đã duyệt (16/10/2026)
- **Tác nhân:** Quản lý, Điều phối viên, Tài xế, Kế toán (Khách không đăng nhập)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-01, đặc tả rút gọn ở dưới) · `docs/kien-truc.md` mục 5, 7, 11 · `docs/api.md` mục 2.1
- **Quy tắc nghiệp vụ liên quan:** BR-57 (phân quyền kiểm ở máy chủ), BR-60 (tài khoản `NGUNG`) · NFR-SEC-01 (băm mật khẩu, token ≤ 8 giờ), NFR-SEC-02 (403 khi sai vai trò), NFR-SEC-05 (giới hạn đăng nhập sai)
- **Người làm:** Tài

## Mô tả ngắn
Người dùng nội bộ nhập tên đăng nhập và mật khẩu; đúng thì máy chủ đặt cookie `access_token` (JWT, httpOnly) và giao diện chuyển tới trang theo vai trò. Story này cũng làm phần dùng chung cho mọi UC sau: kiểm token, kiểm vai trò `can_vai_tro(...)` (Quản lý kế thừa quyền Điều phối), và lệnh tạo tài khoản Quản lý đầu tiên.

## Đặc tả rút gọn
- **Luồng chính:** 1. Mở trang đăng nhập, nhập tên đăng nhập + mật khẩu. 2. `POST /api/auth/dang-nhap` kiểm mật khẩu (argon2). 3. Đúng → cookie `access_token`: `HttpOnly`, `Secure`, `SameSite=Strict`, hết hạn 8 giờ; trả `{id, ho_ten, vai_tro}`. 4. Giao diện chuyển tới trang của vai trò.
- **Đăng xuất:** `POST /api/auth/dang-xuat` xóa cookie, về trang đăng nhập.
- **Ngoại lệ:** sai tên hoặc sai mật khẩu → một thông báo chung, không lộ tên đăng nhập có tồn tại hay không; tài khoản `NGUNG` → không đăng nhập được; sai liên tiếp quá ngưỡng → khóa tạm (NFR-SEC-05).
- **Mỗi request sau đó:** đọc cookie, kiểm chữ ký (chỉ `HS256`), hạn, và tài khoản còn `HOAT_DONG` (khóa tài khoản có hiệu lực ngay, không đợi token hết hạn).
- **Ngoài phạm vi:** tạo/sửa/khóa người dùng (UC-02), đổi mật khẩu, quên mật khẩu (hướng phát triển).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-01-AC1 | Mật khẩu lưu dạng băm argon2, không lưu bản rõ; kiểm đúng mật khẩu → đúng, sai một ký tự → sai | Logic | NFR-SEC-01 |
| UC-01-AC2 | Thiếu `JWT_SECRET` hoặc `DATABASE_URL` → ứng dụng báo lỗi rõ khi khởi động, không chạy với giá trị mặc định | Logic | security-rules |
| UC-01-AC3 | Đăng nhập đúng → 200, body `{id, ho_ten, vai_tro}` (không chứa token), cookie `access_token` có `HttpOnly`, `Secure`, `SameSite=Strict`, `Max-Age` = 8 giờ | API | NFR-SEC-01 |
| UC-01-AC4 | Sai mật khẩu và tên đăng nhập không tồn tại → **cùng** 401, cùng `ma` và `thong_diep` "Sai tên đăng nhập hoặc mật khẩu" | API | security-rules |
| UC-01-AC5 | Tài khoản `NGUNG`, mật khẩu đúng → 403 "Tài khoản đã bị khóa"; mật khẩu sai → 401 như AC4 | API | BR-60 |
| UC-01-AC6 | `GET /api/auth/toi`: cookie hợp lệ → 200 thông tin người dùng; không cookie → 401; token hết hạn (ca biên: còn 1 giây → 200, quá 1 giây → 401) → 401; token sửa chữ ký, token `alg: none`, token ký bằng khóa khác → 401 | API | NFR-SEC-01 |
| UC-01-AC7 | Token còn hạn nhưng tài khoản vừa chuyển `NGUNG` → request kế tiếp 401 | API | BR-60 |
| UC-01-AC8 | Đăng xuất → cookie bị xóa; gọi `/api/auth/toi` sau đó → 401 | API | — |
| UC-01-AC9 | `can_vai_tro`: đúng vai trò → 200; sai vai trò → 403; `QUAN_LY` gọi endpoint yêu cầu `DIEU_PHOI` → 200; `QUAN_LY` gọi endpoint chỉ cho `KE_TOAN` → 403; chưa đăng nhập → 401 | API | BR-57, NFR-SEC-02 |
| UC-01-AC10 | Sai mật khẩu 5 lần liên tiếp cho cùng tên đăng nhập → khóa tạm 15 phút: lần thứ 5 vẫn 401 (biên), lần 6 → 429 kể cả mật khẩu đúng; sau 15 phút đăng nhập đúng được; đăng nhập đúng trước ngưỡng thì đếm lại từ 0 | API | NFR-SEC-05 |
| UC-01-AC11 | Lệnh `python -m app.tao_quan_ly` tạo tài khoản Quản lý đầu tiên: mật khẩu nhập ẩn, ≥ 8 ký tự, không in ra; trùng tên đăng nhập → báo lỗi, không ghi đè | Dữ liệu | security-rules |
| UC-01-AC12 | Giao diện: trang đăng nhập; đăng nhập đúng chuyển tới trang của vai trò (trang tạm cho 4 vai trò); vào trang nội bộ khi chưa đăng nhập → về trang đăng nhập; có nút đăng xuất; sai thông tin / bị khóa / khóa tạm hiện câu tiếng Việt | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi:
- Test đã viết:
- Lệnh chạy test:
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa:

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-01-AC1 | Logic | | CHƯA KIỂM | |
| UC-01-AC2 | Logic | | CHƯA KIỂM | |
| UC-01-AC3 | API | | CHƯA KIỂM | |
| UC-01-AC4 | API | | CHƯA KIỂM | |
| UC-01-AC5 | API | | CHƯA KIỂM | |
| UC-01-AC6 | API | | CHƯA KIỂM | |
| UC-01-AC7 | API | | CHƯA KIỂM | |
| UC-01-AC8 | API | | CHƯA KIỂM | |
| UC-01-AC9 | API | | CHƯA KIỂM | |
| UC-01-AC10 | API | | CHƯA KIỂM | |
| UC-01-AC11 | Dữ liệu | | CHƯA KIỂM | |
| UC-01-AC12 | UI | `docs/test-evidence/UC-01/` | CHƯA KIỂM | |
