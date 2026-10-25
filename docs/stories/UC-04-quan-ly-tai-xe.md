# UC-04: Quản lý tài xế

- **Trạng thái:** Hoàn thành (25/10/2026) · duyệt 25/10/2026, Kiệt
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán: chỉ xem
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-04, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2.2 · ERD `docs/so-do.md` mục 5 (TAI_XE, NGUOI_DUNG) · khuôn `docs/mau-use-case.md`
- **Quy tắc nghiệp vụ liên quan:** BR-14 (hạng GPLX theo khối lượng toàn bộ), BR-15 (hạn GPLX), BR-60 (không xóa, chỉ `NGUNG`), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Khuôn:** UC-03 Quản lý xe

## Mô tả ngắn
Điều phối viên thêm, xem, sửa tài xế và chuyển tài xế giữa `HOAT_DONG` / `NGUNG`. Thêm tài xế là tạo luôn tài khoản đăng nhập vai trò `TAI_XE` trong cùng một giao dịch. Tài xế lưu số, hạng, hạn GPLX để UC-11, 12 kiểm BR-14, 15 khi lập chuyến; ngừng tài xế thì khóa luôn tài khoản.

## Đặc tả rút gọn
- **Thêm tài xế** (`POST /api/tai-xe`): tên đăng nhập, họ tên, mật khẩu ban đầu (≥ 8 ký tự, băm bằng `bam_mat_khau`), số GPLX, hạng GPLX (`B` / `C1` / `C`), hạn GPLX, SĐT. Tạo `NGUOI_DUNG` (vai trò `TAI_XE`) và `TAI_XE` trong **một giao dịch**; lỗi ở bất kỳ bước nào thì không tạo gì. Tài xế mới ở `HOAT_DONG`.
- **Danh sách:** lọc theo trạng thái, tìm theo họ tên / số GPLX / SĐT, phân trang `?trang&so_dong` → `{du_lieu, tong}`.
- **Sửa** (`PATCH /api/tai-xe/{id}`): họ tên, số GPLX, hạng, hạn GPLX, SĐT, trạng thái. Không sửa tên đăng nhập, mật khẩu ở đây (để UC-02).
- **Ngừng / hoạt động lại** (BR-60): tài xế `NGUNG` thì tài khoản `NGUNG` theo (mất quyền ngay, như UC-01-AC7); hoạt động lại thì mở lại tài khoản. Không có xóa.
- **Chỉ lưu**, không chặn: hạn GPLX đã qua vẫn lưu được (dữ liệu thật), giao diện tô đỏ. Chặn tài xế sai hạng hoặc hết hạn là việc của UC-11, 12 (Tài); UC-04 viết sẵn hàm domain BR-14 để UC-11 dùng.
- Kết quả trả về **không bao giờ** có mật khẩu hay mật khẩu băm.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-04-AC1 | Thêm tài xế hợp lệ → 201: tài xế ở `HOAT_DONG`, có tài khoản vai trò `TAI_XE`, đăng nhập được bằng tên và mật khẩu vừa đặt; kết quả trả về không có `mat_khau` / `mat_khau_bam`; SĐT chuẩn hóa theo `SoDienThoai`, số GPLX bỏ khoảng trắng đầu cuối, viết hoa | API | — |
| UC-04-AC2 | Dữ liệu sai → 400 và không lưu gì: mật khẩu 7 ký tự bị từ chối, 8 ký tự được (biên); hạng GPLX ngoài `B` / `C1` / `C` sau khi chuẩn hóa (ví dụ `D`, `A1`; xem câu hỏi 2); thiếu họ tên, tên đăng nhập, số GPLX, hạn GPLX; SĐT sai định dạng | API | — |
| UC-04-AC3 | Trùng → 409 và **không tạo gì**: tên đăng nhập đã có (kể cả tài khoản không phải tài xế); số GPLX đã có (kể cả khác hoa thường, khoảng trắng) – kiểm tài khoản `NGUOI_DUNG` cũng không bị tạo thừa (một giao dịch). Hai yêu cầu cùng số GPLX đồng thời chỉ một thành công (unique ở CSDL) | API | — |
| UC-04-AC4 | Hàm domain `kiem_br14_hang_gplx(hang, ktt_toan_bo_kg)`: ≤ 3.500 kg cần B trở lên; > 3.500–7.500 kg cần C1 trở lên; > 7.500 kg cần C; thứ bậc C ⊇ C1 ⊇ B. Ca biên: 3.500 với B đạt, 3.501 với B → `LoiNghiepVu("BR-14")`, 3.501 với C1 đạt, 7.500 với C1 đạt, 7.501 với C1 bị chặn, 7.501 với C đạt; C lái được mọi mức | Logic | BR-14 |
| UC-04-AC5 | Hạn GPLX đã qua vẫn lưu được (201/200); danh sách trả kèm hạn để giao diện tô đỏ. Không chặn ở UC-04 (BR-15 kiểm ở UC-11, 12) | API | BR-15 |
| UC-04-AC6 | Danh sách: lọc `trang_thai`; tìm theo một phần họ tên, số GPLX hoặc SĐT (ký tự `%`, `_` không làm lệch kết quả); phân trang trả đúng `tong`; trang ngoài phạm vi trả `du_lieu` rỗng | API | — |
| UC-04-AC7 | Sửa → 200 và lưu (họ tên đổi trên tài khoản, các trường GPLX, SĐT đổi trên tài xế); gửi `ten_dang_nhap` hoặc `mat_khau` trong yêu cầu sửa → 400; gửi `null` cho trường bắt buộc → 400; sửa số GPLX thành số đã có → 409 | API | — |
| UC-04-AC8 | Ngừng tài xế → tài khoản `NGUNG`, token đang dùng của tài xế đó bị từ chối ngay (401) và không đăng nhập lại được; hoạt động lại → tài khoản `HOAT_DONG`, đăng nhập lại được; trạng thái khác → 400; không có endpoint xóa (DELETE `/api/tai-xe/{id}` → 405) | API | BR-60 |
| UC-04-AC9 | Phân quyền: Điều phối và Quản lý thêm/sửa được; Kế toán chỉ xem danh sách và chi tiết (GET 200, POST/PATCH 403); Tài xế mọi thao tác → 403; chưa đăng nhập → 401; tài xế không tồn tại → 404 | API | BR-57 |
| UC-04-AC10 | Giao diện Điều phối (menu "Tài xế"): danh sách (họ tên, tên đăng nhập, số GPLX, hạng, hạn GPLX, SĐT, trạng thái), ô tìm, lọc trạng thái; form thêm (có mật khẩu ban đầu) / sửa (không có tên đăng nhập, mật khẩu) báo lỗi tiếng Việt từng trường; nút Ngừng / Hoạt động lại; hạn GPLX đã qua tô đỏ | UI | NFR-USA-02 |

## Quyết định đã chốt (25/10/2026, Kiệt)
1. **Định dạng số GPLX:** 6–20 ký tự chữ/số, chuẩn hóa viết hoa, bỏ khoảng trắng (không ép đúng 12 số của mẫu GPLX mới, để nhập được bằng cũ).
2. **Hạng GPLX gõ thường** (`c1`): tự chuyển thành `C1`; giá trị khác `B` / `C1` / `C` sau chuẩn hóa → 400.
3. **Ngừng tài xế đang có chuyến chưa chạy:** UC-04 vẫn cho ngừng; UC-11, 12 lọc bỏ tài xế `NGUNG` khi lập/đổi chuyến (cần Tài biết khi làm UC-11, 12).
4. **Đổi mật khẩu, đổi tên đăng nhập:** để UC-02 Người dùng, không làm ở UC-04.
5. **Ngừng tài xế khóa luôn tài khoản** (theo yêu cầu của Tài trong `TIEN-DO.md`): tài xế nghỉ việc/đình chỉ không được xem chuyến, quét mã, khai chi phí; hoạt động lại thì mở lại tài khoản, lịch sử giữ nguyên.

## Ghi chú triển khai
- AC10 thử tay 25/10 (Kiệt, Edge/Chrome, `http://localhost:5173`): 9 ca trong `du-lieu-test.md` đạt hết. Ảnh `5-tai-xe-bi-khoa-tk.png` chụp trùng ảnh ngừng; bằng chứng khóa tài khoản lấy từ log backend.
- File đã đổi: `backend/app/domain/xe_tai_xe.py` (thêm `hang_gplx_toi_thieu`, `kiem_br14_hang_gplx`), `backend/app/modules/danh_muc/tai_xe/{schemas,service,router}.py` (mới), `backend/app/main.py` (gắn router); `frontend/src/api/taiXe.ts` (mới), `frontend/src/pages/dieu-phoi/TaiXeDanhSach.tsx` (mới), `frontend/src/App.tsx` (menu "Tài xế"). Không đụng `models/`, không thêm migration.
- Test đã viết: `backend/tests/unit/test_uc04_domain.py` (AC4, 16 ca), `backend/tests/api/test_uc04_tai_xe.py` (AC1–AC3, AC5–AC9, 51 ca). UC-04: **67 passed**; toàn bộ backend **266 passed** (25/10). `ruff check`, `ruff format --check`, `npm run lint`, `npm run build` sạch.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/unit/test_uc04_domain.py tests/api/test_uc04_tai_xe.py` (Docker Desktop đang chạy)
- Cách làm đáng chú ý: thêm tài xế `flush` tài khoản trước để lấy id, rồi commit cả hai; trùng số GPLX thì rollback cả giao dịch nên không để lại tài khoản thừa. Phân biệt trùng tên đăng nhập / số GPLX theo tên ràng buộc unique của PostgreSQL. Ngừng tài xế khóa tài khoản qua `nguoi_dung.trang_thai`; `nguoi_dung_hien_tai` (UC-01) đã chặn tài khoản khác `HOAT_DONG` nên token cũ mất hiệu lực ngay. Giao diện hỏi xác nhận trước khi ngừng.
- Review `ponytail-review` 25/10: Ship, 2 mục nhỏ đã sửa – `_luu` chỉ xử lý trùng số GPLX (bỏ nhánh báo "trùng tên đăng nhập" không bao giờ chạy tới); tìm SĐT có dấu cách/chấm/gạch ("0909 111") vẫn ra, gõ riêng "." không khớp mọi SĐT (thêm test `test_uc04_ac6_tim_sdt_co_dau_cach_hoac_cham`).
- Lệch đặc tả: không. `api.md` mục 2.2 đã có `/api/tai-xe` đúng như làm.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-04-AC1 | API | `test_uc04_ac1_* (2 ca)` | Đạt | 25/10/2026 |
| UC-04-AC2 | API | `test_uc04_ac2_* (23 ca)` | Đạt | 25/10/2026 |
| UC-04-AC3 | API | `test_uc04_ac3_* (4 ca)` | Đạt | 25/10/2026 |
| UC-04-AC4 | Logic | `tests/unit/test_uc04_domain.py` (16 ca) | Đạt | 25/10/2026 |
| UC-04-AC5 | API | `test_uc04_ac5_han_gplx_da_qua_van_luu` | Đạt | 25/10/2026 |
| UC-04-AC6 | API | `test_uc04_ac6_* (3 ca)` | Đạt | 25/10/2026 |
| UC-04-AC7 | API | `test_uc04_ac7_* (11 ca)` | Đạt | 25/10/2026 |
| UC-04-AC8 | API | `test_uc04_ac8_* (2 ca)` | Đạt | 25/10/2026 |
| UC-04-AC9 | API | `test_uc04_ac9_* (5 ca)` | Đạt | 25/10/2026 |
| UC-04-AC10 | UI | `docs/test-evidence/UC-04/` (6 ảnh: thêm, trùng GPLX báo dưới ô, hạn hết tô đỏ, ngừng, form sửa) + Kiệt xác nhận; khóa tài khoản xác nhận qua log (đăng nhập tài xế ngừng → 403 "Tài khoản đã bị khóa") | Đạt | 25/10/2026 |
