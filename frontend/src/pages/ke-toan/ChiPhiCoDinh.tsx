import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachXe, datChiPhiCoDinh, xemChiPhiCoDinh, type Xe } from '../../api/xe'
import { DauDanhMuc } from '../danh-muc'

// Tháng theo giờ máy người dùng (Việt Nam), không theo UTC: đầu tháng không bị chọn nhầm tháng trước
const thangNay = () => new Date().toLocaleDateString('sv-SE').slice(0, 7) // YYYY-MM

export default function ChiPhiCoDinh() {
  const [dsXe, setDsXe] = useState<Xe[]>([])
  const [xeId, setXeId] = useState('')
  const [thang, setThang] = useState(thangNay())
  const [daLuu, setDaLuu] = useState<number | null>(null)
  const [soTien, setSoTien] = useState('')
  const [thongBao, setThongBao] = useState('')
  const [loi, setLoi] = useState('')

  useEffect(() => {
    // shortcut: lấy tối đa 100 xe một lần, đủ cho nhà xe khoảng 10 xe; nhiều hơn thì thêm ô tìm
    danhSachXe({ so_dong: 100 })
      .then((ds) => setDsXe(ds.du_lieu))
      .catch(() => setLoi('Không tải được danh sách xe'))
  }, [])

  useEffect(() => {
    if (!xeId || !thang) return
    let bo = false // đổi xe/tháng nhanh: số của lựa chọn cũ về muộn thì bỏ, không hiện nhầm dưới xe khác
    xemChiPhiCoDinh(Number(xeId), thang)
      .then((r) => {
        if (bo) return
        setDaLuu(r.so_tien)
        setSoTien(r.so_tien === null ? '' : String(r.so_tien))
      })
      .catch((e) => {
        if (!bo) setLoi(e instanceof LoiApi ? e.message : 'Không tải được chi phí')
      })
    return () => {
      bo = true
    }
  }, [xeId, thang])

  async function luu(e: FormEvent) {
    e.preventDefault()
    setLoi('')
    setThongBao('')
    try {
      const r = await datChiPhiCoDinh(Number(xeId), thang, Number(soTien))
      setDaLuu(r.so_tien)
      setThongBao('Đã lưu')
    } catch (err) {
      setLoi(
        loiTheoTruong(err).so_tien ??
          (err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại'),
      )
    }
  }

  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Chi phí cố định xe"
        phu="Khấu hao, bảo hiểm, phí đường bộ… tính theo tháng; dùng cho lãi theo xe (không vào lãi chuyến)."
      />
      <div className="kinh dm-the">
        <form className="o-nhap" onSubmit={luu}>
          <label>
            Xe
            <select
              value={xeId}
              onChange={(e) => {
                setXeId(e.target.value)
                setThongBao('')
                setLoi('')
              }}
              required
            >
              <option value="">– Chọn xe –</option>
              {dsXe.map((x) => (
                <option key={x.id} value={x.id}>
                  {x.bien_so}
                  {x.trang_thai === 'NGUNG' ? ' (ngừng)' : ''}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tháng
            <input
              type="month"
              value={thang}
              onChange={(e) => {
                setThang(e.target.value)
                setThongBao('')
                setLoi('')
              }}
              required
            />
          </label>
          <label>
            Số tiền (đồng)
            <input
              type="number"
              min={0}
              step={1000}
              value={soTien}
              onChange={(e) => setSoTien(e.target.value)}
              required
              disabled={!xeId}
            />
          </label>
          <button disabled={!xeId}>Lưu</button>
        </form>
        {!xeId ? (
          <p className="ghi-chu">Chọn xe và tháng để xem số đã lưu hoặc nhập mới.</p>
        ) : daLuu === null ? (
          <p className="ghi-chu">Chưa nhập cho tháng {thang.split('-').reverse().join('/')}.</p>
        ) : (
          <div className="so-lieu dm-so">
            <div>
              <b>{daLuu.toLocaleString('vi-VN')} đ</b>
              <span>đã lưu cho tháng {thang.split('-').reverse().join('/')}</span>
            </div>
          </div>
        )}
        {thongBao && <p className="thanh-cong">{thongBao}</p>}
        {loi && (
          <p role="alert" className="loi">
            {loi}
          </p>
        )}
      </div>
    </section>
  )
}
