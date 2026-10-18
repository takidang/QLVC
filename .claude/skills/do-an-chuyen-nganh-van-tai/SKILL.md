---
name: do-an-chuyen-nganh-van-tai
description: "Dùng khi Tai làm đồ án chuyên ngành CNPM (hệ thống quản lý vận tải, chuyến xe là trung tâm): phạm vi, thứ tự sản phẩm (đặc tả, sơ đồ, ERD, API, mockup, kiểm thử, báo cáo), yêu cầu chất lượng, báo cáo tiến độ tuần. Code từng use case thì dùng story-flow; viết code thì dùng ponytail."
---

# Đồ án chuyên ngành CNPM – Hệ thống quản lý vận tải

Nhóm 8: Đặng Lê Tấn Tài, Nguyễn Đỗ Tuấn Kiệt (cả hai code). Thực hiện 12/10–20/12/2026, nộp LMS 21–27/12, bảo vệ 28/12/2026–10/01/2027.

**Nguồn sự thật về nghiệp vụ:** trong repo là `docs/nghiep-vu.md`; trong chat claude.ai là bản sao của file đó trong mục tài liệu (knowledge) của Project "Đồ án chuyên ngành CNPM – Hệ thống quản lý vận tải". Repo là bản gốc: sửa `docs/nghiep-vu.md` trước, rồi tải lại file lên Project. Mọi thứ phải nhất quán với: **CHUYẾN XE LÀ TRUNG TÂM, ĐƠN HÀNG ĐƯỢC GHÉP VÀO CHUYẾN**.

Không dùng skill này cho môn Quản lý Dự án CNTT (QLDACNTT) – môn đó có skill riêng.

## 1. Phạm vi: CHỈ làm sản phẩm

Đồ án chỉ chấm sản phẩm. KHÔNG làm các phần quản lý dự án:
- Bỏ: chi phí, ngân sách, NPV/ROI, EVM, Gantt, đường găng, PERT, quản lý rủi ro, nhân sự/RAM, truyền thông, mua sắm/hợp đồng.
- Ngoại lệ duy nhất: báo cáo tiến độ hằng tuần (mục 4), viết theo sản phẩm, không tính tiền/giờ công.
- YAGNI/KISS/DRY: vừa sức 2 người × 10 tuần. Tính năng nặng hoặc phát sinh → "Hướng phát triển".
- AI là module phụ, làm sau khi lõi chạy ổn. Không chatbot; ưu tiên tự train mô hình.

## 2. Chuỗi sản phẩm (làm theo thứ tự)

1. Đặc tả yêu cầu: tác nhân, use case, đặc tả use case, quy tắc nghiệp vụ, yêu cầu phi chức năng.
2. Sơ đồ use case; activity/sequence cho luồng chính (tạo chuyến, ghép đơn, chốt chuyến, quét mã bốc/giao, quyết toán).
3. Sơ đồ trạng thái Chuyến và Đơn (đúng vòng đời trong `docs/nghiep-vu.md`).
4. ERD (bảng chính: chuyến, đơn, điểm dừng, xe, tài xế, lượt quét mã, chi phí chuyến, tạm ứng, khách hàng, người dùng/vai trò).
5. Kiến trúc hệ thống + đặc tả API.
6. Mockup giao diện (web cho điều phối/kế toán/quản lý; web responsive cho tài xế).
7. Code: web chạy được, có phân quyền, triển khai demo. Mỗi use case theo skill `story-flow`.
8. Kiểm thử + báo cáo kiểm thử (`story report` của `story-flow`).
9. Báo cáo cuối kỳ + slide bảo vệ.

Chia việc theo phân hệ: Chuyến, Đơn, Xe/Tài xế, Quét mã giao nhận, Quyết toán, Tra cứu, AI.

## 3. Chất lượng (rút từ bài giảng MAN104 Bài 5)

- Yêu cầu phi chức năng viết theo nhóm ISO/IEC 25010: chức năng, hiệu năng, bảo mật, khả năng bảo trì.
- Bảo mật theo checklist OWASP; quy tắc cụ thể của đồ án ở `docs/security-rules.md`.
- Kiểm thử đủ mức: unit → tích hợp (API) → hệ thống (luồng chính) → hồi quy mỗi lần sửa.
- Test case bám quy tắc nghiệp vụ, tối thiểu: vượt tải trọng/thể tích, ngoài tuyến, lệch khung giờ, xe hết đăng kiểm/bảo hiểm, tài xế sai hạng bằng, trùng giờ xe/tài xế, một đơn ghép 2 chuyến, chuyển trạng thái sai, cước = max(kg thật, thể tích quy đổi), lãi chuyến. Mỗi mục là tiêu chí chấp nhận trong story tương ứng.
- Báo cáo kiểm thử: số test pass/fail, số lỗi còn tồn.
- Review code chéo giữa 2 người (`ponytail-review`); CI (GitHub Actions) chạy test khi push.

## 4. Báo cáo tiến độ hằng tuần

Mẫu (~nửa trang):

**Báo cáo tuần X (dd/mm – dd/mm) – Nhóm 8**
1. **Đã hoàn thành**: tính năng/tài liệu xong, người làm, minh chứng (link PR/commit, ảnh màn hình, sơ đồ). VD: "API tạo chuyến + kiểm tra tải trọng (Tài) – PR #12, 8/8 test pass".
2. **Trạng thái chức năng**: bảng các phân hệ, mỗi cái *Chưa làm / Đang làm / Xong / Đã test* (bảng dùng cả kỳ, mỗi tuần chỉ cập nhật).
3. **Vướng mắc / cần thầy góp ý**: lỗi chưa giải quyết, câu hỏi nghiệp vụ.
4. **Kế hoạch tuần sau**: 2–4 việc cụ thể, có người phụ trách.
5. **Thay đổi so với tuần trước** (nếu có): thầy góp ý gì → đã sửa gì.

Tùy chọn: số test pass/fail, số lỗi còn tồn (lấy từ CI hoặc `docs/test-report.md`).

Để đỡ công: commit/PR đặt tên rõ ràng (mục 1 = liệt kê PR đã merge); trạng thái từng story lấy từ `docs/stories/`.

## 5. Quy tắc làm việc

- Không bịa: dataset, giấy phép, tính năng phần mềm, quy định pháp luật phải có nguồn; chưa kiểm tra thì ghi "cần kiểm tra".
- Câu hỏi nghiệp vụ chưa có câu trả lời của thầy → ghi thành giả thiết rõ ràng, không tự chốt.
