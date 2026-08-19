"""Màn hình hồ sơ: thống kê học tập và tuỳ chọn của ứng dụng."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ..tien_do import TienDo
from .chu_de import CapMau, KichThuoc, Mau, phong
from .man_hinh_goc import ManHinh
from .thanh_phan import KieuNut, NutDuo, The

__all__ = ["ManHinhHoSo"]


class ManHinhHoSo(ManHinh):
    """Tổng hợp thành tích và cho phép đặt lại tiến độ."""

    def dung_giao_dien(self) -> None:
        vung = ctk.CTkScrollableFrame(
            self, fg_color=Mau.NEN, corner_radius=0, scrollbar_button_color=Mau.VIEN
        )
        vung.pack(fill="both", expand=True)

        self._dung_dau_trang(vung)
        self._dung_thong_ke(vung)
        self._dung_lich_su_kiem_tra(vung)
        self._dung_tuy_chon(vung)

    def _dung_dau_trang(self, cha: ctk.CTkBaseClass) -> None:
        tien_do = self.ung_dung.tien_do

        khung = ctk.CTkFrame(cha, fg_color="transparent")
        khung.pack(fill="x", padx=KichThuoc.LE * 2, pady=(32, 8))

        ctk.CTkLabel(khung, text="🦉", font=phong(64)).pack()
        ctk.CTkLabel(
            khung,
            text=f"Cấp {tien_do.cap_do}",
            font=phong(28),
            text_color=Mau.CHU,
        ).pack(pady=(8, 2))
        ctk.CTkLabel(
            khung,
            text=f"Còn {100 - tien_do.xp_trong_cap} XP nữa là lên cấp mới",
            font=phong(14, dam=False),
            text_color=Mau.CHU_MO,
        ).pack()

    def _dung_thong_ke(self, cha: ctk.CTkBaseClass) -> None:
        tien_do = self.ung_dung.tien_do
        tong_bai = len(self.ung_dung.giao_trinh.tat_ca_bai_hoc)
        tong_tu = len(self.ung_dung.giao_trinh.tat_ca_tu_vung)
        so_tu_da_hoc = self._dem_tu_da_hoc(tien_do)

        ctk.CTkLabel(
            cha,
            text="Thống kê",
            font=phong(20),
            text_color=Mau.CHU,
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 10))

        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x", padx=KichThuoc.LE * 2)
        luoi.grid_columnconfigure((0, 1), weight=1, uniform="thong_ke")

        cac_o = (
            ("🔥", str(tien_do.chuoi_ngay_thuc_te()), "Ngày liên tiếp", Mau.CAM),
            ("⚡", str(tien_do.xp), "Tổng XP", Mau.VANG_DAM),
            ("📘", f"{tien_do.so_bai_da_xong}/{tong_bai}", "Bài đã xong", Mau.XANH_DUONG),
            ("🔤", f"{so_tu_da_hoc}/{tong_tu}", "Từ đã học", Mau.XANH_LA_DAM),
        )
        for thu_tu, (bieu_tuong, gia_tri, nhan, mau) in enumerate(cac_o):
            self._o_thong_ke(luoi, bieu_tuong, gia_tri, nhan, mau).grid(
                row=thu_tu // 2, column=thu_tu % 2, sticky="ew", padx=6, pady=6
            )

    def _o_thong_ke(
        self,
        cha: ctk.CTkBaseClass,
        bieu_tuong: str,
        gia_tri: str,
        nhan: str,
        mau: CapMau,
    ) -> The:
        the = The(cha)
        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(trong, text=bieu_tuong, font=phong(26)).pack(side="left", padx=(0, 14))

        chu = ctk.CTkFrame(trong, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(chu, text=gia_tri, font=phong(22), text_color=mau, anchor="w").pack(fill="x")
        ctk.CTkLabel(
            chu, text=nhan, font=phong(13, dam=False), text_color=Mau.CHU_MO, anchor="w"
        ).pack(fill="x")
        return the

    def _dem_tu_da_hoc(self, tien_do: TienDo) -> int:
        """Số từ nằm trong những bài học đã hoàn thành."""
        return sum(
            len(bai)
            for bai in self.ung_dung.giao_trinh.tat_ca_bai_hoc
            if tien_do.da_hoan_thanh(bai.ma)
        )

    def _dung_lich_su_kiem_tra(self, cha: ctk.CTkBaseClass) -> None:
        """Bảng điểm các bài kiểm tra gần đây."""
        lich_su = self.ung_dung.tien_do.lich_su_kiem_tra
        if not lich_su:
            return

        ctk.CTkLabel(
            cha, text="Bảng điểm kiểm tra", font=phong(20), text_color=Mau.CHU
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 10))

        for ket_qua in lich_su[:5]:
            the = The(cha)
            the.pack(fill="x", padx=KichThuoc.LE * 2 + 6, pady=4)

            trong = ctk.CTkFrame(the, fg_color="transparent")
            trong.pack(fill="x", padx=18, pady=12)

            ctk.CTkLabel(
                trong,
                text=f"{ket_qua.diem}",
                font=phong(22),
                text_color=self._mau_theo_diem(ket_qua.diem),
                width=54,
            ).pack(side="left")

            chu = ctk.CTkFrame(trong, fg_color="transparent")
            chu.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(
                chu,
                text=ket_qua.xep_loai,
                font=phong(15),
                text_color=Mau.CHU,
                anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                chu,
                text=f"Đúng {ket_qua.so_dung}/{ket_qua.so_cau} câu",
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
                anchor="w",
            ).pack(fill="x")

            ctk.CTkLabel(
                trong,
                text=ket_qua.ngay.strftime("%d/%m/%Y"),
                font=phong(12, dam=False),
                text_color=Mau.CHU_MO,
            ).pack(side="right")

    @staticmethod
    def _mau_theo_diem(diem: float) -> CapMau:
        if diem >= 8:
            return Mau.XANH_LA_DAM
        if diem >= 6.5:
            return Mau.XANH_DUONG
        if diem >= 5:
            return Mau.CAM
        return Mau.DO

    def _dung_tuy_chon(self, cha: ctk.CTkBaseClass) -> None:
        ctk.CTkLabel(
            cha,
            text="Tuỳ chọn",
            font=phong(20),
            text_color=Mau.CHU,
        ).pack(anchor="w", padx=KichThuoc.LE * 2, pady=(28, 10))

        khung = The(cha)
        khung.pack(fill="x", padx=KichThuoc.LE * 2 + 6)

        trong = ctk.CTkFrame(khung, fg_color="transparent")
        trong.pack(fill="x", padx=18, pady=16)

        hang_giao_dien = ctk.CTkFrame(trong, fg_color="transparent")
        hang_giao_dien.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            hang_giao_dien,
            text="Giao diện",
            font=phong(15),
            text_color=Mau.CHU,
        ).pack(side="left")
        chon_giao_dien = ctk.CTkSegmentedButton(
            hang_giao_dien,
            values=["Sáng", "Tối", "Theo hệ thống"],
            command=self._doi_giao_dien,
            font=phong(13),
            corner_radius=KichThuoc.BO_GOC_NHO,
            selected_color=Mau.XANH_LA,
            selected_hover_color=Mau.XANH_LA_DAM,
            unselected_color=Mau.NEN_PHU,
            text_color=Mau.CHU,
        )
        chon_giao_dien.pack(side="right")
        chon_giao_dien.set(
            "Tối" if ctk.get_appearance_mode() == "Dark" else "Sáng"
        )

        NutDuo(
            trong,
            text="ĐẶT LẠI TIẾN ĐỘ",
            command=self._dat_lai_tien_do,
            kieu=KieuNut.NGUY_HIEM,
            chieu_rong=230,
            chieu_cao=44,
            co_chu=14,
        ).pack(anchor="w")

    @staticmethod
    def _doi_giao_dien(lua_chon: str) -> None:
        che_do = {"Sáng": "light", "Tối": "dark", "Theo hệ thống": "system"}
        ctk.set_appearance_mode(che_do.get(lua_chon, "system"))

    def _dat_lai_tien_do(self) -> None:
        """Xoá sạch tiến độ sau khi người dùng xác nhận."""
        dong_y = messagebox.askyesno(
            title="Đặt lại tiến độ",
            message=(
                "Toàn bộ XP, chuỗi ngày và các bài đã hoàn thành sẽ bị xoá.\n"
                "Bạn có chắc chắn không?"
            ),
            icon="warning",
            default="no",
            parent=self,
        )
        if not dong_y:
            return

        self.ung_dung.tien_do.dat_lai()
        self.ung_dung.luu_tien_do()
        self.ung_dung.mo_ho_so()
