// NFR-PER-03: nén ảnh trên trình duyệt trước khi gửi – cạnh dài ≤ 1280 px, JPEG chất lượng 0,7.
// Máy chủ vẫn chặn ảnh > 500 KB (app/luu_tru.py); ảnh chưa đủ nhỏ thì giảm chất lượng thêm vài lần.
const CANH_TOI_DA = 1280
const TOI_DA_BYTE = 500 * 1024

export async function nenAnh(file: File): Promise<Blob> {
  const anh = await createImageBitmap(file)
  const ty_le = Math.min(1, CANH_TOI_DA / Math.max(anh.width, anh.height))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(anh.width * ty_le)
  canvas.height = Math.round(anh.height * ty_le)
  canvas.getContext('2d')!.drawImage(anh, 0, 0, canvas.width, canvas.height)
  anh.close()
  let ket_qua: Blob | null = null
  for (const chat_luong of [0.7, 0.55, 0.4]) {
    ket_qua = await new Promise<Blob | null>((xong) =>
      canvas.toBlob(xong, 'image/jpeg', chat_luong),
    )
    if (ket_qua && ket_qua.size <= TOI_DA_BYTE) break
  }
  if (!ket_qua) throw new Error('Không đọc được ảnh, vui lòng chụp lại')
  return ket_qua
}
