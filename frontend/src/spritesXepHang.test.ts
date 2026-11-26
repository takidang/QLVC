import { describe, expect, it } from 'vitest'
import { coKhoi, NGUONG_LON, NGUONG_NHO, NGUONG_VUA, xepHangTheoCo } from './spritesXepHang'

const CAO_KHOANG = 28 // lòng thùng Pixel cao 28 ô
const RONG_KHOANG = 93
const MUC_F = [0.01, 0.05, NGUONG_NHO, 0.2, NGUONG_VUA, 0.5, NGUONG_LON - 0.01, NGUONG_LON, 0.95, 1]

describe('xepHangTheoCo: kiện luôn nguyên, không cắt', () => {
  it('mọi loại hàng, bề rộng khối từ 6 ô trở lên, mọi cỡ: kiện nằm trọn trong khối', () => {
    const loi: string[] = []
    for (let loai = 0; loai < 4; loai++)
      for (let w = 6; w <= RONG_KHOANG; w++)
        for (const f of MUC_F) {
          const kien = xepHangTheoCo(loai, w, CAO_KHOANG, f)
          if (kien.length === 0) loi.push(`loai ${loai} w ${w} f ${f}: không có kiện nào`)
          for (const k of kien) {
            const ra =
              k.x < 0 || k.y < 0 || k.x + k.sprite.rong > w || k.y + k.sprite.cao > CAO_KHOANG
            if (ra) loi.push(`loai ${loai} w ${w} f ${f}: kiện ra ngoài (x=${k.x}, y=${k.y})`)
          }
        }
    expect(loi).toEqual([])
  })

  it('đơn chiếm từ 70% khoang trở lên: vẽ một sprite liền mạch phủ tới nóc', () => {
    const kien = xepHangTheoCo(1, RONG_KHOANG, CAO_KHOANG, 0.9)
    expect(kien).toHaveLength(1)
    expect(kien[0].sprite.cao).toBeGreaterThanOrEqual(26)
  })

  it('đầu vào hỏng (rỗng, âm, NaN, vô cực) thì không vẽ gì và không ném lỗi', () => {
    expect(xepHangTheoCo(0, 0, CAO_KHOANG, 0.5)).toEqual([])
    expect(xepHangTheoCo(0, 40, CAO_KHOANG, 0)).toEqual([])
    expect(xepHangTheoCo(0, -5, CAO_KHOANG, 0.5)).toEqual([])
    expect(xepHangTheoCo(0, 40, CAO_KHOANG, Number.NaN)).toEqual([])
    expect(xepHangTheoCo(0, Number.POSITIVE_INFINITY, CAO_KHOANG, 0.5)).toEqual([])
  })

  it('id đơn âm hoặc lẻ vẫn chọn được loại hàng hợp lệ', () => {
    expect(xepHangTheoCo(-3, 40, CAO_KHOANG, 0.3).length).toBeGreaterThan(0)
    expect(xepHangTheoCo(2.7, 40, CAO_KHOANG, 0.3).length).toBeGreaterThan(0)
  })
})

describe('coKhoi: cỡ khối theo thể tích', () => {
  const W = 558
  const H = 168
  const MIN = 60
  const tong = (ds: { w: number }[]) => ds.reduce((t, k) => t + k.w, 0)

  it('đơn nhỏ thành hộp thấp trên sàn, đủ lớn để thấy; đơn lớn cao tới nóc', () => {
    const [nho, lon] = coKhoi([0.2 / 14, 7 / 14], W, H, MIN)
    expect(nho).toEqual({ w: MIN, h: MIN })
    expect(lon.h).toBe(H)
    expect(lon.w).toBeCloseTo(W / 2)
  })

  it('còn chỗ thì diện tích khối đúng tỉ lệ thể tích', () => {
    const [a, b] = coKhoi([0.1, 0.2], W, H, MIN)
    expect((b.w * b.h) / (a.w * a.h)).toBeCloseTo(2)
  })

  it('thùng đầy: tổng bề rộng không vượt thùng, đơn nhỏ vẫn giữ bề rộng tối thiểu', () => {
    const ds = coKhoi([0.97, 0.01, 0.01, 0.01], W, H, MIN)
    expect(tong(ds)).toBeLessThanOrEqual(W + 1e-6)
    expect(ds[1].w).toBeCloseTo(MIN)
  })

  it('quá nhiều đơn nhỏ vẫn nằm trong thùng; thể tích 0 không vẽ', () => {
    expect(tong(coKhoi(Array(30).fill(0.01), W, H, MIN))).toBeCloseTo(W)
    expect(coKhoi([0], W, H, MIN)).toEqual([{ w: 0, h: 0 }])
  })
})
