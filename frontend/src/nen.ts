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
const KHOA = 'qlvc-che-do'
const mayToi = matchMedia('(prefers-color-scheme: dark)')

export const cheDoDaLuu = () => localStorage.getItem(KHOA) ?? ''
export function apCheDo(ma: string) {
  if (ma) localStorage.setItem(KHOA, ma)
  else localStorage.removeItem(KHOA)
  document.documentElement.dataset.cheDo = ma || (mayToi.matches ? 'toi' : 'sang')
}
apCheDo(cheDoDaLuu())
mayToi.addEventListener('change', () => apCheDo(cheDoDaLuu()))
