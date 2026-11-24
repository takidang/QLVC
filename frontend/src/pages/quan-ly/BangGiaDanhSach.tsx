import { useEffect, useState, type FormEvent, type InputHTMLAttributes } from 'react'
import {
  danhSachBangGia,
  suaBangGia,
  tenTinhDaDung,
  themBangGia,
  type BangGia,
} from '../../api/bangGia'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'
import { Nhan } from '../../nhan'
import { DauDanhMuc, OTim } from '../danh-muc'

const SO_DONG = 20
const ngayVN = (d: string) => d.split('-').reverse().join('/')
const dong = (n: number) => n.toLocaleString('vi-VN')

export default function BangGiaDanhSach() {
  const [tim, setTim] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: BangGia[]; tong: number } | null>(null) // null = đang tải
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<BangGia | 'moi' | null>(null)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachBangGia({ tim, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được bảng giá')
      })
    return () => {
      bo = true
    }
  }, [tim, trang, lanTai])

  const duLieu = ds?.du_lieu ?? []
  const soTrang = Math.max(1, Math.ceil((ds?.tong ?? 0) / SO_DONG))
  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Bảng giá"
        phu="Cước = max(cước tối thiểu, đơn giá/kg × khối lượng tính cước), làm tròn lên (BR-48). Đổi giá: thêm mức mới với ngày hiệu lực mới; đơn đã tạo giữ giá cũ."
        nut="Thêm mức giá"
        onNut={() => setDangSua('moi')}
      />

      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <div className="kinh bang-khung dm">
        <div className="cong-cu">
          <span className="ghi-chu">{ds ? `${ds.tong} mức giá` : '–'}</span>
          <OTim
            giaTri={tim}
            goiY="Tìm tỉnh"
            onDoi={(v) => {
              setTim(v)
              setTrang(1)
            }}
          />
        </div>
        <table>
          <thead>
            <tr>
              <th>Tỉnh lấy → tỉnh giao</th>
              <th className="so">Đơn giá (đ/kg)</th>
              <th className="so">Cước tối thiểu (đ)</th>
              <th>Hiệu lực từ</th>
              <th>Trạng thái</th>
              <th>
                <span className="an-chu">Thao tác</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {duLieu.map((bg) => (
              <tr key={bg.id} className={bg.dang_ap_dung ? undefined : 'mo'}>
                <td className="tuyen">
                  {bg.tinh_lay} → {bg.tinh_giao}
                </td>
                <td className="so">{dong(bg.don_gia_kg)}</td>
                <td className="so">{dong(bg.cuoc_toi_thieu)}</td>
                <td>{ngayVN(bg.hieu_luc_tu)}</td>
                <td>
                  {bg.dang_ap_dung ? (
                    <Nhan loai="HOAN_THANH">Đang áp dụng</Nhan>
                  ) : (
                    <span className="ghi-chu">Đã thay hoặc chưa tới ngày</span>
                  )}
                </td>
                <td className="hanh-dong so">
                  <button className="phu" onClick={() => setDangSua(bg)}>
                    Sửa
                  </button>
                </td>
              </tr>
            ))}
            {duLieu.length === 0 && (ds || !loiTai) && (
              <tr>
                <td colSpan={6} className="trong">
                  {ds ? (
                    'Chưa có mức giá nào'
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
          Trang {trang}/{soTrang} · {ds ? `${ds.tong} mức giá` : '–'}
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {dangSua && (
        <FormBangGia
          bg={dangSua === 'moi' ? null : dangSua}
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

type Form = Record<
  'tinh_lay' | 'tinh_giao' | 'don_gia_kg' | 'cuoc_toi_thieu' | 'hieu_luc_tu',
  string
>

function FormBangGia({
  bg,
  onDong,
  onLuu,
}: {
  bg: BangGia | null
  onDong: () => void
  onLuu: () => void
}) {
  const [f, setF] = useState<Form>(() => ({
    tinh_lay: bg?.tinh_lay ?? '',
    tinh_giao: bg?.tinh_giao ?? '',
    don_gia_kg: bg ? String(bg.don_gia_kg) : '',
    cuoc_toi_thieu: bg ? String(bg.cuoc_toi_thieu) : '0',
    hieu_luc_tu: bg?.hieu_luc_tu ?? new Date().toLocaleDateString('sv-SE'),
  }))
  const [tenTinh, setTenTinh] = useState<string[]>([])
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState('')
  const [dangGui, setDangGui] = useState(false)

  useEffect(() => {
    // Gợi ý tên tỉnh đã dùng để tránh gõ lệch ("TP.HCM" khác "Hồ Chí Minh")
    tenTinhDaDung()
      .then(setTenTinh)
      .catch(() => {})
  }, [])

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung('')
    setDangGui(true)
    const vao = {
      ...f,
      don_gia_kg: Number(f.don_gia_kg),
      cuoc_toi_thieu: Number(f.cuoc_toi_thieu),
    }
    try {
      if (bg) await suaBangGia(bg.id, vao)
      else await themBangGia(vao)
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

  const o = (k: keyof Form, nhan: string, props: InputHTMLAttributes<HTMLInputElement>) => (
    <label>
      {nhan}
      <input
        value={f[k]}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
        aria-invalid={!!loiTruong[k]}
        required
        {...props}
      />
      {loiTruong[k] && <span className="loi">{loiTruong[k]}</span>}
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>{bg ? 'Sửa mức giá' : 'Thêm mức giá'}</h2>
        <datalist id="ten-tinh">
          {tenTinh.map((t) => (
            <option key={t} value={t} />
          ))}
        </datalist>
        <div className="hai-cot">
          {o('tinh_lay', 'Tỉnh lấy', { list: 'ten-tinh', maxLength: 50 })}
          {o('tinh_giao', 'Tỉnh giao', { list: 'ten-tinh', maxLength: 50 })}
          {o('don_gia_kg', 'Đơn giá (đồng/kg)', { type: 'number', min: 1 })}
          {o('cuoc_toi_thieu', 'Cước tối thiểu (đồng)', { type: 'number', min: 0, step: 1000 })}
          {o('hieu_luc_tu', 'Hiệu lực từ ngày', { type: 'date' })}
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
