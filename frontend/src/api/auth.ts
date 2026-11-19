import { goi, guiJson } from './goi'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type VaiTro = 'QUAN_LY' | 'DIEU_PHOI' | 'TAI_XE' | 'KE_TOAN'
export type NguoiDung = {
  id: number
  ho_ten: string
  vai_tro: VaiTro
  co_anh_dai_dien: boolean
}
export type TaiXeHoSo = {
  sdt: string
  so_gplx: string
  hang_gplx: string
  han_gplx: string
}
export type HoSo = {
  id: number
  ten_dang_nhap: string
  ho_ten: string
  vai_tro: VaiTro
  trang_thai: string
  co_anh_dai_dien: boolean
  tai_xe: TaiXeHoSo | null
}

export { LoiApi } from './goi'

export const dangNhap = (ten_dang_nhap: string, mat_khau: string) =>
  guiJson<NguoiDung>('/api/auth/dang-nhap', 'POST', { ten_dang_nhap, mat_khau })

export const toi = () => goi<NguoiDung>('/api/auth/toi')

export const dangXuat = () => goi<void>('/api/auth/dang-xuat', { method: 'POST' })

// UC-35: tự đổi mật khẩu (mọi vai trò). 204 xong; 422 SAI_MAT_KHAU_CU / MAT_KHAU_TRUNG; 429 KHOA_TAM
export const doiMatKhau = (mat_khau_cu: string, mat_khau_moi: string) =>
  guiJson<void>('/api/auth/mat-khau', 'PUT', { mat_khau_cu, mat_khau_moi })

// UC-39: hồ sơ cá nhân chỉ xem và tự đổi / xóa ảnh đại diện
export const hoSo = () => goi<HoSo>('/api/auth/ho-so')

export function doiAnhDaiDien(file: Blob) {
  const form = new FormData()
  form.append('anh', file, file.type === 'image/png' ? 'anh-dai-dien.png' : 'anh-dai-dien.jpg')
  return goi<HoSo>('/api/auth/anh-dai-dien', { method: 'PUT', body: form })
}

export const xoaAnhDaiDien = () => goi<void>('/api/auth/anh-dai-dien', { method: 'DELETE' })

export const urlAnhDaiDien = (phienBan: number) => `/api/auth/anh-dai-dien?v=${phienBan}`

export const chuTat = (hoTen: string) =>
  hoTen
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(-2)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
