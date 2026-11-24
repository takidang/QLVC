"""Mục 06: Kiểm thử chức năng Xếp hàng lên xe trên GIAO DIỆN PIXEL (vai trò dieuphoi).

Kịch bản (trên chuyến LAP PHA- mới tạo với xe tải trọng 1000 kg, thể tích 10 m³):
1. Dòng gợi ý "Xe còn trống … m³ · … kg — N đơn ghép vừa" và tem "VỪA XE" / "QUÁ m³" / "QUÁ kg" khớp số thật
2. Rê chuột đơn chờ -> hiện khối nét đứt xem trước; rê đơn vượt tải -> đổi cảnh báo vượt sức chứa
3. Ghép lần lượt theo 4 cỡ (nhỏ 1 m³ -> vừa 4 m³ -> lớn 9.5 m³ -> đầy khít 10 m³):
   kiểm hình hàng trong khoang SVG có bị cắt dở hay vẽ tràn ra ngoài thùng xe không
4. Ghép đơn vượt tải (quá m³ và quá kg) -> bị chặn, hiện cảnh báo BR-01/BR-02
5. Bấm khối hàng trong khoang -> hiện bảng chọn -> bấm "Gỡ khỏi xe" -> gỡ sạch
6. Đổi cỡ cửa sổ giữa chừng (1440 -> 1100 -> 768 -> 390 -> 1440): bố cục và SVG không vỡ/tràn

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_06_xep_hang_xe.py
"""

from __future__ import annotations

import os
import re
import sys

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
    mo_trang_moi,
    tao_chuyen_lap_pha,
    tao_context_pixel,
    tao_don_pha,
)


def phan_tich_so_vn(s: str) -> float | None:
    s = s.strip().replace("\xa0", "").replace(" ", "")
    if not s:
        return None
    # Dạng Việt Nam: 1.000,5 -> 1000.5 hoặc 9,5 -> 9.5
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif re.match(r"^\d{1,3}(\.\d{3})+$", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def kiem_svg_khoang_hang(page: Page) -> dict:
    """Đo tọa độ các khối hàng trong SVG so với khung thùng xe (.xh-thung) để phát hiện tràn/cắt."""
    return page.evaluate(
        """() => {
            const xh = document.querySelector('.xh') || document.querySelector('.xh-xe');
            if (!xh) return { coXh: false };
            const svg = xh.querySelector('svg');
            if (!svg) return { coXh: true, coSvg: false };

            const svgR = svg.getBoundingClientRect();
            const thung = svg.querySelector('.xh-thung') || svg.querySelector('rect');
            const thungR = thung ? thung.getBoundingClientRect() : svgR;

            const khois = Array.from(svg.querySelectorAll('.xh-khoi'));
            const chiTietKhoi = [];
            const loiTran = [];
            for (const g of khois) {
                const rect = g.querySelector('rect') || g;
                const r = rect.getBoundingClientRect();
                const label = g.getAttribute('aria-label') || (g.textContent || '').trim().slice(0, 30);
                // Kiểm tràn ra ngoài thùng xe (cho phép sai số 3px cho viền pixel)
                const tranPhai = r.right > thungR.right + 3;
                const tranTrai = r.left < thungR.left - 3;
                const tranTren = r.top < thungR.top - 3;
                const tranDuoi = r.bottom > thungR.bottom + 3;
                // Kiểm text bên trong khối có tràn ra ngoài rect khối không
                const texts = Array.from(g.querySelectorAll('text'));
                let chuTran = false;
                for (const t of texts) {
                    const tr = t.getBoundingClientRect();
                    if (tr.width > 0 && (tr.right > r.right + 4 || tr.left < r.left - 4 || tr.right > thungR.right + 3)) {
                        chuTran = true;
                    }
                }
                const item = {
                    label: label.slice(0, 40),
                    w: Math.round(r.width),
                    h: Math.round(r.height),
                    tranPhai, tranTrai, tranTren, tranDuoi, chuTran,
                };
                chiTietKhoi.push(item);
                if (tranPhai || tranTrai || tranTren || tranDuoi || chuTran) {
                    loiTran.push(item);
                }
            }

            // Kiểm xem trước nét đứt (.xh-thu) nếu đang hiện
            const thu = svg.querySelector('.xh-thu');
            const thuInfo = thu ? {
                co: true,
                qua: thu.classList.contains('qua'),
                w: Math.round(thu.getBoundingClientRect().width),
                dash: getComputedStyle(thu).strokeDasharray,
            } : { co: false };

            // Đọc toàn bộ chữ vùng .xh để kiểm dòng gợi ý & tem VỪA XE / QUÁ
            const xhText = (xh.innerText || '').replace(/\\s+/g, ' ').trim();
            const dsThe = Array.from(xh.querySelectorAll('.xh-cho li')).map(li => ({
                txt: (li.innerText || '').replace(/\\s+/g, ' ').trim(),
            }));

            return {
                coXh: true,
                coSvg: true,
                svgTranViewport: svgR.right > window.innerWidth + 3,
                svgW: Math.round(svgR.width),
                thungW: Math.round(thungR.width),
                soKhoi: khois.length,
                chiTietKhoi,
                loiTran,
                thuInfo,
                xhText,
                dsThe,
            };
        }"""
    )


def kiem_goi_y_va_tem(
    info: dict,
    m3_con: float,
    kg_con: float,
    don_cho_du_kien: dict[str, tuple[float, float]],
) -> list[str]:
    """Đối chiếu dòng gợi ý 'Xe còn trống ... m³ · ... kg — N đơn ghép vừa' và tem VỪA XE / QUÁ."""
    van_de: list[str] = []
    xh_text = info.get("xhText", "")

    # Tính số đơn ghép vừa theo toán học thật
    so_vua_that = sum(
        1 for (dkg, dm3) in don_cho_du_kien.values() if dkg <= kg_con + 1e-6 and dm3 <= m3_con + 1e-6
    )

    m = re.search(
        r"Xe\s+còn\s+trống\s+([\d.,]+)\s*m[³3]\s*[·•-]\s*([\d.,]+)\s*kg\s*[—–-]\s*(\d+)\s*đơn\s*ghép\s*vừa",
        xh_text,
        re.IGNORECASE,
    )
    if m:
        m3_ui = phan_tich_so_vn(m.group(1))
        kg_ui = phan_tich_so_vn(m.group(2))
        n_ui = int(m.group(3))
        if m3_ui is None or abs(m3_ui - m3_con) > 0.15:
            van_de.append(f"Dòng gợi ý sai m³ còn trống: UI={m.group(1)}, thật={m3_con:.2f}")
        if kg_ui is None or abs(kg_ui - kg_con) > 1.5:
            van_de.append(f"Dòng gợi ý sai kg còn trống: UI={m.group(2)}, thật={kg_con:.1f}")
        # Lưu ý: trên hệ thống có thể có thêm đơn chờ ghép sẵn khác cùng tuyến -> n_ui >= so_vua_that
        if n_ui < so_vua_that:
            van_de.append(f"Dòng gợi ý ghi {n_ui} đơn ghép vừa, nhưng riêng đơn PHA đã có {so_vua_that} đơn vừa")

    # Kiểm tem VỪA XE / QUÁ trên từng thẻ đơn PHA
    for ma_don, (dkg, dm3) in don_cho_du_kien.items():
        the = next((x["txt"] for x in info.get("dsThe", []) if ma_don in x["txt"]), None)
        if not the:
            continue
        the_up = the.upper()
        qua_kg = dkg > kg_con + 1e-6
        qua_m3 = dm3 > m3_con + 1e-6
        co_tem_vua = "VỪA XE" in the_up
        co_tem_qua = "QUÁ" in the_up
        if co_tem_vua or co_tem_qua:
            if (qua_kg or qua_m3) and co_tem_vua:
                van_de.append(
                    f"Đơn {ma_don} ({dkg}kg/{dm3}m³) vượt phần trống ({kg_con}kg/{m3_con}m³) nhưng gắn tem VỪA XE"
                )
            if (not qua_kg and not qua_m3) and co_tem_qua:
                van_de.append(
                    f"Đơn {ma_don} ({dkg}kg/{dm3}m³) vừa phần trống ({kg_con}kg/{m3_con}m³) nhưng gắn tem QUÁ"
                )
    return van_de


def main() -> None:
    bc = BaoCaoScript(6, "Xếp hàng lên xe (SVG khoang hàng, gợi ý, tem VỪA/QUÁ, hover, quá tải, resize)", "ket_qua_06.json")

    api_dp = dang_nhap_api("dieuphoi")
    khach_id = lay_khach_hang_dau(api_dp)
    if not khach_id:
        bc.ghi("XH00_SETUP", "Chuẩn bị khách hàng", False, "Không có khách hàng hoạt động", muc="Nghiêm trọng")
        bc.ket_thuc()
        return

    # Tạo chuyến LAP PHA- với sức chứa tròn: 1000 kg, 10.00 m³
    chuyen, _, (nut_lay, nut_giao) = tao_chuyen_lap_pha(api_dp, tai_trong_kg=1000, the_tich_m3="10.00", gio_them=6)
    ch_id = chuyen["id"]

    # Tạo 6 đơn PHA- cùng tuyến để thử đủ 4 mức (nhỏ, vừa, lớn, đầy 100%) + 2 đơn vượt m³/kg
    don_nho = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="100.00", m3="1.00", nhan="XH-NHO")
    don_vua = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="300.00", m3="3.00", nhan="XH-VUA")
    don_lon = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="500.00", m3="5.50", nhan="XH-LON")
    don_day = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="100.00", m3="0.50", nhan="XH-DAY")
    don_qua_m3 = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="50.00", m3="2.00", nhan="XH-QUAM3")
    don_qua_kg = tao_don_pha(api_dp, khach_id, nut_lay, nut_giao, kg="250.00", m3="0.30", nhan="XH-QUAKG")

    tat_ca_don = {
        don_nho["ma_don"]: (100.0, 1.0),
        don_vua["ma_don"]: (300.0, 3.0),
        don_lon["ma_don"]: (500.0, 5.5),
        don_day["ma_don"]: (100.0, 0.5),
        don_qua_m3["ma_don"]: (50.0, 2.0),
        don_qua_kg["ma_don"]: (250.0, 0.3),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP)
            page, mon = mo_trang_moi(ctx)
            try:
                dang_nhap_nhanh(ctx, page, "dieuphoi")
                page.goto(f"{BASE_FE}/dieu-phoi/chuyen/{ch_id}", wait_until="domcontentloaded", timeout=15000)
                cho_yen(page, ms=600)

                # 6.1 Kiểm tra khởi đầu thùng trống, dòng gợi ý & tem VỪA XE
                def test_thung_trong_va_goi_y():
                    mon.reset()
                    info = kiem_svg_khoang_hang(page)
                    if not info.get("coXh") or not info.get("coSvg"):
                        return False, f"Không thấy khối Xếp hàng / SVG: {info}", "Nghiêm trọng"
                    van_de = kiem_goi_y_va_tem(info, m3_con=10.0, kg_con=1000.0, don_cho_du_kien=tat_ca_don)
                    if info["svgTranViewport"]:
                        van_de.append("SVG xe tràn khỏi viewport")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de) if van_de else f"Thùng trống, SVG {info['svgW']}px, gợi ý & tem khớp số thật (10 m³ / 1000 kg)",
                        "Vừa",
                    )

                bc.chay_ca(
                    "XH01_TRONG_GOI_Y",
                    "Thùng trống: kiểm dòng gợi ý còn trống & tem VỪA XE khớp sức chứa 10 m³ / 1000 kg",
                    test_thung_trong_va_goi_y,
                    page=page,
                    tai_hien=f"Mở /dieu-phoi/chuyen/{ch_id} (xe 1000kg/10m³ chưa ghép đơn)",
                    mong_doi="SVG hiển thị gọn, dòng gợi ý và tem VỪA XE khớp 10 m³ / 1000 kg",
                )

                # 6.2 Rê chuột đơn chờ xem trước khối nét đứt
                def test_hover_xem_truoc():
                    mon.reset()
                    the = page.locator(".xh-cho li", has_text=don_vua["ma_don"]).first
                    the.wait_for(state="visible", timeout=6000)
                    the.scroll_into_view_if_needed()
                    the.hover()
                    page.wait_for_timeout(300)
                    info = kiem_svg_khoang_hang(page)
                    page.mouse.move(10, 10)
                    page.wait_for_timeout(200)
                    thu = info.get("thuInfo", {})
                    if not thu.get("co") or thu.get("w", 0) <= 0:
                        return False, f"Rê chuột lên thẻ {don_vua['ma_don']} không hiện khối xem trước .xh-thu: {thu}", "Vừa"
                    return True, f"Rê chuột hiện khối xem trước nét đứt (w={thu['w']}px, dash={thu['dash']}, qua={thu['qua']})", ""

                bc.chay_ca(
                    "XH02_HOVER_NET_DUT",
                    "Rê chuột đơn chờ ghép hiện khối nét đứt xem trước trong khoang xe",
                    test_hover_xem_truoc,
                    page=page,
                    tai_hien=f"Rê chuột vào thẻ đơn {don_vua['ma_don']} trong danh sách đơn chờ ghép",
                    mong_doi="Khoang xe hiện khối xem trước nét đứt (.xh-thu) đúng kích cỡ",
                )

                # 6.3 Ghép tuần tự 4 mức: nhỏ (1 m³) -> vừa (4 m³) -> lớn (9.5 m³) -> đầy khoang (10 m³)
                da_ghep_kg = 0.0
                da_ghep_m3 = 0.0
                con_lai = dict(tat_ca_don)
                for ten_muc, d_obj in [
                    ("NHO_10PT", don_nho),
                    ("VUA_40PT", don_vua),
                    ("LON_95PT", don_lon),
                ]:
                    def make_ghep_muc(don_cur=d_obj, label_muc=ten_muc):
                        def chay():
                            nonlocal da_ghep_kg, da_ghep_m3
                            mon.reset()
                            ma_d = don_cur["ma_don"]
                            the = page.locator(".xh-cho li", has_text=ma_d).first
                            the.wait_for(state="visible", timeout=6000)
                            the.locator('button:has-text("Ghép")').first.click()
                            cho_yen(page, ms=500)
                            da_ghep_kg += float(don_cur["kg"])
                            da_ghep_m3 += float(don_cur["m3"])
                            con_lai.pop(ma_d, None)

                            info = kiem_svg_khoang_hang(page)
                            van_de = []
                            if mon.page_errors or mon.http_5xx:
                                van_de.append(f"pageerror={mon.page_errors[:2]}, 5xx={mon.http_5xx[:2]}")
                            if info.get("loiTran"):
                                van_de.append(f"Khối hàng bị tràn/cắt ngoài thùng xe: {info['loiTran']}")
                            if info.get("svgTranViewport"):
                                van_de.append("SVG tràn viewport")
                            van_de.extend(
                                kiem_goi_y_va_tem(
                                    info,
                                    m3_con=10.0 - da_ghep_m3,
                                    kg_con=1000.0 - da_ghep_kg,
                                    don_cho_du_kien=con_lai,
                                )
                            )
                            return (
                                not van_de,
                                " | ".join(van_de)
                                if van_de
                                else f"Đã ghép {ma_d} ({da_ghep_kg:.0f}kg/{da_ghep_m3:.1f}m³), {info['soKhoi']} khối nằm gọn trong thùng, gợi ý & tem khớp",
                                "Vừa",
                            )
                        return chay

                    bc.chay_ca(
                        f"XH03_{ten_muc}",
                        f"Ghép mức {ten_muc} ({d_obj['ma_don']}): kiểm hình khoang hàng, dòng gợi ý & tem VỪA/QUÁ",
                        make_ghep_muc(),
                        page=page,
                        tai_hien=f"Bấm 'Ghép vào xe' đơn {d_obj['ma_don']} trên chuyến {ch_id}",
                        mong_doi="Khối hàng vẽ gọn trong thùng xe không tràn/cắt; dòng gợi ý & tem VỪA XE / QUÁ m³/kg khớp số thật",
                    )

                # 6.4 Ở mức 95% (900 kg / 9.5 m³), thử rê & ghép đơn vượt m³ (don_qua_m3) và vượt kg (don_qua_kg) -> PHẢI BỊ CHẶN
                def test_vuot_tai():
                    mon.reset()
                    van_de = []
                    for ten_loai, d_qua in [("QUÁ m³", don_qua_m3), ("QUÁ kg", don_qua_kg)]:
                        ma_d = d_qua["ma_don"]
                        the = page.locator(".xh-cho li", has_text=ma_d).first
                        if the.count() == 0:
                            van_de.append(f"Không thấy đơn {ma_d} ({ten_loai}) trong danh sách chờ")
                            continue
                        the.scroll_into_view_if_needed()
                        the.hover()
                        page.wait_for_timeout(250)
                        info_hover = kiem_svg_khoang_hang(page)
                        co_bao_hover = page.locator(".xh-bao").count() > 0 or info_hover["thuInfo"].get("qua")
                        if not co_bao_hover:
                            van_de.append(f"Rê chuột {ma_d} ({ten_loai}) không hiện cảnh báo quá tải / khối cam")
                        # Bấm ghép thử -> máy chủ phải chặn BR-01/BR-02
                        btn = the.locator('button:has-text("Ghép")').first
                        if btn.is_enabled():
                            btn.click()
                            cho_yen(page, ms=500)
                            alert_txt = page.locator('[role="alert"]').first.inner_text() if page.locator('[role="alert"]').count() else ""
                            if not alert_txt and not ("BR-01" in alert_txt or "BR-02" in alert_txt or "vượt" in alert_txt.lower()):
                                van_de.append(f"Bấm ghép {ma_d} ({ten_loai}) không hiện cảnh báo chặn từ máy chủ")
                        # Kiểm lại qua API đơn vẫn chưa bị ghép vào chuyến
                        _, ct, _ = api_dp.raw("GET", f"/api/chuyen/{ch_id}")
                        if any(x["id"] == d_qua["id"] for x in ct.get("don", [])):
                            van_de.append(f"NGHIÊM TRỌNG: Ghép lọt đơn quá tải {ma_d} ({ten_loai}) vào chuyến!")
                    return (
                        not van_de and not mon.http_5xx and not mon.page_errors,
                        " | ".join(van_de) if van_de else "Đơn quá m³ và quá kg đều hiện cảnh báo khi hover và bị chặn khi ghép",
                        "Nghiêm trọng" if any("NGHIÊM TRỌNG" in v for v in van_de) else "Vừa",
                    )

                bc.chay_ca(
                    "XH04_CHAN_VUOT_TAI",
                    "Rê chuột & ghép đơn vượt m³ và vượt kg (tại 95% khoang): phải cảnh báo và bị chặn",
                    test_vuot_tai,
                    page=page,
                    tai_hien=f"Khi xe đã 900kg/9.5m³, hover & bấm Ghép đơn {don_qua_m3['ma_don']} (+2m³) và {don_qua_kg['ma_don']} (+250kg)",
                    mong_doi="Hiện cảnh báo vượt tải, máy chủ chặn (BR-01/BR-02), không cho ghép lọt",
                )

                # 6.5 Ghép đơn cuối (don_day: 100kg / 0.5m³) -> ĐẦY KHOANG 100% (1000kg / 10.0m³)
                def test_day_khoang_100():
                    mon.reset()
                    ma_d = don_day["ma_don"]
                    the = page.locator(".xh-cho li", has_text=ma_d).first
                    the.wait_for(state="visible", timeout=6000)
                    the.locator('button:has-text("Ghép")').first.click()
                    cho_yen(page, ms=500)
                    info = kiem_svg_khoang_hang(page)
                    van_de = []
                    if info.get("loiTran"):
                        van_de.append(f"Đầy khoang 100% có khối tràn/cắt ngoài thùng: {info['loiTran']}")
                    if info["soKhoi"] < 4:
                        van_de.append(f"Thiếu khối trong SVG (chỉ thấy {info['soKhoi']}/4)")
                    return (
                        not van_de and not mon.page_errors,
                        " | ".join(van_de) if van_de else f"Đầy khoang 100% (1000kg/10m³): {info['soKhoi']} khối nằm gọn trong thùng",
                        "Vừa",
                    )

                bc.chay_ca(
                    "XH05_DAY_KHOANG_100",
                    "Ghép đến đầy khoang 100% (1000 kg / 10 m³): kiểm hình khối không cắt dở/tràn thùng",
                    test_day_khoang_100,
                    page=page,
                    tai_hien=f"Ghép thêm {don_day['ma_don']} để đạt đúng 1000 kg / 10.0 m³",
                    mong_doi="Cả 4 khối hàng nằm gọn trong khung thùng xe, không tràn mép phải hay cắt chữ",
                )

                # 6.6 Đổi cỡ cửa sổ giữa chừng khi đang đầy khoang (1440 -> 1100 -> 768 -> 390 -> 1440)
                def test_doi_co_cua_so():
                    mon.reset()
                    van_de = []
                    for w, h in [(1100, 800), (768, 900), (390, 844), (1440, 900)]:
                        page.set_viewport_size({"width": w, "height": h})
                        page.wait_for_timeout(300)
                        info = kiem_svg_khoang_hang(page)
                        if info.get("svgTranViewport"):
                            van_de.append(f"{w}x{h}: SVG tràn viewport")
                        if info.get("loiTran"):
                            van_de.append(f"{w}x{h}: khối tràn thùng {info['loiTran'][:1]}")
                    if mon.page_errors:
                        van_de.append(f"pageerror={mon.page_errors[:2]}")
                    return (
                        not van_de,
                        " | ".join(van_de) if van_de else "Đổi cỡ 1440 -> 1100 -> 768 -> 390 -> 1440: SVG & khối hàng co giãn sạch",
                        "Vừa",
                    )

                bc.chay_ca(
                    "XH06_RESIZE_GIUA_CHUNG",
                    "Đổi cỡ cửa sổ giữa chừng (1100, 768, 390, 1440px) khi khoang đang đầy 100%",
                    test_doi_co_cua_so,
                    page=page,
                    tai_hien="Trên màn chi tiết chuyến đầy 100% -> đổi viewport lần lượt 1100, 768, 390, 1440px",
                    mong_doi="SVG khoang hàng co giãn vừa màn hình, khối không tràn thùng, không lỗi JS",
                )

                # 6.7 Bấm khối trong khoang SVG -> bấm Gỡ khỏi xe
                def test_bam_khoi_de_go():
                    mon.reset()
                    truoc_so = page.locator(".xh-khoi").count()
                    page.locator(".xh-khoi").last.click()
                    btn_go = page.locator('button:has-text("Gỡ khỏi xe")').first
                    btn_go.wait_for(state="visible", timeout=5000)
                    btn_go.click()
                    cho_yen(page, ms=500)
                    sau_so = page.locator(".xh-khoi").count()
                    if sau_so != truoc_so - 1:
                        return False, f"Gỡ đơn không giảm số khối trong khoang ({truoc_so} -> {sau_so})", "Vừa"
                    return True, f"Bấm khối -> Gỡ khỏi xe thành công ({truoc_so} -> {sau_so} khối)", ""

                bc.chay_ca(
                    "XH07_BAM_KHOI_GO",
                    "Bấm vào khối hàng trong SVG để chọn và bấm 'Gỡ khỏi xe'",
                    test_bam_khoi_de_go,
                    page=page,
                    tai_hien="Bấm khối hàng cuối trong SVG -> bấm nút 'Gỡ khỏi xe'",
                    mong_doi="Đơn được gỡ khỏi chuyến, số khối trong SVG giảm đi 1",
                )
            finally:
                ctx.close()
        finally:
            browser.close()

    bc.ket_thuc()


if __name__ == "__main__":
    main()
