"""Kiểm thử phần lõi: mô hình, sinh câu hỏi, phiên học, tiến độ và kho dữ liệu.

Toàn bộ kiểm thử chạy không cần cửa sổ Tk.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from random import Random

import pytest

from hoc_tieng_anh.bai_tap import (
    DAP_AN_GHEP_DUNG,
    LoaiBaiTap,
    PhienHoc,
    TrangThaiPhien,
    TrinhTaoCauHoi,
)
from hoc_tieng_anh.kho_du_lieu import KhoDuLieu, LoiDuLieu
from hoc_tieng_anh.mo_hinh import BaiHoc, GiaoTrinh, TuVung, chuan_hoa
from hoc_tieng_anh.tien_do import XP_MOI_CAP, TienDo


# ---------------------------------------------------------------------- #
# Dữ liệu dùng chung
# ---------------------------------------------------------------------- #


@pytest.fixture
def bai_hoc() -> BaiHoc:
    return BaiHoc(
        ma="thu-1",
        ten="Bài 1",
        tu_vung=(
            TuVung("hello", "xin chào"),
            TuVung("dog", "con chó"),
            TuVung("water", "nước"),
            TuVung("book", "quyển sách"),
            TuVung("red", "màu đỏ"),
        ),
    )


@pytest.fixture
def kho_nhieu() -> tuple[TuVung, ...]:
    return (
        TuVung("cat", "con mèo"),
        TuVung("milk", "sữa"),
        TuVung("pen", "cái bút"),
        TuVung("blue", "màu xanh dương"),
    )


# ---------------------------------------------------------------------- #
# Mô hình
# ---------------------------------------------------------------------- #


class TestChuanHoa:
    @pytest.mark.parametrize(
        ("dau_vao", "mong_doi"),
        [
            ("Xin chào!", "xin chao"),
            ("  HELLO  ", "hello"),
            ("Tiếng  Việt", "tieng viet"),
            ("good morning.", "good morning"),
        ],
    )
    def test_bo_dau_va_gop_khoang_trang(self, dau_vao: str, mong_doi: str) -> None:
        assert chuan_hoa(dau_vao) == mong_doi


class TestTuVung:
    def test_khop_dap_an_bo_qua_hoa_thuong_va_khoang_trang(self) -> None:
        tu = TuVung("Good morning", "chào buổi sáng")
        assert tu.khop_dap_an("  good MORNING ")
        assert tu.khop_dap_an("good morning!")
        assert not tu.khop_dap_an("good evening")

    def test_tu_rong_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            TuVung("", "trống")


class TestGiaoTrinh:
    def test_bai_hoc_khong_co_tu_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            BaiHoc(ma="x", ten="X", tu_vung=())

    def test_giao_trinh_rong_van_hop_le(self) -> None:
        assert GiaoTrinh.rong().tat_ca_bai_hoc == ()


# ---------------------------------------------------------------------- #
# Sinh câu hỏi
# ---------------------------------------------------------------------- #


class TestTrinhTaoCauHoi:
    def test_moi_tu_deu_co_cau_hoi(self, bai_hoc: BaiHoc, kho_nhieu) -> None:
        cau_hoi = TrinhTaoCauHoi(kho_nhieu, Random(1)).tao(bai_hoc)
        tu_duoc_hoi = {
            c.tu.en for c in cau_hoi if c.loai is not LoaiBaiTap.GHEP_DOI
        }
        assert tu_duoc_hoi == {tu.en for tu in bai_hoc.tu_vung}

    def test_cung_seed_cho_cung_ket_qua(self, bai_hoc: BaiHoc, kho_nhieu) -> None:
        mot = TrinhTaoCauHoi(kho_nhieu, Random(42)).tao(bai_hoc)
        hai = TrinhTaoCauHoi(kho_nhieu, Random(42)).tao(bai_hoc)
        assert mot == hai

    def test_trac_nghiem_luon_chua_dap_an_dung(
        self, bai_hoc: BaiHoc, kho_nhieu
    ) -> None:
        for cau in TrinhTaoCauHoi(kho_nhieu, Random(3)).tao(bai_hoc):
            if cau.loai in (LoaiBaiTap.CHON_NGHIA, LoaiBaiTap.CHON_TU):
                assert cau.dap_an in cau.lua_chon
                assert len(set(cau.lua_chon)) == len(cau.lua_chon)

    def test_co_cau_ghep_doi_khi_du_tu(self, bai_hoc: BaiHoc, kho_nhieu) -> None:
        cau_hoi = TrinhTaoCauHoi(kho_nhieu, Random(5)).tao(bai_hoc)
        assert any(c.loai is LoaiBaiTap.GHEP_DOI for c in cau_hoi)

    def test_bai_qua_ngan_khong_sinh_cau_ghep(self, kho_nhieu) -> None:
        ngan = BaiHoc(ma="ngan", ten="Ngắn", tu_vung=(TuVung("sun", "mặt trời"),))
        cau_hoi = TrinhTaoCauHoi(kho_nhieu, Random(0)).tao(ngan)
        assert all(c.loai is not LoaiBaiTap.GHEP_DOI for c in cau_hoi)

    def test_thieu_tu_nhieu_van_tao_duoc_cau_hoi(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(9)).tao(bai_hoc)
        for cau in cau_hoi:
            if cau.loai in (LoaiBaiTap.CHON_NGHIA, LoaiBaiTap.CHON_TU):
                assert cau.dap_an in cau.lua_chon


# ---------------------------------------------------------------------- #
# Phiên học
# ---------------------------------------------------------------------- #


def _tao_phien(bai_hoc: BaiHoc, seed: int = 11) -> PhienHoc:
    cau_hoi = TrinhTaoCauHoi((), Random(seed)).tao(bai_hoc)
    return PhienHoc(bai_hoc, cau_hoi)


def _dap_an_dung(cau) -> str:
    if cau.loai is LoaiBaiTap.GHEP_DOI:
        return DAP_AN_GHEP_DUNG
    return cau.dap_an


class TestPhienHoc:
    def test_tra_loi_dung_het_thi_hoan_thanh(self, bai_hoc: BaiHoc) -> None:
        phien = _tao_phien(bai_hoc)
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi(_dap_an_dung(phien.cau_hoi_hien_tai))

        assert phien.trang_thai is TrangThaiPhien.HOAN_THANH
        assert phien.hoan_hao
        assert phien.con_tim == PhienHoc.SO_TIM_TOI_DA
        assert phien.ty_le_hoan_thanh == 1.0

    def test_thuong_xp_khi_khong_sai_cau_nao(self, bai_hoc: BaiHoc) -> None:
        phien = _tao_phien(bai_hoc)
        so_cau = len(phien._hang_doi)  # noqa: SLF001 - kiểm tra nội bộ có chủ đích
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi(_dap_an_dung(phien.cau_hoi_hien_tai))

        assert phien.xp_dat_duoc == (
            so_cau * PhienHoc.XP_MOI_CAU + PhienHoc.XP_THUONG_HOAN_HAO
        )

    def test_tra_loi_sai_mat_tim_va_hoi_lai(self, bai_hoc: BaiHoc) -> None:
        phien = _tao_phien(bai_hoc)
        cau_dau = phien.cau_hoi_hien_tai

        ket_qua = phien.tra_loi("đáp án chắc chắn sai")

        assert not ket_qua.dung
        assert ket_qua.con_tim == PhienHoc.SO_TIM_TOI_DA - 1
        assert not phien.hoan_hao
        # Câu sai được đẩy xuống cuối hàng đợi để hỏi lại.
        assert phien.cau_hoi_hien_tai is not cau_dau
        assert cau_dau in phien._hang_doi  # noqa: SLF001

    def test_het_tim_thi_dung_phien(self, bai_hoc: BaiHoc) -> None:
        phien = _tao_phien(bai_hoc)
        for _ in range(PhienHoc.SO_TIM_TOI_DA):
            phien.tra_loi("sai")

        assert phien.trang_thai is TrangThaiPhien.HET_TIM
        assert phien.con_tim == 0
        assert phien.xp_dat_duoc == 0

    def test_tra_loi_khi_da_ket_thuc_bao_loi(self, bai_hoc: BaiHoc) -> None:
        phien = _tao_phien(bai_hoc)
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi(_dap_an_dung(phien.cau_hoi_hien_tai))

        with pytest.raises(RuntimeError):
            phien.tra_loi("bất kỳ")

    def test_phien_khong_co_cau_hoi_bi_tu_choi(self, bai_hoc: BaiHoc) -> None:
        with pytest.raises(ValueError):
            PhienHoc(bai_hoc, ())


# ---------------------------------------------------------------------- #
# Tiến độ
# ---------------------------------------------------------------------- #


class TestTienDo:
    def test_cap_do_tang_theo_xp(self) -> None:
        assert TienDo(xp=0).cap_do == 1
        assert TienDo(xp=XP_MOI_CAP - 1).cap_do == 1
        assert TienDo(xp=XP_MOI_CAP).cap_do == 2
        assert TienDo(xp=XP_MOI_CAP * 3 + 5).cap_do == 4

    def test_hoc_lan_dau_bat_dau_chuoi(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("b1", 20, date(2026, 8, 18))
        assert tien_do.chuoi_ngay == 1
        assert tien_do.xp == 20

    def test_hoc_ngay_ke_tiep_tang_chuoi(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("b1", 10, date(2026, 8, 18))
        tien_do.ghi_nhan_hoan_thanh("b2", 10, date(2026, 8, 19))
        assert tien_do.chuoi_ngay == 2

    def test_hoc_lai_trong_ngay_khong_tang_chuoi(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("b1", 10, date(2026, 8, 18))
        tien_do.ghi_nhan_hoan_thanh("b2", 10, date(2026, 8, 18))
        assert tien_do.chuoi_ngay == 1
        assert tien_do.xp == 20

    def test_nghi_qua_lau_thi_chuoi_bat_dau_lai(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("b1", 10, date(2026, 8, 10))
        tien_do.ghi_nhan_hoan_thanh("b2", 10, date(2026, 8, 18))
        assert tien_do.chuoi_ngay == 1

    def test_chuoi_thuc_te_ve_khong_khi_da_dut(self) -> None:
        hom_nay = date(2026, 8, 18)
        tien_do = TienDo(xp=50, chuoi_ngay=7, ngay_hoc_cuoi=hom_nay - timedelta(days=3))
        assert tien_do.chuoi_ngay_thuc_te(hom_nay) == 0

    def test_chuoi_thuc_te_giu_nguyen_khi_moi_hoc_hom_qua(self) -> None:
        hom_nay = date(2026, 8, 18)
        tien_do = TienDo(xp=50, chuoi_ngay=7, ngay_hoc_cuoi=hom_nay - timedelta(days=1))
        assert tien_do.chuoi_ngay_thuc_te(hom_nay) == 7

    def test_xp_am_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            TienDo().ghi_nhan_hoan_thanh("b1", -5)

    def test_dat_lai_xoa_sach(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("b1", 30, date(2026, 8, 18))
        tien_do.dat_lai()
        assert (tien_do.xp, tien_do.chuoi_ngay, tien_do.ngay_hoc_cuoi) == (0, 0, None)
        assert tien_do.so_lan_hoan_thanh == {}

    def test_chuyen_doi_json_qua_lai(self) -> None:
        goc = TienDo()
        goc.ghi_nhan_hoan_thanh("b1", 22, date(2026, 8, 18))
        moi = TienDo.tu_dict(goc.sang_dict())
        assert moi == goc

    def test_du_lieu_hong_khong_lam_vo_ung_dung(self) -> None:
        tien_do = TienDo.tu_dict(
            {"xp": "hỏng", "chuoi_ngay": None, "ngay_hoc_cuoi": "không-phải-ngày"}
        )
        assert tien_do == TienDo()


# ---------------------------------------------------------------------- #
# Kho dữ liệu
# ---------------------------------------------------------------------- #


class TestKhoDuLieu:
    @staticmethod
    def _viet_giao_trinh(thu_muc: Path, so_tu: int = 7) -> None:
        du_lieu = {
            "cac_don_vi": [
                {
                    "ma": "test",
                    "ten": "Kiểm thử",
                    "mo_ta": "",
                    "mau": "xanh_la",
                    "bieu_tuong": "🧪",
                    "tu_vung": [
                        {"en": f"word{i}", "vi": f"từ {i}"} for i in range(so_tu)
                    ],
                }
            ]
        }
        (thu_muc / "tu_vung.json").write_text(
            json.dumps(du_lieu, ensure_ascii=False), encoding="utf-8"
        )

    def test_tai_giao_trinh_va_chia_bai(self, tmp_path: Path) -> None:
        self._viet_giao_trinh(tmp_path, so_tu=7)
        giao_trinh = KhoDuLieu(tmp_path).tai_giao_trinh()

        assert len(giao_trinh.don_vi) == 1
        assert len(giao_trinh.tat_ca_bai_hoc) == 2  # 5 từ + 2 từ
        assert len(giao_trinh.tat_ca_tu_vung) == 7

    def test_thieu_tep_thi_bao_loi_ro_rang(self, tmp_path: Path) -> None:
        with pytest.raises(LoiDuLieu):
            KhoDuLieu(tmp_path).tai_giao_trinh()

    def test_json_hong_thi_bao_loi(self, tmp_path: Path) -> None:
        (tmp_path / "tu_vung.json").write_text("{ hỏng", encoding="utf-8")
        with pytest.raises(LoiDuLieu):
            KhoDuLieu(tmp_path).tai_giao_trinh()

    def test_luu_va_tai_lai_tien_do(self, tmp_path: Path) -> None:
        kho = KhoDuLieu(tmp_path)
        tien_do = TienDo()
        tien_do.ghi_nhan_hoan_thanh("test-1", 24, date(2026, 8, 18))

        kho.luu_tien_do(tien_do)
        assert kho.tai_tien_do() == tien_do

    def test_khong_co_tep_tien_do_thi_bat_dau_moi(self, tmp_path: Path) -> None:
        assert KhoDuLieu(tmp_path).tai_tien_do() == TienDo()

    def test_tep_tien_do_hong_thi_bat_dau_moi(self, tmp_path: Path) -> None:
        (tmp_path / "tien_do.json").write_text("không phải json", encoding="utf-8")
        assert KhoDuLieu(tmp_path).tai_tien_do() == TienDo()

    def test_luu_khong_de_lai_tep_tam(self, tmp_path: Path) -> None:
        kho = KhoDuLieu(tmp_path)
        kho.luu_tien_do(TienDo(xp=10))
        assert list(tmp_path.glob("*.tmp")) == []
