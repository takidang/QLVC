import { useCallback, useEffect, useRef } from 'react'

// Phần logic của hộp xác nhận dùng chung (giao diện ở HopXacNhan.tsx): mỗi lúc chỉ một câu hỏi.
// Mọi đường không phải bấm nút đồng ý (Thôi, Esc, bấm nền, đổi trang, nơi hỏi bị tháo) đều trả false.
export type YeuCau = { ma: number; cau: string; nut: string }

let dang: (YeuCau & { chu: object; xong: (dongY: boolean) => void }) | null = null
let dem = 0
const nguoiNghe = new Set<() => void>()
const bao = () => nguoiNghe.forEach((f) => f())

export function theoDoi(f: () => void) {
  nguoiNghe.add(f)
  return () => void nguoiNghe.delete(f)
}
export const yeuCauDang = (): YeuCau | null => dang

export function hoiXacNhan(chu: object, cau: string, nut = 'Đồng ý'): Promise<boolean> {
  // Đang có câu hỏi mở: lần hỏi sau (bấm hai lần) coi như không đồng ý, không xếp hàng
  if (dang) return Promise.resolve(false)
  return new Promise((xong) => {
    dang = { ma: ++dem, cau, nut, chu, xong }
    bao()
  })
}

// ma: câu trả lời cho câu hỏi đã đóng thì bỏ qua
export function traLoi(ma: number, dongY: boolean) {
  if (dang?.ma !== ma) return
  const { xong } = dang
  dang = null
  bao()
  xong(dongY)
}

// Đóng câu đang mở với câu trả lời "không"; truyền chu thì chỉ đóng câu của nơi đó
export function huyXacNhan(chu?: object) {
  if (dang && (!chu || dang.chu === chu)) traLoi(dang.ma, false)
}

// const hoi = useXacNhan(); if (!(await hoi('Xóa?', 'Xóa'))) return
// Gắn câu hỏi với thành phần gọi: thành phần bị tháo thì câu hỏi tự đóng (false), hỏi sau khi tháo cũng false
export function useXacNhan() {
  const chu = useRef({ song: true })
  useEffect(() => {
    const o = chu.current
    o.song = true
    return () => {
      o.song = false
      huyXacNhan(o)
    }
  }, [])
  return useCallback(
    (cau: string, nut?: string) =>
      chu.current.song ? hoiXacNhan(chu.current, cau, nut) : Promise.resolve(false),
    [],
  )
}
