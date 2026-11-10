# UC-33: Báo sự cố

- **Trạng thái:** Chờ review – 9/9 AC đạt (đã duyệt 10/11/2026 (Kiệt: "duyệt bỏ 7" – quyết định 1–6, 8 như đề xuất, bỏ quyết định 7))
- **Tác nhân:** Tài xế (điện thoại)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-33) · `docs/nghiep-vu.md` (thuật ngữ "Sự cố", mục 10 tình huống xe hỏng) · `docs/api.md` mục 2.5 (`POST /api/toi/chuyen/{id}/su-co`) · `docs/security-rules.md` (upload) · bảng `SU_CO`, `TEP` trong `docs/so-do.md`
- **Quy tắc nghiệp vụ liên quan:** BR-58 (chỉ chuyến của mình), BR-57 (chỉ tài xế), NFR-PER-03 (ảnh ≤ 500 KB, nén trên trình duyệt). Phía Điều phối (cờ `SU_CO`, xem, đóng sự cố, kết thúc do sự cố BR-68) đã làm ở UC-32 của Tài.
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-33-bao-su-co` tách từ `dev`

## Mô tả ngắn
Khi chuyến đang chạy, tài xế báo sự cố: chọn loại, ghi chú, chụp ảnh. Sự cố lưu ở trạng thái **mở**, bảng chuyến của Điều phối hiện cờ đỏ "Sự cố" (UC-32). Chuyến vẫn chạy tiếp, trạng thái không đổi. Tài xế xem lại các sự cố đã báo và cách Điều phối xử lý.

## Đặc tả rút gọn
- **`POST /api/toi/chuyen/{id}/su-co`** (TX, multipart): `loai` ∈ `HONG_XE`, `TAI_NAN`, `KET_XE`, `THOI_TIET`, `KHAC`; `ghi_chu` 1–500 ký tự (NFC, bỏ khoảng trắng hai đầu); `anh` 0–5 ảnh JPG/PNG ≤ 500 KB (`app/luu_tru.py` như UC-21). Trường lạ → 400.
  - Thứ tự kiểm: chuyến không phải của mình / không có / `LAP` / `HUY` → **404** (như UC-17, 21); chuyến không `DANG_CHAY` → **409 `CHUYEN_KHONG_DANG_CHAY`**; thiếu ghi chú → **422**; sai loại, ghi chú quá dài → 400; ảnh sai loại 400, quá lớn 413.
  - Lưu `SU_CO` `MO`, `tai_xe_id` = tài xế; ảnh vào `TEP` (`su_co_id`, loại `ANH`). CSDL lỗi → xóa ảnh vừa ghi. Trả 201 sự cố vừa tạo. Không đổi trạng thái chuyến, đơn.
- **`GET /api/toi/chuyen/{id}/su-co`** (TX) – **endpoint mới**: sự cố của chuyến mình (loại, ghi chú, số ảnh, trạng thái, cách xử lý, lúc), cũ trước.
- **Giao diện** (trang chuyến của tài xế, 360 px): khối **Sự cố** khi chuyến đang chạy: danh sách (Mở / Đã xử lý kèm cách xử lý của Điều phối) và form **Báo sự cố** (loại, ghi chú, ảnh nén như UC-19, 21). Chuyến đã về thì khối chỉ còn danh sách.

## Quyết định (Kiệt duyệt 10/11/2026)
1. **Module mới `backend/app/modules/su_co/`** (router, service, schemas), đường dẫn `/api/toi/…` như `api.md`. Không đổi CSDL, không migration, không thêm gói.
2. **Danh sách loại cố định** (cột `loai` chuỗi 50, chưa có danh mục): `HONG_XE` Hỏng xe, `TAI_NAN` Tai nạn, `KET_XE` Kẹt xe / tắc đường, `THOI_TIET` Thời tiết xấu, `KHAC` Khác. Lưu mã, giao diện hiện tên tiếng Việt.
3. **Ghi chú bắt buộc, ảnh không bắt buộc** (tối đa 5): không BR nào bắt buộc ảnh; tai nạn ban đêm, hỏng camera vẫn phải báo được ngay.
4. **Chỉ báo khi `DANG_CHAY`** (tiền điều kiện UC-33). `DA_CHOT`, `HOAN_THANH`, `DA_QUYET_TOAN` → 409 `CHUYEN_KHONG_DANG_CHAY`; chuyến người khác, `LAP`, `HUY` → 404 như UC-21 quyết định 5, 10.
5. **Thêm `GET /api/toi/chuyen/{id}/su-co`** vào `api.md`: tài xế cần xem lại sự cố đã báo và cách Điều phối xử lý.
6. **Tài xế không sửa, không xóa sự cố** đã báo (là bằng chứng trong dòng thời gian khi tranh chấp). Báo nhầm thì báo thêm một sự cố ghi chú "báo nhầm", Điều phối đóng.
7. ~~Sửa trang Điều phối hiện tên loại tiếng Việt~~ **Bỏ** (Kiệt 10/11): UC-33 không sửa code UC-32 của Tài (`TheoDoiChuyen.tsx`, `theo_doi.py`); trang Điều phối tạm hiện mã `loai`. Bảng tên loại có ở `frontend/src/api/suCo.ts` (`TEN_LOAI_SU_CO`); nhắn Tài trong mô tả PR.
8. **Ngoài phạm vi:** Điều phối xem **ảnh** sự cố (link ảnh `/api/tep/{id}/link` hiện chỉ cho ảnh chi phí; mở cho ảnh sự cố cần Điều phối nên đụng UC-32 của Tài, nhắn Tài qua PR); thông báo đẩy cho Điều phối; sự cố tự kết thúc chuyến (Điều phối tự quyết theo BR-68).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-33-AC1 | C01 `DANG_CHAY`, An báo `HONG_XE`, ghi chú "Nổ lốp", 1 ảnh → 201 `MO`, `tai_xe_id` = An, 1 tệp `ANH` gắn `su_co_id`; chuyến vẫn `DANG_CHAY`, đơn không đổi | API | UC-33 |
| UC-33-AC2 | Báo không ảnh được (ca biên 0 ảnh); 5 ảnh được, 6 → 400; ảnh sai loại → 400; ảnh > 500 KB → 413; lỗi thì không lưu sự cố, không còn tệp trên đĩa | API | security-rules, NFR-PER-03 |
| UC-33-AC3 | Ghi chú: thiếu, chỉ khoảng trắng → 422; 500 ký tự được, 501 → 400; loại ngoài danh sách → 400; trường lạ (`trang_thai`, `tai_xe_id`) → 400 | API | UC-33 |
| UC-33-AC4 | Trạng thái chuyến: `DA_CHOT`, `HOAN_THANH`, `DA_QUYET_TOAN` → 409 `CHUYEN_KHONG_DANG_CHAY`, không lưu; `LAP`, `HUY`, chuyến của Bình, id không có → 404 | API | BR-58 |
| UC-33-AC5 | Phân quyền: Điều phối, Kế toán, Quản lý gọi POST / GET → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-33-AC6 | Xem: `GET` trả sự cố của chuyến mình, cũ trước, kèm số ảnh; sau khi Điều phối đóng (`POST /api/su-co/{id}/dong`) thì trả `DONG` và cách xử lý; chuyến của Bình → 404 | API | BR-58 |
| UC-33-AC7 | Sau khi báo: bảng chuyến trong ngày của Điều phối (`GET /api/chuyen?ngay=`) có cờ `SU_CO` cho C01; đóng hết sự cố thì mất cờ; dòng thời gian chi tiết chuyến có sự kiện `SU_CO` | API | UC-32 bước 4 |
| UC-33-AC8 | CSDL lỗi giữa chừng (ép lỗi lúc lưu tệp) → không có sự cố, không có tệp mồ côi trên đĩa | API | NFR-REL-01 |
| UC-33-AC9 | Giao diện tài xế (360 px): khối Sự cố ở chuyến đang chạy; báo thành công hiện ngay trong danh sách "Mở"; thiếu ghi chú báo lỗi rõ; chuyến đã về chỉ xem; sự cố đã đóng hiện cách xử lý | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (10/11):
  - `backend/app/modules/su_co/` (mới): `service.py` (báo: chuyến của mình qua `toi._chuyen_cua_toi`, khóa dòng chuyến, chỉ `DANG_CHAY`, ghi chú NFC bắt buộc, ảnh 0–5 qua `luu_tru`, CSDL lỗi thì xóa ảnh vừa ghi; xem; bảng `TEN_LOAI`), `router.py` (2 endpoint dưới `/api/toi`, chỉ `TAI_XE`, chặn trường lạ như UC-19, 21), `schemas.py`. `app/main.py` thêm router theo chữ cái.
  - Giao diện: `frontend/src/api/suCo.ts`, `pages/tai-xe/SuCo.tsx` (khối Sự cố: danh sách Đang mở / Đã xử lý kèm cách xử lý của Điều phối, form loại + ghi chú + ảnh nén), `ChuyenCuaToiChiTiet.tsx` gắn khối dưới Chi phí (chuyến đang chạy báo được, đã về chỉ xem).
  - Tài liệu: `api.md` 2.5 (thêm `GET`, chi tiết `POST`), `docs/test-evidence/UC-33/du-lieu.md`.
- Không đổi CSDL, không migration, không thêm gói. Không sửa code UC-32 (quyết định 7 bỏ).
- Test: `backend/tests/api/test_uc33_bao_su_co.py` 30 ca (AC1–AC8). Thử phá 5 quy tắc (bỏ kiểm đang chạy, bỏ bắt buộc ghi chú, bỏ xóa ảnh mồ côi, bỏ chặn trường lạ, bỏ giới hạn 5 ảnh): 5/5 bị test bắt.
- Giao diện Claude thử nhanh trên máy Kiệt (360 px, chuyến CH-261110-04): thiếu ghi chú báo lỗi, báo có ảnh / không ảnh hiện ngay "Đang mở", không tràn ngang. Kiệt thử tay 8/8 ca theo `du-lieu.md` (AC9).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc33_bao_su_co.py`
- Lệch đặc tả: `api.md` thêm `GET /api/toi/chuyen/{id}/su-co` (quyết định 5); mã lỗi mới `CHUYEN_KHONG_DANG_CHAY` (409), `THIEU_GHI_CHU` (422).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-33-AC1 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac1_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC2 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac2_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC3 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac3_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC4 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac4_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC5 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac5_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC6 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac6_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC7 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac7_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC8 | API | `backend/tests/api/test_uc33_bao_su_co.py::test_uc33_ac8_*` | Đạt (30 passed) | 10/11/2026 |
| UC-33-AC9 | UI | Kiệt thử 10/11, 8/8 ca a–h (`docs/test-evidence/UC-33/`) | Đạt | 10/11/2026 |
