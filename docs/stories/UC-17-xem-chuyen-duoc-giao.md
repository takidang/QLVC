# UC-17: Xem chuyến được giao

- **Trạng thái:** Hoàn thành (31/10/2026) · duyệt 31/10/2026, Kiệt · chờ Tài review PR vào `dev`
- **Tác nhân:** Tài xế (trên điện thoại, web responsive 360 px)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-17, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2 (`/api/toi/chuyen`) · `docs/nghiep-vu.md` mục 9.2 · `docs/security-rules.md` (IDOR)
- **Quy tắc nghiệp vụ liên quan:** BR-58 (tài xế chỉ xem chuyến của mình), BR-63 (thứ tự lịch trình), BR-71 (ETA kế hoạch, lương lưu lúc chốt), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Dùng lại:** `app/domain/lich_trinh.py`, `_ngu_canh`, `_don_ghep` trong `app/modules/chuyen/service.py` (UC-13)

## Mô tả ngắn
Tài xế mở điện thoại, thấy danh sách chuyến được giao cho mình (việc cần làm và lịch sử), bấm vào một chuyến để xem lịch trình theo thứ tự điểm dừng, giờ dự kiến, và ở từng điểm: lấy/giao đơn nào, địa chỉ, người liên hệ, số điện thoại, hàng gì. Đây là màn hình gốc cho UC-18 (bắt đầu/kết thúc), UC-19, 20 (quét mã).

## Đặc tả rút gọn
- **Danh sách** (`GET /api/toi/chuyen?nhom=can_lam|da_xong&trang&so_dong`): chỉ chuyến có `tai_xe_id` là hồ sơ tài xế của người đang đăng nhập.
  - `can_lam` (mặc định): `DA_CHOT`, `DANG_CHAY`; `DANG_CHAY` lên đầu, rồi theo giờ khởi hành tăng dần.
  - `da_xong`: `HOAN_THANH`, `DA_QUYET_TOAN`; mới nhất lên đầu.
  - Không bao giờ có `LAP` (Điều phối còn sửa) và `HUY`.
  - Mỗi dòng: mã chuyến, tuyến, biển số xe, khởi hành / kết thúc dự kiến, trạng thái, số đơn (mỗi đơn 2 điểm dừng: lấy, giao).
- **Chi tiết** (`GET /api/toi/chuyen/{id}`): thông tin chuyến như dòng danh sách, cộng:
  - **Lịch trình** theo thứ tự BR-63: mỗi điểm có thứ tự, tên nút, việc (`LAY` / `GIAO`), giờ dự kiến, và đơn ở điểm đó (mã đơn, khách, mô tả, kg, m³, số kiện, địa chỉ, người liên hệ / người nhận, SĐT, khung giờ lấy hoặc hạn giao, trạng thái đơn).
  - Giờ dự kiến: **ETA kế hoạch** đã lưu lúc chốt (BR-71) nếu có; chưa có thì tính theo lịch trình hiện tại (UC-13).
  - **Lương chuyến** đã chốt của tài xế (`luong_tai_xe_chot`).
  - Đơn: các đơn ghép **hiệu lực**, và đơn đã có kết quả trên chuyến này (`ket_qua` khác rỗng – đơn thất bại vẫn hiện trong lịch sử sau BR-36).
- **Không có tiền khác:** không trả cước đơn, đơn giá, lãi dự kiến, định mức chi phí (quyết định số 3).
- **Chuyến không phải của mình, chuyến `LAP` / `HUY`, id không có** → cùng **404** "Không tìm thấy chuyến" (không lộ chuyến có tồn tại – security-rules IDOR).
- Chỉ xem: UC-17 không đổi gì trong CSDL.

## Quyết định đã chốt (31/10/2026, Kiệt – Tài xem khi review PR)
1. **Trạng thái thấy được:** từ `DA_CHOT` trở đi (`DA_CHOT`, `DANG_CHAY`, `HOAN_THANH`, `DA_QUYET_TOAN`); không thấy `LAP`, `HUY`.
2. **Chuyến của người khác:** 404 giống chuyến không tồn tại, không trả 403.
3. **Tiền:** chỉ hiện lương chuyến đã chốt của chính tài xế; ẩn cước, lãi, định mức.
4. **ETA:** dùng ETA kế hoạch lưu lúc chốt; chuyến chốt trước khi UC-15 lưu ETA (cột rỗng) thì tính lại theo lịch trình hiện tại.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-17-AC1 | Danh sách chỉ có chuyến của tài xế đang đăng nhập: tài xế An có 2 chuyến, Bình có 1 → An thấy đúng 2 của mình, không thấy chuyến của Bình | API | BR-58 |
| UC-17-AC2 | Lọc theo trạng thái: `can_lam` có `DA_CHOT`, `DANG_CHAY` (chạy lên đầu, rồi khởi hành sớm trước); `da_xong` có `HOAN_THANH`, `DA_QUYET_TOAN` (mới nhất trước); chuyến `LAP`, `HUY` của chính mình **không** hiện ở nhóm nào; `nhom` lạ → 400 | API | BR-58 |
| UC-17-AC3 | Mỗi dòng có mã chuyến, tuyến, biển số, khởi hành / kết thúc dự kiến, trạng thái, số đơn; không có trường tiền, không có lương; phân trang đúng `tong`; chưa có chuyến → `du_lieu` rỗng | API | — |
| UC-17-AC4 | Chi tiết: lịch trình đúng thứ tự BR-63 và giờ của kịch bản mục 11 (chuyến 06:00 có Đ1, Đ4, Đ2: 06:00 / 06:20 / 07:40 / 09:00 / 11:50 / 12:10); mỗi điểm có đủ thông tin đơn (địa chỉ, người liên hệ/nhận, SĐT, hàng, khung giờ/hạn, trạng thái) | API | BR-63 |
| UC-17-AC5 | Giờ dự kiến lấy ETA kế hoạch đã lưu (đặt `eta_giao_ke_hoach` khác giờ tính → trả giờ đã lưu); cột rỗng → giờ tính theo lịch trình | API | BR-71 |
| UC-17-AC6 | Chi tiết có `luong_tai_xe_chot`; JSON **không** chứa `cuoc_tinh`, `don_gia_chot`, `lai_du_kien`, `dm_*` ở bất kỳ cấp nào | API | security-rules |
| UC-17-AC7 | Chuyến chạy rỗng (`DA_CHOT`, không đơn) → lịch trình rỗng, không lỗi. Chuyến `HOAN_THANH` có một đơn thất bại đã gỡ hiệu lực (BR-36) → đơn đó vẫn hiện với trạng thái `THAT_BAI` | API | BR-23, BR-36 |
| UC-17-AC8 | Chi tiết chuyến của tài xế khác, chuyến `LAP` / `HUY` của chính mình, id không có → **cùng** 404, cùng `ma` và `thong_diep` | API | BR-58, security-rules |
| UC-17-AC9 | Phân quyền: Điều phối, Quản lý, Kế toán gọi `/api/toi/chuyen` và `/api/toi/chuyen/{id}` → 403; chưa đăng nhập → 401; tài xế bị ngừng (UC-04) → 401 | API | BR-57 |
| UC-17-AC10 | Giao diện tài xế (điện thoại 360 px, không cuộn ngang): sau đăng nhập vào thẳng "Chuyến của tôi", hai thẻ **Cần làm / Đã xong**; bấm chuyến → lịch trình từng điểm, SĐT bấm gọi được (`tel:`), không thấy cước | UI | NFR-USA |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/toi/{schemas,service,router}.py` (mới), `backend/app/main.py` (gắn router); `frontend/src/api/toi.ts` (mới), `frontend/src/pages/tai-xe/{ChuyenCuaToi,ChuyenCuaToiChiTiet}.tsx` (mới), `frontend/src/App.tsx` (menu tài xế, vào thẳng "Chuyến của tôi"), `frontend/src/index.css` (thẻ cho điện thoại); `docs/api.md`. Không đụng `models/`, không thêm migration, không sửa code UC-11/13 của Tài.
- Dùng lại từ `app/modules/chuyen/service.py` (UC-13): `_truy_van`, `_ra`, `_ngu_canh`, `_don_ghep` và `lich_trinh` trong `app/domain/lich_trinh.py` – chỉ gọi, không sửa. Tài đổi các hàm này thì test UC-17 báo ngay.
- Test đã viết: `backend/tests/api/test_uc17_xem_chuyen.py` – **14 passed**; toàn bộ backend **368 passed** (31/10, nhánh tách từ `dev`, không chứa code UC-02). Gộp `dev` sau PR #5 (01/11): sửa xung đột `main.py` (router xếp theo chữ cái), `TIEN-DO.md`; dữ liệu thử tách thành `docs/test-evidence/UC-xx/du-lieu.md` theo luật PR #7 – UC-17 ở `docs/test-evidence/UC-17/du-lieu.md`.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc17_xem_chuyen.py`
- Lệch đặc tả: thêm tham số `nhom`, mô tả rõ trường trả về và 404 → đã sửa `docs/api.md` cùng commit.
- AC10 thử tay 31/10 (Kiệt, DevTools 360 px): 4 ca đạt. Lỗi bắt được khi thử: bấm lại thẻ đang chọn thì kẹt "Đang tải…" → sửa trong `ChuyenCuaToi.tsx`, thử lại đạt (lỗi giao diện, test backend không bắt được).
- `ponytail-review` 31/10 (Kiệt tự review): không có mục phải sửa. Lưu ý cho Tài: `toi/service.py` gọi các hàm có dấu `_` của `chuyen/service.py` (`_truy_van`, `_ra`, `_ngu_canh`, `_don_ghep`) để không chép lại code UC-13; Tài muốn thì đổi tên bỏ dấu `_` cho rõ là hàm dùng chung.
- Máy chủ trả giờ dạng UTC (như UC-13); giao diện đổi sang giờ Việt Nam khi hiện.
- Ghi chú: hai đơn lấy cùng nút, không có khung giờ, xếp theo mã đơn (BR-63 trong `lich_trinh.py`), nên thứ tự lấy trên máy thật có thể khác kịch bản mục 11 (đã báo Tài ở lần thử UC-13).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-17-AC1 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac1_chi_thay_chuyen_cua_minh` | Đạt | 31/10/2026 |
| UC-17-AC2 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac2_nhom_va_thu_tu` | Đạt | 31/10/2026 |
| UC-17-AC3 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac3_* (2 ca)` | Đạt | 31/10/2026 |
| UC-17-AC4 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac4_lich_trinh_theo_kich_ban` | Đạt | 31/10/2026 |
| UC-17-AC5 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac5_dung_eta_ke_hoach_da_luu` | Đạt | 31/10/2026 |
| UC-17-AC6 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac6_chi_co_luong` | Đạt | 31/10/2026 |
| UC-17-AC7 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac7_* (2 ca)` | Đạt | 31/10/2026 |
| UC-17-AC8 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac8_cung_mot_404` | Đạt | 31/10/2026 |
| UC-17-AC9 | API | `tests/api/test_uc17_xem_chuyen.py::test_uc17_ac9_* (4 ca)` | Đạt | 31/10/2026 |
| UC-17-AC10 | UI | `docs/test-evidence/UC-17/` (3 ảnh, ca a–d ở `docs/test-evidence/UC-17/du-lieu.md`) + Kiệt xác nhận khổ 360 không cuộn ngang | Đạt | 31/10/2026 |
