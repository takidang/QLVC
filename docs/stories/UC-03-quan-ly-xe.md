# UC-03: Quản lý xe

- **Trạng thái:** Hoàn thành (24/10/2026)
- **Tác nhân:** Điều phối viên (Quản lý kế thừa); Kế toán: chi phí cố định tháng của xe
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-03, đặc tả rút gọn ở dưới) · `docs/api.md` mục 2.2 · ERD `docs/so-do.md` mục 5, 7 (XE, CHI_PHI_CO_DINH_XE)
- **Quy tắc nghiệp vụ liên quan:** BR-11 (trạng thái xe), BR-12, BR-13 (lưu hạn đăng kiểm, bảo hiểm; kiểm khi lập chuyến ở UC-11, 12), BR-14 (khối lượng toàn bộ), BR-60 (không xóa, chỉ `NGUNG`), BR-62 (nhật ký tiền), BR-57 (phân quyền)
- **Người làm:** Tài · **Vai trò mẫu:** UC-04 (Kiệt), UC-05, UC-06 chép theo khuôn này

## Mô tả ngắn
Điều phối viên thêm, xem, sửa xe và chuyển xe giữa `HOAT_DONG` / `NGUNG`. Xe lưu tải trọng, thể tích (dùng kiểm ghép đơn), khối lượng toàn bộ (xét hạng bằng lái), hạn đăng kiểm và bảo hiểm (kiểm khi lập chuyến), định mức lít/100 km và km đồng hồ. Kế toán nhập chi phí cố định hằng tháng của xe, dùng cho lãi theo xe (UC-26).

## Đặc tả rút gọn
- **Thêm xe:** biển số, tải trọng (kg), thể tích (m³), khối lượng toàn bộ theo thiết kế (kg), hạn đăng kiểm, hạn bảo hiểm, định mức lít/100 km (không bắt buộc), km đồng hồ ban đầu. Xe mới ở `HOAT_DONG`.
- **Danh sách:** lọc theo trạng thái, tìm theo biển số, phân trang `?trang&so_dong` → `{du_lieu, tong}` (quy ước `api.md` mục 1).
- **Sửa:** mọi trường trừ km đồng hồ (km chỉ đổi qua bắt đầu/kết thúc chuyến, BR-70). Đổi trạng thái `HOAT_DONG` ↔ `NGUNG` (BR-11; xe đi bảo dưỡng thì `NGUNG` tạm).
- **Không có xóa** (BR-60, `api.md` mục 1).
- **Chi phí cố định tháng:** Kế toán nhập/sửa số tiền cho một xe, một tháng `YYYY-MM`; mỗi lần ghi `NHAT_KY_TIEN` (BR-62).
- Hạn giấy tờ chỉ lưu ở đây; chặn chạy xe hết hạn là việc của UC-11, 12 (BR-12, 13); cảnh báo sắp hết hạn là UC-27 (BR-21).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-03-AC1 | Thêm xe hợp lệ → 201, xe ở `HOAT_DONG`; biển số được chuẩn hóa (bỏ khoảng trắng đầu cuối, viết hoa): " 51c-111.11 " lưu thành "51C-111.11" | API | — |
| UC-03-AC2 | Dữ liệu sai → 400 và không lưu: tải trọng, khối lượng toàn bộ ≤ 0 (biên: 0 bị từ chối, 1 được); thể tích ≤ 0 (biên: 0 từ chối, 0.01 được); km đồng hồ < 0 (biên: 0 được); định mức lít < 0; thiếu biển số, thiếu hạn đăng kiểm hoặc bảo hiểm | API | — |
| UC-03-AC3 | Khối lượng toàn bộ phải ≥ tải trọng (khối lượng toàn bộ gồm cả xe và hàng – chốt 24/10): bằng nhau được, nhỏ hơn 1 kg → 422, kiểm cả khi thêm và khi sửa một trong hai số | Logic | BR-14 |
| UC-03-AC4 | Biển số trùng (kể cả khác hoa thường, khoảng trắng) → 409, xe cũ không đổi; hai yêu cầu thêm cùng biển số đồng thời chỉ một thành công (ràng buộc unique ở CSDL) | API | — |
| UC-03-AC5 | Danh sách: lọc `trang_thai`, tìm theo một phần biển số, phân trang trả đúng `tong`; trang ngoài phạm vi trả `du_lieu` rỗng | API | — |
| UC-03-AC6 | Sửa xe → 200 và lưu; gửi `km_dong_ho` trong yêu cầu sửa → 400, km không đổi (km chỉ nhập lúc tạo, sau đó đổi qua chuyến – chốt 24/10); sửa biển số thành biển số đã có → 409 | API | BR-70 |
| UC-03-AC7 | Đổi trạng thái `HOAT_DONG` → `NGUNG` → `HOAT_DONG` được; giá trị trạng thái khác → 400; không có endpoint xóa (DELETE `/api/xe/{id}` → 405) | API | BR-11, BR-60 |
| UC-03-AC8 | Phân quyền: Điều phối và Quản lý thêm/sửa được; Kế toán chỉ xem danh sách và chi tiết (GET 200, POST/PATCH 403 – chốt 24/10, để chọn xe khi nhập chi phí cố định); Tài xế mọi thao tác → 403; chưa đăng nhập → 401; xe không tồn tại → 404 | API | BR-57 |
| UC-03-AC9 | Chi phí cố định: Kế toán `PUT` lần đầu tạo, lần sau sửa; tháng sai định dạng (`2026-13`, `2026-1`, `10-2026`) → 400; số tiền âm → 400, bằng 0 được; Điều phối, Quản lý, Tài xế → 403 (chỉ Kế toán sửa – chốt 24/10) | API | — |
| UC-03-AC10 | Mỗi lần tạo/sửa chi phí cố định ghi một dòng `NHAT_KY_TIEN`: người làm, giá trị cũ (rỗng khi tạo), giá trị mới; sửa cùng số tiền cũ thì không ghi | API | BR-62 |
| UC-03-AC11 | Giao diện Điều phối: danh sách xe (biển số, tải trọng, thể tích, hạn đăng kiểm, hạn bảo hiểm, trạng thái), ô tìm biển số, lọc trạng thái; form thêm/sửa báo lỗi tiếng Việt từng trường; nút Ngừng / Hoạt động lại; hạn đã qua tô đỏ | UI | NFR-USA-02 |
| UC-03-AC12 | Giao diện Kế toán: chọn xe, chọn tháng, nhập chi phí cố định, lưu và thấy số đã lưu | UI | — |
| UC-03-AC13 | Tài liệu `docs/mau-use-case.md`: các bước và các file cần tạo cho một UC danh mục (model đã có → schema → service → router → test → trang giao diện), lấy UC-03 làm ví dụ, để Kiệt làm UC-04 | Dữ liệu | — |

## Ghi chú triển khai
- File đã đổi: `backend/app/domain/xe_tai_xe.py`, `backend/app/phan_trang.py`, `backend/app/modules/danh_muc/xe/{schemas,service,router}.py`, `backend/app/main.py`; `frontend/src/api/{goi,auth,xe}.ts`, `frontend/src/pages/dieu-phoi/XeDanhSach.tsx`, `frontend/src/pages/ke-toan/ChiPhiCoDinh.tsx`, `frontend/src/App.tsx` (menu, trang con theo vai trò), `frontend/src/index.css`; `docs/mau-use-case.md` (mới), `docs/api.md`, `docs/kien-truc.md` mục 4.
- Test đã viết: `backend/tests/unit/test_uc03_domain.py` (AC3), `backend/tests/api/test_uc03_xe.py` (AC1–AC10, 37 ca); fixture `dang_nhap_voi` trong `tests/conftest.py` dùng chung. Toàn bộ **68 passed** (24/10).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest` (Docker Desktop đang chạy).
- Lệch đặc tả: 4 quyết định chốt 24/10 (khối lượng toàn bộ ≥ tải trọng; km chỉ nhập lúc tạo; Kế toán xem xe; chỉ Kế toán sửa chi phí cố định) – đã sửa `api.md`. Thêm cấu trúc thư mục con mỗi danh mục – đã sửa `kien-truc.md`.
- AC11, AC12 thử tay 24/10 (Tài, Edge/Chrome): thêm xe chuẩn hóa biển số, hạn đã qua tô đỏ, báo lỗi khối lượng và biển số trùng, tìm/lọc/ngừng, Kế toán lưu chi phí cố định. Sau khi chụp ảnh sửa thêm: biển số không xuống dòng; lỗi biển số trùng và BR-14 hiện ngay dưới ô.
- Tài khoản thử `ketoan` (Kế toán) tạo tay trong DB dev, không có trong repo; UC-02 sẽ thay.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-03-AC1 | API | `test_uc03_ac1_them_xe_hop_le` | Đạt | 24/10/2026 |
| UC-03-AC2 | API | `test_uc03_ac2_* (12 ca)` | Đạt | 24/10/2026 |
| UC-03-AC3 | Logic | `test_uc03_ac3_* (unit 2 ca + API)` | Đạt | 24/10/2026 |
| UC-03-AC4 | API | `test_uc03_ac4_* (2 ca)` | Đạt | 24/10/2026 |
| UC-03-AC5 | API | `test_uc03_ac5_* (2 ca)` | Đạt | 24/10/2026 |
| UC-03-AC6 | API | `test_uc03_ac6_sua_xe` | Đạt | 24/10/2026 |
| UC-03-AC7 | API | `test_uc03_ac7_doi_trang_thai_va_khong_xoa` | Đạt | 24/10/2026 |
| UC-03-AC8 | API | `test_uc03_ac8_* (5 ca)` | Đạt | 24/10/2026 |
| UC-03-AC9 | API | `test_uc03_ac9_* (9 ca)` | Đạt | 24/10/2026 |
| UC-03-AC10 | API | `test_uc03_ac9_ac10_ke_toan_nhap_chi_phi_co_dinh` | Đạt | 24/10/2026 |
| UC-03-AC11 | UI | `docs/test-evidence/UC-03/ac11-*.png` (4 ảnh) + Tài xác nhận | Đạt | 24/10/2026 |
| UC-03-AC12 | UI | `docs/test-evidence/UC-03/ac12-chi-phi-co-dinh.png` + Tài xác nhận | Đạt | 24/10/2026 |
| UC-03-AC13 | Dữ liệu | `docs/mau-use-case.md` | Đạt | 24/10/2026 |
