import type { ReactNode } from 'react'

// Biểu tượng nét mảnh tự vẽ (lưới 24), màu theo chữ xung quanh
const DUONG = {
  cong: <path d="M12 5v14M5 12h14" />,
  phai: <path d="M9 6l6 6-6 6" />,
  xuong: <path d="M6 9l6 6 6-6" />,
  'dong-ho': (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  'canh-bao': <path d="M12 4 2.5 20h19zM12 10v4.5M12 17.2v.3" />,
  // Menu cột trái (v3)
  chuyen: (
    <>
      <circle cx="6" cy="18" r="2.2" />
      <circle cx="18" cy="5" r="2.2" />
      <path d="M8.2 18h6.3a3.25 3.25 0 0 0 0-6.5h-5a3.25 3.25 0 0 1 0-6.5h6.3" />
    </>
  ),
  don: (
    <>
      <path d="M4 8.2 12 4l8 4.2v7.6L12 20l-8-4.2z" />
      <path d="M4 8.2l8 4.2 8-4.2M12 12.4V20" />
    </>
  ),
  xe: (
    <>
      <path d="M3 6.5h10.5v10H3zM13.5 10h4l3.5 3.5v3h-7.5" />
      <circle cx="7.5" cy="17.5" r="1.8" />
      <circle cx="17" cy="17.5" r="1.8" />
    </>
  ),
  'tai-xe': (
    <>
      <circle cx="12" cy="8" r="3.6" />
      <path d="M4.5 20c.6-3.6 3.6-5.5 7.5-5.5s6.9 1.9 7.5 5.5" />
    </>
  ),
  'khach-hang': <path d="M5 20V5.5h9V20M14 10h5v10M3.5 20h17M8 9h3M8 12.5h3M8 16h3" />,
  nut: (
    <>
      <path d="M12 20.5s6.5-5.6 6.5-10.5a6.5 6.5 0 0 0-13 0c0 4.9 6.5 10.5 6.5 10.5z" />
      <circle cx="12" cy="10" r="2.3" />
    </>
  ),
  tuyen: <path d="M6 4v16M6 7.5h9l3 2.5-3 2.5H6" />,
  'tong-quan': <path d="M4 4v16h16M8.5 16v-5M12.5 16V8M16.5 16v-3" />,
  'cong-no': <path d="M6 3.5h12v17l-3-1.8-3 1.8-3-1.8-3 1.8zM9 8.5h6M9 12h6" />,
  'quyet-toan': <path d="M4.5 5.5h15v13h-15zM8 12.2l2.6 2.6 5.4-5.6" />,
  'tam-ung': (
    <path d="M17 5H5.5A1.5 1.5 0 0 0 4 6.5V18a1.5 1.5 0 0 0 1.5 1.5h13A1.5 1.5 0 0 0 20 18V9a1.5 1.5 0 0 0-1.5-1.5H4M16 13.5h.5" />
  ),
  'chi-phi-xe': <path d="M4.5 6.5h15v13h-15zM4.5 10.5h15M8.5 4v4M15.5 4v4" />,
  'nguoi-dung': (
    <>
      <circle cx="9" cy="8.5" r="3.2" />
      <path d="M3 19.5c.5-3 2.8-4.8 6-4.8s5.5 1.8 6 4.8M16 5.6a3.2 3.2 0 0 1 0 5.8M18 15c1.7.6 2.7 2 3 4.5" />
    </>
  ),
  'bang-gia': (
    <>
      <path d="M12.5 3.5h8v8l-9 9-8-8z" />
      <circle cx="16" cy="8" r="1.3" />
    </>
  ),
  'cau-hinh': (
    <>
      <path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1" />
      <circle cx="15" cy="7" r="2" />
      <circle cx="9" cy="12" r="2" />
      <circle cx="17" cy="17" r="2" />
    </>
  ),
}
export type TenIc = keyof typeof DUONG
export const Ic = ({ ten }: { ten: TenIc }) => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    {DUONG[ten]}
  </svg>
)

// Hình của nhãn (lưới 16): mỗi trạng thái một hình riêng, không chỉ dựa vào màu (docs/giao-dien.md)
const net = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round',
} as const
const vong = <circle cx="8" cy="8" r="5.5" {...net} />
const HINH: Record<string, ReactNode> = {
  lap: <circle cx="8" cy="8" r="5.5" {...net} strokeDasharray="2.3 2.02" strokeLinecap="butt" />,
  chot: (
    <>
      {vong}
      <circle cx="8" cy="8" r="2.2" fill="currentColor" />
    </>
  ),
  chay: (
    <>
      {vong}
      <path d="M8 2.5a5.5 5.5 0 0 1 0 11z" fill="currentColor" />
    </>
  ),
  xong: (
    <>
      <circle cx="8" cy="8" r="6.25" fill="currentColor" />
      <path d="M5.2 8.2l1.9 1.9 3.7-4" {...net} stroke="var(--nen)" strokeLinejoin="round" />
    </>
  ),
  huy: (
    <>
      {vong}
      <path d="M6 6l4 4M10 6l-4 4" {...net} />
    </>
  ),
  tre: (
    <>
      {vong}
      <path d="M8 5v3.2l2 1.3" {...net} strokeLinejoin="round" />
    </>
  ),
  suco: (
    <>
      <path d="M8 2.5 1.8 13.2h12.4z" {...net} strokeLinejoin="round" />
      <path d="M8 6.5v3M8 11.3v.2" {...net} />
    </>
  ),
}
// Mã trạng thái chuyến hoặc mã cờ → [hình, lớp màu]
const LOAI: Record<string, [string, string]> = {
  LAP: ['lap', ''],
  DA_CHOT: ['chot', 'chot'],
  DANG_CHAY: ['chay', 'chay'],
  HOAN_THANH: ['xong', 'xong'],
  DA_QUYET_TOAN: ['xong', 'qt'],
  HUY: ['huy', ''],
  TRE: ['tre', 'tre'],
  // Trễ của chuyến đã xong: chỉ là thông tin, không tô đặc để khỏi báo động sai
  TRE_XONG: ['tre', 'tre-nhe'],
  SU_CO: ['suco', 'suco'],
  THAT_BAI: ['suco', 'suco'],
  CHONG_LICH: ['suco', 'suco'],
  CHUA_QUYET_TOAN: ['tre', ''],
}

export function Nhan({
  loai,
  title,
  children,
}: {
  loai: string
  title?: string
  children: ReactNode
}) {
  const [hinh, lop] = LOAI[loai] ?? ['lap', '']
  return (
    <span className={`nhan ${lop}`} title={title}>
      <svg viewBox="0 0 16 16" aria-hidden="true">
        {HINH[hinh]}
      </svg>
      {children}
    </span>
  )
}
