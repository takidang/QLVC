# Dữ liệu thử giao diện UC-22 Xử lý đơn thất bại (UC-22-AC12)

> Tài ghi 08/11/2026. Thử trên `dev` sau khi PR #23 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC12 trong `docs/stories/UC-22-xu-ly-don-that-bai.md`.

## Chuẩn bị (chạy trọn một chuyến có đơn thất bại, như lần thử UC-19, 20)
- Điều phối: chuyến T01 ngày mai có 3 đơn: **A** (TP.HCM → Cần Thơ), **B** (TP.HCM → Tiền Giang), **C** (Long An → Cần Thơ). Chốt chuyến.
- Tài xế (`taixe` / `demo12345`, điện thoại hoặc 360 px): Bắt đầu chuyến; quét lấy **A**, **B**; **C** bấm Không lấy được (lý do phía khách + ảnh); **A** Giao không được, lý do "Người nhận vắng" (phía khách) + ảnh; **B** giao thành công; Kết thúc chuyến.
- Kết quả cần có: A `THAT_BAI` đã lấy (1 lần giao thất bại phía khách), C `THAT_BAI` chưa lấy.

Đăng nhập `dieuphoi` → **Đơn hàng**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Mở trang Đơn hàng | Thẻ "Đơn thất bại cần xử lý (2)": A "Đã lấy", 1/3, lý do "Người nhận vắng", có nút Ghép lại + Trả hàng; C "Chưa lấy", 0/3, có Ghép lại + Hủy | `a-the-that-bai.png` | |
| b | A → **Ghép lại**, không chọn nút giữ → bấm Ghép lại | Trình duyệt bắt chọn nút (ô bắt buộc); chọn nút Cần Thơ, địa chỉ "Kho Cần Thơ", hạn mới ngày kia 17:00 → báo "Đã đưa đơn … về Chờ ghép"; A biến khỏi thẻ, bảng đơn A "Chờ ghép", cước không đổi | `b-ghep-lai.png` | |
| c | C → **Hủy** → lý do "khách không gửi nữa" | C "Hủy", thẻ đơn thất bại biến mất (hết đơn) | `c-huy.png` | |
| d | (Tùy chọn, cần thêm một đơn thất bại đã lấy) → **Trả hàng** → OK | Đơn "Trả hàng" | `d-tra-hang.png` | |
| e | (Tùy chọn) Đơn đã 3 lần giao thất bại phía khách | Nút Ghép lại mờ, rê chuột hiện "Đạt 3 lần … (BR-37)" | `e-dat-nguong.png` | |

Ca d, e cần nhiều chuyến; đã có test tự động (`test_uc22_ac6_tra_hang`, `test_uc22_ac3_*`), thử giao diện nếu kịp.
