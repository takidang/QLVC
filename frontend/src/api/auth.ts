// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type VaiTro = 'QUAN_LY' | 'DIEU_PHOI' | 'TAI_XE' | 'KE_TOAN'
export type NguoiDung = { id: number; ho_ten: string; vai_tro: VaiTro }

export class LoiApi extends Error {
  status: number
  ma: string
  constructor(status: number, ma: string, thongDiep: string) {
    super(thongDiep)
    this.status = status
    this.ma = ma
  }
}

async function goi<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { credentials: 'same-origin', ...init })
  if (r.status === 204) return undefined as T
  const body = await r.json().catch(() => ({}))
  if (!r.ok)
    throw new LoiApi(r.status, body.ma ?? 'LOI', body.thong_diep ?? 'Có lỗi, vui lòng thử lại')
  return body as T
}

export const dangNhap = (ten_dang_nhap: string, mat_khau: string) =>
  goi<NguoiDung>('/api/auth/dang-nhap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ten_dang_nhap, mat_khau }),
  })

export const toi = () => goi<NguoiDung>('/api/auth/toi')

export const dangXuat = () => goi<void>('/api/auth/dang-xuat', { method: 'POST' })
