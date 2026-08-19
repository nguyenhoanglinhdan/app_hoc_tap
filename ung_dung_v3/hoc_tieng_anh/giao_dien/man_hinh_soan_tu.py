"""Màn hình soạn từ vựng: thêm, sửa, xoá chủ đề và từ ngay trong ứng dụng."""

from __future__ import annotations

import logging
import unicodedata
from dataclasses import dataclass, field
from tkinter import messagebox
from typing import Sequence

import customtkinter as ctk

from ..kho_du_lieu import LoiDuLieu
from ..mo_hinh import DonVi, GiaoTrinh, MauDonVi, TuVung
from .chu_de import MAU_THEO_DON_VI, KichThuoc, Mau, phong
from .hop_thoai import (
    HopThoaiDonVi,
    HopThoaiNhapHangLoat,
    HopThoaiTu,
    ThongTinDonVi,
)
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import KieuNut, NutDuo, The

__all__ = ["ManHinhSoanTu"]

_log = logging.getLogger(__name__)


@dataclass(slots=True)
class _DonViSoan:
    """Bản nháp có thể sửa được của một đơn vị.

    Các lớp trong :mod:`hoc_tieng_anh.mo_hinh` đều bất biến, nên màn hình soạn
    thảo giữ riêng bản nháp này rồi mới dựng lại giáo trình khi lưu.
    """

    ma: str
    ten: str
    mo_ta: str
    mau: MauDonVi
    bieu_tuong: str
    tu_vung: list[TuVung] = field(default_factory=list)
    lop: int | None = None
    unit: str = ""

    @classmethod
    def tu_don_vi(cls, don_vi: DonVi) -> "_DonViSoan":
        return cls(
            ma=don_vi.ma,
            ten=don_vi.ten,
            mo_ta=don_vi.mo_ta,
            mau=don_vi.mau,
            bieu_tuong=don_vi.bieu_tuong,
            tu_vung=list(don_vi.tat_ca_tu_vung),
            lop=don_vi.lop,
            unit=don_vi.unit,
        )

    @property
    def nhan_sgk_nhap(self) -> str:
        """Nhãn lớp và bài, giống DonVi.nhan_sgk nhưng cho bản nháp."""
        phan = []
        if self.lop is not None:
            phan.append(f"Lớp {self.lop}")
        if self.unit:
            phan.append(self.unit)
        return " · ".join(phan)

    def sang_don_vi(self) -> DonVi:
        return DonVi.tu_danh_sach_tu(
            ma=self.ma,
            ten=self.ten,
            mo_ta=self.mo_ta,
            mau=self.mau,
            bieu_tuong=self.bieu_tuong,
            tu_vung=tuple(self.tu_vung),
            lop=self.lop,
            unit=self.unit,
        )


def _tao_ma(ten: str, da_dung: set[str]) -> str:
    """Sinh mã không dấu, không trùng, từ tên chủ đề."""
    khong_dau = "".join(
        ky_tu
        for ky_tu in unicodedata.normalize("NFD", ten)
        if unicodedata.category(ky_tu) != "Mn"
    )
    goc = "".join(
        ky_tu if ky_tu.isalnum() else "-" for ky_tu in khong_dau.casefold()
    ).strip("-")
    goc = "-".join(phan for phan in goc.split("-") if phan) or "chu-de"

    ma = goc
    dem = 2
    while ma in da_dung:
        ma = f"{goc}-{dem}"
        dem += 1
    return ma


class ManHinhSoanTu(ManHinh):
    """Trình soạn thảo nội dung học, ghi thẳng vào ``tu_vung.json``."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        self._ban_nhap = [
            _DonViSoan.tu_don_vi(dv) for dv in ung_dung.giao_trinh.don_vi
        ]
        self._co_thay_doi = False
        super().__init__(master, ung_dung)

    def dung_giao_dien(self) -> None:
        self._dung_dau_trang()
        self._vung = ctk.CTkScrollableFrame(
            self, fg_color=Mau.NEN, corner_radius=0, scrollbar_button_color=Mau.VIEN
        )
        self._vung.pack(fill="both", expand=True)
        self._ve_danh_sach()

    # ------------------------------------------------------------------ #

    def _dung_dau_trang(self) -> None:
        thanh = ctk.CTkFrame(self, fg_color=Mau.NEN, corner_radius=0)
        thanh.pack(fill="x", padx=KichThuoc.LE * 2, pady=(24, 12))

        chu = ctk.CTkFrame(thanh, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            chu, text="Soạn từ vựng", font=phong(26), text_color=Mau.CHU, anchor="w"
        ).pack(fill="x")
        self._nhan_trang_thai = ctk.CTkLabel(
            chu,
            text="Mọi thay đổi sẽ được ghi vào tệp tu_vung.json",
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
            anchor="w",
        )
        self._nhan_trang_thai.pack(fill="x", pady=(2, 0))

        self._nut_luu = NutDuo(
            thanh,
            text="LƯU LẠI",
            command=self._luu,
            chieu_rong=150,
            chieu_cao=44,
            co_chu=14,
            bat=False,
        )
        self._nut_luu.pack(side="right")

        ctk.CTkFrame(self, height=2, fg_color=Mau.VIEN, corner_radius=0).pack(fill="x")

    def _ve_danh_sach(self) -> None:
        for con in self._vung.winfo_children():
            con.destroy()

        for don_vi in self._ban_nhap:
            self._ve_don_vi(don_vi)

        NutDuo(
            self._vung,
            text="+  THÊM CHỦ ĐỀ",
            command=self._them_don_vi,
            kieu=KieuNut.THONG_TIN,
            chieu_rong=230,
        ).pack(pady=(20, 30))

    def _ve_don_vi(self, don_vi: _DonViSoan) -> None:
        bo_mau = MAU_THEO_DON_VI[don_vi.mau]

        the = The(self._vung)
        the.pack(fill="x", padx=KichThuoc.LE, pady=8)

        dau = ctk.CTkFrame(the, fg_color="transparent")
        dau.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            dau, text=don_vi.bieu_tuong, font=phong(24), text_color=bo_mau.chinh
        ).pack(side="left", padx=(0, 12))

        chu = ctk.CTkFrame(dau, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            chu, text=don_vi.ten, font=phong(18), text_color=Mau.CHU, anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            chu,
            text=" · ".join(
                phan
                for phan in (
                    f"{len(don_vi.tu_vung)} từ",
                    don_vi.nhan_sgk_nhap,
                    don_vi.mo_ta,
                )
                if phan
            ),
            font=phong(12, dam=False),
            text_color=Mau.CHU_MO,
            anchor="w",
        ).pack(fill="x")

        self._nut_nho(dau, "Xoá", lambda: self._xoa_don_vi(don_vi), Mau.DO).pack(
            side="right", padx=(6, 0)
        )
        self._nut_nho(dau, "Sửa", lambda: self._sua_don_vi(don_vi), Mau.CHU_PHU).pack(
            side="right"
        )

        for tu in don_vi.tu_vung:
            self._ve_tu(the, don_vi, tu)

        hang_nut = ctk.CTkFrame(the, fg_color="transparent")
        hang_nut.pack(anchor="w", padx=18, pady=(8, 16))

        NutDuo(
            hang_nut,
            text="+ Thêm từ",
            command=lambda: self._them_tu(don_vi),
            kieu=KieuNut.PHU,
            chieu_rong=140,
            chieu_cao=36,
            co_chu=13,
        ).pack(side="left")
        NutDuo(
            hang_nut,
            text="Dán danh sách",
            command=lambda: self._nhap_hang_loat(don_vi),
            kieu=KieuNut.PHU,
            chieu_rong=160,
            chieu_cao=36,
            co_chu=13,
        ).pack(side="left", padx=(8, 0))

    def _ve_tu(self, cha: ctk.CTkBaseClass, don_vi: _DonViSoan, tu: TuVung) -> None:
        hang = ctk.CTkFrame(cha, fg_color=Mau.NEN_PHU, corner_radius=KichThuoc.BO_GOC_NHO)
        hang.pack(fill="x", padx=18, pady=3)

        trong = ctk.CTkFrame(hang, fg_color="transparent")
        trong.pack(fill="x", padx=14, pady=9)

        ctk.CTkLabel(
            trong, text=tu.en, font=phong(15), text_color=Mau.CHU, anchor="w", width=150
        ).pack(side="left")
        ctk.CTkLabel(
            trong,
            text=tu.vi,
            font=phong(14, dam=False),
            text_color=Mau.CHU_PHU,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        self._nut_nho(trong, "Xoá", lambda: self._xoa_tu(don_vi, tu), Mau.DO).pack(
            side="right", padx=(6, 0)
        )
        self._nut_nho(trong, "Sửa", lambda: self._sua_tu(don_vi, tu), Mau.CHU_PHU).pack(
            side="right"
        )

    @staticmethod
    def _nut_nho(
        cha: ctk.CTkBaseClass, nhan: str, khi_bam, mau_chu
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            cha,
            text=nhan,
            command=khi_bam,
            width=52,
            height=30,
            corner_radius=KichThuoc.BO_GOC_NHO,
            fg_color="transparent",
            hover_color=Mau.VIEN,
            text_color=mau_chu,
            font=phong(13),
        )

    # ------------------------------------------------------------------ #
    # Thao tác
    # ------------------------------------------------------------------ #

    @property
    def _ma_tu_da_dung(self) -> list[str]:
        return [tu.ma for dv in self._ban_nhap for tu in dv.tu_vung]

    def _danh_dau_thay_doi(self) -> None:
        self._co_thay_doi = True
        self._nut_luu.dat_bat(True)
        self._nhan_trang_thai.configure(
            text="Có thay đổi chưa lưu", text_color=Mau.CAM_DAM
        )
        self._ve_danh_sach()

    def _them_don_vi(self) -> None:
        def luu(thong_tin: ThongTinDonVi) -> None:
            ma = _tao_ma(thong_tin.ten, {dv.ma for dv in self._ban_nhap})
            self._ban_nhap.append(
                _DonViSoan(
                    ma=ma,
                    ten=thong_tin.ten,
                    mo_ta=thong_tin.mo_ta,
                    mau=thong_tin.mau,
                    bieu_tuong=thong_tin.bieu_tuong,
                    lop=thong_tin.lop,
                    unit=thong_tin.unit,
                )
            )
            self._danh_dau_thay_doi()

        HopThoaiDonVi(self, khi_luu=luu)

    def _sua_don_vi(self, don_vi: _DonViSoan) -> None:
        def luu(thong_tin: ThongTinDonVi) -> None:
            don_vi.ten = thong_tin.ten
            don_vi.mo_ta = thong_tin.mo_ta
            don_vi.mau = thong_tin.mau
            don_vi.bieu_tuong = thong_tin.bieu_tuong
            don_vi.lop = thong_tin.lop
            don_vi.unit = thong_tin.unit
            self._danh_dau_thay_doi()

        HopThoaiDonVi(
            self,
            khi_luu=luu,
            thong_tin=ThongTinDonVi(
                ten=don_vi.ten,
                mo_ta=don_vi.mo_ta,
                mau=don_vi.mau,
                bieu_tuong=don_vi.bieu_tuong,
                lop=don_vi.lop,
                unit=don_vi.unit,
            ),
        )

    def _xoa_don_vi(self, don_vi: _DonViSoan) -> None:
        if not messagebox.askyesno(
            title="Xoá chủ đề",
            message=f"Xoá chủ đề “{don_vi.ten}” cùng {len(don_vi.tu_vung)} từ trong đó?",
            icon="warning",
            default="no",
            parent=self,
        ):
            return
        self._ban_nhap.remove(don_vi)
        self._danh_dau_thay_doi()

    def _them_tu(self, don_vi: _DonViSoan) -> None:
        def luu(tu: TuVung) -> None:
            don_vi.tu_vung.append(tu)
            self._danh_dau_thay_doi()

        HopThoaiTu(self, khi_luu=luu, ma_da_dung=self._ma_tu_da_dung)

    def _nhap_hang_loat(self, don_vi: _DonViSoan) -> None:
        """Dán cả danh sách từ vào một chủ đề."""

        def luu(cac_tu: Sequence[TuVung]) -> None:
            don_vi.tu_vung.extend(cac_tu)
            self._danh_dau_thay_doi()
            self._nhan_trang_thai.configure(
                text=f"Đã thêm {len(cac_tu)} từ, nhớ bấm Lưu lại",
                text_color=Mau.CAM_DAM,
            )

        HopThoaiNhapHangLoat(
            self, khi_luu=luu, ma_da_dung=self._ma_tu_da_dung
        )

    def _sua_tu(self, don_vi: _DonViSoan, tu: TuVung) -> None:
        def luu(moi: TuVung) -> None:
            don_vi.tu_vung[don_vi.tu_vung.index(tu)] = moi
            self._danh_dau_thay_doi()

        HopThoaiTu(self, khi_luu=luu, tu=tu, ma_da_dung=self._ma_tu_da_dung)

    def _xoa_tu(self, don_vi: _DonViSoan, tu: TuVung) -> None:
        don_vi.tu_vung.remove(tu)
        self._danh_dau_thay_doi()

    # ------------------------------------------------------------------ #
    # Lưu
    # ------------------------------------------------------------------ #

    def _luu(self) -> None:
        """Dựng lại giáo trình từ bản nháp rồi ghi xuống tệp."""
        trong_rong = [dv.ten for dv in self._ban_nhap if not dv.tu_vung]
        if trong_rong:
            messagebox.showwarning(
                title="Chủ đề chưa có từ",
                message=(
                    "Các chủ đề sau chưa có từ nào nên chưa lưu được:\n\n"
                    + "\n".join(f"· {ten}" for ten in trong_rong)
                ),
                parent=self,
            )
            return

        if not self._ban_nhap:
            messagebox.showwarning(
                title="Giáo trình trống",
                message="Cần ít nhất một chủ đề có từ vựng.",
                parent=self,
            )
            return

        try:
            giao_trinh = GiaoTrinh(
                don_vi=tuple(dv.sang_don_vi() for dv in self._ban_nhap)
            )
            self.ung_dung.luu_giao_trinh(giao_trinh)
        except (LoiDuLieu, ValueError) as loi:
            _log.exception("Không lưu được giáo trình")
            messagebox.showerror(
                title="Không lưu được", message=str(loi), parent=self
            )
            return

        self._co_thay_doi = False
        self._nut_luu.dat_bat(False)
        self._nhan_trang_thai.configure(
            text="Đã lưu vào tu_vung.json", text_color=Mau.XANH_LA_DAM
        )
