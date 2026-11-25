// Bẫy focus chung cho mọi hộp thoại (.nen-mo > .hop-thoai), không phải sửa từng hộp:
// Tab / Shift+Tab đi vòng trong hộp trên cùng; mở thì đưa focus vào hộp; đóng thì trả về chỗ cũ.
const CO_THE_FOCUS = 'a[href], button, input, select, textarea, summary, [tabindex]'

const dungDuoc = (el: HTMLElement) =>
  el.tabIndex >= 0 &&
  !el.matches(':disabled, input[type="hidden"]') &&
  el.getClientRects().length > 0 &&
  getComputedStyle(el).visibility !== 'hidden'

export function ganBayFocus() {
  let lichSu: HTMLElement[] = [] // các chỗ vừa được focus, mới nhất ở cuối
  const hopMo = new Map<Element, HTMLElement | undefined>() // nền đang mở → chỗ trả focus

  const khiFocus = (e: FocusEvent) => {
    if (e.target instanceof HTMLElement) lichSu = [...lichSu.slice(-19), e.target]
  }

  const khiPhim = (e: KeyboardEvent) => {
    if (e.key !== 'Tab' || e.defaultPrevented) return
    const nen = Array.from(document.querySelectorAll('.nen-mo')).pop()
    if (!nen) return
    const ds = Array.from(nen.querySelectorAll<HTMLElement>(CO_THE_FOCUS)).filter(dungDuoc)
    const i = ds.indexOf(document.activeElement as HTMLElement)
    // Ở giữa thì để trình duyệt tự đi; ở mép hoặc đang ở ngoài danh sách thì quay vòng
    if (i !== -1 && (e.shiftKey ? i > 0 : i < ds.length - 1)) return
    e.preventDefault()
    ds[e.shiftKey ? ds.length - 1 : 0]?.focus()
  }

  const quanSat = new MutationObserver(() => {
    const dangCo = new Set(document.querySelectorAll('.nen-mo'))
    for (const [nen, tro] of hopMo) {
      if (dangCo.has(nen)) continue
      hopMo.delete(nen)
      // Đợi React vẽ xong (nút vừa bị khóa được mở lại); đã focus chỗ khác thì không giành
      window.setTimeout(() => {
        if (document.activeElement && document.activeElement !== document.body) return
        if (tro?.isConnected) tro.focus({ preventScroll: true })
      }, 0)
    }
    for (const nen of dangCo) {
      if (hopMo.has(nen)) continue
      const tro = [...lichSu].reverse().find((el) => el.isConnected && !nen.contains(el))
      hopMo.set(nen, tro)
      const hop = nen.querySelector<HTMLElement>('.hop-thoai')
      if (hop && !nen.contains(document.activeElement)) {
        hop.tabIndex = -1
        hop.focus({ preventScroll: true })
      }
    }
  })

  document.addEventListener('focusin', khiFocus, true)
  document.addEventListener('keydown', khiPhim)
  quanSat.observe(document.body, { childList: true, subtree: true })
  return () => {
    document.removeEventListener('focusin', khiFocus, true)
    document.removeEventListener('keydown', khiPhim)
    quanSat.disconnect()
  }
}
