# Nghiệp vụ – Hệ thống quản lý vận tải (chuyến là trung tâm)

> Phiên bản: 0.4 (đề xuất, chờ thầy góp ý) · Cập nhật: 10/10/2026 · Nhóm 10
> Nguyên tắc: **Chuyến xe là trung tâm, đơn hàng là thứ được ghép vào chuyến.**
> Mọi use case, user story và test case trỏ về mã `BR-xx`, `ST-xx`, `CFG-xx` trong file này.
> Nguồn sự thật về nghiệp vụ cho code và tài liệu. Sửa ở đây trước, rồi chép sang Project instructions trên claude.ai để hai nơi không lệch nhau.
> Đề tài (thầy giao): "Hệ thống quản lý vận tải cho một doanh nghiệp vận tải hàng hóa nhỏ: CHUYẾN XE LÀ TRUNG TÂM, ĐƠN HÀNG LÀ THỨ ĐƯỢC GHÉP VÀO CHUYẾN."

---

## 0. Tham khảo sản phẩm tương tự (đã tra cứu)

| Sản phẩm | Điểm học được | Áp dụng vào đồ án |
|---|---|---|
| Rose Rocket (TMS, Bắc Mỹ) | Đơn có thể chia chặng để điều phối; hỗ trợ chuyến nhiều điểm dừng; app tài xế xem chuyến, điểm dừng, lấy chữ ký điện tử, chụp ảnh chứng từ; chữ ký xác nhận cả lúc lấy và lúc giao (POD) | Lấy: chuyến nhiều điểm dừng, chữ ký/ảnh POD. Bỏ: chia chặng đơn (vi phạm "không tách đơn"), tích hợp ELD/GPS liên tục |
| Smartlog STM SME (Việt Nam) | App tài xế ghi chi phí phát sinh, ảnh chứng từ POD, xem lương theo chuyến; quản lý theo dõi trạng thái đơn và chuyến | Lấy: tài xế tự ghi chi phí phát sinh kèm ảnh, lương theo chuyến. Bỏ: theo dõi vị trí trực tiếp |
| MISA AMIS Kế toán – mảng vận tải | Giá thành và lãi lỗ theo chuyến, theo phương tiện; công nợ tạm ứng theo từng lái xe | Lấy: lãi lỗ theo chuyến/xe/tuyến, tạm ứng – quyết toán theo tài xế. Bỏ: sổ sách kế toán đầy đủ |
| Smart Cargo TMS – ĐPV (Việt Nam) | Phân công rõ người điều phối đơn/chuyến, báo cáo KPI nhân viên | Lấy: ghi người phụ trách chuyến. Bỏ: KPI (hướng phát triển) |

Nhận xét: các TMS lớn đều có định tuyến tối ưu + theo dõi GPS liên tục. Đồ án **không** làm GPS liên tục (chỉ GPS lúc quét) và đưa tối ưu vào module phụ → đúng phạm vi 2 người/10 tuần.

---

## 1. Giả định phạm vi (chờ thầy trả lời)

| Mã | Câu hỏi | Giả định mặc định | Nếu thầy trả lời khác |
|---|---|---|---|
| A1 | Lấy hàng tận nơi hay khách mang đến kho? | **Cả hai** – kho công ty chỉ là một "điểm lấy" có địa chỉ. Mô hình không đổi | Không ảnh hưởng mô hình |
| A2 | Có xe thuê ngoài không? | **Không** – chỉ xe của công ty | Thêm thực thể Nhà xe, chi phí thuê thay cho dầu + lương → làm ở "hướng phát triển" |
| A3 | Nội thành, liên tỉnh hay cả hai? | **Liên tỉnh theo tuyến cố định**; nội thành = tuyến có 1 nút | Không đổi mô hình; chỉ đổi dữ liệu tuyến |
| A4 | Khách có tự tạo đơn? | **Không** – Điều phối viên tạo đơn (khách gọi/nhắn). Khách chỉ tra cứu | Thêm UC "Khách gửi yêu cầu" → đơn ở trạng thái `MOI` chờ điều phối xác nhận (đã có sẵn trạng thái này) |

Nên hỏi thêm thầy 2 câu (ảnh hưởng tài chính): (A5) khách thanh toán ngay hay ghi công nợ cuối kỳ? có thu hộ COD không? (A6) hoàn hàng / giao lại có tính thêm phí không?
Giả định: A5 = ghi công nợ, không COD; A6 = không tính thêm phí ở bản này.

**Ngoài phạm vi (hướng phát triển):** xe thuê ngoài, GPS theo dõi liên tục, quét mã từng kiện, giao một phần, chia chặng/trung chuyển, rơ moóc, COD, hóa đơn điện tử, chế độ offline cho tài xế, KPI nhân viên.

---

## 2. Thuật ngữ và thực thể

| Thuật ngữ | Định nghĩa |
|---|---|
| **Tuyến** | Danh sách **nút** có thứ tự (tỉnh/thành hoặc kho), mỗi nút có `phút_từ_điểm_đầu` (thời gian chạy dự kiến) và cờ `là_điểm_nghỉ`. Có định mức chi phí (dầu, cầu đường, bốc xếp, lương tài xế) dùng cho tạm ứng và lãi dự kiến |
| **Chuyến** | Xe + tài xế + tuyến + giờ khởi hành dự kiến + danh sách đơn + danh sách điểm dừng + chi phí + lãi lỗ |
| **Điểm dừng** | Một địa chỉ cụ thể trên chuyến, loại `LAY` hoặc `GIAO`, thuộc một nút của tuyến, có thứ tự |
| **Đơn hàng** | Khách + hàng (kg thực, m³, số kiện, mô tả) + điểm lấy + khung giờ lấy + điểm giao + hạn giao + cước. Điểm lấy và điểm giao có tọa độ (Điều phối chấm trên bản đồ khi tạo đơn). Một đơn = một mã QR |
| **Ghép** | Bản ghi liên kết Đơn–Chuyến, có cờ `hiệu_lực`. Lịch sử ghép được giữ (đơn giao thất bại có thể có nhiều lần ghép) |
| **ETA điểm dừng** | Giờ khởi hành chuyến + `phút_từ_điểm_đầu` của nút chứa điểm dừng |
| **Khoảng thời gian chuyến** | `[giờ khởi hành dự kiến, giờ kết thúc dự kiến)` – kết thúc = khởi hành + thời gian toàn tuyến + `CFG-05` |
| **Tải trọng cho phép chở** | Khối lượng hàng tối đa xe được chở (khác *khối lượng toàn bộ theo thiết kế*, dùng để xét hạng bằng lái) |

---

## 3. Tham số cấu hình (Quản lý chỉnh được)

| Mã | Tham số | Mặc định | Nguồn / ghi chú |
|---|---|---|---|
| CFG-01 | Hệ số quy đổi thể tích (kg/m³) | 333 | Một số tài liệu logistics nêu đường bộ thường quy đổi 1 m³ = 333 kg; các hãng chuyển phát dùng công thức D×R×C/hằng số khác nhau → **cần kiểm tra với doanh nghiệp thực tế**, vì vậy để cấu hình |
| CFG-02 | Cảnh báo giấy tờ sắp hết hạn trước (ngày) | 30 | Đề xuất của nhóm |
| CFG-03 | Bán kính cảnh báo vị trí quét (km) | 2 | Đề xuất của nhóm |
| CFG-04 | Số lần giao tối đa trước khi bắt buộc hoàn hàng | 3 | Đề xuất của nhóm |
| CFG-05 | Thời gian đệm sau chuyến (phút) | 60 | Đề xuất: dỡ hàng, nghỉ trước chuyến sau |
| CFG-06 | Làm tròn cước | 1.000 đ | Đề xuất |
| CFG-07 | Giờ lái tối đa/ngày, /tuần, liên tục | 10 / 48 / 4 giờ | Điều 64 Luật TTATGT đường bộ 2024 (xem Nguồn) |

---

## 4. Quy tắc nghiệp vụ

Mức độ: **Chặn** = hệ thống từ chối thao tác; **Cảnh báo** = cho làm nhưng hiện cảnh báo và ghi log.
Thời điểm kiểm: G = khi ghép đơn, C = khi chốt chuyến, X = khi gán xe/tài xế.

### Nhóm A – Ghép đơn vào chuyến

| Mã | Quy tắc | Mức | Kiểm khi |
|---|---|---|---|
| BR-01 | Tổng **kg thực** của các đơn hiệu lực trong chuyến ≤ tải trọng cho phép chở của xe | Chặn | G, C, X |
| BR-02 | Tổng **m³** của các đơn hiệu lực trong chuyến ≤ thể tích thùng xe | Chặn | G, C, X |
| BR-03 | Điểm lấy và điểm giao của đơn đều thuộc một nút của tuyến chuyến | Chặn | G |
| BR-04 | Đúng chiều tuyến: thứ tự nút lấy ≤ thứ tự nút giao | Chặn | G |
| BR-05 | ETA của nút lấy nằm trong khung giờ lấy của đơn | Chặn | G, C |
| BR-06 | ETA của nút giao ≤ hạn giao của đơn | Chặn | G, C |
| BR-07 | Một đơn có tối đa **một** bản ghi ghép `hiệu_lực = true` | Chặn | G (ràng buộc unique ở CSDL) |
| BR-08 | Không tách đơn: toàn bộ kg, m³, số kiện của đơn đi cùng một chuyến | Chặn | Theo mô hình (đơn không có số lượng con) |
| BR-09 | Chỉ ghép đơn `CHO_GHEP` vào chuyến `GHEP_DON` | Chặn | G |
| BR-10 | Khi ghép, hệ thống tự thêm 2 điểm dừng (LAY, GIAO); khi gỡ đơn thì xóa 2 điểm dừng đó. Thứ tự điểm dừng phải giữ: nút không giảm dần, và điểm LAY của một đơn đứng trước điểm GIAO của chính đơn đó | Chặn | G, khi sắp xếp |

> Ghi chú BR-01: bản này kiểm **tổng** (bảo thủ, đơn giản). Kiểm tải theo từng đoạn (hàng lên xuống dọc đường) là chính xác hơn nhưng để ở hướng phát triển.

### Nhóm B – Xe và tài xế

| Mã | Quy tắc | Mức | Kiểm khi |
|---|---|---|---|
| BR-11 | Xe ở trạng thái `HOAT_DONG` (không `BAO_DUONG`, `NGUNG`) | Chặn | X, C |
| BR-12 | Hạn đăng kiểm của xe ≥ ngày kết thúc dự kiến chuyến | Chặn | X, C |
| BR-13 | Hạn bảo hiểm TNDS bắt buộc của xe ≥ ngày kết thúc dự kiến chuyến | Chặn | X, C |
| BR-14 | Hạng GPLX tài xế phù hợp **khối lượng toàn bộ theo thiết kế** của xe: ≤ 3.500 kg → B trở lên; > 3.500–7.500 kg → C1 trở lên; > 7.500 kg → C. Thứ bậc: C ⊇ C1 ⊇ B | Chặn | X, C |
| BR-15 | GPLX tài xế còn hạn đến ngày kết thúc dự kiến chuyến | Chặn | X, C |
| BR-16 | Xe không có hai chuyến (khác `HUY`) có khoảng thời gian giao nhau | Chặn | X, C |
| BR-17 | Tài xế không có hai chuyến (khác `HUY`) có khoảng thời gian giao nhau | Chặn | X, C |
| BR-18 | Tổng giờ lái dự kiến của tài xế trong một ngày (00:00–24:00) ≤ 10 giờ | Chặn | X, C |
| BR-19 | Tổng giờ lái dự kiến của tài xế trong một tuần ≤ 48 giờ | Chặn | X, C |
| BR-20 | Giữa hai nút liên tiếp có `là_điểm_nghỉ` cách nhau > 4 giờ chạy → cảnh báo tuyến thiếu điểm nghỉ | Cảnh báo | Khi lưu tuyến |
| BR-21 | Xe/tài xế có giấy tờ hết hạn trong `CFG-02` ngày → hiện trên bảng cảnh báo | Cảnh báo | Hằng ngày, trang chủ |

> Ghi chú BR-18/19/20: hệ thống chỉ kiểm **giờ lái dự kiến** theo lịch. Giờ lái thực tế cần thiết bị giám sát hành trình – ngoài phạm vi.
> Ghi chú BR-14: không xét rơ moóc (ngoài phạm vi).

### Nhóm C – Vòng đời chuyến (xem sơ đồ mục 5.1)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-22 | Chỉ chuyển `LEN_KE_HOACH → GHEP_DON` khi chuyến đã gán xe và tài xế thỏa BR-11…BR-19 (vì kiểm tải cần biết xe) | Chặn |
| BR-23 | Chốt chuyến (`GHEP_DON → DA_CHOT`) khi: có ≥ 1 đơn; mọi BR nhóm A và B đều thỏa (kiểm lại toàn bộ vì giấy tờ/lịch có thể đã đổi) | Chặn |
| BR-24 | Mở chốt (`DA_CHOT → GHEP_DON`) chỉ khi chưa cấp tạm ứng | Chặn |
| BR-25 | Hủy chuyến chỉ khi trạng thái ∈ {`LEN_KE_HOACH`, `GHEP_DON`, `DA_CHOT`}; mọi đơn trong chuyến về `CHO_GHEP`; nếu đã cấp tạm ứng thì các khoản tạm ứng `HIEU_LUC` chuyển sang `PHAI_HOAN`; Kế toán xác nhận tài xế đã nộp thì chuyển `DA_HOAN`, ghi nhật ký BR-62 | Chặn |
| BR-26 | Bắt đầu bốc (`DA_CHOT → DANG_BOC`) chỉ do **tài xế của chuyến**, trong ngày khởi hành dự kiến | Chặn |
| BR-27 | Xuất phát (`DANG_BOC → DANG_CHAY`) khi tài xế xác nhận; đơn chưa quét lấy ở điểm lấy đầu tiên vẫn có thể được lấy ở các điểm sau | — |
| BR-28 | Kết thúc (`DANG_CHAY → HOAN_THANH`) chỉ khi mọi đơn hiệu lực đã ở trạng thái kết thúc của chuyến: `DA_GIAO`, `GIAO_THAT_BAI` hoặc `KHONG_LAY_DUOC` | Chặn |
| BR-29 | Sau `DA_QUYET_TOAN`, chuyến và chi phí chỉ đọc | Chặn |
| BR-30 | Mọi chuyển trạng thái chuyến và đơn ghi lịch sử: trạng thái cũ, mới, người thực hiện, thời điểm, lý do | — |

### Nhóm D – Đơn hàng (xem sơ đồ mục 5.2)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-31 | Đơn hợp lệ: có khách, kg > 0, m³ > 0, số kiện ≥ 1, điểm lấy ≠ điểm giao, khung giờ lấy `từ < đến`, hạn giao > giờ lấy sớm nhất | Chặn |
| BR-32 | Xác nhận đơn (`MOI → CHO_GHEP`) tính và **chốt cước**: lưu bản sao đơn giá/kg, cước tối thiểu, hệ số quy đổi `CFG-01` và bước làm tròn `CFG-06` vào đơn. BR-33 tính lại cước chỉ từ bản sao này, không đọc bảng giá mới; đổi bảng giá hay cấu hình sau đó không ảnh hưởng đơn đã xác nhận | — |
| BR-33 | Sửa kg/m³/điểm/khung giờ chỉ khi đơn chưa `DA_LAY_HANG`; nếu đơn đang ghép thì kiểm lại BR-01…BR-06, vi phạm thì từ chối sửa. Đơn đã xác nhận thì hệ thống tính lại cước theo đơn giá đã chốt (không lấy bảng giá mới). Cước không bao giờ nhập tay ở bước này; điều chỉnh tay theo BR-61 | Chặn |
| BR-34 | Hủy đơn chỉ khi trạng thái ∈ {`MOI`, `CHO_GHEP`, `DA_GHEP`}; đang ghép thì gỡ khỏi chuyến trước | Chặn |
| BR-35 | Không giao một phần: một đơn hoặc giao thành công toàn bộ, hoặc giao thất bại | Chặn |
| BR-36 | Đơn `GIAO_THAT_BAI` hoặc `KHONG_LAY_DUOC`: khi chuyến hoàn thành, bản ghi ghép chuyển `hiệu_lực = false`; Điều phối viên chọn **ghép lại** (→ `CHO_GHEP`) hoặc **hoàn hàng** (→ `HOAN_HANG`, chỉ với `GIAO_THAT_BAI`) | — |
| BR-37 | Số lần giao thất bại đạt `CFG-04` → chỉ được chọn hoàn hàng | Chặn |

### Nhóm E – Quét mã (tài xế)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-38 | Tài xế chỉ quét được đơn có bản ghi ghép hiệu lực thuộc chuyến của chính mình đang ở `DANG_BOC` hoặc `DANG_CHAY` | Chặn |
| BR-39 | Quét **lấy**: đơn đang `DA_GHEP` → `DA_LAY_HANG`. Có thể báo **không lấy được** (lý do bắt buộc) → `KHONG_LAY_DUOC` | Chặn |
| BR-40 | Quét **giao**: đơn đang `DA_LAY_HANG` → `DA_GIAO` hoặc `GIAO_THAT_BAI` | Chặn |
| BR-41 | Giao thành công bắt buộc: ≥ 1 ảnh, chữ ký người nhận, tên người nhận | Chặn |
| BR-42 | Giao thất bại / không lấy được bắt buộc: lý do (chọn từ danh mục) + ≥ 1 ảnh | Chặn |
| BR-43 | Mỗi lượt quét lưu: giờ **máy chủ**, GPS (vĩ độ, kinh độ, độ chính xác) nếu điện thoại cho phép. Không có GPS vẫn cho quét nhưng gắn cờ `thiếu_GPS` | Cảnh báo |
| BR-44 | Vị trí quét cách **tọa độ địa chỉ của đơn** (điểm lấy khi quét lấy, điểm giao khi quét giao; không tính tới tâm nút vì nút là tỉnh) > `CFG-03` km → gắn cờ `sai_vị_trí`, hiện cho Điều phối viên | Cảnh báo |
| BR-45 | Quét lại một đơn đã chuyển trạng thái → không tạo bản ghi mới, trả về trạng thái hiện tại (idempotent) | — |

### Nhóm F – Cước, chi phí, tạm ứng, quyết toán, công nợ

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-46 | KL quy đổi (kg) = m³ × `CFG-01` | — |
| BR-47 | KL tính cước = max(kg thực, KL quy đổi) | — |
| BR-48 | Cước = max(cước tối thiểu, đơn giá/kg của cặp (tỉnh lấy, tỉnh giao) × KL tính cước), làm tròn lên theo `CFG-06`. Không có giá cho cặp tỉnh → không xác nhận được đơn | Chặn |
| BR-49 | Kiểm tải (BR-01) dùng **kg thực**, không dùng KL tính cước | — |
| BR-50 | Doanh thu của đơn ghi nhận cho **chuyến giao thành công**; chuyến giao thất bại ghi doanh thu đơn đó = 0 (chi phí vẫn tính) | — |
| BR-51 | Lãi chuyến = Σ doanh thu đơn ghi nhận − (dầu + cầu đường + bốc xếp + lương tài xế + phát sinh) | — |
| BR-52 | Khi chốt, hiện **lãi dự kiến** = Σ cước đơn − định mức chi phí tuyến; âm thì cảnh báo | Cảnh báo |
| BR-53 | Tạm ứng chỉ cấp khi chuyến `DA_CHOT` trở đi và trước `HOAN_THANH`; tổng tạm ứng ≤ định mức tuyến, vượt phải có Quản lý duyệt. Kiểm lại ở **mọi lần tạo và sửa** khoản tạm ứng: sửa làm tổng vượt định mức → khoản đó về `CHO_QUAN_LY_DUYET`, chưa có hiệu lực đến khi Quản lý duyệt | Chặn |
| BR-54 | Chi phí phát sinh phải có số tiền > 0, ghi chú và ≥ 1 ảnh chứng từ | Chặn |
| BR-55 | Quyết toán chỉ khi `HOAN_THANH`, không còn khoản chi `CHO_DUYET` và không còn tạm ứng `CHO_QUAN_LY_DUYET`; Kế toán duyệt từng khoản chi. Chênh lệch = tổng tạm ứng − tổng chi do tài xế chi được duyệt: dương → tài xế nộp lại, âm → công ty trả thêm | Chặn |
| BR-56 | Công nợ: đơn `DA_GIAO` tự sinh khoản phải thu bằng cước. **Trạng thái thanh toán** (`CHUA_THU`, `THU_MOT_PHAN`, `DA_THU`) là trường riêng, không phải trạng thái vòng đời đơn | — |
| BR-61 | Điều chỉnh cước tay (giảm giá, phụ phí): chỉ Kế toán hoặc Quản lý; đơn đã xác nhận cước; bắt buộc lý do; cước sau điều chỉnh ≥ 0. Lưu cước hệ thống tính và khoản điều chỉnh riêng (cước cuối = cước tính + điều chỉnh), không ghi đè cước tính. **Khóa** khi: khoản phải thu của đơn đã `THU_MOT_PHAN` trở lên, **hoặc** chuyến ghi nhận doanh thu đơn đó đã `DA_QUYET_TOAN` (BR-29), hoặc đơn `HUY`/`HOAN_HANG`. Có khoản phải thu `CHUA_THU` thì cập nhật số phải thu theo | Chặn |
| BR-62 | Nhật ký tiền: mọi lần tạo, sửa, duyệt, từ chối cước điều chỉnh, chi phí, tạm ứng, quyết toán, khoản phải thu đều ghi: người làm, thời điểm (giờ máy chủ), giá trị cũ, giá trị mới, lý do. Chỉ thêm, không sửa/xóa. Tách khỏi lịch sử trạng thái (BR-30) | Chặn |

### Nhóm G – Phân quyền, tra cứu, dữ liệu

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-57 | Phân quyền theo vai trò, kiểm tại **máy chủ** cho mọi API (ẩn nút trên giao diện là không đủ) | Chặn |
| BR-58 | Tài xế chỉ xem và thao tác chuyến được giao cho mình | Chặn |
| BR-59 | Khách tra cứu không cần tài khoản: nhập mã đơn + 4 số cuối SĐT người gửi hoặc người nhận. Chỉ hiện trạng thái và mốc thời gian, không hiện GPS, SĐT tài xế, cước | Chặn |
| BR-60 | Xe, tài xế, tuyến, khách đã có chuyến/đơn tham chiếu thì không xóa, chỉ chuyển `NGUNG` | Chặn |

---

## 5. Trạng thái

### 5.1 Chuyến (`ST-T`)

| Mã | Trạng thái | Ý nghĩa |
|---|---|---|
| `LEN_KE_HOACH` | Lên kế hoạch | Có tuyến + giờ khởi hành, chưa đủ xe/tài xế |
| `GHEP_DON` | Ghép đơn | Đã gán xe + tài xế hợp lệ, đang thêm/gỡ đơn |
| `DA_CHOT` | Đã chốt | Danh sách đơn cố định, được cấp tạm ứng |
| `DANG_BOC` | Đang bốc hàng | Tài xế đã bắt đầu tại điểm lấy đầu |
| `DANG_CHAY` | Đang chạy | Đã xuất phát |
| `HOAN_THANH` | Hoàn thành | Mọi đơn đã kết thúc trong chuyến, chờ quyết toán |
| `DA_QUYET_TOAN` | Đã quyết toán | Khóa sổ |
| `HUY` | Hủy | |

| Từ | Sang | Ai | Điều kiện |
|---|---|---|---|
| LEN_KE_HOACH | GHEP_DON | Điều phối | BR-22 |
| GHEP_DON | DA_CHOT | Điều phối | BR-23 |
| DA_CHOT | GHEP_DON | Điều phối | BR-24 |
| DA_CHOT | DANG_BOC | Tài xế | BR-26 |
| DANG_BOC | DANG_CHAY | Tài xế | BR-27 |
| DANG_CHAY | HOAN_THANH | Tài xế | BR-28 |
| HOAN_THANH | DA_QUYET_TOAN | Kế toán | BR-55 |
| LEN_KE_HOACH / GHEP_DON / DA_CHOT | HUY | Điều phối | BR-25 |

### 5.2 Đơn hàng (`ST-O`)

| Mã | Trạng thái |
|---|---|
| `MOI` | Mới tạo, chưa xác nhận cước |
| `CHO_GHEP` | Đã xác nhận, chờ ghép chuyến |
| `DA_GHEP` | Đã ghép vào một chuyến |
| `DA_LAY_HANG` | Tài xế đã quét lấy |
| `KHONG_LAY_DUOC` | Đến điểm lấy nhưng không lấy được |
| `DA_GIAO` | Giao thành công (kết thúc) |
| `GIAO_THAT_BAI` | Giao không thành công, hàng còn trên xe |
| `HOAN_HANG` | Trả lại người gửi (kết thúc) |
| `HUY` | Hủy (kết thúc) |

| Từ | Sang | Ai / sự kiện | Điều kiện |
|---|---|---|---|
| MOI | CHO_GHEP | Điều phối xác nhận | BR-31, BR-32, BR-48 |
| CHO_GHEP | DA_GHEP | Ghép vào chuyến | BR-01…BR-10 |
| DA_GHEP | CHO_GHEP | Gỡ khỏi chuyến / chuyến bị hủy | Chuyến ∈ {GHEP_DON, HUY} |
| DA_GHEP | DA_LAY_HANG | Tài xế quét lấy | BR-38, BR-39 |
| DA_GHEP | KHONG_LAY_DUOC | Tài xế báo | BR-39, BR-42 |
| DA_LAY_HANG | DA_GIAO | Tài xế quét giao | BR-40, BR-41 |
| DA_LAY_HANG | GIAO_THAT_BAI | Tài xế báo | BR-40, BR-42 |
| GIAO_THAT_BAI / KHONG_LAY_DUOC | CHO_GHEP | Điều phối ghép lại | BR-36, BR-37 |
| GIAO_THAT_BAI | HOAN_HANG | Điều phối | BR-36 |
| MOI / CHO_GHEP / DA_GHEP | HUY | Điều phối | BR-34 |

**Góp ý so với bản nháp cũ:**
1. "Ghi công nợ" không phải trạng thái vòng đời mà là trạng thái thanh toán (BR-56) → tách trường riêng, tránh trạng thái đơn bị "kẹt" giữa vận hành và kế toán.
2. Thêm `KHONG_LAY_DUOC` vì lấy tận nơi có thể thất bại (khách vắng, hàng chưa sẵn).
3. Thêm `HUY` cho đơn.
4. `LEN_KE_HOACH` và `GHEP_DON` giữ tách nhau vì có điều kiện rõ: chưa biết xe thì không kiểm được tải (BR-22).

---

## 6. Ma trận phân quyền (tóm tắt)

| Chức năng | Quản lý | Điều phối | Tài xế | Kế toán | Khách |
|---|---|---|---|---|---|
| Người dùng, cấu hình, bảng giá | ✔ | | | | |
| Xe, tài xế, tuyến, khách | ✔ | ✔ | | | |
| Tạo/xác nhận/sửa/hủy đơn | ✔ | ✔ | | | |
| Lập chuyến, ghép đơn, chốt, hủy | ✔ | ✔ | | | |
| Xem chuyến của mình, quét mã, ghi phát sinh | | | ✔ | | |
| Tạm ứng, quyết toán, công nợ | ✔ (duyệt vượt định mức) | | | ✔ | |
| Điều chỉnh cước tay (BR-61) | ✔ | | | ✔ | |
| Báo cáo lãi lỗ | ✔ | xem | | ✔ | |
| Tra cứu đơn | | | | | ✔ (không đăng nhập) |

## 7. Module phụ trợ (làm sau cùng)
- Gợi ý ghép đơn vào chuyến và thứ tự điểm dừng: thuật toán tối ưu (OR-Tools). Chỉ gợi ý, mọi BR vẫn do lõi kiểm (UC-29).
- AI dự đoán nguy cơ trễ của chuyến, train trên dataset công khai (Kaggle "Delivery Truck Trips Data" – cần kiểm tra), train lại bằng giờ thực tế từ các lần quét mã (UC-30).

## 8. Nền tảng (đề xuất, chưa chốt)
- Web cho điều phối, kế toán, quản lý; web responsive cho tài xế trên điện thoại (quét QR bằng camera, lấy GPS lúc quét). Không làm GPS theo dõi liên tục.
- FastAPI (Python) + React + PostgreSQL; bản đồ Leaflet + OpenStreetMap.

---

## Nguồn

- Hạng GPLX C1, C theo khối lượng toàn bộ theo thiết kế – Điều 57 Luật Trật tự, an toàn giao thông đường bộ 2024 (hiệu lực 01/01/2025): https://thuvienphapluat.vn/hoi-dap-phap-luat/tu-ngay-01012025-bang-lai-xe-hang-c-lai-duoc-xe-gi-thoi-han-bao-lau-138031288.html ; https://lsvn.vn/bo-cong-an-thong-tin-ve-viec-doi-giay-phep-lai-xe-cap-truoc-01-01-2025-1724814246-a146630.html
- Giờ lái ≤ 10 giờ/ngày, ≤ 48 giờ/tuần, liên tục ≤ 4 giờ – Điều 64 cùng luật: https://luatvietnam.vn/tin-van-ban-moi/de-tai-xe-lai-xe-lien-tuc-qua-4h-chu-phuong-tien-bi-phat-den-12-trieu-dong-186-100622-article.html
- Bảo hiểm TNDS bắt buộc của chủ xe cơ giới, thời hạn 1–3 năm – Nghị định 67/2023/NĐ-CP: https://lsvn.vn/o-to-duoc-mua-bao-hiem-xe-co-thoi-han-den-03-nam-1694558007-a135111.html
- Quy đổi thể tích đường bộ 1 m³ = 333 kg (cần kiểm tra): https://jobsgo.vn/blog/cbm-la-gi/ ; công thức của hãng chuyển phát: https://ghtk.vn/blog/cach-tinh-khoi-luong-van-chuyen-hang-hoa-chuan-toi-uu-chi-phi/
- Rose Rocket: https://marketplace.geotab.com/solutions/rose-rocket/ ; https://www.roserocket.com/solutions/mobile
- Smartlog STM SME: https://apps.apple.com/us/app/smartlog-tms-stm-sme/id6443633211
- MISA AMIS Kế toán – vận tải: https://helpact.misa.vn/ac/van-tai/
- Smart Cargo TMS: https://apps.apple.com/us/app/smart-cargo-tms-%C4%91pv/id1673436151
- Chưa kiểm tra: hạn đăng kiểm theo loại xe tải (chu kỳ kiểm định) – hệ thống chỉ lưu ngày hết hạn ghi trên giấy, không tự tính chu kỳ.
