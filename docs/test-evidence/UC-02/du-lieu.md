# Dữ liệu thử giao diện UC-02 Người dùng

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).

Ảnh lưu vào `docs/test-evidence/UC-02/` · Kiệt thử 30/10/2026 (nhánh `kiet/uc-02-nguoi-dung`).

**Tài khoản có sẵn trong CSDL máy Kiệt lúc thử** (mật khẩu thật không ghi vào đây):

| Tên đăng nhập | Vai trò | Ghi chú |
|---|---|---|
| `kiet` | Quản lý | Tạo 30/10 bằng `python -m app.tao_quan_ly`, dùng để thử UC-02 |
| `kietquanly` | Quản lý | Tài khoản cũ quên mật khẩu, khóa ở ca c |
| `an` | Tài xế | Tạo ở UC-04 ca 1, mật khẩu `matkhau123` |
| `binh` | Tài xế | Tạo ở UC-04 ca 3, đang `NGUNG` |

| Ca | Làm gì | Dữ liệu nhập | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|---|
| a | Thêm người dùng | Tên đăng nhập `thu` · Họ tên `Lê Thị Thu` · Mật khẩu `matkhau123` · Vai trò **Kế toán** | Dòng `thu` hiện trong bảng, "Hoạt động" | `a-them-nguoi-dung.png` | Đạt (ảnh: dòng `thu` Kế toán, Hoạt động; dòng `kiet (bạn)`, `an`, `binh` không có nút Khóa) |
| b | Thêm trùng tên đăng nhập | Tên đăng nhập `binh` (trùng tài xế) · Họ tên `Trùng` · Mật khẩu `matkhau123` · Vai trò Kế toán | Báo **"Tên đăng nhập binh đã có người dùng"** ngay dưới ô, không lưu | `b-trung-ten-nguoi-dung.png` | Đạt (ảnh) |
| c | Khóa tài khoản | Bấm **Khóa** ở dòng `kietquanly` → OK | Hỏi xác nhận; trạng thái thành "Đã khóa". Dòng `kiet (bạn)` và dòng tài xế `an`, `binh` **không có** nút Khóa | `c-khoa-tai-khoan.png` | Đạt (ảnh hộp xác nhận "Người này bị đăng xuất ngay"; CSDL sau đó `kietquanly` = `NGUNG`) |
| d | Sửa tài xế | Bấm **Sửa** ở dòng `an` | Không có ô chọn vai trò, hiện "Vai trò: Tài xế (đổi ở trang Tài xế)" | `d-sua.png` | Đạt (ảnh) |
| e | Đặt lại mật khẩu | Dòng `thu`: nhập `abc1234` (7 ký tự) → Lưu; rồi `matkhau456` → Lưu | 7 ký tự bị chặn (cần ít nhất 8); 8 ký tự trở lên hiện "Đã đặt mật khẩu mới…" | `e-dat-lai-mat-khau.png` | Đạt (ảnh bước 8 ký tự; bước 7 ký tự bị trình duyệt chặn – Kiệt xác nhận, không chụp; máy chủ cũng chặn: test `test_uc02_ac7_mat_khau_sai`) |
| f | Lọc và tìm | Lọc vai trò **Tài xế**; rồi "Mọi vai trò" + gõ `thu` | Chỉ còn `an`, `binh`; rồi chỉ còn `thu` | `f-loc-tim-kiem.png` | Đạt (ảnh: lọc Kế toán + tìm `thu` còn 1 dòng; lọc Tài xế thử tay không chụp) |

Sau khi thử (kiểm CSDL 30/10): `thu` có mật khẩu `matkhau456`; `kietquanly` đã đổi sang Điều phối và khóa (muốn dùng lại: đăng nhập `kiet` → Mở khóa → Đặt lại mật khẩu); họ tên tài xế `an` đã thành `Nguyễn Văn A` lúc thử ca d (sửa lại `Nguyễn Văn An` nếu cần cho kịch bản mục 11).
