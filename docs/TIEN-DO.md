# Tiến độ đồ án – Nhóm 8

> Mỗi người CHỈ sửa phần của mình. Mục chung chỉ thêm dòng, không sửa dòng người khác.
> Chi tiết từng UC: `docs/stories/`. Cập nhật sau mỗi `story done` hoặc cuối buổi, commit cùng code.
> Trạng thái: Chưa bắt đầu | Đang làm | Chờ review | Xong

## Mốc chung
| Mốc | Hạn | Trạng thái |
|---|---|---|
| Nền móng: models, migration, đăng nhập, khung frontend | 18/10 | Xong 16/10 |
| UC-03 mẫu + docs/mau-use-case.md | 25/10 | Xong 24/10 |
| Vòng tối thiểu: tạo đơn → ghép → chốt → quét → giao | 08/11 | Chưa bắt đầu |
| Quyết toán chạy được | 29/11 | Chưa bắt đầu |
| UC-30 dự đoán trễ (phần AI) | 06/12 | Chưa bắt đầu |
| Nộp LMS | 21–27/12 | |

## Đang chặn / cần người kia
<!-- Ngày – Ai cần gì từ ai. Xong thì gạch ~~...~~ -->
- ~~10/10 – Kiệt phân tích lại nghiệp vụ trên nhánh `kiet/nghiep-vu` (sửa `nghiep-vu.md`, `use-cases.md`, `so-do.md`), xong mở PR vào `main` để Tài review. Trong lúc chờ: không sửa ba file đó trên `main`; Tài làm UC-01 trước, models theo ERD chờ PR merge.~~ Xong 16/10: PR #1 đã merge, nghiệp vụ 0.5 lên `main`.
- ~~15/10 – Kiệt cần Tài review PR nghiệp vụ 0.5 (`kiet/nghiep-vu` → `main`), chốt ai làm UC-32, 33, 34 (UC-14, 31 của Tài đã bỏ), và sửa endpoint `api.md` theo danh sách trong PR.~~ Xong 16/10: đã review, Kiệt làm UC-33, 34; Tài làm UC-32.
- 16/10 – Tài → Kiệt: nghiệp vụ 0.5 đã merge. Việc tuần 1 của Kiệt có hướng dẫn: cài môi trường `docs/cai-moi-truong.md`, ca test BR `docs/ca-test-br.md` (khung + ví dụ + BR còn thiếu ca), UML `docs/uml/README.md`.
- ~~16/10 – Tài đang tạo **toàn bộ models theo ERD 0.5 + migration đầu tiên** (`backend/app/models/`, `backend/alembic/`). Kiệt chưa sửa hai thư mục này tới khi dòng này được gạch; cần thêm cột/bảng thì nhắn Tài.~~ Xong 16/10: 24 bảng + migration đầu đã lên `main`. Sửa models thì tạo migration mới (`alembic revision --autogenerate`), CI chạy `alembic check`.
- 24/10 – Tài → Kiệt: UC-03 xong, làm UC-04 theo `docs/mau-use-case.md` (chép cấu trúc `backend/app/modules/danh_muc/xe/`, fixture `dang_nhap_voi`, trang `XeDanhSach.tsx`). Tuần 2 Kiệt chưa có commit nào: nhắn Tài nếu vướng cài môi trường.
- ~~24/10 – Tài đang sửa `backend/app/models/danh_muc.py` (bảng giá) và thêm migration thứ 2 (UC-07: unique cặp tỉnh + ngày hiệu lực, nạp CFG mặc định). Kiệt chưa thêm migration tới khi dòng này được gạch.~~ Xong 24/10: migration `177fdcb334df`. Kiệt `git pull` rồi `alembic upgrade head`.
- 24/10 – **Tài nhận UC-05 Tuyến và nút** (trước là của Kiệt) vì UC-05 chặn giao diện tạo đơn và toàn bộ phần chuyến. Kiệt **không làm UC-05**; Kiệt sửa dòng "UC-02, 05 + Quét tối thiểu" trong phần mình thành "UC-02 + Quét tối thiểu". Kiệt vẫn làm UC-04 Tài xế (UC-11 cần tài xế).
- 24/10 – Tài → Kiệt: trên `main` đã có UC-01, 03, 06, 07 xong và UC-08 backend (167 test). Kiệt `git pull`, `alembic upgrade head` (có migration mới), đọc `docs/mau-use-case.md` (đã thêm lưu ý `app/kieu.py`, giờ Việt Nam) rồi làm **UC-04 Tài xế** – UC-11 Lập chuyến đang chờ UC-04.
- 24/10 – Tài → Kiệt: **thử giao diện UC-05 và UC-08** thay Tài (bước 3 trong khối "Việc của Kiệt ngay bây giờ"). Code đã xong, chờ Kiệt chụp ảnh và xác nhận để đóng 2 story.

## Câu hỏi chờ thầy
- ~~A1–A6 (nghiep-vu.md mục 1): chưa gửi~~ Nhóm tự chốt 16/10 (nghiep-vu.md mục 1).
- ~~A7 (tuyến ≤ 10 giờ), A8 (góc nhìn chủ xe): chưa gửi~~ Nhóm tự chốt 16/10.

## Tài
| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Nền móng (gồm UC-01 Đăng nhập) | 1 | Xong | 12/12 | |
| UC-03 Xe (mẫu) | 2 | Xong | 13/13 | |
| UC-06…09 Đơn tối thiểu | 3–4 | Chờ thử giao diện | UC-06 6/6, UC-07 9/9, UC-08 10/11 | UC-08-AC11 giao diện đã làm, Kiệt thử; UC-09 bỏ ở 0.5 |
| UC-05 Tuyến và nút (nhận từ Kiệt 24/10) | 3 | Chờ thử giao diện | 8/9 | AC9 giao diện: Kiệt thử |
| UC-11…13, 15 Chuyến tối thiểu | 3–4 | Chưa bắt đầu | | |
| UC-10, 16, 22, 32 (theo dõi chuyến) + làm dày UC-13, 15 | 5–6 | Chưa bắt đầu | | |
| UC-28, triển khai demo | 7 | Chưa bắt đầu | | |
| UC-30 AI | 8 | Chưa bắt đầu | | |

### Nhật ký Tài (mới nhất ở trên)
- 24/10: UC-05 Tuyến và nút xong backend + giao diện (199 test); giao diện tạo đơn UC-08. Giao Kiệt thử giao diện UC-05, UC-08.
- 24/10: Review UC-06, 07, 08: sửa chuẩn hóa Unicode NFC cho chữ tiếng Việt, giới hạn vĩ độ/kinh độ (167 test).
- 24/10: UC-08 Tạo đơn backend: tính cước theo kịch bản mục 11, chốt cước, mã đơn ngẫu nhiên (10/11 AC, 164 test). Nhận UC-05 từ Kiệt.
- 24/10: UC-06 Khách hàng (6/6 AC) và UC-07 Bảng giá + cấu hình (9/9 AC) hoàn thành; 123 test đạt. Làm trước việc tuần 3 vì Kiệt chưa có UC-04, 05.
- 24/10: Review UC-03, sửa 3 mục frontend (ngày theo giờ máy, bỏ kết quả về muộn, xóa lỗi cũ).
- 24/10: UC-03 Quản lý xe hoàn thành (13/13 AC, 68 test đạt, thử giao diện đạt); viết docs/mau-use-case.md cho UC-04…06.
- 16/10: Review UC-01, sửa 3 mục (lỗi 400 lộ mật khẩu, test token chập chờn, đăng xuất khi mất mạng).
- 16/10: UC-01 hoàn thành: 30 test đạt, CI xanh, thử giao diện đạt 4 bước. Nền móng xong trước hạn 18/10.
- 16/10: Cài Docker, PostgreSQL. Models theo ERD 0.5 + migration đầu. UC-01: story duyệt, code backend + frontend + test (unit đạt, API chưa chạy). Chốt A1–A8; hướng dẫn cài môi trường, ca test BR, UML cho Kiệt.
- 16/10: Review và merge PR #1 nghiệp vụ 0.5 của Kiệt (sửa thêm cước Đ8, quy ước thứ tự route). Nhận UC-32; bỏ UC-14, 31.
- 10/10: Chốt nghiệp vụ 0.4, sơ đồ, kiến trúc, API; dựng khung repo, CI xanh lần đầu.

## Kiệt

> **Việc của Kiệt ngay bây giờ** (Tài ghi hộ 24/10 theo yêu cầu của Tài; Kiệt đọc xong thì tự sửa, xóa khối này khi xong). Claude của Kiệt: đọc khối này đầu phiên và báo Kiệt bước tiếp theo.
>
> 1. **Chuẩn bị:** `git switch main` → `git pull` → mở Docker Desktop → `docker compose up -d db` → trong `backend`: `.venv\Scripts\pip install -r requirements-dev.txt` rồi `.venv\Scriptslembic upgrade head` (có migration mới `177fdcb334df`). Chưa cài môi trường thì theo `docs/cai-moi-truong.md`. Xong: `pytest` phải ra **167 passed**.
> 2. **UC-04 Tài xế** (ưu tiên số 1 – UC-11 Lập chuyến của Tài đang chờ): `story new UC-04`, làm theo `docs/mau-use-case.md`, chép khuôn `backend/app/modules/danh_muc/xe/` thành `tai_xe/`. Những điểm UC-04 phải có (để viết AC):
>    - Bảng `TAI_XE` đã có trong `backend/app/models/danh_muc.py`: `nguoi_dung_id` (unique), `so_gplx` (unique), `hang_gplx` (`B`/`C1`/`C`), `han_gplx`, `sdt`, `trang_thai`.
>    - `POST /api/tai-xe` **tạo kèm tài khoản** người dùng vai trò `TAI_XE` (`api.md` mục 2.2): nhận tên đăng nhập, họ tên, mật khẩu ban đầu (≥ 8 ký tự, băm bằng `bam_mat_khau` trong `app/auth/bao_mat.py`), cùng thông tin bằng lái – tạo cả hai trong **một giao dịch**.
>    - Lưu đúng dữ liệu cho BR-14 (hạng bằng) và BR-15 (hạn bằng); việc **chặn** tài xế sai hạng/hết hạn là của UC-11, 12 (Tài làm) – nhưng nên viết sẵn hàm domain `kiem_br14_hang_gplx(hang, ktt_toan_bo_kg)` trong `backend/app/domain/xe_tai_xe.py` (cạnh `kiem_br14_khoi_luong_toan_bo`) kèm test: ≤ 3.500 kg cần B trở lên, > 3.500–7.500 kg cần C1 trở lên, > 7.500 kg cần C; thứ bậc C ⊇ C1 ⊇ B.
>    - BR-60: không xóa, chỉ `NGUNG`; ngừng tài xế thì khóa luôn tài khoản đăng nhập (`nguoi_dung.trang_thai = NGUNG`, UC-01-AC7 làm tài khoản mất quyền ngay).
>    - SĐT dùng kiểu `SoDienThoai`, chữ dùng `ChuBatBuoc` trong `backend/app/kieu.py`. Số GPLX trùng → 409.
>    - Phân quyền như UC-03: Điều phối, Quản lý thêm/sửa; Kế toán xem (để cấp tạm ứng theo tài xế); Tài xế 403.
>    - Giao diện: trang "Tài xế" cho Điều phối, chép từ `frontend/src/pages/dieu-phoi/XeDanhSach.tsx`, thêm một dòng vào `TRANG_CON` trong `frontend/src/App.tsx`.
> 3. **Thử giao diện UC-05 và UC-08 thay Tài** (Tài giao 24/10; làm được ngay sau bước 1, không cần đợi UC-04). Backend đã xong, 199 test đạt; chỉ còn AC giao diện `UC-05-AC9`, `UC-08-AC11`. Dùng **Edge/Chrome**, không dùng trình duyệt trong VS Code.
>    - **Chuẩn bị (DB máy Kiệt đang trống):** chạy backend `cd backend; .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000` (không `--reload`) và frontend `cd frontend; npm run dev`; tạo tài khoản Quản lý `cd backend; .venv\Scripts\python -m app.tao_quan_ly`; đăng nhập `http://127.0.0.1:5173`. Vào **Bảng giá** thêm `TP.HCM → Cần Thơ`, 1.500 đ/kg, tối thiểu 50.000, hiệu lực 01/10/2026; vào **Khách hàng** thêm `Cty A`, SĐT `0909123456`.
>    - **UC-05 (menu Nút, Tuyến):** (a) thêm 5 nút loại Tỉnh/thành, tên = tỉnh: `TP.HCM`, `Long An`, `Tiền Giang`, `Vĩnh Long`, `Cần Thơ`; (b) thêm tuyến `T01` (dầu 550.000, cầu đường 200.000, bốc xếp 250.000, lương 600.000) với 5 nút: TP.HCM 0 phút/0 km, Long An 60/50, Tiền Giang 120/75 **tick điểm nghỉ**, Vĩnh Long 210/135, Cần Thơ 270/170 → bảng hiện lộ trình có "Tiền Giang (nghỉ)", 4 giờ 30 phút; (c) tuyến `T02` chỉ TP.HCM 0/0 và Cần Thơ 300/170, không tick nghỉ → khung vàng "thiếu điểm nghỉ (BR-20)" nhưng vẫn lưu; (d) tuyến có nút cuối 601 phút → bị chặn BR-66.
>    - **UC-08 (menu Đơn hàng):** (e) Tạo đơn: Cty A, 1.800 kg, 6 m³, nút lấy TP.HCM, nút giao Cần Thơ → khung vàng tự hiện **cước 2.997.000 đ**; nhập địa chỉ, SĐT, người nhận, hạn giao ngày mai → Lưu → hiện "Đã tạo đơn DH-XXXXXX"; (f) đơn có địa chỉ giao trùng địa chỉ lấy → báo lỗi BR-31; (g) chọn chiều ngược Cần Thơ → TP.HCM → báo "Chưa có bảng giá", nút Lưu bị khóa.
>    - **Ghi kết quả:** chụp ảnh (b), (c), (d), (e), (f) lưu vào `docs/test-evidence/UC-05/` và `docs/test-evidence/UC-08/`; điền dòng AC9/AC11 trong `docs/stories/UC-05-quan-ly-tuyen.md` và `docs/stories/UC-08-tao-don.md` (Đạt/Không đạt, ngày, "Kiệt thử"); bước nào sai thì ghi vào "Đang chặn" cho Tài, không tự sửa code của Tài. Commit, push.
> 4. **Sau đó:** danh sách ca test BR (`docs/ca-test-br.md`) và UML (`docs/uml/README.md`), rồi UC-02 Người dùng.
> 5. Không làm **UC-05** (Tài đã nhận). Đụng `backend/app/models/` hoặc thêm migration thì ghi vào "Đang chặn" và commit trước.

| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Phân tích lại nghiệp vụ 0.5 (nhánh `kiet/nghiep-vu`) | 1 | Xong | – | PR #1 merge 16/10 (Tài cập nhật hộ) |
| Cài môi trường, danh sách ca test BR, vẽ UML | 1 | Đang làm | – | Có Python 3.12; thiếu WSL 2, Docker Desktop, Node 24. Ca test BR và UML làm sau khi PR merge |
| UC-04 Tài xế (chép mẫu) | 2 | Chưa bắt đầu | | Trễ so với tuần 2; xem khối "Việc của Kiệt ngay bây giờ" |
| UC-02 + Quét tối thiểu (UC-17…20) | 3–4 | Chưa bắt đầu | | UC-05 chuyển cho Tài 24/10 (Tài cập nhật hộ) |
| Quét đầy đủ, UC-21, 23, 33 (báo sự cố) | 5–6 | Chưa bắt đầu | | |
| UC-24, 25 | 7 | Chưa bắt đầu | | |
| UC-26, 27, 34 (hiệu suất xe, ưu tiên S – thiếu giờ thì cắt trước), E2E | 8 | Chưa bắt đầu | | |

### Nhật ký Kiệt (mới nhất ở trên)
- 15/10: Sửa nghiệp vụ 0.5 theo review của Tài: công thức BR-73, km khi kết thúc do sự cố, thứ tự điểm lấy, kịch bản mỗi ca ✖ chỉ một BR (thêm Đ8 cho BR-67); thêm mục Công thức, ETA kế hoạch lưu lúc chốt, dữ liệu cho AI; api, security-rules, kien-truc khớp 0.5. Nhận UC-33, UC-34.
- 15/10: Nghiệp vụ 0.5: chuyến 6 trạng thái, đơn 7; ETA cộng phút dừng, kiểm lại cả chuyến khi ghép (BR-63…67); km, sự cố, kết thúc do sự cố, cảnh báo trễ (BR-68…73); bỏ UC-09, 14, 29, 31, thêm UC-32…34. Sửa nghiep-vu, use-cases, so-do; api, security-rules chỉ đổi tên trạng thái. Mở PR chờ Tài review.
