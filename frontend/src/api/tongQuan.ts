import { goi, query } from './goi'

// UC-38: tình hình một ngày (GET /api/tong-quan?ngay=, bỏ trống = hôm nay; QL, DP, KT)
export type TongQuanNgay = {
  ngay: string
  chuyen: { tong: number; theo_trang_thai: Record<string, number> }
  don: { tong: number; da_giao: number; that_bai: number; con_lai: number; kg_da_cho: number }
  dung_gio: { nguong_tre_phut: number; da_quet: number; dung_gio: number; ty_le: number | null }
  doanh_thu_du_kien: number // dự kiến, gồm cả đơn thất bại
}
export const tongQuanNgay = (ngay?: string) =>
  goi<TongQuanNgay>(`/api/tong-quan?${query({ ngay })}`)
