"""Vận hành: đơn, chuyến, ghép, lượt quét, sự cố, tệp (so-do.md mục 5, 6)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, luc_tao
from app.models.danh_muc import ToaDo

SoKg = Numeric(10, 2)


class DonHang(Base):
    __tablename__ = "don_hang"

    id: Mapped[int] = mapped_column(primary_key=True)
    ma_don: Mapped[str] = mapped_column(String(20), unique=True)  # in QR
    khach_hang_id: Mapped[int] = mapped_column(ForeignKey("khach_hang.id"))
    mo_ta: Mapped[str | None] = mapped_column(String(300))
    kg: Mapped[Decimal] = mapped_column(SoKg)
    m3: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    so_kien: Mapped[int]

    nut_lay_id: Mapped[int] = mapped_column(ForeignKey("nut.id"))
    dia_chi_lay: Mapped[str] = mapped_column(String(300))
    lat_lay: Mapped[Decimal | None] = mapped_column(ToaDo)
    lng_lay: Mapped[Decimal | None] = mapped_column(ToaDo)
    nguoi_lien_he_lay: Mapped[str | None] = mapped_column(String(100))
    sdt_lay: Mapped[str] = mapped_column(String(15))
    lay_tu: Mapped[datetime | None]  # null = cả ngày (BR-05)
    lay_den: Mapped[datetime | None]

    nut_giao_id: Mapped[int] = mapped_column(ForeignKey("nut.id"))
    dia_chi_giao: Mapped[str] = mapped_column(String(300))
    lat_giao: Mapped[Decimal | None] = mapped_column(ToaDo)
    lng_giao: Mapped[Decimal | None] = mapped_column(ToaDo)
    nguoi_nhan: Mapped[str] = mapped_column(String(100))
    sdt_nhan: Mapped[str] = mapped_column(String(15))
    han_giao: Mapped[datetime]

    # Nơi giữ hàng khi ghép lại đơn đã lấy (BR-69)
    nut_giu_id: Mapped[int | None] = mapped_column(ForeignKey("nut.id"))
    dia_chi_giu: Mapped[str | None] = mapped_column(String(300))
    lat_giu: Mapped[Decimal | None] = mapped_column(ToaDo)
    lng_giu: Mapped[Decimal | None] = mapped_column(ToaDo)

    # Bản sao giá chốt lúc tạo đơn (BR-32)
    don_gia_chot: Mapped[int]
    cuoc_toi_thieu_chot: Mapped[int]
    he_so_quy_doi_chot: Mapped[int]
    lam_tron_chot: Mapped[int]
    kl_tinh_cuoc: Mapped[Decimal] = mapped_column(SoKg)
    cuoc_tinh: Mapped[int]

    trang_thai: Mapped[str] = mapped_column(String(20), default="CHO_GHEP")  # ST-O
    so_lan_giao_that_bai: Mapped[int] = mapped_column(default=0)  # BR-37
    tao_luc: Mapped[datetime] = luc_tao()


class Chuyen(Base):
    __tablename__ = "chuyen"

    id: Mapped[int] = mapped_column(primary_key=True)
    ma_chuyen: Mapped[str] = mapped_column(String(20), unique=True)
    tuyen_id: Mapped[int] = mapped_column(ForeignKey("tuyen.id"))
    xe_id: Mapped[int] = mapped_column(ForeignKey("xe.id"))  # BR-22: bắt buộc ngay khi lập
    tai_xe_id: Mapped[int] = mapped_column(ForeignKey("tai_xe.id"))
    khoi_hanh_du_kien: Mapped[datetime]
    ket_thuc_du_kien: Mapped[datetime]  # BR-64
    khoi_hanh_thuc_te: Mapped[datetime | None]
    ket_thuc_thuc_te: Mapped[datetime | None]
    km_bat_dau: Mapped[int | None]  # BR-70
    km_ket_thuc: Mapped[int | None]
    # Định mức, lương chép từ tuyến lúc chốt (BR-71)
    dm_dau_chot: Mapped[int | None]
    dm_cau_duong_chot: Mapped[int | None]
    dm_boc_xep_chot: Mapped[int | None]
    luong_tai_xe_chot: Mapped[int | None]
    chay_rong: Mapped[bool] = mapped_column(default=False)  # BR-23
    ket_thuc_bat_thuong: Mapped[bool] = mapped_column(default=False)  # BR-68
    ly_do_ket_thuc: Mapped[str | None] = mapped_column(String(300))
    dieu_phoi_id: Mapped[int] = mapped_column(ForeignKey("nguoi_dung.id"))
    trang_thai: Mapped[str] = mapped_column(String(20), default="LAP")  # ST-T
    tao_luc: Mapped[datetime] = luc_tao()


class Ghep(Base):
    __tablename__ = "ghep"
    # BR-07: mỗi đơn tối đa một bản ghi ghép hiệu lực, chặn ngay ở CSDL
    __table_args__ = (
        Index(
            "uq_ghep_don_hieu_luc",
            "don_hang_id",
            unique=True,
            postgresql_where=text("hieu_luc"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    chuyen_id: Mapped[int] = mapped_column(ForeignKey("chuyen.id"))
    don_hang_id: Mapped[int] = mapped_column(ForeignKey("don_hang.id"))
    hieu_luc: Mapped[bool] = mapped_column(default=True)
    ket_qua: Mapped[str | None] = mapped_column(String(20))  # DA_GIAO|THAT_BAI
    giao_tre: Mapped[bool] = mapped_column(default=False)  # BR-72
    eta_lay_ke_hoach: Mapped[datetime | None]  # BR-71, lưu lúc chốt
    eta_giao_ke_hoach: Mapped[datetime | None]
    tao_luc: Mapped[datetime] = luc_tao()


class LuotQuet(Base):
    __tablename__ = "luot_quet"

    id: Mapped[int] = mapped_column(primary_key=True)
    ghep_id: Mapped[int] = mapped_column(ForeignKey("ghep.id"))
    tai_xe_id: Mapped[int] = mapped_column(ForeignKey("tai_xe.id"))
    loai: Mapped[str] = mapped_column(String(20))  # LAY|KHONG_LAY|GIAO|GIAO_THAT_BAI
    thoi_gian: Mapped[datetime] = luc_tao()  # giờ máy chủ, không nhận từ client
    lat: Mapped[Decimal | None] = mapped_column(ToaDo)
    lng: Mapped[Decimal | None] = mapped_column(ToaDo)
    do_chinh_xac_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 1))
    thieu_gps: Mapped[bool] = mapped_column(default=False)  # BR-43
    ly_do_id: Mapped[int | None] = mapped_column(ForeignKey("ly_do.id"))
    ten_nguoi_nhan: Mapped[str | None] = mapped_column(String(100))


class SuCo(Base):
    __tablename__ = "su_co"

    id: Mapped[int] = mapped_column(primary_key=True)
    chuyen_id: Mapped[int] = mapped_column(ForeignKey("chuyen.id"))
    tai_xe_id: Mapped[int] = mapped_column(ForeignKey("tai_xe.id"))
    loai: Mapped[str] = mapped_column(String(50))
    ghi_chu: Mapped[str | None] = mapped_column(String(500))
    trang_thai: Mapped[str] = mapped_column(String(10), default="MO")  # MO|DONG
    cach_xu_ly: Mapped[str | None] = mapped_column(String(500))
    luc: Mapped[datetime] = luc_tao()


class Tep(Base):
    __tablename__ = "tep"
    # Đúng một trong bốn khóa ngoại có giá trị (so-do.md mục 6)
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(luot_quet_id, chi_phi_id, su_co_id, chuyen_id) = 1",
            name="mot_chu_so_huu",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    luot_quet_id: Mapped[int | None] = mapped_column(ForeignKey("luot_quet.id"))
    chi_phi_id: Mapped[int | None] = mapped_column(ForeignKey("chi_phi.id"))
    su_co_id: Mapped[int | None] = mapped_column(ForeignKey("su_co.id"))
    chuyen_id: Mapped[int | None] = mapped_column(ForeignKey("chuyen.id"))  # ảnh đồng hồ km
    loai: Mapped[str] = mapped_column(String(20))  # ANH|CHU_KY|ANH_KM_BAT_DAU|ANH_KM_KET_THUC
    duong_dan: Mapped[str] = mapped_column(String(300))  # tên do server sinh
    kich_thuoc: Mapped[int]
    tao_luc: Mapped[datetime] = luc_tao()
