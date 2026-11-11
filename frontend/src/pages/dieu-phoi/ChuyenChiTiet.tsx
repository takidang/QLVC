import { lazy, Suspense, useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  chiTietChuyen,
  chotChuyen,
  donPhuHop,
  ghepDon,
  goDon,
  huyChuyen,
  moChotChuyen,
  phanCong,
  TEN_CO,
  taiXeKhaDungChuyen,
  xeKhaDungChuyen,
  type ChuyenChiTiet as Chuyen,
  type TaiXeKhaDung,
  type ViPhamGhep,
  type XacNhanChot,
  type XeKhaDung,
} from '../../api/chuyen'
import { ChonKhaDung, type KhaDung } from './ChuyenDanhSach'
import { TEN_TRANG_THAI_DON, type Don } from '../../api/don'
import { kemMaBr, LoiApi } from '../../api/goi'
import { Nhan } from '../../nhan'
import { CanhBaoTheoDoi, DongThoiGian, KhoiSuCo, KhoiTien } from './TheoDoiChuyen'

// Bản đồ (leaflet + css) tải riêng khi mở chi tiết chuyến, không kéo theo vào màn đăng nhập
const BanDoChuyen = lazy(() => import('./BanDoChuyen'))

const TEN_KET_QUA: Record<string, string> = {
  LAY: 'đã lấy',
  KHONG_LAY: 'không lấy được',
  GIAO: 'đã giao',
  GIAO_THAT_BAI: 'giao không được',
}
// Nhãn đơn dùng hình của nhãn chuyến (giống màn Đơn hàng)
const NHAN_DON: Record<string, string> = {
  CHO_GHEP: 'LAP',
  DA_GHEP: 'DA_CHOT',
  DA_LAY: 'DANG_CHAY',
  DA_GIAO: 'HOAN_THANH',
  THAT_BAI: 'THAT_BAI',
  TRA_HANG: 'HUY',
  HUY: 'HUY',
}

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
// Trễ so ETA kế hoạch: âm là đến sớm
const phut = (n: number) => (n >= 60 ? `${Math.floor(n / 60)} giờ ${n % 60}′` : `${n}′`)
const tre = (n: number) => (n > 0 ? `Trễ ${phut(n)}` : n < 0 ? `Sớm ${phut(-n)}` : 'Đúng giờ')
const XAC_NHAN: Record<string, keyof XacNhanChot> = {
  'BR-23': 'xac_nhan_chay_rong',
  'BR-52': 'xac_nhan_lai_am',
}

// Chi tiết chuyến (giao diện v2, màn 03): đầu trang, số liệu, lịch trình dọc + bản đồ, tiền, dòng thời gian.
// Chi tiết chuyến, thẻ Hàng (UC-13): tải, lịch trình, ghép và gỡ đơn; chốt / mở chốt (UC-15); hủy (UC-16)
export default function ChuyenChiTiet() {
  const id = Number(useParams().id)
  const [c, setC] = useState<Chuyen | null>(null)
  const [phuHop, setPhuHop] = useState<Don[]>([])
  const [chonGhep, setChonGhep] = useState<number[]>([])
  const [chonGo, setChonGo] = useState<number[]>([])
  const [loi, setLoi] = useState('')
  const [lyDoHuy, setLyDoHuy] = useState<string | null>(null) // null: chưa mở ô nhập lý do
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

  async function lam(viec: 'ghep' | 'go' | 'chot' | 'mo-chot' | 'huy') {
    setLoi('')
    setViPham([])
    setDangGui(true)
    try {
      const goi = {
        ghep: () => ghepDon(id, chonGhep),
        go: () => goDon(id, chonGo),
        chot,
        'mo-chot': () => moChotChuyen(id),
        huy: () => huyChuyen(id, lyDoHuy ?? ''),
      }
      const moi = await goi[viec]()
      setC(moi)
      setLyDoHuy(null)
      setChonGhep([])
      setChonGo([])
      setLanTai((n) => n + 1) // tải lại đơn chờ ghép ở effect; lỗi tải lại không bị báo nhầm là lưu hỏng
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
  const daChay = !!c.tien && c.trang_thai !== 'LAP' && c.trang_thai !== 'DA_CHOT'
  // Điểm đang tới: điểm đầu tiên chưa có kết quả khi chuyến đang chạy
  const dangToi =
    c.trang_thai === 'DANG_CHAY' ? c.lich_trinh.find((d) => !d.ket_qua)?.thu_tu : undefined
  const tai = Number(c.tai_trong.da_dung_kg) / c.tai_trong.toi_da_kg
  const theTich = Number(c.the_tich.da_dung_m3) / Number(c.the_tich.toi_da_m3)
  const lapDay = Math.round(Number(c.ty_le_lap_day) * 100)

  return (
    <section className="noi-dung chi-tiet">
      <Link to=".." className="ct-ve">
        ← Danh sách chuyến
      </Link>
      <div className="ct-dau">
        <div>
          <h1>{c.ten_tuyen}</h1>
          <div className="ct-nhan">
            <span className="ma">
              {c.ma_chuyen} · {c.ma_tuyen}
            </span>
            <Nhan loai={c.trang_thai}>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</Nhan>
            {c.co?.map((x) => (
              <Nhan key={x} loai={x} title={x === 'CHONG_LICH' ? c.chong?.join(', ') : undefined}>
                {TEN_CO[x] ?? x}
              </Nhan>
            ))}
          </div>
        </div>
        <div className="ct-hanh-dong">
          {dangLap && lyDoHuy === null && (
            <button disabled={dangGui} onClick={() => lam('chot')}>
              Chốt chuyến
            </button>
          )}
          {c.trang_thai === 'DA_CHOT' && lyDoHuy === null && (
            <button className="phu" disabled={dangGui} onClick={() => lam('mo-chot')}>
              Mở chốt
            </button>
          )}
          {(dangLap || c.trang_thai === 'DA_CHOT') && lyDoHuy === null && (
            <button className="phu" disabled={dangGui} onClick={() => setLyDoHuy('')}>
              Hủy chuyến
            </button>
          )}
        </div>
      </div>
      {lyDoHuy !== null && (
        <form
          className="thanh-cong-cu canh-bao"
          onSubmit={(e) => {
            e.preventDefault()
            lam('huy')
          }}
        >
          <label>
            Lý do hủy
            <input
              required
              autoFocus
              maxLength={300}
              value={lyDoHuy}
              onChange={(e) => setLyDoHuy(e.target.value)}
            />
          </label>
          <button disabled={dangGui || !lyDoHuy.trim()}>Xác nhận hủy</button>
          <button type="button" className="phu" disabled={dangGui} onClick={() => setLyDoHuy(null)}>
            Thôi
          </button>
        </form>
      )}

      {/* Dải thông tin + số liệu chính của chuyến */}
      <div className="kinh ct-tong">
        <div className="ct-ai">
          <div>
            <small>Xe</small>
            <span className="bien">{c.bien_so}</span>
          </div>
          <div>
            <small>Tài xế</small>
            <strong>{c.ten_tai_xe}</strong>
          </div>
          <div>
            <small>Khởi hành</small>
            <strong>{lucVN(c.khoi_hanh_du_kien)}</strong>
          </div>
          <div>
            <small>{c.ket_thuc_dang_chay ? 'Dự kiến xong (đang trễ)' : 'Kết thúc dự kiến'}</small>
            <strong className={c.ket_thuc_dang_chay ? 'ct-tre' : undefined}>
              {lucVN(c.ket_thuc_dang_chay ?? c.ket_thuc_du_kien)}
            </strong>
          </div>
        </div>
        <div className="ct-so">
          <ThanhSo
            nhan="Tải trọng"
            so={`${so(c.tai_trong.da_dung_kg)} / ${dong(c.tai_trong.toi_da_kg)} kg`}
            ty={tai}
          />
          <ThanhSo
            nhan="Thể tích"
            so={`${so(c.the_tich.da_dung_m3)} / ${so(c.the_tich.toi_da_m3)} m³`}
            ty={theTich}
          />
          <div>
            <small>Lấp đầy</small>
            <b className={lapDay > 95 ? 'ct-tre' : undefined}>{lapDay}%</b>
          </div>
          <div>
            <small>{c.tien ? 'Lãi dự kiến' : 'Lãi dự kiến (chưa chốt)'}</small>
            <b className={c.canh_bao_lai_am ? 'het-han' : undefined}>{dong(c.lai_du_kien)} đ</b>
            {dangLap && c.canh_bao_lai_am && <em>lãi âm, phải xác nhận khi chốt</em>}
            {c.chay_rong && <em>chạy rỗng (đã xác nhận)</em>}
          </div>
        </div>
      </div>

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
      <CanhBaoTheoDoi c={c} onDoi={setC} />

      <div className="ct-luoi">
        <div className="ct-ben">
          {/* Lịch trình dạng dòng thời gian dọc: mỗi điểm dừng một dòng */}
          <section className="kinh ct-khoi">
            <h2>
              Lịch trình
              <em>
                {c.lich_trinh.filter((d) => d.ket_qua).length} / {c.lich_trinh.length} điểm
              </em>
            </h2>
            {c.lich_trinh.length === 0 ? (
              <p className="ghi-chu">Chưa có đơn – chuyến đang tính như chạy rỗng</p>
            ) : (
              <ol className="lt">
                {c.lich_trinh.map((d) => {
                  const hong = d.ket_qua === 'KHONG_LAY' || d.ket_qua === 'GIAO_THAT_BAI'
                  const lop = hong
                    ? 'hong'
                    : d.ket_qua === 'BO'
                      ? 'bo'
                      : d.ket_qua
                        ? 'xong'
                        : d.thu_tu === dangToi
                          ? 'toi'
                          : undefined
                  return (
                    <li key={d.thu_tu} className={lop}>
                      <i aria-hidden="true" />
                      <div>
                        <strong>{d.nut}</strong>
                        <small>
                          {d.viec === 'LAY' ? 'Lấy' : 'Giao'} · {d.ma_don}
                          {d.ket_qua === 'BO'
                            ? ' · bỏ (không lấy được)'
                            : d.ket_qua && ` · ${TEN_KET_QUA[d.ket_qua] ?? d.ket_qua}`}
                          {d.thu_tu === dangToi && ' · đang tới'}
                        </small>
                      </div>
                      <div className="lt-gio">
                        <span>{gio(d.eta)}</span>
                        {daChay && d.thuc_te && <small>quét {gio(d.thuc_te)}</small>}
                        {daChay && d.tre_phut != null && (
                          <small className={d.tre_phut > 15 ? 'ct-tre' : undefined}>
                            {tre(d.tre_phut)}
                          </small>
                        )}
                      </div>
                    </li>
                  )
                })}
              </ol>
            )}
          </section>
          <DongThoiGian c={c} />
        </div>

        <div className="ct-ben">
          <Suspense fallback={<p className="ghi-chu">Đang tải bản đồ…</p>}>
            <BanDoChuyen lichTrinh={c.lich_trinh} />
          </Suspense>
          <KhoiTien c={c} />
          <KhoiSuCo c={c} onDoi={() => setLanTai((n) => n + 1)} />
        </div>
      </div>

      <BangDon
        tieu_de={`${['HOAN_THANH', 'DA_QUYET_TOAN', 'HUY'].includes(c.trang_thai) ? 'Đơn của chuyến' : 'Đơn đang ghép'} (${c.don.length})`}
        ds={c.don}
        hienTrangThai
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

// Một số liệu kèm thanh 5 px; trên 95% đổi cam như cột Độ đầy ở bảng chuyến
function ThanhSo({ nhan, so, ty }: { nhan: string; so: string; ty: number }) {
  const pt = Math.round(ty * 100)
  return (
    <div>
      <small>{nhan}</small>
      <span className="ct-thanh-so">{so}</span>
      <span className={pt > 95 ? 'ct-thanh cao' : 'ct-thanh'}>
        <i style={{ width: `${Math.min(pt, 100)}%` }} />
      </span>
    </div>
  )
}

function BangDon({
  tieu_de,
  ds,
  chon,
  onChon,
  nut,
  hienTrangThai = false,
}: {
  tieu_de: string
  ds: Don[]
  chon?: number[]
  onChon: (id: number) => void
  nut: ReactNode
  hienTrangThai?: boolean
}) {
  const soCot = 7 + (chon ? 1 : 0) + (hienTrangThai ? 1 : 0)
  return (
    <section className="kinh bang-khung ct-don">
      <div className="cong-cu">
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
            {hienTrangThai && <th>Trạng thái</th>}
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
              {hienTrangThai && (
                <td>
                  <Nhan loai={NHAN_DON[d.trang_thai] ?? 'LAP'}>
                    {TEN_TRANG_THAI_DON[d.trang_thai] ?? d.trang_thai}
                  </Nhan>
                </td>
              )}
            </tr>
          ))}
          {ds.length === 0 && (
            <tr>
              <td colSpan={soCot} className="trong">
                Không có đơn
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
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
  // Ghép / gỡ đơn khi khung đang mở làm đổi tải cần chở (BR-01): tải lại danh sách khả dụng
  const donGhep = c.don.map((d) => d.id).join(',')

  useEffect(() => {
    if (!mo) return
    let bo = false
    xeKhaDungChuyen(c.id)
      .then((ds) => {
        if (bo) return
        setXe({ khoa: '', ds, loi: '' })
        // xe đang chọn không còn dùng được (vd. vừa ghép thêm đơn, quá tải BR-01): bỏ chọn
        setXeId((v) => (ds.some((x) => String(x.id) === v && x.kha_dung) ? v : ''))
      })
      .catch(
        (e) => !bo && setXe({ khoa: '', ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id, donGhep])
  useEffect(() => {
    if (!mo) return
    let bo = false
    taiXeKhaDungChuyen(c.id, xeId ? Number(xeId) : undefined)
      .then((ds) => {
        if (bo) return
        setTaiXe({ khoa: xeId, ds, loi: '' })
        setTaiXeId((v) => (ds.some((t) => String(t.id) === v && t.kha_dung) ? v : ''))
      })
      .catch(
        (e) =>
          !bo && setTaiXe({ khoa: xeId, ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id, xeId, donGhep])

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
