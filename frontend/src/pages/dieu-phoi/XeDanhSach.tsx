import { useEffect, useState, type FormEvent, type InputHTMLAttributes } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachXe, suaXe, themXe, type Xe } from '../../api/xe'

const SO_DONG = 20
// Ngày theo giờ máy người dùng (Việt Nam), không theo UTC: 'sv-SE' cho dạng YYYY-MM-DD
const homNay = () => new Date().toLocaleDateString('sv-SE')
const ngayVN = (d: string) => d.split('-').reverse().join('/')

type Form = Record<keyof Omit<Xe, 'id' | 'trang_thai'>, string>
const FORM_TRONG: Form = {
  bien_so: '',
  tai_trong_kg: '',
  the_tich_m3: '',
  ktt_toan_bo_kg: '',
  han_dang_kiem: '',
  han_bao_hiem: '',
  dinh_muc_lit_100km: '',
  km_dong_ho: '0',
}
const NHAN: Record<keyof Form, string> = {
  bien_so: 'Biển số',
  tai_trong_kg: 'Tải trọng chở hàng (kg)',
  the_tich_m3: 'Thể tích thùng (m³)',
  ktt_toan_bo_kg: 'Khối lượng toàn bộ theo thiết kế (kg)',
  han_dang_kiem: 'Hạn đăng kiểm',
  han_bao_hiem: 'Hạn bảo hiểm TNDS',
  dinh_muc_lit_100km: 'Định mức dầu (lít/100 km)',
  km_dong_ho: 'Km đồng hồ hiện tại',
}

export default function XeDanhSach() {
  const [tim, setTim] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: Xe[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<Xe | 'moi' | null>(null)
  const [lanTai, setLanTai] = useState(0) // tăng lên để tải lại sau khi thêm/sửa
  const tai = () => setLanTai((n) => n + 1)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn (gõ tìm nhanh, mạng chậm) thì bỏ, không ghi đè kết quả mới
    danhSachXe({ tim, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách xe')
      })
    return () => {
      bo = true
    }
  }, [tim, trangThai, trang, lanTai])

  async function doiTrangThai(xe: Xe) {
    try {
      await suaXe(xe.id, { trang_thai: xe.trang_thai === 'HOAT_DONG' ? 'NGUNG' : 'HOAT_DONG' })
      tai()
    } catch (e) {
      setLoiTai(e instanceof LoiApi ? e.message : 'Không đổi được trạng thái')
    }
  }

  const soTrang = Math.max(1, Math.ceil(ds.tong / SO_DONG))
  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Xe</h1>
        <input
          placeholder="Tìm biển số"
          aria-label="Tìm biển số"
          value={tim}
          onChange={(e) => {
            setTim(e.target.value)
            setTrang(1)
          }}
        />
        <select
          aria-label="Lọc trạng thái"
          value={trangThai}
          onChange={(e) => {
            setTrangThai(e.target.value)
            setTrang(1)
          }}
        >
          <option value="">Mọi trạng thái</option>
          <option value="HOAT_DONG">Hoạt động</option>
          <option value="NGUNG">Ngừng</option>
        </select>
        <button onClick={() => setDangSua('moi')}>Thêm xe</button>
      </div>

      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Biển số</th>
            <th className="so">Tải trọng (kg)</th>
            <th className="so">Thể tích (m³)</th>
            <th>Hạn đăng kiểm</th>
            <th>Hạn bảo hiểm</th>
            <th>Trạng thái</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((xe) => (
            <tr key={xe.id} className={xe.trang_thai === 'NGUNG' ? 'mo' : undefined}>
              <td className="bien-so">{xe.bien_so}</td>
              <td className="so">{xe.tai_trong_kg.toLocaleString('vi-VN')}</td>
              <td className="so">{Number(xe.the_tich_m3).toLocaleString('vi-VN')}</td>
              {[xe.han_dang_kiem, xe.han_bao_hiem].map((han, i) => (
                <td key={i} className={han < homNay() ? 'het-han' : undefined}>
                  {ngayVN(han)}
                  {han < homNay() && ' (hết hạn)'}
                </td>
              ))}
              <td>{xe.trang_thai === 'HOAT_DONG' ? 'Hoạt động' : 'Ngừng'}</td>
              <td className="hanh-dong">
                <button className="phu" onClick={() => setDangSua(xe)}>
                  Sửa
                </button>
                <button className="phu" onClick={() => doiTrangThai(xe)}>
                  {xe.trang_thai === 'HOAT_DONG' ? 'Ngừng' : 'Hoạt động lại'}
                </button>
              </td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={7} className="trong">
                Chưa có xe nào phù hợp
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="phan-trang">
        <button className="phu" disabled={trang <= 1} onClick={() => setTrang(trang - 1)}>
          Trước
        </button>
        <span>
          Trang {trang}/{soTrang} · {ds.tong} xe
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {dangSua && (
        <FormXe
          xe={dangSua === 'moi' ? null : dangSua}
          onDong={() => setDangSua(null)}
          onLuu={() => {
            setDangSua(null)
            tai()
          }}
        />
      )}
    </section>
  )
}

function FormXe({ xe, onDong, onLuu }: { xe: Xe | null; onDong: () => void; onLuu: () => void }) {
  const [f, setF] = useState<Form>(
    xe
      ? (Object.fromEntries(
          Object.keys(FORM_TRONG).map((k) => [k, String(xe[k as keyof Form] ?? '')]),
        ) as Form)
      : FORM_TRONG,
  )
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung('')
    setDangGui(true)
    const vao = {
      bien_so: f.bien_so,
      tai_trong_kg: Number(f.tai_trong_kg),
      the_tich_m3: f.the_tich_m3,
      ktt_toan_bo_kg: Number(f.ktt_toan_bo_kg),
      han_dang_kiem: f.han_dang_kiem,
      han_bao_hiem: f.han_bao_hiem,
      dinh_muc_lit_100km: f.dinh_muc_lit_100km || null,
    }
    try {
      // Km đồng hồ chỉ nhập lúc tạo; sau đó đổi qua bắt đầu/kết thúc chuyến (BR-70)
      if (xe) await suaXe(xe.id, vao)
      else await themXe({ ...vao, km_dong_ho: Number(f.km_dong_ho) })
      onLuu()
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      // Lỗi nghiệp vụ gắn được vào một ô thì hiện ngay dưới ô đó
      const oCuaMa: Record<string, keyof Form> = {
        BIEN_SO_TRUNG: 'bien_so',
        'BR-14': 'ktt_toan_bo_kg',
      }
      if (err instanceof LoiApi && oCuaMa[err.ma]) theoTruong[oCuaMa[err.ma]] = err.message
      setLoiTruong(theoTruong)
      if (Object.keys(theoTruong).length === 0)
        setLoiChung(err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')
    } finally {
      setDangGui(false)
    }
  }

  const o = (k: keyof Form, props: InputHTMLAttributes<HTMLInputElement>) => (
    <label key={k}>
      {NHAN[k]}
      <input
        value={f[k]}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
        aria-invalid={!!loiTruong[k]}
        {...props}
      />
      {loiTruong[k] && <span className="loi">{loiTruong[k]}</span>}
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>{xe ? `Sửa xe ${xe.bien_so}` : 'Thêm xe'}</h2>
        {o('bien_so', { required: true, maxLength: 20 })}
        <div className="hai-cot">
          {o('tai_trong_kg', { type: 'number', required: true, min: 1 })}
          {o('ktt_toan_bo_kg', { type: 'number', required: true, min: 1 })}
          {o('the_tich_m3', { type: 'number', required: true, min: 0.01, step: 0.01 })}
          {o('dinh_muc_lit_100km', { type: 'number', min: 0, step: 0.01 })}
          {o('han_dang_kiem', { type: 'date', required: true })}
          {o('han_bao_hiem', { type: 'date', required: true })}
        </div>
        {xe ? (
          <p className="ghi-chu">
            Km đồng hồ: {xe.km_dong_ho.toLocaleString('vi-VN')} (chỉ đổi qua bắt đầu/kết thúc
            chuyến)
          </p>
        ) : (
          o('km_dong_ho', { type: 'number', required: true, min: 0 })
        )}
        {loiChung && (
          <p role="alert" className="loi">
            {loiChung}
          </p>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            Hủy
          </button>
          <button disabled={dangGui}>{dangGui ? 'Đang lưu…' : 'Lưu'}</button>
        </div>
      </form>
    </div>
  )
}
