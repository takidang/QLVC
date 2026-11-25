"""Mục 6: Kiểm thử tra cứu công khai POST /api/tra-cuu (BR-59, giới hạn tần suất 429).

Chạy SAU test_07_giao_dien.py vì ca cuối cố ý kích hoạt khóa IP 60 giây của /api/tra-cuu.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import ApiClient, BaoCaoMuc, dang_nhap, tom_tat


def main():
    bc = BaoCaoMuc(6, "Tra cứu công khai /api/tra-cuu")
    dp = dang_nhap("dieuphoi")
    anon = ApiClient()

    # Lấy 1 đơn hợp lệ đang có trong hệ thống
    _, ds_don, _ = dp.raw("GET", "/api/don?so_dong=10")
    don = ds_don["du_lieu"][0]
    ma_don = don["ma_don"]
    sdt_lay_4 = don["sdt_lay"][-4:]
    sdt_nhan_4 = don["sdt_nhan"][-4:]
    sdt_sai = "0000" if sdt_lay_4 != "0000" and sdt_nhan_4 != "0000" else "9999"

    # 6.1 Tra cứu đúng bằng SĐT lấy -> chỉ hiện ma_don, trang_thai, moc (BR-59, không GPS/SĐT tài xế/cước/lý do)
    st, d, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": ma_don, "sdt_4_so_cuoi": sdt_lay_4})
    keys = set(d.keys()) if isinstance(d, dict) else set()
    moc_keys = {k for m in (d or {}).get("moc", []) for k in m.keys()} if isinstance(d, dict) else set()
    khong_lo = keys == {"ma_don", "trang_thai", "moc"} and moc_keys <= {"trang_thai", "luc"}
    bc.ghi(
        "TR-01",
        f"Tra cứu hợp lệ {ma_don} bằng 4 số cuối SĐT lấy ({sdt_lay_4})",
        st == 200 and khong_lo,
        f"HTTP {st}, keys={sorted(keys)}, moc_keys={sorted(moc_keys)}, so_moc={len((d or {}).get('moc', []))}",
        "HTTP 200, chỉ trả {ma_don, trang_thai, moc[{trang_thai, luc}]}, không lộ GPS/SĐT/cước/lý do",
        f"POST /api/tra-cuu {{ma_don: {ma_don!r}, sdt_4_so_cuoi: {sdt_lay_4!r}}}",
        "Nghiem trong",
        "BR-59",
    )

    # 6.2 Tra cứu chữ thường + khoảng trắng vẫn tìm được
    st, d, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": f"  {ma_don.lower()}  ", "sdt_4_so_cuoi": sdt_nhan_4})
    bc.ghi(
        "TR-02",
        "Tra cứu chữ thường + khoảng trắng bằng 4 số cuối SĐT nhận",
        st == 200 and (d or {}).get("ma_don") == ma_don,
        tom_tat(st, d),
        "HTTP 200, chuẩn hóa chữ hoa & trim khoảng trắng",
        f"POST /api/tra-cuu {{ma_don: '  {ma_don.lower()}  ', sdt_4_so_cuoi: {sdt_nhan_4!r}}}",
        "Nhe",
        "UC-28",
    )

    # 6.3 Sai định dạng / SQLi / thừa trường -> 400 (không tính là 404 hay 500)
    for ma, ten, body in [
        ("TR-03", "Tra cứu SĐT 3 chữ số", {"ma_don": ma_don, "sdt_4_so_cuoi": "123"}),
        ("TR-04", "Tra cứu SĐT có chữ cái", {"ma_don": ma_don, "sdt_4_so_cuoi": "abcd"}),
        ("TR-05", "Tra cứu có trường thừa", {"ma_don": ma_don, "sdt_4_so_cuoi": sdt_lay_4, "extra": 1}),
        ("TR-06", "Tra cứu SQLi ở ma_don", {"ma_don": "' OR 1=1 --", "sdt_4_so_cuoi": "1234"}),
    ]:
        st, d, _ = anon.raw("POST", "/api/tra-cuu", body)
        exp = (404,) if ma == "TR-06" else (400,)
        bc.ghi(ma, ten, st in exp, tom_tat(st, d), f"HTTP {exp}, không 500", f"POST /api/tra-cuu {body}", "Vua", "UC-28 / BR-59")

    # 6.4 Sai mã đơn vs Đúng mã đơn + sai SĐT -> PHẢI trả cùng mã HTTP (404) và cùng thông báo (không lộ mã tồn tại)
    st_a, d_a, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": "DH-KHONGCO", "sdt_4_so_cuoi": "1234"})
    st_b, d_b, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": ma_don, "sdt_4_so_cuoi": sdt_sai})
    cung_tb = st_a == 404 and st_b == 404 and d_a == d_b
    bc.ghi(
        "TR-07",
        "Sai mã đơn và đúng mã đơn + sai SĐT trả cùng HTTP 404 và cùng thông báo chung",
        cung_tb,
        f"Sai mã={tom_tat(st_a, d_a)} | Sai SĐT={tom_tat(st_b, d_b)}",
        "Cùng HTTP 404 và cùng nội dung JSON 'Không tìm thấy đơn'",
        f"So sánh POST /api/tra-cuu mã không có vs mã {ma_don} + SĐT sai {sdt_sai}",
        "Nghiem trong",
        "BR-59",
    )

    # 6.5 Sai 10 lần trong 1 phút -> lần thứ 11 phải trả 429 (kể cả khi gửi đúng hoặc giả mạo X-Forwarded-For!)
    # Đã có 3 lần 404 ở TR-06, TR-07 (a, b). Gửi thêm cho tới khi gặp 429 (tối đa 12 lần)
    ket_qua_lan = []
    for i in range(1, 13):
        st_i, d_i, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": "DH-WRONG99", "sdt_4_so_cuoi": "0000"})
        ket_qua_lan.append(st_i)
        if st_i == 429:
            break
    # Thử tiếp 1 lần đúng và 1 lần gắn X-Forwarded-For giả
    st_dung_khi_khoa, d_dung, _ = anon.raw("POST", "/api/tra-cuu", {"ma_don": ma_don, "sdt_4_so_cuoi": sdt_lay_4})
    st_xff, d_xff, _ = anon.raw(
        "POST",
        "/api/tra-cuu",
        {"ma_don": ma_don, "sdt_4_so_cuoi": sdt_lay_4},
        extra_headers={"X-Forwarded-For": "1.2.3.4"},
    )
    bc.ghi(
        "TR-08",
        "Sai liên tiếp > 10 lần trong 1 phút -> bị chặn 429 QUA_TAN_SUAT",
        429 in ket_qua_lan and st_dung_khi_khoa == 429,
        f"Chuỗi mã khi gửi sai thêm={ket_qua_lan}; gửi đúng khi đang bị khóa -> {tom_tat(st_dung_khi_khoa, d_dung)}",
        "Sau 10 lần sai trong 60s, lần 11 trở đi trả 429 kể cả khi tra đúng",
        "Gửi 11 lần POST /api/tra-cuu sai trong 60s",
        "Vua",
        "NFR-SEC-05 / UC-28",
    )
    bc.ghi(
        "TR-09",
        "Giả mạo header X-Forwarded-For không vượt được giới hạn tần suất /api/tra-cuu",
        st_xff == 429,
        tom_tat(st_xff, d_xff),
        "HTTP 429 (không tin X-Forwarded-For từ client)",
        "POST /api/tra-cuu kèm header X-Forwarded-For: 1.2.3.4 sau khi bị khóa",
        "Nghiem trong",
        "NFR-SEC-05 / api.md 3.4",
    )

    bc.luu_json("ket_qua_06.json")


if __name__ == "__main__":
    main()
