import { describe, expect, it } from 'vitest'
import { goiYGhep } from './goiYGhep'

const don = (ma: string, m3: string, kg: string) => ({ ma, m3, kg })

describe('goiYGhep', () => {
  it('đơn nhỏ hơn phần còn trống là "vừa", đơn vừa khít cũng "vừa"', () => {
    const r = goiYGhep([don('A', '2', '100'), don('B', '3', '400')], 3, 400)
    expect(r.map((g) => g.vua)).toEqual([true, true])
  })

  it('quá thể tích hoặc quá tải trọng thì báo đúng phía bị vượt', () => {
    const [m3, kg, ca2] = goiYGhep(
      [don('quaM3', '3.5', '100'), don('quaKg', '1', '401'), don('quaCa2', '9', '999')],
      3,
      400,
    )
    expect([m3.quaM3, m3.quaKg, m3.vua]).toEqual([true, false, false])
    expect([kg.quaM3, kg.quaKg, kg.vua]).toEqual([false, true, false])
    expect([ca2.quaM3, ca2.quaKg]).toEqual([true, true])
  })

  it('đơn vừa xếp lên đầu và giữ thứ tự cũ trong từng nhóm', () => {
    const r = goiYGhep(
      [don('q1', '9', '1'), don('v1', '1', '1'), don('q2', '8', '1'), don('v2', '1', '2')],
      2,
      10,
    )
    expect(r.map((g) => g.d.ma)).toEqual(['v1', 'v2', 'q1', 'q2'])
  })

  it('số thực không làm đơn vừa khít bị tính là quá (0,1 + 0,2 = 0,30000000000000004)', () => {
    const r = goiYGhep([don('A', '0.3', '1')], 0.1 + 0.2, 1)
    expect(r[0].vua).toBe(true)
  })

  it('xe đã đầy (còn trống 0) thì mọi đơn có khối lượng đều là "quá"', () => {
    const r = goiYGhep([don('A', '0.1', '1')], 0, 0)
    expect(r[0].vua).toBe(false)
  })

  it('không có đơn nào thì ra danh sách rỗng', () => {
    expect(goiYGhep([], 5, 500)).toEqual([])
  })
})
