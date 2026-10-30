import { goi, guiJson } from './goi'
import type { DanhSach } from './xe'

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

const query = (loc: Record<string, string | number | undefined>) => {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(loc)) if (v !== undefined && v !== '') q.set(k, String(v))
  return q
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
