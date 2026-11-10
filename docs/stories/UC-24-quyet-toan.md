# UC-24: Quyết toán chuyến

- **Trạng thái:** Đã duyệt 10/11/2026 (Kiệt: "duyệt" – 9 quyết định như đề xuất)
- **Tác nhân:** Kế toán (Quản lý xem)
- **Đặc tả:** `docs/use-cases.md` UC-24 · `docs/api.md` mục 2.6 và 3.3 · `docs/so-do.md` mục 10 (sequence quyết toán) · `docs/nghiep-vu.md` mục 11 bước 7 (quyết toán C01) · `docs/security-rules.md` (bảng dữ liệu tiền: chi phí, quyết toán) · ca test `docs/ca-test-br.md` TC-BR29-02, TC-BR50-01/02, TC-BR51-01/02, TC-BR55-01…05
- **Quy tắc nghiệp vụ liên quan:** BR-29 (khóa sau quyết toán), BR-50 (doanh thu tính cho chuyến giao thành công), BR-51 (lãi chuyến), BR-55 (điều kiện quyết toán, chênh lệch tạm ứng), BR-62 (nhật ký tiền), BR-68 (lương nhập tay khi kết thúc do sự cố), BR-71 (định mức, lương đã chốt), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-24-quyet-toan` tách từ `dev` (UC-21 chi phí, UC-23 tạm ứng đã có).

## Mô tả ngắn
Chuyến `HOAN_THANH` hiện ra ở trang **Quyết toán** của Kế toán. Kế toán xem bảng quyết toán (doanh thu, chi theo loại so với định mức, dầu tham khảo, lương, tạm ứng, lãi), duyệt / điều chỉnh / từ chối từng khoản chi tài xế khai, nhập lương tay nếu chuyến kết thúc do sự cố, ghi cách xử lý chênh lệch tạm ứng rồi bấm **Quyết toán** → chuyến `DA_QUYET_TOAN`, mọi số tiền của chuyến chỉ đọc.

## Đặc tả rút gọn
- **`POST /api/chi-phi/{id}/duyet`** (KT) `{so_tien_duyet, ly_do?}`:
  - Chuyến phải `HOAN_THANH` (khác → 409 `BR-55`; `DA_QUYET_TOAN` → 409 `BR-29`). Khóa dòng chuyến `FOR SHARE` (như UC-21) để không chen với quyết toán.
  - `so_tien_duyet` số nguyên **1 … số khai** (lớn hơn số khai → 422 `BR-55`; ≤ 0 → 400). Khác số khai mà thiếu `ly_do` (1–300 ký tự) → 422 `BR-55`.
  - Khoản → `DA_DUYET`, `so_tien_duyet`, `nguoi_duyet`. Nhật ký `chi_phi / DUYET`, cũ "trạng thái + số", mới "DA_DUYET + số duyệt", lý do.
- **`POST /api/chi-phi/{id}/tu-choi`** (KT) `{ly_do}` bắt buộc → `TU_CHOI`, `so_tien_duyet = null`, nhật ký `TU_CHOI`. Điều kiện chuyến như duyệt.
- Duyệt và từ chối **làm lại được** (đổi quyết định) khi chuyến còn `HOAN_THANH`; quyết định giống hệt lần trước → 400 `KHONG_CO_THAY_DOI`. Tài xế không sửa được khoản đã có quyết định (UC-21 đã chặn).
- **`GET /api/chuyen/{id}/quyet-toan`** (KT, QL) – chuyến `HOAN_THANH` (bảng tạm tính) hoặc `DA_QUYET_TOAN` (số đã lưu); trạng thái khác → 409 `BR-55`:
  - thông tin chuyến: mã, xe, tài xế, tuyến, `ket_thuc_bat_thuong`, lý do kết thúc;
  - **doanh thu**: danh sách đơn giao thành công trên chuyến này (mã, khách, cước) và Σ (BR-50); danh sách đơn thất bại trên chuyến (cước bị mất, doanh thu 0);
  - **chi theo loại** Dầu / Cầu đường / Bốc xếp / Phát sinh: định mức đã chốt (Phát sinh = 0), thực tế đã duyệt, chênh lệch; dòng tổng;
  - **dầu tham khảo** (km kết thúc − km bắt đầu) × lít/100 km / 100 so với Σ lít các khoản dầu đã duyệt; thiếu km hoặc định mức lít thì `null`;
  - **khoản chi**: từng khoản (loại, số khai, số duyệt, số lít, ghi chú, trạng thái, id các ảnh); `so_cho_duyet`;
  - **lương**: đã chốt (BR-71); `can_luong_tay` = `ket_thuc_bat_thuong`;
  - **tạm ứng** Σ `HIEU_LUC`; **chênh lệch** = tạm ứng − chi đã duyệt (BR-55) và cách xử lý gợi ý theo dấu;
  - **lãi** = doanh thu − chi đã duyệt − lương (BR-51; khi cần lương tay mà chưa nhập thì tính với lương đã chốt, ghi chú rõ); **lãi dự kiến lúc chốt** = Σ cước mọi đơn trên chuyến − định mức − lương chốt; **lý do lệch**: đơn thất bại (−cước), loại chi vượt định mức (+phần vượt).
- **`POST /api/chuyen/{id}/quyet-toan`** (KT) theo `api.md` 3.3 `{xu_ly_chenh_lech, hinh_thuc, luc_xu_ly, luong_tay, ly_do_luong_tay}`, một giao dịch, khóa dòng chuyến `FOR UPDATE`:
  - không `HOAN_THANH` → 409 (`DA_QUYET_TOAN` → 409 `BR-29`, khác → 409 `BR-55`); còn khoản `CHO_DUYET` → 409 `BR-55` (kèm danh sách id);
  - `xu_ly_chenh_lech` phải khớp dấu: dương → `TAI_XE_DA_NOP`, âm → `CONG_TY_DA_TRA`, bằng 0 → `KHONG_CHENH`; sai hoặc thiếu → 422 `BR-55`;
  - chênh lệch ≠ 0: bắt buộc `hinh_thuc` (`TIEN_MAT` / `CHUYEN_KHOAN`) và `luc_xu_ly` không sau hiện tại → thiếu 422 `BR-55`; bằng 0 thì hai trường này bỏ qua (lưu null);
  - `ket_thuc_bat_thuong`: bắt buộc `luong_tay` (số nguyên 0 … 10¹²) và `ly_do_luong_tay` (1–300 ký tự) → thiếu 422 `BR-68`; chuyến bình thường thì bỏ qua hai trường này, dùng lương đã chốt (đúng `api.md`);
  - tạo `QUYET_TOAN` (doanh thu, tổng chi, lương, lý do lương tay, lãi, chênh lệch, cách xử lý, hình thức, lúc xử lý, kế toán); chuyến → `DA_QUYET_TOAN` + lịch sử trạng thái (BR-30); nhật ký tiền `quyet_toan / QUYET_TOAN` (giá trị mới: doanh thu, chi, lương, lãi, chênh lệch, xử lý) và nếu có lương tay thêm dòng `chuyen / LUONG_TAY` (cũ: lương chốt, mới: lương tay, lý do);
  - trả 200 như `api.md` 3.3. Hai Kế toán bấm cùng lúc: người sau 409 `BR-29` (khóa dòng + unique `QUYET_TOAN.chuyen_id`).
- **Sau quyết toán (BR-29):** duyệt / từ chối chi phí, tài xế ghi / sửa / xóa chi phí, cấp / sửa / thu hồi tạm ứng đều 409 `BR-29` (UC-21, 23 đã có, UC-24 thêm cho duyệt / từ chối).
- **Xem ảnh chứng từ:** `GET /api/tep/{id}/link` đã có trong `api.md`, `kien-truc.md` mục 7 (NFR-SEC-04) nhưng chưa làm. UC-24 làm phần **ảnh chi phí cho KT, QL**: kiểm quyền rồi trả link ký HMAC hạn 5 phút; `GET /api/tep/xem?...` mở link → trả ảnh với `Content-Type` theo đuôi đã kiểm lúc lưu, `X-Content-Type-Options: nosniff`. Link hết hạn hoặc sai chữ ký → 403. Ảnh của lượt quét, sự cố, đồng hồ để UC sau (vai trò khác).
- **Giao diện Kế toán:** menu **Quyết toán** (giữa "Công nợ" và "Tạm ứng", theo chữ cái):
  - bảng chuyến chờ quyết toán (`GET /api/chuyen?trang_thai=HOAN_THANH`, có sẵn) và lọc xem chuyến đã quyết toán;
  - chọn chuyến → bảng quyết toán như trên; mỗi khoản chi có **Duyệt** (số mặc định = số khai, sửa số thì hiện ô lý do), **Từ chối** (ô lý do), nút **Ảnh** mở ảnh chứng từ;
  - khối **Quyết toán**: chênh lệch tô màu và câu "Tài xế nộp lại … đ" / "Công ty trả thêm … đ"; chọn hình thức, giờ xử lý (mặc định bây giờ); chuyến kết thúc do sự cố có ô lương tay + lý do; bấm **Quyết toán** hỏi xác nhận; còn khoản chờ duyệt thì nút mờ kèm câu nhắc;
  - chuyến đã quyết toán: chỉ xem, không còn nút.
- **Quản lý:** thêm **Công nợ** và **Quyết toán** vào menu Quản lý chỉ để xem (góp ý của Tài 10/11): ẩn nút "Đánh dấu đã thu", Duyệt, Từ chối, Quyết toán khi vai trò là Quản lý. Quyền thật vẫn do máy chủ kiểm.

## Quyết định (Kiệt duyệt 10/11/2026)
1. **Module mới `backend/app/modules/tien/quyet_toan/`** cạnh `tam_ung/`, `chi_phi/`, `cong_no/`; duyệt / từ chối chi phí đặt trong module này (là bước của quyết toán). Không đổi CSDL: `QUYET_TOAN`, `CHI_PHI.so_tien_duyet/nguoi_duyet`, `NHAT_KY_TIEN` có sẵn; lý do duyệt nằm ở nhật ký tiền. Không thêm gói.
2. **Duyệt chi chỉ khi chuyến `HOAN_THANH`** (`nghiep-vu.md` mục 10: "HOAN_THANH: Kế toán duyệt chi"). Không duyệt lúc đang chạy để khỏi phải tính lại khi tài xế còn thêm khoản.
3. **Số duyệt chỉ được giảm (1 … số khai)**; muốn duyệt 0 thì dùng Từ chối. Tăng hơn số khai không hợp lý (tài xế khai thiếu thì tự sửa khi còn chờ duyệt).
4. **Đổi quyết định được** (duyệt → từ chối, đổi số duyệt) tới trước khi quyết toán, mỗi lần đều ghi nhật ký; Kế toán bấm nhầm không phải nhờ sửa CSDL.
5. **Lương tay cho phép 0** (xe hỏng ngay đầu chuyến), tối đa 10¹² như các số tiền khác.
6. **Chênh lệch = 0** → `KHONG_CHENH`, không cần hình thức và giờ xử lý.
7. **Xem ảnh chứng từ làm luôn trong UC-24** theo `GET /api/tep/{id}/link` (link HMAC 5 phút, ký bằng `JWT_SECRET` có sẵn, không thêm biến môi trường), chỉ ảnh chi phí, chỉ KT/QL. Không có ảnh thì Kế toán duyệt "mù", trái mục đích BR-54.
8. **Quản lý xem được** bảng quyết toán và trang Công nợ, không thao tác (ma trận quyền `nghiep-vu.md` mục 8: "Tạm ứng, quyết toán, công nợ – Quản lý xem").
9. **Không làm** khi quyết toán: in phiếu, mở lại quyết toán (BR-29 khóa hẳn), báo cáo lãi lỗ (UC-26).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-24-AC1 | Duyệt khoản bằng số khai không cần lý do → `DA_DUYET`, `so_tien_duyet` = số khai, nhật ký `DUYET`. Điều chỉnh 520.000 → 500.000 có lý do → đạt; không lý do → 422 `BR-55`. Ca biên: số duyệt = số khai đạt; số khai + 1 → 422; 0 → 400 | API | BR-55, 62 |
| UC-24-AC2 | Từ chối có lý do → `TU_CHOI`, `so_tien_duyet` null, nhật ký `TU_CHOI`; thiếu lý do → 400. Đổi quyết định (duyệt → từ chối, đổi số) ghi thêm nhật ký; quyết định y hệt → 400 `KHONG_CO_THAY_DOI` | API | BR-55, 62 |
| UC-24-AC3 | Duyệt / từ chối khi chuyến `DANG_CHAY` → 409 `BR-55`; khi `DA_QUYET_TOAN` → 409 `BR-29`, số liệu không đổi (TC-BR29-02); khoản không tồn tại → 404 | API | BR-29, 55 |
| UC-24-AC4 | Doanh thu chỉ gồm đơn `DA_GIAO` trên chuyến này: C01 có Đ2, Đ4 giao, Đ1 thất bại → 2.240.000, Đ1 = 0 (TC-BR50-01); Đ1 ghép lại và giao ở C05 thì doanh thu C05 có Đ1 (TC-BR50-02) | Logic | BR-50 |
| UC-24-AC5 | Lãi = doanh thu − chi đã duyệt − lương: 2.240.000 − 1.050.000 − 600.000 = 590.000 (TC-BR51-01); kết thúc do sự cố, lương tay 300.000 → 890.000 (TC-BR51-02). Khoản từ chối không tính vào chi | Logic | BR-51, 68 |
| UC-24-AC6 | `GET /quyet-toan` trả bảng định mức – thực tế – chênh lệch theo loại đúng kịch bản mục 11 bước 7 (dầu −30.000, cầu đường +30.000, bốc xếp +50.000, tổng +50.000), dầu tham khảo 178 km × 15 / 100 = 26,7 lít so với 26 lít, tạm ứng, chênh lệch, lãi dự kiến và lý do lệch (Đ1 thất bại). Thiếu km → dầu tham khảo null. Chuyến `LAP`/`DA_CHOT`/`DANG_CHAY`/`HUY` → 409 | API | BR-50, 51, 55, 71 |
| UC-24-AC7 | Quyết toán C01 (`HOAN_THANH`, 3 khoản đã duyệt 1.050.000, tạm ứng 1.000.000) với `CONG_TY_DA_TRA`, tiền mặt → 200, chuyến `DA_QUYET_TOAN`, chênh lệch −50.000, có bản ghi `QUYET_TOAN`, lịch sử trạng thái và nhật ký tiền `QUYET_TOAN` (TC-BR55-01) | API | BR-55, 62, 30 |
| UC-24-AC8 | Còn khoản `CHO_DUYET` → 409 `BR-55`, chuyến vẫn `HOAN_THANH` (TC-BR55-02); chuyến `DANG_CHAY` → 409 (TC-BR55-05); đã quyết toán → 409 `BR-29` | API | BR-29, 55 |
| UC-24-AC9 | Cách xử lý chênh lệch: thiếu → 422 (TC-BR55-03); sai dấu `TAI_XE_DA_NOP` khi âm → 422 (TC-BR55-04); chênh lệch dương cần `TAI_XE_DA_NOP`; chênh lệch 0 chỉ nhận `KHONG_CHENH` (ca biên tạm ứng = chi); chênh ≠ 0 thiếu hình thức hoặc giờ xử lý → 422; giờ xử lý ở tương lai → 422 | API | BR-55 |
| UC-24-AC10 | Chuyến `ket_thuc_bat_thuong`: thiếu `luong_tay` hoặc lý do → 422 `BR-68`; lương tay 0 đạt (ca biên); có lương tay thì lưu vào `QUYET_TOAN` và thêm nhật ký `LUONG_TAY` (cũ: lương chốt). Chuyến bình thường gửi `luong_tay` → bỏ qua, dùng lương chốt | API | BR-68, 71, 62 |
| UC-24-AC11 | Sau quyết toán: tài xế ghi / sửa / xóa chi phí, Kế toán cấp / sửa / thu hồi tạm ứng, duyệt / từ chối → đều 409 `BR-29`. Hai lần quyết toán liên tiếp → lần sau 409 `BR-29`, chỉ một `QUYET_TOAN` | API | BR-29 |
| UC-24-AC12 | Phân quyền: Điều phối, Tài xế gọi duyệt / từ chối / GET / POST quyết toán → 403; Quản lý GET được, duyệt / từ chối / POST → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-24-AC13 | Ảnh chứng từ: KT, QL lấy link ảnh chi phí → mở được ảnh đúng loại; Tài xế, Điều phối → 403; link quá 5 phút hoặc sửa chữ ký → 403; tệp không tồn tại → 404 | API | NFR-SEC-04 |
| UC-24-AC14 | Giao diện Kế toán: danh sách chuyến chờ, bảng quyết toán, duyệt / điều chỉnh / từ chối, xem ảnh, quyết toán có hỏi xác nhận, chuyến đã quyết toán chỉ xem; Quản lý thấy menu Công nợ và Quyết toán nhưng không có nút thao tác. Thử tay theo `docs/test-evidence/UC-24/du-lieu.md`, ảnh chụp | UI | BR-29, 55 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/tien/quyet_toan/` (router, schemas, service: duyệt / từ chối, bảng, quyết toán), `backend/app/modules/tep/router.py` (link ảnh ký HMAC 5 phút + mở ảnh), `backend/app/main.py` (2 router, theo chữ cái), `docs/api.md` (2.6, 3.3, tệp).
- Test đã viết: `backend/tests/api/test_uc24_quyet_toan.py` 61 test (AC1–AC13). Thử phá 21 chỗ trong service (đổi điều kiện, bỏ kiểm tra): 21/21 bị test bắt (chỗ "tạm ứng đã thu hồi" lọt lần đầu, đã thêm test).
- Kết quả 10/11: 61 passed; toàn bộ 848 passed.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc24_quyet_toan.py`
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa: đã sửa `api.md`: chi tiết duyệt / từ chối, QL xem GET quyết toán, endpoint mở ảnh `/api/tep/{id}/anh`. Nhỏ: `luc_xu_ly` nhận lệch 5 phút so với giờ máy chủ (máy Kế toán chạy nhanh); `luc_xu_ly` thiếu múi giờ → 400.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-24-AC1 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac1_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC2 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac2_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC3 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac3_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC4 | Logic | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac4_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC5 | Logic | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac5_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC6 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac6_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC7 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac7_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC8 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac8_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC9 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac9_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC10 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac10_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC11 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac11_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC12 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac12_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC13 | API | `backend/tests/api/test_uc24_quyet_toan.py::test_uc24_ac13_*` | Đạt (61 passed) | 10/11/2026 |
| UC-24-AC14 | UI | Thử tay ca a–l theo `docs/test-evidence/UC-24/du-lieu.md`, ảnh `b`, `c`, `d`, `f`, `g`, `h`, `j`, `k`, `l` trong `docs/test-evidence/UC-24/`; Kiệt xác nhận | Đạt | 10/11/2026 |
