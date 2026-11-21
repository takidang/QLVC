import { useEffect, useState } from 'react'
import { danhSachCauHinh, suaCauHinh, type ThamSo } from '../../api/bangGia'
import { LoiApi } from '../../api/goi'
import { DauDanhMuc } from '../danh-muc'

const lucVN = (iso: string) => new Date(iso).toLocaleString('vi-VN')

export default function CauHinh() {
  const [ds, setDs] = useState<ThamSo[]>([])
  const [nhap, setNhap] = useState<Record<string, string>>({})
  const [loi, setLoi] = useState<Record<string, string>>({})
  const [daLuu, setDaLuu] = useState('')
  const [loiTai, setLoiTai] = useState('')

  useEffect(() => {
    danhSachCauHinh()
      .then((r) => {
        setDs(r)
        setNhap(Object.fromEntries(r.map((ts) => [ts.ma, ts.gia_tri])))
      })
      .catch((e) => setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được cấu hình'))
  }, [])

  async function luu(ma: string) {
    setLoi({ ...loi, [ma]: '' })
    setDaLuu('')
    try {
      const r = await suaCauHinh(ma, nhap[ma])
      setDs(r)
      setNhap({ ...nhap, [ma]: r.find((ts) => ts.ma === ma)?.gia_tri ?? nhap[ma] })
      setDaLuu(ma)
    } catch (e) {
      setLoi({ ...loi, [ma]: e instanceof LoiApi ? e.message : 'Không lưu được' })
    }
  }

  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Cấu hình"
        phu="Tham số dùng khi tính cước, lịch trình và cảnh báo (nghiệp vụ mục 3)."
      />
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}
      <div className="kinh bang-khung dm">
        <table>
          <thead>
            <tr>
              <th>Mã</th>
              <th>Tham số</th>
              <th>Giá trị</th>
              <th>Đơn vị</th>
              <th>Sửa lần cuối</th>
              <th>
                <span className="an-chu">Lưu</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {ds.map((ts) => (
              <tr key={ts.ma}>
                <td>
                  <span className="bien">{ts.ma}</span>
                </td>
                <td>{ts.ten}</td>
                <td>
                  <input
                    aria-label={ts.ten}
                    value={nhap[ts.ma] ?? ''}
                    onChange={(e) => setNhap({ ...nhap, [ts.ma]: e.target.value })}
                    size={8}
                  />
                  {loi[ts.ma] && <div className="loi">{loi[ts.ma]}</div>}
                  {daLuu === ts.ma && <div className="thanh-cong">Đã lưu</div>}
                </td>
                <td>{ts.don_vi}</td>
                <td className="ghi-chu">
                  {ts.luc ? `${ts.nguoi_sua ?? ''}, ${lucVN(ts.luc)}` : 'Mặc định'}
                </td>
                <td>
                  <button
                    className="phu"
                    disabled={nhap[ts.ma] === ts.gia_tri}
                    onClick={() => luu(ts.ma)}
                  >
                    Lưu
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
