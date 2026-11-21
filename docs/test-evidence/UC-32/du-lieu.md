# Dữ liệu thử giao diện UC-32 Theo dõi chuyến (UC-32-AC11)

> Tài ghi 08/11/2026. Thử trên `dev` sau khi PR UC-32 gộp. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC11 trong `docs/stories/UC-32-theo-doi-chuyen.md`.

## Chuẩn bị (chuyến chạy **hôm nay**, như lần thử UC-19, 20)
- Điều phối: chuyến T01 hôm nay, ghép 3 đơn (A, B, C), chốt.
- Tài xế (`taixe`): Bắt đầu chuyến; quét lấy A đúng giờ; quét lấy B **trễ hơn 15 phút** so với ETA (đợi qua giờ hoặc lập chuyến giờ sớm hơn hiện tại để ETA đã qua); báo một sự cố nếu UC-33 đã có (chưa có thì bỏ ca e).
- Thêm một chuyến khác cùng **xe** (tài xế khác còn giờ lái) khởi hành ngay trước giờ kết thúc dự kiến + độ trễ (để thấy cờ Chồng lịch). Dùng cùng tài xế thì BR-17/18 chặn lập vì tài xế đã hết giờ lái trong ngày (Kiệt thử 10/11).

Đăng nhập `dieuphoi`.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | **Chuyến** → chọn ngày hôm nay | Bảng có thêm cột Tiến độ ("2/6 điểm"), Đầy (%), Cờ ("Trễ"; "Chồng lịch" nếu có chuyến kế tiếp) | `a-bang-ngay.png` | Đạt (CH-261110-02: "2/6 điểm", 42%, cờ "Trễ"; sau PR #34 cờ màu đỏ: `a-bang-ngay-sau-sua.png`) |
| b | Mở chi tiết chuyến | Lịch trình có cột Giờ quét ("06:05 · đã lấy"), Trễ (số phút, đỏ khi > 15; quét sớm ghi "Sớm 4′"); khối Tiền (doanh thu, định mức, lương, tạm ứng); Dòng thời gian bằng chữ ("Đang lập → Đã chốt", "Quét lấy đơn …"), không hiện mã; cờ Trễ màu đỏ | `b-chi-tiet.png` | Đạt (giờ quét "14:54 · đã lấy", trễ 17′ đỏ; khối Tiền; dòng thời gian. Sau PR #34: dòng thời gian bằng chữ, cờ đỏ, "Sớm 4′": `bd-chi-tiet-sau-sua.png`) |
| c | (Nếu có chuyến kế tiếp bị chồng) | Dòng đỏ "Đang trễ: dự kiến xong …, chồng lên chuyến kế tiếp … (BR-73)" | `c-chong-lich.png` | Đạt 12/11 trên v2 (`c1-v2-bang-ngay-chong-lich.png`, `c2-v2-chi-tiet-chong-lich.png`) |
| d | Bấm **Kết thúc do sự cố** → nhập lý do "hỏng hộp số", km cuối lớn hơn km bắt đầu → Kết thúc chuyến → OK | Hộp hỏi "… N đơn chưa giao sẽ thành Thất bại"; xong: nhãn Hoàn thành, dòng "Kết thúc do sự cố: hỏng hộp số", khối "Đơn của chuyến" có cột Trạng thái, đơn chưa giao "Thất bại"; trang Đơn hàng thấy chúng (cột Lý do gần nhất "Sự cố xe: hỏng hộp số") trong thẻ đơn thất bại (UC-22) | `d-ket-thuc-su-co.png` | Đạt (hỏi "… 3 đơn chưa giao sẽ thành Thất bại."; Hoàn thành, "Kết thúc do sự cố: hỏng hộp số", km 50.500 → 50.600; sau PR #34 khối "Đơn của chuyến" có cột Trạng thái "Thất bại", thẻ UC-22 lý do "Sự cố xe: hỏng hộp số") |
| e | (Chờ UC-33, chưa thử được) Khối Sự cố → nhập cách xử lý → **Đóng sự cố** | Sự cố "Đã đóng", hiện cách xử lý; cờ Sự cố trên bảng ngày mất | `e-dong-su-co.png` | Đạt 12/11 trên v2 (`e-v2-dong-su-co.png`; tài xế thấy cách xử lý: `e2-tai-xe-thay-cach-xu-ly.png`) |

## Kết quả thử (Kiệt, 10/11/2026)

Claude chạy trên Edge 1440 px theo đúng các bước trên, máy Kiệt, `dev` (e1dcb58); ca b, d thử lại trên code PR #34 (a2e5826) bằng chính chuyến này sau khi kết thúc. Chuyến CH-261110-02 (T01 hôm nay 14:17, xe 51C-111.11, `taixe`), A DH-PG3WHN, B DH-QT3VM4, C DH-6K2GFH. Điều phối chuẩn bị bằng API; tài xế bắt đầu và lấy A (14:13, sớm 4 phút) bằng API, **lấy B lúc 14:54 trên giao diện tài xế 360 px** (ETA 14:37, trễ 17 phút).

- **3/3 ca a, b, d đạt**; c, e chưa thử.

## Kết quả thử ca c, e (Kiệt, 12/11/2026, giao diện v2)

Máy Kiệt, backend `dev` (93ab7eb), giao diện nhánh `tai/thu-giao-dien-v2` (30949bf), dữ liệu demo `seed.demo` + `--ngay-moi`.

- **c đạt:** CH-261112-03 (51C-201.11, `taixe`) quét lấy Long An trễ 22′ → kết thúc dự kiến 20:50 → 21:12. Điều phối lập CH-261112-08 cùng xe khởi hành 21:00 (tài xế Trần Minh Bình) → bảng ngày có cờ "Trễ 22′" + "Chồng lịch"; chi tiết có dòng đỏ "Đang trễ: dự kiến xong 21:12 12/11/26, chồng lên chuyến kế tiếp của xe / tài xế: CH-261112-08 (BR-73). Hệ thống không tự đổi lịch."
- **e đạt:** CH-261112-04 có sự cố "Hỏng xe" do tài xế báo (UC-33) → Điều phối nhập cách xử lý, **Đóng sự cố** → khối Sự cố "Đã đóng" kèm cách xử lý, cờ Sự cố trên bảng ngày mất; tài xế `taixe04` trên điện thoại thấy "Đã xử lý" kèm cách xử lý.
- Góp ý đã gửi Tài (sửa ở PR #54): bảng ngày nên hiện giờ kết thúc dự kiến mới của chuyến trễ.
