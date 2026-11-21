# Đặc tả yêu cầu – Hệ thống quản lý vận tải

> Phiên bản: 0.5 (Kiệt đề xuất, chờ Tài review) · Cập nhật: 15/10/2026 · Nhóm 8
> Quy tắc nghiệp vụ, trạng thái, cấu hình: xem `docs/nghiep-vu.md` (`BR-xx`, `ST-xx`, `CFG-xx`).
> Ưu tiên MoSCoW: **M** = phải có (bản demo), **S** = nên có, **C** = có thì tốt (làm nếu dư thời gian).
> Giữ mã UC của 0.4; UC bỏ ghi "Bỏ ở 0.5", không dùng lại số; UC mới từ UC-32.

---

## 1. Tác nhân

| Tác nhân | Mô tả | Thiết bị |
|---|---|---|
| Quản lý | Chủ/giám đốc doanh nghiệp. Quản trị người dùng, bảng giá, cấu hình; xem báo cáo, hiệu suất xe | Web máy tính |
| Điều phối viên | Nhận đơn từ khách, lập chuyến, ghép đơn, chốt chuyến, theo dõi chuyến, xử lý sự cố và đơn thất bại | Web máy tính |
| Tài xế | Bắt đầu/kết thúc chuyến kèm km, quét mã lấy/giao, chụp ảnh, lấy chữ ký, ghi chi phí, báo sự cố | Web responsive trên điện thoại |
| Kế toán | Cấp và thu hồi tạm ứng, quyết toán chuyến, theo dõi công nợ, nhập chi phí cố định xe | Web máy tính |
| Khách hàng | Tra cứu trạng thái đơn, không cần tài khoản | Web điện thoại/máy tính |
| Hệ thống (thời gian) | Tác nhân phụ: quét giấy tờ sắp hết hạn, chuyến trễ, đơn chờ sắp quá hạn (BR-21, 73) | — |

---

## 2. Danh sách use case

| Mã | Tên | Tác nhân chính | Phân hệ | Ưu tiên | BR liên quan |
|---|---|---|---|---|---|
| UC-01 | Đăng nhập / đăng xuất | Tất cả trừ Khách | Chung | M | BR-57 |
| UC-02 | Quản lý người dùng và vai trò | Quản lý | Chung | M | BR-57 |
| UC-03 | Quản lý xe (tải trọng, thể tích, giấy tờ, lít/100 km, km đồng hồ, chi phí cố định tháng) | Điều phối (chi phí cố định: Kế toán) | Xe/Tài xế | M | BR-11…13, 60 |
| UC-04 | Quản lý tài xế (GPLX, hạng, hạn) | Điều phối | Xe/Tài xế | M | BR-14, 15, 60 |
| UC-05 | Quản lý tuyến (nút, phút, km, điểm nghỉ, định mức, lương khoán) | Điều phối | Chuyến | M | BR-20, 60, 66 |
| UC-06 | Quản lý khách hàng | Điều phối | Đơn | M | BR-60 |
| UC-07 | Quản lý bảng giá và cấu hình | Quản lý | Đơn | M | BR-48, CFG-xx |
| UC-08 | Tạo đơn hàng, chốt cước, in phiếu QR | Điều phối | Đơn | M | BR-31, 32, 46–48 |
| UC-09 | ~~Xác nhận đơn~~ | | | | Bỏ ở 0.5 – gộp vào UC-08 vì cước chốt lúc tạo |
| UC-10 | Sửa / hủy đơn | Điều phối | Đơn | M | BR-33, 34, 67 |
| UC-11 | Lập chuyến (chọn tuyến, giờ, xe, tài xế đã lọc kèm lý do loại) | Điều phối | Chuyến | M | BR-11…19, 22, 64, 65 |
| UC-12 | Gán / đổi xe và tài xế (khi chuyến `LAP`) | Điều phối | Chuyến | M | BR-11…19, 67 |
| UC-13 | Ghép / gỡ đơn khỏi chuyến | Điều phối | Chuyến | M | BR-01…10, 52, 63, 67 |
| UC-14 | ~~Sắp xếp thứ tự điểm dừng~~ | | | | Bỏ ở 0.5 – điểm dừng suy ra tự động (BR-63) |
| UC-15 | Chốt / mở chốt chuyến | Điều phối | Chuyến | M | BR-23, 24, 52, 71 |
| UC-16 | Hủy chuyến | Điều phối | Chuyến | M | BR-25 |
| UC-17 | Xem chuyến được giao | Tài xế | Quét mã | M | BR-58 |
| UC-18 | Bắt đầu / kết thúc chuyến kèm km | Tài xế | Quét mã | M | BR-11…15, 26, 28, 70 |
| UC-19 | Quét mã lấy hàng / báo không lấy được | Tài xế | Quét mã | M | BR-38, 39, 42, 43, 45 |
| UC-20 | Quét mã giao hàng / báo giao không được | Tài xế | Quét mã | M | BR-35, 38, 40–43, 45, 72 |
| UC-21 | Ghi chi phí | Tài xế | Quyết toán | M | BR-54 |
| UC-22 | Xử lý đơn thất bại (ghép lại, trả hàng, hủy) | Điều phối | Đơn | M | BR-34, 36, 37, 69 |
| UC-23 | Cấp / sửa / thu hồi tạm ứng | Kế toán | Quyết toán | M | BR-53, 62 |
| UC-24 | Quyết toán chuyến | Kế toán | Quyết toán | M | BR-29, 50, 51, 55, 62, 68 |
| UC-25 | Công nợ: xem nợ theo khách, đánh dấu đã thu | Kế toán | Quyết toán | S | BR-56, 62 |
| UC-26 | Báo cáo lãi lỗ theo chuyến / xe / tháng | Quản lý | Quyết toán | S | BR-51 |
| UC-27 | Xem bảng cảnh báo (giấy tờ, trễ, sự cố, đơn chờ quá hạn, thiếu GPS) | Điều phối | Xe/Tài xế | S | BR-21, 43, 73 |
| UC-28 | Tra cứu đơn | Khách | Tra cứu | M | BR-59 |
| UC-29 | ~~Gợi ý ghép đơn (OR-Tools)~~ | | | | Bỏ ở 0.5 – hướng phát triển |
| UC-30 | Dự đoán nguy cơ trễ chuyến | Điều phối | Phụ trợ | C | — |
| UC-31 | ~~Điều chỉnh cước đơn~~ | | | | Bỏ ở 0.5 – hướng phát triển (BR-61) |
| UC-32 | Theo dõi chuyến (bảng chuyến trong ngày, chi tiết chuyến, cờ trễ, đóng sự cố, kết thúc do sự cố) | Điều phối | Chuyến | M | BR-68, 73 |
| UC-33 | Báo sự cố | Tài xế | Quét mã | M | BR-58 |
| UC-34 | Hiệu suất xe theo tháng | Quản lý | Quyết toán | S | — |
| UC-35 | Đổi mật khẩu của chính mình (giao diện v2: Cài đặt cá nhân) | Mọi vai trò | Chung | S | BR-57 |
| UC-36 | Tìm kiếm chung (ô tìm trên thanh đầu: chuyến, đơn, xe, tài xế, khách) | Mọi vai trò | Chung | S | BR-57, 58 |
| UC-37 | Thông báo theo vai trò (chuông trên thanh đầu) | Mọi vai trò | Chung | S | BR-57, 58 |
| UC-38 | Tổng quan hôm nay (số liệu một ngày cho trang đầu) | Quản lý, Điều phối, Kế toán | Quyết toán | S | BR-57, 73 |
| UC-39 | Hồ sơ cá nhân và ảnh đại diện (giao diện v3: trang Tài khoản) | Mọi vai trò | Chung | C | BR-14, 15, 57 |

Số UC còn hiệu lực: 31 − 4 (UC-09, 14, 29, 31) + 3 (UC-32, 33, 34) + 4 (UC-35…38, thêm 12/11/2026 cho giao diện v2) + 1 (UC-39, thêm 19/11/2026 cho giao diện v3) = **35**.
Ghi chú: UC-30 chỉ **gợi ý**; module phụ hỏng thì lõi vẫn chạy.

---

## 3. Đặc tả chi tiết các use case lõi

### UC-08 Tạo đơn hàng
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Đã đăng nhập vai trò Điều phối/Quản lý; khách đã có trong hệ thống (hoặc tạo nhanh tại chỗ).
- **Kích hoạt:** Khách gọi điện/nhắn yêu cầu gửi hàng.
- **Luồng chính:**
  1. Điều phối chọn khách, nhập hàng hóa (mô tả, kg thực, m³, số kiện), điểm lấy (địa chỉ, tỉnh, tọa độ chấm trên bản đồ Leaflet, người liên hệ, SĐT, khung giờ lấy nếu có), điểm giao (địa chỉ, tỉnh, tọa độ, người nhận, SĐT, hạn giao).
  2. Hệ thống kiểm BR-31.
  3. Hệ thống tính KL quy đổi, KL tính cước, cước (BR-46…48) và hiển thị.
  4. Điều phối lưu. Hệ thống tạo đơn `CHO_GHEP`, chốt cước và lưu bản sao giá (BR-32), sinh mã đơn duy nhất và mã QR.
- **Ngoại lệ:**
  - 2a. Vi phạm BR-31 → báo lỗi từng trường, không lưu.
  - 3a. Không có đơn giá cho cặp tỉnh (BR-48) → báo "chưa có bảng giá", **không tạo được đơn**.
- **Hậu điều kiện:** Đơn `CHO_GHEP`, cước đã chốt, phiếu QR in được.

### UC-11 Lập chuyến / UC-12 Gán, đổi xe và tài xế
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** UC-11: không có. UC-12: chuyến `LAP`.
- **Luồng chính:**
  1. Điều phối chọn tuyến và giờ khởi hành (UC-11) hoặc mở chuyến `LAP`, bấm "Đổi xe/tài xế" (UC-12).
  2. Hệ thống chỉ liệt kê xe và tài xế **khả dụng** cho khoảng chiếm của chuyến (BR-64; đã lọc BR-11…19), kèm lý do loại với xe/tài xế bị loại.
  3. Điều phối chọn xe và tài xế, bấm Lưu.
  4. Hệ thống kiểm lại BR-11…19 (tránh hai người gán cùng lúc); với UC-12 khi chuyến đã có đơn thì kiểm cả chuyến theo BR-67.
  5. UC-11: tạo chuyến ở `LAP` (BR-22). UC-12: lưu xe/tài xế mới.
- **Ngoại lệ:** 4a. Vi phạm bất kỳ BR nào → báo mã BR và nội dung vi phạm, không lưu.
- **Hậu điều kiện:** Chuyến `LAP` có xe + tài xế hợp lệ.

### UC-13 Ghép / gỡ đơn khỏi chuyến
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Chuyến `LAP`.
- **Luồng chính (ghép):**
  1. Điều phối mở chuyến (thẻ Hàng). Màn hình hiện: thanh tải (kg đã dùng / tải trọng), thanh thể tích, % đầy, lịch trình kèm ETA, lãi dự kiến (BR-52), danh sách đơn đang ghép, danh sách đơn `CHO_GHEP` **phù hợp tuyến** (đã lọc BR-03, BR-04).
  2. Điều phối chọn một hoặc nhiều đơn, bấm Ghép.
  3. Hệ thống tính lại lịch trình (BR-63, 64) và kiểm BR-01…09 cho đơn mới, rồi kiểm lại **cả chuyến** theo BR-67, trong một giao dịch.
  4. Hệ thống tạo bản ghi ghép hiệu lực, chuyển đơn → `DA_GHEP`, cập nhật lịch trình, % đầy, lãi dự kiến.
- **Luồng thay thế (gỡ):**
  - 2b. Điều phối chọn đơn đang ghép, bấm Gỡ → kiểm lại cả chuyến theo BR-67 → bản ghi ghép `hieu_luc = false`, đơn → `CHO_GHEP`.
- **Ngoại lệ:**
  - 3a. Có đơn vi phạm (kể cả đơn đã ghép trước đó bị dịch ETA) → **không ghép đơn nào** trong lô; hiện bảng: đơn nào, vi phạm BR nào, vượt bao nhiêu.
  - 3b. Đơn đã bị người khác ghép vào chuyến khác (BR-07) → báo xung đột, tải lại danh sách.
  - 2b-a. Gỡ làm đơn khác vi phạm (ví dụ ETA lấy sớm hơn khung giờ lấy, BR-05) → không gỡ, nêu đơn bị ảnh hưởng.
- **Hậu điều kiện:** Tổng kg, m³ của chuyến ≤ giới hạn xe; mọi đơn kịp khung giờ và hạn; mỗi đơn có đúng 1 ghép hiệu lực.

### UC-15 Chốt / mở chốt chuyến
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Chốt: chuyến `LAP`. Mở chốt: chuyến `DA_CHOT`.
- **Luồng chính (chốt):**
  1. Điều phối bấm Chốt.
  2. Hệ thống kiểm lại toàn bộ nhóm A, B (BR-23). Chuyến 0 đơn → yêu cầu xác nhận "chạy rỗng".
  3. Hệ thống tính lãi dự kiến (BR-52); nếu âm → hiện cảnh báo, yêu cầu xác nhận.
  4. Hệ thống lưu định mức chi phí, lương khoán và ETA kế hoạch của từng điểm dừng vào chuyến (BR-71). Chuyến → `DA_CHOT`; tài xế thấy chuyến ở UC-17.
- **Luồng thay thế (mở chốt):** Điều phối bấm Mở chốt → kiểm BR-24 (không còn tạm ứng `HIEU_LUC`) → chuyến về `LAP`.
- **Ngoại lệ:** 2a. Vi phạm (ví dụ đăng kiểm vừa hết hạn) → liệt kê mã BR, không chốt. Mở chốt khi còn tạm ứng → báo "cần Kế toán thu hồi tạm ứng trước".

### UC-16 Hủy chuyến
- **Tác nhân:** Điều phối viên · **Tiền điều kiện:** Chuyến ∈ {`LAP`, `DA_CHOT`}.
- **Luồng chính:** 1. Nhập lý do (bắt buộc). 2. Hệ thống kiểm BR-25: còn tạm ứng `HIEU_LUC` → từ chối, báo Kế toán thu hồi trước (UC-23). 3. Mọi ghép → không hiệu lực, đơn → `CHO_GHEP`. 4. Chuyến → `HUY`.

### UC-18 Bắt đầu / kết thúc chuyến
- **Tác nhân:** Tài xế
- **Luồng chính:**
  1. Tài xế mở chuyến `DA_CHOT` trong ngày khởi hành, nhập km đồng hồ, chụp ảnh đồng hồ, bấm **Bắt đầu** → kiểm BR-26 (gồm BR-11…15) và BR-70 → `DANG_CHAY`.
  2. Sau khi xử lý hết đơn (UC-19, UC-20), nhập km cuối kèm ảnh, bấm **Kết thúc** → kiểm BR-28, BR-70 → `HOAN_THANH`; cập nhật km đồng hồ của xe; các ghép của đơn `THAT_BAI` chuyển không hiệu lực (BR-36).
- **Ngoại lệ:** 1a. Giấy tờ vừa hết hạn → không cho bắt đầu, báo Điều phối. 1b. Km nhỏ hơn km cuối của xe → từ chối. 2a. Còn đơn chưa xử lý → hiện danh sách đơn còn lại, không cho kết thúc.

### UC-19 Quét mã lấy hàng
- **Tác nhân:** Tài xế
- **Tiền điều kiện:** Chuyến của tài xế ở `DANG_CHAY`; trình duyệt được cấp quyền camera.
- **Luồng chính:**
  1. Tài xế chọn điểm LẤY trong lịch trình, bấm Quét.
  2. Camera đọc QR; trình duyệt lấy GPS.
  3. Hệ thống kiểm BR-38, BR-39 → đơn `DA_LAY`; lưu giờ máy chủ, GPS (BR-43).
  4. Hiện xác nhận "Đã lấy: mã đơn, số kiện".
- **Luồng thay thế:**
  - 2a. Camera không đọc được → nhập mã đơn bằng tay (vẫn ghi GPS).
  - 1b. **Không lấy được:** tài xế chọn đơn, chọn lý do, chụp ảnh (BR-42) → `THAT_BAI`.
- **Ngoại lệ:**
  - 3a. Đơn không thuộc chuyến (BR-38) → báo "Đơn không thuộc chuyến của bạn".
  - 3b. Đơn đã lấy rồi → trả trạng thái hiện tại (BR-45).
  - 2b. Từ chối quyền GPS → vẫn lưu, gắn cờ `thieu_gps`.

### UC-20 Quét mã giao hàng
- **Tác nhân:** Tài xế · **Tiền điều kiện:** như UC-19.
- **Luồng chính:**
  1. Tài xế chọn điểm GIAO, quét QR.
  2. Hệ thống kiểm BR-38, BR-40.
  3. Tài xế chụp ≥ 1 ảnh (trình duyệt tự nén theo NFR-PER-03), nhập tên người nhận, người nhận ký trên màn hình.
  4. Hệ thống kiểm BR-41, lưu ảnh + chữ ký + GPS + giờ máy chủ → đơn `DA_GIAO`; quá hạn giao thì đánh dấu giao trễ (BR-72); sinh khoản phải thu `CHUA_THU` (BR-56).
- **Luồng thay thế:**
  - 3a. **Giao không được:** chọn lý do (người nhận vắng, từ chối nhận, sai địa chỉ, hàng hư hỏng, xe hỏng / sự cố trên đường, khác; mỗi lý do có phía khách/sự cố xe – danh mục ở `app/domain/ly_do.py`), chụp ảnh (BR-42) → `THAT_BAI`.
- **Ngoại lệ:** 2a. Đơn chưa lấy (`DA_GHEP`) → báo "Đơn chưa được quét lấy". 4a. Thiếu ảnh/chữ ký → không cho lưu.

### UC-21 Ghi chi phí
- **Tác nhân:** Tài xế · **Tiền điều kiện:** Chuyến `DANG_CHAY` hoặc `HOAN_THANH`, chưa quyết toán.
- **Luồng chính:** Chọn loại chi (dầu, cầu đường, bốc xếp, phát sinh), nhập số tiền (dầu: thêm số lít), ghi chú, chụp ảnh chứng từ → kiểm BR-54 → lưu trạng thái `CHO_DUYET`.

### UC-22 Xử lý đơn thất bại
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Đơn `THAT_BAI`, chuyến chứa đơn đã `HOAN_THANH`.
- **Luồng chính:**
  1. Điều phối xem danh sách đơn cần xử lý, kèm lý do, ảnh, đã lấy hàng hay chưa, số lần giao thất bại.
  2. Chọn một trong ba:
     - **Ghép lại** → kiểm BR-37; nếu đơn đã lấy thì bắt buộc chọn nơi giữ hàng (BR-69); được đổi hạn giao → `CHO_GHEP`, cước giữ nguyên.
     - **Trả hàng** (chỉ khi đã lấy) → `TRA_HANG`.
     - **Hủy** (chỉ khi chưa lấy) → `HUY`.
- **Ngoại lệ:** 2a. Đã đạt `CFG-04` lần giao thất bại vì lý do phía khách → nút Ghép lại bị khóa (BR-37).

### UC-23 Cấp / sửa / thu hồi tạm ứng
- **Tác nhân:** Kế toán
- **Tiền điều kiện:** Chuyến `DA_CHOT` hoặc `DANG_CHAY`.
- **Luồng chính:** 1. Hệ thống gợi ý số tiền = định mức chi phí đã chốt − tạm ứng `HIEU_LUC` đã cấp. 2. Kế toán nhập số tiền, hình thức (tiền mặt/chuyển khoản). 3. Kiểm BR-53 → lưu `HIEU_LUC`, ghi nhật ký BR-62.
- **Luồng thay thế:** 3a. **Sửa** (khi chuyến chưa quyết toán): nhập số mới + lý do → kiểm lại BR-53. 3b. **Thu hồi** (trước khi mở chốt hoặc hủy chuyến): Kế toán xác nhận tài xế đã nộp lại → `DA_THU_HOI`, ghi nhật ký.
- **Ngoại lệ:** 3c. Tổng vượt định mức đã chốt → từ chối (BR-53).

### UC-24 Quyết toán chuyến
- **Tác nhân:** Kế toán
- **Tiền điều kiện:** Chuyến `HOAN_THANH`.
- **Luồng chính:**
  1. Hệ thống hiện: doanh thu ghi nhận (BR-50), các khoản chi tài xế khai (UC-21), bảng định mức – thực tế – chênh lệch theo loại chi, dầu tham khảo (km thực tế × lít/100 km), lương đã chốt, tạm ứng `HIEU_LUC`, lãi dự kiến và lý do lệch (đơn thất bại, chi vượt định mức).
  2. Kế toán duyệt/điều chỉnh/từ chối từng khoản chi (ghi lý do khi điều chỉnh). Chuyến `ket_thuc_bat_thuong` → Kế toán nhập lương bằng tay kèm lý do (BR-68).
  3. Hệ thống tính lãi chuyến (BR-51) và chênh lệch tạm ứng (BR-55).
  4. Chênh lệch khác 0 → Kế toán ghi cách xử lý (tài xế đã nộp / công ty đã trả, hình thức, thời điểm).
  5. Kế toán xác nhận → chuyến `DA_QUYET_TOAN`, khóa (BR-29).
- **Ngoại lệ:** 5a. Còn khoản chi `CHO_DUYET`, hoặc chưa ghi xử lý chênh lệch → không cho quyết toán (BR-55). 5b. Chuyến không ở `HOAN_THANH` → từ chối.
- **Hậu điều kiện:** Có số lãi/lỗ chuyến và số tiền tài xế đã nộp/được trả.

### UC-28 Tra cứu đơn
- **Tác nhân:** Khách hàng
- **Luồng chính:** 1. Khách vào trang tra cứu, nhập mã đơn + 4 số cuối SĐT. 2. Hệ thống kiểm BR-59. 3. Hiện trạng thái và các mốc (đã tạo, đã lấy, đã giao/không thành công – đang chờ giao lại, kèm thời gian).
- **Ngoại lệ:** 2a. Sai thông tin → thông báo chung "Không tìm thấy đơn" (không tiết lộ mã đơn có tồn tại hay không). 2b. Quá 10 lần sai/phút từ một IP → tạm chặn (NFR-SEC-05).

### UC-32 Theo dõi chuyến
- **Tác nhân:** Điều phối viên
- **Luồng chính:**
  1. Điều phối mở **Bảng chuyến trong ngày**: mỗi dòng có xe, tài xế, tuyến, giờ, % đầy, tiến độ ("3/6 điểm") và cờ đỏ (trễ quá `CFG-09`, sự cố mở, đơn thất bại, chưa quyết toán).
  2. Mở **Chi tiết chuyến** (5 thẻ: Tổng quan, Hàng, Lịch trình, Dòng thời gian, Tiền); thẻ Lịch trình so ETA kế hoạch với giờ quét thực tế, hiện độ trễ từng điểm.
  3. Mỗi lượt quét, hệ thống tính kết thúc dự kiến khi đang chạy = kết thúc dự kiến lúc chốt + độ trễ lượt quét gần nhất; chồng chuyến kế tiếp của xe hoặc tài xế thì cảnh báo (BR-73). Điều phối tự quyết định đổi lịch.
  4. Điều phối xem sự cố tài xế báo (UC-33), ghi cách xử lý và đóng sự cố.
- **Luồng thay thế:** 4a. **Kết thúc do sự cố:** chuyến `DANG_CHAY`, Điều phối nhập lý do và km cuối nếu biết → BR-68: đơn `DA_GHEP`, `DA_LAY` → `THAT_BAI` (lý do "sự cố xe"), chuyến → `HOAN_THANH` với cờ `ket_thuc_bat_thuong`; có km thì cập nhật km đồng hồ xe (BR-70). Xe cần sửa thì chuyển `NGUNG` (UC-03).

### UC-33 Báo sự cố
- **Tác nhân:** Tài xế · **Tiền điều kiện:** Chuyến của mình `DANG_CHAY` (BR-58).
- **Luồng chính:** Chọn loại sự cố, ghi chú, chụp ảnh → lưu sự cố trạng thái mở, hiện cờ trên bảng chuyến của Điều phối. Không đổi trạng thái chuyến.

### UC-35 Đổi mật khẩu
- **Tác nhân:** mọi vai trò đã đăng nhập.
- **Luồng chính:** nhập mật khẩu hiện tại và mật khẩu mới (8–200 ký tự) → đổi được; phiên đang dùng vẫn còn hạn.
- **Ngoại lệ:** sai mật khẩu hiện tại → báo lỗi và **tính như một lần đăng nhập sai** (5 lần liên tiếp khóa 15 phút, dùng chung bộ đếm với đăng nhập, NFR-SEC-05); mật khẩu mới trùng cũ → báo lỗi. Chỉ đổi mật khẩu của chính mình; Quản lý đặt lại cho người khác ở UC-02.

### UC-36 Tìm kiếm chung
- **Tác nhân:** mọi vai trò đã đăng nhập.
- **Luồng chính:** gõ từ khóa (2–100 ký tự) → kết quả gộp theo nhóm chuyến, đơn, xe, tài xế, khách; mỗi nhóm tối đa 5 dòng kèm tổng số khớp. Khớp một phần, không phân biệt hoa thường, gõ tiếng Việt kiểu nào cũng ra.
- **Phân quyền (BR-57, 58):** Điều phối, Quản lý thấy cả 5 nhóm; Kế toán thấy chuyến, đơn, khách; Tài xế chỉ thấy chuyến của mình (không `LAP`, `HUY`).

### UC-37 Thông báo theo vai trò
- **Tác nhân:** mọi vai trò đã đăng nhập.
- **Luồng chính:** bấm chuông → danh sách việc cần chú ý của vai trò mình, mới trước; mỗi thông báo có mức độ (khẩn / cần làm / thông tin), đối tượng để bấm mở và thời điểm sự việc. Tính lại mỗi lần mở từ dữ liệu sẵn có; "đã đọc" do giao diện nhớ bằng mốc lần xem cuối, hệ thống không lưu.
- **Theo vai trò:** Điều phối, Quản lý: các dòng của bảng cảnh báo (UC-27) và đơn thất bại cần xử lý (UC-22). Kế toán: chuyến chờ quyết toán, khoản chi chờ duyệt, tạm ứng chưa quyết toán (UC-24). Tài xế: chuyến được giao hôm nay hoặc ngày mai, sự cố đã được xử lý, khoản chi bị từ chối hoặc điều chỉnh.

### UC-38 Tổng quan hôm nay
- **Tác nhân:** Quản lý, Điều phối, Kế toán.
- **Luồng chính:** mở trang Tổng quan (mặc định hôm nay, đổi được ngày) → số chuyến theo 6 trạng thái; đơn đã giao / thất bại / còn lại và tổng kg đã chở; tỉ lệ điểm đúng giờ (trễ không quá `CFG-09`; chưa quét thì không có tỉ lệ); doanh thu **dự kiến** (số thực ở quyết toán UC-24, báo cáo UC-26). Chỉ đọc.

### UC-39 Hồ sơ cá nhân và ảnh đại diện
- **Tác nhân:** mọi vai trò đã đăng nhập.
- **Luồng chính:** mở trang Tài khoản → xem hồ sơ chỉ đọc (`ten_dang_nhap`, `ho_ten`, `vai_tro`, `trang_thai`; tài xế thêm SĐT, số / hạng / hạn GPLX, tô cảnh báo khi còn ≤ 30 ngày theo BR-21); tự tải lên / thay đổi / xóa **ảnh đại diện** (JPEG/PNG ≤ 500 KB, kiểm byte đầu ở máy chủ, tên file do máy chủ sinh; đổi ảnh thì xóa file cũ; xóa ảnh thì quay về chữ tắt).
- **Phân quyền (BR-57):** chỉ xem và đổi ảnh của chính mình; không có API tự sửa họ tên, SĐT, vai trò, tên đăng nhập hay GPLX (chỉ Quản lý sửa ở UC-02 / UC-04). Ảnh trả qua cookie đăng nhập, không xem được ảnh người khác.

> Các UC còn lại (UC-01…07, 10, 17, 25, 26, 27, 30, 34) là CRUD/xem báo cáo: đặc tả rút gọn khi làm story tương ứng.

---

## 4. Yêu cầu phi chức năng (theo ISO/IEC 25010)

> Dùng tên đặc tính theo ISO/IEC 25010:2011. Bản 2023 đã đổi tên/bổ sung một số đặc tính – **cần kiểm tra** thầy dùng bản nào.
> Mỗi yêu cầu đều đo được để viết test.

| Mã | Đặc tính | Yêu cầu | Cách kiểm |
|---|---|---|---|
| NFR-FUN-01 | Phù hợp chức năng | Mọi BR mức "Chặn" có ít nhất 1 test case dương và 1 âm | Ma trận truy vết BR → test |
| NFR-FUN-02 | Phù hợp chức năng | Tiền lưu kiểu số nguyên (đồng), kg/m³ kiểu decimal; không dùng float | Review mã, test làm tròn |
| NFR-PER-01 | Hiệu năng | API đọc p95 < 500 ms, ghép đơn p95 < 1 s với 50 người dùng đồng thời, dữ liệu 10.000 đơn | Locust/k6 trên bản demo |
| NFR-PER-02 | Hiệu năng | Trang tài xế tải xong < 3 s trên 4G | Lighthouse (mô phỏng mạng chậm) |
| NFR-PER-03 | Hiệu năng | Ảnh nén trên trình duyệt trước khi gửi: cạnh dài ≤ 1280 px, JPEG chất lượng ~70%, mỗi ảnh ≤ 500 KB. Server từ chối file lớn hơn giới hạn | Test upload ảnh gốc từ điện thoại, kiểm kích thước file lưu trong Storage |
| NFR-COM-01 | Tương thích | Web chạy trên Chrome, Edge bản mới; trang tài xế chạy Chrome Android và Safari iOS, màn hình từ 360 px | Test thủ công trên 2 điện thoại |
| NFR-USA-01 | Khả dụng | Quét một đơn ≤ 3 thao tác từ màn hình chuyến | Kịch bản test |
| NFR-USA-02 | Khả dụng | Lỗi nghiệp vụ hiển thị mã BR + câu tiếng Việt dễ hiểu | Test các luồng ngoại lệ |
| NFR-REL-01 | Tin cậy | Ghép đơn, chuyển trạng thái chạy trong giao dịch CSDL; không có trạng thái nửa vời khi lỗi | Test lỗi giữa chừng |
| NFR-REL-02 | Tin cậy | Hai điều phối ghép cùng một đơn đồng thời → chỉ một thành công (BR-07) | Test song song |
| NFR-REL-03 | Tin cậy | Sao lưu CSDL hằng ngày (pg_dump) trên bản demo | Kiểm tra file sao lưu |
| NFR-SEC-01 | Bảo mật | Mật khẩu băm bcrypt/argon2; token hết hạn ≤ 8 giờ | Review mã |
| NFR-SEC-02 | Bảo mật | Phân quyền kiểm tại máy chủ cho 100% endpoint (BR-57, 58) | Test gọi API sai vai trò → 403 |
| NFR-SEC-03 | Bảo mật | Bí mật (khóa, mật khẩu CSDL) chỉ qua biến môi trường; `.env` trong `.gitignore`; quét repo bằng gitleaks trong CI | CI |
| NFR-SEC-04 | Bảo mật | Ảnh, chữ ký chỉ truy cập qua URL có hạn hoặc qua API có kiểm quyền | Test truy cập trực tiếp |
| NFR-SEC-05 | Bảo mật | Giới hạn tần suất trang tra cứu và đăng nhập | Test |
| NFR-SEC-06 | Bảo mật | Ghi log lịch sử chuyển trạng thái, không sửa/xóa được (BR-30) | Test |
| NFR-MAI-01 | Bảo trì | Quy tắc nghiệp vụ nằm ở tầng domain/service, không nằm trong router hay giao diện; mỗi BR là một hàm kiểm có tên chứa mã BR | Review mã |
| NFR-MAI-02 | Bảo trì | Độ phủ test tầng domain ≥ 80%, toàn bộ ≥ 60% | pytest-cov |
| NFR-MAI-03 | Bảo trì | Lint + format (ruff, oxlint, prettier) chạy trong CI | CI |
| NFR-POR-01 | Khả chuyển | Chạy toàn bộ bằng `docker compose up` | Thử trên máy sạch |

---

## 5. Chia việc

Xem `docs/TIEN-DO.md` (ai làm UC nào, tuần nào, trạng thái).
