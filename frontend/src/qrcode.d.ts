// Gói `qrcode` không kèm kiểu TypeScript; chỉ khai báo hàm dùng ở phiếu đơn (UC-19-AC14) thay vì cài thêm @types
declare module 'qrcode' {
  const QRCode: {
    toDataURL(noi_dung: string, tuy_chon?: { margin?: number; width?: number }): Promise<string>
  }
  export default QRCode
}
