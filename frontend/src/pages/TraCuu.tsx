import { useEffect, useRef, useState, type CSSProperties, type FormEvent } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { LoiApi } from '../api/goi'
import { traCuu, type KetQuaTraCuu } from '../api/traCuu'
import { XeTaiHanhTrinhPixel } from '../HieuUngPixel'
import { dangHieuUngPixel, NEN, phongCachDaLuu } from '../nen'
import { useHienKhiCuon } from '../useHienKhiCuon'
import { LogoTK, TenThuongHieu } from '../LogoTK'

// Tên trạng thái đơn viết cho khách (không dùng từ nội bộ như "ghép", "thất bại")
const TEN_CHO_KHACH: Record<string, string> = {
  CHO_GHEP: 'Đã tiếp nhận đơn',
  DA_GHEP: 'Đã xếp chuyến xe',
  DA_LAY: 'Đã lấy hàng, đang vận chuyển',
  DA_GIAO: 'Đã giao hàng',
  THAT_BAI: 'Giao chưa thành công, đang chờ giao lại',
  TRA_HANG: 'Đang hoàn trả hàng',
  HUY: 'Đơn đã hủy',
}
const luc = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })

// UC-28-AC7: trang tra cứu công khai cho khách. ?ma=DH-… điền sẵn mã đơn (link điều phối gửi khách)
export default function TraCuu() {
  const [thamSo] = useSearchParams()
  const [ma, setMa] = useState(thamSo.get('ma') ?? '')
  const [so, setSo] = useState(() => {
    const v = thamSo.get('so') ?? ''
    return /^\d{4}$/.test(v) ? v : ''
  })
  // Từ phiếu tra cứu ở trang đăng nhập đã có sẵn kết quả (state.kq): dùng luôn, khỏi gọi API lần nữa
  const kqSan = (useLocation().state as { kq?: KetQuaTraCuu } | null)?.kq
  const coSan =
    !!kqSan && kqSan.ma_don.toUpperCase() === (thamSo.get('ma') ?? '').trim().toUpperCase()
  const [kq, setKq] = useState<KetQuaTraCuu | null>(coSan ? kqSan : null)
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  const oMa = useRef<HTMLInputElement>(null)
  const oKq = useRef<HTMLHeadingElement>(null)
  useHienKhiCuon(kq?.ma_don)

  async function gui(e?: FormEvent) {
    e?.preventDefault()
    if (!ma.trim() || !/^\d{4}$/.test(so))
      return setLoi('Nhập mã đơn và đúng 4 chữ số cuối số điện thoại')
    setLoi('')
    setKq(null)
    setDangGui(true)
    try {
      setKq(await traCuu(ma.trim(), so))
      // Có kết quả: đưa focus (và màn hình) tới trạng thái, trình đọc màn hình đọc ngay
      requestAnimationFrame(() => oKq.current?.focus())
    } catch (err) {
      setLoi(
        err instanceof LoiApi && err.status === 404
          ? 'Không tìm thấy đơn. Kiểm tra lại mã đơn trên phiếu gửi hàng và 4 số cuối số điện thoại người gửi hoặc người nhận.'
          : err instanceof LoiApi && err.status !== 400
            ? err.message
            : 'Nhập mã đơn và đúng 4 chữ số cuối số điện thoại',
      )
      oMa.current?.focus()
    } finally {
      setDangGui(false)
    }
  }

  // Vào từ phiếu tra cứu ở trang đăng nhập (?ma=&so=): tra một lần ngay khi mở
  const daTuTra = useRef(false) // StrictMode chạy effect 2 lần: chỉ tra 1 lần (API tra cứu có giới hạn tần suất)
  useEffect(() => {
    if (daTuTra.current) return
    daTuTra.current = true
    if (!coSan && ma.trim() && /^\d{4}$/.test(so)) void gui()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Mốc mới nhất trên cùng; mốc đầu là trạng thái hiện tại
  const moc = kq ? [...kq.moc].reverse() : []
  const veMayIn = useNavigate()
  const traKhac = () => {
    // Pixel: quay về máy in ở trang đăng nhập và in luôn phiếu tra cứu mới
    if (phongCachDaLuu() === 'pixel') {
      veMayIn('/dang-nhap', { state: { inPhieu: 'khach' } })
      return
    }
    setKq(null)
    setSo('')
    requestAnimationFrame(() => oMa.current?.select())
  }

  return (
    <main className="tra-cuu">
      <div className="tc-trai">
        <header>
          <span className="thuong-hieu">
            <LogoTK co={22} />
            <TenThuongHieu />
          </span>
          <Link to="/dang-nhap" className="tc-nv">
            Nhân viên đăng nhập
          </Link>
        </header>

        {kq ? (
          // Có kết quả: form thu thành một dòng để trạng thái nổi lên đầu
          <div className="kinh tc-gon">
            <span>
              <strong>{kq.ma_don}</strong> · số cuối {so}
            </span>
            <button type="button" className="phu" onClick={traKhac}>
              Tra đơn khác
            </button>
          </div>
        ) : (
          <section className="kinh tc-khung">
            <h1>Tra cứu đơn hàng</h1>
            <p className="tc-phu">
              Mã đơn in trên phiếu gửi hàng, ví dụ <span className="ma-nguyen">DH-KTD27M</span>.
            </p>
            <form onSubmit={gui} noValidate>
              <label>
                Mã đơn
                <input
                  ref={oMa}
                  value={ma}
                  onChange={(e) => setMa(e.target.value)}
                  autoCapitalize="characters"
                  autoComplete="off"
                  spellCheck={false}
                  maxLength={20}
                  required
                />
              </label>
              <label>
                4 số cuối điện thoại
                <input
                  value={so}
                  onChange={(e) => setSo(e.target.value.replace(/\D/g, '').slice(0, 4))}
                  inputMode="numeric"
                  autoComplete="off"
                  placeholder="vd 6789"
                  maxLength={4}
                  required
                />
                <small>Của người gửi hoặc người nhận</small>
              </label>
              <button disabled={dangGui}>{dangGui ? 'Đang tra cứu…' : 'Tra cứu'}</button>
            </form>
            {loi && (
              <p role="alert" className="loi">
                {loi}
              </p>
            )}
          </section>
        )}

        {kq && (
          <section key={kq.ma_don} className="kinh tc-khung tc-kq" aria-live="polite">
            <h2 ref={oKq} tabIndex={-1}>
              {TEN_CHO_KHACH[kq.trang_thai] ?? kq.trang_thai}
            </h2>
            {/* Hiệu ứng Pixel: xe tải pixel chạy trên dải mốc hành trình tới trạng thái hiện tại */}
            {dangHieuUngPixel() && <XeTaiHanhTrinhPixel trangThai={kq.trang_thai} moc={kq.moc} />}
            <ol className="lt">
              {moc.map((m, i) => (
                <li key={`${m.trang_thai}-${m.luc}`} className={i === 0 ? 'toi' : 'xong'}>
                  <i aria-hidden="true" />
                  <div>
                    {/* Mốc mới nhất chính là trạng thái ở dòng tiêu đề: chỉ ghi "Hiện tại" */}
                    <strong>
                      {i === 0 ? 'Hiện tại' : (TEN_CHO_KHACH[m.trang_thai] ?? m.trang_thai)}
                    </strong>
                    <small>{luc(m.luc)}</small>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        )}
      </div>

      {/* Máy tính: ảnh xe bên phải như màn đăng nhập (cùng ảnh, cùng bộ màu); điện thoại ẩn */}
      <section
        className="dn-hinh tc-hinh"
        aria-hidden="true"
        style={{ '--anh': `url(${NEN.anh})` } as CSSProperties}
      />
    </main>
  )
}
