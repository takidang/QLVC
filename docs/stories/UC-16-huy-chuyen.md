# UC-16: Hủy chuyến

- **Trạng thái:** Hoàn thành 08/11/2026 – 10/10 AC (AC10 Kiệt thử 07/11, PR #18) (Đã duyệt 04/11/2026 – Tài)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-16) · `docs/api.md` mục 2.4 · `docs/nghiep-vu.md` BR-25, 30, mục 5.1, 5.2 · ca test `docs/ca-test-br.md` (TC-BR25-01…04)
- **Quy tắc nghiệp vụ liên quan:** BR-07 (một ghép hiệu lực), BR-16, 17 (chuyến `HUY` không chiếm lịch), BR-25 (hủy), BR-30 (lịch sử), BR-57 (phân quyền)
- **Người làm:** Tài

## Mô tả ngắn
Trên trang chi tiết chuyến `LAP` hoặc `DA_CHOT`, Điều phối bấm **Hủy chuyến**, nhập lý do. Hệ thống chặn nếu chuyến còn tạm ứng `HIEU_LUC` (Kế toán phải thu hồi trước). Được thì mọi bản ghi ghép hết hiệu lực, đơn về `CHO_GHEP`, chuyến sang `HUY`; xe và tài xế rảnh khung giờ đó để lập chuyến khác.

## Quyết định (Tài duyệt 04/11)
1. **API:** `POST /api/chuyen/{id}/huy`, body `{ly_do}` bắt buộc, cắt khoảng trắng, 1–300 ký tự; thiếu, rỗng hoặc toàn khoảng trắng, trường lạ → 400 (TC-BR25-04).
2. **Lưu lý do** vào cột `ly_do` của dòng lịch sử `CHUYEN` (`LAP`/`DA_CHOT` → `HUY`) và của dòng lịch sử từng đơn (`DA_GHEP` → `CHO_GHEP`). Không thêm cột vào bảng `chuyen` → **không cần migration**.
3. **Trạng thái sai** (`DANG_CHAY`, `HOAN_THANH`, `DA_QUYET_TOAN`, `HUY`) → 409 `BR-25` (TC-BR25-03). Còn tạm ứng `HIEU_LUC` → 409 `BR-25` "cần Kế toán thu hồi tạm ứng trước", chuyến và đơn giữ nguyên (TC-BR25-02). UC-23 chưa làm, test tạo tạm ứng trực tiếp trong CSDL như UC-15.
4. **Khóa:** khóa dòng chuyến (như ghép/gỡ/chốt) rồi các đơn đang ghép, để hủy và các thao tác đó cùng lúc chạy lần lượt. Không cần khóa xe, tài xế vì hủy chỉ trả lịch, không chiếm thêm.
5. **Giữ nguyên** các số đã chốt (`dm_*_chot`, ETA kế hoạch) của chuyến đã chốt khi hủy, làm dấu vết; chuyến `HUY` không tính lãi, không quyết toán.
6. **Response:** trả chi tiết chuyến (như ghép/gỡ/chốt), `don` rỗng.
7. **Giao diện:** nút **Hủy chuyến** trên trang chi tiết khi `LAP` hoặc `DA_CHOT`; bấm thì hiện ô nhập lý do bắt buộc và nút xác nhận; xong hiện nhãn "Hủy", ẩn mọi nút thao tác. Kiệt thử (hoặc Tài tự thử nếu đã cài Playwright).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-16-AC1 | Hủy C01 `LAP` có Đ1, Đ2, Đ4, lý do "khách hoãn" → 200, `HUY`; Đ1, Đ2, Đ4 về `CHO_GHEP`; 3 bản ghi ghép `hieu_luc = false`, không còn ghép hiệu lực nào của chuyến (TC-BR25-01) | API | BR-25 |
| UC-16-AC2 | Hủy C01 `DA_CHOT` (không tạm ứng) → `HUY`, đơn về `CHO_GHEP`; số đã chốt vẫn giữ | API | BR-25 |
| UC-16-AC3 | Sau khi hủy: đơn Đ1 ghép được vào chuyến khác (BR-07: đơn có 2 bản ghi, 1 hiệu lực); lập chuyến mới cùng xe, cùng tài xế, cùng giờ với chuyến đã hủy → 201 (BR-16, 17 bỏ qua chuyến `HUY`) | API | BR-07, 16, 17 |
| UC-16-AC4 | Còn tạm ứng 1.000.000 `HIEU_LUC` → 409 `BR-25`, chuyến vẫn `DA_CHOT`, đơn vẫn `DA_GHEP`; tạm ứng `DA_THU_HOI` → hủy được (TC-BR25-02) | API | BR-25 |
| UC-16-AC5 | Trạng thái sai: `DANG_CHAY`, `HOAN_THANH`, `HUY` (hủy lần 2) → 409 `BR-25`, không đổi gì (TC-BR25-03); chuyến không tồn tại → 404 | API | BR-25 |
| UC-16-AC6 | Lý do: thiếu, rỗng, toàn khoảng trắng → 400 (TC-BR25-04); 301 ký tự → 400, đúng 300 ký tự đạt (biên); trường lạ → 400 | API | BR-25 |
| UC-16-AC7 | Lịch sử: 1 dòng `CHUYEN` `LAP → HUY` và 1 dòng mỗi đơn `DA_GHEP → CHO_GHEP`, đều có lý do "khách hoãn" và người hủy | API | BR-30 |
| UC-16-AC8 | Đồng thời: hủy và ghép đơn vào cùng chuyến gửi cùng lúc → không có đơn nào kẹt ở `DA_GHEP` của chuyến `HUY` (hoặc ghép trước rồi hủy trả về `CHO_GHEP`, hoặc hủy trước rồi ghép nhận 409) | API | BR-25, 09 |
| UC-16-AC9 | Phân quyền: Điều phối, Quản lý hủy được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-16-AC10 | Giao diện: nút Hủy chuyến khi `LAP`/`DA_CHOT`; bắt buộc nhập lý do; hủy xong hiện "Hủy", ẩn các nút; còn tạm ứng hiện thông báo kèm BR-25 | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/chuyen/{service,router,schemas}.py` (`huy`, `HuyVao`; `_doi_trang_thai`, `_doi_trang_thai_chuyen` nhận thêm `ly_do`; tách `_con_tam_ung` dùng chung với mở chốt), `frontend/src/api/chuyen.ts`, `frontend/src/pages/dieu-phoi/ChuyenChiTiet.tsx` (nút Hủy chuyến, ô lý do), `docs/api.md`.
- Không cần migration (lý do lưu ở `lich_su_trang_thai.ly_do`).
- Test đã viết: `backend/tests/api/test_uc16_huy_chuyen.py` (21 ca, dùng fixture `kb` của UC-13 và hàm của test UC-15). Toàn bộ 459 passed, ruff sạch, frontend lint + build đạt.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc16_huy_chuyen.py`
- Dữ liệu thử giao diện: `docs/test-evidence/UC-16/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-16-AC1 | API | `test_uc16_ac1_huy_chuyen_lap` | Đạt | 04/11/2026 |
| UC-16-AC2 | API | `test_uc16_ac2_huy_chuyen_da_chot` | Đạt | 04/11/2026 |
| UC-16-AC3 | API | `test_uc16_ac3_don_va_lich_duoc_giai_phong` | Đạt | 04/11/2026 |
| UC-16-AC4 | API | `test_uc16_ac4_con_tam_ung` | Đạt | 04/11/2026 |
| UC-16-AC5 | API | `test_uc16_ac5_* (4 ca)` | Đạt | 04/11/2026 |
| UC-16-AC6 | API | `test_uc16_ac6_* (6 ca)` | Đạt | 04/11/2026 |
| UC-16-AC7 | API | `test_uc16_ac7_lich_su_co_ly_do` | Đạt | 04/11/2026 |
| UC-16-AC8 | API | `test_uc16_ac8_huy_va_ghep_dong_thoi` | Đạt | 04/11/2026 |
| UC-16-AC9 | API | `test_uc16_ac9_* (5 ca)` | Đạt | 04/11/2026 |
| UC-16-AC10 | UI | Kiệt thử 6/6 ca: `docs/test-evidence/UC-16/`; hủy chuyến có đơn → đơn về chờ ghép (CSDL); BR-25 có tạm ứng chưa thử giao diện (test tự động) | Đạt | 07/11/2026 |
