import type { Chuyen } from './chuyen'
import { goi, query } from './goi'
import type { DanhSach } from './xe'

// Trang tài xế (UC-17). shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06)
export type NhomChuyen = 'can_lam' | 'da_xong'
export type ChuyenCuaToi = Chuyen & { so_don: number }
export type DiemCuaToi = {
  thu_tu: number
  nut: string
  viec: 'LAY' | 'GIAO'
  eta: string
  don_id: number
  ma_don: string
  ten_khach: string
  mo_ta: string | null
  kg: string
  m3: string
  so_kien: number
  trang_thai_don: string
  da_lay: boolean // đã quét lấy trong chuyến này
  dia_chi: string
  nguoi_lien_he: string | null
  sdt: string
  lay_tu: string | null
  lay_den: string | null
  han_giao: string
}
export type ChuyenCuaToiChiTiet = ChuyenCuaToi & {
  luong_tai_xe_chot: number | null
  lich_trinh: DiemCuaToi[]
}

export const chuyenCuaToi = (loc: { nhom: NhomChuyen; trang?: number; so_dong?: number }) =>
  goi<DanhSach<ChuyenCuaToi>>(`/api/toi/chuyen?${query(loc)}`)
export const chuyenCuaToiChiTiet = (id: number) => goi<ChuyenCuaToiChiTiet>(`/api/toi/chuyen/${id}`)

export const TEN_TRANG_THAI: Record<string, string> = {
  DA_CHOT: 'Chờ chạy',
  DANG_CHAY: 'Đang chạy',
  HOAN_THANH: 'Hoàn thành',
  DA_QUYET_TOAN: 'Đã quyết toán',
}
export const ngayGio = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })

// UC-18: bắt đầu / kết thúc chuyến – multipart (km + ảnh đồng hồ đã nén), trả lại chi tiết chuyến
export function ghiKm(id: number, viec: 'bat-dau' | 'ket-thuc', km: number, anh: Blob) {
  const form = new FormData()
  form.append(viec === 'bat-dau' ? 'km_bat_dau' : 'km_ket_thuc', String(km))
  form.append('anh_dong_ho', anh, 'dong-ho.jpg')
  return goi<ChuyenCuaToiChiTiet>(`/api/toi/chuyen/${id}/${viec}`, { method: 'POST', body: form })
}

// UC-19: quét mã lấy / báo không lấy được – multipart; giờ quét do máy chủ ghi, chỉ gửi mã, tọa độ, ảnh
export type LoaiQuet = 'LAY' | 'KHONG_LAY' | 'GIAO' | 'GIAO_THAT_BAI'
// `loai` không do máy chủ trả: gắn thêm ở đây để câu báo phân biệt lấy / giao
export type KetQuaQuet = {
  ma_don: string
  trang_thai: string
  canh_bao: string[]
  lap_lai: boolean
  loai: LoaiQuet
}
export type LyDo = { id: number; ten: string; ap_dung: 'LAY' | 'GIAO'; phia: 'KHACH' | 'SU_CO_XE' }
export type Gps = { lat: number; lng: number; do_chinh_xac_m: number }

export const lyDo = (ap_dung: 'LAY' | 'GIAO') =>
  goi<LyDo[]>(`/api/danh-muc/ly-do?ap_dung=${ap_dung}`)

export function quetMa(vao: {
  ma_don: string
  loai: LoaiQuet
  gps: Gps | null
  anh?: Blob[]
  ly_do_id?: number
  chu_ky?: Blob // UC-20: ảnh PNG người nhận ký (BR-41)
  ten_nguoi_nhan?: string
}) {
  const form = new FormData()
  form.append('ma_don', vao.ma_don)
  form.append('loai', vao.loai)
  if (vao.gps) {
    form.append('lat', vao.gps.lat.toFixed(6))
    form.append('lng', vao.gps.lng.toFixed(6))
    form.append('do_chinh_xac_m', vao.gps.do_chinh_xac_m.toFixed(1))
  }
  vao.anh?.forEach((a, i) => form.append('anh', a, `anh-${i + 1}.jpg`))
  if (vao.ly_do_id !== undefined) form.append('ly_do_id', String(vao.ly_do_id))
  if (vao.chu_ky) form.append('chu_ky', vao.chu_ky, 'chu-ky.png')
  if (vao.ten_nguoi_nhan !== undefined) form.append('ten_nguoi_nhan', vao.ten_nguoi_nhan)
  return goi<Omit<KetQuaQuet, 'loai'>>('/api/toi/quet', { method: 'POST', body: form }).then(
    (kq): KetQuaQuet => ({ ...kq, loai: vao.loai }),
  )
}

// BR-43: xin vị trí lúc quét; từ chối hoặc quá 8 giây thì gửi không tọa độ (máy chủ gắn cờ thiếu GPS)
export const layGps = () =>
  new Promise<Gps | null>((xong) => {
    if (!navigator.geolocation) return xong(null)
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => xong({ lat: c.latitude, lng: c.longitude, do_chinh_xac_m: c.accuracy }),
      () => xong(null),
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 },
    )
  })

const TEN_KET_QUA: Record<string, string> = {
  DA_LAY: 'đã lấy',
  DA_GIAO: 'đã giao',
  THAT_BAI: 'đã báo thất bại',
}

const VIEC_XONG: Record<LoaiQuet, string> = {
  LAY: 'Đã lấy',
  KHONG_LAY: 'Đã báo không lấy được',
  GIAO: 'Đã giao',
  GIAO_THAT_BAI: 'Đã báo giao không được',
}
const CANH_BAO: Record<string, string> = {
  THIEU_GPS: 'Không lấy được vị trí GPS: lượt quét vẫn ghi nhận, gắn cờ thiếu GPS (BR-43)',
  GIAO_TRE: 'Giao sau hạn giao: đơn được đánh dấu giao trễ, cước giữ nguyên (BR-72)',
}

// Câu báo sau khi quét (UC-19, 20): "Đã lấy / Đã giao: mã đơn, số kiện" – số kiện lấy từ lịch trình UC-17
export function thongBaoQuet(kq: KetQuaQuet, c: ChuyenCuaToiChiTiet) {
  const kien = c.lich_trinh.find((p) => p.ma_don === kq.ma_don)?.so_kien
  const coKien = kq.loai === 'LAY' || kq.loai === 'GIAO'
  const xong = kq.lap_lai
    ? `Đơn ${kq.ma_don} ${TEN_KET_QUA[kq.trang_thai] ?? kq.trang_thai} từ trước, không ghi thêm (BR-45)`
    : `${VIEC_XONG[kq.loai]} ${kq.ma_don}${coKien && kien ? ` (${kien} kiện)` : ''}`
  return { xong, canhBao: kq.canh_bao.map((m) => CANH_BAO[m] ?? m) }
}
