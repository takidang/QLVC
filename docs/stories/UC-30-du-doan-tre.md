# UC-30: Dự đoán nguy cơ trễ chuyến

- **Trạng thái:** Nháp (chờ Tài duyệt AC, gói cài cho `ml/`, và tải dataset)
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
- File đã đổi:
- Test đã viết:
- Lệnh chạy test:
- Lệch đặc tả (nếu có) và đã sửa `docs/` chưa:

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
