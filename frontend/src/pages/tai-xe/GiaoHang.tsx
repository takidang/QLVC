import { useEffect, useRef, useState, type FormEvent, type PointerEvent } from 'react'
import { LoiApi } from '../../api/goi'
import { layGps, quetMa, type KetQuaQuet } from '../../api/toi'
import { nenAnh } from '../../nenAnh'
import { Camera, LOI_MANG, SO_ANH_TOI_DA } from './QuetLay'

const chuan = (ma: string) => ma.trim().toUpperCase()

// UC-20 luồng chính: quét QR xác nhận đúng kiện của điểm giao → ảnh, tên người nhận, chữ ký (BR-41) → DA_GIAO
export function GiaoHang({ maDon, onXong }: { maDon: string; onXong: (kq: KetQuaQuet) => void }) {
  const [mo, setMo] = useState(false)
  const [moCamera, setMoCamera] = useState(false)
  const [maGo, setMaGo] = useState('')
  const [khop, setKhop] = useState(false)
  const [anh, setAnh] = useState<File[]>([])
  const [ten, setTen] = useState('')
  const [oKy, setOKy] = useState<HTMLCanvasElement | null>(null) // null: chưa ký
  const [dangGui, setDangGui] = useState(false)
  const [loi, setLoi] = useState('')

  // Quyết định 2: mã quét / gõ phải là đơn của điểm này; sai thì báo ngay, chưa gửi gì lên máy chủ
  function xacNhan(ma: string) {
    setMoCamera(false)
    if (chuan(ma) === maDon) {
      setKhop(true)
      setLoi('')
    } else setLoi(`Mã ${chuan(ma) || '(trống)'} không khớp đơn của điểm này (${maDon})`)
  }

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (!khop || !anh.length || !ten.trim() || !oKy)
      return setLoi('Cần quét đúng mã, chụp ảnh, nhập tên người nhận và người nhận ký (BR-41)')
    if (anh.length > SO_ANH_TOI_DA) return setLoi(`Tối đa ${SO_ANH_TOI_DA} ảnh`)
    const gps = layGps() // xin vị trí ngay lúc bấm Xác nhận giao (Safari chỉ hỏi khi có thao tác)
    // Hỏi lại sau khi đã xin vị trí: nút sáng từ nét ký đầu tiên, dễ chạm nhầm
    if (!window.confirm(`Xác nhận đã giao đơn ${maDon} cho ${ten.trim()}?`)) return
    setLoi('')
    setDangGui(true)
    try {
      const daNen = await Promise.all(anh.map(nenAnh))
      const chuKy = await new Promise<Blob | null>((xong) => oKy!.toBlob(xong, 'image/png'))
      if (!chuKy) throw new Error('Không đọc được chữ ký, vui lòng ký lại')
      onXong(
        await quetMa({
          ma_don: maDon,
          loai: 'GIAO',
          gps: await gps,
          anh: daNen,
          chu_ky: chuKy,
          ten_nguoi_nhan: ten.trim(),
        }),
      )
    } catch (err) {
      setLoi(err instanceof LoiApi ? err.message : err instanceof Error ? err.message : LOI_MANG)
    } finally {
      setDangGui(false)
    }
  }

  if (!mo)
    return (
      <button type="button" onClick={() => setMo(true)}>
        Giao hàng
      </button>
    )
  return (
    <form className="form-km giao-hang" onSubmit={gui}>
      <strong>Giao {maDon}</strong>
      {khop ? (
        <p className="thanh-cong">Đã xác nhận đúng kiện {maDon}</p>
      ) : moCamera ? (
        <Camera
          onDoc={xacNhan}
          onLoi={(t) => (setMoCamera(false), setLoi(t))}
          onDong={() => setMoCamera(false)}
        />
      ) : (
        <>
          <button type="button" onClick={() => setMoCamera(true)}>
            Quét mã QR trên kiện
          </button>
          <label>
            Hoặc gõ mã đơn
            <input
              value={maGo}
              maxLength={50}
              autoCapitalize="characters"
              placeholder="DH-…"
              onChange={(e) => setMaGo(e.target.value)}
            />
          </label>
          <button
            type="button"
            className="phu"
            disabled={!maGo.trim()}
            onClick={() => xacNhan(maGo)}
          >
            Xác nhận mã
          </button>
        </>
      )}
      <label>
        Ảnh giao hàng (tối đa {SO_ANH_TOI_DA})
        <input
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          multiple
          onChange={(e) => setAnh([...(e.target.files ?? [])])}
        />
      </label>
      <label>
        Tên người nhận
        <input value={ten} maxLength={100} onChange={(e) => setTen(e.target.value)} />
      </label>
      <KyTen onKy={setOKy} />
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      <div className="hanh-dong">
        <button type="button" className="phu" disabled={dangGui} onClick={() => setMo(false)}>
          Thôi
        </button>
        <button disabled={dangGui || !khop || !anh.length || !ten.trim() || !oKy}>
          {dangGui ? 'Đang gửi…' : 'Xác nhận giao'}
        </button>
      </div>
    </form>
  )
}

// Ô ký bằng ngón tay: canvas có sẵn của trình duyệt, xuất PNG khi gửi (UC-20 quyết định 4, không thêm thư viện).
// Báo lên form canvas đã có nét ký, hoặc null khi xóa
function KyTen({ onKy }: { onKy: (oKy: HTMLCanvasElement | null) => void }) {
  const oKy = useRef<HTMLCanvasElement>(null)
  const dangVe = useRef(false)

  useEffect(() => {
    const cv = oKy.current!
    const tyLe = window.devicePixelRatio || 1 // nét mịn trên màn hình điện thoại
    cv.width = cv.clientWidth * tyLe
    cv.height = cv.clientHeight * tyLe
    const g = cv.getContext('2d')!
    g.scale(tyLe, tyLe)
    g.lineWidth = 2.5
    g.lineCap = g.lineJoin = 'round'
    g.fillStyle = '#fff'
    g.fillRect(0, 0, cv.clientWidth, cv.clientHeight)
  }, [])

  const diem = (e: PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    return [e.clientX - r.left, e.clientY - r.top] as const
  }

  function xoa() {
    const cv = oKy.current!
    cv.getContext('2d')!.fillRect(0, 0, cv.clientWidth, cv.clientHeight)
    onKy(null)
  }

  return (
    <div className="o-ky">
      <span>Người nhận ký tên</span>
      <canvas
        ref={oKy}
        aria-label="Ô ký tên người nhận"
        onPointerDown={(e) => {
          e.currentTarget.setPointerCapture(e.pointerId)
          dangVe.current = true
          const g = e.currentTarget.getContext('2d')!
          g.beginPath()
          g.moveTo(...diem(e))
        }}
        onPointerMove={(e) => {
          if (!dangVe.current) return
          const g = e.currentTarget.getContext('2d')!
          g.lineTo(...diem(e))
          g.stroke()
          onKy(e.currentTarget)
        }}
        onPointerUp={() => (dangVe.current = false)}
        onPointerCancel={() => (dangVe.current = false)}
      />
      <button type="button" className="phu" onClick={xoa}>
        Xóa chữ ký
      </button>
    </div>
  )
}
