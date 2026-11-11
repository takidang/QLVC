import { goi } from './goi'

// UC-33 báo sự cố của tài xế – api.md 2.5
export type LoaiSuCo = 'HONG_XE' | 'TAI_NAN' | 'KET_XE' | 'THOI_TIET' | 'KHAC'
export const TEN_LOAI_SU_CO: Record<LoaiSuCo, string> = {
  HONG_XE: 'Hỏng xe',
  TAI_NAN: 'Tai nạn',
  KET_XE: 'Kẹt xe / tắc đường',
  THOI_TIET: 'Thời tiết xấu',
  KHAC: 'Khác',
}
export type SuCo = {
  id: number
  chuyen_id: number
  loai: string
  ghi_chu: string | null
  trang_thai: 'MO' | 'DONG'
  cach_xu_ly: string | null
  so_anh: number
  luc: string
}

export const suCoChuyen = (chuyen_id: number) => goi<SuCo[]>(`/api/toi/chuyen/${chuyen_id}/su-co`)

// multipart: ảnh đã nén trên trình duyệt (NFR-PER-03); ảnh không bắt buộc (UC-33 quyết định 3)
export function baoSuCo(chuyen_id: number, loai: LoaiSuCo, ghi_chu: string, anh: Blob[]) {
  const form = new FormData()
  form.append('loai', loai)
  form.append('ghi_chu', ghi_chu)
  anh.forEach((a, i) => form.append('anh', a, `su-co-${i + 1}.jpg`))
  return goi<SuCo>(`/api/toi/chuyen/${chuyen_id}/su-co`, { method: 'POST', body: form })
}
