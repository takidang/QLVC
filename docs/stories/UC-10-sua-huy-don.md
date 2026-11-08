# UC-10: Sửa / hủy đơn

- **Trạng thái:** Đang làm – AC1–AC11 đạt, AC12 giao diện đã làm, chờ thử (Đã duyệt 08/11/2026 – Tài: đồng ý cả 9 quyết định)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-10) · `docs/api.md` mục 2.3 (`PATCH /api/don/{id}`, `POST /api/don/{id}/huy`) · `docs/nghiep-vu.md` BR-30…34, 46…48, 62, 67, mục 5.2 · ca test `docs/ca-test-br.md` (TC-BR33-01, 02, TC-BR34-01, 03)
- **Quy tắc nghiệp vụ liên quan:** BR-30 (lịch sử), BR-31 (đơn hợp lệ), BR-32, 33 (sửa, cước từ bản sao), BR-34 (hủy), BR-46…48 (cước), BR-57 (phân quyền), BR-62 (nhật ký tiền), BR-67 (kiểm lại cả chuyến)
- **Người làm:** Tài

## Mô tả ngắn
Điều phối sửa đơn chưa lấy hàng (hàng hóa, địa chỉ, người liên hệ, khung giờ lấy, hạn giao); hệ thống kiểm lại đơn hợp lệ, đơn đang ghép thì kiểm lại cả chuyến, cước tính lại từ bản sao giá đã chốt. Điều phối hủy đơn chưa lấy kèm lý do; đơn đang ghép thì tự gỡ khỏi chuyến trước khi hủy.

## Quyết định (đề xuất, chờ Tài duyệt)
1. **Sửa:** `PATCH /api/don/{id}`, gửi trường nào sửa trường đó. Sửa được: `mo_ta`, `kg`, `m3`, `so_kien`, địa chỉ / tọa độ / người liên hệ / SĐT lấy và giao, `lay_tu`, `lay_den`, `han_giao`. **Không sửa** khách, nút lấy, nút giao (đổi tỉnh thì bản sao giá không còn đúng cặp tỉnh, BR-32): cần thì hủy và tạo đơn mới. Gửi các trường đó hoặc trường lạ → 400. Body rỗng → 400.
2. **Trạng thái được sửa (BR-33):** `CHO_GHEP`; `DA_GHEP` khi chuyến đang `LAP` → kiểm lại cả chuyến theo BR-67 (dùng lại `xet_ghep` của UC-13), vi phạm → 422 `VI_PHAM_SUA` kèm danh sách BR từng đơn, không đổi gì. Chuyến đã chốt → 409 `BR-33` "mở chốt chuyến trước". Trạng thái khác → 409 `BR-33` (TC-BR33-02).
3. **Cước (BR-33, 46…48):** tính lại từ bản sao trên đơn (`don_gia_chot`, `cuoc_toi_thieu_chot`, `he_so_quy_doi_chot`, `lam_tron_chot`), không đọc bảng giá hiện tại. Cước đổi thì ghi 1 dòng nhật ký tiền `don_hang` / `SUA`, giá trị cũ, mới, lý do "Sửa đơn" (BR-62, security-rules: cước là dữ liệu tiền). Cước không đổi thì không ghi.
4. **Kiểm lại BR-31** trên đơn sau khi sửa: kg, m³ > 0, số kiện ≥ 1, khung lấy `từ < đến`, hạn giao > lúc sửa và > `từ`. Hạn giao không đổi thì không bắt > lúc sửa (sửa SĐT đơn sắp tới hạn vẫn được).
5. **Hủy:** `POST /api/don/{id}/huy`, body `{ly_do}` bắt buộc, cắt khoảng trắng, 1–300 ký tự (như UC-16). `CHO_GHEP` → `HUY`. `DA_GHEP` khi chuyến `LAP` → gỡ khỏi chuyến (ghép `hieu_luc = false`, lịch trình tính lại như gỡ ở UC-13) rồi `HUY`; chuyến đã chốt → 409 `BR-34`. `DA_LAY`, `DA_GIAO`, `TRA_HANG`, `HUY` → 409 `BR-34` (TC-BR34-03). `THAT_BAI` để UC-22 (cùng endpoint, UC-22 mở thêm) – ở UC-10 trả 409.
6. **Lịch sử (BR-30):** hủy ghi `… → HUY` kèm lý do; đơn đang ghép ghi thêm `DA_GHEP → CHO_GHEP` trước. Sửa không đổi trạng thái nên không ghi lịch sử trạng thái.
7. **Khóa:** đơn đang ghép thì khóa chuyến trước rồi tới đơn (thứ tự kien-truc.md); đơn chờ ghép khóa dòng đơn. Sửa / hủy và ghép cùng lúc chạy lần lượt.
8. **Response:** cả hai trả chi tiết đơn (`DonRa`) như `GET /api/don/{id}`.
9. **Giao diện:** danh sách đơn (Điều phối) có nút **Sửa** (form như tạo đơn, điền sẵn, ô khách và nút khóa) và **Hủy** (ô lý do bắt buộc) cho đơn `CHO_GHEP` / `DA_GHEP`; vi phạm hiện bảng mã BR như ghép; cước mới hiện ngay sau khi lưu.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-10-AC1 | Đ4 `CHO_GHEP` (bản sao giá 1.000); Quản lý đổi giá HCM → Tiền Giang thành 1.200; sửa Đ4 kg 800 → 900 → 200, cước **900.000** (từ bản sao, TC-BR33-01); nhật ký tiền 1 dòng `SUA` 800.000 → 900.000, người sửa | API | BR-33, 48, 62 |
| UC-10-AC2 | Sửa m³ làm KL quy đổi vượt kg (Đ4 m³ 2 → 3: 3 × 333 = 999 > 800) → cước 999.000; sửa chỉ SĐT nhận → cước giữ, không thêm dòng nhật ký tiền | API | BR-46, 47, 62 |
| UC-10-AC3 | BR-31 khi sửa: kg 0, m³ 0, số kiện 0 → 400; khung lấy 09:00–06:30 → 422 `BR-31`; hạn giao = lúc sửa → 422; hạn giao sau lúc sửa 1 phút đạt (biên); đơn không tồn tại → 404 | API | BR-31 |
| UC-10-AC4 | Đơn đang ghép, chuyến `LAP` (C01 có Đ1, Đ2, Đ4, xe 5.000 kg, tổng 3.800 kg): sửa hạn giao Đ2 thành 11:49 (ETA giao 11:50) → 422 `VI_PHAM_SUA` có `BR-06` của Đ2, không đổi; 11:50 đạt (biên); sửa Đ1 kg thành 3.000 (tổng 5.000) đạt, 3.001 → `BR-01` (biên) | API | BR-33, 67 |
| UC-10-AC5 | Trạng thái sai: Đ1 `DA_LAY` sửa kg → 409 `BR-33`, không đổi (TC-BR33-02); đơn đang ghép vào chuyến `DA_CHOT` → 409 `BR-33` | API | BR-33 |
| UC-10-AC6 | Gửi `nut_giao_id`, `khach_hang_id` hoặc trường lạ → 400; body rỗng → 400 | API | BR-32, 33 |
| UC-10-AC7 | Hủy Đ8 `CHO_GHEP` lý do "khách hủy" → 200, `HUY`; lịch sử 1 dòng `CHO_GHEP → HUY` có lý do, người hủy (TC-BR34-01). Lý do thiếu, rỗng, toàn khoảng trắng, 301 ký tự → 400; đúng 300 ký tự đạt (biên) | API | BR-30, 34 |
| UC-10-AC8 | Hủy Đ4 đang ghép vào C01 `LAP` → `HUY`; ghép của Đ4 `hieu_luc = false`; lịch trình C01 không còn điểm của Đ4; lịch sử `DA_GHEP → CHO_GHEP`, `CHO_GHEP → HUY`. Đơn ở chuyến `DA_CHOT` → 409 `BR-34`, không đổi | API | BR-30, 34, 67 |
| UC-10-AC9 | Hủy sai trạng thái: `DA_LAY` → 409 `BR-34` (TC-BR34-03); `HUY` (hủy lần 2), `DA_GIAO`, `THAT_BAI` → 409 | API | BR-34 |
| UC-10-AC10 | Đồng thời: hủy đơn và ghép chính đơn đó vào chuyến gửi cùng lúc → đơn không vừa `HUY` vừa có ghép hiệu lực (hoặc ghép trước rồi hủy tự gỡ, hoặc hủy trước rồi ghép nhận 409) | API | BR-34, 07 |
| UC-10-AC11 | Phân quyền: Điều phối, Quản lý sửa / hủy được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-10-AC12 | Giao diện: danh sách đơn có Sửa / Hủy cho đơn chờ ghép, đã ghép; form sửa điền sẵn, khách và nút khóa; lưu xong hiện cước mới; vi phạm hiện bảng mã BR; hủy bắt buộc lý do | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/don/sua_huy.py` (mới: `sua`, `huy`, khóa chuyến → xe → tài xế → đơn, đọc lại khi đơn vừa bị ghép / gỡ), `don/{router,schemas}.py` (`PATCH /api/don/{id}`, `POST /api/don/{id}/huy`, `DonSua`, `HuyDonVao`; `DonRa` thêm `nguoi_lien_he_lay` để form sửa điền sẵn), `chuyen/service.py` (tách `xet_ca_chuyen` từ ghép, `go_da_khoa` từ gỡ để dùng chung; hành vi ghép / gỡ không đổi), `frontend/src/api/don.ts`, `frontend/src/pages/dieu-phoi/DonDanhSach.tsx` (nút Sửa / Hủy, form sửa dùng lại form tạo đơn, hộp hủy), `docs/api.md`.
- Không cần migration.
- Test đã viết: `backend/tests/api/test_uc10_sua_huy_don.py` (35 ca, dùng fixture `kb` của UC-13). Toàn bộ 665 passed, ruff sạch; frontend tsc, oxlint, prettier, build sạch.
- Thử làm hỏng 4 chỗ (bỏ kiểm cả chuyến khi sửa, bỏ tự gỡ khi hủy, bỏ nhật ký tiền, bỏ chặn trạng thái) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc10_sua_huy_don.py`
- Lệch đặc tả: thêm mã `VI_PHAM_SUA`, `VI_PHAM_HUY` (như `VI_PHAM_GHEP`, `VI_PHAM_GO`); không cho đổi khách, nút lấy / giao (quyết định 1). Đã ghi vào `api.md`.
- Dữ liệu thử giao diện: `docs/test-evidence/UC-10/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-10-AC1 | API | `test_uc10_ac1_sua_kg_tinh_lai_cuoc_tu_ban_sao` | Đạt | 08/11/2026 |
| UC-10-AC2 | API | `test_uc10_ac2_m3_quy_doi_va_khong_doi_cuoc` | Đạt | 08/11/2026 |
| UC-10-AC3 | API | `test_uc10_ac3_* (5 ca)` | Đạt | 08/11/2026 |
| UC-10-AC4 | API | `test_uc10_ac4_* (2 ca)` | Đạt | 08/11/2026 |
| UC-10-AC5 | API | `test_uc10_ac5_trang_thai_khong_sua_duoc` | Đạt | 08/11/2026 |
| UC-10-AC6 | API | `test_uc10_ac6_* (6 ca)` | Đạt | 08/11/2026 |
| UC-10-AC7 | API | `test_uc10_ac7_* (6 ca)` | Đạt | 08/11/2026 |
| UC-10-AC8 | API | `test_uc10_ac8_* (2 ca)` | Đạt | 08/11/2026 |
| UC-10-AC9 | API | `test_uc10_ac9_* (5 ca)` | Đạt | 08/11/2026 |
| UC-10-AC10 | API | `test_uc10_ac10_huy_va_ghep_dong_thoi` | Đạt | 08/11/2026 |
| UC-10-AC11 | API | `test_uc10_ac11_* (5 ca)` | Đạt | 08/11/2026 |
| UC-10-AC12 | UI | Chờ thử (`docs/test-evidence/UC-10/du-lieu.md`) | CHƯA KIỂM | |
