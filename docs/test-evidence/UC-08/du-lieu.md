# Dữ liệu thử giao diện UC-08 Tạo đơn

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).
> Kiệt thử ngày 25/10/2026 (Edge/Chrome, tài khoản Quản lý). Kết quả đã điền vào story UC-04 (AC10), UC-05 (AC9), UC-08 (AC11); ảnh trong `docs/test-evidence/UC-04/`, `UC-05/`, `UC-08/`.
> Bằng chứng ghi ở cột "Kết quả": **ảnh** (file trong thư mục), **log** (nhật ký backend lúc thử), **test** (test tự động pytest). Ca không có bằng chứng thì ghi rõ.
> Địa chỉ lúc thử: `http://localhost:5173`. Từ 29/10 Tài đã cho Vite chạy ở `127.0.0.1`, nên `http://127.0.0.1:5173` cũng mở được.
> Chụp ảnh: **Win + Shift + S**, lưu đúng thư mục và tên ở cột "Ảnh".
> Đã chuẩn bị sẵn trong CSDL: bảng giá TP.HCM → Cần Thơ (1.500 đ/kg, tối thiểu 50.000, hiệu lực 01/10/2026); khách hàng Cty A (0909123456).
> Thứ tự: Phần 1 → Phần 2 → Phần 3 (UC-08 cần nút của UC-05).

Ảnh lưu vào `docs/test-evidence/UC-08/`

## Ca e: tạo đơn hợp lệ (menu "Đơn hàng" → Tạo đơn)

| Ô | Giá trị |
|---|---|
| Khách hàng | `Cty A` |
| Mô tả hàng | `Thùng carton đồ gia dụng` |
| Khối lượng thực (kg) | `1800` |
| Thể tích (m³) | `6` |
| Số kiện | `40` |
| **Điểm lấy** | |
| Nút lấy | `TP.HCM` |
| Địa chỉ lấy | `12 Nguyễn Huệ, Quận 1` |
| Người liên hệ | `Phạm Văn Gửi` |
| SĐT lấy | `0909123456` |
| Lấy từ | `26/10/2026 07:00` |
| Lấy đến | `26/10/2026 10:00` |
| **Điểm giao** | |
| Nút giao | `Cần Thơ` |
| Địa chỉ giao | `45 Hòa Bình, Ninh Kiều` |
| Người nhận | `Lê Văn Nhận` |
| SĐT nhận | `0909555666` |
| Hạn giao | `27/10/2026 17:00` |

Kết quả đúng: sau khi chọn đủ nút và nhập kg, m³, khung vàng tự hiện **cước 2.997.000 đ** (6 m³ × 333 = 1.998 kg, lớn hơn 1.800 kg thực → 1.998 × 1.500 đ); bấm Lưu hiện **"Đã tạo đơn DH-XXXXXX"**. Ảnh `e-tao-don.png` (chụp lúc thấy cước) và `e-da-tao.png` (chụp thông báo đã tạo). Kết quả: **Đạt** (ảnh `e-tao-don.png` có cước 2.997.000 đ; đơn lưu được theo log, không chụp thông báo)

## Ca f: địa chỉ giao trùng địa chỉ lấy (bị chặn BR-31)

Như ca e, **giữ nút lấy TP.HCM, nút giao Cần Thơ** (để có bảng giá), chỉ đổi:

| Ô | Giá trị |
|---|---|
| Địa chỉ giao | `12 Nguyễn Huệ, Quận 1` (giống hệt địa chỉ lấy) |

Kết quả đúng: báo lỗi **BR-31**, không lưu. Ảnh `f-trung-dia-chi.png`. Kết quả: **Đạt** (ảnh: "Địa chỉ lấy trùng địa chỉ giao")

## Ca g: chưa có bảng giá (nút Lưu bị khóa)

Như ca e, chỉ đổi chiều:

| Ô | Giá trị |
|---|---|
| Nút lấy | `Cần Thơ` |
| Nút giao | `TP.HCM` |

Kết quả đúng: báo **"Chưa có bảng giá"**, nút **Lưu bị khóa** (chỉ có giá TP.HCM → Cần Thơ, chưa có chiều ngược). Kết quả: **Đạt** (ảnh `e-chua-co-tuyen.png` TP.HCM → TP.HCM và `e-chua-co-tuyen-nguoc-lai.png` Cần Thơ → TP.HCM: báo chưa có bảng giá, nút Lưu khóa)

## Ghi chú khi thử (chung UC-04, 05, 08 ngày 25/10)

- Địa chỉ `http://127.0.0.1:5173` lúc thử không mở được trên máy Kiệt, phải dùng `http://localhost:5173`. **Tài đã sửa 29/10** (Vite chạy ở `127.0.0.1`).
- Thông báo lỗi BR-66, BR-31 lúc thử chưa hiện mã BR. **Tài đã sửa 29/10** (lỗi nghiệp vụ hiện kèm mã, ví dụ "… (BR-66)").
- Ca nào sai: ghi lại "làm gì → thấy gì" vào đây. Không tự sửa code của Tài.
