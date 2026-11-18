import { useEffect, useState, type FormEvent } from 'react'
import { LoiApi, loiTheoTruong } from '../../api/goi'
import { Nhan } from '../../nhan'
import { DauDanhMuc, NhanHoatDong, OTim } from '../danh-muc'
import {
  danhSachNut,
  danhSachTuyen,
  suaTuyen,
  themTuyen,
  type Nut,
  type NutTuyenVao,
  type Tuyen,
} from '../../api/tuyen'

const dong = (n: number) => n.toLocaleString('vi-VN')
const gio = (phut: number) => `${Math.floor(phut / 60)} giờ ${phut % 60} phút`

export default function TuyenDanhSach() {
  const [tim, setTim] = useState('')
  const [ds, setDs] = useState<{ du_lieu: Tuyen[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [dangSua, setDangSua] = useState<Tuyen | 'moi' | null>(null)
  const [canhBao, setCanhBao] = useState<{ ma: string; ds: string[] } | null>(null)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachTuyen({ tim, so_dong: 100 })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách tuyến')
      })
    return () => {
      bo = true
    }
  }, [tim, lanTai])

  async function doiTrangThai(t: Tuyen) {
    try {
      await suaTuyen(t.id, { trang_thai: t.trang_thai === 'HOAT_DONG' ? 'NGUNG' : 'HOAT_DONG' })
      setLanTai((n) => n + 1)
    } catch (e) {
      setLoiTai(e instanceof LoiApi ? e.message : 'Không đổi được trạng thái')
    }
  }

  return (
    <section className="noi-dung">
      <DauDanhMuc
        tieuDe="Tuyến"
        phu="Lộ trình cố định, định mức chi phí và lương khoán mỗi chuyến"
        nut="Thêm tuyến"
        onNut={() => setDangSua('moi')}
      />
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}
      {canhBao && canhBao.ds.length > 0 && (
        <div role="status" className="canh-bao">
          <strong>Tuyến {canhBao.ma} đã lưu, nhưng thiếu điểm nghỉ (BR-20):</strong>
          <ul>
            {canhBao.ds.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="kinh bang-khung dm">
        <div className="cong-cu">
          <span className="ghi-chu">{ds.du_lieu.length} tuyến</span>
          <OTim giaTri={tim} goiY="Tìm mã hoặc tên tuyến" onDoi={setTim} />
        </div>
        <table>
          <thead>
            <tr>
              <th>Mã</th>
              <th>Tên</th>
              <th>Lộ trình</th>
              <th className="so">Thời gian</th>
              <th className="so">Km</th>
              <th className="so">Định mức + lương (đ)</th>
              <th>Trạng thái</th>
              <th>
                <span className="an-chu">Thao tác</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {ds.du_lieu.map((t) => (
              <tr key={t.id} className={t.trang_thai === 'NGUNG' ? 'mo' : undefined}>
                <td>
                  <span className="bien">{t.ma}</span>
                </td>
                <td className="tuyen">{t.ten}</td>
                <td>
                  <ol className="lo-trinh">
                    {t.nut.map((n) => (
                      <li key={n.thu_tu} className={n.la_diem_nghi ? 'nghi' : undefined}>
                        {n.ten}
                        {n.la_diem_nghi && <small> nghỉ</small>}
                      </li>
                    ))}
                  </ol>
                  {t.canh_bao.length > 0 && (
                    <Nhan loai="SU_CO" title={t.canh_bao.join('; ')}>
                      Thiếu điểm nghỉ
                    </Nhan>
                  )}
                </td>
                <td className="so">{gio(t.tong_phut)}</td>
                <td className="so">{dong(t.tong_km)}</td>
                <td className="so">
                  {dong(t.dm_dau + t.dm_cau_duong + t.dm_boc_xep)} + {dong(t.dm_luong_tai_xe)}
                </td>
                <td>
                  <NhanHoatDong trangThai={t.trang_thai} />
                </td>
                <td className="hanh-dong so">
                  <button className="phu" onClick={() => setDangSua(t)}>
                    Sửa
                  </button>
                  <button className="phu" onClick={() => doiTrangThai(t)}>
                    {t.trang_thai === 'HOAT_DONG' ? 'Ngừng' : 'Hoạt động lại'}
                  </button>
                </td>
              </tr>
            ))}
            {ds.du_lieu.length === 0 && (
              <tr>
                <td colSpan={8} className="trong">
                  Chưa có tuyến nào
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {dangSua && (
        <FormTuyen
          tuyen={dangSua === 'moi' ? null : dangSua}
          onDong={() => setDangSua(null)}
          onLuu={(t) => {
            setDangSua(null)
            setCanhBao({ ma: t.ma, ds: t.canh_bao })
            setLanTai((n) => n + 1)
          }}
        />
      )}
    </section>
  )
}

type DongNut = { nut_id: string; phut: string; km: string; nghi: boolean }
const DONG_TRONG: DongNut = { nut_id: '', phut: '', km: '', nghi: false }

function FormTuyen({
  tuyen,
  onDong,
  onLuu,
}: {
  tuyen: Tuyen | null
  onDong: () => void
  onLuu: (t: Tuyen) => void
}) {
  const [f, setF] = useState({
    ma: tuyen?.ma ?? '',
    ten: tuyen?.ten ?? '',
    dm_dau: String(tuyen?.dm_dau ?? ''),
    dm_cau_duong: String(tuyen?.dm_cau_duong ?? ''),
    dm_boc_xep: String(tuyen?.dm_boc_xep ?? ''),
    dm_luong_tai_xe: String(tuyen?.dm_luong_tai_xe ?? ''),
  })
  const [dongNut, setDongNut] = useState<DongNut[]>(
    tuyen
      ? tuyen.nut.map((n) => ({
          nut_id: String(n.nut_id),
          phut: String(n.phut_tu_diem_dau),
          km: String(n.km_tu_diem_dau),
          nghi: n.la_diem_nghi,
        }))
      : [{ ...DONG_TRONG, phut: '0', km: '0' }],
  )
  const [dsNut, setDsNut] = useState<Nut[]>([])
  const [loi, setLoi] = useState<string[]>([])

  useEffect(() => {
    // shortcut: lấy tối đa 100 nút, đủ cho nhà xe nhỏ; nhiều hơn thì thêm ô tìm
    danhSachNut({ so_dong: 100 })
      .then((r) => setDsNut(r.du_lieu))
      .catch(() => setLoi(['Không tải được danh sách nút']))
  }, [])

  const doiDong = (i: number, sua: Partial<DongNut>) =>
    setDongNut(dongNut.map((d, j) => (j === i ? { ...d, ...sua } : d)))
  const doiCho = (i: number, j: number) => {
    const moi = [...dongNut]
    ;[moi[i], moi[j]] = [moi[j], moi[i]]
    setDongNut(moi)
  }

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoi([])
    const nut: NutTuyenVao[] = dongNut.map((d) => ({
      nut_id: Number(d.nut_id),
      phut_tu_diem_dau: Number(d.phut),
      km_tu_diem_dau: Number(d.km),
      la_diem_nghi: d.nghi,
    }))
    const dinhMuc = {
      ten: f.ten,
      dm_dau: Number(f.dm_dau),
      dm_cau_duong: Number(f.dm_cau_duong),
      dm_boc_xep: Number(f.dm_boc_xep),
      dm_luong_tai_xe: Number(f.dm_luong_tai_xe),
    }
    try {
      // Chỉ gửi danh sách nút khi có đổi: tuyến đã có chuyến thì không đổi nút được (409)
      const doiNut =
        !tuyen ||
        JSON.stringify(nut) !==
          JSON.stringify(
            tuyen.nut.map(({ nut_id, phut_tu_diem_dau, km_tu_diem_dau, la_diem_nghi }) => ({
              nut_id,
              phut_tu_diem_dau,
              km_tu_diem_dau,
              la_diem_nghi,
            })),
          )
      onLuu(
        tuyen
          ? await suaTuyen(tuyen.id, doiNut ? { ...dinhMuc, nut } : dinhMuc)
          : await themTuyen({ ...dinhMuc, ma: f.ma, nut }),
      )
    } catch (err) {
      const theoTruong = Object.values(loiTheoTruong(err))
      if (err instanceof LoiApi && err.chiTiet.length && !theoTruong.length)
        setLoi(err.chiTiet.map((c) => (c as { thong_diep?: string }).thong_diep ?? err.message))
      else if (theoTruong.length) setLoi(theoTruong)
      else setLoi([err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại'])
    }
  }

  const o = (k: keyof typeof f, nhan: string, so = false) => (
    <label>
      {nhan}
      <input
        value={f[k]}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
        required
        disabled={k === 'ma' && !!tuyen}
        {...(so ? { type: 'number', min: 0, step: 1000 } : {})}
      />
    </label>
  )

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai rong" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>{tuyen ? `Sửa tuyến ${tuyen.ma}` : 'Thêm tuyến'}</h2>
        <div className="hai-cot">
          {o('ma', 'Mã tuyến')}
          {o('ten', 'Tên tuyến')}
          {o('dm_dau', 'Định mức dầu (đ)', true)}
          {o('dm_cau_duong', 'Định mức cầu đường (đ)', true)}
          {o('dm_boc_xep', 'Định mức bốc xếp (đ)', true)}
          {o('dm_luong_tai_xe', 'Lương khoán tài xế mỗi chuyến (đ)', true)}
        </div>

        <h3>Các nút theo thứ tự</h3>
        <p className="ghi-chu">
          Nút đầu: 0 phút, 0 km. Phút tính từ điểm đầu, tăng dần. Tổng thời gian không quá giờ lái
          một ngày (BR-66).
        </p>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nút</th>
              <th>Phút từ đầu</th>
              <th>Km từ đầu</th>
              <th>Điểm nghỉ</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {dongNut.map((d, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>
                  <select
                    aria-label={`Nút thứ ${i + 1}`}
                    value={d.nut_id}
                    onChange={(e) => doiDong(i, { nut_id: e.target.value })}
                    required
                  >
                    <option value="">– Chọn nút –</option>
                    {dsNut.map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.ten} ({n.tinh})
                      </option>
                    ))}
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    min={0}
                    size={5}
                    aria-label={`Phút nút ${i + 1}`}
                    value={d.phut}
                    onChange={(e) => doiDong(i, { phut: e.target.value })}
                    required
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min={0}
                    size={5}
                    aria-label={`Km nút ${i + 1}`}
                    value={d.km}
                    onChange={(e) => doiDong(i, { km: e.target.value })}
                    required
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    aria-label={`Điểm nghỉ nút ${i + 1}`}
                    checked={d.nghi}
                    onChange={(e) => doiDong(i, { nghi: e.target.checked })}
                  />
                </td>
                <td className="hanh-dong">
                  <button
                    type="button"
                    className="phu"
                    disabled={i === 0}
                    onClick={() => doiCho(i, i - 1)}
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    className="phu"
                    disabled={i === dongNut.length - 1}
                    onClick={() => doiCho(i, i + 1)}
                  >
                    ↓
                  </button>
                  <button
                    type="button"
                    className="phu"
                    disabled={dongNut.length === 1}
                    onClick={() => setDongNut(dongNut.filter((_, j) => j !== i))}
                  >
                    Bỏ
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div>
          <button
            type="button"
            className="phu"
            onClick={() => setDongNut([...dongNut, DONG_TRONG])}
          >
            + Thêm nút
          </button>
        </div>

        {loi.length > 0 && (
          <ul role="alert" className="loi">
            {loi.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            Hủy
          </button>
          <button>Lưu</button>
        </div>
      </form>
    </div>
  )
}
