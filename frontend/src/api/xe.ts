import { goi, guiJson } from './goi'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type TrangThaiXe = 'HOAT_DONG' | 'NGUNG'
export type Xe = {
  id: number
  bien_so: string
  tai_trong_kg: number
  the_tich_m3: string // số thập phân, máy chủ trả dạng chuỗi để không mất độ chính xác
  ktt_toan_bo_kg: number
  han_dang_kiem: string // YYYY-MM-DD
  han_bao_hiem: string
  dinh_muc_lit_100km: string | null
  km_dong_ho: number
  trang_thai: TrangThaiXe
}
export type XeVao = Omit<Xe, 'id' | 'trang_thai'>
export type XeSua = Partial<Omit<XeVao, 'km_dong_ho'>> & { trang_thai?: TrangThaiXe }
export type DanhSach<T> = { du_lieu: T[]; tong: number }

export function danhSachXe(loc: {
  tim?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(loc)) if (v !== undefined && v !== '') q.set(k, String(v))
  return goi<DanhSach<Xe>>(`/api/xe?${q}`)
}

export const themXe = (vao: XeVao) => guiJson<Xe>('/api/xe', 'POST', vao)
export const suaXe = (id: number, vao: XeSua) => guiJson<Xe>(`/api/xe/${id}`, 'PATCH', vao)

type ChiPhiCoDinh = { xe_id: number; thang: string; so_tien: number | null }
export const xemChiPhiCoDinh = (xeId: number, thang: string) =>
  goi<ChiPhiCoDinh>(`/api/xe/${xeId}/chi-phi-co-dinh/${thang}`)
export const datChiPhiCoDinh = (xeId: number, thang: string, so_tien: number) =>
  guiJson<ChiPhiCoDinh>(`/api/xe/${xeId}/chi-phi-co-dinh/${thang}`, 'PUT', { so_tien })
