import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachKhachHang, suaKhachHang, themKhachHang, type KhachHang } from '../../api/khachHang'

const SO_DONG = 20
type Form = { ten: string; sdt: string; dia_chi: string; ma_so_thue: string }

export default function KhachHangDanhSach() {
  const [tim, setTim] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: KhachHang[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<KhachHang | 'moi' | null>(null)
  const [lanTai, setLanTai] = useState(0) // tăng lên để tải lại sau khi thêm/sửa
  const tai = () => setLanTai((n) => n + 1)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ, không ghi đè kết quả mới
    danhSachKhachHang({ tim, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách khách hàng')
      })
    return () => {
      bo = true
    }
  }, [tim, trangThai, trang, lanTai])

  async function doiTrangThai(kh: KhachHang) {
    try {
      await suaKhachHang(kh.id, {
        trang_thai: kh.trang_thai === 'HOAT_DONG' ? 'NGUNG' : 'HOAT_DONG',
      })
      tai()
    } catch (e) {
      setLoiTai(e instanceof LoiApi ? e.message : 'Không đổi được trạng thái')
    }
  }

  const soTrang = Math.max(1, Math.ceil(ds.tong / SO_DONG))
  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Khách hàng</h1>
        <input
          placeholder="Tìm tên hoặc SĐT"
          aria-label="Tìm tên hoặc số điện thoại"
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
        <button onClick={() => setDangSua('moi')}>Thêm khách hàng</button>
      </div>

      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Tên</th>
            <th>SĐT</th>
            <th>Địa chỉ</th>
            <th>Mã số thuế</th>
            <th>Trạng thái</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((kh) => (
            <tr key={kh.id} className={kh.trang_thai === 'NGUNG' ? 'mo' : undefined}>
              <td className="bien-so">{kh.ten}</td>
              <td>{kh.sdt}</td>
              <td>{kh.dia_chi}</td>
              <td>{kh.ma_so_thue}</td>
              <td>{kh.trang_thai === 'HOAT_DONG' ? 'Hoạt động' : 'Ngừng'}</td>
              <td className="hanh-dong">
                <button className="phu" onClick={() => setDangSua(kh)}>
                  Sửa
                </button>
                <button className="phu" onClick={() => doiTrangThai(kh)}>
                  {kh.trang_thai === 'HOAT_DONG' ? 'Ngừng' : 'Hoạt động lại'}
                </button>
              </td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={6} className="trong">
                Chưa có khách hàng nào phù hợp
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
          Trang {trang}/{soTrang} · {ds.tong} khách
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {dangSua && (
        <FormKhachHang
          kh={dangSua === 'moi' ? null : dangSua}
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

function FormKhachHang({
  kh,
  onDong,
  onLuu,
}: {
  kh: KhachHang | null
  onDong: () => void
  onLuu: () => void
}) {
  const [f, setF] = useState<Form>({
    ten: kh?.ten ?? '',
    sdt: kh?.sdt ?? '',
    dia_chi: kh?.dia_chi ?? '',
    ma_so_thue: kh?.ma_so_thue ?? '',
  })
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung('')
    setDangGui(true)
    // Ô không bắt buộc để trống thì gửi null (xóa giá trị cũ)
    const vao = { ...f, dia_chi: f.dia_chi.trim() || null, ma_so_thue: f.ma_so_thue.trim() || null }
    try {
      if (kh) await suaKhachHang(kh.id, vao)
      else await themKhachHang(vao)
      onLuu()
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      setLoiTruong(theoTruong)
      if (Object.keys(theoTruong).length === 0)
        setLoiChung(err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')
    } finally {
      setDangGui(false)
    }
  }

  const o = (k: keyof Form, nhan: string, required = false, goiY?: string) => (
    <label>
      {nhan}
      <input
        value={f[k]}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
        required={required}
        placeholder={goiY}
        aria-invalid={!!loiTruong[k]}
      />
      {loiTruong[k] && <span className="loi">{loiTruong[k]}</span>}
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>{kh ? `Sửa khách hàng ${kh.ten}` : 'Thêm khách hàng'}</h2>
        {o('ten', 'Tên khách hàng', true)}
        <div className="hai-cot">
          {o('sdt', 'Số điện thoại', true, '0909 123 456')}
          {o('ma_so_thue', 'Mã số thuế', false, '10 số, chi nhánh thêm -xxx')}
        </div>
        {o('dia_chi', 'Địa chỉ')}
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
