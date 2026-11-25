"""Mục 03: Bấm lặp, nhấp nháy và hiệu ứng đóng dấu (ĐÃ LƯU xanh / ĐÃ HỦY đỏ) trên PIXEL.

Thử bấm nhanh 2–5 lần các nút: Lưu đơn, Ghép, Gỡ, Chốt, Hủy chuyến, Đăng nhập, Đổi mật khẩu.
Kiểm tra:
- Không tạo trùng request / dữ liệu
- Nút bị khóa (disabled) trong lúc đang gửi
- Hiệu ứng đóng dấu (ĐÃ LƯU xanh / ĐÃ HỦY đỏ):
  * KHÔNG hiện khi bấm Hủy / Thôi / Đóng hộp thoại (hiện là SAI)
  * KHÔNG hiện khi lưu lỗi (hiện là SAI)
  * KHÔNG hiện lặp nhiều lần cho 1 thao tác

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_03_bam_lap_dong_dau.py
"""

from __future__ import annotations

import os
import sys
import time
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    VIEWPORT_DESKTOP,
    BaoCaoScript,
    cho_yen,
    dang_nhap_api,
    dang_nhap_nhanh,
    lay_khach_hang_dau,
    ma_ngau_nhien,
    mo_khung_dang_nhap_pixel,
    mo_trang_moi,
    now_vn,
    tao_chuyen_lap_pha,
    tao_context_pixel,
    tao_don_pha,
    tao_tai_khoan_pha,
    tim_cap_nut_co_gia,
)

# Theo dõi mọi lần xuất hiện con dấu ĐÃ LƯU / ĐÃ HỦY bằng MutationObserver ngay cả khi chỉ hiện < 500 ms
JS_GAN_THEO_DOI_DAU = """() => {
  window.__phaStamps = [];
  if (window.__phaStampObs) {
    try { window.__phaStampObs.disconnect(); } catch (e) {}
  }
  const mauDau = /ĐÃ\\s*LƯU|ĐÃ\\s*HỦY|ĐÃ\\s*HUỶ|DA\\s*LUU|DA\\s*HUY/i;
  const ghiNhan = (el) => {
    if (!el || el.nodeType !== 1) return;
    const txt = (el.innerText || el.textContent || '').trim();
    const cls = (el.className || '').toString();
    if (!mauDau.test(txt) && !/px-dau|dong-dau|stamp/i.test(cls)) return;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return;
    const shortTxt = txt.replace(/\\s+/g, ' ').slice(0, 60);
    // Tránh ghi trùng cùng 1 node trong vòng 150ms
    const now = Date.now();
    const trung = window.__phaStamps.some(s => s.text === shortTxt && (now - s.t) < 150 && s.cls === cls);
    if (!trung) {
      window.__phaStamps.push({
        t: now,
        text: shortTxt,
        cls: cls.slice(0, 60),
        color: st.color,
        bg: st.backgroundColor,
        borderColor: st.borderColor,
      });
    }
  };
  const obs = new MutationObserver((muts) => {
    for (const m of muts) {
      if (m.type === 'childList') {
        for (const n of m.addedNodes) {
          if (n.nodeType !== 1) continue;
          ghiNhan(n);
          for (const c of n.querySelectorAll ? n.querySelectorAll('*') : []) {
            ghiNhan(c);
          }
        }
      } else if (m.type === 'attributes') {
        ghiNhan(m.target);
      }
    }
  });
  obs.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style', 'data-trang-thai'] });
  window.__phaStampObs = obs;
}"""


def reset_dau(page: Page) -> None:
    page.evaluate(JS_GAN_THEO_DOI_DAU)


def doc_dau(page: Page) -> list[dict]:
    try:
        return page.evaluate("() => window.__phaStamps || []")
    except Exception:
        return []


def bam_nhanh(page: Page, loc, so_lan: int = 4) -> dict:
    """Bấm nhanh liên tiếp so_lan lần và ghi nhận nút có từng bị disabled trong lúc gửi hay không."""
    tung_khoa = False
    da_bam = 0
    for _ in range(so_lan):
        try:
            if not loc.is_visible():
                break
            if loc.is_disabled():
                tung_khoa = True
                break
            loc.click(timeout=1200, no_wait_after=True)
            da_bam += 1
            page.wait_for_timeout(35)
            try:
                if loc.is_visible() and loc.is_disabled():
                    tung_khoa = True
            except Exception:
                pass
        except Exception:
            break
    return {"da_bam": da_bam, "tung_khoa": tung_khoa}


def gan_tre_post(page: Page, path_sub: str, tre_ms: int = 350):
    """Thêm độ trễ ngắn không chặn luồng (yield greenlet) cho POST để các cú bấm lặp rơi vào lúc đang gửi."""
    def handler(route):
        try:
            if route.request.method == "POST" and path_sub in route.request.url:
                page.wait_for_timeout(tre_ms)
            route.continue_()
        except Exception:
            pass

    page.route(f"**{path_sub}**", handler)
    return handler


def main() -> None:
    bc = BaoCaoScript(3, "Bấm lặp, nhấp nháy & hiệu ứng đóng dấu (ĐÃ LƯU / ĐÃ HỦY)", "ket_qua_03.json")

    api_dp = dang_nhap_api("dieuphoi")
    api_ql = dang_nhap_api("quanly")
    khach_id = lay_khach_hang_dau(api_dp)
    cap_nut = tim_cap_nut_co_gia(api_dp)

    # Chuẩn bị chuyến LAP + 2 đơn PHA- cho các ca Ghép / Gỡ / Chốt / Hủy
    chuyen_1, _, cap_ch1 = tao_chuyen_lap_pha(api_dp, tai_trong_kg=5000, the_tich_m3="20.00", gio_them=5)
    don_ghep = tao_don_pha(api_dp, khach_id, cap_ch1[0], cap_ch1[1], kg="500.00", m3="2.00", nhan="BAM-LAP")
    chuyen_huy, _, _ = tao_chuyen_lap_pha(api_dp, tai_trong_kg=4000, the_tich_m3="16.00", gio_them=8)
    user_pha, pw_pha, _ = tao_tai_khoan_pha(api_ql, vai_tro="DIEU_PHOI")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx, che_do_dialog="accept")
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")

                # 1. Bấm Hủy/Thôi/Đóng trên hộp thoại -> KHÔNG được hiện đóng dấu ĐÃ HỦY hay ĐÃ LƯU
                def test_dong_hop_khong_dong_dau():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    reset_dau(page)
                    page.locator('button:has-text("Tạo đơn")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=5000)
                    form.locator('button[type="button"]:has-text("Hủy")').click()
                    page.wait_for_timeout(700)
                    dau_1 = doc_dau(page)

                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    reset_dau(page)
                    page.locator('button:has-text("Lập chuyến")').first.click()
                    form2 = page.locator("form.hop-thoai").first
                    form2.wait_for(state="visible", timeout=5000)
                    form2.locator('button[type="button"]:has-text("Hủy")').click()
                    page.wait_for_timeout(700)
                    dau_2 = doc_dau(page)

                    tat_ca = dau_1 + dau_2
                    if tat_ca:
                        return False, f"SAI: Đóng/Hủy form vẫn hiện đóng dấu: {tat_ca}", "Vừa"
                    return True, "Bấm Hủy đóng form Tạo đơn & Lập chuyến không hiện đóng dấu giả", ""

                bc.chay_ca(
                    "BL01_HUY_FORM_KHONG_DAU",
                    "Bấm Hủy đóng form Tạo đơn & Lập chuyến KHÔNG được hiện dấu ĐÃ HỦY / ĐÃ LƯU",
                    test_dong_hop_khong_dong_dau,
                    page=page,
                    tai_hien="Mở form Tạo đơn -> bấm Hủy; mở form Lập chuyến -> bấm Hủy",
                    mong_doi="Không hiện hiệu ứng đóng dấu ĐÃ HỦY hay ĐÃ LƯU khi chỉ đóng form",
                )

                # 2. Lưu đơn LỖI (hạn giao quá khứ) -> KHÔNG được hiện đóng dấu ĐÃ LƯU
                def test_luu_loi_khong_dong_dau():
                    mon.reset()
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    reset_dau(page)
                    page.locator('button:has-text("Tạo đơn")').first.click()
                    form = page.locator("form.hop-thoai").first
                    form.wait_for(state="visible", timeout=5000)
                    selects = form.locator("select")
                    selects.nth(0).select_option(str(khach_id))
                    nums = form.locator('input[type="number"]')
                    nums.nth(0).fill("100")
                    nums.nth(1).fill("1")
                    nums.nth(2).fill("2")
                    selects.nth(1).select_option(str(cap_nut[0]))
                    selects.nth(2).select_option(str(cap_nut[1]))
                    form.locator("label", has_text="Mô tả hàng").locator("input").fill(f"PHA-LoiDau-{ma_ngau_nhien(4)}")
                    form.locator("label", has_text="Địa chỉ lấy").locator("input").fill("10 PHA")
                    form.locator("label", has_text="SĐT lấy").locator("input").fill("0909111222")
                    form.locator("label", has_text="Địa chỉ giao").locator("input").fill("20 PHA")
                    form.locator("label", has_text="Người nhận").locator("input").fill("PHA Test")
                    form.locator("label", has_text="SĐT nhận").locator("input").fill("0909333444")
                    form.locator("label", has_text="Hạn giao").locator("input").fill("2020-01-01T10:00")
                    page.wait_for_function(
                        "() => !document.querySelector('form.hop-thoai button:not([type=\"button\"])')?.disabled",
                        timeout=6000,
                    )
                    form.locator('button:has-text("Lưu đơn")').click()
                    page.wait_for_timeout(900)
                    dau = doc_dau(page)
                    form.locator('button[type="button"]:has-text("Hủy")').click()
                    if dau:
                        return False, f"SAI: Lưu đơn thất bại (422) nhưng vẫn hiện đóng dấu: {dau}", "Vừa"
                    return True, "Lưu đơn lỗi không hiện hiệu ứng đóng dấu", ""

                bc.chay_ca(
                    "BL02_LUU_LOI_KHONG_DAU",
                    "Lưu đơn thất bại (hạn giao 2020) KHÔNG được hiện đóng dấu ĐÃ LƯU",
                    test_luu_loi_khong_dong_dau,
                    page=page,
                    tai_hien="Tạo đơn -> điền hạn giao 2020-01-01 -> bấm Lưu đơn",
                    mong_doi="Hiện lỗi BR-31, tuyệt đối không đóng dấu ĐÃ LƯU",
                )

                # 3. Bấm nhanh 4 lần nút Lưu đơn (có trễ POST 350ms)
                def test_bam_lap_luu_don():
                    mon.reset()
                    mon.ghi_requests = True
                    _, truoc, _ = api_dp.raw("GET", "/api/don?so_dong=1")
                    tong_truoc = truoc["tong"]
                    page.goto(f"{BASE_FE}/dieu-phoi/don", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=400)
                    handler = gan_tre_post(page, "/api/don", tre_ms=350)
                    try:
                        reset_dau(page)
                        page.locator('button:has-text("Tạo đơn")').first.click()
                        form = page.locator("form.hop-thoai").first
                        form.wait_for(state="visible", timeout=5000)
                        selects = form.locator("select")
                        selects.nth(0).select_option(str(khach_id))
                        nums = form.locator('input[type="number"]')
                        nums.nth(0).fill("80")
                        nums.nth(1).fill("1")
                        nums.nth(2).fill("2")
                        selects.nth(1).select_option(str(cap_nut[0]))
                        selects.nth(2).select_option(str(cap_nut[1]))
                        sfx = ma_ngau_nhien(5)
                        form.locator("label", has_text="Mô tả hàng").locator("input").fill(f"PHA-BamLap-{sfx}")
                        form.locator("label", has_text="Địa chỉ lấy").locator("input").fill(f"10 PHA {sfx}")
                        form.locator("label", has_text="SĐT lấy").locator("input").fill("0909111222")
                        form.locator("label", has_text="Địa chỉ giao").locator("input").fill(f"20 PHA {sfx}")
                        form.locator("label", has_text="Người nhận").locator("input").fill("PHA BamLap")
                        form.locator("label", has_text="SĐT nhận").locator("input").fill("0909333444")
                        han_local = (now_vn() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
                        form.locator("label", has_text="Hạn giao").locator("input").fill(han_local)
                        page.wait_for_function(
                            "() => !document.querySelector('form.hop-thoai button:not([type=\"button\"])')?.disabled",
                            timeout=6000,
                        )
                        btn_luu = form.locator('button:has-text("Lưu đơn")')
                        kq_bam = bam_nhanh(page, btn_luu, so_lan=4)
                        page.wait_for_timeout(1200)
                    finally:
                        page.unroute("**/api/don**", handler)
                        mon.ghi_requests = False

                    post_don = [u for m, u in mon.requests if m == "POST" and u.rstrip("/").endswith("/api/don")]
                    _, sau, _ = api_dp.raw("GET", "/api/don?so_dong=1")
                    tao_them = sau["tong"] - tong_truoc
                    dau = doc_dau(page)
                    van_de = []
                    if len(post_don) != 1 or tao_them != 1:
                        van_de.append(f"Gửi trùng hoặc sai số đơn: POST={len(post_don)}, tạo thêm={tao_them}")
                    if not kq_bam["tung_khoa"]:
                        van_de.append("Nút Lưu đơn không bị khóa (disabled) trong lúc gửi")
                    if len(dau) > 1:
                        van_de.append(f"Đóng dấu hiện nhiều lần ({len(dau)}): {dau}")
                    if any("HỦY" in d["text"].upper() or "HUỶ" in d["text"].upper() for d in dau):
                        van_de.append(f"Lưu đơn lại hiện dấu HỦY: {dau}")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de)
                        if van_de
                        else f"POST={len(post_don)}, tạo thêm={tao_them}, khóa nút={kq_bam['tung_khoa']}, dấu={len(dau)}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL03_LUU_DON_LAP",
                    "Bấm nhanh 4 lần nút Lưu đơn: chống trùng, khóa nút, đóng dấu ĐÃ LƯU tối đa 1 lần",
                    test_bam_lap_luu_don,
                    page=page,
                    tai_hien="Tạo đơn PHA- -> điền đủ -> bấm nhanh 4 lần nút Lưu đơn (POST trễ 350ms)",
                    mong_doi="Chỉ 1 POST /api/don, tạo đúng 1 đơn, nút bị disabled lúc gửi, đóng dấu hiện ≤ 1 lần",
                )

                # 4. Bấm nhanh 4 lần Ghép đơn trên chi tiết chuyến
                def test_bam_lap_ghep():
                    mon.reset()
                    mon.ghi_requests = True
                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen/{chuyen_1['id']}", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=500)
                    handler = gan_tre_post(page, "/ghep", tre_ms=350)
                    try:
                        reset_dau(page)
                        the_don = page.locator(".xh-cho li", has_text=don_ghep["ma_don"]).first
                        btn_ghep = (
                            the_don.locator('button:has-text("Ghép")').first
                            if the_don.count() > 0
                            else page.locator('button:has-text("Ghép vào xe")').first
                        )
                        btn_ghep.wait_for(state="visible", timeout=6000)
                        kq_bam = bam_nhanh(page, btn_ghep, so_lan=4)
                        page.wait_for_timeout(1200)
                    finally:
                        page.unroute("**/ghep**", handler)
                        mon.ghi_requests = False

                    post_ghep = [u for m, u in mon.requests if m == "POST" and "/ghep" in u]
                    dau = doc_dau(page)
                    van_de = []
                    if len(post_ghep) != 1:
                        van_de.append(f"Gửi {len(post_ghep)} request POST /ghep (phải là 1)")
                    if not kq_bam["tung_khoa"]:
                        van_de.append("Nút Ghép không bị disabled trong lúc gửi")
                    if len(dau) > 1:
                        van_de.append(f"Đóng dấu hiện nhiều lần ({len(dau)}): {dau}")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de) if van_de else f"POST /ghep=1, khóa nút={kq_bam['tung_khoa']}, dấu={dau}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL04_GHEP_DON_LAP",
                    "Bấm nhanh 4 lần nút Ghép vào xe trên chi tiết chuyến",
                    test_bam_lap_ghep,
                    page=page,
                    tai_hien=f"Mở /dieu-phoi/chuyen/{chuyen_1['id']} -> bấm nhanh 4 lần nút Ghép vào xe",
                    mong_doi="Chỉ 1 POST /ghep, nút bị khóa khi đang gửi, không lặp đóng dấu",
                )

                # 5. Bấm nhanh 4 lần Gỡ đơn (bấm khối trong SVG -> Gỡ khỏi xe)
                def test_bam_lap_go():
                    mon.reset()
                    mon.ghi_requests = True
                    handler = gan_tre_post(page, "/go", tre_ms=350)
                    try:
                        reset_dau(page)
                        khoi = page.locator(".xh-khoi").first
                        khoi.wait_for(state="visible", timeout=6000)
                        khoi.click()
                        btn_go = page.locator('button:has-text("Gỡ khỏi xe")').first
                        btn_go.wait_for(state="visible", timeout=5000)
                        kq_bam = bam_nhanh(page, btn_go, so_lan=4)
                        page.wait_for_timeout(1200)
                    finally:
                        page.unroute("**/go**", handler)
                        mon.ghi_requests = False

                    post_go = [u for m, u in mon.requests if m == "POST" and "/go" in u]
                    dau = doc_dau(page)
                    van_de = []
                    if len(post_go) != 1:
                        van_de.append(f"Gửi {len(post_go)} request POST /go (phải là 1)")
                    if len(dau) > 1:
                        van_de.append(f"Đóng dấu hiện nhiều lần ({len(dau)}): {dau}")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de) if van_de else f"POST /go=1, khóa nút={kq_bam['tung_khoa']}, dấu={dau}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL05_GO_DON_LAP",
                    "Bấm nhanh 4 lần nút Gỡ khỏi xe",
                    test_bam_lap_go,
                    page=page,
                    tai_hien=f"Mở /dieu-phoi/chuyen/{chuyen_1['id']} -> chọn khối -> bấm nhanh 4 lần Gỡ khỏi xe",
                    mong_doi="Chỉ 1 POST /go, không lỗi JS, không đóng dấu lặp",
                )

                # 6. Bấm nhanh 4 lần Chốt chuyến
                def test_bam_lap_chot():
                    mon.reset()
                    mon.ghi_requests = True
                    # Ghép lại đơn để chốt có đơn (hoặc chạy rỗng đều được vì che_do_dialog='accept')
                    api_dp.raw("POST", f"/api/chuyen/{chuyen_1['id']}/ghep", {"don_ids": [don_ghep["id"]]})
                    page.reload(wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=500)
                    handler = gan_tre_post(page, "/chot", tre_ms=350)
                    try:
                        reset_dau(page)
                        btn_chot = page.locator('button:has-text("Chốt chuyến")').first
                        btn_chot.wait_for(state="visible", timeout=6000)
                        kq_bam = bam_nhanh(page, btn_chot, so_lan=4)
                        page.wait_for_timeout(1500)
                    finally:
                        page.unroute("**/chot**", handler)
                        mon.ghi_requests = False

                    post_chot = [u for m, u in mon.requests if m == "POST" and "/chot" in u]
                    _, ct, _ = api_dp.raw("GET", f"/api/chuyen/{chuyen_1['id']}")
                    # Nếu có confirm lãi âm (BR-52), 1 lượt chốt gửi 2 POST là hợp lệ
                    toi_da = 2 if mon.dialogs else 1
                    dau = doc_dau(page)
                    van_de = []
                    if ct.get("trang_thai") != "DA_CHOT":
                        van_de.append(f"Chuyến không chuyển sang DA_CHOT (hiện {ct.get('trang_thai')})")
                    if len(post_chot) > toi_da:
                        van_de.append(f"Gửi lặp {len(post_chot)} POST /chot (tối đa {toi_da})")
                    if len(dau) > 1:
                        van_de.append(f"Đóng dấu hiện nhiều lần ({len(dau)}): {dau}")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de)
                        if van_de
                        else f"DA_CHOT OK, POST /chot={len(post_chot)}, khóa nút={kq_bam['tung_khoa']}, dấu={dau}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL06_CHOT_CHUYEN_LAP",
                    "Bấm nhanh 4 lần nút Chốt chuyến",
                    test_bam_lap_chot,
                    page=page,
                    tai_hien=f"Mở /dieu-phoi/chuyen/{chuyen_1['id']} -> bấm nhanh 4 lần Chốt chuyến",
                    mong_doi="Chuyến sang DA_CHOT, không gửi POST lặp chồng chéo, đóng dấu ≤ 1 lần",
                )

                # 7. Bấm nhanh 4 lần Xác nhận hủy chuyến -> kiểm tra dấu ĐÃ HỦY (đỏ), không trùng request
                def test_bam_lap_huy_chuyen():
                    mon.reset()
                    mon.ghi_requests = True
                    page.goto(f"{BASE_FE}/dieu-phoi/chuyen/{chuyen_huy['id']}", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page, ms=500)
                    handler = gan_tre_post(page, "/huy", tre_ms=350)
                    try:
                        reset_dau(page)
                        page.locator('button:has-text("Hủy chuyến")').first.click()
                        # Kiểm ngay sau khi mở form hủy (chưa xác nhận) KHÔNG được hiện dấu ĐÃ HỦY!
                        page.wait_for_timeout(300)
                        dau_som = doc_dau(page)
                        page.locator("label", has_text="Lý do hủy").locator("input").fill("PHA-Test bấm lặp hủy")
                        btn_xn = page.locator('button:has-text("Xác nhận hủy")').first
                        kq_bam = bam_nhanh(page, btn_xn, so_lan=4)
                        page.wait_for_timeout(1200)
                    finally:
                        page.unroute("**/huy**", handler)
                        mon.ghi_requests = False

                    post_huy = [u for m, u in mon.requests if m == "POST" and "/huy" in u]
                    dau_sau = doc_dau(page)
                    van_de = []
                    if dau_som:
                        van_de.append(f"SAI: Mới bấm 'Hủy chuyến' mở ô nhập lý do đã hiện dấu: {dau_som}")
                    if len(post_huy) != 1:
                        van_de.append(f"Gửi {len(post_huy)} POST /huy (phải là 1)")
                    if len(dau_sau) > 1:
                        van_de.append(f"Đóng dấu hiện nhiều lần ({len(dau_sau)}): {dau_sau}")
                    if any("LƯU" in d["text"].upper() for d in dau_sau):
                        van_de.append(f"Hủy chuyến lại hiện dấu ĐÃ LƯU: {dau_sau}")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de)
                        if van_de
                        else f"POST /huy=1, khóa nút={kq_bam['tung_khoa']}, dấu={dau_sau}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL07_HUY_CHUYEN_LAP",
                    "Bấm nhanh 4 lần Xác nhận hủy chuyến & kiểm dấu ĐÃ HỦY",
                    test_bam_lap_huy_chuyen,
                    page=page,
                    tai_hien=f"Mở /dieu-phoi/chuyen/{chuyen_huy['id']} -> Hủy chuyến -> điền lý do -> bấm nhanh 4 lần Xác nhận hủy",
                    mong_doi="Chưa xác nhận không hiện dấu; xác nhận gửi đúng 1 POST /huy; dấu ĐÃ HỦY không lặp/không nhầm ĐÃ LƯU",
                )
            finally:
                ctx.close()

            # 8 & 9. Bấm lặp Đăng nhập và Đổi mật khẩu (trên tài khoản PHA- riêng)
            ctx_auth = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page_a, mon_a = mo_trang_moi(ctx_auth)
            try:
                def test_bam_lap_dang_nhap():
                    mon_a.reset()
                    mon_a.ghi_requests = True
                    page_a.goto(f"{BASE_FE}/dang-nhap", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_a, ms=300)
                    mo_khung_dang_nhap_pixel(page_a)
                    handler = gan_tre_post(page_a, "/api/auth/dang-nhap", tre_ms=350)
                    try:
                        page_a.locator('input[autocomplete="username"]').first.fill(user_pha)
                        page_a.locator('input[autocomplete="current-password"]').first.fill(pw_pha)
                        btn_dn = page_a.locator('button:has-text("Đăng nhập")').first
                        kq_bam = bam_nhanh(page_a, btn_dn, so_lan=5)
                        page_a.wait_for_url(lambda u: "/dang-nhap" not in u, timeout=12000)
                        cho_yen(page_a, ms=500)
                    finally:
                        page_a.unroute("**/api/auth/dang-nhap**", handler)
                        mon_a.ghi_requests = False

                    post_dn = [u for m, u in mon_a.requests if m == "POST" and "/dang-nhap" in u]
                    van_de = []
                    if len(post_dn) != 1:
                        van_de.append(f"Gửi {len(post_dn)} request POST /api/auth/dang-nhap (phải là 1)")
                    if not kq_bam["tung_khoa"]:
                        van_de.append("Nút Đăng nhập không bị khóa trong lúc gửi")
                    return (
                        not van_de and not mon_a.page_errors,
                        " | ".join(van_de) if van_de else f"POST đăng nhập=1, khóa nút={kq_bam['tung_khoa']}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL08_DANG_NHAP_LAP",
                    f"Bấm nhanh 5 lần nút Đăng nhập (tài khoản {user_pha})",
                    test_bam_lap_dang_nhap,
                    page=page_a,
                    tai_hien=f"Mở /dang-nhap -> điền {user_pha} -> bấm nhanh 5 lần Đăng nhập",
                    mong_doi="Chỉ gửi 1 POST /api/auth/dang-nhap, nút bị khóa khi gửi",
                )

                def test_bam_lap_doi_mk():
                    mon_a.reset()
                    mon_a.ghi_requests = True
                    page_a.goto(f"{BASE_FE}/tai-khoan", wait_until="domcontentloaded", timeout=15000)
                    cho_yen(page_a, ms=400)
                    reset_dau(page_a)
                    handler = gan_tre_post(page_a, "/doi-mat-khau", tre_ms=350)
                    try:
                        form = page_a.locator("form.tk-mk").first
                        form.wait_for(state="visible", timeout=6000)
                        mk_moi = "PhaDoiMk2026!"
                        form.locator("label", has_text="Mật khẩu hiện tại").locator("input").fill(pw_pha)
                        form.locator("label", has_text="Mật khẩu mới").first.locator("input").fill(mk_moi)
                        form.locator("label", has_text="Nhập lại mật khẩu mới").locator("input").fill(mk_moi)
                        btn = form.locator('button:has-text("Đổi mật khẩu")')
                        kq_bam = bam_nhanh(page_a, btn, so_lan=5)
                        page_a.wait_for_timeout(1200)
                    finally:
                        page_a.unroute("**/doi-mat-khau**", handler)
                        mon_a.ghi_requests = False

                    post_mk = [u for m, u in mon_a.requests if m == "POST" and "mat-khau" in u]
                    dau = doc_dau(page_a)
                    van_de = []
                    if len(post_mk) != 1:
                        van_de.append(f"Gửi {len(post_mk)} POST đổi mật khẩu (phải là 1)")
                    if not kq_bam["tung_khoa"]:
                        van_de.append("Nút Đổi mật khẩu không bị disabled lúc gửi")
                    if len(dau) > 1:
                        van_de.append(f"Đóng dấu lặp {len(dau)} lần: {dau}")
                    return (
                        not van_de and not mon_a.page_errors,
                        " | ".join(van_de) if van_de else f"POST đổi MK=1, khóa nút={kq_bam['tung_khoa']}, dấu={dau}",
                        "Vừa",
                    )

                bc.chay_ca(
                    "BL09_DOI_MAT_KHAU_LAP",
                    f"Bấm nhanh 5 lần nút Đổi mật khẩu (tài khoản {user_pha})",
                    test_bam_lap_doi_mk,
                    page=page_a,
                    tai_hien=f"Mở /tai-khoan ({user_pha}) -> điền MK mới hợp lệ -> bấm nhanh 5 lần Đổi mật khẩu",
                    mong_doi="Chỉ 1 POST đổi mật khẩu, nút bị khóa lúc gửi, không lặp đóng dấu",
                )
            finally:
                ctx_auth.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
