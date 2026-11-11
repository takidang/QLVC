import { useEffect } from 'react'
import { Toaster, toast } from 'sonner'

// Thông báo thành công dạng toast (Sonner), tự biến mất. Lỗi vẫn hiện tại chỗ, cạnh chỗ cần sửa.
// Dùng thay `{thongBao && <p className="thanh-cong">{thongBao}</p>}`: chỉ cần đặt <ThongBao chu={thongBao} />
export function ThongBao({ chu }: { chu: string }) {
  useEffect(() => {
    if (chu) toast.success(chu)
  }, [chu])
  return null
}

// Khung chứa toast cho cả app, theo bộ màu và font của giao diện v2
export function KhungThongBao() {
  return (
    <Toaster
      position="bottom-right"
      closeButton
      toastOptions={{
        style: {
          fontFamily: 'var(--font)',
          fontSize: '14px',
          color: 'var(--muc)',
          background: '#fbfbf9',
          border: '1px solid var(--vien-dam)',
          borderRadius: '16px',
        },
      }}
    />
  )
}
