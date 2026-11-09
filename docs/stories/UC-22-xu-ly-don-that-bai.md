# UC-22: Xử lý đơn thất bại

- **Trạng thái:** Đang làm – AC1–AC11 đạt, AC12 giao diện đã làm, chờ thử (Tài giao "làm xong hết" 08/11/2026; quyết định dưới đây Claude đề xuất, Tài xem lại khi review PR)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-22) · `docs/api.md` mục 2.3 (`ghep-lai`, `tra-hang`, `huy`) · `docs/nghiep-vu.md` BR-30, 34, 36, 37, 69, mục 5.2, mục 11 bước 6 · ca test `docs/ca-test-br.md` (TC-BR34-02, 04, TC-BR36-02, 03, TC-BR37-01…03, TC-BR69-01, 02)
- **Quy tắc nghiệp vụ liên quan:** BR-30 (lịch sử), BR-34 (hủy), BR-36 (ba cách xử lý), BR-37 (CFG-04 lần giao thất bại phía khách), BR-57 (phân quyền), BR-69 (nơi giữ hàng khi ghép lại)
- **Người làm:** Tài

## Mô tả ngắn
Sau khi chuyến kết thúc, đơn `THAT_BAI` hiện trong danh sách cần xử lý kèm lý do, đã lấy hàng hay chưa, số lần giao thất bại phía khách. Điều phối chọn ghép lại (→ `CHO_GHEP`; đã lấy thì bắt buộc nơi giữ hàng, được đổi hạn giao, cước giữ nguyên), trả hàng (chỉ khi đã lấy → `TRA_HANG`) hoặc hủy (chỉ khi chưa lấy → `HUY`).

## Quyết định
1. **"Đã lấy hàng"** = đơn có lượt quét `LAY` ở bất kỳ lần ghép nào (lọc `loai = 'LAY'`, theo lưu ý của Kiệt). Không dựa vào trạng thái.
2. **Chỉ xử lý khi chuyến đã kết thúc:** đơn `THAT_BAI` còn ghép hiệu lực (chuyến chưa kết thúc, BR-36) → 409 `BR-36` "chờ chuyến kết thúc". Đơn không `THAT_BAI` → 409 `BR-36`.
3. **Ghép lại** `POST /api/don/{id}/ghep-lai {han_giao?, nut_giu_id?, dia_chi_giu?, lat_giu?, lng_giu?}`:
   - Đếm lượt `GIAO_THAT_BAI` có lý do phía `KHACH` (mọi lần ghép) ≥ `CFG-04` → 422 `BR-37`, chỉ còn trả hàng.
   - Đã lấy: `nut_giu_id` + `dia_chi_giu` bắt buộc → thiếu 422 `BR-69`; nơi giữ thay điểm lấy khi ghép (BR-69); khung giờ lấy cũ bỏ (hàng đã ở kho, không còn hẹn lấy với khách).
   - Chưa lấy: không nhận nơi giữ hàng (gửi → 422 `BR-69`), điểm lấy giữ như cũ.
   - `han_giao` mới phải sau lúc xử lý (và sau giờ bắt đầu lấy nếu còn khung) → 422 `BR-31`.
   - Cước giữ nguyên, không ghi nhật ký tiền.
4. **Trả hàng** `POST /api/don/{id}/tra-hang {ly_do?}`: chỉ khi đã lấy → `TRA_HANG`; chưa lấy → 422 `BR-36` (TC-BR36-03). Không sinh doanh thu (không đụng phải thu).
5. **Hủy** dùng endpoint UC-10 `POST /api/don/{id}/huy`: `THAT_BAI` chưa lấy → `HUY` (TC-BR34-02); đã lấy → 422 `BR-34` (TC-BR34-04).
6. **Danh sách cần xử lý** `GET /api/don/can-xu-ly`: đơn `THAT_BAI` kèm `da_lay`, `so_lan_giao_tb_khach`, `nguong` (CFG-04), lý do lần thất bại gần nhất, `cho_chuyen_xong`. Ảnh thất bại chưa hiện (chưa có API xem tệp), ghi hướng phát triển.
7. **Lịch sử (BR-30):** mỗi thao tác ghi `THAT_BAI → …` kèm lý do (ghép lại: "Ghép lại" + nơi giữ nếu có).
8. **Khóa:** khóa dòng đơn `FOR UPDATE` (đơn không còn ghép hiệu lực nên không cần khóa chuyến).
9. **Giao diện:** trang Đơn hàng có thẻ **Đơn thất bại cần xử lý**: mỗi đơn hiện lý do, đã lấy / chưa, số lần thất bại phía khách; nút Ghép lại (khóa khi đạt ngưỡng; đã lấy thì hỏi nơi giữ hàng + hạn mới), Trả hàng (chỉ khi đã lấy), Hủy (chỉ khi chưa lấy).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-22-AC1 | Đ1 `THAT_BAI` đã lấy, ghép lại với nơi giữ kho Cần Thơ, hạn mới → 200, `CHO_GHEP`, `nut_giu_id` = Cần Thơ, cước giữ 2.997.000, không có nhật ký tiền (TC-BR69-01) | API | BR-36, 69 |
| UC-22-AC2 | Đ1 đã lấy ghép lại không gửi nơi giữ hàng → 422 `BR-69`, vẫn `THAT_BAI` (TC-BR69-02); đơn chưa lấy gửi nơi giữ → 422 `BR-69` | API | BR-69 |
| UC-22-AC3 | BR-37: 3 lần giao thất bại phía khách → ghép lại 422 `BR-37`, trả hàng vẫn được (TC-BR37-01); 2 lần phía khách + 1 lần sự cố xe → ghép lại được (TC-BR37-02); 3 lần không lấy được phía khách → ghép lại được (TC-BR37-03) | API | BR-37 |
| UC-22-AC4 | Đơn ghép lại sau khi đã lấy: ghép vào chuyến tuyến đi qua nơi giữ hàng, lịch trình lấy tại nơi giữ (BR-69 thay điểm lấy trong BR-03, 63) | API | BR-69, 03, 63 |
| UC-22-AC5 | Hạn giao mới = lúc xử lý → 422 `BR-31`; sau 1 phút đạt (biên) | API | BR-31, 69 |
| UC-22-AC6 | Trả hàng: Đ1 đã lấy → `TRA_HANG` (TC-BR36-02); Đ4 chưa lấy → 422 `BR-36` (TC-BR36-03) | API | BR-36 |
| UC-22-AC7 | Hủy: Đ4 `THAT_BAI` chưa lấy → `HUY` (TC-BR34-02); Đ1 đã lấy → 422 `BR-34` (TC-BR34-04) | API | BR-34, 36 |
| UC-22-AC8 | Trạng thái và thời điểm: đơn `THAT_BAI` còn ghép hiệu lực (chuyến chưa kết thúc) → 409 `BR-36` cho cả ghép lại, trả hàng; đơn `CHO_GHEP` → 409 `BR-36`; không tồn tại → 404 | API | BR-36 |
| UC-22-AC9 | Lịch sử: mỗi thao tác 1 dòng `THAT_BAI → …` có người làm, lý do | API | BR-30 |
| UC-22-AC10 | Danh sách cần xử lý: chỉ đơn `THAT_BAI`, đúng `da_lay`, `so_lan_giao_tb_khach`, lý do gần nhất, `cho_chuyen_xong` | API | BR-36, 37 |
| UC-22-AC11 | Phân quyền: Điều phối, Quản lý được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-22-AC12 | Giao diện: thẻ đơn thất bại, nút theo điều kiện (Ghép lại khóa khi đạt ngưỡng, Trả hàng chỉ khi đã lấy, Hủy chỉ khi chưa lấy), form nơi giữ hàng + hạn mới | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/don/that_bai.py` (mới: `ghep_lai`, `tra_hang`, `can_xu_ly`, `da_lay`, `so_lan_giao_tb_khach`, `khoa_that_bai`), `don/sua_huy.py` (`huy` nhận `THAT_BAI`), `don/{router,schemas}.py` (`GhepLaiVao`, `TraHangVao`, `DonCanXuLyRa`), `frontend/src/api/don.ts`, `frontend/src/pages/dieu-phoi/DonDanhSach.tsx` (thẻ Đơn thất bại cần xử lý, hộp Ghép lại), `docs/api.md`.
- Không cần migration (`nut_giu_id`, `dia_chi_giu`, `lat_giu`, `lng_giu` đã có từ ERD 0.5).
- Test đã viết: `backend/tests/api/test_uc22_xu_ly_don_that_bai.py` (20 ca). Test UC-10 AC9 bỏ ca `THAT_BAI` → 409 (nay UC-22 cho hủy khi chưa lấy).
- Thử làm hỏng 4 chỗ (bỏ lọc phía khách ở BR-37, bỏ lọc `loai = 'LAY'`, bỏ chặn chuyến chưa kết thúc, không bỏ khung lấy cũ) → test đỏ đúng chỗ (ca cuối thêm test sau khi phát hiện chưa có).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc22_xu_ly_don_that_bai.py`
- Lệch đặc tả: thêm `GET /api/don/can-xu-ly`; `tra-hang` nhận `ly_do` tùy chọn; ảnh thất bại chưa hiện (hướng phát triển). Đã ghi `api.md`.
- Dữ liệu thử giao diện: `docs/test-evidence/UC-22/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-22-AC1 | API | `test_uc22_ac1_* (2 ca)` | Đạt | 08/11/2026 |
| UC-22-AC2 | API | `test_uc22_ac2_* (2 ca)` | Đạt | 08/11/2026 |
| UC-22-AC3 | API | `test_uc22_ac3_* (3 ca)` | Đạt | 08/11/2026 |
| UC-22-AC4 | API | `test_uc22_ac4_lich_trinh_lay_tai_noi_giu` | Đạt | 08/11/2026 |
| UC-22-AC5 | API | `test_uc22_ac5_han_giao_moi` | Đạt | 08/11/2026 |
| UC-22-AC6 | API | `test_uc22_ac6_tra_hang` | Đạt | 08/11/2026 |
| UC-22-AC7 | API | `test_uc22_ac7_huy` | Đạt | 08/11/2026 |
| UC-22-AC8 | API | `test_uc22_ac8_* (2 ca)` | Đạt | 08/11/2026 |
| UC-22-AC9 | API | `test_uc22_ac9_lich_su` | Đạt | 08/11/2026 |
| UC-22-AC10 | API | `test_uc22_ac10_danh_sach_can_xu_ly` | Đạt | 08/11/2026 |
| UC-22-AC11 | API | `test_uc22_ac11_* (5 ca)` | Đạt | 08/11/2026 |
| UC-22-AC12 | UI | Chờ thử (`docs/test-evidence/UC-22/du-lieu.md`) | CHƯA KIỂM | |
