# Sơ đồ UML cho báo cáo

> Người làm: **Kiệt** · Nguồn: `docs/so-do.md` (Mermaid, bản 0.5) và `docs/nghiep-vu.md` · Mục đích: hình đưa vào báo cáo và slide bảo vệ, **đúng ký hiệu UML**.
> `so-do.md` là bản để hiểu nghiệp vụ, Mermaid không có đủ ký hiệu UML. Thư mục này là bản vẽ lại cho báo cáo. **Nghiệp vụ đổi thì sửa `so-do.md` trước, rồi vẽ lại hình ở đây.**

## 1. Công cụ

- **draw.io** (diagrams.net): miễn phí, chạy trên web hoặc bản desktop, có sẵn bộ hình UML (menu *More Shapes → UML*). Lưu file `.drawio` là XML, commit được vào git.
- Muốn vẽ trong VS Code thì cài extension "Draw.io Integration" (hỏi nhóm trước khi cài, theo CLAUDE.md).
- Không dùng công cụ trả phí. StarUML có bản dùng thử, giấy phép cho sinh viên **cần kiểm tra** trước khi dùng.

## 2. Danh sách hình cần vẽ

| # | File | Loại UML | Vẽ lại từ | Ghi chú |
|---|---|---|---|---|
| 1 | `use-case.drawio` | Use case | `so-do.md` mục 2, `use-cases.md` mục 2 | Có khung hệ thống; tác nhân Quản lý **tổng quát hóa** Điều phối (mũi tên tam giác rỗng); UC-01 dùng `<<include>>` từ các UC cần đăng nhập, hoặc ghi chú chung; UC-30 nét đứt hoặc `<<extend>>` |
| 2 | `activity-tong-quan.drawio` | Activity (có swimlane) | `so-do.md` mục 1 | Mỗi làn một tác nhân; nút quyết định có điều kiện trong `[ ]`; có điểm bắt đầu, kết thúc |
| 3 | `state-chuyen.drawio` | State machine | `so-do.md` mục 3, `nghiep-vu.md` mục 5.1 | 6 trạng thái; mỗi chuyển ghi `sự kiện [điều kiện BR-xx]`; có hai đường `DANG_CHAY → HOAN_THANH` (tài xế, sự cố) |
| 4 | `state-don.drawio` | State machine | `so-do.md` mục 4, `nghiep-vu.md` mục 5.2 | 7 trạng thái; `THAT_BAI` có ba nhánh ra, ghi điều kiện "đã có lượt quét lấy" / "chưa có" |
| 5 | `class.drawio` | Class (hoặc ERD) | `so-do.md` mục 5, 6, 7 | Hỏi thầy dùng class diagram hay ERD; mặc định vẽ class, chỉ thuộc tính chính, ghi bội số (`1`, `0..*`) đúng theo ERD |
| 6 | `seq-ghep-don.drawio` | Sequence | `so-do.md` mục 8 | Fragment `alt` cho vi phạm / đạt; lồng `alt` cho xung đột BR-07 |
| 7 | `seq-quet-giao.drawio` | Sequence | `so-do.md` mục 9 | Thứ tự nhánh `alt`: 403 → 409 → 200 lặp lại → 409 chưa lấy → hợp lệ |
| 8 | `seq-quyet-toan.drawio` | Sequence | `so-do.md` mục 10 | Fragment `loop` duyệt từng khoản chi |

Ưu tiên: 1, 3, 4, 5 (báo cáo nào cũng cần), rồi 6–8, cuối cùng 2.

## 3. Quy ước vẽ

- Tên trạng thái giữ **mã** như trong code (`DANG_CHAY`), có thể thêm tên tiếng Việt bên dưới.
- Mỗi chỗ hệ thống kiểm quy tắc ghi mã BR, để thầy đối chiếu được với bảng quy tắc.
- Không thêm trạng thái, UC, bảng nào không có trong `nghiep-vu.md`, `use-cases.md`. Thấy thiếu thì sửa tài liệu trước (nhánh riêng, mở PR), rồi mới vẽ.
- Mỗi hình xuất thêm **PNG** cùng tên (`use-case.png`, nền trắng, đủ rõ khi in A4) để chèn vào báo cáo.
- Commit cả `.drawio` lẫn `.png` vào `docs/uml/`.

## 4. Xong khi

- Đủ 8 hình ở mục 2, mỗi hình có `.drawio` và `.png`.
- Tự kiểm: mỗi trạng thái, mỗi mũi tên chuyển trạng thái, mỗi UC trong hình đều có trong tài liệu, và ngược lại.
- Tài xem lại, hoặc nhờ Claude Code so hình với `so-do.md` (Claude đọc được file `.drawio` vì đó là XML).
