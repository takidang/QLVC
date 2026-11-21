# Dữ liệu thử giao diện UC-36 Tìm kiếm chung

## Chuẩn bị

Máy Kiệt 12/11/2026, backend `dev` (93ab7eb), giao diện nhánh `tai/thu-giao-dien-v2` (30949bf), dữ liệu demo (`seed.demo` + `--ngay-moi`), mật khẩu `demo12345`. Ảnh chụp Edge 1440 px.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `dieuphoi` → ô tìm trên thanh đầu gõ `51C` | Kết quả gộp theo nhóm: Chuyến "5 / 23", Xe 4; mỗi nhóm tối đa 5 dòng, dòng "Chỉ hiện 5 kết quả đầu mỗi nhóm" | `a-tim-chung-51C.png` | Đạt |
| b | Gõ `DH-`; bấm một kết quả | Nhóm Đơn; bấm mở đúng trang đơn / chuyến | – | Đạt (Kiệt thử tay) |
