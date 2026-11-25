"""Mục 7: Kiểm thử giao diện bằng Playwright (1440px & 390px):
- Bấm nhanh 2 lần nút Lưu đơn / Ghép / Chốt
- F5 giữa chừng, nút Back trình duyệt
- Hai tab cùng sửa 1 đơn (kiểm lost update / ghi đè âm thầm)
- Tài xế mở thẳng URL trang vai trò khác
- XSS không thực thi trên giao diện (nhập bừa qua giao diện)
- Kiểm màn trắng, lỗi console/pageerror, chữ/bảng tràn ngang ở 1440px & 390px
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import timedelta

from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ho_tro import BASE_FE, BaoCaoMuc, dang_nhap, iso_vn, now_vn


def dang_nhap_ui(page: Page, user: str, pw: str = "demo12345"):
    page.goto(f"{BASE_FE}/dang-nhap", wait_until="networkidle")
    page.locator('input[autocomplete="username"]').fill(user)
    page.locator('input[autocomplete="current-password"]').fill(pw)
    page.locator('button:has-text("Đăng nhập")').click()
    page.wait_for_url(lambda u: "/dang-nhap" not in u, timeout=10000)
    page.wait_for_load_state("networkidle")


def kiem_tran_ngang(page: Page) -> dict:
    return page.evaluate(
        """() => {
            const doc = document.documentElement;
            const body = document.body;
            const vw = window.innerWidth;
            const sw = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
            const textLen = (body ? body.innerText : '').trim().length;
            const tran = [];
            for (const el of document.querySelectorAll('h1,h2,h3,button,a,table,th,td,input,select,form,section,aside,header,nav')) {
                const r = el.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) continue;
                if (r.right > vw + 2) {
                    const style = getComputedStyle(el);
                    // Bỏ qua phần tử nằm trong container có overflow-x auto/scroll
                    let p = el.parentElement;
                    let trongCuon = false;
                    while (p) {
                        const ps = getComputedStyle(p);
                        if ((ps.overflowX === 'auto' || ps.overflowX === 'scroll') && p.clientWidth <= vw + 2) {
                            trongCuon = true;
                            break;
                        }
                        p = p.parentElement;
                    }
                    if (!trongCuon && style.overflowX !== 'auto' && style.overflowX !== 'scroll') {
                        tran.push({
                            tag: el.tagName.toLowerCase(),
                            cls: (el.className || '').toString().slice(0, 40),
                            txt: (el.innerText || '').trim().slice(0, 40),
                            right: Math.round(r.right),
                            vw
                        });
                    }
                }
            }
            return { vw, sw, overflow: sw > vw + 2, textLen, tran: tran.slice(0, 5) };
        }"""
    )


def main():
    bc = BaoCaoMuc(7, "Giao diện (Playwright 1440px & 390px)")
    dp_api = dang_nhap("dieuphoi")
    sfx = uuid.uuid4().hex[:5]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Theo dõi lỗi console / pageerror / dialog XSS toàn phiên
        def gan_theo_doi(page: Page, bag: dict):
            page.on("console", lambda m: bag["console"].append(f"{m.type}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda e: bag["pageerror"].append(str(e)))
            page.on("response", lambda r: bag["http5xx"].append(f"{r.status} {r.url}") if r.status >= 500 else None)

        # =====================================================================
        # 7.1 Kiểm tra XSS không thực thi trên giao diện (từ dữ liệu NB-51 có <script>alert(1)</script>)
        # =====================================================================
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        bag = {"console": [], "pageerror": [], "http5xx": [], "dialogs": []}
        gan_theo_doi(page, bag)
        page.on("dialog", lambda d: (bag["dialogs"].append(d.message), d.dismiss()))
        dang_nhap_ui(page, "dieuphoi")
        page.goto(f"{BASE_FE}/dieu-phoi/khach-hang", wait_until="networkidle")
        page.wait_for_timeout(500)
        co_text_xss = "<script>alert(1)</script>" in page.content() or "alert(1)" in page.locator("body").inner_text()
        bc.ghi(
            "UI-01",
            "Render tên khách hàng chứa <script>alert(1)</script> và emoji trên trang Khách hàng không kích hoạt XSS",
            len(bag["dialogs"]) == 0 and len(bag["pageerror"]) == 0,
            f"dialogs={bag['dialogs']}, pageerror={bag['pageerror']}, hien_chuoi_tho={co_text_xss}",
            "Không có alert/dialog chạy, chuỗi <script> hiển thị dạng văn bản an toàn, không lỗi JS",
            "Mở /dieu-phoi/khach-hang sau khi tạo khách hàng có tên chứa <script>alert(1)</script>",
            "Nghiem trong",
            "OWASP XSS",
        )

        # =====================================================================
        # 7.2 Bấm nhanh 2 lần nút Lưu đơn khi tạo đơn mới (1440px)
        # =====================================================================
        _, ds_truoc, _ = dp_api.raw("GET", "/api/don?so_dong=5")
        tong_truoc = ds_truoc["tong"]
        page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="networkidle")
        page.locator('button:has-text("Tạo đơn")').click()
        form = page.locator("form.hop-thoai")
        form.wait_for(state="visible", timeout=5000)

        # Chọn khách Cty A (id=1), nút lấy Cần Thơ (5), nút giao An Giang (11)
        selects = form.locator("select")
        selects.nth(0).select_option("1")
        form.locator('input[type="number"]').nth(0).fill("120")  # kg
        form.locator('input[type="number"]').nth(1).fill("1.5")  # m3
        form.locator('input[type="number"]').nth(2).fill("3")    # so_kien
        selects.nth(1).select_option("5")
        selects.nth(2).select_option("11")
        # Điền các ô text bắt buộc
        form.locator("label", has_text="Mô tả hàng").locator("input").fill(f"DblClick-{sfx}")
        form.locator("label", has_text="Địa chỉ lấy").locator("input").fill(f"100 Đường Dbl {sfx}")
        form.locator("label", has_text="SĐT lấy").locator("input").fill("0909777888")
        form.locator("label", has_text="Địa chỉ giao").locator("input").fill(f"200 Đường Dbl {sfx}")
        form.locator("label", has_text="Người nhận").locator("input").fill("Chị Dbl")
        form.locator("label", has_text="SĐT nhận").locator("input").fill("0909888999")
        han_local = (now_vn() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
        form.locator("label", has_text="Hạn giao").locator("input").fill(han_local)

        btn_luu = form.locator('button:has-text("Lưu đơn")')
        # Chờ báo giá tải xong khiến nút Lưu đơn enabled
        page.wait_for_function("() => !document.querySelector('form.hop-thoai button:not([type=\"button\"])')?.disabled", timeout=5000)

        post_don_count = 0

        def dem_post(req):
            nonlocal post_don_count
            if req.method == "POST" and req.url.endswith("/api/don"):
                post_don_count += 1

        page.on("request", dem_post)
        # Bấm nhanh 2 lần liên tiếp (dblclick)
        btn_luu.dblclick()
        page.wait_for_timeout(1500)
        page.remove_listener("request", dem_post)
        _, ds_sau, _ = dp_api.raw("GET", "/api/don?so_dong=5")
        tao_them = ds_sau["tong"] - tong_truoc
        bc.ghi(
            "UI-02",
            "Bấm nhanh 2 lần (dblclick) nút 'Lưu đơn' khi tạo đơn",
            post_don_count == 1 and tao_them == 1,
            f"Số request POST /api/don={post_don_count}, số đơn tạo thêm={tao_them}",
            "Chỉ gửi 1 request và tạo đúng 1 đơn (không tạo trùng khi double-click)",
            "Mở /dieu-phoi/don -> Tạo đơn -> điền đủ -> dblclick nút Lưu đơn",
            "Vua",
            "UI chống bấm đúp",
        )

        # =====================================================================
        # 7.3 Dữ liệu nhập bừa qua giao diện Tạo đơn (kg âm, ngày quá khứ, số kiện 1e15)
        # =====================================================================
        page.locator('button:has-text("Tạo đơn")').click()
        form = page.locator("form.hop-thoai")
        form.wait_for(state="visible", timeout=5000)
        selects = form.locator("select")
        selects.nth(0).select_option("1")
        form.locator('input[type="number"]').nth(0).fill("100")
        form.locator('input[type="number"]').nth(1).fill("1")
        form.locator('input[type="number"]').nth(2).fill("1000000000000000")  # 1e15 số kiện
        selects.nth(1).select_option("5")
        selects.nth(2).select_option("11")
        form.locator("label", has_text="Địa chỉ lấy").locator("input").fill("10 UI Test")
        form.locator("label", has_text="SĐT lấy").locator("input").fill("0909123123")
        form.locator("label", has_text="Địa chỉ giao").locator("input").fill("20 UI Test")
        form.locator("label", has_text="Người nhận").locator("input").fill("Anh UI")
        form.locator("label", has_text="SĐT nhận").locator("input").fill("0909321321")
        form.locator("label", has_text="Hạn giao").locator("input").fill("2020-01-01T10:00")  # quá khứ
        page.wait_for_function("() => !document.querySelector('form.hop-thoai button:not([type=\"button\"])')?.disabled", timeout=5000)
        form.locator('button:has-text("Lưu đơn")').click()
        page.wait_for_timeout(800)
        loi_ui_text = form.locator('[role="alert"]').inner_text() if form.locator('[role="alert"]').count() else ""
        bc.ghi(
            "UI-03",
            "Nhập hạn giao quá khứ (2020) qua form Tạo đơn -> hiện thông báo lỗi tiếng Việt, không crash",
            bool(loi_ui_text) and ("BR-31" in loi_ui_text or "Hạn giao" in loi_ui_text or "hạn giao" in loi_ui_text),
            f"Thông báo hiển thị={loi_ui_text!r}",
            "Hiển thị thông báo lỗi tiếng Việt (BR-31) ngay trong hộp thoại, không crash",
            "Mở Tạo đơn -> nhập hạn giao 2020-01-01 -> bấm Lưu đơn",
            "Vua",
            "BR-31",
        )
        # Bấm Hủy đóng modal
        form.locator('button[type="button"]:has-text("Hủy")').click()

        # =====================================================================
        # 7.4 Bấm nhanh 2 lần nút Ghép & Chốt chuyến trên trang Chi tiết chuyến
        # =====================================================================
        # Tạo 1 xe + 1 tài xế + 1 chuyến LAP + 1 đơn CHO_GHEP sạch để bấm ghép & chốt trên UI
        _, d_xe_ui, _ = dp_api.raw(
            "POST",
            "/api/xe",
            {
                "bien_so": f"51W-{sfx}",
                "tai_trong_kg": 5000,
                "the_tich_m3": "20.00",
                "ktt_toan_bo_kg": 9000,
                "han_dang_kiem": "2028-12-31",
                "han_bao_hiem": "2028-12-31",
                "km_dong_ho": 5000,
            },
        )
        _, d_tx_ui, _ = dp_api.raw(
            "POST",
            "/api/tai-xe",
            {
                "ten_dang_nhap": f"txui_{sfx}",
                "ho_ten": f"Tài xế UI {sfx}",
                "mat_khau": "demo12345",
                "so_gplx": f"UITX{sfx.upper()}01",
                "hang_gplx": "C",
                "han_gplx": "2029-12-31",
                "sdt": "0944332211",
            },
        )
        _, d_ch_ui, _ = dp_api.raw(
            "POST",
            "/api/chuyen",
            {"tuyen_id": 5, "khoi_hanh_du_kien": iso_vn(now_vn() + timedelta(hours=3)), "xe_id": d_xe_ui["id"], "tai_xe_id": d_tx_ui["id"]},
        )
        ch_ui_id = d_ch_ui["id"]
        _, d_don_ui, _ = dp_api.raw(
            "POST",
            "/api/don",
            {
                "khach_hang_id": 1,
                "mo_ta": f"UIGhep-{sfx}",
                "kg": "1000.00",
                "m3": "4.00",
                "so_kien": 5,
                "nut_lay_id": 5,
                "dia_chi_lay": "10 CT",
                "sdt_lay": "0909666001",
                "nut_giao_id": 11,
                "dia_chi_giao": "20 AG",
                "nguoi_nhan": "Anh AG",
                "sdt_nhan": "0909666002",
                "han_giao": iso_vn(now_vn() + timedelta(days=2)),
            },
        )

        page.goto(f"{BASE_FE}/dieu-phoi/chuyen/{ch_ui_id}", wait_until="networkidle")
        page.wait_for_timeout(500)
        ghep_reqs = 0
        chot_reqs = 0

        def dem_chuyen_req(req):
            nonlocal ghep_reqs, chot_reqs
            if req.method == "POST" and f"/api/chuyen/{ch_ui_id}/ghep" in req.url:
                ghep_reqs += 1
            if req.method == "POST" and f"/api/chuyen/{ch_ui_id}/chot" in req.url:
                chot_reqs += 1

        page.on("request", dem_chuyen_req)
        # Bấm nhanh 2 lần nút Ghép đầu tiên trong khối Xếp hàng (nếu có)
        nut_ghep = page.locator('button:has-text("Ghép")').first
        if nut_ghep.count() > 0 and nut_ghep.is_visible():
            nut_ghep.dblclick()
            page.wait_for_timeout(1200)
            bc.ghi(
                "UI-04",
                "Bấm nhanh 2 lần nút Ghép đơn trên chi tiết chuyến",
                ghep_reqs == 1 and len(bag["pageerror"]) == 0,
                f"Số request POST /ghep={ghep_reqs}, pageerror={bag['pageerror']}",
                "Chỉ gửi 1 request ghép đơn, không lỗi JS",
                f"Mở /dieu-phoi/chuyen/{ch_ui_id} -> dblclick nút Ghép",
                "Vua",
                "UI chống bấm đúp",
            )
        else:
            bc.ghi("UI-04", "Bấm nhanh 2 lần nút Ghép đơn trên chi tiết chuyến", False, "Không thấy nút Ghép trên màn chi tiết chuyến", "Thấy nút Ghép cho đơn chờ ghép phù hợp", f"Mở /dieu-phoi/chuyen/{ch_ui_id}", "Vua", "UC-13")

        # Chấp nhận confirm nếu lãi âm rồi bấm nhanh 2 lần Chốt chuyến
        page.remove_listener("dialog", page._impl_obj._listeners if False else lambda *a: None)
        ctx_chot_dialogs = []

        def accept_dialog(d):
            ctx_chot_dialogs.append(d.message)
            d.accept()

        # Tạo page sạch để gán listener accept
        page2 = ctx.new_page()
        bag2 = {"console": [], "pageerror": [], "http5xx": []}
        gan_theo_doi(page2, bag2)
        page2.on("dialog", accept_dialog)
        chot_reqs2 = 0
        page2.on("request", lambda r: None)

        def dem_chot2(r):
            nonlocal chot_reqs2
            if r.method == "POST" and f"/api/chuyen/{ch_ui_id}/chot" in r.url:
                chot_reqs2 += 1

        page2.on("request", dem_chot2)
        page2.goto(f"{BASE_FE}/dieu-phoi/chuyen/{ch_ui_id}", wait_until="networkidle")
        nut_chot = page2.locator('button:has-text("Chốt chuyến")')
        nut_chot.dblclick()
        page2.wait_for_timeout(1500)
        _, ct_sau_chot, _ = dp_api.raw("GET", f"/api/chuyen/{ch_ui_id}")
        # Nếu lãi âm confirm, 1 luồng chốt gửi 2 request (lần 1 422 BR-52, lần 2 kèm xac_nhan_lai_am=true) -> tối đa 2 request là bình thường
        max_ok = 2 if ctx_chot_dialogs else 1
        bc.ghi(
            "UI-05",
            "Bấm nhanh 2 lần nút 'Chốt chuyến'",
            ct_sau_chot["trang_thai"] == "DA_CHOT" and chot_reqs2 <= max_ok and len(bag2["pageerror"]) == 0,
            f"trang_thai={ct_sau_chot['trang_thai']}, so_req_chot={chot_reqs2}, dialogs={ctx_chot_dialogs}, pageerror={bag2['pageerror']}",
            f"Chuyến chuyển sang DA_CHOT, tối đa {max_ok} request (không gửi lặp chồng chéo), không lỗi JS",
            f"Mở /dieu-phoi/chuyen/{ch_ui_id} -> dblclick nút Chốt chuyến",
            "Vua",
            "UC-15",
        )
        page2.close()

        # =====================================================================
        # 7.5 Hai tab cùng sửa 1 đơn -> kiểm tra ghi đè âm thầm (lost update)
        # =====================================================================
        _, d_don_2tab, _ = dp_api.raw(
            "POST",
            "/api/don",
            {
                "khach_hang_id": 1,
                "mo_ta": "Ban dau 2 tab",
                "kg": "100.00",
                "m3": "1.00",
                "so_kien": 2,
                "nut_lay_id": 5,
                "dia_chi_lay": "10 Tab Lay",
                "sdt_lay": "0909111000",
                "nut_giao_id": 11,
                "dia_chi_giao": "20 Tab Giao",
                "nguoi_nhan": "Anh Tab",
                "sdt_nhan": "0909222000",
                "han_giao": iso_vn(now_vn() + timedelta(days=3)),
            },
        )
        ma_2tab = d_don_2tab["ma_don"]
        id_2tab = d_don_2tab["id"]

        tab1 = ctx.new_page()
        tab2 = ctx.new_page()
        tab1.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="networkidle")
        tab2.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="networkidle")
        # Lọc đúng mã đơn ở cả 2 tab
        tab1.locator('input[placeholder*="Tìm mã đơn"]').fill(ma_2tab)
        tab2.locator('input[placeholder*="Tìm mã đơn"]').fill(ma_2tab)
        tab1.wait_for_timeout(600)
        tab2.wait_for_timeout(600)
        # Mở modal Sửa ở cả 2 tab cùng lúc
        tab1.locator("tr", has_text=ma_2tab).locator('button:has-text("Sửa")').click()
        tab2.locator("tr", has_text=ma_2tab).locator('button:has-text("Sửa")').click()
        tab1.locator("form.hop-thoai").wait_for(state="visible")
        tab2.locator("form.hop-thoai").wait_for(state="visible")

        # Tab 1 sửa kg -> 250 và Lưu
        tab1.locator("form.hop-thoai input[type='number']").nth(0).fill("250")
        tab1.locator('form.hop-thoai button:has-text("Lưu đơn")').click()
        tab1.wait_for_timeout(1000)

        # Tab 2 (vẫn giữ dữ liệu cũ kg=100) sửa kg -> 400 và Lưu
        tab2.locator("form.hop-thoai input[type='number']").nth(0).fill("400")
        tab2.locator('form.hop-thoai button:has-text("Lưu đơn")').click()
        tab2.wait_for_timeout(1000)
        tab2_loi = tab2.locator('form.hop-thoai [role="alert"]').inner_text() if tab2.locator('form.hop-thoai [role="alert"]').count() else ""
        _, don_sau_2tab, _ = dp_api.raw("GET", f"/api/don/{id_2tab}")
        bc.ghi(
            "UI-06",
            f"Hai tab cùng mở sửa đơn {ma_2tab}: Tab 1 sửa kg=250 rồi Tab 2 sửa kg=400 (kiểm phát hiện xung đột)",
            bool(tab2_loi),
            f"Tab 2 lưu thành công không cảnh báo xung đột (tab2_loi={tab2_loi!r}); giá trị cuối kg={don_sau_2tab['kg']} (ghi đè âm thầm sửa đổi của Tab 1)",
            "Cảnh báo xung đột / từ chối 409 khi dữ liệu đơn đã bị tab khác sửa trước đó (optimistic lock)",
            f"Mở 2 tab /dieu-phoi/don -> cùng bấm Sửa đơn {ma_2tab} -> Tab 1 đổi kg=250 Lưu -> Tab 2 đổi kg=400 Lưu",
            "Vua",
            "Concurrency / Lost update",
        )
        tab1.close()
        tab2.close()

        # =====================================================================
        # 7.6 F5 giữa chừng & nút Back trình duyệt
        # =====================================================================
        page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="networkidle")
        page.goto(f"{BASE_FE}/dieu-phoi/chuyen/{ch_ui_id}", wait_until="networkidle")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(400)
        sau_f5 = kiem_tran_ngang(page)
        page.go_back(wait_until="networkidle")
        page.wait_for_timeout(400)
        sau_back_url = page.url
        sau_back = kiem_tran_ngang(page)
        bc.ghi(
            "UI-07",
            "F5 giữa chừng trên chi tiết chuyến và bấm nút Back trình duyệt quay lại danh sách chuyến",
            sau_f5["textLen"] > 50 and "/dieu-phoi/chuyen" in sau_back_url and sau_back["textLen"] > 50 and len(bag["pageerror"]) == 0,
            f"Sau F5 textLen={sau_f5['textLen']}; sau Back url={sau_back_url}, textLen={sau_back['textLen']}, pageerror={bag['pageerror']}",
            "Không màn trắng, không lỗi JS, Back quay lại đúng /dieu-phoi/chuyen",
            f"/dieu-phoi/chuyen -> /dieu-phoi/chuyen/{ch_ui_id} -> F5 -> Back",
            "Vua",
            "UI navigation",
        )
        ctx.close()

        # =====================================================================
        # 7.7 Đăng nhập `taixe`, mở thẳng URL trang của vai trò khác (1440px & 390px)
        # =====================================================================
        ctx_tx = browser.new_context(viewport={"width": 390, "height": 844})
        page_tx = ctx_tx.new_page()
        bag_tx = {"console": [], "pageerror": [], "http5xx": []}
        gan_theo_doi(page_tx, bag_tx)
        dang_nhap_ui(page_tx, "taixe")

        forbidden_urls = [
            "/quan-ly/nguoi-dung",
            "/quan-ly/bang-gia",
            "/quan-ly/cau-hinh",
            "/dieu-phoi/don",
            "/dieu-phoi/chuyen",
            "/ke-toan/cong-no",
            "/ke-toan/quyet-toan",
            "/ke-toan/tam-ung",
        ]
        ket_qua_chuyen_huong = []
        for u in forbidden_urls:
            page_tx.goto(f"{BASE_FE}{u}", wait_until="networkidle")
            page_tx.wait_for_timeout(200)
            ket_qua_chuyen_huong.append((u, page_tx.url))
        tat_ca_bi_chan = all("/tai-xe" in final_u for _, final_u in ket_qua_chuyen_huong)
        bc.ghi(
            "UI-08",
            "Tài xế mở thẳng 8 URL của Quản lý / Điều phối / Kế toán",
            tat_ca_bi_chan and len(bag_tx["pageerror"]) == 0,
            f"Kết quả redirect={[(u, f.replace(BASE_FE, '')) for u, f in ket_qua_chuyen_huong]}, pageerror={bag_tx['pageerror']}",
            "Mọi URL vai trò khác đều chuyển hướng về /tai-xe/chuyen, không lộ dữ liệu, không lỗi JS",
            "Đăng nhập taixe -> mở thẳng /quan-ly/..., /dieu-phoi/..., /ke-toan/...",
            "Nghiem trong",
            "BR-57",
        )
        ctx_tx.close()

        # =====================================================================
        # 7.8 Quét bố cục / tràn ngang / lỗi console / màn trắng ở cả 1440px và 390px
        # =====================================================================
        pages_by_role = [
            ("quanly", ["/quan-ly/tong-quan", "/quan-ly/nguoi-dung", "/quan-ly/bang-gia", "/quan-ly/cau-hinh", "/quan-ly/cong-no", "/quan-ly/quyet-toan"]),
            ("dieuphoi", ["/dieu-phoi/chuyen", f"/dieu-phoi/chuyen/{ch_ui_id}", "/dieu-phoi/don", "/dieu-phoi/xe", "/dieu-phoi/tai-xe", "/dieu-phoi/khach-hang", "/dieu-phoi/tuyen"]),
            ("ketoan", ["/ke-toan/tong-quan", "/ke-toan/tam-ung", "/ke-toan/quyet-toan", "/ke-toan/cong-no", "/ke-toan/chi-phi-xe"]),
            ("taixe", ["/tai-xe/chuyen", "/tai-xe/chuyen/9", "/tai-khoan"]),
        ]
        # Trang công khai /tra-cuu và /dang-nhap ở 1440px và 390px
        for vp_name, vp in [("1440px", {"width": 1440, "height": 900}), ("390px", {"width": 390, "height": 844})]:
            ctx_pub = browser.new_context(viewport=vp)
            pg = ctx_pub.new_page()
            bag_pub = {"console": [], "pageerror": [], "http5xx": []}
            gan_theo_doi(pg, bag_pub)
            tran_pub = []
            for path in ["/dang-nhap", "/tra-cuu"]:
                pg.goto(f"{BASE_FE}{path}", wait_until="networkidle")
                pg.wait_for_timeout(300)
                m = kiem_tran_ngang(pg)
                if m["overflow"] or m["textLen"] < 20:
                    tran_pub.append({"path": path, **m})
            ma_ca = "UI-09" if vp_name == "1440px" else "UI-10"
            bc.ghi(
                ma_ca,
                f"Kiểm giao diện /dang-nhap & /tra-cuu ở màn {vp_name}",
                not tran_pub and not bag_pub["pageerror"] and not bag_pub["http5xx"],
                f"tran_hoac_trang={tran_pub}, console_err={bag_pub['console']}, pageerror={bag_pub['pageerror']}, 5xx={bag_pub['http5xx']}",
                "Không tràn ngang, không màn trắng, không lỗi console/5xx",
                f"Mở /dang-nhap và /tra-cuu ở viewport {vp_name}",
                "Nhe",
                "Responsive UI",
            )
            ctx_pub.close()

        idx = 11
        for role, urls in pages_by_role:
            for vp_name, vp in [("1440px", {"width": 1440, "height": 900}), ("390px", {"width": 390, "height": 844})]:
                c_r = browser.new_context(viewport=vp)
                pg = c_r.new_page()
                b_r = {"console": [], "pageerror": [], "http5xx": []}
                gan_theo_doi(pg, b_r)
                dang_nhap_ui(pg, role)
                van_de = []
                for path in urls:
                    pg.goto(f"{BASE_FE}{path}", wait_until="networkidle")
                    pg.wait_for_timeout(350)
                    m = kiem_tran_ngang(pg)
                    if m["overflow"] or m["textLen"] < 20:
                        van_de.append({"path": path, "sw": m["sw"], "vw": m["vw"], "textLen": m["textLen"], "tran": m["tran"]})
                # Lọc bỏ lỗi 401 vô hại lúc kiểm phiên trước đăng nhập nếu có
                console_that = [c for c in b_r["console"] if "401" not in c]
                ok = not van_de and not b_r["pageerror"] and not b_r["http5xx"] and not console_that
                bc.ghi(
                    f"UI-{idx:02d}",
                    f"Quét {len(urls)} trang của vai trò {role} ở màn {vp_name}",
                    ok,
                    f"overflow_or_blank={van_de}, console_err={console_that[:3]}, pageerror={b_r['pageerror'][:2]}, 5xx={b_r['http5xx'][:2]}",
                    "Không màn trắng, không tràn ngang, không lỗi console/JS/5xx",
                    f"Đăng nhập {role} ở {vp_name} -> lần lượt mở {urls}",
                    "Nhe" if (not b_r["pageerror"] and not b_r["http5xx"]) else "Nghiem trong",
                    "Responsive UI",
                )
                idx += 1
                c_r.close()

        browser.close()

    bc.luu_json("ket_qua_07.json")


if __name__ == "__main__":
    main()
