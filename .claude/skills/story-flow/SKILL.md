---
name: story-flow
description: "Dùng khi làm một use case của đồ án vận tải từ đầu đến cuối: tạo story có tiêu chí chấp nhận, code kèm test, kiểm từng tiêu chí bằng bằng chứng thật, đóng story, hoặc xuất bảng truy vết cho báo cáo kiểm thử. Lệnh: story new | dev | done | report."
---

# Story Flow: use case → code → test → bằng chứng

> **Nguồn:** rút gọn từ `dev-story`, `story-done`, `test-evidence-review` của
> https://github.com/Donchitos/Claude-Code-Game-Studios (MIT, Copyright (c) 2026 Donchitos),
> commit `be8993b` (2026-10-08). Bỏ phần game, agent, sprint, gate. Không phải bản chính thức.

Một use case = một story = một file `docs/stories/UC-xx-<ten-ngan>.md`, theo mẫu `templates/story.md` trong thư mục skill này. Chuỗi truy vết bắt buộc: **Use case → Tiêu chí chấp nhận (AC) → Test case (TC) → Bằng chứng**. Đây là nguồn cho chương kiểm thử của báo cáo.

## Lệnh

### `story new UC-xx`
1. Đọc đặc tả use case và quy tắc nghiệp vụ trong `docs/`. Thiếu đặc tả thì dừng, hỏi Tai, không tự bịa nghiệp vụ.
2. Tạo file story từ mẫu. Mỗi AC phải kiểm được, có mã `UC-xx-ACn`, ghi rõ quy tắc nghiệp vụ liên quan (vd `BR-03 tải trọng`).
3. AC có con số hoặc điều kiện ("không vượt tải trọng", "khung giờ") phải kèm ca biên: đúng bằng giới hạn, vượt 1 đơn vị, bằng 0 hoặc rỗng.
4. Gán **loại** cho từng AC (bảng dưới). Trình Tai duyệt danh sách AC trước khi code.

### `story dev UC-xx`
1. Đọc story, đặc tả, `docs/security-rules.md`, phần kiến trúc liên quan. Story chưa được duyệt thì dừng.
2. Code theo skill `ponytail` (thay đổi nhỏ nhất, giữ kiến trúc phân lớp đã chốt).
3. Viết test **cùng lúc** với code, mỗi AC loại Logic/API ít nhất một test. Tên test chứa mã AC, vd `test_uc03_ac2_vuot_tai_trong_bi_tu_choi`.
4. **Chạy test thật** và ghi kết quả. Không ghi "đạt" khi chưa chạy.
5. Code lệch đặc tả (thêm trạng thái, đổi trường) thì dừng, hỏi Tai, rồi sửa `docs/` trong cùng commit.
6. Cập nhật mục "Ghi chú triển khai" trong story: file đã đổi, test đã viết, kết quả chạy.

### `story done UC-xx`
Kiểm từng AC, không suy từ việc đọc code:
- **Tự động:** chạy test của AC. Đạt khi test chạy qua **và** có assert thật (test không assert gì là FAIL vì nó đạt vô nghĩa).
- **Hỏi người dùng máy** (ghi trong `CLAUDE.local.md`; gộp tối đa 4 câu một lần) cho AC về hành vi trên giao diện hoặc trải nghiệm: "Đạt / Không đạt / Chưa thử". Chưa thử → `CHƯA KIỂM`.
- **UI:** cần ảnh chụp thật từng màn hình bị đổi, lưu ở `docs/test-evidence/UC-xx/` (chụp bằng `webapp-testing`).

Sau đó:
1. Điền bảng truy vết trong story: `AC | Loại | Test/Bằng chứng | Kết quả | Ngày`.
2. Có AC `FAIL` hoặc `CHƯA KIỂM` → story **chưa xong**, nói rõ thiếu gì. Không tự đánh dấu xong.
3. Nhắc chạy `ponytail-review` trên thay đổi của story.
4. Tất cả đạt → `Trạng thái: Hoàn thành`, ghi ngày. Gợi ý story tiếp theo theo thứ tự trong `docs/stories/`.
5. Cập nhật `docs/TIEN-DO.md` theo CLAUDE.md (mục "Làm việc hai người"), kể cả khi story chưa xong.

### `story report`
Gom bảng truy vết của mọi story thành `docs/test-report.md`: số AC, đạt / không đạt / chưa kiểm theo từng use case, danh sách lỗi còn mở. Chỉ lấy số liệu từ các story, không ước lượng.

## Loại tiêu chí và bằng chứng bắt buộc

| Loại | Ví dụ trong đề tài | Bằng chứng | Thiếu thì |
|---|---|---|---|
| **Logic** | Quy tắc ghép đơn, tính cước `max(kg, thể tích quy đổi)`, lãi chuyến, chuyển trạng thái Chuyến/Đơn | Unit test (pytest) | Chặn đóng story |
| **API** | Endpoint ghép đơn, quét mã, phân quyền theo vai trò | Test gọi API (pytest + client test của FastAPI), có ca sai quyền | Chặn đóng story |
| **UI** | Màn điều phối, màn tài xế quét QR | Ảnh chụp trong `docs/test-evidence/UC-xx/` + Tai xác nhận | Chặn đóng story |
| **Dữ liệu** | Seed dữ liệu mẫu, cấu hình | Chạy thử một lần, ghi kết quả | Chỉ ghi chú |

## Luật

- Mọi quy tắc nghiệp vụ trong `docs/` phải có ít nhất một AC và một test. Ghi đè mức "một test nhỏ" của ponytail.
- Mỗi AC phân quyền phải có ca **bị từ chối** (sai vai trò, không phải chủ sở hữu).
- Không xoá hay nới AC để story "đạt". Muốn đổi AC thì hỏi Tai và ghi lý do trong story.
- Báo cáo ngắn: AC nào đạt, AC nào chưa và thiếu gì, lệnh để chạy lại test.
