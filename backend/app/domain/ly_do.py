"""Danh mục lý do lấy / giao không được (BR-42), mỗi lý do có phía để BR-37 đếm (story UC-19, quyết định 2).

Migration `uc19_nap_danh_muc_ly_do` ghi cứng cùng danh sách này; test so khớp hai nơi.
"""

LY_DO: tuple[tuple[str, str, str], ...] = (  # (tên, áp dụng, phía)
    ("Hàng chưa chuẩn bị xong", "LAY", "KHACH"),
    ("Không liên lạc được người gửi", "LAY", "KHACH"),
    ("Sai địa chỉ lấy hàng", "LAY", "KHACH"),
    ("Hàng khác mô tả (quá khổ, quá nặng)", "LAY", "KHACH"),
    ("Lý do khác", "LAY", "KHACH"),
    ("Xe hỏng / sự cố trên đường", "LAY", "SU_CO_XE"),
    ("Người nhận vắng", "GIAO", "KHACH"),
    ("Người nhận từ chối nhận", "GIAO", "KHACH"),
    ("Sai địa chỉ giao", "GIAO", "KHACH"),
    ("Lý do khác", "GIAO", "KHACH"),
    ("Hàng hư hỏng", "GIAO", "SU_CO_XE"),  # lỗi bên vận chuyển, không tính ngưỡng thất bại của khách
    ("Xe hỏng / sự cố trên đường", "GIAO", "SU_CO_XE"),
)
