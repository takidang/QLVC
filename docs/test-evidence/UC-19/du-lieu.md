# Dữ liệu thử giao diện UC-19 Quét mã lấy hàng (AC13, AC14, AC15)

> Claude ghi 04/11/2026 cho Kiệt thử trên nhánh `kiet/uc-19-quet-lay`. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC13–AC15 trong `docs/stories/UC-19-quet-ma-lay-hang.md`.

## Chuẩn bị

- Dùng tiếp chuyến **CH-261031-01** trên CSDL máy Kiệt: `DANG_CHAY`, tài xế `an`, 3 đơn chờ lấy **DH-MSKG7T** (10 kiện), **DH-9ZTTPG** (8 kiện), **DH-6HXV2Y** (5 kiện). Migration 12 lý do đã chạy (Claude chạy 04/11).
- Chạy lại cả hai sau khi chuyển nhánh: backend (`cd backend; .venv\Scripts\uvicorn app.main:app --reload`) và frontend (`cd frontend; npm install; npm run dev`, có 2 gói mới `qrcode`, `qr-scanner`).
- Một ảnh JPG/PNG bất kỳ trên máy làm "ảnh hiện trường".

## Phần 1 – Phiếu QR (AC14), máy tính

Đăng nhập `dieuphoi` / `demo12345` (hoặc tài khoản Quản lý), menu **Đơn hàng**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| p1 | Bấm mã đơn **DH-6HXV2Y** trong bảng | Mở trang **Phiếu gửi hàng**: mã đơn chữ to, mã QR, khách, địa chỉ + SĐT lấy, địa chỉ + người nhận + SĐT giao, hạn giao, **5 kiện**, kg, m³; có nút **In phiếu** | `p1-phieu.png` | |
| p2 | Bấm **In phiếu** (hoặc Ctrl+P) | Bản xem trước chỉ có phần phiếu: không có menu, không có nút | `p2-xem-truoc-in.png` | |
| p3 | Mở camera điện thoại (hoặc Zalo → quét mã) chĩa vào QR trên màn hình | Đọc ra đúng **DH-6HXV2Y** (QR chỉ chứa mã đơn) | `p3-doc-qr.png` (chụp màn hình điện thoại) | |

## Phần 2 – Tài xế trên máy tính, giả lập 360 px (AC13)

`F12` → `Ctrl + Shift + M`, chọn rộng 360. Đăng nhập `an` / `matkhau123`, mở **CH-261031-01**.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Xem trang chuyến | Có khối **Lấy hàng**: nút **Quét mã QR**, ô **Hoặc gõ mã đơn**, nút **Lấy hàng**; mỗi điểm lấy "Chờ lấy" có nút **Không lấy được**; không cuộn ngang | `a-khoi-lay-hang.png` | |
| b | Gõ `dh-mskg7t` → **Lấy hàng**; trình duyệt hỏi vị trí → bấm **Chặn** | Xanh "**Đã lấy DH-MSKG7T (10 kiện)**"; khung vàng "Không lấy được vị trí GPS … (BR-43)"; điểm lấy DH-MSKG7T đổi thành **Đã lấy**, mất nút Không lấy được | `b-da-lay-thieu-gps.png` | |
| c | Gõ lại `DH-MSKG7T` → **Lấy hàng** | "Đơn DH-MSKG7T đã lấy từ trước, không ghi thêm (BR-45)" | `c-quet-lai.png` | |
| d | Gõ `DH-KHONGCO` → **Lấy hàng** | Đỏ "Đơn không thuộc chuyến của bạn (BR-38)" | `d-khong-thuoc.png` | |
| e | Ở điểm lấy **DH-9ZTTPG** bấm **Không lấy được** → chọn "Hàng chưa chuẩn bị xong", chọn ảnh → **Báo không lấy được** | "Đã báo không lấy được DH-9ZTTPG"; điểm đổi thành **Thất bại** | `e-khong-lay-duoc.png` | |
| f | Ở **DH-6HXV2Y** bấm **Không lấy được** → không chọn lý do / ảnh → bấm gửi; rồi bấm **Thôi** | Không gửi được (ô bắt buộc / báo "Chọn lý do và chụp ít nhất 1 ảnh (BR-42)"); **Thôi** đóng khung, đơn vẫn Chờ lấy | `f-thieu-ly-do.png` | |
| g | Bấm **Quét mã QR** trên máy tính không có webcam (hoặc bấm **Chặn** khi trình duyệt hỏi quyền camera) | Báo "Không mở được camera … Gõ mã đơn bên dưới."; ô gõ mã vẫn dùng được (luồng 2a) | `g-khong-camera.png` | |

## Phần 3 – Camera trên điện thoại thật (AC15)

Camera chỉ mở trên HTTPS nên dùng Cloudflare Quick Tunnel (docs đã chốt, không cần tài khoản):

1. Cài một lần: `winget install --id Cloudflare.cloudflared` (công cụ trên máy, không phải gói của dự án).
2. Backend, frontend đang chạy → mở terminal mới: `cloudflared tunnel --url http://127.0.0.1:5173`.
3. Terminal in ra địa chỉ `https://…trycloudflare.com` → mở trên điện thoại (Android Chrome hoặc iPhone Safari).
4. Máy tính mở phiếu **DH-6HXV2Y** (Phần 1) để có QR trên màn hình. Tắt tunnel (`Ctrl + C`) khi thử xong.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| h | Điện thoại: đăng nhập `an`, mở CH-261031-01, bấm **Quét mã QR** → **Cho phép** camera | Hiện khung camera (camera sau), nút **Tắt camera** | `h-camera.png` | |
| i | Chĩa camera vào QR của **DH-6HXV2Y** trên màn hình máy tính; trình duyệt hỏi vị trí → **Cho phép** | Camera tự tắt; xanh "**Đã lấy DH-6HXV2Y (5 kiện)**", **không** có khung vàng thiếu GPS; điểm lấy đổi **Đã lấy** | `i-quet-camera.png` | |

## Sau khi thử

DH-MSKG7T, DH-6HXV2Y `DA_LAY`, DH-9ZTTPG `THAT_BAI` – để dùng tiếp cho UC-20 (quét giao). Muốn thử lại từ đầu thì nhờ Claude trả 3 đơn về `DA_GHEP` và xóa lượt quét.
