# Danh sách ca test theo quy tắc nghiệp vụ (BR)

> Người làm: **Kiệt** · Nguồn: `docs/nghiep-vu.md` bản 0.5 (mục 4 quy tắc, mục 2.1 công thức, mục 11 kịch bản) · Trạng thái: **đã chốt 30/10** (Kiệt điền đủ 29/10; Tài đồng ý cả 5 đề xuất ở mục 5, đã ghi vào `nghiep-vu.md`).
> Dùng cho: viết test khi làm từng story (`story-flow`), và bảng truy vết trong báo cáo kiểm thử (`story report`).

## 1. Yêu cầu

- Mỗi BR mức **Chặn**: ít nhất **1 ca đạt (✔)** và **1 ca bị chặn (✖)** (NFR-FUN-01).
- BR mức **Cảnh báo**: 1 ca có cảnh báo, 1 ca không cảnh báo.
- BR công thức (mức "—", ví dụ BR-46…51, 63…65): ít nhất 1 ca tính ra đúng số, ưu tiên ca có điểm biên (làm tròn, bằng đúng giới hạn, qua nửa đêm).
- BR đã bỏ ở 0.5 (27, 44, 61): không viết ca.
- **Dùng lại dữ liệu mục 11** (tuyến T01, xe X1/X2, tài xế An/Bình, đơn Đ1…Đ8) khi được. Cần dữ liệu mới thì ghi vào cột Dữ liệu, giữ cùng tuyến/xe để tính tay kiểm được.
- Mỗi ca **chỉ vi phạm đúng một BR**, nếu không thì ca đó không chứng minh được BR nào (bài học Đ3 ở review PR #1).
- Ca ở biên: "bằng đúng giới hạn" là ✔ hay ✖ phải theo đúng chữ trong BR (≤, <, khoảng nửa mở `[a, b)`).

## 2. Quy ước cột

| Cột | Ghi gì |
|---|---|
| Mã ca | `TC-BRxx-nn`, ví dụ `TC-BR01-01` |
| BR | Mã BR chính đang kiểm |
| Loại | ✔ đạt / ✖ bị chặn / ⚠ có cảnh báo / = tính đúng số |
| Dữ liệu | Đơn, xe, chuyến lấy từ mục 11, hoặc mô tả ngắn dữ liệu thêm |
| Thao tác | Việc làm (ghép, chốt, quét…), theo đúng tên UC/endpoint |
| Kết quả mong đợi | Trạng thái, con số, hoặc lỗi kèm mã BR và mã HTTP (`api.md`, `kien-truc.md` mục 7: 422 vi phạm BR, 409 sai trạng thái, 403 sai quyền) |
| Mức | **U** unit (hàm domain, không cần DB) · **A** API (pytest + PostgreSQL) · **E** E2E (Playwright) |
| UC | Use case sẽ chứa test này (để story biết test nào thuộc mình) |

Chọn mức thấp nhất đủ chứng minh: công thức và kiểm tra thuần → **U**; cần giao dịch, khóa dòng, phân quyền → **A**; luồng trên giao diện → **E**.

## 3. Ví dụ (lấy từ mục 11)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR01-01 | BR-01 | ✔ | C01 (X1, 5.000 kg) có Đ1, Đ4 | Ghép Đ2 | Ghép được, tổng 3.800 kg | U | UC-13 |
| TC-BR01-02 | BR-01 | ✖ | C01 có Đ1, Đ4 | Ghép Đ6 (2.500 kg) | 422 `BR-01`, tổng 5.100 > 5.000, không ghép đơn nào | U | UC-13 |
| TC-BR47-01 | BR-47 | = | Đ8: 300 kg, 1 m³, HCM→Tiền Giang 1.000 đ/kg | Tạo đơn | KL tính cước 333 kg, cước 333.000 | U | UC-08 |
| TC-BR48-02 | BR-48 | ✖ | Đ7 Cần Thơ → Cà Mau, không có giá | Tạo đơn | 422 `BR-48`, không tạo đơn | A | UC-08 |
| TC-BR63-01 | BR-63 | = | C01 có Đ1, Đ2, Đ4, khởi hành 06:00, `CFG-08` = 20′ | Tính lịch trình | 6 điểm, ETA 06:00 / 06:20 / 07:40 / 09:00 / 11:50 (giao Đ2) / 12:10 (giao Đ1) | U | UC-13 |
| TC-BR67-01 | BR-67 | ✖ | C01 có Đ1, Đ2, Đ4 | Ghép Đ8 | 422, vi phạm `BR-06` ở **Đ2** (ETA 12:30 > 12:00), không ghép | U | UC-13 |
| TC-BR73-01 | BR-73 | ⚠ | C01 đang chạy, C00 của An lúc 13:45 | Quét lấy Đ2 lúc 08:10 | Trễ 30′ > `CFG-09`, dự kiến xong 14:00 chồng C00 → cảnh báo | A | UC-32 |
| TC-BR73-02 | BR-73 | không ⚠ | Như trên nhưng C00 lúc 14:00 | Quét lấy Đ2 lúc 08:10 | `[06:00, 14:00)` không chồng `[14:00, …)` → không cảnh báo | U | UC-32 |

## 4. Danh sách ca (Kiệt điền 29/10)

Xếp theo nhóm A…H như mục 4 của `nghiep-vu.md`. Các ví dụ ở mục 3 đã chép vào đúng nhóm.

### 4.0 Dữ liệu dùng chung

**Từ mục 11 (không đổi):** tuyến T01 (HCM 0′/0 km, Long An 60′/50, Tiền Giang 120′/75 nghỉ, Vĩnh Long 210′/135, Cần Thơ 270′/170; định mức dầu 550.000 + cầu đường 200.000 + bốc xếp 250.000 = 1.000.000, lương 600.000); xe X1 (5.000 kg, 20 m³, toàn bộ 9.500 kg, đăng kiểm 30/11/2026, 15 l/100 km, km 120.000), X2 (1.500 kg, 8 m³, toàn bộ 3.400 kg, đăng kiểm 19/10); tài xế An (C), Bình (B); bảng giá HCM→Cần Thơ 1.500, Long An→Cần Thơ 1.200, HCM→Vĩnh Long 1.300, HCM→Tiền Giang 1.000, Vĩnh Long→Long An 1.200 (đ/kg); đơn Đ1…Đ8; chuyến **C01** = T01, khởi hành 06:00 ngày 20/10/2026, X1, An. `CFG-01` = 333, `CFG-05` = 60′, `CFG-06` = 1.000, `CFG-08` = 20′, `CFG-09` = 15′, `CFG-10` = 24 giờ.

**Thêm cho các ca dưới** (giữ cùng tuyến, xe để tính tay được):

| Mã | Dữ liệu |
|---|---|
| Giá | Cước tối thiểu **50.000 đ** cho mọi cặp tỉnh (mục 11 chưa ghi; theo dữ liệu thử UC-08). Thêm giá HCM→Bến Tre 1.100, Cần Thơ→Cần Thơ 800 |
| X1 | Hạn bảo hiểm 30/06/2027 (như test UC-03) |
| X2 | Hạn bảo hiểm 31/12/2026 |
| X3 | Như X1, biển 51C-333.33, trạng thái `NGUNG` |
| X5 | Như X1, biển 51C-555.55, hạn bảo hiểm 19/10/2026 |
| X6 | Như X1, biển 51C-666.66 (xe của chuyến C00 khi cần) |
| X7 | Tải 1.900 kg, 12 m³, toàn bộ 4.000 kg (cần C1), đăng kiểm và bảo hiểm 30/11/2026, `HOAT_DONG` |
| X8 | Như X1, biển 51C-888.88, hạn đăng kiểm 20/11/2026 |
| Cường | Tài xế hạng C, GPLX hết hạn 19/10/2026 |
| Dũng | Tài xế hạng C, GPLX còn hạn (tài xế của chuyến C02) |
| Đ1 | Thêm: SĐT người gửi 0909123456, SĐT người nhận 0909555666 (theo dữ liệu thử UC-08) |
| Đ9 | HCM→Tiền Giang, 2.400 kg, 2 m³, hạn 20/10 18:00 |
| Đ10 | HCM→Tiền Giang, 500 kg, 12 m³, hạn 20/10 18:00 |
| Đ11 | HCM→Tiền Giang, 500 kg, 12,01 m³, hạn 20/10 18:00 |
| Đ12 | HCM→Bến Tre (nút không thuộc T01), 500 kg, 1 m³, hạn 20/10 18:00 |
| Đ13 | Cần Thơ (kho Trà Nóc) → Cần Thơ (Ninh Kiều), 300 kg, 1 m³, hạn 20/10 18:00 |
| Đ14 | HCM→Tiền Giang, 300 kg, 1 m³, **khung lấy 06:00–07:00**, hạn 20/10 18:00 |
| Đ15 | HCM→Tiền Giang, 20 kg, 0,05 m³, hạn 20/10 18:00 |
| Đ2a / Đ2b / Đ2c / Đ2d | Như Đ2, chỉ đổi: khung lấy 06:30–07:30 / khung lấy 08:00–09:00 / khung lấy 07:40–09:00 / hạn giao 20/10 11:50 |

Nhắc lại lịch trình gốc của C01 có Đ1, Đ2, Đ4 (BR-63): lấy Đ1 06:00 · lấy Đ4 06:20 · lấy Đ2 07:40 · giao Đ4 09:00 · giao Đ2 11:50 · giao Đ1 12:10; kết thúc dự kiến 13:30; chạy rỗng kết thúc 11:30.

### Nhóm A – Ghép đơn (BR-01…10)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR01-01 | BR-01 | ✔ | C01 (X1, 5.000 kg) có Đ1, Đ4 | Ghép Đ2 | Ghép được, tổng 3.800 kg | U | UC-13 |
| TC-BR01-02 | BR-01 | ✖ | C01 có Đ1, Đ4 | Ghép Đ6 (2.500 kg) | 422 `BR-01`, tổng 5.100 > 5.000, không ghép đơn nào | U | UC-13 |
| TC-BR01-03 | BR-01 | ✔ biên | C01 có Đ1, Đ4 (2.600 kg, 8 m³) | Ghép Đ9 (2.400 kg) | Ghép được: tổng **đúng 5.000** = tải trọng (≤) | U | UC-13 |
| TC-BR02-01 | BR-02 | ✔ biên | C01 có Đ1, Đ4 (8 m³) | Ghép Đ10 (12 m³) | Ghép được: tổng **đúng 20 m³** = thể tích thùng; tải 3.100 kg | U | UC-13 |
| TC-BR02-02 | BR-02 | ✖ | C01 có Đ1, Đ4 | Ghép Đ11 (12,01 m³) | 422 `BR-02`, tổng 20,01 > 20 m³; tải 3.100 kg vẫn đạt | U | UC-13 |
| TC-BR03-01 | BR-03 | ✔ | C01 có Đ1 | Ghép Đ4 (HCM, Tiền Giang đều thuộc T01) | Ghép được | U | UC-13 |
| TC-BR03-02 | BR-03 | ✖ | C01 có Đ1, Đ4 | Ghép Đ12 (giao Bến Tre) | 422 `BR-03`; `don-phu-hop` của C01 không liệt kê Đ12 | U | UC-13 |
| TC-BR04-01 | BR-04 | ✔ | C01 có Đ1, Đ4 | Ghép Đ2 (Long An thứ 2 → Cần Thơ thứ 5) | Ghép được | U | UC-13 |
| TC-BR04-02 | BR-04 | ✖ | C01 có Đ1, Đ4 | Ghép Đ5 (Vĩnh Long thứ 4 → Long An thứ 2) | 422 `BR-04` sai chiều, không ghép | U | UC-13 |
| TC-BR04-03 | BR-04 | ✔ biên | C01 có Đ1, Đ4 | Ghép Đ13 (lấy và giao cùng nút Cần Thơ) | Ghép được: thứ tự nút lấy = nút giao (≤); trong nút Cần Thơ, điểm LẤY Đ13 đứng trước các điểm GIAO | U | UC-13 |
| TC-BR05-01 | BR-05 | ✔ | C01 có Đ1, Đ4 | Ghép Đ2 (khung 06:30–09:00) | ETA lấy 07:40 trong khung → ghép được | U | UC-13 |
| TC-BR05-02 | BR-05 | ✖ trễ | C01 có Đ1, Đ4 | Ghép Đ2a (khung 06:30–07:30) | 422 `BR-05`: ETA lấy 07:40 > 07:30; giao 11:50 vẫn kịp hạn | U | UC-13 |
| TC-BR05-03 | BR-05 | ✖ sớm | C01 có Đ1, Đ4 | Ghép Đ2b (khung 08:00–09:00) | 422 `BR-05`: ETA lấy 07:40 < 08:00 (xe không đứng chờ – giới hạn đã biết ở ghi chú BR-05) | U | UC-13 |
| TC-BR05-04 | BR-05 | ✔ biên | C01 có Đ1, Đ4 | Ghép Đ2c (khung 07:40–09:00) | Ghép được: ETA lấy đúng 07:40 = đầu khung (khung đóng hai đầu, chốt 30/10) | U | UC-13 |
| TC-BR05-05 | BR-05 | ✔ | C01 rỗng | Ghép Đ1 (không có khung lấy) | Ghép được: không khung coi là cả ngày | U | UC-13 |
| TC-BR06-01 | BR-06 | ✔ | C01 có Đ2, Đ4 | Ghép Đ1 | Giao Đ1 12:10 ≤ hạn 14:00 → ghép được | U | UC-13 |
| TC-BR06-02 | BR-06 | ✖ | C01 có Đ1, Đ4 | Ghép Đ3 (giao Vĩnh Long, hạn 10:00) | 422 `BR-06`: ETA giao = 06:00 + 210′ + 4 × 20′ = 10:50 > 10:00; tải 4.100 kg, 13 m³ vẫn đạt | U | UC-13 |
| TC-BR06-03 | BR-06 | ✔ biên | C01 có Đ1, Đ4 | Ghép Đ2d (hạn 11:50) | Ghép được: giao Đ2d đúng 11:50 = hạn (≤) | U | UC-13 |
| TC-BR07-01 | BR-07 | ✔ | Đ4 đã ghép C01 rồi gỡ; chuyến C02 (`LAP`) | Ghép Đ4 vào C02 | Ghép được; Đ4 có 2 bản ghi `GHEP`, đúng 1 bản `hieu_luc = true` | A | UC-13 |
| TC-BR07-02 | BR-07 | ✖ | Đ8 `CHO_GHEP`; C01 và C02 đều `LAP`, hợp lệ cho Đ8 | Hai yêu cầu ghép Đ8 vào C01 và C02 **cùng lúc** | Đúng một yêu cầu 200, yêu cầu kia 409; Đ8 có đúng 1 bản ghi `hieu_luc = true` (unique index ở CSDL) | A | UC-13 |
| TC-BR08-01 | BR-08 | review | — | Xem thiết kế: `DON_HANG` không có số lượng con; `POST /ghep` chỉ nhận `don_ids` | Không có cách ghép một phần đơn; gửi thêm trường số lượng → 400 (`extra="forbid"`) | A | UC-13 |
| TC-BR09-01 | BR-09 | ✔ | Đ4 `CHO_GHEP`, C01 `LAP` | Ghép Đ4 vào C01 | Ghép được, Đ4 → `DA_GHEP` | U | UC-13 |
| TC-BR09-02 | BR-09 | ✖ đơn | Đ4 đang `DA_GHEP` ở C01; C02 `LAP` | Ghép Đ4 vào C02 | 409 `BR-09` (đơn không ở `CHO_GHEP`) | A | UC-13 |
| TC-BR09-03 | BR-09 | ✖ chuyến | C01 đã `DA_CHOT` | Ghép Đ8 vào C01 | 409 `BR-09` (chuyến không ở `LAP`) | A | UC-13 |
| TC-BR10-01 | BR-10 | review | — | Xem thiết kế: không có bảng điểm dừng, không có endpoint sắp điểm dừng (UC-14 bỏ) | Lịch trình luôn suy ra theo BR-63 (ca ở nhóm H) | — | UC-13 |

### Nhóm B – Xe và tài xế (BR-11…21)

Các ca "lập chuyến" dùng C01 rỗng (chưa ghép đơn): khoảng chiếm [06:00, 11:30), giờ lái 4,5 giờ.

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR11-01 | BR-11 | ✔ | X1 `HOAT_DONG`, An | Lập C01 | 201, C01 `LAP` | A | UC-11 |
| TC-BR11-02 | BR-11 | ✖ | X3 `NGUNG`, An | Lập C01 với X3 | 422 `BR-11`; `xe-kha-dung` liệt kê X3 kèm lý do "xe ngừng hoạt động" | A | UC-11 |
| TC-BR12-01 | BR-12 | ✖ | X2 (đăng kiểm 19/10, bảo hiểm 31/12/2026), An (C ⊇ B) | Lập C01 với X2 | 422 `BR-12`: đăng kiểm 19/10 < ngày kết thúc 20/10 | U | UC-11 |
| TC-BR12-02 | BR-12 | ✔ biên | X2 sửa đăng kiểm thành 20/10/2026 | Lập C01 với X2 | Lập được: hạn = ngày kết thúc (≥) | U | UC-11 |
| TC-BR13-01 | BR-13 | ✖ | X5 (bảo hiểm 19/10), An | Lập C01 với X5 | 422 `BR-13`; đăng kiểm 30/11 vẫn đạt | U | UC-11 |
| TC-BR13-02 | BR-13 | ✔ biên | X5 sửa bảo hiểm thành 20/10/2026 | Lập C01 với X5 | Lập được | U | UC-11 |
| TC-BR14-01 | BR-14 | ✔ | X1 (toàn bộ 9.500 kg), An hạng C | Lập C01 | Lập được | U | UC-11 |
| TC-BR14-02 | BR-14 | ✖ | X1, Bình hạng B | Lập C01 với Bình | 422 `BR-14`: xe 9.500 kg cần hạng C (ca biên 3.500 / 3.501 / 7.500 / 7.501 kg đã có ở `tests/unit/test_uc04_domain.py`) | U | UC-11 |
| TC-BR15-01 | BR-15 | ✖ | X1, Cường (GPLX hết 19/10) | Lập C01 với Cường | 422 `BR-15` | U | UC-11 |
| TC-BR15-02 | BR-15 | ✔ biên | Cường sửa hạn GPLX thành 20/10/2026 | Lập C01 với Cường | Lập được | U | UC-11 |
| TC-BR16-01 | BR-16 | ✖ | X1 đã có chuyến C02 (T01, tài xế Dũng) khởi hành 20/10 10:00 | Lập C01 với X1, An | 422 `BR-16`: [06:00, 11:30) chồng [10:00, …) | A | UC-11 |
| TC-BR16-02 | BR-16 | ✔ biên | C02 khởi hành 20/10 11:30 | Lập C01 với X1, An | Lập được: khoảng nửa mở, 11:30 không chồng 11:30 | U | UC-11 |
| TC-BR17-01 | BR-17 | ✖ | An đã có chuyến C00 (xe X6, 4 giờ lái) lúc 20/10 11:00 | Lập C01 với X1, An | 422 `BR-17`: [06:00, 11:30) chồng [11:00, …); giờ lái 8,5 giờ vẫn đạt | A | UC-11 |
| TC-BR17-02 | BR-17 | ✔ biên | C00 lúc 20/10 11:30 | Lập C01 với X1, An | Lập được | U | UC-11 |
| TC-BR18-01 | BR-18 | ✖ | An đã có chuyến 20/10 14:00 dài **6 giờ** lái (xe X6, không chồng giờ) | Lập C01 với X1, An | 422 `BR-18`: 4,5 + 6 = 10,5 > 10 giờ trong ngày 20/10 | U | UC-11 |
| TC-BR18-02 | BR-18 | ✔ biên | Như trên nhưng chuyến kia dài **5,5 giờ** | Lập C01 | Lập được: đúng 10 giờ (≤) | U | UC-11 |
| TC-BR19-01 | BR-19 | ✖ | An đã có **44 giờ** lái dự kiến trong tuần 19–25/10 (các ngày khác 20/10) | Lập C01 | 422 `BR-19`: 44 + 4,5 = 48,5 > 48 (tuần tính Thứ Hai–Chủ Nhật, chốt 30/10) | U | UC-11 |
| TC-BR19-02 | BR-19 | ✔ biên | An đã có 43,5 giờ trong tuần | Lập C01 | Lập được: đúng 48 giờ | U | UC-11 |
| TC-BR20-01 | BR-20 | ⚠ | T02: HCM 0′ → Cần Thơ 300′, không có điểm nghỉ | Lưu tuyến | 201 kèm cảnh báo `BR-20` (chạy liền 300′ > 240′), vẫn lưu | U | UC-05 |
| TC-BR20-02 | BR-20 | không ⚠ | T01 (đoạn 0→120′ và 120→270′) | Lưu tuyến | Không cảnh báo | U | UC-05 |
| TC-BR20-03 | BR-20 | không ⚠ biên | HCM 0′ → Tiền Giang 240′ (nghỉ) → Cần Thơ 300′ | Lưu tuyến | Không cảnh báo: đoạn đúng 240′ (chỉ cảnh báo khi > 4 giờ) | U | UC-05 |
| TC-BR21-01 | BR-21 | ⚠ | Ngày kiểm 25/10/2026, X8 đăng kiểm 20/11/2026 (còn 26 ngày) | Mở bảng cảnh báo | X8 có trong danh sách "giấy tờ sắp hết hạn" | A | UC-27 |
| TC-BR21-02 | BR-21 | không ⚠ | Ngày kiểm 25/10/2026, X1 đăng kiểm 30/11/2026 (còn 36 ngày) | Mở bảng cảnh báo | X1 không có trong danh sách | A | UC-27 |
| TC-BR21-03 | BR-21 | ⚠ biên | X8 sửa đăng kiểm thành 24/11/2026 (còn đúng 30 ngày) | Mở bảng cảnh báo | Có cảnh báo ("trong 30 ngày" gồm ngày thứ 30, chốt 30/10) | U | UC-27 |

### Nhóm C – Vòng đời chuyến (BR-22…30)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR22-01 | BR-22 | ✔ | T01, 20/10 06:00, X1, An | `POST /api/chuyen` | 201, C01 `LAP` | A | UC-11 |
| TC-BR22-02 | BR-22 | ✖ | Thiếu `xe_id` (hoặc thiếu `tai_xe_id`) | `POST /api/chuyen` | 400, không tạo chuyến | A | UC-11 |
| TC-BR23-01 | BR-23 | ✔ | C01 `LAP` có Đ1, Đ2, Đ4 | Chốt | `DA_CHOT`; lưu định mức, lương và ETA kế hoạch (BR-71) | A | UC-15 |
| TC-BR23-02 | BR-23 | ✖ | C03 = T01, X1, An, 21/10 06:00, **0 đơn** | Chốt, không gửi `xac_nhan_chay_rong` | 422 `BR-23`, vẫn `LAP` | A | UC-15 |
| TC-BR23-03 | BR-23 | ✔ | Như trên | Chốt với `xac_nhan_chay_rong=true` | `DA_CHOT`, `chay_rong = true` | A | UC-15 |
| TC-BR24-01 | BR-24 | ✖ | C01 `DA_CHOT`, tạm ứng 1.000.000 `HIEU_LUC` | Mở chốt | 409 `BR-24`, vẫn `DA_CHOT` | A | UC-15 |
| TC-BR24-02 | BR-24 | ✔ | Như trên, Kế toán ghi thu hồi khoản tạm ứng (`DA_THU_HOI`) | Mở chốt | Về `LAP` | A | UC-15 |
| TC-BR25-01 | BR-25 | ✔ | C01 `LAP` có Đ1, Đ2, Đ4 | Hủy, lý do "khách hoãn" | `HUY`; Đ1, Đ2, Đ4 về `CHO_GHEP`; các bản ghi ghép hết hiệu lực | A | UC-16 |
| TC-BR25-02 | BR-25 | ✖ | C01 `DA_CHOT` còn tạm ứng 1.000.000 `HIEU_LUC` | Hủy, có lý do | 409 `BR-25`, chuyến và đơn giữ nguyên | A | UC-16 |
| TC-BR25-03 | BR-25 | ✖ | C01 `DANG_CHAY` | Hủy | 409, không hủy | A | UC-16 |
| TC-BR25-04 | BR-25 | ✖ | C01 `LAP` | Hủy, không có lý do | 400 | A | UC-16 |
| TC-BR26-01 | BR-26 | ✔ | C01 `DA_CHOT` | An bấm Bắt đầu ngày 20/10 05:45, km 120.000 + ảnh | `DANG_CHAY` | A | UC-18 |
| TC-BR26-02 | BR-26 | ✖ sai ngày | Như trên | An bấm Bắt đầu ngày 19/10 22:00 | 422 `BR-26`, vẫn `DA_CHOT` | A | UC-18 |
| TC-BR26-03 | BR-26 | ✖ người | Như trên | Bình bấm Bắt đầu C01 | 403 (không phải tài xế của chuyến, BR-58) | A | UC-18 |
| TC-BR28-01 | BR-28 | ✖ | C01 `DANG_CHAY`: Đ2, Đ4 `DA_GIAO`, Đ1 còn `DA_LAY` | An bấm Kết thúc, km 120.178 | 422 `BR-28`, trả danh sách đơn còn lại (Đ1), vẫn `DANG_CHAY` | A | UC-18 |
| TC-BR28-02 | BR-28 | ✔ | Đ1 `THAT_BAI`, Đ2, Đ4 `DA_GIAO` | An bấm Kết thúc, km 120.178 + ảnh | `HOAN_THANH` | A | UC-18 |
| TC-BR29-01 | BR-29 | ✔ | C01 `HOAN_THANH` | An ghi chi phí phát sinh 50.000 + ảnh | Lưu, `CHO_DUYET` | A | UC-21 |
| TC-BR29-02 | BR-29 | ✖ | C01 `DA_QUYET_TOAN` | An ghi chi phí 50.000; Kế toán sửa khoản dầu 520.000 → 500.000 | Cả hai 409, số liệu không đổi | A | UC-24 |
| TC-BR30-01 | BR-30 | = | C01 `LAP` | Chốt C01 (người làm: Điều phối `dp1`) | `LICH_SU_TRANG_THAI` thêm 1 dòng: `CHUYEN`, C01, `LAP` → `DA_CHOT`, người `dp1`, thời điểm giờ máy chủ | A | UC-15 |
| TC-BR30-02 | BR-30 | = | Đ4 `CHO_GHEP` | Ghép Đ4 vào C01 | `LICH_SU_TRANG_THAI` thêm dòng `DON`, Đ4, `CHO_GHEP` → `DA_GHEP` | A | UC-13 |

### Nhóm D – Đơn hàng (BR-31…37, 69)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR31-01 | BR-31 | ✔ | Đ1 | Tạo đơn | 201, `CHO_GHEP` | A | UC-08 |
| TC-BR31-02 | BR-31 | ✖ | Như Đ1 nhưng kg = 0 (riêng: m³ = 0; số kiện = 0) | Tạo đơn | 400, không lưu (biên 0,01 kg, 0,01 m³, 1 kiện thì được) | A | UC-08 |
| TC-BR31-03 | BR-31 | ✖ | Như Đ1 nhưng địa chỉ giao = địa chỉ lấy "12 Nguyễn Huệ, Quận 1" | Tạo đơn | 422 `BR-31` | A | UC-08 |
| TC-BR31-04 | BR-31 | ✖ | Như Đ1 nhưng hạn giao = đúng thời điểm tạo | Tạo đơn | 422 `BR-31` (hạn giao phải > thời điểm tạo) | A | UC-08 |
| TC-BR31-05 | BR-31 | ✖ | Như Đ2 nhưng khung lấy 09:00–06:30 (từ > đến) | Tạo đơn | 422 `BR-31` | A | UC-08 |
| TC-BR32-01 | BR-32 | = | Đ1 đã tạo khi giá HCM→Cần Thơ 1.500 | Quản lý đổi giá thành 1.800; xem Đ1; tạo đơn mới giống hệt Đ1 | Đ1 vẫn 2.997.000 và `don_gia_chot` 1.500; đơn mới 1.998 × 1.800 = 3.596.400 → làm tròn lên **3.597.000** | A | UC-08 |
| TC-BR33-01 | BR-33 | ✔ | Đ4 `CHO_GHEP` (bản sao giá 1.000); Quản lý đã đổi giá HCM→Tiền Giang thành 1.200 | Sửa Đ4 kg 800 → 900 | 200; cước tính lại từ bản sao: 900 × 1.000 = **900.000** (không dùng giá mới) | A | UC-10 |
| TC-BR33-02 | BR-33 | ✖ | Đ1 `DA_LAY` | Sửa kg Đ1 | 409, không đổi | A | UC-10 |
| TC-BR34-01 | BR-34 | ✔ | Đ8 `CHO_GHEP` | Hủy Đ8, lý do "khách hủy" | `HUY` | A | UC-10 |
| TC-BR34-02 | BR-34 | ✔ | Đ4 `THAT_BAI`, **chưa có** lượt quét lấy (không lấy được) | Hủy Đ4 | `HUY` | A | UC-22 |
| TC-BR34-03 | BR-34 | ✖ | Đ1 `DA_LAY` | Hủy Đ1 | 409, không hủy | A | UC-10 |
| TC-BR34-04 | BR-34 | ✖ | Đ1 `THAT_BAI`, **đã có** lượt quét lấy | Hủy Đ1 | 422 `BR-34`, không hủy (chỉ được ghép lại hoặc trả hàng; 422 theo chốt 30/10) | A | UC-22 |
| TC-BR35-01 | BR-35 | ✖ | Đ1 `DA_LAY` | Quét giao gửi thêm trường số kiện giao (20/40) | 400 (không có trường giao một phần); Đ1 vẫn `DA_LAY` | A | UC-20 |
| TC-BR35-02 | BR-35 | review | — | Xem thiết kế: kết quả giao chỉ có `DA_GIAO` hoặc `THAT_BAI`, cho toàn bộ đơn | Không có trạng thái "giao một phần" | — | UC-20 |
| TC-BR36-01 | BR-36 | = | C01 vừa `HOAN_THANH`, Đ1 `THAT_BAI` | Kết thúc chuyến | Bản ghi ghép của Đ1 chuyển `hieu_luc = false` | A | UC-18 |
| TC-BR36-02 | BR-36 | ✔ | Đ1 `THAT_BAI`, đã lấy | Trả hàng | `TRA_HANG`, không sinh doanh thu | A | UC-22 |
| TC-BR36-03 | BR-36 | ✖ | Đ4 `THAT_BAI`, chưa lấy | Trả hàng | 422 `BR-36` (chưa lấy hàng thì không có gì để trả; chỉ ghép lại hoặc hủy) | A | UC-22 |
| TC-BR37-01 | BR-37 | ✖ | Đ1 đã **3** lần giao thất bại lý do "người nhận vắng" (phía `KHACH`) | Ghép lại | 422 `BR-37`; trả hàng vẫn được | A | UC-22 |
| TC-BR37-02 | BR-37 | ✔ | Đ1: 2 lần phía khách + 1 lần "sự cố xe" | Ghép lại (có nơi giữ hàng) | Được: chỉ đếm 2 < 3 | U | UC-22 |
| TC-BR37-03 | BR-37 | ✔ | Đ4: 3 lần **không lấy được** phía khách, chưa lần giao nào | Ghép lại | Được: thất bại khi lấy không tính | U | UC-22 |
| TC-BR69-01 | BR-69 | ✔ | Đ1 `THAT_BAI`, đã lấy | Ghép lại: nơi giữ hàng kho Cần Thơ, hạn mới 21/10 17:00 | `CHO_GHEP`; điểm lấy mới = kho Cần Thơ; cước giữ 2.997.000 | A | UC-22 |
| TC-BR69-02 | BR-69 | ✖ | Như trên | Ghép lại **không** gửi nơi giữ hàng | 422 `BR-69`, vẫn `THAT_BAI` | A | UC-22 |

### Nhóm E – Quét mã (BR-38…45)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR38-01 | BR-38 | ✔ | C01 `DANG_CHAY` của An | An quét lấy Đ1 | 200, Đ1 `DA_LAY` | A | UC-19 |
| TC-BR38-02 | BR-38 | ✖ người | Như trên | Bình quét Đ1 | 403 (đơn không thuộc chuyến của Bình, chống IDOR) | A | UC-19 |
| TC-BR38-03 | BR-38 | ✖ trạng thái | C01 còn `DA_CHOT` | An quét Đ1 | 409 (chuyến chưa `DANG_CHAY`) | A | UC-19 |
| TC-BR39-01 | BR-39 | ✔ | Đ4 `DA_GHEP` trong C01 đang chạy | Báo không lấy được: lý do phía khách + 1 ảnh | Đ4 `THAT_BAI`, lượt quét `KHONG_LAY` | A | UC-19 |
| TC-BR39-02 | BR-39 | ✖ | Đ1 đã `DA_LAY` | Báo không lấy được Đ1 | 409, Đ1 vẫn `DA_LAY` | A | UC-19 |
| TC-BR40-01 | BR-40 | ✔ | Đ4 `DA_LAY` | Quét giao đủ ảnh, chữ ký, tên | `DA_GIAO` | A | UC-20 |
| TC-BR40-02 | BR-40 | ✖ | Đ2 còn `DA_GHEP` (chưa lấy) | Quét giao Đ2 | 409 "đơn chưa được quét lấy" | A | UC-20 |
| TC-BR41-01 | BR-41 | ✔ | Đ4 `DA_LAY` | Giao: 1 ảnh, chữ ký, tên "Lê Văn Nhận" | `DA_GIAO` | A | UC-20 |
| TC-BR41-02 | BR-41 | ✖ | Như trên | Giao thiếu chữ ký (riêng: thiếu ảnh; thiếu tên) | 422 `BR-41`, Đ4 vẫn `DA_LAY` | A | UC-20 |
| TC-BR42-01 | BR-42 | ✔ | Đ1 `DA_LAY` | Báo giao không được: lý do "người nhận vắng" + 1 ảnh | `THAT_BAI` | A | UC-20 |
| TC-BR42-02 | BR-42 | ✖ | Như trên | Báo giao không được, không có ảnh (riêng: không có lý do) | 422 `BR-42`, Đ1 vẫn `DA_LAY` | A | UC-20 |
| TC-BR43-01 | BR-43 | ⚠ | C01 đang chạy | An quét lấy Đ1 không gửi `lat`, `lng` | 200, lưu lượt quét, `thieu_gps = true`, `canh_bao` có `THIEU_GPS` | A | UC-19 |
| TC-BR43-02 | BR-43 | không ⚠ | Như trên | Quét có GPS | `thieu_gps = false`; giờ quét = giờ máy chủ (gửi trường thời gian → 400) | A | UC-19 |
| TC-BR45-01 | BR-45 | = | Đ1 vừa quét lấy thành công | Quét lấy Đ1 lần 2 (mạng chập chờn) | 200, `lap_lai = true`, trạng thái `DA_LAY`; số `LUOT_QUET` của Đ1 vẫn là 1 | A | UC-19 |

### Nhóm F – Cước, chi phí, tạm ứng, quyết toán, công nợ (BR-46…56, 62)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR46-01 | BR-46 | = | Đ1 6 m³ | Tính cước | KL quy đổi 6 × 333 = **1.998 kg** | U | UC-08 |
| TC-BR46-02 | BR-46 | = biên | 0,01 m³ | Tính cước | KL quy đổi **3,33 kg** (không làm tròn KL) | U | UC-08 |
| TC-BR47-01 | BR-47 | = | Đ8: 300 kg, 1 m³, HCM→Tiền Giang 1.000 đ/kg | Tạo đơn | KL tính cước 333 kg, cước 333.000 | U | UC-08 |
| TC-BR47-02 | BR-47 | = | Đ4: 800 kg, 2 m³ (quy đổi 666) | Tạo đơn | KL tính cước **800** (kg thực lớn hơn), cước 800.000 | U | UC-08 |
| TC-BR48-01 | BR-48 | = làm tròn | Đ3: 1.665 kg × 1.300 | Tạo đơn | 2.164.500 → làm tròn **lên** 2.165.000 | U | UC-08 |
| TC-BR48-02 | BR-48 | ✖ | Đ7 Cần Thơ → Cà Mau, không có giá | Tạo đơn | 422 `BR-48`, không tạo đơn | A | UC-08 |
| TC-BR48-03 | BR-48 | = tối thiểu | Đ15: 20 kg, 0,05 m³ (quy đổi 16,65), HCM→Tiền Giang | Tạo đơn | 20 × 1.000 = 20.000 < 50.000 → cước **50.000** | U | UC-08 |
| TC-BR48-04 | BR-48 | = biên | Đ4: 800.000 đã tròn nghìn | Tạo đơn | Giữ **800.000** (không làm tròn lên thêm 1.000) | U | UC-08 |
| TC-BR49-01 | BR-49 | = | C01 đổi xe X7 (tải 1.900 kg, 12 m³), chỉ có Đ1 (1.800 kg thực, KL tính cước 1.998) | Ghép Đ1 | Ghép được: kiểm tải dùng **1.800** ≤ 1.900 (nếu dùng 1.998 thì đã vượt) | U | UC-13 |
| TC-BR50-01 | BR-50 | = | C01 quyết toán: Đ2, Đ4 `DA_GIAO`, Đ1 `THAT_BAI` | Tính doanh thu C01 | 1.440.000 + 800.000 = **2.240.000**; Đ1 = 0 trên C01 | U | UC-24 |
| TC-BR50-02 | BR-50 | = | Đ1 ghép lại vào C05 (21/10) và giao thành công | Tính doanh thu C05 | Có 2.997.000 của Đ1 | U | UC-24 |
| TC-BR51-01 | BR-51 | = | C01: doanh thu 2.240.000, chi đã duyệt 1.050.000, lương chốt 600.000 | Tính lãi | **590.000** | U | UC-24 |
| TC-BR51-02 | BR-51 | = | Như trên nhưng kết thúc do sự cố, lương nhập tay 300.000 | Tính lãi | 2.240.000 − 1.050.000 − 300.000 = **890.000** | U | UC-24 |
| TC-BR52-01 | BR-52 | không ⚠ | C01 có Đ1, Đ2, Đ4 | Chốt | Lãi dự kiến 5.237.000 − 1.000.000 − 600.000 = **3.637.000**, không cảnh báo | U | UC-15 |
| TC-BR52-02 | BR-52 | ⚠ | C01 chỉ có Đ8 | Chốt, không gửi `xac_nhan_lai_am` | Lãi dự kiến 333.000 − 1.000.000 − 600.000 = **−1.267.000** → cảnh báo, chưa chốt; gửi `xac_nhan_lai_am=true` thì chốt được | A | UC-15 |
| TC-BR53-01 | BR-53 | ✔ | C01 `DA_CHOT`, định mức chốt 1.000.000 | Cấp tạm ứng 1.000.000 | `HIEU_LUC` | A | UC-23 |
| TC-BR53-02 | BR-53 | ✖ | Như trên | Cấp 1.200.000 | 422 `BR-53`, không lưu | A | UC-23 |
| TC-BR53-03 | BR-53 | ✔ biên | Như trên | Cấp 600.000 rồi 400.000 | Cả hai được, tổng đúng 1.000.000 | A | UC-23 |
| TC-BR53-04 | BR-53 | ✖ biên | Đã có tổng 1.000.000 | Cấp thêm 1 đ | 422 `BR-53` | A | UC-23 |
| TC-BR53-05 | BR-53 | ✖ | Khoản 1.000.000 `HIEU_LUC` | Sửa thành 1.100.000 (có lý do) | 422 `BR-53`, khoản giữ 1.000.000 | A | UC-23 |
| TC-BR53-06 | BR-53 | ✖ | C01 còn `LAP` (riêng: C01 đã `HOAN_THANH`) | Cấp 500.000 | 409, không lưu | A | UC-23 |
| TC-BR54-01 | BR-54 | ✔ | C01 `DANG_CHAY` | An ghi dầu 520.000, 26 lít, ghi chú, 1 ảnh hóa đơn | Lưu `CHO_DUYET` | A | UC-21 |
| TC-BR54-02 | BR-54 | ✖ | Như trên | Ghi số tiền 0 (riêng: thiếu ghi chú; thiếu ảnh) | 400/422, không lưu | A | UC-21 |
| TC-BR54-03 | BR-54 | ✖ | Như trên | Ghi dầu 520.000 **không có số lít** | 400, không lưu | A | UC-21 |
| TC-BR55-01 | BR-55 | ✔ | C01 `HOAN_THANH`, 3 khoản đã duyệt (1.050.000), tạm ứng 1.000.000 | Quyết toán, ghi `CONG_TY_DA_TRA`, tiền mặt | `DA_QUYET_TOAN`; chênh lệch **−50.000** | A | UC-24 |
| TC-BR55-02 | BR-55 | ✖ | Như trên nhưng khoản bốc xếp 300.000 còn `CHO_DUYET` | Quyết toán | 409 `BR-55`, vẫn `HOAN_THANH` | A | UC-24 |
| TC-BR55-03 | BR-55 | ✖ | Như TC-BR55-01 | Quyết toán **không** gửi cách xử lý chênh lệch | 422 `BR-55` | A | UC-24 |
| TC-BR55-04 | BR-55 | ✖ | Như TC-BR55-01 | Gửi `TAI_XE_DA_NOP` (sai dấu: chênh lệch âm) | 422 `BR-55` | A | UC-24 |
| TC-BR55-05 | BR-55 | ✖ | C01 còn `DANG_CHAY` | Quyết toán | 409 | A | UC-24 |
| TC-BR56-01 | BR-56 | = | Đ4 vừa `DA_GIAO` | Quét giao Đ4 | Sinh `PHAI_THU` 800.000 `CHUA_THU`; Đ1 `THAT_BAI` không sinh phải thu | A | UC-20 |
| TC-BR56-02 | BR-56 | = | Đ2, Đ4 `DA_GIAO` của Cty B (2.240.000) | Kế toán đánh dấu đã thu cả hai trong **một** lần | Cả hai `DA_THU`; trạng thái vòng đời đơn vẫn `DA_GIAO` | A | UC-25 |
| TC-BR62-01 | BR-62 | = | C01 `DA_CHOT` | Cấp tạm ứng 1.000.000 rồi thu hồi | `NHAT_KY_TIEN` có 2 dòng: `TAO` (cũ rỗng, mới 1.000.000) và `THU_HOI`; mỗi dòng có người làm, giờ máy chủ, lý do | A | UC-23 |
| TC-BR62-02 | BR-62 | ✖ | Đã có dòng nhật ký | Gọi sửa hoặc xóa nhật ký | Không có endpoint (404/405); dòng giữ nguyên | A | UC-23 |

### Nhóm G – Phân quyền, tra cứu, dữ liệu (BR-57…60)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR57-01 | BR-57 | ✔ | Điều phối đăng nhập | `POST /api/chuyen` | 201 | A | UC-11 |
| TC-BR57-02 | BR-57 | ✖ | Tài xế An đăng nhập (riêng: Kế toán) | `POST /api/chuyen` | 403 (mọi UC đều có ca này trong test của story) | A | UC-11 |
| TC-BR57-03 | BR-57 | ✖ | Chưa đăng nhập | `GET /api/chuyen` | 401 | A | UC-11 |
| TC-BR58-01 | BR-58 | ✔ | C01 của An | An `GET /api/toi/chuyen/{C01}` | 200, thấy lịch trình | A | UC-17 |
| TC-BR58-02 | BR-58 | ✖ | Như trên | Bình `GET /api/toi/chuyen/{C01}` | 403 | A | UC-17 |
| TC-BR59-01 | BR-59 | ✔ | Đ1 (SĐT gửi 0909123456, nhận 0909555666) | Tra cứu mã Đ1 + "3456" (riêng: + "5666") | 200: trạng thái và mốc thời gian; **không** có cước, GPS, SĐT tài xế | A | UC-28 |
| TC-BR59-02 | BR-59 | ✖ | Như trên | Tra cứu mã Đ1 + "0000" (riêng: mã không tồn tại) | 404 cùng thông báo "Không tìm thấy đơn" cho cả hai (không lộ mã có tồn tại) | A | UC-28 |
| TC-BR59-03 | BR-59 | ✖ | Một IP | Tra cứu sai 11 lần trong 1 phút | Lần 11 → 429 | A | UC-28 |
| TC-BR60-01 | BR-60 | ✖ | X1 đã có chuyến C01 | `DELETE /api/xe/{X1}` (tương tự tài xế, tuyến, khách) | 405, X1 còn nguyên | A | UC-03 |
| TC-BR60-02 | BR-60 | ✔ | Như trên | Sửa X1 trạng thái `NGUNG` | 200 `NGUNG`; lịch sử chuyến C01 giữ nguyên | A | UC-03 |

### Nhóm H – Thời gian, sự kiện chuyến (BR-63…73)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|
| TC-BR63-01 | BR-63 | = | C01 có Đ1, Đ2, Đ4, khởi hành 06:00, `CFG-08` = 20′ | Tính lịch trình | 6 điểm, ETA 06:00 / 06:20 / 07:40 / 09:00 / 11:50 (giao Đ2) / 12:10 (giao Đ1) | U | UC-13 |
| TC-BR63-02 | BR-63 | ✖ thứ tự | Như trên, nếu xếp giao Đ1 trước Đ2 ở Cần Thơ | Kiểm thứ tự | Hàm phải xếp Đ2 (hạn 12:00) trước Đ1 (hạn 14:00); xếp ngược thì Đ2 12:10 > 12:00 – test assert thứ tự đúng | U | UC-13 |
| TC-BR63-03 | BR-63 | = thứ tự lấy | C01 có Đ1 (không khung) và Đ14 (khung 06:00–07:00), cùng lấy ở HCM | Tính lịch trình | Lấy Đ14 06:00 trước, lấy Đ1 06:20 sau (có khung xếp trước) | U | UC-13 |
| TC-BR63-04 | BR-63 | = thứ tự lấy | C01 có Đ1, Đ4 (đều không khung, cùng HCM) | Tính lịch trình | Xếp theo mã đơn: Đ1 trước Đ4 | U | UC-13 |
| TC-BR64-01 | BR-64 | = | C01 có Đ1, Đ2, Đ4 | Tính kết thúc dự kiến | 12:10 + 20′ + 60′ = **13:30**, khoảng chiếm [06:00, 13:30) | U | UC-13 |
| TC-BR64-02 | BR-64 | = | C01 rỗng | Tính kết thúc dự kiến | 06:00 + 270′ + 60′ = **11:30** | U | UC-11 |
| TC-BR65-01 | BR-65 | = | C01 | Tính giờ lái | **4,5 giờ** (270′, không tính phút dừng và CFG-05) | U | UC-11 |
| TC-BR65-02 | BR-65 | = qua nửa đêm | T01, khởi hành 20/10 **22:00** | Tính giờ lái theo ngày | Ngày 20/10: **2 giờ** (22:00–24:00); ngày 21/10: **2,5 giờ** | U | UC-11 |
| TC-BR66-01 | BR-66 | ✔ biên | Tuyến nút cuối 600′ (các đoạn ≤ 240′ để không lẫn BR-20) | Lưu tuyến | 201 | U | UC-05 |
| TC-BR66-02 | BR-66 | ✖ | Như trên nhưng nút cuối 601′ | Lưu tuyến | 422 `BR-66` | U | UC-05 |
| TC-BR67-01 | BR-67 | ✖ ghép | C01 có Đ1, Đ2, Đ4 | Ghép Đ8 | 422, vi phạm `BR-06` ở **Đ2** (ETA 12:30 > 12:00), không ghép | U | UC-13 |
| TC-BR67-02 | BR-67 | ✖ gỡ | C01 có Đ1, Đ4, Đ2c (khung 07:40–09:00, ETA lấy 07:40) | Gỡ Đ4 | 422 `BR-05` ở Đ2c: ETA lấy dịch về 06:00 + 60′ + 1 × 20′ = 07:20 < 07:40 → không gỡ | U | UC-13 |
| TC-BR67-03 | BR-67 | ✖ đổi xe | C01 có Đ1, Đ2, Đ4 (3.800 kg, 11 m³) | Đổi xe sang X7 (1.900 kg, 12 m³) | 422 `BR-01` (3.800 > 1.900), thể tích vẫn đạt; giữ X1 | U | UC-12 |
| TC-BR67-04 | BR-67 | ✖ lịch | An có C00 (xe X6) lúc 20/10 13:00; C01 rỗng (chiếm tới 11:30, lập được) có Đ1, Đ4 (giao Đ1 lúc 11:30, kết thúc 12:50, chưa chồng) | Ghép Đ2 | 422 `BR-17`: kết thúc dự kiến thành 13:30, [06:00, 13:30) chồng [13:00, …) | A | UC-13 |
| TC-BR68-01 | BR-68 | ✔ | C01 `DANG_CHAY`: Đ1, Đ2 `DA_LAY`, Đ4 `DA_GIAO`; km bắt đầu 120.000 | Điều phối kết thúc do sự cố, lý do "hỏng hộp số", km 120.090 | `HOAN_THANH`, `ket_thuc_bat_thuong = true`; Đ1, Đ2 `THAT_BAI` lý do "sự cố xe" (không tính BR-37); `km_dong_ho` X1 = 120.090 | A | UC-32 |
| TC-BR68-02 | BR-68 | ✖ | Như trên | Kết thúc do sự cố, không có lý do | 400, vẫn `DANG_CHAY` | A | UC-32 |
| TC-BR68-03 | BR-68 | ✖ | C01 còn `DA_CHOT` (riêng: An gọi API này) | Kết thúc do sự cố | 409 (riêng: 403) | A | UC-32 |
| TC-BR68-04 | BR-68 | = | Như TC-BR68-01 nhưng không nhập km | Kết thúc do sự cố | `km_ket_thuc` rỗng, `km_dong_ho` X1 giữ 120.000 | A | UC-32 |
| TC-BR70-01 | BR-70 | ✔ biên | X1 `km_dong_ho` 120.000, chuyến đầu | Bắt đầu C01 km **120.000** | Được (≥) | A | UC-18 |
| TC-BR70-02 | BR-70 | ✖ | Như trên | Bắt đầu C01 km 119.999 | 422 `BR-70`, vẫn `DA_CHOT` | A | UC-18 |
| TC-BR70-03 | BR-70 | ✖ biên | C01 bắt đầu 120.000 | Kết thúc km **120.000** | 422 `BR-70` (phải > km bắt đầu) | A | UC-18 |
| TC-BR70-04 | BR-70 | ✔ | Như trên | Kết thúc km 120.178 + ảnh | `HOAN_THANH`; `km_dong_ho` X1 = 120.178 | A | UC-18 |
| TC-BR70-05 | BR-70 | ✔ | Chuyến trước của X1 kết thúc do sự cố, không có km cuối, km bắt đầu 120.000 | Bắt đầu chuyến sau km 120.050 | Được: so với km bắt đầu 120.000 của chuyến sự cố | A | UC-18 |
| TC-BR71-01 | BR-71 | = | C01 `LAP` có Đ1, Đ2, Đ4 | Chốt; sau đó Điều phối sửa định mức dầu T01 thành 600.000 | C01 giữ `dm_dau_chot` 550.000, cầu đường 200.000, bốc xếp 250.000, lương 600.000; ETA kế hoạch 6 điểm như TC-BR63-01 | A | UC-15 |
| TC-BR71-02 | BR-71 | = | Như trên, mở chốt (không có tạm ứng) rồi chốt lại | Chốt lại | `dm_dau_chot` thành 600.000 (lưu lại theo số mới) | A | UC-15 |
| TC-BR72-01 | BR-72 | ⚠ | Đ2 `DA_LAY`, hạn 20/10 12:00 | Quét giao lúc 12:35 | `DA_GIAO`, `giao_tre = true`, `canh_bao` có `GIAO_TRE`; cước giữ 1.440.000 | A | UC-20 |
| TC-BR72-02 | BR-72 | không ⚠ | Đ4 `DA_LAY`, hạn 18:00 | Quét giao lúc 09:40 | `DA_GIAO`, `giao_tre = false` | A | UC-20 |
| TC-BR73-01 | BR-73 | ⚠ | C01 đang chạy, C00 của An lúc 13:45 | Quét lấy Đ2 lúc 08:10 | Trễ 30′ > `CFG-09`, dự kiến xong 14:00 chồng C00 → cảnh báo | A | UC-32 |
| TC-BR73-02 | BR-73 | không ⚠ | Như trên nhưng C00 lúc 14:00 | Quét lấy Đ2 lúc 08:10 | `[06:00, 14:00)` không chồng `[14:00, …)` → không cảnh báo | U | UC-32 |
| TC-BR73-03 | BR-73 | không ⚠ | C00 lúc 13:45 | Quét lấy Đ4 lúc 06:30 (ETA kế hoạch 06:20) | Trễ 10′ ≤ 15′: không cờ trễ; dự kiến xong 13:40, không chồng → không cảnh báo | U | UC-32 |
| TC-BR73-04 | BR-73 | ⚠ đơn chờ | Đ8 `CHO_GHEP`, hạn 20/10 18:00; bây giờ 19/10 20:00 (còn 22 giờ) | Mở bảng cảnh báo | Đ8 có trong "đơn chờ sắp quá hạn" | A | UC-27 |
| TC-BR73-05 | BR-73 | không ⚠ biên | Như trên, bây giờ 19/10 18:00 (còn **đúng 24 giờ**) | Mở bảng cảnh báo | Không có Đ8 ("còn **dưới** 24 giờ" mới cảnh báo) | U | UC-27 |

## 5. Độ phủ và câu hỏi đã chốt (Kiệt 29/10, Tài chốt 30/10)

**Độ phủ:** mọi BR còn hiệu lực trong `nghiep-vu.md` 0.5 đã có ca theo mục 1 – **70 BR, 180 ca** (BR-27, 44, 61 đã bỏ, không viết). Các BR Tài rà ngày 16/10 là "chưa có ca" hoặc "thiếu ca ✖" đều đã có ca ở mục 4. BR-08, 10 và một ca của BR-35 là ca **review thiết kế**, không cần test chạy.

**Đã chốt 30/10** – Tài đồng ý cả 5 đề xuất, đã ghi vào `nghiep-vu.md` (BR-05, BR-19, BR-21, mục 11 bảng giá, ghi chú BR-34/36):

1. **BR-05 khung giờ lấy đóng hay mở ở hai đầu?** Đề xuất: đóng – ETA đúng bằng giờ đầu hoặc giờ cuối khung vẫn đạt (TC-BR05-04).
2. **BR-19 tuần tính thế nào?** Đề xuất: Thứ Hai 00:00 → Chủ Nhật 24:00 theo giờ Việt Nam (TC-BR19-01).
3. **BR-21 "hết hạn trong 30 ngày"** có gồm đúng ngày thứ 30 không? Đề xuất: có (TC-BR21-03).
4. **Cước tối thiểu 50.000** cho mọi cặp tỉnh trong kịch bản mục 11 (mục 11 chưa ghi cước tối thiểu). Đề xuất: thêm vào dòng bảng giá ở mục 11.
5. **Mã HTTP khi vi phạm điều kiện trạng thái kèm điều kiện dữ liệu** (ví dụ hủy đơn `THAT_BAI` đã lấy, TC-BR34-04; trả hàng đơn chưa lấy, TC-BR36-03): đề xuất 422 kèm mã BR vì đơn cùng trạng thái `THAT_BAI`, khác nhau ở dữ liệu lượt quét.

## 6. Xong khi

- Mọi BR còn hiệu lực có đủ ca theo mục 1; mục 5 không còn dòng nào.
- Mỗi ca có **Kết quả mong đợi** đủ cụ thể để viết assert (con số, trạng thái, mã lỗi), không ghi chung chung "báo lỗi".
- Tài đọc lại; thống nhất xong thì cập nhật trạng thái ở đầu file thành "đã chốt".
