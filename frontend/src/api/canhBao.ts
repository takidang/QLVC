import { goi } from './goi'

// UC-27: bảng cảnh báo của điều phối (api.md, GET /api/canh-bao)
export type CanhBao = {
  cau_hinh: { ngay_bao_truoc: number; nguong_tre_phut: number; gio_cho_ghep: number }
  giay_to: {
    doi_tuong: 'XE' | 'TAI_XE'
    id: number
    ten: string
    loai: 'DANG_KIEM' | 'BAO_HIEM' | 'GPLX'
    han: string
    con_ngay: number
    het_han: boolean
  }[]
  chuyen_tre: {
    chuyen_id: number
    ma_chuyen: string
    bien_so: string
    ten_tai_xe: string
    tre_phut: number | null
    ket_thuc_dang_chay: string | null
    chong: string[]
  }[]
  su_co_mo: {
    su_co_id: number
    chuyen_id: number
    ma_chuyen: string
    bien_so: string
    ten_tai_xe: string
    loai: string
    ghi_chu: string | null
    luc: string
  }[]
  don_sap_qua_han: {
    don_id: number
    ma_don: string
    ten_khach: string
    tinh_lay: string
    tinh_giao: string
    han_giao: string
    con_phut: number
    qua_han: boolean
  }[]
  thieu_gps: unknown[]
  so_viec: number
}
export const canhBao = () => goi<CanhBao>('/api/canh-bao')
