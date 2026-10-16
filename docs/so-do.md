# Sơ đồ nghiệp vụ và dữ liệu

> Phiên bản 0.5 · 15/10/2026 · Nhóm 10 (Kiệt đề xuất, chờ Tài review). Khớp `docs/nghiep-vu.md` (BR-01…73) và `docs/use-cases.md` (UC-01…34).
> Viết bằng Mermaid: GitHub và VS Code (extension Markdown Preview Mermaid) hiển thị trực tiếp. Sửa nghiệp vụ thì sửa sơ đồ trong cùng commit.
> ERD là bản logic để hiểu nghiệp vụ; kiểu dữ liệu và index chi tiết chốt ở bước thiết kế CSDL.

## 1. Bức tranh nghiệp vụ

Liên quan: BR-01…73

Một vòng đời đầy đủ: đơn đi vào, được ghép lên chuyến, chạy, giao, rồi tiền được quyết toán. Mỗi làn là một tác nhân.

- Đọc từ trên xuống. Mũi tên chéo giữa các làn là lúc việc chuyển từ người này sang người khác.
- Ô thoi là chỗ hệ thống kiểm quy tắc nghiệp vụ; nhánh sai là thao tác bị chặn.
- Đơn thất bại không chết: nó quay về hàng chờ ghép (BR-69), hoặc trả hàng/hủy (BR-36).

```mermaid
flowchart TB
  subgraph KH["Khách hàng"]
    k1(["Gọi/nhắn yêu cầu gửi hàng"])
    k9(["Tra cứu đơn bằng mã + 4 số SĐT"])
  end
  subgraph DP["Điều phối viên"]
    d1["Tạo đơn: hàng, kg, m³, điểm lấy/giao, hạn giao"]
    d2{"Có bảng giá<br/>cặp tỉnh? BR-48"}
    d2b["Không tạo được đơn"]
    d3["Chốt cước ngay<br/>Đơn: CHO_GHEP"]
    d4["Lập chuyến: tuyến, giờ, xe, tài xế"]
    d5{"Xe, tài xế hợp lệ?<br/>BR-11…19"}
    d6["Ghép đơn vào chuyến"]
    d7{"Cả chuyến còn hợp lệ?<br/>tải, tuyến, ETA, lịch BR-67"}
    d8["Chốt chuyến: DA_CHOT<br/>chốt định mức, lương"]
    d10["Theo dõi chuyến: trễ, sự cố"]
    d9["Xử lý đơn thất bại:<br/>ghép lại, trả hàng, hủy"]
  end
  subgraph KT["Kế toán"]
    t1["Cấp tạm ứng BR-53"]
    t2["Duyệt chi phí, quyết toán<br/>Chuyến: DA_QUYET_TOAN"]
    t3["Công nợ: đánh dấu đã thu"]
  end
  subgraph TX["Tài xế"]
    x1["Bắt đầu + km: DANG_CHAY"]
    x2{"Lấy được?"}
    x2a["Quét QR lấy: DA_LAY<br/>giờ server + GPS"]
    x4{"Giao được?"}
    x5["Ảnh + chữ ký → DA_GIAO"]
    x6["Lý do + ảnh → THAT_BAI"]
    x7["Ghi chi phí, báo sự cố"]
    x8["Kết thúc + km: HOAN_THANH"]
  end
  k1 --> d1 --> d2
  d2 -- "không" --> d2b
  d2 -- "có" --> d3
  d4 --> d5
  d5 -- "không" --> d4
  d5 -- "có" --> d6
  d3 --> d6 --> d7
  d7 -- "vi phạm" --> d6
  d7 -- "đạt" --> d8
  d8 --> t1
  d8 --> x1 --> x2
  x2 -- "có" --> x2a --> x4
  x2 -- "không" --> x6
  x4 -- "có" --> x5
  x4 -- "không" --> x6
  x1 -.-> x7
  x7 -.-> d10
  x5 --> x8
  x6 --> x8
  d10 -. "kết thúc do sự cố" .-> x8
  x8 --> t2
  x8 --> d9
  d9 -. "ghép lại" .-> d6
  x5 --> t3
  x5 -.-> k9
```

## 2. Sơ đồ use case

Liên quan: UC-01…34

Ai làm được gì. Use case gom theo phân hệ, khớp cột Phân hệ trong bảng mục 2 của use-cases.md. UC-09, 14, 29, 31 đã bỏ ở 0.5 nên không vẽ.

- Mermaid không có ký hiệu use case chuẩn UML; báo cáo nên vẽ lại bằng draw.io hoặc StarUML theo đúng sơ đồ này.
- UC-01 Đăng nhập dùng chung cho mọi tác nhân trừ Khách, nên không vẽ đường để đỡ rối.
- UC-30 là module phụ, nét đứt: chỉ gợi ý, không quyết định.
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
    UC08(["UC-08 Tạo đơn, chốt cước"])
    UC10(["UC-10 Sửa / hủy đơn"])
    UC22(["UC-22 Xử lý đơn thất bại"])
  end
  subgraph CHUYEN["Chuyến"]
    UC05(["UC-05 Quản lý tuyến"])
    UC11(["UC-11 Lập chuyến"])
    UC12(["UC-12 Đổi xe, tài xế"])
    UC13(["UC-13 Ghép / gỡ đơn"])
    UC15(["UC-15 Chốt / mở chốt"])
    UC16(["UC-16 Hủy chuyến"])
    UC32(["UC-32 Theo dõi chuyến"])
  end
  subgraph QUET["Quét mã"]
    UC17(["UC-17 Xem chuyến của tôi"])
    UC18(["UC-18 Bắt đầu / kết thúc"])
    UC19(["UC-19 Quét lấy hàng"])
    UC20(["UC-20 Quét giao hàng"])
    UC33(["UC-33 Báo sự cố"])
  end
  subgraph TIEN["Quyết toán"]
    UC21(["UC-21 Ghi chi phí"])
    UC23(["UC-23 Tạm ứng"])
    UC24(["UC-24 Quyết toán chuyến"])
    UC25(["UC-25 Công nợ"])
    UC26(["UC-26 Báo cáo lãi lỗ"])
    UC34(["UC-34 Hiệu suất xe"])
  end
  subgraph TRA["Tra cứu"]
    UC28(["UC-28 Tra cứu đơn"])
  end
  subgraph PHU["Phụ trợ"]
    UC30(["UC-30 Dự đoán trễ"])
  end
  QL --- UC02 & UC07 & UC26 & UC34
  DP --- UC03 & UC04 & UC05 & UC06 & UC08 & UC10 & UC11 & UC12 & UC13 & UC15 & UC16 & UC22 & UC27 & UC32
  DP -.- UC30
  TX --- UC17 & UC18 & UC19 & UC20 & UC21 & UC33
  KT --- UC23 & UC24 & UC25 & UC26 & UC03
  KH --- UC28
  HT --- UC27
```

## 3. Trạng thái Chuyến

Liên quan: BR-22…29, 68, 70

Sáu trạng thái của một chuyến. Mỗi mũi tên ghi ai bấm và quy tắc phải thỏa.

- Lập chuyến bắt buộc có xe và tài xế ngay (BR-22), nên không còn bước "lên kế hoạch" riêng.
- Chỉ mở chốt được khi không còn tạm ứng hiệu lực (BR-24): Kế toán thu hồi trước.
- Sau DANG_CHAY không hủy được nữa: hàng đã lên xe. Chuyến kết thúc khi mọi đơn có kết quả (BR-28), hoặc Điều phối kết thúc do sự cố (BR-68).

```mermaid
stateDiagram-v2
  direction LR
  state "Đang lập" as LAP
  state "Đã chốt" as DA_CHOT
  state "Đang chạy" as DANG_CHAY
  state "Hoàn thành" as HOAN_THANH
  state "Đã quyết toán" as DA_QUYET_TOAN
  state "Hủy" as HUY
  [*] --> LAP : Điều phối lập, có xe + tài xế hợp lệ [BR-22]
  LAP --> DA_CHOT : chốt, chốt định mức + lương [BR-23, BR-71]
  DA_CHOT --> LAP : mở chốt, không còn tạm ứng [BR-24]
  DA_CHOT --> DANG_CHAY : Tài xế bắt đầu + km [BR-26, BR-70]
  DANG_CHAY --> HOAN_THANH : mọi đơn có kết quả + km [BR-28, BR-70]
  DANG_CHAY --> HOAN_THANH : Điều phối kết thúc do sự cố [BR-68]
  HOAN_THANH --> DA_QUYET_TOAN : Kế toán quyết toán [BR-55]
  LAP --> HUY : hủy [BR-25]
  DA_CHOT --> HUY : hủy, tạm ứng đã thu hồi [BR-25]
  DA_QUYET_TOAN --> [*]
  HUY --> [*]
```

## 4. Trạng thái Đơn

Liên quan: BR-31…45, 69, 72

Vòng đời vận hành của một đơn. Thanh toán (công nợ) là trường riêng, không nằm trong sơ đồ này.

- Ba trạng thái kết thúc thật: DA_GIAO, TRA_HANG, HUY.
- THAT_BAI là kết thúc trong một chuyến, nhưng đơn vẫn sống. Đã có lượt quét lấy (hàng trong tay công ty) → ghép lại hoặc trả hàng; chưa lấy → ghép lại hoặc hủy (BR-36).
- Hủy chỉ được khi hàng chưa lên xe (BR-34).

```mermaid
stateDiagram-v2
  direction LR
  state "Chờ ghép" as CHO_GHEP
  state "Đã ghép" as DA_GHEP
  state "Đã lấy" as DA_LAY
  state "Đã giao" as DA_GIAO
  state "Thất bại" as THAT_BAI
  state "Trả hàng" as TRA_HANG
  state "Hủy" as HUY
  [*] --> CHO_GHEP : Điều phối tạo, chốt cước [BR-31, BR-32, BR-48]
  CHO_GHEP --> DA_GHEP : ghép vào chuyến [BR-01…10, BR-67]
  DA_GHEP --> CHO_GHEP : gỡ / chuyến bị hủy
  DA_GHEP --> DA_LAY : quét lấy [BR-38, BR-39]
  DA_GHEP --> THAT_BAI : không lấy được / sự cố xe [BR-42, BR-68]
  DA_LAY --> DA_GIAO : quét giao + ảnh + chữ ký [BR-41, BR-72]
  DA_LAY --> THAT_BAI : giao không được / sự cố xe [BR-42, BR-68]
  THAT_BAI --> CHO_GHEP : ghép lại [BR-36, BR-37, BR-69]
  THAT_BAI --> TRA_HANG : trả hàng, đã lấy [BR-36]
  THAT_BAI --> HUY : hủy, chưa lấy [BR-34]
  CHO_GHEP --> HUY : hủy [BR-34]
  DA_GHEP --> HUY : gỡ rồi hủy [BR-34]
  DA_GIAO --> [*]
  TRA_HANG --> [*]
  HUY --> [*]
```

## 5. ERD: vận hành lõi

Liên quan: BR-01…19, 63…71

Phần trung tâm của đề tài. CHUYEN ở giữa; DON_HANG nối vào CHUYEN qua bảng GHEP chứ không trỏ thẳng.

- Vì sao có GHEP: một đơn thất bại có thể đi nhiều chuyến. GHEP giữ lịch sử, cờ hieu_luc cho biết lần ghép hiện tại. Unique index một phần (don_hang_id) WHERE hieu_luc = true thực thi BR-07 ngay trong CSDL.
- Không có bảng điểm dừng: lịch trình và ETA tính từ TUYEN_NUT và danh sách GHEP hiệu lực theo BR-63, 64.
- XE lưu hai số khối lượng: tai_trong_kg để kiểm ghép (BR-01), ktt_toan_bo_kg để kiểm hạng bằng lái (BR-14).
- Các cột _chot của DON_HANG (đơn giá, cước tối thiểu, hệ số quy đổi, bước làm tròn) là bản sao lúc tạo đơn cho BR-32; BR-33 tính lại cước chỉ từ các cột này.
- Các cột _chot của CHUYEN là định mức và lương chép từ TUYEN lúc chốt (BR-71).
- GHEP.eta_lay_ke_hoach, eta_giao_ke_hoach: ETA kế hoạch lưu lúc chốt (BR-71); độ trễ = giờ quét − ETA kế hoạch (BR-73), cũng là dữ liệu cho AI (UC-30).
- nut_giu_id, dia_chi_giu: nơi giữ hàng khi ghép lại đơn đã lấy (BR-69); khi có, thay điểm lấy trong BR-03, 04, 63.
- lat/lng điểm lấy, điểm giao vẫn giữ (Điều phối chấm trên bản đồ) dù BR-44 đã bỏ, để làm lại cảnh báo vị trí sau này.

```mermaid
erDiagram
  TUYEN ||--|{ TUYEN_NUT : "gồm"
  NUT ||--o{ TUYEN_NUT : "nằm trên"
  TUYEN ||--o{ CHUYEN : "theo"
  XE ||--o{ CHUYEN : "chạy"
  TAI_XE ||--o{ CHUYEN : "lái"
  NGUOI_DUNG ||--o| TAI_XE : "tài khoản"
  KHACH_HANG ||--o{ DON_HANG : "gửi"
  NUT ||--o{ DON_HANG : "lấy tại"
  NUT ||--o{ DON_HANG : "giao tại"
  NUT |o--o{ DON_HANG : "giữ hàng tại"
  CHUYEN ||--o{ GHEP : "chứa"
  DON_HANG ||--o{ GHEP : "được ghép"
  NGUOI_DUNG ||--o{ CAU_HINH : "sửa"

  TUYEN {
    int id PK
    string ma UK
    string ten
    int dm_dau "định mức dầu, đồng"
    int dm_cau_duong
    int dm_boc_xep
    int dm_luong_tai_xe "lương khoán mỗi chuyến"
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
    int phut_tu_diem_dau "BR-63, 66"
    int km_tu_diem_dau
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
    decimal dinh_muc_lit_100km
    int km_dong_ho "BR-70"
    string trang_thai "HOAT_DONG|NGUNG"
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
    string trang_thai "HOAT_DONG|NGUNG"
    int so_lan_sai "NFR-SEC-05"
    datetime khoa_den "khóa tạm tới lúc này"
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
    decimal lat_lay
    decimal lng_lay
    string nguoi_lien_he_lay
    string sdt_lay
    datetime lay_tu "null = cả ngày"
    datetime lay_den
    int nut_giao_id FK
    string dia_chi_giao
    decimal lat_giao
    decimal lng_giao
    string nguoi_nhan
    string sdt_nhan
    datetime han_giao
    int nut_giu_id FK "BR-69"
    string dia_chi_giu
    decimal lat_giu
    decimal lng_giu
    int don_gia_chot "BR-32"
    int cuoc_toi_thieu_chot
    int he_so_quy_doi_chot
    int lam_tron_chot
    decimal kl_tinh_cuoc
    int cuoc_tinh "hệ thống tính"
    string trang_thai "ST-O"
    int so_lan_giao_that_bai "BR-37, chỉ lý do phía khách"
  }
  CHUYEN {
    int id PK
    string ma_chuyen UK
    int tuyen_id FK
    int xe_id FK "BR-22"
    int tai_xe_id FK
    datetime khoi_hanh_du_kien
    datetime ket_thuc_du_kien "BR-64"
    datetime khoi_hanh_thuc_te
    datetime ket_thuc_thuc_te
    int km_bat_dau "BR-70"
    int km_ket_thuc
    int dm_dau_chot "BR-71"
    int dm_cau_duong_chot
    int dm_boc_xep_chot
    int luong_tai_xe_chot
    bool chay_rong "BR-23"
    bool ket_thuc_bat_thuong "BR-68"
    string ly_do_ket_thuc
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
    string ket_qua "DA_GIAO|THAT_BAI"
    bool giao_tre "BR-72"
    datetime eta_lay_ke_hoach "BR-71, lưu lúc chốt"
    datetime eta_giao_ke_hoach "BR-71"
    datetime tao_luc
  }
```

## 6. ERD: quét mã, bằng chứng, sự cố

Liên quan: BR-38…45, 68, 70

Mỗi lần tài xế quét tạo một LUOT_QUET gắn vào lần ghép hiện tại. Ảnh, chữ ký, ảnh đồng hồ km lưu thành TEP.

- thoi_gian lấy từ server, không nhận từ điện thoại.
- Cờ thieu_gps là cảnh báo cho Điều phối, không chặn thao tác (BR-43).
- loai của LUOT_QUET vẫn phân biệt KHONG_LAY và GIAO_THAT_BAI (để biết đã lấy hàng chưa), dù trạng thái đơn đều về THAT_BAI.
- LY_DO.phia cho BR-37 biết lần thất bại có tính vào CFG-04 không.
- TEP dùng chung: đúng một trong bốn khóa ngoại có giá trị. Tên file do server sinh.

```mermaid
erDiagram
  GHEP ||--o{ LUOT_QUET : "được quét"
  TAI_XE ||--o{ LUOT_QUET : "thực hiện"
  LY_DO |o--o{ LUOT_QUET : "lý do thất bại"
  CHUYEN ||--o{ SU_CO : "phát sinh"
  LUOT_QUET ||--o{ TEP : "ảnh, chữ ký"
  CHI_PHI ||--o{ TEP : "chứng từ"
  SU_CO ||--o{ TEP : "ảnh"
  CHUYEN ||--o{ TEP : "ảnh đồng hồ km"
  LUOT_QUET {
    int id PK
    int ghep_id FK
    int tai_xe_id FK
    string loai "LAY|KHONG_LAY|GIAO|GIAO_THAT_BAI"
    datetime thoi_gian "giờ server"
    decimal lat
    decimal lng
    decimal do_chinh_xac_m
    bool thieu_gps
    int ly_do_id FK
    string ten_nguoi_nhan
  }
  LY_DO {
    int id PK
    string ten
    string ap_dung "LAY|GIAO"
    string phia "KHACH|SU_CO_XE"
  }
  SU_CO {
    int id PK
    int chuyen_id FK
    int tai_xe_id FK
    string loai
    string ghi_chu
    string trang_thai "MO|DONG"
    string cach_xu_ly
    datetime luc
  }
  TEP {
    int id PK
    int luot_quet_id FK "hoặc"
    int chi_phi_id FK "hoặc"
    int su_co_id FK "hoặc"
    int chuyen_id FK "hoặc, ảnh km"
    string loai "ANH|CHU_KY|ANH_KM_BAT_DAU|ANH_KM_KET_THUC"
    string duong_dan "server sinh"
    int kich_thuoc
    datetime tao_luc
  }
  CHI_PHI {
    int id PK
  }
```

## 7. ERD: tiền

Liên quan: BR-46…62, 68, 71

Mọi khoản tiền đều gắn vào CHUYEN, DON_HANG hoặc XE. Tiền lưu số nguyên đồng.

- Cước của đơn là DON_HANG.cuoc_tinh, không có điều chỉnh tay (BR-61 bỏ).
- PHAI_THU sinh khi đơn DA_GIAO; Kế toán đánh dấu đã thu cho một hoặc nhiều khoản (BR-56). PHIEU_THU rút gọn: một lần đánh dấu đã thu.
- QUYET_TOAN một-một với CHUYEN; tạo ra là khóa sổ (BR-29). Lưu cách xử lý chênh lệch tạm ứng (BR-55).
- Mở chốt hoặc hủy chuyến đã cấp tạm ứng: Kế toán ghi các khoản HIEU_LUC sang DA_THU_HOI trước, có ghi NHAT_KY_TIEN (BR-24, 25).
- CHI_PHI_CO_DINH_XE dùng cho lãi theo xe theo tháng (UC-26, 34), không vào lãi chuyến.
- NHAT_KY_TIEN và LICH_SU_TRANG_THAI chỉ thêm, không sửa xóa (BR-62, BR-30).

```mermaid
erDiagram
  CHUYEN ||--o{ CHI_PHI : "phát sinh"
  CHUYEN ||--o{ TAM_UNG : "cấp cho"
  TAI_XE ||--o{ TAM_UNG : "nhận"
  CHUYEN ||--o| QUYET_TOAN : "khóa sổ"
  DON_HANG ||--o| PHAI_THU : "sinh khi giao"
  PHIEU_THU ||--|{ PHAI_THU : "đánh dấu đã thu"
  XE ||--o{ CHI_PHI_CO_DINH_XE : "theo tháng"
  NGUOI_DUNG ||--o{ NHAT_KY_TIEN : "ghi"
  NGUOI_DUNG ||--o{ LICH_SU_TRANG_THAI : "chuyển"
  CHI_PHI {
    int id PK
    int chuyen_id FK
    string loai "DAU|CAU_DUONG|BOC_XEP|PHAT_SINH"
    int so_tien_khai
    int so_tien_duyet
    decimal so_lit "chỉ loại DAU"
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
    string trang_thai "HIEU_LUC|DA_THU_HOI"
    int nguoi_tao FK
  }
  QUYET_TOAN {
    int id PK
    int chuyen_id FK,UK
    int doanh_thu "BR-50"
    int tong_chi
    int luong_tai_xe "chốt hoặc nhập tay"
    string ly_do_luong_tay "BR-68"
    int lai "BR-51"
    int chenh_lech_tam_ung "BR-55"
    string xu_ly_chenh_lech "TAI_XE_DA_NOP|CONG_TY_DA_TRA|KHONG_CHENH"
    string hinh_thuc "TIEN_MAT|CHUYEN_KHOAN"
    datetime luc_xu_ly
    int ke_toan_id FK
    datetime luc
  }
  PHAI_THU {
    int id PK
    int don_hang_id FK,UK
    int so_tien
    string trang_thai_tt "CHUA_THU|DA_THU"
    int phieu_thu_id FK
  }
  PHIEU_THU {
    int id PK
    int khach_hang_id FK
    int tong_tien
    date ngay
    int nguoi_tao FK
  }
  CHI_PHI_CO_DINH_XE {
    int id PK
    int xe_id FK
    string thang "YYYY-MM"
    int so_tien
  }
  NHAT_KY_TIEN {
    int id PK
    string bang
    int ban_ghi_id
    string hanh_dong "TAO|SUA|DUYET|TU_CHOI|THU_HOI"
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

Liên quan: BR-01…09, 63, 64, 67

Luồng quan trọng nhất của đề tài. Kiểm cả lô và cả chuyến trong một giao dịch: một đơn sai thì không ghép đơn nào.

- Khóa dòng chuyến và các dòng đơn (SELECT … FOR UPDATE) để hai người ghép cùng lúc không làm vượt tải hay ghép trùng một đơn.
- Thêm đơn làm thêm điểm dừng, nên ETA các đơn đã ghép dịch đi và chuyến dài ra: phải kiểm lại cả chuyến (BR-67), không chỉ đơn mới.
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
  SV->>DB: đọc chuyến, xe, tài xế, tuyến, đơn đã ghép, đơn mới
  SV->>SV: BR-09 trạng thái, BR-03/04 tuyến cho đơn mới
  SV->>SV: tính lại lịch trình, ETA, kết thúc dự kiến [BR-63, BR-64]
  SV->>SV: kiểm cả chuyến: BR-01/02 tải, BR-05/06 ETA mọi đơn, BR-12/13/15 giấy tờ [BR-67]
  SV->>DB: đọc chuyến khác của xe và tài xế
  SV->>SV: BR-16/17 khoảng chiếm mới [BR-67]
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
      SV->>DB: UPDATE đơn → DA_GHEP, chuyến.ket_thuc_du_kien, ghi LICH_SU_TRANG_THAI
      SV->>DB: COMMIT
      API-->>UI: 200 + tải, thể tích, % đầy, lịch trình, lãi dự kiến
    end
  end
```

## 9. Sequence: tài xế quét giao (UC-20)

Liên quan: BR-38…45, 72

Điện thoại chỉ gửi mã đơn, tọa độ và ảnh. Giờ quét, quyền và trạng thái đều do server quyết.

- Đơn không thuộc chuyến của tài xế đang đăng nhập → 403, chống IDOR. Chuyến của mình nhưng sai trạng thái → 409.
- Khóa chuyến trước, đơn sau (thứ tự khóa ở `kien-truc.md` mục 6), để tài xế không kết thúc chuyến khi một lượt quét đang chạy.
- Giao thành công sinh khoản phải thu ngay trong cùng giao dịch. Giao sau hạn vẫn cho giao, gắn cờ giao trễ.

```mermaid
sequenceDiagram
  autonumber
  actor TX as Tài xế
  participant APP as Web tài xế (điện thoại)
  participant API as API /api/toi/quet
  participant SV as Dịch vụ Quét
  participant DB as PostgreSQL
  TX->>APP: quét QR tại điểm GIAO
  APP->>APP: lấy GPS (có thể bị từ chối)
  TX->>APP: chụp ảnh, nhập tên, người nhận ký
  APP->>API: POST ma_don, loai=GIAO, lat/lng?, ảnh, chữ ký
  API->>SV: quet(tai_xe hiện tại, ...)
  SV->>DB: BEGIN, tìm GHEP hiệu lực của đơn
  SV->>DB: khóa dòng chuyến (FOR SHARE) rồi dòng đơn (FOR UPDATE)
  alt không thuộc chuyến của tài xế
    SV-->>API: 403 [BR-38]
  else chuyến của mình nhưng không ở DANG_CHAY
    SV-->>API: 409 [BR-38]
  else đơn đã có kết quả (DA_GIAO hoặc THAT_BAI)
    SV-->>API: 200 kèm trạng thái hiện tại [BR-45]
  else đơn đang DA_GHEP
    SV-->>API: 409 "đơn chưa được quét lấy" [BR-40]
  else hợp lệ
    SV->>SV: kiểm loại và kích thước file ảnh, chữ ký (security-rules)
    SV->>SV: kiểm ảnh + chữ ký + tên [BR-41]
    SV->>SV: giờ server; thiếu GPS thì gắn cờ [BR-43]; quá hạn giao thì giao_tre [BR-72]
    SV->>DB: lưu TEP (tên file server sinh), LUOT_QUET
    SV->>DB: đơn → DA_GIAO, GHEP.ket_qua, giao_tre, LICH_SU_TRANG_THAI
    SV->>DB: tạo PHAI_THU = cước, CHUA_THU [BR-56], NHAT_KY_TIEN
    API-->>APP: 200 Đã giao
  end
```

## 10. Sequence: quyết toán chuyến (UC-24)

Liên quan: BR-50…55, 62, 68

Kế toán chốt sổ một chuyến đã hoàn thành.

- Doanh thu chỉ tính đơn giao thành công trên chuyến này (BR-50).
- Lương lấy từ số đã chốt vào chuyến (BR-71); chuyến kết thúc do sự cố thì Kế toán nhập tay kèm lý do (BR-68).
- Chênh lệch dương: tài xế nộp lại; âm: công ty trả thêm. Khác 0 thì phải ghi đã xử lý (BR-55).

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
  SV->>DB: đơn DA_GIAO, chi phí, tạm ứng HIEU_LUC, định mức và lương đã chốt, km
  SV-->>API: doanh thu, định mức – thực tế – chênh lệch, dầu tham khảo, lý do lệch lãi
  API-->>UI: bảng quyết toán
  loop từng khoản chi
    KT->>UI: duyệt / điều chỉnh (lý do) / từ chối
    UI->>API: PATCH chi_phi
    API->>SV: duyet_chi_phi(...)
    SV->>DB: cập nhật + NHAT_KY_TIEN [BR-62]
  end
  KT->>UI: nhập lương tay nếu ket_thuc_bat_thuong [BR-68], ghi xử lý chênh lệch, bấm Quyết toán
  UI->>API: POST {xu_ly_chenh_lech, hinh_thuc, luc_xu_ly, luong_tay?, ly_do?}
  API->>SV: quyet_toan(chuyen_id, ke_toan, ...)
  SV->>DB: BEGIN, khóa dòng chuyến (FOR UPDATE)
  alt chuyến không ở HOAN_THANH
    SV->>DB: ROLLBACK
    SV-->>API: 409
  else còn chi phí CHO_DUYET, hoặc chênh lệch ≠ 0 mà chưa ghi xử lý
    SV->>DB: ROLLBACK
    SV-->>API: 409 / 422 [BR-55]
  else đủ điều kiện
    SV->>DB: tạo QUYET_TOAN: lãi [BR-51], chênh lệch và cách xử lý [BR-55], NHAT_KY_TIEN
    SV->>DB: chuyến → DA_QUYET_TOAN, khóa sửa [BR-29], COMMIT
    SV-->>API: lãi chuyến, số tài xế đã nộp / được trả
  end
  API-->>UI: kết quả
```
