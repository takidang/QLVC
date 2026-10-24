# Mẫu làm một use case danh mục (lấy UC-03 Quản lý xe làm ví dụ)

> Dành cho: UC-04 Tài xế, UC-05 Tuyến, UC-06 Khách hàng, UC-02 Người dùng, UC-07 Bảng giá.
> Đọc kèm: `docs/kien-truc.md` (3 lớp, mã lỗi), `docs/api.md` (endpoint), `docs/security-rules.md`, skill `story-flow`.
> Ví dụ đầy đủ: story `docs/stories/UC-03-quan-ly-xe.md` và code liệt kê ở mục 2.

## 1. Các bước

1. **Story:** `story new UC-xx` → viết AC (mỗi quy tắc một AC, có ca biên, có ca sai quyền) → chờ Tài/Kiệt duyệt. Chỗ nghiệp vụ chưa rõ thì hỏi, ghi quyết định vào story và sửa `docs/` (ví dụ UC-03 chốt "khối lượng toàn bộ ≥ tải trọng").
2. **Model:** bảng đã có trong `backend/app/models/` (24 bảng theo ERD). Cần thêm cột/bảng thì ghi "Đang chặn" trong `TIEN-DO.md`, sửa model, tạo migration `alembic revision --autogenerate -m "..."`, commit sớm.
3. **Domain** (`backend/app/domain/`): quy tắc nghiệp vụ là hàm thuần, tên chứa mã BR, sai thì `raise LoiNghiepVu("BR-xx", "câu tiếng Việt")` (422). Không import SQLAlchemy.
4. **Schema** (`schemas.py`): `XxxVao` (thêm), `XxxSua` (sửa, mọi trường không bắt buộc), `XxxRa` (trả về). Ràng buộc kiểu, `> 0`, độ dài đặt ở đây → sai trả 400. `extra="forbid"` để trường không được sửa (ví dụ `km_dong_ho`) bị từ chối.
5. **Service** (`service.py`): giao dịch, khóa dòng khi sửa (`db.get(..., with_for_update=True)`), gọi domain, bắt `IntegrityError` của ràng buộc unique → 409. Không đọc request.
6. **Router** (`router.py`): mỗi endpoint gọi **một** hàm service; phân quyền bằng `Depends(can_vai_tro(...))`; danh sách dùng `phan_trang` và `DanhSach[...]` trong `app/phan_trang.py`. Gắn router vào `app/main.py`.
7. **Test** (`backend/tests/api/test_ucxx_*.py`, `tests/unit/` cho domain): tên test chứa mã AC; đăng nhập bằng fixture `dang_nhap_voi("DIEU_PHOI")`. Mỗi AC phân quyền có ca 403 và 401.
8. **Giao diện** (`frontend/src/`): hàm gọi API trong `api/<ten>.ts` (dùng `goi`, `guiJson`); trang trong `pages/<vai-tro>/`; thêm một dòng vào `TRANG_CON` trong `App.tsx` là có menu. Lỗi từng trường: `loiTheoTruong(err)` (đổi lỗi 400 sang tiếng Việt).
9. **Chạy và kiểm:** `ruff check .`, `pytest`; `npm run lint`, `npm run build`; thử trên trình duyệt (Edge/Chrome, `http://127.0.0.1:5173`), chụp ảnh vào `docs/test-evidence/UC-xx/`.
10. **Đóng:** `story done UC-xx` → cập nhật `TIEN-DO.md` → commit, push → `ponytail-review`.

## 2. File của UC-03 để chép

| Lớp | File | Ghi chú |
|---|---|---|
| Domain | `backend/app/domain/xe_tai_xe.py` | `kiem_br14_khoi_luong_toan_bo`; UC-04 thêm hàm hạng bằng lái vào cùng file |
| Schema | `backend/app/modules/danh_muc/xe/schemas.py` | Chuẩn hóa biển số bằng `field_validator`; `XeSua` chặn gửi `null` cho trường bắt buộc |
| Service | `backend/app/modules/danh_muc/xe/service.py` | Thêm, sửa, danh sách, chi phí cố định kèm nhật ký tiền (BR-62) |
| Router | `backend/app/modules/danh_muc/xe/router.py` | Điều phối sửa, Kế toán chỉ xem |
| Test | `backend/tests/api/test_uc03_xe.py`, `backend/tests/unit/test_uc03_domain.py` | Ca biên dùng `pytest.mark.parametrize` |
| API client | `frontend/src/api/xe.ts` | |
| Trang | `frontend/src/pages/dieu-phoi/XeDanhSach.tsx` | Bảng + lọc + phân trang + hộp thoại thêm/sửa |

Mỗi danh mục một thư mục con trong `backend/app/modules/danh_muc/` (`xe/`, `tai_xe/`, `tuyen/`…) để hai người làm hai danh mục không sửa chung file.

## 3. Lỗi hay gặp

- Gửi `null` cho trường bắt buộc khi sửa → CSDL báo lỗi 500. Chặn ở schema (xem `XeSua`).
- Tìm kiếm bằng `LIKE` phải thoát ký tự `%`, `_` (`contains(..., autoescape=True)`).
- Đường dẫn cố định đặt trước đường dẫn có `{id}` cùng tiền tố (`api.md` mục 1).
- Số thập phân (m³, lít) máy chủ trả dạng chuỗi; giao diện đổi bằng `Number(...)` khi hiển thị.
- Trên Windows dùng `127.0.0.1`, không dùng `localhost` (CSDL và proxy Vite chậm).
- Trường chữ dùng kiểu chung trong `backend/app/kieu.py`: `ChuBatBuoc` (bỏ khoảng trắng, đưa về Unicode NFC – "Cần Thơ" gõ kiểu tổ hợp và dựng sẵn thành một), `SoDienThoai` (chuẩn hóa về `0` + 9–10 số). Đừng tự viết lại.
- "Hôm nay" theo giờ Việt Nam: `app/thoi_gian.py` (`hom_nay_vn()`, `bay_gio()`); frontend dùng `toLocaleDateString('sv-SE')`, không dùng `toISOString()`.
- Chạy backend lúc dev **không dùng `--reload`** (kẹt trên Windows, tiến trình cũ trả 404 cho route mới); sửa code thì tắt rồi chạy lại.
