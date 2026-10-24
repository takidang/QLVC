import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachNut, suaNut, themNut, type Nut } from '../../api/tuyen'

const SO_DONG = 50

export default function NutDanhSach() {
  const [tim, setTim] = useState('')
  const [ds, setDs] = useState<{ du_lieu: Nut[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<Nut | 'moi' | null>(null)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachNut({ tim, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách nút')
      })
    return () => {
      bo = true
    }
  }, [tim, lanTai])

  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Nút (tỉnh, kho)</h1>
        <input
          placeholder="Tìm tên hoặc tỉnh"
          aria-label="Tìm tên hoặc tỉnh"
          value={tim}
          onChange={(e) => setTim(e.target.value)}
        />
        <button onClick={() => setDangSua('moi')}>Thêm nút</button>
      </div>
      <p className="ghi-chu">
        Tỉnh của nút dùng để tra bảng giá: gõ đúng tên tỉnh như trong Bảng giá.
      </p>
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}
      <table>
        <thead>
          <tr>
            <th>Tên</th>
            <th>Tỉnh</th>
            <th>Loại</th>
            <th>Tọa độ</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((n) => (
            <tr key={n.id}>
              <td className="bien-so">{n.ten}</td>
              <td>{n.tinh}</td>
              <td>{n.loai === 'KHO' ? 'Kho' : 'Tỉnh/thành'}</td>
              <td className="ghi-chu">{n.lat && n.lng ? `${n.lat}, ${n.lng}` : '—'}</td>
              <td className="hanh-dong">
                <button className="phu" onClick={() => setDangSua(n)}>
                  Sửa
                </button>
              </td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={5} className="trong">
                Chưa có nút nào
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {ds.tong > SO_DONG && (
        <p className="ghi-chu">
          Đang hiện {SO_DONG}/{ds.tong} nút, gõ ô tìm để lọc.
        </p>
      )}

      {dangSua && (
        <FormNut
          nut={dangSua === 'moi' ? null : dangSua}
          onDong={() => setDangSua(null)}
          onLuu={() => {
            setDangSua(null)
            setLanTai((n) => n + 1)
          }}
        />
      )}
    </section>
  )
}

function FormNut({
  nut,
  onDong,
  onLuu,
}: {
  nut: Nut | null
  onDong: () => void
  onLuu: () => void
}) {
  const [f, setF] = useState({
    ten: nut?.ten ?? '',
    tinh: nut?.tinh ?? '',
    loai: nut?.loai ?? ('TINH' as Nut['loai']),
    lat: nut?.lat ?? '',
    lng: nut?.lng ?? '',
  })
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState('')

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung('')
    const vao = { ...f, lat: f.lat || null, lng: f.lng || null }
    try {
      if (nut) await suaNut(nut.id, vao)
      else await themNut(vao)
      onLuu()
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      setLoiTruong(theoTruong)
      if (Object.keys(theoTruong).length === 0)
        setLoiChung(err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')
    }
  }

  const o = (k: 'ten' | 'tinh' | 'lat' | 'lng', nhan: string, required = false) => (
    <label>
      {nhan}
      <input
        value={f[k]}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
        required={required}
        aria-invalid={!!loiTruong[k]}
      />
      {loiTruong[k] && <span className="loi">{loiTruong[k]}</span>}
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>{nut ? `Sửa nút ${nut.ten}` : 'Thêm nút'}</h2>
        <div className="hai-cot">
          {o('ten', 'Tên nút', true)}
          {o('tinh', 'Tỉnh (tra bảng giá)', true)}
          <label>
            Loại
            <select
              value={f.loai}
              onChange={(e) => setF({ ...f, loai: e.target.value as Nut['loai'] })}
            >
              <option value="TINH">Tỉnh/thành</option>
              <option value="KHO">Kho</option>
            </select>
          </label>
          <span />
          {o('lat', 'Vĩ độ (không bắt buộc)')}
          {o('lng', 'Kinh độ (không bắt buộc)')}
        </div>
        {loiChung && (
          <p role="alert" className="loi">
            {loiChung}
          </p>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            Hủy
          </button>
          <button>Lưu</button>
        </div>
      </form>
    </div>
  )
}
