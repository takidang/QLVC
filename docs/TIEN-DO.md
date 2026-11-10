# Tiến độ đồ án – Nhóm 8

> Mỗi người CHỈ sửa phần của mình. Mục chung chỉ thêm dòng, không sửa dòng người khác.
> Chi tiết từng UC: `docs/stories/`. Cập nhật sau mỗi `story done` hoặc cuối buổi, commit cùng code.
> Trạng thái: Chưa bắt đầu | Đang làm | Chờ review | Xong

## Mốc chung
| Mốc | Hạn | Trạng thái |
|---|---|---|
| Nền móng: models, migration, đăng nhập, khung frontend | 18/10 | Xong 16/10 |
| UC-03 mẫu + docs/mau-use-case.md | 25/10 | Xong 24/10 |
| Vòng tối thiểu: tạo đơn → ghép → chốt → quét → giao | 08/11 | Xong 08/11 (gộp UC-20, PR #16) |
| Quyết toán chạy được | 29/11 | Xong 10/11 (gộp UC-24, PR #33) |
| UC-30 dự đoán trễ (phần AI) | 06/12 | Chưa bắt đầu |
| Nộp LMS | 21–27/12 | |

## Đang chặn / cần người kia
<!-- Ngày – Ai cần gì từ ai. Xong thì gạch ~~...~~ -->
- ~~10/10 – Kiệt phân tích lại nghiệp vụ trên nhánh `kiet/nghiep-vu` (sửa `nghiep-vu.md`, `use-cases.md`, `so-do.md`), xong mở PR vào `main` để Tài review. Trong lúc chờ: không sửa ba file đó trên `main`; Tài làm UC-01 trước, models theo ERD chờ PR merge.~~ Xong 16/10: PR #1 đã merge, nghiệp vụ 0.5 lên `main`.
- ~~15/10 – Kiệt cần Tài review PR nghiệp vụ 0.5 (`kiet/nghiep-vu` → `main`), chốt ai làm UC-32, 33, 34 (UC-14, 31 của Tài đã bỏ), và sửa endpoint `api.md` theo danh sách trong PR.~~ Xong 16/10: đã review, Kiệt làm UC-33, 34; Tài làm UC-32.
- 16/10 – Tài → Kiệt: nghiệp vụ 0.5 đã merge. Việc tuần 1 của Kiệt có hướng dẫn: cài môi trường `docs/cai-moi-truong.md`, ca test BR `docs/ca-test-br.md` (khung + ví dụ + BR còn thiếu ca), UML `docs/uml/README.md`.
- ~~16/10 – Tài đang tạo **toàn bộ models theo ERD 0.5 + migration đầu tiên** (`backend/app/models/`, `backend/alembic/`). Kiệt chưa sửa hai thư mục này tới khi dòng này được gạch; cần thêm cột/bảng thì nhắn Tài.~~ Xong 16/10: 24 bảng + migration đầu đã lên `main`. Sửa models thì tạo migration mới (`alembic revision --autogenerate`), CI chạy `alembic check`.
- 24/10 – Tài → Kiệt: UC-03 xong, làm UC-04 theo `docs/mau-use-case.md` (chép cấu trúc `backend/app/modules/danh_muc/xe/`, fixture `dang_nhap_voi`, trang `XeDanhSach.tsx`). Tuần 2 Kiệt chưa có commit nào: nhắn Tài nếu vướng cài môi trường.
- ~~24/10 – Tài đang sửa `backend/app/models/danh_muc.py` (bảng giá) và thêm migration thứ 2 (UC-07: unique cặp tỉnh + ngày hiệu lực, nạp CFG mặc định). Kiệt chưa thêm migration tới khi dòng này được gạch.~~ Xong 24/10: migration `177fdcb334df`. Kiệt `git pull` rồi `alembic upgrade head`.
- 24/10 – **Tài nhận UC-05 Tuyến và nút** (trước là của Kiệt) vì UC-05 chặn giao diện tạo đơn và toàn bộ phần chuyến. Kiệt **không làm UC-05**; Kiệt sửa dòng "UC-02, 05 + Quét tối thiểu" trong phần mình thành "UC-02 + Quét tối thiểu". Kiệt vẫn làm UC-04 Tài xế (UC-11 cần tài xế).
- 24/10 – Tài → Kiệt: trên `main` đã có UC-01, 03, 06, 07 xong và UC-08 backend (167 test). Kiệt `git pull`, `alembic upgrade head` (có migration mới), đọc `docs/mau-use-case.md` (đã thêm lưu ý `app/kieu.py`, giờ Việt Nam) rồi làm **UC-04 Tài xế** – UC-11 Lập chuyến đang chờ UC-04.
- 24/10 – Tài → Kiệt: **thử giao diện UC-05 và UC-08** thay Tài (bước 3 trong khối "Việc của Kiệt ngay bây giờ"). Code đã xong, chờ Kiệt chụp ảnh và xác nhận để đóng 2 story.
- 25/10 – Kiệt → Tài: (1) review PR UC-04 (`kiet/uc-04` → `main`); hàm `kiem_br14_hang_gplx` trong `domain/xe_tai_xe.py` dùng cho UC-11, 12; UC-11, 12 cần lọc bỏ tài xế `NGUNG`. (2) Đã thử UC-05-AC9, UC-08-AC11: đạt, Tài xác nhận và đóng story. (3) Hai điểm nhỏ khi thử: `http://127.0.0.1:5173` không mở được trên máy Kiệt (Vite chỉ nghe `localhost`), phải dùng `http://localhost:5173`; thông báo lỗi BR-66 (tuyến) và BR-31 (đơn) trên giao diện chưa hiện mã BR như NFR-USA-02 – Tài quyết có sửa không.
- 25/10 – Tài → Kiệt: UC-04 đã review và merge vào `main` (sửa nhỏ: gộp validator GPLX, bỏ ảnh `5-tai-xe-bi-khoa-tk.png` trùng ảnh 4). UC-05, UC-08 đóng theo ảnh Kiệt thử. Đã sửa 2 điểm Kiệt báo: lỗi nghiệp vụ hiện kèm mã BR; Vite nghe `127.0.0.1` nên `http://127.0.0.1:5173` mở được trên mọi máy. Kiệt `git switch main`, `git pull`. Nhánh `dev` đã tạo; cách chia nhánh Tài và Kiệt bàn sau.
- 29/10 – Kiệt → Tài: đọc lại `docs/ca-test-br.md` và chốt 5 câu ở mục 5 (khung giờ lấy đóng hai đầu; tuần tính giờ lái Thứ Hai–Chủ Nhật; "hết hạn trong 30 ngày" gồm ngày thứ 30; cước tối thiểu 50.000 cho kịch bản mục 11; mã 422 khi hủy/trả hàng đơn `THAT_BAI` sai điều kiện lượt quét).
- 30/10 – Tài → Kiệt: đồng ý cả 5 đề xuất ở `ca-test-br.md` mục 5, đã ghi vào `nghiep-vu.md` (BR-05 khung đóng hai đầu, BR-19 tuần Thứ Hai–Chủ Nhật, BR-21 gồm ngày thứ 30, cước tối thiểu 50.000 ở mục 11, ghi chú 422 cho BR-34/36). Ca test BR đã chốt.
- 30/10 – Tài → Kiệt: **thử giao diện UC-11 Lập chuyến** (`UC-11-AC12`; backend xong, 315 test). `git pull`, chạy backend + frontend như lần thử UC-05. Dùng dữ liệu đã có trên máy Kiệt (tuyến T01, xe, tài xế An hạng C, Bình hạng B); cần thêm 1 xe khối lượng toàn bộ 9.500 kg và 1 xe trạng thái Ngừng nếu chưa có. Menu **Chuyến** → Lập chuyến: (a) T01, ngày mai 06:00 → hiện danh sách xe và tài xế; xe Ngừng hiện "không dùng được" kèm lý do (BR-11); (b) chọn xe 9.500 kg → Bình mờ, lý do hạng GPLX (BR-14); (c) chọn An → Lập chuyến → "Đã lập chuyến CH-yyMMdd-01", kết thúc dự kiến 11:30; (d) lập chuyến khác cùng xe lúc 10:00 → xe đó mờ, lý do trùng lịch chuyến vừa lập (BR-16); (e) chọn giờ hôm qua → Lập chuyến báo "Giờ khởi hành đã qua". Chụp (a)…(e) vào `docs/test-evidence/UC-11/`, điền dòng AC12 trong `docs/stories/UC-11-lap-chuyen.md` (Đạt/Không đạt, ngày, "Kiệt thử"); sai chỗ nào ghi vào "Đang chặn", không tự sửa code của Tài.
- 30/10 – Tài → Kiệt: **thử giao diện UC-13 Ghép đơn** (`UC-13-AC13`), làm sau khi thử UC-11. Cần thêm dữ liệu: bảng giá `Long An → Cần Thơ` 1.200 và `TP.HCM → Tiền Giang` 1.000 (tối thiểu 50.000); xe tải 5.000 kg, thể tích 20 m³; 4 đơn cho **ngày mai**: Đ1 TP.HCM → Cần Thơ 1.800 kg 6 m³ hạn 14:00; Đ2 Long An → Cần Thơ 1.200 kg 3 m³, lấy 06:30–09:00, hạn 12:00; Đ4 TP.HCM → Tiền Giang 800 kg 2 m³ hạn 18:00; Đ8 TP.HCM → Tiền Giang 300 kg 1 m³ hạn 18:00. Lập chuyến T01 ngày mai 06:00 với xe đó, bấm **mã chuyến** để mở trang chi tiết: (a) chưa có đơn: lịch trình trống, lãi dự kiến âm tô đỏ; (b) chọn Đ1, Đ4 → Ghép → lịch trình 4 điểm; (c) ghép Đ2 → 6 điểm, ETA 06:00 / 06:20 / 07:40 / 09:00 / 11:50 (giao Đ2) / 12:10 (giao Đ1), tải 3.800 / 5.000 kg, lấp đầy 76%, lãi 3.637.000 đ; (d) ghép Đ8 → bảng vi phạm: đơn Đ2, BR-06, ETA giao 12:30 sau hạn 12:00, Đ8 không được ghép; (e) chọn Đ4 ở bảng đơn đang ghép → Gỡ → lịch trình còn 4 điểm, Đ4 về danh sách chờ ghép. Chụp (a)…(e) vào `docs/test-evidence/UC-13/`, điền dòng AC13 trong `docs/stories/UC-13-ghep-don.md`.
- 30/10 – **Nhóm chốt quy trình nhánh** (`docs/nhanh-git.md`): `main` bản ổn định (vai trò master, giữ tên), `dev` tích hợp, `test` thử trước khi lên `main`, `hotfix` sửa gấp. Mỗi use case một nhánh `tai/uc-xx-...` / `kiet/uc-xx-...` tách từ `dev`, PR vào `dev`, CI xanh + người kia review mới gộp. Không push thẳng `main`, `dev`. Commit này là lần cuối ghi thẳng lên `main` để cả hai máy đọc được quy trình.
- 30/10 – Kiệt → Tài: (1) đã thử UC-11-AC12 (5 ca) và UC-13-AC13 (5 ca + 1 ảnh phụ): **đạt hết**, ảnh `docs/test-evidence/UC-11/`, `UC-13/`, kết quả điền trong story; Tài xác nhận và đóng 2 story. (2) Lịch trình UC-13 lấy Đ4 trước Đ1 ở TP.HCM, kịch bản mục 11 ghi Đ1 trước – ETA vẫn đúng, Tài xem có cần sửa không. (3) UC-02 xong 11/11, nhờ review PR `kiet/uc-02-nguoi-dung` → `dev` (kết quả thử UC-11, 13 đi cùng PR này vì chung file dữ liệu thử).
- 30/10 – Tài → Kiệt: **review 2 PR vào `dev`**: #3 (sửa sau review UC-13) và PR UC-12 Đổi xe/tài xế. Khi thử UC-13 thì thử thêm UC-12 (`UC-12-AC5`): trên trang chi tiết chuyến đang lập có đơn Đ1, Đ4 → "Đổi xe / tài xế" → xe nhỏ (tải 1.500 kg) hiện lý do BR-01; chọn xe khác đủ tải + tài xế khác → Lưu → biển số, tên tài xế đổi. Ảnh vào `docs/test-evidence/UC-12/`.
- ~~31/10 – Kiệt → Tài: Kiệt **thêm migration thứ 3** (nạp danh mục lý do `LY_DO`: lý do lấy / giao không được kèm `phia` KHACH/SU_CO_XE cho BR-37, 42) trong nhánh UC-19 (`kiet/uc-19-quet-lay`, từ 04/11 tách thẳng từ `dev`; migration `2a4c8d5f38e7` đã viết, gạch dòng này khi PR UC-19 gộp). Tài chưa thêm migration tới khi dòng này được gạch; cần thêm thì nhắn Kiệt để nối sau migration này.~~ Xong 05/11: PR #15 (UC-19) đã gộp `dev`, migration `2a4c8d5f38e7` trên `dev`; UC-20 không thêm migration.

## Câu hỏi chờ thầy
- ~~A1–A6 (nghiep-vu.md mục 1): chưa gửi~~ Nhóm tự chốt 16/10 (nghiep-vu.md mục 1).
- ~~A7 (tuyến ≤ 10 giờ), A8 (góc nhìn chủ xe): chưa gửi~~ Nhóm tự chốt 16/10.

## Tài
| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Nền móng (gồm UC-01 Đăng nhập) | 1 | Xong | 12/12 | |
| UC-03 Xe (mẫu) | 2 | Xong | 13/13 | |
| UC-06…09 Đơn tối thiểu | 3–4 | Xong | UC-06 6/6, UC-07 9/9, UC-08 11/11 | UC-08-AC11 Kiệt thử 25/10; UC-09 bỏ ở 0.5; phiếu QR làm cùng UC-19 |
| UC-05 Tuyến và nút (nhận từ Kiệt 24/10) | 3 | Xong | 9/9 | AC9 Kiệt thử 25/10 |
| UC-11…13, 15 Chuyến tối thiểu | 3–4 | Xong | UC-11 12/12, UC-12 5/5, UC-13 13/13, UC-15 11/11 | Đóng UC-12, 15 ngày 08/11 theo kết quả Kiệt thử (PR #18); còn sửa lỗi nhỏ danh sách xe UC-12 |
| UC-10, 16, 22, 32 (theo dõi chuyến) + làm dày UC-13, 15 | 5–6 | Đang làm | UC-16 10/10, UC-10 12/12, UC-22 11/12, UC-32 10/11 | UC-16 xong 08/11, UC-10 xong 10/11. Còn thiếu: UC-22 AC12 ca e (cần 3 chuyến); UC-32 AC11 ca c (cùng xe, tài xế khác) và ca e (chờ UC-33 của Kiệt). Bản đồ chi tiết chuyến (Leaflet + OSM) đã vào `dev` (PR #25) |
| UC-28, triển khai demo | 7 | Chưa bắt đầu | | |
| UC-30 AI | 8 | Chưa bắt đầu | | |

### Nhật ký Tài (mới nhất ở trên)
- 10/11: Gộp #34 sửa góp ý Kiệt thử UC-10, 22, 32 (dòng thời gian bằng chữ, lý do gần nhất "Sự cố xe", ẩn Sửa/Hủy khi chuyến đã chốt, BR-52 dấu phẩy; 789 passed) và #35 skill "Bước tiếp"; Kiệt gộp #36 ảnh bằng chứng. Đóng UC-10 (12/12). Review, approve #33 UC-24 của Kiệt.
- 10/11: Review và gộp #29 UC-21 Chi phí (kèm nhãn điểm Lấy `da_lay`), #30 UC-25 Công nợ của Kiệt (gỡ xung đột 1 dòng `main.py`, 787 passed); gộp #28 CI chạy một lần mỗi PR, bỏ qua PR tài liệu.
- 09/11: Gộp #25 bản đồ chi tiết chuyến (tọa độ điểm dừng, khóa vùng đất liền VN; ghi giấy phép gói trong PR) và #26 quy ước mới: PR code không sửa TIEN-DO, người gộp cập nhật một lần bằng PR riêng.
- 09/11: Gộp #19…#24 sau khi Kiệt duyệt (gỡ xung đột TIEN-DO ở #23, #24); `dev` có UC-10, 22, 32.
- 08/11: UC-32 Theo dõi chuyến: bảng chuyến trong ngày (tiến độ, % đầy, cờ trễ / sự cố / thất bại / chưa quyết toán / chồng lịch BR-73), chi tiết có giờ quét, trễ, dòng thời gian, tiền, sự cố; kết thúc do sự cố (BR-68), đóng sự cố; 24 test mới, toàn bộ 654 passed; 10/11 AC.
- 08/11: Review và gộp #16 (UC-20), #17 (UC-23; gộp `dev` vào nhánh, sửa xung đột TIEN-DO phần Kiệt, 630 passed), #18 (Kiệt thử giao diện UC-12, 15, 16). Đóng UC-12 (5/5), UC-15 (11/11), UC-16 (10/10). Vòng tối thiểu mốc 08/11 đã vào `dev`.
- 08/11: UC-22 Xử lý đơn thất bại: ghép lại (BR-37 chỉ đếm giao thất bại phía khách, BR-69 nơi giữ hàng, bỏ khung lấy cũ), trả hàng khi đã lấy, hủy khi chưa lấy (BR-34, 36), danh sách cần xử lý; 20 test mới; 11/12 AC; làm chung PR #23 với UC-10 (dùng chung endpoint hủy).
- 08/11: UC-10 Sửa / hủy đơn: sửa khi chưa lấy (BR-33), cước tính lại từ bản sao giá + nhật ký tiền, đơn đang ghép kiểm lại cả chuyến (BR-67); hủy kèm lý do, đơn đang ghép tự gỡ (BR-34); 35 test mới, toàn bộ 665 passed; 11/12 AC. Sửa sau review: lỗi danh sách xe UC-12 (#20), 3 điểm màn tài xế (#21), trang Tạm ứng chống bấm hai lần (#22).
- 04/11: UC-16 Hủy chuyến: chặn khi đã chạy hoặc còn tạm ứng (BR-25), đơn về chờ ghép, lý do vào lịch sử, chuyến hủy không chiếm lịch; 21 test mới, toàn bộ 459 passed; 9/10 AC. Gỡ xung đột PR #10, review và gộp #6 (UC-17), #11; #10 UC-15 vào `dev`.
- 01/11: UC-15 Chốt / mở chốt chuyến: kiểm lại nhóm A, B, xác nhận chạy rỗng (BR-23) và lãi âm (BR-52), lưu định mức, lương, ETA kế hoạch (BR-71), mở chốt chặn khi còn tạm ứng (BR-24); 17 test mới, toàn bộ 412 passed; 10/11 AC, giao diện chờ Kiệt thử.
- 01/11: Đóng UC-11 (12/12), UC-13 (13/13) theo kết quả Kiệt thử giao diện. Lệnh tạo tài khoản demo 4 vai trò (PR #8).
- 30/10: UC-12 Đổi xe/tài xế (nhánh `tai/uc-12-doi-xe-tai-xe`): kiểm lại BR-11…19 và tải theo đơn đang ghép, danh sách khả dụng cho chuyến đã có, khối đổi trên trang chi tiết; 9 test mới, toàn bộ 363 passed; 4/5 AC.
- 30/10: Chốt quy trình 4 nhánh `main` / `dev` / `test` / `hotfix` + nhánh use case (`docs/nhanh-git.md`, `CLAUDE.md`); tạo `test`, `hotfix`, đưa `dev` về đúng `main`.
- 30/10: UC-13 Ghép/gỡ đơn: lịch trình ETA (BR-63, 64), kiểm lại cả chuyến (BR-01…06, 12, 13, 15…17, 67), lãi dự kiến, trang chi tiết chuyến; 39 test mới, toàn bộ 354 passed; 12/13 AC, giao diện chờ Kiệt thử. Review UC-11 sửa 2 mục.
- 30/10: UC-11 Lập chuyến: backend + giao diện, BR-11…19, 64, 65 (khóa dòng chống hai người lập trùng xe), 49 test mới, toàn bộ 315 passed; 11/12 AC, giao diện chờ Kiệt thử.
- 30/10: Chốt 5 câu trong ca test BR của Kiệt, ghi vào nghiep-vu.md.
- 25/10: Review và merge UC-04 của Kiệt vào `main` (gộp validator GPLX, bỏ ảnh trùng). Đóng UC-05, UC-08 theo ảnh Kiệt thử. Giao diện hiện mã BR kèm lỗi nghiệp vụ (NFR-USA-02); Vite nghe 127.0.0.1.
- 24/10: UC-05 Tuyến và nút xong backend + giao diện (199 test); giao diện tạo đơn UC-08. Giao Kiệt thử giao diện UC-05, UC-08.
- 24/10: Review UC-06, 07, 08: sửa chuẩn hóa Unicode NFC cho chữ tiếng Việt, giới hạn vĩ độ/kinh độ (167 test).
- 24/10: UC-08 Tạo đơn backend: tính cước theo kịch bản mục 11, chốt cước, mã đơn ngẫu nhiên (10/11 AC, 164 test). Nhận UC-05 từ Kiệt.
- 24/10: UC-06 Khách hàng (6/6 AC) và UC-07 Bảng giá + cấu hình (9/9 AC) hoàn thành; 123 test đạt. Làm trước việc tuần 3 vì Kiệt chưa có UC-04, 05.
- 24/10: Review UC-03, sửa 3 mục frontend (ngày theo giờ máy, bỏ kết quả về muộn, xóa lỗi cũ).
- 24/10: UC-03 Quản lý xe hoàn thành (13/13 AC, 68 test đạt, thử giao diện đạt); viết docs/mau-use-case.md cho UC-04…06.
- 16/10: Review UC-01, sửa 3 mục (lỗi 400 lộ mật khẩu, test token chập chờn, đăng xuất khi mất mạng).
- 16/10: UC-01 hoàn thành: 30 test đạt, CI xanh, thử giao diện đạt 4 bước. Nền móng xong trước hạn 18/10.
- 16/10: Cài Docker, PostgreSQL. Models theo ERD 0.5 + migration đầu. UC-01: story duyệt, code backend + frontend + test (unit đạt, API chưa chạy). Chốt A1–A8; hướng dẫn cài môi trường, ca test BR, UML cho Kiệt.
- 16/10: Review và merge PR #1 nghiệp vụ 0.5 của Kiệt (sửa thêm cước Đ8, quy ước thứ tự route). Nhận UC-32; bỏ UC-14, 31.
- 10/10: Chốt nghiệp vụ 0.4, sơ đồ, kiến trúc, API; dựng khung repo, CI xanh lần đầu.

## Kiệt

> **Việc của Kiệt ngay bây giờ** (Tài ghi hộ 30/10, thay khối 24/10 đã xong: UC-04, thử UC-05/08, ca test BR). Claude của Kiệt: đọc khối này đầu phiên và báo Kiệt bước tiếp theo; Kiệt xong bước nào thì tự đánh dấu.
>
> 0. **Nhánh git (chốt 30/10):** đọc `docs/nhanh-git.md`. Từ giờ không push thẳng lên `main`. Mỗi việc dưới đây làm trên nhánh tách từ `dev` (ví dụ `kiet/uc-11-thu-giao-dien`, `kiet/uml`, `kiet/uc-02-nguoi-dung`), xong mở PR vào `dev` để Tài review.
> 1. **Cập nhật:** `git fetch` → `git switch dev` → `git pull` → mở Docker Desktop → `docker compose up -d db` → `cd backend; .venv\Scripts\python -m pytest` phải ra **354 passed** (không có migration mới).
> 2. ✅ (xong 30/10) **Thử giao diện UC-11 Lập chuyến** (`UC-11-AC12`): 5 bước (a)…(e) ở dòng "30/10 – Tài → Kiệt: thử giao diện UC-11" trong mục chung phía trên. Ảnh vào `docs/test-evidence/UC-11/`, điền dòng AC12 trong `docs/stories/UC-11-lap-chuyen.md`.
> 3. ✅ (xong 30/10) **Thử giao diện UC-13 Ghép đơn** (`UC-13-AC13`): dữ liệu cần tạo và 5 bước (a)…(e) ở dòng "30/10 – Tài → Kiệt: thử giao diện UC-13". Ảnh vào `docs/test-evidence/UC-13/`, điền dòng AC13 trong `docs/stories/UC-13-ghep-don.md`. Sai chỗ nào ghi vào "Đang chặn", không tự sửa code của Tài.
> 4. **UML** (`docs/uml/README.md`, còn từ tuần 1).
> 5. ✅ (xong 30/10, PR `kiet/uc-02-nguoi-dung` → `dev`) **UC-02 Người dùng** (`story new UC-02`, khuôn `docs/mau-use-case.md`): Quản lý xem danh sách, thêm tài khoản (Quản lý / Điều phối / Kế toán; tài xế tạo ở UC-04), đổi vai trò, khóa/mở (khóa có hiệu lực ngay như UC-01-AC7), đặt lại mật khẩu; đổi tên đăng nhập, mật khẩu của tài xế chuyển từ UC-04 sang đây (quyết định UC-04 số 4). Không cho Quản lý tự khóa hoặc tự hạ quyền chính mình (đề xuất – ghi vào story để Tài duyệt).
> 6. **Quét tối thiểu UC-17…20** (tuần 3–4, phía tài xế, trang điện thoại 360 px): UC-17 xem chuyến được giao (BR-58: chỉ chuyến của mình), UC-18 bắt đầu/kết thúc chuyến kèm km và ảnh đồng hồ (BR-26, 28, 70), UC-19 quét mã lấy hàng / báo không lấy được, UC-20 quét mã giao / báo giao không được (BR-35, 38…43, 45, 72). Ca test sẵn ở `docs/ca-test-br.md` nhóm C, E, H. Lưu ý:
>    - Tài xế chỉ thấy chuyến từ `DA_CHOT`; chốt chuyến là UC-15 Tài đang làm. Trong test đặt `trang_thai = "DA_CHOT"` trực tiếp vào CSDL như `test_uc13_ac9_*`, không cần đợi.
>    - Lịch trình, ETA dùng lại `app/domain/lich_trinh.py` và `chi_tiet` trong `app/modules/chuyen/service.py` (UC-13), không viết lại.
>    - Upload ảnh theo `docs/security-rules.md`. Thư viện quét QR, thư viện in QR (phiếu đơn): **hỏi Tài trước khi cài package** (CLAUDE.md).
> 7. **Sau đó theo kế hoạch:** UC-21 chi phí, UC-23 tạm ứng, UC-33 báo sự cố (tuần 5–6); UC-24 quyết toán, UC-25 công nợ (tuần 7); UC-26, 27, 34 và E2E (tuần 8).
> 8. Không làm UC-11, 12, 13, 15 (Tài). Đụng `backend/app/models/` hoặc thêm migration thì ghi vào "Đang chặn" và commit trước.

| Việc | Tuần | Trạng thái | AC đạt/tổng | Còn thiếu |
|---|---|---|---|---|
| Phân tích lại nghiệp vụ 0.5 (nhánh `kiet/nghiep-vu`) | 1 | Xong | – | PR #1 merge 16/10 (Tài cập nhật hộ) |
| Cài môi trường, danh sách ca test BR, vẽ UML | 1 | Đang làm | – | Cài môi trường xong 19/10 (theo báo cáo tuần 2; Tài sửa hộ 25/10). Ca test BR xong 29/10, Tài chốt 30/10 (Tài cập nhật hộ). Còn UML |
| UC-04 Tài xế (chép mẫu) | 2 | Xong | 10/10 | Tài review, merge vào `main` 25/10 (Tài cập nhật hộ) |
| UC-02 + Quét tối thiểu (UC-17…20) | 3–4 | Xong | UC-02 11/11, UC-17 10/10, UC-18 11/11, UC-19 15/15, UC-20 16/16 | UC-02 (PR #5), UC-17 (PR #6), UC-18 (PR #13), UC-19 (PR #15), UC-20 (PR #16) đã gộp `dev`. UC-20 xong 05/11 (40 test, kèm 3 góp ý review #15: tối đa 5 ảnh, trần độ chính xác GPS, xin vị trí lúc bấm; Safari iPhone đã gửi vị trí), gộp `dev` (PR #16, 08/11). Vòng tối thiểu mốc 08/11 chạy trọn trên giao diện. BR-44 để hướng phát triển (Tài chốt). UC-05 chuyển cho Tài 24/10 (Tài cập nhật hộ) |
| Quét đầy đủ, UC-21, 23, 33 (báo sự cố) | 5–6 | Đang làm | UC-21 14/14, UC-23 14/14 | UC-23 Tạm ứng gộp `dev` 08/11 (PR #17). UC-21 Chi phí (kèm nhãn điểm "Đã lấy") gộp `dev` 10/11 (PR #29). Còn UC-33 báo sự cố, làm sau UC-24 |
| UC-24, 25 | 7 | Đang làm | UC-25 10/10 | UC-25 Công nợ gộp `dev` 10/11 (PR #30). UC-24 Quyết toán bắt đầu 10/11 (mốc 29/11). Để sau: trang Công nợ cho Quản lý (góp ý của Tài, làm cùng giao diện UC-24) |
| UC-26, 27, 34 (hiệu suất xe, ưu tiên S – thiếu giờ thì cắt trước), E2E | 8 | Chưa bắt đầu | | |

### Nhật ký Kiệt (mới nhất ở trên)
- 10/11: Tài gộp #29 UC-21 Chi phí (14/14 AC, 52 test, thử giao diện đạt) và #30 UC-25 Công nợ (10/10 AC, 26 test, thử giao diện đạt), 787 passed. 08–09/11: review, duyệt #19…#28 của Tài; thử giao diện UC-12, 15, 16 (PR #18). Tiếp theo: UC-24 Quyết toán.
- 07/11: Đóng UC-23 (14/14 AC): thử giao diện 7/7 ca (cấp, vượt định mức, sửa, thu hồi, mở chốt bị chặn rồi được); sửa bước ô số tiền và câu báo khi sửa vượt định mức.
- 07/11: UC-23 Tạm ứng: module `tien/tam_ung/` (cấp, sửa, thu hồi, xem; BR-53 kiểm ở mọi lần cấp và sửa, khóa dòng chuyến, nhật ký tiền BR-62, đã quyết toán → BR-29), thêm `GET /api/chuyen/{id}/tam-ung` (gợi ý số còn được cấp); trang Kế toán **Tạm ứng**; 49 test, toàn bộ 590 passed; 13/14 AC. PR #16 (UC-20) chờ Tài review.
- 05/11: Đóng UC-20 (16/16 AC): thử giao diện 10/10 ca (máy tính 360 px; iPhone Safari qua tunnel: quét xác nhận, ký ngón tay, có GPS; kết thúc chuyến CH-261031-01 → vòng tối thiểu chạy trọn); 581 passed. Để sau: khối Kết thúc chuyến tràn khung iPhone, hỏi lại trước Xác nhận giao.
- 05/11: UC-20 Quét giao: `GIAO` (ảnh + chữ ký PNG + tên, BR-41), giao trễ (BR-72), sinh phải thu + nhật ký tiền (BR-56, 62), `GIAO_THAT_BAI` (BR-42), đơn chưa lấy 409 BR-40, bảng quét lặp / trái kết quả; giao diện quét xác nhận + ô ký canvas; xin vị trí lúc bấm (Safari); 40 test, toàn bộ 581 passed; 14/16 AC. Gộp #15 (UC-19).
- 04/11: Đóng UC-19 (15/15 AC): thử giao diện 12/12 ca (phiếu QR, tài xế 360 px, camera iPhone qua Cloudflare Tunnel có GPS thật); 541 passed. Để sau: GPS Safari iPhone, BR-44.
- 04/11: UC-19 giao diện: khối Lấy hàng (camera `qr-scanner` + gõ mã), Không lấy được (lý do + ảnh), phiếu in QR (`qrcode`), cho phép Cloudflare Tunnel trong Vite; chờ thử giao diện.
- 04/11: UC-19 Quét lấy hàng (backend): `POST /api/toi/quet` ở module `quet/` (BR-38, 39, 42, 43, 45: không thuộc chuyến 403, chuyến chưa chạy 409, quét lặp cùng ý trả trạng thái hiện tại, trái kết quả 409 BR-39, trường lạ 400), `GET /api/danh-muc/ly-do`, migration nạp 12 lý do; 50 test, toàn bộ 488 passed; 12/15 AC. Review PR #12 (UC-16) của Tài: đạt, 459 passed. Gộp `dev` mới vào UC-18, mở PR #13.
- 31/10: UC-18 Bắt đầu / kết thúc chuyến: km + ảnh đồng hồ (BR-26, 70), kiểm lại giấy tờ BR-11…15 bằng hàm UC-11, kết thúc khi mọi đơn có kết quả (BR-28), gỡ đơn thất bại (BR-36); `app/luu_tru.py` kiểm/lưu ảnh dùng chung; thêm `python-multipart`; 32 test; thử giao diện đạt.
- 31/10: UC-17 Xem chuyến được giao: danh sách cần làm / đã xong, lịch trình từng điểm cho tài xế (BR-58, 63, 71), chỉ hiện lương chuyến, chuyến người khác → 404; trang điện thoại; 14 test; thử giao diện đạt (sửa 1 lỗi kẹt "Đang tải…").
- 30/10: Thử giao diện UC-11 (5 ca) và UC-13 (5 ca) cho Tài: đạt; thêm dữ liệu thử Phần 5, 6 vào `du-lieu-thu-giao-dien.md`.
- 30/10: UC-02 Người dùng: Quản lý thêm (QL/ĐP/KT), sửa, đổi vai trò, khóa/mở (mở xóa khóa tạm), đặt lại mật khẩu; tài khoản tài xế chỉ đổi tên đăng nhập, họ tên, mật khẩu; chặn tự khóa và khóa Quản lý cuối (kể cả hai người khóa nhau cùng lúc). 41 test, toàn bộ 395 passed; thêm endpoint đặt lại mật khẩu vào `api.md`. Thử giao diện 6 ca đạt; 11/11 AC.
- 29/10: Danh sách ca test BR (`docs/ca-test-br.md`): 70 BR còn hiệu lực, 180 ca theo nhóm A…H, mỗi ca ✖ chỉ vi phạm một BR, có ca biên; thêm dữ liệu X3…X8, Cường, Dũng, Đ9…Đ15. Commit dữ liệu và kết quả thử giao diện UC-04, 05, 08 (`docs/test-evidence/UC-xx/du-lieu.md` (mỗi UC một file)).
- 25/10: UC-04 Tài xế: backend (thêm kèm tài khoản, sửa, ngừng khóa tài khoản), hàm BR-14 hạng GPLX cho UC-11, giao diện; 67 test, toàn bộ 266 passed; thử giao diện 10/10 AC đạt; ponytail-review sửa 2 mục. Thử giao diện UC-05, UC-08 cho Tài: đạt. Mở PR `kiet/uc-04`.
- 15/10: Sửa nghiệp vụ 0.5 theo review của Tài: công thức BR-73, km khi kết thúc do sự cố, thứ tự điểm lấy, kịch bản mỗi ca ✖ chỉ một BR (thêm Đ8 cho BR-67); thêm mục Công thức, ETA kế hoạch lưu lúc chốt, dữ liệu cho AI; api, security-rules, kien-truc khớp 0.5. Nhận UC-33, UC-34.
- 15/10: Nghiệp vụ 0.5: chuyến 6 trạng thái, đơn 7; ETA cộng phút dừng, kiểm lại cả chuyến khi ghép (BR-63…67); km, sự cố, kết thúc do sự cố, cảnh báo trễ (BR-68…73); bỏ UC-09, 14, 29, 31, thêm UC-32…34. Sửa nghiep-vu, use-cases, so-do; api, security-rules chỉ đổi tên trạng thái. Mở PR chờ Tài review.
