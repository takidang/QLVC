import { useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  chiTietChuyen,
  chotChuyen,
  donPhuHop,
  ghepDon,
  goDon,
  moChotChuyen,
  type ChuyenChiTiet as Chuyen,
  type ViPhamGhep,
  type XacNhanChot,
} from '../../api/chuyen'
import type { Don } from '../../api/don'
import { kemMaBr, LoiApi } from '../../api/goi'

const dong = (n: number) => n.toLocaleString('vi-VN')
const so = (s: string) => Number(s).toLocaleString('vi-VN')
const gio = (iso: string) =>
  new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
const TEN_TRANG_THAI: Record<string, string> = {
  LAP: 'Đang lập',
  DA_CHOT: 'Đã chốt',
  DANG_CHAY: 'Đang chạy',
  HOAN_THANH: 'Hoàn thành',
  DA_QUYET_TOAN: 'Đã quyết toán',
  HUY: 'Hủy',
}
const XAC_NHAN: Record<string, keyof XacNhanChot> = {
  'BR-23': 'xac_nhan_chay_rong',
  'BR-52': 'xac_nhan_lai_am',
}

// Chi tiết chuyến, thẻ Hàng (UC-13): tải, lịch trình, ghép và gỡ đơn; chốt / mở chốt (UC-15)
export default function ChuyenChiTiet() {
  const id = Number(useParams().id)
  const [c, setC] = useState<Chuyen | null>(null)
  const [phuHop, setPhuHop] = useState<Don[]>([])
  const [chonGhep, setChonGhep] = useState<number[]>([])
  const [chonGo, setChonGo] = useState<number[]>([])
  const [loi, setLoi] = useState('')
  const [viPham, setViPham] = useState<ViPhamGhep[]>([])
  const [dangGui, setDangGui] = useState(false)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false
    chiTietChuyen(id)
      .then((r) => {
        if (bo) return
        setC(r)
        if (r.trang_thai === 'LAP') donPhuHop(id).then((d) => !bo && setPhuHop(d))
      })
      .catch((e) => !bo && setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến'))
    return () => {
      bo = true
    }
  }, [id, lanTai])

  // Chốt: thiếu xác nhận chạy rỗng (BR-23) hoặc lãi âm (BR-52) thì hỏi, đồng ý thì gửi lại kèm cờ
  async function chot(): Promise<Chuyen> {
    const xn: XacNhanChot = {}
    for (;;) {
      try {
        return await chotChuyen(id, xn)
      } catch (e) {
        const co = e instanceof LoiApi && e.status === 422 && XAC_NHAN[e.ma]
        if (!co || !window.confirm(`${e instanceof Error ? e.message : ''}. Vẫn chốt chuyến?`))
          throw e
        xn[co] = true
      }
    }
  }

  async function lam(viec: 'ghep' | 'go' | 'chot' | 'mo-chot') {
    setLoi('')
    setViPham([])
    setDangGui(true)
    try {
      const goi = {
        ghep: () => ghepDon(id, chonGhep),
        go: () => goDon(id, chonGo),
        chot,
        'mo-chot': () => moChotChuyen(id),
      }
      const moi = await goi[viec]()
      setC(moi)
      setChonGhep([])
      setChonGo([])
      setPhuHop(moi.trang_thai === 'LAP' ? await donPhuHop(id) : [])
    } catch (e) {
      // Người dùng bấm Hủy ở hộp xác nhận: không báo lỗi
      if (e instanceof LoiApi && e.status === 422 && XAC_NHAN[e.ma]) return
      if (e instanceof LoiApi && e.status === 422 && e.chiTiet.length) {
        setLoi(e.message)
        setViPham(e.chiTiet as ViPhamGhep[])
      } else {
        setLoi(e instanceof LoiApi ? e.message : 'Không lưu được, vui lòng thử lại')
        // 409: đơn vừa bị người khác ghép, hoặc chuyến đã đổi trạng thái → tải lại
        if (e instanceof LoiApi && e.status === 409) {
          setChonGhep([])
          setChonGo([])
          setLanTai((n) => n + 1)
        }
      }
    } finally {
      setDangGui(false)
    }
  }

  if (!c)
    return (
      <section className="noi-dung">
        <Link to="..">← Danh sách chuyến</Link>
        {loi ? (
          <p role="alert" className="loi">
            {loi}
          </p>
        ) : (
          <p className="ghi-chu">Đang tải…</p>
        )}
      </section>
    )

  const dangLap = c.trang_thai === 'LAP'
  const maDon = new Map([...c.don, ...phuHop].map((d) => [d.id, d.ma_don]))
  const doi = (ds: number[], dat: (v: number[]) => void, x: number) =>
    dat(ds.includes(x) ? ds.filter((y) => y !== x) : [...ds, x])

  return (
    <section className="noi-dung">
      <Link to="..">← Danh sách chuyến</Link>
      <div className="thanh-cong-cu">
        <h1>Chuyến {c.ma_chuyen}</h1>
        <span className="nhan">{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</span>
        {dangLap && (
          <button disabled={dangGui} onClick={() => lam('chot')}>
            Chốt chuyến
          </button>
        )}
        {c.trang_thai === 'DA_CHOT' && (
          <button className="phu" disabled={dangGui} onClick={() => lam('mo-chot')}>
            Mở chốt
          </button>
        )}
      </div>
      <p>
        {c.ma_tuyen} – {c.ten_tuyen} · Xe <strong>{c.bien_so}</strong> · Tài xế {c.ten_tai_xe} ·
        Khởi hành {lucVN(c.khoi_hanh_du_kien)} · Kết thúc dự kiến {lucVN(c.ket_thuc_du_kien)}
      </p>

      <div className="hai-cot">
        <label>
          Tải: {so(c.tai_trong.da_dung_kg)} / {dong(c.tai_trong.toi_da_kg)} kg
          <meter min={0} max={c.tai_trong.toi_da_kg} value={Number(c.tai_trong.da_dung_kg)} />
        </label>
        <label>
          Thể tích: {so(c.the_tich.da_dung_m3)} / {so(c.the_tich.toi_da_m3)} m³
          <meter min={0} max={Number(c.the_tich.toi_da_m3)} value={Number(c.the_tich.da_dung_m3)} />
        </label>
      </div>
      <p>
        Lấp đầy <strong>{Math.round(Number(c.ty_le_lap_day) * 100)}%</strong> · Lãi dự kiến{' '}
        <strong className={c.canh_bao_lai_am ? 'het-han' : undefined}>
          {dong(c.lai_du_kien)} đ
          {dangLap && c.canh_bao_lai_am && ' (lãi âm – sẽ phải xác nhận khi chốt)'}
        </strong>
        {c.chay_rong && ' · Chạy rỗng (đã xác nhận)'}
      </p>

      {loi && (
        <div role="alert" className="canh-bao">
          <strong className="loi">{loi}</strong>
          {viPham.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Đơn</th>
                  <th>Quy tắc</th>
                  <th>Nội dung</th>
                </tr>
              </thead>
              <tbody>
                {viPham.map((v, i) => (
                  <tr key={i}>
                    <td className="bien-so">
                      {v.don_id ? (maDon.get(v.don_id) ?? v.don_id) : 'Cả chuyến'}
                    </td>
                    <td>{v.ma}</td>
                    <td>{kemMaBr(v.thong_diep, v.ma)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <h2>Lịch trình</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Điểm</th>
            <th>Việc</th>
            <th>Đơn</th>
            <th>ETA</th>
          </tr>
        </thead>
        <tbody>
          {c.lich_trinh.map((d) => (
            <tr key={d.thu_tu}>
              <td>{d.thu_tu}</td>
              <td>{d.nut}</td>
              <td>{d.viec === 'LAY' ? 'Lấy' : 'Giao'}</td>
              <td className="bien-so">{d.ma_don}</td>
              <td>{gio(d.eta)}</td>
            </tr>
          ))}
          {c.lich_trinh.length === 0 && (
            <tr>
              <td colSpan={5} className="trong">
                Chưa có đơn – chuyến đang tính như chạy rỗng
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <BangDon
        tieu_de={`Đơn đang ghép (${c.don.length})`}
        ds={c.don}
        chon={dangLap ? chonGo : undefined}
        onChon={(x) => doi(chonGo, setChonGo, x)}
        nut={
          dangLap && (
            <button
              className="phu"
              disabled={dangGui || chonGo.length === 0}
              onClick={() => lam('go')}
            >
              Gỡ {chonGo.length || ''} đơn đã chọn
            </button>
          )
        }
      />
      {dangLap && (
        <BangDon
          tieu_de={`Đơn chờ ghép phù hợp tuyến (${phuHop.length})`}
          ds={phuHop}
          chon={chonGhep}
          onChon={(x) => doi(chonGhep, setChonGhep, x)}
          nut={
            <button disabled={dangGui || chonGhep.length === 0} onClick={() => lam('ghep')}>
              {dangGui ? 'Đang kiểm…' : `Ghép ${chonGhep.length || ''} đơn đã chọn`}
            </button>
          }
        />
      )}
    </section>
  )
}

function BangDon({
  tieu_de,
  ds,
  chon,
  onChon,
  nut,
}: {
  tieu_de: string
  ds: Don[]
  chon?: number[]
  onChon: (id: number) => void
  nut: ReactNode
}) {
  return (
    <>
      <div className="thanh-cong-cu">
        <h2>{tieu_de}</h2>
        {nut}
      </div>
      <table>
        <thead>
          <tr>
            {chon && <th />}
            <th>Mã đơn</th>
            <th>Khách</th>
            <th>Lấy → giao</th>
            <th className="so">Hàng</th>
            <th>Khung lấy</th>
            <th>Hạn giao</th>
            <th className="so">Cước (đ)</th>
          </tr>
        </thead>
        <tbody>
          {ds.map((d) => (
            <tr key={d.id}>
              {chon && (
                <td>
                  <input
                    type="checkbox"
                    aria-label={`Chọn ${d.ma_don}`}
                    checked={chon.includes(d.id)}
                    onChange={() => onChon(d.id)}
                  />
                </td>
              )}
              <td className="bien-so">{d.ma_don}</td>
              <td>{d.ten_khach}</td>
              <td>
                {d.tinh_lay} → {d.tinh_giao}
              </td>
              <td className="so">
                {so(d.kg)} kg, {so(d.m3)} m³
              </td>
              <td>{d.lay_tu && d.lay_den ? `${gio(d.lay_tu)}–${gio(d.lay_den)}` : 'Cả ngày'}</td>
              <td>{lucVN(d.han_giao)}</td>
              <td className="so">{dong(d.cuoc_tinh)}</td>
            </tr>
          ))}
          {ds.length === 0 && (
            <tr>
              <td colSpan={chon ? 8 : 7} className="trong">
                Không có đơn
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </>
  )
}
