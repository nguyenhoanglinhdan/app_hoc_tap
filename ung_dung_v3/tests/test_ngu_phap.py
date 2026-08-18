"""Kiểm thử phần ngữ pháp: mô hình, sinh câu hỏi, nạp tệp và nội dung thật."""

from __future__ import annotations

import json
from pathlib import Path
from random import Random

import pytest

from hoc_tieng_anh.bai_tap import (
    CheDoPhien,
    LoaiBaiTap,
    NoiDungPhien,
    PhienHoc,
    TrangThaiPhien,
    TrinhTaoCauHoiNguPhap,
)
from hoc_tieng_anh.kho_du_lieu import KhoDuLieu
from hoc_tieng_anh.mo_hinh import MauDonVi, TuVung, chuan_hoa
from hoc_tieng_anh.ngu_phap import (
    BoNguPhap,
    CauNguPhap,
    ChuDiemNguPhap,
    DangNguPhap,
)

THU_MUC_DU_LIEU = Path(__file__).resolve().parent.parent / "du_lieu"


def _cau(
    ma: str = "c1",
    dang: DangNguPhap = DangNguPhap.DIEN_CHO_TRONG,
    **thay_doi: object,
) -> CauNguPhap:
    mac_dinh: dict[str, object] = {
        "ma": ma,
        "dang": dang,
        "de_bai": "Chia động từ",
        "cau": "She ___ (go) to school.",
        "dap_an": "goes",
    }
    mac_dinh.update(thay_doi)
    return CauNguPhap(**mac_dinh)  # type: ignore[arg-type]


@pytest.fixture
def chu_diem() -> ChuDiemNguPhap:
    return ChuDiemNguPhap(
        ma="thi-hien-tai",
        ten="Thì hiện tại đơn",
        mo_ta="Thói quen hằng ngày",
        lop=6,
        mau=MauDonVi.XANH_DUONG,
        bieu_tuong="⏰",
        cau_hoi=(
            _cau("c1", DangNguPhap.DIEN_CHO_TRONG),
            _cau(
                "c2",
                DangNguPhap.CHON_DANG_DUNG,
                cau="He ___ TV.",
                dap_an="watches",
                lua_chon=("watches", "watch", "watching", "watched"),
            ),
            _cau(
                "c3",
                DangNguPhap.SAP_XEP_CAU,
                cau="Tôi đi học.",
                dap_an="I go to school",
            ),
        ),
    )


# ---------------------------------------------------------------------- #
# Mô hình
# ---------------------------------------------------------------------- #


class TestCauNguPhap:
    def test_manh_chu_tu_tach_theo_khoang_trang(self) -> None:
        cau = _cau(dang=DangNguPhap.SAP_XEP_CAU, dap_an="I go to school")
        assert cau.manh_chu == ("I", "go", "to", "school")

    def test_manh_chu_chi_dinh_san_duoc_giu_nguyen(self) -> None:
        cau = _cau(
            dang=DangNguPhap.SAP_XEP_CAU,
            dap_an="I go to school",
            cac_manh=("I", "go", "to school"),
        )
        assert cau.manh_chu == ("I", "go", "to school")

    def test_thieu_dap_an_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            _cau(dap_an="   ")

    def test_trac_nghiem_thieu_dap_an_trong_lua_chon_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            _cau(
                dang=DangNguPhap.CHON_DANG_DUNG,
                dap_an="goes",
                lua_chon=("go", "going", "went", "gone"),
            )

    def test_lua_chon_trung_nhau_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            _cau(
                dang=DangNguPhap.CHON_DANG_DUNG,
                dap_an="goes",
                lua_chon=("goes", "goes", "go", "going"),
            )

    def test_dang_la_bi_thay_bang_mac_dinh(self) -> None:
        assert DangNguPhap.tu_chuoi("khong-ton-tai") is DangNguPhap.CHON_DANG_DUNG


class TestBoNguPhap:
    def test_loc_theo_lop(self, chu_diem: ChuDiemNguPhap) -> None:
        lop7 = ChuDiemNguPhap(
            ma="qua-khu",
            ten="Quá khứ đơn",
            mo_ta="",
            lop=7,
            mau=MauDonVi.VANG,
            bieu_tuong="📅",
            cau_hoi=(_cau("k1"),),
        )
        bo = BoNguPhap(chu_diem=(chu_diem, lop7))

        assert bo.cac_lop == (6, 7)
        assert [cd.ma for cd in bo.theo_lop(6)] == ["thi-hien-tai"]
        assert len(bo.theo_lop(None)) == 2
        assert bo.theo_lop(9) == ()

    def test_tim_theo_ma(self, chu_diem: ChuDiemNguPhap) -> None:
        bo = BoNguPhap(chu_diem=(chu_diem,))
        assert bo.tim("thi-hien-tai") is chu_diem
        assert bo.tim("khong-co") is None

    def test_ma_trung_bi_tu_choi(self, chu_diem: ChuDiemNguPhap) -> None:
        with pytest.raises(ValueError):
            BoNguPhap(chu_diem=(chu_diem, chu_diem))

    def test_chu_diem_rong_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            ChuDiemNguPhap(
                ma="x",
                ten="X",
                mo_ta="",
                lop=6,
                mau=MauDonVi.XANH_LA,
                bieu_tuong="?",
                cau_hoi=(),
            )

    def test_bo_rong_la_falsy(self) -> None:
        assert not BoNguPhap.rong()
        assert BoNguPhap.rong().tong_so_cau == 0


# ---------------------------------------------------------------------- #
# Sinh câu hỏi
# ---------------------------------------------------------------------- #


class TestTrinhTaoCauHoiNguPhap:
    def test_moi_cau_deu_duoc_chuyen_doi(self, chu_diem: ChuDiemNguPhap) -> None:
        cau_hoi = TrinhTaoCauHoiNguPhap(Random(1)).tao(chu_diem)
        assert len(cau_hoi) == len(chu_diem)
        assert {c.ma_muc for c in cau_hoi} == {"c1", "c2", "c3"}

    def test_dang_duoc_anh_xa_dung(self, chu_diem: ChuDiemNguPhap) -> None:
        theo_ma = {c.ma_muc: c for c in TrinhTaoCauHoiNguPhap(Random(1)).tao(chu_diem)}
        assert theo_ma["c1"].loai is LoaiBaiTap.DIEN_CHO_TRONG
        assert theo_ma["c2"].loai is LoaiBaiTap.CHON_DANG_DUNG
        assert theo_ma["c3"].loai is LoaiBaiTap.SAP_XEP_CAU

    def test_cau_ngu_phap_khong_gan_voi_tu_vung(
        self, chu_diem: ChuDiemNguPhap
    ) -> None:
        for cau in TrinhTaoCauHoiNguPhap(Random(2)).tao(chu_diem):
            assert cau.tu is None
            assert cau.la_ngu_phap
            assert cau.khoa_on_tap == cau.ma_muc

    def test_manh_duoc_xao_nhung_van_du(self, chu_diem: ChuDiemNguPhap) -> None:
        cau = next(
            c
            for c in TrinhTaoCauHoiNguPhap(Random(5)).tao(chu_diem)
            if c.loai is LoaiBaiTap.SAP_XEP_CAU
        )
        assert sorted(cau.cac_manh) == sorted("I go to school".split())

    def test_cung_seed_cho_cung_ket_qua(self, chu_diem: ChuDiemNguPhap) -> None:
        mot = TrinhTaoCauHoiNguPhap(Random(9)).tao(chu_diem)
        hai = TrinhTaoCauHoiNguPhap(Random(9)).tao(chu_diem)
        assert mot == hai

    def test_cham_bai_bo_qua_hoa_thuong_va_dau_cau(
        self, chu_diem: ChuDiemNguPhap
    ) -> None:
        theo_ma = {c.ma_muc: c for c in TrinhTaoCauHoiNguPhap(Random(1)).tao(chu_diem)}
        assert theo_ma["c1"].kiem_tra("  GOES ")
        assert theo_ma["c3"].kiem_tra("i go to school.")
        assert not theo_ma["c3"].kiem_tra("go to school I")


class TestNoiDungPhien:
    def test_chu_diem_ngu_phap_co_danh_dau_hoan_thanh(
        self, chu_diem: ChuDiemNguPhap
    ) -> None:
        noi_dung = NoiDungPhien.tu_chu_diem(chu_diem, Random(1))
        assert noi_dung.che_do is CheDoPhien.NGU_PHAP
        assert noi_dung.danh_dau_hoan_thanh
        assert noi_dung.ma == chu_diem.ma

    def test_buoi_luyen_tap_khong_danh_dau(self) -> None:
        cac_tu = (TuVung("hello", "xin chào"), TuVung("dog", "con chó"))
        noi_dung = NoiDungPhien.luyen_tap(cac_tu, cac_tu, Random(1))
        assert noi_dung.che_do is CheDoPhien.LUYEN_TAP
        assert not noi_dung.danh_dau_hoan_thanh

    def test_phien_ngu_phap_chay_tron_ven(self, chu_diem: ChuDiemNguPhap) -> None:
        noi_dung = NoiDungPhien.tu_chu_diem(chu_diem, Random(4))
        phien = PhienHoc(noi_dung.cau_hoi)
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi(phien.cau_hoi_hien_tai.dap_an)
        assert phien.trang_thai is TrangThaiPhien.HOAN_THANH

    def test_ket_qua_mang_theo_loi_giai_thich(self) -> None:
        chu_diem = ChuDiemNguPhap(
            ma="x",
            ten="X",
            mo_ta="",
            lop=6,
            mau=MauDonVi.XANH_LA,
            bieu_tuong="?",
            cau_hoi=(_cau("c1", giai_thich="Ngôi thứ ba số ít thêm -es."),),
        )
        phien = PhienHoc(NoiDungPhien.tu_chu_diem(chu_diem, Random(1)).cau_hoi)
        ket_qua = phien.tra_loi("sai")
        assert ket_qua.giai_thich == "Ngôi thứ ba số ít thêm -es."


# ---------------------------------------------------------------------- #
# Nạp tệp
# ---------------------------------------------------------------------- #


class TestNapNguPhap:
    def test_thieu_tep_thi_tra_ve_bo_rong(self, tmp_path: Path) -> None:
        assert KhoDuLieu(tmp_path).tai_ngu_phap() == BoNguPhap.rong()

    def test_tep_hong_khong_lam_vo_ung_dung(self, tmp_path: Path) -> None:
        (tmp_path / "ngu_phap.json").write_text("{ hỏng", encoding="utf-8")
        assert KhoDuLieu(tmp_path).tai_ngu_phap() == BoNguPhap.rong()

    def test_noi_dung_sai_thi_bo_qua_ca_bo(self, tmp_path: Path) -> None:
        (tmp_path / "ngu_phap.json").write_text(
            json.dumps({"cac_chu_diem": [{"ma": "x"}]}), encoding="utf-8"
        )
        assert KhoDuLieu(tmp_path).tai_ngu_phap() == BoNguPhap.rong()


@pytest.fixture(scope="module")
def bo() -> BoNguPhap:
    """Bộ ngữ pháp thật đi kèm ứng dụng, nạp một lần cho cả module."""
    return KhoDuLieu(THU_MUC_DU_LIEU).tai_ngu_phap()


class TestNoiDungThat:
    """Kiểm tra chính tệp ngữ pháp đi kèm ứng dụng."""

    def test_nap_duoc_va_co_noi_dung(self, bo: BoNguPhap) -> None:
        assert bo.chu_diem
        assert bo.tong_so_cau >= 30

    def test_moi_chu_diem_thuoc_cap_hai(self, bo: BoNguPhap) -> None:
        assert all(6 <= cd.lop <= 9 for cd in bo.chu_diem)

    def test_cau_sap_xep_ghep_lai_dung_dap_an(self, bo: BoNguPhap) -> None:
        """Các mảnh chữ phải ghép lại đúng bằng đáp án, không thừa không thiếu."""
        for chu_diem in bo.chu_diem:
            for cau in chu_diem:
                if cau.dang is not DangNguPhap.SAP_XEP_CAU:
                    continue
                assert chuan_hoa(" ".join(cau.manh_chu)) == chuan_hoa(cau.dap_an), (
                    f"{cau.ma}: mảnh chữ không ghép lại thành đáp án"
                )

    def test_cau_trac_nghiem_hop_le(self, bo: BoNguPhap) -> None:
        for chu_diem in bo.chu_diem:
            for cau in chu_diem:
                if cau.dang is not DangNguPhap.CHON_DANG_DUNG:
                    continue
                assert len(cau.lua_chon) >= 2, f"{cau.ma}: quá ít lựa chọn"
                assert cau.dap_an in cau.lua_chon

    def test_cau_nao_cung_co_giai_thich(self, bo: BoNguPhap) -> None:
        """Giải thích là thứ giúp học sinh hiểu vì sao mình sai."""
        thieu = [
            cau.ma
            for chu_diem in bo.chu_diem
            for cau in chu_diem
            if not cau.giai_thich
        ]
        assert thieu == [], f"Các câu còn thiếu giải thích: {thieu}"

    def test_ma_cau_khong_trung_nhau(self, bo: BoNguPhap) -> None:
        tat_ca = [cau.ma for chu_diem in bo.chu_diem for cau in chu_diem]
        assert len(tat_ca) == len(set(tat_ca))
