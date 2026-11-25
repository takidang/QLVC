import { dangHieuUngPixel } from './nen'

// Hộp thoại (.nen-mo) bị React gỡ ngay khi đóng: dựng bản sao không bấm được rồi cho mờ dần,
// để không phải sửa cách đóng ở từng trang. Chỉ giao diện Pixel.
export function moDanKhiDongHop() {
  const daCuon = new WeakMap<Element, number>()
  document.addEventListener(
    'scroll',
    ({ target }) => {
      if (target instanceof Element) daCuon.set(target, target.scrollTop)
    },
    { capture: true, passive: true },
  )
  new MutationObserver((ds) => {
    for (const d of ds)
      for (const n of d.removedNodes) {
        if (!(n instanceof HTMLElement) || !dangHieuUngPixel()) continue
        const nen = n.matches('.nen-mo') ? n : n.querySelector<HTMLElement>('.nen-mo')
        if (!nen || nen.classList.contains('dang-dong')) continue
        const ban = nen.cloneNode(true) as HTMLElement
        ban.classList.add('dang-dong')
        ban.inert = true
        ban.setAttribute('aria-hidden', 'true')
        ban.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'))
        // cloneNode không giữ lựa chọn của select; vị trí cuộn chỉ gán được sau khi gắn vào trang
        const chon = nen.querySelectorAll('select')
        ban.querySelectorAll('select').forEach((s, i) => (s.selectedIndex = chon[i].selectedIndex))
        // Đọc từ hộp gốc đã gỡ thì scrollTop luôn là 0: lấy số ghi lại lúc người dùng cuộn
        document.body.append(ban)
        const goc = [nen, ...nen.querySelectorAll<HTMLElement>('*')]
        ;[ban, ...ban.querySelectorAll<HTMLElement>('*')].forEach((e, i) => {
          const y = daCuon.get(goc[i])
          if (y) e.scrollTop = y
        })
        window.setTimeout(() => ban.remove(), 160)
      }
  }).observe(document.body, { childList: true, subtree: true })
}
