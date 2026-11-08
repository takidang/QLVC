# Dữ liệu thử giao diện UC-23 Tạm ứng (AC14)

> Claude ghi 07/11/2026 cho Kiệt thử trên nhánh `kiet/uc-23-tam-ung`. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC14 trong `docs/stories/UC-23-tam-ung.md`.

## Chuẩn bị

- Chạy backend và frontend (Claude bật sẵn, hoặc `cd backend; .venv\Scripts\uvicorn app.main:app --reload` và `cd frontend; npm run dev`). Không có gói mới, không có migration mới.
- CSDL máy Kiệt chỉ có chuyến CH-261031-01 đã **Hoàn thành**, nên cần lập một chuyến mới rồi chốt:
  1. Đăng nhập `kiet` (Quản lý, vào được trang Điều phối) → **Chuyến** → **Lập chuyến**: tuyến **T01**, ngày mai 06:00, xe **51C-111.11**, tài xế **An** → Lập chuyến.
  2. Bấm mã chuyến vừa lập → **Chốt chuyến**. Chuyến không có đơn nên trình duyệt lần lượt hỏi "… Vẫn chốt chuyến?" cho **chạy rỗng** (BR-23) và **lãi âm** (BR-52): bấm **OK** cả hai → **Đã chốt**. Định mức chốt của T01 = 550.000 + 200.000 + 250.000 = **1.000.000**.
- Kế toán: tài khoản `thu` (mật khẩu bạn đã đặt), hoặc chạy `cd backend; .venv\Scripts\python -m app.tai_khoan_demo` rồi dùng `ketoan` / `demo12345`.
- Máy tính, cửa sổ thường (Kế toán làm trên máy tính). Hộp xác nhận thu hồi là hộp của trình duyệt.

## Các ca

Đăng nhập Kế toán → menu **Tạm ứng** → chọn chuyến vừa chốt.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Chọn chuyến | "Định mức đã chốt 1.000.000 đ · Đã cấp còn hiệu lực 0 đ · Còn được cấp 1.000.000 đ"; ô số tiền điền sẵn **1000000**; bảng "Chưa cấp tạm ứng cho chuyến này" | `a-chon-chuyen.png` | Đạt |
| b | Sửa ô số tiền thành `1200000` → **Cấp tạm ứng** | Đỏ "Tổng tạm ứng 1.200.000 đ vượt định mức đã chốt 1.000.000 đ … còn được cấp 1.000.000 đ (BR-53)"; bảng vẫn trống | `b-vuot-dinh-muc.png` | Đạt (lần đầu trình duyệt chặn 1200000 vì ô số tiền `step=1000` + `min=1`; đã sửa thành bước 1 đồng rồi thử lại) |
| c | Nhập `600000`, Tiền mặt → **Cấp tạm ứng** | Xanh "Đã cấp 600.000 đ"; đã cấp 600.000, còn được cấp 400.000, ô điền sẵn 400000; bảng 1 dòng **Hiệu lực**, tài xế An | `c-da-cap.png` | Đạt |
| d | Dòng vừa cấp → **Sửa**: số `1100000`, lý do `ghi nhầm` → **Lưu**; rồi số `500000` → **Lưu** | Lần 1 đỏ BR-53, khoản vẫn 600.000; nút Lưu mờ khi lý do trống; lần 2 xanh "Đã sửa thành 500.000 đ", còn được cấp 500.000 | `d-sua.png` | Đạt. Câu báo khi sửa ghi "còn được cấp 1.000.000 đ" dễ nhầm với số tổng 400.000 → đã đổi thành "khoản này sửa tối đa …" (test `test_uc23_ac6_sua_vuot`) |
| e | **Thu hồi** → hộp hỏi "Tài xế … đã nộp lại 500.000 đ?" → **OK** | Dòng thành **Đã thu hồi**, mất nút Sửa / Thu hồi; đã cấp 0, còn được cấp 1.000.000 | `e-thu-hoi.png` | Đạt |
| f | Cấp `300000` → đăng nhập `kiet` → chi tiết chuyến → **Mở chốt** | Báo "Chuyến còn tạm ứng chưa thu hồi … (BR-24)", chuyến vẫn Đã chốt | `f-mo-chot-bi-chan.png` | Đạt |
| g | Kế toán thu hồi khoản 300.000 → `kiet` bấm **Mở chốt** lại | Mở chốt được, chuyến về **Đang lập** (UC-15) | `g-mo-chot-duoc.png` | Đạt |

## Sau khi thử

Claude kiểm CSDL: các khoản `tam_ung` (số, hình thức, trạng thái, `tai_xe_id` = An, `nguoi_tao` = Kế toán); `nhat_ky_tien` bảng `tam_ung` đủ các dòng `TAO`, `SUA`, `THU_HOI` theo thứ tự, có lý do.

### Kết quả (Kiệt thử 07/11/2026, Claude kiểm CSDL)

- 7/7 ca đạt trên chuyến CH-261108-01 (T01, An, chạy rỗng, định mức 1.000.000).
- CSDL: 2 khoản `tam_ung` (600.000 sửa thành 500.000, và 300.000), tài xế An, người tạo `thu`, cả hai `DA_THU_HOI`; lần cấp 1.200.000 không lưu. `nhat_ky_tien` bảng `tam_ung` 5 dòng đúng thứ tự: `TAO` 600000 → `SUA` (lý do "ghi nhầm") → `THU_HOI` → `TAO` 300000 → `THU_HOI`, người làm `thu`. Chuyến về `LAP` sau ca g.
- Sửa trong lúc thử: bước ô số tiền (1 đồng), câu báo vượt định mức khi sửa.
