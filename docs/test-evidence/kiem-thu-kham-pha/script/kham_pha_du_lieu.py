"""Khảo sát nhanh dữ liệu hiện có trên hệ thống QLVC trước khi chạy bộ kiểm thử khám phá."""

import json
from playwright.sync_api import sync_playwright

BASE_API = "http://127.0.0.1:8000"


def dang_nhap(p, user, pw="demo12345"):
    ctx = p.request.new_context(base_url=BASE_API)
    r = ctx.post("/api/auth/dang-nhap", data={"ten_dang_nhap": user, "mat_khau": pw})
    assert r.status == 200, f"Login {user} failed: {r.status} {r.text()}"
    return ctx, r.json()


def main():
    with sync_playwright() as p:
        ql, u_ql = dang_nhap(p, "quanly")
        dp, u_dp = dang_nhap(p, "dieuphoi")
        kt, u_kt = dang_nhap(p, "ketoan")
        tx, u_tx = dang_nhap(p, "taixe")

        print("USERS:", u_ql, u_dp, u_kt, u_tx)

        for name, ctx, path in [
            ("nguoi-dung", ql, "/api/nguoi-dung?so_dong=50"),
            ("bang-gia", ql, "/api/bang-gia?so_dong=50"),
            ("cau-hinh", ql, "/api/cau-hinh"),
            ("xe", dp, "/api/xe?so_dong=50"),
            ("tai-xe", dp, "/api/tai-xe?so_dong=50"),
            ("nut", dp, "/api/nut?so_dong=50"),
            ("tuyen", dp, "/api/tuyen?so_dong=50"),
            ("khach-hang", dp, "/api/khach-hang?so_dong=50"),
            ("don", dp, "/api/don?so_dong=50"),
            ("chuyen", dp, "/api/chuyen?so_dong=50"),
            ("ly-do", dp, "/api/danh-muc/ly-do"),
            ("toi-chuyen-can-lam", tx, "/api/toi/chuyen?nhom=can_lam&so_dong=50"),
            ("toi-chuyen-da-xong", tx, "/api/toi/chuyen?nhom=da_xong&so_dong=50"),
            ("tam-ung", kt, "/api/tam-ung?so_dong=50"),
            ("phai-thu", kt, "/api/phai-thu?so_dong=50"),
        ]:
            r = ctx.get(path)
            body = r.json()
            if isinstance(body, dict) and "du_lieu" in body:
                print(f"\n=== {name} (tong={body.get('tong')}) ===")
                for item in body["du_lieu"][:10]:
                    print(" ", json.dumps(item, ensure_ascii=False))
            else:
                print(f"\n=== {name} ===")
                print(" ", json.dumps(body, ensure_ascii=False)[:800])

        ql.dispose()
        dp.dispose()
        kt.dispose()
        tx.dispose()


if __name__ == "__main__":
    main()
