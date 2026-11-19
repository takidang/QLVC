"""Train mô hình dự đoán nguy cơ trễ chuyến (UC-30-AC1).

Chạy từ gốc repo:  ml\\.venv\\Scripts\\python ml\\train_du_doan_tre.py [đường_dẫn_excel]

Đọc dataset Kaggle "Delivery truck trips data", train hồi quy logistic trên 4 đặc trưng mà cả dataset
và hệ thống đều có, rồi xuất:
- backend/app/modules/goi_y/mo_hinh_tre.json: hệ số, tham số chuẩn hóa, ngưỡng, nguồn
  (định dạng đọc bởi backend/app/modules/goi_y/du_doan_tre.py);
- backend/tests/du_lieu/mau_du_doan_tre.json: 20 mẫu đầu của tập kiểm tra kèm xác suất scikit-learn (test AC2).

Dataset có tên và số điện thoại tài xế: script chỉ đọc đúng các cột cần dùng, không in dữ liệu cá nhân.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

GOC_REPO = Path(__file__).resolve().parent.parent
DATASET_MAC_DINH = GOC_REPO / "ml" / "data" / "Delivery truck trip data.xlsx"
FILE_MO_HINH = GOC_REPO / "backend" / "app" / "modules" / "goi_y" / "mo_hinh_tre.json"
FILE_MAU = GOC_REPO / "backend" / "tests" / "du_lieu" / "mau_du_doan_tre.json"

# Chỉ đọc các cột này (không đọc cột tên, số điện thoại tài xế)
COT_DUNG = ["BookingID_Date", "trip_start_date", "Planned_ETA", "TRANSPORTATION_DISTANCE_IN_KM", "ontime", "delay"]
# Đúng thứ tự đặc trưng của module backend (TEN_DAC_TRUNG trong du_doan_tre.py)
DAC_TRUNG = ["km", "thoi_gian_gio", "gio_khoi_hanh", "thu_trong_tuan"]
NGUONG = {"trung_binh": 0.75, "cao": 0.9}  # theo tỷ lệ trễ nền 82% của dataset (Tài chốt 19/11)
TEN_DATASET = "Kaggle ramakrishnanthiyagu/delivery-truck-trips-data"
SEED = 42
SO_MAU_XUAT = 20


def doc_va_lam_sach(duong_dan: Path) -> pd.DataFrame:
    """Trả DataFrame gồm 4 cột đặc trưng + cột `nhan` (1 = trễ, 0 = đúng giờ); in số dòng bỏ ở từng bước."""
    d = pd.read_excel(duong_dan, usecols=COT_DUNG)
    print(f"Đọc: {len(d)} dòng")

    for cot in ("BookingID_Date", "trip_start_date", "Planned_ETA"):
        d[cot] = pd.to_datetime(d[cot], errors="coerce")

    # Nhãn: delay == "R" → 1; ontime == "G" → 0; bỏ dòng có cả hai hoặc không có cái nào
    tre = d["delay"].eq("R")
    dung_gio = d["ontime"].eq("G")
    giu = tre ^ dung_gio
    print(f"Bỏ (nhãn mâu thuẫn hoặc không có nhãn): {int((~giu).sum())}")
    d = d[giu].copy()
    d["nhan"] = tre[giu].astype(int)

    d["km"] = d["TRANSPORTATION_DISTANCE_IN_KM"]
    d["thoi_gian_gio"] = (d["Planned_ETA"] - d["trip_start_date"]).dt.total_seconds() / 3600
    d["gio_khoi_hanh"] = d["trip_start_date"].dt.hour
    d["thu_trong_tuan"] = d["trip_start_date"].dt.day_of_week  # Thứ Hai = 0 (như datetime.weekday())

    def loc(dk: pd.Series, ly_do: str) -> None:
        nonlocal d
        print(f"Bỏ ({ly_do}): {int((~dk).sum())}")
        d = d[dk]

    loc(d[["BookingID_Date", "trip_start_date", "Planned_ETA", "km"]].notna().all(axis=1), "thiếu giá trị")
    loc(d["km"] > 0, "km <= 0")
    loc((d["thoi_gian_gio"] > 0) & (d["thoi_gian_gio"] <= 240), "thoi_gian_gio <= 0 hoặc > 240")
    # ETA mặc định của hệ thống nguồn: đúng 100 giờ sau lúc đặt, không phản ánh kế hoạch thật
    lech_100_gio = (d["Planned_ETA"] - d["BookingID_Date"] - pd.Timedelta(hours=100)).abs()
    loc(lech_100_gio >= pd.Timedelta(minutes=1), "ETA mặc định = đặt + 100 giờ")

    print(f"Còn lại: {len(d)} mẫu")
    return d[DAC_TRUNG + ["nhan"]].astype(float).astype({"nhan": int}).reset_index(drop=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Train mô hình dự đoán nguy cơ trễ chuyến (UC-30)")
    p.add_argument("dataset", nargs="?", type=Path, default=DATASET_MAC_DINH, help="File Excel dataset")
    args = p.parse_args()

    d = doc_va_lam_sach(args.dataset)
    X, y = d[DAC_TRUNG], d["nhan"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=SEED, stratify=y)

    scaler = StandardScaler().fit(X_train)
    mo_hinh = LogisticRegression(max_iter=1000).fit(scaler.transform(X_train), y_train)

    xs_test = mo_hinh.predict_proba(scaler.transform(X_test))[:, 1]
    du_doan = (xs_test >= 0.5).astype(int)
    auc = roc_auc_score(y_test, xs_test)
    print(f"Train: {len(X_train)} mẫu, kiểm tra: {len(X_test)} mẫu")
    print(f"Tỷ lệ trễ: train {y_train.mean():.3f}, kiểm tra {y_test.mean():.3f}")
    print(f"AUC: {auc:.4f}")
    print(f"Accuracy (ngưỡng 0,5): {accuracy_score(y_test, du_doan):.4f}")
    print(f"Recall (ngưỡng 0,5): {recall_score(y_test, du_doan):.4f}")
    for ten, hs in zip(DAC_TRUNG, mo_hinh.coef_[0], strict=True):
        print(f"Hệ số {ten}: {hs:+.4f}")
    print(f"Chặn: {mo_hinh.intercept_[0]:+.4f}")

    ket_qua = {
        "dac_trung": DAC_TRUNG,
        "trung_binh": [float(v) for v in scaler.mean_],
        "do_lech": [float(v) for v in scaler.scale_],
        "he_so": [float(v) for v in mo_hinh.coef_[0]],
        "chan": float(mo_hinh.intercept_[0]),
        "nguong": NGUONG,
        "nguon": {
            "dataset": TEN_DATASET,
            "ngay_train": date.today().isoformat(),
            "so_mau": len(d),
            "auc": round(float(auc), 3),
        },
    }
    FILE_MO_HINH.write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã ghi {FILE_MO_HINH.relative_to(GOC_REPO)}")

    # 20 mẫu đầu tập kiểm tra: chỉ 4 đặc trưng + xác suất scikit-learn, không cột nào khác của dataset
    mau = [
        {"dac_trung": {t: float(X_test.iloc[i][t]) for t in DAC_TRUNG}, "xac_suat_sklearn": float(xs_test[i])}
        for i in range(SO_MAU_XUAT)
    ]
    FILE_MAU.parent.mkdir(parents=True, exist_ok=True)
    FILE_MAU.write_text(json.dumps(mau, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã ghi {FILE_MAU.relative_to(GOC_REPO)}")


if __name__ == "__main__":
    main()
