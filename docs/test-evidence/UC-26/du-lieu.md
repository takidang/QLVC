# Dữ liệu thử giao diện UC-26 Báo cáo lãi lỗ (UC-26-AC8)

> Kiệt thử 18/11/2026 (Claude chạy trên Edge 1440 px, máy Kiệt). Backend `dev` (1900ad3), giao diện v3 `tai/thu-giao-dien-v3` (7348c6c), CSDL `qlvc_demo` (dữ liệu demo 10–18/11).

Đăng nhập `quanly` → **Tổng quan**. Giao diện v3 đặt lãi lỗ ở trang Tổng quan, không có menu "Báo cáo lãi lỗ" riêng.

| Ca | Làm gì | Kết quả đúng (AC8) | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Mở Tổng quan, tháng 11/2026 | Số liệu tháng chỉ tính chuyến đã quyết toán; có số chuyến chờ quyết toán; cảnh báo thiếu chi phí cố định | `a-tong-quan-lai-lo.png` | Đạt: 18 chuyến đã quyết toán, doanh thu 52.201.000, lãi 23.606.000; "6 chuyến đã chạy xong nhưng chưa quyết toán"; "Chưa nhập chi phí cố định tháng 11/2026: 51C-201.11, …, 51D-305.55" |
| b | Lãi theo xe | Lãi âm tô đỏ | `a-tong-quan-lai-lo.png` | Đạt: 51D-305.55 "−450 k" màu cam đỏ (chuyến CH-261118-01 vừa quyết toán lỗ) |
| c | Lãi theo tháng → **Xem dạng bảng** | Bảng theo tháng, có dòng tổng | `b-lai-theo-thang-dang-bang.png` | Một phần: bảng 6 tháng (06–11/2026) đủ cột Chuyến, Doanh thu, Chi phí, Lương, Cố định, Lãi; **không có dòng tổng** trong bảng (tổng tháng đang chọn nằm ở thẻ phía trên) |
| d | Đổi tháng sang 10/2026 | Số liệu, biểu đồ, bảng đổi theo tháng | `c-chon-thang-10.png` | Đạt: 0 chuyến đã quyết toán, "Tháng này chưa có chuyến nào được quyết toán" (dữ liệu demo chỉ có tháng 11) |
| e | Xem theo Chuyến / Xe / Tháng | Chọn khoảng tháng và kiểu xem thì bảng đổi đúng | | **Không có**: chỉ có theo tháng (6 tháng tới tháng chọn) và theo xe (tháng chọn); không có kiểu xem theo chuyến, không chọn được khoảng tháng tùy ý |

## Kết luận lần 1 (trước khi sửa)
- Đạt: số liệu chỉ từ chuyến đã quyết toán, số chuyến chờ quyết toán, cảnh báo thiếu chi phí cố định, lãi âm tô màu, đổi tháng.
- Lệch AC8: không có menu riêng, không xem theo chuyến, không chọn khoảng tháng, bảng không có dòng tổng. Cần Tài quyết: bổ sung giao diện, hoặc sửa AC8 theo cách làm ở Tổng quan (ghi lý do trong story).

## Thử lại sau khi Tài sửa (18/11/2026, v3 `0cef9cd`)

Tài bổ sung khối **"Bảng lãi lỗ"** cuối trang Tổng quan (không sửa AC). Ảnh chụp theo khung nhìn (1440 × 1700) ở khối này.

| Ca | Làm gì | Ảnh | Kết quả |
|---|---|---|---|
| h | Từ 09/2026 đến 11/2026, xem **Chuyến** | `d-bang-lai-lo-theo-chuyen.png` | Đạt: 18 chuyến đã quyết toán (cột Chuyến, Ngày, Xe, Doanh thu, Chi phí, Lương, Lãi); dòng **Tổng (18 chuyến)** 52.201.000 / 19.295.000 / 9.300.000 / 23.606.000; CH-261118-01 lãi −450.000 tô màu; "9 chuyến chờ quyết toán, chưa vào bảng." |
| i | Xem **Xe** | `e-bang-lai-lo-theo-xe.png` | Đạt: 5 xe, có cột Cố định; tổng khớp; 51D-305.55 −450.000 tô màu; thêm "Chưa nhập chi phí cố định: 51C-201.11 (11/2026), …" |
| j | Xem **Tháng** | `f-bang-lai-lo-theo-thang.png` | Đạt: 09, 10, 11/2026 + dòng tổng, khớp với kiểu xem Chuyến, Xe |
| k | Khoảng 10/2026 – 10/2026 (không có chuyến), xem Tháng rồi Chuyến | `g-khoang-thang-10-rong.png` | Đạt: bảng rỗng, "Tổng (0 chuyến)" toàn 0, không lỗi; đổi qua lại 3 cách xem không sập (không có lỗi trong console) |

**Kết luận: AC8 đạt** (menu riêng không có, báo cáo nằm ở trang Tổng quan của Quản lý; các ý còn lại của AC8 đủ).
