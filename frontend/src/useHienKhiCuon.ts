import { useEffect } from 'react'
import { dangHieuUng } from './nen'

// Khối hiện dần khi cuộn tới (v4): chỉ áp cho khối .kinh (không áp cho dòng bảng tr, thẻ trong danh sách dài).
// Khối đã thấy trong khung nhìn lúc tải trang / lúc dữ liệu vừa đổ về thì không chạy; mỗi khối chỉ chạy một lần.
export function useHienKhiCuon(khoa?: string) {
  useEffect(() => {
    if (!dangHieuUng()) return

    const daXuLy = new WeakSet<Element>()
    const dangCho = new Set<HTMLElement>()
    const henGio = new Set<ReturnType<typeof setTimeout>>()

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const el = entry.target as HTMLElement
          io.unobserve(el)
          dangCho.delete(el)
          if (!dangHieuUng()) {
            el.classList.remove('kinh-cho-cuon', 'kinh-hien-cuon')
            continue
          }
          el.classList.remove('kinh-cho-cuon')
          el.classList.add('kinh-hien-cuon')
          const h = setTimeout(() => {
            el.classList.remove('kinh-hien-cuon')
            henGio.delete(h)
          }, 280)
          henGio.add(h)
        }
      },
      { threshold: 0.08, rootMargin: '0px 0px -16px 0px' },
    )

    const quet = () => {
      if (!dangHieuUng()) return
      const vh = window.innerHeight
      const ds = document.querySelectorAll<HTMLElement>('.kinh')
      ds.forEach((el) => {
        if (daXuLy.has(el)) return
        daXuLy.add(el)
        // Không áp cho dòng bảng tr hoặc thẻ nằm trong danh sách dài (ul/ol/.ds-the)
        if (el.tagName === 'TR' || el.closest('tr, ul, ol, .ds-the')) return
        const r = el.getBoundingClientRect()
        if (r.height === 0 && r.width === 0) return
        // Khối đã nằm trong (hoặc phía trên) vùng nhìn lúc tải trang thì giữ nguyên, không chạy
        if (r.top < vh - 12) return
        el.classList.add('kinh-cho-cuon')
        dangCho.add(el)
        io.observe(el)
      })
    }

    quet()
    // DOM đổi liên tục (số chạy, dữ liệu về): gộp lại, quét tối đa một lần mỗi khung hình
    let rafQuet = 0
    const mo = new MutationObserver(() => {
      if (!rafQuet)
        rafQuet = requestAnimationFrame(() => {
          rafQuet = 0
          quet()
        })
    })
    mo.observe(document.body, { childList: true, subtree: true })

    return () => {
      mo.disconnect()
      cancelAnimationFrame(rafQuet)
      io.disconnect()
      for (const h of henGio) clearTimeout(h)
      for (const el of dangCho) {
        el.classList.remove('kinh-cho-cuon', 'kinh-hien-cuon')
      }
    }
  }, [khoa])
}
