# UC-28: Tra cứu đơn

- **Trạng thái:** Đang làm – AC1–AC6 đạt, AC7 giao diện chờ làm (Đã duyệt 11/11/2026 – Tài: đồng ý 7 AC và 4 quyết định)
- **Tác nhân:** Khách hàng (không đăng nhập)
- **Đặc tả:** `docs/use-cases.md#uc-28-tra-cứu-đơn`, `docs/api.md` mục 3.4
- **Quy tắc nghiệp vụ liên quan:** BR-59, NFR-SEC-05
- **Người làm:** Tài (backend); giao diện trang tra cứu do phiên giao diện v2 làm

## Mô tả ngắn
Khách nhập mã đơn và 4 số cuối số điện thoại, xem trạng thái hiện tại và các mốc thời gian của đơn. Không cần tài khoản, không lộ cước, GPS, số điện thoại tài xế.

## Quyết định (Tài duyệt 11/11/2026)
1. "SĐT người gửi hoặc người nhận" = `sdt_lay` (người liên hệ lấy hàng) hoặc `sdt_nhan` của đơn.
2. Mốc lấy từ lịch sử trạng thái đơn, **không** trả lý do (lý do nội bộ, vd "Sự cố xe: …"), không trả người thao tác.
3. Mã đơn bỏ khoảng trắng đầu cuối, không phân biệt hoa thường.
4. Giới hạn tần suất đếm **lần sai** theo IP trong 60 giây, lưu trong bộ nhớ tiến trình (shortcut: một tiến trình uvicorn, khởi động lại thì đếm lại). Lần sai thứ 11 trong 1 phút → 429, kể cả mã đúng.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-28-AC1 | Đ1 (SĐT lấy 0909123456, nhận 0909555666) + "3456" → 200: `ma_don`, `trang_thai`, `moc` theo thời gian; + "5666" cũng được (TC-BR59-01) | API | BR-59 |
| UC-28-AC2 | Kết quả không có cước, GPS, SĐT, tên tài xế, lý do, người thao tác: chỉ đúng các khóa `ma_don`, `trang_thai`, `moc[].trang_thai`, `moc[].luc` | API | BR-59 |
| UC-28-AC3 | Sai 4 số, mã không tồn tại → cùng 404 "Không tìm thấy đơn" (TC-BR59-02) | API | BR-59 |
| UC-28-AC4 | Dữ liệu sai: thiếu trường, 4 số không phải 4 chữ số, mã quá 20 ký tự → 400 | API | — |
| UC-28-AC5 | Một IP sai 10 lần trong 1 phút vẫn trả 404; lần 11 → 429 kể cả đúng (TC-BR59-03); IP khác không bị ảnh hưởng; qua 60 giây tra được lại | API | NFR-SEC-05 |
| UC-28-AC6 | Không cần đăng nhập; mã viết thường, có khoảng trắng vẫn tìm được | API | BR-59 |
| UC-28-AC7 | Giao diện: trang tra cứu công khai (ô mã, ô 4 số, kết quả dạng dòng thời gian); làm ở phiên giao diện v2 | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/tra_cuu/{router,service,schemas}.py` (mới), `backend/app/main.py` (đăng ký router theo chữ cái), `docs/api.md` mục 3.4.
- Test đã viết: `backend/tests/api/test_uc28_tra_cuu_don.py` (13 ca). Thử làm hỏng 5 chỗ (bỏ lọc dòng tạo đơn, `contains` thay `endswith`, lệch 1 ở ngưỡng 10, đếm chung mọi IP, lần sai không hết hạn) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc28_tra_cuu_don.py`
- Lệch đặc tả: không. Thêm rõ trong `api.md`: mốc không có lý do, IP không đọc `X-Forwarded-For`, bộ đếm trong bộ nhớ.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-28-AC1 | API | `test_uc28_ac1_tra_cuu_dung` (2 ca) | Đạt | 11/11/2026 |
| UC-28-AC2 | API | `test_uc28_ac2_khong_lo_thong_tin` | Đạt | 11/11/2026 |
| UC-28-AC3 | API | `test_uc28_ac3_sai_cung_thong_bao` | Đạt | 11/11/2026 |
| UC-28-AC4 | API | `test_uc28_ac4_du_lieu_sai` (6 ca) | Đạt | 11/11/2026 |
| UC-28-AC5 | API | `test_uc28_ac5_gioi_han_tan_suat`, `test_uc28_ac5_tra_dung_khong_tinh_sai` | Đạt | 11/11/2026 |
| UC-28-AC6 | API | `test_uc28_ac6_khong_dang_nhap_ma_tu_do` | Đạt | 11/11/2026 |
| UC-28-AC7 | UI | Trang tra cứu: phiên giao diện v2 làm | CHƯA KIỂM | |
