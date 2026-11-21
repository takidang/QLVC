import { useEffect, useState } from 'react'
import { goi } from './goi'

// CFG-02 cho giao diện tô cam giấy tờ sắp hết hạn (api.md, GET /api/cau-hinh/ngay-bao-truoc)
const MAC_DINH = 30
let cho: Promise<number> | null = null
let giaTri: number | null = null

export function ngayBaoTruoc(): Promise<number> {
  if (!cho) {
    cho = goi<{ ngay_bao_truoc: number }>('/api/cau-hinh/ngay-bao-truoc')
      .then((r) => {
        giaTri = r.ngay_bao_truoc
        return giaTri
      })
      .catch(() => {
        cho = null // lỗi (mạng, hết phiên) thì lần dựng sau gọi lại, không nhớ 30 mãi
        return MAC_DINH
      })
  }
  return cho
}

// Quản lý vừa lưu cấu hình: bỏ số đã nhớ để trang sau trong cùng tab lấy số mới (góp ý Kiệt #75)
export function quenNgayBaoTruoc() {
  cho = null
  giaTri = null
}

// shortcut: hiện 30 (mặc định CFG-02) tới khi số thật về; lỗi mạng thì giữ 30
export function useNgayBaoTruoc(): number {
  const [ngay, setNgay] = useState(giaTri ?? MAC_DINH)
  useEffect(() => {
    let bo = false
    ngayBaoTruoc().then((n) => {
      if (!bo) setNgay(n)
    })
    return () => {
      bo = true
    }
  }, [])
  return ngay
}
