# Nghiệp vụ (bản nháp, chờ thầy góp ý)

Nguồn sự thật về nghiệp vụ cho code và tài liệu. Sửa ở đây trước, rồi chép sang Project instructions trên claude.ai để hai nơi không lệch nhau.

## Đề tài (thầy giao)
"Hệ thống quản lý vận tải cho một doanh nghiệp vận tải hàng hóa nhỏ: CHUYẾN XE LÀ TRUNG TÂM, ĐƠN HÀNG LÀ THỨ ĐƯỢC GHÉP VÀO CHUYẾN."

## Khái niệm
- **Chuyến** = xe + tài xế + tuyến + giờ chạy + danh sách đơn + điểm dừng (thứ tự lấy/giao) + chi phí + lãi lỗ.
- **Đơn hàng** = khách + hàng hóa (kg, m³) + điểm lấy + điểm giao + cước. Mỗi đơn chỉ thuộc 1 chuyến tại một thời điểm.

## Vòng đời
- **Chuyến:** Lên kế hoạch → Ghép đơn → Đã chốt → Đang bốc hàng → Đang chạy → Hoàn thành → Đã quyết toán (hoặc Hủy).
- **Đơn:** Mới → Chờ ghép → Đã ghép chuyến → Đã lấy hàng → Đã giao (giao thất bại thì quay về Chờ ghép hoặc hoàn hàng) → Ghi công nợ.

## Quy tắc nghiệp vụ
- Ghép đơn: không vượt tải trọng và thể tích xe, nằm trên tuyến, khớp khung giờ, không tách 1 đơn ra nhiều chuyến.
- Xe hết đăng kiểm/bảo hiểm hoặc tài xế sai hạng bằng lái thì không được xếp; xe và tài xế không trùng giờ.
- Tài xế quét mã từng đơn khi bốc và khi giao; hệ thống ghi giờ và GPS lúc quét; chụp ảnh, lấy chữ ký.
- Cước tính theo khối lượng tính cước = max(kg thật, thể tích quy đổi).
- Lãi chuyến = tổng cước − (dầu + cầu đường + bốc xếp + lương tài xế + phát sinh). Có tạm ứng cho tài xế và quyết toán sau chuyến.

## Tác nhân
Quản lý, Điều phối viên, Tài xế, Kế toán, Khách hàng (chỉ tra cứu đơn).

## Câu hỏi chờ thầy (chưa chốt, code theo giả thiết ghi rõ)
- Lấy hàng tận nơi hay khách mang hàng đến kho?
- Có xe thuê ngoài không?
- Nội thành, liên tỉnh hay cả hai?
- Khách có tự tạo đơn không?

## Module phụ trợ (làm sau cùng)
- Gợi ý ghép đơn vào chuyến và thứ tự điểm dừng: thuật toán tối ưu (OR-Tools).
- AI dự đoán nguy cơ trễ của chuyến, train trên dataset công khai (Kaggle "Delivery Truck Trips Data" – cần kiểm tra), train lại bằng giờ thực tế từ các lần quét mã.

## Nền tảng (đề xuất, chưa chốt)
- Web cho điều phối, kế toán, quản lý; web responsive cho tài xế trên điện thoại (quét QR bằng camera, lấy GPS lúc quét). Không làm GPS theo dõi liên tục.
- FastAPI (Python) + React + PostgreSQL; bản đồ Leaflet + OpenStreetMap.
