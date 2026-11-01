# UC-13: Ghép / gỡ đơn khỏi chuyến

- **Trạng thái:** Hoàn thành (01/11/2026, 13/13 AC, giao diện Kiệt thử 30/10) (Đã duyệt 30/10/2026 – Tài: lãi âm khi ghép chỉ cảnh báo; trang chi tiết chuyến riêng)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán xem chi tiết chuyến
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-13) · `docs/api.md` mục 2.4, 3.1 · `docs/nghiep-vu.md` nhóm A, H, mục 2.1, mục 11 bước 3 · ca test `docs/ca-test-br.md` (TC-BR01…09, 30, 49, 52, 63, 64, 67)
- **Quy tắc nghiệp vụ liên quan:** BR-01…09 (ghép), BR-10 (điểm dừng suy ra), BR-30 (lịch sử), BR-49 (kiểm tải theo kg thực), BR-52 (lãi dự kiến), BR-57, BR-63 (lịch trình, ETA), BR-64 (kết thúc dự kiến), BR-67 (kiểm lại cả chuyến)
- **Người làm:** Tài

## Mô tả ngắn
Điều phối mở một chuyến `LAP`, thấy tải, thể tích, % đầy, lịch trình kèm ETA, lãi dự kiến, đơn đang ghép và đơn `CHO_GHEP` phù hợp tuyến. Chọn một hoặc nhiều đơn để ghép, hoặc gỡ đơn đang ghép. Mỗi lần ghép/gỡ hệ thống tính lại lịch trình và kiểm lại **cả chuyến** (BR-67) trong một giao dịch; có vi phạm ở bất kỳ đơn nào (kể cả đơn đã ghép trước bị dịch ETA) thì không làm gì cả, báo đủ đơn nào vi phạm quy tắc nào.

## Quyết định (Tài duyệt 30/10)
1. **Lịch trình là hàm thuần** `lich_trinh(khoi_hanh, phut theo thứ tự nút, đơn, phút dừng)` theo đúng BR-63: thứ tự nút; trong một nút LẤY trước GIAO; LẤY: có khung trước (đầu khung sớm trước), không khung sau, cùng thì theo mã đơn; GIAO: hạn sớm trước, cùng hạn theo mã đơn. ETA = khởi hành + phút của nút + số điểm đứng trước × `CFG-08`. Phút dừng viết thành hàm riêng `phut_dung()` (mục 2.1).
2. **Nút lấy hiệu dụng** = nút giữ hàng nếu có (BR-69, đơn ghép lại), không thì nút lấy – dùng cho BR-03, 04, 63. UC-22 sẽ đặt nút giữ hàng.
3. **Kiểm cả chuyến mỗi lần ghép/gỡ** (BR-67): BR-01, 02, 03, 04, 05, 06 cho mọi đơn hiệu lực; BR-12, 13, 15 theo ngày kết thúc dự kiến mới; BR-16, 17 theo khoảng chiếm mới (bỏ qua chính chuyến này). Giờ lái (BR-18, 19) không đổi khi ghép nên không kiểm lại.
4. **Lưu `ket_thuc_du_kien` mới vào chuyến** sau mỗi lần ghép/gỡ, để UC-11 lập chuyến khác thấy đúng khoảng chiếm.
5. **Chống ghép trùng:** khóa dòng chuyến, rồi xe, tài xế (cùng thứ tự với UC-11), rồi các đơn; đơn không còn `CHO_GHEP` → 409 `BR-09`; chỉ mục unique ở CSDL là lớp chặn cuối (409 `BR-07`).
6. **Lãi dự kiến âm khi ghép:** chỉ hiện cảnh báo (`canh_bao_lai_am: true`), **không** bắt xác nhận; xác nhận ở lúc chốt (UC-15, `xac_nhan_lai_am`).
7. **Chi tiết chuyến** (`GET /api/chuyen/{id}`) trả thêm thẻ Hàng: tải, thể tích, % đầy, lịch trình, kết thúc dự kiến, lãi dự kiến, đơn đang ghép. Response của ghép/gỡ dùng chung dạng này (api.md mục 3.1).
8. **Gỡ đơn không thuộc chuyến** (hoặc đã gỡ) → 422 `DON_KHONG_THUOC_CHUYEN`; chuyến không ở `LAP` → 409 `BR-09`.
9. **Giao diện:** trang chi tiết chuyến riêng (`/dieu-phoi/chuyen/:id`, bấm mã chuyến ở danh sách để mở); Kiệt thử.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-13-AC1 | Lịch trình (hàm thuần): C01 có Đ1, Đ2, Đ4, khởi hành 06:00, `CFG-08` 20′ → 6 điểm, ETA 06:00 lấy Đ1 / 06:20 lấy Đ4 / 07:40 lấy Đ2 / 09:00 giao Đ4 / 11:50 giao Đ2 / 12:10 giao Đ1 (TC-BR63-01, 02); có khung lấy xếp trước không khung (TC-BR63-03); cùng không khung xếp theo mã đơn (TC-BR63-04); lấy và giao cùng nút: LẤY trước GIAO (TC-BR04-03) | Logic | BR-63 |
| UC-13-AC2 | Kết thúc dự kiến: C01 có Đ1, Đ2, Đ4 → 12:10 + 20′ + 60′ = **13:30** (TC-BR64-01); không đơn → công thức chạy rỗng 11:30 | Logic | BR-64 |
| UC-13-AC3 | Tải và thể tích theo **kg thực**: Đ1, Đ4 + Đ2 = 3.800 kg đạt; + Đ6 = 5.100 > 5.000 → `BR-01`; + Đ9 đúng 5.000 đạt (biên); thể tích đúng 20 m³ đạt, 20,01 → `BR-02`; xe 1.900 kg chở Đ1 (1.800 kg thực, KL tính cước 1.998) đạt (TC-BR01-01…03, BR02-01, 02, BR49-01) | Logic | BR-01, 02, 49 |
| UC-13-AC4 | Đúng tuyến, đúng chiều: Đ12 giao Bến Tre (không thuộc T01) → `BR-03`; Đ5 Vĩnh Long → Long An → `BR-04`; lấy và giao cùng nút đạt (biên); đơn có nút giữ hàng thì dùng nút giữ hàng thay nút lấy | Logic | BR-03, 04 |
| UC-13-AC5 | Khung giờ lấy (đóng hai đầu) và hạn giao: Đ2 khung 06:30–09:00, ETA 07:40 đạt; khung 06:30–07:30 → `BR-05` (trễ); 08:00–09:00 → `BR-05` (sớm); 07:40–09:00 đạt (biên); không khung đạt; Đ3 ETA giao 10:50 > hạn 10:00 → `BR-06`; hạn đúng bằng ETA đạt (biên) (TC-BR05-01…05, BR06-01…03) | Logic | BR-05, 06 |
| UC-13-AC6 | Kiểm lại cả chuyến: C01 có Đ1, Đ2, Đ4, ghép Đ8 → vi phạm `BR-06` nằm ở **Đ2** (ETA 12:30 > 12:00), Đ8 không có lỗi (TC-BR67-01); gỡ Đ4 khỏi C01 có Đ2c (khung 07:40–09:00) → `BR-05` ở Đ2c, ETA lấy dịch về 07:20 (TC-BR67-02) | Logic | BR-67 |
| UC-13-AC7 | `POST /api/chuyen/{id}/ghep` hợp lệ (C01, Đ1 + Đ4 rồi Đ2) → 200 đúng mẫu api.md 3.1: 3.800/5.000 kg, 11/20 m³, % đầy 0,76, kết thúc 13:30, lịch trình 6 điểm, lãi dự kiến **3.637.000**; đơn → `DA_GHEP`, có bản ghi ghép hiệu lực, lịch sử `CHO_GHEP → DA_GHEP` (TC-BR30-02); `ket_thuc_du_kien` của chuyến lưu 13:30 | API | BR-30, 52, 63, 64 |
| UC-13-AC8 | Ghép bị chặn, **không ghép đơn nào trong lô**: lô [Đ2, Đ6] → 422 `VI_PHAM_GHEP`, `chi_tiet` có `don_id`, mã BR, câu tiếng Việt; Đ2 vẫn `CHO_GHEP`. Kết thúc dự kiến lùi làm chồng chuyến khác của tài xế → `BR-17` (TC-BR67-04); lùi sang ngày sau khi đăng kiểm hết hôm nay → `BR-12` | API | BR-01…06, 12, 17, 67 |
| UC-13-AC9 | Trạng thái và xung đột: chuyến `DA_CHOT` → 409 `BR-09`; đơn đang `DA_GHEP` ở chuyến khác → 409 `BR-09`; chuyến, đơn không tồn tại → 404; `don_ids` rỗng hoặc có trường lạ → 400 (TC-BR08-01); gỡ rồi ghép vào chuyến khác được, đơn có 2 bản ghi, đúng 1 hiệu lực (TC-BR07-01); hai yêu cầu ghép cùng một đơn vào hai chuyến **đồng thời** → đúng một 200, cái kia 409 (TC-BR07-02) | API | BR-07, 08, 09 |
| UC-13-AC10 | `POST /api/chuyen/{id}/go`: gỡ Đ4 → ghép `hieu_luc = false`, Đ4 `CHO_GHEP`, lịch sử `DA_GHEP → CHO_GHEP`, kết thúc dự kiến rút lại; gỡ làm đơn khác vi phạm → 422, không gỡ (TC-BR67-02); gỡ đơn không thuộc chuyến → 422; chuyến không `LAP` → 409 | API | BR-67 |
| UC-13-AC11 | `GET /api/chuyen/{id}/don-phu-hop`: chỉ đơn `CHO_GHEP` thuộc tuyến và đúng chiều (không có Đ5, Đ12, đơn đã ghép); `GET /api/chuyen/{id}` trả thẻ Hàng (tải, thể tích, % đầy, lịch trình, lãi dự kiến, đơn đang ghép); lãi âm có `canh_bao_lai_am: true` | API | BR-03, 04, 52 |
| UC-13-AC12 | Phân quyền: Điều phối, Quản lý ghép, gỡ, xem đơn phù hợp; Kế toán xem chi tiết chuyến được, ghép/gỡ/đơn phù hợp → 403; Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-13-AC13 | Giao diện: trang chi tiết chuyến – thanh tải, thể tích, % đầy, lãi dự kiến (âm thì tô đỏ), bảng lịch trình kèm ETA, đơn đang ghép (chọn để gỡ), đơn phù hợp (chọn nhiều để ghép); bị chặn thì hiện bảng đơn – mã BR – nội dung | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/lich_trinh.py` (mới: lịch trình BR-63, kết thúc BR-64, kiểm ghép BR-01…06, % đầy, lãi BR-52), `backend/app/modules/chuyen/{schemas,service,router}.py` (ghép, gỡ, đơn phù hợp, chi tiết chuyến), `backend/app/modules/don/service.py` (đổi tên `truy_van_don`, `ra_don` để dùng lại); `frontend/src/pages/dieu-phoi/ChuyenChiTiet.tsx` (mới), `frontend/src/api/{chuyen,don}.ts`, `frontend/src/App.tsx` (route ẩn `chuyen/:id`), `ChuyenDanhSach.tsx` (bấm mã chuyến mở chi tiết); `docs/api.md`. Không đụng `models/`, không thêm migration.
- Test đã viết: `backend/tests/unit/test_uc13_lich_trinh.py` (23 ca, theo TC-BR01…06, 49, 52, 63, 64, 67), `backend/tests/api/test_uc13_ghep_don.py` (16 ca). Sửa `test_uc11_ac10` vì chi tiết chuyến giờ có thêm thẻ Hàng. Toàn bộ **354 passed** (30/10). `ruff`, `npm run lint`, `npm run build` sạch.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/unit/test_uc13_lich_trinh.py tests/api/test_uc13_ghep_don.py`
- Khi viết test phát hiện: lô [Đ2, Đ6] trên C01 vi phạm **hai** quy tắc (BR-01 tải, và BR-06 ở Đ2 vì thêm 2 điểm dừng) – hệ thống báo đủ cả hai, đúng quyết định "báo mọi vi phạm".
- Lệch đặc tả: kết quả ghép trả dạng chi tiết chuyến (`id` thay `chuyen_id`, không có `da_ghep` – danh sách đơn nằm ở `don`); thêm mã `VI_PHAM_GO`, `DON_KHONG_THUOC_CHUYEN` – đã sửa `api.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-13-AC1 | Logic | `tests/unit/test_uc13_lich_trinh.py::test_uc13_ac1_* (3 ca)` | Đạt | 30/10/2026 |
| UC-13-AC2 | Logic | `test_uc13_ac2_ket_thuc_du_kien` | Đạt | 30/10/2026 |
| UC-13-AC3 | Logic | `test_uc13_ac3_* (7 ca)` | Đạt | 30/10/2026 |
| UC-13-AC4 | Logic | `test_uc13_ac4_* (2 ca)` | Đạt | 30/10/2026 |
| UC-13-AC5 | Logic | `test_uc13_ac5_* (7 ca)` | Đạt | 30/10/2026 |
| UC-13-AC6 | Logic | `test_uc13_ac6_* (2 ca)` | Đạt | 30/10/2026 |
| UC-13-AC7 | API | `tests/api/test_uc13_ghep_don.py::test_uc13_ac7_ghep_c01` + unit `test_uc13_lai_du_kien_va_lap_day` | Đạt | 30/10/2026 |
| UC-13-AC8 | API | `test_uc13_ac8_* (3 ca)` | Đạt | 30/10/2026 |
| UC-13-AC9 | API | `test_uc13_ac9_* (3 ca)` | Đạt | 30/10/2026 |
| UC-13-AC10 | API | `test_uc13_ac10_* (2 ca)` | Đạt | 30/10/2026 |
| UC-13-AC11 | API | `test_uc13_ac11_* (2 ca)` | Đạt | 30/10/2026 |
| UC-13-AC12 | API | `test_uc13_ac12_* (5 ca)` | Đạt | 30/10/2026 |
| UC-13-AC13 | UI | `docs/test-evidence/UC-13/` (5 ảnh ca a–e + 1 ảnh phụ, `docs/test-evidence/du-lieu-thu-giao-dien.md` Phần 6) – Kiệt thử | Đạt (Kiệt thử) | 30/10/2026 |
