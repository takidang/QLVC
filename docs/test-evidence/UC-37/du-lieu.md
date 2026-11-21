# Dữ liệu thử giao diện UC-37 Thông báo theo vai trò

## Chuẩn bị

Máy Kiệt 12/11/2026, backend `dev` (93ab7eb), giao diện nhánh `tai/thu-giao-dien-v2` (30949bf), dữ liệu demo (`seed.demo` + `--ngay-moi`), mật khẩu `demo12345`. Ảnh chụp Edge 1440 px.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `dieuphoi` → chuông | Đơn chờ ghép sắp quá hạn, chuyến trễ / chồng lịch, sự cố mở, đơn thất bại; mới trước; số trên chuông | `a-chuong-dieu-phoi.png` | Đạt (16 thông báo) |
| b | `ketoan` → chuông | Chuyến chờ quyết toán, khoản chi chờ duyệt, tạm ứng chưa quyết toán | `b-chuong-ke-toan.png` | Đạt (6 thông báo: CH-261112-05 chờ quyết toán, 1 khoản chi chờ duyệt 50.000, tạm ứng 1.160.000…) |
| c | `taixe04` → chuông | Sự cố của mình đã được xử lý kèm cách xử lý; khoản chi bị điều chỉnh | `c-chuong-tai-xe.png` | Đạt ("Sự cố hỏng xe – chuyến CH-261112-04 đã được xử lý") |
| d | `quanly` → chuông | Như Điều phối | `d-chuong-quan-ly.png` | Đạt |
| e | Bấm một thông báo | Mở đúng chuyến / đơn | – | Đạt (Kiệt thử tay) |

Lỗi đã báo Tài: trên điện thoại khung chuông tràn ra ngoài mép trái (mất chữ đầu mỗi dòng).
