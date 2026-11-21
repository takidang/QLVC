# Dữ liệu thử giao diện UC-38 Tổng quan hôm nay

## Chuẩn bị

Máy Kiệt 12/11/2026, backend `dev` (93ab7eb), giao diện nhánh `tai/thu-giao-dien-v2` (30949bf), dữ liệu demo (`seed.demo` + `--ngay-moi`), mật khẩu `demo12345`. Ảnh chụp Edge 1440 px.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `ketoan` → **Tổng quan** | Khối Hôm nay: số chuyến theo trạng thái, đơn giao / thất bại, % đúng giờ, doanh thu dự kiến; biểu đồ lãi lỗ (UC-26), hiệu suất xe (UC-34) | `a-tong-quan-ke-toan.png` | Đạt |
| b | `quanly` → **Tổng quan**; đổi ngày | Như trên; đổi ngày thì số đổi theo | `b-tong-quan-quan-ly.png` | Đạt |
