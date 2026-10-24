# UC-06: Quản lý khách hàng

- **Trạng thái:** Hoàn thành 24/10/2026 (Đã duyệt 24/10/2026 – Tài giao "làm được việc nào thì làm luôn"; 2 quyết định mới ghi ở mục Quyết định, Tài xem lại)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán chỉ xem
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-06, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2.2 · ERD `docs/so-do.md` mục 5 (KHACH_HANG)
- **Quy tắc nghiệp vụ liên quan:** BR-60 (không xóa, chỉ `NGUNG`), BR-59 (4 số cuối SĐT người gửi dùng để tra cứu), BR-57 (phân quyền)
- **Người làm:** Tài · **Khuôn:** `docs/mau-use-case.md` (như UC-03)

## Mô tả ngắn
Điều phối viên thêm, xem, sửa khách hàng (người gửi hàng) và chuyển khách giữa `HOAT_DONG` / `NGUNG`. Khách được chọn khi tạo đơn (UC-08) và là đơn vị theo dõi công nợ (UC-25).

## Đặc tả rút gọn
- **Thêm:** tên (bắt buộc), SĐT (bắt buộc), địa chỉ, mã số thuế (không bắt buộc). Khách mới ở `HOAT_DONG`.
- **Danh sách:** tìm theo một phần tên (không phân biệt hoa thường) hoặc một phần SĐT; lọc trạng thái; phân trang như UC-03.
- **Sửa:** mọi trường; đổi trạng thái `HOAT_DONG` ↔ `NGUNG`. **Không có xóa** (BR-60).
- Khách `NGUNG` không được chọn khi tạo đơn: kiểm ở UC-08.

## Quyết định (24/10, Tài xem lại)
1. **Kế toán xem được khách hàng** (GET), không sửa – công nợ UC-25 theo khách. Giống quyết định "Kế toán xem xe" ở UC-03. Đã sửa `api.md`.
2. **SĐT kiểm định dạng**: bỏ khoảng trắng, dấu chấm, gạch; `+84` đổi thành `0`; sau đó phải là `0` + 9 hoặc 10 chữ số (di động 10 số, cố định 11 số). Lý do: BR-59 dùng 4 số cuối SĐT người gửi để tra cứu, SĐT sai thì khách không tra được.
3. Không chặn trùng tên hay SĐT (một công ty có thể có nhiều người gửi dùng chung số; nhà xe nhỏ ít khách). Tìm theo tên **có phân biệt dấu** (chưa dùng `unaccent`).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-06-AC1 | Thêm khách hợp lệ → 201, `HOAT_DONG`; tên bỏ khoảng trắng đầu cuối; SĐT chuẩn hóa: "0909 123.456" → "0909123456", "+84 909-123-456" → "0909123456" | API | BR-59 |
| UC-06-AC2 | Dữ liệu sai → 400, không lưu: tên rỗng hoặc toàn khoảng trắng; SĐT 9 số (biên từ chối), 10 số (được), 11 số (được), 12 số (từ chối), có chữ, không bắt đầu bằng 0; mã số thuế có nhưng không phải 10 số hoặc 10 số + "-" + 3 số | API | — |
| UC-06-AC3 | Danh sách: tìm theo một phần tên không phân biệt hoa thường ("cty a" ra "Cty A"), tìm theo một phần SĐT ("6789"), lọc trạng thái, phân trang trả đúng `tong`; ký tự `%` không làm lộ toàn bộ danh sách | API | — |
| UC-06-AC4 | Sửa khách → 200; gửi `null` cho tên hoặc SĐT → 400; đổi trạng thái `HOAT_DONG` ↔ `NGUNG`, giá trị khác → 400; DELETE → 405 | API | BR-60 |
| UC-06-AC5 | Phân quyền: Điều phối, Quản lý thêm/sửa được; Kế toán GET 200, POST/PATCH 403; Tài xế mọi thao tác 403; chưa đăng nhập 401; khách không tồn tại 404 | API | BR-57 |
| UC-06-AC6 | Giao diện Điều phối: danh sách khách (tên, SĐT, địa chỉ, mã số thuế, trạng thái), tìm, lọc, phân trang; hộp thoại thêm/sửa báo lỗi tiếng Việt dưới từng ô; nút Ngừng / Hoạt động lại | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/kieu.py` (mới: `SoDienThoai`, `ChuBatBuoc` dùng lại cho UC-08), `backend/app/modules/danh_muc/khach_hang/{schemas,service,router}.py`, `backend/app/main.py`; `frontend/src/api/khachHang.ts`, `frontend/src/pages/dieu-phoi/KhachHangDanhSach.tsx`, `frontend/src/App.tsx` (menu); `docs/api.md`.
- Test đã viết: `backend/tests/api/test_uc06_khach_hang.py` (22 ca). Toàn bộ **90 passed** (24/10).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest`.
- Lệch đặc tả: 3 quyết định ở mục Quyết định; `api.md` đã sửa.
- AC6 thử tay 24/10 (Tài): chuẩn hóa SĐT, tìm, báo lỗi SĐT dưới ô, ngừng khách. Tài hỏi về hai khách trùng SĐT → giữ quyết định 3 (không chặn): mã đơn duy nhất nên tra cứu BR-59 không lẫn.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-06-AC1 | API | `test_uc06_ac1_* (3 ca)` | Đạt | 24/10/2026 |
| UC-06-AC2 | API | `test_uc06_ac2_* (12 ca)` | Đạt | 24/10/2026 |
| UC-06-AC3 | API | `test_uc06_ac3_tim_loc_phan_trang` | Đạt | 24/10/2026 |
| UC-06-AC4 | API | `test_uc06_ac4_sua_va_trang_thai` | Đạt | 24/10/2026 |
| UC-06-AC5 | API | `test_uc06_ac5_* (5 ca)` | Đạt | 24/10/2026 |
| UC-06-AC6 | UI | `docs/test-evidence/UC-06/` (3 ảnh) + Tài xác nhận | Đạt | 24/10/2026 |
