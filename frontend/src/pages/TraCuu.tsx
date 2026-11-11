import { useRef, useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { LoiApi } from '../api/goi'
import { traCuu, type KetQuaTraCuu } from '../api/traCuu'
import { Nhan } from '../nhan'

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
// Chữ ngắn trên nhãn, cạnh câu đầy đủ
const TEN_NGAN: Record<string, string> = {
  CHO_GHEP: 'Tiếp nhận',
  DA_GHEP: 'Đã xếp chuyến',
  DA_LAY: 'Đang chở',
  DA_GIAO: 'Đã giao',
  THAT_BAI: 'Chờ giao lại',
  TRA_HANG: 'Hoàn trả',
  HUY: 'Đã hủy',
}
// Hình nhãn dùng chung với nhãn chuyến (nhan.tsx)
const NHAN: Record<string, string> = {
  CHO_GHEP: 'LAP',
  DA_GHEP: 'DA_CHOT',
  DA_LAY: 'DANG_CHAY',
  DA_GIAO: 'HOAN_THANH',
  THAT_BAI: 'TRE',
  TRA_HANG: 'HUY',
  HUY: 'HUY',
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
  const [so, setSo] = useState('')
  const [kq, setKq] = useState<KetQuaTraCuu | null>(null)
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  const oMa = useRef<HTMLInputElement>(null)
  const oKq = useRef<HTMLHeadingElement>(null)

  async function gui(e: FormEvent) {
    e.preventDefault()
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

  // Mốc mới nhất trên cùng; mốc đầu là trạng thái hiện tại
  const moc = kq ? [...kq.moc].reverse() : []
  return (
    <main className="tra-cuu">
      <header>
        <span className="thuong-hieu">Quản lý vận tải</span>
        <Link to="/dang-nhap">Nhân viên đăng nhập</Link>
      </header>

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

      {kq && (
        <section className="kinh tc-khung tc-kq" aria-live="polite">
          <span className="ma">Đơn {kq.ma_don}</span>
          <h2 ref={oKq} tabIndex={-1}>
            <Nhan loai={NHAN[kq.trang_thai] ?? 'LAP'}>
              {TEN_NGAN[kq.trang_thai] ?? kq.trang_thai}
            </Nhan>
            {TEN_CHO_KHACH[kq.trang_thai] ?? kq.trang_thai}
          </h2>
          <ol className="lt">
            {moc.map((m, i) => (
              <li key={`${m.trang_thai}-${m.luc}`} className={i === 0 ? 'toi' : 'xong'}>
                <i aria-hidden="true" />
                <div>
                  <strong>{TEN_CHO_KHACH[m.trang_thai] ?? m.trang_thai}</strong>
                  <small>{luc(m.luc)}</small>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}
    </main>
  )
}
