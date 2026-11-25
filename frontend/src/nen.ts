// Ảnh nền (đăng nhập, đầu màn Chuyến, tra cứu): mỗi lần mở web chọn ngẫu nhiên một ảnh.
const DS = ['/anh/dang-nhap-hoang-hon.webp', '/anh/dang-nhap-luot-ngang.webp']
// Pixel: banner đầu màn Chuyến cũng chọn ngẫu nhiên một trong hai ảnh pixel (kho vận / cảng)
const DS_BANNER_PIXEL = ['/anh/banner-kho-pixel.png', '/anh/banner-cang-pixel.png']
export const NEN = {
  anh: DS[Math.floor(Math.random() * DS.length)],
  bannerPixel: DS_BANNER_PIXEL[Math.floor(Math.random() * DS_BANNER_PIXEL.length)],
}

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
  // Phong cách Pixel chỉ có bản sáng: bật Pixel thì luôn sáng, lựa chọn sáng/tối vẫn được lưu
  document.documentElement.dataset.cheDo =
    phongCachDaLuu() === 'pixel' ? 'sang' : ma || (mayToi.matches ? 'toi' : 'sang')
}

// Phong cách (THỬ NGHIỆM): '' = hiện tại (mặc định), 'pixel' = lớp áo phong-cach-pixel.css (chỉ bản sáng)
export const PHONG_CACH = [
  { ma: '', ten: 'Hiện tại' },
  { ma: 'pixel', ten: 'Pixel (thử nghiệm)' },
] as const
const KHOA_PHONG_CACH = 'qlvc-phong-cach'

export function phongCachDaLuu() {
  return localStorage.getItem(KHOA_PHONG_CACH) === 'pixel' ? 'pixel' : ''
}
export function apPhongCach(ma: string) {
  if (ma === 'pixel') {
    localStorage.setItem(KHOA_PHONG_CACH, 'pixel')
    document.documentElement.dataset.phongCach = 'pixel'
  } else {
    localStorage.removeItem(KHOA_PHONG_CACH)
    delete document.documentElement.dataset.phongCach
  }
  apCheDo(cheDoDaLuu())
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

// Con trỏ đi theo: 'bat' (mặc định) | 'tat'. Độc lập với hạt nền và chữ gõ; vẫn tắt khi Hiệu ứng nâng cao tắt hoặc giảm chuyển động.
export const CON_TRO = HIEU_UNG
const KHOA_CON_TRO = 'qlvc-con-tro'
export const conTroDaLuu = (): 'bat' | 'tat' =>
  localStorage.getItem(KHOA_CON_TRO) === 'tat' ? 'tat' : 'bat'
export function apConTro(ma: string) {
  localStorage.setItem(KHOA_CON_TRO, ma === 'tat' ? 'tat' : 'bat')
}
// Phong cách Pixel đã có hiệu ứng riêng nên không chạy đàn con trỏ (tránh trùng hiệu ứng)
export const dangConTro = () =>
  conTroDaLuu() === 'bat' && dangHieuUng() && phongCachDaLuu() !== 'pixel'

// Hiệu ứng Pixel (chỉ có nghĩa khi Phong cách = Pixel): 'tat' thì giữ màu/viền/bóng, bỏ chuyển động riêng của Pixel
export const HIEU_UNG_PIXEL = HIEU_UNG
const KHOA_HU_PIXEL = 'qlvc-hieu-ung-pixel'
export const hieuUngPixelDaLuu = (): 'bat' | 'tat' =>
  localStorage.getItem(KHOA_HU_PIXEL) === 'tat' ? 'tat' : 'bat'
export function apHieuUngPixel(ma: string) {
  if (ma === 'tat') {
    localStorage.setItem(KHOA_HU_PIXEL, 'tat')
    document.documentElement.dataset.hieuUngPixel = 'tat'
  } else {
    localStorage.removeItem(KHOA_HU_PIXEL)
    delete document.documentElement.dataset.hieuUngPixel
  }
}
// Hiệu ứng Pixel: chỉ chạy khi bật phong cách Pixel, bật công tắc và không giảm chuyển động
export const dangHieuUngPixel = () =>
  phongCachDaLuu() === 'pixel' && hieuUngPixelDaLuu() !== 'tat' && !giamChuyenDong()

// Người dùng bấm đổi chế độ: làm mờ chéo ngắn (View Transitions, CSS ::view-transition-*) thay vì đổi
// màu cả màn trong một nhát. Lần áp lúc tải trang và khi máy đổi chế độ vẫn gọi apCheDo thẳng.
export function doiCheDo(ma: string) {
  const d = document as Document & { startViewTransition?: (cb: () => void) => unknown }
  if (d.startViewTransition && !giamChuyenDong()) d.startViewTransition(() => apCheDo(ma))
  else apCheDo(ma)
}

// Áp toàn bộ tùy chọn đã lưu ngay khi khởi động app (main.tsx import file này trước App)
apPhongCach(phongCachDaLuu())
apMatDo(matDoDaLuu())
apCoChu(coChuDaLuu())
apGiamChuyenDong(giamChuyenDongDaLuu())
document.documentElement.dataset.hieuUng = hieuUngDaLuu()
apHieuUngPixel(hieuUngPixelDaLuu())
mayToi.addEventListener('change', () => apCheDo(cheDoDaLuu()))
