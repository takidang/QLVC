import { useCallback, useEffect, useState } from 'react'
import {
  danhDauDaThu,
  danhSachPhaiThu,
  noTheoKhach,
  type NoTheoKhach,
  type PhaiThu,
} from '../../api/congNo'
import { LoiApi } from '../../api/goi'
import { ngayGio } from '../../api/toi'

const dong = (so: number) => `${so.toLocaleString('vi-VN')} đ`
// Ngày theo giờ máy người dùng (Việt Nam), không theo UTC: sáng sớm không bị lùi một ngày
const homNay = () => new Date().toLocaleDateString('sv-SE') // YYYY-MM-DD
const ngayVN = (iso: string) => iso.split('-').reverse().join('/')

// UC-25: nợ theo khách → chọn khách → tích các khoản chưa thu → ngày thu → đánh dấu đã thu (một phiếu thu, BR-56)
// chiXem: Quản lý xem, không đánh dấu đã thu (góp ý của Tài 10/11)
export default function CongNo({ chiXem = false }: { chiXem?: boolean }) {
  const [no, setNo] = useState<NoTheoKhach[]>([])
  const [khach, setKhach] = useState<NoTheoKhach | null>(null)
  const [xem, setXem] = useState<'CHUA_THU' | 'DA_THU'>('CHUA_THU')
  const [khoan, setKhoan] = useState<PhaiThu[]>([])
  const [chon, setChon] = useState<Set<number>>(new Set())
  const [ngay, setNgay] = useState(homNay())
  const [dangGui, setDangGui] = useState(false)
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')

  const taiNo = useCallback(() => {
    noTheoKhach()
      .then(setNo)
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được công nợ'))
  }, [])
  useEffect(taiNo, [taiNo])

  const taiKhoan = useCallback(() => {
    if (!khach) return // bảng khoản chỉ hiện sau khi chọn khách
    let bo = false // đổi khách / bộ lọc nhanh: kết quả cũ về muộn thì bỏ
    // shortcut: 100 khoản mỗi khách, đủ cho nhà xe nhỏ; nhiều hơn thì thêm phân trang
    danhSachPhaiThu({ khach_hang_id: khach.khach_hang_id, trang_thai_tt: xem, so_dong: 100 })
      .then((ds) => !bo && setKhoan(ds.du_lieu))
      .catch(
        (e) => !bo && setLoi(e instanceof LoiApi ? e.message : 'Không tải được khoản phải thu'),
      )
    return () => {
      bo = true
    }
  }, [khach, xem])
  useEffect(taiKhoan, [taiKhoan])

  function chonKhach(k: NoTheoKhach) {
    setKhach(k)
    setXem('CHUA_THU')
    setChon(new Set())
    setThongBao('')
    setLoi('')
  }

  function tich(id: number) {
    const moi = new Set(chon)
    if (moi.has(id)) moi.delete(id)
    else moi.add(id)
    setChon(moi)
  }

  const tongChon = khoan.filter((k) => chon.has(k.id)).reduce((t, k) => t + k.so_tien, 0)

  async function danhDau() {
    if (!khach || !chon.size) return
    if (
      !window.confirm(
        `Đã thu ${dong(tongChon)} của ${khach.ten_khach} (${chon.size} khoản) ngày ${ngayVN(ngay)}?`,
      )
    )
      return
    setDangGui(true)
    setThongBao('')
    setLoi('')
    try {
      const r = await danhDauDaThu([...chon], ngay)
      setThongBao(`Đã lập phiếu thu #${r.phieu_thu_id}: ${dong(r.tong_tien)} (${r.so_khoan} khoản)`)
      setChon(new Set())
      taiNo()
      taiKhoan()
    } catch (err) {
      setLoi(err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')
    } finally {
      setDangGui(false)
    }
  }

  return (
    <section className="noi-dung">
      <h1>Công nợ khách hàng</h1>
      <p className="ghi-chu">
        Mỗi đơn giao xong sinh một khoản phải thu bằng cước. Khách trả thì chọn các khoản của khách
        đó và đánh dấu đã thu: hệ thống lập một phiếu thu, trạng thái đơn không đổi (BR-56).
      </p>
      {thongBao && <p className="thanh-cong">{thongBao}</p>}
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}

      <h2>Nợ theo khách</h2>
      <table>
        <thead>
          <tr>
            <th>Khách</th>
            <th>Số khoản chưa thu</th>
            <th>Tổng nợ</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {no.map((k) => (
            <tr key={k.khach_hang_id}>
              <td>{k.ten_khach}</td>
              <td>{k.so_khoan}</td>
              <td>{dong(k.tong_no)}</td>
              <td>
                <button className="phu" onClick={() => chonKhach(k)}>
                  Xem
                </button>
              </td>
            </tr>
          ))}
          {no.length === 0 && (
            <tr>
              <td colSpan={4} className="trong">
                Không khách nào còn nợ
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {khach && (
        <>
          <h2>Khoản của {khach.ten_khach}</h2>
          <div className="hanh-dong">
            <button className={xem === 'CHUA_THU' ? '' : 'phu'} onClick={() => setXem('CHUA_THU')}>
              Chưa thu
            </button>
            <button className={xem === 'DA_THU' ? '' : 'phu'} onClick={() => setXem('DA_THU')}>
              Đã thu
            </button>
          </div>
          <table>
            <thead>
              <tr>
                {!chiXem && xem === 'CHUA_THU' && <th></th>}
                <th>Mã đơn</th>
                <th>Giao lúc</th>
                <th>Số tiền</th>
                {xem === 'DA_THU' && <th>Phiếu thu</th>}
              </tr>
            </thead>
            <tbody>
              {khoan.map((k) => (
                <tr key={k.id}>
                  {!chiXem && xem === 'CHUA_THU' && (
                    <td>
                      <input
                        type="checkbox"
                        aria-label={`Chọn ${k.ma_don}`}
                        checked={chon.has(k.id)}
                        onChange={() => tich(k.id)}
                      />
                    </td>
                  )}
                  <td className="bien-so">{k.ma_don}</td>
                  <td>{k.ngay_giao ? ngayGio(k.ngay_giao) : '–'}</td>
                  <td>{dong(k.so_tien)}</td>
                  {xem === 'DA_THU' && (
                    <td>
                      #{k.phieu_thu_id} · {k.ngay_thu && ngayVN(k.ngay_thu)}
                    </td>
                  )}
                </tr>
              ))}
              {khoan.length === 0 && (
                <tr>
                  <td colSpan={5} className="trong">
                    {xem === 'CHUA_THU' ? 'Không còn khoản chưa thu' : 'Chưa thu khoản nào'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {!chiXem && xem === 'CHUA_THU' && khoan.length > 0 && (
            <div className="o-nhap">
              <p>
                Đã chọn <strong>{chon.size}</strong> khoản · <strong>{dong(tongChon)}</strong>
              </p>
              <label>
                Ngày thu
                <input
                  type="date"
                  value={ngay}
                  max={homNay()}
                  required
                  onChange={(e) => setNgay(e.target.value)}
                />
              </label>
              <button disabled={dangGui || !chon.size || !ngay} onClick={() => void danhDau()}>
                {dangGui ? 'Đang lưu…' : 'Đánh dấu đã thu'}
              </button>
            </div>
          )}
        </>
      )}
    </section>
  )
}
