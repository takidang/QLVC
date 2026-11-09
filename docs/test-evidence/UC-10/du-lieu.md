# Dữ liệu thử giao diện UC-10 Sửa / hủy đơn (UC-10-AC12)

> Tài ghi 08/11/2026. Người thử chạy trên `dev` sau khi PR UC-10 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC12 trong `docs/stories/UC-10-sua-huy-don.md`.

## Chuẩn bị
- Đăng nhập `dieuphoi` / `demo12345` (quên thì `python -m app.tai_khoan_demo`).
- Dùng dữ liệu thử UC-13 / UC-15 đã có: tuyến T01, xe 5.000 kg, đơn Đ1 (TP.HCM → Cần Thơ 1.800 kg, hạn 14:00), Đ2 (Long An → Cần Thơ 1.200 kg, lấy 06:30–09:00, hạn 12:00), Đ4 (TP.HCM → Tiền Giang 800 kg 2 m³, hạn 18:00, cước 800.000), Đ8 (TP.HCM → Tiền Giang 300 kg) cho **ngày mai**. Thiếu thì tạo lại như `docs/test-evidence/UC-13/`.
- Lập chuyến T01 ngày mai 06:00, ghép Đ1, Đ2 (để Đ4, Đ8 ở Chờ ghép).

Menu **Đơn hàng**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Dòng Đ4 (Chờ ghép) bấm **Sửa** | Hộp "Sửa đơn DH-…": ô khách, nút lấy, nút giao mờ (không chọn được); các ô khác điền sẵn; dòng "Cước hiện tại 800.000 đ…" | `a-form-sua.png` | |
| b | Sửa kg 800 → 900 → **Lưu đơn** | Hộp đóng, báo "Đã sửa đơn …, cước 900.000 đ."; cột cước dòng Đ4 là 900.000 | `b-da-sua.png` | |
| c | Dòng Đ2 (Đã ghép) **Sửa**, hạn giao về **11:49** ngày mai → Lưu | Hộp vẫn mở, danh sách lỗi có "… (BR-06)" (ETA giao Đ2 11:50); đơn không đổi | `c-vi-pham.png` | |
| d | Dòng Đ8 bấm **Hủy** | Hộp "Hủy đơn …", nút **Xác nhận hủy** mờ khi ô lý do trống hoặc chỉ có khoảng trắng | `d-o-ly-do.png` | |
| e | Nhập "khách hủy" → **Xác nhận hủy** | Báo "Đã hủy đơn …"; Đ8 trạng thái "Hủy", không còn nút Sửa / Hủy | `e-da-huy.png` | |
| f | Dòng Đ1 (Đã ghép) **Hủy** | Hộp có dòng "Đơn đang ghép vào chuyến: hủy sẽ gỡ đơn khỏi chuyến trước"; hủy xong Đ1 "Hủy"; mở chuyến: lịch trình không còn Đ1 | `f-huy-dang-ghep.png` | |

Đơn ở chuyến đã chốt bị chặn (409) đã có test tự động (`test_uc10_ac5_*`, `test_uc10_ac8_chuyen_da_chot`); thử thêm trên giao diện nếu tiện: chốt chuyến rồi Sửa Đ2 → báo "… mở chốt chuyến trước …".
