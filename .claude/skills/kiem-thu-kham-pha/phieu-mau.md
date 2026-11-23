<!-- Phiếu mẫu cho skill kiem-thu-kham-pha. Thay mọi <...>; mục 1–7 sửa ví dụ endpoint, BR cho đúng dự án. -->
# Phiếu: kiểm thử khám phá ("phá thử") hệ thống <TÊN DỰ ÁN> – CHỈ TÌM LỖI, KHÔNG SỬA CODE

Bạn là kiểm thử viên đóng vai kẻ phá. Ứng dụng đang chạy sẵn:
- Frontend: <URL frontend>
- Backend: <URL backend> (tài liệu API: <URL /docs nếu có>)
- Tài khoản thử: <tên đăng nhập từng vai trò> – mật khẩu <...>. Cách đăng nhập: <endpoint, body, cookie/token>.

Đọc trước: <CLAUDE.md, tài liệu nghiệp vụ, quy tắc bảo mật, tài liệu API>. Code ở <thư mục backend>, <thư mục frontend>.

## Luật
- **KHÔNG sửa** bất kỳ file nào trong `backend/`, `frontend/`, `docs/` (trừ file báo cáo bên dưới). Không đọc, in, chép `.env`. Không cài package mới. Không chạy `pytest`. Không tắt, khởi động lại backend/frontend.
- Không đăng nhập sai mật khẩu quá 4 lần liên tiếp cùng một tài khoản (<ngưỡng khoá> lần là khoá, làm hỏng các bước sau). Muốn thử khoá thì tạo tài khoản mới bằng vai trò quản trị rồi thử trên tài khoản đó.
- Script thử viết vào thư mục `kiem-thu-kham-pha/` trong thư mục hiện tại. Chạy Python bằng `py -3.12 -I -X utf8 <file>` (đã có `playwright` + Chromium; gọi API bằng `playwright.sync_api` `p.request.new_context(base_url=...)` hoặc `urllib`; KHÔNG có `httpx`, không cài). Không dùng `.venv` của backend.
- Commit báo cáo + script trên nhánh hiện tại. Không push, không mở PR.

## Việc cần thử (mỗi mục ít nhất vài ca, ghi rõ ca nào ĐẠT, ca nào LỖI)
1. **Phân quyền / IDOR qua API**: mỗi vai trò gọi endpoint của vai trò khác (vd `taixe` gọi `/api/don`, `/api/chuyen/{id}/quyet-toan`, `/api/tam-ung`; `dieuphoi` gọi `/api/phai-thu/da-thu`, `/api/bang-gia`). Tài xế gọi `/api/toi/chuyen/{id}` và quét/chi phí/sự cố trên chuyến **không phải của mình** (tạo thêm tài xế + chuyến bằng `dieuphoi`/`quanly` nếu cần). Mong đợi: 403 hoặc 404, không lộ dữ liệu.
2. **Dữ liệu nhập bừa** (qua API và qua giao diện): số âm, 0, số rất lớn (1e15, 10^19 vượt BIGINT), id trong URL rất lớn, trang=10^18, số thập phân ở chỗ cần số nguyên (tiền, kg), chuỗi rỗng, chuỗi 10.000 ký tự, emoji, `<script>alert(1)</script>`, `' OR 1=1 --`, ngày sai (30/02, năm 0, 1900, 3000, 9999), giờ khởi hành trong quá khứ. Mong đợi: 422/400 với thông báo tiếng Việt, không 500, không lưu rác, XSS không chạy trên giao diện.
3. **Thao tác lặp / tranh chấp**: gửi cùng request 2–10 lần song song (tạo đơn, ghép đơn, chốt chuyến, tạo tạm ứng vượt định mức khi gửi song song, duyệt chi phí, quét cùng mã, đánh dấu đã thu). Mong đợi: không tạo trùng, không vượt định mức (BR-53), trạng thái không sai.
4. **Sai trạng thái**: gọi hành động không hợp lệ với trạng thái hiện tại (ghép vào chuyến đã chốt, huỷ chuyến đang chạy, quét giao khi chưa lấy, sửa chi phí đã duyệt, quyết toán chuyến chưa hoàn thành, sửa tạm ứng sau quyết toán). Mong đợi: 409/422 kèm mã BR.
5. **Upload**: ảnh chi phí/sự cố/ảnh đại diện với file không phải ảnh đổi đuôi .jpg, file rỗng, file > giới hạn, tên file `../../x.jpg`, SVG có script. Mong đợi: bị từ chối, không ghi ra ngoài thư mục lưu.
6. **Tra cứu công khai** `/api/tra-cuu`: sai mã/sai SĐT cho cùng thông báo; sai 11 lần trong 1 phút → 429.
7. **Giao diện** (Playwright, màn 1440 px và điện thoại 390 px): bấm nhanh hai lần nút lưu/ghép/chốt, F5 giữa chừng, nút Back trình duyệt, mở hai tab cùng sửa một đơn, mở thẳng URL trang của vai trò khác khi đăng nhập `taixe`. Ghi lại màn trắng, lỗi console, chữ tràn, nút không phản hồi.

## Báo cáo
Viết `kiem-thu-kham-pha/bao-cao.md` bằng tiếng Việt:
- Bảng tổng: mục | số ca | đạt | lỗi.
- Mỗi lỗi: **mức** (Nghiêm trọng: lộ/sửa dữ liệu trái quyền, mất tiền, 500 / Vừa: sai nghiệp vụ, trạng thái sai / Nhẹ: giao diện, câu chữ), **cách tái hiện** (request hoặc các bước, chép được để chạy lại), **kết quả thấy**, **mong đợi**, BR/quy tắc liên quan.
- Chỉ ghi điều đã chạy thật và thấy tận mắt; không đoán. Cái gì chưa thử được thì ghi "chưa thử" và lý do.
