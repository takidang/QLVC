# Kiểm thử khám phá và rà bảo mật – 23/11/2026

Làm theo skill `kiem-thu-kham-pha` (`.claude/skills/kiem-thu-kham-pha/`). Nhánh `tai/kiem-tra-truoc-bao-cao`, chạy trên CSDL dev của Tài (không đụng CSDL demo).

- **Rà tĩnh** (Claude Code): `npm audit`, bảng phân quyền 100 endpoint, IDOR, chống dò, upload, khoá dòng khi ghi tiền, bí mật và cookie.
- **Phá thử** (agy, Gemini 4 Neon high): viết 7 bộ script trong `script/`; Claude Code đọc lại script rồi chạy (`py -3.12 -I -X utf8 script/chay_api.py`), tái hiện từng ca lỗi bằng tay và đối chiếu log backend.

## 1. Rà tĩnh

| Hạng mục | Kết quả |
|---|---|
| Thư viện frontend (`npm audit`) | 0 lỗ hổng |
| Phân quyền | 100 endpoint đều kiểm vai trò ở backend. Không cần đăng nhập: đăng nhập, đăng xuất, tra cứu (BR-59), health, xem ảnh qua link ký HMAC hạn 5 phút (NFR-SEC-04) |
| IDOR | Service của tài xế (`toi`, `quet`, `su_co`, `chi_phi`) lọc theo tài xế đang đăng nhập; sai chủ trả 404 (BR-58) |
| Chống dò | Khoá đăng nhập sau 5 lần sai; tra cứu 10 lần sai/phút/IP, sai mã hay sai SĐT cùng một câu |
| Upload | Nhận theo byte đầu, tên do máy chủ sinh, đọc tối đa 500 KB + 1, tối đa 5 ảnh, `nosniff` |
| Tiền, trạng thái song song | Tạm ứng, chi phí, quyết toán, quét, ghép, chốt đều `FOR UPDATE` trước khi kiểm |
| Bí mật, cookie | `JWT_SECRET` bắt buộc từ môi trường (≥ 32 ký tự); cookie `httponly`, `secure`, `samesite=strict` |

## 2. Phá thử: tổng hợp

| Mục | Số ca | Đạt | Script đánh dấu lỗi | Lỗi thật |
|---|---|---|---|---|
| 1. Phân quyền / IDOR | 51 | 50 | 1 | 0 |
| 2. Nhập bừa | 52 | 30 | 22 | 12 (đã sửa) |
| 3. Gửi song song | 13 | 11 | 2 | 1 (đã sửa) |
| 4. Sai trạng thái | 26 | 26 | 0 | 0 |
| 5. Upload | 19 | 16 | 3 | 0 |
| 6. Tra cứu công khai | 9 | 8 | 1 | 1 (chỉ khi lên Render) |
| 7. Giao diện | 4 | 4 | 0 | 0 |
| **Cộng** | **174** | **145** | **29** | **14** |

Mục 1 dừng sau 51 ca vì dữ liệu dev có chuyến khác đang chạy cùng xe (BR-26 chặn bắt đầu chuyến thử), phần IDOR trên chuyến của tài xế khác đã có test tự động (`test_uc21_ac6_chuyen_nguoi_khac`, UC-17 AC9…). Mục 7 dừng sau 4 ca do lỗi trong script (`remove_listener`).

## 3. Lỗi thật đã sửa (kèm test; bỏ phần sửa thì 10 test mới đều hỏng)

| Ca | Thấy | Nguyên nhân | Sửa | Test |
|---|---|---|---|---|
| TC-10 | 5 lần xoá cùng một chi phí gửi song song → 4 lần **500** | Đọc `chuyen_id` trước, đợi khoá chuyến, lúc có khoá thì khoản đã bị xoá → `None` | Kiểm `None` sau khi khoá → 404 | `test_uc21_xoa_song_song` |
| (rà code) | Cùng kiểu khi Kế toán duyệt đúng lúc tài xế xoá khoản | Như trên, `quyet_toan._khoa_khoan` | Như trên | `test_uc24_duyet_khoan_vua_bi_xoa` |
| NB-09, 10, 23, 26, 29, 40, 41 | Số vượt cột CSDL (10^19 kg, tiền, id trong URL, `trang=10^18`) → **500** | `DataError` của PostgreSQL không có handler | Handler chung `DataError` → 400 `VUOT_GIOI_HAN` "Giá trị vượt giới hạn cho phép" | `test_vuot_gioi_han.py` |
| NB-35 | Lập chuyến khởi hành 9999-12-31 23:30 → **500** | Cộng thời gian chạy tràn `datetime` | Handler `OverflowError` → 400 `VUOT_GIOI_HAN` | `test_khoi_hanh_tran_ngay` |
| NB-36…39, NB-31 | Báo cáo / chi phí cố định với tháng `0000-01`, `9999-12` → **500** hoặc lưu tháng năm 0 | Regex tháng nhận mọi năm 4 chữ số | Tháng chỉ nhận năm 2000–2099 | `test_thang_ngoai_2000_2099` |

## 4. Không phải lỗi / để sau

| Ca | Script báo | Kết luận |
|---|---|---|
| TR-09 | Giả header `X-Forwarded-For` né được giới hạn tra cứu | **Có thật, chỉ khi triển khai.** Ở máy: uvicorn tin header từ 127.0.0.1. Trên Render với `--forwarded-allow-ips="*"` uvicorn lấy IP trái nhất (khách tự đặt). Làm khi lên Render: lấy IP do proxy Render thêm (phải nhất) hoặc chỉ tin dải IP proxy, kèm test. |
| NB-08, 17, 22, 24, 25, 27, 28 | Nhận số 10^15 (kg, đơn giá, tải trọng, chi phí), năm 1900/3000 cho hạn giấy tờ, hiệu lực bảng giá | Nhập liệu lỏng, không lỗi hệ thống. Cần nhóm chốt giới hạn nghiệp vụ trước khi đặt số (không tự đặt). |
| TC-01 | Gửi 5 lần tạo đơn song song → 5 đơn | Hai đơn cùng nội dung là hợp lệ nghiệp vụ; giao diện đã chặn bấm hai lần (UI-02 đạt). Chống gửi lặp từ API (khoá idempotency) để hướng phát triển. |
| UP-06, 12, 19 | Ảnh có 3 byte đầu JPEG + đoạn `<script>` được nhận | Báo nhầm: file lưu tên `.jpg`, phục vụ `image/jpeg` + `nosniff`, trình duyệt không chạy script. |
| PQ-45 | Kế toán xem được danh sách tài xế | Code cố ý cho Kế toán (quyết toán lương, hiệu suất); có từ UC-04; `docs/api.md` ghi thiếu, đã sửa cho khớp trong nhánh này. |
| NB-07 | `so_kien` = 2.0 được nhận thành 2 | Không lỗi (Pydantic đổi số nguyên dạng thực). |
| NB-52 | `chi_tiet.msg` lỗi 400 bằng tiếng Anh | Nhẹ: giao diện hiện `thong_diep` tiếng Việt; `chi_tiet` chỉ để gỡ lỗi. |
