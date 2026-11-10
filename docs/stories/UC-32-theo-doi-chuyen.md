# UC-32: Theo dõi chuyến

- **Trạng thái:** Đang làm – AC1–AC10 đạt, AC11 giao diện đã làm, chờ thử (Tài giao "làm xong hết" 08/11/2026; quyết định dưới đây Claude đề xuất, Tài xem lại khi review PR)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán xem
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-32) · `docs/api.md` mục 2.4 (`GET /api/chuyen?ngay=`, `GET /api/chuyen/{id}`, `ket-thuc-su-co`, `POST /api/su-co/{id}/dong`) · `docs/nghiep-vu.md` BR-36, 68, 70, 73, mục 2.1 · ca test `docs/ca-test-br.md` (TC-BR68-01…04, TC-BR73-01…03)
- **Quy tắc nghiệp vụ liên quan:** BR-30 (lịch sử), BR-36, BR-57 (phân quyền), BR-68 (kết thúc do sự cố), BR-70 (km), BR-71 (ETA kế hoạch), BR-73 (trễ, chồng lịch)
- **Người làm:** Tài

## Mô tả ngắn
Điều phối xem bảng chuyến trong ngày (tiến độ, % đầy, cờ trễ / sự cố / đơn thất bại / chưa quyết toán / chồng lịch) và chi tiết chuyến (lịch trình so ETA kế hoạch với giờ quét, dòng thời gian, tiền, sự cố). Điều phối đóng sự cố tài xế báo và kết thúc chuyến do sự cố.

## Quyết định
1. **Bảng chuyến trong ngày:** `GET /api/chuyen?ngay=` trả thêm `theo_doi` cho mỗi chuyến: `xong` / `tong` điểm (2 điểm mỗi đơn; điểm có lượt quét là xong; không lấy được thì điểm giao cũng tính xong), `ty_le_lap_day`, `co` (danh sách cờ) và `chong` (mã chuyến bị chồng). Không có `ngay` thì không tính (danh sách thường giữ nhẹ).
2. **Cờ:** `TRE` – có điểm quét trễ hơn ETA kế hoạch quá `CFG-09` phút (BR-73, chỉ tính theo lượt quét); `SU_CO` – có sự cố `MO`; `THAT_BAI` – có đơn thất bại; `CHUA_QUYET_TOAN` – chuyến `HOAN_THANH`; `CHONG_LICH` – BR-73 bên dưới.
3. **Kết thúc dự kiến khi đang chạy (BR-73):** chuyến `DANG_CHAY` = kết thúc dự kiến + max(0, độ trễ của lượt quét gần nhất). Chuyến kế tiếp của cùng xe hoặc tài xế (không `HUY`) khởi hành **trước** mốc đó → cờ `CHONG_LICH` kèm mã chuyến (đúng mốc thì không chồng, TC-BR73-02). Hệ thống không tự đổi lịch.
4. **Chi tiết chuyến** (`GET /api/chuyen/{id}`) thêm: mỗi điểm lịch trình có `eta_ke_hoach`, `thuc_te` (giờ quét), `ket_qua`, `tre_phut`; `ket_thuc_dang_chay`, `co`, `chong`; `dong_thoi_gian` (lịch sử trạng thái chuyến và đơn, lượt quét, sự cố theo thời gian); `tien` (định mức, lương, tạm ứng còn hiệu lực, doanh thu dự kiến – Kế toán cũng xem); `su_co`. Đơn thất bại của chuyến đã kết thúc vẫn hiện (ghép có kết quả), để chi tiết chuyến cũ đủ đơn.
5. **Kết thúc do sự cố (BR-68):** `POST /api/chuyen/{id}/ket-thuc-su-co {ly_do, km_ket_thuc?}`, chỉ khi `DANG_CHAY` (không thì 409 `BR-68`); lý do bắt buộc 1–300 ký tự (400). Đơn `DA_GHEP`, `DA_LAY` → `THAT_BAI` lý do "Sự cố xe: …", ghép `ket_qua = THAT_BAI`, hết hiệu lực (BR-36); đơn `DA_GIAO` giữ. Chuyến → `HOAN_THANH`, `ket_thuc_bat_thuong`, `ly_do_ket_thuc`, `ket_thuc_thuc_te` = bây giờ, **kết thúc dự kiến = bây giờ** (giải phóng xe, tài xế). Có km: phải > km bắt đầu (BR-70) → lưu `km_ket_thuc`, cập nhật `km_dong_ho` xe; không có thì để trống. Khóa chuyến → xe → đơn.
6. **Đóng sự cố:** `POST /api/su-co/{id}/dong {cach_xu_ly}` (1–500 ký tự), `MO → DONG`; đã đóng → 409. Sự cố do UC-33 (Kiệt) tạo; router đặt trong module chuyến (`router_su_co`), không tạo module `su_co` để không đụng việc của Kiệt.
7. **Phân quyền:** xem: Điều phối, Quản lý, Kế toán; kết thúc do sự cố, đóng sự cố: Điều phối, Quản lý. Tài xế 403.
8. **Giao diện:** Danh sách chuyến (lọc theo ngày) có cột Tiến độ, % đầy, Cờ. Chi tiết chuyến: lịch trình thêm cột Giờ quét, Trễ; khối Dòng thời gian, Tiền, Sự cố (nút Đóng sự cố + ô cách xử lý); chuyến đang chạy có nút **Kết thúc do sự cố** (ô lý do, km cuối).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-32-AC1 | Bảng ngày: C01 đang chạy Đ1, Đ2, Đ4, đã quét lấy Đ4, Đ1 → `theo_doi` `xong` 2, `tong` 6, `ty_le_lap_day` đúng; Đ2 không lấy được → `xong` 4 (điểm giao Đ2 tính xong); không có `ngay` thì không có `theo_doi` | API | BR-63 |
| UC-32-AC2 | Cờ trễ: quét lấy Đ2 lúc 08:10 (ETA kế hoạch 07:40) → `tre_phut` 30, cờ `TRE`; quét Đ4 06:30 (ETA 06:20) → trễ 10, không cờ; đúng 15 phút không cờ, 16 phút có (biên CFG-09) | API | BR-73 |
| UC-32-AC3 | Chồng lịch: sau lượt quét trễ 30′, kết thúc khi đang chạy 14:00; C00 cùng tài xế khởi hành 13:45 → `CHONG_LICH`, `chong` có C00 (TC-BR73-01); C00 lúc 14:00 → không (TC-BR73-02); trễ 10′ (13:40) không chồng (TC-BR73-03) | API | BR-73 |
| UC-32-AC4 | Cờ khác: sự cố `MO` → `SU_CO`, đóng rồi thì hết; có đơn `THAT_BAI` → `THAT_BAI`; chuyến `HOAN_THANH` → `CHUA_QUYET_TOAN` | API | BR-36 |
| UC-32-AC5 | Chi tiết: lịch trình có `eta_ke_hoach`, `thuc_te`, `ket_qua`, `tre_phut` từng điểm; `dong_thoi_gian` có lịch sử chuyến, lượt quét, sự cố theo thời gian; `tien` có định mức đã chốt 1.000.000, lương 600.000, tạm ứng hiệu lực, doanh thu; chuyến đã kết thúc vẫn hiện đơn thất bại | API | BR-71, 73 |
| UC-32-AC6 | Kết thúc do sự cố (TC-BR68-01): C01 đang chạy, Đ1, Đ2 `DA_LAY`, Đ4 `DA_GIAO`, km bắt đầu 120.000, lý do "hỏng hộp số", km 120.090 → `HOAN_THANH`, `ket_thuc_bat_thuong`; Đ1, Đ2 `THAT_BAI` lý do có "Sự cố xe", ghép hết hiệu lực; Đ4 giữ `DA_GIAO`; xe `km_dong_ho` 120.090; kết thúc dự kiến = giờ kết thúc thực tế | API | BR-68, 70, 36 |
| UC-32-AC7 | Không km (TC-BR68-04) → `km_ket_thuc` rỗng, xe giữ km; km ≤ km bắt đầu → 422 `BR-70`; thiếu / rỗng lý do → 400 (TC-BR68-02); chuyến `DA_CHOT` → 409 `BR-68` (TC-BR68-03); đơn `DA_GHEP` (chưa lấy) cũng thành `THAT_BAI` | API | BR-68, 70 |
| UC-32-AC8 | Sau kết thúc do sự cố: lập chuyến mới cùng xe, tài xế ngay sau giờ kết thúc thực tế được (khoảng chiếm đã giải phóng); đơn thất bại không tính BR-37 (không có lượt quét giao thất bại) | API | BR-68, 37 |
| UC-32-AC9 | Đóng sự cố: `MO` + cách xử lý → `DONG`, lưu cách xử lý; đóng lần 2 → 409; thiếu cách xử lý → 400; không tồn tại → 404 | API | — |
| UC-32-AC10 | Phân quyền: xem bảng / chi tiết: Điều phối, Quản lý, Kế toán; kết thúc do sự cố, đóng sự cố: Điều phối, Quản lý; Kế toán → 403 khi ghi; Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-32-AC11 | Giao diện: danh sách chuyến theo ngày có tiến độ, % đầy, cờ; chi tiết có giờ quét / trễ, dòng thời gian, tiền, sự cố + đóng; nút Kết thúc do sự cố khi đang chạy | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/chuyen/theo_doi.py` (mới: tiến độ, cờ, trễ, chồng lịch, dòng thời gian, tiền, kết thúc do sự cố, đóng sự cố), `chuyen/router.py` (GET danh sách thêm `theo_doi` khi có `ngay`, GET chi tiết dùng `theo_doi.chi_tiet`, `ket-thuc-su-co`, `router_su_co`), `chuyen/schemas.py`, `chuyen/service.py` (`_dong_don_cua_chuyen` lấy cả ghép đã có kết quả), `app/main.py` (đăng ký `router_su_co`), `frontend/src/api/chuyen.ts`, `frontend/src/pages/dieu-phoi/{ChuyenDanhSach,ChuyenChiTiet,TheoDoiChuyen}.tsx`, `docs/api.md`.
- Không cần migration (`su_co`, `ket_thuc_bat_thuong`, `ly_do_ket_thuc`, `eta_*_ke_hoach` đã có).
- Test đã viết: `backend/tests/api/test_uc32_theo_doi_chuyen.py` (24 ca). Test UC-13 so chi tiết GET với kết quả ghép: nay so phần chung (GET có thêm phần theo dõi). Toàn bộ 654 passed, ruff sạch; frontend tsc, oxlint, prettier, build sạch.
- Thử làm hỏng 5 chỗ (mốc chồng lịch `<` thành `<=`, không cho ghép hết hiệu lực, không đặt lại kết thúc dự kiến, không bỏ điểm giao khi không lấy được, ngưỡng trễ `>` thành `>=`) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc32_theo_doi_chuyen.py`
- Lệch đặc tả: "5 thẻ" làm thành các khối trên cùng trang chi tiết; cờ trễ chỉ theo lượt quét (đúng BR-73), chưa cờ "quá ETA mà chưa quét". Đã ghi `api.md`.
- Dữ liệu thử giao diện: `docs/test-evidence/UC-32/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-32-AC1 | API | `test_uc32_ac1_tien_do` | Đạt | 08/11/2026 |
| UC-32-AC2 | API | `test_uc32_ac2_co_tre` (4 ca) | Đạt | 08/11/2026 |
| UC-32-AC3 | API | `test_uc32_ac3_* (4 ca)` | Đạt | 08/11/2026 |
| UC-32-AC4 | API | `test_uc32_ac4_cac_co_khac` | Đạt | 08/11/2026 |
| UC-32-AC5 | API | `test_uc32_ac5_chi_tiet` | Đạt | 08/11/2026 |
| UC-32-AC6 | API | `test_uc32_ac6_ket_thuc_su_co` | Đạt | 08/11/2026 |
| UC-32-AC7 | API | `test_uc32_ac7_* (5 ca)` | Đạt | 08/11/2026 |
| UC-32-AC8 | API | `test_uc32_ac8_giai_phong_lich` | Đạt | 08/11/2026 |
| UC-32-AC9 | API | `test_uc32_ac9_dong_su_co` | Đạt | 08/11/2026 |
| UC-32-AC10 | API | `test_uc32_ac10_* (5 ca)` | Đạt | 08/11/2026 |
| UC-32-AC11 | UI | Kiệt thử 10/11, ca a, b, d đạt (b, d thử lại trên PR #34); c, e chưa thử (`docs/test-evidence/UC-32/`) | Đạt | 10/11/2026 |
