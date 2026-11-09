# Đặc tả API

> Phiên bản 0.2 · 15/10/2026 · Nhóm 8 (cập nhật theo nghiệp vụ 0.5). Khớp `docs/use-cases.md` (UC-01…34), `docs/nghiep-vu.md` (BR, trạng thái), `docs/kien-truc.md` (lỗi, phân quyền).
> Tài liệu này là **hợp đồng** để chia việc frontend/backend. Khi code xong, chi tiết từng trường xem ở OpenAPI do FastAPI sinh tại `/docs`; nếu hai nơi lệch nhau thì sửa file này trong cùng commit.
> Bỏ ở 0.2 (theo nghiệp vụ 0.5): `POST /api/don/{id}/xac-nhan` và `?xac_nhan=true` (UC-09), `PUT /api/chuyen/{id}/diem-dung` (UC-14), `POST /api/toi/chuyen/{id}/xuat-phat` (BR-27), `POST /api/don/{id}/dieu-chinh-cuoc` (UC-31), `POST /api/chuyen/{id}/goi-y-ghep` (UC-29), `POST /api/tam-ung/{id}/duyet`, `/tu-choi`.

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
- Khai báo route: đường dẫn cố định đặt **trước** đường dẫn có tham số cùng tiền tố, ví dụ `GET /api/chuyen/xe-kha-dung` trước `GET /api/chuyen/{id}`; nếu không FastAPI hiểu `xe-kha-dung` là `{id}`. Mỗi cặp như vậy có một test gọi đúng route cố định.

---

## 2. Danh sách endpoint

### 2.1 Xác thực, người dùng, cấu hình

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/auth/dang-nhap` | CK | UC-01 | Đặt cookie; giới hạn tần suất |
| POST | `/api/auth/dang-xuat` | Mọi vai trò | UC-01 | Xóa cookie |
| GET | `/api/auth/toi` | Mọi vai trò | UC-01 | Thông tin và vai trò người đang đăng nhập |
| GET, POST | `/api/nguoi-dung` | QL | UC-02 | BR-57; `?vai_tro=&trang_thai=&tim=&trang=&so_dong=`; POST chỉ tạo `QUAN_LY`/`DIEU_PHOI`/`KE_TOAN` (tài xế tạo ở UC-04); trùng tên đăng nhập → 409 |
| PATCH | `/api/nguoi-dung/{id}` | QL | UC-02 | `ten_dang_nhap`, `ho_ten`, `vai_tro`, `trang_thai` (khóa/mở, mở thì xóa khóa tạm); không nhận `mat_khau`. 409: đổi vai trò/trạng thái tài khoản tài xế (làm ở UC-04), tự đổi vai trò/trạng thái của mình, khóa/hạ Quản lý hoạt động cuối cùng |
| PUT | `/api/nguoi-dung/{id}/mat-khau` | QL | UC-02 | `{mat_khau}` 8–200 ký tự → 204; xóa bộ đếm sai và khóa tạm; mọi vai trò kể cả tài xế |
| GET | `/api/cau-hinh` | QL | UC-07 | Danh sách CFG-xx (gồm CFG-08…10) |
| PUT | `/api/cau-hinh/{ma}` | QL | UC-07 | Ghi người sửa, thời điểm |
| GET, POST | `/api/bang-gia` | QL | UC-07 | BR-48; mỗi mức có `hieu_luc_tu`, danh sách kèm cờ `dang_ap_dung`; trùng cặp tỉnh (không phân biệt hoa thường) + ngày → 409 |
| GET | `/api/bang-gia/ten-tinh` | QL | UC-07 | Tên tỉnh đã dùng, để gợi ý khi nhập (tránh gõ lệch) |
| PATCH | `/api/bang-gia/{id}` | QL | UC-07 | Không ảnh hưởng đơn đã tạo (BR-32) |

### 2.2 Danh mục: xe, tài xế, nút, tuyến, khách

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/xe` | DP, KT | UC-03 | `?trang_thai=&tim=&trang=&so_dong=`; KT chỉ xem (chọn xe nhập chi phí cố định) |
| POST | `/api/xe` | DP | UC-03 | Gồm `dinh_muc_lit_100km`, `km_dong_ho` (km chỉ nhập lúc tạo); xe mới `HOAT_DONG`; biển số trùng → 409; khối lượng toàn bộ < tải trọng → 422 |
| GET | `/api/xe/{id}` | DP, KT | UC-03 | |
| PATCH | `/api/xe/{id}` | DP | UC-03 | Mọi trường trừ `km_dong_ho` (gửi lên → 400, BR-70); `trang_thai` `HOAT_DONG`/`NGUNG` (BR-11); không xóa (BR-60) |
| GET, PUT | `/api/xe/{id}/chi-phi-co-dinh/{thang}` | KT | UC-03 | `{so_tien}`; tháng dạng `YYYY-MM`; ghi `NHAT_KY_TIEN` |
| GET, POST | `/api/tai-xe` | DP | UC-04 | Tạo kèm tài khoản vai trò TX |
| GET, PATCH | `/api/tai-xe/{id}` | DP | UC-04 | BR-60 |
| GET, POST | `/api/nut` | DP | UC-05 | Tỉnh hoặc kho, có tọa độ; tìm theo tên hoặc tỉnh |
| PATCH | `/api/nut/{id}` | DP | UC-05 | Sửa tên, tọa độ; nút đã có đơn thì không đổi tỉnh (422) |
| GET, POST | `/api/tuyen` | DP | UC-05 | Body gồm danh sách nút có thứ tự (phút, km, điểm nghỉ), định mức, lương khoán; BR-66 chặn > 10 giờ; trả kèm cảnh báo BR-20 |
| GET, PATCH | `/api/tuyen/{id}` | DP | UC-05 | BR-60, BR-66; thay danh sách nút chỉ khi tuyến chưa có chuyến (khác `HUY`), không thì 409 |
| GET | `/api/khach-hang` | DP, KT | UC-06 | `?trang_thai=&tim=&trang=&so_dong=`; tìm theo tên hoặc SĐT; KT chỉ xem (công nợ UC-25) |
| POST | `/api/khach-hang` | DP | UC-06 | SĐT chuẩn hóa về `0` + 9–10 số (BR-59) |
| GET | `/api/khach-hang/{id}` | DP, KT | UC-06 | |
| PATCH | `/api/khach-hang/{id}` | DP | UC-06 | `trang_thai` `HOAT_DONG`/`NGUNG`; không xóa (BR-60) |
| GET | `/api/canh-bao` | DP | UC-27 | Giấy tờ sắp hết hạn (BR-21), lượt quét thiếu GPS (BR-43), chuyến trễ làm chồng chuyến kế tiếp, đơn chờ sắp quá hạn (BR-73), sự cố đang mở |

### 2.3 Đơn hàng

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| POST | `/api/don/tinh-cuoc` | DP | UC-08 | Tính thử, không lưu (BR-46…48) |
| POST | `/api/don` | DP | UC-08 | Tạo đơn `CHO_GHEP`, chốt cước ngay (BR-31, 32, 48); thiếu bảng giá → 422 BR-48 |
| GET | `/api/don` | DP, KT | UC-08 | Lọc `trang_thai`, `khach_hang_id`, `tu`, `den`, `sap_qua_han` |
| GET | `/api/don/{id}` | DP, KT | — | Kèm lịch sử trạng thái, các lần ghép, đã lấy hàng hay chưa |
| PATCH | `/api/don/{id}` | DP | UC-10 | BR-33: chỉ khi `CHO_GHEP`/`DA_GHEP` (đơn đang ghép: chuyến phải `LAP`, không thì 409 `BR-33`); gửi trường nào sửa trường đó, không sửa khách, nút lấy / giao (→ 400); kiểm lại BR-31; tính lại cước từ bản sao giá, cước đổi thì ghi nhật ký tiền (BR-62); đang ghép thì kiểm BR-67, vi phạm → 422 `VI_PHAM_SUA` |
| POST | `/api/don/{id}/huy` | DP | UC-10, UC-22 | BR-34, cần `ly_do` (1–300 ký tự); `CHO_GHEP` → `HUY`; `DA_GHEP` ở chuyến `LAP` tự gỡ rồi hủy (gỡ làm đơn khác vi phạm → 422 `VI_PHAM_HUY`), chuyến đã chốt → 409; trạng thái khác → 409 `BR-34`. `THAT_BAI` (chuyến đã kết thúc): chưa có lượt quét `LAY` → `HUY`, đã có → 422 `BR-34` (UC-22) |
| – | ~~`/api/don/{id}/phieu`~~ | DP | UC-08, UC-19 | Bỏ endpoint (Tài chốt 04/11): phiếu gửi hàng là **trang in ở frontend** `/dieu-phoi/don/{id}/phieu`, đọc `GET /api/don/{id}`, vẽ QR bằng gói `qrcode` (QR chỉ chứa mã đơn), in bằng Ctrl+P |
| GET | `/api/don/can-xu-ly` | DP | UC-22 | Đơn `THAT_BAI` kèm `da_lay`, `so_lan_giao_tb_khach`, `nguong` (CFG-04), `ly_do_cuoi`, `cho_chuyen_xong` |
| POST | `/api/don/{id}/ghep-lai` | DP | UC-22 | `THAT_BAI → CHO_GHEP` (BR-36, 37, 69); `{han_giao?, nut_giu_id?, dia_chi_giu?, lat_giu?, lng_giu?}`; chỉ khi chuyến đã kết thúc (ghép hết hiệu lực, không thì 409 `BR-36`); đạt CFG-04 lần giao thất bại phía khách → 422 `BR-37`; đã lấy (có lượt quét `LAY`) thì nơi giữ hàng bắt buộc, bỏ khung giờ lấy cũ; chưa lấy gửi nơi giữ → 422 `BR-69`; hạn mới kiểm BR-31; cước giữ nguyên |
| POST | `/api/don/{id}/tra-hang` | DP | UC-22 | `THAT_BAI → TRA_HANG`, chỉ khi đơn đã có lượt quét lấy (BR-36), không thì 422 `BR-36`; body `{ly_do?}` tùy chọn (vào lịch sử) |

### 2.4 Chuyến (lõi)

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/chuyen/xe-kha-dung`, `/api/chuyen/tai-xe-kha-dung` | DP | UC-11 | `?tuyen_id=&khoi_hanh=` (có múi giờ), tài xế thêm `&xe_id=` không bắt buộc để lọc BR-14. Trả **mọi** xe / tài xế kèm `kha_dung` và `ly_do: [{ma, thong_diep}]` (xe: BR-11…13, 16; tài xế: `TAI_XE_NGUNG`, BR-14, 15, 17…19), khả dụng xếp trước |
| POST | `/api/chuyen` | DP | UC-11 | `{tuyen_id, khoi_hanh_du_kien, xe_id, tai_xe_id}` → `LAP` (BR-22), mã `CH-yyMMdd-NN` theo ngày khởi hành. Vi phạm → 422, `ma` là BR đầu tiên, `chi_tiet` đủ mọi vi phạm; tuyến `NGUNG` → 422 `TUYEN_NGUNG`; giờ đã qua → 422 `KHOI_HANH_DA_QUA` |
| GET | `/api/chuyen` | DP, KT | UC-11, UC-32 | Lọc trạng thái, ngày, tuyến. `?ngay=` trả **bảng chuyến trong ngày**: % đầy, tiến độ "đã xong/tổng điểm", cờ trễ (CFG-09), sự cố mở, đơn thất bại, chưa quyết toán | **UC-32 (đã làm):** có `ngay` thì mỗi chuyến kèm `theo_doi` `{xong, tong, ty_le_lap_day, co, chong}`; cờ `TRE` (quét trễ quá CFG-09), `SU_CO`, `THAT_BAI`, `CHUA_QUYET_TOAN`, `CHONG_LICH` (BR-73).
| GET | `/api/chuyen/{id}` | DP, KT | UC-13, UC-32 | UC-13 đã làm tổng quan + thẻ Hàng (cùng dạng với kết quả ghép ở mục 3.1). Đủ 5 thẻ ở UC-32: tổng quan, hàng (tải, thể tích, % đầy), lịch trình (điểm dừng suy ra theo BR-63; ETA kế hoạch từ khi chốt, giờ quét thực tế, độ trễ; kết thúc dự kiến khi đang chạy theo BR-73), dòng thời gian (km, lượt quét, chi phí, sự cố), tiền | **UC-32 (đã làm):** mỗi điểm lịch trình thêm `eta_ke_hoach`, `thuc_te` (giờ quét đầu tiên), `ket_qua` (`BO` = không lấy được nên bỏ điểm giao), `tre_phut`, `lat`, `lng` (tọa độ nút, vẽ bản đồ; nút chưa có tọa độ thì null); thêm `co`, `chong`, `ket_thuc_dang_chay` (BR-73), `ket_thuc_bat_thuong`, `ly_do_ket_thuc`, `km_bat_dau`, `km_ket_thuc`, `dong_thoi_gian`, `tien` (`dinh_muc`, `luong`, `tam_ung_hieu_luc`, `doanh_thu`), `su_co`. Đơn thất bại của chuyến đã kết thúc vẫn nằm trong `don`. Các trường này không có trong kết quả ghép / gỡ / chốt.
| GET | `/api/chuyen/{id}/xe-kha-dung`, `/tai-xe-kha-dung` | DP | UC-12 | Như trên, cho chuyến đã có: không trùng lịch với chính nó, xe phải chở đủ đơn đang ghép (BR-01, 02); tài xế mặc định xét hạng theo xe hiện tại, `?xe_id=` để xét theo xe sắp đổi |
| PUT | `/api/chuyen/{id}/phan-cong` | DP | UC-12 | `{xe_id, tai_xe_id}`; chỉ khi `LAP`; kiểm BR-11…19 và BR-67 |
| GET | `/api/chuyen/{id}/don-phu-hop` | DP | UC-13 | Đơn `CHO_GHEP` đã lọc BR-03, 04 (nút lấy = nơi giữ hàng nếu có, BR-69), hạn giao gần trước, tối đa 200 |
| POST | `/api/chuyen/{id}/ghep` | DP | UC-13 | **Chi tiết ở mục 3.1** |
| POST | `/api/chuyen/{id}/go` | DP | UC-13 | `{don_ids}`; kiểm lại cả chuyến (BR-67); ghép hết hiệu lực, đơn `→ CHO_GHEP`. Trả như 3.1. Gỡ làm đơn khác vi phạm → 422 `VI_PHAM_GO` (`chi_tiet` như 3.1); đơn không đang ghép trong chuyến → 422 `DON_KHONG_THUOC_CHUYEN`; chuyến không `LAP` → 409 `BR-09` |
| POST | `/api/chuyen/{id}/chot` | DP | UC-15 | Body tùy chọn `{xac_nhan_chay_rong, xac_nhan_lai_am}` (mặc định false). Kiểm lại nhóm A, B (BR-23): vi phạm → 422 `VI_PHAM_CHOT` (`chi_tiet` như 3.1); 0 đơn thiếu `xac_nhan_chay_rong` → 422 `BR-23`; lãi dự kiến âm thiếu `xac_nhan_lai_am` → 422 `BR-52` (chuyến rỗng chỉ cần xác nhận chạy rỗng). Lưu định mức, lương, ETA kế hoạch (BR-71). Trả như 3.1 (thêm `chay_rong`); chuyến không `LAP` → 409 `BR-09` |
| POST | `/api/chuyen/{id}/mo-chot` | DP | UC-15 | BR-24: còn tạm ứng `HIEU_LUC` → 409 `BR-24`. Về `LAP`, xóa số đã chốt và ETA kế hoạch. Trả như 3.1; chuyến không `DA_CHOT` → 409 `BR-09` |
| POST | `/api/chuyen/{id}/huy` | DP | UC-16 | BR-25: body `{ly_do}` bắt buộc, 1–300 ký tự (thiếu, rỗng, trường lạ → 400). Chuyến không ở `LAP`/`DA_CHOT` hoặc còn tạm ứng `HIEU_LUC` → 409 `BR-25`. Ghép hết hiệu lực, đơn → `CHO_GHEP`, lý do lưu ở lịch sử trạng thái chuyến và đơn. Trả như 3.1 |
| POST | `/api/chuyen/{id}/ket-thuc-su-co` | DP | UC-32 | Chỉ khi `DANG_CHAY` (không thì 409 `BR-68`); `{ly_do, km_ket_thuc?}` (BR-68), lý do 1–300 ký tự; km phải > km bắt đầu (422 `BR-70`), có thì cập nhật km xe; đơn `DA_GHEP`, `DA_LAY` → `THAT_BAI` lý do "Sự cố xe: …", ghép hết hiệu lực (BR-36); chuyến `HOAN_THANH`, `ket_thuc_bat_thuong`, kết thúc dự kiến = giờ kết thúc thực tế. Trả chi tiết như `GET /api/chuyen/{id}` |
| POST | `/api/su-co/{id}/dong` | DP | UC-32 | `{cach_xu_ly}` 1–500 ký tự; sự cố `MO → DONG`; đã đóng → 409 `SU_CO_DA_DONG`. Router `router_su_co` trong module chuyến |
| GET | `/api/chuyen/{id}/du-doan-tre` | DP | UC-30 | Lỗi hoặc chưa có mô hình → `{ "co_du_doan": false }` |

### 2.5 Tài xế: chuyến, quét mã, sự cố

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/toi/chuyen` | TX | UC-17 | Chỉ chuyến của mình (BR-58). `?nhom=can_lam` (mặc định: `DA_CHOT`, `DANG_CHAY`, đang chạy lên đầu) \| `da_xong` (`HOAN_THANH`, `DA_QUYET_TOAN`, mới nhất trước); không bao giờ có `LAP`, `HUY`; mỗi dòng có `so_don`, không có tiền |
| GET | `/api/toi/chuyen/{id}` | TX | UC-17 | Lịch trình theo BR-63, đơn ở từng điểm (địa chỉ, người liên hệ, SĐT, hàng, khung/hạn, trạng thái đơn); giờ là ETA kế hoạch lưu lúc chốt (BR-71), chưa lưu thì tính lại; có `luong_tai_xe_chot`, không có cước/lãi/định mức. Chuyến người khác, `LAP`, `HUY`, id không có → cùng 404 |
| POST | `/api/toi/chuyen/{id}/bat-dau` | TX | UC-18 | multipart: `km_bat_dau`, `anh_dong_ho`; BR-26 (đúng ngày khởi hành theo giờ VN, gồm BR-11…15 – vi phạm liệt kê trong `chi_tiet`), BR-70 (km ≥ km sàn của xe). Trả chi tiết chuyến như `GET /api/toi/chuyen/{id}`. Không phải chuyến của mình → 404; không ở `DA_CHOT` → 409 |
| POST | `/api/toi/chuyen/{id}/ket-thuc` | TX | UC-18 | multipart: `km_ket_thuc`, `anh_dong_ho`; BR-28 (còn đơn → 422, `chi_tiet` có `ma_don`), BR-70 (km > km bắt đầu, cập nhật `km_dong_ho` xe), rồi xử lý BR-36. Không ở `DANG_CHAY` → 409. **Ảnh** (mọi API có ảnh): JPEG/PNG theo nội dung file, sai → 400; > 500 KB → 413 |
| POST | `/api/toi/quet` | TX | UC-19, UC-20 | **Chi tiết ở mục 3.2** |
| POST | `/api/toi/chuyen/{id}/chi-phi` | TX | UC-21 | multipart: loại, số tiền, `so_lit` (bắt buộc với dầu), ghi chú, ảnh (BR-54) |
| PATCH, DELETE | `/api/toi/chi-phi/{id}` | TX | UC-21 | Chỉ khoản của mình khi `CHO_DUYET` |
| POST | `/api/toi/chuyen/{id}/su-co` | TX | UC-33 | multipart: loại, ghi chú, ảnh; chuyến của mình `DANG_CHAY`; không đổi trạng thái chuyến |

### 2.6 Tiền: tạm ứng, chi phí, quyết toán, công nợ, báo cáo

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/chuyen/{id}/tam-ung` | KT, QL | UC-23 | Màn hình cấp: `{chuyen_id, ma_chuyen, trang_thai_chuyen, dinh_muc, tong_hieu_luc, con_duoc_cap, khoan: [...]}`; định mức = dầu + cầu đường + bốc xếp đã chốt; `con_duoc_cap` = định mức − tổng `HIEU_LUC` (không âm) là số gợi ý |
| POST | `/api/chuyen/{id}/tam-ung` | KT | UC-23 | `{so_tien, hinh_thuc}` (`so_tien` số nguyên 1…10¹², `TIEN_MAT`/`CHUYEN_KHOAN`; sai, trường lạ → 400). Khóa dòng chuyến; chuyến không `DA_CHOT`/`DANG_CHAY` → 409 `BR-53`; tổng `HIEU_LUC` vượt định mức đã chốt → 422 `BR-53` (`chi_tiet` có `con_duoc_cap`). 201 trả khoản `{id, chuyen_id, ma_chuyen, tai_xe_id, ten_tai_xe, so_tien, hinh_thuc, trang_thai, tao_luc}`; tài xế là tài xế của chuyến |
| PATCH | `/api/tam-ung/{id}` | KT | UC-23 | `{so_tien, hinh_thuc?, ly_do}` (`ly_do` 1–300 ký tự). Kiểm lại BR-53 (các khoản khác + số mới) → 422; khoản `DA_THU_HOI` hoặc chuyến không `DA_CHOT`/`DANG_CHAY`/`HOAN_THANH` → 409 `BR-53`, chuyến `DA_QUYET_TOAN` → 409 `BR-29`; số và hình thức giữ nguyên → 400 `KHONG_CO_THAY_DOI` |
| POST | `/api/tam-ung/{id}/thu-hoi` | KT | UC-23 | `{ly_do?}` (bỏ trống: nhật ký ghi "Tài xế đã nộp lại tạm ứng"). `HIEU_LUC → DA_THU_HOI`; dùng trước khi mở chốt hoặc hủy chuyến (BR-24, 25). Trạng thái như PATCH; đã thu hồi → 409 |
| GET | `/api/tam-ung` | KT, QL | UC-23 | Lọc `trang_thai`, `chuyen_id`, `tai_xe_id`; phân trang, mới nhất trước |
| POST | `/api/chi-phi/{id}/duyet` | KT | UC-24 | `{so_tien_duyet, ly_do?}`; lý do bắt buộc khi khác số khai |
| POST | `/api/chi-phi/{id}/tu-choi` | KT | UC-24 | Cần `ly_do` |
| GET | `/api/chuyen/{id}/quyet-toan` | KT | UC-24 | Bảng quyết toán dự kiến: định mức – thực tế – chênh lệch, dầu tham khảo, lý do lãi lệch dự kiến |
| POST | `/api/chuyen/{id}/quyet-toan` | KT | UC-24 | **Chi tiết ở mục 3.3** |
| GET | `/api/phai-thu` | KT, QL | UC-25 | Lọc `trang_thai_tt`, `khach_hang_id`; phân trang, đơn giao mới trước. `{du_lieu, tong, tong_tien}`; mỗi dòng `{id, don_hang_id, ma_don, khach_hang_id, ten_khach, ngay_giao, so_tien, trang_thai_tt, phieu_thu_id, ngay_thu}` |
| GET | `/api/phai-thu/theo-khach` | KT, QL | UC-25 | Nợ theo khách (chỉ `CHUA_THU`): `[{khach_hang_id, ten_khach, so_khoan, tong_no}]`, nợ nhiều trước |
| POST | `/api/phai-thu/da-thu` | KT | UC-25 | `{phai_thu_ids, ngay}`: 1–100 id không trùng, `ngay` dạng `YYYY-MM-DD` không sau hôm nay (sai → 400); id không có → 404; có khoản đã thu → 409 `BR-56` (cả lô không đổi); khoản của nhiều khách → 422 `BR-56`. Lập một `PHIEU_THU` cho khách, các khoản `DA_THU` + `phieu_thu_id`, mỗi khoản 1 dòng `NHAT_KY_TIEN` `DA_THU`; đơn giữ `DA_GIAO` (BR-56). Trả `{phieu_thu_id, khach_hang_id, tong_tien, ngay, so_khoan}` |
| GET | `/api/bao-cao/lai-lo` | QL, KT (DP xem) | UC-26 | `?theo=chuyen\|xe\|thang&tu=&den=`; theo xe, tháng thì trừ chi phí cố định |
| GET | `/api/bao-cao/hieu-suat-xe` | QL (KT xem) | UC-34 | `?thang=`; % lấp đầy trung bình, số chuyến chạy rỗng, km, dầu thực tế so với định mức |

Mọi endpoint ghi tiền đều ghi `NHAT_KY_TIEN` (BR-62).

### 2.7 File, tra cứu

| Phương thức | Đường dẫn | Vai trò | UC | BR / ghi chú |
|---|---|---|---|---|
| GET | `/api/danh-muc/ly-do` | DP, TX | UC-19, 20, 22 | `?ap_dung=LAY\|GIAO` (bỏ trống: cả hai); trả `[{id, ten, ap_dung, phia}]`, `phia` (`KHACH`/`SU_CO_XE`) cho BR-37, 42. Danh mục nạp bằng migration `2a4c8d5f38e7` (12 lý do, `app/domain/ly_do.py`) |
| GET | `/api/tep/{id}/link` | DP, KT, TX (của chuyến mình) | — | Link có hạn 5 phút (NFR-SEC-04) |
| POST | `/api/tra-cuu` | CK | UC-28 | **Chi tiết ở mục 3.4** |

---

## 3. Chi tiết các endpoint lõi

### 3.1 `POST /api/chuyen/{id}/ghep` (UC-13, sơ đồ 8)

Request:
```json
{ "don_ids": [12, 15, 18] }
```

200: chi tiết chuyến sau khi ghép (cùng dạng `GET /api/chuyen/{id}`: tổng quan + các trường dưới, `don` là các đơn đang ghép). Số thập phân trả dạng chuỗi:
```json
{
  "id": 7,
  "ma_chuyen": "CH-261020-01",
  "tai_trong": { "da_dung_kg": "3800.00", "toi_da_kg": 5000 },
  "the_tich": { "da_dung_m3": 11.0, "toi_da_m3": 20.0 },
  "ty_le_lap_day": 0.76,
  "ket_thuc_du_kien": "2026-10-20T13:30:00+07:00",
  "lich_trinh": [
    { "thu_tu": 1, "nut": "TP.HCM", "viec": "LAY", "don_id": 12, "ma_don": "DH-0012", "eta": "2026-10-20T06:00:00+07:00" }
  ],
  "lai_du_kien": 3637000,
  "canh_bao_lai_am": false,
  "don": [ ]
}
```

422, không ghép đơn nào trong lô. Vi phạm có thể nằm ở đơn đã ghép trước đó do ETA dịch (BR-67); vi phạm của cả chuyến (BR-01, 02 tải; BR-12, 13, 15 giấy tờ theo ngày kết thúc mới; BR-16, 17 trùng lịch theo khoảng chiếm mới) có `don_id: null`. Lãi dự kiến âm không chặn, chỉ `canh_bao_lai_am: true` (xác nhận ở lúc chốt, UC-15):
```json
{
  "ma": "VI_PHAM_GHEP",
  "thong_diep": "Có đơn vi phạm quy tắc ghép, chưa ghép đơn nào",
  "chi_tiet": [
    { "don_id": 15, "ma": "BR-06", "thong_diep": "ETA giao 20/10 11:10 sau hạn giao 20/10 10:00" },
    { "don_id": 9, "ma": "BR-06", "thong_diep": "Đơn đã ghép: ETA giao dịch thành 20/10 12:30, sau hạn 12:00" }
  ]
}
```

409: chuyến không ở `LAP` hoặc đơn không ở `CHO_GHEP` (BR-09), hoặc đơn vừa bị ghép vào chuyến khác (BR-07) → giao diện tải lại danh sách. 404: chuyến hoặc đơn không tồn tại. 400: `don_ids` rỗng hoặc có trường lạ (BR-08).

### 3.2 `POST /api/toi/quet` (UC-19, UC-20, sơ đồ 9)

`multipart/form-data`:

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| `ma_don` | Có | Đọc từ QR hoặc nhập tay |
| `loai` | Có | `LAY`, `KHONG_LAY`, `GIAO`, `GIAO_THAT_BAI` (hai loại sau đưa đơn về `THAT_BAI`) |
| `lat`, `lng`, `do_chinh_xac_m` | Không | Thiếu thì gắn cờ `thieu_gps` (BR-43); `do_chinh_xac_m` 0 ≤ … < 1.000.000 (cột `Numeric(8, 1)`) |
| `anh` (1–5) | Theo loại | Bắt buộc với `GIAO`, `KHONG_LAY`, `GIAO_THAT_BAI` (BR-41, 42); ≤ 500 KB mỗi ảnh; quá 5 ảnh → 400 `QUA_NHIEU_ANH` (review PR #15). `LAY` gửi kèm thì bỏ qua |
| `chu_ky` | Với `GIAO` | PNG |
| `ten_nguoi_nhan` | Với `GIAO` | |
| `ly_do_id` | Với `KHONG_LAY`, `GIAO_THAT_BAI` | Mã trong danh mục lý do |

**Không có trường thời gian**: giờ quét lấy từ server. Gửi trường thời gian hoặc trường lạ bất kỳ → 400 (TC-BR43-02). Gửi một nửa tọa độ (chỉ `lat` hoặc chỉ `lng`) → 400. Lỗi: đơn không thuộc chuyến của mình, chưa ghép hoặc mã không có → 403 `BR-38` (cùng một câu); chuyến không `DANG_CHAY` → 409 `BR-38`; thất bại thiếu lý do / ảnh → 422 `BR-42`; ảnh sai loại 400, quá 500 KB 413. `GIAO`: thiếu ảnh, chữ ký hoặc tên người nhận (1–100 ký tự sau khi bỏ khoảng trắng) → 422 `BR-41`; chữ ký không phải PNG → 400. Giao thành công: ghép `ket_qua = DA_GIAO`, quá hạn giao (giờ máy chủ sau `han_giao`) → `giao_tre`, `canh_bao` `GIAO_TRE`; sinh `PHAI_THU` = cước, `CHUA_THU` + `NHAT_KY_TIEN` `TAO` (BR-56, 62). `GIAO_THAT_BAI` cần lý do áp dụng `GIAO` + ảnh, không sinh phải thu. Code ở `modules/quet/` (UC-19, UC-20).

200:
```json
{ "ma_don": "DH-0012", "trang_thai": "DA_GIAO", "canh_bao": ["GIAO_TRE"], "lap_lai": false }
```
`canh_bao` có thể gồm `THIEU_GPS` (BR-43), `GIAO_TRE` (BR-72). `lap_lai: true` khi quét lặp **cùng ý** với kết quả đã có (BR-45), ví dụ quét lấy đơn đã lấy; khi đó không tạo bản ghi mới, không lưu ảnh. Quét **trái kết quả** → 409, `chi_tiet[0].trang_thai` là trạng thái hiện tại (TC-BR39-02). Đơn còn `DA_GHEP` mà quét giao → 409 `BR-40` "chưa được quét lấy" (TC-BR40-02). Bảng đầy đủ (UC-20 quyết định 3):

| Đơn đang | `LAY` | `KHONG_LAY` | `GIAO` | `GIAO_THAT_BAI` |
|---|---|---|---|---|
| `DA_GHEP` | → `DA_LAY` | → `THAT_BAI` | 409 `BR-40` | 409 `BR-40` |
| `DA_LAY` | lặp (200) | 409 `BR-39` | → `DA_GIAO` | → `THAT_BAI` |
| `DA_GIAO` | lặp (200) | 409 `BR-39` | lặp (200) | 409 `BR-40` |
| `THAT_BAI` | 409 `BR-39` | lặp (200) | 409 `BR-40` | lặp (200) |

Lỗi: 403 đơn không thuộc chuyến của tài xế đang đăng nhập (BR-38, chống IDOR); 409 chuyến của mình nhưng không ở `DANG_CHAY` (BR-38), hoặc sai trạng thái đơn (ví dụ giao khi chưa lấy, BR-40); 422 thiếu ảnh, chữ ký, lý do (BR-41, 42); 413 file quá lớn.

### 3.3 `POST /api/chuyen/{id}/quyet-toan` (UC-24, sơ đồ 10)

Request (số liệu tiền do server tính; Kế toán chỉ gửi phần phải ghi tay):
```json
{
  "xu_ly_chenh_lech": "CONG_TY_DA_TRA",
  "hinh_thuc": "TIEN_MAT",
  "luc_xu_ly": "2026-10-21T09:00:00+07:00",
  "luong_tay": null,
  "ly_do_luong_tay": null
}
```
- `xu_ly_chenh_lech`: `TAI_XE_DA_NOP` | `CONG_TY_DA_TRA` | `KHONG_CHENH` (BR-55). Phải khớp dấu chênh lệch server tính.
- `luong_tay`, `ly_do_luong_tay`: bắt buộc khi chuyến `ket_thuc_bat_thuong` (BR-68); ngược lại bỏ qua, dùng lương đã chốt (BR-71).

200:
```json
{
  "chuyen_id": 7,
  "doanh_thu": 2240000,
  "tong_chi": 1050000,
  "luong_tai_xe": 600000,
  "lai": 590000,
  "tong_tam_ung_hieu_luc": 1000000,
  "chenh_lech_tam_ung": -50000,
  "xu_ly_chenh_lech": "CONG_TY_DA_TRA"
}
```

409: chuyến không ở `HOAN_THANH`; còn chi phí `CHO_DUYET` (BR-55). 422: thiếu hoặc sai `xu_ly_chenh_lech`; thiếu lương tay khi kết thúc do sự cố (BR-68). Sau khi thành công, mọi endpoint ghi tiền của chuyến trả 409 (BR-29).

### 3.4 `POST /api/tra-cuu` (UC-28)

Dùng POST để số điện thoại không nằm trong URL và log truy cập.

Request: `{ "ma_don": "DH-0012", "sdt_4_so_cuoi": "6789" }`

200:
```json
{
  "ma_don": "DH-0012",
  "trang_thai": "DA_LAY",
  "moc": [
    { "trang_thai": "CHO_GHEP", "luc": "2026-10-19T08:10:00+07:00" },
    { "trang_thai": "DA_LAY", "luc": "2026-10-20T06:05:00+07:00" }
  ]
}
```

Không trả GPS, số điện thoại tài xế, cước (BR-59). Sai mã hoặc sai số → 404 với thông báo chung "Không tìm thấy đơn". Quá tần suất → 429.
