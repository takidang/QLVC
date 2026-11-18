import { goi } from './goi'

// UC-37: thông báo theo vai trò (GET /api/thong-bao), mới trước. "Đã đọc" lưu trên trình duyệt (mốc lần mở chuông)
export type ThongBao = {
  loai: string
  muc_do: 'KHAN' | 'CAN_LAM' | 'THONG_TIN'
  tieu_de: string
  noi_dung: string | null
  doi_tuong: { loai: 'CHUYEN' | 'DON' | 'XE' | 'TAI_XE'; id: number } | null
  luc: string
}
export const thongBao = () => goi<{ so_luong: number; thong_bao: ThongBao[] }>('/api/thong-bao')
