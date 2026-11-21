# ml/ – Train mô hình dự đoán nguy cơ trễ chuyến (UC-30)

Chỉ dùng ngoài backend; backend chỉ đọc file JSON xuất ra (không cần scikit-learn).

## Cài đặt
```
python -m venv ml\.venv
ml\.venv\Scripts\python -m pip install -r ml\requirements.txt
```

## Tải dataset
Kaggle "Delivery truck trips data" (`ramakrishnanthiyagu/delivery-truck-trips-data`), cần tài khoản Kaggle:
```
ml\.venv\Scripts\python -c "import kagglehub; print(kagglehub.dataset_download('ramakrishnanthiyagu/delivery-truck-trips-data'))"
```
Chép `Delivery truck trip data.xlsx` vào `ml/data/`. Thư mục này bị gitignore: file có tên, số điện thoại tài xế, **không commit**.

## Nguồn và giấy phép
- Dataset: "Delivery truck trips data" của Ram Thiagu (Kaggle `ramakrishnanthiyagu`), bản duy nhất 04/02/2021: https://www.kaggle.com/datasets/ramakrishnanthiyagu/delivery-truck-trips-data
- Giấy phép: **CC BY-SA 3.0** (https://creativecommons.org/licenses/by-sa/3.0/), theo trường `licenseName` của Kaggle API ngày 21/11/2026. Mô tả dataset không ghi nguồn gốc ban đầu.
- Nhóm đã biến đổi: lọc 6880 → 3783 chuyến, chỉ giữ 4 đặc trưng (quãng đường, thời gian dự kiến, giờ khởi hành, thứ trong tuần) và nhãn trễ; không giữ cột nào về tài xế, khách, xe.
- Hai tệp dẫn xuất từ dataset nằm trong repo, cùng giấy phép CC BY-SA 3.0: `backend/app/modules/goi_y/mo_hinh_tre.json` (hệ số mô hình) và `backend/tests/du_lieu/mau_du_doan_tre.json` (20 mẫu đặc trưng để test).

## Train
Từ gốc repo:
```
ml\.venv\Scripts\python ml\train_du_doan_tre.py            # mặc định ml/data/Delivery truck trip data.xlsx
ml\.venv\Scripts\python ml\train_du_doan_tre.py <file.xlsx>
```
Script in số dòng bỏ ở từng bước lọc, AUC, accuracy, recall trên tập kiểm tra (25%, seed 42) và ghi:
- `backend/app/modules/goi_y/mo_hinh_tre.json`: hệ số, chuẩn hóa, ngưỡng, nguồn;
- `backend/tests/du_lieu/mau_du_doan_tre.json`: 20 mẫu kiểm tra kèm xác suất scikit-learn (test `test_uc30_ac2_khop_sklearn`).

Chạy lại cho cùng kết quả (chỉ `ngay_train` đổi theo ngày).

## Kết quả (19/11/2026)
6880 dòng → 3783 mẫu sau lọc (train 2837, kiểm tra 946, tỷ lệ trễ 82%).
AUC 0,714; accuracy 0,852; recall 0,988 (ngưỡng 0,5). Dữ liệu Ấn Độ, chỉ là mô hình khởi đầu: train lại khi hệ thống có dữ liệu thật.
