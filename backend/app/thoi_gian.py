from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

# "Một ngày" của nghiệp vụ tính theo giờ Việt Nam, không theo giờ máy chủ (Render chạy UTC) – kien-truc.md mục 8
GIO_VN = ZoneInfo("Asia/Ho_Chi_Minh")


def bay_gio() -> datetime:
    return datetime.now(UTC)


def hom_nay_vn() -> date:
    return datetime.now(GIO_VN).date()
