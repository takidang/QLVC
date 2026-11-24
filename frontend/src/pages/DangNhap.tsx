import { useEffect, useRef, useState, type CSSProperties, type FormEvent } from 'react'
import { dangNhap, LoiApi, type NguoiDung } from '../api/auth'
import { traCuu } from '../api/traCuu'
import { Link, useNavigate } from 'react-router-dom'
import { dangHieuUng, dangHieuUngPixel, NEN, phongCachDaLuu } from '../nen'
import NenHat from '../NenHat'
import { LogoTK, TenThuongHieu } from '../LogoTK'

const CAU_GIOI_THIEU =
  'Lập chuyến, theo dõi từng điểm dừng, giao hàng bằng quét mã và quyết toán theo chuyến.'

// QR trang trí trên phiếu (không quét được): '#' là ô đen
const LUOI_QR = [
  '#######.#.#######',
  '#.....#..#.#.....#',
  '#.###.#.##.#.###.#',
  '#.###.#..#.#.###.#',
  '#.###.#.#..#.###.#',
  '#.....#.##.#.....#',
  '#######.#.#.#####.',
  '.........##.......',
  '#.##.#.###..#.##.#',
  '.#..##...#.#..#.#.',
  '###.#.##..#.##..##',
  '........#.#.#.#...',
  '#######.##..#.#.#.',
  '#.....#..#.#..##.#',
  '#.###.#.#.##.#..#.',
  '#.###.#...#.#.#.#.',
  '#######.#.##.#.#..',
] as const
const O_QR = LUOI_QR.flatMap((hang, y) =>
  [...hang].flatMap((c, x) => (c === '#' ? [{ x, y }] : [])),
)

function QrTrangTri() {
  return (
    <svg className="dn-qr" viewBox="0 0 18 17" aria-hidden="true">
      {O_QR.map((o) => (
        <rect key={`${o.x}-${o.y}`} x={o.x} y={o.y} width="1" height="1" />
      ))}
    </svg>
  )
}

type Dau = { id: number; ok: boolean; chu: string; phu: string }
const cho = (ms: number) => new Promise<void>((xong) => window.setTimeout(xong, ms))

const maPhieu = (tien: string) =>
  `#${tien}-${String(Math.floor(Math.random() * 10000)).padStart(4, '0')}`

export default function DangNhap({ onXong }: { onXong: (nd: NguoiDung) => void }) {
  const [ten, setTen] = useState('')
  const [matKhau, setMatKhau] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  const oMatKhau = useRef<HTMLInputElement>(null)
  // Pixel: trang đăng nhập là "máy in phiếu". phieu = tờ đang in (null = chưa in, chờ bấm logo)
  const [pixel] = useState(() => phongCachDaLuu() === 'pixel')
  const navigate = useNavigate()
  const [phieu, setPhieu] = useState<'nv' | 'khach' | null>(() =>
    pixel && !dangHieuUngPixel() ? 'nv' : null,
  )
  const [lan, setLan] = useState(0) // đổi khi in tờ mới để chạy lại hiệu ứng in
  const [xe, setXe] = useState(false)
  const [dangIn, setDangIn] = useState(false)
  const [thongBao, setThongBao] = useState('')
  const [maDon, setMaDon] = useState('')
  const [soCuoi, setSoCuoi] = useState('')
  const [loiKhach, setLoiKhach] = useState('')
  const [ma] = useState(() => ({ nv: maPhieu('NV'), khach: maPhieu('TC') }))
  const [luc] = useState(() =>
    new Date().toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }),
  )
  // Con dấu đóng lên phiếu (chỉ khi có Hiệu ứng Pixel): xanh = được, đỏ = bị từ chối
  const [dau, setDau] = useState<Dau | null>(null)
  const dongDau = (ok: boolean, chu: string, phu: string) => {
    if (!dangHieuUngPixel()) return
    const moi = { id: Date.now(), ok, chu, phu }
    setDau(moi)
    if (!ok) window.setTimeout(() => setDau((d) => (d === moi ? null : d)), 1500)
  }
  const oTen = useRef<HTMLInputElement>(null)
  const oMaDon = useRef<HTMLInputElement>(null)
  // In tờ mới; có hiệu ứng thì đèn nháy ~500 ms, phiếu trượt ra, xong mới báo và đưa con trỏ vào ô đầu
  const inPhieu = (loai: 'nv' | 'khach') => {
    const dong = dangHieuUngPixel()
    setXe(false)
    setPhieu(loai)
    setLan((n) => n + 1)
    setDangIn(dong)
    window.setTimeout(
      () => {
        setDangIn(false)
        setThongBao(loai === 'nv' ? 'Đã in phiếu đăng nhập' : 'Đã in phiếu tra cứu')
        ;(loai === 'nv' ? oTen : oMaDon).current?.focus()
      },
      dong ? 520 : 0,
    )
  }
  // Xé tờ đang hiện (nghiêng, rơi, mờ dần ~350 ms) rồi in tờ kia
  const doiPhieu = (loai: 'nv' | 'khach') => {
    if (xe || phieu === loai) return
    if (phieu === null || !dangHieuUngPixel()) return inPhieu(loai)
    setXe(true)
    window.setTimeout(() => inPhieu(loai), 350)
  }
  async function guiKhach(e: FormEvent) {
    e.preventDefault()
    if (!maDon.trim() || !/^\d{4}$/.test(soCuoi))
      return setLoiKhach('Nhập mã đơn và đúng 4 chữ số cuối số điện thoại')
    setLoiKhach('')
    setDangGui(true)
    const ma = maDon.trim()
    try {
      const kq = await traCuu(ma, soCuoi)
      setThongBao('Đã tìm thấy đơn')
      if (dangHieuUngPixel()) {
        dongDau(true, 'FOUND', 'ĐÃ TÌM THẤY')
        await cho(750)
      }
      navigate(`/tra-cuu?ma=${encodeURIComponent(ma)}&so=${soCuoi}`, { state: { kq } })
    } catch (err) {
      const khongThay = err instanceof LoiApi && err.status === 404
      setThongBao(khongThay ? 'Không tìm thấy đơn' : 'Từ chối')
      dongDau(
        false,
        khongThay ? 'NOT FOUND' : 'DENIED',
        khongThay ? 'SAI MÃ / KHÔNG CÓ ĐƠN' : 'TỪ CHỐI',
      )
      setLoiKhach(
        khongThay
          ? 'Không tìm thấy đơn. Kiểm tra lại mã đơn trên phiếu gửi hàng và 4 số cuối số điện thoại người gửi hoặc người nhận.'
          : err instanceof LoiApi && err.status !== 400
            ? err.message
            : 'Nhập mã đơn và đúng 4 chữ số cuối số điện thoại',
      )
      oMaDon.current?.focus()
    } finally {
      setDangGui(false)
    }
  }

  const [soKyTu, setSoKyTu] = useState(() => (dangHieuUng() ? 0 : CAU_GIOI_THIEU.length))
  const [tro, setTro] = useState<'an' | 'go' | 'nhay'>(() => (dangHieuUng() ? 'go' : 'an'))

  useEffect(() => {
    if (!dangHieuUng()) return
    let i = 0
    let hNhay: ReturnType<typeof setTimeout> | undefined

    const ketThucGo = () => {
      clearInterval(hGo)
      if (hNhay) clearTimeout(hNhay)
      setSoKyTu(CAU_GIOI_THIEU.length)
      setTro('an')
    }

    const hGo = setInterval(() => {
      if (document.hidden || !dangHieuUng()) {
        ketThucGo()
        return
      }
      i += 1
      if (i >= CAU_GIOI_THIEU.length) {
        clearInterval(hGo)
        setSoKyTu(CAU_GIOI_THIEU.length)
        setTro('nhay')
        // Con trỏ nháy đúng 2 lần (2 × 450 ms) rồi ẩn hẳn
        hNhay = setTimeout(() => setTro('an'), 900)
      } else {
        setSoKyTu(i)
      }
    }, 35)

    const khiAnTab = () => {
      if (document.hidden || !dangHieuUng()) ketThucGo()
    }
    document.addEventListener('visibilitychange', khiAnTab)

    return () => {
      clearInterval(hGo)
      if (hNhay) clearTimeout(hNhay)
      document.removeEventListener('visibilitychange', khiAnTab)
    }
  }, [])

  async function gui(e: FormEvent) {
    e.preventDefault()
    // Tự kiểm thay bong bóng của trình duyệt (theo ngôn ngữ trình duyệt, Edge tiếng Anh hiện tiếng Anh)
    if (!ten.trim() || !matKhau) return setLoi('Vui lòng nhập đủ tên đăng nhập và mật khẩu')
    setLoi('')
    setDangGui(true)
    try {
      const nd = await dangNhap(ten.trim(), matKhau)
      setThongBao('Đăng nhập thành công, đã duyệt')
      if (pixel && dangHieuUngPixel()) {
        dongDau(true, 'APPROVED', 'ĐÃ DUYỆT')
        await cho(750) // dấu dập ~250 ms + dừng ~500 ms rồi mới vào
      }
      onXong(nd)
    } catch (err) {
      if (pixel) {
        setThongBao('Từ chối')
        dongDau(false, 'DENIED', 'TỪ CHỐI')
      }
      // Máy chủ đã trả câu tiếng Việt (sai thông tin, bị khóa, khóa tạm); 400 là thiếu trường
      setLoi(
        err instanceof LoiApi && err.status !== 400
          ? err.message
          : 'Vui lòng nhập đủ tên đăng nhập và mật khẩu',
      )
      // Nút bị khóa lúc gửi làm mất focus; đưa về ô mật khẩu để gõ lại ngay
      oMatKhau.current?.focus()
    } finally {
      setDangGui(false)
    }
  }

  const hinh = (
    <section
      className="dn-hinh"
      style={
        {
          '--anh': `url(${phongCachDaLuu() === 'pixel' ? NEN.anh.replace('.webp', '-pixel.png') : NEN.anh})`,
        } as CSSProperties
      }
    >
      <NenHat />
      <p aria-label={CAU_GIOI_THIEU}>
        <span aria-hidden="true">
          {CAU_GIOI_THIEU.slice(0, soKyTu)}
          {tro !== 'an' && <i className={tro === 'nhay' ? 'dn-con-tro nhay' : 'dn-con-tro'} />}
        </span>
      </p>
    </section>
  )

  if (pixel) {
    return (
      <main className="dang-nhap">
        <div className="dn-khung">
          <div className="dn-px-trai">
            <div className="dn-may">
              <div className="dn-may-than">
                <span className="dn-may-nhan">
                  <i className={dangIn ? 'dn-den chay' : 'dn-den'} aria-hidden="true" />
                </span>
                {phieu === null ? (
                  <button
                    type="button"
                    className="dn-thuong-hieu dn-bam-logo"
                    onClick={() => inPhieu('nv')}
                  >
                    <LogoTK co={44} />
                    <TenThuongHieu />
                    <span className="dn-goi-y">▶ Bấm vào logo để in phiếu đăng nhập</span>
                  </button>
                ) : (
                  <div className="dn-may-logo">
                    <LogoTK co={44} />
                    <TenThuongHieu />
                  </div>
                )}
                <div className="dn-khe" aria-hidden="true" />
              </div>
              <div className="dn-giay-vung">
                {phieu && (
                  <div key={lan} className={xe ? 'dn-giay xe' : 'dn-giay'}>
                    {dau && (
                      <div
                        key={dau.id}
                        className={dau.ok ? 'dn-dau ok' : 'dn-dau'}
                        aria-hidden="true"
                      >
                        <b>{dau.chu}</b>
                        <small>{dau.phu}</small>
                      </div>
                    )}
                    {phieu === 'nv' ? (
                      <form
                        className={dau && !dau.ok ? 'dn-phieu rung' : 'dn-phieu'}
                        onSubmit={gui}
                        noValidate
                      >
                        <QrTrangTri />
                        <h1>PHIẾU ĐĂNG NHẬP NHÂN VIÊN</h1>
                        <p className="dn-phieu-ma">
                          {ma.nv} · {luc}
                        </p>
                        <hr />
                        <label>
                          Tên đăng nhập
                          <span className="dn-o">
                            <input
                              ref={oTen}
                              value={ten}
                              onChange={(e) => {
                                setTen(e.target.value)
                                setDau(null)
                              }}
                              autoComplete="username"
                              required
                            />
                          </span>
                        </label>
                        <label>
                          Mật khẩu
                          <span className="dn-o">
                            <input
                              ref={oMatKhau}
                              type="password"
                              value={matKhau}
                              onChange={(e) => {
                                setMatKhau(e.target.value)
                                setDau(null)
                              }}
                              autoComplete="current-password"
                              required
                            />
                          </span>
                        </label>
                        {loi && (
                          <p role="alert" className="loi">
                            {loi}
                          </p>
                        )}
                        <button disabled={dangGui}>
                          {dangGui ? 'Đang đăng nhập…' : 'Đăng nhập'}
                        </button>
                        <button type="button" className="dn-xe" onClick={() => doiPhieu('khach')}>
                          Khách hàng? Xé phiếu
                        </button>
                      </form>
                    ) : (
                      <form
                        className={dau && !dau.ok ? 'dn-phieu rung' : 'dn-phieu'}
                        onSubmit={guiKhach}
                        noValidate
                      >
                        <QrTrangTri />
                        <h1>PHIẾU TRA CỨU ĐƠN HÀNG</h1>
                        <p className="dn-phieu-ma">
                          {ma.khach} · {luc}
                        </p>
                        <hr />
                        <label>
                          Mã đơn
                          <span className="dn-o">
                            <input
                              ref={oMaDon}
                              value={maDon}
                              onChange={(e) => {
                                setMaDon(e.target.value)
                                setDau(null)
                              }}
                              autoCapitalize="characters"
                              autoComplete="off"
                              spellCheck={false}
                              maxLength={20}
                              required
                            />
                          </span>
                        </label>
                        <label>
                          4 số cuối điện thoại
                          <span className="dn-o">
                            <input
                              value={soCuoi}
                              onChange={(e) => {
                                setSoCuoi(e.target.value.replace(/\D/g, '').slice(0, 4))
                                setDau(null)
                              }}
                              inputMode="numeric"
                              autoComplete="off"
                              placeholder="vd 6789"
                              maxLength={4}
                              required
                            />
                          </span>
                        </label>
                        {loiKhach && (
                          <p role="alert" className="loi">
                            {loiKhach}
                          </p>
                        )}
                        <button disabled={dangGui}>{dangGui ? 'Đang tra cứu…' : 'Tra cứu'}</button>
                        <button type="button" className="dn-xe" onClick={() => doiPhieu('nv')}>
                          Nhân viên? Xé phiếu
                        </button>
                      </form>
                    )}
                  </div>
                )}
              </div>
            </div>
            <button
              type="button"
              className="dn-px-doi"
              onClick={() => doiPhieu(phieu === 'khach' ? 'nv' : 'khach')}
            >
              {phieu === 'khach' ? 'Nhân viên? In phiếu đăng nhập' : 'Khách hàng? In phiếu tra cứu'}
            </button>
            <p className="dn-chi-doc" role="status" aria-live="polite">
              {thongBao}
            </p>
          </div>
          {hinh}
        </div>
      </main>
    )
  }

  return (
    <main className="dang-nhap">
      <div className="dn-khung">
        <form onSubmit={gui} noValidate>
          <div className="dn-giua">
            <div className="dn-thuong-hieu">
              <LogoTK co={44} />
              <TenThuongHieu />
            </div>
            <div className="dn-than">
              <h1>Đăng nhập</h1>
              <label>
                Tên đăng nhập
                <span className="dn-o">
                  <input
                    ref={oTen}
                    value={ten}
                    onChange={(e) => setTen(e.target.value)}
                    autoComplete="username"
                    required
                  />
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="12" cy="8" r="4" />
                    <path d="M4 20.5c0-3.6 3.6-5.5 8-5.5s8 1.9 8 5.5" />
                  </svg>
                </span>
              </label>
              <label>
                Mật khẩu
                <span className="dn-o">
                  <input
                    ref={oMatKhau}
                    type="password"
                    value={matKhau}
                    onChange={(e) => setMatKhau(e.target.value)}
                    autoComplete="current-password"
                    required
                  />
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="5" y="10.5" width="14" height="9.5" rx="2" />
                    <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
                  </svg>
                </span>
              </label>
              {loi && (
                <p role="alert" className="loi">
                  {loi}
                </p>
              )}
              <button disabled={dangGui}>
                {dangGui ? 'Đang đăng nhập…' : 'Đăng nhập'}
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </button>
            </div>
            {/* Lối vào cho khách: đặt ngay dưới nút Đăng nhập cho khách dễ thấy, không cần đăng nhập */}
            <Link to="/tra-cuu" className="dn-tra-cuu">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="11" cy="11" r="6.5" />
                <path d="m16 16 4.5 4.5" />
              </svg>
              <span>
                <b>Khách hàng? Tra cứu đơn hàng</b>
                <small>Không cần đăng nhập: nhập mã đơn và 4 số cuối điện thoại.</small>
              </span>
              <i aria-hidden="true">→</i>
            </Link>
          </div>
        </form>

        {hinh}
      </div>
    </main>
  )
}
