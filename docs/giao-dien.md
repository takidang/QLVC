# Giao diện v2 – phần chung (00)

Tài chốt ngày 10/11/2026 trên nhánh `tai/thu-giao-dien-v2`. Mẫu xem được: mở `docs/mockup/giao-dien-v2.html` bằng trình duyệt (có thanh đổi 5 bộ màu ở đáy trang; dữ liệu trong mẫu là minh họa).

Trạng thái (10/11/2026): đã vào code phần chung (nền, nút, ô nhập, bảng, hộp thoại, nhãn), khung trang, **màn đăng nhập (01)** và **chuyến trong ngày (02)**. Các màn khác mới ăn theo phần chung, chưa có bố cục riêng. Mọi màu khai báo một chỗ bằng biến CSS ở đầu `index.css`, tên biến như bảng dưới. Bộ mặc định là "Đá xám xanh"; bộ khác bật bằng `data-mau="suong" | "cat" | "ngoc" | "oai"` trên `<html>` (nút đổi trong Cài đặt làm sau).

## Phong cách

Sạch, nhạt, nét mảnh: nền xám pha một sắc màu, các khối là tấm kính mờ viền sáng, chữ mực đậm. Màu chỉ dùng để báo trạng thái; **cam là màu nhấn duy nhất**, dành cho việc cần chú ý (trễ, quá tải).

## Năm bộ màu

Mỗi bộ chỉ đổi 7 biến nền và mực; bố cục, chữ, màu trạng thái giữ nguyên.

| Biến | Vai trò | Đá xám xanh | Sương xanh | Cát ấm | Ngọc xanh | Oải hương |
|---|---|---|---|---|---|---|
| `--da` | Nền trang | `#C4C8BE` | `#C3CAD3` | `#D2CABB` | `#BFCBC8` | `#CAC6CF` |
| `--sang1` | Vệt sáng nền 1 | `#E6E8E1` | `#E6EAEF` | `#EEE9DF` | `#E3EBE9` | `#EAE7EE` |
| `--sang2` | Vệt sáng nền 2 | `#D3D7CC` | `#D2D9E1` | `#DDD6C8` | `#CFDAD7` | `#D8D4DE` |
| `--muc` | Chữ chính, nút chính | `#1B2420` | `#172030` | `#261F17` | `#14231F` | `#211D29` |
| `--phu` | Chữ phụ | `#47524B` | `#44505F` | `#574D40` | `#3F524D` | `#4F4959` |
| `--o-liu` | Khối nhấn (thẻ chuyến đang chạy trên điện thoại) | `#56624A` | `#3F5673` | `#6B5540` | `#2F5F58` | `#54486E` |
| `--cam` | Màu nhấn: cần chú ý | `#C2410C` | `#C2410C` | `#B4380F` | `#C2410C` | `#C2410C` |

Nền trang vẽ bằng hai vệt sáng tròn trên `--da`:

```css
background:
  radial-gradient(900px 520px at 80% 6%, var(--sang1) 0%, transparent 62%),
  radial-gradient(700px 520px at 6% 34%, var(--sang2) 0%, transparent 66%),
  var(--da);
```

## Màu dùng chung cho cả năm bộ

| Biến | Giá trị | Dùng cho |
|---|---|---|
| `--kinh` | `rgb(250 250 247 / 62%)` + `backdrop-filter: blur(18px)` | Tấm kính: khung nổi, thẻ |
| `--kinh-dac` | `rgb(250 250 247 / 86%)` | Khung bảng (đặc hơn cho dễ đọc) |
| `--vien-sang` | `rgb(255 255 255 / 70%)` | Viền tấm kính |
| `--vien` | `--muc` ở 12% | Đường kẻ bảng, viền nút |
| `--chay` | `#1F6F8B` | Đang chạy, điểm dừng đang tới |
| `--chot` | `#6A55B8` | Đã chốt |
| `--xong` | `#2F7D4F` | Hoàn thành, Đã quyết toán |
| `--do` | `#B3261E` | Sự cố, chồng lịch, giao thất bại |
| `--xam` | `#6B736E` | Đang lập, Hủy |

## Nhãn trạng thái chuyến

Viên thuốc nền trắng mờ, chữ mực, **biểu tượng mang màu và có hình riêng** (vẫn phân biệt được khi máy chiếu nhạt màu).

| Trạng thái | Biểu tượng | Màu |
|---|---|---|
| `LAP` Đang lập | vòng nét đứt | `--xam` |
| `DA_CHOT` Đã chốt | vòng có chấm giữa | `--chot` |
| `DANG_CHAY` Đang chạy | vòng tô nửa | `--chay` |
| `HOAN_THANH` Hoàn thành | vòng đặc có dấu tích | `--xong` |
| `DA_QUYET_TOAN` Đã quyết toán | như Hoàn thành, **nhãn tô đặc** `--xong`, chữ trắng | `--xong` |
| `HUY` Hủy | vòng có dấu x; dòng trong bảng gạch ngang, chữ phụ | `--xam` |
| Cờ Trễ | đồng hồ, nhãn tô đặc, chữ trắng | `--cam` |
| Cờ Chồng lịch, Sự cố | tam giác cảnh báo, nhãn tô đặc, chữ trắng | `--do` |

## Chữ

- **Be Vietnam Pro**, tự host ở `frontend/public/fonts` (woff2, giấy phép OFL, tập ký tự latin + vietnamese), độ đậm 300 / 400 / 500 / 600.

## Màn đăng nhập (01)

Cả trang chia đôi (không khung nổi): trái là form trên nền trang (rộng tối đa 400 px, giữa cột) gồm tiêu đề, hai ô nhập có nhãn phía trên, câu lỗi nền đỏ nhạt, nút chính bo tròn có mũi tên; phải là ảnh xe tải cao hết trang, bo 20 px, phủ màu `--o-liu` đậm dần xuống dưới, có một dòng mô tả hệ thống. Dưới 760 px ảnh thành dải trên đầu (cao 24% màn, từ 96 đến 190 px), form bên dưới. Viền ô nhập `--muc` 62% (≥ 3:1 với nền trang); báo lỗi xong focus về ô mật khẩu. Hành vi và câu lỗi giữ nguyên như UC-01.

**Mỗi lần mở web** (`frontend/src/nen.ts`) chọn ngẫu nhiên một trong hai ảnh, kèm bộ màu hợp ảnh, áp cho cả app:

| Ảnh (`frontend/public/anh/`) | Bộ màu | Nguồn (Unsplash, giấy phép Unsplash) |
|---|---|---|
| `dang-nhap-hoang-hon.webp`: thùng xe, trời xanh chuyển cam | Sương xanh (`suong`) | Caleb Ruiter, <https://unsplash.com/photos/EmEQ6kK_5P0> |
| `dang-nhap-luot-ngang.webp`: đầu kéo lướt ngang, tông be xám | Cát ấm (`cat`) | Roberto, <https://unsplash.com/photos/9Ayfcdmu2YE> |

Khi có nút đổi bộ màu trong Cài đặt, lựa chọn đã lưu của người dùng phải thắng lựa chọn ngẫu nhiên.
- Tiêu đề trang 46 px, đậm 300, giãn chữ -0.03em. Số liệu lớn 32 px, đậm 300.
- Chữ thường 14 px (điện thoại 15 px); chữ phụ 12.5–13.5 px.
- Giờ, số, mã, biển số: `font-variant-numeric: tabular-nums`.

## Khung và thành phần

- **Thanh trên:** logo trái, menu viên thuốc ở giữa (tối đa 5–6 mục, gộp mục danh mục), người dùng bên phải. Không có menu trái.
- **Đầu trang "Chuyến hôm nay":** tiêu đề to, hàng vạch đứng (mỗi vạch một chuyến theo giờ đi), số liệu, nút chính; bên phải là khung kính "Cần chú ý". Các màn danh mục dùng phần đầu thấp hơn.
- **Bảng:** nằm trong khung kính đặc, đường kẻ mảnh, không tô nền tiêu đề cột; cột Giờ đi đứng đầu; tab lọc trạng thái dạng viên thuốc kèm số đếm.
- **Nút:** bo tròn hết cỡ. Nút chính nền `--muc` chữ trắng; nút phụ nền trắng mờ viền `--vien`.
- **Điểm dừng:** dãy đoạn ngang cao 5 px: đã xong `--muc`, đang tới `--chay`, thất bại `--do`, chưa tới mực 16%.
- **Độ đầy:** thanh 5 px + số %; trên 95% đổi sang `--cam`.
- **Biển số:** khung viền mảnh; chưa gán thì viền nét đứt.
- **Bo góc:** tấm kính 16 px, thẻ chính điện thoại 20 px, nhãn / nút / menu bo tròn hết cỡ. Phân lớp bằng viền, không đổ bóng.
- **Điện thoại 360 px:** chuyến đang chạy là khối `--o-liu` chữ trắng với nút trắng cao 52 px; lịch trình dạng dòng thời gian; menu dưới là viên thuốc nổi nền `--muc`.

## Khung trang và màn Chuyến trong ngày (02), đã vào code

- **Khung trang** (`KhungTrang` trong `App.tsx`): tên hệ thống bên trái (tạm "Quản lý vận tải", chờ tên mới), menu viên thuốc ở giữa, tên người dùng + vòng tên tắt + Đăng xuất bên phải. Mục có `nhom: true` trong `TRANG_CON` (Xe, Tài xế, Nút, Tuyến) gộp vào mục xổ xuống "Danh mục". Chỉ có một mục (tài xế) thì ẩn menu.
- **Điều phối đăng nhập vào thẳng màn Chuyến**, mặc định lọc **hôm nay**; nút "Mọi ngày" trả về danh sách đủ mọi ngày, phân trang như trước.
- **Xem theo ngày:** lấy cả ngày một lượt (tối đa 100 chuyến), xếp theo giờ đi, lọc trạng thái tại chỗ nên tab có số đếm. Đầu trang có dải vạch (mỗi vạch một chuyến), 4 số đếm, khung "Cần chú ý" (cờ Trễ, Sự cố, Đơn thất bại, Chồng lịch; bấm vào mở chi tiết chuyến).
- **Bảng:** Giờ đi (giờ đến nhỏ bên dưới, đổi cam khi trễ) · Tuyến + mã chuyến · biển số + tài xế · Điểm dừng (mỗi đoạn một điểm, API chỉ trả số điểm xong / tổng nên chưa tô được điểm thất bại) · Độ đầy · nhãn trạng thái + cờ. Bấm cả dòng để mở chuyến.
- **Nhãn** dùng chung ở `frontend/src/nhan.tsx` (`<Nhan loai="DANG_CHAY">`, nhận mã trạng thái chuyến hoặc mã cờ). Cờ "Chưa quyết toán" là nhãn thường, không tô đặc.
- **Lịch xe theo giờ** (`LichGio.tsx`): mỗi xe một hàng, mỗi chuyến một thanh từ giờ đi tới giờ kết thúc dự kiến, màu theo trạng thái (đang lập nét đứt, đã chốt tím nhạt, đang chạy xanh, trễ cam, xong mực, hủy gạch ngang), có vạch "bây giờ". Bấm thanh để mở chuyến.
- **Bản đồ tuyến trong ngày** (`BanDoNgay.tsx`, tải riêng): ghép `tuyen_id` của chuyến với danh sách tuyến và tọa độ nút; đường nối thẳng các nút, màu theo trạng thái chuyến "nóng" nhất của tuyến. Chưa có vị trí xe (API chưa trả vị trí quét gần nhất).
- **Khung "Cần chú ý" khi xem hôm nay** có thêm: số đơn thất bại chờ xử lý (`GET /api/don/can-xu-ly`), giấy tờ xe và GPLX hết hạn trong 30 ngày (tính từ danh sách xe, tài xế; tạm thay UC-27, số 30 là mặc định của CFG-02 vì điều phối không đọc được cấu hình).
- Mẫu tham khảo 02 (ngoài repo, `tham-khao-ui/02-bang-chuyen-trong-ngay`): lấy thanh menu trên, tab lọc có số đếm, bảng trong khung, phần đầu có số liệu + nút chính, lịch theo giờ, bản đồ.
- Biểu đồ doanh thu, nhiên liệu, hiệu suất, vị trí xe: chờ backend, danh sách ở `..\ghi-chu6-11-10-backend-can-them-cho-giao-dien-v2.md` (ngoài repo).

## Màn Chi tiết chuyến (03), đã vào code

- **Đầu trang:** tên tuyến làm tiêu đề lớn (46 px), dưới là mã chuyến · mã tuyến, nhãn trạng thái và các cờ; nút Chốt / Mở chốt / Hủy bên phải.
- **Khung tổng:** hàng trên Xe (biển số khung viền), Tài xế, Khởi hành, Kết thúc dự kiến (đang trễ thì ghi "Dự kiến xong (đang trễ)" màu cam theo BR-73); hàng dưới Tải trọng và Thể tích (số + thanh 5 px, trên 95% cam), Lấp đầy, Lãi dự kiến (số lớn 32 px).
- **Lưới hai cột:** trái là **Lịch trình dọc** (chấm: xong đặc mực, đang tới vòng xanh, thất bại đỏ, bỏ nét đứt; giờ ETA, giờ quét, "Trễ 2 giờ 5′" / "Sớm 4′") và **Dòng thời gian** (mới nhất trên, khung cuộn); phải là bản đồ, khối **Tiền** (doanh thu − định mức − lương = lãi dự kiến, tạm ứng, km) và **Sự cố**.
- **Đơn của chuyến** trong khung bảng, trạng thái đơn dùng nhãn có hình như màn Đơn hàng.
- Màn Chuyến trong ngày: cờ Trễ chỉ tô cam thanh lịch và đường bản đồ khi chuyến **còn đang chạy**; chuyến đã xong giữ màu trạng thái, nhãn Trễ vẫn ở bảng.

## Màn Tài xế điện thoại (07), đã vào code

- **Chuyến của tôi:** dòng ngày, tiêu đề 32 px, thẻ chọn Cần làm / Đã xong. Chuyến **đang chạy** là khối `--o-liu` chữ trắng (mã, nhãn, tuyến, biển số, giờ, số đơn) với nút trắng cao 52 px "Mở lịch trình, quét mã"; chuyến khác là dòng gọn: giờ đi | tuyến + mã · biển số · số đơn | nhãn.
- **Lịch trình chuyến:** khối chính đậm khi đang chạy (nhạt khi chờ chạy / đã xong): tuyến, biển số, giờ, lương chuyến, dải đoạn tiến độ (xong trắng, đang tới cam nhạt, thất bại đỏ nhạt), **Điểm kế tiếp** (việc, giờ dự kiến, nơi, địa chỉ, kiện, mã đơn) và nút "Gọi …". Dưới là khối Lấy hàng (quét QR), Bắt đầu / Kết thúc chuyến, rồi lịch trình dạng dòng thời gian (mỗi điểm một thẻ; điểm đã xong thu gọn hai dòng; điểm đang tới viền xanh), cuối cùng là Chi phí.
- Không làm menu dưới như mockup: tài xế chỉ có một màn, quét mã nằm ngay trong lịch trình.

## Trang tra cứu đơn cho khách (UC-28), đã vào code

- Đường dẫn công khai `/tra-cuu` (không đăng nhập); `?ma=DH-…` điền sẵn mã đơn để điều phối gửi link cho khách. Màn đăng nhập có dòng "Khách hàng? Tra cứu đơn hàng".
- Điện thoại: một cột tối đa 480 px; tiêu đề 32 px, ô mã đơn, ô 4 số cuối điện thoại (chỉ nhận chữ số), nút Tra cứu cao 48 px. Từ 900 px: chia đôi như màn đăng nhập, cột trái là form và kết quả, phải là ảnh xe (cùng ảnh và bộ màu ngẫu nhiên của `nen.ts`).
- Kết quả: form thu thành một dòng "mã · số cuối · Tra đơn khác"; trạng thái hiện tại là dòng chữ lớn bằng **lời cho khách** (vd "Giao chưa thành công, đang chờ giao lại", không dùng từ nội bộ "ghép", "thất bại"); dưới là các mốc dạng dòng thời gian, mới nhất trên cùng và ghi "Hiện tại". Có kết quả thì focus chuyển tới dòng trạng thái.
- Lỗi: 404 hướng dẫn kiểm lại mã trên phiếu và 4 số của người gửi hoặc người nhận; 429 hiện câu của máy chủ.

## Còn phải quyết khi làm vào code

- Nút đổi bộ màu trong Cài đặt (Tài làm sau).
- Thanh `<meter>` tải / thể tích ở chi tiết chuyến còn màu mặc định của trình duyệt (làm ở 03).
- Thử trên máy chiếu trước buổi demo: tông nhạt, nét mảnh dễ bạc màu.
