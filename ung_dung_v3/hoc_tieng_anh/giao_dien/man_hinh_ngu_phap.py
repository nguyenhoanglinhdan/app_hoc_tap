"""Màn hình ngữ pháp: chọn chủ điểm theo lớp rồi vào luyện."""

from __future__ import annotations

import customtkinter as ctk

from ..ngu_phap import ChuDiemNguPhap
from .chu_de import MAU_THEO_DON_VI, KichThuoc, Mau, phong
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import NutDuo, The

__all__ = ["ManHinhNguPhap"]

_TAT_CA = "Tất cả"


class ManHinhNguPhap(ManHinh):
    """Liệt kê các chủ điểm ngữ pháp, lọc được theo lớp."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        self._lop_dang_chon: int | None = None
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
        thanh.pack(fill="x", padx=KichThuoc.LE * 2, pady=(26, 12))

        ctk.CTkLabel(
            thanh, text="Ngữ pháp", font=phong(26), text_color=Mau.CHU, anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            thanh,
            text="Luyện các chủ điểm hay gặp trong bài kiểm tra ở lớp",
            font=phong(14, dam=False),
            text_color=Mau.CHU_MO,
            anchor="w",
        ).pack(fill="x", pady=(2, 14))

        cac_lop = self.ung_dung.ngu_phap.cac_lop
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
            bo_loc.pack(anchor="w")
            bo_loc.set(_TAT_CA)

        ctk.CTkFrame(self, height=2, fg_color=Mau.VIEN, corner_radius=0).pack(fill="x")

    def _doi_lop(self, lua_chon: str) -> None:
        self._lop_dang_chon = (
            None if lua_chon == _TAT_CA else int(lua_chon.removeprefix("Lớp "))
        )
        self._ve_danh_sach()

    # ------------------------------------------------------------------ #

    def _ve_danh_sach(self) -> None:
        for con in self._vung.winfo_children():
            con.destroy()

        cac_chu_diem = self.ung_dung.ngu_phap.theo_lop(self._lop_dang_chon)
        if not cac_chu_diem:
            self._hien_trong(bool(self.ung_dung.ngu_phap))
            return

        for chu_diem in cac_chu_diem:
            self._ve_chu_diem(chu_diem)

        ctk.CTkLabel(
            self._vung,
            text="Làm xong hết rồi thì quay lại ôn cho nhớ lâu nhé!",
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(pady=(18, 28))

    def _hien_trong(self, co_noi_dung: bool) -> None:
        the = The(self._vung)
        the.pack(fill="x", padx=KichThuoc.LE * 2, pady=20)

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(pady=36)

        ctk.CTkLabel(trong, text="📐", font=phong(52)).pack()
        ctk.CTkLabel(
            trong,
            text=(
                "Lớp này chưa có chủ điểm nào"
                if co_noi_dung
                else "Chưa có nội dung ngữ pháp"
            ),
            font=phong(19),
            text_color=Mau.CHU,
        ).pack(pady=(10, 4))
        ctk.CTkLabel(
            trong,
            text=(
                "Chọn lớp khác ở phía trên nhé!"
                if co_noi_dung
                else "Thêm tệp du_lieu/ngu_phap.json để bật phần này."
            ),
            font=phong(14, dam=False),
            text_color=Mau.CHU_MO,
        ).pack()

    def _ve_chu_diem(self, chu_diem: ChuDiemNguPhap) -> None:
        bo_mau = MAU_THEO_DON_VI[chu_diem.mau]
        so_lan = self.ung_dung.tien_do.so_lan_hoan_thanh.get(chu_diem.ma, 0)

        the = The(self._vung)
        the.pack(fill="x", padx=KichThuoc.LE * 2, pady=6)

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            trong, text=chu_diem.bieu_tuong, font=phong(30), text_color=bo_mau.chinh
        ).pack(side="left", padx=(0, 16))

        chu = ctk.CTkFrame(trong, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)

        hang_ten = ctk.CTkFrame(chu, fg_color="transparent")
        hang_ten.pack(fill="x")
        ctk.CTkLabel(
            hang_ten, text=chu_diem.ten, font=phong(18), text_color=Mau.CHU
        ).pack(side="left")
        if so_lan:
            ctk.CTkLabel(
                hang_ten,
                text=f"  ⭐ đã xong {so_lan} lần",
                font=phong(12),
                text_color=Mau.XANH_LA_DAM,
            ).pack(side="left")

        ctk.CTkLabel(
            chu,
            text=f"Lớp {chu_diem.lop} · {len(chu_diem)} câu · {chu_diem.mo_ta}",
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        NutDuo(
            trong,
            text="ÔN LẠI" if so_lan else "HỌC",
            command=lambda: self.ung_dung.mo_chu_diem_ngu_phap(chu_diem),
            chieu_rong=150,
            chieu_cao=44,
            co_chu=14,
        ).pack(side="right")
