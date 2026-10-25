import { useEffect, useState, type FormEvent, type InputHTMLAttributes } from 'react'
import { danhSachDon, taoDon, tinhCuoc, type BaoGia, type Don } from '../../api/don'
import { kemMaBr, LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachKhachHang, type KhachHang } from '../../api/khachHang'
import { danhSachNut, type Nut } from '../../api/tuyen'

const SO_DONG = 20
const dong = (n: number) => n.toLocaleString('vi-VN')
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
// Ô datetime-local không có múi giờ; nhà xe ở Việt Nam nên gắn +07:00 (API bắt buộc có múi giờ)
const coMuiGio = (v: string) => (v ? `${v}:00+07:00` : null)
const TEN_TRANG_THAI: Record<string, string> = {
  CHO_GHEP: 'Chờ ghép',
  DA_GHEP: 'Đã ghép',
  DA_LAY: 'Đã lấy',
  DA_GIAO: 'Đã giao',
  THAT_BAI: 'Thất bại',
  TRA_HANG: 'Trả hàng',
  HUY: 'Hủy',
}

export default function DonDanhSach() {
  const [tim, setTim] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: Don[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [moForm, setMoForm] = useState(false)
  const [vuaTao, setVuaTao] = useState<Don | null>(null)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachDon({ tim, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách đơn')
      })
    return () => {
      bo = true
    }
  }, [tim, trangThai, trang, lanTai])

  const soTrang = Math.max(1, Math.ceil(ds.tong / SO_DONG))
  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Đơn hàng</h1>
        <input
          placeholder="Tìm mã đơn"
          aria-label="Tìm mã đơn"
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
          {Object.entries(TEN_TRANG_THAI).map(([ma, ten]) => (
            <option key={ma} value={ma}>
              {ten}
            </option>
          ))}
        </select>
        <button onClick={() => setMoForm(true)}>Tạo đơn</button>
      </div>
      {vuaTao && (
        <p className="thanh-cong">
          Đã tạo đơn <strong>{vuaTao.ma_don}</strong>, cước {dong(vuaTao.cuoc_tinh)} đ (đã chốt).
        </p>
      )}
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Mã đơn</th>
            <th>Khách</th>
            <th>Lấy → giao</th>
            <th className="so">Hàng</th>
            <th>Hạn giao</th>
            <th className="so">Cước (đ)</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((d) => (
            <tr key={d.id}>
              <td className="bien-so">{d.ma_don}</td>
              <td>{d.ten_khach}</td>
              <td>
                {d.tinh_lay} → {d.tinh_giao}
              </td>
              <td className="so">
                {Number(d.kg).toLocaleString('vi-VN')} kg, {Number(d.m3).toLocaleString('vi-VN')}{' '}
                m³, {d.so_kien} kiện
              </td>
              <td>{lucVN(d.han_giao)}</td>
              <td className="so">{dong(d.cuoc_tinh)}</td>
              <td>{TEN_TRANG_THAI[d.trang_thai] ?? d.trang_thai}</td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={7} className="trong">
                Chưa có đơn nào phù hợp
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
          Trang {trang}/{soTrang} · {ds.tong} đơn
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {moForm && (
        <FormTaoDon
          onDong={() => setMoForm(false)}
          onLuu={(d) => {
            setMoForm(false)
            setVuaTao(d)
            setLanTai((n) => n + 1)
          }}
        />
      )}
    </section>
  )
}

const FORM_TRONG = {
  khach_hang_id: '',
  mo_ta: '',
  kg: '',
  m3: '',
  so_kien: '1',
  nut_lay_id: '',
  dia_chi_lay: '',
  nguoi_lien_he_lay: '',
  sdt_lay: '',
  lay_tu: '',
  lay_den: '',
  nut_giao_id: '',
  dia_chi_giao: '',
  nguoi_nhan: '',
  sdt_nhan: '',
  han_giao: '',
}
type Form = typeof FORM_TRONG

function FormTaoDon({ onDong, onLuu }: { onDong: () => void; onLuu: (d: Don) => void }) {
  const [f, setF] = useState<Form>(FORM_TRONG)
  const [dsKhach, setDsKhach] = useState<KhachHang[]>([])
  const [dsNut, setDsNut] = useState<Nut[]>([])
  // Kết quả báo giá gắn với đúng bộ dữ liệu đã tính, dữ liệu đổi thì không hiện số cũ
  const [ketQuaGia, setKetQuaGia] = useState<{ khoa: string; gia: BaoGia | null; loi: string }>()
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState<string[]>([])
  const [dangGui, setDangGui] = useState(false)

  useEffect(() => {
    // shortcut: tối đa 100 khách và 100 nút, đủ cho nhà xe nhỏ; nhiều hơn thì thêm ô tìm
    danhSachKhachHang({ trang_thai: 'HOAT_DONG', so_dong: 100 })
      .then((r) => setDsKhach(r.du_lieu))
      .catch(() => setLoiChung(['Không tải được danh sách khách']))
    danhSachNut({ so_dong: 100 })
      .then((r) => setDsNut(r.du_lieu))
      .catch(() => setLoiChung(['Không tải được danh sách nút']))
  }, [])

  // Cước tạm tính: đủ nút lấy, nút giao, kg, m³ thì hỏi máy chủ (BR-46…48); kết quả cũ về muộn thì bỏ
  const { nut_lay_id, nut_giao_id, kg, m3 } = f
  const khoaGia = [nut_lay_id, nut_giao_id, kg, m3].join('|')
  const duDeTinh = !!nut_lay_id && !!nut_giao_id && Number(kg) > 0 && Number(m3) > 0
  useEffect(() => {
    if (!duDeTinh) return
    let bo = false
    tinhCuoc({ nut_lay_id: Number(nut_lay_id), nut_giao_id: Number(nut_giao_id), kg, m3 })
      .then((gia) => {
        if (!bo) setKetQuaGia({ khoa: khoaGia, gia, loi: '' })
      })
      .catch((e) => {
        if (!bo)
          setKetQuaGia({
            khoa: khoaGia,
            gia: null,
            loi: e instanceof LoiApi && e.status !== 400 ? e.message : '',
          })
      })
    return () => {
      bo = true
    }
  }, [duDeTinh, khoaGia, nut_lay_id, nut_giao_id, kg, m3])
  const hienTai = duDeTinh && ketQuaGia?.khoa === khoaGia ? ketQuaGia : undefined
  const baoGia = hienTai?.gia ?? null
  const loiGia = hienTai?.loi ?? ''

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung([])
    setDangGui(true)
    try {
      onLuu(
        await taoDon({
          ...f,
          khach_hang_id: Number(f.khach_hang_id),
          so_kien: Number(f.so_kien),
          nut_lay_id: Number(f.nut_lay_id),
          nut_giao_id: Number(f.nut_giao_id),
          mo_ta: f.mo_ta.trim() || null,
          nguoi_lien_he_lay: f.nguoi_lien_he_lay.trim() || null,
          lay_tu: coMuiGio(f.lay_tu),
          lay_den: coMuiGio(f.lay_den),
          han_giao: coMuiGio(f.han_giao)!,
        }),
      )
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      setLoiTruong(theoTruong)
      if (err instanceof LoiApi && err.ma === 'BR-31')
        setLoiChung(
          err.chiTiet.map((c) => kemMaBr((c as { thong_diep?: string }).thong_diep ?? '', err.ma)),
        )
      else if (Object.keys(theoTruong).length === 0)
        setLoiChung([err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại'])
    } finally {
      setDangGui(false)
    }
  }

  const sua = (k: keyof Form) => (e: { target: { value: string } }) =>
    setF({ ...f, [k]: e.target.value })
  const o = (k: keyof Form, nhan: string, props: InputHTMLAttributes<HTMLInputElement> = {}) => (
    <label>
      {nhan}
      <input value={f[k]} onChange={sua(k)} aria-invalid={!!loiTruong[k]} {...props} />
      {loiTruong[k] && <span className="loi">{loiTruong[k]}</span>}
    </label>
  )
  const chonNut = (k: 'nut_lay_id' | 'nut_giao_id', nhan: string) => (
    <label>
      {nhan}
      <select value={f[k]} onChange={sua(k)} required>
        <option value="">– Chọn nút –</option>
        {dsNut.map((n) => (
          <option key={n.id} value={n.id}>
            {n.ten} ({n.tinh})
          </option>
        ))}
      </select>
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai rong" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>Tạo đơn</h2>
        <div className="hai-cot">
          <label>
            Khách hàng
            <select value={f.khach_hang_id} onChange={sua('khach_hang_id')} required>
              <option value="">– Chọn khách –</option>
              {dsKhach.map((k) => (
                <option key={k.id} value={k.id}>
                  {k.ten} ({k.sdt})
                </option>
              ))}
            </select>
          </label>
          {o('mo_ta', 'Mô tả hàng')}
          {o('kg', 'Khối lượng thực (kg)', {
            type: 'number',
            min: 0.01,
            step: 0.01,
            required: true,
          })}
          {o('m3', 'Thể tích (m³)', { type: 'number', min: 0.01, step: 0.01, required: true })}
          {o('so_kien', 'Số kiện', { type: 'number', min: 1, required: true })}
        </div>

        <h3>Điểm lấy</h3>
        <div className="hai-cot">
          {chonNut('nut_lay_id', 'Nút lấy')}
          {o('dia_chi_lay', 'Địa chỉ lấy', { required: true })}
          {o('nguoi_lien_he_lay', 'Người liên hệ')}
          {o('sdt_lay', 'SĐT lấy', { required: true })}
          {o('lay_tu', 'Lấy từ (không bắt buộc)', { type: 'datetime-local' })}
          {o('lay_den', 'Lấy đến', { type: 'datetime-local' })}
        </div>

        <h3>Điểm giao</h3>
        <div className="hai-cot">
          {chonNut('nut_giao_id', 'Nút giao')}
          {o('dia_chi_giao', 'Địa chỉ giao', { required: true })}
          {o('nguoi_nhan', 'Người nhận', { required: true })}
          {o('sdt_nhan', 'SĐT nhận', { required: true })}
          {o('han_giao', 'Hạn giao', { type: 'datetime-local', required: true })}
        </div>

        <div className="canh-bao">
          {baoGia ? (
            <>
              <strong>Cước: {dong(baoGia.cuoc)} đ</strong> (KL tính cước{' '}
              {Number(baoGia.kl_tinh_cuoc).toLocaleString('vi-VN')} kg × {dong(baoGia.don_gia_kg)}{' '}
              đ/kg, tối thiểu {dong(baoGia.cuoc_toi_thieu)} đ). Cước chốt khi lưu đơn.
            </>
          ) : loiGia ? (
            <span className="loi">{loiGia}</span>
          ) : (
            'Chọn nút lấy, nút giao và nhập kg, m³ để xem cước.'
          )}
        </div>

        {loiChung.length > 0 && (
          <ul role="alert" className="loi">
            {loiChung.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            Hủy
          </button>
          <button disabled={dangGui || !baoGia}>{dangGui ? 'Đang lưu…' : 'Lưu đơn'}</button>
        </div>
      </form>
    </div>
  )
}
