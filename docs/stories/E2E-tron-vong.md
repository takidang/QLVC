# E2E: Chạy trọn vòng từ tạo đơn đến quyết toán

- **Trạng thái:** Nháp (chờ Kiệt duyệt)
- **Tác nhân:** Điều phối viên, Tài xế, Kế toán (mỗi bước dùng đúng tài khoản của vai trò đó)
- **Đặc tả:** `docs/kien-truc.md` (mục kiểm thử: E2E luồng chính), `docs/nghiep-vu.md` mục 11 (kịch bản), UC-08, 11, 13, 15, 18, 19, 20, 21, 23, 24, 25, 26
- **Quy tắc nghiệp vụ liên quan:** BR-29 (khóa sổ sau quyết toán), BR-41 (giao cần ảnh + chữ ký + tên), BR-42 (giao thất bại), BR-56 (sinh phải thu), BR-58 (tài xế chỉ thao tác chuyến của mình), BR-53 (tạm ứng ≤ định mức)
- **Người làm:** Kiệt

## Mô tả ngắn
Một test tự động đi hết vòng nghiệp vụ chính bằng API thật, như người dùng làm trên giao diện: Điều phối tạo đơn, lập chuyến, ghép, chốt; Kế toán cấp tạm ứng; Tài xế bắt đầu, quét lấy, giao một đơn, báo giao không được một đơn, ghi chi phí, kết thúc; Kế toán duyệt chi phí, quyết toán, thu nợ. Mỗi bước kiểm trạng thái và số tiền. Bù cho việc từng UC chỉ có test riêng lẻ: test này bắt lỗi khi các UC ghép với nhau.

## Quyết định (Claude đề xuất, chờ Kiệt duyệt)
1. **Mức API (pytest), chạy trong CI** như các test khác: `backend/tests/e2e/test_tron_vong.py`, dùng CSDL test `*_test`, không cần trình duyệt, không thêm gói. Mỗi vai trò một client đăng nhập riêng (không dùng fixture `dang_nhap_voi` đổi vai trò giữa chừng) để giống người dùng thật.
2. **Dữ liệu tự tạo trong test** (khách, nút, tuyến, xe, tài xế, bảng giá qua API Quản lý / Điều phối), không phụ thuộc `seed.demo`.
3. **Thời gian:** lập chuyến khởi hành hôm nay + vài giờ; bắt đầu, quét, kết thúc gọi tuần tự, không giả đồng hồ (luồng không phụ thuộc giờ trừ BR-26 "bắt đầu đúng ngày khởi hành").
4. **Phần giao diện** (bấm thật trên trình duyệt) **không nằm trong story này**: giao diện đã thử tay từng màn (PR #60, #61). Nếu nhóm muốn E2E trình duyệt thì làm story riêng sau khi chốt công cụ (Playwright cần cài gói, phải hỏi trước theo CLAUDE.md).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| E2E-AC1 | Trạng thái chuyến đi đúng `LAP → DA_CHOT → DANG_CHAY → HOAN_THANH → DA_QUYET_TOAN`; đơn A `CHO_GHEP → DA_GHEP → DA_LAY → DA_GIAO`, đơn B `CHO_GHEP → DA_GHEP → DA_LAY → THAT_BAI`; mỗi bước gọi API của đúng vai trò và nhận 2xx | API | UC-11…24 |
| E2E-AC2 | Giao đơn A kèm ảnh, chữ ký, tên người nhận được; đơn B giao không được kèm lý do phía khách + ảnh được; kết thúc chuyến chỉ được khi mọi điểm đã xong (trước đó bị chặn) | API | BR-41, 42 |
| E2E-AC3 | Tiền khớp từ đầu đến cuối: cước đơn = giá lúc tạo; tạm ứng cấp ≤ định mức; chi phí khai được duyệt (một khoản giảm tiền có lý do); bảng quyết toán: doanh thu = cước A (B thất bại không tính), lãi = doanh thu − chi phí duyệt − lương, chênh lệch tạm ứng đúng dấu | API | BR-53, UC-24 |
| E2E-AC4 | Công nợ: sau khi giao A sinh đúng một khoản phải thu bằng cước A cho khách của A; Kế toán đánh dấu đã thu → khoản sang đã thu, có phiếu thu; B không sinh phải thu | API | BR-56 |
| E2E-AC5 | Sau quyết toán: báo cáo lãi lỗ tháng có chuyến này với đúng lãi ở AC3; sửa / duyệt lại chi phí của chuyến bị chặn | API | BR-29, UC-26 |
| E2E-AC6 | Trong luồng: tài xế khác quét đơn của chuyến này → 403; Tài xế gọi API quyết toán → 403 | API | BR-58, BR-57 |

## Ghi chú triển khai
- File đã đổi:
- Test đã viết:
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/e2e -q`
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa:

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| E2E-AC1 | API | | CHƯA KIỂM | |
| E2E-AC2 | API | | CHƯA KIỂM | |
| E2E-AC3 | API | | CHƯA KIỂM | |
| E2E-AC4 | API | | CHƯA KIỂM | |
| E2E-AC5 | API | | CHƯA KIỂM | |
| E2E-AC6 | API | | CHƯA KIỂM | |
