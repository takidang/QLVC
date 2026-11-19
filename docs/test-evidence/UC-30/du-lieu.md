# Dữ liệu thử giao diện UC-30 Dự đoán nguy cơ trễ (UC-30-AC7)

> Kiệt thử 19/11/2026 (Claude chạy trên Edge, máy Kiệt). Nhánh `tai/uc-30-du-doan-tre` (cf8128b) cho cả backend và giao diện v3, CSDL `qlvc_demo` (chuyến ngày 18/11 và trước đó), mô hình `mo_hinh_tre.json` thật (ngưỡng 0,75 / 0,9).

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `dieuphoi` mở chuyến đang chạy CH-261118-03 (1440 px) | Nhãn nguy cơ trễ ở đầu chi tiết chuyến, kèm xác suất, yếu tố chính, ghi chú chỉ là gợi ý | `a-dp-chuyen-dang-chay.png` | Đạt: "Nguy cơ trễ: Trung bình · 84%", "Thời gian dự kiến ↑ · Giờ khởi hành ↓", "Gợi ý từ mô hình thử nghiệm, không thay đổi ETA · Nguồn: Kaggle … · 3.783 mẫu · AUC 0,714"; ETA và nút thao tác không đổi |
| b | `dieuphoi` mở chuyến đang lập CH-261118-06 | Có nhãn | `b-dp-chuyen-dang-lap.png` | Đạt: "Trung bình · 88%" |
| c | `dieuphoi` mở chuyến đã hủy CH-261118-07 | Không có nhãn | `c-dp-chuyen-huy.png` | Đạt: không có khối dự đoán; API trả `co_du_doan: false` |
| d | `quanly` mở CH-261118-03 | Thấy nhãn (kế thừa Điều phối) | `d-quan-ly.png` | Đạt: cùng nhãn "Trung bình · 84%" |
| e | `ketoan` gọi API và mở `/dieu-phoi/chuyen/31` | Không thấy | `e-ke-toan.png` | Đạt: API 403; trang bị đưa về `/ke-toan/tong-quan` |
| f | Màn 390 px (CH-261118-03) | Khối nằm gọn, không tràn ngang | `f-man-390.png` | Đạt: khối trong khung (37–353 / 390 px), trang không tràn ngang, chữ nguồn xuống dòng |
| g | Bản tối | Đọc rõ | `g-ban-toi.png` | Đạt: nhãn chữ cam sáng trên nền tối |
| h | Chuyến mức Thấp CH-261113-01 | Màu khác mức Trung bình | `h-muc-thap.png` | Đạt: nhãn xanh "Thấp · 72%" |

Không có lỗi trong console trình duyệt.

## Phân bố mức trên dữ liệu demo

Gọi API cho mọi chuyến (id 1–38): 29 chuyến `TRUNG_BINH` (75–90%), 6 chuyến `THAP` (72–75%), 0 chuyến `CAO`, 3 chuyến hủy không có gợi ý. Lúc demo sẽ chỉ thấy hai mức Thấp và Trung bình.

## Góp ý (không chặn AC7)
1. **"Thấp · 72%" dễ gây hiểu lầm**: xác suất trễ 72% mà gọi là "Thấp" (vì tỷ lệ trễ nền của dataset là 82%). Nên bỏ con số %, hoặc ghi rõ "so với mức trễ chung 82%".
2. **Mũi tên yếu tố** "Thời gian dự kiến ↑" dễ đọc thành "thời gian dự kiến tăng"; ý thật là "làm tăng nguy cơ". Nên ghi "Thời gian dự kiến: làm tăng nguy cơ" hoặc chú thích ↑ = tăng nguy cơ.
3. **Làm tròn tại ngưỡng**: CH-261107-02 (xác suất 0,7499) hiện "Thấp · 75%", CH-261113-03 (0,75…) hiện "Trung bình · 75%": cùng 75% nhưng khác mức.
4. Docstring `phan_muc` trong `du_doan_tre.py` còn ghi ngưỡng cũ 0,3 / 0,6.

**Kết luận: AC7 đạt.**
