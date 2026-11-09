# UC-20: Quét mã giao hàng / báo giao không được

- **Trạng thái:** Hoàn thành 16/16 AC (05/11/2026; duyệt 05/11/2026, Kiệt: đồng ý 9 quyết định và 3 chỗ sửa tài liệu – sơ đồ 9 tách quét lặp cùng ý / trái kết quả, `use-cases.md` thêm lý do "Xe hỏng", `api.md` 1–5 ảnh)
- **Tác nhân:** Tài xế (điện thoại)
- **Đặc tả:** `docs/use-cases.md` mục 3 (UC-20) · `docs/api.md` mục 3.2 (`POST /api/toi/quet`) · `docs/so-do.md` mục 9 (sequence quét giao) · `docs/kien-truc.md` mục 6 (thứ tự khóa) · `docs/security-rules.md` (quét mã, upload) · ca test `docs/ca-test-br.md` (TC-BR35, 40, 41, 42, 56, 72)
- **Quy tắc nghiệp vụ liên quan:** BR-35 (không giao một phần), BR-38 (chỉ đơn thuộc chuyến của mình đang chạy), BR-40 (giao: `DA_LAY` → `DA_GIAO` hoặc `THAT_BAI`), BR-41 (giao thành công cần ảnh + chữ ký + tên người nhận), BR-42 (thất bại cần lý do + ảnh), BR-43 (giờ máy chủ, GPS), BR-45 (quét lại không tạo bản ghi mới), BR-56 (giao xong sinh phải thu `CHUA_THU`), BR-62 (nhật ký tiền), BR-72 (giao sau hạn vẫn giao, đánh dấu trễ), BR-30 (lịch sử trạng thái)
- **Người làm:** Kiệt · **Nhánh:** `kiet/uc-20-quet-giao` tách từ `dev` **sau khi PR #15 (UC-19) gộp** (không chồng nhánh). Mở rộng module `modules/quet/` của UC-19, không tạo API mới.

## Mô tả ngắn
Chuyến đang chạy, tài xế tới điểm giao, quét QR trên phiếu để xác nhận đúng đơn, chụp ảnh, nhập tên người nhận và cho người nhận ký trên màn hình: máy chủ chuyển đơn `DA_LAY → DA_GIAO`, ghi giờ máy chủ, GPS, đánh dấu giao trễ nếu quá hạn, và sinh khoản phải thu bằng cước. Giao không được thì chọn lý do giao trong danh mục và chụp ảnh → đơn `THAT_BAI`.

## Đặc tả rút gọn
- **`POST /api/toi/quet`** (multipart, như UC-19) thêm hai loại:
  - `GIAO`: bắt buộc `anh` (≥ 1), `chu_ky` (một ảnh **PNG**), `ten_nguoi_nhan` (bỏ khoảng trắng hai đầu, 1–100 ký tự).
  - `GIAO_THAT_BAI`: bắt buộc `ly_do_id` (lý do áp dụng **GIAO**) và `anh` (≥ 1).
  - Danh sách trường cho phép thêm `chu_ky`, `ten_nguoi_nhan`; trường lạ khác vẫn 400 (gồm "số kiện giao" – TC-BR35-01).
- **Thứ tự kiểm** giữ như UC-19 (`so-do.md` mục 9):
  1. Không thuộc chuyến của mình / chưa ghép / mã không có → 403 BR-38.
  2. Khóa chuyến `FOR SHARE` rồi đơn `FOR UPDATE`.
  3. Chuyến không `DANG_CHAY` → 409 BR-38.
  4. Đơn đã có kết quả cuối (`DA_GIAO`, `THAT_BAI`): quét lặp cùng ý → 200 `lap_lai`; trái kết quả → 409 BR-39/BR-40 (bảng ở quyết định 3).
  5. **Đơn còn `DA_GHEP`** (chưa lấy) mà quét `GIAO` / `GIAO_THAT_BAI` → **409 BR-40 "Đơn chưa được quét lấy"** (TC-BR40-02). Đơn `DA_LAY` mà quét `KHONG_LAY` → 409 BR-39 (đã có ở UC-19).
  6. `GIAO`: thiếu ảnh, chữ ký hoặc tên → **422 BR-41**. `GIAO_THAT_BAI`: thiếu lý do, lý do của LẤY, thiếu ảnh → **422 BR-42**. Ảnh / chữ ký sai loại 400, quá 500 KB 413.
- **Lưu** (một giao dịch, như sơ đồ 9):
  - `LUOT_QUET` (`ten_nguoi_nhan` khi giao), ảnh vào `TEP` loại `ANH`, chữ ký vào `TEP` loại `CHU_KY`.
  - `GIAO`: đơn → `DA_GIAO`, ghép `ket_qua = DA_GIAO`; **quá hạn giao** (giờ máy chủ **sau** `han_giao`) → ghép `giao_tre = true`, `canh_bao` có `GIAO_TRE`, cước giữ nguyên (BR-72).
  - `GIAO`: tạo **`PHAI_THU`** `so_tien = cuoc_tinh`, `CHUA_THU` (BR-56) + 1 dòng **`NHAT_KY_TIEN`** `TAO` (BR-62), người là tài xế. Khóa duy nhất `phai_thu.don_hang_id` chặn sinh hai lần.
  - `GIAO_THAT_BAI`: đơn → `THAT_BAI`, ghép `ket_qua = THAT_BAI`, **không** sinh phải thu. Lý do có phía `KHACH` / `SU_CO_XE` để UC-22 đếm ngưỡng BR-37 (UC-20 chỉ lưu).
  - `LICH_SU_TRANG_THAI` (lý do = tên lý do khi thất bại). CSDL lỗi → xóa mọi file vừa ghi.
- **Trả về** `{ma_don, trang_thai, canh_bao, lap_lai}`; `canh_bao` có thể gồm `THIEU_GPS`, `GIAO_TRE`.
- **Giao diện** (trang chuyến của tài xế, như UC-19): điểm **GIAO** của đơn `DA_LAY` có nút **Giao hàng** và **Giao không được**.
  - **Giao hàng:** bước 1 quét QR (camera `qr-scanner` của UC-19) hoặc gõ mã – mã phải **khớp đơn của điểm đó**, sai thì báo ngay, chưa gửi; bước 2 chụp ảnh, nhập tên người nhận, người nhận **ký trên ô vẽ** (canvas, xuất PNG, không thêm thư viện); nút Xóa chữ ký; bấm **Xác nhận giao**.
  - **Giao không được:** chọn lý do GIAO + chụp ảnh (như "Không lấy được" của UC-19).
  - Câu báo: "Đã giao DH-… (n kiện)"; trễ hạn thì thêm khung vàng "Giao sau hạn … (BR-72)".
  - Giao hết hoặc báo thất bại hết thì khối Kết thúc chuyến của UC-18 dùng được (BR-28).

## Quyết định đề xuất (chờ Kiệt duyệt)
1. **Dùng chung API và module quét của UC-19**, chỉ thêm hai loại; `api.md` 3.2 đã có sẵn `GIAO`, `GIAO_THAT_BAI`, `chu_ky`, `ten_nguoi_nhan`.
2. **Giao theo từng điểm** (đúng đặc tả "chọn điểm GIAO, quét QR"): quét để xác nhận đúng kiện của điểm đó; mã không khớp → báo trên điện thoại, không gửi.
3. **Quét lặp và trái kết quả** (mở rộng quyết định 6 của UC-19):

   | Đơn đang | `LAY` | `KHONG_LAY` | `GIAO` | `GIAO_THAT_BAI` |
   |---|---|---|---|---|
   | `DA_GHEP` | lấy | báo thất bại | 409 BR-40 chưa lấy | 409 BR-40 chưa lấy |
   | `DA_LAY` | lặp (200) | 409 BR-39 | **giao** | **báo thất bại** |
   | `DA_GIAO` | lặp (200) | 409 BR-39 | lặp (200) | 409 BR-40 |
   | `THAT_BAI` | 409 BR-39 | lặp (200) | 409 BR-40 | lặp (200) |

4. **Chữ ký chỉ nhận PNG** (theo `api.md`); JPEG → 400. Không kiểm "chữ ký trống" ở máy chủ; giao diện không cho gửi khi chưa ký.
5. **Giao trễ khi giờ máy chủ sau hạn giao**; đúng bằng hạn là không trễ.
6. **Sinh phải thu ghi nhật ký tiền** (`NHAT_KY_TIEN` `TAO`, bảng `phai_thu`) như sơ đồ 9 và BR-62.
7. **Tên người nhận 1–100 ký tự** (cột `ten_nguoi_nhan` 100), chuẩn hóa như các ô chữ khác (`ChuBatBuoc`).
8. **Làm kèm theo review PR #15 của Tài (04/11)** – áp dụng cho cả lấy (UC-19) và giao:
   - **Tối đa 5 ảnh** mỗi lượt quét; 6 ảnh → 400 (chặn gửi hàng loạt làm đầy ổ đĩa).
   - **`do_chinh_xac_m` < 1.000.000** (cột `Numeric(8, 1)`: gửi 9.999.999,95 sẽ làm tròn thành 10.000.000 và lỗi CSDL 500).
   - **Xin vị trí ngay lúc bấm** Quét mã QR / Lấy hàng / Giao hàng / Xác nhận giao (Safari iPhone chỉ hỏi quyền vị trí khi có thao tác của người dùng; lần thử UC-19 Safari không hỏi nên ghi thiếu GPS).
9. **BR-44 cảnh báo quét sai vị trí không làm** – Tài chốt 04/11 để hướng phát triển (`nghiep-vu.md` mục 10), không làm trước 29/11.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-20-AC1 | Giao hợp lệ: đơn `DA_LAY` gửi `GIAO` + 1 ảnh + chữ ký PNG + tên "Lê Văn Nhận" + GPS → 200 `{trang_thai: DA_GIAO, canh_bao: [], lap_lai: false}`; lượt quét có tên người nhận, giờ máy chủ, tọa độ; 1 `TEP` `ANH` + 1 `TEP` `CHU_KY` có file; ghép `ket_qua = DA_GIAO`; lịch sử `DA_LAY → DA_GIAO` (TC-BR40-01, TC-BR41-01) | API | BR-40, 41, 43 |
| UC-20-AC2 | Phải thu: giao xong sinh đúng 1 `PHAI_THU` = cước của đơn, `CHUA_THU`, và 1 dòng `NHAT_KY_TIEN` `TAO`; đơn báo giao không được **không** sinh phải thu (TC-BR56-01) | API | BR-56, 62 |
| UC-20-AC3 | Giao trễ: hạn giao trước giờ quét → `DA_GIAO`, `giao_tre = true`, `canh_bao` có `GIAO_TRE`, phải thu vẫn bằng cước (TC-BR72-01); hạn sau giờ quét → `giao_tre = false` (TC-BR72-02) | API | BR-72 |
| UC-20-AC4 | Thiếu chữ ký / thiếu ảnh / thiếu tên / tên toàn khoảng trắng / tên 101 ký tự → 422 BR-41 (tên dài → 400); đúng 100 ký tự được; đơn vẫn `DA_LAY`, không có file, không phải thu (TC-BR41-02) | API | BR-41 |
| UC-20-AC5 | Chữ ký JPEG hoặc GIF → 400; chữ ký hoặc ảnh > 500 KB → 413; không để lại file | API | BR-41, security-rules |
| UC-20-AC6 | Báo giao không được hợp lệ (lý do GIAO "Người nhận vắng" + 1 ảnh) → `THAT_BAI`, lượt quét có lý do, lịch sử ghi tên lý do, ghép `ket_qua = THAT_BAI` (TC-BR42-01) | API | BR-40, 42 |
| UC-20-AC7 | Báo giao không được thiếu ảnh / thiếu lý do / lý do của LẤY / lý do không có → 422 BR-42, đơn vẫn `DA_LAY` (TC-BR42-02) | API | BR-42 |
| UC-20-AC8 | Đơn còn `DA_GHEP` (chưa lấy) quét `GIAO` hoặc `GIAO_THAT_BAI` → 409 BR-40 "chưa được quét lấy", không tạo lượt quét (TC-BR40-02) | API | BR-40 |
| UC-20-AC9 | Quét lặp và trái kết quả đúng bảng ở quyết định 3: giao lần hai → 200 `lap_lai`, vẫn 1 lượt quét, 1 phải thu, không lưu ảnh; `GIAO_THAT_BAI` đơn đã giao → 409 BR-40; `GIAO` đơn đã thất bại → 409 BR-40; `KHONG_LAY` đơn đã giao → 409 BR-39 | API | BR-45 |
| UC-20-AC10 | Hai lượt `GIAO` cùng đơn gửi đồng thời → đúng 1 lượt quét, 1 phải thu, một bên `lap_lai: true` | API | BR-45, 56 |
| UC-20-AC11 | Không giao một phần: gửi thêm trường "số kiện giao" (`so_kien_giao`) → 400, đơn vẫn `DA_LAY` (TC-BR35-01); kết quả giao chỉ có `DA_GIAO` hoặc `THAT_BAI` (TC-BR35-02) | API | BR-35 |
| UC-20-AC12 | BR-38 và phân quyền giữ như UC-19: đơn của chuyến người khác → 403; chuyến `HOAN_THANH` → 409; Điều phối, Kế toán, Quản lý → 403; chưa đăng nhập → 401 | API | BR-38, 57 |
| UC-20-AC16 | Theo review #15: gửi 6 ảnh (lấy hoặc giao) → 400, đúng 5 ảnh được; `do_chinh_xac_m` = 999.999,9 được, 1.000.000 → 400, không còn lỗi 500 | API | security-rules, BR-43 |
| UC-20-AC13 | Kết thúc chuyến (UC-18) sau khi mọi đơn đã giao hoặc thất bại → `HOAN_THANH`; đơn `THAT_BAI` khi giao bị gỡ hiệu lực (BR-36), đơn `DA_GIAO` giữ ghép | API | BR-28, 36 |
| UC-20-AC14 | Giao diện (360 px): điểm giao của đơn `DA_LAY` có **Giao hàng** và **Giao không được**; quét / gõ sai mã của điểm → báo "Mã không khớp đơn của điểm này", không gửi; ô ký vẽ được bằng ngón tay, có nút Xóa; chưa ký / chưa chụp / chưa nhập tên thì nút Xác nhận giao không gửi; thành công hiện "Đã giao DH-… (n kiện)", trễ thì có khung vàng BR-72; điểm đổi trạng thái ngay | UI | NFR-USA-02 |
| UC-20-AC15 | Thử trên điện thoại thật qua Cloudflare Tunnel, **cả Safari và Chrome iPhone**: bấm Quét / Giao hàng thì trình duyệt hỏi quyền vị trí, lượt quét có tọa độ; quét QR phiếu ở điểm giao, chụp ảnh, ký bằng ngón tay → đơn `DA_GIAO`; Điều phối mở được phiếu, Kế toán thấy khoản phải thu khi UC-25 có màn hình (nay kiểm bằng CSDL) | UI | BR-41, 56 |

## Dữ liệu thử giao diện (chuẩn bị)
Dùng tiếp CH-261031-01 trên máy Kiệt sau UC-19: **DH-MSKG7T**, **DH-6HXV2Y** `DA_LAY` (giao được; hạn giao 31/10 đã qua nên sẽ **trễ** – dùng để thử BR-72), **DH-9ZTTPG** `THAT_BAI` (thử 409 khi giao đơn đã thất bại). Ca "không trễ" cần một đơn hạn giao sau hôm nay – Claude chuẩn bị khi viết `docs/test-evidence/UC-20/du-lieu.md`.

## Ghi chú triển khai
- File đã đổi (05/11):
  - `backend/app/modules/quet/service.py`: bảng `LAM` (trạng thái đơn, loại → trạng thái mới) và `LAP` (quét lặp cùng ý) thay cho `if` của UC-19, đúng bảng ở quyết định 3; `GIAO` kiểm BR-41 (ảnh, chữ ký PNG, tên), giao trễ BR-72, `_sinh_phai_thu` (BR-56, 62); `GIAO_THAT_BAI` cần lý do áp dụng `GIAO` (BR-42).
  - `router.py`: thêm `chu_ky`, `ten_nguoi_nhan` (≤ 100); **tối đa 5 ảnh** → 400 `QUA_NHIEU_ANH`; `do_chinh_xac_m` < 1.000.000 (review #15). `schemas.py`: `LoaiQuet` đủ 4 loại.
  - `tests/api/test_uc19_quet_lay.py`: ca "gửi `GIAO` → 400" đổi thành "đơn chưa lấy → 409 BR-40" vì từ UC-20 `GIAO` là loại hợp lệ.
  - Frontend: `pages/tai-xe/GiaoHang.tsx` (mới: quét xác nhận đúng kiện của điểm, ảnh, tên, **ô ký canvas** xuất PNG); `QuetLay.tsx`: xin vị trí **ngay lúc bấm** Quét / Lấy hàng / Báo thất bại (sửa Safari iPhone), `KhongLay` dùng chung cho lấy và giao, xuất `Camera`; `ChuyenCuaToiChiTiet.tsx`: nút Giao hàng / Giao không được ở điểm giao của đơn đã lấy, câu báo nhiều cảnh báo; `api/toi.ts`: `quetMa` thêm chữ ký, tên, gắn `loai` vào kết quả, `thongBaoQuet` cho giao; `index.css`: ô ký, khung nút giao.
  - Tài liệu: `api.md` 3.2 (1–5 ảnh, trần độ chính xác, quy tắc giao, bảng quét lặp / trái kết quả), `so-do.md` mục 9 (tách lặp cùng ý 200 / trái kết quả 409), `use-cases.md` UC-20 3a (thêm lý do "Xe hỏng / sự cố trên đường").
- Test đã viết: `tests/api/test_uc20_quet_giao.py` (40 ca). Đã thử làm hỏng 4 quy tắc (bỏ sinh phải thu, bỏ đánh dấu trễ, cho giao đơn chưa lấy, bỏ bắt buộc chữ ký) → mỗi lần có test đỏ, rồi trả lại code.
- Kết quả: 40/40 đạt; toàn bộ **581 passed**; ruff, `alembic check`, oxlint, tsc, prettier, build sạch. Không đổi CSDL, không thêm gói.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc20_quet_giao.py`
- Thử giao diện: `docs/test-evidence/UC-20/du-lieu.md`. Kiệt thử 05/11: 10/10 ca đạt; chạy lại trước khi mở PR: 581 passed, mọi kiểm tra sạch.
- Để sau (ngoài UC-20, Kiệt quyết): khối Kết thúc chuyến (UC-18) tràn khung trên iPhone; nhãn điểm Lấy hiện trạng thái đơn; hỏi lại trước Xác nhận giao để chống chạm nhầm (nút sáng từ nét ký đầu tiên).

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-20-AC1 | API | `test_uc20_ac1_giao_hop_le` | Đạt | 05/11/2026 |
| UC-20-AC2 | API | `test_uc20_ac2_sinh_phai_thu` | Đạt | 05/11/2026 |
| UC-20-AC3 | API | `test_uc20_ac3_*` (2 ca) | Đạt | 05/11/2026 |
| UC-20-AC4 | API | `test_uc20_ac4_*` (6 ca, biên 100 / 101 ký tự) | Đạt | 05/11/2026 |
| UC-20-AC5 | API | `test_uc20_ac5_chu_ky_sai` (4 ca) | Đạt | 05/11/2026 |
| UC-20-AC6 | API | `test_uc20_ac6_giao_khong_duoc` | Đạt | 05/11/2026 |
| UC-20-AC7 | API | `test_uc20_ac7_giao_khong_duoc_thieu` (4 ca) | Đạt | 05/11/2026 |
| UC-20-AC8 | API | `test_uc20_ac8_don_chua_lay` (2 ca) + `test_uc19_ac9_giao_don_chua_lay` | Đạt | 05/11/2026 |
| UC-20-AC9 | API | `test_uc20_ac9_*` (6 ca) | Đạt | 05/11/2026 |
| UC-20-AC10 | API | `test_uc20_ac10_giao_dong_thoi` | Đạt | 05/11/2026 |
| UC-20-AC11 | API | `test_uc20_ac11_khong_giao_mot_phan` | Đạt | 05/11/2026 |
| UC-20-AC12 | API | `test_uc20_ac12_*` (6 ca) | Đạt | 05/11/2026 |
| UC-20-AC13 | API | `test_uc20_ac13_ket_thuc_sau_khi_giao` | Đạt | 05/11/2026 |
| UC-20-AC14 | UI | Kiệt thử máy tính 360 px, ca a–f: `docs/test-evidence/UC-20/a…f-*.png` | Đạt | 05/11/2026 |
| UC-20-AC15 | UI | Kiệt thử iPhone **Safari** qua Cloudflare Tunnel, ca g, h, i, k: `g-quet-xac-nhan.png`, `h-ky-ngon-tay.png`, `k-hoan-thanh.png`; ca i kiểm bằng CSDL (tọa độ có, sai số 35 m: Safari đã hỏi và gửi vị trí); Điều phối mở phiếu QR; phải thu kiểm bằng CSDL. Chrome iPhone không thử lại (UC-19 đã có tọa độ trên Chrome) | Đạt | 05/11/2026 |
| UC-20-AC16 | API | `test_uc20_ac16_*` (4 ca, biên 5 ảnh, 999.999,9 / 1.000.000) | Đạt | 05/11/2026 |
