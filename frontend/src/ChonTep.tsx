import { useEffect, useId, useRef, useState, type InputHTMLAttributes, type ReactNode } from 'react'
import { PhanHoiChonTepPixel } from './HieuUngPixel'
import { dangHieuUngPixel } from './nen'

// Ô chọn file chữ tiếng Việt: ô <input type="file"> thật vẫn nằm đó (trong suốt, phủ lên hàng nút)
// nên bấm, Tab, Enter / Space, `required` của trình duyệt vẫn chạy như cũ; chỉ thay chữ
// "Choose Files / No file chosen" theo ngôn ngữ trình duyệt bằng nút và dòng trạng thái tiếng Việt.
type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'className' | 'children'> & {
  nhan?: ReactNode // chữ nhãn phía trên (vd. "Ảnh hóa đơn (tối đa 5)")
  nut?: ReactNode // chữ trên nút, mặc định "Chọn ảnh"
  chinh?: boolean // nút kiểu chính (nền mực) thay vì nút phụ
  hienTrangThai?: boolean // dòng "Chưa chọn ảnh / Đã chọn N ảnh / tên file"
  dangNen?: boolean // Hiệu ứng Pixel: bật thanh nấc khi trang cha đang nén ảnh gửi lên
}

export default function ChonTep({
  nhan,
  nut = 'Chọn ảnh',
  chinh = false,
  hienTrangThai = true,
  dangNen = false,
  onChange,
  ...input
}: Props) {
  const o = useRef<HTMLInputElement>(null)
  const idTt = useId()
  const [tep, setTep] = useState<string[]>([])
  // Hiệu ứng Pixel: trạng thái "nhai" ảnh theo bậc & thanh nấc nén ảnh (chỉ trang trí, tự gỡ ≤ 1,2 s)
  const [lanChon, setLanChon] = useState(0)
  const [hienPhanHoi, setHienPhanHoi] = useState(false)
  const [cheDoNen, setCheDoNen] = useState(false)

  // Form gọi reset() sau khi gửi xong thì ô file trống lại: dòng trạng thái cũng về "Chưa chọn"
  useEffect(() => {
    const form = o.current?.form
    if (!form) return
    const veRong = () => {
      setTep([])
      setHienPhanHoi(false)
      setCheDoNen(false)
    }
    form.addEventListener('reset', veRong)
    return () => form.removeEventListener('reset', veRong)
  }, [])

  useEffect(() => {
    if (!hienPhanHoi) return
    const t = window.setTimeout(() => {
      setHienPhanHoi(false)
      setCheDoNen(false)
    }, 1200)
    return () => window.clearTimeout(t)
  }, [hienPhanHoi, lanChon])

  useEffect(() => {
    if (dangNen && dangHieuUngPixel()) {
      setCheDoNen(true)
      setLanChon((n) => n + 1)
      setHienPhanHoi(true)
    } else if (!dangNen) {
      setCheDoNen(false)
    }
  }, [dangNen])

  const trangThai =
    tep.length === 0 ? 'Chưa chọn ảnh' : tep.length === 1 ? tep[0] : `Đã chọn ${tep.length} ảnh`
  const huPixel = dangHieuUngPixel()

  return (
    <label className="chon-tep">
      {nhan && <span className="chon-tep-nhan">{nhan}</span>}
      <span className="chon-tep-hang">
        <input
          {...input}
          ref={o}
          type="file"
          className="chon-tep-o"
          aria-describedby={hienTrangThai ? idTt : undefined}
          onChange={(e) => {
            const ds = [...(e.target.files ?? [])]
            setTep(ds.map((f) => f.name))
            // Hiệu ứng Pixel: ô tệp "nhai" ảnh theo bậc & thanh nấc ngắn ngay khi chọn tệp
            if (ds.length > 0 && dangHieuUngPixel()) {
              setCheDoNen(false)
              setLanChon((n) => n + 1)
              setHienPhanHoi(true)
            } else {
              setHienPhanHoi(false)
            }
            onChange?.(e)
          }}
        />
        <span
          className={`${chinh ? 'chon-tep-nut chinh' : 'chon-tep-nut'}${huPixel && hienPhanHoi ? ' px-tep-nhai' : ''}`}
          aria-hidden="true"
        >
          {nut}
        </span>
        {hienTrangThai && (
          <span id={idTt} className="chon-tep-tt" aria-hidden="true">
            {trangThai}
          </span>
        )}
      </span>
      {/* Hiệu ứng Pixel: ô tệp "nhai" ảnh theo bậc & thanh nấc nén ảnh (tự gỡ ≤ 1,2 s) */}
      {huPixel && hienPhanHoi && (
        <PhanHoiChonTepPixel key={lanChon} soTep={tep.length} dangNen={cheDoNen} />
      )}
    </label>
  )
}
