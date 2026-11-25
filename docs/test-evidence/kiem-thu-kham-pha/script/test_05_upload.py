"""Mục 5: Kiểm thử upload file (ảnh đại diện, chi phí, sự cố, quét mã)."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import MIN_JPG, MIN_PNG, BaoCaoMuc, dang_nhap, iso_vn, now_vn, tom_tat

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "uploads"))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main():
    bc = BaoCaoMuc(5, "Upload tệp (ảnh đại diện, chi phí, sự cố, quét)")
    dp = dang_nhap("dieuphoi")

    # Chuẩn bị 1 tài xế + 1 chuyến DANG_CHAY sạch để thử upload chi phí, sự cố, quét
    sfx = uuid.uuid4().hex[:5]
    _, d_tx, _ = dp.raw(
        "POST",
        "/api/tai-xe",
        {
            "ten_dang_nhap": f"txup_{sfx}",
            "ho_ten": f"Tài xế Upload {sfx}",
            "mat_khau": "demo12345",
            "so_gplx": f"UPLD{sfx.upper()}01",
            "hang_gplx": "C",
            "han_gplx": "2029-12-31",
            "sdt": "0955443322",
        },
    )
    tx_id = d_tx["id"]
    tx = dang_nhap(f"txup_{sfx}", "demo12345")

    _, d_xe, _ = dp.raw(
        "POST",
        "/api/xe",
        {
            "bien_so": f"51U-{sfx}",
            "tai_trong_kg": 5000,
            "the_tich_m3": "20.00",
            "ktt_toan_bo_kg": 9000,
            "han_dang_kiem": "2028-12-31",
            "han_bao_hiem": "2028-12-31",
            "dinh_muc_lit_100km": "15.00",
            "km_dong_ho": 30000,
        },
    )
    xe_id = d_xe["id"]

    _, d_c, _ = dp.raw(
        "POST",
        "/api/chuyen",
        {"tuyen_id": 5, "khoi_hanh_du_kien": iso_vn(now_vn() + timedelta(minutes=15)), "xe_id": xe_id, "tai_xe_id": tx_id},
    )
    cid = d_c["id"]
    dp.raw("POST", f"/api/chuyen/{cid}/chot", {"xac_nhan_chay_rong": True})
    tx.multipart("POST", f"/api/toi/chuyen/{cid}/bat-dau", {"km_bat_dau": "30010"}, [("anh_dong_ho", "km.jpg", MIN_JPG, "image/jpeg")])

    fake_jpg = b"This is plain text disguised as JPEG file"
    empty_file = b""
    big_jpg = MIN_JPG + b"\x00" * (505 * 1024)
    svg_script = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    # Magic-byte spoof: 3 byte đầu JPEG nhưng phần sau hoàn toàn không phải ảnh JPEG hợp lệ
    magic_spoof = b"\xff\xd8\xff<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>"

    # --- 5A. Ảnh đại diện PUT /api/auth/anh-dai-dien ---
    avatar_cases = [
        ("UP-01", "Ảnh đại diện: file text đổi đuôi .jpg", "fake.jpg", fake_jpg, "image/jpeg", (400,)),
        ("UP-02", "Ảnh đại diện: file rỗng 0 byte", "empty.jpg", empty_file, "image/jpeg", (400,)),
        ("UP-03", "Ảnh đại diện: file > 500 KB (505 KB)", "big.jpg", big_jpg, "image/jpeg", (413,)),
        ("UP-04", "Ảnh đại diện: SVG có script (.svg)", "xss.svg", svg_script, "image/svg+xml", (400,)),
        ("UP-05", "Ảnh đại diện: SVG có script đổi đuôi .jpg", "xss.jpg", svg_script, "image/jpeg", (400,)),
        ("UP-06", "Ảnh đại diện: giả mạo 3 byte đầu JPEG (\\xff\\xd8\\xff + thẻ script)", "spoof.jpg", magic_spoof, "image/jpeg", (400, 422)),
    ]
    for ma, ten, fname, data_b, ctype, exp in avatar_cases:
        st, data, _ = tx.multipart("PUT", "/api/auth/anh-dai-dien", {}, [("anh", fname, data_b, ctype)])
        bc.ghi(
            ma,
            ten,
            st in exp,
            tom_tat(st, data),
            f"Bị từ chối HTTP {exp}",
            f"PUT /api/auth/anh-dai-dien filename={fname!r} len={len(data_b)}",
            "Vua" if ma == "UP-06" else "Nghiem trong",
            "security-rules / UC-39",
        )

    # Path traversal trên tên file `../../x.jpg` với nội dung JPEG thật -> không được ghi ra ngoài uploads/
    st, data, _ = tx.multipart("PUT", "/api/auth/anh-dai-dien", {}, [("anh", "../../x.jpg", MIN_JPG, "image/jpeg")])
    leaked = any(
        os.path.exists(p)
        for p in [
            os.path.join(BACKEND_DIR, "x.jpg"),
            os.path.join(ROOT_DIR, "x.jpg"),
            os.path.join(UPLOADS_DIR, "x.jpg"),
            os.path.abspath(os.path.join(UPLOADS_DIR, "..", "..", "x.jpg")),
        ]
    )
    bc.ghi(
        "UP-07",
        "Ảnh đại diện: tên file path traversal '../../x.jpg' (không ghi ra ngoài uploads/)",
        not leaked and st in (200, 400),
        f"HTTP {st}, tồn tại x.jpg ngoài uploads={leaked}",
        "Không ghi file tên x.jpg ra ngoài thư mục uploads/ (server tự sinh tên UUID)",
        "PUT /api/auth/anh-dai-dien filename='../../x.jpg' với byte JPEG hợp lệ",
        "Nghiem trong",
        "security-rules",
    )
    tx.raw("DELETE", "/api/auth/anh-dai-dien")

    # --- 5B. Ảnh chi phí POST /api/toi/chuyen/{id}/chi-phi ---
    cp_cases = [
        ("UP-08", "Chi phí: file text đổi đuôi .jpg", "fake.jpg", fake_jpg, "image/jpeg", (400,)),
        ("UP-09", "Chi phí: file rỗng 0 byte", "empty.jpg", empty_file, "image/jpeg", (400,)),
        ("UP-10", "Chi phí: file > 500 KB", "big.jpg", big_jpg, "image/jpeg", (413,)),
        ("UP-11", "Chi phí: SVG có script", "xss.svg", svg_script, "image/svg+xml", (400,)),
        ("UP-12", "Chi phí: giả mạo 3 byte đầu JPEG + script", "spoof.jpg", magic_spoof, "image/jpeg", (400, 422)),
    ]
    for ma, ten, fname, data_b, ctype, exp in cp_cases:
        st, data, _ = tx.multipart(
            "POST",
            f"/api/toi/chuyen/{cid}/chi-phi",
            {"loai": "CAU_DUONG", "so_tien": "20000", "ghi_chu": "Test upload"},
            [("anh", fname, data_b, ctype)],
        )
        bc.ghi(
            ma,
            ten,
            st in exp,
            tom_tat(st, data),
            f"Bị từ chối HTTP {exp}",
            f"POST /api/toi/chuyen/{cid}/chi-phi filename={fname!r}",
            "Vua" if ma == "UP-12" else "Nghiem trong",
            "security-rules / BR-54",
        )

    # Path traversal ở chi phí
    st, data, _ = tx.multipart(
        "POST",
        f"/api/toi/chuyen/{cid}/chi-phi",
        {"loai": "CAU_DUONG", "so_tien": "20000", "ghi_chu": "Test traversal"},
        [("anh", "../../x.jpg", MIN_JPG, "image/jpeg")],
    )
    leaked_cp = any(
        os.path.exists(p)
        for p in [os.path.join(BACKEND_DIR, "x.jpg"), os.path.join(ROOT_DIR, "x.jpg"), os.path.join(UPLOADS_DIR, "x.jpg")]
    )
    bc.ghi(
        "UP-13",
        "Chi phí: tên file '../../x.jpg' không ghi ra ngoài uploads/",
        not leaked_cp and st in (201, 400),
        f"HTTP {st}, tồn tại x.jpg={leaked_cp}",
        "Không ghi ra ngoài thư mục uploads/",
        f"POST /api/toi/chuyen/{cid}/chi-phi filename='../../x.jpg'",
        "Nghiem trong",
        "security-rules",
    )

    # Quá 5 ảnh ở chi phí
    six_files = [("anh", f"a{i}.jpg", MIN_JPG, "image/jpeg") for i in range(6)]
    st, data, _ = tx.multipart(
        "POST",
        f"/api/toi/chuyen/{cid}/chi-phi",
        {"loai": "CAU_DUONG", "so_tien": "20000", "ghi_chu": "6 ảnh"},
        six_files,
    )
    bc.ghi("UP-14", "Chi phí: gửi 6 ảnh (vượt giới hạn 5 ảnh)", st == 400, tom_tat(st, data), "HTTP 400 QUA_NHIEU_ANH", f"POST /api/toi/chuyen/{cid}/chi-phi với 6 ảnh", "Vua", "api.md 2.5")

    # --- 5C. Ảnh sự cố POST /api/toi/chuyen/{id}/su-co ---
    for ma, ten, fname, data_b, ctype, exp in [
        ("UP-15", "Sự cố: file text đổi đuôi .jpg", "fake.jpg", fake_jpg, "image/jpeg", (400,)),
        ("UP-16", "Sự cố: file rỗng 0 byte", "empty.jpg", empty_file, "image/jpeg", (400,)),
        ("UP-17", "Sự cố: file > 500 KB", "big.jpg", big_jpg, "image/jpeg", (413,)),
        ("UP-18", "Sự cố: SVG có script", "xss.svg", svg_script, "image/svg+xml", (400,)),
        ("UP-19", "Sự cố: giả mạo 3 byte đầu JPEG + script", "spoof.jpg", magic_spoof, "image/jpeg", (400, 422)),
    ]:
        st, data, _ = tx.multipart(
            "POST",
            f"/api/toi/chuyen/{cid}/su-co",
            {"loai": "KHAC", "ghi_chu": "Test upload sự cố"},
            [("anh", fname, data_b, ctype)],
        )
        bc.ghi(
            ma,
            ten,
            st in exp,
            tom_tat(st, data),
            f"Bị từ chối HTTP {exp}",
            f"POST /api/toi/chuyen/{cid}/su-co filename={fname!r}",
            "Vua" if ma == "UP-19" else "Nghiem trong",
            "security-rules / UC-33",
        )

    # Kết thúc chuyến sạch
    tx.multipart("POST", f"/api/toi/chuyen/{cid}/ket-thuc", {"km_ket_thuc": "30050"}, [("anh_dong_ho", "k2.jpg", MIN_JPG, "image/jpeg")])

    bc.luu_json("ket_qua_05.json")


if __name__ == "__main__":
    main()
