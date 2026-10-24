# UC-07: Quản lý bảng giá và cấu hình

- **Trạng thái:** Hoàn thành 24/10/2026 (Đã duyệt 24/10/2026 – Tài chọn: tỉnh gõ tự do, giá có ngày hiệu lực)
- **Tác nhân:** Quản lý
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-07, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2.1 · `docs/nghiep-vu.md` mục 3 (CFG), BR-48 · ERD `docs/so-do.md` mục 5 (BANG_GIA, CAU_HINH)
- **Quy tắc nghiệp vụ liên quan:** BR-48 (cước theo đơn giá của cặp tỉnh; không có giá thì không tạo được đơn), BR-32 (đổi bảng giá không ảnh hưởng đơn đã tạo – kiểm ở UC-08), CFG-01…10, BR-57
- **Người làm:** Tài

## Mô tả ngắn
Quản lý nhập đơn giá/kg và cước tối thiểu cho từng cặp (tỉnh lấy, tỉnh giao), mỗi mức có ngày bắt đầu hiệu lực; và chỉnh các tham số cấu hình CFG. Tạo đơn (UC-08) tra giá bằng hàm `tra_gia` của story này.

## Đặc tả rút gọn
- **Bảng giá:** mỗi dòng = (tỉnh lấy, tỉnh giao, đơn giá/kg, cước tối thiểu, hiệu lực từ). Có chiều: HCM→Cần Thơ khác Cần Thơ→HCM. Tỉnh lấy = tỉnh giao được (tuyến nội tỉnh, giả định A3).
- **Tra giá** cho một cặp tại một ngày: mức có `hieu_luc_tu` mới nhất mà ≤ ngày đó. Tên tỉnh so sánh không phân biệt hoa thường, bỏ khoảng trắng đầu cuối.
- **Không xóa mức giá** (`api.md` không có DELETE): nhập sai thì sửa; muốn đổi giá thì thêm mức mới có ngày hiệu lực mới.
- **Cấu hình:** 9 tham số CFG-01, 02, 04…10 (CFG-03 đã bỏ ở 0.5), nạp sẵn giá trị mặc định của `nghiep-vu.md` mục 3. Sửa thì ghi người sửa, thời điểm (giờ máy chủ).

## Quyết định (24/10)
1. **Tỉnh gõ tự do**, so không phân biệt hoa thường; giao diện gợi ý tên tỉnh đã dùng để tránh gõ lệch ("TP.HCM" và "Hồ Chí Minh" vẫn là hai tỉnh khác nhau – người nhập phải dùng thống nhất). Lý do: danh sách tỉnh đang thay đổi sau sáp nhập (cần kiểm tra), không khóa cứng.
2. **Giá theo ngày hiệu lực**: cùng cặp tỉnh, cùng ngày hiệu lực thì trùng (409); khác ngày thì là mức mới.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-07-AC1 | Quản lý thêm mức giá → 201; tên tỉnh bỏ khoảng trắng đầu cuối; đơn giá/kg 0 → 400, 1 → được; cước tối thiểu −1 → 400, 0 → được; thiếu ngày hiệu lực → 400; tỉnh lấy = tỉnh giao được | API | BR-48 |
| UC-07-AC2 | Cùng cặp tỉnh (khác hoa thường: "tp.hcm" / "TP.HCM") và cùng ngày hiệu lực → 409; cùng cặp khác ngày → 201; hai người thêm cùng lúc chỉ một thành công (ràng buộc unique ở CSDL) | API | — |
| UC-07-AC3 | `tra_gia(cặp, ngày)`: có mức 01/10 và 01/11 → ngày 15/10 dùng mức 01/10, ngày 01/11 (biên) dùng mức 01/11; mức tương lai không dùng; chiều ngược không dùng; tỉnh khác hoa thường, có khoảng trắng vẫn khớp; không có mức nào ≤ ngày → không có giá | Logic | BR-48 |
| UC-07-AC4 | Danh sách: tìm theo tên tỉnh (lấy hoặc giao), mỗi mức có cờ `dang_ap_dung` (đúng một mức mỗi cặp có cờ, là mức đang áp dụng hôm nay), phân trang | API | BR-48 |
| UC-07-AC5 | Sửa mức giá → 200; sửa thành trùng cặp + ngày của mức khác → 409; mức không tồn tại → 404; gửi `null` cho trường bắt buộc → 400 | API | — |
| UC-07-AC6 | Cấu hình: danh sách 9 tham số (không có CFG-03) với tên, giá trị, đơn vị; giá trị mặc định đúng mục 3 nghiệp vụ (CFG-01 = 333, CFG-07 = 10/48/4, CFG-08 = 20…) | API | CFG-xx |
| UC-07-AC7 | Sửa cấu hình: kiểm theo từng tham số – CFG-01, 06 số nguyên > 0; CFG-04 ≥ 1; CFG-02, 05, 08, 09, 10 ≥ 0; CFG-07 dạng `ngày/tuần/liên tục` ba số nguyên > 0 – sai thì 400 câu tiếng Việt; mã không có hoặc CFG-03 → 404; lưu người sửa và thời điểm máy chủ | API | CFG-xx |
| UC-07-AC8 | Phân quyền: chỉ Quản lý xem/thêm/sửa bảng giá và cấu hình; Điều phối, Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-07-AC9 | Giao diện Quản lý: trang Bảng giá (danh sách, tìm, thêm/sửa, gợi ý tên tỉnh đã dùng, đánh dấu mức đang áp dụng) và trang Cấu hình (sửa từng tham số, báo lỗi tiếng Việt) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/models/danh_muc.py` (unique `lower(tinh_lay), lower(tinh_giao), hieu_luc_tu`), migration `177fdcb334df` (index + nạp CFG mặc định), `backend/app/domain/cau_hinh.py`, `backend/app/thoi_gian.py` (giờ Việt Nam), `backend/app/modules/danh_muc/{bang_gia,cau_hinh}/`, `backend/app/main.py`, `backend/tests/conftest.py` (nạp lại CFG sau khi xóa bảng; kiểm migration khớp code); `frontend/src/api/bangGia.ts`, `frontend/src/pages/quan-ly/{BangGiaDanhSach,CauHinh}.tsx`, `frontend/src/App.tsx`.
- Test đã viết: `backend/tests/api/test_uc07_bang_gia_cau_hinh.py` (33 ca). Toàn bộ **123 passed** (24/10). `alembic upgrade`/`downgrade`/`check` chạy được.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest`.
- Lệch đặc tả: thêm `GET /api/bang-gia/ten-tinh` (gợi ý tên tỉnh) – đã ghi `api.md`. Hàm `tra_gia` (BR-48) và `cau_hinh.service.lay` để UC-08 và các UC sau dùng.
- AC9 thử tay 24/10 (Tài): hai mức giá, cờ đang áp dụng chuyển sang mức hôm nay, trùng tỉnh viết thường bị chặn, sửa CFG-08 ghi người sửa và giờ, CFG-01 sai báo lỗi. Lần thử đầu báo "Có lỗi" do uvicorn `--reload` kẹt trên Windows (tiến trình cũ chưa có route mới → 404): chạy backend không `--reload`; thông báo lỗi chung giờ kèm mã HTTP. Gợi ý tên tỉnh (`datalist`) hiện sai chỗ trong trình duyệt nhúng VS Code – thử bằng Edge/Chrome.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-07-AC1 | API | `test_uc07_ac1_them_muc_gia (9 ca)` | Đạt | 24/10/2026 |
| UC-07-AC2 | API | `test_uc07_ac2_trung_cap_tinh_va_ngay` | Đạt | 24/10/2026 |
| UC-07-AC3 | Logic | `test_uc07_ac3_tra_gia_theo_ngay_hieu_luc` | Đạt | 24/10/2026 |
| UC-07-AC4 | API | `test_uc07_ac4_danh_sach_va_dang_ap_dung` | Đạt | 24/10/2026 |
| UC-07-AC5 | API | `test_uc07_ac5_sua_muc_gia` | Đạt | 24/10/2026 |
| UC-07-AC6 | API | `test_uc07_ac6_cau_hinh_mac_dinh` | Đạt | 24/10/2026 |
| UC-07-AC7 | API | `test_uc07_ac7_* (15 ca)` | Đạt | 24/10/2026 |
| UC-07-AC8 | API | `test_uc07_ac8_* (4 ca)` | Đạt | 24/10/2026 |
| UC-07-AC9 | UI | `docs/test-evidence/UC-07/` (4 ảnh) + Tài xác nhận | Đạt | 24/10/2026 |
