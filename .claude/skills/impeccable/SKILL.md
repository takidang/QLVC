---
name: "impeccable"
description: "Dùng khi Tai cần front web không bị 'AI slop' cho đồ án: dựng mới, critique, audit hoặc polish giao diện web theo bộ quy tắc rút gọn từ repo Impeccable (pbakaus/impeccable)."
---

# Impeccable (bản rút gọn cho Tai)

> **Nguồn gốc — đọc lại khi quên:**
> - Repo gốc: https://github.com/pbakaus/impeccable (tác giả Paul Bakaus, license Apache 2.0)
> - Docs: https://impeccable.style
> - Bản này rút gọn & dịch ý từ `skill/SKILL.src.md` và `skill/reference/craft-floor.md`, `audit.md`, `polish.md` tại commit `d631a88` (2026-10-08). Không phải bản chính thức.
> - Muốn bản đầy đủ (24 lệnh, 59 detector rule, live mode): chạy `npx impeccable install` ở gốc project rồi `/impeccable init`. Khi đã cài bản chính thức thì dùng bản đó, bỏ skill này để tránh hướng dẫn chồng chéo.

Tuân thủ YAGNI/KISS/DRY: không thêm hiệu ứng, thư viện hay màn hình không được yêu cầu.

## 1. Ngữ cảnh trước khi vẽ

- Đọc `PRODUCT.md` và `DESIGN.md` nếu có. Chưa có `PRODUCT.md` mà làm màn hình mới → hỏi ngắn rồi viết: người dùng là ai, dùng để làm gì, bối cảnh sử dụng (ở đâu, ánh sáng, thiết bị), ràng buộc, giọng văn. Không tự bịa thông tin còn thiếu.
- `DESIGN.md` ghi hệ thống thị giác: palette token, bộ font, spacing, radius, motion. Token định nghĩa một chỗ.
- **Brief thắng.** Tai đã chốt font/màu/phong cách thì theo, kể cả khi trái với quy tắc dưới đây.
- **Refine giữ nguyên, redesign thay hẳn.** Sửa nhỏ thì giữ bản sắc, copy, hành vi cũ. Làm lại thì chọn một thế giới thị giác mới, không vá nửa vời lên giao diện cũ.

## 2. Chọn mode theo màn hình (không theo sản phẩm)

- **Persuade** — landing, pricing: thu hút và dẫn tới hành động. Thiết kế chính là sản phẩm.
- **Operate** — app, dashboard, admin, form, settings: dễ quét, nhất quán, đúng thói quen nền tảng. Thương hiệu nằm ở chi tiết.
- **Read** — docs, bài viết, hướng dẫn: cấu trúc để hiểu, rồi làm trải nghiệm đọc dễ chịu.
- **Experience** — portfolio, gallery: nội dung dẫn dắt, giao diện lùi lại.

## 3. Từ chối các mặc định của AI (trừ khi brief yêu cầu)

Khung trang:
- Lưới card cùng kích thước dạng icon + tiêu đề + text làm cấu trúc trang. Card lồng card: luôn sai.
- Template hero-metric: số to, nhãn nhỏ, vài stat phụ, màu nhấn.
- **Eyebrow/kicker nhỏ phía trên heading: cấm hẳn.**
- Đánh số section 01/02/03 khi thứ tự không mang thông tin.
- Modal cho việc không cần ngắt mạch.

Bề mặt:
- Chữ gradient (nhấn bằng weight/size). Gradient tím→xanh.
- Glass/blur chỉ để trang trí.
- Viền trái/phải màu dày >1px trên card, list, alert.
- Bóng cứng `4px 4px 0` khi không thực sự là neobrutalism.
- Sparkline, progress ring, khối bo góc bóng mờ đứng thay nội dung.
- Mono làm 'trang phục kỹ thuật' thay vì cho code/số liệu.
- Inter/Roboto/Arial/system font làm display. Chọn font có cá tính hợp sản phẩm, self-host, chỉ tải weight dùng.
- Emoji/ký tự unicode thay icon. Dùng một bộ icon thật, cùng nét và độ dày.
- Nền #000/#fff thuần; chữ xám trên nền màu (pha từ hue của nền).
- Sáng/tối chọn theo thói quen ngành. Chọn theo bối cảnh dùng.
- Card radius giữ 12–16px; pill chỉ cho control nhỏ. Độ nổi khai báo một kiểu: border hoặc shadow, không cả hai.
- Nền sọc/lưới, SVG kiểu vẽ tay nguệch ngoạc khi không có lý do từ thế giới sản phẩm.
- Số liệu, lời quảng cáo bịa. Giá trị minh hoạ phải ghi rõ là minh hoạ.

## 4. Sàn chất lượng (kiểm trên bản đã build)

- **Contrast:** body/placeholder ≥ 4.5:1, chữ lớn ≥ 3:1.
- **Spacing:** nhóm chặt, tách nhóm rộng; khoảng trên heading lớn hơn khoảng dưới.
- **Type:** body 65–75ch, display tối đa 6rem, tracking không dưới -0.04em (thường -0.02 đến -0.03em), bậc size/weight rõ. Chạy copy thật ở mọi breakpoint, sửa chỗ tràn chữ.
- **Shadow:** có offset và blur mềm; halo màu không offset là trang trí.
- **Motion:** một khoảnh khắc có chủ đích, không fade-in giống nhau cho mọi section. Ease-out, trạng thái mặc định đã hiển thị. Tôn trọng `prefers-reduced-motion`.
- **State:** hover, focus bàn phím, disabled, loading, error, empty.
- **Bề mặt trình duyệt:** theme cả text selection, caret, scrollbar, focus ring, underline offset, số tabular trong bảng.
- **Copy:** dùng ngôn ngữ của sản phẩm. Nút nói rõ hành động; lỗi nêu vấn đề và cách khắc phục.
- **Đủ yêu cầu:** mọi yêu cầu trong brief có mặt và tìm thấy trong vài giây.

## 5. Lệnh Tai hay gọi

- **build / làm màn hình X:** mục 1 → 2 → build → kiểm mục 4 → cho xem.
- **critique:** review UX: phân cấp thị giác, độ rõ ràng, tải nhận thức, cảm xúc. Chấm điểm từng mục, nêu vấn đề ưu tiên cao nhất trước, kèm cách sửa cụ thể.
- **audit:** kiểm kỹ thuật 5 nhóm: Accessibility, Performance, Theming (token, dark mode), Responsive, Implementation integrity (có chỗ nào giả, chưa nối, hard-code). Báo cáo theo mức độ nghiêm trọng + điểm tốt + hành động đề xuất.
- **polish:** lượt cuối trước demo: chốt hệ thống → thu bằng chứng (screenshot desktop + mobile) → phân loại → sửa cả luồng (flow, layout/type, màu/ảnh/icon, tương tác/state, copy/code) → kiểm lại.
- **bolder / quieter / distill:** khuếch đại thiết kế nhạt / làm dịu thiết kế ồn / cắt về cốt lõi.

## 5a. Quy trình một trang (Tai hay quên lệnh: dẫn từng bước)

1. `build <màn>` → 2. `critique <màn>` → 3. `audit <màn>` → 4. gửi Kiệt thử, sửa một mẻ → 5. `polish` (một lần cho cả app, trước demo).

- Xong mỗi bước, kết thúc câu trả lời bằng **một dòng "Bước tiếp:"** nêu lệnh kế theo thứ tự trên (vd. "Bước tiếp: `impeccable audit màn đăng nhập`"). Không tự chạy bước kế khi Tai chưa bảo.
- Tai nói **"chưa ổn", "chưa đẹp", "kỳ kỳ"** mà không nói rõ: hỏi lại một câu kèm gợi ý, chọn lệnh hợp nhất với điều mình thấy trên màn:
  - `bolder`: nhạt, phẳng, không có điểm nhấn
  - `quieter`: rối, nhiều màu, nhiều thứ tranh nhau
  - `distill`: thừa chi tiết, chữ, khung
  - `critique`: chưa rõ vì sao, cần chấm lại
- Tai không nhớ đang ở bước nào: xem `git log` của trang đó rồi nói bước hiện tại.

## 6. Kiểm có giới hạn, không lặp vô tận

Build xong → một lượt kiểm gộp (desktop + mobile cùng lúc) → sửa hết một mẻ → tối đa một lượt xác nhận nữa → dừng. Báo Tai ngắn gọn đã kiểm gì, sửa gì.