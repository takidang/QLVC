import { useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  chiTietChuyen,
  donPhuHop,
  ghepDon,
  goDon,
  type ChuyenChiTiet as Chuyen,
  type ViPhamGhep,
} from '../../api/chuyen'
import { phanCong, taiXeKhaDungChuyen, xeKhaDungChuyen } from '../../api/chuyen'
import type { TaiXeKhaDung, XeKhaDung } from '../../api/chuyen'
import { ChonKhaDung, type KhaDung } from './ChuyenDanhSach'
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

// Chi tiết chuyến, thẻ Hàng (UC-13): tải, lịch trình, ghép và gỡ đơn
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
        if (r.trang_thai === 'LAP')
          donPhuHop(id)
            .then((d) => !bo && setPhuHop(d))
            .catch(() => !bo && setLoi('Không tải được danh sách đơn chờ ghép'))
      })
      .catch((e) => !bo && setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến'))
    return () => {
      bo = true
    }
  }, [id, lanTai])

  async function lam(viec: 'ghep' | 'go') {
    setLoi('')
    setViPham([])
    setDangGui(true)
    try {
      setC(await (viec === 'ghep' ? ghepDon(id, chonGhep) : goDon(id, chonGo)))
      setChonGhep([])
      setChonGo([])
      setLanTai((n) => n + 1) // tải lại đơn chờ ghép ở effect; lỗi tải lại không bị báo nhầm là lưu hỏng
    } catch (e) {
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
          {dong(c.lai_du_kien)} đ{c.canh_bao_lai_am && ' (lãi âm – sẽ phải xác nhận khi chốt)'}
        </strong>
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

      {dangLap && (
        <DoiXeTaiXe
          c={c}
          onLuu={(r) => {
            setC(r)
            setLanTai((n) => n + 1)
          }}
        />
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

// UC-12: đổi xe và/hoặc tài xế khi chuyến LAP; cái bị loại hiện kèm lý do (BR-11…19, tải theo đơn đang ghép)
function DoiXeTaiXe({ c, onLuu }: { c: Chuyen; onLuu: (c: Chuyen) => void }) {
  const [mo, setMo] = useState(false)
  const [xeId, setXeId] = useState(String(c.xe_id))
  const [taiXeId, setTaiXeId] = useState(String(c.tai_xe_id))
  const [xe, setXe] = useState<KhaDung<XeKhaDung>>()
  const [taiXe, setTaiXe] = useState<KhaDung<TaiXeKhaDung>>()
  const [loi, setLoi] = useState<string[]>([])

  useEffect(() => {
    if (!mo) return
    let bo = false
    xeKhaDungChuyen(c.id)
      .then((ds) => !bo && setXe({ khoa: '', ds, loi: '' }))
      .catch(
        (e) => !bo && setXe({ khoa: '', ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id])
  useEffect(() => {
    if (!mo) return
    let bo = false
    taiXeKhaDungChuyen(c.id, xeId ? Number(xeId) : undefined)
      .then((ds) => !bo && setTaiXe({ khoa: xeId, ds, loi: '' }))
      .catch(
        (e) =>
          !bo && setTaiXe({ khoa: xeId, ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id, xeId])

  async function luu() {
    setLoi([])
    try {
      onLuu(await phanCong(c.id, Number(xeId), Number(taiXeId)))
      setMo(false)
    } catch (e) {
      setLoi(
        e instanceof LoiApi && e.chiTiet.length
          ? (e.chiTiet as { ma: string; thong_diep: string }[]).map((v) =>
              kemMaBr(v.thong_diep, v.ma),
            )
          : [e instanceof LoiApi ? e.message : 'Không lưu được, vui lòng thử lại'],
      )
    }
  }

  if (!mo)
    return (
      <p>
        <button className="phu" onClick={() => setMo(true)}>
          Đổi xe / tài xế
        </button>
      </p>
    )
  return (
    <div className="canh-bao">
      <div className="hai-cot">
        <ChonKhaDung
          nhan="Xe"
          kq={xe}
          gia_tri={xeId}
          onChon={setXeId}
          ten={(x) => `${x.bien_so} (${x.tai_trong_kg.toLocaleString('vi-VN')} kg)`}
        />
        <ChonKhaDung
          nhan="Tài xế"
          kq={taiXe?.khoa === xeId ? taiXe : undefined}
          gia_tri={taiXeId}
          onChon={setTaiXeId}
          ten={(t) => `${t.ho_ten} (hạng ${t.hang_gplx})`}
        />
      </div>
      {loi.length > 0 && (
        <ul role="alert" className="loi">
          {loi.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      )}
      <div className="nut">
        <button type="button" className="phu" onClick={() => setMo(false)}>
          Hủy
        </button>
        <button onClick={luu} disabled={!xeId || !taiXeId}>
          Lưu xe / tài xế
        </button>
      </div>
    </div>
  )
}
