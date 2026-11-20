import { useEffect, useRef } from 'react'
import { dangHieuUng } from './nen'

const KHOA_PHIEN = 'qlvc-dan-tro-da-chay'
const CHO_KHOI_MS = 600
const DT_TOI_DA = 0.05
const TRAN_CHE_DO_2 = 1.42
const TRAN_CHE_DO_1 = 3.6

// Đường dẫn gốc của từng vai trò luôn lập tức chuyển hướng sang trang con (TRANG_DAU trong App.tsx)
const TRANG_GOC = new Set(['/quan-ly', '/dieu-phoi', '/ke-toan', '/tai-xe'])

// Lưu đường dẫn đã chạy trong cùng lượt tải trang để phân biệt bấm menu (chế độ 2) với F5 tải lại
let pathnameTruoc: string | null = null

type Diem = [number, number]
type Dich = Diem | (() => Diem)
type HinhTro = 'mui-ten' | 'dau-cong'
type TrangThaiViec = 'cho' | 'dang' | 'xong'
type KichBan = Generator<void, void, number>

type MauConTro = {
  ten: string
  mau: string
  chu?: string
}

const DS_CON_TRO: readonly MauConTro[] = [
  { ten: 'Điều phối', mau: 'var(--chay)' },
  { ten: 'Kế toán', mau: 'var(--cam)' },
  { ten: 'Tài xế', mau: 'var(--chot)' },
  { ten: 'Thủ kho', mau: 'var(--xong)' },
  { ten: 'Quản lý', mau: 'var(--o-liu)' },
  { ten: 'Giám sát', mau: 'var(--do)' },
  { ten: 'Vận hành', mau: 'var(--muc)', chu: 'var(--tren-muc)' },
  { ten: 'Điều hành', mau: 'var(--xam)' },
]

type KhungChuNhat = {
  left: number
  top: number
  width: number
  height: number
}

type ViecKhoi = {
  el: HTMLElement
  rect: KhungChuNhat
  trongMan: boolean
  trangThai: TrangThaiViec
  boGoc: string
  khungEl: HTMLDivElement | null
  ktEl: HTMLSpanElement | null
}

type ConTro = {
  el: HTMLDivElement
  hinhEl: HTMLDivElement
  x: number
  y: number
  doMo: number
  tyLe: number
  hinh: HinhTro
  mau: string
  chu: string
  tocDo: number
  treSinh: number
  daSinh: boolean
  gioiHanTrai: number | null
  gen: KichBan
  xong: boolean
}

type LuotChay = {
  huy: () => void
}

const kep = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v))
const ngauNhien = (min: number, max: number) => min + Math.random() * (max - min)
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3)
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const giaiDich = (d: Dich): Diem => (typeof d === 'function' ? d() : d)

function docDaChayPhien(): boolean {
  try {
    return sessionStorage.getItem(KHOA_PHIEN) === '1'
  } catch {
    return false
  }
}

function ghiDaChayPhien() {
  try {
    sessionStorage.setItem(KHOA_PHIEN, '1')
  } catch {
    // Bỏ qua khi trình duyệt chặn sessionStorage
  }
}

function hopLeHienThi(el: HTMLElement, vw: number, vh: number): KhungChuNhat | null {
  const r = el.getBoundingClientRect()
  if (r.width < 50 || r.height < 32) return null
  if (r.top >= vh - 12 || r.bottom <= 12 || r.left >= vw - 12 || r.right <= 12) return null
  if (getComputedStyle(el).visibility === 'hidden') return null
  return { left: r.left, top: r.top, width: r.width, height: r.height }
}

function coKhoiKinhHienThi(): boolean {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const ds = document.querySelectorAll<HTMLElement>('.than .trang .kinh')
  for (const el of ds) {
    if (hopLeHienThi(el, vw, vh)) return true
  }
  return false
}

function chonKhoiDich(cheDo1: boolean): ViecKhoi[] {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const than = document.querySelector<HTMLElement>('.than')
  if (!than) return []

  const ungVien: HTMLElement[] = []
  const them = (ds: NodeListOf<HTMLElement>) => {
    ds.forEach((el) => ungVien.push(el))
  }

  if (cheDo1) {
    them(document.querySelectorAll<HTMLElement>('aside.canh > .hieu, aside.canh nav > div'))
  }
  them(than.querySelectorAll<HTMLElement>(':scope > header.dau > *'))
  them(
    than.querySelectorAll<HTMLElement>(
      cheDo1
        ? ':scope > main.trang .kinh, :scope > main.trang .mo-dau'
        : ':scope > main.trang .kinh',
    ),
  )

  const daThay = new Set<HTMLElement>()
  const hopLe: { el: HTMLElement; rect: KhungChuNhat; boGoc: string }[] = []

  for (const el of ungVien) {
    if (daThay.has(el)) continue
    if (!cheDo1 && el.closest('.canh')) continue
    if (el.closest('.dan-con-tro')) continue
    daThay.add(el)
    const rect = hopLeHienThi(el, vw, vh)
    if (!rect) continue
    const br = getComputedStyle(el).borderRadius
    hopLe.push({ el, rect, boGoc: br && br !== '0px' ? br : 'var(--bo-the)' })
  }

  // Bỏ khối con lồng bên trong một khối đích đã chọn để tránh 2 con trỏ vẽ chồng nhau
  const khongLong = hopLe.filter(
    (item) => !hopLe.some((khac) => khac.el !== item.el && khac.el.contains(item.el)),
  )

  khongLong.sort((a, b) => a.rect.top - b.rect.top || a.rect.left - b.rect.left)

  const toiDa = cheDo1 ? 12 : 8
  return khongLong.slice(0, toiDa).map((item) => ({
    el: item.el,
    rect: item.rect,
    trongMan:
      item.rect.top >= 0 &&
      item.rect.left >= 0 &&
      item.rect.top + item.rect.height <= vh &&
      item.rect.left + item.rect.width <= vw,
    trangThai: 'cho',
    boGoc: item.boGoc,
    khungEl: null,
    ktEl: null,
  }))
}

function layViecGanNhat(hangViec: ViecKhoi[], x: number, y: number): ViecKhoi | null {
  const conCho = hangViec.filter((v) => v.trangThai === 'cho')
  if (conCho.length === 0) return null
  const trongMan = conCho.filter((v) => v.trongMan)
  const nhom = trongMan.length > 0 ? trongMan : conCho

  let totNhat = nhom[0]
  let kcMin = Infinity
  for (const v of nhom) {
    const kc = Math.hypot(v.rect.left - x, v.rect.top - y)
    if (kc < kcMin) {
      kcMin = kc
      totNhat = v
    }
  }
  totNhat.trangThai = 'dang'
  return totNhat
}

function mepGanNhat(x: number, y: number, vw: number, vh: number): Diem {
  const dem = 44
  const dTrai = x
  const dPhai = vw - x
  const dTren = y
  const dDuoi = vh - y
  const min = Math.min(dTrai, dPhai, dTren, dDuoi)
  if (min === dTrai) return [-dem, kep(y + ngauNhien(-40, 40), 24, vh - 24)]
  if (min === dPhai) return [vw + dem, kep(y + ngauNhien(-40, 40), 24, vh - 24)]
  if (min === dTren) return [kep(x + ngauNhien(-50, 50), 24, vw - 24), -dem]
  return [kep(x + ngauNhien(-50, 50), 24, vw - 24), vh + dem]
}

function taoSvgConTro(): HTMLDivElement {
  const hinh = document.createElement('div')
  hinh.className = 'dct-hinh'
  // Mũi tên (điểm nóng 2, 2) và dấu cộng (điểm nóng 10, 10)
  hinh.innerHTML =
    '<svg class="dct-svg dct-mui-ten" viewBox="0 0 20 20" width="20" height="20">' +
    '<path d="M2 2L16.4 8.6L10.1 10.6L7.9 16.8L2 2Z" />' +
    '</svg>' +
    '<svg class="dct-svg dct-dau-cong" viewBox="0 0 20 20" width="20" height="20">' +
    '<path class="dct-vien" d="M10 3V17M3 10H17" />' +
    '<path class="dct-net" d="M10 3V17M3 10H17" />' +
    '</svg>'
  return hinh
}

function taoDomConTro(
  mau: MauConTro,
  coNhan: boolean,
): { el: HTMLDivElement; hinhEl: HTMLDivElement } {
  const el = document.createElement('div')
  el.className = 'dct-tro'
  el.dataset.hinh = 'mui-ten'
  el.style.setProperty('--mau-tro', mau.mau)
  el.style.setProperty('--chu-tro', mau.chu ?? '#fff')
  el.style.opacity = '0'

  const hinhEl = taoSvgConTro()
  el.appendChild(hinhEl)

  if (coNhan) {
    const nhan = document.createElement('span')
    nhan.className = 'dct-nhan'
    nhan.textContent = mau.ten
    el.appendChild(nhan)
  }

  return { el, hinhEl }
}

function taoDomKhung(
  viec: ViecKhoi,
  mau: string,
  chu: string,
): { khung: HTMLDivElement; kt: HTMLSpanElement } {
  const khung = document.createElement('div')
  khung.className = 'dct-khung'
  khung.style.setProperty('--mau-tro', mau)
  khung.style.setProperty('--chu-tro', chu)
  khung.style.borderRadius = viec.boGoc
  khung.style.transform = `translate3d(${viec.rect.left.toFixed(1)}px, ${viec.rect.top.toFixed(1)}px, 0)`
  khung.style.width = '2px'
  khung.style.height = '2px'

  const kt = document.createElement('span')
  kt.className = 'dct-kt'
  kt.style.opacity = '0'
  khung.appendChild(kt)

  viec.khungEl = khung
  viec.ktEl = kt
  return { khung, kt }
}

function datViTri(ct: ConTro, x: number, y: number) {
  ct.x = x
  ct.y = y
  ct.el.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, 0)`
}

function datDoMo(ct: ConTro, mo: number) {
  ct.doMo = mo
  ct.el.style.opacity = mo.toFixed(3)
}

function datTyLe(ct: ConTro, tl: number) {
  ct.tyLe = tl
  ct.hinhEl.style.transform = tl === 1 ? '' : `scale(${tl.toFixed(3)})`
}

function datHinh(ct: ConTro, hinh: HinhTro) {
  if (ct.hinh === hinh) return
  ct.hinh = hinh
  ct.el.dataset.hinh = hinh
}

function moKhoiThat(viec: ViecKhoi) {
  if (viec.trangThai === 'xong') return
  viec.trangThai = 'xong'
  const ms = Math.round(ngauNhien(220, 350))
  viec.el.style.setProperty('--dct-hien', `${ms}ms`)
  viec.el.dataset.danTro = 'hien'
  if (viec.khungEl) viec.khungEl.classList.add('xong')
}

function* cho(giay: number): KichBan {
  let daQua = 0
  while (daQua < giay) {
    const dt = yield
    daQua += dt
  }
}

function* hienDan(ct: ConTro, giay: number): KichBan {
  let daQua = 0
  datDoMo(ct, 0)
  while (daQua < giay) {
    const dt = yield
    daQua += dt
    datDoMo(ct, Math.min(1, daQua / giay))
  }
  datDoMo(ct, 1)
}

function* anDan(ct: ConTro, giay: number): KichBan {
  let daQua = 0
  const batDau = ct.doMo
  while (daQua < giay) {
    const dt = yield
    daQua += dt
    datDoMo(ct, Math.max(0, batDau * (1 - daQua / giay)))
  }
  datDoMo(ct, 0)
}

function* nhan(ct: ConTro): KichBan {
  const nua = 0.035
  let daQua = 0
  while (daQua < nua) {
    const dt = yield
    daQua += dt
    const p = Math.min(1, daQua / nua)
    datTyLe(ct, 1 - 0.12 * p)
  }
  daQua = 0
  while (daQua < nua) {
    const dt = yield
    daQua += dt
    const p = Math.min(1, daQua / nua)
    datTyLe(ct, 0.88 + 0.12 * p)
  }
  datTyLe(ct, 1)
}

function* diToi(ct: ConTro, dich: Dich, moCuoi?: boolean): KichBan {
  const x0 = ct.x
  const y0 = ct.y
  const [tx0, ty0] = giaiDich(dich)
  const dx0 = tx0 - x0
  const dy0 = ty0 - y0
  const kc = Math.hypot(dx0, dy0)
  const thoiLuong = kep(0.12 + Math.sqrt(kc) * 0.021, 0.14, 0.9)

  // Độ lệch vuông góc tạo đường bay cong tự nhiên; mỗi lượt bay một độ cong ngẫu nhiên mới
  const px = kc > 0.5 ? -dy0 / kc : 0
  const py = kc > 0.5 ? dx0 / kc : 0
  const doCong = (Math.random() < 0.5 ? -1 : 1) * ngauNhien(0.04, 0.14) * Math.min(kc, 600)

  let daQua = 0
  while (daQua < thoiLuong) {
    const dt = yield
    daQua += dt
    const t = Math.min(1, daQua / thoiLuong)
    const e = easeOut(t)
    const [tx, ty] = giaiDich(dich)
    const lech = Math.sin(Math.PI * e) * doCong
    let nx = x0 + (tx - x0) * e + px * lech
    const ny = y0 + (ty - y0) * e + py * lech
    if (ct.gioiHanTrai !== null) nx = Math.max(ct.gioiHanTrai, nx)
    datViTri(ct, nx, ny)
    if (moCuoi && t > 0.55) {
      datDoMo(ct, Math.max(0, 1 - (t - 0.55) / 0.45))
    }
  }

  const [tx, ty] = giaiDich(dich)
  datViTri(ct, ct.gioiHanTrai !== null ? Math.max(ct.gioiHanTrai, tx) : tx, ty)
  if (moCuoi) datDoMo(ct, 0)
}

function* keoToi(ct: ConTro, dich: Dich, onVe: (x: number, y: number) => void): KichBan {
  const x0 = ct.x
  const y0 = ct.y
  const [tx0, ty0] = giaiDich(dich)
  const kc = Math.hypot(tx0 - x0, ty0 - y0)
  // Kéo đi thẳng (bend = 0), easeInOut, chậm hơn ~0,75 lần so với di chuyển tự do
  const thoiLuong = kep(0.12 + Math.sqrt(kc) * 0.021, 0.14, 0.9) / 0.75

  let daQua = 0
  while (daQua < thoiLuong) {
    const dt = yield
    daQua += dt
    const t = Math.min(1, daQua / thoiLuong)
    const e = easeInOut(t)
    const [tx, ty] = giaiDich(dich)
    let nx = x0 + (tx - x0) * e
    const ny = y0 + (ty - y0) * e
    if (ct.gioiHanTrai !== null) nx = Math.max(ct.gioiHanTrai, nx)
    datViTri(ct, nx, ny)
    onVe(nx, ny)
  }

  const [tx, ty] = giaiDich(dich)
  const fx = ct.gioiHanTrai !== null ? Math.max(ct.gioiHanTrai, tx) : tx
  datViTri(ct, fx, ty)
  onVe(fx, ty)
}

function* dungMotKhoi(
  ct: ConTro,
  viec: ViecKhoi,
  lopKhung: HTMLDivElement,
  cheDo1: boolean,
): KichBan {
  // 1. Đổi sang dấu cộng và tới góc trên-trái khối
  datHinh(ct, 'dau-cong')
  yield* diToi(ct, () => [viec.rect.left, viec.rect.top])

  // 2. Nhấn giữ chuột (co nhẹ 0.88 rồi hồi lại)
  yield* nhan(ct)

  // 3. Kéo khung tạm từ góc trên-trái xuống góc dưới-phải
  const { khung, kt } = taoDomKhung(viec, ct.mau, ct.chu)
  lopKhung.appendChild(khung)

  yield* keoToi(
    ct,
    () => [viec.rect.left + viec.rect.width, viec.rect.top + viec.rect.height],
    (cx, cy) => {
      const w = Math.max(4, cx - viec.rect.left)
      const h = Math.max(4, cy - viec.rect.top)
      khung.style.transform = `translate3d(${viec.rect.left.toFixed(1)}px, ${viec.rect.top.toFixed(1)}px, 0)`
      khung.style.width = `${w.toFixed(1)}px`
      khung.style.height = `${h.toFixed(1)}px`
      kt.textContent = `${Math.round(w)} × ${Math.round(h)}`
      kt.style.opacity = w >= 64 && h >= 28 ? '1' : '0'
    },
  )

  // 4. Thả chuột: chờ ngắn 0,18–0,3 s rồi CSS transition hiện khối thật và mờ khung tạm
  yield* cho(cheDo1 ? ngauNhien(0.18, 0.3) : ngauNhien(0.18, 0.24))
  moKhoiThat(viec)

  // 5. Về lại mũi tên để lấy việc tiếp theo
  datHinh(ct, 'mui-ten')
}

function* kichBanConTro(
  ct: ConTro,
  hangViec: ViecKhoi[],
  lopKhung: HTMLDivElement,
  cheDo1: boolean,
  viecDau: ViecKhoi | null,
  heSoNhip: number,
): KichBan {
  if (cheDo1) {
    datDoMo(ct, 1)
  } else {
    // Chế độ 2: hiện ngay tại chỗ gần khối (fade-in ~80 ms thời gian thực), không bay từ mép vào
    yield* hienDan(ct, 0.08 * heSoNhip * ct.tocDo)
  }

  let viec: ViecKhoi | null = viecDau ?? layViecGanNhat(hangViec, ct.x, ct.y)
  while (viec) {
    yield* dungMotKhoi(ct, viec, lopKhung, cheDo1)
    viec = layViecGanNhat(hangViec, ct.x, ct.y)
  }

  if (cheDo1) {
    datHinh(ct, 'mui-ten')
    const dichRa = mepGanNhat(ct.x, ct.y, window.innerWidth, window.innerHeight)
    yield* diToi(ct, dichRa, true)
  } else {
    // Chế độ 2: mờ đi tại chỗ, không bay ra
    yield* anDan(ct, 0.14 * heSoNhip * ct.tocDo)
  }
}

function taoTocDo(soConTro: number): number[] {
  // ~25% con nhanh, còn lại chậm hơn để chuyển động tự nhiên, không đều tăm tắp
  const soNhanh = Math.max(1, Math.round(soConTro * 0.25))
  const ds: number[] = []
  for (let i = 0; i < soConTro; i++) {
    ds.push(i < soNhanh ? ngauNhien(1.16, 1.3) : ngauNhien(0.84, 1.02))
  }
  for (let i = ds.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[ds[i], ds[j]] = [ds[j], ds[i]]
  }
  return ds
}

// Đàn con trỏ dựng trang (v4): gắn MỘT chỗ trong KhungTrang (App.tsx).
// - Chế độ 1 (lần đầu trong phiên trình duyệt): 6–8 con trỏ bay từ hai mép vào, kèm nhãn vai trò, dựng cả menu trái, ~2–3 s.
// - Chế độ 2 (đổi mục trên menu trái): 3–4 con trỏ hiện tại chỗ trong div.than, bỏ nhãn, không chạm menu trái, ≤ 1,5 s.
export default function DanConTro({ pathname }: { pathname: string }) {
  const lopPhuRef = useRef<HTMLDivElement>(null)
  const luotRef = useRef<LuotChay | null>(null)

  useEffect(() => {
    // Dọn sạch lượt cũ nếu đang chạy (đổi trang giữa chừng hoặc StrictMode)
    luotRef.current?.huy()
    luotRef.current = null

    const lopPhu = lopPhuRef.current
    if (!lopPhu || !dangHieuUng()) {
      if (!TRANG_GOC.has(pathname)) pathnameTruoc = pathname
      return
    }
    if (TRANG_GOC.has(pathname)) return

    const daChayPhien = docDaChayPhien()
    const cheDo1 = !daChayPhien

    // Tải lại trang trong cùng phiên (F5): không chạy lại màn đầu phiên, ghi nhận trang hiện tại rồi thôi
    if (daChayPhien && pathnameTruoc === null) {
      pathnameTruoc = pathname
      return
    }
    // Bấm lại đúng trang đang mở
    if (daChayPhien && pathname === pathnameTruoc) return

    let daHuy = false
    let raf = 0
    let rafQuet = 0
    let henCho = 0
    let henDonCuoi = 0
    let mo: MutationObserver | null = null
    let hangViec: ViecKhoi[] = []
    let dsTro: ConTro[] = []
    let langNghe = false

    const goLangNghe = () => {
      if (!langNghe) return
      langNghe = false
      window.removeEventListener('pointerdown', khiBoQua, true)
      window.removeEventListener('keydown', khiBoQua, true)
      window.removeEventListener('wheel', khiBoQua, true)
      window.removeEventListener('scroll', khiBoQua, true)
      window.removeEventListener('resize', khiDoiCo)
      document.removeEventListener('visibilitychange', khiAnTab)
    }

    const xoaTrangThaiKhoi = () => {
      for (const v of hangViec) {
        delete v.el.dataset.danTro
        v.el.style.removeProperty('--dct-hien')
      }
      hangViec = []
    }

    const donSach = (ghiNhanPhien: boolean) => {
      if (daHuy) return
      daHuy = true
      if (raf) {
        cancelAnimationFrame(raf)
        raf = 0
      }
      if (rafQuet) {
        cancelAnimationFrame(rafQuet)
        rafQuet = 0
      }
      if (henCho) {
        window.clearTimeout(henCho)
        henCho = 0
      }
      if (henDonCuoi) {
        window.clearTimeout(henDonCuoi)
        henDonCuoi = 0
      }
      if (mo) {
        mo.disconnect()
        mo = null
      }
      goLangNghe()
      xoaTrangThaiKhoi()
      lopPhu.replaceChildren()
      lopPhu.style.display = 'none'
      if (ghiNhanPhien) {
        if (cheDo1) ghiDaChayPhien()
        pathnameTruoc = pathname
      }
      if (luotRef.current === luot) luotRef.current = null
    }

    const luot: LuotChay = {
      huy: () => donSach(false),
    }
    luotRef.current = luot

    function khiBoQua() {
      donSach(true)
    }

    function khiAnTab() {
      if (document.hidden || !dangHieuUng()) donSach(true)
    }

    function khiDoiCo() {
      const vw = window.innerWidth
      const vh = window.innerHeight
      for (const v of hangViec) {
        const r = v.el.getBoundingClientRect()
        v.rect = { left: r.left, top: r.top, width: r.width, height: r.height }
        v.trongMan = r.top >= 0 && r.left >= 0 && r.bottom <= vh && r.right <= vw
      }
      if (!cheDo1) {
        const rThan = document.querySelector<HTMLElement>('.than')?.getBoundingClientRect()
        const traiMoi = rThan ? rThan.left + 4 : 0
        for (const ct of dsTro) ct.gioiHanTrai = traiMoi
      }
    }

    const batDauChay = () => {
      if (daHuy) return
      if (!dangHieuUng() || document.hidden) {
        donSach(true)
        return
      }

      hangViec = chonKhoiDich(cheDo1)
      if (hangViec.length === 0) {
        donSach(true)
        return
      }

      const thanEl = document.querySelector<HTMLElement>('.than')
      const thanRect = thanEl?.getBoundingClientRect()
      const gioiHanTrai = cheDo1 ? null : thanRect ? thanRect.left + 4 : 0

      // Ẩn mềm các khối đích bằng opacity (giữ nguyên kích thước, không nhảy bố cục)
      for (const v of hangViec) {
        v.el.dataset.danTro = 'cho'
      }

      const lopKhung = document.createElement('div')
      lopKhung.className = 'dct-lop-khung'
      const lopTro = document.createElement('div')
      lopTro.className = 'dct-lop-tro'
      lopPhu.replaceChildren(lopKhung, lopTro)
      lopPhu.style.display = 'block'

      const vw = window.innerWidth
      const vh = window.innerHeight
      const soKhoi = hangViec.length
      const soConTro = cheDo1 ? Math.min(8, Math.max(1, soKhoi)) : Math.min(4, Math.max(1, soKhoi))

      // Hệ số nhịp chung nhân vào dt theo tỷ lệ số khối / số con trỏ:
      // Chế độ 1 ~2–3 s, Chế độ 2 ≤ 1,5 s (tính cả thời gian CSS transition hiện khối cuối)
      const tbKhoi = soKhoi / soConTro
      const heSoNhip = cheDo1
        ? Math.max(1.25, (0.9 + tbKhoi * 1.35) / 2.15)
        : Math.max(1.55, (0.22 + tbKhoi * 1.35) / 0.92)

      const tocDos = taoTocDo(soConTro)
      dsTro = []

      for (let i = 0; i < soConTro; i++) {
        const mau = DS_CON_TRO[i % DS_CON_TRO.length]
        const { el, hinhEl } = taoDomConTro(mau, cheDo1)
        lopTro.appendChild(el)

        let x0: number
        let y0: number
        let viecDau: ViecKhoi | null = null

        if (cheDo1) {
          const tuTrai = i % 2 === 0
          x0 = tuTrai ? -36 : vw + 36
          y0 = kep(
            vh * (0.12 + (i / Math.max(1, soConTro - 1)) * 0.72) + ngauNhien(-32, 32),
            24,
            vh - 24,
          )
        } else {
          // Chế độ 2: giữ trước một khối cho mỗi con trỏ và xuất hiện ngay gần khối đó trong vùng div.than
          viecDau = hangViec[i] ?? null
          if (viecDau) {
            viecDau.trangThai = 'dang'
            const minX = (gioiHanTrai ?? 0) + 6
            const maxX = Math.max(minX, (thanRect?.right ?? vw) - 24)
            x0 = kep(viecDau.rect.left + ngauNhien(16, 68), minX, maxX)
            y0 = kep(viecDau.rect.top + ngauNhien(12, 46), 16, vh - 24)
          } else {
            x0 = (gioiHanTrai ?? 0) + 40
            y0 = 80
          }
        }

        const ct: ConTro = {
          el,
          hinhEl,
          x: x0,
          y: y0,
          doMo: 0,
          tyLe: 1,
          hinh: 'mui-ten',
          mau: mau.mau,
          chu: mau.chu ?? '#fff',
          tocDo: tocDos[i],
          treSinh: cheDo1 ? i * ngauNhien(0.035, 0.04) : i * 0.018,
          daSinh: false,
          gioiHanTrai,
          gen: null as unknown as KichBan,
          xong: false,
        }
        datViTri(ct, x0, y0)
        ct.gen = kichBanConTro(ct, hangViec, lopKhung, cheDo1, viecDau, heSoNhip)
        dsTro.push(ct)
      }

      window.addEventListener('pointerdown', khiBoQua, { capture: true, passive: true })
      window.addEventListener('keydown', khiBoQua, { capture: true })
      window.addEventListener('wheel', khiBoQua, { capture: true, passive: true })
      window.addEventListener('scroll', khiBoQua, { capture: true, passive: true })
      window.addEventListener('resize', khiDoiCo)
      document.addEventListener('visibilitychange', khiAnTab)
      langNghe = true

      let truoc = performance.now()
      let tongThoiGian = 0
      let daGhiDuongDan = false
      const tran = cheDo1 ? TRAN_CHE_DO_1 : TRAN_CHE_DO_2

      const buoc = (now: number) => {
        if (daHuy) return
        if (!dangHieuUng() || document.hidden) {
          donSach(true)
          return
        }

        if (!daGhiDuongDan) {
          daGhiDuongDan = true
          // Chỉ cập nhật sau khung rAF đầu tiên (không chạy trong lần mount giả của StrictMode)
          pathnameTruoc = pathname
        }

        const dt = Math.min((now - truoc) / 1000, DT_TOI_DA)
        truoc = now
        tongThoiGian += dt

        // Đảm bảo không bao giờ kéo dài quá trần thời gian
        if (tongThoiGian >= tran) {
          for (const v of hangViec) moKhoiThat(v)
          for (const ct of dsTro) datDoMo(ct, 0)
          goLangNghe()
          if (cheDo1) ghiDaChayPhien()
          henDonCuoi = window.setTimeout(() => donSach(true), 320)
          return
        }

        let conHoatDong = false
        for (const ct of dsTro) {
          if (ct.xong) continue
          if (!ct.daSinh) {
            if (tongThoiGian < ct.treSinh) {
              conHoatDong = true
              continue
            }
            ct.daSinh = true
            // Mồi generator tới điểm yield đầu tiên
            const moi = ct.gen.next()
            if (moi.done) {
              ct.xong = true
              ct.el.remove()
              continue
            }
            conHoatDong = true
            continue
          }

          const dtTro = dt * heSoNhip * ct.tocDo
          const kq = ct.gen.next(dtTro)
          if (kq.done) {
            ct.xong = true
            ct.el.remove()
          } else {
            conHoatDong = true
          }
        }

        if (conHoatDong) {
          raf = requestAnimationFrame(buoc)
        } else {
          // Mở nốt khối nào lỡ còn sót, chờ CSS transition chốt xong rồi gỡ thuộc tính và lớp phủ
          for (const v of hangViec) moKhoiThat(v)
          goLangNghe()
          if (cheDo1) ghiDaChayPhien()
          henDonCuoi = window.setTimeout(() => donSach(true), 360)
        }
      }

      raf = requestAnimationFrame(buoc)
    }

    // Nếu trang đã có khối .kinh nhìn thấy thì chạy luôn; nếu đang tải dữ liệu thì chờ tối đa ~600 ms
    if (coKhoiKinhHienThi()) {
      batDauChay()
    } else {
      const gocTheoDoi = document.querySelector('.than') ?? document.body
      const thuChay = () => {
        if (daHuy) return
        if (coKhoiKinhHienThi()) {
          if (mo) {
            mo.disconnect()
            mo = null
          }
          if (henCho) {
            window.clearTimeout(henCho)
            henCho = 0
          }
          batDauChay()
        }
      }
      mo = new MutationObserver(() => {
        if (!rafQuet) {
          rafQuet = requestAnimationFrame(() => {
            rafQuet = 0
            thuChay()
          })
        }
      })
      mo.observe(gocTheoDoi, { childList: true, subtree: true })
      henCho = window.setTimeout(() => {
        henCho = 0
        // Quá 600 ms không có khối .kinh thì bỏ qua lượt này, không hiện gì lạ
        donSach(true)
      }, CHO_KHOI_MS)
    }

    return () => {
      donSach(false)
    }
  }, [pathname])

  return (
    <div ref={lopPhuRef} className="dan-con-tro" aria-hidden="true" style={{ display: 'none' }} />
  )
}
