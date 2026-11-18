import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { baoSuCo, suCoChuyen, TEN_LOAI_SU_CO, type LoaiSuCo, type SuCo } from '../../api/suCo'
import { ngayGio } from '../../api/toi'
import { nenAnh } from '../../nenAnh'
import { LOI_MANG, SO_ANH_TOI_DA } from './QuetLay'
import { ThongBao } from '../../thongBao'

const thongBaoLoi = (err: unknown) => {
  const truong = Object.values(loiTheoTruong(err))
  if (truong.length) return truong.join('; ')
  return err instanceof LoiApi ? err.message : err instanceof Error ? err.message : LOI_MANG
}
const tenLoai = (loai: string) => TEN_LOAI_SU_CO[loai as LoaiSuCo] ?? loai

// UC-33: khối Sự cố trên trang chuyến của tài xế. Báo được khi đang chạy; chuyến đã về chỉ xem (quyết định 4)
export function SuCoChuyen({ chuyenId, baoDuoc }: { chuyenId: number; baoDuoc: boolean }) {
  const [ds, setDs] = useState<SuCo[] | null>(null)
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')

  const tai = useCallback(() => {
    suCoChuyen(chuyenId)
      .then(setDs)
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được sự cố'))
  }, [chuyenId])
  useEffect(tai, [tai])

  // Chuyến đã về mà chưa báo sự cố nào: không hiện khối cho gọn trang
  if (!baoDuoc && ds?.length === 0) return null

  return (
    <div className="the">
      <strong>Sự cố</strong>
      <ThongBao chu={thongBao} />
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      {ds && ds.length === 0 && <p className="ghi-chu">Chưa báo sự cố nào</p>}
      <ul className="ds-chi">
        {ds?.map((s) => (
          <li key={s.id}>
            <div className="the-dau">
              <span>
                <strong>{tenLoai(s.loai)}</strong> · {ngayGio(s.luc)}
              </span>
              <span className={s.trang_thai === 'MO' ? 'nhan do' : 'nhan xam'}>
                {s.trang_thai === 'MO' ? 'Đang mở' : 'Đã xử lý'}
              </span>
            </div>
            <div className="ghi-chu">
              {s.ghi_chu} · {s.so_anh} ảnh
            </div>
            {s.cach_xu_ly && <div>Điều phối: {s.cach_xu_ly}</div>}
          </li>
        ))}
      </ul>
      {baoDuoc && (
        <FormSuCo
          onGui={async (loai, ghiChu, anh) => {
            setThongBao('')
            setLoi('')
            try {
              await baoSuCo(chuyenId, loai, ghiChu, await Promise.all(anh.map(nenAnh)))
              setThongBao(`Đã báo sự cố ${tenLoai(loai).toLowerCase()}, Điều phối sẽ xử lý`)
              tai()
              return true
            } catch (err) {
              setLoi(thongBaoLoi(err))
              return false
            }
          }}
        />
      )}
    </div>
  )
}

function FormSuCo({
  onGui,
}: {
  onGui: (loai: LoaiSuCo, ghiChu: string, anh: File[]) => Promise<boolean>
}) {
  const [loai, setLoai] = useState<LoaiSuCo>('HONG_XE')
  const [ghiChu, setGhiChu] = useState('')
  const [anh, setAnh] = useState<File[]>([])
  const [dangGui, setDangGui] = useState(false)
  const [loi, setLoi] = useState('')

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (!ghiChu.trim()) return setLoi('Ghi rõ sự cố trước khi báo')
    if (anh.length > SO_ANH_TOI_DA) return setLoi(`Tối đa ${SO_ANH_TOI_DA} ảnh`)
    setLoi('')
    setDangGui(true)
    const xong = await onGui(loai, ghiChu.trim(), anh)
    setDangGui(false)
    if (xong) {
      setGhiChu('')
      setAnh([])
      ;(e.target as HTMLFormElement).reset()
    }
  }

  return (
    <form className="form-km" onSubmit={gui}>
      <label>
        Loại sự cố
        <select value={loai} onChange={(e) => setLoai(e.target.value as LoaiSuCo)}>
          {Object.entries(TEN_LOAI_SU_CO).map(([ma, ten]) => (
            <option key={ma} value={ma}>
              {ten}
            </option>
          ))}
        </select>
      </label>
      <label>
        Ghi chú
        <input
          value={ghiChu}
          maxLength={500}
          placeholder="Vd. Nổ lốp sau ở km 45"
          onChange={(e) => setGhiChu(e.target.value)}
        />
      </label>
      <label>
        Ảnh (không bắt buộc, tối đa {SO_ANH_TOI_DA})
        <input
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          multiple
          onChange={(e) => setAnh([...(e.target.files ?? [])])}
        />
      </label>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      <button disabled={dangGui}>{dangGui ? 'Đang gửi…' : 'Báo sự cố'}</button>
    </form>
  )
}
