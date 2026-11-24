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

// Bản Pixel: lưới ô vuông, không viền chữ, đặt trên ô trắng bo góc kiểu pixel
const LUOI_TK = [
  'DDDDDDDDD..KKK',
  'DDDDDDDDD.KKK.',
  'DDDDDDDDDKKK..',
  '...BBB..KKK...',
  '...BBB.KKK....',
  '...BBBKKK.....',
  '...BBBKKK.....',
  '...BBB.KKK....',
  '...BBB..KKK...',
  '...BBB...KKK..',
  '...BBB....KKK.',
  '...BBB.....KKK',
] as const
// Cùng màu với bản thường (thanh than, thân xanh, K đỏ); chỉ khác kiểu vẽ ô vuông
const MAU_O: Record<string, string> = { D: '#3a3e45', B: '#2387bd', K: '#e2473b' }
// Ô nền trắng bo góc kiểu pixel (cắt bậc thang 2 nấc ở 4 góc), chữ không viền
const LE = 2
const RONG = LUOI_TK[0].length + LE * 2
const CAO = LUOI_TK.length + LE * 2
const GOC_CAT = new Set(['0,0', '1,0', '0,1'])
const catGoc = (x: number, y: number) => {
  const gx = x < RONG / 2 ? x : RONG - 1 - x
  const gy = y < CAO / 2 ? y : CAO - 1 - y
  return GOC_CAT.has(`${gx},${gy}`)
}
const O_NEN: { x: number; y: number }[] = []
for (let y = 0; y < CAO; y++) for (let x = 0; x < RONG; x++) if (!catGoc(x, y)) O_NEN.push({ x, y })
const O_LOGO: { x: number; y: number; mau: string }[] = LUOI_TK.flatMap((hang, y) =>
  [...hang].flatMap((c, x) => (c === '.' ? [] : [{ x: x + LE, y: y + LE, mau: MAU_O[c] }])),
)

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
      {O_NEN.map((o) => (
        <rect key={`n-${o.x}-${o.y}`} x={o.x} y={o.y} width={1} height={1} fill="#fff" />
      ))}
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
