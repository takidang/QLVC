import { useEffect, useRef, useState, type FormEvent, type InputHTMLAttributes } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachTaiXe, suaTaiXe, themTaiXe, type HangGplx, type TaiXe } from '../../api/taiXe'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'
import { DauDanhMuc, HanGiayTo, LocTrangThai, NhanHoatDong, OTim } from '../danh-muc'
import { useXacNhan } from '../../xacNhanKho'
import { NutChep } from '../../NutChep'

const SO_DONG = 20
const HANG: HangGplx[] = ['B', 'C1', 'C']

type Form = Record<keyof Omit<TaiXe, 'id' | 'trang_thai'> | 'mat_khau', string>
const FORM_TRONG: Form = {
  ten_dang_nhap: '',
  mat_khau: '',
  ho_ten: '',
  so_gplx: '',
  hang_gplx: 'C',
  han_gplx: '',
  sdt: '',
}
const NHAN: Record<keyof Form, string> = {
  ten_dang_nhap: 'Tên đăng nhập',
  mat_khau: 'Mật khẩu ban đầu (ít nhất 8 ký tự)',
  ho_ten: 'Họ tên',
  so_gplx: 'Số GPLX',
  hang_gplx: 'Hạng GPLX',
  han_gplx: 'Hạn GPLX',
  sdt: 'Số điện thoại',
}

export default function TaiXeDanhSach() {
  const [tim, setTim] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: TaiXe[]; tong: number } | null>(null) // null = đang tải
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<TaiXe | 'moi' | null>(null)
  const [lanTai, setLanTai] = useState(0) // tăng lên để tải lại sau khi thêm/sửa
  const tai = () => setLanTai((n) => n + 1)
  const hoi = useXacNhan()
  const dangDoi = useRef(new Set<number>()) // bấm hai lần không gửi hai yêu cầu

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn (gõ tìm nhanh, mạng chậm) thì bỏ, không ghi đè kết quả mới
    danhSachTaiXe({ tim, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách tài xế')
      })
    return () => {
      bo = true
    }
  }, [tim, trangThai, trang, lanTai])

  async function doiTrangThai(tx: TaiXe) {
    const ngung = tx.trang_thai === 'HOAT_DONG'
    // Ngừng tài xế khóa luôn tài khoản đăng nhập (BR-60, UC-04): hỏi lại cho chắc
    if (dangDoi.current.has(tx.id)) return
    const cau = `Ngừng tài xế ${tx.ho_ten}? Tài khoản "${tx.ten_dang_nhap}" sẽ bị khóa ngay.`
    if (ngung && !(await hoi(cau, 'Ngừng'))) return
    dangDoi.current.add(tx.id)
    try {
      await suaTaiXe(tx.id, { trang_thai: ngung ? 'NGUNG' : 'HOAT_DONG' })
      tai()
    } catch (e) {
      setLoiTai(e instanceof LoiApi ? e.message : 'Không đổi được trạng thái')
    } finally {
      dangDoi.current.delete(tx.id)
    }
  }

  const duLieu = ds?.du_lieu ?? []
  const soTrang = Math.max(1, Math.ceil((ds?.tong ?? 0) / SO_DONG))
  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Tài xế"
        phu={`${ds ? `${ds.tong} tài xế${trangThai === 'NGUNG' ? ' đang ngừng' : trangThai ? ' đang hoạt động' : ''}` : '–'} · GPLX sắp hết hạn tô cam`}
        nut="Thêm tài xế"
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
            goiY="Tìm họ tên, số GPLX, SĐT"
            onDoi={(v) => {
              setTim(v)
              setTrang(1)
            }}
          />
        </div>
        <table>
          <thead>
            <tr>
              <th>Tài xế</th>
              <th>GPLX</th>
              <th>Hạn GPLX</th>
              <th>SĐT</th>
              <th>Trạng thái</th>
              <th>
                <span className="an-chu">Thao tác</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {duLieu.map((tx) => (
              <tr key={tx.id} className={tx.trang_thai === 'NGUNG' ? 'mo' : undefined}>
                <td>
                  <span className="tuyen">{tx.ho_ten}</span>
                  <small>{tx.ten_dang_nhap}</small>
                </td>
                <td>
                  <span className="so-gplx">{tx.so_gplx}</span>
                  <span className="bien">Hạng {tx.hang_gplx}</span>
                </td>
                <td>
                  <HanGiayTo han={tx.han_gplx} />
                </td>
                <td className="ma">
                  {tx.sdt}
                  <NutChep chu={tx.sdt} />
                </td>
                <td>
                  <NhanHoatDong trangThai={tx.trang_thai} />
                </td>
                <td className="hanh-dong so">
                  <button className="phu" onClick={() => setDangSua(tx)}>
                    Sửa
                  </button>
                  <button className="phu" onClick={() => doiTrangThai(tx)}>
                    {tx.trang_thai === 'HOAT_DONG' ? 'Ngừng' : 'Hoạt động lại'}
                  </button>
                </td>
              </tr>
            ))}
            {duLieu.length === 0 && (ds || !loiTai) && (
              <tr>
                <td colSpan={6} className="trong">
                  {ds ? (
                    'Chưa có tài xế nào phù hợp'
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
          Trang {trang}/{soTrang} · {ds ? `${ds.tong} tài xế` : '–'}
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {dangSua && (
        <FormTaiXe
          tx={dangSua === 'moi' ? null : dangSua}
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

function FormTaiXe({
  tx,
  onDong,
  onLuu,
}: {
  tx: TaiXe | null
  onDong: () => void
  onLuu: () => void
}) {
  const [f, setF] = useState<Form>(
    tx
      ? { ...FORM_TRONG, ...Object.fromEntries(Object.entries(tx).map(([k, v]) => [k, String(v)])) }
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
      ho_ten: f.ho_ten,
      so_gplx: f.so_gplx,
      hang_gplx: f.hang_gplx as HangGplx,
      han_gplx: f.han_gplx,
      sdt: f.sdt,
    }
    try {
      // Tên đăng nhập, mật khẩu chỉ nhập lúc thêm; đổi về sau ở UC-02
      if (tx) await suaTaiXe(tx.id, vao)
      else await themTaiXe({ ...vao, ten_dang_nhap: f.ten_dang_nhap, mat_khau: f.mat_khau })
      onLuu()
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      // Lỗi nghiệp vụ gắn được vào một ô thì hiện ngay dưới ô đó
      const oCuaMa: Record<string, keyof Form> = {
        SO_GPLX_TRUNG: 'so_gplx',
        TEN_DANG_NHAP_TRUNG: 'ten_dang_nhap',
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
        <h2>{tx ? `Sửa tài xế ${tx.ho_ten}` : 'Thêm tài xế'}</h2>
        {o('ho_ten', { required: true, maxLength: 100 })}
        {tx ? (
          <p className="ghi-chu">
            Tên đăng nhập: {tx.ten_dang_nhap} (đổi tên, mật khẩu ở mục Người dùng)
          </p>
        ) : (
          <div className="hai-cot">
            {o('ten_dang_nhap', { required: true, maxLength: 50, autoComplete: 'off' })}
            {o('mat_khau', {
              type: 'password',
              required: true,
              minLength: 8,
              autoComplete: 'new-password',
            })}
          </div>
        )}
        <div className="hai-cot">
          {o('so_gplx', { required: true, minLength: 6, maxLength: 20 })}
          <label>
            {NHAN.hang_gplx}
            <select
              value={f.hang_gplx}
              onChange={(e) => setF({ ...f, hang_gplx: e.target.value })}
              aria-invalid={!!loiTruong.hang_gplx}
            >
              {HANG.map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
            {loiTruong.hang_gplx && <span className="loi">{loiTruong.hang_gplx}</span>}
          </label>
          {o('han_gplx', { type: 'date', required: true })}
          {o('sdt', { required: true, inputMode: 'tel' })}
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
          <button disabled={dangGui}>{dangGui ? 'Đang lưu…' : 'Lưu'}</button>
        </div>
      </form>
    </div>
  )
}
