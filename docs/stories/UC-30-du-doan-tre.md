# UC-30: Dự đoán nguy cơ trễ chuyến

- **Trạng thái:** Đang làm
- **Tác nhân:** Điều phối viên (Quản lý kế thừa)
- **Đặc tả:** `docs/use-cases.md` (UC-30, mức C), `docs/nghiep-vu.md` mục 7, `docs/kien-truc.md` KT-08, `docs/api.md` mục 2.4
- **Quy tắc nghiệp vụ liên quan:** không có BR chặn; AI chỉ gợi ý (nghiep-vu.md mục 7)
- **Người làm:** Tài (backend + `ml/`); giao diện do phiên giao diện v2 làm

## Mô tả ngắn
Điều phối mở chi tiết chuyến thấy nhãn "nguy cơ trễ" (thấp / trung bình / cao) kèm xác suất và các yếu tố chính. Chỉ là gợi ý: không chặn thao tác, không đổi ETA kế hoạch. Mô hình train sẵn ngoài backend; lỗi hoặc thiếu mô hình thì trả "không có gợi ý", lõi vẫn chạy.

## Quyết định (Claude đề xuất, chờ Tài duyệt)
1. **Dữ liệu train:** Kaggle "Delivery truck trips data" (ramakrishnanthiyagu): chuyến xe tải ở Ấn Độ có ETA kế hoạch, giờ đến thật, cờ đúng giờ / trễ, quãng đường. **Tài tải về** (Kaggle cần đăng nhập) và đọc giấy phép trên Data Card. File để ở `ml/data/`, **không commit** nếu giấy phép không cho phân phối lại. Không dùng dữ liệu demo (do `seed.demo` tự sinh bằng công thức, nghiep-vu.md cấm).
2. **Đặc trưng chỉ lấy thứ cả dataset và hệ thống đều có** lúc lập chuyến: quãng đường (km tuyến), thời gian dự kiến (giờ, từ ETA kế hoạch), giờ khởi hành trong ngày, thứ trong tuần. Nhãn: trễ khi thực tế > kế hoạch.
3. **Mô hình:** hồi quy logistic (đơn giản, giải thích được từng yếu tố). Train bằng script `ml/train_du_doan_tre.py` dùng `pandas`, `scikit-learn` — **chỉ cài cho `ml/`** (`ml/requirements.txt`), không thêm vào backend. Xuất hệ số và tham số chuẩn hóa ra `backend/app/modules/goi_y/mo_hinh_tre.json`.
4. **Backend không cần gói mới:** đọc JSON lúc chạy, tính bằng `math` (sigmoid). Mức: `THAP` < 0,3 ≤ `TRUNG_BINH` < 0,6 ≤ `CAO`.
5. Ghi rõ độ tin cậy: kèm `nguon` (tên dataset, ngày train, số mẫu, AUC trên tập kiểm tra) để thầy hỏi thì trả lời được; dữ liệu Ấn Độ khác điều kiện Việt Nam, nên đây là mô hình khởi đầu, train lại khi hệ thống có lượt quét thật.

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-30-AC1 | Script train chạy lại được từ file dataset: tách tập train / kiểm tra cố định (seed), in AUC, độ chính xác, recall; xuất JSON có hệ số, chuẩn hóa, ngưỡng, thông tin nguồn | Logic | — |
| UC-30-AC2 | Hàm dự đoán trong backend cho cùng đầu vào trả cùng xác suất như mô hình scikit-learn đã train (sai số < 1e-6) | Logic | — |
| UC-30-AC3 | `GET /api/chuyen/{id}/du-doan-tre` chuyến chưa hủy → `{co_du_doan: true, xac_suat, muc, yeu_to: [{ten, huong}], nguon}`; xác suất trong [0, 1]; `muc` đúng ngưỡng (biên 0,3 và 0,6) | API | — |
| UC-30-AC4 | Không có file mô hình, file hỏng, hoặc tính lỗi → 200 `{co_du_doan: false}`; chuyến hủy → `{co_du_doan: false}`; chuyến không tồn tại → 404 | API | KT-08 |
| UC-30-AC5 | Chỉ gợi ý: gọi dự đoán không đổi trạng thái, ETA, dữ liệu nào của chuyến; mọi thao tác lập / ghép / chốt không phụ thuộc kết quả | API | nghiep-vu mục 7 |
| UC-30-AC6 | Phân quyền: Điều phối, Quản lý xem; Kế toán, Tài xế → 403; chưa đăng nhập → 401 | API | BR-57 |
| UC-30-AC7 | Giao diện: nhãn nguy cơ trễ trên chi tiết chuyến (phiên giao diện v2) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi (đợt 1, backend, chưa có dataset): `backend/app/modules/goi_y/` (`du_doan_tre.py` tính thuần bằng `math`, `service.py` với hằng `DUONG_DAN_MO_HINH`, `router.py`, `schemas.py`), `backend/app/main.py` (gắn `goi_y_router`). Chưa có `mo_hinh_tre.json` thật: API trả `{co_du_doan: false}` cho tới khi đợt 2 train và xuất file (AC1, AC2, AC7 làm sau).
- Đặc trưng: `km` = max `km_tu_diem_dau` của tuyến; `thoi_gian_gio` = kết thúc − khởi hành dự kiến (giờ); `gio_khoi_hanh`, `thu_trong_tuan` (Thứ Hai = 0) theo giờ Việt Nam (`GIO_VN` trong `app/thoi_gian.py`).
- Test đã viết: `backend/tests/api/test_uc30_du_doan_tre.py` (AC3–AC6, file mô hình mẫu ghi vào `tmp_path` + `monkeypatch`), `backend/tests/unit/test_uc30_du_doan_tre.py` (ngưỡng, xác suất tính tay, mô hình sai định dạng).
- Lệnh chạy test: `cd backend` → `.venv\Scripts\python -m pytest tests -q -k uc30`; `.venv\Scripts\python -m ruff check app tests`.
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa: không lệch. Mọi lỗi mô hình (không có file, JSON hỏng, thiếu khóa, mảng lệch độ dài, `do_lech` = 0, đặc trưng lạ, `nguon` không phải object) đều bắt trong service, ghi `logging.warning`, trả 200 `{co_du_doan: false}`.
- Đợt 2 (train thật, AC1, AC2): `ml/train_du_doan_tre.py`, `ml/requirements.txt` (pandas 3.1.1, scikit-learn 1.9.1, openpyxl 3.1.5, kagglehub 1.0.3), `ml/README.md`; xuất `backend/app/modules/goi_y/mo_hinh_tre.json` và `backend/tests/du_lieu/mau_du_doan_tre.json` (20 mẫu tập kiểm tra, chỉ 4 đặc trưng + xác suất scikit-learn); test `test_uc30_ac2_khop_sklearn` trong `backend/tests/unit/test_uc30_du_doan_tre.py`.
- Dữ liệu: chỉ đọc 6 cột `BookingID_Date`, `trip_start_date`, `Planned_ETA`, `TRANSPORTATION_DISTANCE_IN_KM`, `ontime`, `delay` (không đọc cột tên, số điện thoại tài xế). Nhãn: `delay = R` → trễ, `ontime = G` → đúng giờ. 6880 dòng; bỏ 38 (nhãn mâu thuẫn / không có), 701 (thiếu km), 18 (km ≤ 0), 81 (thời gian dự kiến ≤ 0 hoặc > 240 giờ), 2259 (ETA mặc định = lúc đặt + 100 giờ, không phải kế hoạch thật) → **3783 mẫu**.
- Mô hình: `StandardScaler` + `LogisticRegression(max_iter=1000)`, tách 75/25 phân tầng, seed 42 (train 2837, kiểm tra 946, tỷ lệ trễ 82%). Trên tập kiểm tra: **AUC 0,714; độ chính xác 0,852; recall 0,988** (ngưỡng 0,5). Hệ số (trên giá trị chuẩn hóa): km +0,849; thời gian dự kiến −1,150; giờ khởi hành +0,194; thứ trong tuần −0,203; chặn +1,681.
- Độ tin cậy: tỷ lệ trễ trong dataset cao (82%), nên độ chính xác chỉ hơn mức "luôn đoán trễ" (0,82) một chút và đa số chuyến rơi vào mức `CAO`; AUC 0,714 mới là số đo khả năng xếp hạng. Dữ liệu Ấn Độ: mô hình khởi đầu, train lại khi có dữ liệu thật.
- Lặp lại được: chạy train hai lần cho hai file JSON giống hệt từng byte (cùng SHA-256).
- Lệnh: `ml\.venv\Scripts\python ml\train_du_doan_tre.py`; test như trên.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-30-AC1 | Logic | `ml/train_du_doan_tre.py` (seed 42, chạy 2 lần ra JSON giống hệt) | Đạt: 3783 mẫu (train 2837 / kiểm tra 946), AUC 0,714, độ chính xác 0,852, recall 0,988 | 19/11/2026 |
| UC-30-AC2 | Logic | `test_uc30_ac2_khop_sklearn` (unit; 20 mẫu tập kiểm tra, sai số < 1e-6) | Đạt | 19/11/2026 |
| UC-30-AC3 | API | `test_uc30_ac3_du_doan_thanh_cong`, `test_uc30_ac3_muc_tai_bien` (api); `test_uc30_ac3_*` (unit) | Đạt (mô hình mẫu trong test) | 19/11/2026 |
| UC-30-AC4 | API | `test_uc30_ac4_mo_hinh_loi_khong_co_goi_y`, `test_uc30_ac4_chuyen_huy_khong_co_goi_y`, `test_uc30_ac4_chuyen_khong_ton_tai` (api); `test_uc30_ac4_*` (unit) | Đạt | 19/11/2026 |
| UC-30-AC5 | API | `test_uc30_ac5_khong_doi_du_lieu_chuyen` | Đạt | 19/11/2026 |
| UC-30-AC6 | API | `test_uc30_ac6_phan_quyen` | Đạt | 19/11/2026 |
