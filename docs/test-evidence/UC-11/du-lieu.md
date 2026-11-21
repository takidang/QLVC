# Dữ liệu thử giao diện UC-11 Lập chuyến

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).

Ảnh lưu vào `docs/test-evidence/UC-11/` · Số liệu theo kịch bản `nghiep-vu.md` mục 11. **"Ngày mai" = 31/10/2026** (thử tối 30/10). Thử sang ngày 31/10 thì đổi hết thành 01/11.

## Chuẩn bị (làm một lần, dùng chung cho `docs/test-evidence/UC-11/du-lieu.md` và 6)

CSDL máy Kiệt lúc 30/10 **chưa có xe nào**; Bình đang Ngừng và GPLX hết hạn 2020 (lý do sẽ lẫn với BR-14).

| # | Menu | Làm gì | Dữ liệu |
|---|---|---|---|
| 1 | Xe → Thêm xe | Thêm X1 | Biển số `51C-111.11` · Tải trọng `5000` · KL toàn bộ `9500` · Thể tích `20` · Dầu `15` · Hạn đăng kiểm `30/11/2026` · Hạn bảo hiểm `30/06/2027` · Km đồng hồ `50000` |
| 2 | Xe → Thêm xe | Thêm X3 rồi bấm **Ngừng** | Biển số `51C-333.33` · Tải trọng `2000` · KL toàn bộ `4500` · Thể tích `10` · Dầu `12` · Hạn đăng kiểm `31/12/2026` · Hạn bảo hiểm `31/12/2026` · Km `120000` |
| 3 | Tài xế | Bình: bấm **Hoạt động lại**, rồi **Sửa** hạn GPLX | Hạn GPLX `31/12/2028` (để Bình chỉ vướng BR-14 hạng B) |
| 4 | Tài xế | An: **Sửa** họ tên | `Nguyễn Văn An` (lỡ đổi lúc thử UC-02 ca d) |

| Ca | Làm gì | Dữ liệu nhập | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|---|
| a | Chuyến → Lập chuyến | Tuyến `T01` · Khởi hành `31/10/2026 06:00` | Hiện danh sách xe và tài xế; X3 hiện **"không dùng được"** kèm lý do Ngừng (BR-11) | `a-danh-sach-xe.png` | Đạt (ảnh: "Xe 51C-333.33 đang ngừng hoạt động (BR-11)") |
| b | Chọn xe | Chọn `51C-111.11` | **Bình mờ**, lý do hạng GPLX B, xe 9.500 kg cần C (BR-14) | `b-tai-xe-sai-hang.png` | Đạt (ảnh) |
| c | Chọn tài xế → Lập chuyến | Chọn **An** → Lập chuyến | Báo **"Đã lập chuyến CH-261031-01"**, kết thúc dự kiến **11:30** (06:00 + 270′ chạy + 60′ nghỉ) | `c-lap-chuyen.png` | Đạt (ảnh: thông báo "…-01 (T01, 51C-111.11, Nguyễn Văn An)" bị hộp thoại che một phần; mã CH-261031-01 và giờ 06:00 → 11:30 thấy rõ ở ảnh d) |
| d | Lập chuyến khác | `T01` · `31/10/2026 10:00` | Xe `51C-111.11` **mờ**, lý do trùng lịch chuyến vừa lập (BR-16). Không cần lập | `d-trung-lich.png` | Đạt (ảnh, thử với T02 06:00 thay vì T01 10:00: xe trùng lịch CH-261031-01 (BR-16), thêm An trùng lịch (BR-17)) |
| e | Lập chuyến giờ đã qua | `T01` · **hôm qua** `29/10/2026 06:00` → Lập chuyến | Báo **"Giờ khởi hành đã qua"** | `e-da-qua-ngay-thuc-te.png` | Đạt (Kiệt xác nhận thấy "Giờ khởi hành đã qua" sau khi chọn xe + tài xế và bấm; ảnh chụp trước khi bấm) |

Xong ghi kết quả vào dòng **AC12** của `docs/stories/UC-11-lap-chuyen.md` (Đạt/Không đạt, ngày, "Kiệt thử"). Sai chỗ nào ghi vào "Đang chặn" cho Tài, không tự sửa code.
