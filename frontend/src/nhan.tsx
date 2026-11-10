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
}
export const Ic = ({ ten }: { ten: keyof typeof DUONG }) => (
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
