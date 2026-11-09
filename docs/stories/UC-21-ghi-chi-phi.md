# UC-21: Ghi chi phí

- **Trạng thái:** Hoàn thành 14/14 AC (09/11/2026; duyệt 07/11/2026, Kiệt: "làm như bình thường, làm tiếp" – 9 quyết định như đề xuất; khi code chỉnh AC5, xem quyết định 10)
- **Tác nhân:** Tài xế (điện thoại)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-21) · `docs/api.md` mục 2.5 (`/api/toi/chuyen/{id}/chi-phi`, `/api/toi/chi-phi/{id}`) · `docs/security-rules.md` (bảng dữ liệu tiền, upload) · `docs/kien-truc.md` mục 6 (khóa) · ca test `docs/ca-test-br.md` (TC-BR54-01…03) · kịch bản `nghiep-vu.md` mục 11 (dầu 26 lít 520.000, cầu đường 230.000, bốc xếp 300.000)
- **Quy tắc nghiệp vụ liên quan:** BR-54 (số tiền > 0, ghi chú, ≥ 1 ảnh chứng từ; dầu thêm số lít; ghi được tới khi quyết toán), BR-58 (chỉ chuyến của mình), BR-62 (nhật ký tiền), BR-29 (đã quyết toán thì chỉ đọc), NFR-PER-03 (ảnh ≤ 500 KB, nén trên trình duyệt)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-21-chi-phi` tách từ `dev`. **Backend làm ngay; giao diện làm sau khi PR #16 (UC-20) gộp** (cùng trang tài xế), gộp `dev` vào nhánh rồi mới sửa trang.

## Mô tả ngắn
Trong chuyến (đang chạy hoặc đã về, chưa quyết toán), tài xế ghi từng khoản đã chi bằng tiền tạm ứng: chọn loại (dầu, cầu đường, bốc xếp, phát sinh), số tiền, số lít nếu là dầu, ghi chú, chụp ảnh hóa đơn. Khoản lưu ở trạng thái **chờ duyệt**; tài xế sửa hoặc xóa được khoản của mình khi còn chờ duyệt. Kế toán duyệt / từ chối ở UC-24.

## Đặc tả rút gọn
- **`POST /api/toi/chuyen/{id}/chi-phi`** (TX, multipart): `loai` ∈ `DAU`, `CAU_DUONG`, `BOC_XEP`, `PHAT_SINH`; `so_tien` số nguyên 1…10¹²; `so_lit` (> 0, tối đa 2 chữ số thập phân) **bắt buộc khi `DAU`, không được gửi với loại khác**; `ghi_chu` 1–500 ký tự (NFC, bỏ khoảng trắng hai đầu); `anh` 1–5 ảnh JPG/PNG ≤ 500 KB (`app/luu_tru.py` như UC-19). Trường lạ → 400.
  - Thứ tự kiểm: chuyến không phải của mình / không có → **404** (như UC-17, không lộ chuyến); khóa dòng chuyến `FOR SHARE`; chuyến không `DANG_CHAY` / `HOAN_THANH` → **409 `BR-54`** (đã quyết toán → **409 `BR-29`**); thiếu ghi chú hoặc ảnh → **422 `BR-54`**; sai kiểu, số tiền ≤ 0, dầu thiếu số lít → **400**.
  - Lưu `CHI_PHI` `CHO_DUYET`, `nguoi_tao` = tài xế; ảnh vào `TEP` (`chi_phi_id`, loại `ANH`); `NHAT_KY_TIEN` `TAO`. CSDL lỗi → xóa ảnh vừa ghi. Trả 201 khoản vừa tạo.
- **`GET /api/toi/chuyen/{id}/chi-phi`** (TX) – **endpoint mới**: danh sách khoản của chuyến mình (loại, số khai, số lít, ghi chú, trạng thái, số ảnh) + tổng đã khai + **tạm ứng còn hiệu lực đã nhận** (UC-23 để tài xế xem ở đây).
- **`PATCH /api/toi/chi-phi/{id}`** (TX, JSON) `{loai?, so_tien?, so_lit?, ghi_chu?}`: chỉ khoản **mình tạo**, còn `CHO_DUYET`, chuyến chưa quyết toán; kiểm lại BR-54 trên giá trị sau khi sửa; nhật ký `SUA` (cũ, mới).
- **`DELETE /api/toi/chi-phi/{id}`** (TX): cùng điều kiện; xóa khoản + tệp; nhật ký `XOA` (giá trị cũ). 204.
- **Giao diện** (trang chuyến của tài xế, 360 px): khối **Chi phí** khi chuyến đang chạy / đã về: dòng "Tạm ứng đã nhận … · Đã khai …"; danh sách khoản (trạng thái Chờ duyệt / Đã duyệt / Từ chối; Sửa, Xóa khi chờ duyệt); form **Ghi chi phí** (loại, số tiền, số lít hiện khi chọn Dầu, ghi chú, chụp ảnh – nén như UC-19).

## Quyết định (Kiệt duyệt 07/11/2026)
1. **Module mới `backend/app/modules/tien/chi_phi/`**, cạnh `tien/tam_ung/` (UC-23); đường dẫn `/api/toi/…` như `api.md`. UC-24 sẽ thêm duyệt / từ chối vào cùng module. Không đổi CSDL, không thêm gói.
2. **Thêm `GET /api/toi/chuyen/{id}/chi-phi`** vào `api.md` (tài xế cần xem lại khoản đã ghi). Trả kèm **tạm ứng đã nhận** – phần UC-23 để lại cho UC-21 (quyết định 9 của UC-23).
3. **Trạng thái chuyến ghi được:** `DANG_CHAY`, `HOAN_THANH` (tiền điều kiện UC-21; tài xế về rồi vẫn nhập hóa đơn còn sót). `DA_CHOT` chưa chạy thì chưa ghi.
4. **Mã lỗi:** sai kiểu / số tiền ≤ 0 / dầu thiếu lít / loại khác gửi lít → **400** (TC-BR54-02, 03 cho 400/422); thiếu ghi chú hoặc ảnh → **422 `BR-54`** kèm danh sách còn thiếu (như BR-41 ở UC-20).
5. **Chuyến hoặc khoản của người khác → 404** (giống UC-17), không phải 403.
6. **Sửa không đổi ảnh**: muốn đổi ảnh thì xóa khoản rồi ghi lại (đơn giản, ít lỗi). Sửa không bắt buộc lý do (khoản chưa duyệt, chưa ai dùng số này); nhật ký ghi lý do "Tài xế sửa khoản chờ duyệt".
7. **Xóa là xóa hẳn** (khoản chưa duyệt), có nhật ký `XOA` giữ giá trị cũ; thêm `XOA` vào danh sách hành động của `NHAT_KY_TIEN` (chỉ là giá trị chuỗi, không cần migration).
8. **Giá trị trong nhật ký** dạng chữ: `"520000 DAU 26.00"` (loại khác không có số lít).
9. **Ngoài phạm vi:** Kế toán duyệt / từ chối / điều chỉnh (UC-24); xem ảnh chứng từ qua link có hạn (`/api/tep/{id}/link`, làm cùng UC-24 khi Kế toán cần xem); cảnh báo chi vượt định mức (UC-24 bảng quyết toán).
10. **Chuyến `LAP`, `HUY` → 404** (không phải 409): trang tài xế UC-17 coi hai trạng thái này là "không tìm thấy" vì tài xế không được thấy; UC-21 theo đúng như vậy. `DA_CHOT` vẫn 409 `BR-54`. (Chỉnh lúc code 07/11, báo Kiệt.)

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-21-AC1 | C01 `DANG_CHAY`, An ghi dầu 520.000, 26 lít, ghi chú, 1 ảnh → 201 `CHO_DUYET`, `nguoi_tao` = An, 1 tệp `ANH` gắn `chi_phi_id`, 1 dòng `NHAT_KY_TIEN` `TAO`; ghi thêm cầu đường 230.000 và bốc xếp 300.000 (không số lít) được | API | BR-54, 62 (TC-BR54-01) |
| UC-21-AC2 | Thiếu ghi chú, ghi chú chỉ khoảng trắng, không ảnh → 422 `BR-54`, không lưu, không còn tệp trên đĩa | API | BR-54 (TC-BR54-02) |
| UC-21-AC3 | Ca biên số: số tiền 0, âm, lẻ, chữ → 400; 1 đ được; dầu không số lít, số lít 0, âm, 3 chữ số thập phân → 400; cầu đường gửi số lít → 400; ghi chú 500 ký tự được, 501 → 400 | API | BR-54 (TC-BR54-02, 03) |
| UC-21-AC4 | Ảnh: 5 ảnh được, 6 → 400; ảnh sai loại (đuôi .jpg nhưng là PDF) → 400; ảnh > 500 KB → 413; không lưu gì | API | security-rules, NFR-PER-03 |
| UC-21-AC5 | Trạng thái chuyến: `HOAN_THANH` ghi được; `DA_CHOT` → 409 `BR-54`; `DA_QUYET_TOAN` → 409 `BR-29`; `LAP`, `HUY` → 404 như UC-17 (quyết định 10) | API | BR-54, 29, 58 |
| UC-21-AC6 | Chuyến của tài xế khác, chuyến không có → 404; trường lạ → 400; loại ngoài danh sách → 400 | API | BR-58, IDOR |
| UC-21-AC7 | Phân quyền: Điều phối, Kế toán, Quản lý gọi 4 API → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-21-AC8 | Xem: `GET` trả các khoản của chuyến (cũ trước), tổng đã khai, tạm ứng `HIEU_LUC` đã nhận (khoản thu hồi không tính), số ảnh mỗi khoản; chuyến người khác → 404 | API | BR-58 |
| UC-21-AC9 | Sửa: An sửa khoản dầu của mình 520.000 → 500.000 → 200, nhật ký `SUA` (cũ, mới); đổi sang cầu đường mà còn số lít → 400; sửa đầu → dầu mà bỏ số lít → 400; ghi chú rỗng → 422 `BR-54` | API | BR-54, 62 |
| UC-21-AC10 | Xóa: khoản `CHO_DUYET` của mình → 204, khoản và tệp (CSDL, đĩa) mất, nhật ký `XOA` giữ giá trị cũ | API | BR-62 |
| UC-21-AC11 | Sửa / xóa khi không được: khoản `DA_DUYET` hoặc `TU_CHOI` → 409 `BR-54`; chuyến `DA_QUYET_TOAN` → 409 `BR-29`; khoản của tài xế khác hoặc không có → 404; mọi trường hợp khoản giữ nguyên | API | BR-29, 58 |
| UC-21-AC12 | CSDL lỗi giữa chừng (ép lỗi lúc ghi nhật ký) → không có khoản, không có tệp mồ côi trên đĩa | API | NFR-REL-01 |
| UC-21-AC13 | Giao diện tài xế (360 px): khối Chi phí ở chuyến đang chạy / đã về; số lít chỉ hiện khi chọn Dầu; ghi thành công hiện ngay trong danh sách "Chờ duyệt"; thiếu ghi chú / ảnh báo kèm `BR-54`; Sửa, Xóa (hỏi xác nhận) ở khoản chờ duyệt; dòng tạm ứng đã nhận / đã khai | UI | NFR-USA-02 |
| UC-21-AC14 | Thử trên iPhone qua Cloudflare Tunnel: chụp ảnh hóa đơn bằng camera, ảnh được nén ≤ 500 KB, khoản lưu có 1 tệp | UI | NFR-PER-03, NFR-COM-01 |

## Ghi chú triển khai
- File đã đổi (07/11, backend):
  - `backend/app/modules/tien/chi_phi/` (mới): `service.py` (ghi, sửa, xóa, xem; khóa chuyến `FOR SHARE` rồi khoản `FOR UPDATE`; `_kiem_br54` dùng cho ghi và sửa; nhật ký `TAO`/`SUA`/`XOA`; CSDL lỗi → xóa ảnh vừa ghi), `router.py` (4 endpoint dưới `/api/toi`, chỉ `TAI_XE`, chặn trường lạ của form như UC-19, tối đa 5 ảnh), `schemas.py`. `app/main.py` thêm router theo chữ cái.
  - Tài liệu: `api.md` 2.5 (thêm `GET /api/toi/chuyen/{id}/chi-phi`, ghi rõ body, mã lỗi).
- Không đổi CSDL, không thêm gói. Giá trị `XOA` mới trong cột chuỗi `nhat_ky_tien.hanh_dong` (quyết định 7).
- Test đã viết: `tests/api/test_uc21_chi_phi.py` (51 ca, gồm 1 ca khóa: ghi chi phí đợi khi dòng chuyến đang bị khóa, rồi đọc lại trạng thái mới). Đã thử làm hỏng 4 quy tắc (dầu không cần số lít, không bắt buộc ảnh, sửa được khoản đã duyệt, bỏ khóa chuyến) → mỗi lần có test đỏ, rồi trả lại code.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc21_chi_phi.py`
- Giao diện (09/11, sau khi gộp `dev` có #16, #19–#24; `main.py` xung đột 1 dòng router với UC-23, giữ cả hai; 759 passed): `api/chiPhi.ts`, `pages/tai-xe/ChiPhi.tsx` (khối Chi phí: tạm ứng đã nhận / đã khai, danh sách khoản, form ghi có ảnh nén, số lít chỉ hiện khi chọn Dầu, Sửa tại chỗ không đổi ảnh, Xóa hỏi xác nhận; chuyến đã quyết toán chỉ xem), `ChuyenCuaToiChiTiet.tsx` thêm 2 dòng gắn khối, `index.css` (`.ds-chi`). Thiếu ghi chú / ảnh để máy chủ báo 422 kèm `BR-54`.
- Thử giao diện: `docs/test-evidence/UC-21/du-lieu.md`.
- Kèm theo (Tài nhờ 09/11, góp ý ở #21; module `toi` và trang tài xế là của Kiệt): `GET /api/toi/chuyen/{id}` trả thêm `da_lay` cho từng điểm (đã quét lấy **trong chính chuyến này** – không dùng `da_lay` theo đơn của `don/that_bai.py` vì đơn ghép lại BR-69 có thể đã lấy ở chuyến trước); điểm Lấy của đơn giao thất bại hiện "Đã lấy". Test `test_uc20_diem_lay_da_lay_khi_giao_that_bai` (thử làm hỏng: luôn `False` → đỏ). CSS `.ds-chi` đặt sau `.hanh-dong` (không ở cuối tệp) để không xung đột với #25. Toàn bộ 760 passed. Theo quy ước #26: PR này không sửa `TIEN-DO.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-21-AC1 | API | `test_uc21_ac1_*` (2 ca, 4 loại) | Đạt | 07/11/2026 |
| UC-21-AC2 | API | `test_uc21_ac2_thieu_ghi_chu_anh` (4 ca, không còn tệp) | Đạt | 07/11/2026 |
| UC-21-AC3 | API | `test_uc21_ac3_*` (12 ca, biên 1 đ, 0,01 lít, 500 ký tự) | Đạt | 07/11/2026 |
| UC-21-AC4 | API | `test_uc21_ac4_*` (biên 5 / 6 ảnh, 500 KB) | Đạt | 07/11/2026 |
| UC-21-AC5 | API | `test_uc21_ac5_*` (5 ca) | Đạt | 07/11/2026 |
| UC-21-AC6 | API | `test_uc21_ac6_*` (5 ca) | Đạt | 07/11/2026 |
| UC-21-AC7 | API | `test_uc21_ac7_*` (4 ca) | Đạt | 07/11/2026 |
| UC-21-AC8 | API | `test_uc21_ac8_*` (2 ca) | Đạt | 07/11/2026 |
| UC-21-AC9 | API | `test_uc21_ac9_*` (8 ca) | Đạt | 07/11/2026 |
| UC-21-AC10 | API | `test_uc21_ac10_xoa` | Đạt | 07/11/2026 |
| UC-21-AC11 | API | `test_uc21_ac11_*` (4 ca) | Đạt | 07/11/2026 |
| UC-21-AC12 | API | `test_uc21_ac12_loi_giua_chung` | Đạt | 07/11/2026 |
| UC-21-AC13 | UI | Kiệt thử 9 ca a–h, g2 trên máy tính 360 px: `docs/test-evidence/UC-21/a…h-*.png`; CSDL khớp | Đạt | 09/11/2026 |
| UC-21-AC14 | UI | Kiệt thử iPhone Safari qua Cloudflare Tunnel (ca i): chụp hóa đơn bằng camera, ảnh lưu 200 KB (đã nén ≤ 500 KB), khoản có 1 tệp; khối không tràn khung: `i-iphone.png` | Đạt | 09/11/2026 |
