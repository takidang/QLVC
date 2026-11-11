"""Nạp dữ liệu demo tính theo ngày chạy lệnh (story DEMO): python -m seed.demo [--ngay-moi]

Mọi thao tác đi qua API thật (đăng nhập đúng vai trò, đúng kiểm tra quy tắc); chỉ "bây giờ" được đặt lùi
bằng đồng hồ giả (`seed/dong_ho.py`) để có chuyến đã chạy, đã quyết toán. Không xóa dữ liệu nào.

- CSDL chưa có chuyến: tạo danh mục + 7 ngày trước + hôm nay.
- `--ngay-moi`: chỉ thêm chuyến hôm nay trên danh mục đã có (sáng ngày demo). Hôm nay đã có chuyến thì dừng.
"""

import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.db import get_engine
from app.main import app
from app.models import Chuyen, SuCo
from app.tai_khoan_demo import MAT_KHAU_DEV, tao_tai_khoan_demo
from app.thoi_gian import GIO_VN
from seed import dong_ho

JPG = b"\xff\xd8\xff\xe0" + b"0" * 600  # ảnh mẫu tối thiểu (máy chủ chỉ kiểm byte đầu, kích thước)
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 300
SO_NGAY_TRUOC = 7
GIO_SOM, GIO_MUON = 7, 18  # hôm nay có chuyến từ T−5h đến T+5h, phải nằm trong một ngày

# Tên, tỉnh, tọa độ (trung tâm tỉnh, gần đúng)
NUT = [
    ("TP.HCM", "TP.HCM", "10.776900", "106.700900"),
    ("Long An", "Long An", "10.535900", "106.413700"),
    ("Tiền Giang", "Tiền Giang", "10.360000", "106.360000"),
    ("Vĩnh Long", "Vĩnh Long", "10.253700", "105.972200"),
    ("Cần Thơ", "Cần Thơ", "10.045200", "105.746900"),
    ("Bình Dương", "Bình Dương", "10.980400", "106.651900"),
    ("Đồng Nai", "Đồng Nai", "10.957400", "106.842700"),
]
# Mã, tên, [(nút, phút, km)], định mức dầu, cầu đường, bốc xếp, lương
TUYEN = [
    (
        "T01",
        "TP.HCM – Cần Thơ",
        [
            ("TP.HCM", 0, 0),
            ("Long An", 60, 47),
            ("Tiền Giang", 120, 70),
            ("Vĩnh Long", 210, 135),
            ("Cần Thơ", 270, 170),
        ],
        900000,
        250000,
        300000,
        700000,
    ),
    (
        "T02",
        "TP.HCM – Tiền Giang",
        [("TP.HCM", 0, 0), ("Long An", 60, 47), ("Tiền Giang", 120, 70)],
        450000,
        120000,
        200000,
        400000,
    ),
    (
        "T03",
        "TP.HCM – Đồng Nai",
        [("TP.HCM", 0, 0), ("Bình Dương", 50, 30), ("Đồng Nai", 110, 60)],
        400000,
        100000,
        200000,
        400000,
    ),
]
DON_GIA = {"Long An": 600, "Tiền Giang": 800, "Vĩnh Long": 1100, "Cần Thơ": 1300, "Bình Dương": 500, "Đồng Nai": 700}
XE = [
    ("51C-201.11", 5000),
    ("51C-202.22", 5000),
    ("51C-203.33", 8000),
    ("51C-204.44", 8000),
    ("51D-305.55", 3500),
    ("51D-306.66", 3500),
    ("51D-307.77", 5000),
]
TAI_XE = [
    ("taixe", None),
    ("taixe01", "Nguyễn Văn An"),
    ("taixe02", "Trần Minh Bình"),
    ("taixe03", "Lê Quốc Dũng"),
    ("taixe04", "Phạm Thị Hoa"),
    ("taixe05", "Đặng Hữu Nam"),
]
KHACH = [
    ("Cty TNHH Gia Dụng Phương Nam", "0901116789"),
    ("Cty CP Nông Sản Miền Tây", "0902227890"),
    ("Cửa hàng Điện máy Thành Đạt", "0903338901"),
    ("Cty Dược phẩm An Khang", "0904449012"),
    ("Cty May mặc Sài Gòn Xanh", "0905550123"),
    ("HTX Trái cây Cái Bè", "0906661234"),
]


class LoiNap(Exception):
    pass


def _kiem(r, *ma):
    if r.status_code not in (ma or (200, 201, 204)):
        raise LoiNap(f"{r.request.method} {r.request.url.path} → {r.status_code}: {r.text[:300]}")
    return r.json() if r.content else None


def _may(ten: str) -> TestClient:
    c = TestClient(app, base_url="https://testserver")
    _kiem(c.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": MAT_KHAU_DEV}))
    return c


def luc(ngay: date, phut: int) -> datetime:
    return datetime.combine(ngay, time(), GIO_VN) + timedelta(minutes=phut)


@dataclass
class DanhMuc:
    nut: dict[str, int]
    tuyen: dict[str, dict]
    xe: list[dict]
    tai_xe: list[dict]
    khach: list[int]
    ly_do: dict[str, int]


# ---------- Danh mục ----------


def tao_danh_muc(dp: TestClient, ql: TestClient, hom_nay: date) -> None:
    for ten, tinh, lat, lng in NUT:
        _kiem(dp.post("/api/nut", json={"ten": ten, "tinh": tinh, "loai": "TINH", "lat": lat, "lng": lng}))
    nut = {n["ten"]: n["id"] for n in _kiem(dp.get("/api/nut?so_dong=100"))["du_lieu"]}
    da_co_gia: set[tuple[str, str]] = set()
    for ma, ten, diem, dau, cau, boc, luong in TUYEN:
        _kiem(
            dp.post(
                "/api/tuyen",
                json={
                    "ma": ma,
                    "ten": ten,
                    "dm_dau": dau,
                    "dm_cau_duong": cau,
                    "dm_boc_xep": boc,
                    "dm_luong_tai_xe": luong,
                    "nut": [
                        {"nut_id": nut[n], "phut_tu_diem_dau": p, "km_tu_diem_dau": k, "la_diem_nghi": False}
                        for n, p, k in diem
                    ],
                },
            )
        )
        # Giá cho mọi cặp lấy trước → giao sau trên tuyến (BR-48), hiệu lực từ 60 ngày trước
        for i, (lay, _, _) in enumerate(diem):
            for giao, _, _ in diem[i + 1 :]:
                if (lay, giao) in da_co_gia:
                    continue
                da_co_gia.add((lay, giao))
                vao = {
                    "tinh_lay": lay,
                    "tinh_giao": giao,
                    "don_gia_kg": DON_GIA[giao] - (DON_GIA.get(lay, 0) // 2),
                    "cuoc_toi_thieu": 150000,
                    "hieu_luc_tu": (hom_nay - timedelta(days=60)).isoformat(),
                }
                _kiem(ql.post("/api/bang-gia", json=vao))
    han = (hom_nay + timedelta(days=400)).isoformat()
    for bien_so, tai in XE:
        _kiem(
            dp.post(
                "/api/xe",
                json={
                    "bien_so": bien_so,
                    "tai_trong_kg": tai,
                    "the_tich_m3": str(tai // 250),
                    "ktt_toan_bo_kg": tai * 2,
                    "han_dang_kiem": han,
                    "han_bao_hiem": han,
                    "dinh_muc_lit_100km": "18",
                    "km_dong_ho": 100000,
                },
            )
        )
    for i, (ten, ho_ten) in enumerate(TAI_XE):
        if ho_ten:
            _kiem(
                dp.post(
                    "/api/tai-xe",
                    json={
                        "ten_dang_nhap": ten,
                        "ho_ten": ho_ten,
                        "mat_khau": MAT_KHAU_DEV,
                        "so_gplx": f"79{i:010d}",
                        "hang_gplx": "C",
                        "han_gplx": han,
                        "sdt": f"09120000{i:02d}",
                    },
                )
            )
    for ten, sdt in KHACH:
        _kiem(dp.post("/api/khach-hang", json={"ten": ten, "sdt": sdt, "dia_chi": f"{ten}, TP.HCM"}))


def doc_danh_muc(dp: TestClient) -> DanhMuc:
    nut = {n["ten"]: n["id"] for n in _kiem(dp.get("/api/nut?so_dong=100"))["du_lieu"]}
    tuyen = {t["ma"]: t for t in _kiem(dp.get("/api/tuyen?so_dong=100"))["du_lieu"]}
    xe = [x for x in _kiem(dp.get("/api/xe?so_dong=100"))["du_lieu"] if x["bien_so"] in dict(XE)]
    tx = {t["ten_dang_nhap"]: t for t in _kiem(dp.get("/api/tai-xe?so_dong=100"))["du_lieu"]}
    sdt_khach = {sdt for _, sdt in KHACH}
    khach = [k["id"] for k in _kiem(dp.get("/api/khach-hang?so_dong=100"))["du_lieu"] if k["sdt"] in sdt_khach]
    ly_do = {}
    for ld in _kiem(dp.get("/api/danh-muc/ly-do")):
        ly_do.setdefault(f"{ld['ap_dung']}_{ld['phia']}", ld["id"])
    thieu = [m for m in ("T01", "T02", "T03") if m not in tuyen] + [t for t, _ in TAI_XE if t not in tx]
    if thieu or len(xe) < len(XE) or len(khach) < len(KHACH):
        raise LoiNap(f"Danh mục demo chưa đủ ({', '.join(thieu) or 'xe / khách'}): chạy lệnh không có --ngay-moi")
    xe.sort(key=lambda x: x["bien_so"])
    return DanhMuc(nut, tuyen, xe, [tx[t] for t, _ in TAI_XE], khach, ly_do)


# ---------- Một chuyến ----------


@dataclass
class KichBan:
    """Đơn: (lấy, giao, kg, kết quả) với kết quả GIAO | GIAO_THAT_BAI | KHONG_LAY.

    Chuyến `DANG_CHAY` chỉ quét các điểm có giờ trước lúc chạy lệnh; điểm sau đó còn chờ."""

    tuyen: str
    xe: int
    tai_xe: int
    phut: int  # khởi hành, phút từ 0 giờ của ngày
    don: list[tuple[str, str, int, str]]
    den: str = "HOAN_THANH"  # LAP | DA_CHOT | DANG_CHAY | HOAN_THANH | DA_QUYET_TOAN | HUY
    tre: int = 0  # phút trễ mỗi điểm cộng dồn
    chi_phi: bool = True


def _tam_ung(t: dict) -> int:
    """80% định mức tuyến, làm tròn chục nghìn (không vượt định mức, BR-53)."""
    return (t["dm_dau"] + t["dm_cau_duong"] + t["dm_boc_xep"]) * 8 // 10 // 10000 * 10000


def _ten_nhan(i: int) -> str:
    return ["Chị Lan", "Anh Tuấn", "Cô Mai", "Anh Phát", "Chị Hằng"][i % 5]


def chay(m: dict, dm: DanhMuc, ngay: date, kb: KichBan, so: list[int]) -> int:
    dp, kt = m["dp"], m["kt"]
    tx_ten = TAI_XE[kb.tai_xe][0]
    tx = m.setdefault(tx_ten, _may(tx_ten))
    kh = luc(ngay, kb.phut)
    xe, tai_xe = dm.xe[kb.xe], dm.tai_xe[kb.tai_xe]

    # Hôm trước: tạo đơn; trước giờ đi 3 tiếng: lập, ghép, chốt
    dong_ho.dat(kh - timedelta(hours=20))
    don_ids = []
    for lay, giao, kg, _ in kb.don:
        so[0] += 1
        d = _kiem(
            dp.post(
                "/api/don",
                json={
                    "khach_hang_id": dm.khach[so[0] % len(dm.khach)],
                    "mo_ta": "Hàng demo",
                    "kg": str(kg),
                    "m3": str(max(1, kg // 300)),
                    "so_kien": max(1, kg // 100),
                    "nut_lay_id": dm.nut[lay],
                    "dia_chi_lay": f"Kho {lay}",
                    "sdt_lay": f"0908{so[0]:06d}",
                    "nut_giao_id": dm.nut[giao],
                    "dia_chi_giao": f"{so[0]} Đường số {so[0] % 9 + 1}, {giao}",
                    "nguoi_nhan": _ten_nhan(so[0]),
                    "sdt_nhan": f"0938{so[0]:06d}",
                    "han_giao": (kh + timedelta(hours=10)).isoformat(),
                },
            )
        )
        don_ids.append(d["id"])
    dong_ho.dat(kh - timedelta(hours=3))
    c = _kiem(
        dp.post(
            "/api/chuyen",
            json={
                "tuyen_id": dm.tuyen[kb.tuyen]["id"],
                "xe_id": xe["id"],
                "tai_xe_id": tai_xe["id"],
                "khoi_hanh_du_kien": kh.isoformat(),
            },
        )
    )
    cid = c["id"]
    if don_ids:
        _kiem(dp.post(f"/api/chuyen/{cid}/ghep", json={"don_ids": don_ids}))
    if kb.den == "HUY":
        _kiem(dp.post(f"/api/chuyen/{cid}/huy", json={"ly_do": "Khách dời lịch giao, gom sang chuyến sau"}))
        return cid
    if kb.den == "LAP":
        return cid
    _kiem(dp.post(f"/api/chuyen/{cid}/chot", json={"xac_nhan_chay_rong": True, "xac_nhan_lai_am": True}))
    _kiem(
        kt.post(f"/api/chuyen/{cid}/tam-ung", json={"so_tien": _tam_ung(dm.tuyen[kb.tuyen]), "hinh_thuc": "TIEN_MAT"})
    )
    if kb.den == "DA_CHOT":
        return cid

    # Chạy: bắt đầu, quét theo lịch trình kế hoạch, cộng trễ dồn
    km0 = next(x for x in _kiem(dp.get("/api/xe?so_dong=100"))["du_lieu"] if x["id"] == xe["id"])["km_dong_ho"]
    dong_ho.dat(kh + timedelta(minutes=3))
    _kiem(
        tx.post(
            f"/api/toi/chuyen/{cid}/bat-dau",
            data={"km_bat_dau": km0},
            files={"anh_dong_ho": ("km.jpg", JPG, "image/jpeg")},
        )
    )
    ket = {d: kb.don[i] for i, d in enumerate(don_ids)}
    lt = _kiem(dp.get(f"/api/chuyen/{cid}"))["lich_trinh"]
    toa_do = {ten: (lat, lng) for ten, _, lat, lng in NUT}
    bo = set()
    luc_cuoi = kh
    for i, p in enumerate(lt):
        kq = ket[p["don_id"]][3]
        if p["don_id"] in bo:
            continue
        luc_quet = datetime.fromisoformat(p["eta_ke_hoach"]) + timedelta(minutes=kb.tre * (i + 1) // len(lt) + 2)
        if luc_quet > m["that"]:
            if kb.den == "DANG_CHAY":
                break
            raise LoiNap(f"Kịch bản sai: chuyến {c['ma_chuyen']} quét lúc {luc_quet:%H:%M}, sau giờ chạy lệnh")
        luc_cuoi = luc_quet
        dong_ho.dat(luc_cuoi)
        lat, lng = toa_do[p["nut"]]
        data = {"ma_don": p["ma_don"], "lat": lat, "lng": lng, "do_chinh_xac_m": "15"}
        files = [("anh", ("a.jpg", JPG, "image/jpeg"))]
        if p["viec"] == "LAY":
            if kq == "KHONG_LAY":
                data |= {"loai": "KHONG_LAY", "ly_do_id": dm.ly_do["LAY_KHACH"]}
                bo.add(p["don_id"])
            else:
                data["loai"] = "LAY"
        elif kq == "GIAO_THAT_BAI":
            data |= {"loai": "GIAO_THAT_BAI", "ly_do_id": dm.ly_do["GIAO_KHACH"]}
        else:
            data |= {"loai": "GIAO", "ten_nguoi_nhan": _ten_nhan(p["don_id"])}
            files.append(("chu_ky", ("ky.png", PNG, "image/png")))
        _kiem(tx.post("/api/toi/quet", data=data, files=files))
        if kb.chi_phi and i == len(lt) // 2:
            _kiem(
                tx.post(
                    f"/api/toi/chuyen/{cid}/chi-phi",
                    data={"loai": "DAU", "so_tien": "880000", "so_lit": "40", "ghi_chu": "Đổ dầu trạm Trung Lương"},
                    files=files[:1],
                )
            )
    if kb.den == "DANG_CHAY":
        return cid

    km = km0 + dm.tuyen[kb.tuyen]["nut"][-1]["km_tu_diem_dau"] + 4
    dong_ho.dat(luc_cuoi + timedelta(minutes=20))
    if kb.chi_phi:
        _kiem(
            tx.post(
                f"/api/toi/chuyen/{cid}/chi-phi",
                data={"loai": "CAU_DUONG", "so_tien": "235000", "ghi_chu": "Trạm BOT"},
                files=[("anh", ("a.jpg", JPG, "image/jpeg"))],
            )
        )
    _kiem(
        tx.post(
            f"/api/toi/chuyen/{cid}/ket-thuc",
            data={"km_ket_thuc": km},
            files={"anh_dong_ho": ("km.jpg", JPG, "image/jpeg")},
        )
    )
    if kb.den == "HOAN_THANH":
        return cid

    # Kế toán duyệt chi phí rồi khóa sổ (UC-24)
    dong_ho.dat(luc_cuoi + timedelta(hours=2))
    bang = _kiem(kt.get(f"/api/chuyen/{cid}/quyet-toan"))
    for k in bang["khoan"]:
        so_duyet = k["so_tien_khai"] - (30000 if k["loai"] == "DAU" else 0)
        ly_do = "Hóa đơn dầu ghi thiếu 30.000 đ" if so_duyet != k["so_tien_khai"] else None
        _kiem(kt.post(f"/api/chi-phi/{k['id']}/duyet", json={"so_tien_duyet": so_duyet, "ly_do": ly_do}))
    bang = _kiem(kt.get(f"/api/chuyen/{cid}/quyet-toan"))
    vao = {"xu_ly_chenh_lech": bang["xu_ly_goi_y"]}
    if bang["chenh_lech_tam_ung"]:
        vao |= {"hinh_thuc": "TIEN_MAT", "luc_xu_ly": dong_ho.bay_gio().isoformat()}
    _kiem(kt.post(f"/api/chuyen/{cid}/quyet-toan", json=vao))
    return cid


# ---------- Lịch các ngày ----------


def ngay_truoc(m: dict, dm: DanhMuc, ngay: date, i: int, so: list[int]) -> None:
    """Hai chuyến đã quyết toán mỗi ngày; xe, tài xế xoay vòng."""
    t01 = [
        ("TP.HCM", "Cần Thơ", 1800, "GIAO"),
        ("TP.HCM", "Vĩnh Long", 1200, "GIAO"),
        ("Long An", "Cần Thơ", 900, "GIAO"),
    ]
    t03 = [("TP.HCM", "Đồng Nai", 1500, "GIAO"), ("TP.HCM", "Bình Dương", 800, "GIAO")]
    chay(m, dm, ngay, KichBan("T01", i % 2, i % 6, 6 * 60, t01, "DA_QUYET_TOAN", tre=i * 3), so)
    chay(m, dm, ngay, KichBan("T03", 2 + i % 2, (i + 3) % 6, 7 * 60, t03, "DA_QUYET_TOAN"), so)


def hom_nay(m: dict, dm: DanhMuc, ngay: date, t: int, so: list[int]) -> None:
    """Đủ trạng thái quanh giờ chạy lệnh `t` (phút từ 0 giờ): đang chạy trễ / có sự cố, vừa xong, sắp đi."""
    C = KichBan
    chay(
        m,
        dm,
        ngay,
        C(
            "T02",
            4,
            2,
            t - 300,
            [
                ("TP.HCM", "Tiền Giang", 900, "GIAO"),
                ("TP.HCM", "Long An", 700, "GIAO_THAT_BAI"),
                ("Long An", "Tiền Giang", 600, "KHONG_LAY"),
            ],
        ),
        so,
    )
    chay(
        m,
        dm,
        ngay,
        C(
            "T03",
            2,
            3,
            t - 240,
            [("TP.HCM", "Đồng Nai", 1600, "GIAO"), ("TP.HCM", "Bình Dương", 900, "GIAO")],
            "DA_QUYET_TOAN",
        ),
        so,
    )
    chay(
        m,
        dm,
        ngay,
        C(
            "T01",
            0,
            0,
            t - 150,
            [
                ("TP.HCM", "Cần Thơ", 2000, "GIAO"),
                ("TP.HCM", "Vĩnh Long", 1100, "GIAO"),
                ("Long An", "Cần Thơ", 800, "GIAO"),
            ],
            "DANG_CHAY",
            tre=40,
        ),
        so,
    )
    # Đang chạy, đã lấy hàng, tài xế vừa báo sự cố (giờ máy chủ thật)
    c = chay(
        m,
        dm,
        ngay,
        C(
            "T02",
            5,
            4,
            t - 70,
            [("TP.HCM", "Tiền Giang", 1200, "GIAO"), ("TP.HCM", "Long An", 500, "GIAO")],
            "DANG_CHAY",
            chi_phi=False,
        ),
        so,
    )
    _bao_su_co(m, c, luc(ngay, t - 10))
    chay(
        m,
        dm,
        ngay,
        C(
            "T01",
            1,
            1,
            t + 60,
            [("TP.HCM", "Cần Thơ", 1500, "GIAO"), ("Tiền Giang", "Cần Thơ", 1000, "GIAO")],
            "DA_CHOT",
        ),
        so,
    )
    chay(m, dm, ngay, C("T03", 3, 5, t + 120, [("TP.HCM", "Đồng Nai", 700, "GIAO")], "LAP"), so)
    chay(m, dm, ngay, C("T02", 6, 3, t + 180, [], "HUY"), so)
    # Đơn còn chờ ghép cho Điều phối thử ghép
    dong_ho.dat(luc(ngay, t - 30))
    for i, (lay, giao, kg) in enumerate(
        [
            ("TP.HCM", "Cần Thơ", 600),
            ("TP.HCM", "Tiền Giang", 400),
            ("TP.HCM", "Bình Dương", 300),
            ("Long An", "Cần Thơ", 500),
        ]
    ):
        so[0] += 1
        _kiem(
            m["dp"].post(
                "/api/don",
                json={
                    "khach_hang_id": dm.khach[i],
                    "kg": str(kg),
                    "m3": "2",
                    "so_kien": 4,
                    "nut_lay_id": dm.nut[lay],
                    "dia_chi_lay": f"Kho {lay}",
                    "sdt_lay": f"0908{so[0]:06d}",
                    "nut_giao_id": dm.nut[giao],
                    "dia_chi_giao": f"{so[0]} Lê Lợi, {giao}",
                    "nguoi_nhan": _ten_nhan(i),
                    "sdt_nhan": f"0938{so[0]:06d}",
                    "han_giao": luc(ngay + timedelta(days=1), 18 * 60).isoformat(),
                    "mo_ta": "Hàng chờ ghép",
                },
            )
        )


def _bao_su_co(m: dict, chuyen_id: int, luc_bao: datetime) -> None:
    # API báo sự cố của tài xế (UC-33) chưa vào dev thì ghi thẳng một sự cố mở, như tài xế đã báo
    with sessionmaker(get_engine())() as db:
        c = db.get(Chuyen, chuyen_id)
        db.add(
            SuCo(
                chuyen_id=c.id,
                tai_xe_id=c.tai_xe_id,
                loai="HONG_XE",
                ghi_chu="Xe báo đèn nhiệt độ máy, đang tấp vào trạm dừng kiểm tra",
                luc=luc_bao,
            )
        )
        db.commit()


def danh_dau_da_thu(kt: TestClient, truoc: date) -> None:
    """Đơn giao trước ngày `truoc` coi như khách đã trả (để công nợ có cả đã thu, chưa thu)."""
    ds = _kiem(kt.get("/api/phai-thu?so_dong=100"))["du_lieu"]
    theo_khach: dict[int, list[int]] = {}
    for p in ds:
        if p["trang_thai_tt"] == "CHUA_THU" and (p["ngay_giao"] or "9") < truoc.isoformat():
            theo_khach.setdefault(p["khach_hang_id"], []).append(p["id"])
    for ids in theo_khach.values():  # mỗi lần chỉ một khách (BR-56)
        _kiem(kt.post("/api/phai-thu/da-thu", json={"phai_thu_ids": ids[:100], "ngay": truoc.isoformat()}))


# ---------- Lệnh ----------


def nap(ngay_moi: bool = False, bay_gio: datetime | None = None) -> str:
    bay_gio = (bay_gio or datetime.now(GIO_VN)).astimezone(GIO_VN)
    nay = bay_gio.date()
    t = bay_gio.hour * 60 + bay_gio.minute // 10 * 10
    if not GIO_SOM * 60 <= t <= GIO_MUON * 60:
        raise LoiNap(f"Chạy lệnh trong khoảng {GIO_SOM}:00–{GIO_MUON}:00 để chuyến hôm nay không vắt qua nửa đêm")
    with sessionmaker(get_engine())() as db:
        co_chuyen = db.scalar(select(func.count()).select_from(Chuyen))
        dau = datetime.combine(nay, time(), GIO_VN)
        hom_nay_co = db.scalar(
            select(func.count())
            .select_from(Chuyen)
            .where(Chuyen.khoi_hanh_du_kien >= dau, Chuyen.khoi_hanh_du_kien < dau + timedelta(days=1))
        )
        if co_chuyen and not ngay_moi:
            raise LoiNap("CSDL đã có chuyến, không nạp chồng. Sáng ngày demo dùng: python -m seed.demo --ngay-moi")
        if ngay_moi and hom_nay_co:
            raise LoiNap(f"Hôm nay ({nay:%d/%m}) đã có {hom_nay_co} chuyến, không thêm nữa")
        tao_tai_khoan_demo(db, MAT_KHAU_DEV)

    so = [int(bay_gio.timestamp()) % 9000 * 10]  # số trong SĐT mẫu, khác nhau giữa các lần chạy
    with dong_ho.gia():
        dong_ho.dat(bay_gio - timedelta(days=SO_NGAY_TRUOC + 2))
        m = {"dp": _may("dieuphoi"), "kt": _may("ketoan"), "that": bay_gio}
        if not ngay_moi:
            tao_danh_muc(m["dp"], _may("quanly"), nay)
        dm = doc_danh_muc(m["dp"])
        if not ngay_moi:
            for i in range(SO_NGAY_TRUOC, 0, -1):
                ngay_truoc(m, dm, nay - timedelta(days=i), i, so)
            dong_ho.dat(bay_gio - timedelta(hours=6))
            danh_dau_da_thu(m["kt"], nay - timedelta(days=3))
        hom_nay(m, dm, nay, t, so)
    return f"Đã nạp dữ liệu demo cho {nay:%d/%m/%Y}" + ("" if ngay_moi else f" và {SO_NGAY_TRUOC} ngày trước")


def main(argv: list[str]) -> int:
    try:
        print(nap(ngay_moi="--ngay-moi" in argv))
    except LoiNap as e:
        print(f"Không nạp: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
