# UC-19: Quét mã lấy hàng / báo không lấy được

- **Trạng thái:** Nháp (31/10/2026) · chờ duyệt
- **Tác nhân:** Tài xế (điện thoại)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-19) · `docs/api.md` mục 3.2 (`POST /api/toi/quet`), mục 2 (`GET /api/danh-muc/ly-do`) · `docs/so-do.md` mục 9 (thứ tự khóa) · `docs/security-rules.md` (quét mã, upload)
- **Quy tắc nghiệp vụ liên quan:** BR-38 (chỉ đơn thuộc chuyến của mình đang chạy), BR-39 (lấy → `DA_LAY`, không lấy được → `THAT_BAI`), BR-42 (thất bại cần lý do + ảnh), BR-43 (giờ máy chủ, GPS, cờ thiếu GPS), BR-45 (quét lại không tạo bản ghi mới), BR-30 (lịch sử trạng thái), BR-37 (lý do có phía để đếm)
- **Người làm:** Kiệt · **Nối sau:** UC-18 (nhánh `kiet/uc-19-quet-lay`; mở PR sau khi UC-17, UC-18 gộp)

## Mô tả ngắn
Chuyến đang chạy, tài xế tới điểm lấy, quét (hoặc gõ) mã đơn trên phiếu: máy chủ kiểm đơn thuộc chuyến của mình rồi chuyển đơn `DA_GHEP → DA_LAY`, lưu giờ máy chủ và vị trí GPS. Không lấy được hàng thì chọn lý do trong danh mục và chụp ảnh → đơn `THAT_BAI`. Quét lại một đơn đã xử lý chỉ trả trạng thái hiện tại.

## Đặc tả rút gọn
- **`POST /api/toi/quet`** (multipart) – UC-19 làm hai loại `LAY`, `KHONG_LAY`; `GIAO`, `GIAO_THAT_BAI` làm ở UC-20 (gửi lên bây giờ → 400).
  - Trường: `ma_don` (bỏ khoảng trắng, không phân biệt hoa thường), `loai`, `lat` + `lng` + `do_chinh_xac_m` (không bắt buộc; có `lat` thì phải có `lng` và ngược lại; ngoài [-90, 90] / [-180, 180] → 400), `anh` (một hoặc nhiều, bắt buộc với `KHONG_LAY`), `ly_do_id` (bắt buộc với `KHONG_LAY`).
  - **Không có trường thời gian**: giờ quét lấy từ máy chủ.
- **Thứ tự kiểm** (theo `so-do.md` mục 9):
  1. Tìm ghép **hiệu lực** của đơn; không có, hoặc chuyến không phải của mình, hoặc mã đơn không tồn tại → **403** BR-38 "Đơn không thuộc chuyến của bạn" (cùng một câu, không lộ đơn có tồn tại – IDOR).
  2. Khóa chuyến (`FOR SHARE`) rồi đơn (`FOR UPDATE`): tài xế không kết thúc chuyến (UC-18, khóa `FOR UPDATE`) khi một lượt quét đang chạy; quét cùng đơn hai lần cùng lúc thì lần sau thấy kết quả lần trước.
  3. Chuyến không `DANG_CHAY` → **409** BR-38.
  4. Đơn đã khác `DA_GHEP` (đã lấy / giao / thất bại) → **200** `lap_lai: true`, trạng thái hiện tại, không tạo lượt quét, không lưu ảnh (BR-45).
  5. `KHONG_LAY`: thiếu lý do, lý do không có hoặc không áp dụng cho LẤY, thiếu ảnh → **422** BR-42. Ảnh sai loại 400, quá 500 KB 413 (dùng `app/luu_tru.py` của UC-18).
- **Lưu** (một giao dịch): `LUOT_QUET` (ghép, tài xế, loại, GPS, `thieu_gps`, lý do), ảnh vào `TEP` (`luot_quet_id`, `loai = ANH`), đơn → `DA_LAY` / `THAT_BAI`, `LICH_SU_TRANG_THAI` (lý do = tên lý do khi thất bại), ghép `ket_qua = THAT_BAI` khi thất bại. CSDL lỗi → xóa các file vừa ghi.
- **Trả về** `{ma_don, trang_thai, canh_bao, lap_lai}`; `canh_bao` có `THIEU_GPS` khi không gửi tọa độ (BR-43 – vẫn cho quét).
- **`GET /api/danh-muc/ly-do?ap_dung=LAY|GIAO`** (Điều phối, Quản lý, Tài xế): `{id, ten, ap_dung, phia}`.
- **Danh mục lý do** nạp bằng **migration thứ 3** (đã ghi "Đang chặn" trong `TIEN-DO.md`, nhánh `kiet/tai-lieu-chan-migration-ly-do`):

  | Áp dụng | Phía `KHACH` | Phía `SU_CO_XE` |
  |---|---|---|
  | LẤY | Hàng chưa chuẩn bị xong · Không liên lạc được người gửi · Sai địa chỉ lấy hàng · Hàng khác mô tả (quá khổ, quá nặng) · Lý do khác | Xe hỏng / sự cố trên đường |
  | GIAO | Người nhận vắng · Người nhận từ chối nhận · Sai địa chỉ giao · Lý do khác | Hàng hư hỏng · Xe hỏng / sự cố trên đường |

  Lý do giao theo `use-cases.md` UC-20; "Hàng hư hỏng" xếp phía `SU_CO_XE` (lỗi bên vận chuyển, không tính vào ngưỡng thất bại của khách BR-37). UC-20 và UC-32 (BR-68 "sự cố xe") dùng chung danh mục này.
- **Camera quét QR chưa làm** ở story này: cần thư viện frontend, phải hỏi Tài trước (CLAUDE.md). Giao diện có ô **gõ mã đơn** (luồng thay thế 2a của đặc tả), gửi đúng API như khi quét. Camera làm một lần cho cả UC-19, UC-20 khi Tài đồng ý thư viện.

## Quyết định đã chốt (31/10/2026, Kiệt – Tài xem khi review PR)
1. **Nạp lý do bằng migration** (Kiệt chọn 31/10), có ghi "Đang chặn" trước.
2. **Bộ lý do lấy** như bảng trên (Kiệt chọn bộ đề xuất); "Hàng hư hỏng" khi giao thuộc phía `SU_CO_XE`.
3. **Đơn không thuộc chuyến của mình / mã không có → 403** theo `api.md` 3.2 (khác UC-17 trả 404 cho cả chuyến: ở đây mã đơn in trên phiếu, câu báo chung không lộ thêm gì).
4. **Camera QR tách ra**, làm sau khi Tài đồng ý thư viện; story này dùng ô gõ mã.
5. **GPS gửi một nửa** (chỉ `lat` hoặc chỉ `lng`) → 400, không coi là thiếu GPS.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-19-AC1 | Quét `LAY` hợp lệ có GPS → 200 `{trang_thai: DA_LAY, canh_bao: [], lap_lai: false}`: đơn `DA_LAY`, 1 lượt quét có giờ **máy chủ**, đúng tọa độ, `thieu_gps = false`, 1 dòng lịch sử `DA_GHEP → DA_LAY` người làm là tài xế; mã gõ thường và có khoảng trắng (` dh-0001 `) vẫn nhận | API | BR-39, BR-43 |
| UC-19-AC2 | Không gửi GPS → vẫn 200, `canh_bao: [THIEU_GPS]`, `thieu_gps = true`; chỉ gửi `lat` → 400; `lat = 91` → 400; biên `lat = 90, lng = -180` được | API | BR-43 |
| UC-19-AC3 | `KHONG_LAY` hợp lệ (lý do LẤY + 1 ảnh) → `THAT_BAI`; lượt quét có `ly_do_id`; ảnh lưu `TEP` gắn lượt quét, có file; lịch sử ghi tên lý do; ghép `ket_qua = THAT_BAI`, vẫn hiệu lực tới khi kết thúc chuyến (BR-36 ở UC-18); 2 ảnh → 2 bản ghi `TEP` | API | BR-39, BR-42 |
| UC-19-AC4 | `KHONG_LAY` thiếu lý do, lý do không tồn tại, lý do của GIAO, thiếu ảnh → 422 BR-42; ảnh sai loại 400, quá 500 KB 413; mọi lỗi không đổi trạng thái đơn, không để lại file | API | BR-42, security-rules |
| UC-19-AC5 | Đơn thuộc chuyến của tài xế khác, đơn chưa ghép (`CHO_GHEP`), mã không tồn tại → **cùng** 403 BR-38, cùng câu báo; không tạo lượt quét | API | BR-38 |
| UC-19-AC6 | Chuyến của mình nhưng `DA_CHOT` (chưa bắt đầu) hoặc `HOAN_THANH` → 409 BR-38 | API | BR-38 |
| UC-19-AC7 | Quét `LAY` lần hai đơn đã `DA_LAY` → 200 `lap_lai: true`, `trang_thai: DA_LAY`, không thêm lượt quét; đơn `THAT_BAI` quét `LAY` → 200 `lap_lai: true`, vẫn `THAT_BAI`; `KHONG_LAY` đơn đã lấy → `lap_lai: true`, không lưu ảnh | API | BR-45 |
| UC-19-AC8 | Hai lượt `LAY` cùng đơn gửi đồng thời → đúng 1 lượt quét được tạo, một bên `lap_lai: true` | API | BR-45 |
| UC-19-AC9 | `loai` = `GIAO` / `GIAO_THAT_BAI` / lạ → 400 (UC-20 làm); thiếu `ma_don` → 400 | API | — |
| UC-19-AC10 | `GET /api/danh-muc/ly-do?ap_dung=LAY` chỉ lý do LẤY, mỗi dòng có `phia`; `ap_dung` lạ → 400; Tài xế, Điều phối, Quản lý được; Kế toán 403; chưa đăng nhập 401 | API | BR-37, BR-42 |
| UC-19-AC11 | Phân quyền `POST /api/toi/quet`: Điều phối, Kế toán, Quản lý → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-19-AC12 | Migration thứ 3: chạy `alembic upgrade head` trên CSDL dev → bảng `LY_DO` có đúng 12 lý do như bảng trên; `alembic downgrade -1` xóa đúng 12 dòng đó; `alembic check` sạch | Dữ liệu | BR-42 |
| UC-19-AC13 | Giao diện (360 px): chuyến `DANG_CHAY` có ô **gõ mã đơn** + nút **Lấy hàng**; điểm lấy của đơn `DA_GHEP` có nút **Không lấy được** (chọn lý do, chụp ảnh); thành công hiện "Đã lấy DH-… (n kiện)" và trạng thái điểm đổi ngay; lỗi tiếng Việt kèm mã BR; từ chối GPS vẫn gửi được, hiện cảnh báo thiếu GPS | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi:
- Test đã viết:
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc19_quet_lay.py`
- Lệch đặc tả: thêm migration nạp lý do (đã ghi "Đang chặn"); `api.md` ghi rõ UC-19 chỉ nhận `LAY`, `KHONG_LAY`.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-19-AC1 | API | | CHƯA KIỂM | |
| UC-19-AC2 | API | | CHƯA KIỂM | |
| UC-19-AC3 | API | | CHƯA KIỂM | |
| UC-19-AC4 | API | | CHƯA KIỂM | |
| UC-19-AC5 | API | | CHƯA KIỂM | |
| UC-19-AC6 | API | | CHƯA KIỂM | |
| UC-19-AC7 | API | | CHƯA KIỂM | |
| UC-19-AC8 | API | | CHƯA KIỂM | |
| UC-19-AC9 | API | | CHƯA KIỂM | |
| UC-19-AC10 | API | | CHƯA KIỂM | |
| UC-19-AC11 | API | | CHƯA KIỂM | |
| UC-19-AC12 | Dữ liệu | | CHƯA KIỂM | |
| UC-19-AC13 | UI | | CHƯA KIỂM | |
