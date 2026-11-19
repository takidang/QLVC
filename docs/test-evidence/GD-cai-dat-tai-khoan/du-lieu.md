# Dữ liệu thử giao diện GD: Menu tài khoản gọn, trang Tài khoản và Cài đặt

> Kiệt thử 19/11/2026 (Claude chạy trên Edge, máy Kiệt). Nhánh `tai/cai-dat-tai-khoan` (a7ab64e), backend `dev` + UC-30, CSDL `qlvc_demo`. Xóa `localStorage` trước khi thử.

| AC | Làm gì | Ảnh | Kết quả |
|---|---|---|---|
| GD-AC1 | `dieuphoi`, `quanly` bấm vòng tên tắt; bấm ra ngoài; mở lại rồi Esc; bấm link Cài đặt | `a-menu-dieuphoi.png`, `a-menu-quanly.png` | Đạt: đầu "Điều phối Demo / Điều phối viên", link Tài khoản (`/tai-khoan`), Cài đặt (`/cai-dat`), nút Đăng xuất; Quản lý có thêm Cấu hình hệ thống (`/quan-ly/cau-hinh`). Bấm ra ngoài, Esc, bấm link đều đóng menu; link chuyển đúng trang |
| GD-AC2 | `ketoan` → `/tai-khoan`: mật khẩu mới "abc"; nhập lại lệch; mật khẩu cũ sai; đổi đúng sang demo99999, đăng nhập lại, đổi về demo12345 | `h-tai-khoan-mk-ngan.png`, `i-tai-khoan-sai-mk-cu.png`, `j-tai-khoan-doi-xong.png` | Đạt: Họ tên, Vai trò chỉ đọc; form mở sẵn; báo tại chỗ "Mật khẩu mới cần ít nhất 8 ký tự", "Hai lần nhập mật khẩu mới chưa khớp", "Mật khẩu hiện tại không đúng"; đổi đúng hiện "Đã đổi mật khẩu", đăng nhập bằng mật khẩu mới được; đã đổi về `demo12345` |
| GD-AC3 | `quanly` → `/cai-dat`: chọn Tối, Gọn, Lớn, Bật; tải lại trang | `b-cai-dat-quan-ly.png`, `c-cai-dat-toi-gon-lon.png` | Đạt: đủ 4 mục; áp ngay (`data-che-do=toi`, `data-mat-do=gon`, `data-co-chu=lon` cỡ chữ 14 → 15,75 px, `data-giam-chuyen-dong=bat`), không có nút Lưu; tải lại vẫn giữ (4 khóa `qlvc-*` trong `localStorage`); cuối trang có link Cấu hình hệ thống |
| GD-AC4 | `taixe` ở 390 px: menu tài khoản → Tài khoản → Cài đặt (chọn Tối rồi Theo máy) → "← Chuyến của tôi" | `k-tai-xe-menu-390.png`, `l-tai-xe-tai-khoan-390.png`, `m-tai-xe-cai-dat-390.png` | Đạt: menu chỉ Tài khoản, Cài đặt (không có Cấu hình hệ thống), nằm trong màn (12–378 px); hai trang không tràn ngang, các lựa chọn xếp thành hàng ngang dưới tiêu đề; chọn Tối áp ngay; link "← Chuyến của tôi" về `/tai-xe/chuyen` |
| GD-AC5 | Tối + Lớn (+ Gọn): Tổng quan, Chuyến, menu tài khoản, Tài khoản, Cài đặt | `d-tong-quan-toi-lon.png`, `e-chuyen-toi-lon-gon.png`, `f-menu-toi-lon.png`, `g-tai-khoan-toi-lon.png` | Đạt: không trang nào tràn ngang (0 px), chữ sáng trên nền tối đọc rõ, bảng chuyến gọn hơn |

**Kết luận: 5/5 AC đạt.** Không có lỗi trong console.
