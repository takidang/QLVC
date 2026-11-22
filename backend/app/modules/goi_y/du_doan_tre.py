"""Dự đoán nguy cơ trễ chuyến (UC-30): hồi quy logistic, chỉ tính bằng `math`, không đụng CSDL.

Hệ số, tham số chuẩn hóa, ngưỡng đọc từ file mô hình do `ml/` train sẵn (story UC-30, quyết định 3, 4).
Sai định dạng thì raise (KeyError, ValueError, TypeError…); service bắt và trả "không có gợi ý".
"""

import math

# Nhãn tiếng Việt của từng đặc trưng, hiện trong `yeu_to`
TEN_DAC_TRUNG = {
    "km": "Quãng đường",
    "thoi_gian_gio": "Thời gian dự kiến",
    "gio_khoi_hanh": "Giờ khởi hành",
    "thu_trong_tuan": "Thứ trong tuần",
}


def phan_muc(xac_suat: float, nguong: dict) -> str:
    """THAP < nguong["trung_binh"] ≤ TRUNG_BINH < nguong["cao"] ≤ CAO; ngưỡng đọc từ file mô hình (hiện 0,75 / 0,9)."""
    if xac_suat < nguong["trung_binh"]:
        return "THAP"
    if xac_suat < nguong["cao"]:
        return "TRUNG_BINH"
    return "CAO"


def du_doan(mo_hinh: dict, dac_trung: dict[str, float]) -> dict:
    """Trả {xac_suat, muc, yeu_to}. `dac_trung` là giá trị của chuyến theo tên đặc trưng."""
    ten = mo_hinh["dac_trung"]
    trung_binh, do_lech, he_so = mo_hinh["trung_binh"], mo_hinh["do_lech"], mo_hinh["he_so"]
    if not ten or not (len(ten) == len(trung_binh) == len(do_lech) == len(he_so)):
        raise ValueError("Độ dài các mảng trong mô hình không khớp nhau")

    dong_gop = []  # (tên, he_so_i * z_i, giá trị đầu vào)
    for i, t in enumerate(ten):
        if t not in TEN_DAC_TRUNG:
            raise ValueError(f"Đặc trưng lạ trong mô hình: {t}")
        if do_lech[i] == 0:
            raise ValueError(f"Độ lệch chuẩn của {t} bằng 0")
        gt = float(dac_trung[t])
        z = (gt - trung_binh[i]) / do_lech[i]
        dong_gop.append((t, he_so[i] * z, gt))

    logit = mo_hinh["chan"] + sum(g for _, g, _ in dong_gop)
    xac_suat = 1 / (1 + math.exp(-logit))
    if not 0 <= xac_suat <= 1:  # NaN do hệ số hỏng
        raise ValueError("Xác suất không hợp lệ")

    dong_gop.sort(key=lambda x: abs(x[1]), reverse=True)
    yeu_to = [
        {"ma": t, "ten": TEN_DAC_TRUNG[t], "huong": "TANG" if g > 0 else "GIAM", "gia_tri": gt} for t, g, gt in dong_gop
    ]
    return {"xac_suat": xac_suat, "muc": phan_muc(xac_suat, mo_hinh["nguong"]), "yeu_to": yeu_to}
