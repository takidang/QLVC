"""Quy tắc tuyến (nghiep-vu.md mục 2, BR-20, BR-66; quyết định UC-05). Hàm thuần, test không cần CSDL."""

from dataclasses import dataclass

from app.loi import LoiNghiepVu


@dataclass(frozen=True)
class NutTuyen:
    nut_id: int
    phut_tu_diem_dau: int
    km_tu_diem_dau: int
    la_diem_nghi: bool = False


def kiem_cau_truc_tuyen(nut: list[NutTuyen]) -> None:
    """Quyết định UC-05 số 3: ≥ 1 nút; nút đầu 0 phút 0 km; phút tăng hẳn; km không giảm; không lặp nút."""
    loi = []
    if not nut:
        loi.append("Tuyến phải có ít nhất 1 nút")
    else:
        if nut[0].phut_tu_diem_dau != 0 or nut[0].km_tu_diem_dau != 0:
            loi.append("Nút đầu tuyến phải có phút và km bằng 0")
        for i, (truoc, sau) in enumerate(zip(nut, nut[1:], strict=False), start=2):
            if sau.phut_tu_diem_dau <= truoc.phut_tu_diem_dau:
                loi.append(f"Nút thứ {i}: phút từ điểm đầu phải lớn hơn nút trước")
            if sau.km_tu_diem_dau < truoc.km_tu_diem_dau:
                loi.append(f"Nút thứ {i}: km từ điểm đầu không được nhỏ hơn nút trước")
        if len({n.nut_id for n in nut}) != len(nut):
            loi.append("Một nút không được xuất hiện hai lần trong tuyến")
    if loi:
        raise LoiNghiepVu("TUYEN_SAI", "Tuyến không hợp lệ", chi_tiet=[{"thong_diep": x} for x in loi])


def kiem_br66_thoi_gian_tuyen(nut: list[NutTuyen], gio_lai_ngay: int) -> None:
    """BR-66: thời gian chạy (phút nút cuối) ≤ giới hạn giờ lái một ngày (CFG-07, mặc định 10 giờ)."""
    phut = nut[-1].phut_tu_diem_dau
    if phut > gio_lai_ngay * 60:
        raise LoiNghiepVu(
            "BR-66", f"Tuyến chạy {phut} phút, vượt {gio_lai_ngay} giờ lái một ngày (một tài xế không chạy hết)"
        )


def canh_bao_br20(nut: list[NutTuyen], ten: dict[int, str], gio_lai_lien_tuc: int) -> list[str]:
    """BR-20: khoảng giữa hai điểm nghỉ liên tiếp (nút đầu, nút cuối tính là điểm nghỉ) > giờ lái liên tục."""
    diem_nghi = [n for i, n in enumerate(nut) if n.la_diem_nghi or i in (0, len(nut) - 1)]
    gioi_han = gio_lai_lien_tuc * 60
    return [
        f"Từ {ten.get(a.nut_id, a.nut_id)} đến {ten.get(b.nut_id, b.nut_id)} chạy "
        f"{b.phut_tu_diem_dau - a.phut_tu_diem_dau} phút không có điểm nghỉ (quá {gio_lai_lien_tuc} giờ)"
        for a, b in zip(diem_nghi, diem_nghi[1:], strict=False)
        if b.phut_tu_diem_dau - a.phut_tu_diem_dau > gioi_han
    ]
