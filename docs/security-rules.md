# Quy tắc bảo mật của đồ án

Dùng khi viết code và khi chạy ponytail-review.

- Phân quyền theo vai trò: Quản lý, Điều phối viên, Tài xế, Kế toán, Khách hàng. Mọi endpoint phải kiểm tra vai trò ở backend, không chỉ ẩn nút ở frontend.
- Kiểm tra quyền sở hữu (IDOR): tài xế chỉ xem và cập nhật chuyến được phân cho mình; khách hàng không có tài khoản, chỉ tra cứu bằng mã đơn + 4 số cuối SĐT (BR-59), trả về thông báo chung khi sai. Truy vấn theo `id` từ request phải lọc thêm theo người dùng hiện tại.
- Quét mã khi bốc/giao: chỉ nhận khi đơn thuộc chuyến của tài xế đang đăng nhập và chuyến đang ở trạng thái hợp lệ. Giờ quét lấy từ server, không tin giờ do client gửi.
- Ảnh và chữ ký upload: kiểm tra loại file và kích thước, đặt tên file do server sinh, không dùng tên file người dùng gửi làm đường dẫn.
- Dữ liệu tiền (cước, chi phí, tạm ứng, quyết toán): phân biệt **tạo theo nghiệp vụ** và **sửa số tiền đã ghi**. Mọi lần tạo, sửa, duyệt đều ghi nhật ký tiền chỉ-thêm: người làm, thời điểm, giá trị cũ, giá trị mới, lý do (BR-62). Tiền lưu số nguyên (đồng).

  | Khoản tiền | Ai tạo, lúc nào | Ai được sửa sau khi đã ghi | Khóa khi |
  |---|---|---|---|
  | Cước đơn | **Hệ thống tính**, không ai gõ tay. Điều phối bấm Xác nhận đơn → chốt cước (BR-32). Điều phối sửa kg/m³/điểm trước `DA_LAY_HANG` → hệ thống tính lại theo đơn giá đã chốt (BR-33) | Kế toán, Quản lý: điều chỉnh tay (giảm giá, phụ phí), lưu thành khoản điều chỉnh riêng, bắt buộc lý do (BR-61, UC-31) | Khoản phải thu đã thu một phần trở lên, **hoặc** chuyến ghi nhận doanh thu đơn đã `DA_QUYET_TOAN`, hoặc đơn `HUY`/`HOAN_HANG` (BR-61) |
  | Chi phí phát sinh | Tài xế của chuyến, kèm ảnh chứng từ (UC-21, BR-54) | Tài xế: sửa/xóa khoản **của mình** khi còn `CHO_DUYET`. Kế toán: duyệt, điều chỉnh (có lý do), từ chối | Chuyến `DA_QUYET_TOAN` (BR-29) |
  | Tạm ứng | Kế toán (UC-23). Vượt định mức → Quản lý duyệt (BR-53) | Kế toán, khi chưa quyết toán. **Mỗi lần sửa kiểm lại BR-53**: tổng vượt định mức → khoản đó về chờ Quản lý duyệt | Chuyến `DA_QUYET_TOAN` |
  | Quyết toán, lương tài xế | Kế toán (UC-24); lương lấy từ định mức tuyến | Kế toán, trước khi xác nhận quyết toán | Chuyến `DA_QUYET_TOAN` |
  | Bảng giá, định mức tuyến | Quản lý (UC-07); Điều phối nhập định mức tuyến (UC-05) | Như người tạo. Đổi bảng giá không ảnh hưởng đơn đã chốt cước | — |

  Điều phối và Tài xế **không có endpoint** nào nhận số tiền cước. Endpoint sửa tiền của Kế toán/Quản lý phải có ca test bị từ chối với vai trò khác và với chuyến đã quyết toán.
- Không log mật khẩu, token, số điện thoại, tọa độ GPS đầy đủ của khách.
- Key, chuỗi kết nối DB, secret JWT chỉ đọc từ biến môi trường; không có giá trị mặc định thật trong code.
