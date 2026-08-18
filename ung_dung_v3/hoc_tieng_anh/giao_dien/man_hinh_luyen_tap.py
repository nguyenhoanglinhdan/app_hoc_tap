"""Màn hình luyện tập tổng hợp: ôn lại từ đã học ở mọi đơn vị."""

from __future__ import annotations

from typing import Callable, Final, Sequence

import customtkinter as ctk

from ..mo_hinh import TuVung
from ..on_tap import LichOnTap, MucThuoc
from .chu_de import CapMau, KichThuoc, Mau, phong
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import NutDuo, The

__all__ = ["ManHinhLuyenTap"]

SO_TU_MOI_BUOI: Final[int] = 8
"""Số từ đưa vào một buổi luyện tập."""

_MAU_THEO_MUC: Final[dict[MucThuoc, CapMau]] = {
    MucThuoc.MOI: Mau.CHU_MO,
    MucThuoc.DANG_HOC: Mau.CAM,
    MucThuoc.QUEN_THUOC: Mau.XANH_DUONG,
    MucThuoc.THUOC_LONG: Mau.XANH_LA,
}


class ManHinhLuyenTap(ManHinh):
    """Gợi ý các buổi luyện dựa trên lịch ôn tập của từng từ."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        self._lich = LichOnTap(ung_dung.giao_trinh, ung_dung.tien_do.trang_thai_tu)
        super().__init__(master, ung_dung)

    def dung_giao_dien(self) -> None:
        vung = ctk.CTkScrollableFrame(
            self, fg_color=Mau.NEN, corner_radius=0, scrollbar_button_color=Mau.VIEN
        )
        vung.pack(fill="both", expand=True)

        ctk.CTkLabel(
            vung,
            text="Luyện tập",
            font=phong(26),
            text_color=Mau.CHU,
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 4))
        ctk.CTkLabel(
            vung,
            text="Ôn lại những từ đã gặp, trộn từ mọi chủ đề",
            font=phong(14, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(0, 18))

        if not self._lich.tu_da_gap:
            self._hien_chua_co_gi(vung)
            return

        self._dung_the_buoi_luyen(vung)
        self._dung_bang_muc_thuoc(vung)
        self._dung_danh_sach_yeu(vung)

    # ------------------------------------------------------------------ #

    def _hien_chua_co_gi(self, cha: ctk.CTkBaseClass) -> None:
        """Chưa học bài nào thì chưa có gì để ôn."""
        the = The(cha)
        the.pack(fill="x", padx=KichThuoc.LE * 2, pady=20)

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(pady=36)

        ctk.CTkLabel(trong, text="🌱", font=phong(52)).pack()
        ctk.CTkLabel(
            trong,
            text="Chưa có từ nào để ôn",
            font=phong(19),
            text_color=Mau.CHU,
        ).pack(pady=(10, 4))
        ctk.CTkLabel(
            trong,
            text="Học vài bài ở trang chủ trước đã, rồi quay lại đây nhé!",
            font=phong(14, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(pady=(0, 18))
        NutDuo(
            trong,
            text="VỀ TRANG CHỦ",
            command=self.ung_dung.mo_trang_chu,
            chieu_rong=220,
        ).pack()

    def _dung_the_buoi_luyen(self, cha: ctk.CTkBaseClass) -> None:
        """Ba lựa chọn luyện tập, mỗi lựa chọn là một thẻ có nút riêng."""
        den_han = self._lich.den_han()
        hay_sai = self._lich.hay_sai(SO_TU_MOI_BUOI)
        tat_ca = self._lich.tu_da_gap

        self._the_lua_chon(
            cha,
            bieu_tuong="⏰",
            tieu_de="Ôn từ tới hạn",
            mo_ta=(
                f"{len(den_han)} từ đang chờ ôn lại hôm nay"
                if den_han
                else "Chưa có từ nào tới hạn - quay lại sau nhé!"
            ),
            mau=Mau.CAM,
            nhan_nut="ÔN NGAY",
            bat=bool(den_han),
            khi_bam=lambda: self._bat_dau(
                self._lich.chon_cho_buoi_luyen(SO_TU_MOI_BUOI)
            ),
        )

        self._the_lua_chon(
            cha,
            bieu_tuong="🎯",
            tieu_de="Luyện từ hay sai",
            mo_ta=(
                f"{len(hay_sai)} từ bạn từng trả lời sai"
                if hay_sai
                else "Chưa sai từ nào cả, giỏi lắm!"
            ),
            mau=Mau.DO,
            nhan_nut="LUYỆN NGAY",
            bat=bool(hay_sai),
            khi_bam=lambda: self._bat_dau(hay_sai),
        )

        self._the_lua_chon(
            cha,
            bieu_tuong="🔀",
            tieu_de="Trộn ngẫu nhiên",
            mo_ta=f"Bốc {min(SO_TU_MOI_BUOI, len(tat_ca))} từ bất kỳ trong {len(tat_ca)} từ đã gặp",
            mau=Mau.TIM,
            nhan_nut="BẮT ĐẦU",
            bat=bool(tat_ca),
            khi_bam=lambda: self._bat_dau(self._tron_ngau_nhien()),
        )

    def _the_lua_chon(
        self,
        cha: ctk.CTkBaseClass,
        *,
        bieu_tuong: str,
        tieu_de: str,
        mo_ta: str,
        mau: CapMau,
        nhan_nut: str,
        bat: bool,
        khi_bam: Callable[[], None],
    ) -> None:
        the = The(cha)
        the.pack(fill="x", padx=KichThuoc.LE * 2, pady=6)

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(trong, text=bieu_tuong, font=phong(30), text_color=mau).pack(
            side="left", padx=(0, 16)
        )

        chu = ctk.CTkFrame(trong, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            chu, text=tieu_de, font=phong(18), text_color=Mau.CHU, anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            chu,
            text=mo_ta,
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        NutDuo(
            trong,
            text=nhan_nut,
            command=khi_bam,
            chieu_rong=170,
            chieu_cao=44,
            co_chu=14,
            bat=bat,
        ).pack(side="right")

    # ------------------------------------------------------------------ #

    def _dung_bang_muc_thuoc(self, cha: ctk.CTkBaseClass) -> None:
        """Đếm số từ ở từng mức thuộc."""
        ctk.CTkLabel(
            cha, text="Mức độ thuộc", font=phong(20), text_color=Mau.CHU
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 10))

        dem = self._lich.dem_theo_muc()
        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x", padx=KichThuoc.LE * 2)
        luoi.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="muc")

        for cot, muc in enumerate(MucThuoc):
            the = The(luoi)
            the.grid(row=0, column=cot, sticky="ew", padx=4)

            trong = ctk.CTkFrame(the, fg_color="transparent")
            trong.pack(pady=14)
            ctk.CTkLabel(
                trong,
                text=str(dem[muc]),
                font=phong(24),
                text_color=_MAU_THEO_MUC[muc],
            ).pack()
            ctk.CTkLabel(
                trong,
                text=muc.nhan,
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
            ).pack()

    def _dung_danh_sach_yeu(self, cha: ctk.CTkBaseClass) -> None:
        """Liệt kê vài từ cần chú ý nhất kèm tỷ lệ đúng."""
        yeu = self._lich.yeu_nhat(6)
        if not yeu:
            return

        ctk.CTkLabel(
            cha, text="Cần chú ý nhất", font=phong(20), text_color=Mau.CHU
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 10))

        trang_thai = self.ung_dung.tien_do.trang_thai_tu
        for tu in yeu:
            thong_tin = trang_thai[tu.ma]
            the = The(cha)
            the.pack(fill="x", padx=KichThuoc.LE * 2, pady=4)

            trong = ctk.CTkFrame(the, fg_color="transparent")
            trong.pack(fill="x", padx=18, pady=11)

            ctk.CTkLabel(
                trong, text=tu.en, font=phong(16), text_color=Mau.CHU, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                trong,
                text=tu.vi,
                font=phong(14, dam=False),
                text_color=Mau.CHU_PHU,
            ).pack(side="left", padx=(12, 0))

            ctk.CTkLabel(
                trong,
                text=thong_tin.muc_thuoc.nhan,
                font=phong(12),
                text_color=_MAU_THEO_MUC[thong_tin.muc_thuoc],
            ).pack(side="right")
            ctk.CTkLabel(
                trong,
                text=f"{thong_tin.tong_dung}/{thong_tin.tong_lan} đúng",
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
            ).pack(side="right", padx=(0, 14))

    # ------------------------------------------------------------------ #

    def _tron_ngau_nhien(self) -> tuple[TuVung, ...]:
        from random import sample

        tat_ca = self._lich.tu_da_gap
        so_luong = min(SO_TU_MOI_BUOI, len(tat_ca))
        return tuple(sample(list(tat_ca), so_luong))

    def _bat_dau(self, cac_tu: Sequence[TuVung]) -> None:
        if cac_tu:
            self.ung_dung.mo_buoi_luyen(cac_tu)
