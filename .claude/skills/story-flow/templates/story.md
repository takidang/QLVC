# UC-xx: <Tên use case>

- **Trạng thái:** Nháp | Đã duyệt | Đang làm | Hoàn thành
- **Tác nhân:** <Điều phối viên / Tài xế / ...>
- **Đặc tả:** `docs/use-cases.md#uc-xx`
- **Quy tắc nghiệp vụ liên quan:** BR-xx, BR-yy
- **Người làm:** Tài | Kiệt

## Mô tả ngắn
<1-3 câu: ai làm gì, kết quả là gì>

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-xx-AC1 | <vd: Ghép đơn làm tổng khối lượng vượt tải trọng xe thì bị từ chối, báo lỗi rõ> | Logic | BR-xx |
| UC-xx-AC2 | <ca biên: đúng bằng tải trọng thì ghép được> | Logic | BR-xx |
| UC-xx-AC3 | <phân quyền: Tài xế gọi API ghép đơn thì nhận 403> | API | - |

## Ghi chú triển khai
- File đã đổi:
- Test đã viết:
- Lệnh chạy test:
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa:

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-xx-AC1 | Logic | `tests/...::test_ucxx_ac1_...` | Đạt / FAIL / CHƯA KIỂM | |
