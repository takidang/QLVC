# UC-02: Quản lý người dùng và vai trò

- **Trạng thái:** Hoàn thành (30/10/2026) · duyệt 30/10/2026, Kiệt · chờ Tài review PR vào `dev`
- **Tác nhân:** Quản lý (chỉ Quản lý; Điều phối **không** kế thừa ngược)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-02, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2.1 · ERD `docs/so-do.md` mục 5 (NGUOI_DUNG) · khuôn `docs/mau-use-case.md`
- **Quy tắc nghiệp vụ liên quan:** BR-57 (phân quyền ở máy chủ), BR-60 (không xóa, chỉ `NGUNG`) · NFR-SEC-01 (băm mật khẩu), NFR-SEC-05 (khóa tạm khi sai mật khẩu)
- **Người làm:** Kiệt · **Khuôn:** UC-04 Tài xế

## Mô tả ngắn
Quản lý xem danh sách tài khoản, thêm tài khoản Quản lý / Điều phối / Kế toán, đổi họ tên, tên đăng nhập, vai trò, khóa/mở tài khoản và đặt lại mật khẩu. Tài khoản Tài xế tạo, khóa ở UC-04; ở đây chỉ đổi tên đăng nhập, họ tên, đặt lại mật khẩu (quyết định UC-04 số 4).

## Đặc tả rút gọn
- **Danh sách** (`GET /api/nguoi-dung`): mọi tài khoản kể cả Tài xế; lọc `vai_tro`, `trang_thai`; tìm theo một phần tên đăng nhập hoặc họ tên; phân trang `?trang&so_dong` → `{du_lieu, tong}`. Mỗi dòng: `id, ten_dang_nhap, ho_ten, vai_tro, trang_thai, khoa_den`.
- **Thêm** (`POST /api/nguoi-dung`): tên đăng nhập, họ tên, mật khẩu ban đầu (8–200 ký tự, băm `bam_mat_khau`), vai trò `QUAN_LY` / `DIEU_PHOI` / `KE_TOAN`. Tài khoản mới `HOAT_DONG`.
- **Sửa** (`PATCH /api/nguoi-dung/{id}`): `ten_dang_nhap`, `ho_ten`, `vai_tro`, `trang_thai`. Không nhận `mat_khau` (đi endpoint riêng).
- **Khóa / mở** (BR-60): `trang_thai = NGUNG` có hiệu lực ngay (token đang dùng bị từ chối, như UC-01-AC7). Mở lại (`HOAT_DONG`) thì xóa luôn bộ đếm sai mật khẩu và khóa tạm (`so_lan_sai = 0`, `khoa_den = null`). Không có xóa.
- **Đặt lại mật khẩu** (`PUT /api/nguoi-dung/{id}/mat-khau`, body `{mat_khau}`): mọi vai trò kể cả Tài xế; xóa bộ đếm sai và khóa tạm. Máy chủ không trả lại mật khẩu.
- **Tài khoản Tài xế:** không tạo ở đây, không đổi vai trò sang hay từ `TAI_XE`, không khóa/mở ở đây (làm ở UC-04 để hồ sơ tài xế và tài khoản luôn cùng trạng thái).
- **Không tự khóa mình:** Quản lý không đổi `vai_tro` / `trang_thai` của chính mình; luôn còn ít nhất một Quản lý `HOAT_DONG` (kể cả hai Quản lý khóa nhau cùng lúc).
- Kết quả trả về **không bao giờ** có mật khẩu hay mật khẩu băm.

## Quyết định đã chốt (30/10/2026, Kiệt – Tài xem khi review PR)
1. **Tài khoản Tài xế:** UC-02 chỉ xem, đổi tên đăng nhập, họ tên, đặt lại mật khẩu; tạo, khóa/mở, vai trò làm ở UC-04.
2. **Tự khóa / tự hạ quyền:** chặn; và chặn khóa/hạ Quản lý `HOAT_DONG` cuối cùng. Lỡ mất hết Quản lý vẫn cứu được bằng lệnh `python -m app.tao_quan_ly` (UC-01-AC11).
3. **Đặt lại mật khẩu:** có (Quản lý nhập mật khẩu mới cho nhân viên quên mật khẩu). Đổi mật khẩu tự phục vụ, quên mật khẩu qua email vẫn là hướng phát triển.
4. **Mã lỗi:** đổi vai trò/khóa tài khoản Tài xế, tự khóa mình, khóa Quản lý cuối → **409** (sai trạng thái của tài khoản, không phải BR có mã trong `nghiep-vu.md`).
5. **Giới hạn đã biết:** đặt lại mật khẩu **không** làm mất hiệu lực token đang dùng của người đó (JWT không có phiên bản, muốn làm cần thêm cột và migration). Nghi bị lộ tài khoản thì khóa trước rồi đặt lại mật khẩu.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-02-AC1 | Thêm hợp lệ → 201: tài khoản `HOAT_DONG` đúng vai trò, đăng nhập được bằng tên và mật khẩu vừa đặt; mật khẩu lưu dạng băm; kết quả không có `mat_khau` / `mat_khau_bam` | API | NFR-SEC-01 |
| UC-02-AC2 | Dữ liệu sai → 400, không lưu: mật khẩu 7 ký tự bị chặn, 8 được (biên), 200 được, 201 bị chặn; vai trò `TAI_XE` hoặc lạ (`ADMIN`) bị chặn; thiếu tên đăng nhập, họ tên, mật khẩu; tên đăng nhập chỉ khoảng trắng; trường lạ | API | — |
| UC-02-AC3 | Trùng tên đăng nhập → 409 `TEN_DANG_NHAP_TRUNG` (cả khi trùng tài khoản Tài xế) khi thêm và khi đổi tên; đổi tên thành chính tên cũ → 200 | API | — |
| UC-02-AC4 | Danh sách: có cả tài khoản Tài xế; lọc `vai_tro`, `trang_thai`; tìm một phần tên đăng nhập / họ tên (`%`, `_` không làm lệch); phân trang đúng `tong`; trang ngoài phạm vi → rỗng; không dòng nào có mật khẩu băm | API | — |
| UC-02-AC5 | Sửa họ tên, tên đăng nhập, vai trò (giữa `QUAN_LY` / `DIEU_PHOI` / `KE_TOAN`) → 200 và lưu; đổi vai trò có hiệu lực ở request kế tiếp (Điều phối đổi thành Kế toán gọi API điều phối → 403); gửi `mat_khau` trong PATCH → 400; gửi `null` trường bắt buộc → 400 | API | BR-57 |
| UC-02-AC6 | Khóa → token đang dùng của người đó bị từ chối ngay (401), không đăng nhập lại được (403); mở lại → đăng nhập được, kể cả khi đang bị khóa tạm vì sai 5 lần (bộ đếm và `khoa_den` xóa); `trang_thai` khác `HOAT_DONG` / `NGUNG` → 400; `DELETE` → 405 | API | BR-60, NFR-SEC-05 |
| UC-02-AC7 | Đặt lại mật khẩu → 204: mật khẩu cũ không đăng nhập được, mật khẩu mới được; xóa bộ đếm sai và khóa tạm; mật khẩu 7 ký tự → 400; làm được với tài khoản Tài xế | API | NFR-SEC-01 |
| UC-02-AC8 | Tài khoản Tài xế: đổi `vai_tro` → 409; đổi `trang_thai` → 409 (chỉ ở UC-04); đổi tên đăng nhập, họ tên → 200; tài khoản khác đổi vai trò thành `TAI_XE` → 400 | API | — |
| UC-02-AC9 | Quản lý tự đổi `vai_tro` hoặc `trang_thai` của mình → 409, không đổi gì; tự đổi họ tên → 200. Có 2 Quản lý `HOAT_DONG`: khóa người kia → 200; còn 1 thì không ai khóa/hạ được (do chặn tự khóa). Hai Quản lý khóa nhau đồng thời → chỉ một thành công | API | — |
| UC-02-AC10 | Phân quyền: chỉ Quản lý; Điều phối, Kế toán, Tài xế gọi mọi endpoint → 403; chưa đăng nhập → 401; id không có → 404 | API | BR-57 |
| UC-02-AC11 | Giao diện Quản lý (menu "Người dùng"): bảng (tên đăng nhập, họ tên, vai trò, trạng thái, khóa tạm), ô tìm, lọc vai trò và trạng thái; form thêm (có mật khẩu) / sửa (không có mật khẩu; tài khoản Tài xế khóa ô vai trò); nút Khóa / Mở (hỏi xác nhận, ẩn với dòng của chính mình và dòng Tài xế); nút Đặt lại mật khẩu; lỗi tiếng Việt | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/nguoi_dung/{schemas,service,router}.py` (mới), `backend/app/main.py` (gắn router); `frontend/src/api/nguoiDung.ts` (mới), `frontend/src/pages/quan-ly/NguoiDungDanhSach.tsx` (mới), `frontend/src/App.tsx` (menu "Người dùng" của Quản lý); `docs/api.md` mục 2.1. Không đụng `models/`, không thêm migration.
- Test đã viết: `backend/tests/api/test_uc02_nguoi_dung.py` – **41 passed**; toàn bộ backend **395 passed** (30/10). `ruff check`, `ruff format`, `npm run lint`, `npm run build` sạch.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc02_nguoi_dung.py` (Docker Desktop đang chạy)
- Lệch đặc tả: thêm endpoint `PUT /api/nguoi-dung/{id}/mat-khau` và ghi rõ các ca 409 → đã sửa `docs/api.md` mục 2.1 cùng commit.
- Cách làm đáng chú ý: tên đăng nhập, họ tên, mật khẩu dùng lại kiểu `TenDangNhap`, `HoTen`, `MatKhau` của UC-04. Đổi vai trò/trạng thái thì khóa (`FOR UPDATE`) mọi Quản lý đang hoạt động theo thứ tự id **trước** khi khóa dòng cần sửa: hai Quản lý khóa nhau cùng lúc thì xếp hàng, không deadlock, người sau bị chặn. Đã thử bỏ khóa dòng: test `test_uc02_ac9_hai_quan_ly_khoa_nhau_cung_luc` hỏng 5/5 lần, có khóa thì đạt.
- AC11 thử tay 30/10 (Kiệt, Edge/Chrome, `http://127.0.0.1:5173`): 6 ca a–f đạt, ảnh trong `docs/test-evidence/UC-02/`. Ca e bước 7 ký tự bị trình duyệt chặn (Kiệt xác nhận, không chụp).
- `ponytail-review` 30/10 (Kiệt tự review): không có mục phải sửa; sửa câu báo lỗi `TAI_KHOAN_TAI_XE` cho đúng cả khi đổi vai trò. Để Tài quyết: gộp `client_rieng` (lặp ở test UC-02 và UC-04) vào `tests/conftest.py`.
- Giao diện ẩn nút Khóa ở dòng của chính mình và dòng tài xế, khóa ô vai trò khi sửa tài xế hoặc chính mình; máy chủ vẫn chặn (409) nếu gọi thẳng API.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-02-AC1 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac1_them_hop_le (3 ca)` | Đạt | 30/10/2026 |
| UC-02-AC2 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac2_* (14 ca)` | Đạt | 30/10/2026 |
| UC-02-AC3 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac3_trung_ten_dang_nhap` | Đạt | 30/10/2026 |
| UC-02-AC4 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac4_danh_sach_loc_tim_phan_trang` | Đạt | 30/10/2026 |
| UC-02-AC5 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac5_* (5 ca)` | Đạt | 30/10/2026 |
| UC-02-AC6 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac6_* (2 ca)` | Đạt | 30/10/2026 |
| UC-02-AC7 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac7_* (5 ca)` | Đạt | 30/10/2026 |
| UC-02-AC8 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac8_tai_khoan_tai_xe` | Đạt | 30/10/2026 |
| UC-02-AC9 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac9_* (5 ca, có ca đồng thời)` | Đạt | 30/10/2026 |
| UC-02-AC10 | API | `tests/api/test_uc02_nguoi_dung.py::test_uc02_ac10_* (4 ca)` | Đạt | 30/10/2026 |
| UC-02-AC11 | UI | `docs/test-evidence/UC-02/` (6 ảnh, ca a–f trong `docs/test-evidence/UC-02/du-lieu.md`) + Kiệt xác nhận | Đạt | 30/10/2026 |
