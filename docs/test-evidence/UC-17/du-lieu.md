# Dữ liệu thử giao diện UC-17 Xem chuyến được giao

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).

Ảnh lưu vào `docs/test-evidence/UC-17/` · Kiệt thử 31/10/2026 (nhánh `kiet/uc-17-xem-chuyen`).

## Chuẩn bị

- Dùng chuyến **CH-261031-01** của UC-11, UC-13 (`docs/test-evidence/UC-11/du-lieu.md`, `UC-13/du-lieu.md`) (T01, xe `51C-111.11`, tài xế An, 06:00 31/10, 3 đơn `DH-MSKG7T`, `DH-9ZTTPG`, `DH-6HXV2Y`).
- UC-15 (Chốt chuyến) chưa có, nên 31/10 Claude đổi thẳng trong CSDL thử: `trang_thai = DA_CHOT`, `luong_tai_xe_chot = 600000` (lương khoán T01). Định mức chốt và ETA kế hoạch để trống → giờ tự tính lại (quyết định UC-17 số 4). Muốn thử lại UC-13 thì nhờ Claude đổi về `LAP`.
- **Chạy lại backend** sau khi chuyển nhánh (`Ctrl + C` rồi chạy lại lệnh uvicorn); frontend tự cập nhật.
- Giả lập điện thoại: Chrome/Edge `http://127.0.0.1:5173` → `F12` → `Ctrl + Shift + M` → chiều ngang **360**.
- Đăng xuất Quản lý, đăng nhập tài xế `an` / `matkhau123` (đặt ở `docs/test-evidence/UC-04/du-lieu.md`).

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Đăng nhập `an` | Vào thẳng **Chuyến của tôi**, thẻ **Cần làm** có CH-261031-01 ("Chờ chạy", T01, xe 51C-111.11, 3 đơn); **không** có thanh cuộn ngang | `a-can-lam.png` | Đạt (ảnh; Kiệt xác nhận xem ở khổ 360 không cuộn ngang, ảnh chụp khổ rộng) |
| b | Bấm thẻ **Đã xong** | Báo "Chưa có chuyến đã xong" | `b-da-xong.png` | Đạt (ảnh) |
| c | Quay lại **Cần làm**, bấm vào CH-261031-01 | Lịch trình **6 điểm** (06:00 … 12:10); mỗi điểm có mã đơn, khách, kg/m³/kiện, địa chỉ, người liên hệ, SĐT **gạch chân bấm gọi được**, khung lấy hoặc hạn giao; có **"Lương chuyến 600.000 đ"**; **không** thấy cước, lãi | `c-lich-trinh.png` | Đạt (ảnh: 6 điểm 06:00…12:10, SĐT là link gọi, "Lương chuyến 600.000 đ", không có cước) |
| d | Bấm **← Chuyến của tôi** | Về lại danh sách | – | Đạt (Kiệt xác nhận) |

Lỗi bắt được khi thử: bấm lại thẻ **Cần làm** đang chọn thì kẹt "Đang tải…" (danh sách bị xóa mà không tải lại). Đã sửa 31/10 (`ChuyenCuaToi.tsx`: bấm lại thẻ đang chọn thì không làm gì), Kiệt thử lại đạt.

Xong ghi kết quả vào dòng **AC10** của `docs/stories/UC-17-xem-chuyen-duoc-giao.md`.
