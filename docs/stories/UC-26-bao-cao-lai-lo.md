# UC-26: Báo cáo lãi lỗ theo chuyến / xe / tháng

- **Trạng thái:** Đang làm – backend xong 7/8 AC (11/11/2026; duyệt 11/11/2026, Kiệt: "duyệt" – 7 quyết định như đề xuất). AC8 giao diện chờ Tài làm, Kiệt thử
- **Tác nhân:** Quản lý, Kế toán (Điều phối chỉ xem)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-26, ưu tiên S; đặc tả rút gọn ở story này) · `docs/api.md` `GET /api/bao-cao/lai-lo` · `nghiep-vu.md` bảng chỉ số ("Lãi xe theo tháng") và mục 11 bước 8 (X1 tháng 10: Σ lãi các chuyến − chi phí cố định 9.000.000) · `so-do.md` (`CHI_PHI_CO_DINH_XE` chỉ dùng cho lãi theo xe/tháng, không vào lãi chuyến)
- **Quy tắc nghiệp vụ liên quan:** BR-51 (lãi chuyến), BR-29 (quyết toán khóa sổ), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-26-bao-cao-lai-lo` tách từ `dev` (cần UC-24 quyết toán, đã có trên `dev`). Chỉ đọc, không ghi CSDL. **Kiệt làm backend; giao diện + biểu đồ Tài làm** (Tài nhắn 11/11), Kiệt ghi tên trường API trong mô tả PR.

## Mô tả ngắn
Quản lý (và Kế toán) chọn khoảng tháng và cách xem: **theo chuyến**, **theo xe** hoặc **theo tháng**. Hệ thống cộng số đã khóa trong quyết toán của các chuyến (doanh thu, chi phí đã duyệt, lương, lãi). Theo xe và theo tháng thì trừ thêm chi phí cố định hằng tháng của xe để ra lãi thật.

## Đặc tả rút gọn
- **`GET /api/bao-cao/lai-lo?theo=chuyen|xe|thang&tu=YYYY-MM&den=YYYY-MM`** (QL, KT, DP):
  - `tu`, `den` là tháng; thiếu thì lấy tháng hiện tại (giờ Việt Nam); `tu > den` hoặc quá 12 tháng → 400; trường lạ → 400.
  - Chỉ lấy chuyến **`DA_QUYET_TOAN`**, đọc số trong bảng `QUYET_TOAN` (không tính lại). Chuyến thuộc tháng theo **ngày khởi hành thực tế** (giờ Việt Nam).
  - `theo=chuyen`: mỗi chuyến `{chuyen_id, ma_chuyen, ngay, bien_so, ten_tuyen, doanh_thu, tong_chi, luong_tai_xe, lai}`, mới trước.
  - `theo=xe`: mỗi xe `{xe_id, bien_so, so_chuyen, doanh_thu, tong_chi, luong_tai_xe, lai_chuyen, chi_phi_co_dinh, lai}` với `lai = lai_chuyen − chi_phi_co_dinh` (Σ chi phí cố định các tháng trong khoảng). Xe không chạy chuyến nào nhưng có chi phí cố định vẫn có dòng (lỗ).
  - `theo=thang`: mỗi tháng trong khoảng một dòng `{thang, so_chuyen, doanh_thu, tong_chi, luong_tai_xe, lai_chuyen, chi_phi_co_dinh, lai}`, kể cả tháng trống.
  - Kèm `tong` (dòng tổng cùng cột), `so_chuyen_cho_quyet_toan` (chuyến `HOAN_THANH` khởi hành trong khoảng, chưa vào báo cáo) và `thieu_chi_phi_co_dinh` (theo xe/tháng: các cặp xe – tháng có chuyến mà chưa nhập chi phí cố định).
- **Giao diện (Tài làm):** menu **Báo cáo lãi lỗ**; chọn khoảng tháng, Chuyến / Xe / Tháng, bảng có dòng tổng, biểu đồ lãi theo tháng (`theo=thang` trả đủ mọi tháng kể cả tháng trống để vẽ liền trục), lãi âm tô đỏ, ghi chú chuyến chờ quyết toán và thiếu chi phí cố định.

## Quyết định (Kiệt duyệt 11/11/2026)
1. **Chỉ chuyến đã quyết toán**, đọc số đã khóa (BR-29): báo cáo không đổi theo thời gian, khớp sổ Kế toán. Chuyến `HOAN_THANH` chỉ báo số lượng.
2. **Tháng của chuyến = ngày khởi hành thực tế**, giờ Việt Nam (chuyến đã quyết toán luôn có giờ này).
3. **Chi phí cố định chưa nhập tính 0** và hiện cảnh báo, không chặn báo cáo.
4. **Khoảng tối đa 12 tháng**, mặc định tháng hiện tại.
5. **Điều phối được xem** như `api.md` ghi; Tài xế 403.
6. **Module mới `backend/app/modules/bao_cao/`**, không đổi CSDL, không thêm gói. Biểu đồ do Tài làm ở giao diện.
7. **Ngoài phạm vi:** xuất Excel/PDF, lãi theo khách hàng / tuyến, hiệu suất xe (UC-34).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-26-AC1 | Theo chuyến: chuyến đã quyết toán trong khoảng hiện đủ cột, số **bằng đúng** bảng `QUYET_TOAN`; chuyến `LAP`, `DA_CHOT`, `DANG_CHAY`, `HOAN_THANH`, `HUY` không có dòng; `so_chuyen_cho_quyet_toan` đếm đúng chuyến `HOAN_THANH` | API | BR-51, 29 |
| UC-26-AC2 | Biên tháng: chuyến khởi hành 23:59 ngày cuối tháng (giờ VN) thuộc tháng đó; 00:00 ngày đầu tháng sau thuộc tháng sau | Logic | — |
| UC-26-AC3 | Theo xe (kịch bản mục 11 bước 8): X1 có 2 chuyến tháng 10 lãi 3.000.000 và 2.500.000, chi phí cố định tháng 10 là 9.000.000 → `lai_chuyen` 5.500.000, `lai` −3.500.000; xe không chạy nhưng có chi phí cố định 4.000.000 → dòng `so_chuyen` 0, `lai` −4.000.000 | API | nghiep-vu bảng chỉ số |
| UC-26-AC4 | Theo tháng: khoảng 09–11 trả đủ 3 dòng kể cả tháng trống; mỗi tháng trừ đúng chi phí cố định của tháng đó (không trừ tháng khác); `tong` = cộng các dòng | API | nghiep-vu bảng chỉ số |
| UC-26-AC5 | Thiếu chi phí cố định: xe có chuyến tháng 10 mà chưa nhập → tính 0, có trong `thieu_chi_phi_co_dinh`; đã nhập thì không có | API | — |
| UC-26-AC6 | Tham số sai → 400: `theo` khác 3 giá trị, tháng sai dạng (`2026-13`, `2026-1`), `tu > den`, 13 tháng (biên: đúng 12 tháng được), trường lạ. Thiếu `tu`, `den` → tháng hiện tại | API | security-rules |
| UC-26-AC7 | Phân quyền: Quản lý, Kế toán, Điều phối xem được; Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-26-AC8 | (Tài làm, Kiệt thử) Giao diện: menu Báo cáo lãi lỗ; chọn khoảng tháng và Chuyến / Xe / Tháng thì bảng đổi đúng; có dòng tổng; lãi âm tô đỏ; hiện số chuyến chờ quyết toán và cảnh báo thiếu chi phí cố định | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (11/11, backend):
  - `backend/app/modules/bao_cao/` (mới): `service.py` (đọc `QUYET_TOAN` của chuyến `DA_QUYET_TOAN`, lọc theo khởi hành thực tế với mốc đầu tháng giờ VN, gom theo chuyến / xe / tháng, trừ `CHI_PHI_CO_DINH_XE`, danh sách thiếu chi phí cố định), `router.py` (`GET /api/bao-cao/lai-lo`, QL/KT/DP, tham số lạ → 400). `app/main.py` thêm router theo chữ cái.
  - Tài liệu: `api.md` dòng `/api/bao-cao/lai-lo` ghi đủ tên trường cho giao diện.
- Không đổi CSDL, không thêm gói. Không phân trang theo chuyến (tối đa 12 tháng, đội ~10 xe).
- Test đã viết: `tests/api/test_uc26_bao_cao_lai_lo.py` (18 ca). Đã thử làm hỏng 5 chỗ: bỏ trừ chi phí cố định, mốc tháng theo UTC, cho 13 tháng, bỏ báo thiếu chi phí cố định → có test đỏ; bỏ điều kiện `DA_QUYET_TOAN` → vẫn xanh vì phép nối với `QUYET_TOAN` đã loại chuyến chưa quyết toán (điều kiện giữ lại cho rõ).
- Toàn bộ: 868 passed (11/11, nhánh tách từ `dev`).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc26_bao_cao_lai_lo.py`
- Lệch đặc tả: `api.md` ghi "DP xem" → giữ, Điều phối gọi được API (quyết định 5). Không lệch khác.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-26-AC1 | API | `test_uc26_ac1_theo_chuyen_lay_so_da_khoa`, `test_uc26_ac1_chuyen_ngoai_khoang_khong_vao` | Đạt | 11/11/2026 |
| UC-26-AC2 | Logic | `test_uc26_ac2_bien_thang_gio_viet_nam` | Đạt | 11/11/2026 |
| UC-26-AC3 | API | `test_uc26_ac3_theo_xe_tru_chi_phi_co_dinh` | Đạt | 11/11/2026 |
| UC-26-AC4 | API | `test_uc26_ac4_theo_thang_du_thang_tru_dung_thang` | Đạt | 11/11/2026 |
| UC-26-AC5 | API | `test_uc26_ac5_thieu_chi_phi_co_dinh_tinh_0_va_bao` | Đạt | 11/11/2026 |
| UC-26-AC6 | API | `test_uc26_ac6_tham_so_sai_400` (7 ca), `test_uc26_ac6_bien_12_thang_duoc_va_mac_dinh_thang_nay` | Đạt | 11/11/2026 |
| UC-26-AC7 | API | `test_uc26_ac7_vai_tro_duoc_xem` (3 vai trò), `test_uc26_ac7_tai_xe_403_chua_dang_nhap_401` | Đạt | 11/11/2026 |
| UC-26-AC8 | UI | Tài làm giao diện, Kiệt thử | CHƯA KIỂM | |
