# Dữ liệu thử giao diện: UC-04, UC-05, UC-08, UC-02, UC-11, UC-13, UC-17, UC-18

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

## Phần 4: UC-02 Người dùng (menu "Người dùng", chỉ Quản lý thấy)

Ảnh lưu vào `docs/test-evidence/UC-02/` · Kiệt thử 30/10/2026 (nhánh `kiet/uc-02-nguoi-dung`).

**Tài khoản có sẵn trong CSDL máy Kiệt lúc thử** (mật khẩu thật không ghi vào đây):

| Tên đăng nhập | Vai trò | Ghi chú |
|---|---|---|
| `kiet` | Quản lý | Tạo 30/10 bằng `python -m app.tao_quan_ly`, dùng để thử UC-02 |
| `kietquanly` | Quản lý | Tài khoản cũ quên mật khẩu, khóa ở ca c |
| `an` | Tài xế | Tạo ở UC-04 ca 1, mật khẩu `matkhau123` |
| `binh` | Tài xế | Tạo ở UC-04 ca 3, đang `NGUNG` |

| Ca | Làm gì | Dữ liệu nhập | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|---|
| a | Thêm người dùng | Tên đăng nhập `thu` · Họ tên `Lê Thị Thu` · Mật khẩu `matkhau123` · Vai trò **Kế toán** | Dòng `thu` hiện trong bảng, "Hoạt động" | `a-them-nguoi-dung.png` | Đạt (ảnh: dòng `thu` Kế toán, Hoạt động; dòng `kiet (bạn)`, `an`, `binh` không có nút Khóa) |
| b | Thêm trùng tên đăng nhập | Tên đăng nhập `binh` (trùng tài xế) · Họ tên `Trùng` · Mật khẩu `matkhau123` · Vai trò Kế toán | Báo **"Tên đăng nhập binh đã có người dùng"** ngay dưới ô, không lưu | `b-trung-ten-nguoi-dung.png` | Đạt (ảnh) |
| c | Khóa tài khoản | Bấm **Khóa** ở dòng `kietquanly` → OK | Hỏi xác nhận; trạng thái thành "Đã khóa". Dòng `kiet (bạn)` và dòng tài xế `an`, `binh` **không có** nút Khóa | `c-khoa-tai-khoan.png` | Đạt (ảnh hộp xác nhận "Người này bị đăng xuất ngay"; CSDL sau đó `kietquanly` = `NGUNG`) |
| d | Sửa tài xế | Bấm **Sửa** ở dòng `an` | Không có ô chọn vai trò, hiện "Vai trò: Tài xế (đổi ở trang Tài xế)" | `d-sua.png` | Đạt (ảnh) |
| e | Đặt lại mật khẩu | Dòng `thu`: nhập `abc1234` (7 ký tự) → Lưu; rồi `matkhau456` → Lưu | 7 ký tự bị chặn (cần ít nhất 8); 8 ký tự trở lên hiện "Đã đặt mật khẩu mới…" | `e-dat-lai-mat-khau.png` | Đạt (ảnh bước 8 ký tự; bước 7 ký tự bị trình duyệt chặn – Kiệt xác nhận, không chụp; máy chủ cũng chặn: test `test_uc02_ac7_mat_khau_sai`) |
| f | Lọc và tìm | Lọc vai trò **Tài xế**; rồi "Mọi vai trò" + gõ `thu` | Chỉ còn `an`, `binh`; rồi chỉ còn `thu` | `f-loc-tim-kiem.png` | Đạt (ảnh: lọc Kế toán + tìm `thu` còn 1 dòng; lọc Tài xế thử tay không chụp) |

Sau khi thử (kiểm CSDL 30/10): `thu` có mật khẩu `matkhau456`; `kietquanly` đã đổi sang Điều phối và khóa (muốn dùng lại: đăng nhập `kiet` → Mở khóa → Đặt lại mật khẩu); họ tên tài xế `an` đã thành `Nguyễn Văn A` lúc thử ca d (sửa lại `Nguyễn Văn An` nếu cần cho kịch bản mục 11).

---

## Phần 5: UC-11 Lập chuyến (Tài giao 30/10)

Ảnh lưu vào `docs/test-evidence/UC-11/` · Số liệu theo kịch bản `nghiep-vu.md` mục 11. **"Ngày mai" = 31/10/2026** (thử tối 30/10). Thử sang ngày 31/10 thì đổi hết thành 01/11.

### Chuẩn bị (làm một lần, dùng chung cho Phần 5 và 6)

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

---

## Phần 6: UC-13 Ghép đơn (Tài giao 30/10, làm sau Phần 5)

Ảnh lưu vào `docs/test-evidence/UC-13/` · Dùng luôn **chuyến CH-261031-01** (X1, An, 06:00 ngày 31/10) vừa lập ở Phần 5 ca c.

### Chuẩn bị

**Bảng giá** (menu Bảng giá → Thêm mức giá; mỗi dòng dưới là một lần thêm, nhập đủ 5 ô theo đúng thứ tự trên form):

| # | Tỉnh lấy | Tỉnh giao | Đơn giá (đồng/kg) | Cước tối thiểu (đồng) | Hiệu lực từ ngày |
|---|---|---|---|---|---|
| 1 | `Long An` | `Cần Thơ` | `1200` | `50000` | `01/10/2026` |
| 2 | `TP.HCM` | `Tiền Giang` | `1000` | `50000` | `01/10/2026` |

Tên tỉnh gõ **đúng như tên nút** (`TP.HCM`, `Long An`, `Tiền Giang`, `Cần Thơ`), nếu không thì tạo đơn sẽ báo "Chưa có bảng giá". Giá `TP.HCM → Cần Thơ` 1.500 đã có từ lần thử UC-08, không thêm lại.

**4 đơn** (menu Đơn hàng → Tạo đơn). Mỗi dòng là một đơn; các cột xếp **đúng thứ tự ô trên form** từ trái sang phải. Nút hiện dạng `tên (tỉnh)`, ví dụ `hcm1 (TP.HCM)`.

| Đơn | Khách hàng | Mô tả hàng | Khối lượng thực (kg) | Thể tích (m³) | Số kiện | Nút lấy | Địa chỉ lấy | Người liên hệ | SĐT lấy | Lấy từ | Lấy đến | Nút giao | Địa chỉ giao | Người nhận | SĐT nhận | Hạn giao | Cước tự hiện (kiểm, không nhập) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Đ1** | `Cty A` | `Hàng điện tử` | `1800` | `6` | `10` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `cantho1 (Cần Thơ)` | `45 Hòa Bình, Ninh Kiều` | `Chị Lan` | `0939111222` | `31/10/2026 14:00` | 2.997.000 |
| **Đ2** | `Cty A` | `Nông sản` | `1200` | `3` | `8` | `longan1 (Long An)` | `8 Quốc lộ 1A, Tân An` | `Chị Mai` | `0909555666` | `31/10/2026 06:30` | `31/10/2026 09:00` | `cantho1 (Cần Thơ)` | `10 Trần Hưng Đạo, Ninh Kiều` | `Anh Minh` | `0939222333` | `31/10/2026 12:00` | 1.440.000 |
| **Đ4** | `Cty A` | `Văn phòng phẩm` | `800` | `2` | `5` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `tiengiang1 (Tiền Giang)` | `5 Ấp Bắc, Mỹ Tho` | `Chị Hoa` | `0939333444` | `31/10/2026 18:00` | 800.000 |
| **Đ8** | `Cty A` | `Phụ tùng` | `300` | `1` | `2` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `tiengiang1 (Tiền Giang)` | `20 Lê Lợi, Mỹ Tho` | `Anh Tú` | `0939444555` | `31/10/2026 18:00` | 333.000 |

**Mã đơn hệ thống sinh trên máy Kiệt (30/10)** – mã ngẫu nhiên, máy khác sẽ khác:

| Đơn | Mã | Nhận biết |
|---|---|---|
| Đ1 | `DH-MSKG7T` | TP.HCM → Cần Thơ, 1.800 kg, hạn 14:00 31/10 |
| Đ2 | `DH-9ZTTPG` | Long An → Cần Thơ, 1.200 kg, lấy 06:30–09:00 |
| Đ4 | `DH-6HXV2Y` | TP.HCM → Tiền Giang, 800 kg |
| Đ8 | `DH-SZAK8H` | TP.HCM → Tiền Giang, 300 kg |
| bỏ qua | `DH-79S3VJ` | Đơn cũ lần thử UC-08 (hạn 26/10), **không tick** |

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Chuyến → bấm **mã CH-261031-01** | Trang chi tiết: lịch trình trống, **lãi dự kiến âm, tô đỏ** | `a-chuyen-trong.png` | Đạt (ảnh: lãi −1.600.000 đ chữ đỏ) |
| b | Ở "Đơn chờ ghép" tick `DH-MSKG7T` (Đ1) và `DH-6HXV2Y` (Đ4) → **Ghép đơn đã chọn** | Lịch trình **4 điểm** | `b-ghep-d1-d4.png` | Đạt (ảnh: 4 điểm, tải 2.600 kg, lãi 2.197.000 đ) |
| c | Tick `DH-9ZTTPG` (Đ2) → **Ghép đơn đã chọn** | 6 điểm, ETA **06:00 / 06:20 / 07:40 / 09:00 / 11:50** (giao Đ2) / **12:10** (giao Đ1); tải **3.800 / 5.000 kg**, lấp đầy **76%**, lãi **3.637.000 đ** | `c-ghep-don-d2.png` | Đạt (ảnh: đúng 6 ETA, 3.800/5.000 kg, 76%, 3.637.000 đ) |
| d | Tick `DH-SZAK8H` (Đ8) → **Ghép đơn đã chọn** | Bảng vi phạm: đơn **Đ2 (`DH-9ZTTPG`), BR-06**, ETA giao **12:30** sau hạn 12:00; Đ8 **không** được ghép | `d-vi-pham-thoi-gian-d8.png` | Đạt (ảnh: 1 dòng `DH-9ZTTPG` BR-06, ETA 12:30 sau hạn 12:00) |
| e | Ở "Đơn đang ghép" tick `DH-6HXV2Y` (Đ4) → **Gỡ đơn đã chọn** | Lịch trình còn **4 điểm**, Đ4 về danh sách chờ ghép | `e-go-don-d4.png` | Đạt (ảnh: còn 4 điểm, `DH-6HXV2Y` về chờ ghép) |

Ảnh phụ `f-don-qua-han-vuot-tai-trong-vipham.png`: lỡ tick đơn cũ `DH-79S3VJ` (1.800 kg, hạn 26/10) → bị chặn đủ 4 dòng: BR-01 tổng 5.600 kg > 5.000, BR-05 trễ khung lấy, BR-06 trễ hạn của chính nó và của `DH-9ZTTPG`. Đúng.

**Ghi chú cho Tài:** ở TP.HCM lịch trình lấy `DH-6HXV2Y` (Đ4) lúc 06:00 rồi `DH-MSKG7T` (Đ1) lúc 06:20; kịch bản mục 11 ghi lấy Đ1 trước. ETA các điểm sau vẫn đúng, chỉ khác thứ tự hai đơn lấy cùng nút.

Lãi ở ca c: cước 2.997.000 + 1.440.000 + 800.000 = 5.237.000 − định mức 1.000.000 − lương 600.000 = 3.637.000 đ.
Xong ghi kết quả vào dòng **AC13** của `docs/stories/UC-13-ghep-don.md`.

---

## Phần 7: UC-17 Xem chuyến được giao (tài xế, điện thoại)

Ảnh lưu vào `docs/test-evidence/UC-17/` · Kiệt thử 31/10/2026 (nhánh `kiet/uc-17-xem-chuyen`).

### Chuẩn bị

- Dùng chuyến **CH-261031-01** của Phần 5, 6 (T01, xe `51C-111.11`, tài xế An, 06:00 31/10, 3 đơn `DH-MSKG7T`, `DH-9ZTTPG`, `DH-6HXV2Y`).
- UC-15 (Chốt chuyến) chưa có, nên 31/10 Claude đổi thẳng trong CSDL thử: `trang_thai = DA_CHOT`, `luong_tai_xe_chot = 600000` (lương khoán T01). Định mức chốt và ETA kế hoạch để trống → giờ tự tính lại (quyết định UC-17 số 4). Muốn thử lại UC-13 thì nhờ Claude đổi về `LAP`.
- **Chạy lại backend** sau khi chuyển nhánh (`Ctrl + C` rồi chạy lại lệnh uvicorn); frontend tự cập nhật.
- Giả lập điện thoại: Chrome/Edge `http://127.0.0.1:5173` → `F12` → `Ctrl + Shift + M` → chiều ngang **360**.
- Đăng xuất Quản lý, đăng nhập tài xế `an` / `matkhau123` (đặt ở Phần 1).

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Đăng nhập `an` | Vào thẳng **Chuyến của tôi**, thẻ **Cần làm** có CH-261031-01 ("Chờ chạy", T01, xe 51C-111.11, 3 đơn); **không** có thanh cuộn ngang | `a-can-lam.png` | Đạt (ảnh; Kiệt xác nhận xem ở khổ 360 không cuộn ngang, ảnh chụp khổ rộng) |
| b | Bấm thẻ **Đã xong** | Báo "Chưa có chuyến đã xong" | `b-da-xong.png` | Đạt (ảnh) |
| c | Quay lại **Cần làm**, bấm vào CH-261031-01 | Lịch trình **6 điểm** (06:00 … 12:10); mỗi điểm có mã đơn, khách, kg/m³/kiện, địa chỉ, người liên hệ, SĐT **gạch chân bấm gọi được**, khung lấy hoặc hạn giao; có **"Lương chuyến 600.000 đ"**; **không** thấy cước, lãi | `c-lich-trinh.png` | Đạt (ảnh: 6 điểm 06:00…12:10, SĐT là link gọi, "Lương chuyến 600.000 đ", không có cước) |
| d | Bấm **← Chuyến của tôi** | Về lại danh sách | – | Đạt (Kiệt xác nhận) |

Lỗi bắt được khi thử: bấm lại thẻ **Cần làm** đang chọn thì kẹt "Đang tải…" (danh sách bị xóa mà không tải lại). Đã sửa 31/10 (`ChuyenCuaToi.tsx`: bấm lại thẻ đang chọn thì không làm gì), Kiệt thử lại đạt.

Xong ghi kết quả vào dòng **AC10** của `docs/stories/UC-17-xem-chuyen-duoc-giao.md`.

---

## Phần 8: UC-18 Bắt đầu / kết thúc chuyến (tài xế, điện thoại)

Ảnh lưu vào `docs/test-evidence/UC-18/` · Kiệt thử 31/10/2026 (nhánh `kiet/uc-18-bat-dau-ket-thuc`).

### Chuẩn bị

- Dùng tiếp chuyến **CH-261031-01** (đã `DA_CHOT` ở Phần 7). Chuyến chạy **ngày 31/10** nên **chỉ thử được trong ngày 31/10** (BR-26); thử ngày khác sẽ bị báo BR-26 – nhờ Claude đổi ngày khởi hành của chuyến.
- Xe `51C-111.11` trên máy Kiệt có km đồng hồ **50.000** (lúc thêm xe ở Phần 5 nhập 50.000, không phải 120.000 như bảng chuẩn bị).
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

---

## Ghi chú khi thử

- Địa chỉ `http://127.0.0.1:5173` lúc thử không mở được trên máy Kiệt, phải dùng `http://localhost:5173`. **Tài đã sửa 29/10** (Vite chạy ở `127.0.0.1`).
- Thông báo lỗi BR-66, BR-31 lúc thử chưa hiện mã BR. **Tài đã sửa 29/10** (lỗi nghiệp vụ hiện kèm mã, ví dụ "… (BR-66)").
- Ca nào sai: ghi lại "làm gì → thấy gì" vào đây. Không tự sửa code của Tài.

