# Dữ liệu thử giao diện UC-33 Báo sự cố (UC-33-AC9)

> Kiệt ghi 10/11/2026. **Tài thử** (người kia, theo `story-flow`) trên `dev` sau khi PR UC-33 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC9 trong `docs/stories/UC-33-bao-su-co.md`.

## Chuẩn bị

- Điều phối: chuyến T01 **hôm nay** (tài xế chỉ bắt đầu được đúng ngày khởi hành, BR-26), ghép 1–2 đơn, chốt.
- Tài xế (`taixe` / `demo12345`, điện thoại hoặc 360 px): mở chuyến → **Bắt đầu chuyến** (km + ảnh đồng hồ).
- Không có gói mới, không có migration mới.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Tài xế mở chuyến đang chạy, kéo xuống khối **Sự cố** | Khối có dòng "Chưa báo sự cố nào" và form: Loại sự cố (5 loại), Ghi chú, Ảnh (không bắt buộc, tối đa 5), nút **Báo sự cố** | `a-khoi-su-co.png` | Đạt (form 5 loại, Ghi chú, Ảnh không bắt buộc; chuyến đã có sự cố nên không có dòng "Chưa báo") |
| b | Để trống Ghi chú → **Báo sự cố** | Báo đỏ "Ghi rõ sự cố trước khi báo", không gửi | `b-trong-ghi-chu.png` | Đạt ("Ghi rõ sự cố trước khi báo") |
| c | Loại **Hỏng xe**, ghi chú "Nổ lốp sau ở km 45", chụp 1 ảnh → **Báo sự cố** | Xanh "Đã báo sự cố hỏng xe, Điều phối sẽ xử lý"; danh sách có "Hỏng xe · giờ", nhãn đỏ **Đang mở**, "… · 1 ảnh"; chuyến vẫn **Đang chạy** | `c-da-bao.png` | Đạt ("Đã báo sự cố hỏng xe…", nhãn đỏ Đang mở, 1 ảnh) |
| d | Loại **Kẹt xe / tắc đường**, ghi chú, **không** chụp ảnh → Báo | Báo được, dòng "· 0 ảnh" | – | Đạt (dòng "Kẹt xe / tắc đường · 0 ảnh") |
| e | Đăng nhập `dieuphoi` → **Chuyến** → chọn ngày hôm nay | Chuyến có cờ đỏ **Sự cố** | `e-co-su-co.png` | Đạt (CH-261110-04 cờ đỏ Sự cố) |
| f | Mở chi tiết chuyến → khối **Sự cố** → nhập cách xử lý "Gọi cứu hộ thay lốp" → **Đóng sự cố**, đóng **hết** sự cố đang mở của chuyến (cờ chỉ mất khi không còn sự cố mở) | Sự cố "Đã đóng"; bảng chuyến hết cờ Sự cố (đây cũng là **UC-32 ca e**) | `f-dong-su-co.png` | Đạt (đóng 5/5 sự cố; bảng chuyến hết cờ Sự cố, còn "Đơn thất bại", "Chưa quyết toán") |
| g | Đăng nhập lại `taixe` → mở chuyến | Sự cố đã đóng có nhãn xám **Đã xử lý** và dòng "Điều phối: Gọi cứu hộ thay lốp" | `g-tai-xe-thay-xu-ly.png` | Đạt (nhãn xám "Đã xử lý", "Điều phối: Gọi cứu hộ thay lốp") |
| h | Tài xế **Kết thúc chuyến** (hoặc Điều phối kết thúc do sự cố) rồi mở lại chuyến | Khối Sự cố chỉ còn danh sách, không còn form báo | `h-chuyen-da-ve.png` | Đạt (Điều phối kết thúc do sự cố vì còn đơn chưa lấy, BR-28; khối Sự cố chỉ còn danh sách, không còn form) |

## Không thử tay (có test tự động)

| Nội dung | Test |
|---|---|
| 6 ảnh, ảnh sai loại, ảnh > 500 KB, ghi chú 501 ký tự, loại sai, trường lạ | `test_uc33_ac2_*`, `test_uc33_ac3_*` |
| Chuyến đã chốt / đã về / đã quyết toán → 409; chuyến người khác, Đang lập, Hủy → 404 | `test_uc33_ac4_*` |
| Điều phối, Kế toán, Quản lý gọi API → 403; chưa đăng nhập → 401 | `test_uc33_ac5_*` |
| CSDL / đĩa lỗi giữa chừng không để ảnh mồ côi | `test_uc33_ac8_loi_giua_chung` |

## Lưu ý

- Trang Điều phối và dòng thời gian (code UC-32) tạm hiện **mã** loại (`HONG_XE`, `KET_XE`…), không phải tên tiếng Việt: UC-33 bỏ quyết định 7, không sửa code UC-32. Bảng tên có sẵn ở `frontend/src/api/suCo.ts` (`TEN_LOAI_SU_CO`) nếu Tài muốn dùng.

## Kết quả thử (Kiệt, 10/11/2026)

Kiệt thử tay trên máy (360 px tài xế, 1440 px Điều phối), nhánh `kiet/uc-33-bao-su-co`, chuyến CH-261110-04 (T01 23:05 hôm nay, `taixe`, xe 51C-150.00). Chuyến có thêm 4 sự cố 18:50, 18:51 do Claude báo khi thử nhanh trước đó; sự cố 19:22 là Kiệt báo.

- **8/8 ca a–h đạt.** Ca f cũng là UC-32 ca e (đóng sự cố, mất cờ).
- Như dự kiến khi bỏ quyết định 7: trang Điều phối và dòng thời gian hiện mã `HONG_XE`, `KET_XE`.
