"""Mục 4: Kiểm thử sai trạng thái (chuyển trạng thái / hành động không hợp lệ)."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import MIN_JPG, MIN_PNG, BaoCaoMuc, dang_nhap, iso_vn, now_vn, tom_tat


def main():
    bc = BaoCaoMuc(4, "Sai trạng thái (State Machine)")
    dp = dang_nhap("dieuphoi")
    kt = dang_nhap("ketoan")

    sfx = uuid.uuid4().hex[:5]
    han_ok = iso_vn(now_vn() + timedelta(days=3))

    # Tạo tài xế & xe riêng để chạy trọn vòng đời sạch: LAP -> DA_CHOT -> DANG_CHAY -> HOAN_THANH -> DA_QUYET_TOAN
    _, d_tx, _ = dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": f"txst_{sfx}",
            "ho_ten": f"Tài xế State {sfx}",
            "mat_khau": "demo12345",
            "so_gplx": f"STAT{sfx.upper()}01",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0966554433",
        },
    )
    tx_id = d_tx["id"]
    tx = dang_nhap(f"txst_{sfx}", "demo12345")

    _, d_xe, _ = dp.raw(
        "POST",
        "/api/xe",
        {
            "bien_so": f"51S-{sfx}",
            "tai_trong_kg": 5000,
            "the_tich_m3": "20.00",
            "ktt_toan_bo_kg": 9000,
            "han_dang_kiem": "2028-12-31",
            "han_bao_hiem": "2028-12-31",
            "dinh_muc_lit_100km": "15.00",
            "km_dong_ho": 20000,
        },
    )
    xe_id = d_xe["id"]

    def tao_don(tag: str) -> dict:
        st, d, _ = dp.raw(
            "POST",
            "/api/don",
            {
                "khach_hang_id": 1,
                "mo_ta": f"ST-{tag}-{sfx}",
                "kg": "100.00",
                "m3": "1.00",
                "so_kien": 1,
                "nut_lay_id": 5,
                "dia_chi_lay": f"10 Lay {tag} {sfx}",
                "sdt_lay": "0909444001",
                "nut_giao_id": 11,
                "dia_chi_giao": f"20 Giao {tag} {sfx}",
                "nguoi_nhan": "Nguoi Nhan",
                "sdt_nhan": "0909444002",
                "han_giao": han_ok,
            },
        )
        assert st == 201, f"Tao don fail: {st} {d}"
        return d

    don_chinh = tao_don("chinh")
    don_phu = tao_don("phu")
    don_tb_chua_lay = tao_don("tbchualay")
    don_tb_da_lay = tao_don("tbdalay")

    # Tạo chuyến ở trạng thái LAP
    st_c, d_c, _ = dp.raw(
        "POST",
        "/api/chuyen",
        {"tuyen_id": 5, "khoi_hanh_du_kien": iso_vn(now_vn() + timedelta(minutes=15)), "xe_id": xe_id, "tai_xe_id": tx_id},
    )
    assert st_c == 201
    cid = d_c["id"]

    # --- Trạng thái LAP ---
    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 100000, "hinh_thuc": "TIEN_MAT"})
    bc.ghi("ST-01", "Cấp tạm ứng khi chuyến đang LAP", st == 409 and (d or {}).get("ma") == "BR-53", tom_tat(st, d), "409 BR-53", f"kt POST /api/chuyen/{cid}/tam-ung (LAP)", "Vua", "BR-53")

    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/quyet-toan", {"xu_ly_chenh_lech": "KHONG_CHENH"})
    bc.ghi("ST-02", "Quyết toán khi chuyến đang LAP", st == 409 and (d or {}).get("ma") == "BR-55", tom_tat(st, d), "409 BR-55", f"kt POST /api/chuyen/{cid}/quyet-toan (LAP)", "Vua", "BR-55")

    # Ghép 3 đơn rồi chốt chuyến -> DA_CHOT
    dp.raw("POST", f"/api/chuyen/{cid}/ghep", {"don_ids": [don_chinh["id"], don_tb_chua_lay["id"], don_tb_da_lay["id"]]})
    st_chot, _, _ = dp.raw("POST", f"/api/chuyen/{cid}/chot", {"xac_nhan_lai_am": True})
    assert st_chot == 200

    # --- Trạng thái DA_CHOT ---
    st, d, _ = dp.raw("POST", f"/api/chuyen/{cid}/ghep", {"don_ids": [don_phu["id"]]})
    bc.ghi("ST-03", "Ghép đơn vào chuyến đã chốt (DA_CHOT)", st == 409 and (d or {}).get("ma") == "BR-09", tom_tat(st, d), "409 BR-09", f"dp POST /api/chuyen/{cid}/ghep (DA_CHOT)", "Vua", "BR-09")

    st, d, _ = dp.raw("PATCH", f"/api/don/{don_chinh['id']}", {"kg": "200.00"})
    bc.ghi("ST-04", "Sửa đơn đang ở chuyến DA_CHOT", st == 409 and (d or {}).get("ma") == "BR-33", tom_tat(st, d), "409 BR-33", f"dp PATCH /api/don/{don_chinh['id']} (chuyến DA_CHOT)", "Vua", "BR-33")

    st, d, _ = dp.raw("POST", f"/api/don/{don_chinh['id']}/huy", {"ly_do": "Thử hủy"})
    bc.ghi("ST-05", "Hủy đơn đang ở chuyến DA_CHOT", st == 409 and (d or {}).get("ma") == "BR-34", tom_tat(st, d), "409 BR-34", f"dp POST /api/don/{don_chinh['id']}/huy (chuyến DA_CHOT)", "Vua", "BR-34")

    st, d, _ = tx.multipart("POST", "/api/toi/quet", {"ma_don": don_chinh["ma_don"], "loai": "LAY"})
    bc.ghi("ST-06", "Quét lấy khi chuyến mới DA_CHOT (chưa bắt đầu)", st == 409 and (d or {}).get("ma") == "BR-38", tom_tat(st, d), "409 BR-38", f"tx POST /api/toi/quet loai=LAY (DA_CHOT)", "Vua", "BR-38")

    st, d, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/chi-phi", {"loai": "CAU_DUONG", "so_tien": "20000", "ghi_chu": "Thử"}, [("anh", "a.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("ST-07", "Ghi chi phí khi chuyến mới DA_CHOT", st == 409 and (d or {}).get("ma") == "BR-54", tom_tat(st, d), "409 BR-54", f"tx POST /api/toi/chuyen/{cid}/chi-phi (DA_CHOT)", "Vua", "BR-54")

    # Cấp tạm ứng rồi thử mở chốt & hủy chuyến (phải bị chặn BR-24, BR-25)
    st_tu, d_tu, _ = kt.raw("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 200000, "hinh_thuc": "TIEN_MAT"})
    assert st_tu == 201
    tu_id = d_tu["id"]

    st, d, _ = dp.raw("POST", f"/api/chuyen/{cid}/mo-chot")
    bc.ghi("ST-08", "Mở chốt chuyến còn tạm ứng HIEU_LUC", st == 409 and (d or {}).get("ma") == "BR-24", tom_tat(st, d), "409 BR-24", f"dp POST /api/chuyen/{cid}/mo-chot (còn tạm ứng)", "Vua", "BR-24")

    st, d, _ = dp.raw("POST", f"/api/chuyen/{cid}/huy", {"ly_do": "Hủy khi còn tạm ứng"})
    bc.ghi("ST-09", "Hủy chuyến DA_CHOT còn tạm ứng HIEU_LUC", st == 409 and (d or {}).get("ma") == "BR-25", tom_tat(st, d), "409 BR-25", f"dp POST /api/chuyen/{cid}/huy (còn tạm ứng)", "Vua", "BR-25")

    # Bắt đầu chuyến -> DANG_CHAY
    st_bd, _, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/bat-dau", {"km_bat_dau": "20010"}, [("anh_dong_ho", "k.jpg", MIN_JPG, "image/jpeg")])
    assert st_bd == 200

    # --- Trạng thái DANG_CHAY ---
    st, d, _ = dp.raw("POST", f"/api/chuyen/{cid}/huy", {"ly_do": "Hủy chuyến đang chạy"})
    bc.ghi("ST-10", "Hủy chuyến đang chạy (DANG_CHAY)", st == 409 and (d or {}).get("ma") == "BR-25", tom_tat(st, d), "409 BR-25", f"dp POST /api/chuyen/{cid}/huy (DANG_CHAY)", "Vua", "BR-25")

    st, d, _ = tx.multipart(
        "POST",
        "/api/toi/quet",
        {"ma_don": don_chinh["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Test"},
        [("anh", "g.jpg", MIN_JPG, "image/jpeg"), ("chu_ky", "k.png", MIN_PNG, "image/png")],
    )
    bc.ghi("ST-11", "Quét GIAO khi đơn chưa quét lấy (DA_GHEP)", st == 409 and (d or {}).get("ma") == "BR-40", tom_tat(st, d), "409 BR-40", f"tx POST /api/toi/quet ma_don={don_chinh['ma_don']} loai=GIAO (chưa lấy)", "Vua", "BR-40")

    st, d, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/ket-thuc", {"km_ket_thuc": "20080"}, [("anh_dong_ho", "k2.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("ST-12", "Kết thúc chuyến khi còn đơn chưa có kết quả", st == 422 and (d or {}).get("ma") == "BR-28", tom_tat(st, d), "422 BR-28", f"tx POST /api/toi/chuyen/{cid}/ket-thuc (còn đơn)", "Vua", "BR-28")

    # Tạo 1 khoản chi phí rồi thử duyệt khi chuyến DANG_CHAY
    st_cp, d_cp, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/chi-phi", {"loai": "CAU_DUONG", "so_tien": "50000", "ghi_chu": "Cầu đường"}, [("anh", "a.jpg", MIN_JPG, "image/jpeg")])
    assert st_cp == 201
    cp_id = d_cp["id"]

    st, d, _ = kt.raw("POST", f"/api/chi-phi/{cp_id}/duyet", {"so_tien_duyet": 50000})
    bc.ghi("ST-13", "Kế toán duyệt chi phí khi chuyến đang chạy (chưa HOAN_THANH)", st == 409 and (d or {}).get("ma") == "BR-55", tom_tat(st, d), "409 BR-55", f"kt POST /api/chi-phi/{cp_id}/duyet (DANG_CHAY)", "Vua", "BR-55")

    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/quyet-toan", {"xu_ly_chenh_lech": "KHONG_CHENH"})
    bc.ghi("ST-14", "Quyết toán chuyến đang chạy (chưa HOAN_THANH)", st == 409 and (d or {}).get("ma") == "BR-55", tom_tat(st, d), "409 BR-55", f"kt POST /api/chuyen/{cid}/quyet-toan (DANG_CHAY)", "Vua", "BR-55")

    # Báo 1 sự cố, đóng rồi thử đóng lại
    _, d_sc, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/su-co", {"loai": "KET_XE", "ghi_chu": "Kẹt xe cầu"})
    sc_id = d_sc["id"]
    dp.raw("POST", f"/api/su-co/{sc_id}/dong", {"cach_xu_ly": "Đã thông xe"})
    st, d, _ = dp.raw("POST", f"/api/su-co/{sc_id}/dong", {"cach_xu_ly": "Đóng lại lần 2"})
    bc.ghi("ST-15", "Đóng sự cố đã đóng", st == 409 and (d or {}).get("ma") == "SU_CO_DA_DONG", tom_tat(st, d), "409 SU_CO_DA_DONG", f"dp POST /api/su-co/{sc_id}/dong (đã DONG)", "Vua", "UC-32")

    # Quét hoàn tất 3 đơn: 1 giao thành công, 1 không lấy được, 1 lấy được nhưng giao thất bại
    tx.multipart("POST", "/api/toi/quet", {"ma_don": don_chinh["ma_don"], "loai": "LAY"})
    tx.multipart(
        "POST",
        "/api/toi/quet",
        {"ma_don": don_chinh["ma_don"], "loai": "GIAO", "ten_nguoi_nhan": "Anh Nhan"},
        [("anh", "g.jpg", MIN_JPG, "image/jpeg"), ("chu_ky", "k.png", MIN_PNG, "image/png")],
    )
    tx.multipart("POST", "/api/toi/quet", {"ma_don": don_tb_chua_lay["ma_don"], "loai": "KHONG_LAY", "ly_do_id": "1"}, [("anh", "f.jpg", MIN_JPG, "image/jpeg")])
    tx.multipart("POST", "/api/toi/quet", {"ma_don": don_tb_da_lay["ma_don"], "loai": "LAY"})
    tx.multipart("POST", "/api/toi/quet", {"ma_don": don_tb_da_lay["ma_don"], "loai": "GIAO_THAT_BAI", "ly_do_id": "7"}, [("anh", "f.jpg", MIN_JPG, "image/jpeg")])

    # Kết thúc chuyến -> HOAN_THANH
    st_kt, _, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/ket-thuc", {"km_ket_thuc": "20090"}, [("anh_dong_ho", "k2.jpg", MIN_JPG, "image/jpeg")])
    assert st_kt == 200

    # --- Trạng thái HOAN_THANH ---
    # Kiểm xử lý sai điều kiện đơn THAT_BAI (BR-34, BR-36)
    st, d, _ = dp.raw("POST", f"/api/don/{don_tb_chua_lay['id']}/tra-hang", {"ly_do": "Trả khi chưa lấy"})
    bc.ghi("ST-16", "Trả hàng đơn THAT_BAI chưa có lượt quét lấy", st == 422 and (d or {}).get("ma") == "BR-36", tom_tat(st, d), "422 BR-36", f"dp POST /api/don/{don_tb_chua_lay['id']}/tra-hang", "Vua", "BR-36")

    st, d, _ = dp.raw("POST", f"/api/don/{don_tb_da_lay['id']}/huy", {"ly_do": "Hủy khi đã lấy"})
    bc.ghi("ST-17", "Hủy đơn THAT_BAI đã có lượt quét lấy", st == 422 and (d or {}).get("ma") == "BR-34", tom_tat(st, d), "422 BR-34", f"dp POST /api/don/{don_tb_da_lay['id']}/huy", "Vua", "BR-34")

    # Quyết toán khi còn chi phí CHO_DUYET
    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/quyet-toan", {"xu_ly_chenh_lech": "TAI_XE_DA_NOP", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": iso_vn(now_vn())})
    bc.ghi("ST-18", "Quyết toán khi còn chi phí CHO_DUYET", st == 409 and (d or {}).get("ma") == "BR-55", tom_tat(st, d), "409 BR-55", f"kt POST /api/chuyen/{cid}/quyet-toan (còn chi phí chờ duyệt)", "Vua", "BR-55")

    # Duyệt chi phí rồi thử tài xế sửa / xóa chi phí ĐÃ DUYỆT
    st_dy, _, _ = kt.raw("POST", f"/api/chi-phi/{cp_id}/duyet", {"so_tien_duyet": 50000})
    assert st_dy == 200

    st, d, _ = tx.raw("PATCH", f"/api/toi/chi-phi/{cp_id}", {"so_tien": 60000})
    bc.ghi("ST-19", "Tài xế sửa chi phí đã duyệt (DA_DUYET)", st == 409 and (d or {}).get("ma") == "BR-54", tom_tat(st, d), "409 BR-54", f"tx PATCH /api/toi/chi-phi/{cp_id}", "Vua", "BR-54")

    st, d, _ = tx.raw("DELETE", f"/api/toi/chi-phi/{cp_id}")
    bc.ghi("ST-20", "Tài xế xóa chi phí đã duyệt (DA_DUYET)", st == 409 and (d or {}).get("ma") == "BR-54", tom_tat(st, d), "409 BR-54", f"tx DELETE /api/toi/chi-phi/{cp_id}", "Vua", "BR-54")

    # Cấp tạm ứng mới khi chuyến HOAN_THANH (BR-53 chỉ cấp từ DA_CHOT tới trước HOAN_THANH)
    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/tam-ung", {"so_tien": 50000, "hinh_thuc": "TIEN_MAT"})
    bc.ghi("ST-21", "Cấp tạm ứng khi chuyến đã HOAN_THANH", st == 409 and (d or {}).get("ma") == "BR-53", tom_tat(st, d), "409 BR-53", f"kt POST /api/chuyen/{cid}/tam-ung (HOAN_THANH)", "Vua", "BR-53")

    # Quyết toán thành công -> DA_QUYET_TOAN (tam_ung 200k - chi 50k = +150k -> TAI_XE_DA_NOP)
    st_qt, d_qt, _ = kt.raw(
        "POST",
        f"/api/chuyen/{cid}/quyet-toan",
        {"xu_ly_chenh_lech": "TAI_XE_DA_NOP", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": iso_vn(now_vn())},
    )
    assert st_qt == 200, f"Quyet toan fail: {st_qt} {d_qt}"

    # --- Trạng thái DA_QUYET_TOAN (BR-29: chỉ đọc) ---
    st, d, _ = kt.raw("PATCH", f"/api/tam-ung/{tu_id}", {"so_tien": 150000, "ly_do": "Sửa sau quyết toán"})
    bc.ghi("ST-22", "Sửa tạm ứng sau khi chuyến DA_QUYET_TOAN", st == 409 and (d or {}).get("ma") == "BR-29", tom_tat(st, d), "409 BR-29", f"kt PATCH /api/tam-ung/{tu_id}", "Nghiem trong", "BR-29")

    st, d, _ = kt.raw("POST", f"/api/tam-ung/{tu_id}/thu-hoi", {"ly_do": "Thu hồi sau quyết toán"})
    bc.ghi("ST-23", "Thu hồi tạm ứng sau khi chuyến DA_QUYET_TOAN", st == 409 and (d or {}).get("ma") == "BR-29", tom_tat(st, d), "409 BR-29", f"kt POST /api/tam-ung/{tu_id}/thu-hoi", "Nghiem trong", "BR-29")

    st, d, _ = kt.raw("POST", f"/api/chi-phi/{cp_id}/tu-choi", {"ly_do": "Từ chối sau quyết toán"})
    bc.ghi("ST-24", "Từ chối chi phí sau khi chuyến DA_QUYET_TOAN", st == 409 and (d or {}).get("ma") == "BR-29", tom_tat(st, d), "409 BR-29", f"kt POST /api/chi-phi/{cp_id}/tu-choi", "Nghiem trong", "BR-29")

    st, d, _ = tx.multipart("POST", f"/api/toi/chuyen/{cid}/chi-phi", {"loai": "CAU_DUONG", "so_tien": "10000", "ghi_chu": "Ghi sau QT"}, [("anh", "a.jpg", MIN_JPG, "image/jpeg")])
    bc.ghi("ST-25", "Tài xế ghi thêm chi phí sau khi chuyến DA_QUYET_TOAN", st == 409 and (d or {}).get("ma") == "BR-29", tom_tat(st, d), "409 BR-29", f"tx POST /api/toi/chuyen/{cid}/chi-phi (DA_QUYET_TOAN)", "Nghiem trong", "BR-29")

    st, d, _ = kt.raw("POST", f"/api/chuyen/{cid}/quyet-toan", {"xu_ly_chenh_lech": "TAI_XE_DA_NOP", "hinh_thuc": "TIEN_MAT", "luc_xu_ly": iso_vn(now_vn())})
    bc.ghi("ST-26", "Quyết toán lại chuyến đã DA_QUYET_TOAN", st == 409 and (d or {}).get("ma") == "BR-29", tom_tat(st, d), "409 BR-29", f"kt POST /api/chuyen/{cid}/quyet-toan (lần 2)", "Nghiem trong", "BR-29")

    bc.luu_json("ket_qua_04.json")


if __name__ == "__main__":
    main()
