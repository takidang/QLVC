# Sơ đồ nghiệp vụ và dữ liệu

> Phiên bản 0.4 · 10/10/2026 · Nhóm 10. Khớp `docs/nghiep-vu.md` (BR-01…62) và `docs/use-cases.md` (UC-01…31).
> Viết bằng Mermaid: GitHub và VS Code (extension Markdown Preview Mermaid) hiển thị trực tiếp. Sửa nghiệp vụ thì sửa sơ đồ trong cùng commit.
> ERD là bản logic để hiểu nghiệp vụ; kiểu dữ liệu và index chi tiết chốt ở bước thiết kế CSDL.

## 1. Bức tranh nghiệp vụ

Liên quan: BR-01…62

Một vòng đời đầy đủ: đơn đi vào, được ghép lên chuyến, chạy, giao, rồi tiền được quyết toán. Mỗi làn là một tác nhân.

- Đọc từ trên xuống. Mũi tên chéo giữa các làn là lúc việc chuyển từ người này sang người khác.
- Ô thoi là chỗ hệ thống kiểm quy tắc nghiệp vụ; nhánh sai là thao tác bị chặn.
- Đơn thất bại không chết: nó quay về hàng chờ ghép (tối đa CFG-04 lần) hoặc hoàn hàng.

```mermaid
flowchart TB
  subgraph KH["Khách hàng"]
    k1(["Gọi/nhắn yêu cầu gửi hàng"])
    k9(["Tra cứu đơn bằng mã + 4 số SĐT"])
  end
  subgraph DP["Điều phối viên"]
    d1["Tạo đơn: hàng, kg, m³, điểm lấy/giao, khung giờ"]
    d2{"Có bảng giá<br/>cặp tỉnh? BR-48"}
    d2b["Đơn lưu ở MOI<br/>chờ bổ sung bảng giá"]
    d3["Xác nhận đơn → chốt cước<br/>Đơn: CHO_GHEP"]
    d4["Lập chuyến: tuyến + giờ khởi hành"]
    d5{"Xe, tài xế hợp lệ?<br/>BR-11…19"}
    d6["Ghép đơn vào chuyến"]
    d7{"Tải, thể tích, tuyến,<br/>khung giờ? BR-01…10"}
    d8["Chốt chuyến: DA_CHOT"]
    d9["Xử lý đơn thất bại:<br/>ghép lại hoặc hoàn hàng"]
  end
  subgraph KT["Kế toán"]
    t1["Cấp tạm ứng BR-53"]
    t2["Duyệt chi phí, quyết toán<br/>Chuyến: DA_QUYET_TOAN"]
    t3["Thu tiền khách: công nợ"]
  end
  subgraph TX["Tài xế"]
    x1["Bắt đầu bốc: DANG_BOC"]
    x2["Quét QR lấy hàng<br/>giờ server + GPS"]
    x2b["Không lấy được: lý do + ảnh<br/>→ KHONG_LAY_DUOC"]
    x3["Xuất phát: DANG_CHAY"]
    x4{"Giao được?"}
    x5["Ảnh + chữ ký → DA_GIAO"]
    x6["Lý do + ảnh → GIAO_THAT_BAI"]
    x7["Ghi chi phí phát sinh + ảnh"]
    x8["Kết thúc: HOAN_THANH"]
  end
  k1 --> d1 --> d2
  d2 -- "không" --> d2b
  d2b -.-> d2
  d2 -- "có" --> d3
  d4 --> d5
  d5 -- "không" --> d4
  d5 -- "có" --> d6
  d3 --> d6 --> d7
  d7 -- "vi phạm" --> d6
  d7 -- "đạt" --> d8
  d8 --> t1
  d8 --> x1 --> x2 --> x3 --> x4
  x4 -- "có" --> x5
  x4 -- "không" --> x6
  x1 -. "không lấy được" .-> x2b
  x2b --> x8
  x3 -.-> x7
  x5 --> x8
  x6 --> x8
  x8 --> t2
  x8 --> d9
  d9 -. "ghép lại" .-> d6
  x5 --> t3
  x5 -.-> k9
```

## 2. Sơ đồ use case

Liên quan: UC-01…31

Ai làm được gì. Use case gom theo phân hệ, khớp cột Phân hệ trong bảng mục 2 của use-cases.md.

- Mermaid không có ký hiệu use case chuẩn UML; báo cáo nên vẽ lại bằng draw.io hoặc StarUML theo đúng sơ đồ này.
- UC-01 Đăng nhập dùng chung cho mọi tác nhân trừ Khách, nên không vẽ đường để đỡ rối.
- UC-29, UC-30 là module phụ, nét đứt: chỉ gợi ý, không quyết định.
- Quản lý làm được mọi việc của Điều phối (ma trận phân quyền mục 6 của nghiep-vu.md). Khi vẽ lại bằng UML, dùng quan hệ tổng quát hóa Quản lý → Điều phối thay vì nối lại từng use case.

```mermaid
flowchart LR
  QL(("Quản lý"))
  DP(("Điều phối viên"))
  TX(("Tài xế"))
  KT(("Kế toán"))
  KH(("Khách hàng"))
  HT(("Hệ thống<br/>hằng ngày"))
  subgraph CHUNG["Chung"]
    UC02(["UC-02 Người dùng, vai trò"])
  end
  subgraph XTX["Xe / Tài xế"]
    UC03(["UC-03 Quản lý xe"])
    UC04(["UC-04 Quản lý tài xế"])
    UC27(["UC-27 Bảng cảnh báo"])
  end
  subgraph DON["Đơn"]
    UC06(["UC-06 Khách hàng"])
    UC07(["UC-07 Bảng giá, cấu hình"])
    UC08(["UC-08 Tạo đơn"])
    UC09(["UC-09 Xác nhận đơn"])
    UC10(["UC-10 Sửa / hủy đơn"])
    UC22(["UC-22 Xử lý đơn thất bại"])
  end
  subgraph CHUYEN["Chuyến"]
    UC05(["UC-05 Quản lý tuyến"])
    UC11(["UC-11 Lập chuyến"])
    UC12(["UC-12 Gán xe, tài xế"])
    UC13(["UC-13 Ghép / gỡ đơn"])
    UC14(["UC-14 Sắp điểm dừng"])
    UC15(["UC-15 Chốt / mở chốt"])
    UC16(["UC-16 Hủy chuyến"])
  end
  subgraph QUET["Quét mã"]
    UC17(["UC-17 Xem chuyến của tôi"])
    UC18(["UC-18 Bắt đầu / xuất phát / kết thúc"])
    UC19(["UC-19 Quét lấy hàng"])
    UC20(["UC-20 Quét giao hàng"])
    UC21(["UC-21 Ghi chi phí phát sinh"])
  end
  subgraph TIEN["Quyết toán"]
    UC23(["UC-23 Tạm ứng"])
    UC24(["UC-24 Quyết toán chuyến"])
    UC25(["UC-25 Công nợ"])
    UC26(["UC-26 Báo cáo lãi lỗ"])
    UC31(["UC-31 Điều chỉnh cước"])
  end
  subgraph TRA["Tra cứu"]
    UC28(["UC-28 Tra cứu đơn"])
  end
  subgraph PHU["Phụ trợ"]
    UC29(["UC-29 Gợi ý ghép đơn"])
    UC30(["UC-30 Dự đoán trễ"])
  end
  QL --- UC02 & UC07 & UC26
  DP --- UC03 & UC04 & UC05 & UC06 & UC08 & UC09 & UC10 & UC11 & UC12 & UC13 & UC14 & UC15 & UC16 & UC22 & UC27
  DP -.- UC29 & UC30
  TX --- UC17 & UC18 & UC19 & UC20 & UC21
  KT --- UC23 & UC24 & UC25 & UC26 & UC31
  QL --- UC31
  QL --- UC23
  KH --- UC28
  HT --- UC27
```

## 3. Trạng thái Chuyến

Liên quan: BR-22…29

Tám trạng thái của một chuyến. Mỗi mũi tên ghi ai bấm và quy tắc phải thỏa.

- LEN_KE_HOACH tách khỏi GHEP_DON vì chưa có xe thì chưa kiểm được tải (BR-22).
- Chỉ mở chốt được khi chưa quét mã và chưa cấp tạm ứng (BR-24).
- Sau DANG_BOC không hủy được nữa: hàng đã lên xe. Chuyến chỉ kết thúc khi mọi đơn đã có kết quả (BR-28).

```mermaid
stateDiagram-v2
  direction LR
  state "Lên kế hoạch" as LEN_KE_HOACH
  state "Ghép đơn" as GHEP_DON
  state "Đã chốt" as DA_CHOT
  state "Đang bốc hàng" as DANG_BOC
  state "Đang chạy" as DANG_CHAY
  state "Hoàn thành" as HOAN_THANH
  state "Đã quyết toán" as DA_QUYET_TOAN
  state "Hủy" as HUY
  [*] --> LEN_KE_HOACH : Điều phối lập chuyến
  LEN_KE_HOACH --> GHEP_DON : gán xe + tài xế hợp lệ [BR-22]
  GHEP_DON --> DA_CHOT : chốt [BR-23]
  DA_CHOT --> GHEP_DON : mở chốt [BR-24]
  DA_CHOT --> DANG_BOC : Tài xế bắt đầu [BR-26]
  DANG_BOC --> DANG_CHAY : Tài xế xuất phát [BR-27]
  DANG_CHAY --> HOAN_THANH : mọi đơn có kết quả [BR-28]
  HOAN_THANH --> DA_QUYET_TOAN : Kế toán quyết toán [BR-55]
  LEN_KE_HOACH --> HUY : hủy [BR-25]
  GHEP_DON --> HUY : hủy [BR-25]
  DA_CHOT --> HUY : hủy, hoàn tạm ứng [BR-25]
  DA_QUYET_TOAN --> [*]
  HUY --> [*]
```

## 4. Trạng thái Đơn

Liên quan: BR-31…45

Vòng đời vận hành của một đơn. Thanh toán (công nợ) là trường riêng, không nằm trong sơ đồ này.

- Ba trạng thái kết thúc thật: DA_GIAO, HOAN_HANG, HUY.
- GIAO_THAT_BAI và KHONG_LAY_DUOC là kết thúc trong một chuyến, nhưng đơn vẫn sống: Điều phối ghép lại hoặc hoàn hàng (BR-36).
- Hủy chỉ được trước khi hàng lên xe (BR-34).

```mermaid
stateDiagram-v2
  direction LR
  state "Mới" as MOI
  state "Chờ ghép" as CHO_GHEP
  state "Đã ghép" as DA_GHEP
  state "Đã lấy hàng" as DA_LAY_HANG
  state "Không lấy được" as KHONG_LAY_DUOC
  state "Đã giao" as DA_GIAO
  state "Giao thất bại" as GIAO_THAT_BAI
  state "Hoàn hàng" as HOAN_HANG
  state "Hủy" as HUY
  [*] --> MOI : Điều phối tạo [BR-31]
  MOI --> CHO_GHEP : xác nhận, chốt cước [BR-32, BR-48]
  CHO_GHEP --> DA_GHEP : ghép vào chuyến [BR-01…10]
  DA_GHEP --> CHO_GHEP : gỡ / chuyến bị hủy
  DA_GHEP --> DA_LAY_HANG : quét lấy [BR-38, BR-39]
  DA_GHEP --> KHONG_LAY_DUOC : báo không lấy được [BR-42]
  DA_LAY_HANG --> DA_GIAO : quét giao + ảnh + chữ ký [BR-41]
  DA_LAY_HANG --> GIAO_THAT_BAI : lý do + ảnh [BR-42]
  GIAO_THAT_BAI --> CHO_GHEP : ghép lại [BR-36, BR-37]
  KHONG_LAY_DUOC --> CHO_GHEP : ghép lại [BR-36]
  GIAO_THAT_BAI --> HOAN_HANG : hoàn hàng
  MOI --> HUY : hủy [BR-34]
  CHO_GHEP --> HUY : hủy [BR-34]
  DA_GHEP --> HUY : gỡ rồi hủy [BR-34]
  DA_GIAO --> [*]
  HOAN_HANG --> [*]
  HUY --> [*]
```

## 5. ERD: vận hành lõi

Liên quan: BR-01…19

Phần trung tâm của đề tài. CHUYEN ở giữa; DON_HANG nối vào CHUYEN qua bảng GHEP chứ không trỏ thẳng.

- Vì sao có GHEP: một đơn giao thất bại có thể đi nhiều chuyến. GHEP giữ lịch sử, cờ hieu_luc cho biết lần ghép hiện tại. Unique index một phần (don_hang_id) WHERE hieu_luc = true thực thi BR-07 ngay trong CSDL.
- NUT là tỉnh hoặc kho. TUYEN_NUT cho thứ tự và phút chạy từ điểm đầu; ETA điểm dừng = giờ khởi hành + phút đó.
- XE lưu hai số khối lượng: tai_trong_kg để kiểm ghép (BR-01), ktt_toan_bo_kg để kiểm hạng bằng lái (BR-14).
- DON_HANG chép lại đơn giá lúc xác nhận (don_gia_chot) để đổi bảng giá không làm đổi cước cũ (BR-32).
- lat/lng của điểm lấy và điểm giao do Điều phối chấm trên bản đồ; BR-44 đo khoảng cách từ vị trí quét tới các tọa độ này, không tới tâm nút.
- Các cột _chot (đơn giá, cước tối thiểu, hệ số quy đổi, bước làm tròn) là bản sao lúc xác nhận cho BR-32; BR-33 tính lại cước chỉ từ các cột này.

```mermaid
erDiagram
  TUYEN ||--|{ TUYEN_NUT : "gồm"
  NUT ||--o{ TUYEN_NUT : "nằm trên"
  TUYEN ||--o{ CHUYEN : "theo"
  XE |o--o{ CHUYEN : "chạy"
  TAI_XE |o--o{ CHUYEN : "lái"
  NGUOI_DUNG ||--o| TAI_XE : "tài khoản"
  KHACH_HANG ||--o{ DON_HANG : "gửi"
  NUT ||--o{ DON_HANG : "lấy tại"
  NUT ||--o{ DON_HANG : "giao tại"
  BANG_GIA |o--o{ DON_HANG : "chốt giá từ"
  CHUYEN ||--o{ GHEP : "chứa"
  DON_HANG ||--o{ GHEP : "được ghép"
  GHEP ||--|{ DIEM_DUNG : "sinh 2 điểm"
  CHUYEN ||--o{ DIEM_DUNG : "dừng tại"
  NUT ||--o{ DIEM_DUNG : "thuộc nút"
  NGUOI_DUNG ||--o{ CAU_HINH : "sửa"

  TUYEN {
    int id PK
    string ma UK
    string ten
    int dm_dau "định mức dầu, đồng"
    int dm_cau_duong
    int dm_boc_xep
    int dm_luong_tai_xe
    string trang_thai "HOAT_DONG|NGUNG"
  }
  NUT {
    int id PK
    string ten
    string tinh "dùng tra bảng giá"
    string loai "TINH|KHO"
    decimal lat
    decimal lng
  }
  TUYEN_NUT {
    int tuyen_id PK,FK
    int thu_tu PK
    int nut_id FK
    int phut_tu_diem_dau
    bool la_diem_nghi
  }
  XE {
    int id PK
    string bien_so UK
    int tai_trong_kg "BR-01"
    decimal the_tich_m3 "BR-02"
    int ktt_toan_bo_kg "BR-14"
    date han_dang_kiem "BR-12"
    date han_bao_hiem "BR-13"
    string trang_thai "HOAT_DONG|BAO_DUONG|NGUNG"
  }
  TAI_XE {
    int id PK
    int nguoi_dung_id FK,UK
    string so_gplx UK
    string hang_gplx "B|C1|C"
    date han_gplx
    string sdt
    string trang_thai
  }
  NGUOI_DUNG {
    int id PK
    string ten_dang_nhap UK
    string mat_khau_bam
    string ho_ten
    string vai_tro "QUAN_LY|DIEU_PHOI|TAI_XE|KE_TOAN"
    string trang_thai
  }
  KHACH_HANG {
    int id PK
    string ten
    string sdt
    string dia_chi
    string ma_so_thue
    string trang_thai
  }
  BANG_GIA {
    int id PK
    string tinh_lay
    string tinh_giao
    int don_gia_kg
    int cuoc_toi_thieu
    date hieu_luc_tu
  }
  DON_HANG {
    int id PK
    string ma_don UK "in QR"
    int khach_hang_id FK
    string mo_ta
    decimal kg
    decimal m3
    int so_kien
    int nut_lay_id FK
    string dia_chi_lay
    decimal lat_lay "BR-44"
    decimal lng_lay
    string nguoi_lien_he_lay
    string sdt_lay
    datetime lay_tu
    datetime lay_den
    int nut_giao_id FK
    string dia_chi_giao
    decimal lat_giao "BR-44"
    decimal lng_giao
    string nguoi_nhan
    string sdt_nhan
    datetime han_giao
    int bang_gia_id FK
    int don_gia_chot
    int cuoc_toi_thieu_chot
    int he_so_quy_doi_chot
    int lam_tron_chot
    decimal kl_tinh_cuoc
    int cuoc_tinh "hệ thống tính"
    string trang_thai "ST-O"
    int so_lan_that_bai
  }
  CHUYEN {
    int id PK
    string ma_chuyen UK
    int tuyen_id FK
    int xe_id FK "null khi LEN_KE_HOACH"
    int tai_xe_id FK
    datetime khoi_hanh_du_kien
    datetime ket_thuc_du_kien
    datetime khoi_hanh_thuc_te
    datetime ket_thuc_thuc_te
    int dieu_phoi_id FK
    string trang_thai "ST-T"
  }
  CAU_HINH {
    string ma PK "CFG-xx"
    string gia_tri
    int nguoi_sua FK
    datetime luc
  }
  GHEP {
    int id PK
    int chuyen_id FK
    int don_hang_id FK
    bool hieu_luc "unique khi true, BR-07"
    string ket_qua "DA_GIAO|GIAO_THAT_BAI|KHONG_LAY_DUOC"
    datetime tao_luc
  }
  DIEM_DUNG {
    int id PK
    int chuyen_id FK
    int ghep_id FK
    int nut_id FK
    string loai "LAY|GIAO"
    int thu_tu "BR-10"
  }
```

## 6. ERD: quét mã và bằng chứng

Liên quan: BR-38…45

Mỗi lần tài xế quét tạo một LUOT_QUET gắn vào lần ghép hiện tại. Ảnh và chữ ký lưu thành TEP.

- thoi_gian lấy từ server, không nhận từ điện thoại.
- Hai cờ thieu_gps, sai_vi_tri là cảnh báo cho Điều phối, không chặn thao tác (BR-43, BR-44).
- TEP dùng chung cho ảnh quét và ảnh chứng từ chi phí: đúng một trong hai khóa ngoại có giá trị. Tên file do server sinh.

```mermaid
erDiagram
  GHEP ||--o{ LUOT_QUET : "được quét"
  DIEM_DUNG ||--o{ LUOT_QUET : "tại điểm"
  TAI_XE ||--o{ LUOT_QUET : "thực hiện"
  LUOT_QUET ||--o{ TEP : "ảnh, chữ ký"
  CHI_PHI ||--o{ TEP : "chứng từ"
  LUOT_QUET {
    int id PK
    int ghep_id FK
    int diem_dung_id FK
    int tai_xe_id FK
    string loai "LAY|KHONG_LAY|GIAO|GIAO_THAT_BAI"
    datetime thoi_gian "giờ server"
    decimal lat
    decimal lng
    decimal do_chinh_xac_m
    bool thieu_gps
    bool sai_vi_tri
    string ly_do
    string ten_nguoi_nhan
  }
  TEP {
    int id PK
    int luot_quet_id FK "hoặc"
    int chi_phi_id FK "hoặc"
    string loai "ANH|CHU_KY"
    string duong_dan "server sinh"
    int kich_thuoc
    datetime tao_luc
  }
  CHI_PHI {
    int id PK
  }
```

## 7. ERD: tiền

Liên quan: BR-46…62

Mọi khoản tiền đều gắn vào CHUYEN hoặc DON_HANG. Tiền lưu số nguyên đồng.

- Cước cuối = DON_HANG.cuoc_tinh + tổng DIEU_CHINH_CUOC. Không ghi đè cước gốc (BR-61).
- PHAI_THU sinh khi đơn DA_GIAO; PHIEU_THU là từng lần khách trả (BR-56).
- QUYET_TOAN một-một với CHUYEN; tạo ra là khóa sổ (BR-29).
- Hủy chuyến đã cấp tạm ứng: các khoản HIEU_LUC chuyển PHAI_HOAN; Kế toán xác nhận tài xế đã nộp thì chuyển DA_HOAN, có ghi NHAT_KY_TIEN (BR-25).
- NHAT_KY_TIEN và LICH_SU_TRANG_THAI chỉ thêm, không sửa xóa (BR-62, BR-30).

```mermaid
erDiagram
  CHUYEN ||--o{ CHI_PHI : "phát sinh"
  CHUYEN ||--o{ TAM_UNG : "cấp cho"
  TAI_XE ||--o{ TAM_UNG : "nhận"
  CHUYEN ||--o| QUYET_TOAN : "khóa sổ"
  DON_HANG ||--o{ DIEU_CHINH_CUOC : "điều chỉnh"
  DON_HANG ||--o| PHAI_THU : "sinh khi giao"
  PHAI_THU ||--o{ PHIEU_THU : "thu"
  NGUOI_DUNG ||--o{ NHAT_KY_TIEN : "ghi"
  NGUOI_DUNG ||--o{ LICH_SU_TRANG_THAI : "chuyển"
  CHI_PHI {
    int id PK
    int chuyen_id FK
    string loai "DAU|CAU_DUONG|BOC_XEP|PHAT_SINH"
    int so_tien_khai
    int so_tien_duyet
    string ghi_chu
    string trang_thai "CHO_DUYET|DA_DUYET|TU_CHOI"
    int nguoi_tao FK
    int nguoi_duyet FK
  }
  TAM_UNG {
    int id PK
    int chuyen_id FK
    int tai_xe_id FK
    int so_tien
    string hinh_thuc "TIEN_MAT|CHUYEN_KHOAN"
    string trang_thai "HIEU_LUC|CHO_QUAN_LY_DUYET|TU_CHOI|PHAI_HOAN|DA_HOAN"
    int nguoi_tao FK
    int nguoi_duyet FK
  }
  QUYET_TOAN {
    int id PK
    int chuyen_id FK,UK
    int doanh_thu "BR-50"
    int tong_chi
    int luong_tai_xe
    int lai "BR-51"
    int chenh_lech_tam_ung "BR-55"
    int ke_toan_id FK
    datetime luc
  }
  DIEU_CHINH_CUOC {
    int id PK
    int don_hang_id FK
    int so_tien "âm: giảm, dương: phụ phí"
    string ly_do
    int nguoi_tao FK
    datetime tao_luc
  }
  PHAI_THU {
    int id PK
    int don_hang_id FK,UK
    int so_tien
    int da_thu
    string trang_thai_tt "CHUA_THU|THU_MOT_PHAN|DA_THU"
  }
  PHIEU_THU {
    int id PK
    int phai_thu_id FK
    int so_tien
    date ngay
    int nguoi_tao FK
  }
  NHAT_KY_TIEN {
    int id PK
    string bang
    int ban_ghi_id
    string hanh_dong "TAO|SUA|DUYET|TU_CHOI"
    string gia_tri_cu
    string gia_tri_moi
    string ly_do
    int nguoi FK
    datetime luc
  }
  LICH_SU_TRANG_THAI {
    int id PK
    string doi_tuong "CHUYEN|DON"
    int doi_tuong_id
    string tu
    string sang
    string ly_do
    int nguoi FK
    datetime luc
  }
```

## 8. Sequence: ghép đơn vào chuyến (UC-13)

Liên quan: BR-01…10

Luồng quan trọng nhất của đề tài. Kiểm cả lô trong một giao dịch: một đơn sai thì không ghép đơn nào.

- Khóa dòng chuyến và các dòng đơn (SELECT … FOR UPDATE) để hai người ghép cùng lúc không làm vượt tải hay ghép trùng một đơn.
- Lỗi trả về danh sách mã BR bị vi phạm để giao diện hiện cho Điều phối (NFR-USA-02).

```mermaid
sequenceDiagram
  autonumber
  actor DP as Điều phối
  participant UI as Web điều phối
  participant API as API /chuyen/{id}/ghep
  participant SV as Dịch vụ Chuyến
  participant DB as PostgreSQL
  DP->>UI: chọn các đơn, bấm Ghép
  UI->>API: POST don_ids[]
  API->>API: kiểm vai trò DIEU_PHOI/QUAN_LY [BR-57]
  API->>SV: ghep(chuyen_id, don_ids)
  SV->>DB: BEGIN, khóa dòng chuyến và các dòng đơn (FOR UPDATE)
  SV->>DB: đọc chuyến, xe, tuyến, đơn
  SV->>SV: BR-09 trạng thái, BR-03/04 tuyến, BR-05/06 khung giờ
  SV->>SV: BR-01/02 tổng kg, m³ với xe
  alt có vi phạm
    SV->>DB: ROLLBACK
    SV-->>API: danh sách {don, BR, chênh}
    API-->>UI: 422 + mã BR
    UI-->>DP: bảng lỗi, không ghép đơn nào
  else đạt hết
    SV->>DB: INSERT GHEP hieu_luc=true
    Note over DB: unique (don_hang_id) khi hieu_luc chặn trùng [BR-07]
    alt vi phạm unique: đơn vừa bị ghép vào chuyến khác [BR-07]
      SV->>DB: ROLLBACK
      API-->>UI: 409, tải lại danh sách đơn
    else
      SV->>DB: INSERT 2 DIEM_DUNG mỗi đơn [BR-10]
      SV->>DB: UPDATE đơn → DA_GHEP, ghi LICH_SU_TRANG_THAI
      SV->>DB: COMMIT
      API-->>UI: 200 + tải, thể tích, lãi dự kiến
    end
  end
```

## 9. Sequence: tài xế quét giao (UC-20)

Liên quan: BR-38…45

Điện thoại chỉ gửi mã đơn, tọa độ và ảnh. Giờ quét, quyền và trạng thái đều do server quyết.

- Đơn không thuộc chuyến của tài xế đang đăng nhập → 403, chống IDOR.
- Giao thành công sinh khoản phải thu ngay trong cùng giao dịch.

```mermaid
sequenceDiagram
  autonumber
  actor TX as Tài xế
  participant APP as Web tài xế (điện thoại)
  participant API as API /quet
  participant SV as Dịch vụ Quét
  participant DB as PostgreSQL
  TX->>APP: quét QR tại điểm GIAO
  APP->>APP: lấy GPS (có thể bị từ chối)
  TX->>APP: chụp ảnh, nhập tên, người nhận ký
  APP->>API: POST ma_don, loai=GIAO, lat/lng?, ảnh, chữ ký
  API->>SV: quet(tai_xe hiện tại, ...)
  SV->>DB: tìm GHEP hiệu lực của đơn
  alt không thuộc chuyến của tài xế hoặc chuyến sai trạng thái
    SV-->>API: 403 [BR-38]
  else đơn đã có kết quả (DA_GIAO hoặc GIAO_THAT_BAI)
    SV-->>API: 200 kèm trạng thái hiện tại [BR-45]
  else đơn đang DA_GHEP
    SV-->>API: 409 "đơn chưa được quét lấy" [BR-40]
  else hợp lệ
    SV->>SV: kiểm loại và kích thước file ảnh, chữ ký (security-rules)
    SV->>SV: kiểm ảnh + chữ ký + tên [BR-41]
    SV->>SV: giờ server, thiếu GPS hoặc cách tọa độ điểm giao của đơn > CFG-03 thì gắn cờ [BR-43/44]
    SV->>DB: lưu TEP (tên file server sinh), LUOT_QUET
    SV->>DB: đơn → DA_GIAO, GHEP.ket_qua, LICH_SU_TRANG_THAI
    SV->>DB: tạo PHAI_THU = cước cuối [BR-56], NHAT_KY_TIEN
    API-->>APP: 200 Đã giao
  end
```

## 10. Sequence: quyết toán chuyến (UC-24)

Liên quan: BR-50…55, 62

Kế toán chốt sổ một chuyến đã hoàn thành.

- Doanh thu chỉ tính đơn giao thành công trên chuyến này (BR-50).
- Chênh lệch dương: tài xế nộp lại; âm: công ty trả thêm.

```mermaid
sequenceDiagram
  autonumber
  actor KT as Kế toán
  participant UI as Web kế toán
  participant API as API /chuyen/{id}/quyet-toan
  participant SV as Dịch vụ Quyết toán
  participant DB as PostgreSQL
  KT->>UI: mở chuyến HOAN_THANH
  UI->>API: GET bảng quyết toán
  API->>SV: lay_bang_quyet_toan(chuyen_id)
  SV->>DB: đơn DA_GIAO, chi phí, tạm ứng, định mức lương
  SV-->>API: doanh thu, các khoản chi chờ duyệt, tạm ứng
  API-->>UI: bảng quyết toán
  loop từng khoản chi
    KT->>UI: duyệt / điều chỉnh (lý do) / từ chối
    UI->>API: PATCH chi_phi
    API->>SV: duyet_chi_phi(...)
    SV->>DB: cập nhật + NHAT_KY_TIEN [BR-62]
  end
  KT->>UI: bấm Quyết toán
  UI->>API: POST
  API->>SV: quyet_toan(chuyen_id, ke_toan)
  SV->>DB: BEGIN, khóa dòng chuyến (FOR UPDATE)
  alt chuyến không ở HOAN_THANH
    SV->>DB: ROLLBACK
    SV-->>API: 409
  else còn chi phí CHO_DUYET hoặc tạm ứng CHO_QUAN_LY_DUYET
    SV->>DB: ROLLBACK
    SV-->>API: 409 [BR-55]
  else đủ điều kiện
    SV->>DB: tạo QUYET_TOAN: lãi [BR-51], chênh lệch tạm ứng [BR-55]
    SV->>DB: chuyến → DA_QUYET_TOAN, khóa sửa [BR-29], COMMIT
    SV-->>API: lãi chuyến, số tài xế nộp / được nhận
  end
  API-->>UI: kết quả
```
