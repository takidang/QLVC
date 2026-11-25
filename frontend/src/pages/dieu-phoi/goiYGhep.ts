// Gợi ý ghép: đơn nào còn vừa phần thể tích / tải trọng xe chưa dùng (đơn vừa xếp lên đầu).
// Chỉ để gợi ý; máy chủ vẫn là nơi chặn thật (BR-01, BR-02).
export type DonCoKhoiLuong = { m3: string | number; kg: string | number }

export type GoiY<T extends DonCoKhoiLuong> = {
  d: T
  quaM3: boolean
  quaKg: boolean
  vua: boolean
}

// Dung sai 1e-9 để số thực (vd. 0,1 + 0,2) không làm đơn vừa khít bị tính là quá
const DUNG_SAI = 1e-9

export function goiYGhep<T extends DonCoKhoiLuong>(
  dsDon: readonly T[],
  conM3: number,
  conKg: number,
): GoiY<T>[] {
  return dsDon
    .map((d) => {
      const quaM3 = Number(d.m3) > conM3 + DUNG_SAI
      const quaKg = Number(d.kg) > conKg + DUNG_SAI
      return { d, quaM3, quaKg, vua: !quaM3 && !quaKg }
    })
    .sort((a, b) => Number(b.vua) - Number(a.vua)) // sort ổn định: đơn vừa lên đầu, giữ thứ tự cũ
}
