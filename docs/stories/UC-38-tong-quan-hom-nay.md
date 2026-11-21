# UC-38: Tổng quan hôm nay

- **Trạng thái:** Hoàn thành 12/11/2026 – 6/6 AC đạt (Đã duyệt 12/11/2026 – Tài: "ok làm theo kế hoạch", tiêu chí như đề xuất 12/11)
- **Tác nhân:** Quản lý, Điều phối, Kế toán
- **Đặc tả:** chưa có trong `docs/use-cases.md` (UC mới, hàng số liệu đầu trang Tổng quan của giao diện v2, mục B1 trong ghi chú của phiên giao diện); `docs/api.md` mục 2.7
- **Quy tắc nghiệp vụ liên quan:** BR-57, BR-73 (độ trễ), CFG-09
- **Người làm:** Tài (backend); giao diện do phiên giao diện v2 làm

## Mô tả ngắn
Số liệu một ngày cho trang đầu: chuyến theo trạng thái, đơn đã giao / thất bại / còn lại, tỉ lệ điểm đúng giờ, doanh thu dự kiến. Chỉ đọc, tính lại mỗi lần, không thêm bảng.

## Quyết định (Tài duyệt 12/11/2026)
1. `GET /api/tong-quan?ngay=YYYY-MM-DD` (mặc định hôm nay theo giờ Việt Nam). "Chuyến của ngày" là chuyến có khởi hành dự kiến trong ngày đó, giờ Việt Nam (như bảng chuyến trong ngày UC-32).
2. Đơn của chuyến tính như UC-32: ghép còn hiệu lực hoặc đã có kết quả; **không tính chuyến hủy**. "Đã giao", "thất bại" theo kết quả ghi trên chính chuyến này (`Ghep.ket_qua`), nên đơn thất bại sau đó được ghép lại vẫn tính thất bại của chuyến này.
3. "Đúng giờ" = điểm đã có lượt quét có độ trễ **không quá** ngưỡng CFG-09 (đúng bằng ngưỡng vẫn đúng giờ, sớm là đúng giờ); tỉ lệ = đúng giờ / số điểm đã quét. Chưa quét điểm nào thì `ty_le` là `null`.
4. Doanh thu dự kiến = tổng cước của mọi đơn của các chuyến không hủy (kể cả đơn thất bại, vì là dự kiến; số thực nằm ở quyết toán UC-24, báo cáo UC-26).

## Tiêu chí chấp nhận

| Mã | Tiêu chí (kiểm được) | Loại | Quy tắc |
|---|---|---|---|
| UC-38-AC1 | `chuyen.theo_trang_thai` luôn đủ 6 khóa (`LAP`, `DA_CHOT`, `DANG_CHAY`, `HOAN_THANH`, `DA_QUYET_TOAN`, `HUY`), `chuyen.tong` là tổng; chỉ chuyến khởi hành trong ngày (biên: 00:00 hôm đó tính, 00:00 hôm sau không) | API | — |
| UC-38-AC2 | `don`: `tong`, `da_giao`, `that_bai`, `con_lai` = tổng − giao − thất bại, `kg_da_cho` là tổng kg đơn đã giao; không tính chuyến hủy, đơn đã gỡ khỏi chuyến | API | BR-36 |
| UC-38-AC3 | `dung_gio`: `nguong_tre_phut` (CFG-09), `da_quet`, `dung_gio`, `ty_le`; biên đúng bằng ngưỡng là đúng giờ, ngưỡng + 1 là trễ, quét sớm là đúng giờ; chưa quét → `ty_le` `null` | API | BR-73 |
| UC-38-AC4 | `doanh_thu_du_kien`: tổng cước đơn của chuyến không hủy, gồm đơn thất bại; không gồm đơn đã gỡ | API | — |
| UC-38-AC5 | Quản lý, Điều phối, Kế toán xem được; Tài xế 403; chưa đăng nhập 401; ngày sai định dạng hoặc tham số lạ 400; bỏ trống `ngay` thì là hôm nay | API | BR-57 |
| UC-38-AC6 | Giao diện: hàng số liệu đầu trang Tổng quan (phiên giao diện v2) | UI | NFR-USA-02 |

## Ghi chú triển khai
- File đã đổi: `backend/app/modules/tong_quan/{router,service}.py` (mới; dùng lại `theo_doi._ghep`, `_diem` của UC-32), `backend/app/main.py` (đăng ký router theo chữ cái), `docs/api.md` mục 2.7.
- Test đã viết: `backend/tests/api/test_uc38_tong_quan.py` (17 ca). Thử làm hỏng 7 chỗ (biên ngưỡng lệch, tính cả chuyến hủy, biên ngày lệch, đếm giao theo trạng thái đơn, doanh thu bỏ đơn thất bại, tỉ lệ chưa quét là 0, ngày theo UTC thay giờ VN) → test đỏ đúng chỗ. Hai lần đầu chưa bắt được (test dùng ghép đã gỡ nên quy tắc "không tính chuyến hủy" chưa bị chạm; một lệnh thử sai) nên đã sửa test và thử lại.
- Lệnh chạy test: `cd backend; .venv\Scripts\python -m pytest tests/api/test_uc38_tong_quan.py`
- Lệch đặc tả: không (UC mới, ghi `api.md`). Mỗi chuyến trong ngày vài truy vấn, đủ cho một ngày của đội nhỏ.

## Truy vết và kết quả

| AC | Loại | Test / Bằng chứng | Kết quả | Ngày |
|---|---|---|---|---|
| UC-38-AC1 | API | `test_uc38_ac1_*` (2 ca) | Đạt | 12/11/2026 |
| UC-38-AC2 | API | `test_uc38_ac2_*` (2 ca) | Đạt | 12/11/2026 |
| UC-38-AC3 | API | `test_uc38_ac3_*` (2 ca) | Đạt | 12/11/2026 |
| UC-38-AC4 | API | `test_uc38_ac4_doanh_thu` | Đạt | 12/11/2026 |
| UC-38-AC5 | API | `test_uc38_ac5_*` (10 ca) | Đạt | 12/11/2026 |
| UC-38-AC6 | UI | Khối Hôm nay trang Tổng quan Quản lý, Kế toán: Kiệt thử 12/11, ảnh `docs/test-evidence/UC-38/a-…`, `b-…` (PR #55) | Đạt | 12/11/2026 |
