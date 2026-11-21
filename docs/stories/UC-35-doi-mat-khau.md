# UC-35: Đổi mật khẩu của chính mình

- **Trạng thái:** Hoàn thành 12/11/2026 – 5/5 AC đạt (Đã duyệt 12/11/2026 – Tài: "làm UC-35 36 đi")
- **Tác nhân:** Quản lý, Điều phối, Kế toán, Tài xế
- **Đặc tả:** chưa có trong `docs/use-cases.md` (UC mới, giao diện v2 "Cài đặt cá nhân"); `docs/api.md` mục 2.1
- **Quy tắc nghiệp vụ liên quan:** BR-57, NFR-SEC-05, `docs/security-rules.md`
- **Người làm:** Tài (backend); giao diện do phiên giao diện v2 làm

## Mô tả ngắn
Người dùng đang đăng nhập tự đổi mật khẩu bằng cách nhập mật khẩu hiện tại và mật khẩu mới. Hiện chỉ Quản lý đặt lại được mật khẩu người khác (UC-02).

## Quyết định (Tài duyệt 12/11/2026)
1. `PUT /api/auth/mat-khau` `{mat_khau_cu, mat_khau_moi}` → 204. Mật khẩu mới 8–200 ký tự như `MatKhau` ở UC-02, 04.
2. Sai mật khẩu hiện tại → 422 `SAI_MAT_KHAU_CU` (không dùng 401, để giao diện không tưởng phiên hết hạn). Tính là một lần sai như đăng nhập: sai 5 lần liên tiếp thì khóa 15 phút (dùng chung `so_lan_sai`, `khoa_den`), nên không dò mật khẩu qua chức năng này được.
3. Mật khẩu mới trùng mật khẩu cũ → 422 `MAT_KHAU_TRUNG`.
4. Phiên đang dùng vẫn còn hạn sau khi đổi (JWT không có phiên bản, như UC-02 quyết định 5). Không log mật khẩu.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-35-AC1 | Đúng mật khẩu cũ, mật khẩu mới hợp lệ → 204; đăng nhập bằng mật khẩu mới được, bằng mật khẩu cũ → 401; bộ đếm sai được xóa | API | BR-57 |
| UC-35-AC2 | Sai mật khẩu cũ → 422 `SAI_MAT_KHAU_CU`, mật khẩu không đổi; sai 5 lần liên tiếp → tài khoản khóa 15 phút (đăng nhập, đổi mật khẩu đều 429 `KHOA_TAM`, kể cả mật khẩu đúng); đổi đúng thì đếm lại | API | NFR-SEC-05 |
| UC-35-AC3 | Mật khẩu mới trùng cũ → 422 `MAT_KHAU_TRUNG`; mới 7 ký tự (biên: 8 được), quá 200, thiếu trường, trường lạ → 400 | API | — |
| UC-35-AC4 | Cả 4 vai trò đổi được; chưa đăng nhập → 401; chỉ đổi mật khẩu của chính mình (không nhận id người khác) | API | BR-57 |
| UC-35-AC5 | Giao diện: màn Cài đặt cá nhân (phiên giao diện v2) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/auth/{router,schemas,service}.py` (`PUT /api/auth/mat-khau`, `DoiMatKhauVao`, `doi_mat_khau`), `docs/api.md` mục 2.1.
- Test đã viết: `backend/tests/api/test_uc35_doi_mat_khau.py` (17 ca). Thử làm hỏng 4 chỗ (không đếm lần sai, bỏ kiểm trùng, bỏ kiểm khóa, không xóa đếm khi đổi đúng) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc35_doi_mat_khau.py`
- Lệch đặc tả: không (UC mới, chưa có trong `use-cases.md`; ghi `api.md`).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-35-AC1 | API | `test_uc35_ac1_doi_dung` | Đạt | 12/11/2026 |
| UC-35-AC2 | API | `test_uc35_ac2_*` (3 ca) | Đạt | 12/11/2026 |
| UC-35-AC3 | API | `test_uc35_ac3_*` (7 ca, gồm biên 8 ký tự) | Đạt | 12/11/2026 |
| UC-35-AC4 | API | `test_uc35_ac4_*` (6 ca) | Đạt | 12/11/2026 |
| UC-35-AC5 | UI | Màn Cài đặt cá nhân (menu tài khoản): Kiệt thử 12/11, ảnh `docs/test-evidence/UC-35/a-sai-mat-khau-cu.png` (PR #55) | Đạt | 12/11/2026 |
