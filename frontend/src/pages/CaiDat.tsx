import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { VaiTro } from '../api/auth'
import {
  CHE_DO,
  CON_TRO,
  CO_CHU,
  GIAM_CHUYEN_DONG,
  HIEU_UNG,
  HIEU_UNG_PIXEL,
  MAT_DO,
  PHONG_CACH,
  doiCheDo,
  apCoChu,
  apConTro,
  apGiamChuyenDong,
  apHieuUng,
  apHieuUngPixel,
  apMatDo,
  apPhongCach,
  cheDoDaLuu,
  coChuDaLuu,
  conTroDaLuu,
  giamChuyenDongDaLuu,
  hieuUngDaLuu,
  hieuUngPixelDaLuu,
  matDoDaLuu,
  phongCachDaLuu,
} from '../nen'
import { DauDanhMuc } from './danh-muc'

type LuaChon = readonly { readonly ma: string; readonly ten: string }[]

// Trang Cài đặt (mọi vai trò): 6 tùy chọn hiển thị, lưu localStorage và áp ngay không cần nút Lưu.
export default function CaiDat({ vaiTro }: { vaiTro: VaiTro }) {
  const [cheDo, setCheDo] = useState(cheDoDaLuu)
  const [matDo, setMatDo] = useState(matDoDaLuu)
  const [coChu, setCoChu] = useState(coChuDaLuu)
  const [giamCD, setGiamCD] = useState(giamChuyenDongDaLuu)
  const [hieuUng, setHieuUng] = useState(hieuUngDaLuu)
  const [phongCach, setPhongCach] = useState(phongCachDaLuu)
  const [conTro, setConTro] = useState(conTroDaLuu)
  const [hieuUngPixel, setHieuUngPixel] = useState(hieuUngPixelDaLuu)

  return (
    <section className="noi-dung cd-trang">
      {vaiTro === 'TAI_XE' && (
        <Link to="/tai-xe/chuyen" className="ct-ve">
          ← Chuyến của tôi
        </Link>
      )}
      <DauDanhMuc tieuDe="Cài đặt" phu="Tùy chọn hiển thị trên trình duyệt này, áp dụng ngay." />

      <div className="kinh cd-ds">
        <MucCaiDat
          tieuDe="Giao diện"
          moTa={`Chọn nền sáng, nền tối hoặc tự động theo cài đặt của máy.${phongCach === 'pixel' ? ' (Pixel chỉ có bản sáng)' : ''}`}
          ds={CHE_DO}
          giaTri={cheDo}
          onChon={(ma) => {
            doiCheDo(ma)
            setCheDo(ma)
          }}
        />
        <MucCaiDat
          tieuDe="Phong cách"
          moTa="Thử nghiệm: phủ phong cách pixel (bảng màu Nostalgos 12, viền rõ, bóng cứng) lên giao diện. Chỉ có bản sáng; nội dung và thao tác giữ nguyên."
          ds={PHONG_CACH}
          giaTri={phongCach}
          onChon={(ma) => {
            apPhongCach(ma)
            setPhongCach(ma)
          }}
        />
        <MucCaiDat
          tieuDe="Mật độ bảng"
          moTa="Thu gọn khoảng trống dòng bảng và thẻ danh sách để xem được nhiều hơn."
          ds={MAT_DO}
          giaTri={matDo}
          onChon={(ma) => {
            apMatDo(ma)
            setMatDo(ma)
          }}
        />
        <MucCaiDat
          tieuDe="Cỡ chữ"
          moTa="Tăng cỡ chữ toàn giao diện khoảng 112,5% cho dễ đọc hơn."
          ds={CO_CHU}
          giaTri={coChu}
          onChon={(ma) => {
            apCoChu(ma)
            setCoChu(ma)
          }}
        />
        <MucCaiDat
          tieuDe="Giảm chuyển động"
          moTa="Tắt hiệu ứng chuyển cảnh và số chạy khi thao tác."
          ds={GIAM_CHUYEN_DONG}
          giaTri={giamCD}
          onChon={(ma) => {
            apGiamChuyenDong(ma)
            setGiamCD(ma)
          }}
        />
        <MucCaiDat
          tieuDe="Hiệu ứng nâng cao"
          moTa="Hạt nền, đàn con trỏ, chữ gõ ở màn đăng nhập và tổng quan. Tắt nếu máy chậm."
          ds={HIEU_UNG}
          giaTri={hieuUng}
          onChon={(ma) => {
            apHieuUng(ma)
            setHieuUng(hieuUngDaLuu())
          }}
        />
        <MucCaiDat
          tieuDe="Con trỏ đi theo"
          moTa={
            phongCach === 'pixel'
              ? 'Đang dùng phong cách Pixel: con trỏ luôn tắt vì Pixel đã có hiệu ứng riêng.'
              : 'Đàn con trỏ chạy theo thao tác trên màn hình. Cần bật Hiệu ứng nâng cao; hạt nền và chữ gõ không bị ảnh hưởng.'
          }
          ds={CON_TRO}
          giaTri={conTro}
          onChon={(ma) => {
            apConTro(ma)
            setConTro(conTroDaLuu())
          }}
        />
        {phongCach === 'pixel' && (
          <MucCaiDat
            tieuDe="Hiệu ứng Pixel"
            moTa="Rung ô lỗi, lún nút, hiện lớp nổi theo kiểu pixel. Tắt thì giữ màu, viền, bóng và bỏ chuyển động."
            ds={HIEU_UNG_PIXEL}
            giaTri={hieuUngPixel}
            onChon={(ma) => {
              apHieuUngPixel(ma)
              setHieuUngPixel(hieuUngPixelDaLuu())
            }}
          />
        )}
      </div>

      {vaiTro === 'QUAN_LY' && (
        <p className="cd-chan ghi-chu">
          Tham số nghiệp vụ (cước, định mức…) ở{' '}
          <Link to="/quan-ly/cau-hinh">Cấu hình hệ thống</Link>.
        </p>
      )}
    </section>
  )
}

function MucCaiDat({
  tieuDe,
  moTa,
  ds,
  giaTri,
  onChon,
}: {
  tieuDe: string
  moTa: string
  ds: LuaChon
  giaTri: string
  onChon: (ma: string) => void
}) {
  return (
    <div className="cd-muc">
      <div>
        <h2>{tieuDe}</h2>
        <p>{moTa}</p>
      </div>
      <div className="vien-thuoc" role="group" aria-label={tieuDe}>
        {ds.map((c) => (
          <button
            key={c.ma || 'mac-dinh'}
            type="button"
            aria-pressed={giaTri === c.ma}
            onClick={() => onChon(c.ma)}
          >
            {c.ten}
          </button>
        ))}
      </div>
    </div>
  )
}
