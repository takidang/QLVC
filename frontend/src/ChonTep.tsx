import { useEffect, useId, useRef, useState, type InputHTMLAttributes, type ReactNode } from 'react'

// Ô chọn file chữ tiếng Việt: ô <input type="file"> thật vẫn nằm đó (trong suốt, phủ lên hàng nút)
// nên bấm, Tab, Enter / Space, `required` của trình duyệt vẫn chạy như cũ; chỉ thay chữ
// "Choose Files / No file chosen" theo ngôn ngữ trình duyệt bằng nút và dòng trạng thái tiếng Việt.
type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'className' | 'children'> & {
  nhan?: ReactNode // chữ nhãn phía trên (vd. "Ảnh hóa đơn (tối đa 5)")
  nut?: ReactNode // chữ trên nút, mặc định "Chọn ảnh"
  chinh?: boolean // nút kiểu chính (nền mực) thay vì nút phụ
  hienTrangThai?: boolean // dòng "Chưa chọn ảnh / Đã chọn N ảnh / tên file"
}

export default function ChonTep({
  nhan,
  nut = 'Chọn ảnh',
  chinh = false,
  hienTrangThai = true,
  onChange,
  ...input
}: Props) {
  const o = useRef<HTMLInputElement>(null)
  const idTt = useId()
  const [tep, setTep] = useState<string[]>([])

  // Form gọi reset() sau khi gửi xong thì ô file trống lại: dòng trạng thái cũng về "Chưa chọn"
  useEffect(() => {
    const form = o.current?.form
    if (!form) return
    const veRong = () => setTep([])
    form.addEventListener('reset', veRong)
    return () => form.removeEventListener('reset', veRong)
  }, [])

  const trangThai =
    tep.length === 0 ? 'Chưa chọn ảnh' : tep.length === 1 ? tep[0] : `Đã chọn ${tep.length} ảnh`

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
            setTep([...(e.target.files ?? [])].map((f) => f.name))
            onChange?.(e)
          }}
        />
        <span className={chinh ? 'chon-tep-nut chinh' : 'chon-tep-nut'} aria-hidden="true">
          {nut}
        </span>
        {hienTrangThai && (
          <span id={idTt} className="chon-tep-tt" aria-hidden="true">
            {trangThai}
          </span>
        )}
      </span>
    </label>
  )
}
