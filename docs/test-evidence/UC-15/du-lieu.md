# Dữ liệu thử giao diện UC-15 Chốt / mở chốt chuyến (UC-15-AC11)

> Tài ghi 01/11/2026, nhờ Kiệt thử. Chụp ảnh lưu vào thư mục này, tên ở cột "Ảnh"; điền cột "Kết quả" và dòng AC11 trong `docs/stories/UC-15-chot-chuyen.md`.
> Chuẩn bị: `git pull` nhánh `tai/uc-15-chot-chuyen` (hoặc `dev` sau khi gộp), chạy backend + frontend. Đăng nhập `dieuphoi` / `demo12345` (lệnh `python -m app.tai_khoan_demo`, xem `docs/cai-moi-truong.md`).
> Dùng lại dữ liệu UC-13 trên máy Kiệt (`docs/test-evidence/UC-13/du-lieu.md`): tuyến T01, xe 5.000 kg / 20 m³, đơn Đ1, Đ2, Đ4, Đ8 cho **ngày mai** (tạo đơn mới nếu đơn cũ đã qua ngày).

| Ca | Thao tác | Mong đợi | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Lập chuyến T01 ngày mai 06:00, ghép Đ1, Đ2, Đ4 → bấm **Chốt chuyến** | Không hỏi gì; nhãn đổi "Đã chốt", lãi 3.637.000 đ; phần đơn chờ ghép và nút Gỡ biến mất; hiện nút **Mở chốt** | `a-chot.png` | Đạt (3.637.000 đ, ETA 06:00 / 06:20 / 07:40 / 09:00 / 11:50 / 12:10) |
| b | Bấm **Mở chốt** | Về "Đang lập", hiện lại phần ghép/gỡ | `b-mo-chot.png` | Đạt |
| c | Lập chuyến khác (xe khác, tài xế khác) ngày mai 14:00, không ghép đơn → **Chốt chuyến** → bấm **Hủy** ở hộp xác nhận | Hộp hỏi "Chuyến chưa có đơn nào, cần xác nhận chạy rỗng (BR-23). Vẫn chốt chuyến?"; Hủy thì vẫn "Đang lập", không báo lỗi | `c-hoi-chay-rong.png` | Đạt |
| d | Bấm **Chốt chuyến** lại → **OK** | "Đã chốt", hiện "Chạy rỗng (đã xác nhận)" | – | Đạt, kiểm bằng CSDL (ảnh d bị chụp đè thành ảnh c): CH-261109-01 `DA_CHOT`, `chay_rong = true`; dùng T02 09/11 thay T01 14:00 |
| e | Chuyến ca a: mở chốt, gỡ Đ1, Đ2, ghép Đ8 (còn Đ4, Đ8) → **Chốt chuyến** | Hộp hỏi "Lãi dự kiến âm (…) (BR-52). Vẫn chốt chuyến?"; OK thì "Đã chốt" | `e-lai-am.png` | Đạt (chỉ còn Đ4, chưa ghép Đ8: lãi −800.000 đ; vẫn qua hộp xác nhận lãi âm rồi chốt) |
| f | Mở chốt chuyến ca e. Ở menu **Xe**, sửa hạn đăng kiểm xe của chuyến thành **hôm nay** → quay lại chuyến bấm **Chốt chuyến** | Bảng vi phạm: "Cả chuyến – BR-12 – … đăng kiểm …", chuyến vẫn "Đang lập". Sửa hạn lại như cũ sau khi chụp | `f-vi-pham.png` | Đạt (sửa hạn **GPLX tài xế** thay vì đăng kiểm xe → bảng vi phạm "Cả chuyến – BR-15"; đã trả hạn GPLX về 31/12/2035) |

Mở chốt khi còn tạm ứng (BR-24) chưa thử trên giao diện được vì UC-23 Tạm ứng chưa làm; đã có test tự động `test_uc15_ac7_mo_chot_va_chot_lai`.

### Kết quả (Kiệt thử 07/11/2026 trên `dev`, Claude kiểm ảnh và CSDL)

- 6/6 ca đạt trên CH-261108-01 (đã đổi sang 51C-222.22 · Tài xế Demo ở UC-12) và CH-261109-01 (chuyến rỗng). Đơn dùng: Đ1 DH-B582U9, Đ2 DH-HC63DS, Đ4 DH-PK9DZK (xem `docs/test-evidence/UC-12/du-lieu.md`).
- Lệch so với bảng: ca e chưa ghép Đ8, ca f vi phạm BR-15 thay BR-12 – cả hai vẫn đúng hành vi cần thử (hộp xác nhận lãi âm, bảng vi phạm kèm mã BR).
- Mở chốt khi còn tạm ứng (BR-24): đã thử trên giao diện ở UC-23 (nhánh `kiet/uc-23-tam-ung`, PR #17, ảnh `docs/test-evidence/UC-23/f-mo-chot-bi-chan.png`, `g-mo-chot-duoc.png`).
