# Dữ liệu thử giao diện UC-25 Công nợ (AC10)

> Claude ghi 09/11/2026 cho Kiệt thử trên nhánh `kiet/uc-25-cong-no` (đã gộp `dev`). Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC10 trong `docs/stories/UC-25-cong-no.md`.

## Chuẩn bị (CSDL máy Kiệt)

- 3 khoản phải thu của **Cty A**, đều **chưa thu** (sinh khi giao ở UC-20 và khi thử PR #21): **DH-MSKG7T** 2.997.000, **DH-6HXV2Y** 800.000, **DH-S4JPYG** 800.000 → Cty A nợ **4.597.000**.
- CSDL chỉ có một khách nên không thử được "khoản của hai khách" trên giao diện (giao diện chỉ cho chọn khoản của khách đang xem); ca này có test tự động `test_uc25_ac4_khac_khach`.
- Đăng nhập Kế toán `ketoan` / `demo12345` (hoặc `thu`). Máy tính, cửa sổ thường. Không có gói mới, không có migration mới.

## Các ca

Menu **Công nợ** (giữa "Chi phí cố định xe" và "Tạm ứng").

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Mở **Công nợ** | Bảng nợ theo khách: **Cty A · 3 khoản · 4.597.000 đ** | `a-no-theo-khach.png` | |
| b | Cty A → **Xem** | Bảng "Khoản của Cty A", nút **Chưa thu** đang chọn, 3 khoản có ô tích, cột giờ giao; "Đã chọn 0 khoản · 0 đ", ô **Ngày thu** = hôm nay, nút **Đánh dấu đã thu** mờ | `b-khoan-chua-thu.png` | |
| c | Tích **DH-6HXV2Y** và **DH-S4JPYG** | "Đã chọn 2 khoản · 1.600.000 đ"; nút sáng | – | |
| d | Ô Ngày thu thử chọn **ngày mai** | Lịch không cho chọn ngày sau hôm nay (nếu gõ tay được thì bấm sẽ báo "Ngày thu không được sau hôm nay") | – | |
| e | Ngày thu **hôm qua** → **Đánh dấu đã thu** → hộp hỏi "Đã thu 1.600.000 đ của Cty A (2 khoản) ngày …?" → **OK** | Xanh "Đã lập phiếu thu #…: 1.600.000 đ (2 khoản)"; bảng còn **DH-MSKG7T**; bảng nợ: **Cty A · 1 khoản · 2.997.000 đ** | `e-da-thu.png` | |
| f | Bấm **Đã thu** | 2 khoản DH-6HXV2Y, DH-S4JPYG, cột "Phiếu thu" có **#số · ngày hôm qua**; không có ô tích | `f-da-thu-list.png` | |
| g | Về **Chưa thu**, tích **DH-MSKG7T**, ngày hôm nay → **Đánh dấu đã thu** → **OK** | Phiếu thu thứ hai 2.997.000 đ; bảng nợ "Không khách nào còn nợ" | `g-het-no.png` | |

## Sau khi thử

Claude kiểm CSDL: 2 `phieu_thu` (1.600.000 ngày hôm qua; 2.997.000 hôm nay) của Cty A, người tạo là Kế toán; 3 `phai_thu` `DA_THU` đúng `phieu_thu_id`; 3 dòng `nhat_ky_tien` `DA_THU`; trạng thái 3 đơn vẫn `DA_GIAO`.
