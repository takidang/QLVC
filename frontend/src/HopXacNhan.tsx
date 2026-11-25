import { useEffect, useId, useSyncExternalStore } from 'react'
import { createPortal } from 'react-dom'
import { useLocation } from 'react-router-dom'
import { ganBayFocus } from './bayFocus'
import './HopXacNhan.css'
import { huyXacNhan, theoDoi, traLoi, yeuCauDang } from './xacNhanKho'

// Gắn một lần trong App (trong BrowserRouter): vẽ hộp xác nhận và bẫy focus cho mọi hộp thoại .hop-thoai
export function HopXacNhan() {
  const yc = useSyncExternalStore(theoDoi, yeuCauDang)
  const { pathname } = useLocation()
  const idCau = useId()
  useEffect(() => ganBayFocus(), [])
  // Đổi trang (kể cả nút Back, hết phiên) khi hộp đang mở: đóng, không coi là đồng ý
  useEffect(() => () => huyXacNhan(), [pathname])

  if (!yc) return null
  // Hai nút đều type="button": DongDauPixel không đóng dấu (lúc này chưa lưu gì).
  // e.detail > 1: cú bấm thứ hai của bấm đúp vào nút mở hộp không được tính (bàn phím và Esc có detail = 0)
  return createPortal(
    <div className="nen-mo" onClick={(e) => e.detail <= 1 && traLoi(yc.ma, false)}>
      <div
        key={yc.ma}
        className="hop-thoai xac-nhan"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={idCau}
        onClick={(e) => e.stopPropagation()}
      >
        <p id={idCau} className="xn-cau">
          {yc.cau}
        </p>
        <div className="nut">
          {/* Focus mặc định ở Thôi: nhấn Enter không vô tình đồng ý */}
          <button type="button" className="phu" autoFocus onClick={() => traLoi(yc.ma, false)}>
            Thôi
          </button>
          <button type="button" onClick={(e) => e.detail <= 1 && traLoi(yc.ma, true)}>
            {yc.nut}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
