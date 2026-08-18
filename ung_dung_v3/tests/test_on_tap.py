"""Kiểm thử thuật toán ôn tập lặp ngắt quãng và phần lưu trạng thái từng từ."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from hoc_tieng_anh.mo_hinh import BaiHoc, DonVi, GiaoTrinh, MauDonVi, TuVung
from hoc_tieng_anh.on_tap import (
    DE_DANG_TOI_DA,
    DE_DANG_TOI_THIEU,
    KHOANG_CACH_TOI_DA,
    LichOnTap,
    MucThuoc,
    TrangThaiTu,
)
from hoc_tieng_anh.tien_do import TienDo

HOM_NAY = date(2026, 8, 18)


@pytest.fixture
def giao_trinh() -> GiaoTrinh:
    tu = (
        TuVung("hello", "xin chào"),
        TuVung("dog", "con chó"),
        TuVung("water", "nước"),
        TuVung("book", "quyển sách"),
    )
    return GiaoTrinh(
        don_vi=(
            DonVi(
                ma="u1",
                ten="Đơn vị 1",
                mo_ta="",
                mau=MauDonVi.XANH_LA,
                bieu_tuong="🧪",
                bai_hoc=(BaiHoc(ma="u1-1", ten="Bài 1", tu_vung=tu),),
            ),
        )
    )


class TestTrangThaiTu:
    def test_tu_moi_luon_den_han(self) -> None:
        assert TrangThaiTu(ma="hello").den_han(HOM_NAY)

    def test_dung_lan_dau_hen_lai_sau_mot_ngay(self) -> None:
        tu = TrangThaiTu(ma="hello")
        tu.ghi_nhan(True, HOM_NAY)
        assert tu.khoang_cach == 1
        assert tu.ngay_on_ke_tiep == HOM_NAY + timedelta(days=1)
        assert not tu.den_han(HOM_NAY)

    def test_khoang_cach_gian_dan_khi_lien_tuc_dung(self) -> None:
        tu = TrangThaiTu(ma="hello")
        cac_khoang: list[int] = []
        ngay = HOM_NAY
        for _ in range(5):
            tu.ghi_nhan(True, ngay)
            cac_khoang.append(tu.khoang_cach)
            ngay = tu.ngay_on_ke_tiep

        assert cac_khoang[0] == 1
        assert cac_khoang[1] == 3
        # Từ lần thứ ba trở đi khoảng cách phải nới rộng dần
        assert cac_khoang[2] > cac_khoang[1]
        assert cac_khoang[3] > cac_khoang[2]

    def test_tra_loi_sai_dua_tu_ve_on_ngay(self) -> None:
        tu = TrangThaiTu(ma="hello")
        for _ in range(3):
            tu.ghi_nhan(True, HOM_NAY)
        assert tu.khoang_cach > 1

        tu.ghi_nhan(False, HOM_NAY)
        assert tu.khoang_cach == 0
        assert tu.dung_lien_tiep == 0
        assert tu.den_han(HOM_NAY)

    def test_he_so_de_dang_bi_chan_hai_dau(self) -> None:
        de = TrangThaiTu(ma="a")
        for _ in range(30):
            de.ghi_nhan(True, HOM_NAY)
        assert de.de_dang <= DE_DANG_TOI_DA

        kho = TrangThaiTu(ma="b")
        for _ in range(30):
            kho.ghi_nhan(False, HOM_NAY)
        assert kho.de_dang >= DE_DANG_TOI_THIEU

    def test_khoang_cach_khong_vuot_tran(self) -> None:
        """Không chặn trần thì date sẽ tràn số sau vài chục lần đúng liên tiếp."""
        tu = TrangThaiTu(ma="hello")
        for _ in range(50):
            tu.ghi_nhan(True, HOM_NAY)
        assert tu.khoang_cach <= KHOANG_CACH_TOI_DA
        assert tu.ngay_on_ke_tiep is not None

    def test_muc_thuoc_tang_theo_so_lan_dung_lien_tiep(self) -> None:
        tu = TrangThaiTu(ma="hello")
        assert tu.muc_thuoc is MucThuoc.MOI

        tu.ghi_nhan(True, HOM_NAY)
        assert tu.muc_thuoc is MucThuoc.DANG_HOC

        for _ in range(2):
            tu.ghi_nhan(True, HOM_NAY)
        assert tu.muc_thuoc is MucThuoc.QUEN_THUOC

        for _ in range(2):
            tu.ghi_nhan(True, HOM_NAY)
        assert tu.muc_thuoc is MucThuoc.THUOC_LONG

    def test_ty_le_dung(self) -> None:
        tu = TrangThaiTu(ma="hello")
        tu.ghi_nhan(True, HOM_NAY)
        tu.ghi_nhan(False, HOM_NAY)
        tu.ghi_nhan(True, HOM_NAY)
        assert tu.tong_lan == 3
        assert tu.ty_le_dung == pytest.approx(2 / 3)

    def test_chuyen_doi_json_qua_lai(self) -> None:
        goc = TrangThaiTu(ma="hello")
        goc.ghi_nhan(True, HOM_NAY)
        goc.ghi_nhan(False, HOM_NAY)
        moi = TrangThaiTu.tu_dict("hello", goc.sang_dict())
        assert moi == goc

    def test_du_lieu_hong_ve_mac_dinh(self) -> None:
        tu = TrangThaiTu.tu_dict(
            "hello", {"de_dang": "hỏng", "ngay_on_ke_tiep": "không-phải-ngày"}
        )
        assert tu == TrangThaiTu(ma="hello")


class TestLichOnTap:
    def test_chi_xet_tu_da_gap(self, giao_trinh: GiaoTrinh) -> None:
        trang_thai = {"hello": TrangThaiTu(ma="hello")}
        lich = LichOnTap(giao_trinh, trang_thai)
        assert [tu.en for tu in lich.tu_da_gap] == ["hello"]

    def test_tu_chua_toi_han_khong_duoc_chon(self, giao_trinh: GiaoTrinh) -> None:
        moi_hoc = TrangThaiTu(ma="hello")
        moi_hoc.ghi_nhan(True, HOM_NAY)
        lich = LichOnTap(giao_trinh, {"hello": moi_hoc})
        assert lich.den_han(HOM_NAY) == ()

    def test_tu_qua_han_duoc_chon(self, giao_trinh: GiaoTrinh) -> None:
        cu = TrangThaiTu(ma="hello")
        cu.ghi_nhan(True, HOM_NAY - timedelta(days=10))
        lich = LichOnTap(giao_trinh, {"hello": cu})
        assert [tu.en for tu in lich.den_han(HOM_NAY)] == ["hello"]

    def test_hay_sai_uu_tien_tu_ty_le_dung_thap(self, giao_trinh: GiaoTrinh) -> None:
        kem = TrangThaiTu(ma="dog")
        kem.ghi_nhan(False, HOM_NAY)
        kem.ghi_nhan(False, HOM_NAY)
        kha = TrangThaiTu(ma="hello")
        kha.ghi_nhan(True, HOM_NAY)
        kha.ghi_nhan(False, HOM_NAY)

        lich = LichOnTap(giao_trinh, {"dog": kem, "hello": kha})
        assert [tu.en for tu in lich.hay_sai()] == ["dog", "hello"]

    def test_dem_theo_muc_tinh_ca_tu_chua_gap(self, giao_trinh: GiaoTrinh) -> None:
        thuoc = TrangThaiTu(ma="hello")
        for _ in range(5):
            thuoc.ghi_nhan(True, HOM_NAY)

        dem = LichOnTap(giao_trinh, {"hello": thuoc}).dem_theo_muc()
        assert dem[MucThuoc.THUOC_LONG] == 1
        assert dem[MucThuoc.MOI] == 3  # ba từ còn lại chưa gặp

    def test_buoi_luyen_bu_them_tu_yeu_khi_thieu(self, giao_trinh: GiaoTrinh) -> None:
        chua_den_han = TrangThaiTu(ma="hello")
        chua_den_han.ghi_nhan(True, HOM_NAY)
        yeu = TrangThaiTu(ma="dog")
        yeu.ghi_nhan(True, HOM_NAY)

        lich = LichOnTap(giao_trinh, {"hello": chua_den_han, "dog": yeu})
        chon = lich.chon_cho_buoi_luyen(so_luong=5, hom_nay=HOM_NAY)

        assert {tu.en for tu in chon} == {"hello", "dog"}
        assert len({tu.ma for tu in chon}) == len(chon)  # không trùng lặp


class TestTienDoGhiNhanTuVung:
    def test_ghi_nhan_tra_loi_tao_trang_thai_moi(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_tra_loi("hello", True, HOM_NAY)

        assert tien_do.so_tu_da_gap == 1
        assert tien_do.trang_thai_tu["hello"].tong_dung == 1

    def test_ghi_nhan_nhieu_lan_cong_don(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_tra_loi("hello", True, HOM_NAY)
        tien_do.ghi_nhan_tra_loi("hello", False, HOM_NAY)

        trang_thai = tien_do.trang_thai_tu["hello"]
        assert (trang_thai.tong_dung, trang_thai.tong_sai) == (1, 1)
        assert tien_do.so_tu_da_gap == 1

    def test_dat_lai_xoa_ca_trang_thai_tu(self) -> None:
        tien_do = TienDo()
        tien_do.ghi_nhan_tra_loi("hello", True, HOM_NAY)
        tien_do.dat_lai()
        assert tien_do.trang_thai_tu == {}

    def test_json_giu_duoc_trang_thai_tu(self) -> None:
        goc = TienDo()
        goc.ghi_nhan_hoan_thanh("u1-1", 20, HOM_NAY)
        goc.ghi_nhan_tra_loi("hello", True, HOM_NAY)
        goc.ghi_nhan_tra_loi("dog", False, HOM_NAY)

        moi = TienDo.tu_dict(goc.sang_dict())
        assert moi == goc
        assert moi.trang_thai_tu["dog"].tong_sai == 1

    def test_trang_thai_tu_hong_bi_bo_qua(self) -> None:
        tien_do = TienDo.tu_dict({"trang_thai_tu": {"hello": "không phải dict"}})
        assert tien_do.trang_thai_tu == {}
