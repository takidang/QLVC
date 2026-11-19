# UC-39: Hồ sơ cá nhân và ảnh đại diện

- **Trạng thái:** Hoàn thành 19/11/2026 – 7/7 AC (Tài chốt "cách 1" 19/11; AC7 Kiệt thử, PR #67)
- **Tác nhân:** mọi người dùng đã đăng nhập (Quản lý, Điều phối, Kế toán, Tài xế)
- **Đặc tả:** `docs/use-cases.md` (UC-39, mức C, thêm 19/11/2026 cho giao diện v3), `docs/api.md` mục Xác thực, `docs/security-rules.md` (upload)
- **Quy tắc nghiệp vụ liên quan:** BR-57 (phân quyền ở máy chủ), BR-14, 15 (GPLX: chỉ xem)
- **Người làm:** Tài
- **Liên quan:** trang Tài khoản (`docs/stories/GD-cai-dat-tai-khoan.md`), UC-35 đổi mật khẩu, UC-02 người dùng, UC-04 tài xế

## Mô tả ngắn
Trên trang Tài khoản, người dùng xem hồ sơ của mình và tự đổi **ảnh đại diện**. Mọi thông tin khác do công ty quản lý, chỉ Quản lý sửa ở UC-02 / UC-04; trang Tài khoản hiện chữ xám kèm "Liên hệ Quản lý để thay đổi".

## Quyết định (Tài chốt 19/11/2026)
1. **Tự đổi:** ảnh đại diện (và mật khẩu – UC-35). **Chỉ xem:** họ tên, tên đăng nhập, vai trò, trạng thái; tài xế thêm SĐT, số / hạng / hạn GPLX.
2. **SĐT không cho tự đổi:** Điều phối dùng SĐT để gọi tài xế khi có sự cố; tự đổi thì gõ nhầm là mất liên lạc, người khác cầm máy có thể đổi sang số mình, và không ai được báo. Phương án "gửi yêu cầu, Quản lý duyệt" bị bỏ vì nặng (bảng yêu cầu, màn duyệt, thông báo) so với lợi ích.
3. **Lưu ảnh:** thêm cột `nguoi_dung.anh_dai_dien` (tên file do máy chủ sinh, nullable), dùng `app/luu_tru.py` (`kiem_anh`, `luu`, `xoa`) như ảnh chứng từ. Không dùng bảng `TEP` (ràng buộc "đúng một chủ sở hữu" chỉ cho lượt quét / chi phí / sự cố / chuyến).
4. **Xem ảnh:** chỉ ảnh của chính mình (vòng tên góc phải, trang Tài khoản) → `GET /api/auth/anh-dai-dien` trả ảnh theo cookie đăng nhập (cùng tên miền), không cần link ký HMAC. Không có màn nào xem ảnh người khác (YAGNI).
5. Đổi ảnh thì xóa file cũ; xóa ảnh thì quay về chữ tắt.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-39-AC1 | `GET /api/auth/ho-so` trả hồ sơ của chính người gọi: `ten_dang_nhap, ho_ten, vai_tro, trang_thai, co_anh_dai_dien`; tài xế thêm `tai_xe: {sdt, so_gplx, hang_gplx, han_gplx}`; người khác vai trò không có `tai_xe`. Chưa đăng nhập → 401 | API | BR-57 |
| UC-39-AC2 | `PUT /api/auth/anh-dai-dien` (multipart, 1 file): JPEG/PNG nhận theo byte đầu, ≤ 500 KB → 200, `co_anh_dai_dien` true; file sai loại / rỗng → 400, quá lớn → 413 (mã như `kiem_anh`); tên file do máy chủ sinh, không dùng tên client gửi | API | security-rules |
| UC-39-AC3 | Đổi ảnh lần hai: file cũ bị xóa khỏi nơi lưu; `DELETE /api/auth/anh-dai-dien` → 204, xóa file, `co_anh_dai_dien` false; xóa khi chưa có ảnh → 204 | API | — |
| UC-39-AC4 | `GET /api/auth/anh-dai-dien` trả đúng ảnh của người gọi, `Content-Type` theo đuôi đã kiểm, `X-Content-Type-Options: nosniff`, `Cache-Control: private, no-cache`; chưa có ảnh → 404; chưa đăng nhập → 401. Không có đường nào lấy ảnh người khác | API | BR-57, security-rules |
| UC-39-AC5 | Không có API nào cho người dùng tự sửa họ tên, SĐT, vai trò, tên đăng nhập, GPLX: `PATCH`/`PUT /api/auth/ho-so` → 405; các trường đó gửi kèm form ảnh bị bỏ qua (CSDL không đổi) | API | BR-57 |
| UC-39-AC6 | `GET /api/auth/toi` (đang dùng ở khung trang) có thêm `co_anh_dai_dien` để vòng góc phải biết hiện ảnh hay chữ tắt | API | — |
| UC-39-AC7 | Giao diện: trang Tài khoản có khối Ảnh đại diện (xem, chọn ảnh, nén ở trình duyệt như ảnh chứng từ nếu có sẵn hàm nén, xóa); thông tin chỉ xem ghi "Liên hệ Quản lý để thay đổi"; tài xế thấy GPLX, hạn còn ≤ 30 ngày tô cảnh báo (BR-21); vòng góc phải hiện ảnh, không có ảnh thì chữ tắt; màn 390 px, bản tối không vỡ | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi:
  - Backend: `backend/app/models/danh_muc.py` (cột `NguoiDung.anh_dai_dien`, property `co_anh_dai_dien`), `backend/alembic/versions/2026_11_19_1618-5367154f7c64_uc_39_anh_dai_dien.py` (revision `5367154f7c64`), `backend/app/luu_tru.py` (`doc`, kiểm dạng tên hex + `.jpg`/`.png` chặn traversal ở `doc`/`xoa`, `LOAI_ANH`), `backend/app/auth/{schemas,service,router}.py` (`GET /api/auth/ho-so`, `PUT/DELETE/GET /api/auth/anh-dai-dien`, thêm `co_anh_dai_dien` vào `NguoiDungRa`).
  - Frontend: `frontend/src/api/auth.ts` (`HoSo`, `TaiXeHoSo`, `hoSo`, `doiAnhDaiDien`, `xoaAnhDaiDien`, `urlAnhDaiDien`, `NguoiDung.co_anh_dai_dien`), `frontend/src/pages/TaiKhoan.tsx`, `frontend/src/MenuTaiKhoan.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`.
  - Tài liệu: `docs/use-cases.md`, `docs/api.md`, `docs/so-do.md`, `docs/giao-dien.md`, `docs/stories/UC-39-ho-so-ca-nhan.md`.
- Test đã viết: `backend/tests/api/test_uc39_ho_so.py` (38 ca: AC1–AC6 và unit `luu_tru.doc`/`xoa`), cập nhật `backend/tests/api/test_uc01_dang_nhap.py` (`co_anh_dai_dien` trong phản hồi đăng nhập).
- Lệnh chạy test:
  - `cd backend; .venv\Scripts\python -m alembic check`
  - `cd backend; .venv\Scripts\python -m pytest -q`
  - `cd backend; .venv\Scripts\python -m ruff check app tests`
  - `cd frontend; npm run typecheck; npm run lint; npm run format; npm run build`
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa: không lệch; đã cập nhật `docs/use-cases.md`, `docs/api.md`, `docs/so-do.md`, `docs/giao-dien.md` cùng commit.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-39-AC1 | API | `test_uc39_ac1_vai_tro_khac_khong_co_tai_xe` (3 vai trò), `test_uc39_ac1_tai_xe_du_bon_truong`, `test_uc39_ac1_chua_dang_nhap_401` | Đạt | 19/11/2026 |
| UC-39-AC2 | API | `test_uc39_ac2_tai_len_jpeg_va_png` (2 ca), `test_uc39_ac2_anh_dung_500kb`, `test_uc39_ac2_tu_choi_anh_sai_hoac_qua_lon` (5 ca), `test_uc39_ac2_thieu_file_va_chua_dang_nhap`, `test_uc39_ac2_rollback_xoa_file_moi_khi_csdl_loi` | Đạt | 19/11/2026 |
| UC-39-AC3 | API | `test_uc39_ac3_doi_lan_hai_xoa_file_cu`, `test_uc39_ac3_loi_xoa_file_cu_khong_lam_hong_request`, `test_uc39_ac3_delete_xoa_file_va_delete_khi_chua_co`, `test_uc39_ac3_delete_chua_dang_nhap_401` | Đạt | 19/11/2026 |
| UC-39-AC4 | API | `test_uc39_ac4_tra_dung_byte_va_header` (2 ca), `test_uc39_ac4_chua_co_anh_hoac_file_mat_404`, `test_uc39_ac4_hai_nguoi_chi_nhan_anh_cua_minh`, `test_uc39_ac4_chua_dang_nhap_401`, `test_uc39_unit_luu_tru_doc_*` (11 ca) | Đạt | 19/11/2026 |
| UC-39-AC5 | API | `test_uc39_ac5_patch_put_ho_so_405`, `test_uc39_ac5_truong_la_trong_form_anh_khong_doi_csdl` | Đạt | 19/11/2026 |
| UC-39-AC6 | API | `test_uc39_ac6_toi_co_co_anh_dai_dien` | Đạt | 19/11/2026 |
| UC-39-AC7 | UI | `docs/test-evidence/UC-39/` (7 ảnh, `du-lieu.md`): tải / đổi / xóa ảnh, tệp sai loại, thông tin chỉ xem, tài xế GPLX còn 20 ngày tô cam, 390 px, bản tối | Đạt (Kiệt thử; 1 góp ý không chặn) | 19/11/2026 |
