"""Trang chủ: lộ trình học uốn lượn với các chặng hình tròn."""

from __future__ import annotations

from typing import Final

import customtkinter as ctk

from ..mo_hinh import BaiHoc, DonVi
from .chu_de import MAU_THEO_DON_VI, KichThuoc, Mau, phong
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import HuyHieu, NutTron, ThanhTienDo, TrangThaiNut

__all__ = ["ManHinhChinh"]

_DO_LECH: Final[tuple[int, ...]] = (0, -70, -110, -70, 0, 70, 110, 70)
"""Độ lệch ngang của từng chặng, tạo hình con rắn quen thuộc."""

_CAO_HANG: Final[int] = 122
"""Chiều cao mỗi hàng chứa một chặng học."""


class ManHinhChinh(ManHinh):
    """Hiển thị toàn bộ đơn vị và các chặng học kèm trạng thái mở khoá."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        self._thu_tu_toan_cuc = 0
        self._ma_bai_hien_tai: str | None = None
        super().__init__(master, ung_dung)

    def dung_giao_dien(self) -> None:
        self._ma_bai_hien_tai = self._tim_bai_dang_hoc()
        self._dung_thanh_chi_so()
        self._dung_lo_trinh()

    def _tim_bai_dang_hoc(self) -> str | None:
        """Bài đầu tiên chưa hoàn thành - nơi gắn nhãn BẮT ĐẦU."""
        tien_do = self.ung_dung.tien_do
        return next(
            (
                bai.ma
                for bai in self.ung_dung.giao_trinh.tat_ca_bai_hoc
                if not tien_do.da_hoan_thanh(bai.ma)
            ),
            None,
        )

    # ------------------------------------------------------------------ #
    # Thanh chỉ số phía trên
    # ------------------------------------------------------------------ #

    def _dung_thanh_chi_so(self) -> None:
        tien_do = self.ung_dung.tien_do

        thanh = ctk.CTkFrame(self, fg_color=Mau.NEN, corner_radius=0, height=76)
        thanh.pack(fill="x", side="top")
        thanh.pack_propagate(False)

        trong = ctk.CTkFrame(thanh, fg_color="transparent")
        trong.pack(fill="both", expand=True, padx=KichThuoc.LE, pady=(18, 10))

        HuyHieu(
            trong,
            bieu_tuong="🔥",
            gia_tri=str(tien_do.chuoi_ngay_thuc_te()),
            mau_chu=Mau.CAM,
            co_chu=17,
        ).pack(side="left", padx=(0, 18))
        HuyHieu(
            trong,
            bieu_tuong="⚡",
            gia_tri=str(tien_do.xp),
            mau_chu=Mau.VANG_DAM,
            co_chu=17,
        ).pack(side="left", padx=(0, 18))
        HuyHieu(
            trong,
            bieu_tuong="👑",
            gia_tri=f"Cấp {tien_do.cap_do}",
            mau_chu=Mau.TIM_DAM,
            co_chu=17,
        ).pack(side="left")

        khung_thanh = ctk.CTkFrame(trong, fg_color="transparent", width=200)
        khung_thanh.pack(side="right", fill="y")
        khung_thanh.pack_propagate(False)
        ctk.CTkLabel(
            khung_thanh,
            text=f"{tien_do.xp_trong_cap}/100 XP",
            font=phong(12),
            text_color=Mau.CHU_MO,
        ).pack(anchor="e")
        thanh_cap = ThanhTienDo(khung_thanh, mau=Mau.VANG, chieu_cao=10)
        thanh_cap.pack(fill="x", pady=(4, 0))
        thanh_cap.dat_gia_tri(tien_do.ty_le_len_cap, muot=False)

        ctk.CTkFrame(self, height=2, fg_color=Mau.VIEN, corner_radius=0).pack(fill="x")

    # ------------------------------------------------------------------ #
    # Lộ trình
    # ------------------------------------------------------------------ #

    def _dung_lo_trinh(self) -> None:
        vung_cuon = ctk.CTkScrollableFrame(
            self, fg_color=Mau.NEN, corner_radius=0, scrollbar_button_color=Mau.VIEN
        )
        vung_cuon.pack(fill="both", expand=True)

        giao_trinh = self.ung_dung.giao_trinh
        for don_vi in giao_trinh.don_vi:
            self._dung_bang_don_vi(vung_cuon, don_vi)
            for bai_hoc in don_vi.bai_hoc:
                self._dung_chang(vung_cuon, don_vi, bai_hoc)

        ctk.CTkLabel(
            vung_cuon,
            text="🏁  Hết lộ trình - hẹn gặp lại ở bài mới!",
            font=phong(14),
            text_color=Mau.CHU_MO,
        ).pack(pady=(24, 32))

    def _dung_bang_don_vi(self, cha: ctk.CTkBaseClass, don_vi: DonVi) -> None:
        """Bảng tiêu đề màu đặc trưng mở đầu mỗi đơn vị."""
        bo_mau = MAU_THEO_DON_VI[don_vi.mau]

        boc = ctk.CTkFrame(cha, fg_color="transparent")
        boc.pack(fill="x", padx=KichThuoc.LE * 2, pady=(24, 8))

        bong = ctk.CTkFrame(boc, fg_color=bo_mau.dam, corner_radius=KichThuoc.BO_GOC)
        bong.pack(fill="x", pady=(KichThuoc.DO_SAU_NUT, 0))

        bang = ctk.CTkFrame(bong, fg_color=bo_mau.chinh, corner_radius=KichThuoc.BO_GOC)
        bang.pack(fill="x", pady=(0, KichThuoc.DO_SAU_NUT))

        noi_dung = ctk.CTkFrame(bang, fg_color="transparent")
        noi_dung.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(
            noi_dung,
            text=don_vi.bieu_tuong,
            font=phong(26),
            text_color=Mau.CHU_TREN_NEN_DAM,
        ).pack(side="left", padx=(0, 14))

        chu = ctk.CTkFrame(noi_dung, fg_color="transparent")
        chu.pack(side="left", fill="x", expand=True)
        hang_ten = ctk.CTkFrame(chu, fg_color="transparent")
        hang_ten.pack(fill="x")
        ctk.CTkLabel(
            hang_ten,
            text=don_vi.ten,
            font=phong(19),
            text_color=Mau.CHU_TREN_NEN_DAM,
        ).pack(side="left")
        if don_vi.nhan_sgk:
            ctk.CTkLabel(
                hang_ten,
                text=f"   {don_vi.nhan_sgk}",
                font=phong(12),
                text_color=Mau.CHU_TREN_NEN_DAM,
            ).pack(side="left")
        ctk.CTkLabel(
            chu,
            text=don_vi.mo_ta,
            font=phong(13, dam=False),
            text_color=Mau.CHU_TREN_NEN_DAM,
            anchor="w",
        ).pack(fill="x")

        so_xong = sum(
            1 for bai in don_vi.bai_hoc if self.ung_dung.tien_do.da_hoan_thanh(bai.ma)
        )
        ctk.CTkLabel(
            noi_dung,
            text=f"{so_xong}/{len(don_vi.bai_hoc)}",
            font=phong(16),
            text_color=Mau.CHU_TREN_NEN_DAM,
        ).pack(side="right")

    def _dung_chang(
        self, cha: ctk.CTkBaseClass, don_vi: DonVi, bai_hoc: BaiHoc
    ) -> None:
        """Vẽ một chặng học, lệch trái phải theo thứ tự để tạo đường uốn lượn."""
        trang_thai = self._trang_thai_chang(bai_hoc)
        do_lech = _DO_LECH[self._thu_tu_toan_cuc % len(_DO_LECH)]
        self._thu_tu_toan_cuc += 1

        hang = ctk.CTkFrame(cha, fg_color="transparent", height=_CAO_HANG)
        hang.pack(fill="x")
        hang.pack_propagate(False)

        if trang_thai is TrangThaiNut.MO and bai_hoc.ma == self._ma_bai_hien_tai:
            nhan = ctk.CTkLabel(
                hang,
                text="BẮT ĐẦU",
                font=phong(11),
                text_color=MAU_THEO_DON_VI[don_vi.mau].chinh,
            )
            nhan.place(relx=0.5, x=do_lech, y=2, anchor="n")

        bieu_tuong = {
            TrangThaiNut.HOAN_THANH: "⭐",
            TrangThaiNut.MO: don_vi.bieu_tuong,
            TrangThaiNut.KHOA: "🔒",
        }[trang_thai]

        nut = NutTron(
            hang,
            bo_mau=MAU_THEO_DON_VI[don_vi.mau],
            trang_thai=trang_thai,
            bieu_tuong=bieu_tuong,
            command=lambda: self.ung_dung.mo_bai_hoc(bai_hoc),
        )
        nut.place(relx=0.5, x=do_lech, y=26, anchor="n")

    # ------------------------------------------------------------------ #
    # Quy tắc mở khoá
    # ------------------------------------------------------------------ #

    def _trang_thai_chang(self, bai_hoc: BaiHoc) -> TrangThaiNut:
        """Chặng mở khi là chặng đầu tiên hoặc chặng liền trước đã xong."""
        tien_do = self.ung_dung.tien_do
        if tien_do.da_hoan_thanh(bai_hoc.ma):
            return TrangThaiNut.HOAN_THANH

        danh_sach = self.ung_dung.giao_trinh.tat_ca_bai_hoc
        chi_so = self.ung_dung.giao_trinh.thu_tu_bai_hoc(bai_hoc.ma)
        if chi_so <= 0:
            return TrangThaiNut.MO
        truoc_do = danh_sach[chi_so - 1]
        return (
            TrangThaiNut.MO
            if tien_do.da_hoan_thanh(truoc_do.ma)
            else TrangThaiNut.KHOA
        )
