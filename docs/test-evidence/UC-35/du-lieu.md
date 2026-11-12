# Dữ liệu thử giao diện UC-35 Đổi mật khẩu

## Chuẩn bị

Máy Kiệt 12/11/2026, backend `dev` (93ab7eb), giao diện nhánh `tai/thu-giao-dien-v2` (30949bf), dữ liệu demo (`seed.demo` + `--ngay-moi`), mật khẩu `demo12345`. Ảnh chụp Edge 1440 px.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `dieuphoi` → ô tròn tài khoản → **Đổi mật khẩu** → mật khẩu hiện tại sai, mật khẩu mới + nhập lại → Lưu | Báo đỏ "Mật khẩu hiện tại không đúng", không đổi | `a-sai-mat-khau-cu.png` | Đạt |
| b | Nhập đúng mật khẩu hiện tại, mật khẩu mới → Lưu; đăng xuất, đăng nhập bằng mật khẩu mới; đổi lại về `demo12345` | Đổi được, đăng nhập bằng mật khẩu mới được | – | Đạt (Kiệt thử tay; đã đổi lại `demo12345`, CSDL kiểm cả 9 tài khoản còn `demo12345`, không tài khoản nào bị khóa) |
