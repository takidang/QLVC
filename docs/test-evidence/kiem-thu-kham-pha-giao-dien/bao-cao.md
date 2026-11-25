# Kiểm thử khám phá giao diện Pixel – 25/11/2026

Làm theo skill `kiem-thu-kham-pha`. Nhánh `tai/kiem-thu-kham-pha-2` (tách từ `tai/kiem-tra-truoc-bao-cao`, nên mang theo 14 lỗi backend đã sửa ở vòng 23/11). Chạy trên CSDL thử `qlvc_xem` của Tài, frontend và backend chạy từ worktree Pixel (`tai/pixel-note-loi`).

- **Rà tĩnh** (Claude Code): bảng phân quyền 100 route đúng; `npm audit` 0 lỗ hổng. Chưa chạy `pip-audit` (chưa cài trong `.venv`, chờ Tài đồng ý).
- **Phá thử** (agy, Gemini 4 Neon high, phiếu 35): viết 10 script Playwright trong `script/`. agy không chạy được shell nên Claude Code đọc lướt (chỉ gọi localhost, chỉ ghi file kết quả JSON) rồi chạy: `py -3.12 -I -X utf8 script/giao_dien_NN_*.py`. Log từng script ở `ket-qua/`.
- Vòng này không có lỗi backend mới: mọi lỗi thật đều ở frontend.

## 1. Tổng hợp

Script ghi 151 ca: 54 đạt, 97 bị đánh dấu lỗi. Sau khi tái hiện từng nhóm bằng tay: **5 lỗi thật (đã sửa)**, **2 việc để sau**, còn lại là báo nhầm.

| Mục | Ca | Đạt | Script báo lỗi | Lỗi thật | Báo nhầm | Để sau |
|---|---|---|---|---|---|---|
| 1. Quét trang × 4 vai trò × 2 cỡ | 83 | 17 | 66 | 1 (đăng nhập 390 px cuộn ngang) | 65 | 0 |
| 2. Nhập bừa qua giao diện | 12 | 7 | 5 | 0 | 5 | 0 |
| 3. Bấm lặp, đóng dấu | 9 | 7 | 2 | 0 | 2 | 0 |
| 4. Hộp thoại | 10 | 4 | 6 | 2 (Esc không đóng, nền cuộn được) | 2 | 2 (focus trap, hộp "Thêm tuyến" 390 px) |
| 5. Chuyển trang, tải chậm, mạng lỗi | 5 | 0 | 5 | 1 (bốn ca CT01–04 cùng một nguyên nhân: `filter` còn lại sau hiệu ứng mờ-hiện) | 1 (CT05) | 0 |
| 6. Xếp hàng lên xe | 9 | 4 | 5 | 0 | 5 | 0 |
| 7. Chuông, popover, menu | 6 | 4 | 2 | 0 (cùng nguyên nhân với mục 5; hai ca script hết thời gian chờ, đã tự đo lại) | 2 | 0 |
| 8. Phân quyền, phiên | 6 | 3 | 3 | 1 (hết phiên không về đăng nhập) | 2 | 0 |
| 9. Phong cách, trợ năng | 6 | 3 | 3 | 0 | 3 | 0 |
| 10. Hiệu năng (chỉ đo) | 5 | 5 | 0 | 0 | 0 | 0 |
| **Cộng** | **151** | **54** | **97** | **5 lỗi thật** | **87** | **2** |

Số ca và số đạt lấy từ dòng "TỔNG KẾT MỤC" trong log từng script. Cột "Lỗi thật" đếm theo nguyên nhân gốc, không theo số ca script báo (4 ca CT01–04 là một lỗi), nên 97 ca script đánh dấu = 8 ca thuộc 5 lỗi thật (1 + 2 + 4 + 1) + 87 báo nhầm + 2 để sau.

## 2. Lỗi thật đã sửa

| Mã | Mức | Thấy | Nguyên nhân | Sửa |
|---|---|---|---|---|
| PQ05 | Vừa | Xóa cookie rồi bấm menu tiếp: vẫn ở trang cũ với danh sách trống/lỗi, không về `/dang-nhap`. Thực tế gặp khi phiên 8 giờ (NFR-SEC-01) hết hạn lúc Điều phối đang làm việc. | `goi()` không xử lý 401. | `api/goi.ts`: 401 mã `CHUA_DANG_NHAP` (trừ `/api/auth/toi`) phát sự kiện `qlvc-het-phien`; `App.tsx` nghe, đặt `nd = null` (tự về đăng nhập) và hiện toast một lần. Đã thử lại: về `/dang-nhap`, 1 toast. |
| HT01 | Vừa | Nhấn Esc không đóng hộp thoại (Tạo đơn, Lập chuyến, Thêm xe). | Chỉ có xử lý bấm lớp nền `.nen-mo`. | `App.tsx`: Esc bấm hộ `.nen-mo` trên cùng (mọi hộp thoại đã đóng khi bấm nền). Đã thử: đóng. |
| HT05 | Nhẹ | Hộp thoại mở mà trang nền vẫn cuộn. | Không khóa cuộn. | `index.css`: `body:has(.nen-mo) { overflow: hidden }`. Đã thử: `hidden` khi mở, `visible` sau khi đóng. |
| PUB_DN_390 | Vừa | Trang đăng nhập 390 px cuộn ngang 11 px (ở Pixel). | `grid-template-columns: 1fr` bị nội dung đẩy rộng hơn màn. | `index.css`: `minmax(0, 1fr)`. Đã đo: `scrollWidth` = 390. |
| CT01–04, TB04 | Vừa | Script báo "kẹt filter blur". Nhìn không nhòe, nhưng hiệu ứng mờ-hiện hôm nay (`px-hien-mo`, fill-mode `both`) để lại `filter: blur(0)` trên `main.trang > *`. `filter` làm phần tử thành khung chứa của mọi con `position: fixed`, nên popover "ĐƠN THẤT BẠI" bị kéo lệch (nguồn gốc lỗi "popover che menu trái"). | Lỗi do chính thay đổi loading hôm nay. | `phong-cach-pixel.css`: keyframe kết thúc `filter: none`, fill-mode `backwards`; popover đặt `left: 256px; right: 12px; max-width: 1100px` (chừa cột menu), màn dưới 900 px `left/right: 12px`. Đã đo popover: 1440 px → 292…1392, 1100 px → 256…1088, 390 px → 12…378, không che menu, không tràn. |

Frontend chưa có khung test tự động (không cài package mới khi chưa hỏi), nên các sửa trên được kiểm bằng Playwright thật như ghi ở cột "Sửa" (script xác minh nằm trong lịch sử phiên, không đưa vào repo).

## 3. Báo nhầm (đã tái hiện, không phải lỗi)

| Mã (số ca) | Script báo | Kết luận |
|---|---|---|
| m01 `menu-tk-ds` ở 390 px (38) | `nav.menu-tk-ds` tràn khung (right 428 > 390) | Menu tài khoản đang đóng (`details` đóng vẫn có hình học); trang không cuộn ngang. |
| m01 "chồng `a(A)`" ở 1440 px (27) và TN01, TN04 | Hai liên kết "A" chồng nhau | Trang không có liên kết nào chữ "A"; không tái hiện được. |
| F02, F06, F07, F10, F11 | "Chữ lỗi bị tràn/cắt" | Script đo `scrollWidth` của ô nhập chứa chuỗi 10.000 ký tự và của toast ẩn. Thông báo lỗi tiếng Việt hiện đúng. |
| BL03, BL09 | Nút Lưu không khóa, đóng dấu nhiều lần, 0 POST | Script bấm cưỡng bức trên hộp lỗi. Bấm đúp thật (`dblclick`) chỉ gửi 1 POST và tạo đúng 1 khách. |
| HT02 | Bấm ngoài không đóng | Script bấm đúng giữa hộp thoại. Bấm góc lớp nền thì đóng. |
| HT06, TB04 1100/390 | Hết thời gian chờ | Lỗi script (không bấm được nút). TB04 đã tự đo lại ở mục 2. |
| CT05 | Màn trắng khi chặn 30% `/api/**` | Mẫu `**/api/**` của Playwright chặn cả module nguồn `/src/api/*.ts`. Chặn đúng `/api/` của máy chủ: 4 trang vẫn hiện, báo lỗi tại chỗ. |
| XH03, XH05, XH06 | Khối hàng tràn ngoài thùng | Script đo sai phần tử nhỏ; ảnh xếp đầy khoang đúng, hàng nằm trọn trong thùng. |
| PQ04 | Quản lý thấy nút "Quyết toán" | Script khớp nhầm tab "Chờ quyết toán"; trang dùng `chiXem` (`ghiDuoc = !chiXem && …`). |
| PQ06 | Back sau đăng xuất lộ trang cũ | URL là `about:blank`, không lộ nội dung. |
| TN05 | Ô "Tìm chung" không có viền focus | Viền focus nằm ở khung bao `.tim-o:focus-within`. |

## 4. Để sau

| Mục | Ghi chú |
|---|---|
| HT03 focus trap hộp thoại | Tab thoát khỏi hộp thoại ra nền (trợ năng). Có khoảng 13 hộp thoại viết riêng; nên làm một thành phần hộp thoại dùng chung rồi mới thêm bẫy focus. Không sửa lẻ từng chỗ. |
| HT07 hộp "Thêm tuyến" ở 390 px | Script không mở được hộp, chưa xác minh. |
| Thanh menu dưới ở 390 px | Nhãn nhóm "VẬN HÀNH" xuống dòng và "DANH MỤC" bị cắt mép phải (quan sát từ ảnh). Nhẹ, thẩm mỹ. |
| `pip-audit` | Chờ Tài đồng ý cài vào `.venv`. |

## 5. Hiệu năng cảm nhận (mục 10)

Đo trên 5 trang nặng nhất bằng Chromium trên máy này: 60 fps cả khi để yên và khi cuộn, khung hình dài nhất 16,8 ms, 0 tác vụ dài (>50 ms), DOM 623–1.511 phần tử, 1–2 animation đang chạy. Chưa thấy hiệu ứng nào cần tối ưu trên máy này. Nếu Tài thấy giật ở trang hoặc máy cụ thể, cho biết trang đó để đo lại. Số liệu: `ket-qua/hieu_nang_10.json`.
