// Gọi API cùng origin (cookie httpOnly đi kèm); lỗi theo dạng chung {ma, thong_diep, chi_tiet} (kien-truc.md mục 7)
type ChiTietLoi = { loc?: (string | number)[]; msg?: string; type?: string }

export class LoiApi extends Error {
  status: number
  ma: string
  chiTiet: ChiTietLoi[]
  constructor(status: number, ma: string, thongDiep: string, chiTiet: ChiTietLoi[] = []) {
    super(thongDiep)
    this.status = status
    this.ma = ma
    this.chiTiet = chiTiet
  }
}

export async function goi<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { credentials: 'same-origin', ...init })
  if (r.status === 204) return undefined as T
  const body = await r.json().catch(() => ({}))
  if (!r.ok)
    throw new LoiApi(
      r.status,
      body.ma ?? 'LOI',
      body.thong_diep ?? 'Có lỗi, vui lòng thử lại',
      body.chi_tiet ?? [],
    )
  return body as T
}

export const guiJson = <T>(url: string, method: string, du_lieu: unknown) =>
  goi<T>(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(du_lieu),
  })

// Lỗi 400 của máy chủ là tiếng Anh (Pydantic): đổi sang câu tiếng Việt theo loại lỗi, gắn vào từng trường
const LOI_THEO_LOAI: Record<string, string> = {
  missing: 'Bắt buộc nhập',
  greater_than: 'Giá trị quá nhỏ',
  greater_than_equal: 'Giá trị quá nhỏ',
  less_than_equal: 'Giá trị quá lớn',
  int_parsing: 'Phải là số nguyên',
  decimal_parsing: 'Phải là số',
  decimal_max_places: 'Quá nhiều chữ số thập phân',
  date_from_datetime_parsing: 'Ngày không hợp lệ',
  date_parsing: 'Ngày không hợp lệ',
  string_too_long: 'Quá dài',
  string_too_short: 'Bắt buộc nhập',
}

export function loiTheoTruong(err: unknown): Record<string, string> {
  if (!(err instanceof LoiApi) || err.status !== 400) return {}
  const ket_qua: Record<string, string> = {}
  for (const e of err.chiTiet) {
    const truong = String(e.loc?.at(-1) ?? '')
    // Lỗi do nhóm tự viết (ValueError) đã là tiếng Việt, chỉ bỏ tiền tố "Value error, "
    ket_qua[truong] =
      e.type === 'value_error'
        ? (e.msg ?? '').replace(/^Value error, /, '')
        : (LOI_THEO_LOAI[e.type ?? ''] ?? 'Giá trị không hợp lệ')
  }
  return ket_qua
}
