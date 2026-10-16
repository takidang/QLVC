class LoiNghiepVu(Exception):
    """Lỗi trả cho client theo dạng chung {ma, thong_diep, chi_tiet} (kien-truc.md mục 7)."""

    def __init__(self, ma: str, thong_diep: str, status_code: int = 422, chi_tiet: list | None = None):
        super().__init__(thong_diep)
        self.ma = ma
        self.thong_diep = thong_diep
        self.status_code = status_code
        self.chi_tiet = chi_tiet or []
