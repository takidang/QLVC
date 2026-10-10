# Đặc tả API

> Phiên bản 0.1 · 10/10/2026 · Nhóm 10. Khớp `docs/use-cases.md` (UC-01…31), `docs/nghiep-vu.md` (BR, trạng thái), `docs/kien-truc.md` (lỗi, phân quyền).
> Tài liệu này là **hợp đồng** để chia việc frontend/backend. Khi code xong, chi tiết từng trường xem ở OpenAPI do FastAPI sinh tại `/docs`; nếu hai nơi lệch nhau thì sửa file này trong cùng commit.

---

## 1. Quy ước chung

- Tiền tố `/api`. JSON, tên trường `snake_case` không dấu. Upload file dùng `multipart/form-data`.
- Đăng nhập bằng cookie `access_token` (httpOnly). Không gửi token trong URL.
- Vai trò: **QL** Quản lý, **DP** Điều phối, **TX** Tài xế, **KT** Kế toán, **CK** công khai (không đăng nhập). QL được làm mọi việc của DP.
- Danh sách: `?trang=1&so_dong=20`, trả `{ "du_lieu": [...], "tong": 123 }`.
- Lỗi: `{ "ma", "thong_diep", "chi_tiet" }`, mã HTTP theo `kien-truc.md` mục 7. Vi phạm nghiệp vụ là **422** kèm mọi mã BR vi phạm; sai trạng thái hoặc xung đột là **409**.
- Tiền là số nguyên đồng; thời gian ISO 8601 có múi giờ.
- **Không có endpoint xóa** xe, tài xế, tuyến, khách, đơn: chuyển `NGUNG` hoặc `HUY` (BR-60, BR-34).
- Chuyển trạng thái dùng `POST /.../<hanh-dong>` (ví dụ `/chot`, `/huy`), không cho `PATCH` trường `trang_thai`.

---

## 2. Danh sách endpoint

### 2.1 Xác thực, người dùng, cấu hình

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/auth/dang-nhap` | CK | UC-01 | Đặt cookie; giới hạn tần suất |
| POST | `/api/auth/dang-xuat` | Mọi vai trò | UC-01 | Xóa cookie |
| GET | `/api/auth/toi` | Mọi vai trò | UC-01 | Thông tin và vai trò người đang đăng nhập |
| GET, POST | `/api/nguoi-dung` | QL | UC-02 | BR-57 |
| PATCH | `/api/nguoi-dung/{id}` | QL | UC-02 | Đổi vai trò, khóa tài khoản |
| GET | `/api/cau-hinh` | QL | UC-07 | Danh sách CFG-xx |
| PUT | `/api/cau-hinh/{ma}` | QL | UC-07 | Ghi người sửa, thời điểm |
| GET, POST | `/api/bang-gia` | QL | UC-07 | BR-48 |
| PATCH | `/api/bang-gia/{id}` | QL | UC-07 | Không ảnh hưởng đơn đã chốt cước (BR-32) |

### 2.2 Danh mục: xe, tài xế, nút, tuyến, khách

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET, POST | `/api/xe` | DP | UC-03 | |
| GET, PATCH | `/api/xe/{id}` | DP | UC-03 | BR-60: ngừng thay vì xóa |
| GET, POST | `/api/tai-xe` | DP | UC-04 | Tạo kèm tài khoản vai trò TX |
| GET, PATCH | `/api/tai-xe/{id}` | DP | UC-04 | BR-60 |
| GET, POST | `/api/nut` | DP | UC-05 | Tỉnh hoặc kho, có tọa độ |
| GET, POST | `/api/tuyen` | DP | UC-05 | Body gồm danh sách nút có thứ tự; trả kèm cảnh báo BR-20 |
| GET, PATCH | `/api/tuyen/{id}` | DP | UC-05 | BR-60 |
| GET, POST | `/api/khach-hang` | DP | UC-06 | |
| GET, PATCH | `/api/khach-hang/{id}` | DP | UC-06 | BR-60 |
| GET | `/api/canh-bao` | DP | UC-27 | Giấy tờ sắp hết hạn (BR-21), lượt quét thiếu GPS, sai vị trí (BR-43, 44) |

### 2.3 Đơn hàng

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/don/tinh-cuoc` | DP | UC-08 | Tính thử, không lưu (BR-46…48) |
| POST | `/api/don` | DP | UC-08 | Tạo đơn `MOI` (BR-31); `?xac_nhan=true` để xác nhận luôn |
| GET | `/api/don` | DP, KT | UC-08 | Lọc `trang_thai`, `khach_hang_id`, `tu`, `den` |
| GET | `/api/don/{id}` | DP, KT | — | Kèm lịch sử trạng thái, các lần ghép |
| PATCH | `/api/don/{id}` | DP | UC-10 | BR-33: chỉ trước `DA_LAY_HANG`; tính lại cước từ giá đã chốt |
| POST | `/api/don/{id}/xac-nhan` | DP | UC-09 | `MOI → CHO_GHEP`, chốt cước (BR-32, 48) |
| POST | `/api/don/{id}/huy` | DP | UC-10 | BR-34, cần `ly_do` |
| GET | `/api/don/{id}/phieu` | DP | UC-08 | Phiếu gửi hàng có QR (PDF hoặc PNG) |
| POST | `/api/don/{id}/ghep-lai` | DP | UC-22 | `→ CHO_GHEP` (BR-36, 37); có thể đổi `han_giao` |
| POST | `/api/don/{id}/hoan-hang` | DP | UC-22 | `GIAO_THAT_BAI → HOAN_HANG` |
| POST | `/api/don/{id}/dieu-chinh-cuoc` | KT, QL | UC-31 | BR-61, 62 |

### 2.4 Chuyến (lõi)

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/chuyen` | DP | UC-11 | Tuyến + giờ khởi hành → `LEN_KE_HOACH` |
| GET | `/api/chuyen` | DP, KT | UC-11 | Lọc trạng thái, ngày, tuyến |
| GET | `/api/chuyen/{id}` | DP, KT | — | Xe, tài xế, đơn, điểm dừng, tải/thể tích đã dùng, lãi dự kiến |
| GET | `/api/chuyen/{id}/xe-kha-dung` | DP | UC-12 | Kèm lý do loại từng xe (BR-11…13, 16) |
| GET | `/api/chuyen/{id}/tai-xe-kha-dung` | DP | UC-12 | Kèm lý do loại (BR-14, 15, 17…19) |
| PUT | `/api/chuyen/{id}/phan-cong` | DP | UC-12 | `{xe_id, tai_xe_id}`; BR-01, 02, 11…19, 22 |
| GET | `/api/chuyen/{id}/don-phu-hop` | DP | UC-13 | Đơn `CHO_GHEP` đã lọc BR-03, 04 |
| POST | `/api/chuyen/{id}/ghep` | DP | UC-13 | **Chi tiết ở mục 3.1** |
| POST | `/api/chuyen/{id}/go` | DP | UC-13 | `{don_ids}`; gỡ đơn: ghép hết hiệu lực, đơn `→ CHO_GHEP`, xóa 2 điểm dừng |
| PUT | `/api/chuyen/{id}/diem-dung` | DP | UC-14 | Thứ tự mới; BR-10 |
| POST | `/api/chuyen/{id}/chot` | DP | UC-15 | BR-23; trả cảnh báo lãi âm (BR-52), cần `xac_nhan_lai_am=true` để chốt |
| POST | `/api/chuyen/{id}/mo-chot` | DP | UC-15 | BR-24 |
| POST | `/api/chuyen/{id}/huy` | DP | UC-16 | BR-25, cần `ly_do` |

### 2.5 Tài xế: chuyến và quét mã

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/toi/chuyen` | TX | UC-17 | Chỉ chuyến của mình (BR-58) |
| GET | `/api/toi/chuyen/{id}` | TX | UC-17 | Điểm dừng theo thứ tự, đơn ở từng điểm |
| POST | `/api/toi/chuyen/{id}/bat-dau` | TX | UC-18 | BR-26 |
| POST | `/api/toi/chuyen/{id}/xuat-phat` | TX | UC-18 | BR-27 |
| POST | `/api/toi/chuyen/{id}/ket-thuc` | TX | UC-18 | BR-28, rồi xử lý BR-36 |
| POST | `/api/toi/quet` | TX | UC-19, UC-20 | **Chi tiết ở mục 3.2** |
| POST | `/api/toi/chuyen/{id}/chi-phi` | TX | UC-21 | multipart: loại, số tiền, ghi chú, ảnh (BR-54) |
| PATCH, DELETE | `/api/toi/chi-phi/{id}` | TX | UC-21 | Chỉ khoản của mình khi `CHO_DUYET` |

### 2.6 Tiền: tạm ứng, chi phí, quyết toán, công nợ, báo cáo

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/chuyen/{id}/tam-ung` | KT | UC-23 | BR-53; vượt định mức → `CHO_QUAN_LY_DUYET` |
| PATCH | `/api/tam-ung/{id}` | KT | UC-23 | Kiểm lại BR-53 mỗi lần sửa; cần `ly_do` |
| POST | `/api/tam-ung/{id}/duyet`, `/tu-choi` | QL | UC-23 | |
| POST | `/api/tam-ung/{id}/xac-nhan-hoan` | KT | UC-16 | `PHAI_HOAN → DA_HOAN` (BR-25) |
| GET | `/api/tam-ung` | KT, QL | UC-23 | Lọc `trang_thai` (`CHO_QUAN_LY_DUYET` cho Quản lý duyệt, `PHAI_HOAN` cho Kế toán thu lại), `chuyen_id`, `tai_xe_id` |
| POST | `/api/chi-phi/{id}/duyet` | KT | UC-24 | `{so_tien_duyet, ly_do?}`; lý do bắt buộc khi khác số khai |
| POST | `/api/chi-phi/{id}/tu-choi` | KT | UC-24 | Cần `ly_do` |
| GET | `/api/chuyen/{id}/quyet-toan` | KT | UC-24 | Bảng quyết toán dự kiến |
| POST | `/api/chuyen/{id}/quyet-toan` | KT | UC-24 | **Chi tiết ở mục 3.3** |
| GET | `/api/phai-thu` | KT | UC-25 | Lọc `trang_thai_tt`, khách |
| POST | `/api/phai-thu/{id}/phieu-thu` | KT | UC-25 | `{so_tien, ngay}`; cập nhật trạng thái thanh toán (BR-56) |
| GET | `/api/bao-cao/lai-lo` | QL, KT (DP xem) | UC-26 | `?theo=chuyen\|xe\|tuyen&tu=&den=` |

Mọi endpoint ghi tiền đều ghi `NHAT_KY_TIEN` (BR-62).

### 2.7 File, tra cứu, module phụ

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/danh-muc/ly-do` | DP, TX | UC-19, 20, 22 | `?loai=KHONG_LAY\|GIAO_THAT_BAI`; danh mục lý do cho BR-42 |
| GET | `/api/tep/{id}/link` | DP, KT, TX (của chuyến mình) | — | Link có hạn 5 phút (NFR-SEC-04) |
| POST | `/api/tra-cuu` | CK | UC-28 | **Chi tiết ở mục 3.4** |
| POST | `/api/chuyen/{id}/goi-y-ghep` | DP | UC-29 | Chỉ trả gợi ý; áp dụng thì gọi `/ghep` |
| GET | `/api/chuyen/{id}/du-doan-tre` | DP | UC-30 | Lỗi hoặc chưa có mô hình → `{ "co_du_doan": false }` |

---

## 3. Chi tiết các endpoint lõi

### 3.1 `POST /api/chuyen/{id}/ghep` (UC-13, sơ đồ 8)

Request:
```json
{ "don_ids": [12, 15, 18] }
```

200:
```json
{
  "chuyen_id": 7,
  "da_ghep": [12, 15, 18],
  "tai_trong": { "da_dung_kg": 4200, "toi_da_kg": 5000 },
  "the_tich": { "da_dung_m3": 18.5, "toi_da_m3": 24.0 },
  "lai_du_kien": 3150000
}
```

422, không ghép đơn nào trong lô:
```json
{
  "ma": "VI_PHAM_GHEP",
  "thong_diep": "Có đơn vi phạm quy tắc ghép, chưa ghép đơn nào",
  "chi_tiet": [
    { "don_id": 15, "ma": "BR-01", "thong_diep": "Vượt tải trọng 350 kg" },
    { "don_id": 18, "ma": "BR-06", "thong_diep": "ETA giao 15/10 18:00 sau hạn giao 15/10 12:00" }
  ]
}
```

409: chuyến không ở `GHEP_DON` (BR-09), hoặc đơn vừa bị ghép vào chuyến khác (BR-07) → giao diện tải lại danh sách.

### 3.2 `POST /api/toi/quet` (UC-19, UC-20, sơ đồ 9)

`multipart/form-data`:

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| `ma_don` | Có | Đọc từ QR hoặc nhập tay |
| `loai` | Có | `LAY`, `KHONG_LAY`, `GIAO`, `GIAO_THAT_BAI` |
| `lat`, `lng`, `do_chinh_xac_m` | Không | Thiếu thì gắn cờ `thieu_gps` (BR-43) |
| `anh` (1 hoặc nhiều) | Theo loại | Bắt buộc với `GIAO`, `KHONG_LAY`, `GIAO_THAT_BAI` (BR-41, 42); ≤ 500 KB mỗi ảnh |
| `chu_ky` | Với `GIAO` | PNG |
| `ten_nguoi_nhan` | Với `GIAO` | |
| `ly_do` | Với `KHONG_LAY`, `GIAO_THAT_BAI` | Mã trong danh mục lý do |

**Không có trường thời gian**: giờ quét lấy từ server.

200:
```json
{ "ma_don": "DH-0012", "trang_thai": "DA_GIAO", "canh_bao": ["SAI_VI_TRI"], "lap_lai": false }
```
`lap_lai: true` khi đơn đã có kết quả từ trước (BR-45); khi đó không tạo bản ghi mới.

Lỗi: 403 đơn không thuộc chuyến của tài xế đang đăng nhập (BR-38, chống IDOR); 409 chuyến của mình nhưng không ở `DANG_BOC`/`DANG_CHAY` (BR-38), hoặc sai trạng thái đơn (ví dụ giao khi chưa lấy, BR-40); 422 thiếu ảnh, chữ ký, lý do (BR-41, 42); 413 file quá lớn.

### 3.3 `POST /api/chuyen/{id}/quyet-toan` (UC-24, sơ đồ 10)

Request: `{}` (mọi số liệu do server tính).

200:
```json
{
  "chuyen_id": 7,
  "doanh_thu": 12500000,
  "tong_chi": 6900000,
  "luong_tai_xe": 1500000,
  "lai": 4100000,
  "tong_tam_ung_hieu_luc": 7000000,
  "chenh_lech_tam_ung": 100000,
  "huong": "TAI_XE_NOP_LAI"
}
```

409: chuyến không ở `HOAN_THANH`; còn chi phí `CHO_DUYET` hoặc tạm ứng `CHO_QUAN_LY_DUYET` (BR-55). Sau khi thành công, mọi endpoint ghi tiền của chuyến trả 409 (BR-29).

### 3.4 `POST /api/tra-cuu` (UC-28)

Dùng POST để số điện thoại không nằm trong URL và log truy cập.

Request: `{ "ma_don": "DH-0012", "sdt_4_so_cuoi": "6789" }`

200:
```json
{
  "ma_don": "DH-0012",
  "trang_thai": "DA_LAY_HANG",
  "moc": [
    { "trang_thai": "CHO_GHEP", "luc": "2026-10-14T08:10:00+07:00" },
    { "trang_thai": "DA_LAY_HANG", "luc": "2026-10-15T07:42:00+07:00" }
  ]
}
```

Không trả GPS, số điện thoại tài xế, cước (BR-59). Sai mã hoặc sai số → 404 với thông báo chung "Không tìm thấy đơn". Quá tần suất → 429.
