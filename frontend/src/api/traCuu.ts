import { guiJson } from './goi'

// UC-28: khách tra cứu đơn, không đăng nhập (api.md 3.4). POST để số điện thoại không nằm trong URL
export type KetQuaTraCuu = {
  ma_don: string
  trang_thai: string
  moc: { trang_thai: string; luc: string }[]
}
export const traCuu = (ma_don: string, sdt_4_so_cuoi: string) =>
  guiJson<KetQuaTraCuu>('/api/tra-cuu', 'POST', { ma_don, sdt_4_so_cuoi })
