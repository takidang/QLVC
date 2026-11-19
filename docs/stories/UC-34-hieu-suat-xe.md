# UC-34: Hiệu suất xe theo tháng

- **Trạng thái:** Hoàn thành 19/11/2026 – 7/7 AC (backend 11/11; AC7 giao diện v3 Kiệt thử 18/11, PR #60). Duyệt 11/11/2026, Kiệt: "duyệt" – 6 quyết định như đề xuất
- **Tác nhân:** Quản lý (Kế toán xem)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-34, ưu tiên S; đặc tả rút gọn ở story này) · `docs/api.md` `GET /api/bao-cao/hieu-suat-xe` · `nghiep-vu.md` bảng chỉ số "Hiệu suất xe theo tháng" (% lấp đầy trung bình các chuyến không hủy; số chuyến chạy rỗng; Σ km; Σ lít dầu thực tế so với Σ dầu tham khảo), A8 (giữ góc nhìn chủ xe), mục 11 bước 8
- **Quy tắc nghiệp vụ liên quan:** BR-23 (chạy rỗng), BR-70 (km đầu / cuối), BR-54 (khoản dầu ghi số lít), BR-57 (phân quyền); công thức lấp đầy mục 2.1
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-34-hieu-suat-xe` tách từ `kiet/uc-26-bao-cao-lai-lo` (dùng chung module `bao_cao/`; mở PR sau khi UC-26 gộp). **Kiệt làm backend; giao diện Tài làm**, Kiệt ghi tên trường API trong mô tả PR. Chỉ đọc.

## Mô tả ngắn
Quản lý chọn tháng, xem mỗi xe chạy mấy chuyến, mấy chuyến chạy rỗng, chở đầy trung bình bao nhiêu %, chạy bao nhiêu km, đổ bao nhiêu lít dầu so với định mức của xe. Biết xe nào chạy ít, chở vơi hay hao dầu.

## Đặc tả rút gọn
- **`GET /api/bao-cao/hieu-suat-xe?thang=YYYY-MM`** (QL, KT): thiếu `thang` → tháng hiện tại (giờ VN); sai dạng, tham số lạ → 400.
- Chuyến tính: **đã chạy xong** (`HOAN_THANH`, `DA_QUYET_TOAN`), khởi hành thực tế trong tháng (giờ VN, như UC-26).
- Trả `{thang, du_lieu, tong}`; mỗi xe `{xe_id, bien_so, so_chuyen, so_chuyen_rong, lap_day_tb, km, dau_thuc_te_lit, dau_tham_khao_lit, chenh_lech_lit, so_chuyen_chua_quyet_toan}`:
  - `lap_day_tb`: trung bình % lấp đầy các chuyến (chuyến chạy rỗng tính 0); lấp đầy một chuyến = max(Σ kg / tải trọng, Σ m³ / thể tích) của các đơn đã ghép (như UC-13, gồm đơn thất bại); xe không có chuyến → `null`.
  - `km` = Σ (km kết thúc − km bắt đầu).
  - `dau_thuc_te_lit` = Σ số lít của khoản dầu **đã duyệt**; `dau_tham_khao_lit` = Σ km × định mức lít/100 km của xe (như UC-24); xe chưa có định mức → `null`, `chenh_lech_lit` `null`.
  - `so_chuyen_chua_quyet_toan`: số chuyến `HOAN_THANH` (dầu thực tế có thể còn khoản chờ duyệt).
- Danh sách: mọi xe có chuyến trong tháng + xe `HOAT_DONG` không chạy (dòng 0, để thấy xe nằm bãi); theo biển số. `tong` cộng các cột (lấp đầy trung bình trên mọi chuyến).

## Quyết định (Kiệt duyệt 11/11/2026)
1. **Chỉ chuyến đã chạy xong** (`HOAN_THANH`, `DA_QUYET_TOAN`) thay vì "mọi chuyến không hủy": chuyến chưa chạy chưa có km, dầu, và lấp đầy kế hoạch làm số tháng sai. Đã ghi cách hiểu này vào `nghiep-vu.md` bảng chỉ số.
2. **Tính cả chuyến chưa quyết toán**, kèm `so_chuyen_chua_quyet_toan` để biết dầu có thể chưa đủ (khác UC-26 chỉ lấy đã quyết toán, vì đây là số vận hành, không phải sổ tiền).
3. **Dầu so sánh bằng lít** (đặc tả ghi "lít dầu thực tế so với dầu tham khảo"), chỉ khoản `DA_DUYET`.
4. **Xe đang hoạt động không chạy vẫn có dòng**; xe ngừng không chạy thì không.
5. **Quyền theo `api.md`:** Quản lý, Kế toán; Điều phối, Tài xế 403.
6. Dùng chung module `bao_cao/` của UC-26, không đổi CSDL, không thêm gói. Ngoài phạm vi: theo tài xế, theo tuyến, nhiều tháng.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-34-AC1 | X1 tháng 10 có 3 chuyến xong: lấp đầy 76%, 50%, chạy rỗng → `so_chuyen` 3, `so_chuyen_rong` 1, `lap_day_tb` 0,42; `km` = tổng km 3 chuyến | API | BR-23, mục 2.1 |
| UC-34-AC2 | Chỉ chuyến `HOAN_THANH`, `DA_QUYET_TOAN` khởi hành thực tế trong tháng (biên 23:59 ngày cuối tháng / 00:00 ngày đầu tháng sau, giờ VN); chuyến `DANG_CHAY`, `HUY` không tính; đơn đã gỡ khỏi chuyến không vào lấp đầy | API | — |
| UC-34-AC3 | Dầu: chỉ số lít khoản dầu `DA_DUYET` (chờ duyệt, từ chối không tính); tham khảo = km × định mức / 100; chênh lệch = thực tế − tham khảo; xe không có định mức → tham khảo, chênh lệch `null`; `so_chuyen_chua_quyet_toan` đếm đúng | API | BR-54 |
| UC-34-AC4 | Xe hoạt động không chạy có dòng 0, `lap_day_tb` null; xe ngừng không chạy không có dòng; `tong` đúng (lấp đầy trung bình trên mọi chuyến, không phải trung bình của các xe) | API | — |
| UC-34-AC5 | Tham số: `thang` sai dạng (`2030-13`, `2030-1`), tham số lạ → 400; thiếu `thang` → tháng hiện tại | API | security-rules |
| UC-34-AC6 | Phân quyền: Quản lý, Kế toán xem được; Điều phối, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-34-AC7 | (Tài làm, Kiệt thử) Giao diện: chọn tháng, bảng mỗi xe, tô chênh lệch dầu dương (hao) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (11/11, backend):
  - `backend/app/modules/bao_cao/service.py`: thêm `hieu_suat_xe` (gom hàng theo ghép như UC-13 bằng một truy vấn, lít dầu đã duyệt một truy vấn, lấp đầy bằng `domain.lich_trinh.ty_le_lap_day`, dầu tham khảo như UC-24). `router.py`: `GET /api/bao-cao/hieu-suat-xe` (QL, KT); hàm chặn tham số lạ dùng chung cho hai báo cáo.
  - Tài liệu: `api.md` dòng `/api/bao-cao/hieu-suat-xe` ghi đủ tên trường; `nghiep-vu.md` bảng chỉ số ghi "chuyến đã chạy xong" (quyết định 1).
- Không đổi CSDL, không thêm gói.
- Test đã viết: `tests/api/test_uc34_hieu_suat_xe.py` (13 ca). Đã thử làm hỏng 8 chỗ (tính cả chuyến chưa chạy, tính đơn đã gỡ, tính dầu chưa duyệt, bỏ xe nằm bãi, thêm xe ngừng, tổng lấp đầy trung bình theo xe, mốc tháng UTC, bỏ đếm chạy rỗng) → lần nào cũng có test đỏ (đơn đã gỡ: lần đầu lọt vì fixture gắn nhầm vào chuyến hủy, đã sửa fixture).
- Toàn bộ: 881 passed (11/11, nhánh tách từ UC-26).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc34_hieu_suat_xe.py`
- Lệch đặc tả: `nghiep-vu.md` "các chuyến không hủy" → "đã chạy xong" (đã sửa tài liệu cùng commit); `api.md` "QL (KT xem)" giữ nguyên nghĩa.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-34-AC1 | API | `test_uc34_ac1_x1_thang_10` | Đạt | 11/11/2026 |
| UC-34-AC2 | API | `test_uc34_ac2_chi_chuyen_xong_trong_thang` | Đạt | 11/11/2026 |
| UC-34-AC3 | API | `test_uc34_ac3_dau` | Đạt | 11/11/2026 |
| UC-34-AC4 | API | `test_uc34_ac4_xe_nam_bai_va_tong` | Đạt | 11/11/2026 |
| UC-34-AC5 | API | `test_uc34_ac5_tham_so_sai_400` (3 ca), `test_uc34_ac5_mac_dinh_thang_nay` | Đạt | 11/11/2026 |
| UC-34-AC6 | API | `test_uc34_ac6_phan_quyen` (4 vai trò), `test_uc34_ac6_chua_dang_nhap_401` | Đạt | 11/11/2026 |
| UC-34-AC7 | UI | `docs/test-evidence/UC-34/` (Tổng quan, bảng "Hiệu suất xe": chọn tháng, mỗi xe một dòng, cột Chênh lệch (lít) dương tô màu; xe chưa duyệt dầu hiện "–" từ 3d8ebab) | Đạt (Kiệt thử trên giao diện v3 0cef9cd) | 18/11/2026 |
