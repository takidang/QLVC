# Dữ liệu thử giao diện UC-04 Tài xế

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).
> Kiệt thử ngày 25/10/2026 (Edge/Chrome, tài khoản Quản lý). Kết quả đã điền vào story UC-04 (AC10), UC-05 (AC9), UC-08 (AC11); ảnh trong `docs/test-evidence/UC-04/`, `UC-05/`, `UC-08/`.
> Bằng chứng ghi ở cột "Kết quả": **ảnh** (file trong thư mục), **log** (nhật ký backend lúc thử), **test** (test tự động pytest). Ca không có bằng chứng thì ghi rõ.
> Địa chỉ lúc thử: `http://localhost:5173`. Từ 29/10 Tài đã cho Vite chạy ở `127.0.0.1`, nên `http://127.0.0.1:5173` cũng mở được.
> Chụp ảnh: **Win + Shift + S**, lưu đúng thư mục và tên ở cột "Ảnh".
> Đã chuẩn bị sẵn trong CSDL: bảng giá TP.HCM → Cần Thơ (1.500 đ/kg, tối thiểu 50.000, hiệu lực 01/10/2026); khách hàng Cty A (0909123456).
> Thứ tự: Phần 1 → Phần 2 → Phần 3 (UC-08 cần nút của UC-05).

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
