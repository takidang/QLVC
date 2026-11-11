import { goi, query } from './goi'

// UC-36: tìm chung trên thanh đầu (GET /api/tim?q=, q 2–100 ký tự). Mỗi nhóm {tong, ds ≤ 5};
// nhóm vai trò không được xem trả rỗng
type Nhom<T> = { tong: number; ds: T[] }
export type KetQuaTim = {
  q: string
  chuyen: Nhom<{
    id: number
    ma_chuyen: string
    trang_thai: string
    bien_so: string
    ten_tai_xe: string
    khoi_hanh_du_kien: string
  }>
  don: Nhom<{
    id: number
    ma_don: string
    trang_thai: string
    ten_khach: string
    tinh_lay: string
    tinh_giao: string
  }>
  xe: Nhom<{ id: number; bien_so: string; trang_thai: string }>
  tai_xe: Nhom<{ id: number; ho_ten: string; trang_thai: string }>
  khach_hang: Nhom<{ id: number; ten: string; sdt: string }>
}
export const timChung = (q: string, signal?: AbortSignal) =>
  goi<KetQuaTim>(`/api/tim?${query({ q })}`, { signal })
