# Kiểm thử khám phá trên `test` – 25/11/2026

Làm theo skill `kiem-thu-kham-pha`. Code: nhánh `test` (`d46f62c`, bằng `dev` sau #108). CSDL thử riêng `qlvc_pha` (dữ liệu mẫu 8 ngày), máy local.
agy (Gemini 4 Neon high) đọc code và viết 4 script, **không có quyền chạy lệnh**; Claude Code đọc lại (chỉ gọi 127.0.0.1) rồi chạy và xác minh.

## Rà tĩnh
- `npm audit`, `pip-audit`: 0 lỗ hổng.
- ruff, prettier, build đạt; `pytest` 1130 đạt; vitest 14 đạt.

## Phá thử

| Script | Nội dung | Số ca | Đạt | Lỗi thật | Báo nhầm | Bỏ qua |
|---|---|---|---|---|---|---|
| 01 | Hộp xác nhận ở 10 thao tác | 17 | 16 | 0 | 0 | 1 |
| 02 | Nút chép, Pixel 1440 / 1024 / 390 px, hộp thoại | 118 | 111 | 0 | 7 | 0 |
| 03 | Gửi song song: tiền, trạng thái | 23 | 23 | 0 | 0 | 0 |
| 04 | Phân quyền chéo API thêm sau | 17 | 16 | 0 | 1 | 0 |
| **Cộng** | | **175** | **166** | **0** | **8** | **1** |

Log backend không có traceback.

## Báo nhầm
- 02, trang đăng nhập và tra cứu (6 ca): lỗi console 401 là lượt kiểm phiên khi chưa đăng nhập.
- 02, trang Đơn hàng 1440 px (1 ca): nút "Ghép lại", "Trả hàng", "Hủy" bị coi là che; đó là nút trong phiếu "Đơn thất bại" đang đóng (chụp màn hình để xác minh).
- 04 PQ-10: thiếu ngày trả 400 như mong đợi; tham số lạ bị bỏ qua là bình thường.

## Sửa script trước khi tính kết quả
- 01: nhãn "Tên người nhận" khớp cả ô ký, đổi sang chọn theo vai trò textbox (ca XN-17 trước đó chết giữa chừng).
- 03: hạn giao của đơn thử quá gần so với ngày chuyến nên máy chủ chặn đúng BR-06 (SS-10 báo nhầm, các ca sau không chạy); nới hạn.

## Chưa kiểm
- XN-12 (hai hộp chồng nhau): không dựng được tình huống.
- Các lỗi đã biết của đợt trước đã sửa ở #114; đợt này không chạy lại các script đó.
- Còn để sau báo cáo: "Cần chú ý" hiện trễ số phút âm; `ChuyenChiTiet` còn hiện chuyến cũ khi đang tải.

## Sau đợt này
Thêm `logging.warning` cho lỗi `VUOT_GIOI_HAN` (Kiệt góp ý #114), kèm test.
