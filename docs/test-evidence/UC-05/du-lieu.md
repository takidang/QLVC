# Dữ liệu thử giao diện UC-05 Nút, Tuyến

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).
> Kiệt thử ngày 25/10/2026 (Edge/Chrome, tài khoản Quản lý). Kết quả đã điền vào story UC-04 (AC10), UC-05 (AC9), UC-08 (AC11); ảnh trong `docs/test-evidence/UC-04/`, `UC-05/`, `UC-08/`.
> Bằng chứng ghi ở cột "Kết quả": **ảnh** (file trong thư mục), **log** (nhật ký backend lúc thử), **test** (test tự động pytest). Ca không có bằng chứng thì ghi rõ.
> Địa chỉ lúc thử: `http://localhost:5173`. Từ 29/10 Tài đã cho Vite chạy ở `127.0.0.1`, nên `http://127.0.0.1:5173` cũng mở được.
> Chụp ảnh: **Win + Shift + S**, lưu đúng thư mục và tên ở cột "Ảnh".
> Đã chuẩn bị sẵn trong CSDL: bảng giá TP.HCM → Cần Thơ (1.500 đ/kg, tối thiểu 50.000, hiệu lực 01/10/2026); khách hàng Cty A (0909123456).
> Thứ tự: Phần 1 → Phần 2 → Phần 3 (UC-08 cần nút của UC-05).

Ảnh lưu vào `docs/test-evidence/UC-05/`

## Ca a: thêm 5 nút (menu "Nút" → Thêm nút)

Ô **Tỉnh** phải gõ đúng như bảng giá (`TP.HCM`, `Cần Thơ`) thì UC-08 mới tra được giá. Vĩ độ, kinh độ không bắt buộc, điền để đủ dữ liệu.

| # | Tên nút | Tỉnh (tra bảng giá) | Loại | Vĩ độ | Kinh độ |
|---|---|---|---|---|---|
| 1 | `TP.HCM` | `TP.HCM` | Tỉnh/thành | `10.7769` | `106.7009` |
| 2 | `Long An` | `Long An` | Tỉnh/thành | `10.5359` | `106.4137` |
| 3 | `Tiền Giang` | `Tiền Giang` | Tỉnh/thành | `10.3600` | `106.3600` |
| 4 | `Vĩnh Long` | `Vĩnh Long` | Tỉnh/thành | `10.2537` | `105.9722` |
| 5 | `Cần Thơ` | `Cần Thơ` | Tỉnh/thành | `10.0452` | `105.7469` |

Kết quả đúng: lưu được cả 5, hiện trong danh sách. Kết quả: **Đạt** (log: 5 lần thêm nút thành công; Kiệt đặt tên nút `hcm1`, `longan1`… thay cho tên tỉnh, ô Tỉnh vẫn đúng)

## Ca b: tuyến T01 hợp lệ (menu "Tuyến" → Thêm tuyến)

| Ô | Giá trị |
|---|---|
| Mã tuyến | `T01` |
| Tên tuyến | `TP.HCM – Cần Thơ` |
| Định mức dầu (đ) | `550000` |
| Định mức cầu đường (đ) | `200000` |
| Định mức bốc xếp (đ) | `250000` |
| Lương khoán tài xế mỗi chuyến (đ) | `600000` |

Các nút theo thứ tự (bấm thêm dòng cho đủ 5 nút):

| # | Nút | Phút từ đầu | Km từ đầu | Điểm nghỉ |
|---|---|---|---|---|
| 1 | TP.HCM | `0` | `0` | |
| 2 | Long An | `60` | `50` | |
| 3 | Tiền Giang | `120` | `75` | **✔ tick** |
| 4 | Vĩnh Long | `210` | `135` | |
| 5 | Cần Thơ | `270` | `170` | |

Kết quả đúng: lưu được; bảng hiện lộ trình có **"Tiền Giang (nghỉ)"**, thời gian **4 giờ 30 phút**. Ảnh `b-tuyen-t01.png`. Kết quả: **Đạt** (ảnh)

## Ca c: tuyến T02 thiếu điểm nghỉ (vẫn lưu được)

| Ô | Giá trị |
|---|---|
| Mã tuyến | `T02` |
| Tên tuyến | `TP.HCM – Cần Thơ (chạy thẳng)` |
| Định mức dầu (đ) | `600000` |
| Định mức cầu đường (đ) | `200000` |
| Định mức bốc xếp (đ) | `200000` |
| Lương khoán tài xế mỗi chuyến (đ) | `600000` |

| # | Nút | Phút từ đầu | Km từ đầu | Điểm nghỉ |
|---|---|---|---|---|
| 1 | TP.HCM | `0` | `0` | |
| 2 | Cần Thơ | `300` | `170` | không tick |

Kết quả đúng: khung vàng **"thiếu điểm nghỉ (BR-20)"** (chạy 5 giờ liền không nghỉ) nhưng **vẫn lưu được**. Ảnh `c-thieu-diem-nghi.png`. Kết quả: **Đạt** (không chụp riêng; dòng T02 có chữ đỏ "Thiếu điểm nghỉ" trong ảnh `b-tuyen-t01.png`)

## Ca d: tuyến quá 10 giờ (bị chặn)

| Ô | Giá trị |
|---|---|
| Mã tuyến | `T03` |
| Tên tuyến | `Tuyến thử quá 10 giờ` |
| Định mức dầu (đ) | `1000000` |
| Định mức cầu đường (đ) | `300000` |
| Định mức bốc xếp (đ) | `250000` |
| Lương khoán tài xế mỗi chuyến (đ) | `900000` |

| # | Nút | Phút từ đầu | Km từ đầu | Điểm nghỉ |
|---|---|---|---|---|
| 1 | TP.HCM | `0` | `0` | |
| 2 | Long An | `200` | `50` | **✔ tick** |
| 3 | Tiền Giang | `400` | `75` | **✔ tick** |
| 4 | Cần Thơ | **`601`** | `170` | |

Kết quả đúng: **bị chặn, báo BR-66** (601 phút > 10 giờ = 600 phút), tuyến không được lưu. Ảnh `d-qua-10-gio.png`. Kết quả: **Đạt** (ảnh: "Tuyến chạy 601 phút, vượt 10 giờ…"; thử thêm ca biên 600 phút → lưu được, thấy trong ảnh b)

(Tick nghỉ ở Long An, Tiền Giang để mỗi đoạn dưới 4 giờ: lỗi chỉ là BR-66, không lẫn cảnh báo BR-20. Muốn thử thêm ca biên: đổi `601` thành `600` → lưu được.)

## Ghi chú khi thử (chung UC-04, 05, 08 ngày 25/10)

- Địa chỉ `http://127.0.0.1:5173` lúc thử không mở được trên máy Kiệt, phải dùng `http://localhost:5173`. **Tài đã sửa 29/10** (Vite chạy ở `127.0.0.1`).
- Thông báo lỗi BR-66, BR-31 lúc thử chưa hiện mã BR. **Tài đã sửa 29/10** (lỗi nghiệp vụ hiện kèm mã, ví dụ "… (BR-66)").
- Ca nào sai: ghi lại "làm gì → thấy gì" vào đây. Không tự sửa code của Tài.
