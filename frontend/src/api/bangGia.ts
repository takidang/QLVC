import { goi, guiJson } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type BangGia = {
  id: number
  tinh_lay: string
  tinh_giao: string
  don_gia_kg: number
  cuoc_toi_thieu: number
  hieu_luc_tu: string // YYYY-MM-DD
  dang_ap_dung: boolean
}
export type BangGiaVao = Omit<BangGia, 'id' | 'dang_ap_dung'>

export type ThamSo = {
  ma: string
  ten: string
  don_vi: string
  gia_tri: string
  nguoi_sua: string | null
  luc: string | null
}

export function danhSachBangGia(loc: { tim?: string; trang?: number; so_dong?: number }) {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(loc)) if (v !== undefined && v !== '') q.set(k, String(v))
  return goi<DanhSach<BangGia>>(`/api/bang-gia?${q}`)
}
export const tenTinhDaDung = () => goi<string[]>('/api/bang-gia/ten-tinh')
export const themBangGia = (vao: BangGiaVao) => guiJson<BangGia>('/api/bang-gia', 'POST', vao)
export const suaBangGia = (id: number, vao: Partial<BangGiaVao>) =>
  guiJson<BangGia>(`/api/bang-gia/${id}`, 'PATCH', vao)

export const danhSachCauHinh = () => goi<ThamSo[]>('/api/cau-hinh')
export const suaCauHinh = (ma: string, gia_tri: string) =>
  guiJson<ThamSo[]>(`/api/cau-hinh/${ma}`, 'PUT', { gia_tri })
