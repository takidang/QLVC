import { useEffect, useState, type FormEvent, type InputHTMLAttributes } from 'react'
import { toi, type VaiTro } from '../../api/auth'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import {
  datLaiMatKhau,
  danhSachNguoiDung,
  suaNguoiDung,
  themNguoiDung,
  type TaiKhoan,
  type VaiTroTao,
} from '../../api/nguoiDung'

const SO_DONG = 20
const TEN_VAI_TRO: Record<VaiTro, string> = {
  QUAN_LY: 'Quản lý',
  DIEU_PHOI: 'Điều phối',
  KE_TOAN: 'Kế toán',
  TAI_XE: 'Tài xế',
}
const VAI_TRO_TAO: VaiTroTao[] = ['QUAN_LY', 'DIEU_PHOI', 'KE_TOAN']
const dangKhoaTam = (tk: TaiKhoan) => !!tk.khoa_den && new Date(tk.khoa_den) > new Date()

type Form = { ten_dang_nhap: string; ho_ten: string; mat_khau: string; vai_tro: string }
const FORM_TRONG: Form = { ten_dang_nhap: '', ho_ten: '', mat_khau: '', vai_tro: 'DIEU_PHOI' }
const NHAN: Record<keyof Form, string> = {
  ten_dang_nhap: 'Tên đăng nhập',
  ho_ten: 'Họ tên',
  mat_khau: 'Mật khẩu ban đầu (ít nhất 8 ký tự)',
  vai_tro: 'Vai trò',
}

export default function NguoiDungDanhSach() {
  const [tim, setTim] = useState('')
  const [vaiTro, setVaiTro] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: TaiKhoan[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [toiId, setToiId] = useState<number>()
  const [dangSua, setDangSua] = useState<TaiKhoan | 'moi' | null>(null)
  const [datMk, setDatMk] = useState<TaiKhoan | null>(null)
  const [lanTai, setLanTai] = useState(0) // tăng lên để tải lại sau khi thêm/sửa
  const tai = () => setLanTai((n) => n + 1)

  useEffect(() => {
    toi()
      .then((nd) => setToiId(nd.id))
      .catch(() => {})
  }, [])

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ, không ghi đè kết quả mới
    danhSachNguoiDung({ tim, vai_tro: vaiTro, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách người dùng')
      })
    return () => {
      bo = true
    }
  }, [tim, vaiTro, trangThai, trang, lanTai])

  async function doiTrangThai(tk: TaiKhoan) {
    const khoa = tk.trang_thai === 'HOAT_DONG'
    if (khoa && !confirm(`Khóa tài khoản "${tk.ten_dang_nhap}"? Người này bị đăng xuất ngay.`))
      return
    try {
      await suaNguoiDung(tk.id, { trang_thai: khoa ? 'NGUNG' : 'HOAT_DONG' })
      tai()
    } catch (e) {
      setLoiTai(e instanceof LoiApi ? e.message : 'Không đổi được trạng thái')
    }
  }

  const soTrang = Math.max(1, Math.ceil(ds.tong / SO_DONG))
  const locTrang = (set: (v: string) => void) => (v: string) => {
    set(v)
    setTrang(1)
  }
  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Người dùng</h1>
        <input
          placeholder="Tìm tên đăng nhập, họ tên"
          aria-label="Tìm tên đăng nhập, họ tên"
          value={tim}
          onChange={(e) => locTrang(setTim)(e.target.value)}
        />
        <select
          aria-label="Lọc vai trò"
          value={vaiTro}
          onChange={(e) => locTrang(setVaiTro)(e.target.value)}
        >
          <option value="">Mọi vai trò</option>
          {(Object.keys(TEN_VAI_TRO) as VaiTro[]).map((vt) => (
            <option key={vt} value={vt}>
              {TEN_VAI_TRO[vt]}
            </option>
          ))}
        </select>
        <select
          aria-label="Lọc trạng thái"
          value={trangThai}
          onChange={(e) => locTrang(setTrangThai)(e.target.value)}
        >
          <option value="">Mọi trạng thái</option>
          <option value="HOAT_DONG">Hoạt động</option>
          <option value="NGUNG">Đã khóa</option>
        </select>
        <button onClick={() => setDangSua('moi')}>Thêm người dùng</button>
      </div>

      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Tên đăng nhập</th>
            <th>Họ tên</th>
            <th>Vai trò</th>
            <th>Trạng thái</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((tk) => (
            <tr key={tk.id} className={tk.trang_thai === 'NGUNG' ? 'mo' : undefined}>
              <td>
                {tk.ten_dang_nhap}
                {tk.id === toiId && ' (bạn)'}
              </td>
              <td>{tk.ho_ten}</td>
              <td>{TEN_VAI_TRO[tk.vai_tro]}</td>
              <td className={dangKhoaTam(tk) ? 'het-han' : undefined}>
                {tk.trang_thai === 'HOAT_DONG' ? 'Hoạt động' : 'Đã khóa'}
                {dangKhoaTam(tk) && ' · khóa tạm do sai mật khẩu'}
              </td>
              <td className="hanh-dong">
                <button className="phu" onClick={() => setDangSua(tk)}>
                  Sửa
                </button>
                <button className="phu" onClick={() => setDatMk(tk)}>
                  Đặt lại mật khẩu
                </button>
                {/* Tài xế khóa ở trang Tài xế (UC-04); không tự khóa chính mình */}
                {tk.vai_tro !== 'TAI_XE' && tk.id !== toiId && (
                  <button className="phu" onClick={() => doiTrangThai(tk)}>
                    {tk.trang_thai === 'HOAT_DONG' ? 'Khóa' : 'Mở khóa'}
                  </button>
                )}
              </td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={5} className="trong">
                Chưa có người dùng nào phù hợp
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
          Trang {trang}/{soTrang} · {ds.tong} người dùng
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {dangSua && (
        <FormNguoiDung
          tk={dangSua === 'moi' ? null : dangSua}
          laToi={dangSua !== 'moi' && dangSua.id === toiId}
          onDong={() => setDangSua(null)}
          onLuu={() => {
            setDangSua(null)
            tai()
          }}
        />
      )}
      {datMk && <FormMatKhau tk={datMk} onDong={() => setDatMk(null)} />}
    </section>
  )
}

function FormNguoiDung({
  tk,
  laToi,
  onDong,
  onLuu,
}: {
  tk: TaiKhoan | null
  laToi: boolean
  onDong: () => void
  onLuu: () => void
}) {
  const [f, setF] = useState<Form>(tk ? { ...FORM_TRONG, ...tk } : FORM_TRONG)
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState('')
  const [dangGui, setDangGui] = useState(false)
  // Tài xế đổi vai trò ở UC-04; tự hạ quyền mình bị chặn (UC-02-AC8, AC9)
  const khoaVaiTro = tk?.vai_tro === 'TAI_XE' || laToi

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung('')
    setDangGui(true)
    const vao = { ten_dang_nhap: f.ten_dang_nhap, ho_ten: f.ho_ten }
    try {
      if (tk)
        await suaNguoiDung(tk.id, khoaVaiTro ? vao : { ...vao, vai_tro: f.vai_tro as VaiTroTao })
      else await themNguoiDung({ ...vao, mat_khau: f.mat_khau, vai_tro: f.vai_tro as VaiTroTao })
      onLuu()
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      if (err instanceof LoiApi && err.ma === 'TEN_DANG_NHAP_TRUNG')
        theoTruong.ten_dang_nhap = err.message
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
        <h2>{tk ? `Sửa người dùng ${tk.ten_dang_nhap}` : 'Thêm người dùng'}</h2>
        <div className="hai-cot">
          {o('ten_dang_nhap', { required: true, maxLength: 50, autoComplete: 'off' })}
          {o('ho_ten', { required: true, maxLength: 100 })}
        </div>
        {!tk &&
          o('mat_khau', {
            type: 'password',
            required: true,
            minLength: 8,
            maxLength: 200,
            autoComplete: 'new-password',
          })}
        {khoaVaiTro ? (
          <p className="ghi-chu">
            Vai trò: {TEN_VAI_TRO[tk!.vai_tro]}
            {laToi ? ' (không tự đổi vai trò của chính mình)' : ' (đổi ở trang Tài xế)'}
          </p>
        ) : (
          <label>
            {NHAN.vai_tro}
            <select
              value={f.vai_tro}
              onChange={(e) => setF({ ...f, vai_tro: e.target.value })}
              aria-invalid={!!loiTruong.vai_tro}
            >
              {VAI_TRO_TAO.map((vt) => (
                <option key={vt} value={vt}>
                  {TEN_VAI_TRO[vt]}
                </option>
              ))}
            </select>
            {loiTruong.vai_tro && <span className="loi">{loiTruong.vai_tro}</span>}
          </label>
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

function FormMatKhau({ tk, onDong }: { tk: TaiKhoan; onDong: () => void }) {
  const [matKhau, setMatKhau] = useState('')
  const [loi, setLoi] = useState('')
  const [xong, setXong] = useState(false)
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoi('')
    setDangGui(true)
    try {
      await datLaiMatKhau(tk.id, matKhau)
      setXong(true)
    } catch (err) {
      setLoi(
        loiTheoTruong(err).mat_khau ??
          (err instanceof LoiApi ? err.message : 'Không đặt lại được, vui lòng thử lại'),
      )
    } finally {
      setDangGui(false)
    }
  }

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>Đặt lại mật khẩu cho {tk.ten_dang_nhap}</h2>
        {xong ? (
          <p className="ghi-chu">
            Đã đặt mật khẩu mới. Báo cho {tk.ho_ten} trực tiếp, không gửi qua kênh công khai.
          </p>
        ) : (
          <label>
            Mật khẩu mới (ít nhất 8 ký tự)
            <input
              type="password"
              value={matKhau}
              onChange={(e) => setMatKhau(e.target.value)}
              required
              minLength={8}
              maxLength={200}
              autoComplete="new-password"
              aria-invalid={!!loi}
            />
            {loi && <span className="loi">{loi}</span>}
          </label>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            {xong ? 'Đóng' : 'Hủy'}
          </button>
          {!xong && <button disabled={dangGui}>{dangGui ? 'Đang lưu…' : 'Lưu'}</button>}
        </div>
      </form>
    </div>
  )
}
