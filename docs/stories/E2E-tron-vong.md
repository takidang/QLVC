# E2E: Chạy trọn vòng từ tạo đơn đến quyết toán

- **Trạng thái:** Hoàn thành 19/11/2026 – 6/6 AC (Tài duyệt story 19/11, kèm 6 góp ý đã sửa)
- **Tác nhân:** Điều phối viên, Tài xế, Kế toán, Quản lý (mỗi bước dùng đúng tài khoản của vai trò đó)
- **Đặc tả:** `docs/kien-truc.md` (mục kiểm thử: E2E luồng chính), `docs/nghiep-vu.md` mục 11 (kịch bản), UC-08, 11, 13, 15, 18, 19, 20, 21, 23, 24, 25, 26
- **Quy tắc nghiệp vụ liên quan:** BR-28 (kết thúc khi mọi đơn có kết quả), BR-29 (khóa sổ), BR-38 (quét đơn không thuộc chuyến), BR-41, 42 (giao / giao không được), BR-53 (tạm ứng ≤ định mức), BR-55 (duyệt chi phí, chênh lệch tạm ứng), BR-56 (phải thu), BR-57, 58 (phân quyền, chống IDOR)
- **Người làm:** Kiệt

## Mô tả ngắn
Một test tự động đi hết vòng nghiệp vụ chính bằng API thật, như người dùng làm trên giao diện: Điều phối tạo đơn, lập chuyến, ghép, chốt; Kế toán cấp tạm ứng; Tài xế bắt đầu, quét lấy, giao một đơn, báo giao không được một đơn, ghi chi phí, kết thúc; Kế toán duyệt chi phí, quyết toán, thu nợ; Quản lý xem báo cáo lãi lỗ. Mỗi bước kiểm trạng thái và số tiền. Bù cho việc từng UC chỉ có test riêng lẻ: test này bắt lỗi khi các UC ghép với nhau.

## Quyết định (Tài duyệt 19/11/2026)
1. **Mức API (pytest), chạy trong CI** như các test khác: `backend/tests/e2e/test_tron_vong.py`, dùng CSDL test `*_test`, không cần trình duyệt, không thêm gói, không thêm migration. Mỗi vai trò một `TestClient` đăng nhập riêng.
2. **Danh mục dùng lại fixture `kb` của UC-13** (nút, tuyến T01, xe X1, tài xế An, Dũng, khách Cty A) + 2 dòng bảng giá; đặt mật khẩu cho 2 tài xế của `kb`. Từ đơn trở đi gọi API thật bằng đúng vai trò. Ảnh, chữ ký dùng `JPG`, `PNG` giả của test UC-19 và đổi `luu_tru.THU_MUC` sang thư mục tạm (không ghi vào `backend/uploads/`).
3. **Thời gian theo giờ Việt Nam** (`GIO_VN`): khởi hành = bây giờ + 10 phút; nếu giờ đó sang ngày hôm sau (chạy gần nửa đêm VN, CI chạy giờ UTC) thì `pytest.skip` kèm lý do, vì BR-26 chỉ cho bắt đầu trong ngày khởi hành. Không để test lúc đỏ lúc xanh.
4. **Một hàm test dài**, mỗi assert ghi bước ("bước 9: A DA_GIAO") để fail là biết chỗ hỏng.
5. **Phần giao diện** (bấm thật trên trình duyệt) không nằm trong story này: giao diện đã thử tay từng màn (PR #60, #61). Muốn E2E trình duyệt thì làm story riêng sau khi chốt công cụ (Playwright cần cài gói, phải hỏi trước theo CLAUDE.md).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| E2E-AC1 | Trạng thái chuyến đi đúng `LAP → DA_CHOT → DANG_CHAY → HOAN_THANH → DA_QUYET_TOAN`; đơn A `CHO_GHEP → DA_GHEP → DA_LAY → DA_GIAO`, đơn B `CHO_GHEP → DA_GHEP → DA_LAY → THAT_BAI`; mỗi bước gọi API của đúng vai trò và nhận 2xx | API | UC-11…24 |
| E2E-AC2 | Giao đơn A kèm ảnh, chữ ký, tên người nhận được; đơn B giao không được kèm lý do phía khách + ảnh được; kết thúc chuyến khi còn đơn chưa có kết quả → 422 `BR-28`, `chi_tiet` liệt kê đúng mã đơn còn thiếu | API | BR-28, 41, 42 |
| E2E-AC3 | Tiền khớp từ đầu đến cuối: cước đơn = giá lúc tạo; tạm ứng vượt định mức → 422 `BR-53`, cấp ≤ định mức được; dầu duyệt giảm tiền thiếu lý do → 422 `BR-55`, có lý do được; bảng quyết toán: doanh thu = cước A (B thất bại không tính), lãi = doanh thu − chi phí duyệt − lương; **chênh lệch tạm ứng = tạm ứng − chi phí đã duyệt** (nghiep-vu mục 11 bước 7): dương thì tài xế nộp lại, âm thì công ty trả thêm, ghi nhận theo BR-55 rồi mới quyết toán; kiểm cả dấu (gợi ý `TAI_XE_DA_NOP`, gửi sai dấu → 422 `BR-55`) lẫn số tiền | API | BR-53, 55, UC-24 |
| E2E-AC4 | Công nợ: sau khi giao A sinh đúng một khoản phải thu bằng cước A cho khách của A; B không sinh phải thu; Kế toán đánh dấu đã thu → khoản `DA_THU` gắn phiếu thu, đơn giữ `DA_GIAO` | API | BR-56 |
| E2E-AC5 | Sau quyết toán: báo cáo lãi lỗ theo chuyến tháng này có chuyến với đúng lãi ở AC3; duyệt lại chi phí của chuyến → 409 `BR-29` | API | BR-29, UC-26 |
| E2E-AC6 | Trong luồng: tài xế khác quét đơn của chuyến này → 403 `BR-38` ("Đơn không thuộc chuyến của bạn"); tài xế khác xem chuyến (`GET /api/toi/chuyen/{id}`) → 404 `KHONG_TIM_THAY` (BR-58, không lộ chuyến có tồn tại); Tài xế gọi quyết toán → 403 `KHONG_DU_QUYEN` (BR-57) | API | BR-38, 57, 58 |

## Ghi chú triển khai
- File đã đổi: `backend/tests/e2e/__init__.py`, `backend/tests/e2e/test_tron_vong.py` (mới). Không đổi code ứng dụng, không thêm gói, không thêm migration.
- Kịch bản số: A TP.HCM → Cần Thơ 1.800 kg 6 m³ (cước 2.997.000), B TP.HCM → Tiền Giang 800 kg 2 m³ (800.000); định mức T01 1.000.000, tạm ứng 800.000; dầu khai 600.000 duyệt 580.000, cầu đường 200.000; lương 600.000 → lãi 1.617.000, chênh lệch tạm ứng +20.000 (tài xế nộp lại).
- Test đã viết: `test_e2e_tron_vong` (18 bước, mỗi assert ghi bước).
- Đã thử làm hỏng 3 chỗ trong code (bỏ kiểm BR-28 khi kết thúc chuyến; doanh thu quyết toán cộng cả đơn thất bại; phải thu lệch 1 đồng) → lần nào test cũng đỏ, rồi trả code lại.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/e2e -q`
- Lệch đặc tả: không.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| E2E-AC1 | API | `test_e2e_tron_vong` bước 1–4, 6, 7, 9, 12, 15 | Đạt | 19/11/2026 |
| E2E-AC2 | API | `test_e2e_tron_vong` bước 8, 9 | Đạt | 19/11/2026 |
| E2E-AC3 | API | `test_e2e_tron_vong` bước 1, 5, 13, 14, 15 | Đạt | 19/11/2026 |
| E2E-AC4 | API | `test_e2e_tron_vong` bước 10, 18 | Đạt | 19/11/2026 |
| E2E-AC5 | API | `test_e2e_tron_vong` bước 16, 17 | Đạt | 19/11/2026 |
| E2E-AC6 | API | `test_e2e_tron_vong` bước 6, 7, 15 | Đạt | 19/11/2026 |
