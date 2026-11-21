# Báo cáo kiểm thử theo tiêu chí chấp nhận

> Sinh từ bảng "Truy vết và kết quả" của các story trong `docs/stories/` (lệnh `story report` của skill `story-flow`), chỉ lấy số liệu từ story, không ước lượng. Cập nhật 21/11/2026 theo `dev`. Story còn **Nháp** (chưa duyệt tiêu chí) không tính. Chuỗi truy vết: use case → tiêu chí chấp nhận (AC) → test case → bằng chứng; mỗi AC loại Logic / API có test tự động, loại UI có ảnh chụp trong `docs/test-evidence/`.

## Tổng hợp

- **38 story**, **368 tiêu chí** (AC): **368 đạt**, **0 chưa kiểm**, **0 không đạt**.
- Story hoàn thành: 38/38.

## Theo loại tiêu chí

| Loại | Số AC | Đạt | Chưa kiểm | Không đạt |
|---|---|---|---|---|
| API | 294 | 294 | 0 | 0 |
| UI | 45 | 45 | 0 | 0 |
| Logic | 25 | 25 | 0 | 0 |
| Dữ liệu | 3 | 3 | 0 | 0 |
| Tài liệu | 1 | 1 | 0 | 0 |

## Theo use case

| Mã | Tên | Số AC | Đạt | Chưa kiểm | Không đạt | Story |
|---|---|---|---|---|---|---|
| UC-01 | Đăng nhập / đăng xuất | 12 | 12 | 0 | 0 | Hoàn thành |
| UC-02 | Quản lý người dùng và vai trò | 11 | 11 | 0 | 0 | Hoàn thành |
| UC-03 | Quản lý xe | 13 | 13 | 0 | 0 | Hoàn thành |
| UC-04 | Quản lý tài xế | 10 | 10 | 0 | 0 | Hoàn thành |
| UC-05 | Quản lý tuyến và nút | 9 | 9 | 0 | 0 | Hoàn thành |
| UC-06 | Quản lý khách hàng | 6 | 6 | 0 | 0 | Hoàn thành |
| UC-07 | Quản lý bảng giá và cấu hình | 9 | 9 | 0 | 0 | Hoàn thành |
| UC-08 | Tạo đơn hàng | 11 | 11 | 0 | 0 | Hoàn thành |
| UC-10 | Sửa / hủy đơn | 12 | 12 | 0 | 0 | Hoàn thành |
| UC-11 | Lập chuyến | 12 | 12 | 0 | 0 | Hoàn thành |
| UC-12 | Gán / đổi xe và tài xế | 5 | 5 | 0 | 0 | Hoàn thành |
| UC-13 | Ghép / gỡ đơn khỏi chuyến | 13 | 13 | 0 | 0 | Hoàn thành |
| UC-15 | Chốt / mở chốt chuyến | 11 | 11 | 0 | 0 | Hoàn thành |
| UC-16 | Hủy chuyến | 10 | 10 | 0 | 0 | Hoàn thành |
| UC-17 | Xem chuyến được giao | 10 | 10 | 0 | 0 | Hoàn thành |
| UC-18 | Bắt đầu / kết thúc chuyến | 12 | 12 | 0 | 0 | Hoàn thành |
| UC-19 | Quét mã lấy hàng / báo không lấy được | 15 | 15 | 0 | 0 | Hoàn thành |
| UC-20 | Quét mã giao hàng / báo giao không được | 16 | 16 | 0 | 0 | Hoàn thành |
| UC-21 | Ghi chi phí | 14 | 14 | 0 | 0 | Hoàn thành |
| UC-22 | Xử lý đơn thất bại | 12 | 12 | 0 | 0 | Hoàn thành |
| UC-23 | Cấp / sửa / thu hồi tạm ứng | 14 | 14 | 0 | 0 | Hoàn thành |
| UC-24 | Quyết toán chuyến | 14 | 14 | 0 | 0 | Hoàn thành |
| UC-25 | Công nợ – xem nợ theo khách, đánh dấu đã thu | 10 | 10 | 0 | 0 | Hoàn thành |
| UC-26 | Báo cáo lãi lỗ theo chuyến / xe / tháng | 8 | 8 | 0 | 0 | Hoàn thành |
| UC-27 | Bảng cảnh báo cho Điều phối | 8 | 8 | 0 | 0 | Hoàn thành |
| UC-28 | Tra cứu đơn | 7 | 7 | 0 | 0 | Hoàn thành |
| UC-30 | Dự đoán nguy cơ trễ chuyến | 7 | 7 | 0 | 0 | Hoàn thành |
| UC-32 | Theo dõi chuyến | 16 | 16 | 0 | 0 | Hoàn thành |
| UC-33 | Báo sự cố | 9 | 9 | 0 | 0 | Hoàn thành |
| UC-34 | Hiệu suất xe theo tháng | 7 | 7 | 0 | 0 | Hoàn thành |
| UC-35 | Đổi mật khẩu của chính mình | 5 | 5 | 0 | 0 | Hoàn thành |
| UC-36 | Tìm kiếm chung | 5 | 5 | 0 | 0 | Hoàn thành |
| UC-37 | Thông báo theo vai trò | 5 | 5 | 0 | 0 | Hoàn thành |
| UC-38 | Tổng quan hôm nay | 6 | 6 | 0 | 0 | Hoàn thành |
| UC-39 | Hồ sơ cá nhân và ảnh đại diện | 7 | 7 | 0 | 0 | Hoàn thành |
| DEMO | Dữ liệu mẫu cho buổi demo | 6 | 6 | 0 | 0 | Hoàn thành |
| E2E | Chạy trọn vòng từ tạo đơn đến quyết toán | 6 | 6 | 0 | 0 | Hoàn thành |
| GD | Menu tài khoản, trang Tài khoản và Cài đặt | 5 | 5 | 0 | 0 | Hoàn thành |

## Việc còn mở

Không còn tiêu chí nào chưa kiểm.

## Lỗi còn mở

Không có tiêu chí nào ở trạng thái "không đạt".
