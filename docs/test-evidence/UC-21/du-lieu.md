# Dữ liệu thử giao diện UC-21 Ghi chi phí (AC13, AC14)

> Claude ghi 09/11/2026 cho Kiệt thử trên nhánh `kiet/uc-21-chi-phi` (đã gộp `dev` sau #19–#24). Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC13, AC14 trong `docs/stories/UC-21-ghi-chi-phi.md`.

## Chuẩn bị (CSDL máy Kiệt)

- Chuyến **CH-261109-02** (T01, 51C-111.11, tài xế **An**, **Đang chạy**; đơn DH-S4JPYG đã giao khi thử PR #21). Định mức 1.000.000, Kế toán demo đã cấp **tạm ứng 1.000.000** (tiền mặt) để thấy dòng "Tạm ứng đã nhận".
- Một ảnh JPG/PNG bất kỳ làm "ảnh hóa đơn" (máy tính); iPhone thì chụp thật.
- Không có gói mới, không có migration mới.
- **Kiểm app đang chạy đúng nhánh UC-21:** trong khối Chi phí phải thấy dòng "Tạm ứng đã nhận 1.000.000 đ". Không thấy dòng này, hoặc bấm Ghi mà báo "Có lỗi (mã 404)", nghĩa là backend còn chạy bản của nhánh khác (đổi nhánh mà backend không tự tải lại) → nhờ Claude khởi động lại backend rồi **F5**. (09/11 gặp đúng lỗi này sau khi chuyển nhánh UC-25 → UC-21.)
- Các lần ghi bị từ chối không lưu gì, nên thử lại từ đầu được; muốn form trống hẳn thì **F5**.

## Phần 1 – Máy tính, giả lập 360 px (AC13)

Tab ẩn danh, `F12` → `Ctrl + Shift + M`, rộng 360. Đăng nhập `an` → mở **CH-261109-02** → khối **Chi phí** (dưới khối Kết thúc chuyến).

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Xem khối Chi phí | "Tạm ứng đã nhận 1.000.000 đ · Đã khai 0 đ", "Chưa ghi khoản chi nào"; form có Loại chi = **Dầu** và ô **Số lít**; không cuộn ngang | `a-khoi-chi-phi.png` | Đạt |
| b | Đổi Loại chi sang **Cầu đường** rồi về **Dầu** | Ô Số lít biến mất khi chọn Cầu đường, hiện lại khi chọn Dầu | `b-mat-so-lit.png` | Đạt |
| c | Dầu, `520000`, `26` lít, **để trống ghi chú** (hoặc chỉ gõ dấu cách), chọn ảnh → **Ghi chi phí** | Đỏ "Chi phí cần có ghi chú (BR-54)", chưa có khoản nào | `c-thieu-ghi-chu.png` | Đạt |
| d | **F5** cho form trống (Chrome giữ ảnh đã chọn khi mở hộp chọn tệp rồi bấm Hủy, nên không bỏ ảnh được bằng cách đó) → Dầu, `520000`, `26`, ghi chú `Đổ dầu Cai Lậy`, **không chọn ảnh** → **Ghi chi phí** | Đỏ "Chi phí cần có ảnh chứng từ (BR-54)", chưa có khoản nào | `d-thieu-anh.png` | Đạt |
| e | Dầu, `520000`, `26`, ghi chú, 1 ảnh → **Ghi chi phí** | Xanh "Đã ghi dầu 520.000 đ, chờ Kế toán duyệt"; khoản "Dầu · 520.000 đ · 26 lít" nhãn **Chờ duyệt**, "1 ảnh"; "Đã khai 520.000 đ"; form trống lại | `e-da-ghi.png` | Đạt |
| f | Ghi **Cầu đường** `230000`, ghi chú `Trạm BOT`, 1 ảnh | Khoản thứ hai, không có số lít; đã khai 750.000 đ | `f-cau-duong.png` | Đạt |
| g | Khoản dầu → **Sửa** → bấm **Lưu** ngay (chưa đổi gì) → rồi đổi số tiền `500000` → **Lưu** | Lần đầu đỏ "Không có gì thay đổi"; lần sau xanh "Đã sửa khoản chi", khoản còn 500.000 đ, vẫn 26 lít, vẫn 1 ảnh; đã khai 730.000 đ | `g-da-sua.png` | Đạt |
| g2 | Khoản dầu → **Sửa** → Loại chi **Cầu đường** (ô số lít biến mất) → **Thôi** | Form sửa đóng, khoản vẫn là Dầu 500.000 đ (Thôi không lưu gì) | – | Đạt |
| h | Khoản cầu đường → **Xóa** → hộp hỏi "Xóa khoản cầu đường 230.000 đ?" → **Hủy** trước, rồi **Xóa** lại → **OK** | Bấm Hủy thì khoản còn nguyên; bấm OK thì khoản biến mất, xanh "Đã xóa khoản chi"; đã khai 500.000 đ | `h-da-xoa.png` | Đạt |

## Phần 2 – iPhone thật qua Cloudflare Tunnel (AC14)

1. Máy tính chạy tunnel: `& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:5173`, lấy địa chỉ `https://…trycloudflare.com`.
2. iPhone **Safari**: mở địa chỉ tunnel (để cửa sổ PowerShell chạy tunnel mở suốt lúc thử), đăng nhập `an`, mở **CH-261109-02** → khối Chi phí.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| i | **Bốc xếp** `300000`, ghi chú `Bốc xếp Cần Thơ`, ô ảnh → **Chụp ảnh** hóa đơn bằng camera (cho phép camera nếu Safari hỏi) → **Ghi chi phí** | Ghi được, khoản "Bốc xếp · 300.000 đ" có "1 ảnh", không có số lít; đã khai 800.000 đ; khối Chi phí và các ô nhập không tràn khung | `i-iphone.png` | Đạt |

## Không thử tay (có test tự động)

| Nội dung | Vì sao không thử tay | Test |
|---|---|---|
| Chuyến **đã quyết toán**: khối Chi phí chỉ xem, không có form, không có Sửa / Xóa | Máy Kiệt chưa có chuyến đã quyết toán (UC-24 chưa làm) | `test_uc21_ac5_*`, `test_uc21_ac11_da_quyet_toan` (409 BR-29) |
| Khoản **Đã duyệt / Từ chối** không có nút Sửa / Xóa | Duyệt chi phí thuộc UC-24 | `test_uc21_ac11_khoan_da_xu_ly` |
| Điểm **Lấy** của đơn **giao thất bại** hiện "Đã lấy" (Tài nhờ, góp ý #21) | CH-261109-02 không có đơn giao thất bại | `test_uc20_diem_lay_da_lay_khi_giao_that_bai` |
| Quá 5 ảnh, ảnh sai loại, ảnh > 500 KB | Trình duyệt nén ảnh trước khi gửi nên khó tạo | `test_uc21_ac4_*` |

## Sau khi thử

Claude kiểm CSDL:
- `chi_phi` của CH-261109-02: còn **Dầu 500.000 / 26 lít** và **Bốc xếp 300.000**, cả hai `CHO_DUYET`, `nguoi_tao` = An; khoản cầu đường đã xóa không còn.
- `tep`: mỗi khoản 1 ảnh `ANH`, kích thước ≤ 500 KB (ảnh iPhone đã nén).
- `nhat_ky_tien` bảng `chi_phi`: `TAO` dầu → `TAO` cầu đường → `SUA` dầu (520000 → 500000) → `XOA` cầu đường (giữ giá trị cũ) → `TAO` bốc xếp.
- Không có khoản nào từ các lần bị từ chối (ca c, d).

### Kết quả (Kiệt thử 09/11/2026, Claude kiểm CSDL)

- 10/10 ca đạt (a–i, g2). Ca d làm lại bằng cách F5 rồi không chọn ảnh (Chrome giữ ảnh khi bấm Hủy ở hộp chọn tệp).
- Lần đầu ca c–e báo "Có lỗi (mã 404)": backend còn chạy bản nhánh UC-25 sau khi chuyển nhánh (không tự tải lại) – Claude khởi động lại backend, thử lại đạt. Không phải lỗi của UC-21.
- CSDL: còn Dầu 500.000 / 26 lít (ảnh 30 KB) và Bốc xếp 300.000 (ảnh iPhone 200 KB, đã nén), `CHO_DUYET`, `nguoi_tao` = An; cầu đường đã xóa. `nhat_ky_tien` `chi_phi`: TAO dầu → TAO cầu đường → SUA dầu (520000 → 500000) → XOA cầu đường (giữ giá trị cũ) → TAO bốc xếp. Ảnh iPhone: khối Chi phí không tràn khung, đã khai 800.000 đ.
