# Dữ liệu thử giao diện: UC-04, UC-05, UC-08

> Kiệt thử ngày 25/10/2026 (Edge/Chrome, tài khoản Quản lý). Kết quả đã điền vào story UC-04 (AC10), UC-05 (AC9), UC-08 (AC11); ảnh trong `docs/test-evidence/UC-04/`, `UC-05/`, `UC-08/`.
> Bằng chứng ghi ở cột "Kết quả": **ảnh** (file trong thư mục), **log** (nhật ký backend lúc thử), **test** (test tự động pytest). Ca không có bằng chứng thì ghi rõ.
> Địa chỉ lúc thử: `http://localhost:5173`. Từ 29/10 Tài đã cho Vite chạy ở `127.0.0.1`, nên `http://127.0.0.1:5173` cũng mở được.
> Chụp ảnh: **Win + Shift + S**, lưu đúng thư mục và tên ở cột "Ảnh".
> Đã chuẩn bị sẵn trong CSDL: bảng giá TP.HCM → Cần Thơ (1.500 đ/kg, tối thiểu 50.000, hiệu lực 01/10/2026); khách hàng Cty A (0909123456).
> Thứ tự: Phần 1 → Phần 2 → Phần 3 (UC-08 cần nút của UC-05).

---

## Phần 1: UC-04 Tài xế (menu "Tài xế")

Ảnh lưu vào `docs/test-evidence/UC-04/`

| Ca | Làm gì | Dữ liệu nhập | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|---|
| 1 | Thêm tài xế | Họ tên `Nguyễn Văn An` · Tên đăng nhập `an` · Mật khẩu `matkhau123` · Số GPLX `790123456789` · Hạng `C` · Hạn GPLX `31/05/2030` · SĐT `0909111222` | Lưu được, An hiện trong danh sách, trạng thái "Hoạt động" | `1-them-tai-xe.png` | Đạt (ảnh) |
| 2 | Thêm tài xế trùng số GPLX | Họ tên `Trùng GPLX` · Tên đăng nhập `trung` · Mật khẩu `matkhau123` · Số GPLX `790123456789` · Hạng `B` · Hạn `31/12/2028` · SĐT `0909000000` | Báo lỗi trùng **ngay dưới ô Số GPLX**, không lưu | `2-trung-gplx.png` | Đạt (ảnh: "Số GPLX 790123456789 đã có trong hệ thống" dưới ô) |
| 3 | Thêm tài xế hạn GPLX đã qua | Họ tên `Trần Bình` · Tên đăng nhập `binh` · Mật khẩu `matkhau123` · Số GPLX `790222333444` · Hạng `B` · Hạn GPLX `01/01/2020` · SĐT `0909222333` | Lưu được; cột Hạn GPLX **tô đỏ "(hết hạn)"** | `3-het-han-gplx.png` | Đạt (ảnh) |
| 4 | Tìm và lọc | Ô tìm gõ `nguyễn`; rồi xóa ô tìm, chọn lọc "Ngừng" | Tìm ra đúng An; lọc "Ngừng" chưa có ai | | Đạt (Kiệt thử, không chụp; log có các lượt tìm "Nguyễn" và lọc trạng thái) |
| 5 | Sửa tài xế | Bấm **Sửa** ở dòng An, đổi SĐT thành `0909111333` → Lưu | Form **không có** ô tên đăng nhập, mật khẩu; SĐT đổi trong danh sách | `6-form-sua.png` | Đạt (ảnh: form sửa không có ô tên đăng nhập, mật khẩu) |
| 6 | Ngừng tài xế | Bấm **Ngừng** ở dòng An → bấm OK | Có hộp hỏi xác nhận; dòng An mờ đi, trạng thái "Ngừng" | `4-ngung-tai-xe.png` | Đạt (ảnh, thử ngừng với tài xế Bình) |
| 7 | Tài khoản bị khóa (tùy chọn) | Mở **cửa sổ ẩn danh** (Ctrl + Shift + N), vào http://localhost:5173, đăng nhập `an` / `matkhau123` | Không đăng nhập được | | Đạt (log: đăng nhập tài xế đã ngừng → 403 "Tài khoản đã bị khóa"; ảnh `5-tai-xe-bi-khoa-tk.png` chụp trùng ảnh 4 nên Tài đã bỏ) |
| 8 | Hoạt động lại | Ở cửa sổ chính, bấm **Hoạt động lại** ở dòng An | Trạng thái về "Hoạt động"; ẩn danh đăng nhập `an` lại được | | Không có bằng chứng thử tay; đã có test tự động `test_uc04_ac8_ngung_khoa_tai_khoan_va_mo_lai` (đạt) |
| 9 | Dữ liệu sai | Thêm tài xế mật khẩu `1234567` (7 ký tự), các ô khác như ca 1 nhưng tên đăng nhập `sai`, số GPLX `111111` | Báo lỗi mật khẩu, không lưu | | Log có 1 lần thêm tài xế bị 400 (dữ liệu sai), không chụp; đã có test tự động `test_uc04_ac2_du_lieu_sai_bi_chan` (đạt) |

---

## Phần 2: UC-05 Nút, Tuyến (Tài giao)

Ảnh lưu vào `docs/test-evidence/UC-05/`

### Ca a: thêm 5 nút (menu "Nút" → Thêm nút)

Ô **Tỉnh** phải gõ đúng như bảng giá (`TP.HCM`, `Cần Thơ`) thì UC-08 mới tra được giá. Vĩ độ, kinh độ không bắt buộc, điền để đủ dữ liệu.

| # | Tên nút | Tỉnh (tra bảng giá) | Loại | Vĩ độ | Kinh độ |
|---|---|---|---|---|---|
| 1 | `TP.HCM` | `TP.HCM` | Tỉnh/thành | `10.7769` | `106.7009` |
| 2 | `Long An` | `Long An` | Tỉnh/thành | `10.5359` | `106.4137` |
| 3 | `Tiền Giang` | `Tiền Giang` | Tỉnh/thành | `10.3600` | `106.3600` |
| 4 | `Vĩnh Long` | `Vĩnh Long` | Tỉnh/thành | `10.2537` | `105.9722` |
| 5 | `Cần Thơ` | `Cần Thơ` | Tỉnh/thành | `10.0452` | `105.7469` |

Kết quả đúng: lưu được cả 5, hiện trong danh sách. Kết quả: **Đạt** (log: 5 lần thêm nút thành công; Kiệt đặt tên nút `hcm1`, `longan1`… thay cho tên tỉnh, ô Tỉnh vẫn đúng)

### Ca b: tuyến T01 hợp lệ (menu "Tuyến" → Thêm tuyến)

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

### Ca c: tuyến T02 thiếu điểm nghỉ (vẫn lưu được)

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

### Ca d: tuyến quá 10 giờ (bị chặn)

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

---

## Phần 3: UC-08 Đơn hàng (Tài giao)

Ảnh lưu vào `docs/test-evidence/UC-08/`

### Ca e: tạo đơn hợp lệ (menu "Đơn hàng" → Tạo đơn)

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

### Ca f: địa chỉ giao trùng địa chỉ lấy (bị chặn BR-31)

Như ca e, **giữ nút lấy TP.HCM, nút giao Cần Thơ** (để có bảng giá), chỉ đổi:

| Ô | Giá trị |
|---|---|
| Địa chỉ giao | `12 Nguyễn Huệ, Quận 1` (giống hệt địa chỉ lấy) |

Kết quả đúng: báo lỗi **BR-31**, không lưu. Ảnh `f-trung-dia-chi.png`. Kết quả: **Đạt** (ảnh: "Địa chỉ lấy trùng địa chỉ giao")

### Ca g: chưa có bảng giá (nút Lưu bị khóa)

Như ca e, chỉ đổi chiều:

| Ô | Giá trị |
|---|---|
| Nút lấy | `Cần Thơ` |
| Nút giao | `TP.HCM` |

Kết quả đúng: báo **"Chưa có bảng giá"**, nút **Lưu bị khóa** (chỉ có giá TP.HCM → Cần Thơ, chưa có chiều ngược). Kết quả: **Đạt** (ảnh `e-chua-co-tuyen.png` TP.HCM → TP.HCM và `e-chua-co-tuyen-nguoc-lai.png` Cần Thơ → TP.HCM: báo chưa có bảng giá, nút Lưu khóa)

---

## Ghi chú khi thử

- Địa chỉ `http://127.0.0.1:5173` lúc thử không mở được trên máy Kiệt, phải dùng `http://localhost:5173`. **Tài đã sửa 29/10** (Vite chạy ở `127.0.0.1`).
- Thông báo lỗi BR-66, BR-31 lúc thử chưa hiện mã BR. **Tài đã sửa 29/10** (lỗi nghiệp vụ hiện kèm mã, ví dụ "… (BR-66)").
- Ca nào sai: ghi lại "làm gì → thấy gì" vào đây. Không tự sửa code của Tài.

