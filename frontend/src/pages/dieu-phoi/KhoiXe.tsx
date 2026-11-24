import { useNgayBaoTruoc } from '../../api/cauHinh'
import type { TaiXe } from '../../api/taiXe'
import type { Xe } from '../../api/xe'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'

// Khối "Xe & tài xế" ở chi tiết chuyến (lấy ý "Vehicle Information" của ảnh mẫu, nhưng chỉ dùng dữ liệu
// có thật): thông số xe, km đồng hồ, các thanh "còn bao nhiêu ngày" tới hạn đăng kiểm, bảo hiểm, GPLX.
const NGAY = 86_400_000
const homNay = () => new Date(new Date().toLocaleDateString('sv-SE')).getTime()
const ngayVN = (ymd: string) => ymd.split('-').reverse().join('/')

export default function KhoiXe({ xe, taiXe }: { xe: Xe | null; taiXe: TaiXe | null }) {
  return (
    <section className="kinh ct-khoi khoi-xe">
      <h2>Xe & tài xế</h2>
      {!xe ? (
        phongCachDaLuu() === 'pixel' ? (
          /* Hiệu ứng Pixel: màn tải kiểu Pixel thay chữ Đang tải… */
          <DangTaiPixel kieu="trang" />
        ) : (
          <p className="ghi-chu">Đang tải…</p>
        )
      ) : (
        <>
          <div className="kx-so">
            <div>
              <small>Biển số</small>
              <span className="bien">{xe.bien_so}</span>
            </div>
            <div>
              <small>Tải trọng</small>
              <strong>{xe.tai_trong_kg.toLocaleString('vi-VN')} kg</strong>
            </div>
            <div>
              <small>Thể tích thùng</small>
              <strong>{Number(xe.the_tich_m3).toLocaleString('vi-VN')} m³</strong>
            </div>
            <div>
              <small>Km đồng hồ</small>
              <strong>{xe.km_dong_ho.toLocaleString('vi-VN')}</strong>
            </div>
          </div>
          <ul className="kx-han">
            <Han ten="Đăng kiểm" han={xe.han_dang_kiem} />
            <Han ten="Bảo hiểm" han={xe.han_bao_hiem} />
            {taiXe && (
              <Han
                ten={`GPLX hạng ${taiXe.hang_gplx} · ${taiXe.ho_ten}`}
                han={taiXe.han_gplx}
                phu={
                  <a href={`tel:${taiXe.sdt}`} onClick={(e) => e.stopPropagation()}>
                    {taiXe.sdt}
                  </a>
                }
              />
            )}
          </ul>
        </>
      )}
    </section>
  )
}

// Một hạn giấy tờ: chấm màu + tên + "còn N ngày"; thanh đầy khi còn ≥ 1 năm, ngắn dần khi tới hạn.
// Hết hạn đỏ, còn ≤ CFG-02 ngày cam
function Han({ ten, han, phu }: { ten: string; han: string; phu?: React.ReactNode }) {
  const ngayBaoTruoc = useNgayBaoTruoc()
  const con = Math.round((new Date(han).getTime() - homNay()) / NGAY)
  const muc = con < 0 ? 'het' : con <= ngayBaoTruoc ? 'sap' : 'on'
  return (
    <li className={muc}>
      <div className="kx-dong">
        <strong>{ten}</strong>
        <span>{con < 0 ? `hết hạn ${-con} ngày` : `còn ${con} ngày`}</span>
      </div>
      <small>
        Hạn {ngayVN(han)}
        {phu && <> · {phu}</>}
      </small>
      <span className="kx-thanh">
        <i style={{ width: `${Math.max(0, Math.min(con / 365, 1)) * 100}%` }} />
      </span>
    </li>
  )
}
