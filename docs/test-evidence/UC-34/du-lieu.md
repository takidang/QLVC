# Dữ liệu thử giao diện UC-34 Hiệu suất xe (UC-34-AC7)

> Kiệt thử 18/11/2026 (Claude chạy trên Edge 1440 px, máy Kiệt). Backend `dev` (1900ad3), giao diện v3 `tai/thu-giao-dien-v3` (7348c6c), CSDL `qlvc_demo`.

Đăng nhập `quanly` → **Tổng quan** → bảng "Hiệu suất xe" (cuối trang).

| Ca | Làm gì | Kết quả đúng (AC7) | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Tháng 11/2026 | Bảng mỗi xe một dòng | `a-hieu-suat-xe-thang-11.png` | Đạt: mỗi xe chạy trong tháng một dòng: số chuyến, lấp đầy trung bình (thanh + %), km, dầu thực tế / tham khảo, số chuyến chưa quyết toán; "1 xe đang hoạt động không chạy chuyến nào trong tháng" |
| b | Đổi tháng sang 10/2026 | Bảng đổi theo tháng | `b-hieu-suat-xe-thang-10.png` | Đạt: "Tháng này chưa có xe nào chạy xong chuyến" |
| c | Xe có dầu thực tế lớn hơn tham khảo | Tô chênh lệch dầu dương (hao) | `a-hieu-suat-xe-thang-11.png` | **Không đạt**: không hiện cột chênh lệch (`chenh_lech_lit` API có trả), không tô màu. Ví dụ 51C-203.33 dầu 240 / tham khảo 69,12 lít, 51C-204.44 160 / 46,08 lít vẫn cùng màu chữ thường như mọi dòng |

## Thử lại sau khi Tài sửa (18/11/2026, v3 `0cef9cd`)
- Bảng có thêm cột **Chênh lệch (lít)**; số dương (hao dầu) tô màu cam như màu lỗ: 51C-201.11 +26,04, 51C-203.33 +170,88, 51C-204.44 +113,92, 51D-305.55 +0,04. Số âm, 0 giữ màu chữ thường (51C-202.22 −20). Ảnh `a-hieu-suat-xe-thang-11.png` đã thay bằng ảnh mới.
- Góp ý nhỏ (không chặn AC): xe chưa có khoản dầu được duyệt vẫn hiện chênh lệch âm (51D-307.77 "0 / 62,64 chưa duyệt dầu", chênh lệch −62,64), dễ hiểu nhầm là tiết kiệm dầu; nên để "–" khi chưa duyệt dầu.

**Kết luận: AC7 đạt.**
