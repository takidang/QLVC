import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'
import { DauDanhMuc, OTim } from '../danh-muc'
import { danhSachNut, suaNut, themNut, type Nut } from '../../api/tuyen'

const SO_DONG = 50

export default function NutDanhSach() {
  const [tim, setTim] = useState('')
  const [ds, setDs] = useState<{ du_lieu: Nut[]; tong: number } | null>(null) // null = đang tải
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

  const duLieu = ds?.du_lieu ?? []
  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Nút"
        phu="Tỉnh, thành và kho trên các tuyến. Tỉnh của nút dùng để tra bảng giá: gõ đúng tên tỉnh như trong Bảng giá."
        nut="Thêm nút"
        onNut={() => setDangSua('moi')}
      />
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}
      <div className="kinh bang-khung dm">
        <div className="cong-cu">
          <span className="ghi-chu">{ds ? `${duLieu.length} nút` : '–'}</span>
          <OTim giaTri={tim} goiY="Tìm tên hoặc tỉnh" onDoi={setTim} />
        </div>
        <table>
          <thead>
            <tr>
              <th>Tên</th>
              <th>Tỉnh</th>
              <th>Loại</th>
              <th>Tọa độ</th>
              <th>
                <span className="an-chu">Thao tác</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {duLieu.map((n) => (
              <tr key={n.id}>
                <td className="tuyen">{n.ten}</td>
                <td>{n.tinh}</td>
                <td>
                  <span className="bien">{n.loai === 'KHO' ? 'Kho' : 'Tỉnh/thành'}</span>
                </td>
                <td className="ma">{n.lat && n.lng ? `${n.lat}, ${n.lng}` : 'Chưa có tọa độ'}</td>
                <td className="hanh-dong so">
                  <button className="phu" onClick={() => setDangSua(n)}>
                    Sửa
                  </button>
                </td>
              </tr>
            ))}
            {duLieu.length === 0 && (ds || !loiTai) && (
              <tr>
                <td colSpan={5} className="trong">
                  {ds ? (
                    'Chưa có nút nào'
                  ) : phongCachDaLuu() === 'pixel' ? (
                    /* Hiệu ứng Pixel: màn tải bảng kiểu Pixel thay chữ Đang tải… */
                    <DangTaiPixel kieu="bang" soCot={5} />
                  ) : (
                    'Đang tải…'
                  )}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {ds && ds.tong > SO_DONG && (
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
