"""Phá thử giao diện 26/11 (chạy trên CSDL vứt đi qlvc_pha2, chỉ gọi localhost)."""

import random
import re

from playwright.sync_api import sync_playwright

B = "http://127.0.0.1:5173"
KQ = []


def ghi(muc, ten, dat, thay=""):
    KQ.append(bool(dat))
    print(("ĐẠT " if dat else "LỖI ") + f"[{muc}] {ten}" + (f" -> {thay}" if thay != "" else ""), flush=True)


def mo_cx(br, u=None, pc="pixel", vp=(1366, 768), giam=""):
    cx = br.new_context(viewport={"width": vp[0], "height": vp[1]}, locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    cx.add_init_script(
        f"localStorage.setItem('qlvc-phong-cach','{pc}');localStorage.setItem('qlvc-giam-chuyen-dong','{giam}')"
    )
    if u:
        r = cx.request.post(B + "/api/auth/dang-nhap", data={"ten_dang_nhap": u, "mat_khau": "demo12345"})
        assert r.ok, r.status
    pg = cx.new_page()
    loi = []
    pg.on("pageerror", lambda e: loi.append(str(e)[:200]))
    pg.on("console", lambda m: m.type == "error" and "status of 4" not in m.text and loi.append(m.text[:200]))
    pg.on("dialog", lambda d: (loi.append("ALERT " + d.message), d.dismiss()))
    return cx, pg, loi


SACH = "()=>({nen:document.querySelectorAll('.nen-mo').length, tran:getComputedStyle(document.body).overflow})"


def sach(pg):
    pg.wait_for_timeout(500)
    return pg.evaluate(SACH)


def them(pg):
    pg.get_by_role("button", name=re.compile("^(\\+ )?Thêm")).first.click()


def muc(ten, ham):
    try:
        ham()
    except Exception as e:  # một mục hỏng không chặn các mục sau
        ghi(ten, "kịch bản dừng giữa chừng", False, str(e).splitlines()[0][:200])


with sync_playwright() as p:
    br = p.chromium.launch()

    def hop(pc, giam):
        cx, pg, loi = mo_cx(br, "dieuphoi", pc, giam=giam)
        nhan = f"{pc or 'thường'}{' giảm-cđ' if giam else ''}"
        pg.goto(B + "/dieu-phoi/xe")
        pg.wait_for_load_state("networkidle")
        for i in range(25):
            them(pg)
            pg.wait_for_timeout(random.choice([0, 10, 60]))
            if i % 3 == 0:
                pg.keyboard.press("Escape")
            elif i % 3 == 1:
                pg.locator(".nen-mo:not(.dang-dong) .hop-thoai button", has_text="Hủy").click()
            else:
                pg.locator(".nen-mo:not(.dang-dong)").click(position={"x": 5, "y": 5})
        s = sach(pg)
        ghi("hộp", f"{nhan}: mở/đóng 25 lần không sót", s["nen"] == 0 and s["tran"] != "hidden", s)
        them(pg)
        pg.wait_for_timeout(250)
        for _ in range(8):
            pg.keyboard.press("Escape")
        s = sach(pg)
        ghi("hộp", f"{nhan}: Esc liên tục", s["nen"] == 0, s)
        pg.goto(B + "/dieu-phoi/don")
        pg.wait_for_load_state("networkidle")
        pg.goto(B + "/dieu-phoi/xe")
        pg.wait_for_load_state("networkidle")
        pg.locator(".canh nav a[href$='/don']").click()
        pg.wait_for_timeout(500)
        pg.locator(".canh nav a[href$='/xe']").click()
        pg.wait_for_timeout(500)
        them(pg)
        pg.wait_for_timeout(200)
        pg.evaluate("history.back()")
        s = sach(pg)
        ghi("hộp", f"{nhan}: bấm Back khi hộp đang mở không kẹt lớp phủ", s["nen"] == 0 and s["tran"] != "hidden", s)
        ghi("hộp", f"{nhan}: không lỗi JS", not loi, loi[:3] or "")
        cx.close()

    for pc, giam in [("pixel", ""), ("pixel", "bat"), ("", "")]:
        muc("hộp", lambda: hop(pc, giam))

    def gui_kep():
        cx, pg, loi = mo_cx(br, "dieuphoi")
        pg.goto(B + "/dieu-phoi/khach-hang")
        pg.wait_for_load_state("networkidle")
        gui = []
        pg.on("request", lambda r: r.method == "POST" and "/api/khach-hang" in r.url and gui.append(r.url))
        them(pg)
        pg.wait_for_timeout(300)
        o = pg.locator(".hop-thoai input, .hop-thoai textarea")
        gia = ["<img src=x onerror=alert(1)> Pha", "0909000999", "12 Duong Thu"]
        for i in range(min(o.count(), 3)):
            o.nth(i).fill(gia[i])
        nut = pg.locator(".hop-thoai button:not([type=button]):not(.phu)").last
        box = nut.bounding_box()
        for _ in range(6):
            pg.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        for _ in range(4):
            pg.keyboard.press("Enter")
        pg.wait_for_timeout(1500)
        ghi("gửi", "bấm Lưu 6 lần + Enter 4 lần chỉ gửi 1 yêu cầu", len(gui) == 1, f"{len(gui)} yêu cầu")
        ghi("xss", "tên có thẻ HTML hiện thành chữ, không chạy",
            not any("ALERT" in x for x in loi) and pg.locator("img[src=x]").count() == 0, loi[:2] or "")
        print("     hộp sau khi lưu:", sach(pg), "(mở lại hộp do Enter vào nút Thêm là bình thường)")
        cx.close()

    muc("gửi", gui_kep)

    def mat_khau_va_phien():
        cx, pg, loi = mo_cx(br, "quanly")
        pg.goto(B + "/quan-ly/nguoi-dung")
        pg.wait_for_load_state("networkidle")
        them(pg)
        pg.wait_for_timeout(300)
        mk = pg.locator(".hop-thoai input[type=password]")
        mk.first.fill("MatKhauThu123")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(500)
        con = pg.evaluate("[...document.querySelectorAll('input')].filter(i=>i.value==='MatKhauThu123').length")
        ghi("mk", "mật khẩu không sót trong trang sau khi đóng hộp", con == 0, con)
        them(pg)
        pg.wait_for_timeout(300)
        o = pg.locator(".hop-thoai input")
        for i in range(o.count()):
            kieu = o.nth(i).get_attribute("type")
            if kieu in (None, "text", "password"):
                o.nth(i).fill("MatKhauThu123" if kieu == "password" else f"phathu{i}")
        cx.clear_cookies()
        pg.locator(".hop-thoai button:not([type=button]):not(.phu)").last.click()
        pg.wait_for_timeout(1500)
        s = sach(pg)
        ghi("phiên", "hết phiên khi đang lưu: về đăng nhập, không kẹt lớp phủ",
            "dang-nhap" in pg.url and s["nen"] == 0 and s["tran"] != "hidden", (pg.url.replace(B, ""), s))
        la = [x for x in loi if "401" not in x]
        ghi("phiên", "không lỗi JS", not la, la[:3] or "")
        cx.close()

    muc("mk/phiên", mat_khau_va_phien)

    def dang_nhap(vp):
        cx, pg, loi = mo_cx(br, vp=vp)
        pg.goto(B + "/dang-nhap")
        pg.wait_for_timeout(800)
        pg.locator(".dn-bam-logo").dblclick()
        for _ in range(14):
            n = pg.get_by_role("button", name=re.compile("Xé phiếu|In phiếu"))
            if n.count():
                try:
                    n.nth(random.randrange(n.count())).click(force=True, timeout=1000)
                except Exception:
                    pass  # nút vừa bị gỡ giữa lúc xé
            pg.wait_for_timeout(random.choice([20, 120, 400]))
        pg.wait_for_timeout(1500)
        st = pg.evaluate(
            "[document.querySelectorAll('.dn-giay').length, document.querySelectorAll('.dn-giay.xe').length,"
            " document.querySelector('.dn-may-than').getAnimations().length,"
            " document.documentElement.scrollWidth-innerWidth]"
        )
        ghi("đn", f"{vp[0]}: bấm lia in/xé phiếu còn đúng 1 phiếu, không kẹt",
            st[0] == 1 and st[1] == 0 and st[2] == 0 and st[3] <= 1, st)
        if not pg.get_by_label("Tên đăng nhập").count():
            pg.get_by_role("button", name=re.compile("Nhân viên")).first.click()
            pg.wait_for_timeout(1200)
        pg.get_by_label("Tên đăng nhập").fill("dieuphoi")
        pg.get_by_label("Mật khẩu").fill("sai-mat-khau")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(900)
        pg.get_by_label("Mật khẩu").fill("demo12345")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(2500)
        ghi("đn", f"{vp[0]}: sai rồi đúng mật khẩu vẫn vào được", "dieu-phoi" in pg.url, pg.url.replace(B, ""))
        la = [x for x in loi if "401" not in x]
        ghi("đn", f"{vp[0]}: không lỗi JS", not la, la[:3] or "")
        cx.close()

    for vp in [(1366, 768), (390, 844)]:
        muc("đn", lambda: dang_nhap(vp))

    def xep_hang():
        cx, pg, loi = mo_cx(br, "dieuphoi")
        pg.goto(B + "/dieu-phoi/chuyen")
        pg.wait_for_selector(".xe-tx")
        h = pg.get_by_role("link", name=re.compile(r"^CH-\d+-01$")).first.get_attribute("href")
        ca = {"rỗng": [], "bằng 0": [0, 0], "tí hon": [0.01] * 3, "30 đơn nhỏ": [0.05] * 30,
              "đầy khít": [3.5, 3.5, 7], "vượt sức chứa": [20, 5], "1 đơn kín": [14]}
        for ten, ds in ca.items():
            def sua(route, request, ds=ds):
                r = route.fetch()
                j = r.json()
                mau = j["don"][0]
                j["don"] = [{**mau, "id": 9000 + i, "ma_don": f"DH-T{i}", "m3": str(v)} for i, v in enumerate(ds)]
                j["the_tich"] = {**j["the_tich"], "da_dung_m3": str(sum(ds)), "toi_da_m3": "14"}
                route.fulfill(response=r, json=j)

            pg.unroute_all()
            pg.route(re.compile(r"/api/chuyen/\d+$"), sua)
            loi.clear()
            pg.goto(B + h)
            pg.wait_for_selector(".xh-xe svg")
            pg.wait_for_timeout(700)
            hong = pg.evaluate(
                "[...document.querySelectorAll('.xh-xe svg *')].filter(e=>[...e.attributes].some(a=>"
                "/NaN|Infinity/.test(a.value)||(/^(width|height)$/.test(a.name)&&+a.value<0))).length"
            )
            # mép phải của khối xa nhất so với mép phải lòng thùng (container)
            tran = pg.evaluate(
                "(()=>{const t=document.querySelector('.xh-px-vien-loi').getBoundingClientRect().right;"
                "return Math.round(Math.max(0,...[...document.querySelectorAll('.xh-khoi .xh-o')]"
                ".map(r=>r.getBoundingClientRect().right-t)))})()"
            )
            ghi("xếp", f"{ten}: không NaN/âm, khối không tràn thùng",
                hong == 0 and (ten == "vượt sức chứa" or tran <= 0) and not loi,
                f"hỏng={hong} tràn={tran}px {loi[:2]}")
        cx.close()

    muc("xếp", xep_hang)
    br.close()

print("TONG", len(KQ), "DAT", sum(KQ), "LOI", len(KQ) - sum(KQ))
