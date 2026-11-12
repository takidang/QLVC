# UC-37: Thông báo theo vai trò

- **Trạng thái:** Đang làm – AC1–AC4 đạt, AC5 giao diện chờ làm (Đã duyệt 12/11/2026 – Tài: "làm theo kế hoạch", tiêu chí như đề xuất 12/11)
- **Tác nhân:** Quản lý, Điều phối, Kế toán, Tài xế
- **Đặc tả:** chưa có trong `docs/use-cases.md` (UC mới, chuông trên thanh đầu của giao diện v2); `docs/api.md` mục 2.7
- **Quy tắc nghiệp vụ liên quan:** BR-57, BR-58; dùng lại UC-27 (bảng cảnh báo), UC-22, UC-24
- **Người làm:** Tài (backend); giao diện do phiên giao diện v2 làm

## Mô tả ngắn
Chuông thông báo cho mọi vai trò: mỗi người thấy việc cần chú ý của mình. Danh sách tính lại mỗi lần mở từ dữ liệu sẵn có; "đã đọc" do giao diện tự nhớ bằng mốc lần xem cuối.

## Quyết định (Tài duyệt 12/11/2026)
1. `GET /api/thong-bao` → `{so_luong, thong_bao: [...]}`, xếp mới trước theo `luc`. Không thêm bảng, không migration: giao diện lưu mốc lần mở chuông trên trình duyệt, thông báo có `luc` sau mốc đó là chưa đọc.
2. Mỗi thông báo: `loai`, `muc_do` (`KHAN` | `CAN_LAM` | `THONG_TIN`), `tieu_de`, `noi_dung` (có thể null), `doi_tuong` `{loai, id}` để bấm mở, `luc`.
3. `luc` là lúc sự việc xảy ra: sự cố lúc báo, chuyến trễ lúc quét gần nhất, đơn chờ ghép lúc bắt đầu vào ngưỡng CFG-10, đơn thất bại lúc thành thất bại, chuyến chờ quyết toán lúc kết thúc, khoản chi lúc khai / lúc Kế toán xử lý, chuyến được giao lúc chốt. Giấy tờ sắp hết hạn không có mốc sự việc nên lấy **đầu ngày hôm nay** (nhắc lại mỗi ngày).
4. Sự cố không lưu giờ đóng, nên "sự cố vừa được đóng" của tài xế lọc theo lúc báo trong 3 ngày.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-37-AC1 | Điều phối, Quản lý: một thông báo cho mỗi dòng của bảng cảnh báo UC-27 (giấy tờ, chuyến trễ, sự cố mở, đơn sắp quá hạn, thiếu GPS) và mỗi đơn thất bại đã sẵn sàng xử lý (UC-22) | API | BR-73, 21, 36 |
| UC-37-AC2 | Kế toán: chuyến `HOAN_THANH` chờ quyết toán; khoản chi chờ duyệt (gộp theo chuyến `HOAN_THANH`); tạm ứng còn hiệu lực của chuyến `HOAN_THANH`. Chuyến đã quyết toán không còn thông báo | API | BR-55 |
| UC-37-AC3 | Tài xế: chuyến của mình `DA_CHOT` khởi hành hôm nay hoặc ngày mai; sự cố của mình đã đóng (báo trong 3 ngày) kèm cách xử lý; khoản chi của mình bị từ chối hoặc duyệt khác số khai (xử lý trong 3 ngày) kèm lý do. Không thấy của tài xế khác | API | BR-58 |
| UC-37-AC4 | Đủ trường, xếp mới trước, `luc` đúng mốc sự việc; mỗi vai trò chỉ thấy loại của mình; chưa đăng nhập → 401; tham số lạ → 400 | API | BR-57 |
| UC-37-AC5 | Giao diện: chuông trên thanh đầu, số chưa đọc (phiên giao diện v2) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/thong_bao/{router,service}.py` (mới; Điều phối dùng lại `canh_bao.bang` và `that_bai.can_xu_ly`), `backend/app/main.py` (đăng ký router theo chữ cái), `docs/api.md` mục 2.7.
- Test đã viết: `backend/tests/api/test_uc37_thong_bao.py` (12 ca). Thử làm hỏng 11 chỗ (báo cả đơn thất bại còn ghép, đếm cả khoản chi đã duyệt, cộng cả tạm ứng thu hồi, tài xế thấy chuyến người khác, lấy cả ngày kia, sự cố quá 3 ngày, báo cả khoản duyệt đúng số, không xếp mới trước, giấy tờ lấy giờ hiện tại, đơn sắp quá hạn lấy hạn giao, không bỏ trùng khoản chi xử lý nhiều lần) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc37_thong_bao.py`
- Lệch đặc tả: không (UC mới, ghi `api.md`). Khoản chi bị từ chối rồi duyệt lại chỉ giữ lần xử lý mới nhất.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-37-AC1 | API | `test_uc37_ac1_*` (3 ca) | Đạt | 12/11/2026 |
| UC-37-AC2 | API | `test_uc37_ac2_*` (3 ca) | Đạt | 12/11/2026 |
| UC-37-AC3 | API | `test_uc37_ac3_*` (3 ca) | Đạt | 12/11/2026 |
| UC-37-AC4 | API | `test_uc37_ac4_*` (3 ca) | Đạt | 12/11/2026 |
| UC-37-AC5 | UI | Chuông trên thanh đầu: phiên giao diện v2 làm | CHƯA KIỂM | |
