# UC-25: Công nợ – xem nợ theo khách, đánh dấu đã thu

- **Trạng thái:** Đang làm (duyệt 09/11/2026, Kiệt: "đồng ý vậy làm đi" – 8 quyết định như đề xuất)
- **Tác nhân:** Kế toán (Quản lý xem)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-25, ưu tiên S; đặc tả rút gọn ở story này) · `docs/api.md` mục 2.6 (`/api/phai-thu`) · `docs/so-do.md` ERD (`PHAI_THU`, `PHIEU_THU`: "một lần đánh dấu đã thu") · `docs/security-rules.md` (bảng dữ liệu tiền: phải thu khóa khi `DA_THU`) · ca test `docs/ca-test-br.md` TC-BR56-02 · kịch bản `nghiep-vu.md` mục 11 bước 8 (Cty B nợ 2.240.000, đánh dấu đã thu cả hai đơn một lần)
- **Quy tắc nghiệp vụ liên quan:** BR-56 (đơn `DA_GIAO` sinh phải thu bằng cước – UC-20 đã làm; trạng thái thanh toán `CHUA_THU`/`DA_THU` là trường riêng, không đổi vòng đời đơn; Kế toán đánh dấu đã thu cho một hoặc nhiều đơn), BR-62 (nhật ký tiền), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-25-cong-no` tách từ `dev` (phải thu đã có từ UC-20). Chỉ trang Kế toán, không đụng trang tài xế.

## Mô tả ngắn
Giao xong mỗi đơn sinh một khoản phải thu bằng cước (UC-20). Kế toán xem tổng nợ theo từng khách, xem các khoản chưa thu; khi khách trả tiền thì chọn một hoặc nhiều khoản **của cùng một khách**, nhập ngày thu → hệ thống lập một **phiếu thu**, các khoản chuyển `DA_THU`. Trạng thái đơn vẫn là `DA_GIAO`.

## Đặc tả rút gọn
- **`GET /api/phai-thu`** (KT, QL): lọc `trang_thai_tt` (`CHUA_THU`/`DA_THU`), `khach_hang_id`; phân trang, đơn giao mới trước. Mỗi dòng: `id`, mã đơn, khách, ngày giao (lượt quét giao), `so_tien`, `trang_thai_tt`, `phieu_thu_id`, ngày thu. Kèm `tong_tien` của bộ lọc.
- **`GET /api/phai-thu/theo-khach`** (KT, QL) – **endpoint mới**: mỗi khách còn nợ một dòng `{khach_hang_id, ten_khach, so_khoan, tong_no}` (chỉ `CHUA_THU`), nợ nhiều trước.
- **`POST /api/phai-thu/da-thu`** (KT) `{phai_thu_ids, ngay}`:
  - `phai_thu_ids` 1–100 id, không trùng; `ngay` là ngày (không giờ), **không sau hôm nay** (giờ Việt Nam); trường lạ → 400.
  - Khóa các khoản `FOR UPDATE` theo id tăng dần. Có id không tồn tại → 404; có khoản đã `DA_THU` → **409 `BR-56`** (kèm danh sách), không đổi gì; các khoản **khác khách** → **422 `BR-56`**.
  - Lập `PHIEU_THU` (`khach_hang_id`, `tong_tien` = Σ, `ngay`, `nguoi_tao`); mỗi khoản → `DA_THU`, `phieu_thu_id`; mỗi khoản 1 dòng `NHAT_KY_TIEN` (`bang = phai_thu`, `hanh_dong = DA_THU`, cũ `CHUA_THU`, mới `DA_THU`, lý do "Phiếu thu #… ngày …"). Đơn giữ `DA_GIAO`. Một giao dịch.
  - Trả `{phieu_thu_id, khach_hang_id, tong_tien, ngay, so_khoan}`.
- **Giao diện Kế toán:** menu **Công nợ** (giữa "Chi phí cố định xe" và "Tạm ứng", theo chữ cái): bảng **nợ theo khách**; chọn khách → bảng khoản chưa thu có ô tích, dòng tổng đã chọn; ô **Ngày thu** (mặc định hôm nay) → **Đánh dấu đã thu** (hỏi xác nhận "Đã thu … đ của [khách]?"); lọc xem các khoản đã thu kèm số phiếu, ngày thu.

## Quyết định (Kiệt duyệt 09/11/2026)
1. **Module mới `backend/app/modules/tien/cong_no/`**, cạnh `tam_ung/`; không đổi CSDL (`PHAI_THU`, `PHIEU_THU` có từ migration đầu), không thêm gói.
2. **Một phiếu thu chỉ cho một khách:** bảng `PHIEU_THU` có `khach_hang_id`, nên chọn khoản của nhiều khách → 422 `BR-56`. Giao diện chỉ cho chọn sau khi chọn khách nên ít khi gặp.
3. **Thêm `GET /api/phai-thu/theo-khach`** cho bảng nợ theo khách ("tổng nợ theo khách" trong `api.md`), tách khỏi danh sách khoản cho đơn giản.
4. **Ngày thu không được sau hôm nay**, được trước (khách trả từ hôm trước, Kế toán nhập muộn); không ràng buộc với ngày giao.
5. **Không có "bỏ đánh dấu đã thu"**: `security-rules` khóa khoản `DA_THU`. Nhầm thì để hướng phát triển (phiếu điều chỉnh); ghi vào phần ngoài phạm vi.
6. **Đã thu một phần trong lô → cả lô 409**, không thu dở dang (tránh hai Kế toán cùng đánh dấu, lô sau thu trùng).
7. **Nhật ký tiền mỗi khoản một dòng** `DA_THU` (giá trị chuỗi mới cho `hanh_dong`, không cần migration), lý do ghi số phiếu và ngày thu.
8. **Ngoài phạm vi:** thu một phần số tiền của một khoản, COD, bỏ đánh dấu, in phiếu thu, báo cáo tuổi nợ (`nghiep-vu.md` mục bỏ / hướng phát triển).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-25-AC1 | Cty B có Đ2 (1.440.000) và Đ4 (800.000) `DA_GIAO` `CHUA_THU`: đánh dấu đã thu cả hai **một lần**, ngày hôm nay → 200; cả hai `DA_THU`, cùng `phieu_thu_id`; phiếu thu `tong_tien` 2.240.000, đúng khách, người tạo là Kế toán; đơn vẫn `DA_GIAO` | API | BR-56 (TC-BR56-02) |
| UC-25-AC2 | Nhật ký tiền: lần đánh dấu trên tạo đúng 2 dòng `phai_thu` `DA_THU` (cũ `CHUA_THU`, mới `DA_THU`), có người làm, giờ máy chủ, lý do có số phiếu; dòng `TAO` của UC-20 không đổi | API | BR-62 |
| UC-25-AC3 | Đánh dấu một khoản lẻ được (1 id); trong lô có khoản đã `DA_THU` → 409 `BR-56`, không khoản nào đổi, không sinh phiếu | API | BR-56 |
| UC-25-AC4 | Lô có khoản của hai khách → 422 `BR-56`, không đổi gì | API | BR-56 |
| UC-25-AC5 | Dữ liệu sai → 400, không đổi gì: danh sách rỗng, 101 id, id trùng, id không phải số, `ngay` sai dạng hoặc có giờ, **ngày mai** (biên: hôm nay được, hôm qua được), trường lạ. Id không tồn tại → 404 | API | security-rules |
| UC-25-AC6 | Đồng thời: hai Kế toán cùng đánh dấu một khoản → đúng một lần 200, lần kia 409; chỉ một phiếu thu, một dòng nhật ký | API | BR-56, NFR-REL-02 |
| UC-25-AC7 | Danh sách: lọc `trang_thai_tt`, `khach_hang_id` đúng; `tong_tien` đúng theo bộ lọc; khoản đã thu có số phiếu, ngày thu; phân trang | API | BR-56 |
| UC-25-AC8 | Nợ theo khách: chỉ tính `CHUA_THU`; khách đã thu hết không còn dòng; số khoản, tổng nợ đúng; nợ nhiều trước | API | BR-56 |
| UC-25-AC9 | Phân quyền: Điều phối, Tài xế, Quản lý gọi đánh dấu đã thu → 403; Quản lý xem 2 API GET được; Điều phối, Tài xế xem → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-25-AC10 | Giao diện Kế toán: menu Công nợ; bảng nợ theo khách; chọn khách thấy khoản chưa thu, tích nhiều khoản thì hiện tổng; ngày thu mặc định hôm nay; đánh dấu có hỏi xác nhận; xong thì khoản biến khỏi danh sách chưa thu, nợ của khách giảm; lỗi hiện kèm mã BR | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (09/11, backend):
  - `backend/app/modules/tien/cong_no/` (mới): `service.py` (danh sách + `tong_tien`, nợ theo khách, đánh dấu đã thu: khóa các khoản `FOR UPDATE` theo id, lập phiếu thu, nhật ký mỗi khoản), `router.py` (3 endpoint, ghi: `KE_TOAN`; xem: `KE_TOAN`, `QUAN_LY`), `schemas.py` (`ngay` chỉ nhận chuỗi `YYYY-MM-DD`, id số nguyên chặt). `app/main.py` thêm router theo chữ cái.
  - Tài liệu: `api.md` 2.6 (thêm `GET /api/phai-thu/theo-khach`, ghi rõ body, mã lỗi).
- Không đổi CSDL, không thêm gói. Giá trị `DA_THU` mới trong cột chuỗi `nhat_ky_tien.hanh_dong`.
- Test đã viết: `tests/api/test_uc25_cong_no.py` (26 ca). Đã thử làm hỏng 4 quy tắc (cho thu trùng, cho nhiều khách một phiếu, bỏ khóa dòng, cho ngày tương lai) → mỗi lần có test đỏ, rồi trả lại code.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc25_cong_no.py`
- **Giao diện (AC10) chưa làm.**

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-25-AC1 | API | `test_uc25_ac1_thu_hai_khoan_mot_lan` | Đạt | 09/11/2026 |
| UC-25-AC2 | API | `test_uc25_ac2_nhat_ky` | Đạt | 09/11/2026 |
| UC-25-AC3 | API | `test_uc25_ac3_mot_khoan_va_da_thu` | Đạt | 09/11/2026 |
| UC-25-AC4 | API | `test_uc25_ac4_khac_khach` | Đạt | 09/11/2026 |
| UC-25-AC5 | API | `test_uc25_ac5_*` (11 ca, biên hôm nay / hôm qua / ngày mai, 100 / 101 id) | Đạt | 09/11/2026 |
| UC-25-AC6 | API | `test_uc25_ac6_dong_thoi` | Đạt | 09/11/2026 |
| UC-25-AC7 | API | `test_uc25_ac7_danh_sach` | Đạt | 09/11/2026 |
| UC-25-AC8 | API | `test_uc25_ac8_theo_khach` | Đạt | 09/11/2026 |
| UC-25-AC9 | API | `test_uc25_ac9_*` (8 ca) | Đạt | 09/11/2026 |
| UC-25-AC10 | UI | | CHƯA KIỂM | |
