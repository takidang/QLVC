# Dữ liệu thử giao diện UC-28 Tra cứu đơn công khai (UC-28-AC7)

> Kiệt thử 18/11/2026 (Claude chạy trên Edge 1440 px, máy Kiệt, **không đăng nhập**: xóa cookie trước khi mở). Backend `dev` (1900ad3), giao diện v3 `tai/thu-giao-dien-v3` (7348c6c), CSDL `qlvc_demo`.

Đơn thử **DH-CG8AE2** (tạo trên giao diện v3 cùng ngày): SĐT lấy 0901234567, SĐT nhận 0907654321. Mở `http://127.0.0.1:5175/tra-cuu`.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Mở `/tra-cuu` chưa đăng nhập | Trang công khai: ô Mã đơn, ô 4 số cuối điện thoại | `a-trang-tra-cuu.png` | Đạt |
| b | DH-CG8AE2 + 4567 (SĐT lấy) | Trạng thái hiện tại và các mốc dạng dòng thời gian, không có cước, SĐT, tài xế | `b-ket-qua-sdt-lay.png` | Đạt: "Đã xếp chuyến xe – Hiện tại 14:13 18/11/2026", "Đã tiếp nhận đơn 14:12 18/11/2026" |
| c | "  dh-cg8ae2 " (viết thường, có khoảng trắng) + 4321 (SĐT nhận) | Vẫn tìm được | `c-ma-viet-thuong-sdt-nhan.png` | Đạt |
| d | DH-CG8AE2 + 0000 | "Không tìm thấy đơn" | `d-sai-4-so.png` | Đạt: "Không tìm thấy đơn. Kiểm tra lại mã đơn trên phiếu gửi hàng và 4 số cuối…" |
| d2 | DH-CG8AE2 + abcd | Báo nhập sai dạng | | Đạt: "Nhập mã đơn và đúng 4 chữ số cuối số điện thoại" |
| e | Sai thêm 10 lần liên tiếp, rồi nhập đúng 4567 | Bị chặn kể cả khi đúng | `e-qua-nhieu-lan-sai.png` | Đạt: "Tra cứu sai quá nhiều lần, vui lòng thử lại sau 1 phút" |
| f | Đợi hơn 1 phút, nhập đúng 4567 | Tra được lại | `f-sau-1-phut-tra-lai-duoc.png` | Đạt |

Góp ý nhỏ (không chặn AC): sau khi tra được, tiêu đề kết quả "Đã xếp chuyến xe" có khung viền đen dày (viền focus khi trang tự đưa focus vào tiêu đề), nhìn như ô nhập (`b-ket-qua-sdt-lay.png`).

**Kết luận: AC7 đạt.**
