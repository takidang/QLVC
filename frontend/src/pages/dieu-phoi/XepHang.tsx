import { useEffect, useRef, useState } from 'react'
import type { ChuyenChiTiet } from '../../api/chuyen'
import { TEN_TRANG_THAI_DON, type Don } from '../../api/don'
import { BuiThaHangPixel } from '../../HieuUngPixel'
import { dangHieuUngPixel } from '../../nen'

const so = (n: number) => n.toLocaleString('vi-VN', { maximumFractionDigits: 1 })
const ngayGio = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })

// Khung thùng xe trong hình (đơn vị SVG); các khối đơn nằm trong đoạn [X0, X1]
const X0 = 30
const X1 = 446
const Y0 = 34
const Y1 = 150
// Gân tôn dọc của container (Pixel), cách nhau 12 px
const GAN_CONTAINER = Array.from({ length: Math.floor((X1 - X0) / 12) }, (_, i) => X0 + 4 + i * 12)

// "Xếp hàng lên xe": hình xe tải minh họa, thùng lấp theo THỂ TÍCH các đơn đã ghép (mỗi khối một đơn,
// rộng theo phần trăm m³, không phải vị trí thật trong thùng) + hai thanh tải trọng / thể tích.
// Chuyến đang lập: thẻ đơn chờ ghép, rê chuột xem trước phần chiếm thêm, bấm Ghép; bấm khối để gỡ.
// Ghép / gỡ vẫn gọi API cũ (máy chủ kiểm BR-01…10, 67 và trả lỗi kèm mã BR).
export default function XepHang({
  c,
  phuHop,
  dangLap,
  dangGui,
  onGhep,
  onGo,
}: {
  c: ChuyenChiTiet
  phuHop: Don[]
  dangLap: boolean
  dangGui: boolean
  onGhep: (id: number) => void
  onGo: (id: number) => void
}) {
  const [thu, setThu] = useState<Don | null>(null) // đơn đang rê chuột (xem trước)
  const [chon, setChon] = useState<number | null>(null) // khối đơn đang chọn để gỡ
  // Hiệu ứng Pixel: cờ khối hàng vừa ghép rơi xuống thùng và rung khung khi máy chủ báo quá tải
  const [vuaRoi, setVuaRoi] = useState<number[]>([])
  const [rungQuaTai, setRungQuaTai] = useState(false)

  // Đơn còn trên xe (đơn đã giao / thất bại vẫn hiện khi chuyến đã chạy, để thấy chuyến đã chở gì)
  const ds = c.don.filter((d) => d.trang_thai !== 'HUY')
  const maDs = ds.map((d) => d.id).join(',')
  const chuyenTruoc = useRef(c.id)
  const donTruoc = useRef<Set<number>>(new Set(ds.map((d) => d.id)))
  const choGhep = useRef<number | null>(null)
  const dangGuiTruoc = useRef(dangGui)

  useEffect(() => {
    const hienTai = maDs ? maDs.split(',').map(Number) : []
    if (chuyenTruoc.current !== c.id) {
      chuyenTruoc.current = c.id
      donTruoc.current = new Set(hienTai)
      choGhep.current = null
      setVuaRoi([])
      setRungQuaTai(false)
      return
    }
    const moi = hienTai.filter((id) => !donTruoc.current.has(id))
    donTruoc.current = new Set(hienTai)
    if (moi.length > 0 && dangHieuUngPixel()) setVuaRoi(moi)
  }, [c.id, maDs])

  useEffect(() => {
    if (vuaRoi.length === 0) return
    const t = window.setTimeout(() => setVuaRoi([]), 380)
    return () => window.clearTimeout(t)
  }, [vuaRoi])

  useEffect(() => {
    const vuaXong = dangGuiTruoc.current && !dangGui
    dangGuiTruoc.current = dangGui
    if (!vuaXong || choGhep.current === null) return
    const idGhep = choGhep.current
    choGhep.current = null
    const daCo = maDs ? maDs.split(',').map(Number).includes(idGhep) : false
    if (daCo || !dangHieuUngPixel()) return
    const tbLoi = document.querySelector('[role="alert"].canh-bao')?.textContent ?? ''
    if (/BR-0[12]|quá tải|vượt|tải trọng|thể tích|sức chứa/i.test(tbLoi)) {
      setRungQuaTai(true)
    }
  }, [dangGui, maDs])

  useEffect(() => {
    if (!rungQuaTai) return
    const t = window.setTimeout(() => setRungQuaTai(false), 320)
    return () => window.clearTimeout(t)
  }, [rungQuaTai])
  const m3Max = Number(c.the_tich.toi_da_m3) || 1
  const kgMax = c.tai_trong.toi_da_kg || 1
  const m3 = Number(c.the_tich.da_dung_m3)
  const kg = Number(c.tai_trong.da_dung_kg)
  const m3Thu = thu ? Number(thu.m3) : 0
  const kgThu = thu ? Number(thu.kg) : 0
  const quaTai = m3 + m3Thu > m3Max || kg + kgThu > kgMax

  // Vị trí từng khối theo thể tích cộng dồn; x là mép phải sau khối cuối
  const rongKhoi = (d: Don) => (Number(d.m3) / m3Max) * (X1 - X0)
  const khoi = ds.map((d, i) => ({
    d,
    x: X0 + ds.slice(0, i).reduce((t, e) => t + rongKhoi(e), 0),
    w: rongKhoi(d),
  }))
  const x = X0 + ds.reduce((t, e) => t + rongKhoi(e), 0)
  const wThu = (m3Thu / m3Max) * (X1 - X0)
  const dangChon = ds.find((d) => d.id === chon)

  return (
    <section className="kinh xh xh-hai-cot">
      <div className={rungQuaTai && dangHieuUngPixel() ? 'xh-xe px-xh-rung' : 'xh-xe'}>
        <h2>
          Xếp hàng lên xe <span className="bien">{c.bien_so}</span>
        </h2>
        <svg
          viewBox="0 0 600 214"
          preserveAspectRatio="xMinYMid meet"
          role="img"
          aria-label={`Xe ${c.bien_so} đã dùng ${so(m3)} / ${so(m3Max)} m³ và ${so(kg)} / ${so(kgMax)} kg, ${ds.length} đơn`}
        >
          {/* Thùng xe */}
          <rect
            x={X0 - 10}
            y={Y0 - 12}
            width={X1 - X0 + 20}
            height={Y1 - Y0 + 24}
            rx={8}
            className="xh-thung"
          />
          {/* Pixel: trang trí thùng kiểu container (vách tôn gân, ray, góc khóa, cửa sau); ẩn ở giao diện thường */}
          <g className="xh-container" aria-hidden="true">
            {GAN_CONTAINER.map((x) => (
              <rect key={x} x={x} y={Y0 - 4} width={4} height={Y1 - Y0 + 8} className="xh-gan" />
            ))}
            <rect x={X0 - 10} y={Y0 - 12} width={X1 - X0 + 20} height={7} className="xh-ray" />
            <rect x={X0 - 10} y={Y1 + 5} width={X1 - X0 + 20} height={7} className="xh-ray" />
            {[
              [X0 - 10, Y0 - 12],
              [X1, Y0 - 12],
              [X0 - 10, Y1 + 2],
              [X1, Y1 + 2],
            ].map(([x, y]) => (
              <g key={`${x}-${y}`}>
                <rect x={x} y={y} width={10} height={10} className="xh-goc" />
                <rect x={x + 3} y={y + 3} width={4} height={4} className="xh-goc-lo" />
              </g>
            ))}
            {[X1 + 2, X1 + 6].map((x) => (
              <rect key={x} x={x} y={Y0} width={2} height={Y1 - Y0} className="xh-chot" />
            ))}
          </g>
          {/* Vạch chia 25 % cho dễ ước lượng */}
          {[0.25, 0.5, 0.75].map((t) => (
            <line
              key={t}
              x1={X0 + t * (X1 - X0)}
              x2={X0 + t * (X1 - X0)}
              y1={Y0}
              y2={Y1}
              className="xh-vach"
            />
          ))}
          {khoi.map(({ d, x: kx, w }, i) => {
            const dangRoi = vuaRoi.includes(d.id) && dangHieuUngPixel()
            return (
              <g
                key={d.id}
                className={`${chon === d.id ? 'xh-khoi chon' : 'xh-khoi'}${dangRoi ? ' px-khoi-roi' : ''}`}
                tabIndex={dangLap ? 0 : -1}
                role={dangLap ? 'button' : undefined}
                aria-label={`${d.ma_don}: ${so(Number(d.m3))} m³, ${so(Number(d.kg))} kg${dangLap ? ', bấm để chọn gỡ' : ''}`}
                onClick={() => dangLap && setChon(chon === d.id ? null : d.id)}
                onKeyDown={(e) => {
                  if (dangLap && (e.key === 'Enter' || e.key === ' ')) {
                    e.preventDefault()
                    setChon(chon === d.id ? null : d.id)
                  }
                }}
              >
                <rect
                  x={kx + 1}
                  y={Y0}
                  width={Math.max(w - 2, 2)}
                  height={Y1 - Y0}
                  rx={4}
                  className={`xh-o o${i % 3}`}
                />
                {w > 54 && (
                  <>
                    <text
                      x={kx + w / 2}
                      y={(Y0 + Y1) / 2 - 4}
                      textAnchor="middle"
                      className="xh-chu"
                    >
                      {d.ma_don.replace('DH-', '')}
                    </text>
                    <text
                      x={kx + w / 2}
                      y={(Y0 + Y1) / 2 + 14}
                      textAnchor="middle"
                      className="xh-chu nho"
                    >
                      {so(Number(d.m3))} m³
                    </text>
                  </>
                )}
              </g>
            )
          })}
          {/* Hiệu ứng Pixel: hạt bụi ô vuông khi khối hàng vừa rơi xuống sàn thùng xe */}
          {dangHieuUngPixel() &&
            khoi
              .filter(({ d }) => vuaRoi.includes(d.id))
              .map(({ d, x: kx, w }) => (
                <BuiThaHangPixel key={`bui-${d.id}`} x={kx} w={w} y={Y1} />
              ))}
          {/* Xem trước đơn đang rê chuột: khối nét đứt, cam nếu vượt sức chứa */}
          {thu && wThu > 0 && (
            <rect
              x={x + 1}
              y={Y0}
              width={Math.max(Math.min(wThu, X1 + 40 - x) - 2, 2)}
              height={Y1 - Y0}
              rx={4}
              className={quaTai ? 'xh-thu qua' : 'xh-thu'}
            />
          )}
          {ds.length === 0 && !thu && (
            <text x={(X0 + X1) / 2} y={(Y0 + Y1) / 2 + 5} textAnchor="middle" className="xh-trong">
              Thùng trống – chưa ghép đơn
            </text>
          )}
          {/* Đầu xe */}
          <path d="M466 70 h60 q14 0 22 12 l26 40 q6 10 6 22 v26 h-114 z" className="xh-dau" />
          <path d="M488 84 h34 q8 0 13 8 l18 28 h-65 z" className="xh-kinh" />
          {/* Gầm và bánh */}
          <line x1={14} x2={584} y1={174} y2={174} className="xh-gam" />
          {[96, 156, 522].map((cx) => (
            <g key={cx}>
              <circle cx={cx} cy={184} r={20} className="xh-banh" />
              <circle cx={cx} cy={184} r={7} className="xh-mam" />
            </g>
          ))}
        </svg>

        <div className="xh-thanh">
          <Thanh nhan="Thể tích" dung={m3} them={m3Thu} max={m3Max} donVi="m³" />
          <Thanh nhan="Tải trọng" dung={kg} them={kgThu} max={kgMax} donVi="kg" />
        </div>
        {thu && quaTai && (
          <p className="xh-bao">
            Ghép {thu.ma_don} sẽ vượt sức chứa của xe; máy chủ sẽ chặn (BR-01, BR-02).
          </p>
        )}
        {dangLap && dangChon && (
          <div className="xh-chon">
            <span>
              <strong>{dangChon.ma_don}</strong> · {dangChon.tinh_lay} → {dangChon.tinh_giao} ·{' '}
              {so(Number(dangChon.kg))} kg · {so(Number(dangChon.m3))} m³
            </span>
            <button
              className="phu"
              disabled={dangGui}
              onClick={() => {
                onGo(dangChon.id)
                setChon(null)
              }}
            >
              Gỡ khỏi xe
            </button>
          </div>
        )}
        <p className="ghi-chu">
          Mỗi khối là phần thể tích một đơn chiếm, không phải vị trí thật trong thùng.
          {dangLap && ' Bấm vào khối để gỡ đơn.'}
        </p>
      </div>

      {/* Chuyến đã chốt / đang chạy / đã xong: nửa phải là các đơn đang ở trên xe */}
      {!dangLap && (
        <div className="xh-cho">
          <h2>
            Đơn trên xe <em>{ds.length}</em>
          </h2>
          <ul>
            {ds.map((d) => (
              <li key={d.id}>
                <div>
                  <strong>{d.ma_don}</strong>
                  <span>
                    {d.tinh_lay} → {d.tinh_giao}
                  </span>
                  <small>
                    {so(Number(d.kg))} kg · {so(Number(d.m3))} m³ · {d.so_kien} kiện
                  </small>
                </div>
                <span className="nhan">{TEN_TRANG_THAI_DON[d.trang_thai] ?? d.trang_thai}</span>
              </li>
            ))}
            {ds.length === 0 && <li className="ghi-chu">Chuyến chạy rỗng</li>}
          </ul>
        </div>
      )}
      {dangLap && (
        <div className="xh-cho">
          <h2>
            Đơn chờ ghép phù hợp tuyến <em>{phuHop.length}</em>
          </h2>
          <ul>
            {phuHop.map((d) => (
              <li
                key={d.id}
                onMouseEnter={() => setThu(d)}
                onMouseLeave={() => setThu(null)}
                onFocus={() => setThu(d)}
                onBlur={() => setThu(null)}
              >
                <div>
                  <strong>{d.ma_don}</strong>
                  <span>
                    {d.tinh_lay} → {d.tinh_giao}
                  </span>
                  <small>
                    {so(Number(d.kg))} kg · {so(Number(d.m3))} m³ · {d.so_kien} kiện · hạn{' '}
                    {ngayGio(d.han_giao)}
                  </small>
                </div>
                <button
                  disabled={dangGui}
                  onClick={() => {
                    // Hiệu ứng Pixel: ghi nhận đơn vừa bấm ghép để bắt phản hồi từ máy chủ
                    choGhep.current = d.id
                    onGhep(d.id)
                  }}
                >
                  Ghép vào xe
                </button>
              </li>
            ))}
            {phuHop.length === 0 && (
              <li className="ghi-chu">Không có đơn chờ ghép hợp tuyến này</li>
            )}
          </ul>
        </div>
      )}
    </section>
  )
}

// Thanh sức chứa: phần đã dùng đặc, phần xem trước sọc; vượt 100 % đổi cam
function Thanh({
  nhan,
  dung,
  them,
  max,
  donVi,
}: {
  nhan: string
  dung: number
  them: number
  max: number
  donVi: string
}) {
  const pt = (v: number) => `${Math.min((v / max) * 100, 100)}%`
  const qua = dung + them > max
  return (
    <div className={qua ? 'xh-hang qua' : 'xh-hang'}>
      <span>{nhan}</span>
      <span className="xh-ray">
        <i style={{ width: pt(dung) }} />
        {them > 0 && (
          <i
            className="thu"
            style={{ left: pt(dung), width: pt(Math.max(Math.min(them, max - dung), 0)) }}
          />
        )}
      </span>
      <span className="so">
        {so(dung + them)} / {so(max)} {donVi}
      </span>
    </div>
  )
}
