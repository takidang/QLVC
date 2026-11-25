"""Chạy toàn bộ 7 bộ kiểm thử khám phá (mục 7 UI chạy trước mục 6 tra-cuu 429)."""

import subprocess
import sys

SCRIPTS = [
    "docs/test-evidence/kiem-thu-kham-pha/script/test_01_phan_quyen_idor.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_02_du_lieu_nhap_bua.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_03_tranh_chap_song_song.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_04_sai_trang_thai.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_05_upload.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_07_giao_dien.py",
    "docs/test-evidence/kiem-thu-kham-pha/script/test_06_tra_cuu.py",
]

for sc in SCRIPTS:
    print(f"\n==================== {sc} ====================", flush=True)
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", sc], check=False)
    if r.returncode != 0:
        print(f"!!! {sc} thoat voi ma {r.returncode}", flush=True)
