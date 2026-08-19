"""Kiểm thử nhập từ hàng loạt và chế độ kiểm tra chấm thang 10."""

from __future__ import annotations

from datetime import date
from random import Random

import pytest

from hoc_tieng_anh.bai_tap import (
    SO_CAU_KIEM_TRA,
    CheDoPhien,
    LoaiBaiTap,
    NoiDungPhien,
    PhienHoc,
    TrangThaiPhien,
)
from hoc_tieng_anh.mo_hinh import BaiHoc, MauDonVi, TuVung
from hoc_tieng_anh.ngu_phap import CauNguPhap, ChuDiemNguPhap, DangNguPhap
from hoc_tieng_anh.nhap_hang_loat import tach_danh_sach
from hoc_tieng_anh.tien_do import SO_DIEM_LUU, KetQuaKiemTra, TienDo

HOM_NAY = date(2026, 8, 19)


# ---------------------------------------------------------------------- #
# Nhập hàng loạt
# ---------------------------------------------------------------------- #


class TestTachDanhSach:
    @pytest.mark.parametrize(
        "dong",
        [
            "borrow = mượn",
            "borrow : mượn",
            "borrow\tmượn",
            "borrow | mượn",
            "borrow - mượn",
        ],
    )
    def test_nhan_moi_dau_ngan_thong_dung(self, dong: str) -> None:
        ket_qua = tach_danh_sach(dong)
        assert ket_qua.so_tu == 1
        assert ket_qua.tu_vung[0].en == "borrow"
        assert ket_qua.tu_vung[0].vi == "mượn"

    def test_cot_thu_ba_thanh_cau_vi_du(self) -> None:
        ket_qua = tach_danh_sach("borrow = mượn = Can I borrow your pen?")
        assert ket_qua.tu_vung[0].vi_du == "Can I borrow your pen?"

    def test_chon_dau_ngan_xuat_hien_som_nhat(self) -> None:
        """Dòng lẫn nhiều loại dấu phải cắt ở dấu gõ trước, không phải dấu bất kỳ."""
        ket_qua = tach_danh_sach("shout | hét | He shouted loudly.")
        tu = ket_qua.tu_vung[0]
        assert (tu.en, tu.vi, tu.vi_du) == ("shout", "hét", "He shouted loudly.")

    def test_bo_qua_so_thu_tu_dau_dong(self) -> None:
        ket_qua = tach_danh_sach("1. borrow = mượn\n2) lend = cho mượn")
        assert [t.en for t in ket_qua.tu_vung] == ["borrow", "lend"]

    def test_bo_qua_dong_trong_va_chu_thich(self) -> None:
        ket_qua = tach_danh_sach("# danh sách\n\nborrow = mượn\n// ghi chú\n")
        assert ket_qua.so_tu == 1
        assert not ket_qua.co_loi

    def test_bao_loi_dong_thieu_dau_ngan(self) -> None:
        ket_qua = tach_danh_sach("borrow mượn")
        assert ket_qua.so_tu == 0
        assert ket_qua.dong_loi[0].so_dong == 1
        assert "dấu ngăn" in ket_qua.dong_loi[0].ly_do

    def test_bao_loi_dong_thieu_cot(self) -> None:
        ket_qua = tach_danh_sach("borrow = ")
        assert ket_qua.so_tu == 0
        assert ket_qua.co_loi

    def test_bao_trung_voi_tu_da_co(self) -> None:
        ket_qua = tach_danh_sach("Hello = xin chào", ma_da_co=("hello",))
        assert ket_qua.so_tu == 0
        assert "đã có" in ket_qua.dong_loi[0].ly_do

    def test_bao_trung_ngay_trong_danh_sach_dan_vao(self) -> None:
        ket_qua = tach_danh_sach("borrow = mượn\nBORROW = mượn lại")
        assert ket_qua.so_tu == 1
        assert len(ket_qua.dong_loi) == 1

    def test_van_ban_rong(self) -> None:
        ket_qua = tach_danh_sach("   \n\n")
        assert not ket_qua
        assert not ket_qua.co_loi

    def test_giu_nguyen_thu_tu_dan_vao(self) -> None:
        ket_qua = tach_danh_sach("a = một\nb = hai\nc = ba")
        assert [t.en for t in ket_qua.tu_vung] == ["a", "b", "c"]


# ---------------------------------------------------------------------- #
# Chế độ kiểm tra
# ---------------------------------------------------------------------- #


@pytest.fixture
def cac_tu() -> tuple[TuVung, ...]:
    return tuple(TuVung(f"word{i}", f"từ {i}") for i in range(30))


@pytest.fixture
def chu_diem() -> ChuDiemNguPhap:
    return ChuDiemNguPhap(
        ma="cd",
        ten="Chủ điểm",
        mo_ta="",
        lop=6,
        mau=MauDonVi.XANH_LA,
        bieu_tuong="?",
        cau_hoi=tuple(
            CauNguPhap(
                ma=f"cd-{i}",
                dang=DangNguPhap.DIEN_CHO_TRONG,
                de_bai="Điền",
                cau=f"Câu {i} ___",
                dap_an=f"dapan{i}",
                giai_thich="vì thế",
            )
            for i in range(8)
        ),
    )


class TestPhienKhongCoTim:
    def test_khong_gioi_han_tim_thi_khong_bao_gio_het_tim(self) -> None:
        cau_hoi = NoiDungPhien.tu_bai_hoc(
            BaiHoc(
                ma="b",
                ten="B",
                tu_vung=tuple(TuVung(f"w{i}", f"t{i}") for i in range(6)),
            ),
            (),
            Random(1),
        ).cau_hoi
        phien = PhienHoc(cau_hoi, so_tim=None, hoi_lai_cau_sai=False)

        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi("chắc chắn sai")

        assert phien.trang_thai is TrangThaiPhien.HOAN_THANH
        assert phien.so_cau_dung == 0
        assert phien.diem_thang_muoi == 0.0

    def test_khong_hoi_lai_thi_moi_cau_chi_hoi_mot_lan(self) -> None:
        cau_hoi = NoiDungPhien.tu_bai_hoc(
            BaiHoc(
                ma="b",
                ten="B",
                tu_vung=tuple(TuVung(f"w{i}", f"t{i}") for i in range(5)),
            ),
            (),
            Random(2),
        ).cau_hoi
        tong = len(cau_hoi)
        phien = PhienHoc(cau_hoi, so_tim=None, hoi_lai_cau_sai=False)

        so_lan = 0
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            phien.tra_loi("sai")
            so_lan += 1

        assert so_lan == tong

    def test_diem_thang_muoi(self) -> None:
        cau_hoi = NoiDungPhien.tu_bai_hoc(
            BaiHoc(
                ma="b",
                ten="B",
                tu_vung=tuple(TuVung(f"w{i}", f"t{i}") for i in range(10)),
            ),
            (),
            Random(3),
        ).cau_hoi
        phien = PhienHoc(cau_hoi, so_tim=None, hoi_lai_cau_sai=False)

        thu_tu = 0
        while phien.trang_thai is TrangThaiPhien.DANG_HOC:
            cau = phien.cau_hoi_hien_tai
            phien.tra_loi(cau.dap_an if thu_tu % 2 == 0 else "sai")
            thu_tu += 1

        assert phien.diem_thang_muoi == pytest.approx(
            round(phien.so_cau_dung / phien.tong_so_cau * 10, 1)
        )


class TestDeKiemTra:
    def test_de_tron_ca_tu_vung_lan_ngu_phap(self, cac_tu, chu_diem) -> None:
        noi_dung = NoiDungPhien.kiem_tra(cac_tu, (chu_diem,), Random(5))
        assert noi_dung.che_do is CheDoPhien.KIEM_TRA
        assert noi_dung.la_kiem_tra
        assert len(noi_dung.cau_hoi) == SO_CAU_KIEM_TRA

        co_ngu_phap = any(c.la_ngu_phap for c in noi_dung.cau_hoi)
        co_tu_vung = any(not c.la_ngu_phap for c in noi_dung.cau_hoi)
        assert co_ngu_phap and co_tu_vung

    def test_de_khong_chua_cau_ghep_doi(self, cac_tu, chu_diem) -> None:
        """Ghép đôi gộp nhiều từ vào một câu nên không hợp để chấm điểm."""
        noi_dung = NoiDungPhien.kiem_tra(cac_tu, (chu_diem,), Random(6))
        assert all(c.loai is not LoaiBaiTap.GHEP_DOI for c in noi_dung.cau_hoi)

    def test_de_khong_danh_dau_hoan_thanh(self, cac_tu, chu_diem) -> None:
        noi_dung = NoiDungPhien.kiem_tra(cac_tu, (chu_diem,), Random(7))
        assert not noi_dung.danh_dau_hoan_thanh

    def test_chi_co_ngu_phap_van_ra_duoc_de(self, chu_diem) -> None:
        noi_dung = NoiDungPhien.kiem_tra((), (chu_diem,), Random(8))
        assert noi_dung.cau_hoi
        assert all(c.la_ngu_phap for c in noi_dung.cau_hoi)

    def test_khong_co_noi_dung_thi_bao_loi(self) -> None:
        with pytest.raises(ValueError):
            NoiDungPhien.kiem_tra((), (), Random(9))


class TestKetQuaKiemTra:
    def test_diem_va_xep_loai(self) -> None:
        assert KetQuaKiemTra(HOM_NAY, 20, 20).diem == 10.0
        assert KetQuaKiemTra(HOM_NAY, 20, 16).xep_loai == "Giỏi"
        assert KetQuaKiemTra(HOM_NAY, 20, 14).xep_loai == "Khá"
        assert KetQuaKiemTra(HOM_NAY, 20, 11).xep_loai == "Trung bình"
        assert KetQuaKiemTra(HOM_NAY, 20, 4).xep_loai == "Cần cố gắng"

    def test_so_lieu_khong_hop_le_bi_tu_choi(self) -> None:
        with pytest.raises(ValueError):
            KetQuaKiemTra(HOM_NAY, 0, 0)
        with pytest.raises(ValueError):
            KetQuaKiemTra(HOM_NAY, 10, 11)

    def test_ghi_nhan_luu_lich_su_va_cong_xp(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_kiem_tra(20, 15, giay=180, hom_nay=HOM_NAY)

        assert len(tien_do.lich_su_kiem_tra) == 1
        assert tien_do.lich_su_kiem_tra[0].diem == 7.5
        assert tien_do.xp == 15
        assert tien_do.chuoi_ngay == 1

    def test_bai_moi_nhat_dung_dau(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_kiem_tra(10, 5, hom_nay=HOM_NAY)
        tien_do.ghi_nhan_kiem_tra(10, 9, hom_nay=HOM_NAY)
        assert tien_do.lich_su_kiem_tra[0].so_dung == 9
        assert tien_do.diem_kiem_tra_cao_nhat == 9.0

    def test_chi_giu_lai_so_bai_gan_nhat(self) -> None:
        tien_do = TienDo()
        for i in range(SO_DIEM_LUU + 5):
            tien_do.ghi_nhan_kiem_tra(10, i % 10, hom_nay=HOM_NAY)
        assert len(tien_do.lich_su_kiem_tra) == SO_DIEM_LUU

    def test_json_qua_lai_giu_duoc_lich_su(self) -> None:
        goc = TienDo()
        goc.ghi_nhan_kiem_tra(20, 18, giay=120, hom_nay=HOM_NAY)
        moi = TienDo.tu_dict(goc.sang_dict())
        assert moi == goc

    def test_ban_ghi_hong_bi_bo_qua(self) -> None:
        tien_do = TienDo.tu_dict(
            {"lich_su_kiem_tra": [{"ngay": "hỏng"}, {"so_cau": 10, "so_dung": 5}]}
        )
        assert tien_do.lich_su_kiem_tra == []

    def test_dat_lai_xoa_ca_bang_diem(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_kiem_tra(10, 8, hom_nay=HOM_NAY)
        tien_do.dat_lai()
        assert tien_do.lich_su_kiem_tra == []
        assert tien_do.diem_kiem_tra_cao_nhat is None
