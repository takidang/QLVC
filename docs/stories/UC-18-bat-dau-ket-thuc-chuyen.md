# UC-18: Bắt đầu / kết thúc chuyến

- **Trạng thái:** Hoàn thành (31/10/2026) · duyệt 31/10/2026, Kiệt · chờ Tài review PR vào `dev` (sau UC-17)
- **Tác nhân:** Tài xế (điện thoại)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-18) · `docs/api.md` mục 2 (`/api/toi/chuyen/{id}/bat-dau`, `/ket-thuc`) · `docs/kien-truc.md` mục 9 (lưu file) · `docs/security-rules.md` (upload)
- **Quy tắc nghiệp vụ liên quan:** BR-26 (bắt đầu: đúng tài xế, đúng ngày, kiểm lại BR-11…15), BR-28 (kết thúc khi mọi đơn có kết quả), BR-70 (km + ảnh), BR-36 (đơn thất bại gỡ hiệu lực khi kết thúc), BR-58 · NFR-PER-03 (ảnh ≤ 500 KB, nén trên trình duyệt), NFR-SEC-04
- **Người làm:** Kiệt · **Nối sau:** UC-17 (nhánh `kiet/uc-18-bat-dau-ket-thuc` tách từ `kiet/uc-17-xem-chuyen`; mở PR sau khi UC-17 gộp)

## Mô tả ngắn
Trên trang lịch trình (UC-17), tài xế nhập km đồng hồ, chụp ảnh đồng hồ và bấm **Bắt đầu** → chuyến `DA_CHOT → DANG_CHAY`. Giao/lấy xong hết đơn (UC-19, 20), nhập km cuối kèm ảnh, bấm **Kết thúc** → `HOAN_THANH`, km đồng hồ của xe được cập nhật, đơn thất bại được gỡ hiệu lực để Điều phối xử lý.

## Đặc tả rút gọn
- **Bắt đầu** `POST /api/toi/chuyen/{id}/bat-dau` (multipart: `km_bat_dau`, `anh_dong_ho`):
  - Chuyến của mình (không phải → 404 như UC-17), đang `DA_CHOT` (khác → 409).
  - **Hôm nay** (giờ Việt Nam) là ngày khởi hành dự kiến; sớm hơn giờ khởi hành trong cùng ngày vẫn được (kịch bản mục 11: bắt đầu 05:45 cho chuyến 06:00). Khác ngày → 422 BR-26.
  - Kiểm lại BR-11…15 theo ngày kết thúc dự kiến (dùng `xet_xe`, `xet_tai_xe` của UC-11); vi phạm → 422, liệt kê đủ trong `chi_tiet` (ngoại lệ 1a: giấy tờ vừa hết hạn).
  - BR-70: `km_bat_dau` ≥ km sàn của xe = lớn nhất của `km_dong_ho` và km bắt đầu các chuyến trước của cùng xe (phủ cả "chuyến trước kết thúc do sự cố không có km cuối"). Nhỏ hơn → 422 BR-70.
  - Lưu: `trang_thai = DANG_CHAY`, `khoi_hanh_thuc_te` = giờ **máy chủ**, `km_bat_dau`, ảnh vào `TEP` (`loai = ANH_KM_BAT_DAU`), một dòng `LICH_SU_TRANG_THAI`.
- **Kết thúc** `POST /api/toi/chuyen/{id}/ket-thuc` (multipart: `km_ket_thuc`, `anh_dong_ho`):
  - Chuyến của mình, đang `DANG_CHAY` (khác → 409).
  - BR-28: mọi đơn ghép hiệu lực phải `DA_GIAO` hoặc `THAT_BAI`; còn đơn khác → 422 BR-28, `chi_tiet` liệt kê mã đơn còn lại (ngoại lệ 2a).
  - BR-70: `km_ket_thuc` > `km_bat_dau` (bằng → 422).
  - Lưu: `HOAN_THANH`, `ket_thuc_thuc_te` giờ máy chủ, `km_ket_thuc`, `xe.km_dong_ho = km_ket_thuc`, ảnh `ANH_KM_KET_THUC`, lịch sử trạng thái. Ghép của từng đơn ghi `ket_qua` = trạng thái cuối (nếu UC-19/20 chưa ghi); đơn `THAT_BAI` → ghép `hieu_luc = false` (BR-36).
- **Ảnh** (dùng chung cho UC-19, 20, 21, 33 – `app/luu_tru.py`):
  - Kiểm loại theo **nội dung** file (đầu file JPEG `FF D8 FF` / PNG `89 50 4E 47`), không tin đuôi tên hay `Content-Type` → sai → 400.
  - > 500 KB → **413** (NFR-PER-03, `kien-truc.md` mục 7). Rỗng → 400.
  - Tên file do máy chủ sinh (`uuid` + đuôi theo loại thật), không dùng tên người dùng gửi. Dev ghi vào thư mục `backend/uploads/` (đã có trong `.gitignore`); Supabase làm khi triển khai demo.
  - Ghi file sau khi kiểm xong mọi quy tắc; lỗi ghi CSDL thì xóa file vừa ghi.
- **Một giao dịch, khóa dòng chuyến** (`FOR UPDATE`): bấm Bắt đầu hai lần liên tiếp → lần hai 409, không có ảnh thừa.
- Xem lại ảnh (`GET /api/tep/{id}/link`) **chưa làm** ở UC-18: chưa có màn hình nào cần; làm cùng UC-32 theo dõi chuyến hoặc UC-24 quyết toán.

## Quyết định đã chốt (31/10/2026, Kiệt – Tài xem khi review PR)
1. **Upload ảnh:** cài `python-multipart` (Kiệt đồng ý 31/10), đúng thiết kế multipart trong `api.md`.
2. **"Trong ngày khởi hành":** so ngày theo giờ Việt Nam; sớm giờ trong cùng ngày được, khác ngày bị chặn.
3. **Km sàn BR-70:** lớn nhất của `km_dong_ho` xe và km bắt đầu các chuyến trước của xe.
4. **Kết thúc ghi `ket_qua` cho ghép** nếu chưa có, để lịch sử chuyến (UC-17 "Đã xong") vẫn thấy đơn thất bại sau BR-36.
5. **Ảnh sai loại → 400, quá lớn → 413**; lưu local ở dev (`backend/uploads/`), Supabase để lúc triển khai.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-18-AC1 | Bắt đầu hợp lệ (kịch bản mục 11: X1 km 120.000, nhập 120.000 + ảnh JPEG) → 200: chuyến `DANG_CHAY`, `khoi_hanh_thuc_te` là giờ máy chủ, `km_bat_dau` lưu, 1 bản ghi `TEP` loại `ANH_KM_BAT_DAU` có file thật trên đĩa, 1 dòng lịch sử `DA_CHOT → DANG_CHAY`; đơn giữ nguyên `DA_GHEP` | API | BR-26, BR-70 |
| UC-18-AC2 | Ngày: bắt đầu trước giờ khởi hành trong cùng ngày được; khởi hành ngày mai hoặc hôm qua → 422 BR-26, chuyến giữ `DA_CHOT` | API | BR-26 |
| UC-18-AC3 | Giấy tờ: xe `NGUNG` (BR-11), đăng kiểm hết trước ngày kết thúc (BR-12), bảo hiểm hết (BR-13), tài xế hạng thấp (BR-14), GPLX hết hạn (BR-15) → 422 với mã BR tương ứng, `chi_tiet` liệt kê đủ khi vi phạm nhiều; ca biên: hạn đúng bằng ngày kết thúc vẫn đạt | API | BR-11…15 |
| UC-18-AC4 | Km bắt đầu: = km sàn được; km sàn − 1 → 422 BR-70; chuyến trước của xe kết thúc do sự cố, không có km cuối, km bắt đầu 120.500 → nhập 120.499 bị chặn, 120.500 được | API | BR-70 |
| UC-18-AC5 | Ảnh: thiếu ảnh → 400; file đuôi `.jpg` nhưng nội dung không phải ảnh → 400; ảnh 500 KB được, 500 KB + 1 byte → 413; PNG được; tên lưu trên đĩa là `uuid`, không chứa tên người dùng gửi (gửi tên `../../x.jpg`); lỗi nào cũng không đổi trạng thái chuyến, không để lại file | API | security-rules, NFR-PER-03 |
| UC-18-AC6 | Kết thúc hợp lệ: mọi đơn `DA_GIAO` / `THAT_BAI`, km 120.178 → 200: `HOAN_THANH`, `ket_thuc_thuc_te`, `km_ket_thuc`, `xe.km_dong_ho = 120.178`, ảnh `ANH_KM_KET_THUC`, lịch sử; ghép của đơn `THAT_BAI` thành `hieu_luc = false`, ghép của đơn `DA_GIAO` vẫn hiệu lực; cả hai có `ket_qua` | API | BR-28, BR-36, BR-70 |
| UC-18-AC7 | Còn đơn `DA_GHEP` hoặc `DA_LAY` → 422 BR-28, `chi_tiet` có đúng mã các đơn còn lại; chuyến 0 đơn (chạy rỗng) kết thúc được | API | BR-28, BR-23 |
| UC-18-AC8 | Km kết thúc = km bắt đầu → 422 BR-70; km bắt đầu + 1 được | API | BR-70 |
| UC-18-AC9 | Sai trạng thái: bắt đầu chuyến `DANG_CHAY` / `HOAN_THANH` → 409; kết thúc chuyến `DA_CHOT` → 409; bấm Bắt đầu hai lần liên tiếp → lần hai 409, chỉ có 1 ảnh | API | ST-T |
| UC-18-AC10 | Phân quyền: chuyến của tài xế khác, chuyến `LAP`, id không có → 404 (như UC-17), không lưu ảnh; Điều phối, Kế toán, Quản lý → 403; chưa đăng nhập → 401 | API | BR-26, BR-58 |
| UC-18-AC11 | Giao diện (điện thoại 360 px): chuyến `DA_CHOT` có ô km + nút chụp ảnh + **Bắt đầu**; ảnh nén trên trình duyệt trước khi gửi; lỗi hiện tiếng Việt kèm mã BR; sau bắt đầu thẻ chuyển "Đang chạy" và hiện ô **Kết thúc**; còn đơn chưa xong thì hiện danh sách đơn còn lại | UI | NFR-USA-02, NFR-PER-03 |
| UC-18-AC12 | Xe hoặc tài xế đang có chuyến khác `DANG_CHAY` (BR-26): (a) xe X1 có chuyến khác `DANG_CHAY` → An bắt đầu C01 bị chặn 409 `BR-26`, thông điệp có mã chuyến đang chạy, C01 giữ `DA_CHOT` và không lưu ảnh; (b) chuyến khác đã `HOAN_THANH` hoặc `HUY` → bắt đầu được (200); (c) tài xế An có chuyến khác `DANG_CHAY` trên xe khác → bị chặn 409 `BR-26` | API | BR-26 |

## Ghi chú triển khai
- File đã đổi: `backend/app/luu_tru.py` (mới – kiểm và lưu ảnh, dùng chung cho UC-19…21, 33), `backend/app/modules/toi/{service,router}.py` (bắt đầu, kết thúc; tách `_chuyen_cua_toi` dùng chung với UC-17), `backend/requirements.txt` (`python-multipart==0.0.32`); `frontend/src/nenAnh.ts` (mới – nén ảnh bằng canvas, không thêm thư viện), `frontend/src/api/toi.ts` (`ghiKm`), `frontend/src/pages/tai-xe/ChuyenCuaToiChiTiet.tsx` (ô Bắt đầu / Kết thúc), `frontend/src/index.css`; `docs/api.md`. Không đụng `models/`, không thêm migration.
- Dùng lại `xet_xe`, `xet_tai_xe` (UC-11, `app/domain/chuyen.py`) để kiểm lại BR-11…15 – cùng câu báo lỗi với lúc lập chuyến.
- Test đã viết: `backend/tests/api/test_uc18_bat_dau_ket_thuc.py` – **32 passed**; toàn bộ backend **400 passed** (31/10, nhánh nối sau UC-17). `ruff check`, `ruff format`, `npm run lint`, `npm run build` sạch. Test ghi ảnh vào thư mục tạm (`tmp_path`), không để file trong `backend/uploads/`.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc18_bat_dau_ket_thuc.py` (máy khác cần `pip install -r requirements-dev.txt` để có `python-multipart`)
- Lệch đặc tả: thêm `python-multipart`; `api.md` ghi rõ mã lỗi và giới hạn ảnh; thư mục lưu dev là `backend/uploads/` (đã có trong `.gitignore`) thay cho `backend/tep/` ghi lúc nháp.
- AC11 thử tay 31/10 (Kiệt, DevTools 360 px): ca a–d đạt; ảnh nén còn ~60 KB. Ca e (kết thúc thành công) không thử tay, đã có test AC6.
- **Chưa kiểm, để sau:** Quản lý / Điều phối xem km và ảnh đồng hồ – chưa có màn hình, kiểm khi UC-32 Theo dõi chuyến (Tài) xong.
- `ponytail-review` 31/10 (Kiệt tự review): không có mục phải sửa. Nice to have: câu lỗi BR-70 in số kiểu `49,999` (dấu phẩy) – đổi sang `49.999` cho đúng kiểu Việt Nam khi nào sửa lại giao diện. Ghi file trước khi commit: máy chủ sập đúng giữa hai bước có thể để lại 1 file thừa trong `uploads/` (không có bản ghi) – chấp nhận.
- Test dựa vào "hôm nay" theo giờ Việt Nam (chuyến 23:00 hôm nay): chạy test đúng lúc qua nửa đêm có thể lệch ngày – xác suất rất nhỏ, chấp nhận.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-18-AC1 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac1_bat_dau_hop_le` | Đạt | 31/10/2026 |
| UC-18-AC2 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac2_* (3 ca)` | Đạt | 31/10/2026 |
| UC-18-AC3 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac3_* (6 ca)` | Đạt | 31/10/2026 |
| UC-18-AC4 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac4_* (2 ca)` | Đạt | 31/10/2026 |
| UC-18-AC5 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac5_* (7 ca)` | Đạt | 31/10/2026 |
| UC-18-AC6 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac6_ket_thuc_hop_le` | Đạt | 31/10/2026 |
| UC-18-AC7 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac7_* (3 ca)` | Đạt | 31/10/2026 |
| UC-18-AC8 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac8_km_ket_thuc` | Đạt | 31/10/2026 |
| UC-18-AC9 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac9_* (3 ca)` | Đạt | 31/10/2026 |
| UC-18-AC10 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac10_* (5 ca)` | Đạt | 31/10/2026 |
| UC-18-AC11 | UI | `docs/test-evidence/UC-18/` (4 ảnh, ca a–d ở `docs/test-evidence/UC-18/du-lieu.md`) – Kiệt thử | Đạt | 31/10/2026 |
| UC-18-AC12 | API | `tests/api/test_uc18_bat_dau_ket_thuc.py::test_uc18_ac12_* (4 ca)` | CHƯA KIỂM | — |
