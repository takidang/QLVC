# Dữ liệu thử giao diện UC-13 Ghép đơn

> Tách từ `docs/test-evidence/du-lieu-thu-giao-dien.md` ngày 01/11/2026 (luật tránh xung đột PR #7: mỗi UC một file).

Ảnh lưu vào `docs/test-evidence/UC-13/` · Dùng luôn **chuyến CH-261031-01** (X1, An, 06:00 ngày 31/10) vừa lập ở `docs/test-evidence/UC-11/du-lieu.md` ca c.

## Chuẩn bị

**Bảng giá** (menu Bảng giá → Thêm mức giá; mỗi dòng dưới là một lần thêm, nhập đủ 5 ô theo đúng thứ tự trên form):

| # | Tỉnh lấy | Tỉnh giao | Đơn giá (đồng/kg) | Cước tối thiểu (đồng) | Hiệu lực từ ngày |
|---|---|---|---|---|---|
| 1 | `Long An` | `Cần Thơ` | `1200` | `50000` | `01/10/2026` |
| 2 | `TP.HCM` | `Tiền Giang` | `1000` | `50000` | `01/10/2026` |

Tên tỉnh gõ **đúng như tên nút** (`TP.HCM`, `Long An`, `Tiền Giang`, `Cần Thơ`), nếu không thì tạo đơn sẽ báo "Chưa có bảng giá". Giá `TP.HCM → Cần Thơ` 1.500 đã có từ lần thử UC-08, không thêm lại.

**4 đơn** (menu Đơn hàng → Tạo đơn). Mỗi dòng là một đơn; các cột xếp **đúng thứ tự ô trên form** từ trái sang phải. Nút hiện dạng `tên (tỉnh)`, ví dụ `hcm1 (TP.HCM)`.

| Đơn | Khách hàng | Mô tả hàng | Khối lượng thực (kg) | Thể tích (m³) | Số kiện | Nút lấy | Địa chỉ lấy | Người liên hệ | SĐT lấy | Lấy từ | Lấy đến | Nút giao | Địa chỉ giao | Người nhận | SĐT nhận | Hạn giao | Cước tự hiện (kiểm, không nhập) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Đ1** | `Cty A` | `Hàng điện tử` | `1800` | `6` | `10` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `cantho1 (Cần Thơ)` | `45 Hòa Bình, Ninh Kiều` | `Chị Lan` | `0939111222` | `31/10/2026 14:00` | 2.997.000 |
| **Đ2** | `Cty A` | `Nông sản` | `1200` | `3` | `8` | `longan1 (Long An)` | `8 Quốc lộ 1A, Tân An` | `Chị Mai` | `0909555666` | `31/10/2026 06:30` | `31/10/2026 09:00` | `cantho1 (Cần Thơ)` | `10 Trần Hưng Đạo, Ninh Kiều` | `Anh Minh` | `0939222333` | `31/10/2026 12:00` | 1.440.000 |
| **Đ4** | `Cty A` | `Văn phòng phẩm` | `800` | `2` | `5` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `tiengiang1 (Tiền Giang)` | `5 Ấp Bắc, Mỹ Tho` | `Chị Hoa` | `0939333444` | `31/10/2026 18:00` | 800.000 |
| **Đ8** | `Cty A` | `Phụ tùng` | `300` | `1` | `2` | `hcm1 (TP.HCM)` | `12 Nguyễn Huệ, Quận 1` | `Anh Hùng` | `0909123456` | để trống | để trống | `tiengiang1 (Tiền Giang)` | `20 Lê Lợi, Mỹ Tho` | `Anh Tú` | `0939444555` | `31/10/2026 18:00` | 333.000 |

**Mã đơn hệ thống sinh trên máy Kiệt (30/10)** – mã ngẫu nhiên, máy khác sẽ khác:

| Đơn | Mã | Nhận biết |
|---|---|---|
| Đ1 | `DH-MSKG7T` | TP.HCM → Cần Thơ, 1.800 kg, hạn 14:00 31/10 |
| Đ2 | `DH-9ZTTPG` | Long An → Cần Thơ, 1.200 kg, lấy 06:30–09:00 |
| Đ4 | `DH-6HXV2Y` | TP.HCM → Tiền Giang, 800 kg |
| Đ8 | `DH-SZAK8H` | TP.HCM → Tiền Giang, 300 kg |
| bỏ qua | `DH-79S3VJ` | Đơn cũ lần thử UC-08 (hạn 26/10), **không tick** |

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Chuyến → bấm **mã CH-261031-01** | Trang chi tiết: lịch trình trống, **lãi dự kiến âm, tô đỏ** | `a-chuyen-trong.png` | Đạt (ảnh: lãi −1.600.000 đ chữ đỏ) |
| b | Ở "Đơn chờ ghép" tick `DH-MSKG7T` (Đ1) và `DH-6HXV2Y` (Đ4) → **Ghép đơn đã chọn** | Lịch trình **4 điểm** | `b-ghep-d1-d4.png` | Đạt (ảnh: 4 điểm, tải 2.600 kg, lãi 2.197.000 đ) |
| c | Tick `DH-9ZTTPG` (Đ2) → **Ghép đơn đã chọn** | 6 điểm, ETA **06:00 / 06:20 / 07:40 / 09:00 / 11:50** (giao Đ2) / **12:10** (giao Đ1); tải **3.800 / 5.000 kg**, lấp đầy **76%**, lãi **3.637.000 đ** | `c-ghep-don-d2.png` | Đạt (ảnh: đúng 6 ETA, 3.800/5.000 kg, 76%, 3.637.000 đ) |
| d | Tick `DH-SZAK8H` (Đ8) → **Ghép đơn đã chọn** | Bảng vi phạm: đơn **Đ2 (`DH-9ZTTPG`), BR-06**, ETA giao **12:30** sau hạn 12:00; Đ8 **không** được ghép | `d-vi-pham-thoi-gian-d8.png` | Đạt (ảnh: 1 dòng `DH-9ZTTPG` BR-06, ETA 12:30 sau hạn 12:00) |
| e | Ở "Đơn đang ghép" tick `DH-6HXV2Y` (Đ4) → **Gỡ đơn đã chọn** | Lịch trình còn **4 điểm**, Đ4 về danh sách chờ ghép | `e-go-don-d4.png` | Đạt (ảnh: còn 4 điểm, `DH-6HXV2Y` về chờ ghép) |

Ảnh phụ `f-don-qua-han-vuot-tai-trong-vipham.png`: lỡ tick đơn cũ `DH-79S3VJ` (1.800 kg, hạn 26/10) → bị chặn đủ 4 dòng: BR-01 tổng 5.600 kg > 5.000, BR-05 trễ khung lấy, BR-06 trễ hạn của chính nó và của `DH-9ZTTPG`. Đúng.

**Ghi chú cho Tài:** ở TP.HCM lịch trình lấy `DH-6HXV2Y` (Đ4) lúc 06:00 rồi `DH-MSKG7T` (Đ1) lúc 06:20; kịch bản mục 11 ghi lấy Đ1 trước. ETA các điểm sau vẫn đúng, chỉ khác thứ tự hai đơn lấy cùng nút.

Lãi ở ca c: cước 2.997.000 + 1.440.000 + 800.000 = 5.237.000 − định mức 1.000.000 − lương 600.000 = 3.637.000 đ.
Xong ghi kết quả vào dòng **AC13** của `docs/stories/UC-13-ghep-don.md`.
