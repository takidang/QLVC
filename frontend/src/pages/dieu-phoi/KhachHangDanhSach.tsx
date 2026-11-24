import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'
import { DauDanhMuc, LocTrangThai, NhanHoatDong, OTim } from '../danh-muc'
import { danhSachKhachHang, suaKhachHang, themKhachHang, type KhachHang } from '../../api/khachHang'

const SO_DONG = 20
type Form = { ten: string; sdt: string; dia_chi: string; ma_so_thue: string }

export default function KhachHangDanhSach() {
  const [tim, setTim] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: KhachHang[]; tong: number } | null>(null) // null = đang tải
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

  const duLieu = ds?.du_lieu ?? []
  const soTrang = Math.max(1, Math.ceil((ds?.tong ?? 0) / SO_DONG))
  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Khách hàng"
        phu={
          ds
            ? `${ds.tong} khách${trangThai === 'NGUNG' ? ' đang ngừng' : trangThai ? ' đang hoạt động' : ''}`
            : '–'
        }
        nut="Thêm khách hàng"
        onNut={() => setDangSua('moi')}
      />

      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <div className="kinh bang-khung dm">
        <div className="cong-cu">
          <LocTrangThai
            chon={trangThai}
            onChon={(ma) => {
              setTrangThai(ma)
              setTrang(1)
            }}
          />
          <OTim
            giaTri={tim}
            goiY="Tìm tên hoặc SĐT"
            onDoi={(v) => {
              setTim(v)
              setTrang(1)
            }}
          />
        </div>
        <table>
          <thead>
            <tr>
              <th>Tên</th>
              <th>SĐT</th>
              <th>Địa chỉ</th>
              <th>Mã số thuế</th>
              <th>Trạng thái</th>
              <th>
                <span className="an-chu">Thao tác</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {duLieu.map((kh) => (
              <tr key={kh.id} className={kh.trang_thai === 'NGUNG' ? 'mo' : undefined}>
                <td className="tuyen">{kh.ten}</td>
                <td className="ma">{kh.sdt}</td>
                <td>{kh.dia_chi || <span className="ghi-chu">—</span>}</td>
                <td className="ma">{kh.ma_so_thue || '—'}</td>
                <td>
                  <NhanHoatDong trangThai={kh.trang_thai} />
                </td>
                <td className="hanh-dong so">
                  <button className="phu" onClick={() => setDangSua(kh)}>
                    Sửa
                  </button>
                  <button className="phu" onClick={() => doiTrangThai(kh)}>
                    {kh.trang_thai === 'HOAT_DONG' ? 'Ngừng' : 'Hoạt động lại'}
                  </button>
                </td>
              </tr>
            ))}
            {duLieu.length === 0 && (ds || !loiTai) && (
              <tr>
                <td colSpan={6} className="trong">
                  {ds ? (
                    'Chưa có khách hàng nào phù hợp'
                  ) : phongCachDaLuu() === 'pixel' ? (
                    /* Hiệu ứng Pixel: màn tải bảng kiểu Pixel thay chữ Đang tải… */
                    <DangTaiPixel kieu="bang" soCot={6} />
                  ) : (
                    'Đang tải…'
                  )}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="phan-trang">
        <button className="phu" disabled={trang <= 1} onClick={() => setTrang(trang - 1)}>
          Trước
        </button>
        <span>
          Trang {trang}/{soTrang} · {ds ? `${ds.tong} khách` : '–'}
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
