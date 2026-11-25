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
- **Cần chú ý cao suốt (Tài góp ý 12/11):** cột phải 460 px chỉ có Cần chú ý, cao bằng cả khối đầu + lịch xe bên trái (lịch xe chuyển vào cột trái), chữ to hơn một bậc (15 / 13 px); dưới 1000 px thứ tự số liệu → Cần chú ý → lịch xe. Mục dưới đây là bố cục trước đó.
- **Bố cục màn Chuyến (Tài góp ý 11/11):** hàng trên hai khối cao bằng nhau: trái là tiêu đề + số liệu + nút Lập chuyến, phải (420 px) là Cần chú ý (cuộn trong khung, thanh cuộn mảnh). Dưới là **lịch xe theo giờ trải hết bề rộng**, rồi bảng chuyến. Khung trang rộng tối đa 1680 px. Dưới 1000 px một cột.
- **Khối đầu "điện ảnh" (impeccable bolder, Tài góp ý 12/11):** khối tiêu đề + số liệu dùng ảnh xe tải của màn đăng nhập (cùng ảnh, cùng bộ màu ngẫu nhiên của phiên, `nen.ts`) phủ màu `--o-liu` đậm dần sang trái, chữ trắng, nút Lập chuyến nền trắng, dải vạch đổi sang tông trắng. Ngày đang xem không có chuyến: câu "Chưa có chuyến nào khởi hành ngày này. Gần nhất có chuyến: ngày …" (lấy chuyến mới nhất từ API), bấm để chuyển ngày. Nền trang thêm vệt màu khối nhấn rất nhạt ở góc trên trái.
- **Bỏ bản đồ tuyến trong ngày** khỏi màn Chuyến (Tài: khó hiểu, các tuyến chung đoạn đè lên nhau, hai chuyến cùng tuyến chỉ thấy một đường). Bản đồ chỉ còn ở chi tiết chuyến.
- **Lọc trạng thái không làm nhảy trang:** khi xem theo ngày, bảng vẽ đủ mọi chuyến của ngày, dòng khớp lọc lên đầu, dòng không khớp ẩn (`visibility: hidden`) nhưng giữ chỗ; bảng `table-layout: fixed` với độ rộng cột cố định nên cột không đổi kích cỡ.
- **Xem theo ngày:** lấy cả ngày một lượt (tối đa 100 chuyến), xếp theo giờ đi, lọc trạng thái tại chỗ nên tab có số đếm. Đầu trang có dải vạch (mỗi vạch một chuyến), 4 số đếm, khung "Cần chú ý" (cờ Trễ, Sự cố, Đơn thất bại, Chồng lịch; bấm vào mở chi tiết chuyến).
- **Bảng:** Giờ đi (giờ đến nhỏ bên dưới, đổi cam khi trễ) · Tuyến + mã chuyến · biển số + tài xế · Điểm dừng (mỗi đoạn một điểm theo `theo_doi.diem`: xong mực, đang tới xanh, thất bại đỏ, kèm "· 1 thất bại") · Độ đầy · nhãn trạng thái + cờ; cờ Trễ ghi số phút (`theo_doi.tre_phut`, vd "Trễ 3 giờ 21′"). Bấm cả dòng để mở chuyến. Ô tìm (mã chuyến, biển số, tài xế; `tu_khoa`, chờ 300 ms sau khi ngừng gõ) dùng cho cả xem theo ngày và mọi ngày.
- **Nhãn** dùng chung ở `frontend/src/nhan.tsx` (`<Nhan loai="DANG_CHAY">`, nhận mã trạng thái chuyến hoặc mã cờ). Cờ "Chưa quyết toán" là nhãn thường, không tô đặc.
- **Lịch xe theo giờ** (`LichGio.tsx`): mỗi xe một hàng, mỗi chuyến một thanh từ giờ đi tới giờ kết thúc dự kiến, màu theo trạng thái (đang lập nét đứt, đã chốt tím nhạt, đang chạy xanh, trễ cam, xong mực, hủy gạch ngang), có vạch "bây giờ". Bấm thanh để mở chuyến.
- **Khung "Cần chú ý" khi xem hôm nay** có thêm, lấy từ bảng cảnh báo UC-27 (`GET /api/canh-bao`): sự cố đang mở, chuyến trễ / chồng lịch của ngày khác, đơn chờ ghép đã quá hoặc sắp tới hạn (CFG-10), lượt quét thiếu GPS, giấy tờ xe và GPLX sắp hết hạn (CFG-02); cộng số đơn thất bại chờ xử lý (`GET /api/don/can-xu-ly`). Chuyến đã có trong danh sách ngày đang xem không lặp lại.
- Mẫu tham khảo 02 (ngoài repo, `tham-khao-ui/02-bang-chuyen-trong-ngay`): lấy thanh menu trên, tab lọc có số đếm, bảng trong khung, phần đầu có số liệu + nút chính, lịch theo giờ, bản đồ.
- Biểu đồ doanh thu, nhiên liệu, hiệu suất, vị trí xe: chờ backend, danh sách ở `..\ghi-chu6-11-10-backend-can-them-cho-giao-dien-v2.md` (ngoài repo).

## Màn Chi tiết chuyến (03), đã vào code

- **Đầu trang:** tên tuyến làm tiêu đề lớn (46 px), dưới là mã chuyến · mã tuyến, nhãn trạng thái và các cờ; nút Chốt / Mở chốt / Hủy bên phải.
- **Khung tổng:** hàng trên Xe (biển số khung viền), Tài xế, Khởi hành, Kết thúc dự kiến (đang trễ thì ghi "Dự kiến xong (đang trễ)" màu cam theo BR-73); hàng dưới Tải trọng và Thể tích (số + thanh 5 px, trên 95% cam), Lấp đầy, Lãi dự kiến (số lớn 32 px).
- **Xếp hàng lên xe** (`XepHang.tsx`, lấy ý từ ảnh mẫu load-planning nhưng không chia ô vị trí): hình xe tải nhìn ngang vẽ SVG; thùng lấp theo **thể tích** các đơn trên xe, mỗi khối một đơn (rộng theo % m³, một màu ba độ đậm, ghi mã và m³), vạch chia 25 %; dưới là thanh thể tích và tải trọng. Ghi rõ "không phải vị trí thật trong thùng". Chuyến **đang lập**: nửa phải là thẻ đơn chờ ghép hợp tuyến với nút "Ghép vào xe"; rê chuột / focus vào thẻ thì thùng hiện khối nét đứt và thanh sọc phần sẽ chiếm thêm, vượt sức chứa thì đổi cam kèm câu báo (BR-01, 02); bấm một khối để chọn và "Gỡ khỏi xe". Ghép / gỡ gọi API cũ, máy chủ vẫn kiểm mọi quy tắc. Chuyến khác: nửa phải là danh sách đơn trên xe kèm trạng thái. Bảng "Đơn chờ ghép" cũ thay bằng thẻ; bảng "Đơn đang ghép" giữ nguyên (gỡ nhiều đơn một lúc).
- **Lưới hai cột:** trái là **Lịch trình dọc** (chấm: xong đặc mực, đang tới vòng xanh, thất bại đỏ, bỏ nét đứt; giờ ETA, giờ quét, "Trễ 2 giờ 5′" / "Sớm 4′") và **Dòng thời gian** (mới nhất trên, khung cuộn); phải là bản đồ, khối **Tiền** (doanh thu − định mức − lương = lãi dự kiến, tạm ứng, km) và **Sự cố**.
- **Đơn của chuyến** trong khung bảng, trạng thái đơn dùng nhãn có hình như màn Đơn hàng.
- Màn Chuyến trong ngày: cờ Trễ chỉ tô cam thanh lịch và đường bản đồ khi chuyến **còn đang chạy**; chuyến đã xong giữ màu trạng thái, nhãn Trễ vẫn ở bảng.

## Chi tiết chuyến bố cục 2 (theo ảnh mẫu 03 Fleetlog, Tài duyệt 12/11)

- **Căn mép như ảnh mẫu 01 (Tài góp ý 12/11):** trang tràn hết bề rộng (khung trang không giới hạn bề rộng, chỉ có lề); cột trái cao suốt màn hình (sticky, danh sách cuộn bên trong); khối đầu (tên, nhãn, số liệu, nút, cảnh báo chồng lịch, nút kết thúc do sự cố, form hủy) là một khối có viền, mép trên thẳng với cột trái; các khối bên dưới cùng lề trái phải, khối cạnh nhau cao bằng nhau; hình xe ở Xếp hàng cao tối đa 260 px, canh trái.
- **Cột trái (300 px) "Chuyến ngày …":** các chuyến cùng ngày khởi hành dạng thẻ (mã + nhãn, nơi đi → nơi đến, dải điểm dừng theo `theo_doi.diem`, giờ đi → đến, biển số); chuyến đang xem tô đậm `--muc` chữ trắng; bấm thẻ khác là chuyển chuyến. Dưới 1100 px ẩn cột này, hiện lại "← Danh sách chuyến".
- **Đầu chi tiết:** tên tuyến 34 px, mã · mã tuyến, nhãn, cờ; một dòng số: kg / tải trọng, số điểm dừng, km tuyến (`GET /api/tuyen/{id}`), khởi hành, kết thúc (đang trễ thì cam, BR-73); nút Chốt / Mở chốt / Hủy bên phải.
- **Hàng bản đồ:** bản đồ lớn (đoạn đã đi nét liền, còn lại nét đứt) có chấm vị trí xe lúc quét gần nhất khi chuyến đang chạy (lấy `theo_doi.vi_tri` từ danh sách cùng ngày); bên phải là lịch trình dọc, dài thì cuộn trong khung.
- **Xếp hàng lên xe** cả bề rộng.
- **Xe & tài xế** (`KhoiXe.tsx`, thay "Vehicle Information" của ảnh mẫu, chỉ dữ liệu thật từ `GET /api/xe/{id}`, `GET /api/tai-xe/{id}`): biển số, tải trọng, thể tích, km đồng hồ; thanh "còn N ngày" tới hạn đăng kiểm, bảo hiểm, GPLX (đầy khi còn ≥ 1 năm; chấm xanh / cam ≤ 30 ngày / đỏ hết hạn), số điện thoại tài xế bấm gọi. Cạnh là khối Tiền; dưới là Dòng thời gian và Sự cố. Khối cạnh nhau cao bằng nhau.
- Không lấy từ ảnh mẫu: gợi ý tuyến AI, nhiệt độ, bảo dưỡng phanh / lốp (không có dữ liệu), màu xanh dương chủ đạo.

## Màn Tài xế điện thoại (07), đã vào code

- **Chuyến của tôi:** dòng ngày, tiêu đề 32 px, thẻ chọn Cần làm / Đã xong. Chuyến **đang chạy** là khối `--o-liu` chữ trắng (mã, nhãn, tuyến, biển số, giờ, số đơn) với nút trắng cao 52 px "Mở lịch trình, quét mã"; chuyến khác là dòng gọn: giờ đi | tuyến + mã · biển số · số đơn | nhãn.
- **Lịch trình chuyến:** khối chính đậm khi đang chạy (nhạt khi chờ chạy / đã xong): tuyến, biển số, giờ, lương chuyến, dải đoạn tiến độ (xong trắng, đang tới cam nhạt, thất bại đỏ nhạt), **Điểm kế tiếp** (việc, giờ dự kiến, nơi, địa chỉ, kiện, mã đơn) và nút "Gọi …". Dưới là khối Lấy hàng (quét QR), Bắt đầu / Kết thúc chuyến, rồi lịch trình dạng dòng thời gian (mỗi điểm một thẻ; điểm đã xong thu gọn hai dòng; điểm đang tới viền xanh), cuối cùng là Chi phí.
- Không làm menu dưới như mockup: tài xế chỉ có một màn, quét mã nằm ngay trong lịch trình.
- **Báo sự cố (UC-33):** khối Sự cố (của Kiệt) ở cuối trang; khối chính có nút viền "Gặp sự cố trên đường" nhảy thẳng tới khối này.

## Trang tra cứu đơn cho khách (UC-28), đã vào code

- Đường dẫn công khai `/tra-cuu` (không đăng nhập); `?ma=DH-…` điền sẵn mã đơn để điều phối gửi link cho khách. Màn đăng nhập có dòng "Khách hàng? Tra cứu đơn hàng".
- Điện thoại: một cột tối đa 480 px; tiêu đề 32 px, ô mã đơn, ô 4 số cuối điện thoại (chỉ nhận chữ số), nút Tra cứu cao 48 px. Từ 900 px: chia đôi như màn đăng nhập, cột trái là form và kết quả, phải là ảnh xe (cùng ảnh và bộ màu ngẫu nhiên của `nen.ts`).
- Kết quả: form thu thành một dòng "mã · số cuối · Tra đơn khác"; trạng thái hiện tại là dòng chữ lớn bằng **lời cho khách** (vd "Giao chưa thành công, đang chờ giao lại", không dùng từ nội bộ "ghép", "thất bại"); dưới là các mốc dạng dòng thời gian, mới nhất trên cùng và ghi "Hiện tại". Có kết quả thì focus chuyển tới dòng trạng thái.
- Lỗi: 404 hướng dẫn kiểm lại mã trên phiếu và 4 số của người gửi hoặc người nhận; 429 hiện câu của máy chủ.

## Trang Tổng quan (Quản lý, Kế toán), đã vào code

- Trang đầu sau đăng nhập của Quản lý và Kế toán (`/quan-ly/tong-quan`, `/ke-toan/tong-quan`, mục đầu menu). Chọn tháng (mặc định tháng này). Chỉ tính chuyến đã quyết toán (UC-26), tháng theo ngày khởi hành.
- **Hàng số liệu** của tháng: doanh thu (kèm số chuyến), chi phí chuyến, lương tài xế, chi phí cố định xe, lãi (lỗ thì màu cam).
- **Lưu ý** khi số liệu chưa đủ: số chuyến chạy xong chưa quyết toán, xe chưa nhập chi phí cố định tháng; Kế toán có link tới Quyết toán / Chi phí cố định.
- **Lãi theo tháng** (6 tháng tới tháng chọn): cột trên mốc 0, lãi đi lên màu `--bd-lai`, lỗ đi xuống màu `--bd-lo`; tháng chọn đậm hơn; rê chuột / Tab / chạm vào cột hiện doanh thu − chi phí − lương − cố định = lãi; có "Xem dạng bảng". Màn hẹp vẽ khung nhỏ hơn để chữ trục đủ to.
- **Lãi theo xe** của tháng: thanh ngang xếp từ lãi cao xuống, mốc 0 chung.
- **Hiệu suất xe** (UC-34): xe có chạy trong tháng, số chuyến (rỗng), lấp đầy trung bình dạng thanh, km, dầu thực tế / tham khảo, số chuyến chưa quyết toán; dòng cuối đếm xe không chạy.
- Màu biểu đồ `--bd-lai: #16799F`, `--bd-lo: #C2410C` đã chạy `validate_palette.js` (skill dataviz) trên nền khung sáng: đạt dải sáng, độ đậm màu, mù màu (ΔE 19,4), tương phản. Màu `--chay` của hệ thống bị nhạt quá cho mảng lớn nên biểu đồ dùng biến riêng. Biểu đồ vẽ SVG tay, không thêm thư viện.

## Màn Quyết toán (UC-24) và Công nợ (UC-25), đã vào code

- Chung một bố cục: danh sách bên trái trong khung kính (chuyến chờ / đã quyết toán; khách còn nợ, nhiều nợ trước), bấm để mở chi tiết bên phải; dưới 1000 px danh sách lên trên.
- **Quyết toán:** đầu chi tiết là mã + tuyến, biển số, tài xế; hàng số tóm tắt (doanh thu, chi phí đã duyệt kèm định mức, lương, lãi kèm dự kiến lúc chốt, chênh lệch tạm ứng); các khối Doanh thu, Chi phí so với định mức, Khoản chi tài xế khai (xét duyệt ngay trong dòng), Kết quả; form quyết toán trong khung riêng. Dòng tổng, dòng lãi trong bảng đậm.
- **Công nợ:** hàng số tổng nợ chưa thu, số khoản, số khách còn nợ; khung khoản của khách có tab Chưa thu / Đã thu; form đánh dấu đã thu trong khung riêng.
- Hành vi, quyền (Quản lý chỉ xem), câu lỗi giữ nguyên như Kiệt làm.

## Thư viện giao diện (Tài đồng ý cài 12/11/2026)

Theo gợi ý video Tài xem: không chuyển sang shadcn/ui (phải thêm Tailwind và viết lại mọi màn ngay trước demo); chỉ thêm hai gói nhỏ, ghi phiên bản cố định:

- **Sonner 2.0.8** (`frontend/src/thongBao.tsx`): `KhungThongBao` đặt ở gốc `App.tsx` (góc phải dưới, nền sáng, viền `--vien-dam`, bo 16 px, font của app); `<ThongBao chu={...} />` hiện thông báo **thành công** dạng toast tự biến mất, thay cho dòng chữ xanh giữa trang (lập chuyến, tạo / sửa / hủy đơn, chi phí cố định, công nợ, quyết toán, tạm ứng, chi phí và sự cố của tài xế). **Lỗi vẫn hiện tại chỗ**, cạnh chỗ cần sửa. Kết quả quét mã của tài xế vẫn hiện tại chỗ vì kèm cảnh báo.
- **NumberFlow 0.6.2**: mỗi trang tối đa một điểm động. Tổng quan: các số tiền chạy khi đổi tháng. Màn Chuyến: bốn số đếm chạy khi đổi ngày. Tự tắt khi máy bật giảm chuyển động.
- **Chuyển động báo trạng thái** (20/11, chỉ CSS, tắt hết khi giảm chuyển động): lớp nổi (menu tài khoản, chuông, tìm chung, hộp thoại) mở ra mờ dần + trượt 4 px trong 140–160 ms, đóng tức thời; nút lún `scale(0.98)` khi nhấn; màn tài xế bấm "Tới điểm" / "Gặp sự cố" thì thẻ đích nháy viền một lần 700 ms (`.vua-toi`); đổi Sáng / Tối trong Cài đặt làm mờ chéo 180 ms (`doiCheDo`, View Transitions). Không làm: hiện lần lượt từng dòng bảng, trượt cả trang khi chuyển menu, nhấp nháy liên tục trên nhãn cảnh báo, nâng thẻ khi rê chuột.
- **Đang tải**: khối biểu đồ / bảng ở Tổng quan giữ chỗ bằng nền `--mat-2` cao gần bằng khối thật (`.tq-cho`) để trang không nhảy khi số liệu về. Ô chọn ảnh dùng `ChonTep.tsx` (nút "Chọn ảnh", dòng "Chưa chọn ảnh / Đã chọn N ảnh"), không để chữ của trình duyệt theo ngôn ngữ máy.
- Không dùng: Vaul (để sau nếu form tài xế khó dùng), cmdk, Magic UI, Aceternity.
- Gói JS chính tăng từ khoảng 412 KB lên 536 KB (gzip 159 KB) sau khi thêm hai gói và các màn mới.

## Chuông thông báo và menu tài khoản (12/11/2026)

- **Menu tài khoản** (`MenuTaiKhoan.tsx`, bấm vòng tên tắt góc phải, mọi vai trò): họ tên, vai trò, **chọn bộ màu** (Ngẫu nhiên theo ảnh / 5 bộ màu), nút Đăng xuất. Bộ màu lưu trên trình duyệt (`localStorage` khóa `qlvc-bo-mau`, `nen.ts`), thắng bộ màu ngẫu nhiên. Đổi mật khẩu thêm vào đây khi backend có UC-35. (Dùng nút `aria-pressed` thay ô radio: radio ẩn trong `<details>` làm trình duyệt kiểm thử bị sập khi chọn.)
- **Chuông thông báo** (`ChuongThongBao.tsx`, **mọi vai trò**, UC-37 `GET /api/thong-bao`): danh sách mới trước, mỗi dòng có chấm mức độ (đỏ khẩn, cam cần làm, xám thông tin), tiêu đề (câu tiếng Việt từ máy chủ), nội dung phụ, giờ; nhãn "mới" cho thông báo sau lần mở chuông trước. Số trên chuông = số thông báo mới; mở chuông thì lưu mốc thời gian mới nhất vào trình duyệt (`qlvc-da-doc-<id người dùng>`). Bấm dẫn tới: chuyến → chi tiết chuyến (tài xế: chuyến của tôi; kế toán: Quyết toán), đơn → phiếu đơn (kế toán: Công nợ), tạm ứng treo → Tạm ứng, xe / tài xế → danh mục. Tải lại khi đổi trang và mỗi 2 phút; đóng khi bấm / Tab ra ngoài.

## Tìm chung (UC-36) và đổi mật khẩu (UC-35), giao diện (12/11/2026)

- **Ô tìm chung** (`TimChung.tsx`) trên thanh đầu, bên phải, mọi vai trò: gọi `GET /api/tim?q=` khi đủ 2 ký tự, chờ 250 ms sau khi ngừng gõ, hủy yêu cầu cũ. Kết quả xổ xuống theo nhóm (Chuyến, Đơn hàng, Xe, Tài xế, Khách hàng; ẩn nhóm rỗng), mỗi nhóm ghi "5 / tổng" khi có nhiều hơn 5. Bấm dẫn tới: chuyến → chi tiết chuyến (tài xế: chuyến của mình; kế toán: Quyết toán); đơn → phiếu đơn (kế toán: Công nợ); xe, tài xế, khách → màn danh mục. Esc hoặc bấm ra ngoài để đóng. Dưới 760 px ẩn ô này.
- **Đổi mật khẩu** trong menu tài khoản: nút "Đổi mật khẩu" mở form (hiện tại, mới, nhập lại); kiểm tại chỗ ≥ 8 ký tự và nhập lại khớp; lỗi máy chủ hiện trong form (sai mật khẩu hiện tại, trùng mật khẩu cũ, khóa tạm 15 phút); xong thì toast "Đã đổi mật khẩu", phiên vẫn dùng tiếp. Menu đóng khi bấm / Tab ra ngoài (không dựa vào blur vì nút bị khóa lúc gửi làm mất focus).
- Đã thử bằng phản hồi giả lập đúng dạng PR #50; chờ backend gộp `dev` để thử thật.

## Tổng quan: khối "Hôm nay" (UC-38) và thanh đầu Quản lý (12/11/2026)

- Trang Tổng quan có khối **Hôm nay** (`GET /api/tong-quan?ngay=`, mặc định hôm nay, có ô đổi ngày và nút "Hôm nay"; mọi chuyến trong ngày, không chỉ chuyến đã quyết toán): chuyến (đang chạy · xong · chưa đi), đơn (đã giao · thất bại · còn lại), **điểm dừng đúng giờ** (tỉ lệ, "–" khi chưa quét; số điểm đã quét; ngưỡng trễ), hàng đã chở (kg), **doanh thu dự kiến** (ghi rõ chưa trừ đơn thất bại). Lỗi API thì ẩn khối, không chặn trang. Dưới là khối tháng, có tiêu đề "Tháng … chỉ tính chuyến đã quyết toán".
- **Thanh đầu Quản lý:** Xe, Tài xế, Nút, Tuyến gộp vào "Danh mục" cùng Người dùng, Bảng giá, Cấu hình (Điều phối vẫn thấy thẳng); tên người dùng ẩn dưới 1600 px; ô tìm 210 px (≤ 1600) / 150 px (≤ 1400). Thanh đầu một hàng từ 1280 px trở lên với mọi vai trò.

## Sửa theo lượt thử của Kiệt (12/11/2026)
- Điện thoại (≤ 760 px): hộp chuông, menu tài khoản, kết quả tìm chung cố định cách hai mép 12 px, không tràn mép trái.
- Tài xế: chuyến đang chạy còn điểm chưa xong thì khối "Kết thúc chuyến" bị khóa, ghi "Còn N điểm chưa xong…"; hết điểm mới hiện ô nhập km cuối.
- Tài xế: Kết thúc chuyến, Chi phí, Sự cố cách nhau 14 px, thẳng mép trái phải với thẻ lịch trình.
- Nút bị khóa (vd. Duyệt ở Quyết toán khi lệch tiền) dùng nền xám đặc, chữ mờ, không còn chỉ giảm độ trong suốt.
- Bảng chuyến, chuyến đang trễ (`theo_doi.ket_thuc_dang_chay` muộn hơn giờ theo lịch ≥ 1 phút, PR #54): giờ theo lịch gạch ngang màu phụ, giờ xong mới màu cam bên cạnh, vd. "→ ~~13:30~~ 14:10". Chưa có trường thì hiện như cũ.

## Giao diện v3 "Giấy ngà, mực đêm" (nhánh `tai/thu-giao-dien-v3`, Tài duyệt hướng 16/11/2026)

Bản thử làm lại toàn bộ cho hiện đại hơn, tách khỏi nhánh v2. Các mục phía trên tả v2; ở nhánh này những điểm dưới đây thay thế.

- **Phong cách:** nền giấy ngà phẳng (`--giay`), thẻ đặc (`--mat`) viền mảnh, không kính mờ, không vệt sáng nền. Lớp nổi (menu xổ, hộp thoại, toast) mới có bóng (`--bong`). Một màu thương hiệu xanh rêu đậm (`--o-liu` `#1F4D3F`); cam vẫn chỉ để cảnh báo.
- **Sáng / Tối:** bỏ 5 bộ màu. Bản sáng ở `:root`, bản tối ở `:root[data-che-do='toi']`; chọn "Theo máy / Sáng / Tối" trong menu tài khoản (`nen.ts`, khóa `qlvc-che-do`). Màu trạng thái có thêm biến `--…-chu` để làm chữ / biểu tượng (bản tối sáng hơn); màu tô đặc giữ nguyên hai bản. Phiếu in luôn nền sáng. Bản đồ đảo màu ở bản tối.
- **Khung trang:** cột menu trái nền mực đêm (`--dem`), mục chia nhóm Vận hành / Danh mục / Tài chính / Quản trị, mỗi mục một biểu tượng (`nhan.tsx`). Thanh trên: tìm chung bên trái, tên + vai trò, chuông, tài khoản bên phải. Tài xế (một mục) không có cột menu. Dưới 900 px cột menu thành thanh đáy cuộn ngang.
- **Chữ:** tiêu đề trang 28 px đậm 600 (v2: 46 px mảnh 300); số liệu lớn 26 px đậm 600.
- **Bo góc:** nút, ô nhập 10 px (`--bo`), thẻ 14 px (`--bo-the`), nhãn trạng thái 7 px. Chỉ thanh tiến độ còn bo tròn hết cỡ.
- **Nhãn trạng thái:** nền nhuộm nhạt theo màu trạng thái, không viền; cờ khẩn (Trễ, Sự cố, Chồng lịch) và Đã quyết toán vẫn tô đặc. Hình biểu tượng giữ như v2.
- **Tab lọc:** rãnh lõm `--mat-2`, mục đang chọn nổi lên bằng `--mat` + bóng nhỏ.
- **Form tài xế** (giao hàng, giao không được, quét lấy, chi phí, sự cố, km): xếp dọc cách 12 px, nhãn trên ô. Ô ký tên luôn nền trắng nét đen ở cả hai bản.
- **Hộp thoại** phủ cả cột menu và thanh trên (lớp mờ z-index 40).
- **Đã soát với dữ liệu thật (16/11):** mọi màn của 4 vai trò, hộp thoại lập chuyến / tạo đơn / sửa xe, form tài xế 360 px, phiếu in, bản đồ; cả bản sáng và tối.
- **Chưa làm:** màu biểu đồ bản tối chưa chạy bộ kiểm dataviz; bố cục bên trong từng màn vẫn như v2.

## Menu tài khoản gọn, trang Tài khoản và trang Cài đặt (nhánh `tai/cai-dat-tai-khoan`)

- **Menu tài khoản** (`MenuTaiKhoan.tsx`, bấm vòng góc phải): vòng tròn hiện ảnh đại diện (`/api/auth/anh-dai-dien?v=...`) khi `co_anh_dai_dien` bật (lỗi tải thì tự về chữ tắt), mở ra phần đầu (họ tên + vai trò), link **Tài khoản** (`/tai-khoan`), link **Cài đặt** (`/cai-dat`), link **Cấu hình hệ thống** (`/quan-ly/cau-hinh`, chỉ vai trò Quản lý), đường kẻ ngăn rồi nút **Đăng xuất**. Bấm link, bấm/Tab ra ngoài hoặc nhấn Esc đều đóng menu.
- **Trang Tài khoản** (`/tai-khoan`, `pages/TaiKhoan.tsx`, mọi vai trò đã đăng nhập, không thêm vào cột menu trái): gọi `GET /api/auth/ho-so` (UC-39), gồm 3 khối:
  1. **Ảnh đại diện:** ảnh tròn (hoặc chữ tắt), nút **Chọn ảnh** (`accept="image/jpeg,image/png"`, nén bằng `nenAnh` trên trình duyệt trước khi gửi), nút **Xóa ảnh** khi đã có ảnh, báo toast kết quả, lỗi hiện thông điệp máy chủ; đổi / xóa ảnh cập nhật ngay vòng góc phải.
  2. **Thông tin cá nhân** (chỉ xem, kèm dòng "Liên hệ Quản lý để thay đổi"): họ tên, tên đăng nhập, vai trò, trạng thái; riêng tài xế hiện thêm SĐT, số / hạng / hạn GPLX (hạn còn ≤ 30 ngày hoặc hết hạn tô cảnh báo bằng `HanGiayTo` theo BR-21).
  3. **Đổi mật khẩu** mở sẵn (form UC-35, kiểm 8–200 ký tự, nhập lại, báo toast).
- **Trang Cài đặt** (`/cai-dat`, `pages/CaiDat.tsx`, mọi vai trò đã đăng nhập, không thêm vào cột menu trái): 5 tùy chọn hiển thị lưu `localStorage` trong `nen.ts`, áp ngay khi chọn và tự khôi phục lúc khởi động app:
  1. **Giao diện** (`qlvc-che-do` → `data-che-do`): Theo máy / Sáng / Tối.
  2. **Mật độ bảng** (`qlvc-mat-do` → `data-mat-do="gon"`): Thoải mái (mặc định) / Gọn (thu gọn padding bảng và thẻ danh sách qua biến CSS `--dem-*`).
  3. **Cỡ chữ** (`qlvc-co-chu` → `data-co-chu="lon"`): Vừa (mặc định) / Lớn (tăng cỡ chữ gốc 112,5% qua `font-size` gốc và biến `--ty-le-chu`).
  4. **Giảm chuyển động** (`qlvc-giam-chuyen-dong` → `data-giam-chuyen-dong="bat"`): Theo máy (mặc định) / Bật (tắt transition/animation bằng CSS và truyền `animated={false}` cho `NumberFlow`).
  5. **Hiệu ứng nâng cao** (`qlvc-hieu-ung` → `data-hieu-ung="bat" | "tat"`): Bật (mặc định khi chưa lưu) / Tắt ("Hạt nền, đàn con trỏ, chữ gõ ở màn đăng nhập và tổng quan. Tắt nếu máy chậm."). Hàm `dangHieuUng()` trả về `true` khi mục này đang bật và `giamChuyenDong()` là `false`.
  - Vai trò Quản lý có dòng dẫn tới **Cấu hình hệ thống** ở cuối trang. Tài xế (không có cột menu trái) có link quay lại "← Chuyến của tôi" và có thể bấm tên hệ thống trên thanh đầu để về trang chính.

## Giao diện v4: hiệu ứng nâng cao (nhánh `tai/thu-giao-dien-v4`)

Giữ nguyên toàn bộ bố cục, biến màu và thành phần của giao diện v3, bổ sung lớp hiệu ứng nâng cao có thể tắt trong **Cài đặt → Hiệu ứng nâng cao** (`qlvc-hieu-ung`, mặc định `bat`) và tự tắt hoàn toàn khi `giamChuyenDong()` (cài đặt Giảm chuyển động hoặc `prefers-reduced-motion: reduce`):

- **Màn Đăng nhập (`DangNhap.tsx`, `NenHat.tsx`):**
  - Form bên trái hiện tức thời để gõ ngay; khung ảnh bên phải (`.dn-hinh`) hiện mờ dần `220 ms`.
  - Canvas `NenHat.tsx` phủ trên vùng ảnh (`pointer-events: none`), vẽ ~76 hạt dạng vệt ngắn (màn ≤ 600 px: 30 hạt) màu `--chay`, `--cam`, `--nhan-sang` và trắng, trôi chậm, dạt khỏi con trỏ chuột trong bán kính `120 px` rồi đàn hồi trôi về; tự co giãn theo `devicePixelRatio` và `ResizeObserver`, dừng `requestAnimationFrame` khi ẩn tab (`visibilitychange`) hoặc unmount.
  - Dòng giới thiệu trên ảnh tự gõ một lần (`35 ms/ký tự`), gõ xong con trỏ nháy 2 lần rồi ẩn; thẻ `<p>` giữ `aria-label` câu đầy đủ, phần chữ đang gõ đặt `aria-hidden="true"`.
  - Dòng thương hiệu phụ `"Hệ thống quản lý vận tải"` tách ký tự `inline-block`, 4 chữ cái cuối nổi lên lệch nhịp (`translateY(-0.12em…-0.3em)`, `600 ms`, trễ `300 ms`), giữ `aria-label` câu đầy đủ.
- **Đàn con trỏ dựng trang (`DanConTro.tsx`):** gắn một chỗ trong `KhungTrang` (`App.tsx`), nghe `pathname`. Ý tưởng lấy từ phân tích extension Swarm (không có license, không chép code). Một vòng `requestAnimationFrame` (`dt ≤ 50 ms`), mỗi con trỏ chạy một generator `function*` làm kịch bản (`diToi` cong ngẫu nhiên `sin(π·e) × bend`, easeOut, thời lượng `clamp(0,12 + √d × 0,021; 0,14; 0,9) s`; `nhan` co 0,88; `keoToi` đi thẳng, easeInOut; `cho`). Con trỏ rảnh lấy khối gần nhất còn chờ, ưu tiên khối trong màn. Dựng một khối kiểu Figma: đổi sang dấu cộng, tới góc trên-trái, nhấn, kéo khung xám (viền màu con trỏ, nhãn `W × H`) tới góc dưới-phải, thả, chờ 0,18–0,3 s rồi khối thật hiện bằng transition opacity 220–350 ms. Khối chờ dựng chỉ `opacity: 0` (giữ bố cục). **Chế độ 1** (lần đầu trong phiên trình duyệt, `sessionStorage` `qlvc-dan-tro-da-chay`, chỉ ghi khi chạy xong/bị bỏ qua): 6–8 con trỏ có nhãn vai trò bay vào từ hai mép, dựng cả menu trái, xong bay ra mép gần nhất, trần 3,6 s; F5 trong phiên không chạy lại. **Chế độ 2** (bấm mục ở menu trái, Tài chốt 20/11): chỉ vùng `div.than` (thanh trên + nội dung), không đụng `aside.canh`; 3–4 con trỏ không nhãn hiện tại chỗ (fade 80 ms), dựng nhanh rồi mờ tại chỗ, trần 1,42 s. Trước khi đo, `main.trang` tạm ẩn (`data-dan-tro-doi`) và chờ DOM trong `.than` yên 120 ms (tối đa 600 ms) để không đo nhầm khung giữ chỗ lúc tải; khối đang dựng được đo lại mỗi khung hình. Màn tài xế (khung `.mot`, không menu) dựng các thẻ `.the-chon`, `.the-chinh`, `.the` thay cho `.kinh`. Màn hẹp (menu thành thanh đáy): chế độ 2 cắt lớp phủ bỏ thanh đáy (`clip-path`) và cắt khối cách mép trên thanh 8 px, nên con trỏ không đè menu. Bấm chuột, gõ phím, cuộn, ẩn tab bất kỳ lúc nào: dừng, hiện đủ mọi khối.
- **Khối `.kinh` hiện dần khi cuộn tới (`useHienKhiCuon.ts`):** dùng `IntersectionObserver` chung cho các khối `.kinh` nằm ngoài khung nhìn lúc tải trang (bỏ qua dòng bảng `tr` và phần tử trong danh sách `ul`/`ol`/`.ds-the`); lần đầu cuộn tới hiện `opacity 0 → 1` + `translateY(8px → 0)` trong `260 ms` (`cubic-bezier(0.16, 1, 0.3, 1)`), mỗi khối chỉ chạy một lần.
- **Thanh tải trọng và độ đầy (`.xh-ray i`, `.day span i`, `.kx-thanh i`, `.ct-thanh i`, `.tq-xe-truc i`):** co giãn mượt `transition: width 180ms cubic-bezier(0.22, 1, 0.36, 1), background-color 150ms ease-out` khi thử ghép đơn hoặc đổi số liệu (chuyển động nhỏ báo trạng thái, giữ cả khi tắt Hiệu ứng nâng cao, chỉ tắt khi giảm chuyển động).
- **Khung chi tiết hiện êm (`.qt-ct`, `.tc-kq`):** khi đổi chuyến ở Quyết toán, đổi khách ở Công nợ hoặc nhận kết quả ở Tra cứu đơn, khung chi tiết hiện êm `opacity 0 → 1` + `translateY(4px → 0)` trong `150 ms`.
- **Logo cột menu trái (`.canh .hieu`):** khi rê chuột hoặc focus vào chữ `"Quản lý vận tải"` ở đầu cột menu trái, 3 chữ cái cuối (`t`, `ả`, `i`) nổi nhẹ lên lệch nhịp (`transition 200 ms`), rời chuột thì trở về.

## Còn phải quyết khi làm vào code

- Nút đổi bộ màu trong Cài đặt (Tài làm sau).
- Thanh `<meter>` tải / thể tích ở chi tiết chuyến còn màu mặc định của trình duyệt (làm ở 03).
- Thử trên máy chiếu trước buổi demo: tông nhạt, nét mảnh dễ bạc màu.

## Phong cách Pixel (thử nghiệm, 24/11)

- Trang Cài đặt có mục **Phong cách: Hiện tại / Pixel (thử nghiệm)**; mặc định *Hiện tại*. Lưu ở trình duyệt (`qlvc-phong-cach`), `nen.ts` đặt `data-phong-cach="pixel"` trên `<html>`.
- `frontend/src/phong-cach-pixel.css` là **lớp áo**: chỉ đặt lại biến màu, bo góc, bóng của `index.css` và vài quy tắc (viền 2 px, bóng cứng, nút lún khi bấm, bỏ kính mờ). Không đổi bố cục, màn, luồng nghiệp vụ, API.
- Bảng màu Nostalgos 12 (Lospec), **chỉ bản sáng**: bật Pixel thì luôn sáng (lựa chọn sáng/tối vẫn được lưu, tắt Pixel là về như cũ). Màu trạng thái được làm đậm để chữ trắng ≥ 4.5:1; đã đo mọi trang của 4 vai trò + đăng nhập, tra cứu: 0 lỗi JS, 0 chữ thiếu tương phản.
- Quy ước: màn mới dùng biến màu (`var(--...)`), không viết mã màu cứng, để đúng ở cả hai phong cách.
- Công tắc **Con trỏ đi theo** (Bật/Tắt, `qlvc-con-tro`): tắt thì `DanConTro` không chạy; hạt nền và chữ gõ vẫn theo "Hiệu ứng nâng cao".
- Công tắc **Hiệu ứng Pixel** (chỉ hiện khi chọn Pixel; `qlvc-hieu-ung-pixel`, `data-hieu-ung-pixel="tat"`): tắt thì bỏ rung/lún/hiện lớp nổi, giữ màu, viền, bóng.
- Hiệu ứng chuyển động cho phong cách này: đề xuất ở nhánh thử `tai/agy-ui-moments`, làm sau.
- Ảnh nền đăng nhập ở Pixel: `frontend/public/anh/*-pixel.png`, chuyển từ hai ảnh Unsplash ở bảng trên sang pixel art bằng PixelLab (`image_to_pixelart`, vẽ lại kiểu pixel art; ảnh hoàng hôn dùng `image_to_pixelart_pro_flash` 95×119, ảnh lướt ngang 160×107), hiển thị `image-rendering: pixelated`. Giấy phép Unsplash cho phép chỉnh sửa; ghi công giữ như ảnh gốc.
