# Hệ thống quản lý vận tải – Nhóm 8 (Tài, Kiệt)

Nghiệp vụ ở `docs/nghiep-vu.md`; thiết kế và quyết định nằm trong `docs/`. Đọc file liên quan trước khi code; code làm đổi thiết kế thì sửa `docs/` trong cùng commit.

## Skill và plugin
Danh sách, lúc nào dùng cái nào: `docs/SKILLS.md`.

## Quy ước bắt buộc
- Mỗi use case làm theo skill `story-flow`: story trong `docs/stories/`, tiêu chí chấp nhận, test, bằng chứng. Mọi quy tắc nghiệp vụ đều phải có test, không theo mức "một test nhỏ" của ponytail.
- Giữ kiến trúc phân lớp đã chốt trong `docs/`; ponytail chỉ rút gọn bên trong từng lớp.
- Code chạm tới phân quyền, upload, tiền, quét mã: theo `docs/security-rules.md`.
- Không đọc, in hay commit `.env`. Cần biến mới thì thêm tên vào `.env.example`.
- Không cài package mới khi chưa hỏi.

## Làm việc hai người
- Người đang dùng máy ghi trong `CLAUDE.local.md`. Không có file đó thì hỏi trước khi sửa tiến độ.
- Đầu phiên: `git switch dev` → `git pull`, đọc `docs/TIEN-DO.md` (mục "Đang chặn" và phần của người dùng máy này), báo ngắn việc tiếp theo.
- Chỉ sửa phần của người dùng máy này trong `TIEN-DO.md`; mục chung chỉ thêm dòng.
- Sau `story done` hoặc trước khi kết thúc phiên: cập nhật dòng việc (trạng thái, AC đạt/tổng, còn thiếu), thêm 1 dòng nhật ký, commit cùng code.
- Trước khi sửa file dùng chung (`models/`, migration, `domain/trang_thai.py`): ghi vào "Đang chặn" và commit trước.

## Nhánh git (chi tiết: `docs/nhanh-git.md`)
- 4 nhánh dài hạn: `main` (bản ổn định, vai trò master), `dev` (tích hợp), `test` (thử trước khi lên `main`), `hotfix` (sửa gấp trên `main`).
- Mỗi use case một nhánh tách từ `dev`: `tai/uc-xx-...` hoặc `kiet/uc-xx-...`; xong mở PR vào `dev`, CI xanh và người kia review rồi mới gộp.
- Không push thẳng lên `main`, `dev`; `main` chỉ nhận PR từ `test` hoặc `hotfix`. Không `push --force` lên nhánh dài hạn.
