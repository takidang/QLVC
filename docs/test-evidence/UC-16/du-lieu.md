# Dữ liệu thử giao diện UC-16 Hủy chuyến (UC-16-AC10)

> Tài ghi 04/11/2026. Đăng nhập `dieuphoi` / `demo12345`. Dùng lại dữ liệu UC-13 (`docs/test-evidence/UC-13/du-lieu.md`): tuyến T01, xe 5.000 kg, đơn Đ1, Đ4 cho **ngày mai**. Ảnh lưu vào thư mục này, điền cột "Kết quả" và dòng AC10 trong `docs/stories/UC-16-huy-chuyen.md`.

| Ca | Thao tác | Mong đợi | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Lập chuyến T01 ngày mai 06:00, ghép Đ1, Đ4 → bấm **Hủy chuyến** | Hiện ô "Lý do hủy"; nút **Xác nhận hủy** mờ khi ô trống hoặc chỉ có khoảng trắng | `a-o-ly-do.png` | Đạt |
| b | Bấm **Thôi** | Ô lý do đóng, chuyến vẫn "Đang lập" | `b-thoi.png` | Đạt |
| c | Bấm **Hủy chuyến**, nhập "khách hoãn" → **Xác nhận hủy** | Nhãn "Hủy"; bảng đơn đang ghép trống; không còn nút Chốt / Hủy / ghép / gỡ / đổi xe | `c-da-huy.png` | Đạt (ảnh chụp chuyến rỗng CH-261108-02; lần hủy có đơn là CH-261108-01, kiểm bằng CSDL + ảnh d) |
| d | Mở menu **Đơn hàng** | Đ1, Đ4 về "Chờ ghép" | `d-don-cho-ghep.png` | Đạt (hủy CH-261108-01 có Đ1, Đ2, Đ4 → cả ba "Chờ ghép") |
| e | Lập chuyến mới cùng xe, cùng tài xế, cùng 06:00 ngày mai | Xe và tài xế hiện khả dụng (chuyến đã hủy không chiếm lịch), lập được | `e-lap-lai.png` | Đạt (CH-261108-03 cùng 51C-111.11, An, 06:00 08/11 sau khi CH-261108-02 hủy) |
| f | Lập chuyến, ghép Đ1, **Chốt chuyến** → **Hủy chuyến** với lý do bất kỳ | Chuyến đã chốt hủy được (chưa có tạm ứng) | `f-huy-da-chot.png` | Đạt (chuyến đã chốt hủy được, nhãn Hủy, ẩn các nút) |

Hủy khi còn tạm ứng (BR-25) chưa thử trên giao diện được vì UC-23 Tạm ứng chưa làm; đã có test `test_uc16_ac4_con_tam_ung`.

### Kết quả (Kiệt thử 07/11/2026 trên `dev`, Claude kiểm ảnh và CSDL)

- 6/6 ca đạt. Đơn dùng Đ1 DH-B582U9, Đ2 DH-HC63DS (thay Đ4 vì Đ4 đang ở chuyến UC-15), Đ4 DH-PK9DZK.
- CSDL: CH-261108-01 `DA_CHOT → HUY` lý do "khách hoãn", 3 ghép `hieu_luc = false`, Đ1, Đ2, Đ4 `CHO_GHEP`; CH-261108-02, -03, CH-261109-01 `HUY` kèm lý do ở lịch sử trạng thái.
- Hủy khi còn tạm ứng (BR-25): chưa thử trên giao diện ở đây; UC-23 đã thử mở chốt bị chặn khi còn tạm ứng (BR-24), cùng cách hiện thông báo. Test tự động `test_uc16_ac4_con_tam_ung`, `test_uc23_ac9_huy_sau_thu_hoi`.
