"""Kiểm thử dạng bài cần âm thanh và việc ghi lại giáo trình đã sửa."""

from __future__ import annotations

import json
from pathlib import Path
from random import Random

import pytest

from hoc_tieng_anh.am_thanh import DichVuAmThanh, KetQuaPhatAm
from hoc_tieng_anh.bai_tap import (
    DAP_AN_NOI_DUNG,
    LoaiBaiTap,
    PhienHoc,
    TrangThaiPhien,
    TrinhTaoCauHoi,
)
from hoc_tieng_anh.kho_du_lieu import KhoDuLieu
from hoc_tieng_anh.mo_hinh import (
    SO_TU_MOI_BAI,
    BaiHoc,
    DonVi,
    GiaoTrinh,
    MauDonVi,
    TuVung,
)


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


class TestDangBaiCanAmThanh:
    def test_khong_co_loa_thi_khong_sinh_cau_nghe(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(1), co_loa=False, co_micro=False).tao(
            bai_hoc
        )
        assert all(not c.can_am_thanh for c in cau_hoi)

    def test_co_loa_thi_xuat_hien_cau_nghe(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(1), co_loa=True).tao(bai_hoc)
        assert any(c.loai is LoaiBaiTap.NGHE_CHON for c in cau_hoi)

    def test_cau_nghe_giau_chu_nhung_van_du_lua_chon(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(1), co_loa=True).tao(bai_hoc)
        cau_nghe = next(c for c in cau_hoi if c.loai is LoaiBaiTap.NGHE_CHON)

        assert cau_nghe.cau_hoi == ""  # không lộ đáp án ra màn hình
        assert cau_nghe.dap_an in cau_nghe.lua_chon
        assert cau_nghe.dap_an == cau_nghe.tu.en

    def test_co_micro_thi_chi_them_dung_mot_cau_noi(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(1), co_micro=True).tao(bai_hoc)
        so_cau_noi = sum(1 for c in cau_hoi if c.loai is LoaiBaiTap.NOI_THEO)
        assert so_cau_noi == 1

    def test_cau_noi_chi_nhan_dap_an_rieng(self, bai_hoc: BaiHoc) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(1), co_micro=True).tao(bai_hoc)
        cau_noi = next(c for c in cau_hoi if c.loai is LoaiBaiTap.NOI_THEO)

        assert cau_noi.kiem_tra(DAP_AN_NOI_DUNG)
        assert not cau_noi.kiem_tra(cau_noi.tu.en)
        assert not cau_noi.kiem_tra("")

    def test_phien_hoc_van_ket_thuc_duoc_voi_du_moi_dang(
        self, bai_hoc: BaiHoc
    ) -> None:
        cau_hoi = TrinhTaoCauHoi((), Random(4), co_loa=True, co_micro=True).tao(
            bai_hoc
        )
        phien = PhienHoc(cau_hoi)
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi(phien.cau_hoi_hien_tai.dap_an)
        assert phien.trang_thai is TrangThaiPhien.HOAN_THANH


class TestKhaNangAmThanh:
    def test_dich_vu_luon_khoi_tao_duoc(self) -> None:
        """Thiếu thư viện hay thiếu micro cũng không được ném lỗi."""
        dich_vu = DichVuAmThanh()
        assert isinstance(dich_vu.kha_nang.doc, bool)
        assert isinstance(dich_vu.kha_nang.thu_am, bool)
        dich_vu.dong()

    def test_doc_chuoi_rong_khong_lam_gi(self) -> None:
        dich_vu = DichVuAmThanh()
        dich_vu.doc("   ")  # không được ném lỗi
        dich_vu.dong()

    def test_ket_qua_loi_luon_la_khong_dat(self) -> None:
        ket_qua = KetQuaPhatAm.tu_loi("mất mạng")
        assert not ket_qua.dat
        assert ket_qua.diem == 0
        assert ket_qua.loi == "mất mạng"


class TestGhiLaiGiaoTrinh:
    @staticmethod
    def _giao_trinh(so_tu: int = 7) -> GiaoTrinh:
        return GiaoTrinh(
            don_vi=(
                DonVi.tu_danh_sach_tu(
                    ma="the-thao",
                    ten="Thể thao",
                    mo_ta="Các môn thể thao",
                    mau=MauDonVi.CAM,
                    bieu_tuong="⚽",
                    tu_vung=tuple(
                        TuVung(f"word{i}", f"từ {i}") for i in range(so_tu)
                    ),
                ),
            )
        )

    def test_luu_roi_tai_lai_giu_nguyen_noi_dung(self, tmp_path: Path) -> None:
        kho = KhoDuLieu(tmp_path)
        goc = self._giao_trinh()

        kho.luu_giao_trinh(goc)
        moi = kho.tai_giao_trinh()

        assert moi == goc

    def test_tep_ghi_ra_dung_dinh_dang_da_thoa_thuan(self, tmp_path: Path) -> None:
        kho = KhoDuLieu(tmp_path)
        kho.luu_giao_trinh(self._giao_trinh(so_tu=3))

        du_lieu = json.loads(
            (tmp_path / "tu_vung.json").read_text(encoding="utf-8")
        )
        don_vi = du_lieu["cac_don_vi"][0]
        assert don_vi["ma"] == "the-thao"
        assert don_vi["mau"] == "cam"
        assert len(don_vi["tu_vung"]) == 3
        assert don_vi["tu_vung"][0]["en"] == "word0"

    def test_chia_bai_giong_nhau_o_ca_hai_duong(self, tmp_path: Path) -> None:
        """Đơn vị dựng trong bộ nhớ và đơn vị đọc từ tệp phải cắt bài như nhau."""
        kho = KhoDuLieu(tmp_path)
        goc = self._giao_trinh(so_tu=SO_TU_MOI_BAI * 2 + 1)
        kho.luu_giao_trinh(goc)

        tai_lai = kho.tai_giao_trinh()
        assert [b.ma for b in tai_lai.tat_ca_bai_hoc] == [
            b.ma for b in goc.tat_ca_bai_hoc
        ]
        assert len(tai_lai.tat_ca_bai_hoc) == 3

    def test_ghi_de_khong_de_lai_tep_tam(self, tmp_path: Path) -> None:
        kho = KhoDuLieu(tmp_path)
        kho.luu_giao_trinh(self._giao_trinh())
        kho.luu_giao_trinh(self._giao_trinh(so_tu=2))
        assert list(tmp_path.glob("*.tmp")) == []
        assert len(kho.tai_giao_trinh().tat_ca_tu_vung) == 2
