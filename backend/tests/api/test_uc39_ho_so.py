import re
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import luu_tru
from app.main import app
from app.models import NguoiDung, TaiXe

JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"1" * 100
TEN_HEX = re.compile(r"[0-9a-f]{32}\.(?:jpg|png)")


@pytest.fixture
def thu_muc(tmp_path, monkeypatch):
    monkeypatch.setattr(luu_tru, "THU_MUC", tmp_path)
    return tmp_path


@pytest.fixture
def tao_tai_xe(db, tao_nguoi_dung):
    def tao(ten="tx1", sdt="0901234567", so_gplx="GPLX0001", hang="C", han=date(2028, 6, 15)):
        nd = tao_nguoi_dung(ten=ten, vai_tro="TAI_XE")
        tx = TaiXe(nguoi_dung_id=nd.id, so_gplx=so_gplx, hang_gplx=hang, han_gplx=han, sdt=sdt)
        db.add(tx)
        db.commit()
        return nd, tx

    return tao


def dang_nhap(client, ten, mat_khau="matkhau123"):
    r = client.post("/api/auth/dang-nhap", json={"ten_dang_nhap": ten, "mat_khau": mat_khau})
    assert r.status_code == 200, r.text
    return r


def gui_anh(client, du_lieu: bytes, ten="avatar.jpg", loai="image/jpeg", data=None):
    return client.put("/api/auth/anh-dai-dien", files={"anh": (ten, du_lieu, loai)}, data=data)


def lay_nd(db, nd_id: int) -> NguoiDung:
    db.expire_all()
    return db.get(NguoiDung, nd_id)


# AC1 – GET /api/auth/ho-so
@pytest.mark.parametrize("vai_tro", ["QUAN_LY", "DIEU_PHOI", "KE_TOAN"])
def test_uc39_ac1_vai_tro_khac_khong_co_tai_xe(client, dang_nhap_voi, vai_tro):
    nd = dang_nhap_voi(vai_tro)
    r = client.get("/api/auth/ho-so")
    assert r.status_code == 200
    body = r.json()
    assert body == {
        "id": nd.id,
        "ten_dang_nhap": nd.ten_dang_nhap,
        "ho_ten": nd.ho_ten,
        "vai_tro": vai_tro,
        "trang_thai": "HOAT_DONG",
        "co_anh_dai_dien": False,
        "tai_xe": None,
    }
    assert "anh_dai_dien" not in body and "mat_khau_bam" not in body


def test_uc39_ac1_tai_xe_du_bon_truong(client, tao_tai_xe):
    nd, tx = tao_tai_xe(ten="tx_ho_so", sdt="0912345678", so_gplx="B2998877", hang="C1", han=date(2027, 12, 31))
    dang_nhap(client, "tx_ho_so")
    r = client.get("/api/auth/ho-so")
    assert r.status_code == 200
    assert r.json() == {
        "id": nd.id,
        "ten_dang_nhap": "tx_ho_so",
        "ho_ten": nd.ho_ten,
        "vai_tro": "TAI_XE",
        "trang_thai": "HOAT_DONG",
        "co_anh_dai_dien": False,
        "tai_xe": {
            "sdt": tx.sdt,
            "so_gplx": tx.so_gplx,
            "hang_gplx": tx.hang_gplx,
            "han_gplx": "2027-12-31",
        },
    }


def test_uc39_ac1_chua_dang_nhap_401(client):
    assert client.get("/api/auth/ho-so").status_code == 401


# AC2 – PUT /api/auth/anh-dai-dien
@pytest.mark.parametrize(
    ("du_lieu", "duoi", "ten_client"),
    [
        (JPG, ".jpg", "../../hack.png"),  # giả tên đường dẫn và đuôi khác: máy chủ bỏ qua
        (PNG, ".png", "anh-cua-toi.jpeg"),
    ],
    ids=["jpeg", "png"],
)
def test_uc39_ac2_tai_len_jpeg_va_png(client, db, dang_nhap_voi, thu_muc, du_lieu, duoi, ten_client):
    nd = dang_nhap_voi("DIEU_PHOI")
    r = gui_anh(client, du_lieu, ten=ten_client, loai="text/plain")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["co_anh_dai_dien"] is True
    assert "anh_dai_dien" not in body

    tep = list(thu_muc.iterdir())
    assert len(tep) == 1
    assert TEN_HEX.fullmatch(tep[0].name) and tep[0].suffix == duoi
    assert tep[0].name != ten_client
    assert tep[0].read_bytes() == du_lieu
    assert lay_nd(db, nd.id).anh_dai_dien == tep[0].name
    # Không lộ tên file hay đường dẫn lưu trữ trong phản hồi
    assert tep[0].name not in r.text and str(thu_muc) not in r.text


def test_uc39_ac2_anh_dung_500kb(client, dang_nhap_voi, thu_muc):
    dang_nhap_voi("QUAN_LY")
    vua = b"\xff\xd8\xff" + b"0" * (luu_tru.KICH_THUOC_TOI_DA - 3)
    r = gui_anh(client, vua)
    assert r.status_code == 200
    assert r.json()["co_anh_dai_dien"] is True


@pytest.mark.parametrize(
    ("du_lieu", "status", "ma_loi"),
    [
        (b"GIF89a" + b"0" * 50, 400, "ANH_SAI_LOAI"),
        (b"khong phai anh", 400, "ANH_SAI_LOAI"),
        (b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", 400, "ANH_SAI_LOAI"),
        (b"", 400, "ANH_RONG"),
        (b"\xff\xd8\xff" + b"0" * (luu_tru.KICH_THUOC_TOI_DA - 2), 413, "ANH_QUA_LON"),
    ],
    ids=["gif", "chu-thuong", "svg", "rong", "qua-500kb"],
)
def test_uc39_ac2_tu_choi_anh_sai_hoac_qua_lon(client, db, dang_nhap_voi, thu_muc, du_lieu, status, ma_loi):
    nd = dang_nhap_voi("KE_TOAN")
    r = gui_anh(client, du_lieu)
    assert (r.status_code, r.json()["ma"]) == (status, ma_loi)
    assert list(thu_muc.iterdir()) == []
    assert lay_nd(db, nd.id).anh_dai_dien is None


def test_uc39_ac2_thieu_file_va_chua_dang_nhap(client, dang_nhap_voi, thu_muc):
    assert gui_anh(client, JPG).status_code == 401
    dang_nhap_voi("DIEU_PHOI")
    assert client.put("/api/auth/anh-dai-dien").status_code == 400
    assert list(thu_muc.iterdir()) == []


def test_uc39_ac2_rollback_xoa_file_moi_khi_csdl_loi(db, tao_nguoi_dung, thu_muc, monkeypatch):
    from app.auth import service

    nd = tao_nguoi_dung(ten="nd_loi_db", vai_tro="DIEU_PHOI")

    def commit_loi():
        raise RuntimeError("csdl hong")

    monkeypatch.setattr(db, "commit", commit_loi)
    with pytest.raises(RuntimeError, match="csdl hong"):
        service.doi_anh_dai_dien(db, nd.id, JPG)
    assert list(thu_muc.iterdir()) == []


# AC3 – đổi lần hai xóa file cũ; DELETE xóa file và trả 204
def test_uc39_ac3_doi_lan_hai_xoa_file_cu(client, db, dang_nhap_voi, thu_muc):
    nd = dang_nhap_voi("DIEU_PHOI")
    assert gui_anh(client, JPG).status_code == 200
    ten_cu = lay_nd(db, nd.id).anh_dai_dien
    assert (thu_muc / ten_cu).is_file()

    assert gui_anh(client, PNG, ten="moi.png", loai="image/png").status_code == 200
    ten_moi = lay_nd(db, nd.id).anh_dai_dien
    assert ten_moi != ten_cu
    assert not (thu_muc / ten_cu).exists()
    assert [p.name for p in thu_muc.iterdir()] == [ten_moi]


def test_uc39_ac3_loi_xoa_file_cu_khong_lam_hong_request(client, db, dang_nhap_voi, thu_muc, monkeypatch, caplog):
    nd = dang_nhap_voi("DIEU_PHOI")
    assert gui_anh(client, JPG).status_code == 200

    def xoa_loi(_ten: str) -> None:
        raise OSError("khong xoa duoc")

    monkeypatch.setattr(luu_tru, "xoa", xoa_loi)
    with caplog.at_level("WARNING"):
        r = gui_anh(client, PNG, ten="moi.png", loai="image/png")
    assert r.status_code == 200 and r.json()["co_anh_dai_dien"] is True
    assert lay_nd(db, nd.id).anh_dai_dien.endswith(".png")
    assert any("Không xóa được ảnh đại diện cũ" in rec.message for rec in caplog.records)


def test_uc39_ac3_delete_xoa_file_va_delete_khi_chua_co(client, db, dang_nhap_voi, thu_muc):
    nd = dang_nhap_voi("QUAN_LY")
    # Chưa có ảnh → 204
    assert client.delete("/api/auth/anh-dai-dien").status_code == 204
    assert lay_nd(db, nd.id).anh_dai_dien is None

    assert gui_anh(client, JPG).status_code == 200
    ten = lay_nd(db, nd.id).anh_dai_dien
    assert (thu_muc / ten).is_file()

    r = client.delete("/api/auth/anh-dai-dien")
    assert r.status_code == 204
    assert not (thu_muc / ten).exists()
    assert lay_nd(db, nd.id).anh_dai_dien is None
    assert client.get("/api/auth/ho-so").json()["co_anh_dai_dien"] is False
    # Xóa lần nữa vẫn 204
    assert client.delete("/api/auth/anh-dai-dien").status_code == 204


def test_uc39_ac3_delete_chua_dang_nhap_401(client):
    assert client.delete("/api/auth/anh-dai-dien").status_code == 401


# AC4 – GET /api/auth/anh-dai-dien
@pytest.mark.parametrize(("du_lieu", "loai"), [(JPG, "image/jpeg"), (PNG, "image/png")], ids=["jpeg", "png"])
def test_uc39_ac4_tra_dung_byte_va_header(client, dang_nhap_voi, thu_muc, du_lieu, loai):
    dang_nhap_voi("DIEU_PHOI")
    assert gui_anh(client, du_lieu).status_code == 200
    r = client.get("/api/auth/anh-dai-dien")
    assert r.status_code == 200
    assert r.content == du_lieu
    assert r.headers["content-type"] == loai
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "private, no-cache"


def test_uc39_ac4_chua_co_anh_hoac_file_mat_404(client, db, dang_nhap_voi, thu_muc):
    nd = dang_nhap_voi("DIEU_PHOI")
    r = client.get("/api/auth/anh-dai-dien")
    assert (r.status_code, r.json()["ma"]) == (404, "KHONG_TIM_THAY")

    assert gui_anh(client, JPG).status_code == 200
    ten = lay_nd(db, nd.id).anh_dai_dien
    (thu_muc / ten).unlink()
    r2 = client.get("/api/auth/anh-dai-dien")
    assert (r2.status_code, r2.json()["ma"]) == (404, "KHONG_TIM_THAY")
    assert ten not in r2.text and str(thu_muc) not in r2.text


def test_uc39_ac4_hai_nguoi_chi_nhan_anh_cua_minh(db, tao_nguoi_dung, thu_muc):
    tao_nguoi_dung(ten="nguoi_a", vai_tro="DIEU_PHOI")
    tao_nguoi_dung(ten="nguoi_b", vai_tro="KE_TOAN")
    with (
        TestClient(app, base_url="https://testserver") as ca,
        TestClient(app, base_url="https://testserver") as cb,
    ):
        dang_nhap(ca, "nguoi_a")
        dang_nhap(cb, "nguoi_b")
        assert gui_anh(ca, JPG).status_code == 200
        assert gui_anh(cb, PNG).status_code == 200

        ra = ca.get("/api/auth/anh-dai-dien")
        rb = cb.get("/api/auth/anh-dai-dien")
        assert (ra.status_code, ra.headers["content-type"], ra.content) == (200, "image/jpeg", JPG)
        assert (rb.status_code, rb.headers["content-type"], rb.content) == (200, "image/png", PNG)


def test_uc39_ac4_chua_dang_nhap_401(client):
    assert client.get("/api/auth/anh-dai-dien").status_code == 401


# AC5 – không có API tự sửa hồ sơ; trường lạ trong form ảnh bị bỏ qua
def test_uc39_ac5_patch_put_ho_so_405(client, dang_nhap_voi):
    dang_nhap_voi("DIEU_PHOI")
    assert client.patch("/api/auth/ho-so", json={"ho_ten": "Tên mới"}).status_code == 405
    assert client.put("/api/auth/ho-so", json={"ho_ten": "Tên mới"}).status_code == 405


def test_uc39_ac5_truong_la_trong_form_anh_khong_doi_csdl(client, db, tao_tai_xe, thu_muc):
    nd, tx = tao_tai_xe(ten="tx_ac5", sdt="0909998888", so_gplx="GPLX5566", hang="C", han=date(2029, 1, 20))
    ho_ten_goc = nd.ho_ten
    dang_nhap(client, "tx_ac5")

    r = gui_anh(
        client,
        JPG,
        data={
            "ho_ten": "Tên giả mạo",
            "vai_tro": "QUAN_LY",
            "ten_dang_nhap": "admin",
            "trang_thai": "NGUNG",
            "sdt": "0911111111",
            "so_gplx": "FAKE9999",
            "hang_gplx": "B",
            "han_gplx": "2035-01-01",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["co_anh_dai_dien"] is True

    db.expire_all()
    nd_sau = db.get(NguoiDung, nd.id)
    tx_sau = db.scalar(select(TaiXe).where(TaiXe.nguoi_dung_id == nd.id))
    assert (nd_sau.ho_ten, nd_sau.vai_tro, nd_sau.ten_dang_nhap, nd_sau.trang_thai) == (
        ho_ten_goc,
        "TAI_XE",
        "tx_ac5",
        "HOAT_DONG",
    )
    assert (tx_sau.sdt, tx_sau.so_gplx, tx_sau.hang_gplx, tx_sau.han_gplx) == (
        "0909998888",
        "GPLX5566",
        "C",
        date(2029, 1, 20),
    )


# AC6 – /api/auth/toi (và đăng nhập) có co_anh_dai_dien đúng trước / sau khi đổi & xóa
def test_uc39_ac6_toi_co_co_anh_dai_dien(client, dang_nhap_voi, thu_muc):
    dang_nhap_voi("DIEU_PHOI")
    assert client.get("/api/auth/toi").json()["co_anh_dai_dien"] is False

    assert gui_anh(client, JPG).status_code == 200
    toi_sau = client.get("/api/auth/toi").json()
    assert toi_sau["co_anh_dai_dien"] is True
    assert "anh_dai_dien" not in toi_sau

    dn = dang_nhap(client, "dieu_phoi").json()
    assert dn["co_anh_dai_dien"] is True

    assert client.delete("/api/auth/anh-dai-dien").status_code == 204
    assert client.get("/api/auth/toi").json()["co_anh_dai_dien"] is False


# Unit – luu_tru.doc chặn traversal và tên sai dạng
def test_uc39_unit_luu_tru_doc_hop_le_va_thieu(thu_muc):
    ten = luu_tru.luu(JPG, ".jpg")
    assert luu_tru.doc(ten) == JPG
    luu_tru.xoa(ten)
    with pytest.raises(FileNotFoundError):
        luu_tru.doc(ten)


@pytest.mark.parametrize(
    "ten_xau",
    [
        "../secret.jpg",
        "..\\secret.jpg",
        "sub/file.jpg",
        "sub\\file.jpg",
        f"../{'a' * 32}.jpg",
        "avatar.jpg",
        "A" * 32 + ".jpg",
        "a" * 32 + ".gif",
        "a" * 32 + ".jpg\n",
        "",
    ],
)
def test_uc39_unit_luu_tru_doc_chan_ten_khong_hop_le(thu_muc, ten_xau):
    with pytest.raises(ValueError):
        luu_tru.doc(ten_xau)
    with pytest.raises(ValueError):
        luu_tru.xoa(ten_xau)
