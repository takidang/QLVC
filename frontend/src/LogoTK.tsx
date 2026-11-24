// Logo TK (TAKI Logistics), vẽ bằng SVG để sắc nét và đổi màu được.
// Vẽ cả hai bản, CSS chọn bản hiện theo phong cách (phong-cach-pixel.css: .logo-thuong / .logo-pixel),
// nên đổi phong cách ở Cài đặt là logo đổi ngay, không cần tải lại.

// Bản thường: phẳng — thanh ngang chữ T màu than, thân T xanh, chữ K đỏ
function LogoThuong({ co }: { co: number }) {
  return (
    <svg
      className="logo-tk logo-thuong"
      width={co}
      height={co}
      viewBox="0 0 64 64"
      aria-hidden="true"
    >
      <rect x="4" y="12" width="34" height="9" rx="1.5" fill="#3a3e45" />
      <rect x="15" y="21" width="12" height="31" rx="1.5" fill="#2387bd" />
      <path d="M31 36 L49 12 H60 L42 36 Z" fill="#e2473b" />
      <path d="M31 36 H42 L60 52 H49 Z" fill="#e2473b" />
    </svg>
  )
}

// Bản Pixel: lưới ô vuông theo bảng màu Nostalgos — T vàng bơ, K san hô, viền than (tự sinh từ lưới)
const LUOI_TK = [
  'TTTTTTTTT..KKK',
  'TTTTTTTTT.KKK.',
  'TTTTTTTTTKKK..',
  '...TTT..KKK...',
  '...TTT.KKK....',
  '...TTTKKK.....',
  '...TTTKKK.....',
  '...TTT.KKK....',
  '...TTT..KKK...',
  '...TTT...KKK..',
  '...TTT....KKK.',
  '...TTT.....KKK',
] as const
const MAU_O: Record<string, string> = { T: '#ffd183', K: '#dc6250' }
const RONG = LUOI_TK[0].length + 2
const CAO = LUOI_TK.length + 2
const O_LOGO: { x: number; y: number; mau: string }[] = (() => {
  const co = (x: number, y: number) => LUOI_TK[y]?.[x] !== undefined && LUOI_TK[y][x] !== '.'
  const ds: { x: number; y: number; mau: string }[] = []
  for (let y = -1; y <= LUOI_TK.length; y++) {
    for (let x = -1; x <= LUOI_TK[0].length; x++) {
      if (co(x, y)) ds.push({ x: x + 1, y: y + 1, mau: MAU_O[LUOI_TK[y][x]] })
      else {
        let ke = false
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) ke ||= co(x + dx, y + dy)
        if (ke) ds.push({ x: x + 1, y: y + 1, mau: '#272a32' })
      }
    }
  }
  return ds
})()

function LogoPixel({ co }: { co: number }) {
  return (
    <svg
      className="logo-tk logo-pixel"
      width={co}
      height={Math.round((co * CAO) / RONG)}
      viewBox={`0 0 ${RONG} ${CAO}`}
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      {O_LOGO.map((o) => (
        <rect key={`${o.x}-${o.y}`} x={o.x} y={o.y} width={1} height={1} fill={o.mau} />
      ))}
    </svg>
  )
}

export function LogoTK({ co = 28 }: { co?: number }) {
  return (
    <>
      <LogoThuong co={co} />
      <LogoPixel co={co} />
    </>
  )
}

// Tên thương hiệu: thường "TAKI Logistics"; Pixel "TAKI" in hoa kèm chữ nhỏ "LOGISTICS"
export function TenThuongHieu() {
  return (
    <>
      <span className="ten-thuong">TAKI Logistics</span>
      <span className="ten-pixel">
        TAKI<small>LOGISTICS</small>
      </span>
    </>
  )
}
