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

// App lắng nghe sự kiện này để về /dang-nhap khi API trả 401 giữa phiên
export const SU_KIEN_HET_PHIEN = 'qlvc-het-phien'

const MAT_KET_NOI = 'Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại.'

export async function goi<T>(url: string, init?: RequestInit): Promise<T> {
  let r: Response
  try {
    r = await fetch(url, { credentials: 'same-origin', ...init })
  } catch {
    throw new LoiApi(0, 'MAT_KET_NOI', MAT_KET_NOI) // mất mạng, máy chủ không trả lời
  }
  if (r.status === 204) return undefined as T
  const body = await r.json().catch(() => ({}))
  // Phiên hết hạn giữa chừng (cookie 8 giờ, NFR-SEC-01): báo cho App đưa về trang đăng nhập.
  // /api/auth/toi (kiểm phiên lúc mở trang) và đăng nhập sai (mã khác) không tính.
  if (r.status === 401 && body.ma === 'CHUA_DANG_NHAP' && !url.endsWith('/api/auth/toi'))
    window.dispatchEvent(new Event(SU_KIEN_HET_PHIEN))
  if (!r.ok)
    throw new LoiApi(
      r.status,
      body.ma ?? 'LOI',
      body.thong_diep
        ? kemMaBr(body.thong_diep, body.ma)
        : [502, 503, 504].includes(r.status)
          ? MAT_KET_NOI // proxy/cổng báo backend tắt hoặc quá tải
          : // Lỗi không theo mẫu khác (404 đường dẫn sai…): kèm mã HTTP để dễ dò
            `Có lỗi (mã ${r.status}), vui lòng thử lại`,
      body.chi_tiet ?? [],
    )
  return body as T
}

// Lỗi quy tắc nghiệp vụ hiện kèm mã để đối chiếu tài liệu (NFR-USA-02): "… (BR-66)"
export const kemMaBr = (thongDiep: string, ma?: string) =>
  ma && /^BR-\d+$/.test(ma) ? `${thongDiep} (${ma})` : thongDiep

// Bộ lọc → chuỗi tham số URL, bỏ ô trống
export const query = (loc: Record<string, string | number | undefined>) => {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(loc)) if (v !== undefined && v !== '') q.set(k, String(v))
  return q
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
