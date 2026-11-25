import { toast } from 'sonner'
import './NutChep.css'

// Nút chép nhanh (SĐT) vào bộ nhớ tạm. Bộ nhớ tạm cần localhost hoặc HTTPS; không được thì báo lỗi
export function NutChep({ chu, ten = 'số điện thoại' }: { chu: string; ten?: string }) {
  async function chep() {
    try {
      await navigator.clipboard.writeText(chu)
      toast.success(`Đã chép ${chu}`)
    } catch {
      toast.error(`Không chép được, hãy bôi đen ${ten} để chép`)
    }
  }
  return (
    <button
      type="button"
      className="nut-chep"
      aria-label={`Chép ${ten} ${chu}`}
      title={`Chép ${ten}`}
      onClick={(e) => {
        e.stopPropagation() // không mở dòng / thẻ chứa nút
        void chep()
      }}
    >
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
        <path
          d="M5.5 5.5h8v8h-8zM10.5 5.5v-3h-8v8h3"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
        />
      </svg>
    </button>
  )
}
