# Dữ liệu thử giao diện UC-24 Quyết toán (AC14)

> Claude ghi 10/11/2026 cho Kiệt thử trên nhánh `kiet/uc-24-quyet-toan`. Ảnh lưu vào thư mục này, điền cột "Kết quả" rồi điền dòng AC14 trong `docs/stories/UC-24-quyet-toan.md`.

## Chuẩn bị (CSDL máy Kiệt, 10/11)

- **CH-261031-01** (An, `HOAN_THANH`): đơn DH-MSKG7T 2.997.000 và DH-6HXV2Y 800.000 giao thành công, DH-9ZTTPG giao thất bại; không có khoản chi, không có tạm ứng; chuyến chốt trước UC-15 nên định mức = 0. Dùng cho ca "chênh lệch = 0".
- **CH-261109-02** (An, `DANG_CHAY`): DH-S4JPYG 800.000 đã giao; tạm ứng 1.000.000; khoản chi Dầu 500.000 và Bốc xếp 300.000 đang chờ duyệt (có ảnh). Ca a cho An kết thúc chuyến để thành `HOAN_THANH`.
- Đăng nhập: Kế toán `ketoan` hoặc `thu`, Quản lý `kiet` hoặc `quanly`, tài xế `an` (mật khẩu demo như các lần trước). Máy tính, cửa sổ thường. Không có gói mới, không có migration mới.
- **Kiểm app chạy đúng nhánh UC-24:** menu Kế toán phải có **Quyết toán** (giữa "Công nợ" và "Tạm ứng"). Không có, hoặc trang báo "Có lỗi (mã 404)" → nhờ Claude khởi động lại backend rồi **F5**.
- Quyết toán **không mở lại được** (BR-29), nên làm đúng thứ tự.

## Các ca

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Đăng nhập `an` → chuyến **CH-261109-02** → khối Chi phí ghi thêm **Cầu đường 230.000**, ghi chú "Trạm BOT", 1 ảnh → **Kết thúc chuyến** (km lớn hơn 50.300, ảnh đồng hồ) | Khoản cầu đường "Chờ duyệt"; chuyến thành **Hoàn thành** | – | |
| b | Đăng nhập `ketoan` → **Quyết toán** → nút **Chờ quyết toán** → chọn **CH-261109-02** | Doanh thu 800.000 (DH-S4JPYG); bảng chi theo loại có định mức đã chốt, thực tế 0 (chưa duyệt); cảnh báo "Còn 3 khoản chờ duyệt"; nút **Quyết toán** mờ, ghi "Còn 3 khoản chờ duyệt" | `b-bang-chua-duyet.png` | |
| c | Khoản Dầu → **Ảnh 1** | Hộp hiện ảnh hóa đơn tài xế đã chụp; bấm nền hoặc **Đóng** để tắt | `c-anh-chung-tu.png` | |
| d | Khoản Dầu → **Xét** → sửa số duyệt **480000**, để trống lý do | Nút **Duyệt** mờ (giảm số phải có lý do). Ghi lý do "Hóa đơn 480.000" → **Duyệt** → xanh "Đã duyệt 480.000 đ", dòng Dầu "Đã duyệt · 480.000" | `d-dieu-chinh.png` | |
| e | Khoản Dầu → **Xét**, gõ số **600000** → **Duyệt** (ghi lý do bất kỳ) | Ô số không cho vượt số khai (trình duyệt báo), hoặc máy chủ báo đỏ "Số duyệt không được lớn hơn số tài xế khai 500.000 đ (BR-55)"; khoản giữ 480.000 | – | |
| f | Khoản Bốc xếp → **Xét** → lý do "Không có hóa đơn" → **Từ chối**; rồi **Đổi** → **Duyệt** đúng 300.000 (không lý do) | Lần 1: "Từ chối", số duyệt "–". Lần 2: "Đã duyệt · 300.000" (đổi quyết định được trước khi quyết toán) | `f-tu-choi-roi-duyet.png` | |
| g | Khoản Cầu đường → **Xét** → **Duyệt** 230.000 | Hết cảnh báo chờ duyệt. Bảng: Dầu 480.000, Cầu đường 230.000, Bốc xếp 300.000, tổng **1.010.000**; Kết quả: lãi = 800.000 − 1.010.000 − 600.000 = **−810.000** (đỏ); có dòng lý do lệch; tạm ứng 1.000.000, chênh lệch **−10.000: công ty trả thêm 10.000 đ**; khối quyết toán ghi "Công ty đã trả thêm 10.000 đ", ô Hình thức, Lúc xử lý | `g-du-dieu-kien.png` | |
| h | Hình thức **Chuyển khoản**, Lúc xử lý để mặc định → **Quyết toán** → hộp hỏi "Quyết toán CH-261109-02? Công ty đã trả thêm 10.000 đ…" → **Hủy** trước, rồi bấm lại → **OK** | Hủy: không đổi gì. OK: xanh "Đã quyết toán CH-261109-02"; danh sách chờ không còn chuyến này; bảng hiện "Đã quyết toán … · Công ty đã trả thêm · Chuyển khoản lúc …", không còn nút Xét, Quyết toán | `h-da-quyet-toan.png` | |
| i | Nút **Đã quyết toán** → chọn CH-261109-02; rồi vào **Tạm ứng** chọn chuyến này (nếu có trong danh sách) | Chỉ xem. Tạm ứng: chuyến không còn trong danh sách sửa được (đã quyết toán) | – | |
| j | **Chờ quyết toán** → **CH-261031-01** | Doanh thu 3.797.000 (DH-MSKG7T, DH-6HXV2Y), DH-9ZTTPG "0 – giao thất bại"; "Tài xế không khai khoản chi nào"; dầu ghi 200 km; chênh lệch 0 "không chênh", không có ô hình thức / lúc xử lý → **Quyết toán** → **OK** → đạt | `j-khong-chenh.png` | |
| k | Đăng nhập `an` → chuyến CH-261109-02 | Khối Chi phí chỉ xem, các khoản hiện trạng thái Đã duyệt; không có form ghi | `k-tai-xe-chi-xem.png` | |
| l | Đăng nhập `kiet` (Quản lý) → menu có **Công nợ** và **Quyết toán** → mở Quyết toán, nút **Đã quyết toán**, chọn CH-261109-02, bấm **Ảnh 1**; mở **Công nợ** → chọn khách | Xem được bảng và ảnh, **không** có nút Xét / Quyết toán; Công nợ không có ô tích, không có nút "Đánh dấu đã thu" | `l-quan-ly-chi-xem.png` | |

## Không thử tay (có test tự động)

| Nội dung | Vì sao không thử tay | Test |
|---|---|---|
| Chuyến **kết thúc do sự cố**: ô lương tay + lý do, lương 0 | Máy Kiệt chưa có chuyến kết thúc do sự cố (phải cho Bình chạy CH-261108-04 rồi Điều phối kết thúc do sự cố); làm thêm được nếu còn thời gian | `test_uc24_ac10_*`, `test_uc24_ac5_lai_luong_tay` |
| Chênh lệch **dương** (tài xế nộp lại), gửi sai dấu | Giao diện tự chọn đúng cách xử lý theo dấu | `test_uc24_ac9_*` |
| Lúc xử lý ở tương lai | Ô giờ không cho chọn sau bây giờ | `test_uc24_ac9_xu_ly_sai` |
| Quyết toán lần hai, sửa tạm ứng / chi phí sau quyết toán → 409 BR-29 | Giao diện ẩn mọi nút sau khi khóa | `test_uc24_ac11_khoa_sau_quyet_toan` |
| Điều phối, Tài xế gọi API → 403; link ảnh hết hạn / sửa chữ ký → 403 | Không có menu; cần sửa URL bằng tay | `test_uc24_ac12_*`, `test_uc24_ac13_*` |

## Sau khi thử
