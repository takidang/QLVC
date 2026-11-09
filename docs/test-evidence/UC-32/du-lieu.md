# Dữ liệu thử giao diện UC-32 Theo dõi chuyến (UC-32-AC11)

> Tài ghi 08/11/2026. Thử trên `dev` sau khi PR UC-32 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC11 trong `docs/stories/UC-32-theo-doi-chuyen.md`.

## Chuẩn bị (chuyến chạy **hôm nay**, như lần thử UC-19, 20)
- Điều phối: chuyến T01 hôm nay, ghép 3 đơn (A, B, C), chốt.
- Tài xế (`taixe`): Bắt đầu chuyến; quét lấy A đúng giờ; quét lấy B **trễ hơn 15 phút** so với ETA (đợi qua giờ hoặc lập chuyến giờ sớm hơn hiện tại để ETA đã qua); báo một sự cố nếu UC-33 đã có (chưa có thì bỏ ca e).
- Thêm một chuyến khác cùng tài xế khởi hành ngay trước giờ kết thúc dự kiến + độ trễ (để thấy cờ Chồng lịch) – tùy chọn.

Đăng nhập `dieuphoi`.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | **Chuyến** → chọn ngày hôm nay | Bảng có thêm cột Tiến độ ("2/6 điểm"), Đầy (%), Cờ ("Trễ"; "Chồng lịch" nếu có chuyến kế tiếp) | `a-bang-ngay.png` | |
| b | Mở chi tiết chuyến | Lịch trình có cột Giờ quét ("06:05 · đã lấy"), Trễ (số phút, đỏ khi > 15); khối Tiền (doanh thu, định mức, lương, tạm ứng); Dòng thời gian (lập, chốt, bắt đầu, các lượt quét) | `b-chi-tiet.png` | |
| c | (Nếu có chuyến kế tiếp bị chồng) | Dòng đỏ "Đang trễ: dự kiến xong …, chồng lên chuyến kế tiếp … (BR-73)" | `c-chong-lich.png` | |
| d | Bấm **Kết thúc do sự cố** → nhập lý do "hỏng hộp số", km cuối lớn hơn km bắt đầu → Kết thúc chuyến → OK | Hộp hỏi "… N đơn chưa giao sẽ thành Thất bại"; xong: nhãn Hoàn thành, dòng "Kết thúc do sự cố: hỏng hộp số", đơn chưa giao "Thất bại"; trang Đơn hàng thấy chúng trong thẻ đơn thất bại (UC-22) | `d-ket-thuc-su-co.png` | |
| e | (Khi UC-33 có) Khối Sự cố → nhập cách xử lý → **Đóng sự cố** | Sự cố "Đã đóng", hiện cách xử lý; cờ Sự cố trên bảng ngày mất | `e-dong-su-co.png` | |
