# UC-08: Tạo đơn hàng

- **Trạng thái:** Hoàn thành (25/10/2026, giao diện Kiệt thử) (Đã duyệt 24/10/2026 – Tài chọn: mã đơn ngẫu nhiên; phiếu QR làm cùng UC-19; giao diện làm sau UC-05)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán xem đơn
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-08) · `docs/api.md` mục 2.3 · `docs/nghiep-vu.md` mục 2.1 (công thức), mục 11 (kịch bản Đ1…Đ8)
- **Quy tắc nghiệp vụ liên quan:** BR-31 (đơn hợp lệ), BR-32 (chốt cước ngay, lưu bản sao giá), BR-46, 47, 48 (cước), BR-30 (lịch sử trạng thái), BR-59 (SĐT dùng tra cứu), BR-57
- **Người làm:** Tài

## Mô tả ngắn
Điều phối viên tạo đơn cho khách: hàng (kg, m³, số kiện), điểm lấy và điểm giao (thuộc một nút), hạn giao, khung giờ lấy nếu có. Hệ thống tính cước theo bảng giá của cặp tỉnh, **chốt cước ngay** kèm bản sao giá, sinh mã đơn ngẫu nhiên, đơn ở `CHO_GHEP`.

## Phạm vi story này
- **Làm:** domain tính cước, `POST /api/don/tinh-cuoc`, `POST /api/don`, `GET /api/don`, `GET /api/don/{id}`, test theo kịch bản mục 11.
- **Để sau:** giao diện tạo đơn (cần chọn nút – UC-05, Tài làm tiếp); phiếu in QR `GET /api/don/{id}/phieu` (làm cùng UC-19 để chọn thư viện QR một lần); bản đồ chấm tọa độ (cần thư viện bản đồ – hỏi khi làm giao diện). Tọa độ lấy/giao vì vậy **không bắt buộc** ở API (BR-44 đã bỏ, tọa độ chỉ để dành).

## Quyết định (24/10)
1. **Mã đơn ngẫu nhiên** `DH-` + 6 ký tự từ bảng 32 ký tự bỏ chữ dễ nhầm (không có 0, O, 1, I): không đoán được mã đơn của người khác để dò tra cứu (BR-59). Kịch bản mục 11 dùng "DH-0012" chỉ là tên minh họa.
2. **Thời gian gửi lên phải có múi giờ** (ISO 8601, ví dụ `2026-10-20T14:00:00+07:00`); thiếu múi giờ → 400. Ngày tra giá là ngày tạo đơn theo giờ Việt Nam.
3. **"Điểm lấy ≠ điểm giao" (BR-31) so địa chỉ**, không so nút: tuyến nội thành chỉ có một nút (giả định A3) nên lấy và giao có thể cùng nút.
4. Vi phạm kiểu dữ liệu (kg ≤ 0, số kiện < 1…) → 400; vi phạm giữa các trường của BR-31 (địa chỉ trùng, hạn giao đã qua, khung giờ ngược) → 422 mã `BR-31`, liệt kê mọi vi phạm.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-08-AC1 | Tính cước đúng kịch bản mục 11 (CFG-01 = 333, CFG-06 = 1.000): Đ1 1.800 kg, 6 m³, 1.500 đ/kg → KL tính cước 1.998, cước 2.997.000; Đ2 1.200 kg, 3 m³ → 1.200, 1.440.000; Đ3 1.500 kg, 5 m³, 1.300 đ/kg → 2.164.500 làm tròn **lên** 2.165.000; Đ8 300 kg, 1 m³, 1.000 đ/kg → 333 kg, 333.000; đơn nhỏ 10 kg dưới cước tối thiểu 50.000 → 50.000; số tiền đúng bội 1.000 thì không làm tròn thêm; m³ thập phân 1,5 → quy đổi 499,5 kg | Logic | BR-46, 47, 48 |
| UC-08-AC2 | `POST /api/don/tinh-cuoc` trả KL quy đổi, KL tính cước, đơn giá, cước tối thiểu, cước; không lưu gì vào CSDL; cặp tỉnh chưa có giá → 422 `BR-48` | API | BR-46…48 |
| UC-08-AC3 | Tạo đơn hợp lệ → 201, trạng thái `CHO_GHEP`, `cuoc_tinh` đúng AC1; lưu bản sao `don_gia_chot`, `cuoc_toi_thieu_chot`, `he_so_quy_doi_chot` (= CFG-01), `lam_tron_chot` (= CFG-06); mã đơn dạng `DH-XXXXXX` chỉ gồm ký tự trong bảng 32 ký tự; ghi một dòng lịch sử trạng thái (rỗng → `CHO_GHEP`, người tạo) | API | BR-30, 32 |
| UC-08-AC4 | BR-31 chặn và không lưu: kg 0, m³ 0, số kiện 0 → 400 (biên: 0,01 kg, 0,01 m³, 1 kiện được); địa chỉ lấy = địa chỉ giao (không phân biệt hoa thường, khoảng trắng) → 422; hạn giao ≤ thời điểm tạo → 422; khung giờ lấy chỉ có một đầu, hoặc `từ ≥ đến`, hoặc hạn giao ≤ `từ` → 422; không có khung giờ lấy → được (cả ngày) | API | BR-31 |
| UC-08-AC5 | Khách không tồn tại hoặc nút không tồn tại → 404; khách `NGUNG` → 422, không tạo đơn | API | BR-60 |
| UC-08-AC6 | Cặp (tỉnh nút lấy, tỉnh nút giao) chưa có giá có hiệu lực hôm nay → 422 `BR-48`, không tạo đơn (Đ7 Cần Thơ → Cà Mau) | API | BR-48 |
| UC-08-AC7 | Đổi bảng giá hoặc CFG-01, CFG-06 sau khi tạo đơn → đơn giữ nguyên cước và bản sao giá | API | BR-32 |
| UC-08-AC8 | SĐT lấy, SĐT nhận chuẩn hóa như UC-06 ("0909 123.456" → "0909123456"); thời gian không có múi giờ → 400 | API | BR-59 |
| UC-08-AC9 | Danh sách đơn: lọc trạng thái, khách, tìm theo mã đơn; phân trang; chi tiết đơn kèm tên khách, tỉnh lấy, tỉnh giao | API | — |
| UC-08-AC10 | Phân quyền: Điều phối, Quản lý tạo và xem; Kế toán chỉ xem (POST 403); Tài xế mọi thao tác 403; chưa đăng nhập 401; đơn không tồn tại 404 | API | BR-57 |
| UC-08-AC11 | Giao diện tạo đơn: chọn khách, chọn nút lấy/giao, nhập hàng, hạn giao, khung giờ; hiện cước tạm tính trước khi lưu; báo lỗi tiếng Việt | UI | NFR-USA-02 – **làm sau UC-05** |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/cuoc.py` (BR-31, 46–48), `backend/app/modules/don/{schemas,service,router}.py`, `backend/app/main.py`.
- Test đã viết: `backend/tests/unit/test_uc08_cuoc.py` (14 ca, kịch bản Đ1, Đ2, Đ3, Đ8), `backend/tests/api/test_uc08_tao_don.py` (27 ca). Toàn bộ **164 passed** (24/10).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest`.
- Review `ponytail-review` 24/10 (UC-06, 07, 08): (1) chữ tiếng Việt đưa về Unicode dựng sẵn NFC trong `ChuBatBuoc` và `tra_gia` – gõ kiểu tổ hợp (Unikey tổ hợp, macOS) vẫn khớp giá, chặn trùng, so địa chỉ BR-31; (2) vĩ độ giới hạn −90…90, kinh độ −180…180. Thêm 3 test (`test_uc07_ac3_tinh_go_kieu_to_hop_van_khop`, `test_uc08_review_*`). Tổng 167 passed.
- Sau khi Kiệt thử (25/10): từng vi phạm BR-31 trên giao diện hiện kèm mã "(BR-31)" (`kemMaBr`, NFR-USA-02).
- Lệch đặc tả: 4 quyết định ở mục Quyết định. `bao_gia()` dùng chung cho tính thử và tạo đơn; UC-10 sửa đơn sẽ tính lại từ bản sao `_chot` (BR-33).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-08-AC1 | Logic | `tests/unit/test_uc08_cuoc.py::test_uc08_ac1_* (7 ca)` | Đạt | 24/10/2026 |
| UC-08-AC2 | API | `test_uc08_ac2_* (2 ca)` | Đạt | 24/10/2026 |
| UC-08-AC3 | API | `test_uc08_ac3_* (2 ca)` | Đạt | 24/10/2026 |
| UC-08-AC4 | API | `test_uc08_ac4_* (unit 8 + API 13 ca)` | Đạt | 24/10/2026 |
| UC-08-AC5 | API | `test_uc08_ac5_khach_va_nut` | Đạt | 24/10/2026 |
| UC-08-AC6 | API | `test_uc08_ac6_chua_co_gia_khong_tao` | Đạt | 24/10/2026 |
| UC-08-AC7 | API | `test_uc08_ac7_doi_gia_khong_anh_huong_don_cu` | Đạt | 24/10/2026 |
| UC-08-AC8 | API | `test_uc08_ac8_sdt_va_mui_gio` | Đạt | 24/10/2026 |
| UC-08-AC9 | API | `test_uc08_ac9_danh_sach_va_chi_tiet` | Đạt | 24/10/2026 |
| UC-08-AC10 | API | `test_uc08_ac10_* (5 ca)` | Đạt | 24/10/2026 |
| UC-08-AC11 | UI | `docs/test-evidence/UC-08/e-tao-don.png` (cước 2.997.000 đ; đơn lưu được – 201 trong log), `f-trung-dia-chi.png` (BR-31), `e-chua-co-tuyen.png`, `e-chua-co-tuyen-nguoc-lai.png` (chưa có bảng giá, nút Lưu khóa) – Kiệt thử, Tài xác nhận 25/10 | Đạt | 25/10/2026 |
