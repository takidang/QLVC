import { goi, guiJson, query } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type Nut = {
  id: number
  ten: string
  tinh: string
  loai: 'TINH' | 'KHO'
  lat: string | null
  lng: string | null
}
export type NutVao = Omit<Nut, 'id'>

export type NutTuyenVao = {
  nut_id: number
  phut_tu_diem_dau: number
  km_tu_diem_dau: number
  la_diem_nghi: boolean
}
export type Tuyen = {
  id: number
  ma: string
  ten: string
  dm_dau: number
  dm_cau_duong: number
  dm_boc_xep: number
  dm_luong_tai_xe: number
  trang_thai: 'HOAT_DONG' | 'NGUNG'
  nut: (NutTuyenVao & { thu_tu: number; ten: string; tinh: string })[]
  tong_phut: number
  tong_km: number
  canh_bao: string[]
}
export type TuyenVao = Pick<
  Tuyen,
  'ma' | 'ten' | 'dm_dau' | 'dm_cau_duong' | 'dm_boc_xep' | 'dm_luong_tai_xe'
> & { nut: NutTuyenVao[] }

export const danhSachNut = (loc: { tim?: string; trang?: number; so_dong?: number }) =>
  goi<DanhSach<Nut>>(`/api/nut?${query(loc)}`)
export const themNut = (vao: NutVao) => guiJson<Nut>('/api/nut', 'POST', vao)
export const suaNut = (id: number, vao: Partial<NutVao>) =>
  guiJson<Nut>(`/api/nut/${id}`, 'PATCH', vao)

export const danhSachTuyen = (loc: {
  tim?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) => goi<DanhSach<Tuyen>>(`/api/tuyen?${query(loc)}`)
export const themTuyen = (vao: TuyenVao) => guiJson<Tuyen>('/api/tuyen', 'POST', vao)
export const suaTuyen = (
  id: number,
  vao: Partial<Omit<TuyenVao, 'ma'>> & { trang_thai?: Tuyen['trang_thai'] },
) => guiJson<Tuyen>(`/api/tuyen/${id}`, 'PATCH', vao)
