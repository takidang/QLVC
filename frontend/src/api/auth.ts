import { goi, guiJson } from './goi'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type VaiTro = 'QUAN_LY' | 'DIEU_PHOI' | 'TAI_XE' | 'KE_TOAN'
export type NguoiDung = { id: number; ho_ten: string; vai_tro: VaiTro }

export { LoiApi } from './goi'

export const dangNhap = (ten_dang_nhap: string, mat_khau: string) =>
  guiJson<NguoiDung>('/api/auth/dang-nhap', 'POST', { ten_dang_nhap, mat_khau })

export const toi = () => goi<NguoiDung>('/api/auth/toi')

export const dangXuat = () => goi<void>('/api/auth/dang-xuat', { method: 'POST' })
