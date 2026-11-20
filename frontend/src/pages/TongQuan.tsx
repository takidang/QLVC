import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  hieuSuatXe,
  laiLo,
  laiLoThang,
  laiLoXe,
  type DongLaiLo,
  type HieuSuatXe,
  type LaiLo,
} from '../api/baoCao'
import { LoiApi } from '../api/goi'
import { tongQuanNgay, type TongQuanNgay } from '../api/tongQuan'
import { dangGiamChuyenDong } from '../nen'
import DanConTro from '../DanConTro'
import NumberFlow from '@number-flow/react'

// Trang Tổng quan của Quản lý và Kế toán (UC-26 lãi lỗ, UC-34 hiệu suất xe).
// Biểu đồ vẽ SVG tay theo skill dataviz: lãi xanh, lỗ cam (cặp đã chạy validate_palette.js, đạt cả mù màu),
// mốc ở số 0, mỗi cột có chú thích khi rê chuột / focus bàn phím và có bảng xem kèm.

const thangNay = () => new Date().toLocaleDateString('sv-SE').slice(0, 7)
const lui = (thang: string, n: number) => {
  const [y, m] = thang.split('-').map(Number)
  const d = new Date(y, m - 1 - n, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}
const tenThang = (t: string) => `${t.slice(5)}/${t.slice(0, 4)}`
const dong = (n: number) => `${n.toLocaleString('vi-VN')} đ`
// Số gọn trên trục và nhãn cột: 2,4 tr; 950 k
const gon = (n: number) => {
  const a = Math.abs(n)
  const s =
    a >= 1e6
      ? `${(a / 1e6).toLocaleString('vi-VN', { maximumFractionDigits: 1 })} tr`
      : a >= 1e3
        ? `${Math.round(a / 1e3)} k`
        : `${a}`
  return n < 0 ? `−${s}` : s
}

export default function TongQuan({ ketToan = false }: { ketToan?: boolean }) {
  const [thang, setThang] = useState(thangNay)
  const [theoThang, setTheoThang] = useState<LaiLo<DongLaiLo & { thang: string }> | null>(null)
  const [theoXe, setTheoXe] = useState<LaiLo<
    DongLaiLo & { xe_id: number; bien_so: string }
  > | null>(null)
  const [hieuSuat, setHieuSuat] = useState<HieuSuatXe[] | null>(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    let bo = false
    Promise.all([laiLoThang(lui(thang, 5), thang), laiLoXe(thang), hieuSuatXe(thang)])
      .then(([a, b, c]) => {
        if (bo) return
        setLoi('')
        setTheoThang(a)
        setTheoXe(b)
        setHieuSuat(c.du_lieu)
      })
      .catch((e) => !bo && setLoi(e instanceof LoiApi ? e.message : 'Không tải được số liệu'))
    return () => {
      bo = true
    }
  }, [thang])

  const t = theoThang?.du_lieu.find((d) => d.thang === thang)
  return (
    <section className="noi-dung tong-quan">
      <DanConTro />
      <div className="tq-dau">
        <div>
          <h1>Tổng quan</h1>
          <p className="ghi-chu">Tình hình hôm nay và lãi lỗ theo tháng.</p>
        </div>
        <label className="tq-thang">
          Tháng
          <input
            type="month"
            value={thang}
            max={thangNay()}
            onChange={(e) => e.target.value && setThang(e.target.value)}
          />
        </label>
      </div>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}

      <HomNay />

      {/* Hàng số liệu của tháng đang chọn */}
      <h2 className="tq-tieu-de">
        Tháng {tenThang(thang)} <small>chỉ tính chuyến đã quyết toán, theo ngày khởi hành</small>
      </h2>
      <div className="kinh tq-so">
        <SoLieu
          nhan="Doanh thu"
          so={t?.doanh_thu}
          phu={t ? `${t.so_chuyen} chuyến đã quyết toán` : undefined}
        />
        <SoLieu nhan="Chi phí chuyến" so={t?.tong_chi} />
        <SoLieu nhan="Lương tài xế" so={t?.luong_tai_xe} />
        <SoLieu nhan="Chi phí cố định xe" so={t?.chi_phi_co_dinh} />
        <SoLieu nhan="Lãi" so={t?.lai} lai />
      </div>

      {/* Việc làm số liệu chưa đủ: chuyến chờ quyết toán, xe thiếu chi phí cố định */}
      {theoThang &&
      (theoThang.so_chuyen_cho_quyet_toan > 0 || theoXe?.thieu_chi_phi_co_dinh.length) ? (
        <ul className="tq-luu-y">
          {theoThang.so_chuyen_cho_quyet_toan > 0 && (
            <li>
              {theoThang.so_chuyen_cho_quyet_toan} chuyến đã chạy xong nhưng chưa quyết toán, chưa
              vào số liệu. {ketToan && <Link to="../quyet-toan">Quyết toán</Link>}
            </li>
          )}
          {(theoXe?.thieu_chi_phi_co_dinh.length ?? 0) > 0 && (
            <li>
              Chưa nhập chi phí cố định tháng {tenThang(thang)}:{' '}
              {theoXe!.thieu_chi_phi_co_dinh.map((x) => x.bien_so).join(', ')}.{' '}
              {ketToan && <Link to="../chi-phi-xe">Nhập chi phí</Link>}
            </li>
          )}
        </ul>
      ) : !theoThang && !loi ? (
        // Đang tải: giữ chỗ một dòng lưu ý để khi số liệu về khung này không đẩy biểu đồ xuống
        <div className="tq-luu-y-cho" aria-hidden="true" />
      ) : null}

      <div className="tq-luoi">
        <section className="kinh tq-khoi">
          <h2>Lãi theo tháng</h2>
          {theoThang ? <CotLai ds={theoThang.du_lieu} chon={thang} /> : <GiuCho loai="cot" />}
          {theoThang && (
            <details className="tq-bang">
              <summary>Xem dạng bảng</summary>
              <div className="tq-cuon">
                <table>
                  <thead>
                    <tr>
                      <th>Tháng</th>
                      <th className="so">Chuyến</th>
                      <th className="so">Doanh thu</th>
                      <th className="so">Chi phí</th>
                      <th className="so">Lương</th>
                      <th className="so">Cố định</th>
                      <th className="so">Lãi</th>
                    </tr>
                  </thead>
                  <tbody>
                    {theoThang.du_lieu.map((d) => (
                      <tr key={d.thang}>
                        <td>{tenThang(d.thang)}</td>
                        <td className="so">{d.so_chuyen}</td>
                        <td className="so">{d.doanh_thu.toLocaleString('vi-VN')}</td>
                        <td className="so">{d.tong_chi.toLocaleString('vi-VN')}</td>
                        <td className="so">{d.luong_tai_xe.toLocaleString('vi-VN')}</td>
                        <td className="so">{d.chi_phi_co_dinh.toLocaleString('vi-VN')}</td>
                        <td className={d.lai < 0 ? 'so tq-am' : 'so'}>
                          {d.lai.toLocaleString('vi-VN')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          )}
        </section>

        <section className="kinh tq-khoi">
          <h2>Lãi theo xe · {tenThang(thang)}</h2>
          {theoXe ? <ThanhXe ds={theoXe.du_lieu} /> : <GiuCho loai="xe" />}
        </section>
      </div>

      <section className="kinh tq-khoi">
        <h2>Hiệu suất xe · {tenThang(thang)}</h2>
        {hieuSuat ? <BangHieuSuat ds={hieuSuat} /> : <GiuCho loai="bang" />}
      </section>

      <BangLaiLo den={thang} />
    </section>
  )
}

// UC-26-AC8: bảng lãi lỗ chọn khoảng tháng, xem theo Chuyến / Xe / Tháng, có dòng tổng, lãi âm tô màu lỗ
type DongChiTiet = DongLaiLo & {
  thang?: string
  bien_so?: string
  ma_chuyen?: string
  ngay?: string
  ten_tuyen?: string
}
const CACH_XEM: [LaiLo<DongChiTiet>['theo'], string][] = [
  ['chuyen', 'Chuyến'],
  ['xe', 'Xe'],
  ['thang', 'Tháng'],
]
function BangLaiLo({ den: denMacDinh }: { den: string }) {
  const [tu, setTu] = useState(() => lui(denMacDinh, 2))
  const [den, setDen] = useState(denMacDinh)
  const [theo, setTheo] = useState<LaiLo<DongChiTiet>['theo']>('chuyen')
  const [kq, setKq] = useState<LaiLo<DongChiTiet> | null>(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    let bo = false
    laiLo<DongChiTiet>(theo, tu, den)
      .then((r) => {
        if (bo) return
        setLoi('')
        setKq(r)
      })
      .catch((e) => {
        if (bo) return
        setKq(null)
        setLoi(e instanceof LoiApi ? e.message : 'Không tải được số liệu')
      })
    return () => {
      bo = true
    }
  }, [theo, tu, den])

  const so = (n: number) => n.toLocaleString('vi-VN')
  const lai = (n: number) => <td className={n < 0 ? 'so tq-am' : 'so'}>{so(n)}</td>
  // Vẽ theo cách xem của số liệu đang có (không theo nút vừa bấm, số liệu mới chưa về)
  const xem = kq?.theo ?? theo
  const coDinh = xem !== 'chuyen'
  return (
    <section className="kinh tq-khoi tq-chi-tiet">
      <h2>Bảng lãi lỗ</h2>
      <div className="tq-loc">
        <label>
          Từ tháng
          <input
            type="month"
            value={tu}
            max={den}
            onChange={(e) => e.target.value && setTu(e.target.value)}
          />
        </label>
        <label>
          Đến tháng
          <input
            type="month"
            value={den}
            min={tu}
            max={thangNay()}
            onChange={(e) => e.target.value && setDen(e.target.value)}
          />
        </label>
        <div className="vien-thuoc" role="group" aria-label="Xem theo">
          {CACH_XEM.map(([ma, ten]) => (
            <button key={ma} aria-pressed={theo === ma} onClick={() => setTheo(ma)}>
              {ten}
            </button>
          ))}
        </div>
      </div>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      {kq && (kq.so_chuyen_cho_quyet_toan > 0 || kq.thieu_chi_phi_co_dinh.length > 0) && (
        <ul className="tq-luu-y">
          {kq.so_chuyen_cho_quyet_toan > 0 && (
            <li>{kq.so_chuyen_cho_quyet_toan} chuyến chờ quyết toán, chưa vào bảng.</li>
          )}
          {kq.thieu_chi_phi_co_dinh.length > 0 && (
            <li>
              Chưa nhập chi phí cố định:{' '}
              {kq.thieu_chi_phi_co_dinh
                .map((x) => `${x.bien_so} (${tenThang(x.thang)})`)
                .join(', ')}
              .
            </li>
          )}
        </ul>
      )}
      {!kq ? (
        !loi && <p className="ghi-chu">Đang tải…</p>
      ) : (
        <div className="tq-cuon">
          <table>
            <thead>
              <tr>
                {xem === 'chuyen' && (
                  <>
                    <th>Chuyến</th>
                    <th>Ngày</th>
                    <th>Xe</th>
                  </>
                )}
                {xem === 'xe' && <th>Xe</th>}
                {xem === 'thang' && <th>Tháng</th>}
                {xem !== 'chuyen' && <th className="so">Chuyến</th>}
                <th className="so">Doanh thu</th>
                <th className="so">Chi phí</th>
                <th className="so">Lương</th>
                {coDinh && <th className="so">Cố định</th>}
                <th className="so">Lãi</th>
              </tr>
            </thead>
            <tbody>
              {kq.du_lieu.length === 0 && (
                <tr>
                  <td colSpan={8} className="ghi-chu">
                    Không có chuyến đã quyết toán trong khoảng này.
                  </td>
                </tr>
              )}
              {kq.du_lieu.map((d, i) => (
                <tr key={d.ma_chuyen ?? d.bien_so ?? d.thang ?? i}>
                  {xem === 'chuyen' && (
                    <>
                      <td className="ma-don">{d.ma_chuyen}</td>
                      <td>{d.ngay?.split('-').reverse().join('/')}</td>
                      <td>
                        <span className="bien">{d.bien_so}</span>
                      </td>
                    </>
                  )}
                  {xem === 'xe' && (
                    <td>
                      <span className="bien">{d.bien_so}</span>
                    </td>
                  )}
                  {xem === 'thang' && <td>{tenThang(d.thang!)}</td>}
                  {xem !== 'chuyen' && <td className="so">{d.so_chuyen}</td>}
                  <td className="so">{so(d.doanh_thu)}</td>
                  <td className="so">{so(d.tong_chi)}</td>
                  <td className="so">{so(d.luong_tai_xe)}</td>
                  {coDinh && <td className="so">{so(d.chi_phi_co_dinh)}</td>}
                  {lai(d.lai)}
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={xem === 'chuyen' ? 3 : 2}>
                  Tổng
                  {xem === 'chuyen'
                    ? ` (${kq.du_lieu.length} chuyến)`
                    : ` (${kq.tong.so_chuyen} chuyến)`}
                </td>
                <td className="so">{so(kq.tong.doanh_thu)}</td>
                <td className="so">{so(kq.tong.tong_chi)}</td>
                <td className="so">{so(kq.tong.luong_tai_xe)}</td>
                {coDinh && <td className="so">{so(kq.tong.chi_phi_co_dinh)}</td>}
                {lai(kq.tong.lai)}
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </section>
  )
}

// Khối giữ chỗ lúc đang tải: nền tĩnh cao gần bằng khối thật (CSS .tq-cho-*) để trang không nhảy khi số liệu về
function GiuCho({ loai }: { loai: 'cot' | 'xe' | 'bang' }) {
  return (
    <div className={`tq-cho tq-cho-${loai}`}>
      <span className="an-chu" role="status">
        Đang tải…
      </span>
    </div>
  )
}

function SoLieu({
  nhan,
  so,
  phu,
  lai,
}: {
  nhan: string
  so?: number
  phu?: string
  lai?: boolean
}) {
  return (
    <div>
      <small>{nhan}</small>
      <b className={lai && so !== undefined && so < 0 ? 'tq-am' : undefined}>
        {so === undefined ? (
          '–'
        ) : (
          <NumberFlow value={so} locales="vi-VN" suffix=" đ" animated={!dangGiamChuyenDong()} />
        )}
      </b>
      {lai && so !== undefined && so < 0 && <em>Lỗ trong tháng</em>}
      {phu && <em>{phu}</em>}
    </div>
  )
}

// Cột lãi theo tháng: mốc 0 nằm ngang, lãi đi lên (xanh), lỗ đi xuống (cam); tháng đang chọn đậm hơn
function CotLai({ ds, chon }: { ds: (DongLaiLo & { thang: string })[]; chon: string }) {
  const [tro, setTro] = useState<string | null>(null)
  // Màn hẹp vẽ khung nhỏ hơn để chữ trên trục không bị thu quá bé
  const [hep] = useState(() => matchMedia('(max-width: 600px)').matches)
  const W = hep ? 340 : 560
  const H = 220
  const trai = 56
  const tren = 16
  const duoi = 28
  const lon = Math.max(...ds.map((d) => d.lai), 0)
  const nho = Math.min(...ds.map((d) => d.lai), 0)
  const bien = lon - nho || 1
  const y = (v: number) => tren + ((lon - v) / bien) * (H - tren - duoi)
  const rong = (W - trai) / ds.length
  const cot = Math.min(36, rong * 0.5)
  const dangTro = ds.find((d) => d.thang === tro)
  return (
    <div className="bd-khung">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`Lãi theo tháng từ ${tenThang(ds[0].thang)} đến ${tenThang(ds.at(-1)!.thang)}`}
      >
        {/* Lưới: chỉ đường 0 và hai mức đầu, nét mảnh */}
        {[lon, 0, nho]
          .filter((v, i, a) => a.indexOf(v) === i)
          .map((v) => (
            <g key={v}>
              <line
                x1={trai}
                x2={W}
                y1={y(v)}
                y2={y(v)}
                className={v === 0 ? 'bd-moc' : 'bd-luoi'}
              />
              <text x={trai - 8} y={y(v) + 4} className="bd-truc" textAnchor="end">
                {gon(v)}
              </text>
            </g>
          ))}
        {ds.map((d, i) => {
          const x = trai + i * rong + (rong - cot) / 2
          const y0 = y(Math.max(d.lai, 0))
          const h = Math.abs(y(d.lai) - y(0))
          return (
            <g
              key={d.thang}
              tabIndex={0}
              role="img"
              aria-label={`${tenThang(d.thang)}: ${d.lai < 0 ? 'lỗ' : 'lãi'} ${dong(Math.abs(d.lai))}, ${d.so_chuyen} chuyến`}
              onClick={() => setTro((v) => (v === d.thang ? null : d.thang))}
              onMouseEnter={() => setTro(d.thang)}
              onMouseLeave={() => setTro(null)}
              onFocus={() => setTro(d.thang)}
              onBlur={() => setTro(null)}
              className="bd-cot-nhom"
            >
              {/* Vùng chạm rộng hơn cột */}
              <rect
                x={trai + i * rong}
                y={tren}
                width={rong}
                height={H - tren - duoi}
                className="bd-cham"
              />
              {h > 0 && (
                <rect
                  x={x}
                  y={y0}
                  width={cot}
                  height={Math.max(h, 2)}
                  rx={4}
                  className={`${d.lai < 0 ? 'bd-am' : 'bd-duong'}${d.thang === chon ? ' chon' : ''}`}
                />
              )}
              {/* Nhãn số: lãi trên đầu cột; lỗ nằm trong cột khi cột đủ to, cột hẹp thì xem ở chú thích */}
              {(d.lai > 0 || (d.lai < 0 && h > 28 && cot >= 30)) && (
                <text
                  x={x + cot / 2}
                  y={d.lai < 0 ? (h > 28 ? y(d.lai) - 8 : y(d.lai) + 14) : y0 - 6}
                  textAnchor="middle"
                  className={d.lai < 0 && h > 28 ? 'bd-nhan trong' : 'bd-nhan'}
                >
                  {gon(d.lai)}
                </text>
              )}
              <text
                x={x + cot / 2}
                y={H - 8}
                textAnchor="middle"
                className={d.thang === chon ? 'bd-truc chon' : 'bd-truc'}
              >
                {tenThang(d.thang).slice(0, 2)}/{d.thang.slice(2, 4)}
              </text>
            </g>
          )
        })}
      </svg>
      {dangTro && (
        <div
          className={ds.indexOf(dangTro) >= ds.length / 2 ? 'bd-goi-y trai' : 'bd-goi-y'}
          role="status"
        >
          <strong>Tháng {tenThang(dangTro.thang)}</strong>
          <span>Doanh thu {dong(dangTro.doanh_thu)}</span>
          <span>Chi phí chuyến − {dong(dangTro.tong_chi)}</span>
          <span>Lương tài xế − {dong(dangTro.luong_tai_xe)}</span>
          <span>Chi phí cố định − {dong(dangTro.chi_phi_co_dinh)}</span>
          <b className={dangTro.lai < 0 ? 'tq-am' : undefined}>
            {dangTro.lai < 0 ? 'Lỗ' : 'Lãi'} {dong(Math.abs(dangTro.lai))}
          </b>
        </div>
      )}
      <p className="bd-chu-giai">
        <span>
          <i className="bd-duong" /> Lãi
        </span>
        <span>
          <i className="bd-am" /> Lỗ
        </span>
        <span>· chạm, rê chuột hoặc Tab vào cột để xem chi tiết</span>
      </p>
    </div>
  )
}

// Lãi theo xe: thanh ngang xếp từ lãi cao xuống, mốc 0 chung; xe lỗ thanh cam đi về bên trái
function ThanhXe({ ds }: { ds: (DongLaiLo & { bien_so: string })[] }) {
  if (ds.length === 0)
    return <p className="ghi-chu">Tháng này chưa có chuyến nào được quyết toán.</p>
  const sx = [...ds].sort((a, b) => b.lai - a.lai)
  const lon = Math.max(...sx.map((d) => d.lai), 0)
  const nho = Math.min(...sx.map((d) => d.lai), 0)
  const bien = lon - nho || 1
  const moc = (-nho / bien) * 100
  return (
    <ul className="tq-xe">
      {sx.map((d) => (
        <li key={d.bien_so}>
          <span className="bien">{d.bien_so}</span>
          <span className="tq-xe-truc" style={{ ['--moc' as string]: `${moc}%` }}>
            <i
              className={d.lai < 0 ? 'bd-am' : 'bd-duong'}
              style={{
                left: `${d.lai < 0 ? moc - (-d.lai / bien) * 100 : moc}%`,
                width: `${(Math.abs(d.lai) / bien) * 100}%`,
              }}
            />
          </span>
          <span className={d.lai < 0 ? 'so tq-am' : 'so'}>
            {gon(d.lai)}
            <small>{d.so_chuyen} chuyến</small>
          </span>
        </li>
      ))}
    </ul>
  )
}

// Hiệu suất xe: mỗi xe một dòng; lấp đầy là thanh trên giới hạn 100%, dầu thực tế so với tham khảo
function BangHieuSuat({ ds }: { ds: HieuSuatXe[] }) {
  const chay = ds.filter((d) => d.so_chuyen > 0)
  const nghi = ds.length - chay.length
  if (chay.length === 0)
    return <p className="ghi-chu">Tháng này chưa có xe nào chạy xong chuyến.</p>
  return (
    <>
      <div className="tq-cuon">
        <table className="tq-hs">
          <thead>
            <tr>
              <th>Xe</th>
              <th className="so">Chuyến</th>
              <th>Lấp đầy trung bình</th>
              <th className="so">Km</th>
              <th className="so">Dầu thực tế / tham khảo (lít)</th>
              <th className="so">Chênh lệch (lít)</th>
              <th className="so">Chưa quyết toán</th>
            </tr>
          </thead>
          <tbody>
            {chay.map((d) => {
              const pt = d.lap_day_tb === null ? null : Math.round(d.lap_day_tb * 100)
              return (
                <tr key={d.xe_id}>
                  <td>
                    <span className="bien">{d.bien_so}</span>
                  </td>
                  <td className="so">
                    {d.so_chuyen}
                    {d.so_chuyen_rong > 0 && <small> ({d.so_chuyen_rong} rỗng)</small>}
                  </td>
                  <td>
                    {pt !== null && (
                      <div className="day">
                        <span>
                          <i style={{ width: `${Math.min(pt, 100)}%` }} />
                        </span>
                        {pt}%
                      </div>
                    )}
                  </td>
                  <td className="so">{d.km.toLocaleString('vi-VN')}</td>
                  <td className="so">
                    {d.dau_thuc_te_lit.toLocaleString('vi-VN')} /{' '}
                    {d.dau_tham_khao_lit === null
                      ? '–'
                      : d.dau_tham_khao_lit.toLocaleString('vi-VN')}
                    {d.dau_thuc_te_lit === 0 && <small> chưa duyệt dầu</small>}
                  </td>
                  {/* UC-34-AC7: chênh lệch dương = hao hơn định mức, tô màu lỗ.
                      Chưa duyệt khoản dầu nào thì so sánh vô nghĩa (âm giả), hiện "–" (Kiệt 18/11) */}
                  {d.chenh_lech_lit === null || d.dau_thuc_te_lit === 0 ? (
                    <td className="so">–</td>
                  ) : (
                    <td className={d.chenh_lech_lit > 0 ? 'so tq-am' : 'so'}>
                      {d.chenh_lech_lit > 0 ? '+' : ''}
                      {d.chenh_lech_lit.toLocaleString('vi-VN')}
                    </td>
                  )}
                  <td className="so">{d.so_chuyen_chua_quyet_toan || ''}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {nghi > 0 && (
        <p className="ghi-chu">{nghi} xe đang hoạt động không chạy chuyến nào trong tháng.</p>
      )}
    </>
  )
}

// UC-38: tình hình hôm nay (mọi chuyến, không chỉ chuyến đã quyết toán). Lỗi thì ẩn cả khối, không chặn trang.
// Đang tải (tq === undefined) thì vẽ sẵn khung với số "–" để phần dưới không bị đẩy xuống khi số liệu về.
function HomNay() {
  const homNay = new Date().toLocaleDateString('sv-SE')
  const [ngayChon, setNgayChon] = useState(homNay) // mặc định hôm nay, đổi được ngày khác
  const [tq, setTq] = useState<TongQuanNgay | null | undefined>(undefined)
  useEffect(() => {
    tongQuanNgay(ngayChon)
      .then(setTq)
      .catch(() => setTq(null))
  }, [ngayChon])
  if (tq === null) return null
  const tt: Record<string, number> = tq?.chuyen.theo_trang_thai ?? {}
  const dg = tq?.dung_gio
  const ngayXem = tq?.ngay ?? ngayChon
  const ngay = new Date(`${ngayXem}T00:00`).toLocaleDateString('vi-VN', {
    weekday: 'long',
    day: '2-digit',
    month: '2-digit',
  })
  const cho = '\u00a0' // giữ chiều cao dòng phụ lúc đang tải
  return (
    <section className="tq-hom-nay" aria-busy={!tq}>
      <div className="tq-hn-dau">
        <h2>
          {ngayXem === homNay ? 'Hôm nay' : 'Ngày'} · {ngay}
        </h2>
        <input
          type="date"
          aria-label="Xem ngày"
          value={ngayChon}
          max={homNay}
          onChange={(e) => e.target.value && setNgayChon(e.target.value)}
        />
        {ngayChon !== homNay && (
          <button className="phu" onClick={() => setNgayChon(homNay)}>
            Hôm nay
          </button>
        )}
      </div>
      <div className="kinh tq-so">
        <div>
          <small>Chuyến</small>
          <b>{tq ? tq.chuyen.tong : '–'}</b>
          <em>
            {tq ? (
              <>
                {tt.DANG_CHAY ?? 0} đang chạy · {(tt.HOAN_THANH ?? 0) + (tt.DA_QUYET_TOAN ?? 0)}{' '}
                xong · {(tt.LAP ?? 0) + (tt.DA_CHOT ?? 0)} chưa đi
              </>
            ) : (
              cho
            )}
          </em>
        </div>
        <div>
          <small>Đơn</small>
          <b>{tq ? tq.don.tong : '–'}</b>
          <em>
            {tq
              ? `${tq.don.da_giao} đã giao · ${tq.don.that_bai} thất bại · ${tq.don.con_lai} còn lại`
              : cho}
          </em>
        </div>
        <div>
          <small>Điểm dừng đúng giờ</small>
          <b>{!dg || dg.ty_le === null ? '–' : `${Math.round(dg.ty_le * 100)}%`}</b>
          <em>
            {dg ? (
              <>
                {dg.da_quet ? `${dg.dung_gio} / ${dg.da_quet} điểm đã quét` : 'Chưa quét điểm nào'}{' '}
                · trễ quá {dg.nguong_tre_phut}′ tính là trễ
              </>
            ) : (
              cho
            )}
          </em>
        </div>
        <div>
          <small>Hàng đã chở</small>
          <b>
            {tq
              ? `${tq.don.kg_da_cho.toLocaleString('vi-VN', { maximumFractionDigits: 0 })} kg`
              : '–'}
          </b>
        </div>
        <div>
          <small>Doanh thu dự kiến</small>
          <b>{tq ? `${tq.doanh_thu_du_kien.toLocaleString('vi-VN')} đ` : '–'}</b>
          <em>cước các đơn của chuyến trong ngày, chưa trừ đơn thất bại</em>
        </div>
      </div>
    </section>
  )
}
