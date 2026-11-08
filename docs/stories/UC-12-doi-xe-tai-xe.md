# UC-12: Gán / đổi xe và tài xế

- **Trạng thái:** Xong 08/11/2026 – 5/5 AC (AC5 Kiệt thử 07/11, PR #18). Còn 1 lỗi giao diện nhỏ ngoài AC: khung Đổi xe đang mở mà ghép thêm đơn thì danh sách xe không tải lại (máy chủ vẫn chặn BR-01), Tài sửa riêng (Tài giao "làm luôn" 30/10; quyết định dưới đây Tài xem lại)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-11/UC-12) · `docs/api.md` mục 2.4 (`/api/chuyen/{id}/xe-kha-dung`, `/tai-xe-kha-dung`, `PUT /phan-cong`)
- **Quy tắc nghiệp vụ liên quan:** BR-01, 02 (tải theo đơn đang ghép), BR-09, BR-11…19, BR-57, BR-67
- **Người làm:** Tài

## Mô tả ngắn
Chuyến `LAP` cần đổi xe hoặc tài xế (xe hỏng, tài xế nghỉ). Điều phối mở chi tiết chuyến, bấm "Đổi xe / tài xế", chọn trong danh sách đã đánh dấu khả dụng kèm lý do loại, rồi lưu. Hệ thống kiểm lại BR-11…19 với chính chuyến này (không coi là trùng lịch với nó) và tải, thể tích theo đơn đang ghép (BR-67).

## Quyết định (Tài xem lại)
1. **Gửi cả xe và tài xế mỗi lần** (`{xe_id, tai_xe_id}`), giữ nguyên cái không đổi. Kiểm đủ BR-11…19 cho cả hai – đơn giản hơn kiểm riêng từng trường hợp, và đổi xe có thể làm tài xế cũ sai hạng (BR-14).
2. **Kết thúc dự kiến không đổi** khi đổi xe/tài xế (ETA không phụ thuộc xe), nên dùng `ket_thuc_du_kien` đang lưu để kiểm giấy tờ và trùng lịch.
3. **Chỉ khóa xe, tài xế mới** (sau khóa chuyến), theo thứ tự xe → tài xế như lập chuyến, để không khóa chéo với UC-11.
4. Không ghi lịch sử trạng thái (trạng thái chuyến không đổi).
5. `tai-xe-kha-dung` của chuyến mặc định xét hạng GPLX theo xe hiện tại, truyền `xe_id` để xét theo xe sắp đổi.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-12-AC1 | `PUT /api/chuyen/{id}/phan-cong` hợp lệ (C01 có Đ1, Đ4 → X4, Dũng) → 200 trả chi tiết chuyến với xe, tài xế mới, đơn và lịch trình giữ nguyên; giữ nguyên xe, tài xế hiện tại vẫn 200 (không trùng lịch với chính nó) | API | BR-67 |
| UC-12-AC2 | Bị chặn, không đổi: xe 1.500 kg với hàng 2.600 kg → 422 `BR-01`; tài xế hạng B với xe 9.500 kg → `BR-14`; tài xế có chuyến chồng giờ → `BR-17`; xe có chuyến chồng giờ → `BR-16`; chuyến, xe, tài xế không tồn tại → 404; trường lạ → 400; chuyến không `LAP` → 409 `BR-09` | API | BR-01, 09, 14, 16, 17 |
| UC-12-AC3 | `GET /api/chuyen/{id}/xe-kha-dung` và `/tai-xe-kha-dung[?xe_id]`: xe đang dùng khả dụng; xe nhỏ hơn hàng đang ghép bị loại `BR-01`; tài xế hạng B bị loại `BR-14` theo xe hiện tại, khả dụng khi truyền xe nhỏ | API | BR-01, 14 |
| UC-12-AC4 | Phân quyền: Điều phối, Quản lý được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-12-AC5 | Giao diện: trang chi tiết chuyến `LAP` có nút "Đổi xe / tài xế" → chọn xe, tài xế (cái bị loại hiện lý do kèm mã BR) → lưu, thông tin chuyến cập nhật; lỗi hiện kèm mã BR | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/lich_trinh.py` (tách `xet_tai` cho BR-01, 02 dùng chung), `backend/app/modules/chuyen/{schemas,service,router}.py` (`phan_cong`, danh sách khả dụng cho chuyến đã có, dùng chung `_ds_xe`, `_ds_tai_xe` với UC-11); `frontend/src/api/chuyen.ts`, `frontend/src/pages/dieu-phoi/ChuyenChiTiet.tsx` (khối Đổi xe / tài xế, dùng lại `ChonKhaDung` của UC-11).
- Test đã viết: `backend/tests/api/test_uc12_doi_xe_tai_xe.py` (9 ca, dùng lại dữ liệu kịch bản của `test_uc13_ghep_don.py`).  Toàn bộ **363 passed** (30/10), `ruff`, `npm run lint`, `npm run build` sạch.
- Lệnh chạy test: `cd backend; .venv\\Scripts\\python -m pytest tests/api/test_uc12_doi_xe_tai_xe.py`
- Lệch đặc tả: không.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-12-AC1 | API | `test_uc12_ac1_doi_xe_va_tai_xe` | Đạt | 30/10/2026 |
| UC-12-AC2 | API | `test_uc12_ac2_* (3 ca)` | Đạt | 30/10/2026 |
| UC-12-AC3 | API | `test_uc12_ac3_kha_dung_cho_chuyen` | Đạt | 30/10/2026 |
| UC-12-AC4 | API | `test_uc12_ac4_* (4 ca)` | Đạt | 30/10/2026 |
| UC-12-AC5 | UI | Kiệt thử 3/3 ca: `docs/test-evidence/UC-12/a…c-*.png`; ghi nhận: danh sách xe không tải lại khi ghép đơn lúc khung đổi xe đang mở (máy chủ vẫn chặn BR-01) – Tài xem | Đạt | 07/11/2026 |
