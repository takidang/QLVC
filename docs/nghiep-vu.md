# Nghiệp vụ – Hệ thống quản lý vận tải (chuyến là trung tâm)

> Phiên bản: 0.5 (Kiệt đề xuất, Tài đã review, merge 16/10/2026) · Cập nhật: 30/10/2026 (chốt 5 câu từ ca test BR) · Nhóm 8
> Nguyên tắc: **Chuyến xe là trung tâm, đơn hàng là thứ được ghép vào chuyến.**
> Mọi use case, user story và test case trỏ về mã `BR-xx`, `ST-xx`, `CFG-xx` trong file này.
> Nguồn sự thật về nghiệp vụ cho code và tài liệu. Repo là bản gốc: sửa ở đây trước (chỉ phiên Claude Code sửa và commit), rồi tải lại file này lên mục tài liệu (knowledge) của Project trên claude.ai để chat không dùng bản cũ.
> Đề tài (thầy giao): "Hệ thống quản lý vận tải cho một doanh nghiệp vận tải hàng hóa nhỏ: CHUYẾN XE LÀ TRUNG TÂM, ĐƠN HÀNG LÀ THỨ ĐƯỢC GHÉP VÀO CHUYẾN."
> Đánh số: BR, UC, CFG bị bỏ thì ghi "Bỏ ở 0.5 – lý do", **không xóa và không dùng lại số**. Quy tắc mới từ BR-63, UC mới từ UC-32, tham số mới từ CFG-08. Bản 0.4 xem lịch sử git.

---

## Thay đổi so với 0.4

| Hạng mục | 0.4 | 0.5 | Lý do |
|---|---|---|---|
| Trạng thái chuyến | 8 | 6: `LEN_KE_HOACH` + `GHEP_DON` → `LAP`; `DANG_BOC` + `DANG_CHAY` → `DANG_CHAY` | Lập chuyến bắt buộc có xe, tài xế ngay; bước bốc hàng không có quy tắc riêng |
| Trạng thái đơn | 9 | 7: bỏ `MOI`; `KHONG_LAY_DUOC` + `GIAO_THAT_BAI` → `THAT_BAI`; `HOAN_HANG` → `TRA_HANG` | Cước chốt lúc tạo; "hàng đã trong tay công ty" suy ra từ lượt quét lấy |
| Điểm dừng | Bảng `DIEM_DUNG`, sắp tay (UC-14) | Suy ra tự động (BR-63) | Thứ tự trong cùng nút quyết định kịp/trễ hạn |
| ETA, kết thúc dự kiến | Không tính phút dừng | Cộng `CFG-08` mỗi điểm dừng (BR-63, 64) | Bỏ sót thời gian dừng làm ETA sai |
| Ghép/gỡ/đổi xe, tài xế | Kiểm đơn mới | Kiểm lại cả chuyến (BR-67) | ETA dịch, chuyến dài ra |
| Tạm ứng | Vượt định mức → Quản lý duyệt | Không được vượt định mức đã chốt (BR-53) | Bỏ một luồng duyệt |
| Công nợ | Thu nhiều lần, phiếu thu | Chỉ `CHUA_THU`/`DA_THU`, đánh dấu một hoặc nhiều đơn (BR-56) | Không xoay quanh chuyến |
| Bỏ | BR-27, 44, 61; UC-09, 14, 29, 31; CFG-03 | Hướng phát triển (mục 10) | Giảm phạm vi |
| Thêm | | Km đầu/cuối, sự cố, kết thúc do sự cố, theo dõi chuyến, cảnh báo trễ, chốt định mức vào chuyến, hiệu suất xe | Chuyến là đơn vị nghiệp vụ trọn vẹn (mục 9) |

---

## 0. Tham khảo sản phẩm tương tự (đã tra cứu)

| Sản phẩm | Điểm học được | Áp dụng vào đồ án |
|---|---|---|
| Rose Rocket (TMS, Bắc Mỹ) | Đơn có thể chia chặng để điều phối; hỗ trợ chuyến nhiều điểm dừng; app tài xế xem chuyến, điểm dừng, lấy chữ ký điện tử, chụp ảnh chứng từ; chữ ký xác nhận cả lúc lấy và lúc giao (POD) | Lấy: chuyến nhiều điểm dừng, chữ ký/ảnh POD. Bỏ: chia chặng đơn (vi phạm "không tách đơn"), tích hợp ELD/GPS liên tục |
| Smartlog STM SME (Việt Nam) | App tài xế ghi chi phí phát sinh, ảnh chứng từ POD, xem lương theo chuyến; quản lý theo dõi trạng thái đơn và chuyến | Lấy: tài xế tự ghi chi phí phát sinh kèm ảnh, lương theo chuyến. Bỏ: theo dõi vị trí trực tiếp |
| MISA AMIS Kế toán – mảng vận tải | Giá thành và lãi lỗ theo chuyến, theo phương tiện; công nợ tạm ứng theo từng lái xe | Lấy: lãi lỗ theo chuyến/xe/tháng, tạm ứng – quyết toán theo chuyến. Bỏ: sổ sách kế toán đầy đủ |
| Smart Cargo TMS – ĐPV (Việt Nam) | Phân công rõ người điều phối đơn/chuyến, báo cáo KPI nhân viên | Lấy: ghi người phụ trách chuyến. Bỏ: KPI (hướng phát triển) |

Nhận xét: các TMS lớn đều có định tuyến tối ưu + theo dõi GPS liên tục. Đồ án **không** làm GPS liên tục (chỉ GPS lúc quét), tuyến cố định và lịch trình suy ra theo quy tắc → đúng phạm vi 2 người/10 tuần.

---

## 1. Bài toán và giả định phạm vi (nhóm đã chốt 16/10/2026)

Doanh nghiệp vận tải nhỏ, khoảng 10 xe tải, chạy tuyến liên tỉnh cố định. **Chuyến xe là trung tâm; đơn là thứ được ghép vào chuyến.** Mỗi chuyến phải: **chạy đầy** (không quá tải, biết trước lời/lỗ), **đúng luật** (giấy tờ còn hạn, bằng lái đúng hạng, không lái quá giờ), **có bằng chứng** (mỗi lần lấy, giao có giờ, vị trí, ảnh, chữ ký), **rõ tiền** (tạm ứng, chi phí, doanh thu, lãi của chuyến). Năm vai trò: Quản lý, Điều phối, Tài xế, Kế toán, Khách.

| Mã | Câu hỏi | Quyết định của nhóm | Nếu sau này thầy yêu cầu khác |
|---|---|---|---|
| A1 | Lấy tận nơi hay khách mang tới kho? | **Cả hai** – kho là một điểm lấy | Không ảnh hưởng mô hình |
| A2 | Có xe thuê ngoài? | **Không** | Thêm thực thể Nhà xe, chi phí thuê thay cho dầu + lương → hướng phát triển |
| A3 | Nội thành, liên tỉnh? | **Liên tỉnh theo tuyến cố định**; nội thành = tuyến 1 nút | Chỉ đổi dữ liệu tuyến |
| A4 | Khách tự tạo đơn? | **Không** – Điều phối tạo đơn (khách gọi/nhắn). Khách chỉ tra cứu | Thêm thực thể "yêu cầu gửi hàng" tách riêng khỏi đơn; Điều phối duyệt yêu cầu thì sinh đơn `CHO_GHEP`. Vòng đời đơn không đổi |
| A5 | Thanh toán thế nào, có COD? | **Người gửi trả, ghi công nợ, không COD** | COD để hướng phát triển |
| A6 | Hoàn hàng, giao lại có tính phí? | **Không tính phí**; trả hàng xử lý ngoài hệ thống | Thêm phí hoàn vào cước |
| A7 | Chỉ phục vụ tuyến ≤ 10 giờ chạy (mỗi chuyến một tài xế)? | **Có** (BR-66) | Tuyến dài cần hai tài xế → hướng phát triển |
| A8 | Có giữ góc nhìn chủ xe (km, dầu, lãi theo xe)? | **Có**, ở mức vài trường và báo cáo | Bỏ UC-34 và phần mở rộng của UC-26 |

Giả định khác:
- Mỗi chuyến một tài xế; tuyến cố định, không tự tìm đường.
- Không GPS liên tục; tiến độ lấy từ các lượt quét. Tài xế cần có mạng, không offline.
- Một đơn nhiều kiện: in nhiều tem cùng một mã, quét một lần.
- Không giao một phần, không tách đơn.
- Tài xế trả mọi chi phí chuyến bằng tiền tạm ứng.
- Lương = khoán theo chuyến; lương cứng và BHXH nằm ngoài hệ thống.
- Doanh thu của đơn ghép lại tính cho chuyến giao thành công.

**Ngoài phạm vi (hướng phát triển):** mục 10.

---

## 2. Thuật ngữ và thực thể

| Thuật ngữ | Định nghĩa |
|---|---|
| **Tuyến** | Danh sách **nút** có thứ tự (tỉnh/thành hoặc kho), mỗi nút có `phut_tu_diem_dau`, `km_tu_diem_dau` và cờ `la_diem_nghi`. Có định mức chi phí (dầu, cầu đường, bốc xếp) và lương khoán tài xế mỗi chuyến. Tối đa 10 giờ chạy (BR-66) |
| **Chuyến** | Tuyến + giờ khởi hành + xe + tài xế + các đơn được ghép. Hệ thống sinh ra **lịch trình** (điểm dừng, ETA), **dòng thời gian** (km, lượt quét, chi phí, sự cố) và **sổ tiền** (tạm ứng, chi phí, lương, doanh thu, lãi) |
| **Điểm dừng** | Không lưu bảng. Mỗi đơn hiệu lực sinh 2 điểm: LẤY tại nút lấy (hoặc nơi giữ hàng) và GIAO tại nút giao. Thứ tự theo BR-63 |
| **Đơn hàng** | Khách + hàng (kg thực, m³, số kiện, mô tả) + điểm lấy + khung giờ lấy (không bắt buộc) + điểm giao + hạn giao + cước (chốt lúc tạo). Điểm lấy, điểm giao có tọa độ (Điều phối chấm trên bản đồ). Một đơn = một mã QR |
| **Nơi giữ hàng** | Nút + địa chỉ + tọa độ nơi đơn đã lấy nhưng chưa giao đang nằm (thường là kho). Bắt buộc khi ghép lại đơn đã lấy (BR-69); khi có, nó thay điểm lấy trong BR-03, 04, 63 |
| **Ghép** | Bản ghi liên kết Đơn–Chuyến, có cờ `hieu_luc`. Lịch sử ghép được giữ (đơn thất bại có thể có nhiều lần ghép) |
| **Sự cố** | Tài xế báo trong chuyến: loại, ghi chú, ảnh; trạng thái mở/đóng. Không đổi trạng thái chuyến; xe không chạy tiếp được thì Điều phối kết thúc do sự cố (BR-68) |
| **Tải trọng cho phép chở** | Khối lượng hàng tối đa xe được chở (khác *khối lượng toàn bộ theo thiết kế*, dùng để xét hạng bằng lái) |
| **Tỷ lệ lấp đầy** | max(tổng kg / tải trọng, tổng m³ / thể tích) |

### 2.1 Công thức

Mọi con số hệ thống tính ra đều theo bảng này; code viết mỗi dòng thành một hàm (domain), test theo đúng công thức. Số liệu đầu vào (giá, phút chạy, định mức, tham số CFG) là dữ liệu, thay bằng số thật không phải sửa công thức. Thời gian tính theo phút, giờ Việt Nam; tiền là số nguyên đồng; kg, m³ là số thập phân (không dùng float).

| Đại lượng | Công thức | Đơn vị, làm tròn | BR |
|---|---|---|---|
| KL quy đổi | m³ × `CFG-01` | kg | BR-46 |
| KL tính cước | max(kg thực, KL quy đổi) | kg | BR-47 |
| Cước | max(cước tối thiểu, đơn giá/kg × KL tính cước), làm tròn **lên** bội `CFG-06`; dùng bản sao giá chốt lúc tạo đơn | đồng | BR-32, 48 |
| Phút dừng của điểm | Hiện bằng `CFG-08` cho mọi điểm. Viết thành hàm riêng để sau thay bằng số theo loại điểm hoặc theo dữ liệu thật | phút | BR-63 |
| ETA điểm dừng i | giờ khởi hành + `phut_tu_diem_dau` của nút chứa i + Σ phút dừng của các điểm đứng trước i | phút | BR-63 |
| Kết thúc dự kiến | ETA điểm cuối + phút dừng điểm cuối + `CFG-05`. Chạy rỗng: giờ khởi hành + `phut_tu_diem_dau` nút cuối + `CFG-05` | phút | BR-64 |
| Khoảng chiếm | [giờ khởi hành, kết thúc dự kiến), **nửa mở**: chuyến kết thúc 14:00 không chồng chuyến bắt đầu 14:00 | — | BR-16, 17, 64 |
| Giờ lái dự kiến | `phut_tu_diem_dau` nút cuối; qua nửa đêm chia theo phần giao với từng ngày | phút | BR-18, 19, 65 |
| Tỷ lệ lấp đầy | max(Σ kg / tải trọng, Σ m³ / thể tích) | % | — |
| Lãi dự kiến | Σ cước đơn hiệu lực − (định mức dầu + cầu đường + bốc xếp) − lương khoán; khi `LAP` lấy từ tuyến, từ khi chốt lấy số đã chốt | đồng | BR-52, 71 |
| ETA kế hoạch | ETA của từng điểm tại lúc chốt chuyến, **lưu lại**, không tính lại khi chạy | phút | BR-71 |
| Độ trễ của điểm | giờ quét thực tế (giờ máy chủ) − ETA kế hoạch của điểm đó; âm là sớm | phút | BR-73 |
| Kết thúc dự kiến khi đang chạy | kết thúc dự kiến lúc chốt + max(0, độ trễ của lượt quét gần nhất) | phút | BR-73 |
| Lãi chuyến | Σ doanh thu đơn giao thành công trên chuyến − Σ chi phí đã duyệt − lương (đã chốt, hoặc nhập tay theo BR-68) | đồng | BR-50, 51 |
| Chênh lệch tạm ứng | Σ tạm ứng `HIEU_LUC` − Σ chi phí đã duyệt; dương: tài xế nộp lại, âm: công ty trả thêm | đồng | BR-55 |
| Dầu tham khảo | (km kết thúc − km bắt đầu) × `dinh_muc_lit_100km` / 100; chỉ để xem | lít | UC-24, 34 |
| Lãi xe theo tháng | Σ lãi các chuyến của xe khởi hành trong tháng − chi phí cố định tháng của xe | đồng | UC-26 |
| Hiệu suất xe theo tháng | % lấp đầy trung bình các chuyến không hủy; số chuyến chạy rỗng; Σ km; Σ lít dầu thực tế so với Σ dầu tham khảo | — | UC-34 |

Vì ETA phụ thuộc số điểm dừng, mọi thao tác làm đổi danh sách đơn, xe hoặc tài xế đều kiểm lại cả chuyến (BR-67).

---

## 3. Tham số cấu hình (Quản lý chỉnh được)

| Mã | Tham số | Mặc định | Nguồn / ghi chú |
|---|---|---|---|
| CFG-01 | Hệ số quy đổi thể tích (kg/m³) | 333 | Một số tài liệu logistics nêu đường bộ thường quy đổi 1 m³ = 333 kg; các hãng chuyển phát dùng công thức D×R×C/hằng số khác nhau → **cần kiểm tra với doanh nghiệp thực tế**, vì vậy để cấu hình |
| CFG-02 | Cảnh báo giấy tờ sắp hết hạn trước (ngày) | 30 | Đề xuất của nhóm |
| CFG-03 | ~~Bán kính cảnh báo vị trí quét (km)~~ | — | Bỏ ở 0.5 – BR-44 đã bỏ |
| CFG-04 | Số lần giao thất bại vì lý do phía khách trước khi chỉ còn trả hàng | 3 | Đề xuất của nhóm (BR-37) |
| CFG-05 | Thời gian đệm sau chuyến (phút) | 60 | Đề xuất: dỡ hàng, nghỉ trước chuyến sau |
| CFG-06 | Làm tròn cước | 1.000 đ | Đề xuất |
| CFG-07 | Giờ lái tối đa/ngày, /tuần, liên tục | 10 / 48 / 4 giờ | Điều 64 Luật TTATGT đường bộ 2024 (xem Nguồn) |
| CFG-08 | Phút dừng mỗi điểm | 20 | Đề xuất; **cần kiểm tra với nhà xe** |
| CFG-09 | Ngưỡng trễ so với ETA để gắn cờ trễ (phút) | 15 | Đề xuất (UC-32) |
| CFG-10 | Cảnh báo đơn chờ ghép khi còn dưới (giờ) tới hạn giao | 24 | Đề xuất (BR-73) |

---

## 4. Quy tắc nghiệp vụ

Mức độ: **Chặn** = hệ thống từ chối thao tác; **Cảnh báo** = cho làm nhưng hiện cảnh báo và ghi log.
Thời điểm kiểm: G = khi ghép/gỡ đơn, C = khi chốt chuyến, X = khi lập chuyến hoặc đổi xe/tài xế, B = khi tài xế bắt đầu chuyến.

### Nhóm A – Ghép đơn vào chuyến

| Mã | Quy tắc | Mức | Kiểm khi |
|---|---|---|---|
| BR-01 | Tổng **kg thực** của các đơn hiệu lực trong chuyến ≤ tải trọng cho phép chở của xe | Chặn | G, C, X |
| BR-02 | Tổng **m³** của các đơn hiệu lực trong chuyến ≤ thể tích thùng xe | Chặn | G, C, X |
| BR-03 | Điểm lấy (hoặc nơi giữ hàng, nếu có) và điểm giao của đơn đều thuộc một nút của tuyến chuyến | Chặn | G |
| BR-04 | Đúng chiều tuyến: thứ tự nút lấy (hoặc nút giữ hàng) ≤ thứ tự nút giao | Chặn | G |
| BR-05 | Nếu đơn có khung giờ lấy: ETA điểm LẤY nằm trong khung, **tính cả hai đầu** (ETA đúng bằng giờ đầu hoặc giờ cuối khung vẫn đạt; chốt 30/10). Khung giờ lấy **không bắt buộc**, không nhập thì coi là cả ngày | Chặn | G, C (theo BR-67) |
| BR-06 | ETA điểm GIAO ≤ hạn giao của đơn | Chặn | G, C (theo BR-67) |
| BR-07 | Một đơn có tối đa **một** bản ghi ghép `hieu_luc = true` | Chặn | G (ràng buộc unique ở CSDL) |
| BR-08 | Không tách đơn: toàn bộ kg, m³, số kiện của đơn đi cùng một chuyến | Chặn | Theo mô hình (đơn không có số lượng con) |
| BR-09 | Chỉ ghép đơn `CHO_GHEP` vào chuyến `LAP` | Chặn | G |
| BR-10 | Điểm dừng không lưu bảng riêng, không sắp tay: mỗi đơn hiệu lực sinh 2 điểm (LẤY, GIAO), thứ tự suy ra theo BR-63 (0.4: thêm/xóa bản ghi điểm dừng, sắp tay – bỏ) | — | Mỗi lần tính lịch trình |

> Ghi chú BR-01: bản này kiểm **tổng** (bảo thủ, đơn giản). Kiểm tải theo từng đoạn (hàng lên xuống dọc đường) là chính xác hơn nhưng để ở hướng phát triển.
> Ghi chú BR-05: xe đến sớm hơn đầu khung giờ lấy cũng bị chặn, vì mô hình chưa có việc đứng chờ. Đây là giới hạn đã biết, chọn để giữ ETA đơn giản; hướng phát triển: cho xe chờ và dịch ETA các điểm sau.

### Nhóm B – Xe và tài xế

| Mã | Quy tắc | Mức | Kiểm khi |
|---|---|---|---|
| BR-11 | Xe ở trạng thái `HOAT_DONG` (không `NGUNG`). Xe đi bảo dưỡng thì chuyển `NGUNG` tạm; lịch bảo dưỡng là hướng phát triển | Chặn | X, C, B |
| BR-12 | Hạn đăng kiểm của xe ≥ ngày kết thúc dự kiến chuyến | Chặn | X, C, B, G (theo BR-67) |
| BR-13 | Hạn bảo hiểm TNDS bắt buộc của xe ≥ ngày kết thúc dự kiến chuyến | Chặn | X, C, B, G (theo BR-67) |
| BR-14 | Hạng GPLX tài xế phù hợp **khối lượng toàn bộ theo thiết kế** của xe: ≤ 3.500 kg → B trở lên; > 3.500–7.500 kg → C1 trở lên; > 7.500 kg → C. Thứ bậc: C ⊇ C1 ⊇ B | Chặn | X, C, B |
| BR-15 | GPLX tài xế còn hạn đến ngày kết thúc dự kiến chuyến | Chặn | X, C, B, G (theo BR-67) |
| BR-16 | Xe không có hai chuyến (khác `HUY`) có khoảng chiếm (BR-64) giao nhau | Chặn | X, C, G (theo BR-67) |
| BR-17 | Tài xế không có hai chuyến (khác `HUY`) có khoảng chiếm (BR-64) giao nhau | Chặn | X, C, G (theo BR-67) |
| BR-18 | Tổng giờ lái dự kiến (BR-65) của tài xế trong một ngày (00:00–24:00) ≤ 10 giờ | Chặn | X, C |
| BR-19 | Tổng giờ lái dự kiến của tài xế trong một tuần (Thứ Hai 00:00 → hết Chủ Nhật, giờ Việt Nam; chốt 30/10) ≤ 48 giờ | Chặn | X, C |
| BR-20 | Giữa hai nút liên tiếp có `la_diem_nghi` cách nhau > 4 giờ chạy → cảnh báo tuyến thiếu điểm nghỉ | Cảnh báo | Khi lưu tuyến |
| BR-21 | Xe/tài xế có giấy tờ hết hạn trong `CFG-02` ngày (tính cả ngày thứ `CFG-02`; chốt 30/10) → hiện trên bảng cảnh báo | Cảnh báo | Hằng ngày, trang chủ |

> Ghi chú BR-18/19/20: hệ thống chỉ kiểm **giờ lái dự kiến** theo lịch. Giờ lái thực tế cần thiết bị giám sát hành trình – ngoài phạm vi.
> Ghi chú BR-14: không xét rơ moóc (ngoài phạm vi).

### Nhóm C – Vòng đời chuyến (xem mục 5.1)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-22 | Lập chuyến bắt buộc có tuyến, giờ khởi hành, xe và tài xế thỏa BR-11…19 ngay khi tạo; chuyến sinh ra ở `LAP` | Chặn |
| BR-23 | Chốt (`LAP → DA_CHOT`): kiểm lại toàn bộ nhóm A, B (giấy tờ, lịch có thể đã đổi); chuyến 0 đơn phải xác nhận "chạy rỗng"; chốt định mức và lương vào chuyến (BR-71) | Chặn |
| BR-24 | Mở chốt (`DA_CHOT → LAP`) chỉ khi chuyến không còn tạm ứng `HIEU_LUC`. Muốn mở chốt thì Kế toán ghi thu hồi trước | Chặn |
| BR-25 | Hủy chuyến chỉ khi trạng thái ∈ {`LAP`, `DA_CHOT`}, bắt buộc lý do; mọi đơn trong chuyến về `CHO_GHEP`; còn tạm ứng `HIEU_LUC` thì Kế toán ghi `DA_THU_HOI` trước (ghi nhật ký BR-62) | Chặn |
| BR-26 | Bắt đầu (`DA_CHOT → DANG_CHAY`) chỉ do **tài xế của chuyến**, trong ngày khởi hành dự kiến; kiểm lại BR-11…15; nhập km (BR-70) | Chặn |
| BR-27 | ~~Xuất phát `DANG_BOC → DANG_CHAY`~~ | Bỏ ở 0.5 – gộp bước bốc hàng vào bước chạy |
| BR-28 | Tài xế kết thúc (`DANG_CHAY → HOAN_THANH`) chỉ khi mọi đơn hiệu lực đã `DA_GIAO` hoặc `THAT_BAI`; nhập km cuối (BR-70) | Chặn |
| BR-29 | Sau `DA_QUYET_TOAN`, chuyến và chi phí chỉ đọc | Chặn |
| BR-30 | Mọi chuyển trạng thái chuyến và đơn ghi lịch sử: trạng thái cũ, mới, người thực hiện, thời điểm, lý do | — |

### Nhóm D – Đơn hàng (xem mục 5.2)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-31 | Đơn hợp lệ: có khách, kg > 0, m³ > 0, số kiện ≥ 1, điểm lấy ≠ điểm giao, hạn giao > thời điểm tạo; nếu có khung giờ lấy thì `từ < đến` và hạn giao > `từ` | Chặn |
| BR-32 | Tạo đơn tính và **chốt cước ngay**: lưu bản sao đơn giá/kg, cước tối thiểu, hệ số `CFG-01` và bước làm tròn `CFG-06` vào đơn. BR-33 tính lại cước chỉ từ bản sao này; đổi bảng giá hay cấu hình sau đó không ảnh hưởng đơn đã tạo | — |
| BR-33 | Sửa kg/m³/điểm/khung giờ/hạn giao chỉ khi hàng chưa lấy (`CHO_GHEP`, `DA_GHEP`); đơn đang ghép thì kiểm theo BR-67, vi phạm thì từ chối sửa. Cước tính lại từ bản sao đã chốt, không bao giờ nhập tay | Chặn |
| BR-34 | Hủy đơn khi ∈ {`CHO_GHEP`, `DA_GHEP`} (đang ghép thì gỡ khỏi chuyến trước), hoặc `THAT_BAI` chưa có lượt quét lấy | Chặn |
| BR-35 | Không giao một phần: một đơn hoặc giao thành công toàn bộ, hoặc thất bại | Chặn |
| BR-36 | Đơn `THAT_BAI`: khi chuyến hoàn thành, bản ghi ghép chuyển `hieu_luc = false`; Điều phối chọn **ghép lại** (→ `CHO_GHEP`, theo BR-69 nếu đã lấy), **trả hàng** (→ `TRA_HANG`, chỉ khi đã có lượt quét lấy; xử lý ngoài hệ thống, không doanh thu) hoặc **hủy** (→ `HUY`, chỉ khi chưa có lượt quét lấy) | Chặn |
| BR-37 | `CFG-04` chỉ đếm thất bại **khi giao** vì lý do phía khách; lý do "sự cố xe" và thất bại khi lấy không tính. Đạt ngưỡng → không được ghép lại, chỉ còn trả hàng | Chặn |

> Ghi chú BR-34, 36 (chốt 30/10): đơn đúng trạng thái `THAT_BAI` nhưng sai điều kiện lượt quét lấy (hủy khi đã lấy, trả hàng khi chưa lấy) → **422** kèm mã BR; sai trạng thái (ví dụ hủy đơn `DA_LAY`) → 409.

### Nhóm E – Quét mã (tài xế)

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-38 | Tài xế chỉ quét được đơn có bản ghi ghép hiệu lực thuộc chuyến của chính mình đang ở `DANG_CHAY` | Chặn |
| BR-39 | Quét **lấy**: đơn `DA_GHEP` → `DA_LAY`. Báo **không lấy được** (lý do + ảnh) → `THAT_BAI` | Chặn |
| BR-40 | Quét **giao**: đơn `DA_LAY` → `DA_GIAO`, hoặc báo giao không được → `THAT_BAI` | Chặn |
| BR-41 | Giao thành công bắt buộc: ≥ 1 ảnh, chữ ký người nhận, tên người nhận | Chặn |
| BR-42 | Thất bại (lấy hoặc giao) bắt buộc: lý do (chọn từ danh mục; mỗi lý do ghi phía `KHACH` hoặc `SU_CO_XE` để BR-37 đếm) + ≥ 1 ảnh | Chặn |
| BR-43 | Mỗi lượt quét lưu: giờ **máy chủ**, GPS (vĩ độ, kinh độ, độ chính xác) nếu điện thoại cho phép. Không có GPS vẫn cho quét nhưng gắn cờ `thieu_gps` | Cảnh báo |
| BR-44 | ~~Cảnh báo quét sai vị trí theo tọa độ địa chỉ đơn~~ | Bỏ ở 0.5 – không tự đo khoảng cách. Vẫn giữ tọa độ điểm lấy, điểm giao để sau làm lại dễ |
| BR-45 | Quét lại một đơn đã chuyển trạng thái → không tạo bản ghi mới, trả về trạng thái hiện tại (idempotent) | — |

### Nhóm F – Cước, chi phí, tạm ứng, quyết toán, công nợ

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-46 | KL quy đổi (kg) = m³ × `CFG-01` | — |
| BR-47 | KL tính cước = max(kg thực, KL quy đổi) | — |
| BR-48 | Cước = max(cước tối thiểu, đơn giá/kg của cặp (tỉnh lấy, tỉnh giao) × KL tính cước), làm tròn lên theo `CFG-06`. Không có giá cho cặp tỉnh → **không tạo được đơn** | Chặn |
| BR-49 | Kiểm tải (BR-01) dùng **kg thực**, không dùng KL tính cước | — |
| BR-50 | Doanh thu của đơn ghi nhận cho **chuyến giao thành công**; chuyến giao thất bại ghi doanh thu đơn đó = 0 (chi phí vẫn tính) | — |
| BR-51 | Lãi chuyến = Σ doanh thu đơn ghi nhận − Σ chi phí đã duyệt − lương tài xế (đã chốt theo BR-71, hoặc nhập tay theo BR-68) | — |
| BR-52 | Lãi dự kiến = Σ cước đơn hiệu lực − định mức chi phí − lương khoán (khi `LAP` lấy từ tuyến, từ khi chốt lấy số đã chốt); hiện khi ghép và khi chốt; âm thì cảnh báo, yêu cầu xác nhận | Cảnh báo |
| BR-53 | Tạm ứng cấp khi chuyến từ `DA_CHOT` tới trước `HOAN_THANH`; tổng tạm ứng `HIEU_LUC` ≤ định mức chi phí đã chốt của chuyến (dầu + cầu đường + bốc xếp). Vượt → chặn (bỏ luồng Quản lý duyệt). Kiểm ở mọi lần tạo và sửa. Trạng thái: `HIEU_LUC` / `DA_THU_HOI` | Chặn |
| BR-54 | Chi phí: số tiền > 0, ghi chú, ≥ 1 ảnh chứng từ; khoản dầu ghi thêm số lít. Tài xế ghi được tới khi chuyến quyết toán | Chặn |
| BR-55 | Quyết toán chỉ khi `HOAN_THANH` và không còn khoản chi `CHO_DUYET`; Kế toán duyệt từng khoản chi. Chênh lệch = tổng tạm ứng `HIEU_LUC` − tổng chi tài xế chi được duyệt: dương → tài xế nộp lại, âm → công ty trả thêm. Phải ghi cách xử lý chênh lệch (tài xế đã nộp / công ty đã trả, hình thức, thời điểm) | Chặn |
| BR-56 | Công nợ: đơn `DA_GIAO` tự sinh khoản phải thu bằng cước. **Trạng thái thanh toán** (`CHUA_THU`, `DA_THU`) là trường riêng, không phải trạng thái vòng đời đơn. Kế toán đánh dấu đã thu cho một hoặc nhiều đơn | — |
| BR-61 | ~~Điều chỉnh cước tay~~ | Bỏ ở 0.5 – hướng phát triển |
| BR-62 | Nhật ký tiền: mọi lần tạo, sửa, duyệt, từ chối chi phí, tạm ứng (kể cả thu hồi), quyết toán, lương nhập tay, khoản phải thu đều ghi: người làm, thời điểm (giờ máy chủ), giá trị cũ, giá trị mới, lý do. Chỉ thêm, không sửa/xóa. Tách khỏi lịch sử trạng thái (BR-30) | Chặn |

### Nhóm G – Phân quyền, tra cứu, dữ liệu

| Mã | Quy tắc | Mức |
|---|---|---|
| BR-57 | Phân quyền theo vai trò, kiểm tại **máy chủ** cho mọi API (ẩn nút trên giao diện là không đủ) | Chặn |
| BR-58 | Tài xế chỉ xem và thao tác chuyến được giao cho mình | Chặn |
| BR-59 | Khách tra cứu không cần tài khoản: nhập mã đơn + 4 số cuối SĐT người gửi hoặc người nhận. Chỉ hiện trạng thái và mốc thời gian, không hiện GPS, SĐT tài xế, cước | Chặn |
| BR-60 | Xe, tài xế, tuyến, khách đã có chuyến/đơn tham chiếu thì không xóa, chỉ chuyển `NGUNG` | Chặn |

### Nhóm H – Thời gian, sự kiện chuyến (mới ở 0.5)

| Mã | Quy tắc | Mức | Kiểm khi |
|---|---|---|---|
| BR-63 | ETA điểm dừng = giờ khởi hành + `phut_tu_diem_dau` của nút + Σ phút dừng của các điểm đứng trước (phút dừng mỗi điểm hiện bằng `CFG-08`, mục 2.1). Thứ tự điểm dừng: theo thứ tự nút; trong cùng một nút, các điểm LẤY trước rồi tới các điểm GIAO. Điểm LẤY: đầu khung giờ lấy sớm trước, đơn không có khung xếp sau, cùng thì theo mã đơn. Điểm GIAO: hạn giao sớm trước, cùng hạn thì theo mã đơn | — | Mỗi lần tính lịch trình |
| BR-64 | Kết thúc dự kiến = ETA điểm cuối + phút dừng điểm cuối + `CFG-05`. Chuyến 0 đơn (chạy rỗng): giờ khởi hành + thời gian toàn tuyến + `CFG-05`. Khoảng chiếm = [khởi hành, kết thúc dự kiến) | — | Mỗi lần tính lịch trình |
| BR-65 | Giờ lái dự kiến = `phut_tu_diem_dau` của nút cuối, không tính phút dừng và `CFG-05`. Chuyến qua nửa đêm chia theo phần giao với từng ngày (làm rõ BR-18, 19) | — | X, C |
| BR-66 | Tuyến có thời gian chạy (`phut_tu_diem_dau` nút cuối) ≤ 10 giờ | Chặn | Khi lưu tuyến |
| BR-67 | Mỗi lần ghép, gỡ đơn, đổi xe hoặc đổi tài xế: kiểm lại cho cả chuyến BR-01, 02, 05, 06 (ETA dịch theo số điểm dừng), BR-12, 13, 15 (kết thúc dự kiến có thể lùi sang ngày sau), BR-16, 17 (khoảng chiếm dài ra); đổi tài xế thì kiểm thêm BR-14, 18, 19. Vi phạm ở bất kỳ đơn nào → không thực hiện thao tác, nêu đơn bị ảnh hưởng | Chặn | G, X |
| BR-68 | Điều phối kết thúc chuyến `DANG_CHAY` do sự cố (lý do bắt buộc, gắn cờ `ket_thuc_bat_thuong`): đơn `DA_LAY` và `DA_GHEP` thành `THAT_BAI` với lý do "sự cố xe"; khoảng chiếm kết thúc ở giờ kết thúc thực tế (xe và tài xế được giải phóng). Điều phối nhập km cuối nếu biết (cập nhật `km_dong_ho`); không có thì để trống (xem BR-70). Xe cần sửa thì Điều phối chuyển `NGUNG` (BR-11 chặn xe ở chuyến sau). Kế toán nhập lương chuyến bằng tay, có lý do | Chặn | — |
| BR-69 | Ghép lại đơn `THAT_BAI` đã lấy hàng: bắt buộc cập nhật nơi giữ hàng (thành điểm lấy mới); được đổi hạn giao theo thỏa thuận với khách; cước giữ nguyên | Chặn | — |
| BR-70 | Bắt đầu và kết thúc chuyến phải nhập km đồng hồ kèm ảnh; km bắt đầu ≥ km kết thúc chuyến trước của cùng xe (chuyến đầu: ≥ `km_dong_ho` của xe; chuyến trước kết thúc do sự cố không có km cuối: ≥ km bắt đầu của chuyến đó); km kết thúc > km bắt đầu. Kết thúc chuyến (có km) cập nhật `km_dong_ho` | Chặn | B, khi kết thúc |
| BR-71 | Lúc chốt chuyến, lưu vào chuyến: định mức chi phí và lương khoán của tuyến, và **ETA kế hoạch** của từng điểm dừng (mục 2.1). Đổi định mức tuyến sau đó không ảnh hưởng; mở chốt rồi chốt lại thì lưu lại theo số mới | — | C |
| BR-72 | Giao sau hạn vẫn cho giao, đánh dấu "giao trễ"; không giảm cước | Cảnh báo | Khi quét giao |
| BR-73 | Khi chuyến `DANG_CHAY`: độ trễ = giờ quét thực tế − ETA kế hoạch của điểm đó (mục 2.1); trễ quá `CFG-09` thì gắn cờ trễ. **Kết thúc dự kiến khi đang chạy** = kết thúc dự kiến lúc chốt + max(0, độ trễ của lượt quét gần nhất); nếu khoảng [khởi hành, kết thúc dự kiến khi đang chạy) chồng lên khoảng chiếm của chuyến kế tiếp của cùng xe hoặc tài xế → cảnh báo Điều phối. Ngoài ra cảnh báo đơn `CHO_GHEP` còn dưới `CFG-10` giờ tới hạn giao mà chưa được ghép. Hệ thống không tự đổi lịch | Cảnh báo | Mỗi lượt quét; bảng cảnh báo |

> Ghi chú BR-67: gỡ đơn làm ETA các đơn phía sau sớm lên, có thể rơi trước đầu khung giờ lấy (BR-05) – khi đó gỡ bị chặn.

---

## 5. Trạng thái

### 5.1 Chuyến (`ST-T`)

| Mã | Trạng thái | Ý nghĩa |
|---|---|---|
| `LAP` | Đang lập | Có tuyến, giờ, xe, tài xế hợp lệ; đang ghép/gỡ đơn |
| `DA_CHOT` | Đã chốt | Danh sách đơn cố định, định mức và lương đã chốt, được cấp tạm ứng, tài xế thấy chuyến |
| `DANG_CHAY` | Đang chạy | Tài xế đã bắt đầu: quét lấy, quét giao, ghi chi phí, báo sự cố |
| `HOAN_THANH` | Hoàn thành | Mọi đơn đã có kết quả (hoặc kết thúc do sự cố), chờ quyết toán |
| `DA_QUYET_TOAN` | Đã quyết toán | Khóa sổ |
| `HUY` | Hủy | |

| Từ | Sang | Ai | Điều kiện |
|---|---|---|---|
| (mới) | LAP | Điều phối | BR-22 |
| LAP | DA_CHOT | Điều phối | BR-23 |
| DA_CHOT | LAP | Điều phối | BR-24 |
| DA_CHOT | DANG_CHAY | Tài xế của chuyến | BR-26, BR-70 |
| DANG_CHAY | HOAN_THANH | Tài xế | BR-28, BR-70 |
| DANG_CHAY | HOAN_THANH | Điều phối (kết thúc do sự cố) | BR-68 |
| HOAN_THANH | DA_QUYET_TOAN | Kế toán | BR-55 |
| LAP / DA_CHOT | HUY | Điều phối | BR-25 |

### 5.2 Đơn hàng (`ST-O`)

| Mã | Trạng thái |
|---|---|
| `CHO_GHEP` | Đã tạo, cước đã chốt, chờ ghép chuyến |
| `DA_GHEP` | Đã ghép vào một chuyến |
| `DA_LAY` | Tài xế đã quét lấy |
| `DA_GIAO` | Giao thành công (kết thúc) |
| `THAT_BAI` | Không lấy được hoặc giao không được trong chuyến; đã lấy hay chưa suy ra từ lượt quét lấy |
| `TRA_HANG` | Trả lại người gửi, xử lý ngoài hệ thống (kết thúc, không doanh thu) |
| `HUY` | Hủy (kết thúc) |

| Từ | Sang | Ai / sự kiện | Điều kiện |
|---|---|---|---|
| (mới) | CHO_GHEP | Điều phối tạo đơn | BR-31, BR-32, BR-48 |
| CHO_GHEP | DA_GHEP | Ghép vào chuyến | BR-01…10, BR-67 |
| DA_GHEP | CHO_GHEP | Gỡ khỏi chuyến / chuyến bị hủy | Chuyến ∈ {LAP, HUY} |
| DA_GHEP | DA_LAY | Tài xế quét lấy | BR-38, BR-39 |
| DA_LAY | DA_GIAO | Tài xế quét giao | BR-40, BR-41, BR-72 |
| DA_GHEP | THAT_BAI | Lấy không được (tài xế báo, hoặc kết thúc do sự cố) | BR-39, BR-42, BR-68 |
| DA_LAY | THAT_BAI | Giao không được (tài xế báo, hoặc kết thúc do sự cố) | BR-40, BR-42, BR-68 |
| THAT_BAI | CHO_GHEP | Điều phối ghép lại | BR-36, BR-37, BR-69 |
| THAT_BAI | TRA_HANG | Điều phối, đơn đã có lượt quét lấy | BR-36, BR-37 |
| THAT_BAI | HUY | Điều phối, đơn chưa có lượt quét lấy | BR-34, BR-36 |
| CHO_GHEP / DA_GHEP | HUY | Điều phối | BR-34 |

**Ghi chú:**
1. Trạng thái thanh toán (`CHUA_THU`/`DA_THU`) là trường riêng (BR-56), tránh trạng thái đơn bị "kẹt" giữa vận hành và kế toán.
2. Gộp hai kiểu thất bại vì cách xử lý giống nhau; điểm khác duy nhất (hàng đã trong tay công ty chưa) = đơn đã có lượt quét lấy chưa.
3. Bỏ `MOI` vì cước chốt lúc tạo; không có bảng giá thì không tạo được đơn (BR-48).

---

## 6. Ma trận phân quyền (tóm tắt)

| Chức năng | Quản lý | Điều phối | Tài xế | Kế toán | Khách |
|---|---|---|---|---|---|
| Người dùng, cấu hình, bảng giá | ✔ | | | | |
| Xe, tài xế, tuyến, khách | ✔ | ✔ | | chi phí cố định xe | |
| Tạo/sửa/hủy đơn, xử lý đơn thất bại | ✔ | ✔ | | | |
| Lập chuyến, ghép đơn, chốt, hủy | ✔ | ✔ | | | |
| Theo dõi chuyến, đóng sự cố, kết thúc do sự cố | ✔ | ✔ | | | |
| Chuyến của mình: bắt đầu, kết thúc, quét, chi phí, báo sự cố | | | ✔ | | |
| Tạm ứng, quyết toán, công nợ | xem | | | ✔ | |
| Báo cáo lãi lỗ | ✔ | xem | | ✔ | |
| Hiệu suất xe | ✔ | | | xem | |
| Tra cứu đơn | | | | | ✔ (không đăng nhập) |

## 7. Module phụ trợ và dữ liệu cho AI (làm sau cùng)

- **UC-30 dự đoán nguy cơ trễ** của chuyến. Gợi ý ghép đơn bằng OR-Tools (UC-29) đã bỏ ở 0.5, chuyển sang hướng phát triển.
- **Ranh giới:** AI chỉ **gợi ý** cho Điều phối. Mọi quy tắc chặn (tải, tuyến, hạn giao, giấy tờ, giờ lái, tiền) dùng công thức cố định ở mục 2.1 để kết quả luôn như nhau, test được và giải thích được bằng mã BR. Kết quả AI không chặn thao tác, không đổi ETA kế hoạch.
- **Nguồn dữ liệu train:**
  1. Dataset công khai (Kaggle "Delivery Truck Trips Data" – cần kiểm tra nội dung và giấy phép). Cột khác hệ thống nên cần bước **chuyển đổi** sang khái niệm của đồ án: quãng đường, giờ khởi hành, số điểm dừng, thời gian dự kiến, thời gian thực tế, có trễ hay không.
  2. Dữ liệu của chính hệ thống: train lại dần khi có lượt quét thật.
  - Không train trên dữ liệu tự sinh bằng công thức của hệ thống (mô hình chỉ học lại công thức, không có giá trị).
- **Dữ liệu hệ thống thu để học** (đã có trong ERD): ETA kế hoạch và giờ quét thực tế từng điểm (ra độ trễ), giờ khởi hành/kết thúc thực tế, tuyến, xe, tài xế, số điểm dừng, tải, cờ giao trễ, lý do thất bại kèm `phia`, km đầu/cuối, số lít dầu.
- **Thay số giả định bằng số thật:** `CFG-08`, `phut_tu_diem_dau`, định mức là dữ liệu do Quản lý/Điều phối chỉnh; có dữ liệu thật thì cập nhật số, không sửa công thức. Phút dừng thật xấp xỉ bằng chênh lệch giữa các lượt quét liên tiếp; nút "đã đến điểm" cho tài xế là hướng phát triển.
- **Số liệu kịch bản mục 11** là test case cố định, tính tay kiểm được (NFR-FUN-01), không thay bằng dataset.

## 8. Nền tảng và triển khai (đã chốt 10/10/2026)
- **Một web app duy nhất**, chia màn hình theo vai trò:
  - Quản lý, Điều phối, Kế toán: dùng trên máy tính.
  - Tài xế: mở **cùng web đó trên trình duyệt điện thoại** (giao diện responsive), đăng nhập tài khoản tài xế. Quét QR bằng camera, lấy GPS lúc quét, chụp ảnh, ký trên màn hình. Không cài app. Có thể "Thêm vào màn hình chính" cho tiện. Không làm GPS theo dõi liên tục, không làm chế độ offline.
  - Khách hàng: trang **tra cứu công khai** trên cùng web, không cần tài khoản: nhập mã đơn + 4 số cuối SĐT (BR-59). Mã đơn có trên phiếu gửi hàng in kèm QR; Điều phối gửi mã cho khách (nhắn tay, ngoài hệ thống).
- Công nghệ: **FastAPI (Python)** + **React với TypeScript** + **PostgreSQL**; bản đồ Leaflet + OpenStreetMap. Lý do chọn Python: module phụ (mô hình dự đoán trễ) cùng ngôn ngữ; nhóm dùng AI hỗ trợ viết code nên chọn ngôn ngữ dễ đọc để tự giải thích được khi bảo vệ.
- Camera và GPS trên trình duyệt chỉ chạy qua **HTTPS** (hoặc localhost), nên bản demo phải có HTTPS.
- Triển khai (chi tiết kỹ thuật ở `docs/kien-truc.md`):
  - Dev: chạy local, PostgreSQL bằng `docker compose`. Thử camera trên điện thoại qua Cloudflare Quick Tunnel.
  - Demo: **Render** chạy một web service (FastAPI phục vụ luôn bản build React), tên miền miễn phí `*.onrender.com`, không mua domain. **Supabase** chứa PostgreSQL và Storage (bucket private) cho ảnh, chữ ký. Không dùng Postgres miễn phí của Render vì hết hạn sau 30 ngày.
  - Ổ đĩa Render không giữ file, nên mọi file upload vào Supabase Storage; ảnh chỉ xem qua link có hạn (NFR-SEC-04).
  - Chuỗi kết nối DB và khóa Supabase chỉ đặt trong Environment của Render; khóa `service_role` chỉ backend dùng.
  - Gói miễn phí: Render ngủ sau 15 phút không có truy cập, mở lại mất khoảng 1 phút; Supabase tạm dừng project sau 1 tuần không hoạt động. Có thể trả $7/tháng cho Render trong tháng bảo vệ. **Kiểm tra lại hạn mức ở tuần 8–9.**
  - Dữ liệu 10.000 đơn để test hiệu năng chỉ chạy local; bản demo seed vài trăm đơn.
- Hướng phát triển: app tài xế riêng bằng Flutter (dùng lại API), thông báo trạng thái đơn cho khách qua SMS/Zalo.

---

## 9. Vận hành chuyến

### 9.1 Chuyến gồm những gì

```
                        ┌────────────── CHUYẾN ──────────────┐
  Chuẩn bị (vào)        │  Kế hoạch: tuyến + giờ khởi hành    │        Kết quả (ra)
  ─────────────         │  Nguồn lực: xe + tài xế             │        ─────────────
  Xe, tài xế, tuyến ──▶ │  Hàng: các đơn được ghép            │ ──▶   Lãi lỗ chuyến
  Đơn chờ ghép     ──▶  │  Lịch trình: điểm dừng + ETA        │ ──▶   Lãi theo xe, theo tháng
  Bảng giá, định mức ─▶ │  Sự kiện: km, quét, chi phí, sự cố  │ ──▶   Đơn giao xong / thất bại
                        │  Tiền: tạm ứng, chi phí, lương,     │ ──▶   Tra cứu của khách
                        │        doanh thu, quyết toán        │
                        └─────────────────────────────────────┘
```

Đơn chỉ có ý nghĩa khi được ghép vào chuyến; kết quả của đơn (đã lấy, đã giao, thất bại) đều do sự kiện của chuyến tạo ra. **Trước chuyến** đảm bảo hợp lệ (tải, tuyến, giờ, luật); **trong chuyến** ghi bằng chứng (dòng thời gian); **sau chuyến** khóa sổ tài chính (quyết toán).

### 9.2 Việc ở từng trạng thái

| Trạng thái | Người dùng làm | Hệ thống làm | Sang bước sau khi |
|---|---|---|---|
| `LAP` | Điều phối chọn tuyến, giờ, xe, tài xế; ghép, gỡ đơn | Chỉ hiện xe/tài xế hợp lệ kèm lý do loại; chặn quá tải, sai tuyến, không kịp hạn; hiện % đầy, lịch trình, lãi dự kiến | Điều phối bấm Chốt |
| `DA_CHOT` | Kế toán cấp tạm ứng; Điều phối mở chốt nếu cần sửa (phải thu hồi tạm ứng trước) | Kiểm lại toàn bộ; chốt định mức, lương; cảnh báo lãi âm; chuyến hiện trên điện thoại tài xế | Tài xế bấm Bắt đầu đúng ngày |
| `DANG_CHAY` | Tài xế quét, ghi chi phí, báo sự cố; Điều phối theo dõi | Ghi km, lượt quét (giờ, GPS, ảnh, chữ ký), chi phí, sự cố; so thực tế với ETA, cảnh báo trễ | Tài xế bấm Kết thúc, hoặc Điều phối kết thúc do sự cố |
| `HOAN_THANH` | Điều phối xử lý đơn thất bại; Kế toán duyệt chi | Tính lãi tạm, bảng đối chiếu định mức – thực tế | Kế toán bấm Quyết toán |
| `DA_QUYET_TOAN` | Chỉ xem | Khóa chuyến; số liệu vào báo cáo tháng | — |
| `HUY` | Điều phối hủy kèm lý do khi chuyến chưa chạy | Trả đơn về hàng chờ; tạm ứng phải ghi đã thu hồi | — |

### 9.3 Màn hình chính

- **Bảng chuyến trong ngày**: chuyến theo ngày, lọc theo trạng thái; mỗi dòng có xe, tài xế, tuyến, giờ, % đầy, tiến độ ("3/6 điểm") và cờ đỏ (trễ, sự cố, đơn thất bại, chưa quyết toán).
- **Chi tiết chuyến** (5 thẻ): **Tổng quan** (tuyến, giờ, xe, tài xế, trạng thái, % đầy, lãi) · **Hàng** (đơn, thanh tải/thể tích, ghép/gỡ) · **Lịch trình** (điểm dừng, ETA, giờ thực tế, sớm/trễ) · **Dòng thời gian** (km, lượt quét kèm ảnh/chữ ký/GPS, chi phí, sự cố; là bằng chứng khi tranh chấp) · **Tiền** (tạm ứng, chi phí định mức – thực tế – chênh lệch, lương, doanh thu, lãi, chênh lệch tạm ứng).

### 9.4 Tình huống thường gặp

| Tình huống | Cách làm |
|---|---|
| Khách gửi thêm hàng sau khi đã chốt | Thu hồi tạm ứng nếu đã cấp → mở chốt → ghép thêm (BR-67) → chốt lại → cấp lại tạm ứng |
| Đổi xe hoặc tài xế | Chỉ khi `LAP` (mở chốt nếu cần); kiểm lại theo BR-67 |
| Tài xế không đi được, lỡ ngày khởi hành | Mở chốt → đổi tài xế hoặc đổi giờ; không thì hủy chuyến, đơn về hàng chờ |
| Chuyến đang trễ | Hệ thống gắn cờ; ảnh hưởng chuyến kế tiếp thì cảnh báo (BR-73). Điều phối quyết |
| Xe gặp sự cố nhẹ | Tài xế báo sự cố, chuyến chạy tiếp; tiền sửa xe ghi thành chi phí. Sửa lớn vượt tạm ứng: tài xế tự ứng, công ty trả lại khi quyết toán (chênh lệch âm, BR-55) |
| Xe hỏng, không chạy tiếp được | Điều phối kết thúc do sự cố (BR-68) |
| Giao thất bại | Sau khi chuyến xong: ghi nơi giữ hàng, đổi hạn nếu khách đồng ý → ghép chuyến sau (BR-69); hoặc trả hàng |

### 9.5 Chỉ số

- Trước khi chạy: % lấp đầy, lãi dự kiến.
- Trong khi chạy: điểm đã xong / tổng, phút sớm/trễ so với ETA.
- Sau khi chạy: lãi thực tế so với dự kiến kèm lý do lệch (đơn thất bại, chi vượt định mức); km thực tế so với km tuyến; dầu tham khảo = `dinh_muc_lit_100km` × km thực tế (chỉ để xem); chênh lệch tạm ứng.
- Theo xe, theo tháng: Σ lãi các chuyến − chi phí cố định tháng; % lấp đầy trung bình; số chuyến chạy rỗng; km; dầu thực tế so với định mức (đối chiếu chính thức theo tháng).

---

## 10. Hướng phát triển (ngoài phạm vi)

Xe thuê ngoài (A2) · COD (A5) · yêu cầu gửi hàng do khách tự tạo (A4) · OR-Tools gợi ý ghép đơn (UC-29) · điều chỉnh cước tay (BR-61, UC-31) · luồng duyệt tạm ứng vượt định mức · sổ tạm ứng cộng dồn · bảng lương tháng · lịch bảo dưỡng · bảng kê công nợ · biên bản kiểm tra xe trước khi chạy · cảnh báo quét sai vị trí (BR-44) · xe đến sớm đứng chờ và dịch ETA (BR-05) · nút "đã đến điểm" để đo phút dừng thật · kiểm tải theo từng đoạn · GPS liên tục, hành vi lái xe · xe lạnh · giờ cấm tải · tuyến dài nhiều tài xế (A7) · quét mã từng kiện, giao một phần, chia chặng/trung chuyển · rơ moóc · hóa đơn điện tử · chế độ offline cho tài xế · KPI nhân viên.

---

## 11. Kịch bản kiểm chứng (dùng cho test và demo)

> Số liệu minh họa do nhóm đặt ra (km, giá cước, giá dầu), không phải số liệu thật. Mỗi dòng ✔/✖ là một ca test cho BR ghi trong ngoặc.

**Dữ liệu.** `CFG-01` = 333, `CFG-05` = 60′, `CFG-06` = 1.000 đ, `CFG-08` = 20′.

Tuyến T01 TP.HCM → Cần Thơ. Định mức: dầu 550.000 + cầu đường 200.000 + bốc xếp 250.000 = 1.000.000 đ; lương khoán 600.000 đ/chuyến.

| Nút | Phút từ đầu | Km | Điểm nghỉ |
|---|---|---|---|
| TP.HCM | 0 | 0 | |
| Long An | 60 | 50 | |
| Tiền Giang | 120 | 75 | ✔ |
| Vĩnh Long | 210 | 135 | |
| Cần Thơ | 270 | 170 | |

| Xe | Tải | Thể tích | KL toàn bộ | Hạn đăng kiểm | Dầu | Km đồng hồ |
|---|---|---|---|---|---|---|
| X1 51C-111.11 | 5.000 kg | 20 m³ | 9.500 kg (cần C) | 30/11 | 15 l/100 km | 120.000 |
| X2 51C-222.22 | 1.500 kg | 8 m³ | 3.400 kg (cần B) | 19/10 | | |

Tài xế: An (hạng C, đã có chuyến C00 lúc 13:45 ngày 20/10, 4 giờ lái) · Bình (hạng B).
Bảng giá (đ/kg): HCM→Cần Thơ 1.500 · Long An→Cần Thơ 1.200 · HCM→Vĩnh Long 1.300 · HCM→Tiền Giang 1.000 · Vĩnh Long→Long An 1.200. Cước tối thiểu mọi cặp: 50.000 đ.

**1. Tạo đơn (19/10).**

| Đơn | Lấy → giao | Hàng | Hạn giao | Cước | Kết quả |
|---|---|---|---|---|---|
| Đ1 | HCM → Cần Thơ | 1.800 kg, 6 m³ (quy đổi 1.998 kg) | 20/10 14:00 | 1.998 × 1.500 = 2.997.000 | ✔ `CHO_GHEP` (BR-46…48) |
| Đ2 | Long An → Cần Thơ, lấy 06:30–09:00 | 1.200 kg, 3 m³ | 20/10 12:00 | 1.440.000 | ✔ |
| Đ3 | HCM → Vĩnh Long | 1.500 kg, 5 m³ (1.665 kg) | 20/10 10:00 | 2.164.500 → 2.165.000 | ✔ (làm tròn CFG-06) |
| Đ4 | HCM → Tiền Giang | 800 kg, 2 m³ | 20/10 18:00 | 800.000 | ✔ |
| Đ5 | Vĩnh Long → Long An | 500 kg, 1,5 m³ | 20/10 18:00 | 500 × 1.200 = 600.000 | ✔ tạo được, chặn lúc ghép |
| Đ6 | HCM → Cần Thơ | 2.500 kg, 5 m³ | 20/10 18:00 | 2.500 × 1.500 = 3.750.000 | ✔ tạo được, chặn lúc ghép |
| Đ8 | HCM → Tiền Giang | 300 kg, 1 m³ (quy đổi 333 kg) | 20/10 18:00 | 333 × 1.000 = 333.000 (BR-47: lấy KL quy đổi vì lớn hơn kg thực) | ✔ (dùng cho ca BR-67) |
| Đ7 | Cần Thơ → Cà Mau | | | Không có giá | ✖ không tạo được (BR-48) |

**2. Lập chuyến C01** (T01, chạy ngày 20/10/2026, khởi hành 06:00).
- X2 ✖ đăng kiểm hết 19/10, trước ngày chạy 20/10 (BR-12). X1 ✔.
- Bình ✖ hạng B, xe 9.500 kg cần C (BR-14). An ✔: giờ lái 20/10 = 4,5 + 4 = 8,5 ≤ 10 (BR-18, 65).
- Biến thể: nếu C00 của An bắt đầu 13:00 → khi ghép đủ đơn, C01 chiếm [06:00, 13:30) chồng C00 ✖ (BR-17 theo BR-67). Lúc lập (chưa có đơn) C01 chỉ chiếm tới 11:30 (BR-64, chạy rỗng: 06:00 + 270′ + 60′) nên chưa bị chặn.

**3. Ghép đơn.**
- Ghép Đ1, Đ4 ✔ (2.600 kg, 8 m³).
- Thử trên chuyến đang có Đ1, Đ4; mỗi ca chỉ vi phạm đúng một quy tắc:
  - Đ5 ✖ sai chiều (BR-04).
  - Đ6 ✖ 1.800 + 800 + 2.500 = 5.100 kg > 5.000 (BR-01); thể tích 13 m³ và hạn giao vẫn đạt.
  - Đ3 ✖ ETA Vĩnh Long = 06:00 + 210′ + 4 × 20′ = 10:50 > 10:00 (BR-06); tải 4.100 kg, thể tích 13 m³ vẫn đạt.
- Ghép Đ2 ✔: 3.800 kg ≤ 5.000, 11 m³ ≤ 20, đúng tuyến, đúng chiều. Lịch trình:

| # | Điểm | Việc | ETA | Hạn / khung | |
|---|---|---|---|---|---|
| 1 | TP.HCM | Lấy Đ1 | 06:00 | | ✔ |
| 2 | TP.HCM | Lấy Đ4 | 06:20 | | ✔ |
| 3 | Long An | Lấy Đ2 | 07:40 | 06:30–09:00 | ✔ BR-05 |
| 4 | Tiền Giang | Giao Đ4 | 09:00 | 18:00 | ✔ |
| 5 | Cần Thơ | Giao Đ2 | 11:50 | 12:00 | ✔ BR-63: hạn sớm đi trước |
| 6 | Cần Thơ | Giao Đ1 | 12:10 | 14:00 | ✔ |

- Nếu xếp ngược thứ tự giao ở Cần Thơ: Đ2 12:10 > 12:00 ✖ → ca test của BR-63.
- Thử ghép thêm Đ8 ✖ (ca test BR-67): bản thân Đ8 hợp lệ (tải 4.100 kg, kịp hạn), nhưng thêm một điểm lấy ở HCM và một điểm giao ở Tiền Giang trước Cần Thơ, nên ETA giao Đ2 = 06:00 + 270′ + 6 × 20′ = 12:30 > 12:00. Lỗi nằm ở **đơn đã ghép**, không phải đơn mới → không ghép.
- Lấp đầy = max(3.800/5.000, 11/20) = 76%. Kết thúc dự kiến = 12:10 + 20′ + 60′ = 13:30 (BR-64), không chồng C00 lúc 13:45 (BR-17). Lãi dự kiến = 5.237.000 − 1.000.000 − 600.000 = 3.637.000 (BR-52).

**4. Chốt và tạm ứng (19/10 16:00).** Kiểm lại toàn bộ ✔ → `DA_CHOT`, lưu định mức, lương và ETA kế hoạch 6 điểm (BR-71). Tạm ứng 1.000.000 ✔; nhập 1.200.000 ✖ vượt định mức (BR-53). Mở chốt khi còn tạm ứng `HIEU_LUC` ✖ (BR-24).

**5. Ngày chạy 20/10 (An).**

| Giờ | Sự kiện | Hệ thống |
|---|---|---|
| 05:45 | Bắt đầu, km 120.000 + ảnh | Đúng ngày, giấy tờ ✔, km ≥ km cuối của X1 ✔ → `DANG_CHAY` (BR-26, 70) |
| 06:05 | Quét lấy Đ1; mạng chập chờn, bấm lại | `DA_LAY`, trễ 5′; lần sau không sinh bản ghi (BR-45) |
| 06:30 | Quét lấy Đ4 | Trễ 10′ so với ETA kế hoạch 06:20; dự kiến xong 13:30 + 10′ = 13:40, không chồng C00 13:45 → không cảnh báo (BR-73) |
| 08:10 | Quét lấy Đ2 ở Long An | Trễ 30′ so với ETA kế hoạch 07:40 > `CFG-09` → cờ trễ; dự kiến xong 13:30 + 30′ = 14:00 chồng C00 13:45 → cảnh báo Điều phối (BR-73) |
| 09:40 | Giao Đ4: ảnh, chữ ký, tên | `DA_GIAO`, sinh phải thu 800.000 `CHUA_THU` (BR-41, 56) |
| 10:00 | Chi phí dầu 26 lít = 520.000 + ảnh | `CHO_DUYET` (BR-54) |
| 10:30 | Chi phí cầu đường 230.000 + ảnh | ✔ |
| 12:35 | Giao Đ2 (hạn 12:00) | `DA_GIAO`, đánh dấu giao trễ, cước giữ nguyên (BR-72) |
| 12:40 | Đ1: người nhận vắng, lý do + ảnh | `THAT_BAI`, lần giao thất bại 1/3 (BR-42, 37) |
| 12:50 | Chi phí bốc xếp 300.000 | ✔ |
| 13:00 | Kết thúc, km 120.178 | Mọi đơn có kết quả ✔ → `HOAN_THANH` (BR-28, 70); 178 km so với 170 km tuyến (chỉ hiển thị) |

Ca đối chứng BR-73: nếu C00 bắt đầu 14:00 thì [06:00, 14:00) không chồng [14:00, …) (khoảng nửa mở) → không cảnh báo.

Khách Cty A tra cứu Đ1 bằng mã + 4 số cuối SĐT: "Giao không thành công – đang chờ giao lại", không thấy cước, GPS (BR-59).

**6. Xử lý Đ1.** Đ1 đã có lượt quét lấy → bắt buộc nơi giữ hàng: kho Cần Thơ (BR-69). Đổi hạn giao 21/10 17:00 → `CHO_GHEP`, cước giữ 2.997.000. Ghép vào C05 ngày 21/10 (tuyến qua Cần Thơ); doanh thu Đ1 tính cho C05 (BR-50).

**7. Quyết toán C01 (21/10).**

| Khoản | Thực tế | Định mức | Chênh lệch |
|---|---|---|---|
| Dầu (26 lít) | 520.000 | 550.000 | −30.000 |
| Cầu đường | 230.000 | 200.000 | +30.000 |
| Bốc xếp | 300.000 | 250.000 | +50.000 |
| Tổng | 1.050.000 | 1.000.000 | +50.000 |

- Dầu tham khảo: 178 km × 15 / 100 = 26,7 lít; thực tế 26 lít.
- Doanh thu = Đ2 1.440.000 + Đ4 800.000 = 2.240.000 (BR-50). Lãi = 2.240.000 − 1.050.000 − 600.000 = 590.000 (BR-51); lệch dự kiến chủ yếu do Đ1 thất bại.
- Chênh lệch tạm ứng = 1.000.000 − 1.050.000 = −50.000 → công ty trả thêm An 50.000, ghi "đã trả, tiền mặt" (BR-55) → `DA_QUYET_TOAN`, chỉ đọc (BR-29).

**8. Cuối tháng.** Cty B nợ 2.240.000 (Đ2 + Đ4); khách trả thì Kế toán đánh dấu đã thu cả hai đơn một lần (BR-56, UC-25). X1 tháng 10: Σ lãi các chuyến − chi phí cố định 9.000.000 = lãi thật của xe; kèm % lấp đầy trung bình, số chuyến chạy rỗng, dầu so với định mức (UC-26, 34).

## 12. Câu hỏi còn mở
- ~~Thầy: A1–A8.~~ Nhóm tự chốt A1–A8 ngày 16/10/2026 (thầy để nhóm tự quyết). Cột "Nếu sau này thầy yêu cầu khác" ở mục 1 giữ hướng xử lý.
- Nhà xe (nếu phỏng vấn được): mỗi điểm dừng mất bao lâu (`CFG-08`); ai trả cước; hàng giao hỏng xử lý thế nào.

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
