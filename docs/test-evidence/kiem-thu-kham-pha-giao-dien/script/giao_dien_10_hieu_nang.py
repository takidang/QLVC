"""Mục 10: Đo hiệu năng cảm nhận (CHỈ ĐO, KHÔNG PHÁN) trên 5 trang nặng nhất GIAO DIỆN PIXEL.

5 trang đo (viewport 1440×900, Pixel sáng):
1. Chi tiết chuyến (/dieu-phoi/chuyen/<id>, dieuphoi)
2. Danh sách đơn (/dieu-phoi/don, dieuphoi)
3. Tổng quan quản lý (/quan-ly/tong-quan, quanly)
4. Quyết toán (/ke-toan/quyet-toan, ketoan — tự chọn chuyến đầu nếu có)
5. Tài khoản (/tai-khoan, dieuphoi)

Chỉ số đo bằng page.evaluate:
- Số animation đang chạy: document.getAnimations().length (và danh sách tên)
- Số node DOM: document.querySelectorAll('*').length
- FPS qua requestAnimationFrame trong 3 s khi để yên (idle) và khi cuộn (scroll)
- PerformanceObserver long task > 50 ms (số lượng, tổng ms, max ms)

Xuất bảng Markdown + file JSON kiem-thu-kham-pha/ket_qua_10.json để Claude chọn hiệu ứng tối ưu.

Chạy: py -3.12 -I -X utf8 kiem-thu-kham-pha/giao_dien_10_hieu_nang.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import Page, sync_playwright

from ho_tro_pixel import (
    BASE_FE,
    DIR_GOC,
    VIEWPORT_DESKTOP,
    BaoCaoScript,
    cho_yen,
    dang_nhap_api,
    dang_nhap_nhanh,
    lay_chuyen_mau,
    mo_trang_moi,
    tao_context_pixel,
)

INIT_LONGTASK_JS = """
window.__phaLongTasks = [];
try {
  const po = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.duration > 50) {
        window.__phaLongTasks.push({
          t: Math.round(entry.startTime),
          dur: Math.round(entry.duration * 10) / 10,
          name: entry.name || 'longtask',
        });
      }
    }
  });
  po.observe({ type: 'longtask', buffered: true });
} catch (e) {}
"""

JS_DO_FPS_3S = """(cuon) => new Promise((resolve) => {
  const start = performance.now();
  let last = start;
  let frames = 0;
  let maxFrameMs = 0;
  let dir = 1;
  const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);

  function tick(now) {
    frames += 1;
    const dt = now - last;
    if (frames > 1 && dt > maxFrameMs) maxFrameMs = dt;
    last = now;

    if (cuon && maxScroll > 20) {
      const nextY = window.scrollY + dir * 24;
      if (nextY >= maxScroll) {
        window.scrollTo(0, maxScroll);
        dir = -1;
      } else if (nextY <= 0) {
        window.scrollTo(0, 0);
        dir = 1;
      } else {
        window.scrollTo(0, nextY);
      }
    }

    const elapsed = now - start;
    if (elapsed >= 3000) {
      if (cuon) window.scrollTo(0, 0);
      resolve({
        fps: Math.round((frames * 1000 / elapsed) * 10) / 10,
        frames,
        elapsedMs: Math.round(elapsed),
        maxFrameMs: Math.round(maxFrameMs * 10) / 10,
      });
    } else {
      requestAnimationFrame(tick);
    }
  }
  requestAnimationFrame(tick);
})"""


def do_mot_trang(page: Page, ten: str, path: str, buoc_phu=None) -> dict:
    page.goto(f"{BASE_FE}{path}", wait_until="domcontentloaded", timeout=15000)
    cho_yen(page, ms=700, network_timeout=6000)
    if buoc_phu:
        buoc_phu(page)
        cho_yen(page, ms=500, network_timeout=4000)

    # Lấy long task trong lúc tải trang
    lt_tai = page.evaluate("() => (window.__phaLongTasks || []).slice()")

    # Snapshot DOM & animations
    snap = page.evaluate(
        """() => {
            const anims = document.getAnimations ? document.getAnimations() : [];
            const running = anims.filter(a => a.playState === 'running');
            const names = [...new Set(anims.map(a => a.animationName || a.transitionProperty || 'waapi'))].slice(0, 8);
            return {
                domNodes: document.querySelectorAll('*').length,
                animTotal: anims.length,
                animRunning: running.length,
                animNames: names,
            };
        }"""
    )

    # Reset long task trước giai đoạn idle 3s
    page.evaluate("() => { window.__phaLongTasks = []; }")
    fps_idle = page.evaluate(JS_DO_FPS_3S, False)
    lt_idle = page.evaluate("() => (window.__phaLongTasks || []).slice()")

    # Reset long task trước giai đoạn scroll 3s
    page.evaluate("() => { window.__phaLongTasks = []; }")
    fps_scroll = page.evaluate(JS_DO_FPS_3S, True)
    lt_scroll = page.evaluate("() => (window.__phaLongTasks || []).slice()")

    all_lt = lt_tai + lt_idle + lt_scroll
    max_lt = max((x["dur"] for x in all_lt), default=0.0)
    tong_lt = round(sum(x["dur"] for x in all_lt), 1)

    return {
        "trang": ten,
        "path": path,
        "dom_nodes": snap["domNodes"],
        "animations_total": snap["animTotal"],
        "animations_running": snap["animRunning"],
        "animation_names": snap["animNames"],
        "fps_idle": fps_idle["fps"],
        "max_frame_idle_ms": fps_idle["maxFrameMs"],
        "fps_scroll": fps_scroll["fps"],
        "max_frame_scroll_ms": fps_scroll["maxFrameMs"],
        "long_tasks_tai": len(lt_tai),
        "long_tasks_idle": len(lt_idle),
        "long_tasks_scroll": len(lt_scroll),
        "long_tasks_tong": len(all_lt),
        "long_task_max_ms": max_lt,
        "long_task_tong_ms": tong_lt,
    }


def main() -> None:
    bc = BaoCaoScript(10, "Đo hiệu năng cảm nhận trên 5 trang nặng nhất (chỉ đo, không phán)", "ket_qua_10.json")

    chuyen_id = 1
    try:
        api_dp = dang_nhap_api("dieuphoi")
        c = lay_chuyen_mau(api_dp)
        if c:
            chuyen_id = int(c["id"])
    except Exception:
        pass

    bang_so_lieu: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # 1, 2, 5: dieuphoi (Chi tiết chuyến, Danh sách đơn, Tài khoản)
            ctx_dp = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP, extra_init_js=INIT_LONGTASK_JS)
            pg_dp, mon_dp = mo_trang_moi(ctx_dp)
            try:
                dang_nhap_nhanh(ctx_dp, pg_dp, "dieuphoi")

                for ma, ten, path in [
                    ("HN01_CHI_TIET_CHUYEN", "Chi tiết chuyến", f"/dieu-phoi/chuyen/{chuyen_id}"),
                    ("HN02_DANH_SACH_DON", "Danh sách đơn", "/dieu-phoi/don"),
                    ("HN05_TAI_KHOAN", "Tài khoản", "/tai-khoan"),
                ]:
                    def make_measure(t=ten, p_url=path):
                        def chay():
                            mon_dp.reset()
                            m = do_mot_trang(pg_dp, t, p_url)
                            bang_so_lieu.append(m)
                            tom_tat = (
                                f"DOM={m['dom_nodes']}, anim={m['animations_total']}(run={m['animations_running']}), "
                                f"FPS idle={m['fps_idle']} / scroll={m['fps_scroll']}, "
                                f"longTasks={m['long_tasks_tong']}(max={m['long_task_max_ms']}ms)"
                            )
                            return (not mon_dp.page_errors), tom_tat, "Nhẹ"
                        return chay

                    bc.chay_ca(ma, f"Đo hiệu năng: {ten} ({path})", make_measure(), page=pg_dp)
            finally:
                ctx_dp.close()

            # 3: quanly (Tổng quan quản lý)
            ctx_ql = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP, extra_init_js=INIT_LONGTASK_JS)
            pg_ql, mon_ql = mo_trang_moi(ctx_ql)
            try:
                dang_nhap_nhanh(ctx_ql, pg_ql, "quanly")

                def do_tq():
                    mon_ql.reset()
                    m = do_mot_trang(pg_ql, "Tổng quan quản lý", "/quan-ly/tong-quan")
                    bang_so_lieu.append(m)
                    tom_tat = (
                        f"DOM={m['dom_nodes']}, anim={m['animations_total']}(run={m['animations_running']}), "
                        f"FPS idle={m['fps_idle']} / scroll={m['fps_scroll']}, "
                        f"longTasks={m['long_tasks_tong']}(max={m['long_task_max_ms']}ms)"
                    )
                    return (not mon_ql.page_errors), tom_tat, "Nhẹ"

                bc.chay_ca("HN03_TONG_QUAN", "Đo hiệu năng: Tổng quan quản lý (/quan-ly/tong-quan)", do_tq, page=pg_ql)
            finally:
                ctx_ql.close()

            # 4: ketoan (Quyết toán — bấm chọn chuyến đầu tiên nếu có)
            ctx_kt = tao_context_pixel(browser, viewport=VIEWPORT_DESKTOP, extra_init_js=INIT_LONGTASK_JS)
            pg_kt, mon_kt = mo_trang_moi(ctx_kt)
            try:
                dang_nhap_nhanh(ctx_kt, pg_kt, "ketoan")

                def chon_chuyen_qt(pg: Page):
                    btns = pg.locator(".qt-ds ul button")
                    if btns.count() > 0:
                        btns.first.click()

                def do_qt():
                    mon_kt.reset()
                    m = do_mot_trang(pg_kt, "Quyết toán", "/ke-toan/quyet-toan", buoc_phu=chon_chuyen_qt)
                    bang_so_lieu.append(m)
                    tom_tat = (
                        f"DOM={m['dom_nodes']}, anim={m['animations_total']}(run={m['animations_running']}), "
                        f"FPS idle={m['fps_idle']} / scroll={m['fps_scroll']}, "
                        f"longTasks={m['long_tasks_tong']}(max={m['long_task_max_ms']}ms)"
                    )
                    return (not mon_kt.page_errors), tom_tat, "Nhẹ"

                bc.chay_ca("HN04_QUYET_TOAN", "Đo hiệu năng: Quyết toán (/ke-toan/quyet-toan)", do_qt, page=pg_kt)
            finally:
                ctx_kt.close()
        finally:
            browser.close()

    # In bảng số liệu Markdown gọn gàng để chép thẳng vào bao-cao.md
    print("\n### Bảng số liệu hiệu năng cảm nhận (Pixel sáng, 1440×900)")
    print("| Trang | Route | DOM nodes | Animations (chạy) | FPS đứng yên (3s) | FPS cuộn (3s) | Long task >50ms (max ms) | Tên animation |")
    print("|---|---|---:|---:|---:|---:|---:|---|")
    for m in bang_so_lieu:
        ten_anim = ", ".join(m["animation_names"]) or "—"
        print(
            f"| {m['trang']} | `{m['path']}` | {m['dom_nodes']} | "
            f"{m['animations_total']} ({m['animations_running']}) | "
            f"{m['fps_idle']} (max {m['max_frame_idle_ms']}ms) | "
            f"{m['fps_scroll']} (max {m['max_frame_scroll_ms']}ms) | "
            f"{m['long_tasks_tong']} (max {m['long_task_max_ms']}ms) | {ten_anim} |"
        )

    # Lưu riêng bảng hiệu năng để tiện đọc lại
    with open(os.path.join(DIR_GOC, "hieu_nang_10.json"), "w", encoding="utf-8") as f:
        json.dump(bang_so_lieu, f, ensure_ascii=False, indent=2)

    bc.ket_thuc()


if __name__ == "__main__":
    main()
