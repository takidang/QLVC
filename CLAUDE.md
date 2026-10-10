# Hệ thống quản lý vận tải – Nhóm 10 (Tài, Kiệt)

Nghiệp vụ ở `docs/nghiep-vu.md`; thiết kế và quyết định nằm trong `docs/`. Đọc file liên quan trước khi code; code làm đổi thiết kế thì sửa `docs/` trong cùng commit.

## Skill và plugin
Danh sách, lúc nào dùng cái nào: `docs/SKILLS.md`.

## Quy ước bắt buộc
- Mỗi use case làm theo skill `story-flow`: story trong `docs/stories/`, tiêu chí chấp nhận, test, bằng chứng. Mọi quy tắc nghiệp vụ đều phải có test, không theo mức "một test nhỏ" của ponytail.
- Giữ kiến trúc phân lớp đã chốt trong `docs/`; ponytail chỉ rút gọn bên trong từng lớp.
- Code chạm tới phân quyền, upload, tiền, quét mã: theo `docs/security-rules.md`.
- Không đọc, in hay commit `.env`. Cần biến mới thì thêm tên vào `.env.example`.
- Không cài package mới khi chưa hỏi.
