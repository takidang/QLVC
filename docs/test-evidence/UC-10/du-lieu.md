# Dữ liệu thử giao diện UC-10 Sửa / hủy đơn (UC-10-AC12)

> Tài ghi 08/11/2026. Người thử chạy trên `dev` sau khi PR UC-10 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC12 trong `docs/stories/UC-10-sua-huy-don.md`.

## Chuẩn bị
- Đăng nhập `dieuphoi` / `demo12345` (quên thì `python -m app.tai_khoan_demo`).
- Dùng dữ liệu thử UC-13 / UC-15 đã có: tuyến T01, xe 5.000 kg, đơn Đ1 (TP.HCM → Cần Thơ 1.800 kg, hạn 14:00), Đ2 (Long An → Cần Thơ 1.200 kg, lấy 06:30–09:00, hạn 12:00), Đ4 (TP.HCM → Tiền Giang 800 kg 2 m³, hạn 18:00, cước 800.000), Đ8 (TP.HCM → Tiền Giang 300 kg) cho **ngày mai**. Thiếu thì tạo lại như `docs/test-evidence/UC-13/`.
- Lập chuyến T01 ngày mai 06:00, ghép Đ1, Đ2 (để Đ4, Đ8 ở Chờ ghép).

Menu **Đơn hàng**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Dòng Đ4 (Chờ ghép) bấm **Sửa** | Hộp "Sửa đơn DH-…": ô khách, nút lấy, nút giao mờ (không chọn được); các ô khác điền sẵn; dòng "Cước hiện tại 800.000 đ…" | `a-form-sua.png` || Đạt (khách, nút lấy, nút giao mờ; "Cước hiện tại 800.000 đ") |
| b | Sửa kg 800 → 900 → **Lưu đơn** | Hộp đóng, báo "Đã sửa đơn …, cước 900.000 đ."; cột cước dòng Đ4 là 900.000 | `b-da-sua.png` || Đạt ("Đã sửa đơn …, cước 900.000 đ.") |
| c | Dòng Đ2 (Đã ghép) **Sửa**, hạn giao về **11:09** ngày mai → Lưu | Hộp vẫn mở, tự cuộn tới danh sách lỗi có "… (BR-06)" (chỉ ghép Đ1, Đ2 thì ETA giao Đ2 là 11:10; 11:50 là khi có thêm Đ4); đơn không đổi | `c-vi-pham.png` || Đạt (PR #34: "ETA giao 11:10 11/11 sau hạn giao 11:09 11/11 (BR-06)", hộp tự cuộn tới lỗi, đơn không đổi) |
| d | Dòng Đ8 bấm **Hủy** | Hộp "Hủy đơn …", nút **Xác nhận hủy** mờ khi ô lý do trống hoặc chỉ có khoảng trắng | `d-o-ly-do.png` || Đạt (nút mờ khi trống và khi chỉ có khoảng trắng) |
| e | Nhập "khách hủy" → **Xác nhận hủy** | Báo "Đã hủy đơn …"; Đ8 trạng thái "Hủy", không còn nút Sửa / Hủy | `e-da-huy.png` || Đạt ("Đã hủy đơn …", không còn Sửa / Hủy) |
| f | Dòng Đ1 (Đã ghép) **Hủy** | Hộp có dòng "Đơn đang ghép vào chuyến: hủy sẽ gỡ đơn khỏi chuyến trước"; hủy xong Đ1 "Hủy"; mở chuyến: lịch trình không còn Đ1 | `f-huy-dang-ghep.png` || Đạt (có dòng cảnh báo đang ghép; lịch trình không còn Đ1; ảnh thêm `f1-…`, `f2-…`) |
| g | Chốt chuyến (Đ2 còn ghép), quay lại **Đơn hàng** | Dòng Đ2 không có nút Sửa / Hủy, cột cuối ghi "Chuyến đã chốt" (BR-33, 34); đường kẻ dưới dòng đủ tới cột cuối | `g-chuyen-da-chot.png` || Đạt (PR #34: Đ2 không có nút, ghi "Chuyến đã chốt"; đường kẻ dưới đủ tới cột cuối) |

Đơn ở chuyến đã chốt bị chặn (409) đã có test tự động (`test_uc10_ac5_*`, `test_uc10_ac8_chuyen_da_chot`); thử thêm trên giao diện nếu tiện: chốt chuyến rồi Sửa Đ2 → báo "… mở chốt chuyến trước …".

## Kết quả thử (Kiệt, 10/11/2026)

Claude chạy trên Edge 1440 px theo đúng các bước trên, máy Kiệt. Ca a–f thử trên `dev` (e1dcb58); ca c, g thử lại trên code PR #34 (a2e5826). Dữ liệu: chuyến CH-261111-01 (T01 ngày mai 06:00), Đ2 DH-GAHXAZ.

- **7/7 ca đạt.**
- Thử thêm (dòng cuối ở trên): chốt chuyến rồi Sửa Đ2 trên `dev` (trước PR #34, khi nút Sửa còn hiện) → "Đơn đang ở chuyến CH-261111-01 không còn Đang lập (mở chốt chuyến trước), không sửa được (BR-33)" (`them-sua-khi-chuyen-da-chot.png`).
