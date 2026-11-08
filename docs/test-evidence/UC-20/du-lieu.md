# Dữ liệu thử giao diện UC-20 Quét mã giao hàng (AC14, AC15)

> Claude ghi 05/11/2026 cho Kiệt thử trên nhánh `kiet/uc-20-quet-giao`. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC14, AC15 trong `docs/stories/UC-20-quet-ma-giao-hang.md`.

## Chuẩn bị

- Dùng tiếp chuyến **CH-261031-01** trên CSDL máy Kiệt (sau khi thử UC-19): `DANG_CHAY`, tài xế `an`.
  - **DH-MSKG7T** (10 kiện) `DA_LAY` → thử trên máy tính (Phần 1).
  - **DH-6HXV2Y** (5 kiện) `DA_LAY` → để dành thử camera + ký tay trên iPhone (Phần 2).
  - **DH-9ZTTPG** `THAT_BAI` (không lấy được ở UC-19) → không có nút giao.
  - Hạn giao của các đơn là **31/10** (đã qua) nên giao xong sẽ hiện **giao trễ** (BR-72) – đúng như mong đợi.
- Chạy backend và frontend (Claude bật sẵn, hoặc `cd backend; .venv\Scripts\uvicorn app.main:app --reload` và `cd frontend; npm run dev`). Không có gói mới, không có migration mới.
- Một ảnh JPG/PNG bất kỳ làm "ảnh giao hàng".

## Phần 1 – Máy tính, giả lập 360 px (AC14)

Tab ẩn danh, `F12` → `Ctrl + Shift + M`, rộng 360. Đăng nhập `an` / `matkhau123`, mở **CH-261031-01**, kéo xuống **Lịch trình**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Xem các điểm **Giao** | Điểm giao DH-MSKG7T và DH-6HXV2Y có nút **Giao hàng** và **Giao không được**; điểm giao DH-9ZTTPG (Thất bại) không có nút; không cuộn ngang | `a-nut-giao.png` | Đạt |
| b | DH-MSKG7T → **Giao hàng** → gõ `DH-6HXV2Y` → **Xác nhận mã** | Đỏ "Mã DH-6HXV2Y không khớp đơn của điểm này (DH-MSKG7T)"; nút **Xác nhận giao** mờ | `b-sai-ma.png` | Đạt |
| c | Gõ `dh-mskg7t` → **Xác nhận mã** | Xanh "Đã xác nhận đúng kiện DH-MSKG7T" | `c-dung-ma.png` | Đạt |
| d | Chọn ảnh, nhập tên `Lê Văn Nhận`, **ký bằng chuột** vào ô ký; bấm **Xóa chữ ký** | Có nét ký; xóa thì ô trắng lại và nút **Xác nhận giao** mờ lại | `d-ky-va-xoa.png` | Đạt |
| e | Ký lại → **Xác nhận giao** | Xanh "**Đã giao DH-MSKG7T (10 kiện)**"; khung vàng "Giao sau hạn giao … (BR-72)" (có thể thêm khung thiếu GPS nếu máy không cho vị trí); điểm giao đổi **Đã giao**, mất nút | `e-da-giao-tre.png` | Đạt (có thêm khung thiếu GPS vì máy tính không cho vị trí) |
| f | DH-6HXV2Y → **Giao không được** | Hiện ô "Lý do giao không được DH-6HXV2Y" với 6 lý do giao (Người nhận vắng … Xe hỏng / sự cố trên đường), ô ảnh; bấm **Thôi** để đóng, **không gửi** (đơn để dành cho Phần 2) | `f-ly-do-giao.png` | Đạt |

## Phần 2 – iPhone thật qua Cloudflare Tunnel (AC15)

1. Terminal mới: `& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:5173` → lấy địa chỉ `https://…trycloudflare.com`.
2. Máy tính: đăng nhập `kiet` (hoặc `dieuphoi`) → **Đơn hàng** → bấm **DH-6HXV2Y** để mở phiếu có QR.
3. iPhone **Safari**: mở địa chỉ tunnel, đăng nhập `an`, mở CH-261031-01.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| g | DH-6HXV2Y → **Giao hàng** → **Quét mã QR trên kiện** → cho phép camera → quét QR trên màn hình máy tính | Camera tắt, hiện "Đã xác nhận đúng kiện DH-6HXV2Y" | `g-quet-xac-nhan.png` | Đạt |
| h | Chụp ảnh bằng camera, nhập tên, **ký bằng ngón tay** (trang không bị cuộn khi ký) | Nét ký mượt theo ngón tay | `h-ky-ngon-tay.png` | Đạt (chữ ký lưu trên máy chủ trùng nét trong ảnh) |
| i | **Xác nhận giao** → Safari hỏi vị trí → **Cho phép** | **Safari có hỏi quyền vị trí** (sửa lỗi của UC-19); "Đã giao DH-6HXV2Y (5 kiện)" + khung giao trễ, **không** có khung thiếu GPS | – | Đạt, kiểm bằng CSDL, không chụp ảnh: lượt quét `GIAO` của DH-6HXV2Y có tọa độ 10.849955, 106.796945, sai số 35 m, `thieu_gps = false` |

## Phần 3 – Kết thúc vòng tối thiểu (tùy chọn, làm cuối cùng)

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| k | Sau khi DH-MSKG7T, DH-6HXV2Y đã giao: khối **Kết thúc chuyến** nhập km `50200` + ảnh → **Kết thúc** | Chuyến **Hoàn thành**; vòng tạo đơn → ghép → chốt → bắt đầu → lấy → giao → kết thúc chạy trọn (mốc 08/11). Sau ca này chuyến không thử lại được | `k-hoan-thanh.png` | Đạt (ảnh chụp lúc nhập km trước khi bấm; CSDL: chuyến `HOAN_THANH`) |

## Sau khi thử

Claude kiểm CSDL: lượt quét `GIAO` có tên người nhận, tọa độ (Safari), 2 tệp (`ANH`, `CHU_KY`); ghép `ket_qua = DA_GIAO`, `giao_tre = true`; mỗi đơn đã giao có 1 `PHAI_THU` = cước, `CHUA_THU` và 1 dòng `NHAT_KY_TIEN`.

### Kết quả (Kiệt thử 05/11/2026, Claude kiểm CSDL)

- 10/10 ca đạt (a–i, k). Lần thử đầu ở Phần 2, Kiệt lỡ bấm **Xác nhận giao** khi chưa ký xong (nút sáng ngay từ nét ký đầu tiên) nên chưa chụp được ảnh ca h. Claude đưa DH-6HXV2Y về `DA_LAY` trên CSDL thử, xóa lượt giao, 2 tệp, phải thu, nhật ký tiền và lịch sử của lần đó, rồi Kiệt thử lại. Vì vậy `nhat_ky_tien` trên máy Kiệt không có id 2.
- CSDL: DH-MSKG7T và DH-6HXV2Y đều `DA_GIAO`, ghép `ket_qua = DA_GIAO`, `giao_tre = true`. Mỗi lượt `GIAO` có tên người nhận và 2 tệp (`ANH`, `CHU_KY` PNG), các tệp có trên đĩa. Phải thu 2.997.000 và 800.000, đúng bằng cước, `CHUA_THU`, mỗi khoản 1 dòng `NHAT_KY_TIEN` `TAO`. Chuyến CH-261031-01 `HOAN_THANH`.
- Ghi nhận ngoài UC-20 (để sau, Kiệt quyết): khối **Kết thúc chuyến** (UC-18) tràn khỏi khung bên phải trên iPhone; nhãn điểm **Lấy** hiện trạng thái đơn ("Đã giao"); có thể thêm bước hỏi lại trước **Xác nhận giao** để chống chạm nhầm.
