import { goi, guiJson } from './goi'

// UC-21 chi phí của tài xế – api.md 2.5
export type LoaiChi = 'DAU' | 'CAU_DUONG' | 'BOC_XEP' | 'PHAT_SINH'
export const TEN_LOAI_CHI: Record<LoaiChi, string> = {
  DAU: 'Dầu',
  CAU_DUONG: 'Cầu đường',
  BOC_XEP: 'Bốc xếp',
  PHAT_SINH: 'Phát sinh',
}
export const TEN_TRANG_THAI_CHI: Record<string, string> = {
  CHO_DUYET: 'Chờ duyệt',
  DA_DUYET: 'Đã duyệt',
  TU_CHOI: 'Từ chối',
}
export type KhoanChi = {
  id: number
  chuyen_id: number
  loai: LoaiChi
  so_tien_khai: number
  so_tien_duyet: number | null
  so_lit: string | null
  ghi_chu: string
  trang_thai: 'CHO_DUYET' | 'DA_DUYET' | 'TU_CHOI'
  so_anh: number
  tao_luc: string
}
export type ChiPhiChuyen = {
  chuyen_id: number
  tam_ung_da_nhan: number
  tong_da_khai: number
  khoan: KhoanChi[]
}
export type KhoanChiVao = { loai: LoaiChi; so_tien: number; so_lit: string | null; ghi_chu: string }

export const chiPhiChuyen = (chuyen_id: number) =>
  goi<ChiPhiChuyen>(`/api/toi/chuyen/${chuyen_id}/chi-phi`)

// multipart: ảnh đã nén trên trình duyệt (NFR-PER-03); số lít chỉ gửi với dầu (BR-54)
export function ghiChiPhi(chuyen_id: number, vao: KhoanChiVao, anh: Blob[]) {
  const form = new FormData()
  form.append('loai', vao.loai)
  form.append('so_tien', String(vao.so_tien))
  if (vao.so_lit !== null) form.append('so_lit', vao.so_lit)
  form.append('ghi_chu', vao.ghi_chu)
  anh.forEach((a, i) => form.append('anh', a, `hoa-don-${i + 1}.jpg`))
  return goi<KhoanChi>(`/api/toi/chuyen/${chuyen_id}/chi-phi`, { method: 'POST', body: form })
}

export const suaChiPhi = (id: number, vao: KhoanChiVao) =>
  guiJson<KhoanChi>(`/api/toi/chi-phi/${id}`, 'PATCH', vao)

export const xoaChiPhi = (id: number) => goi<void>(`/api/toi/chi-phi/${id}`, { method: 'DELETE' })
