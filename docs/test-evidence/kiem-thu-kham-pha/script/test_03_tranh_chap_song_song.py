"""Mục 3: Kiểm thử thao tác lặp / tranh chấp đồng thời (2-10 request song song)."""

from __future__ import annotations

import os
import sys
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import MIN_JPG, MIN_PNG, ApiClient, BaoCaoMuc, dang_nhap, iso_vn, now_vn, tom_tat


def chay_song_song(n: int, fn):
    barrier = threading.Barrier(n)

    def worker(i: int):
        barrier.wait()
        return fn(i)

    with ThreadPoolExecutor(max_workers=n) as ex:
        futs = [ex.submit(worker, i) for i in range(n)]
        return [f.result() for f in futs]


def main():
    bc = BaoCaoMuc(3, "Thao tác lặp / tranh chấp song song")
    dp = dang_nhap("dieuphoi")
    kt = dang_nhap("ketoan")
    tx = dang_nhap("taixe")

    sfx = uuid.uuid4().hex[:5]
    han_ok = iso_vn(now_vn() + timedelta(days=3))

    # --- 3.1 Tạo đơn song song 5 lần cùng nội dung ---
    don_body = {
        "khach_hang_id": 1,
        "mo_ta": f"RaceDon-{sfx}",
        "kg": "100.00",
        "m3": "1.00",
        "so_kien": 2,
        "nut_lay_id": 5,
        "dia_chi_lay": f"10 Race Lay {sfx}",
        "sdt_lay": "0909555001",
        "nut_giao_id": 11,
        "dia_chi_giao": f"20 Race Giao {sfx}",
        "nguoi_nhan": "Race Nhan",
        "sdt_nhan": "0909555002",
        "han_giao": han_ok,
    }
    res = chay_song_song(5, lambda i: dp.clone().raw("POST", "/api/don", don_body))
    ok_dons = [d["id"] for st, d, _ in res if st == 201]
    statuses = [st for st, _, _ in res]
    bc.ghi(
        "TC-01",
        "Gửi 5 request POST /api/don song song cùng nội dung",
        len(ok_dons) == 1,
        f"statuses={statuses}, tạo ra {len(ok_dons)} đơn trùng nội dung (ids={ok_dons})",
        "Không tạo trùng đơn khi gửi cùng request song song (chỉ tạo 1 hoặc chặn trùng)",
        "5 luồng đồng thời POST /api/don cùng payload",
        "Vua",
        "Chống tạo trùng / idempotency",
    )

    # Tạo 1 tài xế + 2 xe riêng (hoặc dùng 2 xe khả dụng) cho các ca tranh chấp chuyến
    st_tx, d_tx, _ = dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": f"txrace_{sfx}",
            "ho_ten": f"Tài xế Race {sfx}",
            "mat_khau": "demo12345",
            "so_gplx": f"RACE{sfx.upper()}01",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0977665544",
        },
    )
    assert st_tx == 201, f"Tao tx race fail: {st_tx} {d_tx}"
    tx_race_id = d_tx["id"]
    tx_race = dang_nhap(f"txrace_{sfx}", "demo12345")

    st_tx2, d_tx2, _ = dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": f"txrace2_{sfx}",
            "ho_ten": f"Tài xế Race2 {sfx}",
            "mat_khau": "demo12345",
            "so_gplx": f"RACE{sfx.upper()}02",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0977665545",
        },
    )
    assert st_tx2 == 201
    tx_race2_id = d_tx2["id"]

    # Tạo 2 xe riêng để không vướng lịch xe seed
    st_x1, d_x1, _ = dp.raw(
        "POST",
        "/api/xe",
        {
            "bien_so": f"51R-{sfx}1",
            "tai_trong_kg": 5000,
            "the_tich_m3": "20.00",
            "ktt_toan_bo_kg": 9000,
            "han_dang_kiem": "2028-12-31",
            "han_bao_hiem": "2028-12-31",
            "dinh_muc_lit_100km": "15.00",
            "km_dong_ho": 10000,
        },
    )
    st_x2, d_x2, _ = dp.raw(
        "POST",
        "/api/xe",
        {
            "bien_so": f"51R-{sfx}2",
            "tai_trong_kg": 5000,
            "the_tich_m3": "20.00",
            "ktt_toan_bo_kg": 9000,
            "han_dang_kiem": "2028-12-31",
            "han_bao_hiem": "2028-12-31",
            "dinh_muc_lit_100km": "15.00",
            "km_dong_ho": 10000,
        },
    )
    assert st_x1 == 201 and st_x2 == 201, f"Tao xe race fail: {st_x1} {st_x2}"
    xe1_id, xe2_id = d_x1["id"], d_x2["id"]

    # --- 3.2 Lập chuyến song song 5 lần cùng xe/tài xế/giờ (BR-16, BR-17) ---
    kh_now = iso_vn(now_vn() + timedelta(minutes=15))
    res = chay_song_song(
        5,
        lambda i: dp.clone().raw(
            "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": kh_now, "xe_id": xe1_id, "tai_xe_id": tx_race_id}
        ),
    )
    ok_ch = [d["id"] for st, d, _ in res if st == 201]
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-02",
        "Gửi 5 request POST /api/chuyen song song cùng xe + tài xế + giờ",
        len(ok_ch) == 1 and all(s in (201, 422) for s in sts),
        f"statuses={sts}, số chuyến tạo được={len(ok_ch)}",
        "Chỉ tạo 1 chuyến (201), 4 request còn lại bị chặn 422 BR-16/BR-17",
        "5 luồng đồng thời POST /api/chuyen cùng xe/tài xế/giờ",
        "Nghiem trong",
        "BR-16, BR-17",
    )
    ch1_id = ok_ch[0]

    # Tạo chuyến thứ 2 cho xe2 + tx_race2 để test ghép 1 đơn vào 2 chuyến song song
    st_c2, d_c2, _ = dp.raw(
        "POST", "/api/chuyen", {"tuyen_id": 5, "khoi_hanh_du_kien": kh_now, "xe_id": xe2_id, "tai_xe_id": tx_race2_id}
    )
    assert st_c2 == 201
    ch2_id = d_c2["id"]

    # --- 3.3 Ghép cùng 1 đơn vào cùng 1 chuyến (5 luồng song song) ---
    don_ghep_1 = ok_dons[0]
    res = chay_song_song(5, lambda i: dp.clone().raw("POST", f"/api/chuyen/{ch1_id}/ghep", {"don_ids": [don_ghep_1]}))
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-03",
        f"Ghép cùng 1 đơn (id={don_ghep_1}) vào chuyến {ch1_id} bằng 5 luồng song song",
        sts.count(200) == 1 and all(s in (200, 409) for s in sts),
        f"statuses={sts}",
        "Chỉ 1 lần 200, 4 lần còn lại 409 (BR-07/BR-09), không 500",
        f"5 luồng đồng thời POST /api/chuyen/{ch1_id}/ghep don_ids=[{don_ghep_1}]",
        "Nghiem trong",
        "BR-07, BR-09",
    )

    # --- 3.4 Ghép cùng 1 đơn vào 2 chuyến KHÁC nhau song song (BR-07) ---
    don_ghep_2 = ok_dons[1] if len(ok_dons) > 1 else dp.raw("POST", "/api/don", don_body)[1]["id"]
    res = chay_song_song(
        4,
        lambda i: dp.clone().raw("POST", f"/api/chuyen/{ch1_id if i % 2 == 0 else ch2_id}/ghep", {"don_ids": [don_ghep_2]}),
    )
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-04",
        f"Ghép cùng 1 đơn (id={don_ghep_2}) vào 2 chuyến khác nhau ({ch1_id}, {ch2_id}) song song",
        sts.count(200) == 1 and all(s in (200, 409) for s in sts),
        f"statuses={sts}",
        "Chỉ đúng 1 chuyến ghép được (200), các request còn lại 409 BR-07/BR-09",
        f"4 luồng xen kẽ POST /api/chuyen/{ch1_id}/ghep và /{ch2_id}/ghep cùng don_id={don_ghep_2}",
        "Nghiem trong",
        "BR-07",
    )

    # --- 3.5 Ghép 2 đơn nặng song song vượt tải trọng xe (mỗi đơn 3000 kg, xe tải 5000 kg -> tổng 6000 > 5000) ---
    _, d_nang1, _ = dp.raw("POST", "/api/don", {**don_body, "kg": "3000.00", "m3": "5.00"})
    _, d_nang2, _ = dp.raw("POST", "/api/don", {**don_body, "kg": "3000.00", "m3": "5.00"})
    res = chay_song_song(
        2,
        lambda i: dp.clone().raw(
            "POST", f"/api/chuyen/{ch2_id}/ghep", {"don_ids": [d_nang1["id"] if i == 0 else d_nang2["id"]]}
        ),
    )
    sts = [st for st, _, _ in res]
    _, ct_ch2, _ = dp.raw("GET", f"/api/chuyen/{ch2_id}")
    kg_ch2 = float(ct_ch2["tai_trong"]["da_dung_kg"])
    bc.ghi(
        "TC-05",
        "Ghép song song 2 đơn nặng (3000kg + 3000kg) vào xe tải 5000kg",
        kg_ch2 <= 5000 and sts.count(200) == 1 and sts.count(422) == 1,
        f"statuses={sts}, tải đã dùng={kg_ch2}kg / 5000kg",
        "Chỉ 1 đơn ghép được (200), đơn kia bị chặn 422 BR-01, tải không vượt 5000kg",
        f"2 luồng song song ghép 2 đơn 3000kg vào chuyến {ch2_id}",
        "Nghiem trong",
        "BR-01",
    )

    # --- 3.6 Chốt chuyến song song 5 lần ---
    res = chay_song_song(
        5,
        lambda i: dp.clone().raw("POST", f"/api/chuyen/{ch1_id}/chot", {"xac_nhan_lai_am": True}),
    )
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-06",
        f"Chốt chuyến {ch1_id} bằng 5 luồng song song",
        sts.count(200) == 1 and all(s in (200, 409) for s in sts),
        f"statuses={sts}",
        "Chỉ 1 lần 200, 4 lần sau 409 BR-09",
        f"5 luồng đồng thời POST /api/chuyen/{ch1_id}/chot",
        "Vua",
        "BR-23, BR-09",
    )

    # --- 3.7 Tạm ứng song song 8 lần vượt định mức (BR-53) ---
    # Tuyến 5 có định mức 500k + 150k + 200k = 850.000 đ -> mỗi luồng xin 500.000 đ (2 lần là 1.000.000 > 850.000)
    res = chay_song_song(
        8,
        lambda i: kt.clone().raw("POST", f"/api/chuyen/{ch1_id}/tam-ung", {"so_tien": 500000, "hinh_thuc": "TIEN_MAT"}),
    )
    sts = [st for st, _, _ in res]
    _, tu_info, _ = kt.raw("GET", f"/api/chuyen/{ch1_id}/tam-ung")
    tong_hl = tu_info["tong_hieu_luc"]
    dm = tu_info["dinh_muc"]
    bc.ghi(
        "TC-07",
        f"8 luồng song song cấp tạm ứng 500.000đ trên chuyến định mức {dm:,}đ (BR-53)",
        sts.count(201) == 1 and tong_hl <= dm and all(s in (201, 422) for s in sts),
        f"statuses={sts}, tong_hieu_luc={tong_hl:,} / dinh_muc={dm:,}",
        f"Chỉ 1 request thành công (201), 7 request bị chặn 422 BR-53, tổng <= {dm:,}",
        f"8 luồng đồng thời POST /api/chuyen/{ch1_id}/tam-ung so_tien=500000",
        "Nghiem trong",
        "BR-53",
    )

    # Bắt đầu chuyến ch1 để test quét song song & chi phí song song
    st_bd, d_bd, _ = tx_race.multipart(
        "POST",
        f"/api/toi/chuyen/{ch1_id}/bat-dau",
        {"km_bat_dau": "10010"},
        [("anh_dong_ho", "km.jpg", MIN_JPG, "image/jpeg")],
    )
    assert st_bd == 200, f"Bat dau ch1 fail: {st_bd} {d_bd}"

    _, ct_ch1, _ = dp.raw("GET", f"/api/chuyen/{ch1_id}")
    ma_dons_ch1 = [d["ma_don"] for d in ct_ch1["don"]]
    ma_don_test = ma_dons_ch1[0]

    # --- 3.8 Quét LAY song song 6 lần cùng mã đơn (BR-45) ---
    res = chay_song_song(
        6,
        lambda i: tx_race.clone().multipart("POST", "/api/toi/quet", {"ma_don": ma_don_test, "loai": "LAY"}),
    )
    sts = [st for st, _, _ in res]
    lap_false = sum(1 for st, d, _ in res if st == 200 and d and d.get("lap_lai") is False)
    lap_true = sum(1 for st, d, _ in res if st == 200 and d and d.get("lap_lai") is True)
    bc.ghi(
        "TC-08",
        f"Quét LAY song song 6 lần cùng mã {ma_don_test}",
        all(s == 200 for s in sts) and lap_false == 1 and lap_true == 5,
        f"statuses={sts}, lap_lai=False: {lap_false}, lap_lai=True: {lap_true}",
        "6 lần đều 200: đúng 1 lần ghi mới (lap_lai=False), 5 lần lặp (lap_lai=True)",
        f"6 luồng đồng thời POST /api/toi/quet ma_don={ma_don_test} loai=LAY",
        "Vua",
        "BR-45",
    )

    # --- 3.9 Quét GIAO song song 6 lần cùng mã đơn (kiểm không sinh trùng phải thu) ---
    res = chay_song_song(
        6,
        lambda i: tx_race.clone().multipart(
            "POST",
            "/api/toi/quet",
            {"ma_don": ma_don_test, "loai": "GIAO", "ten_nguoi_nhan": "Anh Nhan"},
            [("anh", "giao.jpg", MIN_JPG, "image/jpeg"), ("chu_ky", "ky.png", MIN_PNG, "image/png")],
        ),
    )
    sts = [st for st, _, _ in res]
    lap_false = sum(1 for st, d, _ in res if st == 200 and d and d.get("lap_lai") is False)
    lap_true = sum(1 for st, d, _ in res if st == 200 and d and d.get("lap_lai") is True)
    bc.ghi(
        "TC-09",
        f"Quét GIAO song song 6 lần cùng mã {ma_don_test} (kiểm idempotent + không trùng phải thu)",
        all(s == 200 for s in sts) and lap_false == 1 and lap_true == 5,
        f"statuses={sts}, lap_lai=False: {lap_false}, lap_lai=True: {lap_true}",
        "6 lần 200: đúng 1 lần lap_lai=False, 5 lần lap_lai=True, không 500",
        f"6 luồng đồng thời POST /api/toi/quet ma_don={ma_don_test} loai=GIAO",
        "Nghiem trong" if any(s >= 500 for s in sts) else "Vua",
        "BR-45, BR-56",
    )

    # Quét xong các đơn còn lại trong ch1 (nếu có) để kết thúc chuyến
    for ma_d in ma_dons_ch1[1:]:
        tx_race.multipart("POST", "/api/toi/quet", {"ma_don": ma_d, "loai": "LAY"})
        tx_race.multipart(
            "POST",
            "/api/toi/quet",
            {"ma_don": ma_d, "loai": "GIAO", "ten_nguoi_nhan": "Anh Nhan"},
            [("anh", "giao.jpg", MIN_JPG, "image/jpeg"), ("chu_ky", "ky.png", MIN_PNG, "image/png")],
        )

    # --- 3.10 Tài xế gửi 5 request DELETE /api/toi/chi-phi/{id} song song ---
    st_cp1, d_cp1, _ = tx_race.multipart(
        "POST",
        f"/api/toi/chuyen/{ch1_id}/chi-phi",
        {"loai": "CAU_DUONG", "so_tien": "30000", "ghi_chu": "Test xóa song song"},
        [("anh", "a.jpg", MIN_JPG, "image/jpeg")],
    )
    assert st_cp1 == 201
    cp_del_id = d_cp1["id"]
    res = chay_song_song(5, lambda i: tx_race.clone().raw("DELETE", f"/api/toi/chi-phi/{cp_del_id}"))
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-10",
        f"5 luồng song song DELETE /api/toi/chi-phi/{cp_del_id}",
        sts.count(204) == 1 and all(s in (204, 404) for s in sts),
        f"statuses={sts}, chi_tiet={[d for s, d, _ in res if s >= 500][:2]}",
        "1 lần 204, 4 lần 404, tuyệt đối không 500",
        f"5 luồng đồng thời DELETE /api/toi/chi-phi/{cp_del_id}",
        "Nghiem trong",
        "NFR-REL-01",
    )

    # Tạo thêm 2 khoản chi phí rồi kết thúc chuyến ch1 -> test duyệt song song & race xóa-vs-duyệt
    st_cp2, d_cp2, _ = tx_race.multipart(
        "POST",
        f"/api/toi/chuyen/{ch1_id}/chi-phi",
        {"loai": "CAU_DUONG", "so_tien": "40000", "ghi_chu": "Test duyệt song song"},
        [("anh", "a.jpg", MIN_JPG, "image/jpeg")],
    )
    st_cp3, d_cp3, _ = tx_race.multipart(
        "POST",
        f"/api/toi/chuyen/{ch1_id}/chi-phi",
        {"loai": "CAU_DUONG", "so_tien": "45000", "ghi_chu": "Test race xóa vs duyệt"},
        [("anh", "a.jpg", MIN_JPG, "image/jpeg")],
    )
    assert st_cp2 == 201 and st_cp3 == 201
    cp_duyet_id = d_cp2["id"]
    cp_race_id = d_cp3["id"]

    st_kt, d_kt, _ = tx_race.multipart(
        "POST",
        f"/api/toi/chuyen/{ch1_id}/ket-thuc",
        {"km_ket_thuc": "10080"},
        [("anh_dong_ho", "km2.jpg", MIN_JPG, "image/jpeg")],
    )
    assert st_kt == 200, f"Ket thuc ch1 fail: {st_kt} {d_kt}"

    # --- 3.11 Duyệt cùng 1 khoản chi phí bằng 5 luồng song song ---
    res = chay_song_song(
        5,
        lambda i: kt.clone().raw("POST", f"/api/chi-phi/{cp_duyet_id}/duyet", {"so_tien_duyet": 40000}),
    )
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-11",
        f"5 luồng song song POST /api/chi-phi/{cp_duyet_id}/duyet",
        sts.count(200) == 1 and all(s in (200, 400) for s in sts),
        f"statuses={sts}",
        "Chỉ 1 lần 200, 4 lần còn lại 400 KHONG_CO_THAY_DOI, không 500",
        f"5 luồng đồng thời POST /api/chi-phi/{cp_duyet_id}/duyet so_tien_duyet=40000",
        "Nghiem trong" if any(s >= 500 for s in sts) else "Vua",
        "BR-55, BR-62",
    )

    # --- 3.12 Tranh chấp: Tài xế DELETE chi phí đồng thời Kế toán POST /duyet ---
    res = chay_song_song(
        2,
        lambda i: (
            tx_race.clone().raw("DELETE", f"/api/toi/chi-phi/{cp_race_id}")
            if i == 0
            else kt.clone().raw("POST", f"/api/chi-phi/{cp_race_id}/duyet", {"so_tien_duyet": 45000})
        ),
    )
    sts = [st for st, _, _ in res]
    bc.ghi(
        "TC-12",
        f"Tranh chấp Tài xế DELETE /api/toi/chi-phi/{cp_race_id} song song Kế toán POST /duyet",
        not any(s >= 500 for s in sts),
        f"statuses(delete, duyet)={sts}, bodies={[d for _, d, _ in res]}",
        "Một bên thành công, bên kia 404/409, tuyệt đối không 500",
        f"Song song: tx DELETE /api/toi/chi-phi/{cp_race_id} & kt POST /api/chi-phi/{cp_race_id}/duyet",
        "Nghiem trong",
        "BR-54, BR-55, NFR-REL-01",
    )

    # --- 3.13 Đánh dấu đã thu song song 5 lần trên cùng khoản phải thu ---
    _, ds_pt, _ = kt.raw("GET", "/api/phai-thu?trang_thai_tt=CHUA_THU&so_dong=50")
    pt_cua_don = next((p for p in ds_pt["du_lieu"] if p["ma_don"] == ma_don_test), None)
    if pt_cua_don:
        pt_id = pt_cua_don["id"]
        ngay_nay = now_vn().strftime("%Y-%m-%d")
        res = chay_song_song(
            5,
            lambda i: kt.clone().raw("POST", "/api/phai-thu/da-thu", {"phai_thu_ids": [pt_id], "ngay": ngay_nay}),
        )
        sts = [st for st, _, _ in res]
        bc.ghi(
            "TC-13",
            f"5 luồng song song POST /api/phai-thu/da-thu cho phai_thu_id={pt_id}",
            sts.count(200) == 1 and all(s in (200, 409) for s in sts),
            f"statuses={sts}",
            "Chỉ 1 lần 200 tạo 1 phiếu thu, 4 lần còn lại 409 BR-56",
            f"5 luồng đồng thời POST /api/phai-thu/da-thu phai_thu_ids=[{pt_id}]",
            "Nghiem trong",
            "BR-56",
        )

    bc.luu_json("ket_qua_03.json")


if __name__ == "__main__":
    main()
