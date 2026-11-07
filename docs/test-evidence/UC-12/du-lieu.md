# Dữ liệu thử giao diện UC-12 Đổi xe / tài xế (UC-12-AC5)

> Claude ghi 07/11/2026 theo dòng "30/10 – Tài → Kiệt: … thử thêm UC-12" trong `docs/TIEN-DO.md`; Kiệt thử trên `dev`. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC5 trong `docs/stories/UC-12-doi-xe-tai-xe.md`.

## Chuẩn bị (CSDL máy Kiệt, 07/11/2026)

- `python -m app.tai_khoan_demo` → `dieuphoi`, `ketoan`, `taixe` / `demo12345` ("Tài xế Demo", hạng C).
- Xe: **51C-111.11** (5.000 kg), **51C-222.22** (5.000 kg, mới), **51C-150.00** (1.500 kg, KTT toàn bộ 3.400 kg, mới), 51C-333.33 (Ngừng).
- Tài xế: An (C), Bình (**B**), Tài xế Demo (C).
- Đơn cho **08/11/2026** (tạo qua API, cước theo bảng giá): Đ1 **DH-B582U9** (TP.HCM → Cần Thơ, 1.800 kg, hạn 14:00), Đ2 **DH-HC63DS** (Long An → Cần Thơ, 1.200 kg, lấy 06:30–09:00, hạn 12:00), Đ4 **DH-PK9DZK** (TP.HCM → Tiền Giang, 800 kg, hạn 18:00), Đ8 **DH-LMNRRH** (TP.HCM → Tiền Giang, 300 kg, hạn 18:00).
- Chuyến **CH-261108-01** (T01, 08/11 06:00, 51C-111.11, An, **Đang lập**, chưa có đơn) – còn lại sau khi thử UC-23.

Đăng nhập `dieuphoi` / `demo12345` → **Chuyến** → mở **CH-261108-01**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | **Ghép trước** Đ1, Đ4 (tải 2.600 kg) → bấm **Đổi xe / tài xế** | Xe bị loại không có trong ô chọn mà hiện thành dòng lý do bên dưới: **51C-150.00 (1.500 kg): … (BR-01)**, 51C-333.33: … ngừng hoạt động (BR-11); ô chọn có 51C-111.11, 51C-222.22. (Chưa ghép đơn thì 51C-150.00 vẫn chọn được – đúng) | `a-xe-bi-loai.png` | Đạt (máy chủ chặn BR-01 kèm mã; xem ghi nhận 1) |
| b | Chọn **51C-222.22** → xem ô tài xế | Dòng lý do **Trần Bình (hạng B): … (BR-14)** (hạng B không lái xe KTT 9.500 kg), Bình không có trong ô chọn; An, Tài xế Demo chọn được | `b-tai-xe-bi-loai.png` | Đạt |
| c | Chọn **Tài xế Demo** → **Lưu** | Đầu trang đổi thành "Xe **51C-222.22** · Tài xế Tài xế Demo"; lịch trình, đơn ghép giữ nguyên | `c-da-doi.png` | Đạt |

Sau ca c, chuyến CH-261108-01 (51C-222.22, Tài xế Demo, Đ1 + Đ4) dùng tiếp cho UC-15 (`docs/test-evidence/UC-15/du-lieu.md`, ca a: ghép thêm Đ2).

### Kết quả (Kiệt thử 07/11/2026 trên `dev`, Claude kiểm ảnh)

- 3/3 ca đạt: lý do BR-01 (51C-150.00, 2.600 > 1.500 kg), BR-11 (51C-333.33 ngừng; kèm BR-01 vì 2.000 kg), BR-14 (Trần Bình hạng B, KTT 9.500 kg) hiện đúng, có mã BR; đổi sang 51C-222.22 · Tài xế Demo thành công, đơn và lịch trình giữ nguyên.
- Ghi nhận 1 (cho Tài xem): ở ảnh a, **51C-150.00 vẫn nằm trong ô chọn** và hiện dòng đỏ BR-01, ảnh b thì xe này đã nằm ở danh sách bị loại. Có vẻ danh sách xe khả dụng không tải lại khi khung đổi xe đang mở rồi mới ghép đơn. Máy chủ vẫn chặn đúng (BR-01), chỉ giao diện chưa khớp.
- Ảnh phụ trước ca a: chọn nhầm đơn cũ DH-79S3VJ (khung lấy 25/10, hạn 26/10) → bảng vi phạm BR-05, BR-06, không ghép đơn nào (đúng; không lưu ảnh).
