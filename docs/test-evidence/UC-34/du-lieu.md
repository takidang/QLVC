# Dữ liệu thử giao diện UC-34 Hiệu suất xe (UC-34-AC7)

> Kiệt thử 18/11/2026 (Claude chạy trên Edge 1440 px, máy Kiệt). Backend `dev` (1900ad3), giao diện v3 `tai/thu-giao-dien-v3` (7348c6c), CSDL `qlvc_demo`.

Đăng nhập `quanly` → **Tổng quan** → bảng "Hiệu suất xe" (cuối trang).

| Ca | Làm gì | Kết quả đúng (AC7) | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Tháng 11/2026 | Bảng mỗi xe một dòng | `a-hieu-suat-xe-thang-11.png` | Đạt: mỗi xe chạy trong tháng một dòng: số chuyến, lấp đầy trung bình (thanh + %), km, dầu thực tế / tham khảo, số chuyến chưa quyết toán; "1 xe đang hoạt động không chạy chuyến nào trong tháng" |
| b | Đổi tháng sang 10/2026 | Bảng đổi theo tháng | `b-hieu-suat-xe-thang-10.png` | Đạt: "Tháng này chưa có xe nào chạy xong chuyến" |
| c | Xe có dầu thực tế lớn hơn tham khảo | Tô chênh lệch dầu dương (hao) | `a-hieu-suat-xe-thang-11.png` | **Không đạt**: không hiện cột chênh lệch (`chenh_lech_lit` API có trả), không tô màu. Ví dụ 51C-203.33 dầu 240 / tham khảo 69,12 lít, 51C-204.44 160 / 46,08 lít vẫn cùng màu chữ thường như mọi dòng |

**Kết luận: AC7 chưa đạt** (thiếu tô chênh lệch dầu dương). Chọn tháng và bảng mỗi xe đã đạt.
