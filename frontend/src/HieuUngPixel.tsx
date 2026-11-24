import { type CSSProperties } from 'react'
import { dangHieuUngPixel } from './nen'

// Hiệu ứng Pixel: tia laser quét dọc và 4 góc ngắm 8-bit trên khung camera QR
export function TiaLaserPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-laser" aria-hidden="true">
      <span className="px-laser-goc tl" />
      <span className="px-laser-goc tr" />
      <span className="px-laser-goc bl" />
      <span className="px-laser-goc br" />
      <span className="px-laser-thanh" />
    </div>
  )
}

// Hiệu ứng Pixel: con dấu "ĐÃ GIAO" đóng xuống xoay nhẹ, nảy rồi tự mờ sau ~1,2 s
export function ConDauDaGiaoPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-con-dau" aria-hidden="true">
      <span className="px-con-dau-khung">
        <span className="px-con-dau-chu">ĐÃ GIAO</span>
      </span>
    </div>
  )
}

// Hiệu ứng Pixel: hạt bụi ô vuông nhỏ bật ra khi khối hàng rơi xuống sàn thùng xe
export function BuiThaHangPixel({ x, w, y }: { x: number; w: number; y: number }) {
  if (!dangHieuUngPixel()) return null
  const giua = x + w / 2
  return (
    <g className="px-bui-roi" aria-hidden="true">
      <rect x={Math.max(x - 4, 24)} y={y - 6} width={5} height={5} className="px-bui-o" />
      <rect x={giua - 2} y={y - 5} width={4} height={4} className="px-bui-o nhat" />
      <rect x={Math.min(x + w, 444)} y={y - 6} width={5} height={5} className="px-bui-o" />
    </g>
  )
}

const MOC_HANH_TRINH = [
  { ma: 'CHO_GHEP', ten: 'Tiếp nhận' },
  { ma: 'DA_GHEP', ten: 'Xếp chuyến' },
  { ma: 'DA_LAY', ten: 'Vận chuyển' },
  { ma: 'DA_GIAO', ten: 'Đã giao' },
] as const

function viTriHanhTrinh(
  trangThai: string,
  moc: { trang_thai: string; luc: string }[],
): { buoc: number; kieu: 'chay' | 'xong' | 'canh-bao' | 'huy' } {
  if (trangThai === 'CHO_GHEP') return { buoc: 0, kieu: 'chay' }
  if (trangThai === 'DA_GHEP') return { buoc: 1, kieu: 'chay' }
  if (trangThai === 'DA_LAY') return { buoc: 2, kieu: 'chay' }
  if (trangThai === 'DA_GIAO') return { buoc: 3, kieu: 'xong' }
  if (trangThai === 'THAT_BAI' || trangThai === 'TRA_HANG') {
    return { buoc: 2, kieu: 'canh-bao' }
  }
  let buoc = 0
  for (const m of moc) {
    if (m.trang_thai === 'DA_LAY') buoc = Math.max(buoc, 2)
    else if (m.trang_thai === 'DA_GHEP') buoc = Math.max(buoc, 1)
  }
  return { buoc, kieu: trangThai === 'HUY' ? 'huy' : 'chay' }
}

// Hiệu ứng Pixel: dải 4 mốc hành trình và xe tải pixel chạy tới mốc hiện tại ở trang Tra cứu
export function XeTaiHanhTrinhPixel({
  trangThai,
  moc,
}: {
  trangThai: string
  moc: { trang_thai: string; luc: string }[]
}) {
  if (!dangHieuUngPixel()) return null
  const { buoc, kieu } = viTriHanhTrinh(trangThai, moc)
  const tyLe = buoc / (MOC_HANH_TRINH.length - 1)
  const dich = `${(tyLe * 100).toFixed(3)}%`
  const bien = { '--px-xe-dich': dich, '--px-ty-le': String(tyLe) } as CSSProperties

  return (
    <div className={`px-hanh-trinh ${kieu}`} style={bien} aria-hidden="true">
      <div className="px-duong-xe">
        <div className="px-xe-chay-bo">
          <svg
            className="px-xe-tai"
            viewBox="0 0 32 18"
            width={32}
            height={18}
            shapeRendering="crispEdges"
          >
            <rect x={0} y={11} width={2} height={2} className="px-xe-khoi" />
            <rect x={2} y={3} width={18} height={10} className="px-xe-thung" />
            <rect x={4} y={5} width={14} height={2} className="px-xe-soc" />
            <rect x={20} y={5} width={6} height={1} className="px-xe-dau" />
            <rect x={20} y={6} width={9} height={7} className="px-xe-dau" />
            <rect x={23} y={7} width={4} height={3} className="px-xe-kinh" />
            <rect x={1} y={13} width={29} height={2} className="px-xe-gam" />
            <rect x={5} y={14} width={5} height={4} className="px-xe-banh" />
            <rect x={7} y={15} width={1} height={2} className="px-xe-mam" />
            <rect x={22} y={14} width={5} height={4} className="px-xe-banh" />
            <rect x={24} y={15} width={1} height={2} className="px-xe-mam" />
          </svg>
        </div>
      </div>
      <div className="px-duong-ray">
        <span className="px-duong-tien" />
        <div className="px-moc-ds">
          {MOC_HANH_TRINH.map((m, i) => (
            <span
              key={m.ma}
              className={
                i < buoc ? 'px-moc-diem xong' : i === buoc ? 'px-moc-diem toi' : 'px-moc-diem'
              }
            />
          ))}
        </div>
      </div>
      <div className="px-moc-nhan">
        {MOC_HANH_TRINH.map((m, i) => (
          <span key={m.ma} className={i === buoc ? 'toi' : undefined}>
            {m.ten}
          </span>
        ))}
      </div>
    </div>
  )
}

const CHU_SO_ODO = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] as const

// Hiệu ứng Pixel: đồng hồ km cuộn số (odometer) khi tài xế nhập hoặc vừa ghi km chuyến
export function DongHoKmPixel({
  giaTri,
  vuaGhi = false,
}: {
  giaTri: string | number
  vuaGhi?: boolean
}) {
  if (!dangHieuUngPixel()) return null
  const trong = giaTri === '' || giaTri === null || giaTri === undefined
  const so = trong ? 0 : Math.max(0, Math.min(999999, Math.round(Number(giaTri) || 0)))
  const chuoi = String(so).padStart(6, '0')
  return (
    <div className={`px-odo${trong ? ' trong' : ''}${vuaGhi ? ' vua-ghi' : ''}`} aria-hidden="true">
      <div className="px-odo-so">
        {chuoi.split('').map((kt, i) => {
          const d = Number(kt)
          return (
            <span key={i} className="px-odo-nhom">
              {i === 3 && <span className="px-odo-cham">.</span>}
              <span className="px-odo-cot">
                <span
                  className="px-odo-dai"
                  style={{
                    transform: `translate3d(0, -${d * 10}%, 0)`,
                    transitionDelay: `${(5 - i) * 28}ms`,
                  }}
                >
                  {CHU_SO_ODO.map((n) => (
                    <span key={n} className="px-odo-o">
                      {n}
                    </span>
                  ))}
                </span>
              </span>
            </span>
          )
        })}
      </div>
      <span className="px-odo-dv">{vuaGhi ? 'km ✓' : 'km'}</span>
    </div>
  )
}

// Hiệu ứng Pixel: kim cân minh hoạ nhảy theo số kg khi nhập khối lượng đơn (không kiểm giới hạn)
export function KimCanPixel({ kg }: { kg: string | number }) {
  if (!dangHieuUngPixel()) return null
  const v = Math.max(0, Number(kg) || 0)
  // Thang log để cả đơn nhỏ (vài kg) lẫn đơn nặng (vài tấn) đều thấy kim nhích rõ
  const tyLe = v <= 0 ? 0 : Math.min(1, Math.log10(1 + v) / Math.log10(1 + 5000))
  const goc = -76 + tyLe * 152
  return (
    <div className="px-can" aria-hidden="true">
      <svg className="px-can-svg" viewBox="0 0 120 66">
        <path d="M12 58 A48 48 0 0 1 108 58 Z" className="px-can-mat" />
        <path d="M18 58 A42 42 0 0 1 60 16" className="px-can-cung nhe" />
        <path d="M60 16 A42 42 0 0 1 92 31" className="px-can-cung vua" />
        <path d="M92 31 A42 42 0 0 1 102 58" className="px-can-cung nang" />
        <g className="px-can-vach">
          <line x1={16} y1={58} x2={23} y2={58} />
          <line x1={29} y1={27} x2={34} y2={32} />
          <line x1={60} y1={13} x2={60} y2={20} />
          <line x1={91} y1={27} x2={86} y2={32} />
          <line x1={104} y1={58} x2={97} y2={58} />
        </g>
        <g className="px-can-kim" style={{ transform: `rotate(${goc.toFixed(1)}deg)` }}>
          <polygon points="60,17 63,58 57,58" className="px-can-mui" />
          <circle cx={60} cy={58} r={4.5} className="px-can-truc" />
        </g>
      </svg>
      <span className="px-can-so">
        {v > 0 ? `${v.toLocaleString('vi-VN', { maximumFractionDigits: 2 })} kg` : '0 kg'}
      </span>
    </div>
  )
}

// Hiệu ứng Pixel: đồng hồ định mức (chi thực tế so với định mức) trên màn Quyết toán
export function DongHoDinhMucPixel({ thucTe, dinhMuc }: { thucTe: number; dinhMuc: number }) {
  if (!dangHieuUngPixel()) return null
  const tyLe = dinhMuc > 0 ? thucTe / dinhMuc : thucTe > 0 ? 1.25 : 0
  const phanTram = dinhMuc > 0 ? Math.round(tyLe * 100) : thucTe > 0 ? 100 : 0
  const tyLeKim = Math.min(1.25, Math.max(0, tyLe))
  const goc = -80 + (tyLeKim / 1.25) * 160
  const muc = tyLe > 1 ? 'vuot' : tyLe >= 0.8 ? 'gan' : 'on'
  const nhanMuc =
    muc === 'vuot' ? 'Vượt định mức' : muc === 'gan' ? 'Gần định mức' : 'Trong định mức'

  return (
    <div className={`px-dm ${muc}`} aria-hidden="true">
      <div className="px-dm-khung">
        <svg className="px-dm-svg" viewBox="0 0 164 74">
          <path d="M22 64 A60 60 0 0 1 142 64" className="px-dm-nen" />
          {/* 0% → 80% (-80° → +22.4°), 80% → 100% (+22.4° → +48°), 100% → 125% (+48° → +80°) */}
          <path d="M22 64 A60 60 0 0 1 105 9" className="px-dm-vung on" />
          <path d="M105 9 A60 60 0 0 1 127 24" className="px-dm-vung gan" />
          <path d="M127 24 A60 60 0 0 1 142 64" className="px-dm-vung vuot" />
          <g className="px-dm-vach">
            <line x1={18} y1={64} x2={28} y2={64} />
            <line x1={52} y1={13} x2={57} y2={21} />
            <line x1={82} y1={2} x2={82} y2={11} />
            <line x1={127} y1={20} x2={120} y2={27} className="px-dm-moc" />
            <line x1={146} y1={64} x2={136} y2={64} />
          </g>
          <text x={11} y={72} className="px-dm-chu">
            0%
          </text>
          <text x={128} y={16} className="px-dm-chu moc">
            100%
          </text>
          <g className="px-dm-kim-boc" style={{ transform: `rotate(${goc.toFixed(1)}deg)` }}>
            <g className="px-dm-kim-rung">
              <line x1={82} y1={64} x2={82} y2={14} className="px-dm-kim" />
              <circle cx={82} cy={64} r={5} className="px-dm-truc" />
            </g>
          </g>
        </svg>
      </div>
      <div className="px-dm-thong-tin">
        <div className="px-dm-hang">
          <span className="px-dm-pt">{phanTram}% định mức</span>
          <span className="px-dm-den">{nhanMuc}</span>
        </div>
        <span className="px-dm-chi-tiet">
          Thực tế {thucTe.toLocaleString('vi-VN')} đ / Định mức {dinhMuc.toLocaleString('vi-VN')} đ
        </span>
      </div>
    </div>
  )
}

// Hiệu ứng Pixel: đồng xu rơi vào két sau khi ghi thu công nợ thành công (tự mờ ≤ 1,4 s)
export function DongXuRoiKetPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-xu-ket" aria-hidden="true">
      <div className="px-xu-khung">
        <svg
          className="px-xu-svg"
          viewBox="0 0 96 84"
          width={96}
          height={84}
          shapeRendering="crispEdges"
        >
          {/* 3 đồng xu pixel rơi lệch nhịp vào khe két */}
          <g className="px-xu px-xu-1">
            <rect x={41} y={28} width={14} height={14} className="px-xu-vien" />
            <rect x={43} y={30} width={10} height={10} className="px-xu-vang" />
            <rect x={46} y={32} width={4} height={6} className="px-xu-tam" />
          </g>
          <g className="px-xu px-xu-2">
            <rect x={33} y={26} width={12} height={12} className="px-xu-vien" />
            <rect x={35} y={28} width={8} height={8} className="px-xu-vang" />
            <rect x={38} y={30} width={2} height={4} className="px-xu-tam" />
          </g>
          <g className="px-xu px-xu-3">
            <rect x={51} y={26} width={12} height={12} className="px-xu-vien" />
            <rect x={53} y={28} width={8} height={8} className="px-xu-vang" />
            <rect x={56} y={30} width={2} height={4} className="px-xu-tam" />
          </g>
          {/* Tia lóe pixel khi xu chạm két */}
          <g className="px-xu-tia">
            <rect x={22} y={36} width={4} height={4} className="px-xu-vang" />
            <rect x={70} y={36} width={4} height={4} className="px-xu-vang" />
            <rect x={28} y={24} width={4} height={4} className="px-ket-den" />
            <rect x={64} y={24} width={4} height={4} className="px-ket-den" />
          </g>
          {/* Thân két sắt pixel */}
          <g className="px-ket-than">
            <rect x={16} y={40} width={64} height={38} className="px-ket-vien" />
            <rect x={20} y={44} width={56} height={30} className="px-ket-mat" />
            <rect x={36} y={42} width={24} height={4} className="px-ket-khe" />
            <rect x={26} y={50} width={44} height={18} className="px-ket-cua" />
            <rect x={56} y={56} width={8} height={6} className="px-xu-vang" />
            <rect x={30} y={54} width={10} height={10} className="px-ket-den" />
            <rect x={22} y={78} width={10} height={4} className="px-ket-vien" />
            <rect x={64} y={78} width={10} height={4} className="px-ket-vien" />
          </g>
        </svg>
        <span className="px-xu-chu">ĐÃ THU VÀO KÉT</span>
      </div>
    </div>
  )
}

// Hiệu ứng Pixel: băng dính niêm phong kéo ngang thẻ chuyến sau khi chốt chuyến thành công
export function BangDinhNiemPhongPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-niem-phong" aria-hidden="true">
      <div className="px-np-bang">
        <span className="px-np-chu">ĐÃ CHỐT CHUYẾN</span>
      </div>
      <div className="px-np-cuon" />
    </div>
  )
}

// Hiệu ứng Pixel: hộp carton gấp nắp đóng gói sau khi tạo đơn thành công (tự mờ ≤ 1,4 s)
export function HopCartonGapNapPixel() {
  if (!dangHieuUngPixel()) return null
  return (
    <div className="px-hop-carton" aria-hidden="true">
      <div className="px-hop-khung">
        <svg
          className="px-hop-svg"
          viewBox="0 0 96 82"
          width={96}
          height={82}
          shapeRendering="crispEdges"
        >
          {/* Nắp trái & nắp phải gấp vào giữa */}
          <g className="px-hop-nap-trai">
            <rect x={20} y={24} width={28} height={10} className="px-hop-nap" />
          </g>
          <g className="px-hop-nap-phai">
            <rect x={48} y={24} width={28} height={10} className="px-hop-nap" />
          </g>
          {/* Thân hộp carton pixel */}
          <rect x={18} y={32} width={60} height={42} className="px-hop-vien" />
          <rect x={22} y={36} width={52} height={34} className="px-hop-than" />
          <rect x={54} y={36} width={20} height={34} className="px-hop-bong" />
          {/* Đường băng keo niêm phong giữa hộp */}
          <rect x={22} y={32} width={52} height={6} className="px-hop-keo" />
          <rect x={44} y={36} width={8} height={14} className="px-hop-keo" />
          {/* Nhãn vận đơn nhỏ trên mặt hộp */}
          <rect x={26} y={52} width={16} height={12} className="px-hop-nhan" />
          <rect x={28} y={55} width={10} height={2} className="px-hop-vien" />
          <rect x={28} y={59} width={8} height={2} className="px-hop-vien" />
        </svg>
        <span className="px-hop-chu">ĐÃ ĐÓNG GÓI ĐƠN</span>
      </div>
    </div>
  )
}

const DO_RONG_SKEL = ['72%', '90%', '58%', '82%', '64%', '48%', '76%'] as const

// Hiệu ứng Pixel: khung tải skeleton quét theo bậc thay chữ "Đang tải…" ở các bảng chính
export function KhungTaiBangPixel({ soHang = 4, soCot = 5 }: { soHang?: number; soCot?: number }) {
  if (!dangHieuUngPixel()) return null
  const hang = Array.from({ length: soHang }, (_, r) => r)
  const cot = Array.from({ length: soCot }, (_, c) => c)
  return (
    <div className="px-skel-bang" aria-hidden="true">
      {hang.map((r) => (
        <div key={r} className="px-skel-hang">
          {cot.map((c) => (
            <span
              key={c}
              className="px-skel-thanh"
              style={
                {
                  width: DO_RONG_SKEL[(r * 3 + c) % DO_RONG_SKEL.length],
                  '--px-tre': `${(r * 2 + c) * 60}ms`,
                } as CSSProperties
              }
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// Hiệu ứng Pixel: nội dung nút gửi giữ bề ngang cố định và đổi chữ theo bậc "Đang gửi…" → "Xong ✓"
export function NoiDungNutGuiPixel({
  nhan,
  dangGui,
  vuaXong,
}: {
  nhan: string
  dangGui: boolean
  vuaXong: boolean
}) {
  const chuHien = dangGui ? 'Đang gửi…' : vuaXong ? 'Xong ✓' : nhan
  return (
    <span className="px-ng-khung">
      <span className="px-ng-giu" data-giu={nhan} aria-hidden="true" />
      <span className="px-ng-giu px-ng-giu-gui" data-giu="Đang gửi…" aria-hidden="true" />
      <span className="px-ng-giu" data-giu="Xong ✓" aria-hidden="true" />
      <span key={dangGui ? 'gui' : vuaXong ? 'xong' : 'cho'} className="px-ng-chu">
        {dangGui && <span className="px-ng-xoay" aria-hidden="true" />}
        {chuHien}
      </span>
    </span>
  )
}

const VACH_TAM_UNG = [0, 25, 50, 75, 100] as const

// Hiệu ứng Pixel: thước vạch định mức tạm ứng và rung ngắn khi máy chủ báo vượt trần (BR-53)
export function ThuocTamUngPixel({
  dinhMuc,
  daCap,
  rung = 0,
}: {
  dinhMuc: number
  daCap: number
  rung?: number
}) {
  if (!dangHieuUngPixel()) return null
  const tyLe = dinhMuc > 0 ? Math.max(0, Math.min(1, daCap / dinhMuc)) : 0
  const phanTram = Math.round(tyLe * 100)
  const cao = tyLe > 0.95
  const dangRung = rung > 0

  return (
    <div
      key={dangRung ? `rung-${rung}` : 'tinh'}
      className={`px-thuoc-tu${cao ? ' cao' : ''}${dangRung ? ' vuot-tran' : ''}`}
      aria-hidden="true"
    >
      <div className="px-tu-dau">
        <span className="px-tu-nhan">Thước định mức tạm ứng</span>
        <span className="px-tu-pt">
          {dangRung
            ? 'Chạm trần BR-53'
            : `${phanTram}% / trần ${dinhMuc.toLocaleString('vi-VN')} đ`}
        </span>
      </div>
      <div className="px-tu-ray">
        <span className="px-tu-muc" style={{ width: `${phanTram}%` }} />
        <span className="px-tu-tran" />
      </div>
      <div className="px-tu-vach">
        {VACH_TAM_UNG.map((m) => (
          <span key={m} className={m === 100 ? 'tran' : undefined}>
            {m}%
          </span>
        ))}
      </div>
    </div>
  )
}

// Hiệu ứng Pixel: dải 4 điều kiện giao hàng sáng dần theo trạng thái đã có trên màn
export function DaiDieuKienGiaoPixel({
  daQuet,
  coAnh,
  coTen,
  daKy,
}: {
  daQuet: boolean
  coAnh: boolean
  coTen: boolean
  daKy: boolean
}) {
  if (!dangHieuUngPixel()) return null
  const muc = [
    { ma: 'qr', ten: 'Quét mã', dat: daQuet },
    { ma: 'anh', ten: 'Ảnh', dat: coAnh },
    { ma: 'ten', ten: 'Tên', dat: coTen },
    { ma: 'ky', ten: 'Chữ ký', dat: daKy },
  ] as const
  const soDat = muc.filter((m) => m.dat).length

  return (
    <div className={`px-dk-giao${soDat === 4 ? ' du' : ''}`} aria-hidden="true">
      <div className="px-dk-dau">
        <span className="px-dk-tieu-de">Điều kiện giao</span>
        <span className="px-dk-dem">{soDat}/4</span>
      </div>
      <div className="px-dk-thanh">
        {muc.map((m) => (
          <span key={m.ma} className={m.dat ? 'px-dk-nac dat' : 'px-dk-nac'} />
        ))}
      </div>
      <div className="px-dk-ds">
        {muc.map((m) => (
          <span key={m.ma} className={m.dat ? 'px-dk-muc dat' : 'px-dk-muc'}>
            <span className="px-dk-o">{m.dat ? '✓' : ''}</span>
            <span>{m.ten}</span>
          </span>
        ))}
      </div>
    </div>
  )
}

const NAC_NEN_ANH = [0, 1, 2, 3, 4, 5] as const

// Hiệu ứng Pixel: ô tệp "nhai" ảnh theo bậc và thanh nấc nén ảnh (chỉ trang trí, tự gỡ ≤ 1,2 s)
export function PhanHoiChonTepPixel({
  soTep,
  dangNen = false,
}: {
  soTep: number
  dangNen?: boolean
}) {
  if (!dangHieuUngPixel()) return null
  const nhan = dangNen ? 'Đang nén ảnh…' : soTep > 1 ? `Đã nhận ${soTep} ảnh ✓` : 'Đã nhận ảnh ✓'
  return (
    <span className={`px-tep-ph${dangNen ? ' nen' : ''}`} aria-hidden="true">
      <svg
        className="px-tep-svg"
        viewBox="0 0 28 24"
        width={28}
        height={24}
        shapeRendering="crispEdges"
      >
        {/* Thẻ ảnh nhỏ rơi vào khe máy nhai theo bậc */}
        <g className="px-tep-anh">
          <rect x={8} y={2} width={12} height={10} className="px-tep-giay" />
          <rect x={10} y={4} width={3} height={3} className="px-tep-nang" />
          <rect x={10} y={8} width={8} height={2} className="px-tep-nui" />
        </g>
        {/* Khe nuốt tệp kiểu 8-bit */}
        <rect x={3} y={12} width={22} height={10} className="px-tep-hop" />
        <rect x={6} y={13} width={16} height={3} className="px-tep-khe" />
        <rect x={7} y={18} width={4} height={2} className="px-tep-den" />
      </svg>
      <span className="px-tep-nen-khoi">
        <span className="px-tep-nen-chu">{nhan}</span>
        <span className="px-tep-nen-thanh">
          {NAC_NEN_ANH.map((i) => (
            <span key={i} className="px-tep-nen-o" style={{ '--px-i': i } as CSSProperties} />
          ))}
        </span>
      </span>
    </span>
  )
}

// Hiệu ứng Pixel: biên lai nhiệt trượt ra từ khe sau khi khóa sổ quyết toán thành công (≤ 1,5 s)
export function BienLaiNhietPixel({
  maChuyen,
  doanhThu,
  tongChi,
  lai,
}: {
  maChuyen: string
  doanhThu: number
  tongChi: number
  lai: number
}) {
  if (!dangHieuUngPixel()) return null
  const dong = (so: number) => `${so.toLocaleString('vi-VN')} đ`
  const hang = [
    { k: 'CHUYẾN', v: maChuyen },
    { k: 'DOANH THU', v: dong(doanhThu) },
    { k: 'CHI PHÍ', v: dong(tongChi) },
    { k: 'LÃI CHUYẾN', v: dong(lai) },
    { k: 'KHÓA SỔ', v: 'ĐÃ QUYẾT TOÁN ✓' },
  ] as const

  return (
    <div className="px-bien-lai" aria-hidden="true">
      <div className="px-bl-may">
        <div className="px-bl-dau">
          <span className="px-bl-tieu-de">BIÊN LAI QUYẾT TOÁN</span>
          <span className="px-bl-den" />
        </div>
        <div className="px-bl-khe" />
        <div className="px-bl-ong">
          <div className="px-bl-giay">
            {hang.map((r) => (
              <div key={r.k} className="px-bl-hang">
                <span>{r.k}</span>
                <strong>{r.v}</strong>
              </div>
            ))}
            <svg
              className="px-bl-rang"
              viewBox="0 0 216 8"
              preserveAspectRatio="none"
              shapeRendering="crispEdges"
            >
              <path d="M0 0 H216 V2 L207 8 L198 2 L189 8 L180 2 L171 8 L162 2 L153 8 L144 2 L135 8 L126 2 L117 8 L108 2 L99 8 L90 2 L81 8 L72 2 L63 8 L54 2 L45 8 L36 2 L27 8 L18 2 L9 8 L0 2 Z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}
