# Quy tắc bảo mật của đồ án

Dùng khi viết code và khi chạy ponytail-review.

- Phân quyền theo vai trò: Quản lý, Điều phối viên, Tài xế, Kế toán, Khách hàng. Mọi endpoint phải kiểm tra vai trò ở backend, không chỉ ẩn nút ở frontend.
- Kiểm tra quyền sở hữu (IDOR): tài xế chỉ xem và cập nhật chuyến được phân cho mình; khách hàng chỉ tra cứu đơn của mình. Truy vấn theo `id` từ request phải lọc thêm theo người dùng hiện tại.
- Quét mã khi bốc/giao: chỉ nhận khi đơn thuộc chuyến của tài xế đang đăng nhập và chuyến đang ở trạng thái hợp lệ. Giờ quét lấy từ server, không tin giờ do client gửi.
- Ảnh và chữ ký upload: kiểm tra loại file và kích thước, đặt tên file do server sinh, không dùng tên file người dùng gửi làm đường dẫn.
- Dữ liệu tiền (cước, chi phí, tạm ứng, quyết toán): chỉ Kế toán và Quản lý được sửa; mọi thay đổi ghi lại người sửa và thời điểm.
- Không log mật khẩu, token, số điện thoại, tọa độ GPS đầy đủ của khách.
- Key, chuỗi kết nối DB, secret JWT chỉ đọc từ biến môi trường; không có giá trị mặc định thật trong code.
