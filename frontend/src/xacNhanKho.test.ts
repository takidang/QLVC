import { afterEach, describe, expect, it } from 'vitest'
import { hoiXacNhan, huyXacNhan, theoDoi, traLoi, yeuCauDang } from './xacNhanKho'

const chu = {}
afterEach(() => huyXacNhan())

describe('hộp xác nhận: chỉ bấm đồng ý mới là true', () => {
  it('trả đúng câu trả lời, đóng hộp và báo cho giao diện', async () => {
    let soLanBao = 0
    const thoi = theoDoi(() => soLanBao++)
    for (const dongY of [true, false]) {
      const kq = hoiXacNhan(chu, 'Xóa?', 'Xóa')
      expect(yeuCauDang()).toMatchObject({ cau: 'Xóa?', nut: 'Xóa' })
      traLoi(yeuCauDang()!.ma, dongY)
      expect(await kq).toBe(dongY)
      expect(yeuCauDang()).toBeNull()
    }
    expect(soLanBao).toBe(4)
    thoi()
  })

  it('hỏi lần hai khi hộp đang mở: false ngay, câu đầu giữ nguyên', async () => {
    const dau = hoiXacNhan(chu, 'Câu 1')
    expect(await hoiXacNhan(chu, 'Câu 2')).toBe(false)
    expect(yeuCauDang()?.cau).toBe('Câu 1')
    traLoi(yeuCauDang()!.ma, true)
    expect(await dau).toBe(true)
  })

  it('hủy (đổi trang, nơi hỏi bị tháo) là false; nơi khác bị tháo không đụng câu đang mở', async () => {
    const kq = hoiXacNhan(chu, 'Quyết toán?')
    huyXacNhan({})
    expect(yeuCauDang()).not.toBeNull()
    huyXacNhan(chu)
    expect(await kq).toBe(false)
  })

  it('câu trả lời cho hộp đã đóng không rơi sang hộp mới', async () => {
    void hoiXacNhan(chu, 'Cũ')
    const maCu = yeuCauDang()!.ma
    huyXacNhan()
    const moi = hoiXacNhan(chu, 'Mới')
    traLoi(maCu, true)
    expect(yeuCauDang()?.cau).toBe('Mới')
    huyXacNhan()
    expect(await moi).toBe(false)
  })
})
