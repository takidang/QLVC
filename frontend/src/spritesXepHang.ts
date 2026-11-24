// Dữ liệu sprite pixel art thuần cho màn "Xếp hàng lên xe" ở phong cách Pixel.
// Mỗi ký tự trong mảng chuỗi tương ứng một ô vuông lưới (scale nguyên 4 ⇒ 4×4 đơn vị SVG);
// dấu '.' và ký tự lạ đều rơi vào trong suốt.

export type BangMauPixel = Readonly<Record<string, string>>

export type DoanPixel = {
  readonly x: number
  readonly y: number
  readonly w: number
  readonly h: number
  readonly fill: string
}

export type SpriteDaGop = {
  readonly rong: number
  readonly cao: number
  readonly doan: readonly DoanPixel[]
}

export type KienDaXep = {
  sprite: SpriteDaGop
  x: number
  y: number
}

// Ngưỡng tỉ lệ khoang (f = w / (x1 - x0)) để chọn cỡ kiện hàng trong "Xếp hàng lên xe"
export const NGUONG_NHO = 0.12
export const NGUONG_VUA = 0.3
export const NGUONG_LON = 0.7

// Bảng màu thùng container, đầu xe, gầm và bánh xe: ưu tiên biến Nostalgos,
// bổ sung sắc độ thép xanh, vách xám sáng và sàn gỗ nâu để phân khối sáng/tối rõ nét.
export const MAU_XE: BangMauPixel = {
  // Viền và bóng tối
  k: 'var(--n-charcoal)', // #272a32 — viền than
  o: '#152e35', // lỗ khóa 2×1 trong khối góc container (không viền đen riêng)
  S: '#183f47', // thép xanh rất đậm (bóng góc dưới-phải, khe sâu)
  // 3 sắc thép xanh thân thùng & đầu xe
  d: 'var(--n-teal)', // #21525a — thép xanh đậm (khối góc đậm hơn khung 1 nấc, bóng dầm)
  m: '#38767d', // thép xanh vừa (dầm nóc, dầm sàn, cột góc, thân ca-bin)
  l: '#6aa9a8', // thép xanh sáng (cạnh trên-trái bắt sáng)
  h: '#a4d3cc', // điểm sáng thép góc trên-trái
  // Kim loại sáng (thanh chốt cửa, ống xả, lưới tản nhiệt, vành bánh, bình dầu)
  r: '#cad4d2', // kim loại sáng
  R: '#98a3a5', // kim loại xám vừa
  // Lòng thùng rỗng sáng (vách trong xám nhạt có gân đứng)
  W: '#ece8df', // vách trong sáng
  g: '#dad5ca', // gân vách xám nhạt
  c: '#c2bdb1', // bóng gân vách & bóng dưới dầm nóc
  // Sàn gỗ ván nâu có vạch
  U: '#e5be8a', // mặt ván gỗ sáng
  u: '#cfa067', // mặt ván gỗ vừa
  w: '#b5844c', // mép trước sàn gỗ
  f: '#7f5834', // vạch khe giữa các tấm ván gỗ
  // Kính, đèn và dải nhấn đầu xe
  K: '#b9e3e8', // vệt phản quang kính lái
  G: 'var(--n-sky)', // #5a8bde — kính lái & kính cửa xanh trời
  E: '#325a94', // bóng đáy kính
  Y: 'var(--n-butter)', // #ffd183 — đèn pha & sọc vàng bơ
  O: 'var(--n-ochre)', // #eeb24a — bóng sọc vàng / xi-nhan
  A: 'var(--n-coral)', // #dc6250 — đèn hậu, đèn nóc & xi-nhan san hô
  // Gầm xe, lốp cao su và bóng mặt đất
  T: '#3e4450', // lốp cao su / cản thép tối
  t: '#5a6270', // gầm thép xám / má lốp sáng
  N: '#b8b1a3', // bóng đổ mặt đất dưới gầm xe
}

// Bảng màu 4 kiểu kiện hàng (carton, thùng gỗ, phuy, bao có pallet)
export const MAU_HANG: BangMauPixel = {
  k: 'var(--n-charcoal)', // #272a32 — viền than
  // Thùng carton có băng keo
  c: '#ecc78f', // nắp trên carton sáng
  C: '#d7a565', // thân carton vừa
  b: '#b47f45', // bóng dưới nắp / hông phải carton
  B: '#8c5d2f', // bóng sâu giữa các thùng
  p: '#8c9099', // băng keo xám vừa
  P: '#b6bac2', // vệt sáng băng keo
  l: 'var(--noi)', // #f1ede5 — tem vận đơn nhỏ
  // Thùng gỗ đóng đai & pallet gỗ
  w: '#e6be86', // nan gỗ sáng
  W: '#c99658', // nan gỗ vừa
  g: '#9b6d3b', // khe ván & bóng gỗ
  G: '#6f4a26', // bóng sâu trong khe pallet / góc gỗ
  i: '#464d59', // đai sắt tối
  I: '#6b7482', // đai sắt sáng
  r: '#cad4d2', // đinh tán sắt / vành đai phuy sáng
  // Phuy thép (xanh lá & xanh dương Nostalgos)
  e: 'var(--n-sage)', // #55927f — phuy xanh lá sáng
  E: '#35715f', // phuy xanh lá vừa
  v: 'var(--n-teal)', // #21525a — phuy xanh lá đậm
  s: 'var(--n-sky)', // #5a8bde — phuy xanh dương sáng
  S: 'var(--n-cobalt)', // #2152a5 — phuy xanh dương vừa
  d: '#183a75', // phuy xanh dương đậm
  R: '#8d99a1', // nắp và đai phuy xám vừa
  // Bao tải trên pallet
  a: '#f4f0e8', // mặt sáng trên bao
  A: 'var(--n-cream)', // #dad4c9 — thân bao màu kem
  n: '#bcb5a8', // bóng dưới bao
  N: '#8f897e', // nếp gấp giữa các bao
  t: 'var(--n-coral)', // #dc6250 — vạch chỉ nhận diện trên bao
}

// Gộp các ô liền kề cùng màu trên một hàng, rồi gộp thêm các hàng kề nhau có cùng (x, w, fill)
// để giảm mạnh số thẻ <rect> trong SVG mà vẫn giữ đúng từng ô pixel 100 %.
export function chuanBiSprite(hang: readonly string[], mau: BangMauPixel): SpriteDaGop {
  const cao = hang.length
  let rong = 0
  const tam: { x: number; y: number; w: number; h: number; fill: string }[] = []
  let truoc = new Map<string, { x: number; y: number; w: number; h: number; fill: string }>()

  for (let y = 0; y < cao; y++) {
    const dong = hang[y] ?? ''
    if (dong.length > rong) rong = dong.length
    const hienTai = new Map<string, { x: number; y: number; w: number; h: number; fill: string }>()
    let x = 0
    while (x < dong.length) {
      const kt = dong[x]
      const fill = kt !== '.' && Object.hasOwn(mau, kt) ? mau[kt] : undefined
      if (!fill) {
        x++
        continue
      }
      let w = 1
      while (x + w < dong.length) {
        const ktKe = dong[x + w]
        const fillKe = ktKe !== '.' && Object.hasOwn(mau, ktKe) ? mau[ktKe] : undefined
        if (fillKe !== fill) break
        w++
      }
      const khoa = `${x}:${w}:${fill}`
      const coSan = truoc.get(khoa)
      if (coSan) {
        coSan.h += 1
        hienTai.set(khoa, coSan)
      } else {
        const o = { x, y, w, h: 1, fill }
        tam.push(o)
        hienTai.set(khoa, o)
      }
      x += w
    }
    truoc = hienTai
  }

  return { rong, cao, doan: tam }
}

// Hằng tỷ lệ & toạ độ lưới (đơn vị SVG, scale = 4 ⇒ mỗi ô = 4×4 đơn vị SVG)
export const TI_LE_PIXEL = 4
// Thùng container: 115×38 ô ⇒ 460×152 đơn vị SVG, đặt tại (8, 12) → [8..468] × [12..164]
export const CONTAINER_X = 8
export const CONTAINER_Y = 12
// Vùng lòng thùng mở (nơi xếp các kiện hàng): cột 7..99 (93 ô = 372), hàng 5..32 (28 ô = 112)
export const PX0 = CONTAINER_X + 7 * TI_LE_PIXEL // 36
export const PX1 = CONTAINER_X + 100 * TI_LE_PIXEL // 408
export const PY0 = CONTAINER_Y + 5 * TI_LE_PIXEL // 32
export const PY1 = CONTAINER_Y + 33 * TI_LE_PIXEL // 144
// Đầu xe tải: 31×31 ô ⇒ 124×124, nối khít mép phải thùng tại x = 468
export const DAU_XE_X = CONTAINER_X + 115 * TI_LE_PIXEL // 468
export const DAU_XE_Y = 52
// Gầm xe + bình dầu + thanh chắn hông + bóng mặt đất: 146×12 ô ⇒ 584×48 tại (8, 164)
export const GAM_XE_X = 8
export const GAM_XE_Y = 164
// 3 bánh xe pixel (10×10 ô ⇒ 40×40): 2 bánh sau dưới thùng, 1 bánh trước dưới ca-bin
export const VI_TRI_BANH_X: readonly number[] = [76, 132, 508]
export const BANH_XE_Y = 168

// 1. Thùng container nhìn ngang (115×38 ô):
//    - 4 khối góc liền mạch với khung (rộng 5 ô, vát góc 1 ô ngoài, sáng trên-trái, tối dưới-phải,
//      lỗ khóa 2×1 không viền đen riêng)
//    - Dầm nóc và dầm sàn dày đều 3 ô (dầm sàn có 2 khe càng xe nâng)
//    - Lòng thùng mở sáng: vách trong xám nhạt có gân đứng + sàn gỗ ván nâu có vạch
//    - Hông phải: cánh cửa có gân đứng, 2 thanh chốt inox, tay gạt và 3 bản lề
const GIUA_DAM_NOC_1 = 'll' + 'llllllllllllllhl'.repeat(5) + 'lllllllllllll' // 95 ô
const GIUA_VACH_TRONG = 'kc' + 'WWgc'.repeat(22) + 'WWgck' // 95 ô
const GIUA_SAN_GO_MAT = 'kUUuf' + 'UUUuuf'.repeat(14) + 'UUUuuk' // 95 ô
const GIUA_SAN_GO_MEP = 'kwwwf' + 'wwwwwf'.repeat(14) + 'wwwwwk' // 95 ô
const GIUA_DAM_SAN_2 = 'm'.repeat(20) + 'SooooooS' + 'm'.repeat(39) + 'SooooooS' + 'm'.repeat(20) // 95 ô
const GIUA_DAM_SAN_3 = 'd'.repeat(20) + 'SSSSSSSS' + 'd'.repeat(39) + 'SSSSSSSS' + 'd'.repeat(20) // 95 ô

const HANG_CUA_THUONG = 'drmSmrdk' // 8 ô: gân đứng + 2 thanh chốt r
const HANG_CUA_GIU = 'dkmSmkdk' // 8 ô: ngàm giữ thanh chốt
const HANG_CUA_BAN_LE = 'drmSmrkk' // 8 ô: bản lề phải
const HANG_CUA_TAY = 'drkSmrkk' // 8 ô: tay gạt chốt cửa

const cuaTaiHang = (r: number): string => {
  if (r === 4 || r === 32) return HANG_CUA_GIU
  if (r === 7 || r === 19 || r === 30) return HANG_CUA_BAN_LE
  if (r === 21 || r === 22) return HANG_CUA_TAY
  return HANG_CUA_THUONG
}

// Tổng mỗi dòng = 6 (trái) + 95 (giữa) + 6 (phải) + 8 (cửa phải) = 115 ô
export const LUOI_CONTAINER: readonly string[] = [
  '.kkkkk' + 'k'.repeat(95) + 'kkkkk.' + '........', // r0: viền trên, vát 1 ô ở 2 góc
  'khllld' + GIUA_DAM_NOC_1 + 'hllldk' + 'kkkkkkk.', // r1: dầm nóc hàng 1 + viền trên cửa
  'kldooS' + 'm'.repeat(95) + 'ldooSk' + 'lllllddk', // r2: dầm nóc hàng 2 + lỗ khóa 2×1
  'kddSSS' + 'd'.repeat(95) + 'ddSSSk' + HANG_CUA_THUONG, // r3: dầm nóc hàng 3 + bóng góc
  'klmmdS' + 'k'.repeat(95) + 'lmmdSk' + cuaTaiHang(4), // r4: mép trong trên + cột góc 5 ô
  'klmmdS' + 'k' + 'c'.repeat(93) + 'k' + 'lmmdSk' + cuaTaiHang(5), // r5: bóng trần lòng thùng
  ...Array.from(
    { length: 25 },
    (_, i) => 'klmmdS' + GIUA_VACH_TRONG + 'lmmdSk' + cuaTaiHang(6 + i),
  ), // r6..r30: vách trong sáng có gân đứng + cửa hông phải
  'klmmdS' + 'k' + 'f'.repeat(93) + 'k' + 'lmmdSk' + cuaTaiHang(31), // r31: chân vách gặp sàn gỗ
  'klmmdS' + GIUA_SAN_GO_MAT + 'lmmdSk' + cuaTaiHang(32), // r32: mặt sàn gỗ ván nâu có vạch
  'klmmdS' + GIUA_SAN_GO_MEP + 'lmmdSk' + cuaTaiHang(33), // r33: mép trước sàn gỗ
  'khllld' + 'l'.repeat(95) + 'hllldk' + HANG_CUA_THUONG, // r34: dầm sàn hàng 1
  'kldooS' + GIUA_DAM_SAN_2 + 'ldooSk' + 'dddddSSk', // r35: dầm sàn hàng 2 + lỗ khóa 2×1
  'kddSSS' + GIUA_DAM_SAN_3 + 'ddSSSk' + 'kkkkkkk.', // r36: dầm sàn hàng 3 + viền dưới cửa
  '.kkkkk' + 'k'.repeat(95) + 'kkkkk.' + '........', // r37: viền dưới, vát 1 ô ở 2 góc
]

// 2. Đầu xe tải pixel (31×31 ô, hướng sang phải, nối khít mép phải thùng container):
//    ống xả đứng sát vách thùng, kính lái xiên có phản quang, gương chiếu hậu, sọc vàng bơ,
//    lưới tản nhiệt, đèn pha, xi-nhan, cản trước thép dày và hốc bánh trước.
// Thước cột:       0123456789012345678901234567890 (31 ô)
export const LUOI_DAU_XE: readonly string[] = [
  '.kk............................',
  'krkkkkkkkkkkkkkkkkkkkkk........',
  'krkhlllllllllllllllllAAk.......',
  'krklmmmmmmmmmmmmmmmmmmmdk......',
  'kRklmkkkkkkkkkkmkkkkkkkkdk.....',
  'kRklmkGGGGGGGKkmkGGGGKKGkdk....',
  'kRklmkGGGGGKKGkmkGGGKKGGkdk....',
  'kRklmkGGGGKKGGkmkGGKKGGGGkdk...',
  'kRklmkGGGKKGGGkmkGKKGGGGGkdk...',
  'kRklmkGGKKGGGGkmkKKGGGGGGkdkkk.',
  'kRklmkGGGGGGGGkmkGGGGGGGGGkdkRk',
  'kRklmkGGGGGGGGkmkGGGGGGGGGkdkRk',
  'kRklmkGGGGGGGGkmkGGGGGGGGGkdkk.',
  'kRklmkEEEEEEEEkmkEEEEEEEEEkdk..',
  'kRklmkkkkkkkkkkmkkkkkkkkkkkdk..',
  'kRklmmmmmmmmmmmdmmmmmmmmmmmmdk.',
  'kRklYYYYYYYYYYYYYYYYYYYYYYYYYk.',
  'kRklOOOOOOOOOOOdOOOOOOOOOOOOOk.',
  'kRklmmmdmmmmmmmdmmmmmmkkkkkkkk.',
  'kRklmmmdrrrmmmmdmmmmmkTrrrrTTk.',
  'kRklmmmdmmmmmmmdmmmmmkTTTTTTTk.',
  'kRklmmmdmmmmmmmdmmmmmkTrrrrTTk.',
  'kRklmmmdmmmmmmmdmmmmmkTTTYYAAk.',
  'kRklmmmdmmmmmmmdmmmmmkTTTYYAAk.',
  'kRkddddddkkkkkkkkkkkkdkkkkkkkk.',
  'kTkdddddkTTTTTTTTTTTTkdmmmmmmk.',
  'kTkddddkTTkkkkkkkkkkTTkmmmmmmk.',
  'kTkdddkTTkkkkkkkkkkkkTTkkkkkkkk',
  'kTkkkkkTTkTTTTTTTTTTkTTkttttttk',
  'kkkkddkTTkTTTTTTTTTTkTTkTTTTTTk',
  '....kkkk.k..........k..kkkkkkkk',
]

// 3. Gầm xe, đèn hậu, chắn bùn, bình dầu inox, thanh chắn hông và bóng mặt đất (146×12 ô)
const GAM_RONG = '.'.repeat(146)
export const LUOI_GAM_XE: readonly string[] = [
  '.kAk' + 't'.repeat(111) + '.'.repeat(31), // r0: dầm gầm trên + đèn hậu san hô
  '.kAk' +
    'T'.repeat(12) +
    'k'.repeat(12) +
    'TT' +
    'k'.repeat(12) +
    'T'.repeat(83) +
    'k'.repeat(10) +
    '.'.repeat(11), // r1: thân dầm gầm + hốc tối phía trên 3 bánh
  '.' + 'k'.repeat(134) + '.'.repeat(11), // r2: mép dưới khung gầm
  '.'.repeat(14) +
    'kTk' +
    '.'.repeat(10) +
    'kTk' +
    '.'.repeat(11) +
    'kTk' +
    '.'.repeat(10) +
    'krrrkrrrrrrkrrrrrk' +
    '.'.repeat(6) +
    'k' +
    't'.repeat(28) +
    'k' +
    '.'.repeat(38), // r3: chắn bùn + bình dầu sáng (có 2 đai) + thanh chắn hông trên
  '.'.repeat(14) +
    'kTk' +
    '.'.repeat(10) +
    'kTk' +
    '.'.repeat(11) +
    'kTk' +
    '.'.repeat(10) +
    'kRRRkRRRRRRkRRRRRk' +
    '.'.repeat(6) +
    'kTk' +
    '.'.repeat(10) +
    'kTk' +
    '.'.repeat(11) +
    'kTk' +
    '.'.repeat(38), // r4: bình dầu thân giữa + 3 trụ thanh chắn hông
  '.'.repeat(14) +
    'kkk' +
    '.'.repeat(10) +
    'kkk' +
    '.'.repeat(11) +
    'kkk' +
    '.'.repeat(10) +
    'ktttkttttttktttttk' +
    '.'.repeat(6) +
    'k' +
    'R'.repeat(28) +
    'k' +
    '.'.repeat(38), // r5: đáy chắn bùn + đáy bình dầu + thanh chắn hông dưới
  // r6: viền đáy bình dầu & thanh chắn hông
  '.'.repeat(55) + 'k'.repeat(16) + '.'.repeat(7) + 'k'.repeat(30) + '.'.repeat(38),
  GAM_RONG,
  GAM_RONG,
  GAM_RONG,
  GAM_RONG,
  '.'.repeat(12) + 'N'.repeat(128) + '.'.repeat(6), // r11: bóng mặt đất dưới 3 bánh xe
]

// 4. Bánh xe pixel (10×10 ô): lốp cao su dày, vành thép sáng/tối, nắp trục xanh thép
// Thước cột:       0123456789 (10 ô)
export const LUOI_BANH_XE: readonly string[] = [
  '...kkkk...',
  '..kTTTTk..',
  '.kTtkktTk.',
  'kTtkrrktTk',
  'kTkrddRkTk',
  'kTkRdSRkTk',
  'kTtkRRktTk',
  '.kTtkktTk.',
  '..kTTTTk..',
  '...kkkk...',
]

// 5. Sprite kiện hàng theo CỠ (thu gọn 6×6, nhỏ 8×8, vừa 12×9, lớn 16×9) và ĐẦY KHOANG cho 4 loại:
//    0: thùng carton có băng keo · 1: thùng gỗ đóng đai · 2: phuy thép · 3: bao có pallet.
//    Mỗi kiện giữ nguyên vẹn (không cắt), có 2 biến thể nhẹ để đổi giữa các tầng/cột cho đỡ nhàm.
const SO_LOAI_HANG = 4

// --- Loại 0: Thùng carton có băng keo & tem vận đơn ---
// Thu gọn 6×6 (khi khối hẹp hơn 8 ô)
const LUOI_CARTON_THU_GON: readonly string[] = [
  'kkkkkk',
  'kcPPck',
  'kbppbk',
  'kCppbk',
  'kClbbk',
  'kkkkkk',
]
// Nhỏ 8×8 (2 biến thể)
const LUOI_CARTON_NHO_A: readonly string[] = [
  'kkkkkkkk',
  'kccPPcbk',
  'kbbppbbk',
  'kCCppCbk',
  'kCCppCbk',
  'kCllCCbk',
  'kCllbbBk',
  'kkkkkkkk',
]
const LUOI_CARTON_NHO_B: readonly string[] = [
  'kkkkkkkk',
  'kcccPPbk',
  'kbbbppbk',
  'kCCCppbk',
  'kCllCCbk',
  'kCllCCbk',
  'kbbbbbBk',
  'kkkkkkkk',
]
// Vừa 12×9 (2 biến thể)
const LUOI_CARTON_VUA_A: readonly string[] = [
  'kkkkkkkkkkkk',
  'kccccPPcccbk',
  'kbbbbppbbbbk',
  'kCCCCppCCCbk',
  'kCCCCppCCCbk',
  'kClllCCCCCbk',
  'kClllCCCCCbk',
  'kbbbbbbbbbBk',
  'kkkkkkkkkkkk',
]
const LUOI_CARTON_VUA_B: readonly string[] = [
  'kkkkkkkkkkkk',
  'kcccPPccccbk',
  'kbbbppbbbbbk',
  'kCCCppCCCCbk',
  'kCCCppCCCCbk',
  'kCCCCClllCbk',
  'kCCCCClllCbk',
  'kbbbbbbbbbBk',
  'kkkkkkkkkkkk',
]
// Lớn 16×9 (2 biến thể)
const LUOI_CARTON_LON_A: readonly string[] = [
  'kkkkkkkkkkkkkkkk',
  'kccccccPPcccccbk',
  'kbbbbbbppbbbbbbk',
  'kCCCCCCppCCCCCbk',
  'kCCCCCCppCCCCCbk',
  'kCllllCCCCCCCCbk',
  'kCllllCCCCCCCCbk',
  'kbbbbbbbbbbbbbBk',
  'kkkkkkkkkkkkkkkk',
]
const LUOI_CARTON_LON_B: readonly string[] = [
  'kkkkkkkkkkkkkkkk',
  'kccccccccPPcccbk',
  'kbbbbbbbbppbbbbk',
  'kCCCCCCCCppCCCbk',
  'kCCCCCCCCppCCCbk',
  'kCCllllCCCCCCCbk',
  'kCCllllCCCCCCCbk',
  'kbbbbbbbbbbbbbBk',
  'kkkkkkkkkkkkkkkk',
]

// --- Loại 1: Thùng gỗ đóng đai sắt & đinh tán ---
// Thu gọn 6×6
const LUOI_GO_THU_GON: readonly string[] = [
  'kkkkkk',
  'krIirk',
  'kIwwgk',
  'kIWWgk',
  'krIirk',
  'kkkkkk',
]
// Nhỏ 8×8 (2 biến thể: thanh chéo \ và /)
const LUOI_GO_NHO_A: readonly string[] = [
  'kkkkkkkk',
  'kIrIirIk',
  'kIwwwwgk',
  'kIWwWWgk',
  'kIggwggk',
  'kIWWWwgk',
  'kIrIirIk',
  'kkkkkkkk',
]
const LUOI_GO_NHO_B: readonly string[] = [
  'kkkkkkkk',
  'kIrIirIk',
  'kIwwwwgk',
  'kIWWWwgk',
  'kIggwggk',
  'kIWwWWgk',
  'kIrIirIk',
  'kkkkkkkk',
]
// Vừa 12×9 (2 biến thể)
const LUOI_GO_VUA_A: readonly string[] = [
  'kkkkkkkkkkkk',
  'kIriIiiIirIk',
  'kIiwwwwwwiIk',
  'kIiWwWWWWgIk',
  'kIigggwgggIk',
  'kIiWWWWwWgIk',
  'kIiWWWWWwgIk',
  'kIriIiiIirIk',
  'kkkkkkkkkkkk',
]
const LUOI_GO_VUA_B: readonly string[] = [
  'kkkkkkkkkkkk',
  'kIriIiiIirIk',
  'kIiwwwwwwiIk',
  'kIiWWWWWwgIk',
  'kIigggwgggIk',
  'kIiWWwWWWgIk',
  'kIiWwWWWWgIk',
  'kIriIiiIirIk',
  'kkkkkkkkkkkk',
]
// Lớn 16×9 (2 biến thể)
const LUOI_GO_LON_A: readonly string[] = [
  'kkkkkkkkkkkkkkkk',
  'kIriIiiiiiiIirIk',
  'kIiwwwwwwwwwwiIk',
  'kIiWWwWWWWWWWgIk',
  'kIiggggwggggggIk',
  'kIiWWWWWWwWWWgIk',
  'kIiWWWWWWWWwWgIk',
  'kIriIiiiiiiIirIk',
  'kkkkkkkkkkkkkkkk',
]
const LUOI_GO_LON_B: readonly string[] = [
  'kkkkkkkkkkkkkkkk',
  'kIriIiiiiiiIirIk',
  'kIiwwwwwwwwwwiIk',
  'kIiWWWWWWWWwWgIk',
  'kIiggggggwggggIk',
  'kIiWWWWwWWWWWgIk',
  'kIiWWwWWWWWWWgIk',
  'kIriIiiiiiiIirIk',
  'kkkkkkkkkkkkkkkk',
]

// --- Loại 2: Phuy thép hình trụ, vành sáng, xen kẽ xanh lá & xanh dương ---
// Thu gọn 6×6
const LUOI_PHUY_THU_GON: readonly string[] = [
  '.kkkk.',
  'kRrrRk',
  'kEeevk',
  'krRRRk',
  'kEevvk',
  '.kkkk.',
]
// Nhỏ 8×8 (2 biến thể: xanh lá & xanh dương)
const LUOI_PHUY_NHO_A: readonly string[] = [
  '.kkkkkk.',
  'kRrrrRRk',
  'kEeeEEvk',
  'krrRRRRk',
  'kEeeEEvk',
  'krrRRRRk',
  'kvvvvvvk',
  '.kkkkkk.',
]
const LUOI_PHUY_NHO_B: readonly string[] = [
  '.kkkkkk.',
  'kRrrrRRk',
  'kSssSSdk',
  'krrRRRRk',
  'kSssSSdk',
  'krrRRRRk',
  'kddddddk',
  '.kkkkkk.',
]
// Vừa 12×9 (cặp 2 phuy đứng 6×9, đảo màu giữa 2 biến thể)
const LUOI_PHUY_VUA_A: readonly string[] = [
  '.kkkk..kkkk.',
  'kRrrRkkRrrRk',
  'kEeevkkSssdk',
  'krRRRkkrRRRk',
  'kEeevkkSssdk',
  'kEeevkkSssdk',
  'krRRRkkrRRRk',
  'kvvvvkkddddk',
  '.kkkk..kkkk.',
]
const LUOI_PHUY_VUA_B: readonly string[] = [
  '.kkkk..kkkk.',
  'kRrrRkkRrrRk',
  'kSssdkkEeevk',
  'krRRRkkrRRRk',
  'kSssdkkEeevk',
  'kSssdkkEeevk',
  'krRRRkkrRRRk',
  'kddddkkvvvvk',
  '.kkkk..kkkk.',
]
// Lớn 16×9 (cặp 2 phuy đứng 8×9, đảo màu giữa 2 biến thể)
const LUOI_PHUY_LON_A: readonly string[] = [
  '.kkkkkk..kkkkkk.',
  'kRrrrRRkkRrrrRRk',
  'kEeeEEvkkSssSSdk',
  'krrRRRRkkrrRRRRk',
  'kEeeEEvkkSssSSdk',
  'kEeeEEvkkSssSSdk',
  'krrRRRRkkrrRRRRk',
  'kvvvvvvkkddddddk',
  '.kkkkkk..kkkkkk.',
]
const LUOI_PHUY_LON_B: readonly string[] = [
  '.kkkkkk..kkkkkk.',
  'kRrrrRRkkRrrrRRk',
  'kSssSSdkkEeeEEvk',
  'krrRRRRkkrrRRRRk',
  'kSssSSdkkEeeEEvk',
  'kSssSSdkkEeeEEvk',
  'krrRRRRkkrrRRRRk',
  'kddddddkkvvvvvvk',
  '.kkkkkk..kkkkkk.',
]

// --- Loại 3: Bao tải màu kem có vạch chỉ đặt trên pallet gỗ ---
// Thu gọn 6×6
const LUOI_BAO_THU_GON: readonly string[] = [
  '.kkkk.',
  'kaaaak',
  'kAttnk',
  'kAnNNk',
  'kwwwwk',
  'kkGGkk',
]
// Nhỏ 8×8 (2 biến thể)
const LUOI_BAO_NHO_A: readonly string[] = [
  '.kkkkkk.',
  'kaAAAAak',
  'kAAttAnk',
  'kAnnnNNk',
  'kkkkkkkk',
  'kwwwwwwk',
  'kWkGGkWk',
  'kkkkkkkk',
]
const LUOI_BAO_NHO_B: readonly string[] = [
  '.kkkkkk.',
  'kaAAAAak',
  'kAttAAnk',
  'kAnnnNNk',
  'kkkkkkkk',
  'kwwwwwwk',
  'kWkGGkWk',
  'kkkkkkkk',
]
// Vừa 12×9 (2 bao trên pallet có 2 khe càng xe nâng, 2 biến thể)
const LUOI_BAO_VUA_A: readonly string[] = [
  '.kkkk..kkkk.',
  'kaaaakkaaaak',
  'kAttnkkAttnk',
  'kAAAnkkAAAnk',
  'kAnNNkkAnNNk',
  'kkkkkkkkkkkk',
  'kwwwwwwwwwwk',
  'kWkGGkkGGkWk',
  'kkkkkkkkkkkk',
]
const LUOI_BAO_VUA_B: readonly string[] = [
  '.kkkk..kkkk.',
  'kaaaakkaaaak',
  'kAAAnkkAAAnk',
  'kAttnkkAttnk',
  'kAnNNkkAnNNk',
  'kkkkkkkkkkkk',
  'kwwwwwwwwwwk',
  'kWkGGkkGGkWk',
  'kkkkkkkkkkkk',
]
// Lớn 16×9 (2 bao rộng trên pallet, 2 biến thể)
const LUOI_BAO_LON_A: readonly string[] = [
  '.kkkkkk..kkkkkk.',
  'kaaaaaakkaaaaaak',
  'kAAttAnkkAAttAnk',
  'kAAAAAnkkAAAAAnk',
  'kAnnnNNkkAnnnNNk',
  'kkkkkkkkkkkkkkkk',
  'kwwwwwwwwwwwwwwk',
  'kWWkGGkWWkGGkWWk',
  'kkkkkkkkkkkkkkkk',
]
const LUOI_BAO_LON_B: readonly string[] = [
  '.kkkkkk..kkkkkk.',
  'kaaaaaakkaaaaaak',
  'kAAAAAnkkAttAAnk',
  'kAttAAnkkAAAAAnk',
  'kAnnnNNkkAnnnNNk',
  'kkkkkkkkkkkkkkkk',
  'kwwwwwwwwwwwwwwk',
  'kWWkGGkWWkGGkWWk',
  'kkkkkkkkkkkkkkkk',
]

// Các sprite xe tải đã gộp đoạn ngang/dọc sẵn một lần lúc nạp mô-đun để nhẹ DOM khi render lại
export const SPRITE_CONTAINER = chuanBiSprite(LUOI_CONTAINER, MAU_XE)
export const SPRITE_DAU_XE = chuanBiSprite(LUOI_DAU_XE, MAU_XE)
export const SPRITE_GAM_XE = chuanBiSprite(LUOI_GAM_XE, MAU_XE)
export const SPRITE_BANH_XE = chuanBiSprite(LUOI_BANH_XE, MAU_XE)

type BoSpriteHang = {
  readonly thuGon: SpriteDaGop
  readonly nho: readonly [SpriteDaGop, SpriteDaGop]
  readonly vua: readonly [SpriteDaGop, SpriteDaGop]
  readonly lon: readonly [SpriteDaGop, SpriteDaGop]
}

const BO_SPRITE_HANG: readonly BoSpriteHang[] = [
  {
    thuGon: chuanBiSprite(LUOI_CARTON_THU_GON, MAU_HANG),
    nho: [chuanBiSprite(LUOI_CARTON_NHO_A, MAU_HANG), chuanBiSprite(LUOI_CARTON_NHO_B, MAU_HANG)],
    vua: [chuanBiSprite(LUOI_CARTON_VUA_A, MAU_HANG), chuanBiSprite(LUOI_CARTON_VUA_B, MAU_HANG)],
    lon: [chuanBiSprite(LUOI_CARTON_LON_A, MAU_HANG), chuanBiSprite(LUOI_CARTON_LON_B, MAU_HANG)],
  },
  {
    thuGon: chuanBiSprite(LUOI_GO_THU_GON, MAU_HANG),
    nho: [chuanBiSprite(LUOI_GO_NHO_A, MAU_HANG), chuanBiSprite(LUOI_GO_NHO_B, MAU_HANG)],
    vua: [chuanBiSprite(LUOI_GO_VUA_A, MAU_HANG), chuanBiSprite(LUOI_GO_VUA_B, MAU_HANG)],
    lon: [chuanBiSprite(LUOI_GO_LON_A, MAU_HANG), chuanBiSprite(LUOI_GO_LON_B, MAU_HANG)],
  },
  {
    thuGon: chuanBiSprite(LUOI_PHUY_THU_GON, MAU_HANG),
    nho: [chuanBiSprite(LUOI_PHUY_NHO_A, MAU_HANG), chuanBiSprite(LUOI_PHUY_NHO_B, MAU_HANG)],
    vua: [chuanBiSprite(LUOI_PHUY_VUA_A, MAU_HANG), chuanBiSprite(LUOI_PHUY_VUA_B, MAU_HANG)],
    lon: [chuanBiSprite(LUOI_PHUY_LON_A, MAU_HANG), chuanBiSprite(LUOI_PHUY_LON_B, MAU_HANG)],
  },
  {
    thuGon: chuanBiSprite(LUOI_BAO_THU_GON, MAU_HANG),
    nho: [chuanBiSprite(LUOI_BAO_NHO_A, MAU_HANG), chuanBiSprite(LUOI_BAO_NHO_B, MAU_HANG)],
    vua: [chuanBiSprite(LUOI_BAO_VUA_A, MAU_HANG), chuanBiSprite(LUOI_BAO_VUA_B, MAU_HANG)],
    lon: [chuanBiSprite(LUOI_BAO_LON_A, MAU_HANG), chuanBiSprite(LUOI_BAO_LON_B, MAU_HANG)],
  },
]

// --- Dựng sprite ĐẦY KHOANG liền mạch (kết thúc ở kiện nguyên, không cắt ở mép) ---
function chiaDoRong(
  tong: number,
  minR: number,
  maxR: number,
  lech: number,
  doiSoKien = false,
): number[] {
  if (tong < minR) return []
  const kMin = Math.ceil(tong / maxR)
  const kMax = Math.floor(tong / minR)
  if (kMin > kMax) {
    const k = Math.max(1, Math.floor(tong / minR))
    return Array.from({ length: k }, () => minR)
  }
  const tb = (minR + maxR) / 2
  let kChon = Math.max(kMin, Math.min(kMax, Math.round(tong / tb)))
  if (doiSoKien && kMin < kMax) {
    kChon = kChon + 1 <= kMax ? kChon + 1 : kChon - 1
  }
  const coBan = Math.floor(tong / kChon)
  const du = tong - coBan * kChon
  const kq: number[] = []
  for (let i = 0; i < kChon; i++) {
    const idx = (i + lech) % kChon
    kq.push(idx < du ? coBan + 1 : coBan)
  }
  return kq
}

function ghepHangNgang(dsLuoi: readonly (readonly string[])[]): string[] {
  if (dsLuoi.length === 0) return []
  const cao = dsLuoi[0].length
  return Array.from({ length: cao }, (_, r) => dsLuoi.map((luoi) => luoi[r] ?? '').join(''))
}

function demCanGiua(dong: readonly string[], rongDich: number): string[] {
  return dong.map((hang) => {
    const du = rongDich - hang.length
    if (du <= 0) return hang
    const trai = Math.floor(du / 2)
    return '.'.repeat(trai) + hang + '.'.repeat(du - trai)
  })
}

// Kiện carton cao 9 ô, rộng linh hoạt 10..16 ô cho tường carton đầy khoang
function veKienCarton(rong: number, bienThe: number): string[] {
  const trong = rong - 2
  const keoLech = bienThe % 3 === 1 ? 1 : bienThe % 3 === 2 ? -1 : 0
  const keo = Math.max(1, Math.min(trong - 4, Math.floor((trong - 2) / 2) + keoLech))
  const phaiKeo = trong - keo - 3
  const rongTem = rong >= 14 ? 4 : rong >= 10 ? 3 : 2
  const tem = bienThe % 2 === 0 ? 1 : Math.max(1, trong - rongTem - 2)
  const phaiTem = trong - tem - rongTem - 1
  return [
    'k'.repeat(rong),
    'k' + 'c'.repeat(keo) + 'PP' + 'c'.repeat(phaiKeo) + 'bk',
    'k' + 'b'.repeat(keo) + 'pp' + 'b'.repeat(phaiKeo + 1) + 'k',
    'k' + 'C'.repeat(keo) + 'pp' + 'C'.repeat(phaiKeo) + 'bk',
    'k' + 'C'.repeat(keo) + 'pp' + 'C'.repeat(phaiKeo) + 'bk',
    'k' + 'C'.repeat(tem) + 'l'.repeat(rongTem) + 'C'.repeat(phaiTem) + 'bk',
    'k' + 'C'.repeat(tem) + 'l'.repeat(rongTem) + 'C'.repeat(phaiTem) + 'bk',
    'k' + 'b'.repeat(trong - 1) + 'Bk',
    'k'.repeat(rong),
  ]
}

// Thùng gỗ cao 9 ô, rộng linh hoạt 12..18 ô cho tường thùng gỗ đầy khoang
function veThungGo(rong: number, bienThe: number): string[] {
  const go = rong - 6
  const nguoc = bienThe % 2 === 1
  const thanhCheo = (t: number, nen: string): string => {
    const buoc = Math.round(((t + 0.5) * (go - 1)) / 4)
    const viTri = nguoc
      ? Math.max(0, Math.min(go - 1, go - 1 - buoc))
      : Math.max(0, Math.min(go - 1, buoc))
    return 'kIi' + nen.repeat(viTri) + 'w' + nen.repeat(go - 1 - viTri) + 'gIk'
  }
  return [
    'k'.repeat(rong),
    'kIriI' + 'i'.repeat(rong - 10) + 'IirIk',
    'kIi' + 'w'.repeat(go) + 'iIk',
    thanhCheo(0, 'W'),
    thanhCheo(1, 'g'),
    thanhCheo(2, 'W'),
    thanhCheo(3, 'W'),
    'kIriI' + 'i'.repeat(rong - 10) + 'IirIk',
    'k'.repeat(rong),
  ]
}

// Phuy thép đứng cao 13 ô, rộng 7..9 ô cho hàng phuy đầy khoang
function vePhuyCao(rong: number, xanhDuong: boolean): string[] {
  const trong = rong - 2
  const s = xanhDuong ? 's' : 'e'
  const m = xanhDuong ? 'S' : 'E'
  const d = xanhDuong ? 'd' : 'v'
  const than = 'k' + m + s + s + m.repeat(trong - 4) + d + 'k'
  const dai = 'krr' + 'R'.repeat(trong - 2) + 'k'
  const vien = '.' + 'k'.repeat(trong) + '.'
  return [
    vien,
    'kR' + 'r'.repeat(trong - 3) + 'RRk',
    than,
    than,
    dai,
    than,
    than,
    than,
    dai,
    than,
    than,
    'k' + d.repeat(trong) + 'k',
    vien,
  ]
}

// Bao tải cao 7 ô, rộng 8..10 ô cho chồng bao trên pallet đầy khoang
function veBaoCao(rong: number, bienThe: number): string[] {
  const trong = rong - 2
  const traiA = Math.floor((trong - 3) / 2)
  const phaiA = trong - 3 - traiA
  const vien = '.' + 'k'.repeat(trong) + '.'
  const dongSoc = 'k' + 'A'.repeat(traiA) + 'tt' + 'A'.repeat(phaiA) + 'nk'
  const dongThan = 'k' + 'A'.repeat(trong - 1) + 'nk'
  const socDuoi = bienThe % 2 === 1
  return [
    vien,
    'k' + 'a'.repeat(trong) + 'k',
    socDuoi ? dongThan : dongSoc,
    socDuoi ? dongSoc : dongThan,
    dongThan,
    'kA' + 'n'.repeat(trong - 3) + 'NNk',
    vien,
  ]
}

// Đế pallet gỗ liên tục cao 5 ô có khe càng xe nâng đều nhau
function vePalletDay(rong: number): string[] {
  const trong = rong - 2
  const nan = 'WWg'.repeat(Math.ceil(trong / 3)).slice(0, trong)
  const nhip = Math.max(2, Math.floor(trong / 8))
  let khe = ''
  for (let i = 0; i < trong; i++) {
    const pos = Math.floor((i * nhip) / trong)
    const batDau = Math.floor((pos * trong) / nhip)
    const ketThuc = Math.floor(((pos + 1) * trong) / nhip)
    const trongNhip = i - batDau
    const giua = Math.floor((ketThuc - batDau) / 2)
    if (trongNhip === giua - 1 || trongNhip === giua) khe += 'G'
    else if (trongNhip === giua - 2 || trongNhip === giua + 1) khe += 'k'
    else khe += 'W'
  }
  return [
    'k'.repeat(rong),
    'k' + 'w'.repeat(trong) + 'k',
    'k' + nan + 'k',
    'k' + khe + 'k',
    'k'.repeat(rong),
  ]
}

function taoLuoiDayKhoang(loai: number, rongSuDung: number, caoToiDa: number): string[] {
  // Loại 0: Tường carton 3 tầng so le (27 ô cao)
  if (loai === 0) {
    const soTang = caoToiDa >= 27 ? 3 : caoToiDa >= 18 ? 2 : 1
    const luoi: string[] = []
    for (let tang = soTang - 1; tang >= 0; tang--) {
      const dsR = chiaDoRong(rongSuDung, 10, 12, tang * 3, tang === 1)
      const hang = ghepHangNgang(dsR.map((r, i) => veKienCarton(r, tang + i)))
      luoi.push(...hang)
    }
    const rongThuc = luoi.reduce((m, s) => Math.max(m, s.length), 0)
    return demCanGiua(luoi, rongThuc)
  }

  // Loại 1: Tường thùng gỗ đóng đai 3 tầng so le (27 ô cao)
  if (loai === 1) {
    const soTang = caoToiDa >= 27 ? 3 : caoToiDa >= 18 ? 2 : 1
    const luoi: string[] = []
    for (let tang = soTang - 1; tang >= 0; tang--) {
      const dsR = chiaDoRong(rongSuDung, 14, 18, tang === 1 ? 3 : tang, tang === 1)
      const hang = ghepHangNgang(dsR.map((r, i) => veThungGo(r, tang + i)))
      luoi.push(...hang)
    }
    const rongThuc = luoi.reduce((m, s) => Math.max(m, s.length), 0)
    return demCanGiua(luoi, rongThuc)
  }

  // Loại 2: Hàng phuy thép đứng 2 tầng ngăn ván gỗ (27 ô cao, mỗi phuy nguyên cùng kích cỡ)
  if (loai === 2) {
    let rChon = 9
    let duNhoNhat = rongSuDung % 9
    for (const r of [8, 7]) {
      const du = rongSuDung % r
      if (du < duNhoNhat) {
        duNhoNhat = du
        rChon = r
      }
    }
    const soPhuy = Math.max(1, Math.floor(rongSuDung / rChon))
    const rongThuc = soPhuy * rChon
    const tangDuoi = ghepHangNgang(
      Array.from({ length: soPhuy }, (_, i) => vePhuyCao(rChon, i % 2 === 1)),
    )
    if (caoToiDa < 26) return tangDuoi
    const tangTren = ghepHangNgang(
      Array.from({ length: soPhuy }, (_, i) => vePhuyCao(rChon, i % 2 === 0)),
    )
    if (caoToiDa >= 27) {
      const tamNgan = 'k' + 'w'.repeat(rongThuc - 2) + 'k'
      return [...tangTren, tamNgan, ...tangDuoi]
    }
    return [...tangTren, ...tangDuoi]
  }

  // Loại 3: Chồng bao tải 3 tầng so le thu nhẹ lên nóc trên đế pallet liên tục (26 ô cao)
  const soTangBao = caoToiDa >= 26 ? 3 : caoToiDa >= 19 ? 2 : 1
  const pallet = vePalletDay(rongSuDung)
  const luoi: string[] = []
  for (let tang = soTangBao - 1; tang >= 0; tang--) {
    const thuVao = tang * 2
    const rongTang = Math.max(16, rongSuDung - thuVao * 2)
    const dsR = chiaDoRong(rongTang, 8, 10, tang * 2 + 1, tang === 1)
    const hang = ghepHangNgang(dsR.map((r, i) => veBaoCao(r, tang + i)))
    luoi.push(...demCanGiua(hang, rongSuDung))
  }
  luoi.push(...pallet)
  return luoi
}

const boDemDayKhoang = new Map<string, SpriteDaGop>()

function laySpriteDayKhoang(loai: number, rongOKhoi: number, caoOKhoang: number): SpriteDaGop {
  // Chừa mép 1 ô sát hai vách khoang nếu khối đủ rộng
  const rongSuDung = rongOKhoi >= 20 ? rongOKhoi - 2 : rongOKhoi
  const caoSuDung = Math.min(27, caoOKhoang)
  const khoa = `${loai}:${rongSuDung}:${caoSuDung}`
  const coSan = boDemDayKhoang.get(khoa)
  if (coSan) return coSan
  const sprite = chuanBiSprite(taoLuoiDayKhoang(loai, rongSuDung, caoSuDung), MAU_HANG)
  boDemDayKhoang.set(khoa, sprite)
  return sprite
}

// Xếp một hàng các kiện nguyên nằm ngang trong bề rộng W ô (không cắt, chia khe đều, lệch tầng nhẹ)
function xepMotHangNgang(
  dsSprite: readonly SpriteDaGop[],
  W: number,
  y: number,
  kheToiDa: number,
  lech = 0,
): KienDaXep[] {
  const tongRong = dsSprite.reduce((t, s) => t + s.rong, 0)
  if (tongRong > W || dsSprite.length === 0) return []
  const du = W - tongRong
  const khe = dsSprite.length > 1 ? Math.min(kheToiDa, Math.floor(du / (dsSprite.length + 1))) : 0
  const span = tongRong + khe * (dsSprite.length - 1)
  const leTraiCoBan = Math.floor((W - span) / 2)
  const leTrai = Math.max(0, Math.min(W - span, leTraiCoBan + lech))
  const kq: KienDaXep[] = []
  let curX = leTrai
  for (const sprite of dsSprite) {
    kq.push({ sprite, x: curX, y })
    curX += sprite.rong + khe
  }
  return kq
}

// Hàm thuần tính danh sách kiện hàng cần vẽ theo tỉ lệ khoang f và bề rộng khối (đơn vị: ô).
// Gốc toạ độ (0, 0) ở góc trái-dưới khối; y tăng hướng lên trên; KHÔNG bao giờ cắt kiện.
export function xepHangTheoCo(
  loai: number,
  rongOKhoi: number,
  caoOKhoang: number,
  f: number,
): KienDaXep[] {
  if (!Number.isFinite(f) || !Number.isFinite(rongOKhoi) || !Number.isFinite(caoOKhoang)) {
    return []
  }
  const W = Math.floor(rongOKhoi)
  const H = Math.floor(caoOKhoang)
  if (f <= 0 || W <= 0 || H <= 0) return []

  const loaiHopLe = Number.isFinite(loai)
    ? ((Math.trunc(loai) % SO_LOAI_HANG) + SO_LOAI_HANG) % SO_LOAI_HANG
    : 0
  const bo = BO_SPRITE_HANG[loaiHopLe]
  const tiLe = Math.max(0, Math.min(1, f))

  // Khối quá hẹp (< 8 ô): dùng đúng 1 kiện thu gọn 6×6 nguyên vẹn
  if (W < bo.nho[0].rong) {
    if (H < bo.thuGon.cao) return []
    const x = Math.max(0, Math.floor((W - bo.thuGon.rong) / 2))
    return [{ sprite: bo.thuGon, x, y: 0 }]
  }

  // Cỡ ĐẦY (f ≥ NGUONG_LON): một sprite liền mạch phủ kín khoang tới nóc, kết thúc ở kiện nguyên
  if (tiLe >= NGUONG_LON && W >= 18 && H >= 26) {
    const spriteDay = laySpriteDayKhoang(loaiHopLe, W, H)
    const x = Math.max(0, Math.floor((W - spriteDay.rong) / 2))
    return [{ sprite: spriteDay, x, y: 0 }]
  }

  // Cỡ NHỎ (f < NGUONG_NHO): 1 kiện nhỏ 8×8 hoặc 2 kiện nhỏ xếp dọc, đặt giữa khối
  if (tiLe < NGUONG_NHO) {
    const soTang = tiLe >= NGUONG_NHO * 0.58 && H >= bo.nho[0].cao * 2 ? 2 : 1
    const kq: KienDaXep[] = []
    for (let tang = 0; tang < soTang; tang++) {
      const sprite = bo.nho[(loaiHopLe + tang) % 2]
      const x = Math.max(0, Math.floor((W - sprite.rong) / 2))
      kq.push({ sprite, x, y: tang * sprite.cao })
    }
    return kq
  }

  // Cỡ VỪA (NGUONG_NHO ≤ f < NGUONG_VUA): chồng 2 tầng, mỗi tầng 1–2 kiện cỡ trung 12×9
  if (tiLe < NGUONG_VUA || W < bo.lon[0].rong) {
    // Khối nằm sát mép dưới cỡ VỪA (10–11 ô < 12 ô): hạ xuống 2 tầng kiện nhỏ 8×8 để không cắt kiện
    if (W < bo.vua[0].rong) {
      const soTang = H >= bo.nho[0].cao * 2 ? 2 : 1
      const kq: KienDaXep[] = []
      for (let tang = 0; tang < soTang; tang++) {
        const sprite = bo.nho[(loaiHopLe + tang) % 2]
        const x = Math.max(0, Math.floor((W - sprite.rong) / 2))
        kq.push({ sprite, x, y: tang * sprite.cao })
      }
      return kq
    }

    const soTang = H >= bo.vua[0].cao * 2 ? 2 : 1
    const nVua = Math.max(1, Math.floor(W / bo.vua[0].rong))
    // Khi rộng 20..23 ô (nVua = 1, dư ≥ 8 ô): ghép thêm 1 cột kiện nhỏ 8×8 bên cạnh cho đầy khối
    if (nVua === 1 && W >= bo.vua[0].rong + bo.nho[0].rong) {
      const tong = bo.vua[0].rong + bo.nho[0].rong
      const khe = W - tong >= 2 ? 1 : 0
      const leTrai = Math.floor((W - tong - khe) / 2)
      const kq: KienDaXep[] = []
      for (let tang = 0; tang < soTang; tang++) {
        const sv = bo.vua[(loaiHopLe + tang) % 2]
        const sn = bo.nho[(loaiHopLe + tang + 1) % 2]
        kq.push({ sprite: sv, x: leTrai, y: tang * sv.cao })
        kq.push({ sprite: sn, x: leTrai + sv.rong + khe, y: tang * sn.cao })
      }
      return kq
    }

    const kq: KienDaXep[] = []
    for (let tang = 0; tang < soTang; tang++) {
      const hang = Array.from({ length: nVua }, (_, i) => bo.vua[(loaiHopLe + tang + i) % 2])
      kq.push(...xepMotHangNgang(hang, W, tang * bo.vua[0].cao, 1, 0))
    }
    return kq
  }

  // Cỡ LỚN (NGUONG_VUA ≤ f < NGUONG_LON): chồng 3 tầng so le, cao 27 ô (3 × 9)
  const caoTang = bo.lon[0].cao
  const soTang = H >= caoTang * 3 ? 3 : H >= caoTang * 2 ? 2 : 1

  // Bề rộng 24..31 ô: 2 kiện vừa (12×9) ở 2 tầng dưới + 1 kiện lớn (16×9) gối giữa ở tầng trên
  if (W < bo.lon[0].rong * 2) {
    if (W >= bo.vua[0].rong * 2) {
      const kq: KienDaXep[] = []
      kq.push(...xepMotHangNgang([bo.vua[0], bo.vua[1]], W, 0, 1, 0))
      if (soTang >= 2) {
        kq.push(...xepMotHangNgang([bo.vua[1], bo.vua[0]], W, caoTang, 1, 1))
      }
      if (soTang >= 3) {
        kq.push(...xepMotHangNgang([bo.lon[loaiHopLe % 2]], W, caoTang * 2, 0, 0))
      }
      return kq
    }
    // Bề rộng 16..23 ô (chỉ gọi trực tiếp mới gặp): 1 kiện lớn mỗi tầng, tầng giữa lệch 1 ô
    const kq: KienDaXep[] = []
    for (let tang = 0; tang < soTang; tang++) {
      const sprite = bo.lon[(loaiHopLe + tang) % 2]
      kq.push(...xepMotHangNgang([sprite], W, tang * caoTang, 0, tang === 1 ? 1 : 0))
    }
    return kq
  }

  const nLon = Math.floor(W / bo.lon[0].rong)
  const du = W - nLon * bo.lon[0].rong
  const kq: KienDaXep[] = []

  // Nếu phần dư đủ ghép thêm 1 kiện vừa (12×9 cùng chiều cao): đảo đầu tầng 2 để so le tự nhiên
  if (du >= bo.vua[0].rong) {
    const tang0 = [
      ...Array.from({ length: nLon }, (_, i) => bo.lon[(loaiHopLe + i) % 2]),
      bo.vua[loaiHopLe % 2],
    ]
    const tang1 = [
      bo.vua[(loaiHopLe + 1) % 2],
      ...Array.from({ length: nLon }, (_, i) => bo.lon[(loaiHopLe + i + 1) % 2]),
    ]
    const tang2 = Array.from({ length: nLon }, (_, i) => bo.lon[(loaiHopLe + i) % 2])
    kq.push(...xepMotHangNgang(tang0, W, 0, 1, 0))
    if (soTang >= 2) kq.push(...xepMotHangNgang(tang1, W, caoTang, 1, 0))
    if (soTang >= 3) kq.push(...xepMotHangNgang(tang2, W, caoTang * 2, 0, 0))
    return kq
  }

  // Hàng chuẩn nLon kiện lớn: tầng 2 lệch 1 ô, tầng 3 lùi gọn vào trong (hoặc giảm 1 kiện gối giữa)
  const hang0 = Array.from({ length: nLon }, (_, i) => bo.lon[(loaiHopLe + i) % 2])
  const hang1 = Array.from({ length: nLon }, (_, i) => bo.lon[(loaiHopLe + i + 1) % 2])
  kq.push(...xepMotHangNgang(hang0, W, 0, 2, 0))
  if (soTang >= 2) {
    kq.push(...xepMotHangNgang(hang1, W, caoTang, 2, du >= 2 ? 1 : 0))
  }
  if (soTang >= 3) {
    const soKienTren = du >= 4 || nLon <= 1 ? nLon : nLon - 1
    const hang2 = Array.from({ length: soKienTren }, (_, i) => bo.lon[(loaiHopLe + i) % 2])
    kq.push(...xepMotHangNgang(hang2, W, caoTang * 2, 0, 0))
  }
  return kq
}
