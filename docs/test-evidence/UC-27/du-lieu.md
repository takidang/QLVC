# Dữ liệu thử giao diện UC-27 Bảng cảnh báo (UC-27-AC8)

> Kiệt thử 18/11/2026 (Claude chạy trên Edge 1440 px, máy Kiệt). Backend `dev` (1900ad3), giao diện v3 `tai/thu-giao-dien-v3` (7348c6c), CSDL `qlvc_demo`.

Khung "Cần chú ý" ở màn **Chuyến** lấy dữ liệu từ `GET /api/canh-bao` (`ChuyenDanhSach.tsx` gọi `canhBao()`). Dữ liệu demo không có giấy tờ sắp hết hạn, nên sửa một xe trên giao diện để có ca thử.

| Ca | Làm gì | Kết quả đúng | Ảnh | Kết quả |
|---|---|---|---|---|
| a | `quanly` → Xe → sửa 51D-307.77, hạn đăng kiểm 08/12/2026 (còn 20 ngày) → `dieuphoi` → Chuyến | Khung "Cần chú ý" có dòng giấy tờ, số ngày đúng (CFG-02 = 30) | `a-can-chu-y-cfg02-30.png` | Đạt: "51D-307.77 · đăng kiểm sắp hết hạn – Hạn 08/12/2026 · còn 20 ngày"; khung có cả chuyến trễ (CH-261118-03 Trễ 22′), sự cố (CH-261118-04), đơn thất bại, 8 đơn chờ ghép quá hạn giao; "6 việc" |
| b | `quanly` → Cấu hình → CFG-02 = 10 → Lưu | Lưu được | `b-cau-hinh-cfg02-10.png` | Đạt: "Đã lưu", ghi Quản lý Demo 14:19:43 18/11/2026 |
| c | `dieuphoi` → Chuyến | Dòng 51D-307.77 (còn 20 ngày > 10) biến mất | `c-can-chu-y-cfg02-10.png` | Đạt: còn "5 việc", không còn dòng giấy tờ → số ngày báo trước theo CFG-02 thật, không cố định 30 |

Sau khi thử: CFG-02 đổi lại 30. Hạn đăng kiểm 51D-307.77 vẫn là 08/12/2026 trên `qlvc_demo` (nạp lại CSDL demo trước buổi demo).

**Kết luận: AC8 đạt.**
