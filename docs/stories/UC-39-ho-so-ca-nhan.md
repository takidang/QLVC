# UC-39: Hồ sơ cá nhân và ảnh đại diện

- **Trạng thái:** Đang làm
- **Tác nhân:** mọi người dùng đã đăng nhập (Quản lý, Điều phối, Kế toán, Tài xế)
- **Đặc tả:** `docs/use-cases.md` (UC-39, mức C, thêm 19/11/2026 cho giao diện v3), `docs/api.md` mục Xác thực, `docs/security-rules.md` (upload)
- **Quy tắc nghiệp vụ liên quan:** BR-57 (phân quyền ở máy chủ), BR-14, 15 (GPLX: chỉ xem)
- **Người làm:** Tài
- **Liên quan:** trang Tài khoản (`docs/stories/GD-cai-dat-tai-khoan.md`), UC-35 đổi mật khẩu, UC-02 người dùng, UC-04 tài xế

## Mô tả ngắn
Trên trang Tài khoản, người dùng xem hồ sơ của mình và tự đổi **ảnh đại diện**. Mọi thông tin khác do công ty quản lý, chỉ Quản lý sửa ở UC-02 / UC-04; trang Tài khoản hiện chữ xám kèm "Liên hệ Quản lý để thay đổi".

## Quyết định (Tài chốt 19/11/2026)
1. **Tự đổi:** ảnh đại diện (và mật khẩu – UC-35). **Chỉ xem:** họ tên, tên đăng nhập, vai trò, trạng thái; tài xế thêm SĐT, số / hạng / hạn GPLX.
2. **SĐT không cho tự đổi:** Điều phối dùng SĐT để gọi tài xế khi có sự cố; tự đổi thì gõ nhầm là mất liên lạc, người khác cầm máy có thể đổi sang số mình, và không ai được báo. Phương án "gửi yêu cầu, Quản lý duyệt" bị bỏ vì nặng (bảng yêu cầu, màn duyệt, thông báo) so với lợi ích.
3. **Lưu ảnh:** thêm cột `nguoi_dung.anh_dai_dien` (tên file do máy chủ sinh, nullable), dùng `app/luu_tru.py` (`kiem_anh`, `luu`, `xoa`) như ảnh chứng từ. Không dùng bảng `TEP` (ràng buộc "đúng một chủ sở hữu" chỉ cho lượt quét / chi phí / sự cố / chuyến).
4. **Xem ảnh:** chỉ ảnh của chính mình (vòng tên góc phải, trang Tài khoản) → `GET /api/auth/anh-dai-dien` trả ảnh theo cookie đăng nhập (cùng tên miền), không cần link ký HMAC. Không có màn nào xem ảnh người khác (YAGNI).
5. Đổi ảnh thì xóa file cũ; xóa ảnh thì quay về chữ tắt.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-39-AC1 | `GET /api/auth/ho-so` trả hồ sơ của chính người gọi: `ten_dang_nhap, ho_ten, vai_tro, trang_thai, co_anh_dai_dien`; tài xế thêm `tai_xe: {sdt, so_gplx, hang_gplx, han_gplx}`; người khác vai trò không có `tai_xe`. Chưa đăng nhập → 401 | API | BR-57 |
| UC-39-AC2 | `PUT /api/auth/anh-dai-dien` (multipart, 1 file): JPEG/PNG nhận theo byte đầu, ≤ 500 KB → 200, `co_anh_dai_dien` true; file sai loại / rỗng → 400, quá lớn → 413 (mã như `kiem_anh`); tên file do máy chủ sinh, không dùng tên client gửi | API | security-rules |
| UC-39-AC3 | Đổi ảnh lần hai: file cũ bị xóa khỏi nơi lưu; `DELETE /api/auth/anh-dai-dien` → 204, xóa file, `co_anh_dai_dien` false; xóa khi chưa có ảnh → 204 | API | — |
| UC-39-AC4 | `GET /api/auth/anh-dai-dien` trả đúng ảnh của người gọi, `Content-Type` theo đuôi đã kiểm, `X-Content-Type-Options: nosniff`, `Cache-Control: private, no-cache`; chưa có ảnh → 404; chưa đăng nhập → 401. Không có đường nào lấy ảnh người khác | API | BR-57, security-rules |
| UC-39-AC5 | Không có API nào cho người dùng tự sửa họ tên, SĐT, vai trò, tên đăng nhập, GPLX: `PATCH`/`PUT /api/auth/ho-so` → 405; các trường đó gửi kèm form ảnh bị bỏ qua (CSDL không đổi) | API | BR-57 |
| UC-39-AC6 | `GET /api/auth/toi` (đang dùng ở khung trang) có thêm `co_anh_dai_dien` để vòng góc phải biết hiện ảnh hay chữ tắt | API | — |
| UC-39-AC7 | Giao diện: trang Tài khoản có khối Ảnh đại diện (xem, chọn ảnh, nén ở trình duyệt như ảnh chứng từ nếu có sẵn hàm nén, xóa); thông tin chỉ xem ghi "Liên hệ Quản lý để thay đổi"; tài xế thấy GPLX, hạn còn ≤ 30 ngày tô cảnh báo (BR-21); vòng góc phải hiện ảnh, không có ảnh thì chữ tắt; màn 390 px, bản tối không vỡ | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi:
- Test đã viết:
- Lệnh chạy test:
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa:

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
