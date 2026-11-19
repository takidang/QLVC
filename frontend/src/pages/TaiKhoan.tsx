import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import {
  chuTat,
  doiAnhDaiDien,
  doiMatKhau,
  hoSo,
  LoiApi,
  urlAnhDaiDien,
  xoaAnhDaiDien,
  type HoSo,
  type NguoiDung,
} from '../api/auth'
import { nenAnh } from '../nenAnh'
import { DauDanhMuc, HanGiayTo, NhanHoatDong } from './danh-muc'

// Trang Tài khoản (mọi vai trò): ảnh đại diện (UC-39), hồ sơ chỉ xem và form đổi mật khẩu (UC-35).
export default function TaiKhoan({
  nd,
  tenVaiTro,
  phienBanAnh,
  onDoiAnh,
}: {
  nd: NguoiDung
  tenVaiTro: string
  phienBanAnh: number
  onDoiAnh: (coAnh: boolean) => void
}) {
  const [hs, setHs] = useState<HoSo | null>(null)
  const [loiTai, setLoiTai] = useState('')
  const [loiAnh, setLoiAnh] = useState('')
  const [dangXuLyAnh, setDangXuLyAnh] = useState(false)
  const [loiHienAnhV, setLoiHienAnhV] = useState<number | null>(null)
  const oFile = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let bo = false
    hoSo()
      .then((duLieu) => {
        if (bo) return
        setHs(duLieu)
        setLoiTai('')
      })
      .catch((err) => {
        if (!bo) setLoiTai(err instanceof LoiApi ? err.message : 'Không tải được hồ sơ cá nhân')
      })
    return () => {
      bo = true
    }
  }, [nd.id])

  const hoTen = hs?.ho_ten ?? nd.ho_ten
  const coAnh = hs ? hs.co_anh_dai_dien : nd.co_anh_dai_dien
  const hienAnh = coAnh && loiHienAnhV !== phienBanAnh

  async function chonAnh(e: ChangeEvent<HTMLInputElement>) {
    const tep = e.target.files?.[0]
    e.target.value = '' // cho phép chọn lại cùng một file sau khi lỗi hoặc xóa
    if (!tep) return
    setLoiAnh('')
    setDangXuLyAnh(true)
    try {
      let duLieuGui: Blob = tep
      if (tep.type === 'image/jpeg' || tep.type === 'image/png') {
        try {
          duLieuGui = await nenAnh(tep)
        } catch {
          // File hỏng hoặc giả đuôi .jpg/.png: gửi thẳng để máy chủ kiểm byte đầu và báo lỗi chuẩn
          duLieuGui = tep
        }
      }
      const moi = await doiAnhDaiDien(duLieuGui)
      setHs(moi)
      onDoiAnh(true)
      toast.success('Đã cập nhật ảnh đại diện')
    } catch (err) {
      setLoiAnh(
        err instanceof LoiApi ? err.message : 'Không cập nhật được ảnh đại diện, vui lòng thử lại',
      )
    } finally {
      setDangXuLyAnh(false)
    }
  }

  async function xoaAnh() {
    setLoiAnh('')
    setDangXuLyAnh(true)
    try {
      await xoaAnhDaiDien()
      setHs((cu) => (cu ? { ...cu, co_anh_dai_dien: false } : cu))
      onDoiAnh(false)
      toast.success('Đã xóa ảnh đại diện')
    } catch (err) {
      setLoiAnh(
        err instanceof LoiApi ? err.message : 'Không xóa được ảnh đại diện, vui lòng thử lại',
      )
    } finally {
      setDangXuLyAnh(false)
    }
  }

  return (
    <section className="noi-dung cd-trang">
      {nd.vai_tro === 'TAI_XE' && (
        <Link to="/tai-xe/chuyen" className="ct-ve">
          ← Chuyến của tôi
        </Link>
      )}
      <DauDanhMuc
        tieuDe="Tài khoản"
        phu="Ảnh đại diện, thông tin cá nhân và đổi mật khẩu đăng nhập."
      />

      <div className="cd-cot">
        <section className="kinh cd-khoi" aria-labelledby="tk-anh">
          <h2 id="tk-anh">Ảnh đại diện</h2>
          <p className="ghi-chu">Ảnh JPEG hoặc PNG, tối đa 500 KB (tự nén trước khi gửi).</p>
          <div className="tk-anh-hang">
            <div className="tk-anh">
              {hienAnh ? (
                <img
                  src={urlAnhDaiDien(phienBanAnh)}
                  alt={`Ảnh đại diện của ${hoTen}`}
                  onError={() => setLoiHienAnhV(phienBanAnh)}
                />
              ) : (
                <span aria-hidden="true">{chuTat(hoTen)}</span>
              )}
            </div>
            <div className="tk-anh-nut">
              <input
                ref={oFile}
                type="file"
                accept="image/jpeg,image/png"
                hidden
                onChange={chonAnh}
                disabled={dangXuLyAnh}
              />
              <button type="button" onClick={() => oFile.current?.click()} disabled={dangXuLyAnh}>
                {dangXuLyAnh ? 'Đang xử lý…' : 'Chọn ảnh'}
              </button>
              {coAnh && (
                <button type="button" className="phu" onClick={xoaAnh} disabled={dangXuLyAnh}>
                  Xóa ảnh
                </button>
              )}
            </div>
          </div>
          {loiAnh && (
            <p role="alert" className="loi">
              {loiAnh}
            </p>
          )}
        </section>

        <section className="kinh cd-khoi" aria-labelledby="tk-thong-tin">
          <h2 id="tk-thong-tin">Thông tin cá nhân</h2>
          <p className="ghi-chu">Thông tin chỉ xem · Liên hệ Quản lý để thay đổi.</p>
          {loiTai && (
            <p role="alert" className="loi">
              {loiTai}
            </p>
          )}
          <dl className="tk-tt">
            <div>
              <dt>Họ tên</dt>
              <dd>{hoTen}</dd>
            </div>
            <div>
              <dt>Tên đăng nhập</dt>
              <dd className="ma">{hs ? hs.ten_dang_nhap : '…'}</dd>
            </div>
            <div>
              <dt>Vai trò</dt>
              <dd>{tenVaiTro}</dd>
            </div>
            <div>
              <dt>Trạng thái</dt>
              <dd>{hs ? <NhanHoatDong trangThai={hs.trang_thai} /> : '…'}</dd>
            </div>
            {hs?.tai_xe && (
              <>
                <div>
                  <dt>Số điện thoại</dt>
                  <dd className="ma">{hs.tai_xe.sdt}</dd>
                </div>
                <div>
                  <dt>Số GPLX</dt>
                  <dd className="ma">{hs.tai_xe.so_gplx}</dd>
                </div>
                <div>
                  <dt>Hạng GPLX</dt>
                  <dd>Hạng {hs.tai_xe.hang_gplx}</dd>
                </div>
                <div>
                  <dt>Hạn GPLX</dt>
                  <dd>
                    <HanGiayTo han={hs.tai_xe.han_gplx} />
                  </dd>
                </div>
              </>
            )}
          </dl>
        </section>

        <section className="kinh cd-khoi" aria-labelledby="tk-doi-mk">
          <h2 id="tk-doi-mk">Đổi mật khẩu</h2>
          <p className="ghi-chu">Mật khẩu mới từ 8 đến 200 ký tự, khác mật khẩu hiện tại.</p>
          <DoiMatKhau />
        </section>
      </div>
    </section>
  )
}

// UC-35: mật khẩu hiện tại + mật khẩu mới (8–200 ký tự) + nhập lại. Xong thì báo bằng toast, phiên vẫn dùng tiếp
function DoiMatKhau() {
  const [cu, setCu] = useState('')
  const [moi, setMoi] = useState('')
  const [lai, setLai] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (moi.length < 8) return setLoi('Mật khẩu mới cần ít nhất 8 ký tự')
    if (moi.length > 200) return setLoi('Mật khẩu mới tối đa 200 ký tự')
    if (moi !== lai) return setLoi('Hai lần nhập mật khẩu mới chưa khớp')
    setLoi('')
    setDangGui(true)
    try {
      await doiMatKhau(cu, moi)
      toast.success('Đã đổi mật khẩu')
      setCu('')
      setMoi('')
      setLai('')
    } catch (err) {
      setLoi(
        err instanceof LoiApi && err.status === 429
          ? 'Nhập sai mật khẩu hiện tại quá nhiều lần, tài khoản tạm khóa 15 phút'
          : err instanceof LoiApi && err.status === 422
            ? err.message
            : err instanceof LoiApi && err.status === 400
              ? 'Mật khẩu mới cần 8–200 ký tự'
              : 'Không đổi được mật khẩu, vui lòng thử lại',
      )
    } finally {
      setDangGui(false)
    }
  }

  return (
    <form className="tk-mk" onSubmit={gui} noValidate>
      <label>
        Mật khẩu hiện tại
        <input
          type="password"
          autoComplete="current-password"
          value={cu}
          onChange={(e) => setCu(e.target.value)}
          required
        />
      </label>
      <label>
        Mật khẩu mới
        <input
          type="password"
          autoComplete="new-password"
          value={moi}
          onChange={(e) => setMoi(e.target.value)}
          minLength={8}
          maxLength={200}
          required
        />
      </label>
      <label>
        Nhập lại mật khẩu mới
        <input
          type="password"
          autoComplete="new-password"
          value={lai}
          onChange={(e) => setLai(e.target.value)}
          required
        />
      </label>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      <div className="tk-mk-nut">
        <button disabled={dangGui || !cu || !moi || !lai}>
          {dangGui ? 'Đang lưu…' : 'Đổi mật khẩu'}
        </button>
      </div>
    </form>
  )
}
