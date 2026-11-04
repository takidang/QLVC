# UC-15: Chốt / mở chốt chuyến

- **Trạng thái:** Đang làm – AC1–AC10 đạt, AC11 giao diện đã làm, chờ Kiệt thử (Đã duyệt 01/11/2026 – Tài: xác nhận chạy rỗng một lần là đủ; mở chốt xóa số đã chốt)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-15) · `docs/api.md` mục 2.4 · `docs/nghiep-vu.md` BR-23, 24, 52, 71, mục 2.1, 5.1, mục 11 bước 4 · ca test `docs/ca-test-br.md` (TC-BR23-01…03, BR24-01, 02, BR30-01, BR52-01, 02, BR71-01, 02)
- **Quy tắc nghiệp vụ liên quan:** BR-01…06 (nhóm A), BR-11…19 (nhóm B), BR-23 (chốt), BR-24 (mở chốt), BR-30 (lịch sử), BR-52 (lãi dự kiến), BR-57 (phân quyền), BR-71 (lưu định mức, lương, ETA kế hoạch)
- **Người làm:** Tài

## Mô tả ngắn
Trên trang chi tiết chuyến `LAP`, Điều phối bấm **Chốt**. Hệ thống kiểm lại cả chuyến (nhóm A, B), bắt xác nhận nếu chuyến không có đơn (chạy rỗng) hoặc lãi dự kiến âm, rồi lưu định mức, lương khoán của tuyến và ETA kế hoạch từng điểm vào chuyến; chuyến sang `DA_CHOT` (tài xế thấy ở UC-17). Chuyến `DA_CHOT` bấm **Mở chốt** để về `LAP` nếu không còn tạm ứng `HIEU_LUC`.

## Quyết định (Tài duyệt 01/11)
1. **Kiểm lại khi chốt:** BR-01…06 cho mọi đơn đang ghép (dùng lại `xet_ghep` của UC-13, lô mới rỗng) và đủ BR-11…19 cho xe, tài xế theo khoảng chiếm hiện tại (bỏ qua chính chuyến này). Có vi phạm → 422 `VI_PHAM_CHOT`, `chi_tiet` liệt kê mã BR, không chốt.
2. **Thứ tự kiểm:** vi phạm → chạy rỗng → lãi âm. Chuyến 0 đơn thiếu `xac_nhan_chay_rong` → 422 `BR-23`. Có đơn, lãi âm, thiếu `xac_nhan_lai_am` → 422 `BR-52`, thông điệp kèm số lãi. Chuyến rỗng luôn lãi âm (chỉ có chi phí), nên **xác nhận chạy rỗng là đủ**, không hỏi thêm lãi âm (khớp TC-BR23-03).
3. **Lưu khi chốt (BR-71):** `dm_dau_chot`, `dm_cau_duong_chot`, `dm_boc_xep_chot`, `luong_tai_xe_chot` từ tuyến; `chay_rong`; `eta_lay_ke_hoach`, `eta_giao_ke_hoach` vào từng bản ghi ghép hiệu lực. Đơn giữ `DA_GHEP` (ST-O không đổi khi chốt). Ghi 1 dòng lịch sử `LAP → DA_CHOT` (BR-30).
4. **Mở chốt (BR-24):** còn tạm ứng `HIEU_LUC` → 409 `BR-24` "cần Kế toán thu hồi tạm ứng trước". Được thì về `LAP`, **xóa** các số đã chốt, `chay_rong`, ETA kế hoạch (khi `LAP` lãi dự kiến lấy từ tuyến – BR-52; chốt lại lưu theo số mới – BR-71). Ghi lịch sử `DA_CHOT → LAP`. UC-23 tạm ứng chưa làm, test tạo tạm ứng trực tiếp trong CSDL.
5. **Trạng thái sai:** chốt chuyến không `LAP`, mở chốt chuyến không `DA_CHOT` → 409 `BR-09` như UC-13. Khóa dòng chuyến → xe → tài xế (kien-truc.md mục 5) để chốt và ghép cùng lúc chạy lần lượt.
6. **Response:** cả hai trả chi tiết chuyến (như ghép/gỡ), thêm `chay_rong`; lãi dự kiến sau chốt lấy số đã chốt (code UC-13 đã có).
7. **Giao diện:** trên trang chi tiết chuyến: nút **Chốt chuyến** (khi `LAP`) và **Mở chốt** (khi `DA_CHOT`); chặn vì chạy rỗng / lãi âm thì hiện hộp xác nhận rồi gửi lại kèm cờ; vi phạm hiện bảng mã BR như ghép. Chuyến `DA_CHOT` ẩn phần ghép/gỡ. Kiệt thử.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-15-AC1 | Chốt C01 `LAP` có Đ1, Đ2, Đ4 (`POST /api/chuyen/{id}/chot`) → 200, `DA_CHOT`, lãi dự kiến **3.637.000**, không cần xác nhận (TC-BR23-01, BR52-01) | API | BR-23, 52 |
| UC-15-AC2 | Sau chốt lưu `dm_dau_chot` 550.000, cầu đường 200.000, bốc xếp 250.000, lương 600.000; ETA kế hoạch 6 điểm khớp lịch trình (06:00 / 06:20 / 07:40 / 09:00 / 11:50 / 12:10); sửa định mức dầu T01 thành 600.000 → chuyến vẫn giữ 550.000, lãi không đổi (TC-BR71-01) | API | BR-71 |
| UC-15-AC3 | Chuyến 0 đơn: chốt không gửi `xac_nhan_chay_rong` → 422 `BR-23`, vẫn `LAP`; gửi `xac_nhan_chay_rong=true` → `DA_CHOT`, `chay_rong = true` (TC-BR23-02, 03) | API | BR-23 |
| UC-15-AC4 | C01 chỉ có Đ8: chốt không gửi `xac_nhan_lai_am` → 422 `BR-52`, thông điệp có −1.267.000, vẫn `LAP`; gửi `xac_nhan_lai_am=true` → `DA_CHOT` (TC-BR52-02); lãi đúng bằng 0 không cần xác nhận (biên) | API | BR-52 |
| UC-15-AC5 | Kiểm lại nhóm B khi chốt: đăng kiểm xe hết hạn trước ngày kết thúc (sửa trực tiếp sau khi lập) → 422 `VI_PHAM_CHOT` có `BR-12`, vẫn `LAP`; hạn đúng bằng ngày kết thúc đạt (biên); tài xế bị chuyển `NGUNG` → có lý do tài xế ngừng; xe `NGUNG` → `BR-11` | API | BR-11…19, 23 |
| UC-15-AC6 | Kiểm lại nhóm A khi chốt: sửa trực tiếp hạn giao Đ2 sớm hơn ETA giao (11:50 → hạn 11:49) → 422 `VI_PHAM_CHOT` có `BR-06` của Đ2; hạn đúng 11:50 đạt (biên) | API | BR-01…06, 23 |
| UC-15-AC7 | Mở chốt (`POST /api/chuyen/{id}/mo-chot`): còn tạm ứng 1.000.000 `HIEU_LUC` → 409 `BR-24`, vẫn `DA_CHOT`; tạm ứng `DA_THU_HOI` → về `LAP`, số chốt và ETA kế hoạch bị xóa, lãi lấy lại từ tuyến; chốt lại sau khi định mức dầu thành 600.000 → `dm_dau_chot` 600.000 (TC-BR24-01, 02, BR71-02) | API | BR-24, 71 |
| UC-15-AC8 | Lịch sử: chốt rồi mở chốt C01 bởi `dp1` → 2 dòng `CHUYEN` `LAP → DA_CHOT`, `DA_CHOT → LAP`, người `dp1` (TC-BR30-01) | API | BR-30 |
| UC-15-AC9 | Trạng thái và khóa: chốt chuyến `DA_CHOT` → 409 `BR-09`; mở chốt chuyến `LAP` → 409 `BR-09`; chuyến đã chốt không ghép/gỡ được (409 `BR-09`); chuyến không tồn tại → 404; trường lạ trong body → 400; hai yêu cầu chốt **đồng thời** → đúng một 200, cái kia 409 | API | BR-09, 23 |
| UC-15-AC10 | Phân quyền: Điều phối, Quản lý chốt / mở chốt được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-15-AC11 | Giao diện: trang chi tiết chuyến có nút Chốt chuyến / Mở chốt theo trạng thái; chuyến rỗng hoặc lãi âm hiện hộp xác nhận, đồng ý thì chốt; vi phạm hiện bảng mã BR; mở chốt khi còn tạm ứng hiện thông báo BR-24; chuyến đã chốt ẩn phần ghép/gỡ | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/chuyen/{service,router,schemas}.py` (`chot`, `mo_chot`, `ChotVao`; `_khoa_chuyen` nhận trạng thái cần và tên việc; chi tiết chuyến thêm `chay_rong`), `frontend/src/api/chuyen.ts`, `frontend/src/pages/dieu-phoi/ChuyenChiTiet.tsx` (nút Chốt chuyến / Mở chốt, hộp xác nhận), `docs/api.md`.
- Không cần migration: các cột `dm_*_chot`, `luong_tai_xe_chot`, `chay_rong`, `eta_*_ke_hoach` có từ ERD 0.5.
- Test đã viết: `backend/tests/api/test_uc15_chot_chuyen.py` (17 ca, dùng fixture `kb` của UC-13). Toàn bộ 412 passed, ruff sạch, frontend lint + build đạt.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc15_chot_chuyen.py`
- Lệch đặc tả: thêm mã `VI_PHAM_CHOT` (như `VI_PHAM_GHEP`); body chốt tùy chọn. Đã ghi vào `api.md`.
- Dữ liệu thử giao diện cho Kiệt: `docs/test-evidence/UC-15/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-15-AC1 | API | `test_uc15_ac1_ac2_chot_c01` | Đạt | 01/11/2026 |
| UC-15-AC2 | API | `test_uc15_ac1_ac2_chot_c01` | Đạt | 01/11/2026 |
| UC-15-AC3 | API | `test_uc15_ac3_chay_rong_can_xac_nhan` | Đạt | 01/11/2026 |
| UC-15-AC4 | API | `test_uc15_ac4_* (2 ca)` | Đạt | 01/11/2026 |
| UC-15-AC5 | API | `test_uc15_ac5_* (3 ca)` | Đạt | 01/11/2026 |
| UC-15-AC6 | API | `test_uc15_ac6_han_giao_doi_sau_khi_ghep` | Đạt | 01/11/2026 |
| UC-15-AC7 | API | `test_uc15_ac7_mo_chot_va_chot_lai` | Đạt | 01/11/2026 |
| UC-15-AC8 | API | `test_uc15_ac8_lich_su` | Đạt | 01/11/2026 |
| UC-15-AC9 | API | `test_uc15_ac9_* (2 ca, có ca đồng thời)` | Đạt | 01/11/2026 |
| UC-15-AC10 | API | `test_uc15_ac10_* (5 ca)` | Đạt | 01/11/2026 |
| UC-15-AC11 | UI | Chờ Kiệt thử (`docs/test-evidence/UC-15/du-lieu.md`) | CHƯA KIỂM | |
