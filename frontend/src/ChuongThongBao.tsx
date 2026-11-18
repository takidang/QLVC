import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { VaiTro } from './api/auth'
import { thongBao, type ThongBao } from './api/thongBao'

// Chuông thông báo cho mọi vai trò (UC-37, GET /api/thong-bao). Số trên chuông = thông báo mới hơn
// lần mở chuông trước (mốc lưu trên trình duyệt theo người dùng). Tải lại khi đổi trang và mỗi 2 phút.
const MUC: Record<ThongBao['muc_do'], string> = {
  KHAN: 'khan',
  CAN_LAM: 'can-lam',
  THONG_TIN: 'thong-tin',
}
const luc = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })

export default function ChuongThongBao({
  nguoiDungId,
  vaiTro,
}: {
  nguoiDungId: number
  vaiTro: VaiTro
}) {
  const { pathname } = useLocation()
  const [ds, setDs] = useState<ThongBao[] | null>(null)
  const [loi, setLoi] = useState(false)
  const khoa = `qlvc-da-doc-${nguoiDungId}`
  const [moc, setMoc] = useState(() => localStorage.getItem(khoa) ?? '')
  const hop = useRef<HTMLDetailsElement>(null)

  useEffect(() => {
    let bo = false
    const tai = () =>
      thongBao()
        .then((r) => {
          if (bo) return
          setDs(r.thong_bao)
          setLoi(false)
        })
        .catch(() => !bo && setLoi(true))
    tai()
    const h = setInterval(tai, 120_000)
    return () => {
      bo = true
      clearInterval(h)
    }
  }, [pathname])

  // Đóng khi bấm hoặc Tab ra ngoài
  useEffect(() => {
    const ngoai = (e: Event) => {
      if (hop.current?.open && !hop.current.contains(e.target as Node)) hop.current.open = false
    }
    document.addEventListener('pointerdown', ngoai)
    document.addEventListener('focusin', ngoai)
    return () => {
      document.removeEventListener('pointerdown', ngoai)
      document.removeEventListener('focusin', ngoai)
    }
  }, [])

  const moi = (ds ?? []).filter((t) => !moc || t.luc > moc)
  const soMoi = moi.length
  // Mở chuông: những thông báo đang hiện tính là đã đọc (lần sau mở mới hiện dấu "mới")
  const [mocLucMo, setMocLucMo] = useState(moc)
  const mo = (open: boolean) => {
    if (!open || !ds?.length) return
    const moiNhat = ds.reduce((m, t) => (t.luc > m ? t.luc : m), moc)
    setMocLucMo(moc)
    localStorage.setItem(khoa, moiNhat)
    setMoc(moiNhat)
  }

  const dp = vaiTro === 'DIEU_PHOI' || vaiTro === 'QUAN_LY'
  const den = (t: ThongBao) => {
    const d = t.doi_tuong
    if (vaiTro === 'TAI_XE')
      return d?.loai === 'CHUYEN' ? `/tai-xe/chuyen/${d.id}` : '/tai-xe/chuyen'
    if (vaiTro === 'KE_TOAN') {
      if (t.loai === 'TAM_UNG_TREO') return '/ke-toan/tam-ung'
      return d?.loai === 'DON' ? '/ke-toan/cong-no' : '/ke-toan/quyet-toan'
    }
    if (!dp || !d) return '/dieu-phoi/chuyen'
    return {
      CHUYEN: `/dieu-phoi/chuyen/${d.id}`,
      DON: `/dieu-phoi/don/${d.id}/phieu`,
      XE: '/dieu-phoi/xe',
      TAI_XE: '/dieu-phoi/tai-xe',
    }[d.loai]
  }

  return (
    <details ref={hop} className="chuong" onToggle={(e) => mo(e.currentTarget.open)}>
      <summary aria-label={soMoi ? `Thông báo: ${soMoi} mới` : 'Thông báo'}>
        <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15zM10 20.5a2 2 0 0 0 4 0" />
        </svg>
        {soMoi > 0 && <em>{soMoi > 99 ? '99+' : soMoi}</em>}
      </summary>
      <div className="chuong-hop">
        <strong>Thông báo {ds && <small>{ds.length}</small>}</strong>
        <ul>
          {(ds ?? []).map((t, i) => (
            <li key={`${t.loai}-${t.luc}-${i}`}>
              <Link
                to={den(t)}
                className={MUC[t.muc_do]}
                onClick={() => hop.current?.removeAttribute('open')}
              >
                <i aria-hidden="true" />
                <span>
                  <b>
                    {t.tieu_de}
                    {(!mocLucMo || t.luc > mocLucMo) && <span className="tb-moi">mới</span>}
                  </b>
                  {t.noi_dung && <small>{t.noi_dung}</small>}
                  <time>{luc(t.luc)}</time>
                </span>
              </Link>
            </li>
          ))}
        </ul>
        {ds && ds.length === 0 && <p>Không có thông báo nào.</p>}
        {loi && !ds && <p>Không tải được thông báo.</p>}
      </div>
    </details>
  )
}
