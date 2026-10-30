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
}
export type ChuyenChiTiet = Chuyen & {
  tai_trong: { da_dung_kg: string; toi_da_kg: number }
  the_tich: { da_dung_m3: string; toi_da_m3: string }
  ty_le_lap_day: string
  lich_trinh: DiemDung[]
  lai_du_kien: number
  canh_bao_lai_am: boolean
  don: Don[]
}
// Vi phạm khi ghép/gỡ: don_id null là vi phạm của cả chuyến (tải, thể tích, giấy tờ, trùng lịch)
export type ViPhamGhep = { don_id: number | null; ma: string; thong_diep: string }

export const chiTietChuyen = (id: number) => goi<ChuyenChiTiet>(`/api/chuyen/${id}`)
export const donPhuHop = (id: number) => goi<Don[]>(`/api/chuyen/${id}/don-phu-hop`)
export const ghepDon = (id: number, don_ids: number[]) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/ghep`, 'POST', { don_ids })
export const goDon = (id: number, don_ids: number[]) =>
  guiJson<ChuyenChiTiet>(`/api/chuyen/${id}/go`, 'POST', { don_ids })
