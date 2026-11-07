# UC-23: Cấp / sửa / thu hồi tạm ứng

- **Trạng thái:** Đang làm (duyệt 07/11/2026, Kiệt: đồng ý 9 quyết định)
- **Tác nhân:** Kế toán (Quản lý chỉ xem)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-23) · `docs/api.md` mục 2.6 · `docs/security-rules.md` (bảng dữ liệu tiền) · `docs/kien-truc.md` mục 6 (khóa dòng chuyến) · ca test `docs/ca-test-br.md` (TC-BR53-01…06, TC-BR62-01, TC-BR24-01/02, TC-BR25-02) · kịch bản `nghiep-vu.md` mục 11 bước 4
- **Quy tắc nghiệp vụ liên quan:** BR-53 (chỉ cấp khi chuyến `DA_CHOT` tới trước `HOAN_THANH`; tổng `HIEU_LUC` ≤ định mức đã chốt; kiểm ở mọi lần tạo và sửa), BR-62 (nhật ký tiền chỉ thêm), BR-24 / BR-25 (mở chốt, hủy chuyến cần thu hồi trước – UC-15, 16 đã kiểm), BR-29 (đã quyết toán thì chỉ đọc)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-23-tam-ung` tách từ `dev` (không đụng trang tài xế nên không chờ PR #16)

## Mô tả ngắn
Chuyến đã chốt, Kế toán cấp tiền tạm ứng cho tài xế để trả chi phí dọc đường. Hệ thống gợi ý số còn được cấp = định mức đã chốt − tạm ứng còn hiệu lực, chặn khi vượt định mức. Kế toán sửa được số tiền (kèm lý do) và ghi thu hồi khi tài xế nộp lại (bắt buộc trước khi mở chốt hoặc hủy chuyến). Mọi lần ghi đều vào nhật ký tiền.

## Đặc tả rút gọn
- **Định mức đã chốt** của chuyến = `dm_dau_chot + dm_cau_duong_chot + dm_boc_xep_chot` (UC-15 lưu lúc chốt, BR-71). **Còn được cấp** = định mức − Σ tạm ứng `HIEU_LUC` (không âm). Khoản `DA_THU_HOI` không tính.
- **`POST /api/chuyen/{id}/tam-ung`** (KT) `{so_tien, hinh_thuc}`:
  - `so_tien` số nguyên đồng, ≥ 1; `hinh_thuc` ∈ `TIEN_MAT`, `CHUYEN_KHOAN`; trường lạ → 400.
  - Khóa dòng chuyến `FOR UPDATE` (kien-truc mục 6) → chuyến không `DA_CHOT`/`DANG_CHAY` → 409 `BR-53`; tổng mới vượt định mức → 422 `BR-53` (kèm còn được cấp), không lưu.
  - Lưu `TAM_UNG` `HIEU_LUC`, `tai_xe_id` = tài xế của chuyến, `nguoi_tao` = Kế toán; `NHAT_KY_TIEN` `TAO` (cũ rỗng, mới = số tiền + hình thức). Trả 201 khoản vừa tạo.
- **`PATCH /api/tam-ung/{id}`** (KT) `{so_tien, hinh_thuc?, ly_do}` (`ly_do` 1–300 ký tự):
  - Khoản phải `HIEU_LUC`, chuyến chưa quyết toán → còn lại 409.
  - Kiểm lại BR-53 với số mới (tổng các khoản khác + số mới) → vượt 422, khoản giữ số cũ.
  - `NHAT_KY_TIEN` `SUA` (cũ, mới, lý do).
- **`POST /api/tam-ung/{id}/thu-hoi`** (KT) `{ly_do?}`: khoản `HIEU_LUC` → `DA_THU_HOI`, chuyến chưa quyết toán; `NHAT_KY_TIEN` `THU_HOI`. Khoản đã thu hồi → 409.
- **`GET /api/chuyen/{id}/tam-ung`** (KT, QL) – **endpoint mới**: `{dinh_muc, tong_hieu_luc, con_duoc_cap, khoan: [...]}` cho màn hình cấp (gợi ý số tiền).
- **`GET /api/tam-ung`** (KT, QL): lọc `trang_thai`, `chuyen_id`, `tai_xe_id`; mỗi dòng có mã chuyến, tên tài xế.
- **Giao diện Kế toán:** menu **Tạm ứng** (sau "Chi phí cố định xe", theo chữ cái): danh sách chuyến `DA_CHOT` / `DANG_CHAY` / `HOAN_THANH` kèm đã cấp / định mức; chọn chuyến → ô số tiền điền sẵn số còn được cấp, chọn hình thức → **Cấp**; bảng các khoản có **Sửa** (số mới + lý do) và **Thu hồi** (hỏi xác nhận "Tài xế đã nộp lại …?"). Lỗi hiện kèm mã BR (NFR-USA-02).

## Quyết định (Kiệt duyệt 07/11/2026)
1. **Module mới `backend/app/modules/tien/tam_ung/`** (router, service, schemas) theo `kien-truc.md` (thư mục `tien/` cho chi phí, tạm ứng, quyết toán…). Không đổi CSDL, không thêm gói.
2. **Thêm `GET /api/chuyen/{id}/tam-ung`** (tóm tắt một chuyến) vào `api.md` 2.6, vì chi tiết chuyến hiện không trả định mức đã chốt mà màn hình cấp cần để gợi ý.
3. **Sửa và thu hồi được tới khi quyết toán:** chuyến `DA_CHOT`, `DANG_CHAY`, `HOAN_THANH` (đặc tả 3a "khi chuyến chưa quyết toán"). **Cấp mới** chỉ `DA_CHOT`, `DANG_CHAY` (BR-53). Chuyến `DA_QUYET_TOAN` → 409 (BR-29).
4. **Mã lỗi:** sai trạng thái chuyến hoặc khoản → **409** `BR-53`; vượt định mức → **422** `BR-53` (như TC-BR53-02 và `api.md`); dữ liệu sai → 400.
5. **Thu hồi không bắt buộc lý do**; bỏ trống thì nhật ký ghi "Tài xế đã nộp lại tạm ứng". Sửa thì **bắt buộc** lý do (đặc tả 3a).
6. **Sửa mà số tiền và hình thức giữ nguyên** → 400 `KHONG_CO_THAY_DOI`, không ghi nhật ký (tránh dòng nhật ký rỗng).
7. **Giá trị trong nhật ký** dạng chữ như UC-20: `"1000000 TIEN_MAT"`; `TAO` cũ rỗng; `THU_HOI` cũ `"HIEU_LUC"`, mới `"DA_THU_HOI"`.
8. **Chặn số quá lớn** ở API (`so_tien` ≤ 1.000.000.000.000 → trên thì 400), vì bảng không có ràng buộc `so_tien > 0`; không thêm migration chỉ cho việc này.
9. **Ngoài phạm vi:** tài xế xem tạm ứng của mình trên điện thoại (để UC-21 hoặc sau); chênh lệch tạm ứng khi quyết toán (UC-24).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-23-AC1 | Chuyến `DA_CHOT`, định mức chốt 1.000.000: cấp 1.000.000 tiền mặt → 201, khoản `HIEU_LUC`, `tai_xe_id` là tài xế của chuyến, `nguoi_tao` là Kế toán; có 1 dòng `NHAT_KY_TIEN` `TAO` | API | BR-53, 62 (TC-BR53-01) |
| UC-23-AC2 | Ca biên tổng: cấp 600.000 rồi 400.000 → cả hai được (tổng đúng 1.000.000); cấp thêm 1 đ → 422 `BR-53`, không lưu; cấp một lần 1.200.000 → 422, không lưu | API | BR-53 (TC-BR53-02…04) |
| UC-23-AC3 | Trạng thái chuyến: `DANG_CHAY` cấp được; `LAP`, `HOAN_THANH`, `HUY`, `DA_QUYET_TOAN` → 409 `BR-53`, không lưu | API | BR-53 (TC-BR53-06) |
| UC-23-AC4 | Dữ liệu sai → 400, không lưu: `so_tien` 0, âm, số lẻ, chữ, vượt 1.000.000.000.000; `hinh_thuc` ngoài 2 giá trị; thiếu trường; trường lạ. Chuyến không có → 404 | API | security-rules |
| UC-23-AC5 | Khoản `DA_THU_HOI` không tính vào tổng: cấp 1.000.000 → thu hồi → cấp lại 1.000.000 được | API | BR-53 |
| UC-23-AC6 | Sửa: giảm 1.000.000 → 800.000 kèm lý do → khoản đổi, nhật ký `SUA` có cũ, mới, lý do; sửa lên 1.100.000 → 422 `BR-53`, khoản giữ 1.000.000; ca biên sửa đúng bằng định mức được; thiếu / rỗng lý do → 400; số và hình thức giữ nguyên → 400 | API | BR-53, 62 (TC-BR53-05) |
| UC-23-AC7 | Sửa, thu hồi theo trạng thái: chuyến `HOAN_THANH` sửa được; khoản `DA_THU_HOI` sửa → 409; chuyến `DA_QUYET_TOAN` sửa / thu hồi → 409 | API | BR-29, 53 |
| UC-23-AC8 | Thu hồi: `HIEU_LUC → DA_THU_HOI`, nhật ký `THU_HOI` (bỏ trống lý do thì ghi câu mặc định); thu hồi lần hai → 409. Cấp rồi thu hồi → nhật ký đúng 2 dòng `TAO`, `THU_HOI`, mỗi dòng có người làm, giờ máy chủ, lý do | API | BR-62 (TC-BR62-01) |
| UC-23-AC9 | Nối với UC-15, 16: còn khoản `HIEU_LUC` → mở chốt 409 `BR-24`, hủy 409 `BR-25`; Kế toán thu hồi xong → mở chốt về `LAP`, hủy được | API | BR-24, 25 (TC-BR24-01/02, TC-BR25-02) |
| UC-23-AC10 | Nhật ký chỉ thêm: cấp → sửa → thu hồi tạo 3 dòng theo thứ tự, các dòng cũ không đổi | API | BR-62 |
| UC-23-AC11 | Phân quyền: Điều phối, Tài xế, Quản lý gọi cấp / sửa / thu hồi → 403; Quản lý xem 2 API GET được; Điều phối, Tài xế xem → 403; chưa đăng nhập → 401. Khoản / chuyến không có → 404 | API | BR-57, NFR-SEC-02 |
| UC-23-AC12 | Xem: `GET /api/chuyen/{id}/tam-ung` trả định mức, tổng hiệu lực, còn được cấp (không âm), danh sách khoản; `GET /api/tam-ung` lọc đúng theo `trang_thai`, `chuyen_id`, `tai_xe_id` | API | BR-53 |
| UC-23-AC13 | Đồng thời: hai Kế toán cùng cấp 600.000 cho chuyến định mức 1.000.000 → đúng một lần được, tổng không vượt định mức | API | BR-53, kien-truc mục 6 |
| UC-23-AC14 | Giao diện Kế toán: menu Tạm ứng, chọn chuyến thấy định mức / đã cấp / còn được cấp, ô số tiền điền sẵn; cấp vượt hiện lỗi kèm `BR-53`; sửa có lý do; thu hồi hỏi xác nhận; số liệu cập nhật ngay sau mỗi thao tác | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (07/11):
  - `backend/app/modules/tien/tam_ung/` (mới): `service.py` (cấp, sửa, thu hồi, xem; khóa dòng chuyến rồi khoản; `_kiem_br53` dùng cho cả cấp và sửa, sửa thì trừ chính khoản đang sửa; nhật ký `TAO`/`SUA`/`THU_HOI`), `router.py` (5 endpoint, ghi: chỉ `KE_TOAN`; xem: `KE_TOAN`, `QUAN_LY`), `schemas.py` (`so_tien` số nguyên chặt 1…10¹², `extra="forbid"`). `app/main.py` thêm router theo chữ cái.
  - Frontend: `api/tamUng.ts`, `pages/ke-toan/TamUng.tsx` (chọn chuyến, số liệu định mức / đã cấp / còn được cấp, form cấp điền sẵn số gợi ý, bảng khoản có Sửa tại dòng và Thu hồi hỏi xác nhận), `App.tsx` thêm menu **Tạm ứng** sau "Chi phí cố định xe".
  - Tài liệu: `api.md` 2.6 (thêm `GET /api/chuyen/{id}/tam-ung`, ghi rõ body, mã lỗi của 4 endpoint còn lại).
- Không đổi CSDL, không thêm gói. UC-15, 16 đã chặn mở chốt / hủy khi còn `HIEU_LUC`; UC-23 chỉ thêm đường thu hồi.
- Test đã viết: `tests/api/test_uc23_tam_ung.py` (49 ca). Đã thử làm hỏng 4 quy tắc (bỏ khóa dòng chuyến, sửa không trừ khoản đang sửa, tính cả khoản đã thu hồi, bỏ nhật ký thu hồi) → mỗi lần có test đỏ, rồi trả lại code.
- Kết quả: 49/49 đạt; toàn bộ **590 passed**; ruff, `alembic check`, oxlint, tsc, prettier, build sạch.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc23_tam_ung.py`
- Thử giao diện: `docs/test-evidence/UC-23/du-lieu.md`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-23-AC1 | API | `test_uc23_ac1_cap_hop_le` | Đạt | 07/11/2026 |
| UC-23-AC2 | API | `test_uc23_ac2_*` (2 ca, biên 600k + 400k, thêm 1 đ) | Đạt | 07/11/2026 |
| UC-23-AC3 | API | `test_uc23_ac3_*` (5 ca) | Đạt | 07/11/2026 |
| UC-23-AC4 | API | `test_uc23_ac4_*` (12 ca, biên trần 10¹²) | Đạt | 07/11/2026 |
| UC-23-AC5 | API | `test_uc23_ac5_thu_hoi_roi_cap_lai` | Đạt | 07/11/2026 |
| UC-23-AC6 | API | `test_uc23_ac6_*` (8 ca) | Đạt | 07/11/2026 |
| UC-23-AC7 | API | `test_uc23_ac7_*` (3 ca) | Đạt | 07/11/2026 |
| UC-23-AC8 | API | `test_uc23_ac8_*` (2 ca) | Đạt | 07/11/2026 |
| UC-23-AC9 | API | `test_uc23_ac9_*` (mở chốt, hủy) | Đạt | 07/11/2026 |
| UC-23-AC10 | API | `test_uc23_ac10_nhat_ky_chi_them` | Đạt | 07/11/2026 |
| UC-23-AC11 | API | `test_uc23_ac11_*` (8 ca) | Đạt | 07/11/2026 |
| UC-23-AC12 | API | `test_uc23_ac12_*` (3 ca) | Đạt | 07/11/2026 |
| UC-23-AC13 | API | `test_uc23_ac13_cap_dong_thoi` | Đạt | 07/11/2026 |
| UC-23-AC14 | UI | | CHƯA KIỂM | |
