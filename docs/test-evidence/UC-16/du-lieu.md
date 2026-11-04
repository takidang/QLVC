# Dữ liệu thử giao diện UC-16 Hủy chuyến (UC-16-AC10)

> Tài ghi 04/11/2026. Đăng nhập `dieuphoi` / `demo12345`. Dùng lại dữ liệu UC-13 (`docs/test-evidence/UC-13/du-lieu.md`): tuyến T01, xe 5.000 kg, đơn Đ1, Đ4 cho **ngày mai**. Ảnh lưu vào thư mục này, điền cột "Kết quả" và dòng AC10 trong `docs/stories/UC-16-huy-chuyen.md`.

| Ca | Thao tác | Mong đợi | Ảnh | Kết quả |
|---|---|---|---|---|
| a | Lập chuyến T01 ngày mai 06:00, ghép Đ1, Đ4 → bấm **Hủy chuyến** | Hiện ô "Lý do hủy"; nút **Xác nhận hủy** mờ khi ô trống hoặc chỉ có khoảng trắng | `a-o-ly-do.png` | |
| b | Bấm **Thôi** | Ô lý do đóng, chuyến vẫn "Đang lập" | – | |
| c | Bấm **Hủy chuyến**, nhập "khách hoãn" → **Xác nhận hủy** | Nhãn "Hủy"; bảng đơn đang ghép trống; không còn nút Chốt / Hủy / ghép / gỡ / đổi xe | `c-da-huy.png` | |
| d | Mở menu **Đơn hàng** | Đ1, Đ4 về "Chờ ghép" | `d-don-cho-ghep.png` | |
| e | Lập chuyến mới cùng xe, cùng tài xế, cùng 06:00 ngày mai | Xe và tài xế hiện khả dụng (chuyến đã hủy không chiếm lịch), lập được | `e-lap-lai.png` | |
| f | Lập chuyến, ghép Đ1, **Chốt chuyến** → **Hủy chuyến** với lý do bất kỳ | Chuyến đã chốt hủy được (chưa có tạm ứng) | `f-huy-da-chot.png` | |

Hủy khi còn tạm ứng (BR-25) chưa thử trên giao diện được vì UC-23 Tạm ứng chưa làm; đã có test `test_uc16_ac4_con_tam_ung`.
