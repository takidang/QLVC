# UC-05: Quản lý tuyến và nút

- **Trạng thái:** Đang làm – AC1–AC8 đạt, AC9 giao diện đang làm (Đã duyệt 24/10/2026 – Tài nhận UC-05 từ Kiệt, giao "làm luôn"; 5 quyết định ở mục Quyết định, Tài xem lại)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-05) · `docs/api.md` mục 2.2 · `docs/nghiep-vu.md` mục 2 (Tuyến), 2.1, mục 11 (tuyến T01) · ERD `docs/so-do.md` mục 5 (NUT, TUYEN, TUYEN_NUT)
- **Quy tắc nghiệp vụ liên quan:** BR-20 (cảnh báo thiếu điểm nghỉ), BR-66 (tuyến ≤ 10 giờ chạy), BR-60 (không xóa, chỉ `NGUNG`), BR-63 (ETA dùng `phut_tu_diem_dau`), BR-71 (định mức chốt vào chuyến lúc chốt), BR-57
- **Người làm:** Tài

## Mô tả ngắn
Điều phối viên quản lý **nút** (tỉnh/thành hoặc kho, có tỉnh để tra giá) và **tuyến** (danh sách nút có thứ tự, mỗi nút có phút và km tính từ điểm đầu, cờ điểm nghỉ; định mức dầu, cầu đường, bốc xếp và lương khoán mỗi chuyến). Tuyến là khung thời gian cho ETA (BR-63) và nguồn định mức cho tạm ứng, lãi dự kiến.

## Quyết định (24/10, Tài xem lại)
1. **Giới hạn BR-66 lấy từ CFG-07 (số giờ lái/ngày, mặc định 10)** thay vì ghi cứng 10: Quản lý đổi giới hạn giờ lái thì giới hạn tuyến đổi theo.
2. **BR-20 tính khoảng giữa các "điểm nghỉ" liên tiếp, coi nút đầu và nút cuối cũng là điểm nghỉ** (tài xế bắt đầu và kết thúc chuyến ở đó). Khoảng nào > giới hạn lái liên tục (CFG-07 số thứ ba, mặc định 4 giờ) → cảnh báo, vẫn cho lưu. Khoảng đúng bằng 4 giờ không cảnh báo.
3. **Tuyến hợp lệ khi:** ít nhất 1 nút (nội thành = tuyến 1 nút, giả định A3); nút đầu có phút = 0 và km = 0; phút **tăng hẳn** theo thứ tự (hai nút liên tiếp không cùng phút), km không giảm; một nút không xuất hiện hai lần trong tuyến.
4. **Không sửa danh sách nút của tuyến đã có chuyến** (khác `HUY`) – đổi nút làm đổi ETA của chuyến đã lập. Muốn đổi thì tạo tuyến mới và ngừng tuyến cũ. Sửa tên, định mức, trạng thái vẫn được (định mức chốt vào chuyến lúc chốt, BR-71).
5. **Thêm `PATCH /api/nut/{id}`** (api.md chỉ có GET, POST) để sửa tên/tọa độ nhập sai; không cho đổi tỉnh khi nút đã có đơn tham chiếu (tỉnh dùng tra giá đơn cũ). Đã sửa `api.md`.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-05-AC1 | Nút: thêm (tên, tỉnh, loại `TINH`/`KHO`, tọa độ không bắt buộc) → 201; tên/tỉnh chuẩn hóa như UC-07 (bỏ khoảng trắng, NFC); loại khác → 400; vĩ độ ngoài −90…90 → 400; danh sách tìm theo tên hoặc tỉnh | API | — |
| UC-05-AC2 | Sửa nút → 200; đổi tỉnh của nút đã có đơn → 422, không đổi | API | BR-48 |
| UC-05-AC3 | Kiểm cấu trúc tuyến (hàm thuần): tuyến T01 kịch bản mục 11 (HCM 0′, Long An 60′, Tiền Giang 120′ nghỉ, Vĩnh Long 210′, Cần Thơ 270′) hợp lệ; tuyến 1 nút hợp lệ; 0 nút, nút đầu phút ≠ 0 hoặc km ≠ 0, phút không tăng hẳn (bằng nhau), km giảm, nút lặp → lỗi kèm câu tiếng Việt | Logic | — |
| UC-05-AC4 | BR-66: phút nút cuối = 600 (10 giờ, biên) được; 601 → 422 `BR-66`; đổi CFG-07 thành `9/48/4` thì 600 → 422 | Logic | BR-66 |
| UC-05-AC5 | BR-20: T01 (nghỉ ở Tiền Giang 120′; khoảng 0→120, 120→270 đều ≤ 240′) không cảnh báo; tuyến 0′ → 300′ không có điểm nghỉ giữa → 1 cảnh báo nêu hai nút; khoảng đúng 240′ không cảnh báo, 241′ cảnh báo; vẫn lưu được | Logic | BR-20 |
| UC-05-AC6 | Thêm tuyến hợp lệ → 201, trả danh sách nút theo thứ tự (tên, tỉnh, phút, km, điểm nghỉ), tổng phút, tổng km, cảnh báo BR-20; mã tuyến trùng → 409; nút không tồn tại → 404; định mức, lương âm → 400 | API | BR-20, 66 |
| UC-05-AC7 | Sửa tuyến: đổi tên, định mức, trạng thái `HOAT_DONG`/`NGUNG` → 200; thay danh sách nút khi tuyến chưa có chuyến → 200 và kiểm lại BR-66, BR-20; tuyến đã có chuyến (khác `HUY`) → 409, nút không đổi; không có endpoint xóa (BR-60) | API | BR-60, 66 |
| UC-05-AC8 | Phân quyền: Điều phối, Quản lý xem/thêm/sửa nút và tuyến; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-05-AC9 | Giao diện Điều phối: trang Nút (danh sách, thêm/sửa); trang Tuyến (danh sách; hộp thoại thêm/sửa có bảng nút: chọn nút, phút, km, điểm nghỉ, thêm/bớt/đổi thứ tự dòng; hiện cảnh báo BR-20 sau khi lưu) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/tuyen.py` (cấu trúc tuyến, BR-66, BR-20), `backend/app/modules/danh_muc/nut/router.py`, `backend/app/modules/danh_muc/tuyen/{schemas,service,router}.py`, `backend/app/main.py`; `docs/api.md`.
- Test đã viết: `backend/tests/unit/test_uc05_tuyen.py` (15 ca), `backend/tests/api/test_uc05_tuyen_nut.py` (17 ca). Toàn bộ **199 passed** (24/10).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest`.
- Lệch đặc tả: 5 quyết định ở mục Quyết định; thêm `PATCH /api/nut/{id}` – đã sửa `api.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-05-AC1 | API | `test_uc05_ac1_them_nut` | Đạt | 24/10/2026 |
| UC-05-AC2 | API | `test_uc05_ac2_sua_nut_va_khoa_tinh_khi_co_don` | Đạt | 24/10/2026 |
| UC-05-AC3 | Logic | `tests/unit/test_uc05_tuyen.py::test_uc05_ac3_* (8 ca)` | Đạt | 24/10/2026 |
| UC-05-AC4 | Logic | `test_uc05_ac4_* (unit 2 + API 1)` | Đạt | 24/10/2026 |
| UC-05-AC5 | Logic | `tests/unit/test_uc05_tuyen.py::test_uc05_ac5_* (5 ca)` | Đạt | 24/10/2026 |
| UC-05-AC6 | API | `test_uc05_ac6_* (6 ca)` | Đạt | 24/10/2026 |
| UC-05-AC7 | API | `test_uc05_ac7_* (3 ca)` | Đạt | 24/10/2026 |
| UC-05-AC8 | API | `test_uc05_ac8_* (5 ca)` | Đạt | 24/10/2026 |
| UC-05-AC9 | UI | `docs/test-evidence/UC-05/` | CHƯA KIỂM | |
