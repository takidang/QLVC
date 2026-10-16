# Tiến độ đồ án – Nhóm 10

> Mỗi người CHỈ sửa phần của mình. Mục chung chỉ thêm dòng, không sửa dòng người khác.
> Chi tiết từng UC: `docs/stories/`. Cập nhật sau mỗi `story done` hoặc cuối buổi, commit cùng code.
> Trạng thái: Chưa bắt đầu | Đang làm | Chờ review | Xong

## Mốc chung
| Mốc | Hạn | Trạng thái |
|---|---|---|
| Nền móng: models, migration, đăng nhập, khung frontend | 18/10 | Chưa bắt đầu |
| UC-03 mẫu + docs/mau-use-case.md | 25/10 | Chưa bắt đầu |
| Vòng tối thiểu: tạo đơn → ghép → chốt → quét → giao | 08/11 | Chưa bắt đầu |
| Quyết toán chạy được | 29/11 | Chưa bắt đầu |
| UC-30 dự đoán trễ (phần AI) | 06/12 | Chưa bắt đầu |
| Nộp LMS | 21–27/12 | |

## Đang chặn / cần người kia
<!-- Ngày – Ai cần gì từ ai. Xong thì gạch ~~...~~ -->
- ~~10/10 – Kiệt phân tích lại nghiệp vụ trên nhánh `kiet/nghiep-vu` (sửa `nghiep-vu.md`, `use-cases.md`, `so-do.md`), xong mở PR vào `main` để Tài review. Trong lúc chờ: không sửa ba file đó trên `main`; Tài làm UC-01 trước, models theo ERD chờ PR merge.~~ Xong 16/10: PR #1 đã merge, nghiệp vụ 0.5 lên `main`.
- ~~15/10 – Kiệt cần Tài review PR nghiệp vụ 0.5 (`kiet/nghiep-vu` → `main`), chốt ai làm UC-32, 33, 34 (UC-14, 31 của Tài đã bỏ), và sửa endpoint `api.md` theo danh sách trong PR.~~ Xong 16/10: đã review, Kiệt làm UC-33, 34; Tài làm UC-32.
- 16/10 – Tài → Kiệt: nghiệp vụ 0.5 đã merge. Việc tuần 1 của Kiệt có hướng dẫn: cài môi trường `docs/cai-moi-truong.md`, ca test BR `docs/ca-test-br.md` (khung + ví dụ + BR còn thiếu ca), UML `docs/uml/README.md`.

## Câu hỏi chờ thầy
- ~~A1–A6 (nghiep-vu.md mục 1): chưa gửi~~ Nhóm tự chốt 16/10 (nghiep-vu.md mục 1).
- ~~A7 (tuyến ≤ 10 giờ), A8 (góc nhìn chủ xe): chưa gửi~~ Nhóm tự chốt 16/10.

## Tài
| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Nền móng (gồm UC-01 Đăng nhập) | 1 | Đang làm | – | Khung repo + CI xong (e2b0701); nghiệp vụ 0.5 đã merge; còn models theo ERD mới, migration, UC-01 – máy chưa cài Docker Desktop |
| UC-03 Xe (mẫu) | 2 | Chưa bắt đầu | | |
| UC-06…09 Đơn tối thiểu | 3–4 | Chưa bắt đầu | | |
| UC-11…13, 15 Chuyến tối thiểu | 3–4 | Chưa bắt đầu | | |
| UC-10, 16, 22, 32 (theo dõi chuyến) + làm dày UC-13, 15 | 5–6 | Chưa bắt đầu | | |
| UC-28, triển khai demo | 7 | Chưa bắt đầu | | |
| UC-30 AI | 8 | Chưa bắt đầu | | |

### Nhật ký Tài (mới nhất ở trên)
- 16/10: Review và merge PR #1 nghiệp vụ 0.5 của Kiệt (sửa thêm cước Đ8, quy ước thứ tự route). Nhận UC-32; bỏ UC-14, 31.
- 10/10: Chốt nghiệp vụ 0.4, sơ đồ, kiến trúc, API; dựng khung repo, CI xanh lần đầu.

## Kiệt
| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Phân tích lại nghiệp vụ 0.5 (nhánh `kiet/nghiep-vu`) | 1 | Chờ review | – | Đã sửa theo review của Tài (6 mục + 3 góp ý) và bổ sung công thức, ETA kế hoạch, dữ liệu cho AI; chờ Tài kiểm lại rồi merge |
| Cài môi trường, danh sách ca test BR, vẽ UML | 1 | Đang làm | – | Có Python 3.12; thiếu WSL 2, Docker Desktop, Node 24. Ca test BR và UML làm sau khi PR merge |
| UC-04 Tài xế (chép mẫu) | 2 | Chưa bắt đầu | | |
| UC-02, 05 + Quét tối thiểu (UC-17…20) | 3–4 | Chưa bắt đầu | | |
| Quét đầy đủ, UC-21, 23, 33 (báo sự cố) | 5–6 | Chưa bắt đầu | | |
| UC-24, 25 | 7 | Chưa bắt đầu | | |
| UC-26, 27, 34 (hiệu suất xe, ưu tiên S – thiếu giờ thì cắt trước), E2E | 8 | Chưa bắt đầu | | |

### Nhật ký Kiệt (mới nhất ở trên)
- 15/10: Sửa nghiệp vụ 0.5 theo review của Tài: công thức BR-73, km khi kết thúc do sự cố, thứ tự điểm lấy, kịch bản mỗi ca ✖ chỉ một BR (thêm Đ8 cho BR-67); thêm mục Công thức, ETA kế hoạch lưu lúc chốt, dữ liệu cho AI; api, security-rules, kien-truc khớp 0.5. Nhận UC-33, UC-34.
- 15/10: Nghiệp vụ 0.5: chuyến 6 trạng thái, đơn 7; ETA cộng phút dừng, kiểm lại cả chuyến khi ghép (BR-63…67); km, sự cố, kết thúc do sự cố, cảnh báo trễ (BR-68…73); bỏ UC-09, 14, 29, 31, thêm UC-32…34. Sửa nghiep-vu, use-cases, so-do; api, security-rules chỉ đổi tên trạng thái. Mở PR chờ Tài review.
