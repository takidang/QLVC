import { useCallback, useEffect, useRef, useState } from 'react'
import { TEN_LOAI_CHI, TEN_TRANG_THAI_CHI } from '../../api/chiPhi'
import { danhSachChuyen, type Chuyen } from '../../api/chuyen'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import {
  bangQuyetToan,
  duyetChi,
  linkAnh,
  quyetToan,
  TEN_XU_LY,
  tuChoiChi,
  type BangQuyetToan,
  type KhoanChiQt,
} from '../../api/quyetToan'
import { TEN_HINH_THUC, type HinhThuc } from '../../api/tamUng'
import { ngayGio } from '../../api/toi'

const dong = (so: number) => `${so.toLocaleString('vi-VN')} đ`
const lit = (s: string | null) => (s === null ? '–' : `${Number(s).toLocaleString('vi-VN')} lít`)
const thongBaoLoi = (err: unknown) => {
  const truong = Object.values(loiTheoTruong(err))
  if (truong.length) return truong.join('; ')
  return err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại'
}
// Giờ hiện tại cho ô datetime-local (giờ máy, không múi giờ)
const bayGio = () => {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

// UC-24: Kế toán duyệt từng khoản chi rồi khóa sổ chuyến; Quản lý chỉ xem (quyết định 8)
export default function QuyetToan({ chiXem = false }: { chiXem?: boolean }) {
  const [loc, setLoc] = useState<'HOAN_THANH' | 'DA_QUYET_TOAN'>('HOAN_THANH')
  const [dsChuyen, setDsChuyen] = useState<Chuyen[]>([])
  const [chuyenId, setChuyenId] = useState('')
  const [bang, setBang] = useState<BangQuyetToan | null>(null)
  const [dangXet, setDangXet] = useState<number | null>(null)
  const [anh, setAnh] = useState<string | null>(null)
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  const chuyenDangXem = useRef(0)

  const taiDs = useCallback(() => {
    // shortcut: 100 chuyến mỗi lần, đủ cho nhà xe khoảng 10 xe
    danhSachChuyen({ trang_thai: loc, so_dong: 100 })
      .then((d) => setDsChuyen(d.du_lieu))
      .catch(() => setLoi('Không tải được danh sách chuyến'))
  }, [loc])
  useEffect(taiDs, [taiDs])

  const tai = useCallback((id: number) => {
    chuyenDangXem.current = id
    bangQuyetToan(id)
      .then((b) => chuyenDangXem.current === id && setBang(b))
      .catch(
        (e) =>
          chuyenDangXem.current === id &&
          setLoi(e instanceof LoiApi ? e.message : 'Không tải được bảng quyết toán'),
      )
  }, [])

  function chonChuyen(id: string) {
    setChuyenId(id)
    setBang(null)
    setDangXet(null)
    setThongBao('')
    setLoi('')
    if (id) tai(Number(id))
    else chuyenDangXem.current = 0
  }

  async function lam(viec: () => Promise<unknown>, xong: string) {
    if (dangGui) return false
    setThongBao('')
    setLoi('')
    setDangGui(true)
    try {
      await viec()
      setThongBao(xong)
      setDangXet(null)
      tai(Number(chuyenId))
      return true
    } catch (err) {
      setLoi(thongBaoLoi(err))
      return false
    } finally {
      setDangGui(false)
    }
  }

  async function xemAnh(tep_id: number) {
    try {
      setAnh((await linkAnh(tep_id)).url)
    } catch (e) {
      setLoi(e instanceof LoiApi ? e.message : 'Không mở được ảnh')
    }
  }

  const ghiDuoc = !chiXem && bang?.trang_thai === 'HOAN_THANH'
  const tamTinh = bang?.can_luong_tay && bang.trang_thai === 'HOAN_THANH'

  return (
    <section className="noi-dung">
      <h1>Quyết toán chuyến</h1>
      <p className="ghi-chu">
        Duyệt từng khoản chi tài xế khai, ghi cách xử lý chênh lệch tạm ứng rồi quyết toán. Quyết
        toán xong, mọi số tiền của chuyến chỉ còn xem (BR-29).
      </p>
      <div className="hanh-dong">
        {(['HOAN_THANH', 'DA_QUYET_TOAN'] as const).map((tt) => (
          <button
            key={tt}
            className={loc === tt ? '' : 'phu'}
            onClick={() => {
              setLoc(tt)
              chonChuyen('')
            }}
          >
            {tt === 'HOAN_THANH' ? 'Chờ quyết toán' : 'Đã quyết toán'}
          </button>
        ))}
      </div>
      <label className="o-nhap">
        Chuyến
        <select value={chuyenId} onChange={(e) => chonChuyen(e.target.value)}>
          <option value="">
            {dsChuyen.length ? '– Chọn chuyến –' : '– Không có chuyến nào –'}
          </option>
          {dsChuyen.map((c) => (
            <option key={c.id} value={c.id}>
              {c.ma_chuyen} · {c.ma_tuyen} · {c.bien_so} · {c.ten_tai_xe}
            </option>
          ))}
        </select>
      </label>

      {thongBao && <p className="thanh-cong">{thongBao}</p>}
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}

      {bang && (
        <>
          <p>
            <strong>{bang.ma_chuyen}</strong> · {bang.ten_tuyen} · Xe {bang.bien_so} · Tài xế{' '}
            {bang.ten_tai_xe}
          </p>
          {bang.ket_thuc_bat_thuong && (
            <p className="canh-bao">
              Chuyến kết thúc do sự cố: {bang.ly_do_ket_thuc ?? 'không ghi lý do'}. Lương tài xế
              nhập tay (BR-68).
            </p>
          )}

          <h2>Doanh thu {dong(bang.doanh_thu)}</h2>
          <table>
            <thead>
              <tr>
                <th>Đơn</th>
                <th>Khách</th>
                <th>Cước</th>
                <th>Doanh thu ghi nhận</th>
              </tr>
            </thead>
            <tbody>
              {[...bang.don_giao, ...bang.don_that_bai].map((d) => {
                const giao = bang.don_giao.includes(d)
                return (
                  <tr key={d.id}>
                    <td className="bien-so">{d.ma_don}</td>
                    <td>{d.ten_khach}</td>
                    <td>{dong(d.cuoc)}</td>
                    <td>{giao ? dong(d.cuoc) : <span className="loi">0 – giao thất bại</span>}</td>
                  </tr>
                )
              })}
              {bang.don_giao.length + bang.don_that_bai.length === 0 && (
                <tr>
                  <td colSpan={4} className="trong">
                    Chuyến chạy rỗng
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <h2>Chi phí so với định mức</h2>
          <table>
            <thead>
              <tr>
                <th>Loại</th>
                <th>Định mức</th>
                <th>Thực tế (đã duyệt)</th>
                <th>Chênh lệch</th>
              </tr>
            </thead>
            <tbody>
              {bang.chi_theo_loai.map((x) => (
                <tr key={x.loai}>
                  <td>{TEN_LOAI_CHI[x.loai]}</td>
                  <td>{dong(x.dinh_muc)}</td>
                  <td>{dong(x.thuc_te)}</td>
                  <td className={x.chenh_lech > 0 ? 'loi' : ''}>
                    {x.chenh_lech > 0 ? '+' : ''}
                    {dong(x.chenh_lech)}
                  </td>
                </tr>
              ))}
              <tr>
                <th>Tổng</th>
                <th>{dong(bang.dinh_muc)}</th>
                <th>{dong(bang.tong_chi)}</th>
                <th>
                  {bang.tong_chi > bang.dinh_muc ? '+' : ''}
                  {dong(bang.tong_chi - bang.dinh_muc)}
                </th>
              </tr>
            </tbody>
          </table>
          <p className="ghi-chu">
            Dầu: {bang.km === null ? 'chưa có km' : `${bang.km} km`} · tham khảo{' '}
            {lit(bang.dau_tham_khao_lit)} · thực tế {lit(bang.dau_thuc_te_lit)} (chỉ để xem)
          </p>

          <h2>Khoản chi tài xế khai</h2>
          {bang.so_cho_duyet > 0 && (
            <p className="canh-bao">Còn {bang.so_cho_duyet} khoản chờ duyệt.</p>
          )}
          <table>
            <thead>
              <tr>
                <th>Loại</th>
                <th>Ghi chú</th>
                <th>Số khai</th>
                <th>Số duyệt</th>
                <th>Trạng thái</th>
                <th>Ảnh</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {bang.khoan.map((k) =>
                dangXet === k.id ? (
                  <XetKhoan
                    key={k.id}
                    k={k}
                    dangGui={dangGui}
                    onDuyet={(so, lyDo) =>
                      lam(() => duyetChi(k.id, so, lyDo), `Đã duyệt ${dong(so)}`)
                    }
                    onTuChoi={(lyDo) => lam(() => tuChoiChi(k.id, lyDo), 'Đã từ chối khoản chi')}
                    onThoi={() => setDangXet(null)}
                  />
                ) : (
                  <tr key={k.id}>
                    <td>
                      {TEN_LOAI_CHI[k.loai]}
                      {k.so_lit !== null && ` · ${lit(k.so_lit)}`}
                    </td>
                    <td>{k.ghi_chu}</td>
                    <td>{dong(k.so_tien_khai)}</td>
                    <td>{k.so_tien_duyet === null ? '–' : dong(k.so_tien_duyet)}</td>
                    <td>{TEN_TRANG_THAI_CHI[k.trang_thai]}</td>
                    <td className="hanh-dong">
                      {k.anh.map((t, i) => (
                        <button key={t} className="phu" onClick={() => void xemAnh(t)}>
                          Ảnh {i + 1}
                        </button>
                      ))}
                    </td>
                    <td className="hanh-dong">
                      {ghiDuoc && (
                        <button
                          className={k.trang_thai === 'CHO_DUYET' ? '' : 'phu'}
                          disabled={dangGui}
                          onClick={() => setDangXet(k.id)}
                        >
                          {k.trang_thai === 'CHO_DUYET' ? 'Xét' : 'Đổi'}
                        </button>
                      )}
                    </td>
                  </tr>
                ),
              )}
              {bang.khoan.length === 0 && (
                <tr>
                  <td colSpan={7} className="trong">
                    Tài xế không khai khoản chi nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <h2>Kết quả</h2>
          <table>
            <tbody>
              <tr>
                <td>Doanh thu</td>
                <td>{dong(bang.doanh_thu)}</td>
              </tr>
              <tr>
                <td>Chi phí đã duyệt</td>
                <td>− {dong(bang.tong_chi)}</td>
              </tr>
              <tr>
                <td>
                  Lương tài xế {bang.luong_tai_xe !== bang.luong_chot ? '(nhập tay)' : '(đã chốt)'}
                  {bang.ly_do_luong_tay && ` – ${bang.ly_do_luong_tay}`}
                </td>
                <td>− {dong(bang.luong_tai_xe)}</td>
              </tr>
              <tr>
                <th>
                  Lãi chuyến
                  {/* Kết thúc do sự cố: lương thật nhập lúc quyết toán (BR-68), giờ tạm lấy lương đã chốt */}
                  {tamTinh && (
                    <span className="ghi-chu"> (tạm tính, lương nhập lúc quyết toán)</span>
                  )}
                </th>
                <th className={bang.lai < 0 ? 'loi' : ''}>{dong(bang.lai)}</th>
              </tr>
              <tr>
                <td>Lãi dự kiến lúc chốt</td>
                <td>{dong(bang.lai_du_kien)}</td>
              </tr>
            </tbody>
          </table>
          {bang.ly_do_lech.length > 0 && (
            <ul className="ghi-chu">
              {bang.ly_do_lech.map((x) => (
                <li key={x.mo_ta}>
                  {x.mo_ta}: {x.so_tien > 0 ? '+' : ''}
                  {dong(x.so_tien)}
                </li>
              ))}
            </ul>
          )}
          <p>
            Tạm ứng còn hiệu lực <strong>{dong(bang.tong_tam_ung_hieu_luc)}</strong> · Chênh lệch{' '}
            <strong>{dong(bang.chenh_lech_tam_ung)}</strong>:{' '}
            {bang.chenh_lech_tam_ung > 0
              ? `tài xế nộp lại ${dong(bang.chenh_lech_tam_ung)}`
              : bang.chenh_lech_tam_ung < 0
                ? `công ty trả thêm ${dong(-bang.chenh_lech_tam_ung)}`
                : 'không chênh'}
          </p>

          {bang.trang_thai === 'DA_QUYET_TOAN' && (
            <p className="thanh-cong">
              Đã quyết toán {bang.luc_quyet_toan && ngayGio(bang.luc_quyet_toan)} ·{' '}
              {bang.xu_ly_chenh_lech && TEN_XU_LY[bang.xu_ly_chenh_lech]}
              {bang.hinh_thuc && ` · ${TEN_HINH_THUC[bang.hinh_thuc]}`}
              {bang.luc_xu_ly && ` lúc ${ngayGio(bang.luc_xu_ly)}`}
            </p>
          )}
          {ghiDuoc && (
            <FormQuyetToan
              key={bang.chuyen_id}
              bang={bang}
              dangGui={dangGui}
              onGui={(vao) =>
                lam(() => quyetToan(bang.chuyen_id, vao), `Đã quyết toán ${bang.ma_chuyen}`).then(
                  (xong) => xong && taiDs(),
                )
              }
            />
          )}
        </>
      )}

      {anh && (
        <div className="nen-mo" onClick={() => setAnh(null)}>
          <div className="hop-thoai" onClick={(e) => e.stopPropagation()}>
            <img src={anh} alt="Ảnh chứng từ" style={{ maxWidth: '100%' }} />
            <button className="phu" onClick={() => setAnh(null)}>
              Đóng
            </button>
          </div>
        </div>
      )}
    </section>
  )
}

// Duyệt (số mặc định = số khai; giảm thì bắt buộc lý do – quyết định 3) hoặc từ chối (lý do bắt buộc)
function XetKhoan({
  k,
  dangGui,
  onDuyet,
  onTuChoi,
  onThoi,
}: {
  k: KhoanChiQt
  dangGui: boolean
  onDuyet: (so: number, lyDo: string) => Promise<boolean>
  onTuChoi: (lyDo: string) => Promise<boolean>
  onThoi: () => void
}) {
  const [so, setSo] = useState(String(k.so_tien_duyet ?? k.so_tien_khai))
  const [lyDo, setLyDo] = useState('')
  const canLyDo = Number(so) !== k.so_tien_khai
  return (
    <tr>
      <td>{TEN_LOAI_CHI[k.loai]}</td>
      <td>{k.ghi_chu}</td>
      <td>{dong(k.so_tien_khai)}</td>
      <td>
        <input
          type="number"
          min={1}
          max={k.so_tien_khai}
          step={1}
          aria-label="Số duyệt"
          value={so}
          onChange={(e) => setSo(e.target.value)}
        />
      </td>
      <td colSpan={2}>
        <input
          aria-label="Lý do"
          placeholder={canLyDo ? 'Lý do điều chỉnh (bắt buộc)' : 'Lý do (bắt buộc khi từ chối)'}
          maxLength={300}
          value={lyDo}
          onChange={(e) => setLyDo(e.target.value)}
        />
      </td>
      <td className="hanh-dong">
        <button
          disabled={dangGui || !so || (canLyDo && !lyDo.trim())}
          onClick={() => void onDuyet(Number(so), lyDo.trim())}
        >
          Duyệt
        </button>
        <button
          className="phu"
          disabled={dangGui || !lyDo.trim()}
          onClick={() => void onTuChoi(lyDo.trim())}
        >
          Từ chối
        </button>
        <button className="phu" onClick={onThoi}>
          Thôi
        </button>
      </td>
    </tr>
  )
}

// Khối khóa sổ: lương tay khi kết thúc do sự cố (BR-68), cách xử lý chênh lệch theo dấu (BR-55)
function FormQuyetToan({
  bang,
  dangGui,
  onGui,
}: {
  bang: BangQuyetToan
  dangGui: boolean
  onGui: (vao: Parameters<typeof quyetToan>[1]) => Promise<unknown>
}) {
  const [hinhThuc, setHinhThuc] = useState<HinhThuc>('TIEN_MAT')
  const [luc, setLuc] = useState(bayGio())
  const [luong, setLuong] = useState(String(bang.luong_chot))
  const [lyDoLuong, setLyDoLuong] = useState('')
  const chenh = bang.chenh_lech_tam_ung
  const thieu =
    bang.so_cho_duyet > 0
      ? `Còn ${bang.so_cho_duyet} khoản chờ duyệt`
      : bang.can_luong_tay && (!luong || !lyDoLuong.trim())
        ? 'Nhập lương tài xế và lý do'
        : chenh !== 0 && !luc
          ? 'Nhập thời điểm xử lý chênh lệch'
          : ''

  function gui() {
    const cau =
      chenh > 0
        ? `Tài xế đã nộp lại ${dong(chenh)}`
        : chenh < 0
          ? `Công ty đã trả thêm ${dong(-chenh)}`
          : 'Không có chênh lệch tạm ứng'
    if (!window.confirm(`Quyết toán ${bang.ma_chuyen}? ${cau}. Sau đó không sửa được nữa.`)) return
    void onGui({
      xu_ly_chenh_lech: bang.xu_ly_goi_y,
      ...(chenh !== 0 && { hinh_thuc: hinhThuc, luc_xu_ly: new Date(luc).toISOString() }),
      ...(bang.can_luong_tay && { luong_tay: Number(luong), ly_do_luong_tay: lyDoLuong.trim() }),
    })
  }

  return (
    <div className="o-nhap">
      {bang.can_luong_tay && (
        <>
          <label>
            Lương tài xế (đồng)
            <input
              type="number"
              min={0}
              step={1}
              value={luong}
              onChange={(e) => setLuong(e.target.value)}
            />
          </label>
          <label>
            Lý do lương nhập tay
            <input
              maxLength={300}
              value={lyDoLuong}
              onChange={(e) => setLyDoLuong(e.target.value)}
            />
          </label>
        </>
      )}
      {chenh !== 0 && (
        <>
          <p>
            <strong>{TEN_XU_LY[bang.xu_ly_goi_y]}</strong> {dong(Math.abs(chenh))}
          </p>
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
          <label>
            Lúc xử lý
            <input
              type="datetime-local"
              value={luc}
              max={bayGio()}
              onChange={(e) => setLuc(e.target.value)}
            />
          </label>
        </>
      )}
      {thieu && <p className="ghi-chu">{thieu}</p>}
      <button disabled={dangGui || !!thieu} onClick={gui}>
        {dangGui ? 'Đang lưu…' : 'Quyết toán'}
      </button>
    </div>
  )
}
