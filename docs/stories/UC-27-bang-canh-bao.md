# UC-27: Bảng cảnh báo cho Điều phối

- **Trạng thái:** Đang làm – backend xong 7/8 AC (11/11/2026; duyệt 11/11/2026, Kiệt: "duyệt" – 7 quyết định như đề xuất). AC8 giao diện chờ Tài nối, Kiệt thử
- **Tác nhân:** Điều phối (Quản lý kế thừa quyền Điều phối)
- **Đặc tả:** `docs/use-cases.md` mục 2 (UC-27, ưu tiên S; đặc tả rút gọn ở story này) · `docs/api.md` `GET /api/canh-bao` · `nghiep-vu.md` BR-21, 43, 73, CFG-02, 09, 10 · khung "Cần chú ý" màn Chuyến của Tài (`ChuyenDanhSach.tsx`: "thay bằng GET /api/canh-bao khi làm UC-27")
- **Quy tắc nghiệp vụ liên quan:** BR-21 (giấy tờ sắp hết hạn trong CFG-02 ngày, tính cả ngày thứ CFG-02), BR-43 (lượt quét thiếu GPS gắn cờ), BR-73 (trễ quá CFG-09, chồng chuyến kế tiếp; đơn chờ ghép còn dưới CFG-10 giờ tới hạn giao), BR-57 (phân quyền)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-27-bang-canh-bao` tách từ `dev`. **Kiệt làm backend; giao diện (khung "Cần chú ý") Tài nối**, Kiệt ghi tên trường API trong mô tả PR. Chỉ đọc, không ghi CSDL.

## Mô tả ngắn
Điều phối mở trang chủ thấy một chỗ gom mọi việc cần chú ý: giấy tờ xe / tài xế sắp hoặc đã hết hạn, chuyến đang chạy bị trễ hoặc làm chồng chuyến kế tiếp, sự cố đang mở, đơn chờ ghép sắp quá hạn giao, lượt quét thiếu GPS. Thay cho việc giao diện tự gọi nhiều API và tự đoán CFG-02 = 30.

## Đặc tả rút gọn
- **`GET /api/canh-bao`** (DP, QL), không tham số (tham số lạ → 400). Trả:
  - `cau_hinh`: `{ngay_bao_truoc (CFG-02), nguong_tre_phut (CFG-09), gio_cho_ghep (CFG-10)}` để giao diện ghi đúng câu chữ, không đoán số.
  - `giay_to`: `[{doi_tuong: XE|TAI_XE, id, ten, loai: DANG_KIEM|BAO_HIEM|GPLX, han, con_ngay, het_han}]` – xe, tài xế **đang hoạt động** có hạn ≤ hôm nay + CFG-02 (giờ VN); `con_ngay` âm là đã quá; hết hạn trước, rồi hạn gần trước.
  - `chuyen_tre`: `[{chuyen_id, ma_chuyen, bien_so, ten_tai_xe, tre_phut, ket_thuc_dang_chay, chong: [ma_chuyen]}]` – chuyến `DANG_CHAY` có cờ `TRE` hoặc `CHONG_LICH`; dùng lại cách tính của UC-32 (`chuyen/theo_doi.py`, không sửa file của Tài) để hai màn luôn khớp.
  - `su_co_mo`: `[{su_co_id, chuyen_id, ma_chuyen, bien_so, ten_tai_xe, loai, ghi_chu, luc}]` – sự cố `MO`, cũ trước.
  - `don_sap_qua_han`: `[{don_id, ma_don, ten_khach, tinh_lay, tinh_giao, han_giao, con_phut, qua_han}]` – đơn `CHO_GHEP` còn **dưới** CFG-10 giờ tới hạn giao (gồm cả đơn đã quá hạn); hạn gần trước.
  - `thieu_gps`: `[{chuyen_id, ma_chuyen, ten_tai_xe, so_luot, luc_gan_nhat}]` – lượt quét `thieu_gps` của chuyến `DANG_CHAY` và chuyến kết thúc trong 24 giờ qua, gom theo chuyến.
  - `so_viec`: tổng số dòng của 5 nhóm.

## Quyết định (Kiệt duyệt 11/11/2026)
1. **Một endpoint gom 5 nhóm**, mỗi nhóm một mảng (giao diện một lần gọi). Không phân trang: đội ~10 xe nên mỗi nhóm ít dòng.
2. **Giấy tờ chỉ xét xe / tài xế `HOAT_DONG`**; xe, tài xế đã ngừng không cần nhắc.
3. **Chuyến trễ dùng lại hàm UC-32** của Tài (chỉ gọi, không sửa), để màn Chuyến và bảng cảnh báo không lệch nhau.
4. **Đơn sắp quá hạn chỉ xét `CHO_GHEP`** (đơn đã ghép thì trễ hiện qua chuyến trễ). Biên: còn đúng CFG-10 giờ thì **không** cảnh báo ("còn dưới"); đã qua hạn thì vẫn hiện, `qua_han = true`.
5. **Thiếu GPS chỉ xét chuyến đang chạy hoặc vừa kết thúc trong 24 giờ**: cảnh báo cũ hơn không còn việc gì để Điều phối làm.
6. **Không có "đã xem / ẩn cảnh báo"**: bảng tính lại mỗi lần mở, hết điều kiện thì tự biến mất. Không đổi CSDL, không thêm gói.
7. **Đơn thất bại chờ xử lý** không thêm vào đây: đã có `GET /api/don/can-xu-ly` (UC-22), giao diện giữ nguyên.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-27-AC1 | Giấy tờ, CFG-02 = 30: hạn hôm nay + 30 ngày **có** (`con_ngay` 30); + 31 ngày **không**; hạn hôm qua có, `het_han` true, `con_ngay` −1; đủ 3 loại (đăng kiểm, bảo hiểm, GPLX); xe / tài xế `NGUNG` không có; đổi CFG-02 thành 10 thì hạn + 11 ngày biến mất | API | BR-21 |
| UC-27-AC2 | Chuyến trễ: chuyến `DANG_CHAY` có lượt quét trễ hơn CFG-09 có dòng, kèm `tre_phut`; trễ đúng bằng CFG-09 không có; chuyến trễ làm chồng chuyến kế tiếp của cùng xe có `chong` đúng mã (kịch bản mục 11: quét Đ2 trễ 30′ → chồng C00 13:45); chuyến không trễ, chuyến không đang chạy không có | API | BR-73 |
| UC-27-AC3 | Sự cố: sự cố `MO` có dòng đủ trường; sự cố đã đóng không có | API | UC-33, BR-68 |
| UC-27-AC4 | Đơn sắp quá hạn, CFG-10 = 24: đơn `CHO_GHEP` còn 23 giờ 59 phút có; còn đúng 24 giờ không; đã qua hạn có, `qua_han` true; đơn `DA_GHEP`, `HUY` không có | API | BR-73, CFG-10 |
| UC-27-AC5 | Thiếu GPS: chuyến đang chạy có 2 lượt thiếu GPS → một dòng `so_luot` 2; chuyến kết thúc hơn 24 giờ trước không có; lượt có GPS không tính | API | BR-43 |
| UC-27-AC6 | `cau_hinh` trả đúng CFG-02, 09, 10 đang lưu; `so_viec` bằng tổng số dòng; không có gì thì mọi mảng rỗng, `so_viec` 0; tham số lạ → 400 | API | — |
| UC-27-AC7 | Phân quyền: Điều phối, Quản lý xem được; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-27-AC8 | (Tài nối, Kiệt thử) Khung "Cần chú ý" màn Chuyến lấy từ `/api/canh-bao`; số ngày báo trước theo CFG-02 thật | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (11/11, backend):
  - `backend/app/modules/canh_bao/` (mới): `service.py` (5 nhóm, mỗi nhóm một hàm; chuyến trễ gọi `chuyen.theo_doi._theo_doi` của UC-32, không sửa file của Tài; `tre_phut` lấy từ lượt quét gần nhất như BR-73), `router.py` (`GET /api/canh-bao`, Điều phối – Quản lý kế thừa; tham số lạ → 400). `app/main.py` thêm router theo chữ cái.
  - Tài liệu: `api.md` dòng `/api/canh-bao` ghi đủ tên trường cho giao diện.
- Không đổi CSDL, không thêm gói. Mỗi chuyến đang chạy gọi `_theo_doi` một lần (đội ~10 xe, vài chuyến chạy cùng lúc).
- Test đã viết: `tests/api/test_uc27_bang_canh_bao.py` (14 ca). Đã thử làm hỏng 9 chỗ (biên ngày thứ 30, bỏ lọc xe / tài xế đang hoạt động, biên đúng 24 giờ, bỏ lọc `CHO_GHEP`, bỏ giới hạn 24 giờ thiếu GPS, bỏ lọc cờ trễ, bỏ lọc sự cố `MO`, bỏ điều kiện `thieu_gps`) → lần nào cũng có test đỏ, rồi trả lại code.
- Toàn bộ: 864 passed (11/11, nhánh tách từ `dev`).
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc27_bang_canh_bao.py`
- Lệch đặc tả: không. `api.md` ghi "DP" → Quản lý cũng xem được vì kế thừa quyền Điều phối (`can_vai_tro`).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-27-AC1 | API | `test_uc27_ac1_giay_to` | Đạt | 11/11/2026 |
| UC-27-AC2 | API | `test_uc27_ac2_chuyen_tre_chong_lich`, `test_uc27_ac2_bien_nguong_tre` (15 / 16 phút), `test_uc27_ac2_chuyen_khong_dang_chay_khong_vao` | Đạt | 11/11/2026 |
| UC-27-AC3 | API | `test_uc27_ac3_su_co_mo` | Đạt | 11/11/2026 |
| UC-27-AC4 | API | `test_uc27_ac4_don_sap_qua_han` | Đạt | 11/11/2026 |
| UC-27-AC5 | API | `test_uc27_ac5_thieu_gps` | Đạt | 11/11/2026 |
| UC-27-AC6 | API | `test_uc27_ac6_cau_hinh_so_viec` | Đạt | 11/11/2026 |
| UC-27-AC7 | API | `test_uc27_ac7_phan_quyen` (4 vai trò), `test_uc27_ac7_chua_dang_nhap_401` | Đạt | 11/11/2026 |
| UC-27-AC8 | UI | Tài nối khung "Cần chú ý", Kiệt thử | CHƯA KIỂM | |
