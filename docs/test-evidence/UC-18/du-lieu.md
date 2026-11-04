# Dữ liệu thử giao diện UC-18 Bắt đầu / kết thúc chuyến

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` (Phần 8) ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).

Ảnh lưu vào `docs/test-evidence/UC-18/` · Kiệt thử 31/10/2026 (nhánh `kiet/uc-18-bat-dau-ket-thuc`).

## Chuẩn bị

- Dùng tiếp chuyến **CH-261031-01** (đã `DA_CHOT` ở `docs/test-evidence/UC-17/du-lieu.md`). Chuyến chạy **ngày 31/10** nên **chỉ thử được trong ngày 31/10** (BR-26); thử ngày khác sẽ bị báo BR-26 – nhờ Claude đổi ngày khởi hành của chuyến.
- Xe `51C-111.11` trên máy Kiệt có km đồng hồ **50.000** (lúc thêm xe ở `docs/test-evidence/UC-11/du-lieu.md` nhập 50.000, không phải 120.000 như bảng chuẩn bị).
- Máy Kiệt: `cd backend; .venv\Scripts\pip install -r requirements-dev.txt` (cài `python-multipart` mới thêm) – Claude đã cài sẵn 31/10. **Chạy lại backend** sau khi chuyển nhánh.
- Chuẩn bị **một ảnh JPG/PNG bất kỳ** trên máy (chụp màn hình cũng được) làm "ảnh đồng hồ". Trên máy tính, ô chụp ảnh mở hộp chọn file; trên điện thoại thật nó mở camera.
- Giả lập điện thoại 360 px (`F12` → `Ctrl + Shift + M`), đăng nhập `an` / `matkhau123`, mở CH-261031-01.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Xem trang chuyến | Có khung **Bắt đầu chuyến**: ô km, ô ảnh đồng hồ, nút **Bắt đầu** | `a-bat-dau.png` | Đạt (ảnh) |
| b | Km `49999` + chọn ảnh → **Bắt đầu** | Báo đỏ "Km bắt đầu 49,999 nhỏ hơn km đã ghi của xe 51C-111.11 (50,000) (BR-70)"; chuyến vẫn "Chờ chạy" | `b-vi-pham-km-ban-dau.png` | Đạt (ảnh: đúng câu BR-70) |
| c | Km `50000` + chọn ảnh → **Bắt đầu** | Thẻ trạng thái thành **"Đang chạy"**; khung đổi thành **Kết thúc chuyến** | `c-dang-chay.png` | Đạt (ảnh; CSDL: `DANG_CHAY`, km 50.000, ảnh đã nén còn ~60 KB) |
| d | Km `50178` + chọn ảnh → **Kết thúc** | Báo "Còn 3 đơn chưa giao hoặc báo thất bại …" và liệt kê **3 dòng** đơn `DH-6HXV2Y`, `DH-9ZTTPG`, `DH-MSKG7T` kèm (BR-28); chuyến vẫn "Đang chạy" (quét giao là UC-19, 20 – chưa có) | `d-con-don.png` | Đạt (ảnh: liệt kê đủ 3 đơn kèm BR-28) |
| e | *(Tùy chọn)* Nhờ Claude đặt 3 đơn thành Đã giao / Thất bại trong CSDL thử, rồi km `50178` + ảnh → **Kết thúc** | Thẻ thành **"Hoàn thành"**, khung Kết thúc biến mất; danh sách: chuyến chuyển sang thẻ **Đã xong** | `e-hoan-thanh.png` | Không thử (tùy chọn); kết thúc thành công đã có test `test_uc18_ac6_ket_thuc_hop_le` |

Lần thử đầu báo "Có lỗi (mã 404)": backend còn chạy bản UC-17, chưa khởi động lại sau khi chuyển nhánh – không phải lỗi code. Lần thử thứ hai nhập 119.999 bắt đầu được vì km thật của xe là 50.000; Claude trả dữ liệu về trước khi thử (chuyến `DA_CHOT`, xóa ảnh và dòng lịch sử) rồi thử lại theo km 50.000.
Quản lý / Điều phối thấy trạng thái chuyến đổi ở menu Chuyến; **km, ảnh đồng hồ chưa có màn hình** – kiểm khi UC-32 xong.
Sau khi thử: CH-261031-01 đang `DANG_CHAY` (km bắt đầu 50.000) để dùng tiếp cho UC-19, 20.

Xong ghi kết quả vào dòng **AC11** của `docs/stories/UC-18-bat-dau-ket-thuc-chuyen.md`.
