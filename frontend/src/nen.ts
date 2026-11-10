// Mỗi lần mở web chọn ngẫu nhiên một ảnh đăng nhập kèm bộ màu hợp với ảnh đó (áp cho cả app).
// Khi có nút đổi bộ màu trong Cài đặt thì lựa chọn đã lưu của người dùng phải thắng.
const DS = [
  { anh: '/anh/dang-nhap-hoang-hon.webp', mau: 'suong' }, // trời xanh chuyển cam → Sương xanh
  { anh: '/anh/dang-nhap-luot-ngang.webp', mau: 'cat' }, // tông be xám → Cát ấm
]

export const NEN = DS[Math.floor(Math.random() * DS.length)]
document.documentElement.dataset.mau = NEN.mau
