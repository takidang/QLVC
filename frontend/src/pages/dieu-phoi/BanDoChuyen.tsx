import 'leaflet/dist/leaflet.css'
import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet'
import type { LatLngBoundsExpression, LatLngTuple } from 'leaflet'
import type { DiemDung } from '../../api/chuyen'

// Khóa vùng trong đất liền Việt Nam (kien-truc.md): kinh độ ≤ 109,6°, phóng nhỏ nhất 7
const VUNG: LatLngBoundsExpression = [
  [8.3, 102.1],
  [23.4, 109.6],
]

type Tram = { nut: string; vt: LatLngTuple; diem: DiemDung[] }

// Gộp các điểm liền nhau cùng một nút thành một trạm (lịch trình đã xếp theo ETA)
function tram(ds: DiemDung[]): Tram[] {
  const ra: Tram[] = []
  for (const p of ds) {
    if (p.lat == null || p.lng == null) continue
    const cuoi = ra[ra.length - 1]
    if (cuoi?.nut === p.nut) cuoi.diem.push(p)
    else ra.push({ nut: p.nut, vt: [Number(p.lat), Number(p.lng)], diem: [p] })
  }
  return ra
}

const xong = (t: Tram) => t.diem.every((p) => p.ket_qua)

// Bản đồ chi tiết chuyến: trạm đã xong tô đặc, chưa tới để rỗng; đường nối thẳng giữa các trạm theo thứ tự
// (không phải đường đi thật – vẽ đường thật cần dịch vụ chỉ đường)
export default function BanDoChuyen({
  lichTrinh,
  viTri,
}: {
  lichTrinh: DiemDung[]
  // Vị trí GPS của lượt quét gần nhất (không theo dõi liên tục); chỉ truyền khi chuyến đang chạy
  viTri?: { lat: string; lng: string; luc: string; nut: string } | null
}) {
  const ds = tram(lichTrinh)
  if (!ds.length) return null
  const vt = ds.map((t) => t.vt)
  // số trạm đã đi qua liên tiếp từ đầu (tô đường đặc tới đó, phần còn lại nét đứt)
  const chuaXong = ds.findIndex((t) => !xong(t))
  const daDi = chuaXong < 0 ? ds.length : chuaXong
  return (
    <MapContainer
      className="ban-do"
      bounds={vt.length > 1 ? vt : undefined}
      center={vt.length > 1 ? undefined : vt[0]}
      zoom={vt.length > 1 ? undefined : 11}
      boundsOptions={{ padding: [32, 32] }}
      maxBounds={VUNG}
      maxBoundsViscosity={1}
      minZoom={7}
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {daDi > 1 && (
        <Polyline positions={vt.slice(0, daDi)} pathOptions={{ color: '#1d4ed8', weight: 4 }} />
      )}
      <Polyline
        positions={vt.slice(Math.max(daDi - 1, 0))}
        pathOptions={{ color: '#64748b', weight: 3, dashArray: '6 8' }}
      />
      {ds.map((t, i) => (
        <CircleMarker
          key={`${t.nut}-${i}`}
          center={t.vt}
          radius={9}
          pathOptions={{
            color: '#1d4ed8',
            weight: 3,
            fillColor: xong(t) ? '#1d4ed8' : '#fff',
            fillOpacity: 1,
          }}
        >
          <Tooltip direction="top" offset={[0, -8]} permanent={i === 0 || i === ds.length - 1}>
            {i + 1}. {t.nut} ·{' '}
            {t.diem.map((p) => `${p.viec === 'LAY' ? 'Lấy' : 'Giao'} ${p.ma_don}`).join(', ')}
          </Tooltip>
        </CircleMarker>
      ))}
      {viTri && (
        <CircleMarker
          center={[Number(viTri.lat), Number(viTri.lng)]}
          radius={9}
          pathOptions={{ className: 'bd-xe' }}
        >
          <Tooltip direction="top" offset={[0, -8]}>
            Xe · quét lúc{' '}
            {new Date(viTri.luc).toLocaleTimeString('vi-VN', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Tooltip>
        </CircleMarker>
      )}
    </MapContainer>
  )
}
