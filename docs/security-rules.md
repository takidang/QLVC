# Quy tắc bảo mật của đồ án

Dùng khi viết code và khi chạy ponytail-review.

- Phân quyền theo vai trò: Quản lý, Điều phối viên, Tài xế, Kế toán, Khách hàng. Mọi endpoint phải kiểm tra vai trò ở backend, không chỉ ẩn nút ở frontend.
- Kiểm tra quyền sở hữu (IDOR): tài xế chỉ xem và cập nhật chuyến được phân cho mình; khách hàng không có tài khoản, chỉ tra cứu bằng mã đơn + 4 số cuối SĐT (BR-59), trả về thông báo chung khi sai. Truy vấn theo `id` từ request phải lọc thêm theo người dùng hiện tại.
- Quét mã khi bốc/giao: chỉ nhận khi đơn thuộc chuyến của tài xế đang đăng nhập và chuyến đang ở trạng thái hợp lệ. Giờ quét lấy từ server, không tin giờ do client gửi.
- Ảnh và chữ ký upload: kiểm tra loại file và kích thước, đặt tên file do server sinh, không dùng tên file người dùng gửi làm đường dẫn.
- Dữ liệu tiền (cước, chi phí, tạm ứng, quyết toán): phân biệt **tạo theo nghiệp vụ** và **sửa số tiền đã ghi**. Mọi lần tạo, sửa, duyệt đều ghi nhật ký tiền chỉ-thêm: người làm, thời điểm, giá trị cũ, giá trị mới, lý do (BR-62). Tiền lưu số nguyên (đồng).

  | Khoản tiền | Ai tạo, lúc nào | Ai được sửa sau khi đã ghi | Khóa khi |
  |---|---|---|---|
  | Cước đơn | **Hệ thống tính**, không ai gõ tay. Điều phối tạo đơn → hệ thống chốt cước ngay (BR-32). Điều phối sửa kg/m³/điểm/hạn khi hàng chưa lấy (`CHO_GHEP`, `DA_GHEP`) → hệ thống tính lại theo bản sao giá đã chốt (BR-33) | Không ai (điều chỉnh cước tay BR-61 đã bỏ ở 0.5) | Đơn đã lấy hàng (BR-33) |
  | Chi phí phát sinh | Tài xế của chuyến, kèm ảnh chứng từ (UC-21, BR-54) | Tài xế: sửa/xóa khoản **của mình** khi còn `CHO_DUYET`. Kế toán: duyệt, điều chỉnh (có lý do), từ chối | Chuyến `DA_QUYET_TOAN` (BR-29) |
  | Tạm ứng | Kế toán (UC-23), khi chuyến từ `DA_CHOT` tới trước `HOAN_THANH`; tổng không vượt định mức đã chốt của chuyến (BR-53, không có luồng Quản lý duyệt) | Kế toán, khi chưa quyết toán. **Mỗi lần sửa kiểm lại BR-53**: vượt định mức → từ chối. Trước khi mở chốt hoặc hủy chuyến, Kế toán ghi thu hồi: `HIEU_LUC → DA_THU_HOI` (BR-24, 25) | Chuyến `DA_QUYET_TOAN`; khoản `DA_THU_HOI` |
  | Quyết toán, lương tài xế | Kế toán (UC-24); lương lấy từ số đã chốt vào chuyến lúc chốt (BR-71). Chuyến kết thúc do sự cố: Kế toán nhập lương tay, bắt buộc lý do (BR-68). Ghi cách xử lý chênh lệch tạm ứng (BR-55) | Kế toán, trước khi xác nhận quyết toán | Chuyến `DA_QUYET_TOAN` |
  | Phải thu (công nợ) | Hệ thống sinh khi đơn `DA_GIAO`, bằng cước (BR-56) | Kế toán: đánh dấu đã thu cho một hoặc nhiều đơn | `DA_THU` |
  | Bảng giá, định mức tuyến | Quản lý (UC-07); Điều phối nhập định mức tuyến (UC-05) | Như người tạo. Đổi bảng giá không ảnh hưởng đơn đã tạo; đổi định mức tuyến không ảnh hưởng chuyến đã chốt (BR-71) | — |

  Điều phối và Tài xế **không có endpoint** nào nhận số tiền cước. Endpoint sửa tiền của Kế toán/Quản lý phải có ca test bị từ chối với vai trò khác và với chuyến đã quyết toán.
- Không log mật khẩu, token, số điện thoại, tọa độ GPS đầy đủ của khách.
- Key, chuỗi kết nối DB, secret JWT chỉ đọc từ biến môi trường; không có giá trị mặc định thật trong code.
