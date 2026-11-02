# Quy trình nhánh git (nhóm chốt 30/10/2026)

Bốn nhánh dài hạn, cộng nhánh ngắn cho từng use case. Claude của cả hai máy làm theo file này; `CLAUDE.md` mục "Nhánh git" tóm tắt.

| Nhánh | Vai trò | Ai đưa code vào | Push thẳng? |
|---|---|---|---|
| `main` | Bản ổn định để demo, nộp (đóng vai *master*, giữ tên `main`) | Chỉ PR từ `test` (sau khi thử đạt) hoặc từ `hotfix` | Không |
| `dev` | Nhánh tích hợp hằng ngày | PR từ nhánh use case | Không |
| `test` | Bản đang thử trước khi lên `main`: thử giao diện theo story, chạy toàn bộ test | Gộp `dev` vào khi chuẩn bị mốc (demo, báo cáo tuần) | Chỉ khi gộp `dev` vào |
| `hotfix` | Sửa lỗi gấp trên `main` | Người sửa | Có, rồi mở PR vào `main` |
| `tai/uc-xx-...`, `kiet/uc-xx-...` | Một use case (hoặc một việc tài liệu) | Người làm | Có |

## 1. Làm một use case
```
git switch dev
git pull
git switch -c kiet/uc-02-nguoi-dung        # tên: <người>/uc-xx-<mô tả ngắn>
# ... story-flow: story, code, test, cập nhật TIEN-DO phần mình ...
git push -u origin kiet/uc-02-nguoi-dung
gh pr create --base dev                     # tiêu đề: "UC-02 Người dùng – nhờ Tài review"
```
- PR vào `dev` phải **CI xanh** và được **người kia review** (Claude của người kia chạy `ponytail-review` trên PR). Góp ý ghi dưới dạng đề xuất, người làm tự quyết sửa hay không.
- Gộp xong thì xóa nhánh use case (`gh pr merge --merge --delete-branch`).
- Làm lâu hơn 1–2 ngày thì kéo `dev` mới về nhánh mình (`git merge origin/dev`) để đỡ xung đột.
- Việc tài liệu nhỏ của riêng mình (một dòng tiến độ, nhật ký) đi cùng nhánh use case; không có use case nào thì dùng nhánh `tai/tai-lieu-...` / `kiet/tai-lieu-...` như trên.

## 2. Lên `test` rồi `main` (trước mốc demo, báo cáo tuần)
```
git switch test
git pull
git merge origin/dev                        # chỉ gộp dev vào, không sửa code trực tiếp trên test
git push
```
- Thử giao diện các AC loại UI còn `CHƯA KIỂM`, chạy toàn bộ test. Lỗi thì sửa trên nhánh use case → PR vào `dev` → gộp `dev` vào `test` lại.
- Đạt thì mở PR `test` → `main`, người kia duyệt, gộp.

## 3. Sửa lỗi gấp trên `main`
```
git switch hotfix
git pull
git merge --ff-only origin/main             # đưa hotfix về đúng main trước khi sửa
# ... sửa, kèm test bắt lỗi đó ...
git push
gh pr create --base main --head hotfix
```
- Gộp xong vào `main` thì gộp `main` vào `dev` (`git switch dev; git pull; git merge origin/main; git push`) để `dev` không mất bản sửa.

## 4. Lưu ý
- File dùng chung (`backend/app/models/`, migration, `domain/trang_thai.py`): vẫn ghi "Đang chặn" trong `TIEN-DO.md` và commit **lên `dev` qua PR nhỏ** trước khi sửa.
- **Tránh xung đột (chốt 31/10, sau lần PR #5 và #6 đụng nhau):**
  - `TIEN-DO.md`: mỗi người **chỉ sửa phần của mình**. Nhắn nhau (nhờ review, nhờ thử giao diện, báo xong việc) ghi vào **mô tả PR hoặc comment trên PR**, không thêm dòng vào mục chung nữa (hai người cùng chèn vào một chỗ là xung đột).
  - Dữ liệu và kết quả thử giao diện: mỗi use case một file `docs/test-evidence/UC-xx/du-lieu.md`, không nối vào file chung.
  - Danh sách cố định trong code (router ở `backend/app/main.py`, menu `TRANG_CON` ở `frontend/src/App.tsx`): chèn theo thứ tự chữ cái, không thêm vào cuối.
  - PR nhỏ, review và gộp trong ngày. **Trước khi mở PR** chạy `git merge origin/dev` trên nhánh mình, sửa xung đột ngay.
  - Không làm nhánh mới chồng lên nhánh chưa gộp (ví dụ UC-18 trên UC-17), trừ khi bắt buộc; nếu chồng thì gộp nhánh dưới trước.
- Không `push --force` lên `main`, `dev`, `test`. Không sửa lịch sử đã push.
- Nhánh cũ `kiet/nghiep-vu` giữ lại (nhóm chốt 30/10); `kiet/uc-04` đã gộp hết, có thể xóa.
