import { useCallback, useEffect, useState, type FormEvent } from 'react'
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

  useEffect(() => {
    // shortcut: 100 chuyến mỗi trạng thái, đủ cho nhà xe khoảng 10 xe
    Promise.all(SUA_DUOC.map((trang_thai) => danhSachChuyen({ trang_thai, so_dong: 100 })))
      .then((ds) => setDsChuyen(ds.flatMap((d) => d.du_lieu)))
      .catch(() => setLoi('Không tải được danh sách chuyến'))
  }, [])

  const tai = useCallback((id: number) => {
    tamUngChuyen(id)
      .then((r) => {
        setTu(r)
        setSoTien(String(r.con_duoc_cap)) // gợi ý = định mức − đã cấp còn hiệu lực (UC-23 bước 1)
      })
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được tạm ứng'))
  }, [])

  function chonChuyen(id: string) {
    setChuyenId(id)
    setTu(null)
    setDangSua(null)
    setThongBao('')
    setLoi('')
    if (id) tai(Number(id))
  }

  async function lam(viec: () => Promise<unknown>, xong: string, truong = 'so_tien') {
    setThongBao('')
    setLoi('')
    try {
      await viec()
      setThongBao(xong)
      setDangSua(null)
      tai(Number(chuyenId))
    } catch (err) {
      setLoi(thongBaoLoi(err, truong))
    }
  }

  function cap(e: FormEvent) {
    e.preventDefault()
    void lam(
      () => capTamUng(Number(chuyenId), Number(soTien), hinhThuc),
      `Đã cấp ${dong(Number(soTien))}`,
    )
  }

  function thuHoi(k: KhoanTamUng) {
    if (!window.confirm(`Tài xế ${k.ten_tai_xe} đã nộp lại ${dong(k.so_tien)}?`)) return
    void lam(() => thuHoiTamUng(k.id), `Đã thu hồi ${dong(k.so_tien)}`)
  }

  const capDuoc = tu && CAP_DUOC.includes(tu.trang_thai_chuyen)
  const suaDuoc = tu && SUA_DUOC.includes(tu.trang_thai_chuyen)

  return (
    <section className="noi-dung">
      <h1>Tạm ứng chuyến</h1>
      <p className="ghi-chu">
        Tổng tạm ứng còn hiệu lực không vượt định mức chi phí đã chốt của chuyến (dầu + cầu đường +
        bốc xếp, BR-53). Muốn mở chốt hoặc hủy chuyến thì thu hồi trước.
      </p>
      <label className="o-nhap">
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
        <>
          <p>
            Định mức đã chốt <strong>{dong(tu.dinh_muc)}</strong> · Đã cấp còn hiệu lực{' '}
            <strong>{dong(tu.tong_hieu_luc)}</strong> · Còn được cấp{' '}
            <strong>{dong(tu.con_duoc_cap)}</strong>
          </p>
          {capDuoc ? (
            <form className="o-nhap" onSubmit={cap}>
              <label>
                Số tiền (đồng)
                <input
                  type="number"
                  min={1}
                  step={1000}
                  value={soTien}
                  onChange={(e) => setSoTien(e.target.value)}
                  required
                />
              </label>
              <label>
                Hình thức
                <select value={hinhThuc} onChange={(e) => setHinhThuc(e.target.value as HinhThuc)}>
                  {Object.entries(TEN_HINH_THUC).map(([ma, ten]) => (
                    <option key={ma} value={ma}>
                      {ten}
                    </option>
                  ))}
                </select>
              </label>
              <button>Cấp tạm ứng</button>
            </form>
          ) : (
            <p className="ghi-chu">
              Chuyến {TEN_TRANG_THAI[tu.trang_thai_chuyen]?.toLowerCase()}: không cấp thêm, vẫn sửa
              hoặc thu hồi được tới khi quyết toán.
            </p>
          )}
        </>
      )}
      {thongBao && <p className="thanh-cong">{thongBao}</p>}
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}

      {tu && (
        <table>
          <thead>
            <tr>
              <th>Lúc cấp</th>
              <th>Tài xế</th>
              <th>Số tiền</th>
              <th>Hình thức</th>
              <th>Trạng thái</th>
              <th></th>
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
                />
              ) : (
                <tr key={k.id}>
                  <td>{ngayGio(k.tao_luc)}</td>
                  <td>{k.ten_tai_xe}</td>
                  <td>{dong(k.so_tien)}</td>
                  <td>{TEN_HINH_THUC[k.hinh_thuc]}</td>
                  <td>{k.trang_thai === 'HIEU_LUC' ? 'Hiệu lực' : 'Đã thu hồi'}</td>
                  <td className="hanh-dong">
                    {suaDuoc && k.trang_thai === 'HIEU_LUC' && (
                      <>
                        <button className="phu" onClick={() => setDangSua(k.id)}>
                          Sửa
                        </button>
                        <button className="phu" onClick={() => thuHoi(k)}>
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
      )}
    </section>
  )
}

// Sửa một khoản: số mới, hình thức, lý do bắt buộc (UC-23 3a); máy chủ kiểm lại BR-53
function SuaKhoan({
  k,
  onLuu,
  onThoi,
}: {
  k: KhoanTamUng
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
          step={1000}
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
        <button disabled={!lyDo.trim() || !so} onClick={() => void onLuu(Number(so), ht, lyDo)}>
          Lưu
        </button>
        <button className="phu" onClick={onThoi}>
          Thôi
        </button>
      </td>
    </tr>
  )
}
