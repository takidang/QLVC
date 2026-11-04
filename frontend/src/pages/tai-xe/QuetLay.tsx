import QrScanner from 'qr-scanner'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { LoiApi } from '../../api/goi'
import { layGps, lyDo, quetMa, type KetQuaQuet, type LyDo } from '../../api/toi'
import { nenAnh } from '../../nenAnh'

const LOI_MANG = 'Không gửi được, kiểm tra mạng rồi thử lại'
// UC-19 luồng chính: camera đọc QR trên phiếu (qr-scanner); luồng 2a: gõ mã đơn. Cả hai gửi cùng một API
export function QuetLay({ onXong }: { onXong: (kq: KetQuaQuet) => void }) {
  const [ma, setMa] = useState('')
  const [moCamera, setMoCamera] = useState(false)
  const [dangGui, setDangGui] = useState(false)
  const [loi, setLoi] = useState('')

  async function gui(maDon: string) {
    setLoi('')
    setDangGui(true)
    try {
      onXong(await quetMa({ ma_don: maDon, loai: 'LAY', gps: await layGps() }))
      setMa('')
    } catch (e) {
      setLoi(e instanceof LoiApi ? e.message : LOI_MANG)
    } finally {
      setDangGui(false)
    }
  }

  return (
    <div className="the form-km">
      <strong>Lấy hàng</strong>
      {moCamera ? (
        <Camera
          onDoc={(m) => {
            setMoCamera(false)
            gui(m)
          }}
          onLoi={(t) => {
            setMoCamera(false)
            setLoi(t)
          }}
          onDong={() => setMoCamera(false)}
        />
      ) : (
        <button type="button" disabled={dangGui} onClick={() => setMoCamera(true)}>
          Quét mã QR
        </button>
      )}
      <form
        className="form-km"
        onSubmit={(e) => {
          e.preventDefault()
          gui(ma)
        }}
      >
        <label>
          Hoặc gõ mã đơn
          <input
            value={ma}
            maxLength={50}
            autoCapitalize="characters"
            placeholder="DH-…"
            onChange={(e) => setMa(e.target.value)}
          />
        </label>
        <button className="phu" disabled={dangGui || !ma.trim()}>
          {dangGui ? 'Đang gửi…' : 'Lấy hàng'}
        </button>
      </form>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
    </div>
  )
}

function Camera(p: {
  onDoc: (ma: string) => void
  onLoi: (t: string) => void
  onDong: () => void
}) {
  const video = useRef<HTMLVideoElement>(null)
  const goiLai = useRef(p)
  useEffect(() => {
    goiLai.current = p
  })

  useEffect(() => {
    let daDoc = false // một lần đọc là đủ: camera còn chạy thêm vài khung hình trước khi tắt
    const may = new QrScanner(
      video.current!,
      (r) => {
        if (daDoc) return
        daDoc = true
        goiLai.current.onDoc(r.data.trim())
      },
      { returnDetailedScanResult: true, highlightScanRegion: true, preferredCamera: 'environment' },
    )
    may
      .start()
      .catch(() =>
        goiLai.current.onLoi(
          'Không mở được camera (chưa cho phép, hoặc trang không chạy HTTPS). Gõ mã đơn bên dưới.',
        ),
      )
    return () => may.destroy()
  }, [])

  return (
    <div className="camera">
      <video ref={video} muted playsInline />
      <button type="button" className="phu" onClick={p.onDong}>
        Tắt camera
      </button>
    </div>
  )
}

// UC-19 luồng 1b: không lấy được – chọn lý do trong danh mục + chụp ít nhất 1 ảnh (BR-42) → đơn THAT_BAI
export function KhongLay({ maDon, onXong }: { maDon: string; onXong: (kq: KetQuaQuet) => void }) {
  const [mo, setMo] = useState(false)
  const [dsLyDo, setDsLyDo] = useState<LyDo[]>([])
  const [lyDoId, setLyDoId] = useState('')
  const [anh, setAnh] = useState<File[]>([])
  const [dangGui, setDangGui] = useState(false)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    if (!mo || dsLyDo.length) return
    lyDo('LAY')
      .then(setDsLyDo)
      .catch(() => setLoi('Không tải được danh mục lý do'))
  }, [mo, dsLyDo.length])

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (!lyDoId || !anh.length) return setLoi('Chọn lý do và chụp ít nhất 1 ảnh (BR-42)')
    setLoi('')
    setDangGui(true)
    try {
      const daNen = await Promise.all(anh.map(nenAnh))
      onXong(
        await quetMa({
          ma_don: maDon,
          loai: 'KHONG_LAY',
          gps: await layGps(),
          anh: daNen,
          ly_do_id: Number(lyDoId),
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
      <button type="button" className="phu" onClick={() => setMo(true)}>
        Không lấy được
      </button>
    )
  return (
    <form className="form-km" onSubmit={gui}>
      <label>
        Lý do không lấy được {maDon}
        <select required value={lyDoId} onChange={(e) => setLyDoId(e.target.value)}>
          <option value="">– Chọn lý do –</option>
          {dsLyDo.map((x) => (
            <option key={x.id} value={x.id}>
              {x.ten}
            </option>
          ))}
        </select>
      </label>
      <label>
        Ảnh hiện trường
        <input
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          multiple
          required
          onChange={(e) => setAnh([...(e.target.files ?? [])])}
        />
      </label>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      <div className="hanh-dong">
        <button type="button" className="phu" disabled={dangGui} onClick={() => setMo(false)}>
          Thôi
        </button>
        <button disabled={dangGui}>{dangGui ? 'Đang gửi…' : 'Báo không lấy được'}</button>
      </div>
    </form>
  )
}
