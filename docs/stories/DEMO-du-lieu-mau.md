# DEMO: Dữ liệu mẫu cho buổi demo

- **Trạng thái:** Hoàn thành 11/11/2026 – 7/7 AC đạt (Đã duyệt 11/11/2026 – Tài: đồng ý 6 AC và 5 quyết định; AC7 thêm 26/11/2026, Tài đồng ý)
- **Tác nhân:** Nhóm (chạy trước buổi demo)
- **Đặc tả:** `docs/kien-truc.md` (thư mục `backend/seed/`), `docs/nghiep-vu.md` mục triển khai ("bản demo seed vài trăm đơn")
- **Quy tắc nghiệp vụ liên quan:** dùng lại toàn bộ service đã có, không thêm quy tắc mới
- **Người làm:** Tài (viết lệnh); **demo chạy trên máy Kiệt**

## Mô tả ngắn
Một lệnh nạp dữ liệu mẫu tính theo **ngày chạy lệnh**, để sáng ngày demo màn "Chuyến trong ngày", bản đồ, cảnh báo, quyết toán, công nợ đều có số liệu thật đủ trạng thái.

## Quyết định (Tài duyệt 11/11/2026)
1. Lệnh: `cd backend; .venv\Scripts\python -m seed.demo`. Thư mục `backend/seed/` đúng như `kien-truc.md`.
2. Tạo dữ liệu **qua service nghiệp vụ** (lập, ghép, chốt, bắt đầu, quét, kết thúc, chi phí, tạm ứng, duyệt, quyết toán) để cước, lãi, chênh lệch tạm ứng đúng quy tắc. Chỉ **giờ** của sự kiện (giờ quét, giờ bắt đầu) được đặt lùi về quá khứ trong ngày, vì service lấy giờ máy chủ.
3. Không bao giờ xóa dữ liệu. CSDL đã có chuyến thì lệnh dừng, báo rõ; muốn thêm ngày mới trên danh mục sẵn có thì `--ngay-moi`.
4. Demo trên máy Kiệt: CSDL dev của Kiệt đã có dữ liệu thử lẫn lộn, nên demo dùng **CSDL riêng, sạch** (vd `qlvc_demo` trong cùng container PostgreSQL); backend và lệnh nạp đều đọc `DATABASE_URL` có sẵn, nên chỉ cần đổi tên CSDL ở cuối chuỗi đó trong `.env` của Kiệt (Kiệt tự sửa, không thêm biến mới). Đổi lại tên cũ là về CSDL dev.
5. Ảnh bắt buộc (đồng hồ km, chữ ký) dùng một ảnh PNG nhỏ sinh trong code, không chép ảnh ngoài.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| DEMO-AC1 | Trên CSDL mới (chỉ có migration): tạo 4 tài khoản vai trò (`demo12345`) + ≥ 4 tài xế, ≥ 5 xe, ≥ 2 tuyến có tọa độ nút, ≥ 5 khách, bảng giá, ≥ 40 đơn | API | — |
| DEMO-AC2 | Hôm nay có chuyến ở đủ trạng thái `LAP`, `DA_CHOT`, `DANG_CHAY`, `HOAN_THANH`, `DA_QUYET_TOAN`, `HUY`; `GET /api/chuyen?ngay=<hôm nay>` có cờ `TRE`, `SU_CO`, `THAT_BAI`, `CHUA_QUYET_TOAN`, có `vi_tri` khác null | API | BR-73 |
| DEMO-AC3 | 7 ngày trước có chuyến đã quyết toán (để báo cáo lãi lỗ, công nợ có số); có đơn thất bại chờ xử lý, khoản chi chờ duyệt, phải thu chưa thu | API | BR-50, 51, 55 |
| DEMO-AC4 | Số liệu khớp nghiệp vụ: bảng quyết toán (`GET /api/chuyen/{id}/quyet-toan`) của mọi chuyến đã quyết toán khớp số đã lưu; cước đơn bằng cước tính lại từ bảng giá | API | BR-46…48, 51 |
| DEMO-AC5 | Chạy lần hai trên CSDL đã có chuyến → dừng, không ghi gì, báo dùng `--ngay-moi`; `--ngay-moi` thêm chuyến hôm nay trên danh mục cũ, không tạo trùng danh mục | API | — |
| DEMO-AC6 | `docs/cai-moi-truong.md` có mục "Dữ liệu demo": tạo CSDL demo riêng, chạy migration + lệnh nạp, trỏ backend sang CSDL demo, việc cần làm sáng ngày demo (`--ngay-moi`), quay lại CSDL dev sau demo. Kiệt làm theo trên máy mình được từ đầu đến cuối | Tài liệu | — |
| DEMO-AC7 | Chi phí mẫu hợp lý (thêm 26/11/2026, Tài đồng ý): số lít dầu mỗi chuyến nằm trong khoảng mức tham khảo (km đồng hồ × định mức) đến 1,2 lần mức đó; có chuyến tài xế nộp lại và có chuyến công ty trả thêm (khoản bốc xếp); ghi chú trạm dầu đúng tuyến | API | BR-55 |

## Ghi chú triển khai
- File đã đổi: `backend/seed/{__init__,dong_ho,demo}.py` (mới), `docs/cai-moi-truong.md` mục 8.
- Cách làm: mọi thao tác qua API thật bằng `TestClient` đăng nhập đúng vai trò (Điều phối, Kế toán, Quản lý, từng tài xế). `dong_ho.gia()` thay `bay_gio` / `hom_nay_vn` trong các module `app.*` và điền giờ giả cho cột `server_default=now()` trước khi flush; ra khỏi khối thì trả lại như cũ. Đăng nhập dùng giờ thật.
- Lịch: 7 ngày trước mỗi ngày 2 chuyến đã quyết toán (T01, T03); hôm nay quanh giờ chạy lệnh T: hoàn thành có 1 đơn giao không được + 1 đơn không lấy được + chi phí chờ duyệt (T−5h), đã quyết toán (T−4h), đang chạy trễ (T−150′), đang chạy có sự cố mở (T−70′), đã chốt (T+1h), đang lập (T+2h), đã hủy (T+3h), 4 đơn chờ ghép. Đơn giao trước 3 ngày đánh dấu đã thu (theo từng khách, BR-56).
- Sự cố "tài xế báo" đi qua API UC-33 (`POST /api/toi/chuyen/{id}/su-co`, có ảnh) sau khi #39 gộp (góp ý 2 review #46).
- Sửa theo Kiệt thử 12/11: ảnh mẫu là **ảnh thật** nhỏ trong `backend/seed/anh/` (hóa đơn JPG 15 KB, đồng hồ km JPG 7 KB, chữ ký PNG 1 KB; sinh một lần bằng Pillow ngoài dự án, không thêm gói) để bấm xem chứng từ ở Quyết toán có hình; `--ngay-moi` tự **kết thúc do sự cố** các chuyến "đang chạy" còn treo của ngày trước (đóng sự cố mở trước), ở giờ kết thúc kế hoạch của chính chuyến để không chồng lịch xe, tài xế của hôm nay (BR-16, 17, 68). Test `test_demo_anh_that`, `test_demo_ngay_moi_ket_thuc_chuyen_treo`.
- Sửa 26/11 (Tài hỏi ở #119, thầy dễ hỏi): trước đây mọi chuyến ghi cứng dầu 40 L / 880.000 đ "trạm Trung Lương", nên tuyến 64 km (mức tham khảo 11,5 L) bị gấp 3,5 lần. Nay số lít = km cả chuyến (tuyến + 4 km ra vào kho) × 18 L/100 km × 1,1, làm tròn: T01 34 L, T02 15 L, T03 13 L; tiền = lít × 22.000 đ. Ghi chú trạm theo tuyến (T01, T02 Trung Lương; T03 Biên Hòa). Dầu giảm thì chuyến nào tài xế cũng nộp lại, nên thêm khoản **bốc xếp** (bằng định mức bốc xếp tuyến) ở T01 các ngày `i % 3 == 0`, T03 các ngày chẵn và chuyến đã quyết toán hôm nay → các chuyến này công ty trả thêm. Test `test_demo_ac7_dau_theo_km_va_chenh_lech_hai_chieu`; thử làm hỏng (40 L cố định; bỏ bốc xếp) → test đỏ đúng chỗ.
- Chỉ chạy khi `APP_ENV=dev`: mật khẩu chung `demo12345` không bao giờ được nạp lên bản Render (góp ý 1 review #46, test `test_demo_chi_chay_o_dev`).
- Test đã viết: `backend/tests/api/test_demo_du_lieu.py` (7 ca, khoảng 2 phút vì mỗi ca nạp lại). Thử làm hỏng 3 chỗ (quét cả điểm sau giờ chạy lệnh, bỏ chặn nạp chồng, không trả đồng hồ) → test đỏ đúng chỗ.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_demo_du_lieu.py`
- Lệch đặc tả: tạm ứng 80% định mức tuyến (lần đầu thử 1.500.000 bị BR-53 chặn đúng). `vi_tri` chỉ kiểm khi có trường (PR #41).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| DEMO-AC1 | API | `test_demo_ac1_danh_muc` | Đạt | 11/11/2026 |
| DEMO-AC2 | API | `test_demo_ac2_hom_nay` (cờ, đủ 6 trạng thái, không quét sau giờ chạy lệnh); `vi_tri` chờ #41 | Đạt | 11/11/2026 |
| DEMO-AC3 | API | `test_demo_ac3_ngay_truoc_va_viec_cho` | Đạt | 11/11/2026 |
| DEMO-AC4 | API | `test_demo_ac4_so_lieu_khop` | Đạt | 11/11/2026 |
| DEMO-AC5 | API | `test_demo_ac5_khong_nap_chong_va_ngay_moi`, `test_demo_chi_chay_o_dev`, `test_demo_ngoai_khung_gio`, `test_demo_tra_lai_dong_ho` | Đạt | 11/11/2026 |
| DEMO-AC6 | Tài liệu | Kiệt làm theo mục 8 trên máy mình 11/11: tạo `qlvc_demo`, nạp không lỗi (15 chuyến đã quyết toán 7 ngày trước; hôm nay đang chạy trễ, đang chạy có sự cố, chờ quyết toán, đã chốt, đang lập, hủy; 52 đơn). Nạp sau 18:00 nên gọi `nap(bay_gio=17:00)` | Đạt | 11/11/2026 |
| DEMO-AC7 | API | `test_demo_ac7_dau_theo_km_va_chenh_lech_hai_chieu` | Đạt | 26/11/2026 |
