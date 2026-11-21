import type { ReactNode } from 'react'
import { useNgayBaoTruoc } from '../api/cauHinh'
import { Ic, Nhan } from '../nhan'

// Phần chung của các màn danh mục (06): đầu trang thấp hơn màn Chuyến (docs/giao-dien.md), nút thêm,
// lọc trạng thái dạng viên thuốc như bảng chuyến, nhãn Hoạt động / Ngừng

export function DauDanhMuc({
  tieuDe,
  phu,
  nut,
  onNut,
}: {
  tieuDe: string
  phu?: ReactNode
  nut?: string
  onNut?: () => void
}) {
  return (
    <div className="dm-dau">
      <div>
        <h1>{tieuDe}</h1>
        {phu && <p>{phu}</p>}
      </div>
      {nut && onNut && (
        <button onClick={onNut}>
          <Ic ten="cong" />
          {nut}
        </button>
      )}
    </div>
  )
}

const HOAT_DONG_NGUNG: [string, string][] = [
  ['', 'Tất cả'],
  ['HOAT_DONG', 'Hoạt động'],
  ['NGUNG', 'Ngừng'],
]

export function LocTrangThai({
  chon,
  ds = HOAT_DONG_NGUNG,
  onChon,
  nhan = 'Lọc trạng thái',
}: {
  chon: string
  ds?: [string, string][]
  onChon: (ma: string) => void
  nhan?: string
}) {
  return (
    <div className="vien-thuoc" role="group" aria-label={nhan}>
      {ds.map(([ma, ten]) => (
        <button key={ma} aria-pressed={chon === ma} onClick={() => onChon(ma)}>
          {ten}
        </button>
      ))}
    </div>
  )
}

// Ô tìm trong thanh công cụ của bảng, đứng bên phải
export function OTim({
  giaTri,
  goiY,
  onDoi,
}: {
  giaTri: string
  goiY: string
  onDoi: (v: string) => void
}) {
  return (
    <div className="dm-tim">
      <input
        type="search"
        placeholder={goiY}
        aria-label={goiY}
        value={giaTri}
        onChange={(e) => onDoi(e.target.value)}
      />
    </div>
  )
}

// Dùng lại hình của nhãn chuyến: hoạt động = vòng đặc dấu tích, ngừng = vòng dấu x (xám)
export const NhanHoatDong = ({ trangThai }: { trangThai: string }) =>
  trangThai === 'HOAT_DONG' ? (
    <Nhan loai="HOAN_THANH">Hoạt động</Nhan>
  ) : (
    <Nhan loai="HUY">Ngừng</Nhan>
  )

// Giấy tờ: hết hạn đỏ, còn ≤ CFG-02 ngày cam (như khung "Cần chú ý" màn Chuyến)
// Số ngày từ hôm nay (giờ máy, Việt Nam) tới hạn; âm là đã quá hạn
function soNgayToi(han: string) {
  const homNay = new Date(new Date().toLocaleDateString('sv-SE'))
  return Math.round((new Date(han).getTime() - homNay.getTime()) / 86_400_000)
}
export function HanGiayTo({ han }: { han: string }) {
  const ngayBaoTruoc = useNgayBaoTruoc()
  const conLai = soNgayToi(han)
  const ngay = han.split('-').reverse().join('/')
  if (conLai < 0) return <span className="het-han">{ngay} · hết hạn</span>
  if (conLai <= ngayBaoTruoc)
    return (
      <span className="han-sap">
        {ngay} · còn {conLai} ngày
      </span>
    )
  return <span>{ngay}</span>
}
