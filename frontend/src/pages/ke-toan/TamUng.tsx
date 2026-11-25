import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { danhSachChuyen, type Chuyen } from '../../api/chuyen'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import {
  capTamUng,
  suaTamUng,
  tamUngChuyen,
  thuHoiTamUng,
  TEN_HINH_THUC,
  type HinhThuc,
  type TamUng as KhoanTamUng,
  type TamUngChuyen,
} from '../../api/tamUng'
import { ngayGio, TEN_TRANG_THAI } from '../../api/toi'
import { ThuocTamUngPixel } from '../../HieuUngPixel'
import { dangHieuUngPixel, phongCachDaLuu } from '../../nen'
import { NoteLoi } from '../../NoteLoi'
import { Ic, Nhan } from '../../nhan'
import { DauDanhMuc } from '../danh-muc'
import { ThongBao } from '../../thongBao'
import { useXacNhan } from '../../xacNhanKho'

// Cấp mới khi chuyến đã chốt / đang chạy (BR-53); sửa, thu hồi tới khi quyết toán (UC-23 quyết định 3)
const CAP_DUOC = ['DA_CHOT', 'DANG_CHAY']
const SUA_DUOC = [...CAP_DUOC, 'HOAN_THANH']
const dong = (so: number) => `${so.toLocaleString('vi-VN')} đ`
const thongBaoLoi = (err: unknown, truong: string) =>
  loiTheoTruong(err)[truong] ??
  (err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')

export default function TamUng() {
  const [dsChuyen, setDsChuyen] = useState<Chuyen[]>([])
  const [chuyenId, setChuyenId] = useState('')
  const [tu, setTu] = useState<TamUngChuyen | null>(null)
  const [soTien, setSoTien] = useState('')
  const [hinhThuc, setHinhThuc] = useState<HinhThuc>('TIEN_MAT')
  const [dangSua, setDangSua] = useState<number | null>(null)
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false) // khóa nút tiền khi đang gửi: bấm hai lần không cấp hai khoản
  // Hiệu ứng Pixel: cờ rung ngắn thước tạm ứng khi máy chủ báo lỗi vượt trần BR-53
  const [rungTran, setRungTran] = useState(0)
  const chuyenDangXem = useRef(0) // bỏ kết quả về muộn của chuyến đã chọn trước đó
  const hoi = useXacNhan()

  useEffect(() => {
    if (rungTran === 0) return
    const t = window.setTimeout(() => setRungTran(0), 500)
    return () => window.clearTimeout(t)
  }, [rungTran])

  useEffect(() => {
    // shortcut: 100 chuyến mỗi trạng thái, đủ cho nhà xe khoảng 10 xe
    Promise.all(SUA_DUOC.map((trang_thai) => danhSachChuyen({ trang_thai, so_dong: 100 })))
      .then((ds) => setDsChuyen(ds.flatMap((d) => d.du_lieu)))
      .catch(() => setLoi('Không tải được danh sách chuyến'))
  }, [])

  const tai = useCallback((id: number) => {
    chuyenDangXem.current = id
    tamUngChuyen(id)
      .then((r) => {
        if (chuyenDangXem.current !== id) return
        setTu(r)
        setSoTien(String(r.con_duoc_cap)) // gợi ý = định mức − đã cấp còn hiệu lực (UC-23 bước 1)
      })
      .catch(
        (e) =>
          chuyenDangXem.current === id &&
          setLoi(e instanceof LoiApi ? e.message : 'Không tải được tạm ứng'),
      )
  }, [])

  function chonChuyen(id: string) {
    setChuyenId(id)
    setTu(null)
    setDangSua(null)
    setThongBao('')
    setLoi('')
    setRungTran(0)
    if (id) tai(Number(id))
    else chuyenDangXem.current = 0
  }

  async function lam(viec: () => Promise<unknown>, xong: string, truong = 'so_tien') {
    if (dangGui) return
    setThongBao('')
    setLoi('')
    setDangGui(true)
    try {
      await viec()
      setThongBao(xong)
      setDangSua(null)
      tai(Number(chuyenId))
    } catch (err) {
      const msg = thongBaoLoi(err, truong)
      setLoi(msg)
      // Hiệu ứng Pixel: rung ngắn thước định mức khi máy chủ báo vượt trần (BR-53), không tự kiểm ở frontend
      const vuotTran =
        (err instanceof LoiApi && err.ma === 'BR-53') ||
        /BR-53|vượt.*định mức|định mức.*tạm ứng|vượt trần/i.test(
          `${msg} ${err instanceof LoiApi ? err.message : ''}`,
        )
      if (vuotTran && dangHieuUngPixel()) setRungTran((n) => n + 1)
    } finally {
      setDangGui(false)
    }
  }

  function cap(e: FormEvent) {
    e.preventDefault()
    void lam(
      () => capTamUng(Number(chuyenId), Number(soTien), hinhThuc),
      `Đã cấp ${dong(Number(soTien))}`,
    )
  }

  async function thuHoi(k: KhoanTamUng) {
    if (!(await hoi(`Tài xế ${k.ten_tai_xe} đã nộp lại ${dong(k.so_tien)}?`, 'Thu hồi'))) return
    void lam(() => thuHoiTamUng(k.id), `Đã thu hồi ${dong(k.so_tien)}`)
  }

  const capDuoc = tu && CAP_DUOC.includes(tu.trang_thai_chuyen)
  const suaDuoc = tu && SUA_DUOC.includes(tu.trang_thai_chuyen)

  const daDung = tu && tu.dinh_muc > 0 ? Math.min(1, tu.tong_hieu_luc / tu.dinh_muc) : 0
  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Tạm ứng chuyến"
        phu="Tổng tạm ứng còn hiệu lực không vượt định mức chi phí đã chốt của chuyến (dầu + cầu đường + bốc xếp, BR-53). Muốn mở chốt hoặc hủy chuyến thì thu hồi trước."
      />

      <div className="kinh dm-the">
        <div className="dm-chon">
          <label>
            Chuyến
            <select value={chuyenId} onChange={(e) => chonChuyen(e.target.value)}>
              <option value="">– Chọn chuyến –</option>
              {dsChuyen.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.ma_chuyen} · {c.ma_tuyen} · {c.ten_tai_xe} ({TEN_TRANG_THAI[c.trang_thai]})
                </option>
              ))}
            </select>
          </label>
          {tu && (
            <Nhan loai={tu.trang_thai_chuyen}>
              {TEN_TRANG_THAI[tu.trang_thai_chuyen] ?? tu.trang_thai_chuyen}
            </Nhan>
          )}
        </div>

        {tu ? (
          <>
            <div className="so-lieu dm-so">
              <div>
                <b>{dong(tu.dinh_muc)}</b>
                <span>định mức đã chốt</span>
              </div>
              <div>
                <b>{dong(tu.tong_hieu_luc)}</b>
                <span>đã cấp còn hiệu lực</span>
              </div>
              <div>
                <b>{dong(tu.con_duoc_cap)}</b>
                <span>còn được cấp</span>
              </div>
              <div
                className={`day${daDung > 0.95 ? ' cao' : ''}`}
                title="Đã cấp so với định mức đã chốt"
              >
                <span>
                  <i style={{ width: `${Math.round(daDung * 100)}%` }} />
                </span>
                {Math.round(daDung * 100)}%
              </div>
            </div>
            {/* Hiệu ứng Pixel: thước vạch định mức tạm ứng & rung khi máy chủ báo vượt trần BR-53 */}
            {dangHieuUngPixel() && (
              <ThuocTamUngPixel dinhMuc={tu.dinh_muc} daCap={tu.tong_hieu_luc} rung={rungTran} />
            )}
            {capDuoc ? (
              <form className="o-nhap" onSubmit={cap}>
                <label>
                  Số tiền (đồng)
                  <input
                    type="number"
                    min={1}
                    step={1}
                    value={soTien}
                    onChange={(e) => setSoTien(e.target.value)}
                    required
                  />
                </label>
                <label>
                  Hình thức
                  <select
                    value={hinhThuc}
                    onChange={(e) => setHinhThuc(e.target.value as HinhThuc)}
                  >
                    {Object.entries(TEN_HINH_THUC).map(([ma, ten]) => (
                      <option key={ma} value={ma}>
                        {ten}
                      </option>
                    ))}
                  </select>
                </label>
                <button disabled={dangGui}>
                  <Ic ten="cong" />
                  {dangGui ? 'Đang gửi…' : 'Cấp tạm ứng'}
                </button>
              </form>
            ) : (
              <p className="ghi-chu">
                Chuyến {TEN_TRANG_THAI[tu.trang_thai_chuyen]?.toLowerCase()}: không cấp thêm, vẫn
                sửa hoặc thu hồi được tới khi quyết toán.
              </p>
            )}
          </>
        ) : (
          <p className="ghi-chu">
            Chọn chuyến đã chốt hoặc đang chạy để cấp; chuyến đã về để sửa hoặc thu hồi.
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
      </div>

      {tu && (
        <div className="kinh bang-khung dm">
          <table>
            <thead>
              <tr>
                <th>Lúc cấp</th>
                <th>Tài xế</th>
                <th className="so">Số tiền</th>
                <th>Hình thức</th>
                <th>Trạng thái</th>
                <th>
                  <span className="an-chu">Thao tác</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {tu.khoan.map((k) =>
                dangSua === k.id ? (
                  <SuaKhoan
                    key={k.id}
                    k={k}
                    onLuu={(so, ht, lyDo) =>
                      lam(() => suaTamUng(k.id, so, ht, lyDo), `Đã sửa thành ${dong(so)}`)
                    }
                    onThoi={() => setDangSua(null)}
                    dangGui={dangGui}
                  />
                ) : (
                  <tr key={k.id}>
                    <td>{ngayGio(k.tao_luc)}</td>
                    <td>{k.ten_tai_xe}</td>
                    <td className="so">{dong(k.so_tien)}</td>
                    <td>{TEN_HINH_THUC[k.hinh_thuc]}</td>
                    <td>
                      {k.trang_thai === 'HIEU_LUC' ? (
                        <Nhan loai="HOAN_THANH">Hiệu lực</Nhan>
                      ) : (
                        <Nhan loai="HUY">Đã thu hồi</Nhan>
                      )}
                    </td>
                    <td className="hanh-dong so">
                      {suaDuoc && k.trang_thai === 'HIEU_LUC' && (
                        <>
                          <button
                            className="phu"
                            disabled={dangGui}
                            onClick={() => setDangSua(k.id)}
                          >
                            Sửa
                          </button>
                          <button className="phu" disabled={dangGui} onClick={() => void thuHoi(k)}>
                            Thu hồi
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ),
              )}
              {tu.khoan.length === 0 && (
                <tr>
                  <td colSpan={6} className="trong">
                    Chưa cấp tạm ứng cho chuyến này
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

// Sửa một khoản: số mới, hình thức, lý do bắt buộc (UC-23 3a); máy chủ kiểm lại BR-53
function SuaKhoan({
  k,
  onLuu,
  onThoi,
  dangGui,
}: {
  k: KhoanTamUng
  dangGui: boolean
  onLuu: (so: number, ht: HinhThuc, lyDo: string) => Promise<void>
  onThoi: () => void
}) {
  const [so, setSo] = useState(String(k.so_tien))
  const [ht, setHt] = useState<HinhThuc>(k.hinh_thuc)
  const [lyDo, setLyDo] = useState('')
  return (
    <tr>
      <td>{ngayGio(k.tao_luc)}</td>
      <td>{k.ten_tai_xe}</td>
      <td>
        <input
          type="number"
          min={1}
          step={1}
          aria-label="Số tiền mới"
          value={so}
          onChange={(e) => setSo(e.target.value)}
        />
      </td>
      <td>
        <select
          aria-label="Hình thức"
          value={ht}
          onChange={(e) => setHt(e.target.value as HinhThuc)}
        >
          {Object.entries(TEN_HINH_THUC).map(([ma, ten]) => (
            <option key={ma} value={ma}>
              {ten}
            </option>
          ))}
        </select>
      </td>
      <td>
        <input
          aria-label="Lý do sửa"
          placeholder="Lý do sửa"
          maxLength={300}
          value={lyDo}
          onChange={(e) => setLyDo(e.target.value)}
        />
      </td>
      <td className="hanh-dong">
        <button
          disabled={dangGui || !lyDo.trim() || !so}
          onClick={() => void onLuu(Number(so), ht, lyDo)}
        >
          Lưu
        </button>
        <button className="phu" onClick={onThoi}>
          Thôi
        </button>
      </td>
    </tr>
  )
}
