# Skill và plugin Claude Code của đồ án

Mọi thứ dưới đây đã nằm sẵn trong repo. Clone repo, mở Claude Code trong thư mục repo, chọn **Trust** khi được hỏi là có đủ. Không cần cài tay.

Cập nhật lần cuối: 25/11/2026 (thêm `kiem-thu-kham-pha`).

## 1. Danh sách

| Tên | Loại | Dùng khi | Gọi |
|---|---|---|---|
| `do-an-chuyen-nganh-van-tai` | Skill | Phạm vi, thứ tự sản phẩm, yêu cầu chất lượng, báo cáo tiến độ tuần | "làm báo cáo tuần 3", "bước tiếp theo của đồ án là gì" |
| `ponytail` | Skill (`.claude/skills/`) | Viết, sửa, refactor code, fix bug, chọn thư viện | Tự kích hoạt; đổi mức: "ponytail lite/full/ultra" |
| `ponytail-review` | Skill | Review thay đổi trước khi merge, kể cả bảo mật theo `docs/security-rules.md` | "review commit cuối", "review PR này" |
| `impeccable` | Skill | Dựng, critique, audit, polish giao diện web (màn điều phối, kế toán dùng mode **Operate**) | "critique màn X", "audit", "polish" |
| `story-flow` | Skill | Làm một use case từ đầu đến cuối: story + tiêu chí chấp nhận → code + test → kiểm bằng chứng → đóng story; xuất bảng truy vết cho báo cáo kiểm thử | "story new UC-03", "story dev UC-03", "story done UC-03", "story report" |
| `webapp-testing` | Skill (Anthropic) | Test E2E bằng Playwright cho luồng ghép đơn, quét mã, quyết toán | "test luồng X trên localhost" |
| `kiem-thu-kham-pha` | Skill | "Phá thử" trước mỗi mốc lên `main`: quét phụ thuộc, rà phân quyền, nhập bừa, gửi song song; xác minh từng lỗi, lỗi thật sửa kèm test | "kiểm thử khám phá", "phá thử" |
| `engineering` | Plugin (Anthropic) | Chỉ dùng: `/architecture`, `/system-design`, `/testing-strategy`, `/documentation`, `/debug` | Gõ lệnh tương ứng |

Không dùng cho đồ án: `security-guidance` (tốn thêm usage mỗi lượt), `code-review` của Engineering (trùng `ponytail-review`), `mini-crew`, `ui-design`, plugin Product Management.

## 2. Phân vai, tránh chồng chéo

- Giao diện trông thế nào → `impeccable`. Code bên dưới giao diện → `ponytail`.
- Quyết định kiến trúc → `/architecture`, ghi vào `docs/`. Code theo kiến trúc đó → `ponytail`.
- Review code và bảo mật → `ponytail-review`, đối chiếu `docs/security-rules.md`.
- Test: chiến lược ở `/testing-strategy`; từng use case theo `story-flow` (tiêu chí → test → bằng chứng); E2E và ảnh chụp bằng `webapp-testing`; trước mốc lên `main` tìm lỗi ngoài tiêu chí bằng `kiem-thu-kham-pha` (không thay test và CI, kết quả phải xác minh lại vì hay báo nhầm). Mọi quy tắc nghiệp vụ phải có test (ghi đè mức "một test nhỏ" của ponytail).

## 3. Phiên bản đã ghim và kết quả kiểm tra bảo mật

| Tên | Nguồn | Phiên bản / commit | Kết luận |
|---|---|---|---|
| `ponytail`, `ponytail-review` | github.com/DietrichGebert/ponytail (MIT) | v5.1.0, `9cc65d0` | **An toàn.** Chỉ SKILL.md, không script, không gọi mạng. |
| `impeccable` | Rút gọn từ github.com/pbakaus/impeccable (Apache 2.0) | `d631a88` | **An toàn.** Chỉ SKILL.md. Không chạy `npx impeccable install` khi chưa kiểm tra. |
| `do-an-chuyen-nganh-van-tai` | Tài viết | - | **An toàn.** Chỉ SKILL.md. |
| `story-flow` | Tài viết, rút gọn từ `dev-story`, `story-done`, `test-evidence-review` của github.com/Donchitos/Claude-Code-Game-Studios (MIT) | `be8993b` | **An toàn.** Chỉ SKILL.md và một file mẫu. Không lấy hook hay script nào của repo gốc. |
| `kiem-thu-kham-pha` | Tài viết | - | **An toàn khi dùng đúng chỗ.** SKILL.md, phiếu mẫu và `quet_route_fastapi.py` (chỉ liệt kê route và vai trò, không gọi mạng; nạp `app` nên đọc cấu hình, không in ra). Quy trình tạo dữ liệu rác: chỉ chạy trên CSDL thử. |
| `webapp-testing` | github.com/anthropics/skills | `dbd4588` | **An toàn.** `with_server.py` chạy lệnh server bạn đưa vào và chỉ kết nối `localhost`. |
| `engineering` | github.com/anthropics/knowledge-work-plugins | v1.2.0, `ae1513e` | **Cần lưu ý.** Chỉ có SKILL.md, nhưng `.mcp.json` khai báo sẵn connector tới Slack, Linear, Asana, Atlassian, Notion, GitHub, PagerDuty, Datadog (URL chính thức). Không đăng nhập thì connector không làm gì. Chỉ đăng nhập Atlassian nếu nhóm dùng Jira. |

## 4. Luật chặn trong `.claude/settings.json`

Claude Code không được đọc hay sửa `.env`, không chạy `rm -rf`, `git push --force`, `git reset --hard`, `git clean -f`, `sudo` (cả Bash và PowerShell). Lấy từ Claude-Code-Game-Studios. Cần làm những việc này thì tự gõ lệnh.

## 5. Cập nhật

- `autoUpdate: false` trong `.claude/settings.json`. Skill trong `.claude/skills/` chỉ đổi khi có commit.
- Muốn lên bản mới: đọc diff từ commit đã ghim ở bảng trên, kiểm tra lại (gọi mạng, đọc biến môi trường, lệnh shell, script cài đặt, file nhị phân, chỉ dẫn ẩn), rồi mới cập nhật bảng và commit.

## 6. Lưu ý khi cài

- Lần đầu mở repo, Claude Code hỏi có tin thư mục không. Chọn **Trust** thì plugin mới được cài.
- Kiểm tra: gõ `/plugin`, thấy `engineering` đang bật. Gõ `/skills`, thấy 7 skill ở mục 1.
- Ai đã cài các skill này trên tài khoản claude.ai thì chúng có thể xuất hiện 2 lần trong Claude Code. Tắt bản trên tài khoản, giữ bản trong repo cho thống nhất.
