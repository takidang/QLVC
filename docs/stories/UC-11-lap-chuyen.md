# UC-11: Lập chuyến

- **Trạng thái:** Đang làm – AC1–AC11 đạt, AC12 giao diện đã làm, chờ Kiệt thử (Đã duyệt 30/10/2026 – Tài)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán chỉ xem
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-11/UC-12) · `docs/api.md` mục 2.4 · `docs/nghiep-vu.md` nhóm B, C, H, mục 2.1 (công thức), mục 11 (C01) · ca test `docs/ca-test-br.md` (TC-BR11…19, 22, 57, 64, 65)
- **Quy tắc nghiệp vụ liên quan:** BR-11…19 (xe, tài xế), BR-22 (lập chuyến ở `LAP`), BR-30 (lịch sử trạng thái), BR-57 (phân quyền), BR-64 (kết thúc dự kiến, khoảng chiếm), BR-65 (giờ lái dự kiến)
- **Người làm:** Tài

## Mô tả ngắn
Điều phối chọn tuyến và giờ khởi hành; hệ thống liệt kê xe và tài xế, đánh dấu cái nào dùng được, cái nào bị loại kèm lý do (mã BR). Điều phối chọn xe, tài xế và lưu; hệ thống kiểm lại BR-11…19 dưới khóa dòng rồi tạo chuyến `LAP`. Chuyến mới chưa có đơn nên tính như chạy rỗng (BR-64); UC-13 ghép đơn sẽ kéo dài kết thúc dự kiến và kiểm lại theo BR-67.

## Quyết định (Tài duyệt 30/10)
1. **Ngày dùng để so hạn giấy tờ** (BR-12, 13, 15) = ngày (giờ Việt Nam) của kết thúc dự kiến. Hạn đúng bằng ngày đó vẫn đạt (≥).
2. **Giờ lái của một chuyến** nằm trong khoảng [khởi hành, khởi hành + giờ lái) để chia theo ngày (BR-18) và theo tuần Thứ Hai–Chủ Nhật (BR-19, chốt 30/10). Giới hạn lấy từ `CFG-07` (mặc định 10/48), đệm `CFG-05`. Chỉ tính chuyến khác `HUY`.
3. **Tài xế `NGUNG`** bị loại (lý do "tài xế ngừng hoạt động", mã `TAI_XE_NGUNG`), theo ghi chú của Kiệt ở UC-04. **Tuyến `NGUNG`** không lập chuyến được (422 `TUYEN_NGUNG`).
4. **Vi phạm nhiều quy tắc cùng lúc:** trả 422, `ma` là BR đầu tiên, `chi_tiet` liệt kê mọi vi phạm (giống BR-31 của UC-08), giao diện hiện đủ.
5. **Chống hai người gán cùng lúc:** khóa dòng xe và tài xế (`SELECT … FOR UPDATE`) trước khi kiểm BR-16…19, trong cùng giao dịch tạo chuyến.
6. **`tai-xe-kha-dung` nhận thêm `xe_id` (không bắt buộc)** để lọc BR-14; không có `xe_id` thì bỏ qua BR-14. Sửa `api.md`.
7. **Danh sách chuyến** (`GET /api/chuyen`) ở story này chỉ lọc trạng thái, ngày khởi hành, tuyến, phân trang; bảng chuyến trong ngày (% đầy, cờ trễ…) làm ở UC-32. Chi tiết chuyến ở đây có tổng quan (tuyến, xe, tài xế, giờ, kết thúc dự kiến, trạng thái); các thẻ khác thêm dần ở UC-13, 15, 32.
8. **Mã chuyến** `CH-yyMMdd-NN`: ngày khởi hành (giờ Việt Nam) + số thứ tự trong ngày, ví dụ `CH-261020-01`. Hai người lập cùng ngày không trùng số nhờ khóa theo ngày (`pg_advisory_xact_lock`).
9. **Giờ khởi hành đã qua** → 422 `KHOI_HANH_DA_QUA` (lập chuyến là lên kế hoạch).
10. **Giao diện** làm trong story này, Kiệt thử (như UC-05, UC-08).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-11-AC1 | Tính thời gian (hàm thuần): C01 rỗng T01 khởi hành 20/10 06:00 → kết thúc dự kiến **11:30** (06:00 + 270′ + `CFG-05` 60′), khoảng chiếm [06:00, 11:30); giờ lái **270′**; khởi hành 22:00 → 20/10: **120′**, 21/10: **150′**; chuyến Chủ Nhật 25/10 22:00 → tuần 19–25/10 được 120′, tuần 26/10–01/11 được 150′ | Logic | BR-64, 65 |
| UC-11-AC2 | Xe (hàm thuần): X1 `HOAT_DONG` đạt; X3 `NGUNG` → `BR-11`; X2 đăng kiểm 19/10 → `BR-12`, sửa thành 20/10 đạt (biên); X5 bảo hiểm 19/10 → `BR-13`, 20/10 đạt (biên); chuyến 22:00 kết thúc 21/10 thì đăng kiểm 20/10 → `BR-12` | Logic | BR-11, 12, 13 |
| UC-11-AC3 | Tài xế (hàm thuần): An hạng C với X1 đạt; Bình hạng B với X1 (9.500 kg) → `BR-14` (dùng `kiem_br14_hang_gplx` của UC-04); Cường GPLX hết 19/10 → `BR-15`, 20/10 đạt (biên); tài xế `NGUNG` bị loại | Logic | BR-14, 15 |
| UC-11-AC4 | Trùng lịch (khoảng nửa mở): X1 có C02 khởi hành 10:00 → `BR-16`, 11:30 đạt (biên); An có C00 lúc 11:00 → `BR-17`, 11:30 đạt; chuyến trước kết thúc đúng 06:00 đạt; chuyến `HUY` không tính | Logic | BR-16, 17 |
| UC-11-AC5 | Giờ lái: An đã có 6 giờ lái ngày 20/10 (không chồng giờ) → 4,5 + 6 = 10,5 > 10 → `BR-18`; 5,5 giờ → đúng 10 đạt (biên); đã có 44 giờ trong tuần → 48,5 → `BR-19`; 43,5 giờ → đúng 48 đạt (biên); đổi `CFG-07` thành `9/48/4` thì 5,5 giờ → `BR-18` | Logic | BR-18, 19 |
| UC-11-AC6 | `POST /api/chuyen` hợp lệ (T01, 20/10 06:00, X1, An) → 201: trạng thái `LAP`, có mã chuyến, `ket_thuc_du_kien` 11:30, người lập là Điều phối đang đăng nhập; ghi một dòng lịch sử trạng thái (rỗng → `LAP`) | API | BR-22, 30 |
| UC-11-AC7 | Lập bị chặn và không tạo gì: vi phạm bất kỳ BR-11…19 → 422 với `ma` là BR đầu tiên, `chi_tiet` đủ mọi vi phạm; thiếu `xe_id` hoặc `tai_xe_id` → 400; giờ khởi hành không có múi giờ → 400; tuyến, xe, tài xế không tồn tại → 404; tuyến `NGUNG` → 422; giờ khởi hành đã qua → 422 | API | BR-22 |
| UC-11-AC8 | Hai yêu cầu lập chuyến cùng xe X1, cùng giờ, gửi đồng thời → đúng một 201, cái còn lại 422 `BR-16` | API | BR-16, 17 |
| UC-11-AC9 | `GET /api/chuyen/xe-kha-dung?tuyen_id&khoi_hanh` và `/tai-xe-kha-dung?tuyen_id&khoi_hanh[&xe_id]`: trả mọi xe / tài xế kèm `kha_dung` và danh sách lý do loại (mã BR + câu tiếng Việt); xe khả dụng xếp trước. Route cố định không bị hiểu là `{id}` (test gọi đúng route) | API | BR-11…19 |
| UC-11-AC10 | `GET /api/chuyen` lọc trạng thái, ngày khởi hành, tuyến, phân trang; `GET /api/chuyen/{id}` trả tổng quan (mã tuyến, biển số, tên tài xế, giờ, kết thúc dự kiến, trạng thái); không tồn tại → 404 | API | — |
| UC-11-AC11 | Phân quyền: Điều phối, Quản lý lập chuyến và xem danh sách khả dụng; Kế toán chỉ xem danh sách, chi tiết chuyến (POST và `*-kha-dung` → 403); Tài xế mọi thao tác → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-11-AC12 | Giao diện Điều phối (menu "Chuyến"): danh sách chuyến; hộp thoại lập chuyến: chọn tuyến, ngày giờ → hiện xe và tài xế khả dụng, cái bị loại hiện mờ kèm lý do; lưu thành công hiện mã chuyến; lỗi 422 hiện đủ các vi phạm kèm mã BR | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/chuyen.py` (mới: BR-11…19, 64, 65 dạng hàm thuần, dùng lại `kiem_br14_hang_gplx` của UC-04), `backend/app/modules/chuyen/{schemas,service,router}.py` (mới), `backend/app/main.py`; `frontend/src/api/chuyen.ts`, `frontend/src/pages/dieu-phoi/ChuyenDanhSach.tsx` (mới), `frontend/src/App.tsx` (menu "Chuyến"); `docs/api.md`. Không đụng `models/`, không thêm migration.
- Test đã viết: `backend/tests/unit/test_uc11_chuyen.py` (28 ca, theo TC-BR11…19, 64, 65 của `ca-test-br.md`), `backend/tests/api/test_uc11_lap_chuyen.py` (21 ca). Toàn bộ **315 passed** (30/10). `ruff`, `npm run lint`, `npm run build` sạch.
- Test chạy đồng thời (AC8) đã kiểm ngược: tạm bỏ khóa dòng thì test hỏng 3/3 lần; có khóa thì đạt.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/unit/test_uc11_chuyen.py tests/api/test_uc11_lap_chuyen.py`
- Cách tính: kết thúc dự kiến lúc lập theo công thức chạy rỗng (BR-64) vì chưa có đơn; UC-13 ghép đơn sẽ tính lại theo lịch trình BR-63 và kiểm cả chuyến (BR-67). Lấy lịch các chuyến khác bằng một truy vấn cho mọi xe (hoặc mọi tài xế), trong các tuần mà chuyến mới chạm tới.
- Review `ponytail-review` 30/10: Ship, sửa 2 mục – test phân quyền thêm xem chi tiết chuyến (Kế toán 200, Tài xế 403); gom hàm dựng tham số URL lặp ở 7 file `frontend/src/api/*.ts` thành `query` trong `api/goi.ts`.
- Lệch đặc tả: thêm `xe_id` cho `tai-xe-kha-dung`, mã lỗi `TUYEN_NGUNG`, `KHOI_HANH_DA_QUA`, `TAI_XE_NGUNG` – đã sửa `api.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-11-AC1 | Logic | `tests/unit/test_uc11_chuyen.py::test_uc11_ac1_* (3 ca)` | Đạt | 30/10/2026 |
| UC-11-AC2 | Logic | `test_uc11_ac2_* (7 ca)` | Đạt | 30/10/2026 |
| UC-11-AC3 | Logic | `test_uc11_ac3_tai_xe (6 ca)` | Đạt | 30/10/2026 |
| UC-11-AC4 | Logic | `test_uc11_ac4_trung_lich (5 ca)` + API `test_uc11_ac7_trung_lich_xe_va_tai_xe`, `test_uc11_ac7_chuyen_huy_khong_tinh` | Đạt | 30/10/2026 |
| UC-11-AC5 | Logic | `test_uc11_ac5_* (7 ca)` | Đạt | 30/10/2026 |
| UC-11-AC6 | API | `tests/api/test_uc11_lap_chuyen.py::test_uc11_ac6_lap_chuyen` | Đạt | 30/10/2026 |
| UC-11-AC7 | API | `test_uc11_ac7_* (11 ca)` | Đạt | 30/10/2026 |
| UC-11-AC8 | API | `test_uc11_ac8_lap_dong_thoi_chi_mot_thanh_cong` | Đạt | 30/10/2026 |
| UC-11-AC9 | API | `test_uc11_ac9_* (2 ca)` | Đạt | 30/10/2026 |
| UC-11-AC10 | API | `test_uc11_ac10_danh_sach_va_chi_tiet` | Đạt | 30/10/2026 |
| UC-11-AC11 | API | `test_uc11_ac11_* (5 ca)` | Đạt | 30/10/2026 |
| UC-11-AC12 | UI | `docs/test-evidence/UC-11/` | CHƯA KIỂM | |
