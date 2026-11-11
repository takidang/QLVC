// Mỗi lần mở web chọn ngẫu nhiên một ảnh đăng nhập kèm bộ màu hợp với ảnh đó (áp cho cả app).
// Người dùng đã chọn bộ màu trong menu tài khoản (lưu trên trình duyệt) thì lựa chọn đó thắng.
const DS = [
  { anh: '/anh/dang-nhap-hoang-hon.webp', mau: 'suong' }, // trời xanh chuyển cam → Sương xanh
  { anh: '/anh/dang-nhap-luot-ngang.webp', mau: 'cat' }, // tông be xám → Cát ấm
]

export const BO_MAU = [
  { ma: 'da', ten: 'Đá xám xanh', nen: '#c4c8be', nhan: '#56624a' },
  { ma: 'suong', ten: 'Sương xanh', nen: '#c3cad3', nhan: '#3f5673' },
  { ma: 'cat', ten: 'Cát ấm', nen: '#d2cabb', nhan: '#6b5540' },
  { ma: 'ngoc', ten: 'Ngọc xanh', nen: '#bfcbc8', nhan: '#2f5f58' },
  { ma: 'oai', ten: 'Oải hương', nen: '#cac6cf', nhan: '#54486e' },
] as const
const KHOA = 'qlvc-bo-mau'

export const NEN = DS[Math.floor(Math.random() * DS.length)]

// '' = ngẫu nhiên theo ảnh; 'da' là bộ mặc định (không gắn data-mau)
export const mauDaLuu = () => localStorage.getItem(KHOA) ?? ''
export function apMau(ma: string) {
  if (ma) localStorage.setItem(KHOA, ma)
  else localStorage.removeItem(KHOA)
  const dung = ma || NEN.mau
  if (dung === 'da') delete document.documentElement.dataset.mau
  else document.documentElement.dataset.mau = dung
}
apMau(mauDaLuu())
