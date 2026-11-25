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
import { Nhan } from '../nhan'
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
          <span className="mui-ten-thuong">← </span>Chuyến của tôi
        </Link>
      )}
      <DauDanhMuc tieuDe="Cài đặt" phu="Tùy chọn hiển thị trên trình duyệt này, áp dụng ngay." />

      {phongCach === 'pixel' ? (
        /* Pixel: bảng tùy chọn game chia nhóm dải than + lưới thẻ + khung Xem trước & Mẹo */
        <div className="px-cd-bo-cuc">
          <div className="px-cd-chinh">
            <section className="kinh px-cd-nhom" aria-labelledby="cd-nhom-gd">
              <div className="px-cd-nhom-dau">
                <h2 id="cd-nhom-gd">Giao diện</h2>
                <span className="px-cd-dem" aria-hidden="true">
                  3 mục
                </span>
              </div>

              <div className="px-cd-pc">
                <div className="px-cd-pc-dau">
                  <h3>Phong cách</h3>
                  <p>
                    Hiện tại hoặc Pixel (thử nghiệm): bảng màu Nostalgos 12, viền rõ, bóng cứng và
                    hiệu ứng riêng. Pixel chỉ có bản sáng; nội dung và thao tác giữ nguyên.
                  </p>
                </div>
                <div className="px-cd-pc-luoi" role="group" aria-label="Phong cách">
                  {PHONG_CACH.map((c) => {
                    const chon = phongCach === c.ma
                    const laPx = c.ma === 'pixel'
                    return (
                      <button
                        key={c.ma || 'mac-dinh'}
                        type="button"
                        className={`px-cd-pc-o${chon ? ' chon' : ''}`}
                        aria-pressed={chon}
                        onClick={() => {
                          apPhongCach(c.ma)
                          setPhongCach(c.ma)
                        }}
                      >
                        <span className="px-cd-pc-ghim" aria-hidden="true">
                          {chon ? 'Đang dùng' : 'Chọn'}
                        </span>
                        <span
                          className={`px-cd-pc-hinh ${laPx ? 'pixel' : 'thuong'}`}
                          aria-hidden="true"
                        >
                          <span className="px-cd-pc-canh" />
                          <span className="px-cd-pc-than">
                            <span className="px-cd-pc-thanh" />
                            <span className="px-cd-pc-the-mau">
                              <i />
                              <i />
                            </span>
                            <span className="px-cd-pc-dong" />
                          </span>
                        </span>
                        <span className="px-cd-pc-ten">
                          <span className="px-cd-pc-mui" aria-hidden="true">
                            ▶
                          </span>
                          {c.ten}
                        </span>
                        <span className="px-cd-pc-phu" aria-hidden="true">
                          {laPx
                            ? 'Nostalgos 12 · viền than · bóng cứng'
                            : 'Sáng / tối · bo góc mềm · mặc định'}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="px-cd-luoi">
                <TheCaiDat
                  tieuDe="Hiệu ứng Pixel"
                  moTa="Chuyển trang, nút lún, rung ô lỗi, laser quét mã, con dấu đã giao, xe tải tra cứu… Tắt thì giữ màu, viền, bóng và bỏ chuyển động."
                  ds={HIEU_UNG_PIXEL}
                  giaTri={hieuUngPixel}
                  dangBat={hieuUngPixel === 'bat'}
                  onChon={(ma) => {
                    apHieuUngPixel(ma)
                    setHieuUngPixel(hieuUngPixelDaLuu())
                  }}
                />
                <TheCaiDat
                  tieuDe="Hiệu ứng nâng cao"
                  moTa="Hạt nền, chữ gõ ở màn đăng nhập và tổng quan. Tắt nếu máy chậm."
                  ds={HIEU_UNG}
                  giaTri={hieuUng}
                  dangBat={hieuUng === 'bat'}
                  onChon={(ma) => {
                    apHieuUng(ma)
                    setHieuUng(hieuUngDaLuu())
                  }}
                />
              </div>
            </section>

            <section className="kinh px-cd-nhom" aria-labelledby="cd-nhom-ht">
              <div className="px-cd-nhom-dau">
                <h2 id="cd-nhom-ht">Hiển thị</h2>
                <span className="px-cd-dem" aria-hidden="true">
                  2 mục
                </span>
              </div>
              <div className="px-cd-luoi">
                <TheCaiDat
                  tieuDe="Mật độ bảng"
                  moTa="Thu gọn khoảng trống dòng bảng và thẻ danh sách để xem được nhiều hơn."
                  ds={MAT_DO}
                  giaTri={matDo}
                  dangBat={matDo === 'gon'}
                  onChon={(ma) => {
                    apMatDo(ma)
                    setMatDo(ma)
                  }}
                />
                <TheCaiDat
                  tieuDe="Cỡ chữ"
                  moTa="Tăng cỡ chữ toàn giao diện khoảng 112,5% cho dễ đọc hơn."
                  ds={CO_CHU}
                  giaTri={coChu}
                  dangBat={coChu === 'lon'}
                  onChon={(ma) => {
                    apCoChu(ma)
                    setCoChu(ma)
                  }}
                />
              </div>
            </section>

            <section className="kinh px-cd-nhom" aria-labelledby="cd-nhom-tn">
              <div className="px-cd-nhom-dau">
                <h2 id="cd-nhom-tn">Trợ năng</h2>
                <span className="px-cd-dem" aria-hidden="true">
                  1 mục
                </span>
              </div>
              <div className="px-cd-luoi mot">
                <TheCaiDat
                  tieuDe="Giảm chuyển động"
                  moTa="Tắt hiệu ứng chuyển cảnh và số chạy khi thao tác."
                  ds={GIAM_CHUYEN_DONG}
                  giaTri={giamCD}
                  dangBat={giamCD === 'bat'}
                  onChon={(ma) => {
                    apGiamChuyenDong(ma)
                    setGiamCD(ma)
                  }}
                />
              </div>
            </section>
          </div>

          <aside className="px-cd-ben" aria-label="Xem trước và mẹo">
            <section className="kinh px-cd-nhom px-cd-xem" aria-labelledby="cd-xem-truoc">
              <div className="px-cd-nhom-dau">
                <h2 id="cd-xem-truoc">Xem trước</h2>
                <span className="px-cd-dem" aria-hidden="true">
                  Trực tiếp
                </span>
              </div>
              <div className="px-cd-xem-than" aria-hidden="true">
                <div className={`px-cd-mau-the${matDo === 'gon' ? ' gon' : ''}`}>
                  <div className="px-cd-mau-dau">
                    <span className="px-cd-mau-ma ma">CH-204</span>
                    <Nhan loai="DANG_CHAY">Đang chạy</Nhan>
                  </div>
                  <p className="px-cd-mau-tuyen">Kho Thủ Đức → KCN Bình Dương</p>
                  <div className="px-cd-mau-bang">
                    <div>
                      <span className="ma">DH-089</span>
                      <Nhan loai="HOAN_THANH">Đã giao</Nhan>
                    </div>
                    <div>
                      <span className="ma">DH-092</span>
                      <span className="px-cd-mau-kg ma">420 kg</span>
                    </div>
                  </div>
                  <div className="px-cd-mau-cuoi">
                    <span className="px-cd-mau-nut">Xác nhận</span>
                    <span
                      className={`px-cd-mau-den${
                        hieuUngPixel === 'bat' && giamCD !== 'bat' ? ' chay' : ''
                      }`}
                    >
                      <i />
                      {hieuUngPixel === 'bat' && giamCD !== 'bat' ? 'Hiệu ứng bật' : 'Tĩnh'}
                    </span>
                  </div>
                </div>

                <dl className="px-cd-tt-luoi">
                  <div>
                    <dt>Mật độ</dt>
                    <dd>{matDo === 'gon' ? 'Gọn' : 'Thoải mái'}</dd>
                  </div>
                  <div>
                    <dt>Cỡ chữ</dt>
                    <dd>{coChu === 'lon' ? 'Lớn (112,5%)' : 'Vừa'}</dd>
                  </div>
                  <div>
                    <dt>Hiệu ứng Pixel</dt>
                    <dd>{hieuUngPixel === 'bat' ? 'Đang bật' : 'Đã tắt'}</dd>
                  </div>
                  <div>
                    <dt>Chuyển động</dt>
                    <dd>{giamCD === 'bat' ? 'Giảm' : 'Theo máy'}</dd>
                  </div>
                </dl>
              </div>
            </section>

            <section className="kinh px-cd-nhom px-cd-meo" aria-labelledby="cd-meo">
              <div className="px-cd-nhom-dau">
                <h2 id="cd-meo">Mẹo</h2>
              </div>
              <ul className="px-cd-meo-ds">
                <li>Mọi tùy chọn được lưu trên trình duyệt này và áp dụng ngay, không cần Lưu.</li>
                <li>Chọn Mật độ Gọn khi theo dõi nhiều chuyến hoặc đơn hàng cùng lúc.</li>
                <li>Bật Giảm chuyển động để bỏ hoạt ảnh và giữ giao diện tĩnh dễ đọc.</li>
              </ul>
            </section>
          </aside>
        </div>
      ) : (
        <div className="kinh cd-ds">
          <MucCaiDat
            tieuDe="Phong cách"
            moTa="Hiện tại hoặc Pixel (thử nghiệm): bảng màu Nostalgos 12, viền rõ, bóng cứng và hiệu ứng riêng. Pixel chỉ có bản sáng; nội dung và thao tác giữ nguyên."
            ds={PHONG_CACH}
            giaTri={phongCach}
            onChon={(ma) => {
              apPhongCach(ma)
              setPhongCach(ma)
            }}
          />
          <MucCaiDat
            tieuDe="Giao diện"
            moTa="Chọn nền sáng, nền tối hoặc tự động theo cài đặt của máy."
            ds={CHE_DO}
            giaTri={cheDo}
            onChon={(ma) => {
              doiCheDo(ma)
              setCheDo(ma)
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
            moTa="Đàn con trỏ chạy theo thao tác trên màn hình. Cần bật Hiệu ứng nâng cao; hạt nền và chữ gõ không bị ảnh hưởng."
            ds={CON_TRO}
            giaTri={conTro}
            onChon={(ma) => {
              apConTro(ma)
              setConTro(conTroDaLuu())
            }}
          />
        </div>
      )}

      {vaiTro === 'QUAN_LY' && (
        <p className="cd-chan ghi-chu">
          Tham số nghiệp vụ (cước, định mức…) ở{' '}
          <Link to="/quan-ly/cau-hinh">Cấu hình hệ thống</Link>.
        </p>
      )}
    </section>
  )
}

// Thẻ tùy chọn nhỏ cho bảng điều khiển Pixel (tiêu đề, mô tả, cụm nút chọn, viền vàng bơ khi bật)
function TheCaiDat({
  tieuDe,
  moTa,
  ds,
  giaTri,
  dangBat,
  onChon,
}: {
  tieuDe: string
  moTa: string
  ds: LuaChon
  giaTri: string
  dangBat: boolean
  onChon: (ma: string) => void
}) {
  return (
    <div className={`px-cd-the${dangBat ? ' bat' : ''}`}>
      <div className="px-cd-the-dau">
        <h3>{tieuDe}</h3>
        {dangBat && (
          <span className="px-cd-the-tem" aria-hidden="true">
            Đang bật
          </span>
        )}
      </div>
      <p>{moTa}</p>
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
