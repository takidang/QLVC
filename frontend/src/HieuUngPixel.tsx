import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useLocation } from 'react-router-dom'
import { dangHieuUngPixel } from './nen'

// Hiệu ứng Pixel: tia laser quét dọc và 4 góc ngắm 8-bit trên khung camera QR
export function TiaLaserPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-laser" aria-hidden="true">
      <span className="px-laser-goc tl" />
      <span className="px-laser-goc tr" />
      <span className="px-laser-goc bl" />
      <span className="px-laser-goc br" />
      <span className="px-laser-thanh" />
    </div>
  )
}

// Hiệu ứng Pixel: con dấu "ĐÃ GIAO" đóng xuống xoay nhẹ, nảy rồi tự mờ sau ~1,2 s
export function ConDauDaGiaoPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-con-dau" aria-hidden="true">
      <span className="px-con-dau-khung">
        <span className="px-con-dau-chu">ĐÃ GIAO</span>
      </span>
    </div>
  )
}

// Hiệu ứng Pixel: hạt bụi ô vuông nhỏ bật ra khi khối hàng rơi xuống sàn thùng xe
export function BuiThaHangPixel({ x, w, y }: { x: number; w: number; y: number }) {
  if (!dangHieuUngPixel()) return null
  const giua = x + w / 2
  return (
    <g className="px-bui-roi" aria-hidden="true">
      <rect x={Math.max(x - 4, 24)} y={y - 6} width={5} height={5} className="px-bui-o" />
      <rect x={giua - 2} y={y - 5} width={4} height={4} className="px-bui-o nhat" />
      <rect x={Math.min(x + w, 444)} y={y - 6} width={5} height={5} className="px-bui-o" />
    </g>
  )
}

const MOC_HANH_TRINH = [
  { ma: 'CHO_GHEP', ten: 'Tiếp nhận' },
  { ma: 'DA_GHEP', ten: 'Xếp chuyến' },
  { ma: 'DA_LAY', ten: 'Vận chuyển' },
  { ma: 'DA_GIAO', ten: 'Đã giao' },
] as const

function viTriHanhTrinh(
  trangThai: string,
  moc: { trang_thai: string; luc: string }[],
): { buoc: number; kieu: 'chay' | 'xong' | 'canh-bao' | 'huy' } {
  if (trangThai === 'CHO_GHEP') return { buoc: 0, kieu: 'chay' }
  if (trangThai === 'DA_GHEP') return { buoc: 1, kieu: 'chay' }
  if (trangThai === 'DA_LAY') return { buoc: 2, kieu: 'chay' }
  if (trangThai === 'DA_GIAO') return { buoc: 3, kieu: 'xong' }
  if (trangThai === 'THAT_BAI' || trangThai === 'TRA_HANG') {
    return { buoc: 2, kieu: 'canh-bao' }
  }
  let buoc = 0
  for (const m of moc) {
    if (m.trang_thai === 'DA_LAY') buoc = Math.max(buoc, 2)
    else if (m.trang_thai === 'DA_GHEP') buoc = Math.max(buoc, 1)
  }
  return { buoc, kieu: trangThai === 'HUY' ? 'huy' : 'chay' }
}

// Hiệu ứng Pixel: dải 4 mốc hành trình và xe tải pixel chạy tới mốc hiện tại ở trang Tra cứu
export function XeTaiHanhTrinhPixel({
  trangThai,
  moc,
}: {
  trangThai: string
  moc: { trang_thai: string; luc: string }[]
}) {
  if (!dangHieuUngPixel()) return null
  const { buoc, kieu } = viTriHanhTrinh(trangThai, moc)
  const tyLe = buoc / (MOC_HANH_TRINH.length - 1)
  const dich = `${(tyLe * 100).toFixed(3)}%`
  const bien = { '--px-xe-dich': dich, '--px-ty-le': String(tyLe) } as CSSProperties

  return (
    <div className={`px-hanh-trinh ${kieu}`} style={bien} aria-hidden="true">
      <div className="px-duong-xe">
        <div className="px-xe-chay-bo">
          <svg
            className="px-xe-tai"
            viewBox="0 0 32 18"
            width={32}
            height={18}
            shapeRendering="crispEdges"
          >
            <rect x={0} y={11} width={2} height={2} className="px-xe-khoi" />
            <rect x={2} y={3} width={18} height={10} className="px-xe-thung" />
            <rect x={4} y={5} width={14} height={2} className="px-xe-soc" />
            <rect x={20} y={5} width={6} height={1} className="px-xe-dau" />
            <rect x={20} y={6} width={9} height={7} className="px-xe-dau" />
            <rect x={23} y={7} width={4} height={3} className="px-xe-kinh" />
            <rect x={1} y={13} width={29} height={2} className="px-xe-gam" />
            <rect x={5} y={14} width={5} height={4} className="px-xe-banh" />
            <rect x={7} y={15} width={1} height={2} className="px-xe-mam" />
            <rect x={22} y={14} width={5} height={4} className="px-xe-banh" />
            <rect x={24} y={15} width={1} height={2} className="px-xe-mam" />
          </svg>
        </div>
      </div>
      <div className="px-duong-ray">
        <span className="px-duong-tien" />
        <div className="px-moc-ds">
          {MOC_HANH_TRINH.map((m, i) => (
            <span
              key={m.ma}
              className={
                i < buoc ? 'px-moc-diem xong' : i === buoc ? 'px-moc-diem toi' : 'px-moc-diem'
              }
            />
          ))}
        </div>
      </div>
      <div className="px-moc-nhan">
        {MOC_HANH_TRINH.map((m, i) => (
          <span key={m.ma} className={i === buoc ? 'toi' : undefined}>
            {m.ten}
          </span>
        ))}
      </div>
    </div>
  )
}

const TRANG_CHUYEN_HUONG = new Set(['/quan-ly', '/dieu-phoi', '/ke-toan', '/tai-xe'])
const COT_CHUYEN_TRANG = [0, 1, 2, 3, 4, 5, 6, 7] as const

// Hiệu ứng Pixel: chuyển trang khung hình 8-bit (che màn bằng dải ô vuông theo steps(), ≤ 250 ms)
export function ChuyenTrangPixel() {
  const { pathname } = useLocation()
  const truoc = useRef(pathname)
  const [lan, setLan] = useState(0)

  useEffect(() => {
    if (pathname === truoc.current) return
    truoc.current = pathname
    if (TRANG_CHUYEN_HUONG.has(pathname) || !dangHieuUngPixel()) return
    setLan((n) => n + 1)
  }, [pathname])

  useEffect(() => {
    if (lan === 0) return
    const t = window.setTimeout(() => setLan(0), 240)
    return () => window.clearTimeout(t)
  }, [lan])

  if (lan === 0 || !dangHieuUngPixel()) return null
  return (
    <div key={lan} className="px-chuyen-trang" aria-hidden="true">
      {COT_CHUYEN_TRANG.map((i) => (
        <span key={i} className="px-chuyen-o" style={{ '--px-i': i } as CSSProperties} />
      ))}
    </div>
  )
}
