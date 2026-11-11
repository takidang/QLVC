import 'leaflet/dist/leaflet.css'
import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet'
import type { LatLngBoundsExpression, LatLngTuple } from 'leaflet'
import type { Chuyen } from '../../api/chuyen'
import { danhSachNut, danhSachTuyen } from '../../api/tuyen'

// Khóa vùng trong đất liền Việt Nam (kien-truc.md): kinh độ ≤ 109,6°, phóng nhỏ nhất 7
const VUNG: LatLngBoundsExpression = [
  [8.3, 102.1],
  [23.4, 109.6],
]
// Tuyến có nhiều chuyến thì tô theo chuyến "nóng" nhất; vẽ tuyến nóng sau cùng để nằm trên
const UU_TIEN = ['HUY', 'HOAN_THANH', 'DA_QUYET_TOAN', 'LAP', 'DA_CHOT', 'DANG_CHAY']
const LOP: Record<string, string> = {
  LAP: 'lap',
  DA_CHOT: 'chot',
  DANG_CHAY: 'chay',
  HOAN_THANH: 'xong',
  DA_QUYET_TOAN: 'xong',
  HUY: 'huy',
}
type Duong = { id: number; nut: { ten: string; vt: LatLngTuple }[] }

// Bản đồ tuyến trong ngày: mỗi tuyến có chuyến là một đường nối thẳng các nút (không phải đường đi thật),
// màu theo trạng thái. Không có vị trí xe: hệ thống chỉ có GPS lúc quét mã, API danh sách chưa trả.
export default function BanDoNgay({ ds, ten }: { ds: Chuyen[]; ten: Record<string, string> }) {
  const [duong, setDuong] = useState<Duong[]>()
  useEffect(() => {
    // shortcut: tối đa 100 tuyến, 100 nút, đủ cho nhà xe nhỏ
    Promise.all([danhSachTuyen({ so_dong: 100 }), danhSachNut({ so_dong: 100 })])
      .then(([t, n]) => {
        const vt = new Map(
          n.du_lieu
            .filter((x) => x.lat != null && x.lng != null)
            .map((x) => [x.id, [Number(x.lat), Number(x.lng)] as LatLngTuple]),
        )
        setDuong(
          t.du_lieu.map((x) => ({
            id: x.id,
            nut: [...x.nut]
              .sort((a, b) => a.thu_tu - b.thu_tu)
              .filter((k) => vt.has(k.nut_id))
              .map((k) => ({ ten: k.ten, vt: vt.get(k.nut_id)! })),
          })),
        )
      })
      .catch(() => setDuong([]))
  }, [])

  const ve = (duong ?? [])
    .map((d) => {
      const chuyen = ds.filter((c) => c.tuyen_id === d.id)
      const nong = [...chuyen].sort(
        (a, b) => UU_TIEN.indexOf(b.trang_thai) - UU_TIEN.indexOf(a.trang_thai),
      )[0]
      return { ...d, chuyen, nong }
    })
    .filter((d) => d.nong && d.nut.length > 1)
    .sort((a, b) => UU_TIEN.indexOf(a.nong.trang_thai) - UU_TIEN.indexOf(b.nong.trang_thai))
  const nut = new Map(ve.flatMap((d) => d.nut).map((n) => [n.ten, n.vt]))

  return (
    <section className="kinh ban-do-ngay">
      <h2>Tuyến trong ngày</h2>
      {ve.length === 0 ? (
        <p className="ghi-chu">
          {duong ? 'Chưa có tuyến nào có tọa độ để vẽ.' : 'Đang tải bản đồ…'}
        </p>
      ) : (
        <MapContainer
          key={ve.map((d) => d.id).join()}
          className="ban-do"
          bounds={[...nut.values()]}
          boundsOptions={{ padding: [24, 24] }}
          maxBounds={VUNG}
          maxBoundsViscosity={1}
          minZoom={7}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {ve.map((d) => (
            <Polyline
              key={d.id}
              positions={d.nut.map((n) => n.vt)}
              pathOptions={{
                className: `bd-tuyen ${d.chuyen.some((c) => c.trang_thai === 'DANG_CHAY' && c.theo_doi?.co.includes('TRE')) ? 'tre' : LOP[d.nong.trang_thai]}`,
              }}
            >
              <Tooltip sticky>
                {d.chuyen
                  .map((c) => `${c.ma_chuyen} ${ten[c.trang_thai] ?? c.trang_thai}`)
                  .join(' · ')}
              </Tooltip>
            </Polyline>
          ))}
          {[...nut].map(([t, vt]) => (
            <CircleMarker key={t} center={vt} radius={5} pathOptions={{ className: 'bd-nut' }}>
              <Tooltip direction="top" offset={[0, -6]}>
                {t}
              </Tooltip>
            </CircleMarker>
          ))}
        </MapContainer>
      )}
      <p className="ghi-chu">
        Đường nối thẳng các nút của tuyến, màu theo trạng thái chuyến. Chưa có vị trí xe.
      </p>
    </section>
  )
}
