# GD: Menu tài khoản gọn, trang Tài khoản và trang Cài đặt

- **Trạng thái:** Hoàn thành 19/11/2026 – 5/5 AC (Kiệt thử, `docs/test-evidence/GD-cai-dat-tai-khoan/`)
- **Tác nhân:** Quản lý, Điều phối, Kế toán, Tài xế
- **Đặc tả:** `docs/giao-dien.md` (mục Giao diện v3 và mục Menu tài khoản gọn, trang Tài khoản, trang Cài đặt); `docs/stories/UC-35-doi-mat-khau.md`
- **Quy tắc nghiệp vụ liên quan:** BR-57, NFR-USA-02 (chỉ thay đổi giao diện, giữ nguyên API UC-35)
- **Người làm:** Tài

## Mô tả ngắn
Thu gọn menu xổ từ vòng tên tắt thành menu điều hướng ngắn gọn, tách form đổi mật khẩu UC-35 sang trang `/tai-khoan` và gom 4 tùy chọn hiển thị cá nhân (giao diện, mật độ bảng, cỡ chữ, giảm chuyển động) vào trang `/cai-dat` lưu trên `localStorage`.

## Quyết định
1. Menu tài khoản chỉ giữ: họ tên + vai trò ở đầu, link **Tài khoản** (`/tai-khoan`), link **Cài đặt** (`/cai-dat`), link **Cấu hình hệ thống** (`/quan-ly/cau-hinh`, chỉ Quản lý), đường kẻ ngăn và nút **Đăng xuất**.
2. Trang `/tai-khoan` dùng đúng đối tượng `NguoiDung` hiện có (`api/auth.ts`: `id`, `ho_ten`, `vai_tro`), không gọi thêm API mới nên chỉ hiển thị Họ tên và Vai trò; form đổi mật khẩu mở sẵn, giữ nguyên quy tắc và thông báo lỗi UC-35.
3. Trang `/cai-dat` áp ngay không cần nút Lưu; cả 4 tùy chọn đọc/ghi/áp tập trung trong `frontend/src/nen.ts` và tự áp khi khởi động ứng dụng (`main.tsx`).
4. Hai route `/tai-khoan` và `/cai-dat` mở cho mọi vai trò đã đăng nhập trong `KhungTrang`, không thêm vào thanh menu bên trái. Riêng Tài xế (không có cột menu trái) có link "← Chuyến của tôi" ở đầu trang và có thể bấm logo thanh trên để về trang chính.
5. Giảm chuyển động tắt transition/animation bằng CSS qua `data-giam-chuyen-dong="bat"` trên `<html>` và truyền `animated={!dangGiamChuyenDong()}` cho `@number-flow/react`.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| GD-AC1 | Menu tài khoản (bấm vòng tên tắt) đúng 4 phần: đầu (họ tên + vai trò), link Tài khoản (`/tai-khoan`), link Cài đặt (`/cai-dat`), đường kẻ + nút Đăng xuất; riêng Quản lý có thêm link Cấu hình hệ thống (`/quan-ly/cau-hinh`). Bấm link hoặc bấm/Tab ra ngoài menu đóng lại | UI | NFR-USA-02 |
| GD-AC2 | Trang `/tai-khoan` hiện thông tin chỉ đọc (họ tên, vai trò) và form Đổi mật khẩu mở sẵn; kiểm tra 8–200 ký tự, nhập lại khớp, báo lỗi tại chỗ và hiện toast "Đã đổi mật khẩu" đúng như UC-35 | UI | BR-57 |
| GD-AC3 | Trang `/cai-dat` có đủ 4 mục (Giao diện, Mật độ bảng, Cỡ chữ, Giảm chuyển động); chọn từng tùy chọn áp dụng ngay lên giao diện (`data-che-do`, `data-mat-do`, `data-co-chu`, `data-giam-chuyen-dong`), không cần nút Lưu, và vẫn giữ sau khi tải lại trang; Quản lý thấy dòng dẫn tới Cấu hình hệ thống ở cuối trang | UI | NFR-USA-02 |
| GD-AC4 | Tài xế ở màn hẹp 390 px mở được cả `/tai-khoan` và `/cai-dat` từ menu tài khoản, thao tác được, quay lại Chuyến của tôi được và bố cục không vỡ hay cuộn ngang | UI | NFR-USA-02 |
| GD-AC5 | Khi bật đồng thời bản tối (`Tối`) và cỡ chữ `Lớn`, cả trang Tài khoản, Cài đặt, menu tài khoản và các màn chính không vỡ bố cục, chữ đủ tương phản | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi / tạo mới:
  - `frontend/src/nen.ts`: gom logic đọc/ghi/áp và khởi động cho 4 tùy chọn (`qlvc-che-do`, `qlvc-mat-do`, `qlvc-co-chu`, `qlvc-giam-chuyen-dong`).
  - `frontend/src/MenuTaiKhoan.tsx`: thu gọn menu chỉ còn đầu + các link điều hướng + Đăng xuất.
  - `frontend/src/pages/TaiKhoan.tsx`: trang `/tai-khoan` (thông tin chỉ đọc + form đổi mật khẩu UC-35 mở sẵn).
  - `frontend/src/pages/CaiDat.tsx`: trang `/cai-dat` (4 mục tùy chọn dạng `vien-thuoc`, link Cấu hình hệ thống cho Quản lý).
  - `frontend/src/App.tsx`: khai báo 2 route chung cho mọi vai trò đã đăng nhập, biến logo `Hieu` thành link về trang chủ vai trò.
  - `frontend/src/pages/dieu-phoi/ChuyenDanhSach.tsx`, `frontend/src/pages/TongQuan.tsx`, `frontend/src/pages/tai-xe/ChuyenCuaToiChiTiet.tsx`: truyền `animated={!dangGiamChuyenDong()}` cho `NumberFlow` và tôn trọng giảm chuyển động khi cuộn.
  - `frontend/src/index.css`: biến CSS mật độ (`--dem-*`), biến tỉ lệ cỡ chữ (`--ty-le-chu`, `--co-chu`), quy tắc `data-mat-do="gon"`, `data-co-chu="lon"`, `data-giam-chuyen-dong="bat"`, và kiểu cho menu gọn + 2 trang mới.
  - `docs/giao-dien.md`, `docs/stories/GD-cai-dat-tai-khoan.md`.
- Lệnh kiểm tra trong `frontend/`: `npm run typecheck`, `npm run lint`, `npx prettier --check`, `npm run build`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| GD-AC1 | UI | `docs/test-evidence/GD-cai-dat-tai-khoan/` `a-menu-dieuphoi.png`, `a-menu-quanly.png` | Đạt (Kiệt thử) | 19/11/2026 |
| GD-AC2 | UI | `docs/test-evidence/GD-cai-dat-tai-khoan/` `h-…`, `i-…`, `j-tai-khoan-doi-xong.png` | Đạt (Kiệt thử) | 19/11/2026 |
| GD-AC3 | UI | `docs/test-evidence/GD-cai-dat-tai-khoan/` `b-cai-dat-quan-ly.png`, `c-cai-dat-toi-gon-lon.png` | Đạt (Kiệt thử) | 19/11/2026 |
| GD-AC4 | UI | `docs/test-evidence/GD-cai-dat-tai-khoan/` `k-…`, `l-…`, `m-tai-xe-cai-dat-390.png` | Đạt (Kiệt thử) | 19/11/2026 |
| GD-AC5 | UI | `docs/test-evidence/GD-cai-dat-tai-khoan/` `d-…`, `e-…`, `f-…`, `g-tai-khoan-toi-lon.png` | Đạt (Kiệt thử) | 19/11/2026 |
