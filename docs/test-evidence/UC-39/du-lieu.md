# Dữ liệu thử giao diện UC-39 Hồ sơ cá nhân và ảnh đại diện (UC-39-AC7)

> Kiệt thử 19/11/2026 (Claude chạy trên Edge, máy Kiệt). Nhánh `tai/uc-39-ho-so` (62629ea), CSDL `qlvc_demo` đã `alembic upgrade head` (5367154f7c64). Ảnh thử: `backend/seed/anh/dong_ho.jpg`, `chung_tu.jpg` (JPEG thật).

| Ca | Làm gì | Ảnh | Kết quả |
|---|---|---|---|
| a | `ketoan` (1440 px) mở `/tai-khoan`, chưa có ảnh | `a-ke-toan-chua-co-anh.png` | Đạt: khối Ảnh đại diện có chữ tắt "TD" và nút Chọn ảnh; thông tin chỉ xem (họ tên, tên đăng nhập, vai trò, trạng thái) kèm "Liên hệ Quản lý để thay đổi"; vòng góc phải là chữ tắt |
| b | Chọn `dong_ho.jpg` | `b-ke-toan-da-tai-anh.png` | Đạt: ảnh nén ở trình duyệt rồi gửi; khối Ảnh đại diện và vòng góc phải hiện ảnh; có nút Xóa ảnh |
| c | Chọn ảnh thứ hai `chung_tu.jpg` | `c-ke-toan-doi-anh-lan-hai.png` | Đạt: cả hai chỗ đổi sang ảnh mới ngay (`?v=2`), báo "Đã cập nhật ảnh đại diện"; `GET /api/auth/anh-dai-dien` 200 `image/jpeg` |
| d | Chọn tệp văn bản `sai.txt` | `d-tep-sai-loai.png` | Đạt: báo "Ảnh phải là JPEG hoặc PNG", ảnh cũ giữ nguyên |
| e | Bấm Xóa ảnh | `e-ke-toan-xoa-anh.png` | Đạt: vòng góc phải và khối ảnh quay về chữ tắt "TD", nút Xóa ảnh ẩn; `GET /api/auth/anh-dai-dien` → 404 |
| f | `dieuphoi` sửa hạn GPLX của "Tài xế Demo" còn 20 ngày (09/12/2026); `taixe` ở 390 px mở `/tai-khoan`, tải ảnh | `f-tai-xe-390.png` | Đạt: tài xế thấy thêm SĐT, số GPLX, hạng GPLX, hạn GPLX "09/12/2026 · còn 20 ngày" tô cam (BR-21); tải ảnh được, vòng góc phải hiện ảnh; trang không tràn ngang |
| g | Bản tối ở 390 px | `g-tai-xe-390-ban-toi.png` | Đạt: chữ đọc rõ, hạn GPLX cam sáng trên nền tối |

Không có lỗi trong console. Sau khi thử đã xóa ảnh của `ketoan`, `taixe`. Hạn GPLX của "Tài xế Demo" còn để 09/12/2026 trên `qlvc_demo` (nạp lại CSDL demo trước buổi demo).

Góp ý nhỏ (không chặn AC7): ngưỡng tô cam hạn GPLX cố định 30 ngày (`HanGiayTo` trong `danh-muc.tsx`), không đọc CFG-02 như khung "Cần chú ý"; đổi CFG-02 thì hai chỗ có thể lệch nhau.

**Kết luận: AC7 đạt.**
