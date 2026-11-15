# Dữ liệu thử giao diện UC-25 Công nợ (AC10)

> Claude ghi 09/11/2026 cho Kiệt thử trên nhánh `kiet/uc-25-cong-no` (đã gộp `dev`). Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC10 trong `docs/stories/UC-25-cong-no.md`.

## Chuẩn bị (CSDL máy Kiệt)

- 3 khoản phải thu của **Cty A**, đều **chưa thu** (sinh khi giao ở UC-20 và khi thử PR #21): **DH-MSKG7T** 2.997.000, **DH-6HXV2Y** 800.000, **DH-S4JPYG** 800.000 → Cty A nợ **4.597.000**.
- CSDL chỉ có một khách nên không thử được "khoản của hai khách" trên giao diện (giao diện chỉ cho chọn khoản của khách đang xem); ca này có test tự động `test_uc25_ac4_khac_khach`.
- Đăng nhập Kế toán `ketoan` / `demo12345` (hoặc `thu`). Máy tính, cửa sổ thường. Không có gói mới, không có migration mới.
- **Kiểm app đang chạy đúng nhánh UC-25:** menu Kế toán phải có **Công nợ**. Không có menu này, hoặc trang báo "Có lỗi (mã 404)", nghĩa là backend / frontend còn chạy nhánh khác → nhờ Claude khởi động lại backend rồi **F5**.
- Đánh dấu đã thu **không bỏ được** (quyết định 5), nên làm đúng thứ tự a → h; các bước bị từ chối hoặc bấm Hủy không lưu gì.

## Các ca

Menu **Công nợ** (giữa "Chi phí cố định xe" và "Tạm ứng").

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Mở **Công nợ** | Bảng nợ theo khách: **Cty A · 3 khoản · 4.597.000 đ** | `a-no-theo-khach.png` | Đạt |
| b | Cty A → **Xem** | Bảng "Khoản của Cty A", nút **Chưa thu** đang chọn, 3 khoản có ô tích, cột giờ giao; "Đã chọn 0 khoản · 0 đ", ô **Ngày thu** = hôm nay, nút **Đánh dấu đã thu** mờ | `b-khoan-chua-thu.png` | Đạt |
| c | Tích **DH-6HXV2Y**, **DH-S4JPYG** và **DH-MSKG7T**, rồi bỏ tích DH-MSKG7T | Lúc 3 khoản: "Đã chọn 3 khoản · 4.597.000 đ"; bỏ tích còn "Đã chọn 2 khoản · 1.600.000 đ"; nút sáng | `c-chon-hai-khoan.png` | Đạt |
| d | Ô Ngày thu: mở lịch thử chọn **ngày mai**; rồi **gõ tay** ngày mai vào ô → **Đánh dấu đã thu** → **OK** | Lịch làm mờ các ngày sau hôm nay. Gõ tay được thì máy chủ báo đỏ "Ngày thu không được sau hôm nay", 2 khoản vẫn chưa thu | `d-ngay-mai.png` | Đạt (gõ tay 10/11 → máy chủ báo "Ngày thu không được sau hôm nay", không đổi gì) |
| e | Ngày thu **hôm qua** → **Đánh dấu đã thu** → hộp hỏi "Đã thu 1.600.000 đ của Cty A (2 khoản) ngày …?" → bấm **Hủy** trước | Không lưu gì: 2 khoản vẫn được tích, nợ vẫn 4.597.000 đ | – | Đạt |
| e2 | Bấm **Đánh dấu đã thu** lại → **OK** | Xanh "Đã lập phiếu thu #…: 1.600.000 đ (2 khoản)"; bảng còn **DH-MSKG7T**, "Đã chọn 0 khoản"; bảng nợ: **Cty A · 1 khoản · 2.997.000 đ** | `e-da-thu.png` | Đạt (Kiệt chọn ngày **hôm nay** 09/11 thay vì hôm qua; nhập ngày trước đó kiểm bằng `test_uc25_ac5_id_trung_va_ngay_mai`) |
| f | Bấm **Đã thu** | 2 khoản DH-6HXV2Y, DH-S4JPYG, cột "Phiếu thu" có **#số · ngày hôm qua**; không có ô tích | `f-da-thu-list.png` | Đạt |
| g | Về **Chưa thu**, tích **DH-MSKG7T**, ngày **hôm nay** → **Đánh dấu đã thu** → **OK** | Phiếu thu thứ hai 2.997.000 đ; bảng nợ "Không khách nào còn nợ"; tab Chưa thu "Không còn khoản chưa thu", không còn ô ngày / nút | `g-het-no.png` | Đạt |
| h | Menu **Đơn hàng** không có với Kế toán → đăng nhập `dieuphoi` → **Đơn hàng** | DH-MSKG7T, DH-6HXV2Y, DH-S4JPYG vẫn **Đã giao** (đã thu không đổi trạng thái đơn, BR-56) | `h-don-van-da-giao.png` | Đạt |

## Không thử tay (có test tự động)

| Nội dung | Vì sao không thử tay | Test |
|---|---|---|
| Khoản của **hai khách** trong một lần → 422 BR-56 | Máy Kiệt chỉ có một khách; giao diện cũng chỉ cho tích khoản của khách đang xem | `test_uc25_ac4_khac_khach` |
| Khoản **đã thu** bị đánh dấu lại → 409 BR-56 (cả lô không đổi) | Giao diện ẩn ô tích của khoản đã thu | `test_uc25_ac3_mot_khoan_va_da_thu` |
| Hai Kế toán đánh dấu **cùng lúc** → một lần được | Cần hai người bấm cùng lúc | `test_uc25_ac6_dong_thoi` |
| **Quản lý** xem được, không ghi được | Giao diện chưa có trang Công nợ cho Quản lý (menu Quản lý không gồm trang Kế toán); chỉ API | `test_uc25_ac9_*` |
| Lọc, phân trang, `tong_tien` của `GET /api/phai-thu` | Giao diện dùng 100 khoản / khách, không phân trang | `test_uc25_ac7_danh_sach` |

## Sau khi thử

Claude kiểm CSDL:
- 2 `phieu_thu` của Cty A: 1.600.000 ngày **hôm qua** (DH-6HXV2Y, DH-S4JPYG) và 2.997.000 ngày **hôm nay** (DH-MSKG7T); người tạo là Kế toán.
- 3 `phai_thu` `DA_THU`, đúng `phieu_thu_id`; không có phiếu thu nào từ các lần bị từ chối hoặc bấm Hủy (ca d, e).
- 3 dòng `nhat_ky_tien` bảng `phai_thu` `DA_THU` (cũ `CHUA_THU`), lý do có số phiếu và ngày; dòng `TAO` của UC-20 giữ nguyên.
- Trạng thái 3 đơn vẫn `DA_GIAO`.

### Kết quả (Kiệt thử 09/11/2026, Claude kiểm CSDL)

- 9/9 ca đạt (a–h, e2).
- CSDL: phiếu thu #1 1.600.000 (DH-6HXV2Y, DH-S4JPYG) và #2 2.997.000 (DH-MSKG7T), cùng Cty A, ngày 09/11, người tạo `thu`; 3 `phai_thu` `DA_THU` đúng `phieu_thu_id`; 3 dòng `nhat_ky_tien` `DA_THU` có "Phiếu thu #… ngày 09/11/2026"; 3 đơn vẫn `DA_GIAO`. Không có phiếu nào từ ca d (bị từ chối) và ca e (bấm Hủy).

## Thử lại trên giao diện v2 (Kiệt, 12/11/2026)

Màn Công nợ v2 (nhánh `tai/thu-giao-dien-v2` 30949bf: chọn khách ở danh sách trái, khoản bên phải), backend `dev` (93ab7eb), dữ liệu demo.

- Đạt: khối số trên cùng (tổng nợ, số khoản, số khách); khách nợ nhiều trước; chọn **Cty Dược phẩm An Khang** → tab Chưa thu có ô tích, "Đã chọn N khoản · … đ" đổi theo, lịch không cho chọn ngày mai; đánh dấu đã thu DH-S8X868 + DH-BJC7N3 → phiếu thu **#7 · 2.998.000 đ** ngày 12/11, khách còn 1 khoản 800.000; tab Đã thu có số phiếu, ngày thu, không ô tích; đơn vẫn "Đã giao". Ảnh `j-v2-chon-khach.png`, `i-v2-da-thu.png`.
