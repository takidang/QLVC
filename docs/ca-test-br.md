# Danh sách ca test theo quy tắc nghiệp vụ (BR)

> Người làm: **Kiệt** · Nguồn: `docs/nghiep-vu.md` bản 0.5 (mục 4 quy tắc, mục 2.1 công thức, mục 11 kịch bản) · Trạng thái: **khung + ví dụ, Kiệt điền tiếp**.
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

## 4. Danh sách ca (Kiệt điền)

Xếp theo nhóm A…H như mục 4 của `nghiep-vu.md`. Chép các ví dụ ở mục 3 vào đúng chỗ.

### Nhóm A – Ghép đơn (BR-01…10)

| Mã ca | BR | Loại | Dữ liệu | Thao tác | Kết quả mong đợi | Mức | UC |
|---|---|---|---|---|---|---|---|

<!-- Tiếp tục cho nhóm B, C, D, E, F, G, H -->

## 5. Độ phủ của kịch bản mục 11 (Tài rà nhanh ngày 16/10, Kiệt kiểm lại)

Mục 11 đã có ca cho nhiều BR, nhưng còn thiếu. Đây là chỗ cần thêm dữ liệu:

- **Chưa có ca nào:** BR-02 (thể tích), 03 (nút ngoài tuyến), 07 (hai người ghép cùng đơn – test song song, mức A), 09, 11, 13, 15, 16, 19, 20, 21, 25, 30, 31, 33, 34, 36 (nhánh trả hàng, hủy), 38, 43, 49, 54, 57, 58, 60, 62, 66, 68.
- **Mới có ca ✔, thiếu ca ✖:** BR-05 (ETA ngoài khung giờ lấy), 18, 22, 23 (chạy rỗng chưa xác nhận), 26 (sai ngày, không phải tài xế của chuyến), 28 (còn đơn chưa có kết quả), 29 (sửa sau quyết toán), 35, 37 (đủ 3 lần thất bại phía khách), 39, 40 (quét sai trạng thái), 41 (thiếu chữ ký), 42 (thiếu ảnh), 52 (lãi âm), 55 (còn chi phí `CHO_DUYET`), 69 (ghép lại thiếu nơi giữ hàng), 70 (km nhỏ hơn chuyến trước).
- **BR-08, 10 kiểm bằng mô hình** (đơn không có số lượng con, không có bảng điểm dừng): ghi 1 ca review thiết kế, không cần test chạy.

## 6. Xong khi

- Mọi BR còn hiệu lực có đủ ca theo mục 1; mục 5 không còn dòng nào.
- Mỗi ca có **Kết quả mong đợi** đủ cụ thể để viết assert (con số, trạng thái, mã lỗi), không ghi chung chung "báo lỗi".
- Tài đọc lại; thống nhất xong thì cập nhật trạng thái ở đầu file thành "đã chốt".
