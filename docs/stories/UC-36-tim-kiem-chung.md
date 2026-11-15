# UC-36: Tìm kiếm chung

- **Trạng thái:** Hoàn thành 12/11/2026 – 5/5 AC đạt (Đã duyệt 12/11/2026 – Tài: "làm UC-35 36 đi")
- **Tác nhân:** Quản lý, Điều phối, Kế toán, Tài xế
- **Đặc tả:** chưa có trong `docs/use-cases.md` (UC mới, ô tìm trên thanh đầu của giao diện v2); `docs/api.md` mục 2
- **Quy tắc nghiệp vụ liên quan:** BR-57, BR-58
- **Người làm:** Tài (backend); giao diện do phiên giao diện v2 làm

## Mô tả ngắn
Một ô tìm duy nhất trả kết quả gộp theo nhóm (chuyến, đơn, xe, tài xế, khách), mỗi người chỉ thấy phần mình được xem, thay cho 5 lần gọi API riêng.

## Quyết định (Tài duyệt 12/11/2026)
1. `GET /api/tim?q=` (2–100 ký tự sau khi bỏ khoảng trắng đầu cuối, chuẩn NFC). Khớp một phần, không phân biệt hoa thường, `%` `_` không làm khớp tất cả.
2. Luôn trả đủ 5 khóa `chuyen`, `don`, `xe`, `tai_xe`, `khach_hang`, mỗi khóa `{tong, ds}` với `ds` tối đa 5 dòng. Nhóm vai trò đó không được xem thì trả `{tong: 0, ds: []}` (giao diện không phải đoán).
3. Quyền (theo quyền xem hiện có ở từng module): Điều phối, Quản lý: cả 5 nhóm. Kế toán: chuyến, đơn, khách. Tài xế: chỉ chuyến của mình (trạng thái được xem như UC-17, không `LAP`, `HUY`), tìm theo mã chuyến, biển số.
4. Chuyến khớp mã chuyến, biển số, tên tài xế; đơn khớp mã đơn, tên khách; xe khớp biển số; tài xế khớp họ tên; khách khớp tên, số điện thoại.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-36-AC1 | Điều phối tìm một từ khóa khớp cả 5 loại → mỗi nhóm có đúng dòng khớp; không phân biệt hoa thường; "bình" gõ kiểu NFD vẫn khớp tên lưu dựng sẵn | API | — |
| UC-36-AC2 | Mỗi nhóm tối đa 5 dòng nhưng `tong` là số khớp thật (biên: đúng 5, 6 khớp) | API | — |
| UC-36-AC3 | Quyền: Quản lý như Điều phối; Kế toán chỉ có chuyến, đơn, khách (xe, tài xế rỗng); Tài xế chỉ có chuyến của mình, không thấy chuyến người khác, chuyến `LAP`, `HUY`, không thấy đơn, xe, tài xế, khách | API | BR-57, 58 |
| UC-36-AC4 | `q` rỗng, chỉ khoảng trắng, 1 ký tự, quá 100 ký tự, thiếu, tham số lạ → 400; `%`, `_` không khớp tất cả; chưa đăng nhập → 401 | API | — |
| UC-36-AC5 | Giao diện: ô tìm trên thanh đầu (phiên giao diện v2) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/tim_kiem/{router,service}.py` (mới, dùng lại `truy_van_chuyen`, `truy_van_don`, `THAY_DUOC`), `backend/app/main.py` (đăng ký router theo chữ cái), `docs/api.md` mục 2.7.
- Test đã viết: `backend/tests/api/test_uc36_tim_kiem_chung.py` (16 ca). Thử làm hỏng 9 chỗ (tài xế thấy mọi chuyến, thấy cả LAP/HUY, Kế toán thấy xe và tài xế, bỏ NFC, 6 dòng/nhóm, bỏ chống ký tự đại diện ở 4 nhóm) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc36_tim_kiem_chung.py`
- Lệch đặc tả: không (UC mới, ghi `api.md`). Mỗi nhóm một truy vấn đếm và một truy vấn lấy 5 dòng (10 truy vấn cho Điều phối), đủ cho đội nhỏ.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-36-AC1 | API | `test_uc36_ac1_*` (2 ca) | Đạt | 12/11/2026 |
| UC-36-AC2 | API | `test_uc36_ac2_toi_da_5_dong` | Đạt | 12/11/2026 |
| UC-36-AC3 | API | `test_uc36_ac3_*` (3 ca) | Đạt | 12/11/2026 |
| UC-36-AC4 | API | `test_uc36_ac4_*` (10 ca) | Đạt | 12/11/2026 |
| UC-36-AC5 | UI | Ô tìm trên thanh đầu: Kiệt thử 12/11, ảnh `docs/test-evidence/UC-36/a-tim-chung-51C.png` (PR #55) | Đạt | 12/11/2026 |
