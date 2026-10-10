# Đặc tả yêu cầu – Hệ thống quản lý vận tải

> Phiên bản: 0.2 (đề xuất) · Cập nhật: 10/10/2026 · Nhóm 10
> Quy tắc nghiệp vụ, trạng thái, cấu hình: xem `docs/nghiep-vu.md` (`BR-xx`, `ST-xx`, `CFG-xx`).
> Ưu tiên MoSCoW: **M** = phải có (bản demo), **S** = nên có, **C** = có thì tốt (làm nếu dư thời gian).

---

## 1. Tác nhân

| Tác nhân | Mô tả | Thiết bị |
|---|---|---|
| Quản lý | Chủ/giám đốc doanh nghiệp. Quản trị người dùng, bảng giá, cấu hình; xem báo cáo; duyệt tạm ứng vượt định mức | Web máy tính |
| Điều phối viên | Nhận đơn từ khách, lập chuyến, ghép đơn, chốt chuyến, xử lý giao thất bại | Web máy tính |
| Tài xế | Nhận chuyến, quét mã lấy/giao, chụp ảnh, lấy chữ ký, ghi chi phí phát sinh | Web responsive trên điện thoại |
| Kế toán | Cấp tạm ứng, quyết toán chuyến, theo dõi công nợ | Web máy tính |
| Khách hàng | Tra cứu trạng thái đơn, không cần tài khoản | Web điện thoại/máy tính |
| Hệ thống (thời gian) | Tác nhân phụ: quét giấy tờ sắp hết hạn hằng ngày (BR-21) | — |

---

## 2. Danh sách use case

| Mã | Tên | Tác nhân chính | Phân hệ | Ưu tiên | BR liên quan |
|---|---|---|---|---|---|
| UC-01 | Đăng nhập / đăng xuất | Tất cả trừ Khách | Chung | M | BR-57 |
| UC-02 | Quản lý người dùng và vai trò | Quản lý | Chung | M | BR-57 |
| UC-03 | Quản lý xe (thông tin, tải trọng, thể tích, giấy tờ) | Điều phối | Xe/Tài xế | M | BR-11…13, 60 |
| UC-04 | Quản lý tài xế (GPLX, hạng, hạn) | Điều phối | Xe/Tài xế | M | BR-14, 15, 60 |
| UC-05 | Quản lý tuyến (nút, thời gian, định mức chi phí) | Điều phối | Chuyến | M | BR-20, 60 |
| UC-06 | Quản lý khách hàng | Điều phối | Đơn | M | BR-60 |
| UC-07 | Quản lý bảng giá và cấu hình | Quản lý | Đơn | M | BR-48, CFG-xx |
| UC-08 | Tạo đơn hàng | Điều phối | Đơn | M | BR-31, 46–48 |
| UC-09 | Xác nhận đơn (chốt cước) | Điều phối | Đơn | M | BR-32, 48 |
| UC-10 | Sửa / hủy đơn | Điều phối | Đơn | M | BR-33, 34 |
| UC-11 | Lập kế hoạch chuyến | Điều phối | Chuyến | M | — |
| UC-12 | Gán xe và tài xế cho chuyến | Điều phối | Chuyến | M | BR-11…19, 22 |
| UC-13 | Ghép / gỡ đơn khỏi chuyến | Điều phối | Chuyến | M | BR-01…10 |
| UC-14 | Sắp xếp thứ tự điểm dừng | Điều phối | Chuyến | S | BR-10 |
| UC-15 | Chốt / mở chốt chuyến | Điều phối | Chuyến | M | BR-23, 24, 52 |
| UC-16 | Hủy chuyến | Điều phối | Chuyến | M | BR-25 |
| UC-17 | Xem chuyến được giao | Tài xế | Quét mã | M | BR-58 |
| UC-18 | Bắt đầu bốc / xuất phát / kết thúc chuyến | Tài xế | Quét mã | M | BR-26–28 |
| UC-19 | Quét mã lấy hàng | Tài xế | Quét mã | M | BR-38, 39, 42–45 |
| UC-20 | Quét mã giao hàng | Tài xế | Quét mã | M | BR-35, 38, 40–45 |
| UC-21 | Ghi chi phí phát sinh | Tài xế | Quyết toán | M | BR-54 |
| UC-22 | Xử lý đơn giao thất bại / không lấy được | Điều phối | Đơn | M | BR-36, 37 |
| UC-23 | Cấp tạm ứng chuyến | Kế toán | Quyết toán | M | BR-53 |
| UC-24 | Quyết toán chuyến | Kế toán | Quyết toán | M | BR-29, 50, 51, 55 |
| UC-25 | Theo dõi công nợ và ghi nhận thu tiền | Kế toán | Quyết toán | S | BR-56 |
| UC-26 | Báo cáo lãi lỗ theo chuyến / xe / tuyến | Quản lý | Quyết toán | S | BR-51 |
| UC-27 | Xem bảng cảnh báo (giấy tờ, quét sai vị trí, thiếu GPS) | Điều phối | Xe/Tài xế | S | BR-21, 43, 44 |
| UC-28 | Tra cứu đơn | Khách | Tra cứu | M | BR-59 |
| UC-29 | Gợi ý ghép đơn và thứ tự điểm dừng (OR-Tools) | Điều phối | Phụ trợ | C | BR-01…10 (ràng buộc) |
| UC-30 | Dự đoán nguy cơ trễ chuyến | Điều phối | Phụ trợ | C | — |

Ghi chú: UC-29 và UC-30 chỉ **gợi ý**; người dùng vẫn phải xác nhận qua UC-13/UC-14, nên mọi BR vẫn do lõi kiểm. Module phụ hỏng thì lõi vẫn chạy.

---

## 3. Đặc tả chi tiết các use case lõi

### UC-08 Tạo đơn hàng
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Đã đăng nhập vai trò Điều phối/Quản lý; khách đã có trong hệ thống (hoặc tạo nhanh tại chỗ).
- **Kích hoạt:** Khách gọi điện/nhắn yêu cầu gửi hàng.
- **Luồng chính:**
  1. Điều phối chọn khách, nhập hàng hóa (mô tả, kg thực, m³, số kiện), điểm lấy (địa chỉ, tỉnh, người liên hệ, SĐT, khung giờ lấy), điểm giao (địa chỉ, tỉnh, người nhận, SĐT, hạn giao).
  2. Hệ thống kiểm BR-31.
  3. Hệ thống tính KL quy đổi, KL tính cước, cước tạm tính (BR-46…48) và hiển thị.
  4. Điều phối lưu. Hệ thống tạo đơn trạng thái `MOI`, sinh mã đơn duy nhất và mã QR.
- **Luồng thay thế:**
  - 4a. Điều phối chọn "Lưu và xác nhận" → thực hiện tiếp UC-09.
- **Ngoại lệ:**
  - 2a. Vi phạm BR-31 → báo lỗi từng trường, không lưu.
  - 3a. Không có đơn giá cho cặp tỉnh (BR-48) → vẫn lưu `MOI`, báo "chưa có bảng giá", không cho xác nhận.
- **Hậu điều kiện:** Đơn `MOI` có mã QR in được.

### UC-09 Xác nhận đơn
- **Tác nhân:** Điều phối viên · **Tiền điều kiện:** Đơn `MOI`.
- **Luồng chính:** 1. Điều phối mở đơn, bấm Xác nhận. 2. Hệ thống tính lại cước theo bảng giá hiện hành, lưu bản sao đơn giá + hệ số (BR-32). 3. Đơn → `CHO_GHEP`, ghi lịch sử (BR-30).
- **Ngoại lệ:** 2a. Thiếu bảng giá (BR-48) → từ chối.

### UC-12 Gán xe và tài xế cho chuyến
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Chuyến `LEN_KE_HOACH` hoặc `GHEP_DON`.
- **Luồng chính:**
  1. Điều phối chọn chuyến, mở "Gán xe/tài xế".
  2. Hệ thống chỉ liệt kê xe và tài xế **khả dụng** cho khoảng thời gian chuyến (đã lọc BR-11…19), kèm lý do loại với những xe/tài xế bị loại.
  3. Điều phối chọn xe và tài xế, bấm Lưu.
  4. Hệ thống kiểm lại BR-11…19 (tránh hai người gán cùng lúc), và nếu chuyến đã có đơn thì kiểm BR-01, BR-02 với xe mới.
  5. Lưu; nếu chuyến đang `LEN_KE_HOACH` thì chuyển `GHEP_DON` (BR-22).
- **Ngoại lệ:**
  - 4a. Vi phạm bất kỳ BR nào → báo mã BR và nội dung vi phạm, không lưu.
- **Hậu điều kiện:** Chuyến có xe + tài xế hợp lệ, ở `GHEP_DON`.

### UC-13 Ghép / gỡ đơn khỏi chuyến
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Chuyến `GHEP_DON`.
- **Luồng chính (ghép):**
  1. Điều phối mở chuyến. Màn hình hiện: thanh tải (kg đã dùng / tải trọng), thanh thể tích, danh sách đơn đang ghép, danh sách đơn `CHO_GHEP` **phù hợp tuyến** (đã lọc BR-03, BR-04).
  2. Điều phối chọn một hoặc nhiều đơn, bấm Ghép.
  3. Hệ thống kiểm BR-01…BR-09 cho **toàn bộ** danh sách mới trong một giao dịch.
  4. Hệ thống tạo bản ghi ghép hiệu lực, chuyển đơn → `DA_GHEP`, thêm điểm dừng LAY/GIAO theo BR-10, cập nhật lãi dự kiến.
- **Luồng thay thế (gỡ):**
  - 2b. Điều phối chọn đơn đang ghép, bấm Gỡ → bản ghi ghép `hiệu_lực = false`, đơn → `CHO_GHEP`, xóa 2 điểm dừng.
- **Ngoại lệ:**
  - 3a. Có đơn vi phạm → **không ghép đơn nào** trong lô; hiện bảng: đơn nào, vi phạm BR nào, vượt bao nhiêu.
  - 3b. Đơn đã bị người khác ghép vào chuyến khác (BR-07) → báo xung đột, tải lại danh sách.
- **Hậu điều kiện:** Tổng kg, m³ của chuyến ≤ giới hạn xe; mỗi đơn có đúng 1 ghép hiệu lực.

### UC-15 Chốt / mở chốt chuyến
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Chốt: chuyến `GHEP_DON`. Mở chốt: chuyến `DA_CHOT`.
- **Luồng chính (chốt):**
  1. Điều phối bấm Chốt.
  2. Hệ thống kiểm lại toàn bộ BR-01…BR-19 và BR-23.
  3. Hệ thống tính lãi dự kiến (BR-52); nếu âm → hiện cảnh báo, yêu cầu xác nhận.
  4. Chuyến → `DA_CHOT`; tài xế thấy chuyến ở UC-17.
- **Luồng thay thế (mở chốt):** Điều phối bấm Mở chốt → kiểm BR-24 → chuyến về `GHEP_DON`.
- **Ngoại lệ:** 2a. Vi phạm (ví dụ đăng kiểm vừa hết hạn) → liệt kê mã BR, không chốt.

### UC-16 Hủy chuyến
- **Tác nhân:** Điều phối viên · **Tiền điều kiện:** Chuyến ∈ {`LEN_KE_HOACH`, `GHEP_DON`, `DA_CHOT`}.
- **Luồng chính:** 1. Nhập lý do (bắt buộc). 2. Hệ thống kiểm BR-25. 3. Mọi ghép → không hiệu lực, đơn → `CHO_GHEP`. 4. Nếu đã có tạm ứng → tạo khoản tài xế phải hoàn, báo Kế toán. 5. Chuyến → `HUY`.

### UC-18 Bắt đầu bốc / xuất phát / kết thúc chuyến
- **Tác nhân:** Tài xế
- **Luồng chính:**
  1. Tài xế mở chuyến `DA_CHOT` trong ngày khởi hành, bấm **Bắt đầu** → kiểm BR-26 → `DANG_BOC`.
  2. Sau khi quét lấy ở điểm đầu (UC-19), bấm **Xuất phát** → `DANG_CHAY`.
  3. Sau khi xử lý hết đơn, bấm **Kết thúc** → kiểm BR-28 → `HOAN_THANH`; hệ thống xử lý BR-36 cho đơn thất bại/không lấy được.
- **Ngoại lệ:** 3a. Còn đơn chưa xử lý → hiện danh sách đơn còn lại, không cho kết thúc.

### UC-19 Quét mã lấy hàng
- **Tác nhân:** Tài xế
- **Tiền điều kiện:** Chuyến của tài xế ở `DANG_BOC` hoặc `DANG_CHAY`; trình duyệt được cấp quyền camera.
- **Luồng chính:**
  1. Tài xế chọn điểm dừng LAY, bấm Quét.
  2. Camera đọc QR; trình duyệt lấy GPS.
  3. Hệ thống kiểm BR-38, BR-39 → đơn `DA_LAY_HANG`; lưu giờ máy chủ, GPS (BR-43), kiểm khoảng cách (BR-44).
  4. Hiện xác nhận "Đã lấy: mã đơn, số kiện".
- **Luồng thay thế:**
  - 2a. Camera không đọc được → nhập mã đơn bằng tay (vẫn ghi GPS).
  - 1b. **Không lấy được:** tài xế chọn đơn, chọn lý do, chụp ảnh (BR-42) → `KHONG_LAY_DUOC`.
- **Ngoại lệ:**
  - 3a. Đơn không thuộc chuyến (BR-38) → báo "Đơn không thuộc chuyến của bạn".
  - 3b. Đơn đã lấy rồi → trả trạng thái hiện tại (BR-45).
  - 2b. Từ chối quyền GPS → vẫn lưu, gắn cờ `thiếu_GPS`.

### UC-20 Quét mã giao hàng
- **Tác nhân:** Tài xế · **Tiền điều kiện:** như UC-19.
- **Luồng chính:**
  1. Tài xế chọn điểm dừng GIAO, quét QR.
  2. Hệ thống kiểm BR-38, BR-40.
  3. Tài xế chụp ≥ 1 ảnh, nhập tên người nhận, người nhận ký trên màn hình.
  4. Hệ thống kiểm BR-41, lưu ảnh + chữ ký + GPS + giờ máy chủ → đơn `DA_GIAO`; sinh khoản phải thu (BR-56).
- **Luồng thay thế:**
  - 3a. **Giao thất bại:** chọn lý do (người nhận vắng, từ chối nhận, sai địa chỉ, hàng hư hỏng, khác), chụp ảnh (BR-42) → `GIAO_THAT_BAI`.
- **Ngoại lệ:** 2a. Đơn chưa lấy (`DA_GHEP`) → báo "Đơn chưa được quét lấy". 4a. Thiếu ảnh/chữ ký → không cho lưu.

### UC-21 Ghi chi phí phát sinh
- **Tác nhân:** Tài xế · **Tiền điều kiện:** Chuyến `DANG_BOC`…`HOAN_THANH`, chưa quyết toán.
- **Luồng chính:** Chọn loại chi (dầu, cầu đường, bốc xếp, phát sinh), nhập số tiền, ghi chú, chụp ảnh chứng từ → kiểm BR-54 → lưu trạng thái `CHO_DUYET`.

### UC-22 Xử lý đơn giao thất bại / không lấy được
- **Tác nhân:** Điều phối viên
- **Tiền điều kiện:** Đơn `GIAO_THAT_BAI` hoặc `KHONG_LAY_DUOC`, chuyến chứa đơn đã `HOAN_THANH`.
- **Luồng chính:** 1. Điều phối xem danh sách đơn cần xử lý, kèm lý do, ảnh. 2. Chọn **Ghép lại** → kiểm BR-37 → `CHO_GHEP` (có thể đổi hạn giao theo thỏa thuận với khách); hoặc **Hoàn hàng** → `HOAN_HANG`.
- **Ngoại lệ:** 2a. Đã đạt `CFG-04` lần thất bại → nút Ghép lại bị khóa.

### UC-23 Cấp tạm ứng chuyến
- **Tác nhân:** Kế toán (Quản lý duyệt khi vượt định mức)
- **Tiền điều kiện:** Chuyến `DA_CHOT`, `DANG_BOC` hoặc `DANG_CHAY`.
- **Luồng chính:** 1. Hệ thống gợi ý số tiền = định mức tuyến − tạm ứng đã cấp. 2. Kế toán nhập số tiền, hình thức (tiền mặt/chuyển khoản). 3. Kiểm BR-53 → lưu.
- **Luồng thay thế:** 3a. Vượt định mức → trạng thái `CHO_QUAN_LY_DUYET`; Quản lý duyệt/từ chối.

### UC-24 Quyết toán chuyến
- **Tác nhân:** Kế toán
- **Tiền điều kiện:** Chuyến `HOAN_THANH`.
- **Luồng chính:**
  1. Hệ thống hiện: doanh thu ghi nhận (BR-50), các khoản chi tài xế khai (UC-21), lương tài xế theo định mức tuyến, tạm ứng đã cấp.
  2. Kế toán duyệt/điều chỉnh/từ chối từng khoản chi (ghi lý do khi điều chỉnh).
  3. Hệ thống tính lãi chuyến (BR-51) và chênh lệch tạm ứng (BR-55).
  4. Kế toán xác nhận → chuyến `DA_QUYET_TOAN`, khóa (BR-29).
- **Ngoại lệ:** 4a. Còn khoản chi `CHO_DUYET` → không cho quyết toán.
- **Hậu điều kiện:** Có số lãi/lỗ chuyến và số tiền tài xế phải nộp/được nhận.

### UC-28 Tra cứu đơn
- **Tác nhân:** Khách hàng
- **Luồng chính:** 1. Khách vào trang tra cứu, nhập mã đơn + 4 số cuối SĐT. 2. Hệ thống kiểm BR-59. 3. Hiện trạng thái và các mốc (đã xác nhận, đã lấy, đã giao/thất bại kèm thời gian).
- **Ngoại lệ:** 2a. Sai thông tin → thông báo chung "Không tìm thấy đơn" (không tiết lộ mã đơn có tồn tại hay không). 2b. Quá 10 lần sai/phút từ một IP → tạm chặn (NFR-SEC-05).

> Các UC còn lại (UC-01…07, 10, 11, 14, 17, 25, 26, 27, 29, 30) là CRUD/xem báo cáo: đặc tả rút gọn khi làm story tương ứng.

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
| NFR-MAI-03 | Bảo trì | Lint + format (ruff, eslint, prettier) chạy trong CI | CI |
| NFR-POR-01 | Khả chuyển | Chạy toàn bộ bằng `docker compose up` | Thử trên máy sạch |

---

## 5. Chia việc theo phân hệ (đề xuất)

| Phân hệ | UC | Người chính | Tuần dự kiến |
|---|---|---|---|
| Chung + Xe/Tài xế | UC-01…05, 27 | Kiệt | 3–4 |
| Đơn | UC-06…10, 22 | Tài | 3–4 |
| Chuyến (lõi) | UC-11…16 | Tài | 5–6 |
| Quét mã (tài xế) | UC-17…21 | Kiệt | 5–6 |
| Quyết toán | UC-23…26 | Kiệt | 7 |
| Tra cứu | UC-28 | Tài | 7 |
| Phụ trợ | UC-29, 30 | Cả hai | 8–9 (chỉ khi lõi đã qua test) |
| Kiểm thử, báo cáo | — | Cả hai | 9–10 |

Lý do: Chuyến và Đơn gắn chặt (ghép đơn) nên một người nắm; Quét mã và Quyết toán cùng dùng dữ liệu chi phí/tài xế nên người kia nắm. Tuần 1–2 dành cho đặc tả + thiết kế.
