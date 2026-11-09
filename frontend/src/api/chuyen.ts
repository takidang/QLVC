import { goi, guiJson, query } from './goi'
import type { DanhSach } from './xe'
import type { Don } from './don'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type Chuyen = {
  id: number
  ma_chuyen: string
  tuyen_id: number
  ma_tuyen: string
  ten_tuyen: string
  xe_id: number
  bien_so: string
  tai_xe_id: number
  ten_tai_xe: string
  khoi_hanh_du_kien: string
  ket_thuc_du_kien: string
  trang_thai: string
  // UC-32: chỉ có khi lọc theo ngày (bảng chuyến trong ngày)
  theo_doi?: {
    xong: number
    tong: number
    ty_le_lap_day: string
    co: string[]
    chong: string[]
  } | null
}
export type ChuyenVao = {
  tuyen_id: number
  khoi_hanh_du_kien: string
  xe_id: number
  tai_xe_id: number
}
export type LyDo = { ma: string; thong_diep: string }
export type XeKhaDung = {
  id: number
  bien_so: string
  tai_trong_kg: number
  the_tich_m3: string
  kha_dung: boolean
  ly_do: LyDo[]
}
export type TaiXeKhaDung = {
  id: number
  ho_ten: string
  hang_gplx: string
  kha_dung: boolean
  ly_do: LyDo[]
}

export const danhSachChuyen = (loc: {
  trang_thai?: string
  ngay?: string
  trang?: number
  so_dong?: number
}) => goi<DanhSach<Chuyen>>(`/api/chuyen?${query(loc)}`)
export const lapChuyen = (vao: ChuyenVao) => guiJson<Chuyen>('/api/chuyen', 'POST', vao)
export const xeKhaDung = (tuyen_id: number, khoi_hanh: string) =>
  goi<XeKhaDung[]>(`/api/chuyen/xe-kha-dung?${query({ tuyen_id, khoi_hanh })}`)
export const taiXeKhaDung = (tuyen_id: number, khoi_hanh: string, xe_id?: number) =>
  goi<TaiXeKhaDung[]>(`/api/chuyen/tai-xe-kha-dung?${query({ tuyen_id, khoi_hanh, xe_id })}`)

export type DiemDung = {
  thu_tu: number
  nut: string
  viec: 'LAY' | 'GIAO'
  don_id: number
  ma_don: string
  eta: string
  eta_ke_hoach?: string | null
  thuc_te?: string | null
  ket_qua?: string | null
  tre_phut?: number | null
  lat?: string | null
  lng?: string | null
}
export type ChuyenChiTiet = Chuyen & {
  tai_trong: { da_dung_kg: string; toi_da_kg: number }
  the_tich: { da_dung_m3: string; toi_da_m3: string }
  ty_le_lap_day: string
  lich_trinh: DiemDung[]
  lai_du_kien: number
  canh_bao_lai_am: boolean
  chay_rong: boolean
  don: Don[]
  // UC-32: chỉ có ở GET chi tiết (không có trong kết quả ghép / gỡ / chốt)
  co?: string[] | null
  chong?: string[] | null
  ket_thuc_dang_chay?: string | null
  ket_thuc_bat_thuong?: boolean | null
  ly_do_ket_thuc?: string | null
  km_bat_dau?: number | null
  km_ket_thuc?: number | null
  dong_thoi_gian?: { luc: string; loai: string; noi_dung: string; nguoi?: string | null }[] | null
  tien?: { dinh_muc: number; luong: number; tam_ung_hieu_luc: number; doanh_thu: number } | null
  su_co?: SuCo[] | null
}
export type SuCo = {
  id: number
  loai: string
  ghi_chu: string | null
  trang_thai: string
  cach_xu_ly: string | null
  luc: string
}
// Vi phạm khi ghép/gỡ: don_id null là vi phạm của cả chuyến (tải, thể tích, giấy tờ, trùng lịch)
export type ViPhamGhep = { don_id: number | null; ma: string; thong_diep: string }

export const chiTietChuyen = (id: number) => goi<ChuyenChiTiet>(`/api/chuyen/${id}`)
export const donPhuHop = (id: number) => goi<Don[]>(`/api/chuyen/${id}/don-phu-hop`)
export const ghepDon = (id: number, don_ids: number[]) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/ghep`, 'POST', { don_ids })
export const goDon = (id: number, don_ids: number[]) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/go`, 'POST', { don_ids })

// UC-12: đổi xe, tài xế khi chuyến LAP
export const xeKhaDungChuyen = (id: number) => goi<XeKhaDung[]>(`/api/chuyen/${id}/xe-kha-dung`)
export const taiXeKhaDungChuyen = (id: number, xe_id?: number) =>
  goi<TaiXeKhaDung[]>(`/api/chuyen/${id}/tai-xe-kha-dung?${query({ xe_id })}`)
export const phanCong = (id: number, xe_id: number, tai_xe_id: number) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/phan-cong`, 'PUT', { xe_id, tai_xe_id })

// Chốt (UC-15): máy chủ trả 422 BR-23 (chuyến rỗng) / BR-52 (lãi âm) khi thiếu xác nhận
export type XacNhanChot = { xac_nhan_chay_rong?: boolean; xac_nhan_lai_am?: boolean }
export const chotChuyen = (id: number, xn: XacNhanChot) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/chot`, 'POST', xn)
export const moChotChuyen = (id: number) =>
  goi<ChuyenChiTiet>(`/api/chuyen/${id}/mo-chot`, { method: 'POST' })

// Hủy (UC-16): lý do bắt buộc; còn tạm ứng hoặc chuyến đã chạy → 409 BR-25
export const huyChuyen = (id: number, ly_do: string) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/huy`, 'POST', { ly_do })

// UC-32: kết thúc do sự cố (BR-68), đóng sự cố tài xế báo (UC-33)
export const ketThucSuCo = (id: number, ly_do: string, km_ket_thuc: number | null) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/ket-thuc-su-co`, 'POST', { ly_do, km_ket_thuc })
export const dongSuCo = (id: number, cach_xu_ly: string) =>
  guiJson<SuCo>(`/api/su-co/${id}/dong`, 'POST', { cach_xu_ly })
// Cờ trên bảng chuyến trong ngày (UC-32)
export const TEN_CO: Record<string, string> = {
  TRE: 'Trễ',
  SU_CO: 'Sự cố',
  THAT_BAI: 'Đơn thất bại',
  CHUA_QUYET_TOAN: 'Chưa quyết toán',
  CHONG_LICH: 'Chồng lịch',
}
