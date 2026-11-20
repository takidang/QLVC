// Ảnh nền (đăng nhập, đầu màn Chuyến, tra cứu): mỗi lần mở web chọn ngẫu nhiên một ảnh.
const DS = ['/anh/dang-nhap-hoang-hon.webp', '/anh/dang-nhap-luot-ngang.webp']
export const NEN = { anh: DS[Math.floor(Math.random() * DS.length)] }

// Chế độ sáng / tối (v3): '' = theo máy. Lưu trên trình duyệt; đặt data-che-do trên <html>
// (index.css chỉ có một khối biến cho bản tối, nên "theo máy" cũng quy về sang / toi ở đây).
export const CHE_DO = [
  { ma: '', ten: 'Theo máy' },
  { ma: 'sang', ten: 'Sáng' },
  { ma: 'toi', ten: 'Tối' },
] as const
const KHOA_CHE_DO = 'qlvc-che-do'
const mayToi = matchMedia('(prefers-color-scheme: dark)')

export const cheDoDaLuu = () => localStorage.getItem(KHOA_CHE_DO) ?? ''
export function apCheDo(ma: string) {
  if (ma) localStorage.setItem(KHOA_CHE_DO, ma)
  else localStorage.removeItem(KHOA_CHE_DO)
  document.documentElement.dataset.cheDo = ma || (mayToi.matches ? 'toi' : 'sang')
}

// Mật độ bảng và danh sách: '' = thoải mái (mặc định), 'gon' = thu gọn padding qua biến CSS
export const MAT_DO = [
  { ma: '', ten: 'Thoải mái' },
  { ma: 'gon', ten: 'Gọn' },
] as const
const KHOA_MAT_DO = 'qlvc-mat-do'

export const matDoDaLuu = () => (localStorage.getItem(KHOA_MAT_DO) === 'gon' ? 'gon' : '')
export function apMatDo(ma: string) {
  if (ma === 'gon') {
    localStorage.setItem(KHOA_MAT_DO, 'gon')
    document.documentElement.dataset.matDo = 'gon'
  } else {
    localStorage.removeItem(KHOA_MAT_DO)
    delete document.documentElement.dataset.matDo
  }
}

// Cỡ chữ: '' = vừa (mặc định), 'lon' = tăng cỡ chữ gốc ~112,5%
export const CO_CHU = [
  { ma: '', ten: 'Vừa' },
  { ma: 'lon', ten: 'Lớn' },
] as const
const KHOA_CO_CHU = 'qlvc-co-chu'

export const coChuDaLuu = () => (localStorage.getItem(KHOA_CO_CHU) === 'lon' ? 'lon' : '')
export function apCoChu(ma: string) {
  if (ma === 'lon') {
    localStorage.setItem(KHOA_CO_CHU, 'lon')
    document.documentElement.dataset.coChu = 'lon'
  } else {
    localStorage.removeItem(KHOA_CO_CHU)
    delete document.documentElement.dataset.coChu
  }
}

// Giảm chuyển động: '' = theo máy (mặc định), 'bat' = tắt transition/animation và số chạy NumberFlow
export const GIAM_CHUYEN_DONG = [
  { ma: '', ten: 'Theo máy' },
  { ma: 'bat', ten: 'Bật' },
] as const
const KHOA_GIAM_CD = 'qlvc-giam-chuyen-dong'

export const giamChuyenDongDaLuu = () => (localStorage.getItem(KHOA_GIAM_CD) === 'bat' ? 'bat' : '')
export const dangGiamChuyenDong = () => giamChuyenDongDaLuu() === 'bat'
export function apGiamChuyenDong(ma: string) {
  if (ma === 'bat') {
    localStorage.setItem(KHOA_GIAM_CD, 'bat')
    document.documentElement.dataset.giamChuyenDong = 'bat'
  } else {
    localStorage.removeItem(KHOA_GIAM_CD)
    delete document.documentElement.dataset.giamChuyenDong
  }
}
// Tắt chuyển động khi người dùng bật trong Cài đặt hoặc hệ điều hành yêu cầu giảm chuyển động
export const giamChuyenDong = () =>
  dangGiamChuyenDong() || matchMedia('(prefers-reduced-motion: reduce)').matches

// Hiệu ứng nâng cao (v4): 'bat' (mặc định khi chưa lưu) | 'tat'. Tắt hoàn toàn khi giảm chuyển động.
export const HIEU_UNG = [
  { ma: 'bat', ten: 'Bật' },
  { ma: 'tat', ten: 'Tắt' },
] as const
const KHOA_HIEU_UNG = 'qlvc-hieu-ung'

export const hieuUngDaLuu = (): 'bat' | 'tat' =>
  localStorage.getItem(KHOA_HIEU_UNG) === 'tat' ? 'tat' : 'bat'
export function apHieuUng(ma: string) {
  const v = ma === 'tat' ? 'tat' : 'bat'
  localStorage.setItem(KHOA_HIEU_UNG, v)
  document.documentElement.dataset.hieuUng = v
}
export const dangHieuUng = () => hieuUngDaLuu() === 'bat' && !giamChuyenDong()

// Người dùng bấm đổi chế độ: làm mờ chéo ngắn (View Transitions, CSS ::view-transition-*) thay vì đổi
// màu cả màn trong một nhát. Lần áp lúc tải trang và khi máy đổi chế độ vẫn gọi apCheDo thẳng.
export function doiCheDo(ma: string) {
  const d = document as Document & { startViewTransition?: (cb: () => void) => unknown }
  if (d.startViewTransition && !giamChuyenDong()) d.startViewTransition(() => apCheDo(ma))
  else apCheDo(ma)
}

// Áp toàn bộ tùy chọn đã lưu ngay khi khởi động app (main.tsx import file này trước App)
apCheDo(cheDoDaLuu())
apMatDo(matDoDaLuu())
apCoChu(coChuDaLuu())
apGiamChuyenDong(giamChuyenDongDaLuu())
document.documentElement.dataset.hieuUng = hieuUngDaLuu()
mayToi.addEventListener('change', () => apCheDo(cheDoDaLuu()))
