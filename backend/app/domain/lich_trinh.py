"""Ghép đơn: lịch trình và ETA (BR-63, 64), kiểm ghép cho cả chuyến (BR-01…06, 67), lãi dự kiến (BR-52). Hàm thuần."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.chuyen import PHUT, ket_thuc_chay_rong
from app.thoi_gian import GIO_VN


@dataclass
class DonGhep:
    id: int
    ma_don: str
    kg: Decimal  # kg thực: kiểm tải theo kg thực, không theo KL tính cước (BR-49)
    m3: Decimal
    nut_lay: int  # nút giữ hàng nếu có (BR-69), không thì nút lấy
    nut_giao: int
    lay_tu: datetime | None
    lay_den: datetime | None
    han_giao: datetime


@dataclass
class DiemDung:
    don: DonGhep
    viec: str  # LAY | GIAO
    nut: int
    eta: datetime


def phut_dung(diem: DiemDung, cfg08: int) -> int:
    """Phút dừng của một điểm (mục 2.1): hiện bằng CFG-08 cho mọi điểm; sau thay theo loại điểm hoặc dữ liệu thật."""
    return cfg08


def lich_trinh(khoi_hanh: datetime, thu_tu: dict[int, int], phut: dict[int, int], don: list[DonGhep], cfg08: int):
    """BR-63. `thu_tu`, `phut`: nút của tuyến → thứ tự, phút từ điểm đầu. Đơn phải thuộc tuyến (đã qua BR-03)."""

    def khoa(d: DiemDung):
        if d.viec == "LAY":  # có khung trước (đầu khung sớm trước), không khung sau, cùng thì theo mã đơn
            co_khung = d.don.lay_tu is not None
            return (thu_tu[d.nut], 0, not co_khung, d.don.lay_tu.timestamp() if co_khung else 0, d.don.ma_don)
        return (thu_tu[d.nut], 1, False, d.don.han_giao.timestamp(), d.don.ma_don)  # hạn sớm trước

    diem = sorted(
        [DiemDung(x, "LAY", x.nut_lay, khoi_hanh) for x in don]
        + [DiemDung(x, "GIAO", x.nut_giao, khoi_hanh) for x in don],
        key=khoa,
    )
    da_dung = 0  # Σ phút dừng của các điểm đứng trước
    for d in diem:
        d.eta = khoi_hanh + (phut[d.nut] + da_dung) * PHUT
        da_dung += phut_dung(d, cfg08)
    return diem


def ket_thuc_du_kien(khoi_hanh: datetime, phut_tuyen: int, diem: list[DiemDung], cfg08: int, cfg05: int) -> datetime:
    """BR-64: ETA điểm cuối + phút dừng điểm cuối + CFG-05; chuyến 0 đơn tính như chạy rỗng."""
    if not diem:
        return ket_thuc_chay_rong(khoi_hanh, phut_tuyen, cfg05)
    return diem[-1].eta + (phut_dung(diem[-1], cfg08) + cfg05) * PHUT


def _so(x: Decimal | int) -> str:
    nguyen, _, le = f"{Decimal(x):f}".partition(".")
    le = le.rstrip("0")
    return f"{int(nguyen):,}".replace(",", ".") + ("," + le if le else "")


def _gio(t: datetime) -> str:
    return t.astimezone(GIO_VN).strftime("%H:%M %d/%m")


def xet_ghep(
    don: list[DonGhep],
    moi: set[int],
    thu_tu: dict[int, int],
    phut: dict[int, int],
    khoi_hanh: datetime,
    cfg08: int,
    tai_trong_kg: int,
    the_tich_m3: Decimal,
) -> tuple[list[DiemDung], list[dict]]:
    """Kiểm cả chuyến sau khi ghép/gỡ (BR-67): BR-01…06 cho mọi đơn hiệu lực. `moi`: id đơn đang ghép thêm.

    Trả (lịch trình, vi phạm); vi phạm ở đơn đã ghép trước được ghi rõ để Điều phối biết vì sao bị chặn."""
    vp: list[dict] = []

    def loi(x: DonGhep | None, ma: str, cau: str):
        ten = "" if x is None else (f"Đơn {x.ma_don}: " if x.id in moi else f"Đơn đã ghép {x.ma_don}: ")
        vp.append({"don_id": x.id if x else None, "ma": ma, "thong_diep": ten + cau})

    hop_le = []
    for x in don:
        if x.nut_lay not in thu_tu or x.nut_giao not in thu_tu:
            loi(x, "BR-03", "điểm lấy hoặc điểm giao không thuộc tuyến của chuyến")
        elif thu_tu[x.nut_lay] > thu_tu[x.nut_giao]:
            loi(x, "BR-04", "sai chiều tuyến, nút giao đứng trước nút lấy")
        else:
            hop_le.append(x)

    kg, m3 = sum((x.kg for x in don), Decimal(0)), sum((x.m3 for x in don), Decimal(0))
    if kg > tai_trong_kg:
        loi(None, "BR-01", f"Tổng {_so(kg)} kg vượt tải trọng xe {_so(tai_trong_kg)} kg")
    if m3 > the_tich_m3:
        loi(None, "BR-02", f"Tổng {_so(m3)} m³ vượt thể tích thùng {_so(the_tich_m3)} m³")

    diem = lich_trinh(khoi_hanh, thu_tu, phut, hop_le, cfg08)
    for d in diem:
        x = d.don
        if d.viec == "LAY" and x.lay_tu and x.lay_den and not (x.lay_tu <= d.eta <= x.lay_den):
            khi = "sớm hơn" if d.eta < x.lay_tu else "trễ hơn"
            cau = f"ETA lấy {_gio(d.eta)} {khi} khung giờ lấy {_gio(x.lay_tu)}–{_gio(x.lay_den)}"
            loi(x, "BR-05", cau)
        if d.viec == "GIAO" and d.eta > x.han_giao:
            loi(x, "BR-06", f"ETA giao {_gio(d.eta)} sau hạn giao {_gio(x.han_giao)}")
    return diem, vp


def ty_le_lap_day(kg: Decimal, m3: Decimal, tai_trong_kg: int, the_tich_m3: Decimal) -> Decimal:
    """max(Σ kg / tải trọng, Σ m³ / thể tích) (mục 2.1)."""
    return round(max(kg / tai_trong_kg, m3 / the_tich_m3), 4)


def lai_du_kien(cuoc: list[int], dinh_muc: int, luong: int) -> int:
    """BR-52: Σ cước đơn hiệu lực − định mức (dầu + cầu đường + bốc xếp) − lương khoán."""
    return sum(cuoc) - dinh_muc - luong
