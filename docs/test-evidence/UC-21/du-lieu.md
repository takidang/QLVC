# Dữ liệu thử giao diện UC-21 Ghi chi phí (AC13, AC14)

> Claude ghi 09/11/2026 cho Kiệt thử trên nhánh `kiet/uc-21-chi-phi` (đã gộp `dev` sau #19–#24). Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC13, AC14 trong `docs/stories/UC-21-ghi-chi-phi.md`.

## Chuẩn bị (CSDL máy Kiệt)

- Chuyến **CH-261109-02** (T01, 51C-111.11, tài xế **An**, **Đang chạy**; đơn DH-S4JPYG đã giao khi thử PR #21). Định mức 1.000.000, Kế toán demo đã cấp **tạm ứng 1.000.000** (tiền mặt) để thấy dòng "Tạm ứng đã nhận".
- Một ảnh JPG/PNG bất kỳ làm "ảnh hóa đơn" (máy tính); iPhone thì chụp thật.
- Không có gói mới, không có migration mới.

## Phần 1 – Máy tính, giả lập 360 px (AC13)

Tab ẩn danh, `F12` → `Ctrl + Shift + M`, rộng 360. Đăng nhập `an` → mở **CH-261109-02** → khối **Chi phí** (dưới khối Kết thúc chuyến).

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Xem khối Chi phí | "Tạm ứng đã nhận 1.000.000 đ · Đã khai 0 đ", "Chưa ghi khoản chi nào"; form có Loại chi = **Dầu** và ô **Số lít**; không cuộn ngang | `a-khoi-chi-phi.png` | |
| b | Đổi Loại chi sang **Cầu đường** rồi về **Dầu** | Ô Số lít biến mất khi chọn Cầu đường, hiện lại khi chọn Dầu | – | |
| c | Dầu, `520000`, `26` lít, **để trống ghi chú**, chọn ảnh → **Ghi chi phí** | Đỏ "Chi phí cần có ghi chú (BR-54)", chưa có khoản nào | `c-thieu-ghi-chu.png` | |
| d | Nhập ghi chú `Đổ dầu Cai Lậy`, **bỏ ảnh** (chọn lại ô tệp rồi Hủy) → **Ghi chi phí** | Đỏ "Chi phí cần có ảnh chứng từ (BR-54)" | – | |
| e | Dầu, `520000`, `26`, ghi chú, 1 ảnh → **Ghi chi phí** | Xanh "Đã ghi dầu 520.000 đ, chờ Kế toán duyệt"; khoản "Dầu · 520.000 đ · 26 lít" nhãn **Chờ duyệt**, "1 ảnh"; "Đã khai 520.000 đ"; form trống lại | `e-da-ghi.png` | |
| f | Ghi **Cầu đường** `230000`, ghi chú `Trạm BOT`, 1 ảnh | Khoản thứ hai, không có số lít; đã khai 750.000 đ | – | |
| g | Khoản dầu → **Sửa** → số tiền `500000` → **Lưu** | Xanh "Đã sửa khoản chi"; khoản còn 500.000 đ, vẫn 1 ảnh; đã khai 730.000 đ | `g-da-sua.png` | |
| h | Khoản cầu đường → **Xóa** → hộp hỏi "Xóa khoản cầu đường 230.000 đ?" → **OK** | Khoản biến mất; đã khai 500.000 đ | `h-da-xoa.png` | |

## Phần 2 – iPhone thật qua Cloudflare Tunnel (AC14)

1. Máy tính chạy tunnel: `& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:5173`, lấy địa chỉ `https://…trycloudflare.com`.
2. iPhone Safari: đăng nhập `an`, mở **CH-261109-02** → khối Chi phí.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| i | **Bốc xếp** `300000`, ghi chú, ô ảnh → **Chụp ảnh** hóa đơn bằng camera → **Ghi chi phí** | Ghi được, khoản có "1 ảnh"; khối không tràn khung | `i-iphone.png` | |

## Sau khi thử

Claude kiểm CSDL: các khoản `chi_phi` (`CHO_DUYET`, `nguoi_tao` = An), tệp ảnh ≤ 500 KB (ảnh iPhone đã nén), `nhat_ky_tien` bảng `chi_phi` đủ `TAO` / `SUA` / `XOA`.
