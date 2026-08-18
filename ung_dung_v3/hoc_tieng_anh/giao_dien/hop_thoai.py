"""Hộp thoại nhập liệu cho màn hình soạn từ vựng."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import customtkinter as ctk

from ..mo_hinh import MauDonVi, TuVung, chuan_hoa
from .chu_de import KichThuoc, Mau, phong
from .thanh_phan import KieuNut, NutDuo

__all__ = ["HopThoaiTu", "HopThoaiDonVi", "ThongTinDonVi"]

_NHAN_MAU: dict[MauDonVi, str] = {
    MauDonVi.XANH_LA: "Xanh lá",
    MauDonVi.XANH_DUONG: "Xanh dương",
    MauDonVi.TIM: "Tím",
    MauDonVi.CAM: "Cam",
    MauDonVi.HONG: "Hồng",
    MauDonVi.VANG: "Vàng",
}


@dataclass(frozen=True, slots=True)
class ThongTinDonVi:
    """Phần thông tin của một đơn vị mà người dùng sửa được."""

    ten: str
    mo_ta: str
    mau: MauDonVi
    bieu_tuong: str


class _HopThoaiGoc(ctk.CTkToplevel):
    """Khung nền chung: tiêu đề, vùng nhập, dòng báo lỗi và hai nút."""

    def __init__(
        self,
        cha: ctk.CTkBaseClass,
        *,
        tieu_de: str,
        chieu_rong: int = 460,
        chieu_cao: int = 420,
    ) -> None:
        super().__init__(cha)
        self.title(tieu_de)
        self.geometry(f"{chieu_rong}x{chieu_cao}")
        self.resizable(False, False)
        self.configure(fg_color=Mau.NEN)

        self.transient(cha.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._huy)

        ctk.CTkLabel(
            self, text=tieu_de, font=phong(20), text_color=Mau.CHU
        ).pack(anchor="w", padx=KichThuoc.LE, pady=(20, 14))

        self.than = ctk.CTkFrame(self, fg_color="transparent")
        self.than.pack(fill="both", expand=True, padx=KichThuoc.LE)

        self._nhan_loi = ctk.CTkLabel(
            self, text="", font=phong(13, dam=False), text_color=Mau.DO_DAM
        )
        self._nhan_loi.pack(padx=KichThuoc.LE, pady=(6, 0))

        hang_nut = ctk.CTkFrame(self, fg_color="transparent")
        hang_nut.pack(fill="x", padx=KichThuoc.LE, pady=16)

        NutDuo(
            hang_nut,
            text="HUỶ",
            command=self._huy,
            kieu=KieuNut.PHU,
            chieu_rong=130,
            chieu_cao=42,
            co_chu=14,
        ).pack(side="left")
        NutDuo(
            hang_nut,
            text="LƯU",
            command=self._luu,
            chieu_rong=150,
            chieu_cao=42,
            co_chu=14,
        ).pack(side="right")

        self.bind("<Escape>", lambda _: self._huy())
        self.bind("<Return>", lambda _: self._luu())

    # ------------------------------------------------------------------ #

    def o_nhap(self, nhan: str, gia_tri: str = "", goi_y: str = "") -> ctk.CTkEntry:
        """Thêm một ô nhập có nhãn vào thân hộp thoại."""
        ctk.CTkLabel(
            self.than,
            text=nhan,
            font=phong(13),
            text_color=Mau.CHU_PHU,
            anchor="w",
        ).pack(fill="x", pady=(10, 4))

        o = ctk.CTkEntry(
            self.than,
            height=42,
            corner_radius=KichThuoc.BO_GOC_NHO,
            border_width=2,
            border_color=Mau.VIEN,
            fg_color=Mau.NEN_THE,
            text_color=Mau.CHU,
            font=phong(15, dam=False),
            placeholder_text=goi_y,
            placeholder_text_color=Mau.CHU_MO,
        )
        o.pack(fill="x")
        if gia_tri:
            o.insert(0, gia_tri)
        return o

    def bao_loi(self, thong_bao: str) -> None:
        self._nhan_loi.configure(text=thong_bao)

    def _luu(self) -> None:
        raise NotImplementedError

    def _huy(self) -> None:
        self.grab_release()
        self.destroy()

    def dong(self) -> None:
        self._huy()


class HopThoaiTu(_HopThoaiGoc):
    """Nhập hoặc sửa một từ vựng."""

    def __init__(
        self,
        cha: ctk.CTkBaseClass,
        *,
        khi_luu: Callable[[TuVung], None],
        tu: TuVung | None = None,
        ma_da_dung: Sequence[str] = (),
    ) -> None:
        super().__init__(
            cha,
            tieu_de="Sửa từ" if tu else "Thêm từ mới",
            chieu_cao=400,
        )
        self._khi_luu = khi_luu
        self._ma_da_dung = {ma for ma in ma_da_dung if not tu or ma != tu.ma}

        self._o_en = self.o_nhap("Từ tiếng Anh", tu.en if tu else "", "hello")
        self._o_vi = self.o_nhap("Nghĩa tiếng Việt", tu.vi if tu else "", "xin chào")
        self._o_phien_am = self.o_nhap(
            "Phiên âm (không bắt buộc)", tu.phien_am if tu else "", "/həˈloʊ/"
        )
        self._o_en.after(60, self._o_en.focus_set)

    def _luu(self) -> None:
        en = self._o_en.get().strip()
        vi = self._o_vi.get().strip()

        if not en or not vi:
            self.bao_loi("Cần nhập cả từ tiếng Anh lẫn nghĩa tiếng Việt.")
            return
        if chuan_hoa(en) in self._ma_da_dung:
            self.bao_loi(f"Từ “{en}” đã có trong giáo trình rồi.")
            return

        self._khi_luu(TuVung(en=en, vi=vi, phien_am=self._o_phien_am.get().strip()))
        self._huy()


class HopThoaiDonVi(_HopThoaiGoc):
    """Nhập hoặc sửa thông tin một đơn vị."""

    def __init__(
        self,
        cha: ctk.CTkBaseClass,
        *,
        khi_luu: Callable[[ThongTinDonVi], None],
        thong_tin: ThongTinDonVi | None = None,
    ) -> None:
        super().__init__(
            cha,
            tieu_de="Sửa chủ đề" if thong_tin else "Thêm chủ đề mới",
            chieu_cao=470,
        )
        self._khi_luu = khi_luu

        self._o_ten = self.o_nhap("Tên chủ đề", thong_tin.ten if thong_tin else "", "Thể thao")
        self._o_mo_ta = self.o_nhap(
            "Mô tả ngắn", thong_tin.mo_ta if thong_tin else "", "Các môn thể thao"
        )
        self._o_bieu_tuong = self.o_nhap(
            "Biểu tượng", thong_tin.bieu_tuong if thong_tin else "📘", "⚽"
        )

        ctk.CTkLabel(
            self.than,
            text="Màu chủ đề",
            font=phong(13),
            text_color=Mau.CHU_PHU,
            anchor="w",
        ).pack(fill="x", pady=(12, 4))

        self._mau = ctk.StringVar(
            value=_NHAN_MAU[thong_tin.mau if thong_tin else MauDonVi.XANH_LA]
        )
        ctk.CTkOptionMenu(
            self.than,
            values=list(_NHAN_MAU.values()),
            variable=self._mau,
            height=40,
            corner_radius=KichThuoc.BO_GOC_NHO,
            font=phong(14),
            fg_color=Mau.NEN_THE,
            button_color=Mau.VIEN,
            button_hover_color=Mau.XAM_DAM,
            text_color=Mau.CHU,
        ).pack(fill="x")

        self._o_ten.after(60, self._o_ten.focus_set)

    def _luu(self) -> None:
        ten = self._o_ten.get().strip()
        if not ten:
            self.bao_loi("Chủ đề cần có tên.")
            return

        nhan_mau = self._mau.get()
        mau = next(
            (m for m, nhan in _NHAN_MAU.items() if nhan == nhan_mau),
            MauDonVi.XANH_LA,
        )
        self._khi_luu(
            ThongTinDonVi(
                ten=ten,
                mo_ta=self._o_mo_ta.get().strip(),
                mau=mau,
                bieu_tuong=self._o_bieu_tuong.get().strip() or "📘",
            )
        )
        self._huy()
