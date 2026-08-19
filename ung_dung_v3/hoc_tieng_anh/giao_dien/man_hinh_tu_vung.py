"""Màn hình tra cứu: toàn bộ từ vựng, nhóm theo đơn vị, có ô tìm kiếm."""

from __future__ import annotations

import customtkinter as ctk

from ..mo_hinh import DonVi, TuVung, chuan_hoa
from .chu_de import MAU_THEO_DON_VI, KichThuoc, Mau, phong
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import The

__all__ = ["ManHinhTuVung"]

_TAT_CA = "Tất cả"


class ManHinhTuVung(ManHinh):
    """Danh sách từ vựng kèm bộ lọc theo từ khoá."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        self._tu_khoa = ""
        self._lop_dang_chon: int | None = None
        super().__init__(master, ung_dung)

    def dung_giao_dien(self) -> None:
        self._dung_thanh_tim()
        self._vung_danh_sach = ctk.CTkScrollableFrame(
            self, fg_color=Mau.NEN, corner_radius=0, scrollbar_button_color=Mau.VIEN
        )
        self._vung_danh_sach.pack(fill="both", expand=True)
        self._ve_danh_sach()

    def _dung_thanh_tim(self) -> None:
        thanh = ctk.CTkFrame(self, fg_color=Mau.NEN, corner_radius=0)
        thanh.pack(fill="x", padx=KichThuoc.LE * 2, pady=(24, 12))

        ctk.CTkLabel(
            thanh,
            text="Sổ tay từ vựng",
            font=phong(26),
            text_color=Mau.CHU,
        ).pack(anchor="w", pady=(0, 12))

        o_tim = ctk.CTkEntry(
            thanh,
            height=46,
            corner_radius=KichThuoc.BO_GOC,
            border_width=2,
            border_color=Mau.VIEN,
            fg_color=Mau.NEN_THE,
            text_color=Mau.CHU,
            font=phong(15, dam=False),
            placeholder_text="🔍  Tìm từ tiếng Anh hoặc nghĩa tiếng Việt...",
            placeholder_text_color=Mau.CHU_MO,
        )
        o_tim.pack(fill="x")
        o_tim.bind("<KeyRelease>", lambda _: self._khi_tim(o_tim.get()))

        cac_lop = self.ung_dung.giao_trinh.cac_lop
        if cac_lop:
            bo_loc = ctk.CTkSegmentedButton(
                thanh,
                values=[_TAT_CA, *(f"Lớp {lop}" for lop in cac_lop)],
                command=self._doi_lop,
                font=phong(13),
                corner_radius=KichThuoc.BO_GOC_NHO,
                selected_color=Mau.XANH_LA,
                selected_hover_color=Mau.XANH_LA_DAM,
                unselected_color=Mau.NEN_PHU,
                text_color=Mau.CHU,
            )
            bo_loc.pack(anchor="w", pady=(12, 0))
            bo_loc.set(_TAT_CA)

        ctk.CTkFrame(self, height=2, fg_color=Mau.VIEN, corner_radius=0).pack(fill="x")

    def _doi_lop(self, lua_chon: str) -> None:
        self._lop_dang_chon = (
            None if lua_chon == _TAT_CA else int(lua_chon.removeprefix("Lớp "))
        )
        self._ve_danh_sach()

    def _khi_tim(self, tu_khoa: str) -> None:
        moi = chuan_hoa(tu_khoa)
        if moi == self._tu_khoa:
            return
        self._tu_khoa = moi
        self._ve_danh_sach()

    # ------------------------------------------------------------------ #

    def _ve_danh_sach(self) -> None:
        for con in self._vung_danh_sach.winfo_children():
            con.destroy()

        so_ket_qua = 0
        for don_vi in self.ung_dung.giao_trinh.don_vi:
            if self._lop_dang_chon is not None and don_vi.lop != self._lop_dang_chon:
                continue
            khop = [tu for tu in don_vi.tat_ca_tu_vung if self._khop(tu)]
            if not khop:
                continue
            so_ket_qua += len(khop)
            self._ve_nhom(don_vi, khop)

        if so_ket_qua == 0:
            ctk.CTkLabel(
                self._vung_danh_sach,
                text="Không tìm thấy từ nào phù hợp 🤔",
                font=phong(16),
                text_color=Mau.CHU_MO,
            ).pack(pady=60)

    def _khop(self, tu: TuVung) -> bool:
        if not self._tu_khoa:
            return True
        return self._tu_khoa in chuan_hoa(tu.en) or self._tu_khoa in chuan_hoa(tu.vi)

    def _ve_nhom(self, don_vi: DonVi, cac_tu: list[TuVung]) -> None:
        bo_mau = MAU_THEO_DON_VI[don_vi.mau]

        tieu_de = ctk.CTkFrame(self._vung_danh_sach, fg_color="transparent")
        tieu_de.pack(fill="x", padx=KichThuoc.LE, pady=(20, 8))
        ctk.CTkLabel(
            tieu_de,
            text=f"{don_vi.bieu_tuong}  {don_vi.ten}",
            font=phong(17),
            text_color=bo_mau.chinh,
        ).pack(side="left")
        if don_vi.nhan_sgk:
            ctk.CTkLabel(
                tieu_de,
                text=f"   {don_vi.nhan_sgk}",
                font=phong(12),
                text_color=Mau.CHU_MO,
            ).pack(side="left")
        ctk.CTkLabel(
            tieu_de,
            text=f"{len(cac_tu)} từ",
            font=phong(13),
            text_color=Mau.CHU_MO,
        ).pack(side="right")

        for tu in cac_tu:
            self._ve_dong(tu)

    def _ve_dong(self, tu: TuVung) -> None:
        the = The(self._vung_danh_sach)
        the.pack(fill="x", padx=KichThuoc.LE, pady=4)

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(fill="x", padx=18, pady=12)

        ben_trai = ctk.CTkFrame(trong, fg_color="transparent")
        ben_trai.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            ben_trai,
            text=tu.en,
            font=phong(17),
            text_color=Mau.CHU,
            anchor="w",
        ).pack(fill="x")
        if tu.phien_am:
            ctk.CTkLabel(
                ben_trai,
                text=tu.phien_am,
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
                anchor="w",
            ).pack(fill="x")

        ctk.CTkLabel(
            trong,
            text=tu.vi,
            font=phong(16, dam=False),
            text_color=Mau.CHU_PHU,
        ).pack(side="right")

        if tu.co_vi_du:
            self._ve_vi_du(the, tu)

    def _ve_vi_du(self, the: The, tu: TuVung) -> None:
        """Câu ví dụ nằm dưới, tách bằng một đường kẻ nhạt."""
        ctk.CTkFrame(the, height=1, fg_color=Mau.VIEN, corner_radius=0).pack(
            fill="x", padx=18
        )

        khung = ctk.CTkFrame(the, fg_color="transparent")
        khung.pack(fill="x", padx=18, pady=(8, 12))

        ctk.CTkLabel(
            khung,
            text=tu.vi_du,
            font=phong(13, dam=False),
            text_color=Mau.CHU_PHU,
            anchor="w",
            justify="left",
        ).pack(fill="x")
        if tu.vi_du_dich:
            ctk.CTkLabel(
                khung,
                text=tu.vi_du_dich,
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
                anchor="w",
                justify="left",
            ).pack(fill="x")
