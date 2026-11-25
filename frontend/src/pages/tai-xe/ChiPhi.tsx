import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import {
  chiPhiChuyen,
  ghiChiPhi,
  suaChiPhi,
  TEN_LOAI_CHI,
  TEN_TRANG_THAI_CHI,
  xoaChiPhi,
  type ChiPhiChuyen,
  type KhoanChi,
  type KhoanChiVao,
  type LoaiChi,
} from '../../api/chiPhi'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import ChonTep from '../../ChonTep'
import { NoiDungNutGuiPixel } from '../../HieuUngPixel'
import { dangHieuUngPixel, phongCachDaLuu } from '../../nen'
import { NoteLoi } from '../../NoteLoi'
import { nenAnh } from '../../nenAnh'
import { Nhan } from '../../nhan'
import { LOI_MANG, SO_ANH_TOI_DA } from './QuetLay'
import { ThongBao } from '../../thongBao'
import { useXacNhan } from '../../xacNhanKho'

const dong = (so: number) => `${so.toLocaleString('vi-VN')} đ`
const thongBaoLoi = (err: unknown) => {
  const truong = Object.values(loiTheoTruong(err))
  if (truong.length) return truong.join('; ')
  return err instanceof LoiApi ? err.message : err instanceof Error ? err.message : LOI_MANG
}

// UC-21: khối Chi phí trên trang chuyến của tài xế. Ghi được khi đang chạy / đã về (BR-54); đã quyết toán chỉ xem
export function ChiPhi({ chuyenId, ghiDuoc }: { chuyenId: number; ghiDuoc: boolean }) {
  const [cp, setCp] = useState<ChiPhiChuyen | null>(null)
  const [dangSua, setDangSua] = useState<number | null>(null)
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')
  const hoi = useXacNhan()
  const daXoa = useRef(new Set<number>()) // bấm hai lần không gửi hai yêu cầu xóa

  const tai = useCallback(() => {
    chiPhiChuyen(chuyenId)
      .then(setCp)
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được chi phí'))
  }, [chuyenId])
  useEffect(tai, [tai])

  async function lam(viec: () => Promise<unknown>, xong: string) {
    setThongBao('')
    setLoi('')
    try {
      await viec()
      setThongBao(xong)
      setDangSua(null)
      tai()
      return true
    } catch (err) {
      setLoi(thongBaoLoi(err))
      return false
    }
  }

  async function xoa(k: KhoanChi) {
    if (daXoa.current.has(k.id)) return
    const cau = `Xóa khoản ${TEN_LOAI_CHI[k.loai].toLowerCase()} ${dong(k.so_tien_khai)}?`
    if (!(await hoi(cau, 'Xóa'))) return
    daXoa.current.add(k.id)
    // Xóa hỏng thì cho bấm lại
    if (!(await lam(() => xoaChiPhi(k.id), 'Đã xóa khoản chi'))) daXoa.current.delete(k.id)
  }

  return (
    <div className="the">
      <strong>Chi phí</strong>
      {cp && (
        <p>
          Tạm ứng đã nhận <strong>{dong(cp.tam_ung_da_nhan)}</strong> · Đã khai{' '}
          <strong>{dong(cp.tong_da_khai)}</strong>
        </p>
      )}
      <ThongBao chu={thongBao} />
      {loi &&
        (phongCachDaLuu() === 'pixel' ? (
          <NoteLoi noiDung={loi} kieu="nho" />
        ) : (
          <p role="alert" className="loi">
            {loi}
          </p>
        ))}
      {cp && cp.khoan.length === 0 && <p className="ghi-chu">Chưa ghi khoản chi nào</p>}
      <ul className="ds-chi">
        {cp?.khoan.map((k) =>
          dangSua === k.id ? (
            <li key={k.id}>
              <FormChi
                dau={k}
                nut="Lưu"
                onGui={(vao) => lam(() => suaChiPhi(k.id, vao), 'Đã sửa khoản chi')}
                onThoi={() => setDangSua(null)}
              />
            </li>
          ) : (
            <li key={k.id}>
              <div className="the-dau">
                <span>
                  {TEN_LOAI_CHI[k.loai]} · <strong>{dong(k.so_tien_khai)}</strong>
                  {k.so_lit !== null && ` · ${Number(k.so_lit).toLocaleString('vi-VN')} lít`}
                </span>
                <Nhan loai={`CHI_${k.trang_thai}`}>
                  {TEN_TRANG_THAI_CHI[k.trang_thai] ?? k.trang_thai}
                </Nhan>
              </div>
              <div className="ghi-chu">
                {k.ghi_chu} · {k.so_anh} ảnh
              </div>
              {ghiDuoc && k.trang_thai === 'CHO_DUYET' && (
                <div className="hanh-dong">
                  <button type="button" className="phu" onClick={() => setDangSua(k.id)}>
                    Sửa
                  </button>
                  <button type="button" className="phu" onClick={() => void xoa(k)}>
                    Xóa
                  </button>
                </div>
              )}
            </li>
          ),
        )}
      </ul>
      {ghiDuoc && dangSua === null && (
        <FormChi
          coAnh
          nut="Ghi chi phí"
          onGui={async (vao, anh) =>
            lam(
              async () => ghiChiPhi(chuyenId, vao, await Promise.all(anh.map(nenAnh))),
              `Đã ghi ${TEN_LOAI_CHI[vao.loai].toLowerCase()} ${dong(vao.so_tien)}, chờ Kế toán duyệt`,
            )
          }
        />
      )}
    </div>
  )
}

// Form ghi mới (có ảnh) hoặc sửa (không đổi ảnh – UC-21 quyết định 6). Số lít chỉ hiện khi chọn Dầu
function FormChi({
  dau,
  coAnh = false,
  nut,
  onGui,
  onThoi,
}: {
  dau?: KhoanChi
  coAnh?: boolean
  nut: string
  onGui: (vao: KhoanChiVao, anh: File[]) => Promise<boolean>
  onThoi?: () => void
}) {
  const [loai, setLoai] = useState<LoaiChi>(dau?.loai ?? 'DAU')
  const [soTien, setSoTien] = useState(dau ? String(dau.so_tien_khai) : '')
  const [soLit, setSoLit] = useState(dau?.so_lit ?? '')
  const [ghiChu, setGhiChu] = useState(dau?.ghi_chu ?? '')
  const [anh, setAnh] = useState<File[]>([])
  const [dangGui, setDangGui] = useState(false)
  const [loi, setLoi] = useState('')
  // Hiệu ứng Pixel: cờ hiện "Xong ✓" ngắn trên nút gửi sau khi API thành công (≤ 1,2 s)
  const [vuaXong, setVuaXong] = useState(false)

  useEffect(() => {
    if (!vuaXong) return
    const t = window.setTimeout(() => setVuaXong(false), 1100)
    return () => window.clearTimeout(t)
  }, [vuaXong])

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (coAnh && anh.length > SO_ANH_TOI_DA) return setLoi(`Tối đa ${SO_ANH_TOI_DA} ảnh`)
    setLoi('')
    setVuaXong(false)
    setDangGui(true)
    const xong = await onGui(
      {
        loai,
        so_tien: Number(soTien),
        so_lit: loai === 'DAU' ? soLit : null,
        ghi_chu: ghiChu.trim(),
      },
      anh,
    )
    setDangGui(false)
    if (xong && !dau) {
      setSoTien('')
      setSoLit('')
      setGhiChu('')
      setAnh([])
      ;(e.target as HTMLFormElement).reset()
      // Hiệu ứng Pixel: đổi nhãn nút sang "Xong ✓" sau khi ghi chi phí thành công
      if (dangHieuUngPixel()) setVuaXong(true)
    }
  }

  const huPixel = dangHieuUngPixel()

  return (
    <form className="form-km" onSubmit={gui}>
      <label>
        Loại chi
        <select value={loai} onChange={(e) => setLoai(e.target.value as LoaiChi)}>
          {Object.entries(TEN_LOAI_CHI).map(([ma, ten]) => (
            <option key={ma} value={ma}>
              {ten}
            </option>
          ))}
        </select>
      </label>
      <label>
        Số tiền (đồng)
        <input
          type="number"
          inputMode="numeric"
          min={1}
          step={1}
          required
          value={soTien}
          onChange={(e) => setSoTien(e.target.value)}
        />
      </label>
      {loai === 'DAU' && (
        <label>
          Số lít
          <input
            type="number"
            inputMode="decimal"
            min={0.01}
            step={0.01}
            required
            value={soLit}
            onChange={(e) => setSoLit(e.target.value)}
          />
        </label>
      )}
      <label>
        Ghi chú
        <input maxLength={500} value={ghiChu} onChange={(e) => setGhiChu(e.target.value)} />
      </label>
      {coAnh && (
        <ChonTep
          nhan={`Ảnh hóa đơn (tối đa ${SO_ANH_TOI_DA})`}
          accept="image/jpeg,image/png"
          capture="environment"
          multiple
          dangNen={dangGui && anh.length > 0}
          onChange={(e) => setAnh([...(e.target.files ?? [])])}
        />
      )}
      {loi &&
        (phongCachDaLuu() === 'pixel' ? (
          <NoteLoi noiDung={loi} kieu="nho" />
        ) : (
          <p role="alert" className="loi">
            {loi}
          </p>
        ))}
      <div className="hanh-dong">
        {onThoi && (
          <button type="button" className="phu" disabled={dangGui} onClick={onThoi}>
            Thôi
          </button>
        )}
        {/* Hiệu ứng Pixel: nút gửi giữ bề ngang và đổi chữ theo bậc "Đang gửi…" → "Xong ✓" */}
        <button
          disabled={dangGui}
          aria-busy={dangGui || undefined}
          className={
            huPixel ? `px-nut-gui${dangGui ? ' dang-gui' : vuaXong ? ' vua-xong' : ''}` : undefined
          }
        >
          {huPixel ? (
            <NoiDungNutGuiPixel nhan={nut} dangGui={dangGui} vuaXong={vuaXong} />
          ) : dangGui ? (
            'Đang gửi…'
          ) : (
            nut
          )}
        </button>
      </div>
    </form>
  )
}
