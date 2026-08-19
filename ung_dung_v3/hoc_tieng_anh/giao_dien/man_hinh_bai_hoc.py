"""Màn hình làm bài: hiển thị câu hỏi, chấm điểm và tổng kết phiên học."""

from __future__ import annotations

import time
from random import Random
from typing import Callable, Final

import customtkinter as ctk

from ..am_thanh import GIAY_THU_AM, KetQuaPhatAm
from ..bai_tap import (
    DAP_AN_GHEP_DUNG,
    DAP_AN_NOI_DUNG,
    CauHoi,
    CheDoPhien,
    LoaiBaiTap,
    NoiDungPhien,
    PhienHoc,
    TrangThaiPhien,
)
from ..mo_hinh import TuVung
from ..tien_do import KetQuaKiemTra
from .chu_de import KichThuoc, Mau, phong
from .man_hinh_goc import DieuHuong, ManHinh
from .thanh_phan import (
    DayTim,
    KieuNut,
    NutDuo,
    NutLoa,
    ThanhTienDo,
    The,
    TheLuaChon,
    TrangThaiThe,
)

__all__ = ["ManHinhBaiHoc"]

_CHO_GHEP_SAI: Final[int] = 420
"""Thời gian giữ màu đỏ khi ghép sai, tính bằng mili giây."""

_CHO_GHEP_XONG: Final[int] = 320
"""Khoảng nghỉ trước khi chuyển tiếp sau khi ghép xong toàn bộ cặp."""


class ManHinhBaiHoc(ManHinh):
    """Điều khiển một lượt học từ câu hỏi đầu tiên tới màn hình tổng kết."""

    an_thanh_ben = True

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        ung_dung: DieuHuong,
        noi_dung: NoiDungPhien,
    ) -> None:
        self._noi_dung = noi_dung
        self._am_thanh = ung_dung.am_thanh
        self._phien = PhienHoc(
            noi_dung.cau_hoi,
            so_tim=None if noi_dung.la_kiem_tra else PhienHoc.SO_TIM_TOI_DA,
            hoi_lai_cau_sai=not noi_dung.la_kiem_tra,
        )
        self._luc_bat_dau = time.monotonic()

        self._dap_an_chon: str | None = None
        self._the_theo_gia_tri: dict[str, TheLuaChon] = {}
        self._o_nhap: ctk.CTkEntry | None = None
        self._da_kiem_tra = False
        self._da_tong_ket = False
        self._ket_qua_kiem_tra: KetQuaKiemTra | None = None
        self._cho_ghep: TheLuaChon | None = None
        self._vi_tri_da_chon: list[int] = []
        self._nut_manh: dict[int, NutDuo] = {}
        self._kho_manh: ctk.CTkFrame | None = None
        self._o_ghep_cau: ctk.CTkLabel | None = None
        self._nut_mic: NutDuo | None = None
        self._nhan_mic: ctk.CTkLabel | None = None
        self._tu_dang_cho: TuVung | None = None
        self._ben_dang_cho = False
        self._con_lai_ghep = 0

        super().__init__(master, ung_dung)

    # ------------------------------------------------------------------ #
    # Dựng khung
    # ------------------------------------------------------------------ #

    def dung_giao_dien(self) -> None:
        self._dung_thanh_tren()
        self._vung_cau_hoi = ctk.CTkFrame(self, fg_color=Mau.NEN)
        self._vung_cau_hoi.pack(fill="both", expand=True)
        self._dung_thanh_duoi()
        self._gan_phim_tat()
        self._hien_cau_hoi()

    def _dung_thanh_tren(self) -> None:
        thanh = ctk.CTkFrame(self, fg_color=Mau.NEN, height=70, corner_radius=0)
        thanh.pack(fill="x")
        thanh.pack_propagate(False)

        trong = ctk.CTkFrame(thanh, fg_color="transparent")
        trong.pack(fill="both", expand=True, padx=KichThuoc.LE, pady=20)

        ctk.CTkButton(
            trong,
            text="✕",
            width=34,
            height=34,
            corner_radius=17,
            fg_color="transparent",
            hover_color=Mau.NEN_PHU,
            text_color=Mau.CHU_MO,
            font=phong(20),
            command=self._thoat,
        ).pack(side="left", padx=(0, 14))

        self._thanh_tien_do = ThanhTienDo(trong, mau=Mau.XANH_LA)
        self._thanh_tien_do.pack(side="left", fill="x", expand=True)

        if self._noi_dung.la_kiem_tra:
            self._day_tim = None
            self._nhan_so_cau = ctk.CTkLabel(
                trong, text="", font=phong(14), text_color=Mau.CHU_PHU
            )
            self._nhan_so_cau.pack(side="left", padx=(14, 0))
            self._cap_nhat_so_cau()
        else:
            self._nhan_so_cau = None
            self._day_tim = DayTim(trong, toi_da=PhienHoc.SO_TIM_TOI_DA)
            self._day_tim.pack(side="left", padx=(14, 0))
            self._day_tim.dat_so_tim(self._phien.con_tim)

    def _dung_thanh_duoi(self) -> None:
        self._thanh_duoi = ctk.CTkFrame(
            self, fg_color=Mau.NEN_PHU, height=112, corner_radius=0
        )
        self._thanh_duoi.pack(fill="x", side="bottom")
        self._thanh_duoi.pack_propagate(False)

        trong = ctk.CTkFrame(self._thanh_duoi, fg_color="transparent")
        trong.pack(fill="both", expand=True, padx=KichThuoc.LE * 2, pady=18)

        self._nhan_phan_hoi = ctk.CTkLabel(
            trong,
            text="",
            font=phong(17),
            text_color=Mau.CHU_PHU,
            justify="left",
            anchor="w",
        )
        self._nhan_phan_hoi.pack(side="left", fill="x", expand=True)

        self._nut_chinh = NutDuo(
            trong,
            text="KIỂM TRA",
            command=self._khi_bam_nut_chinh,
            chieu_rong=200,
            bat=False,
        )
        self._nut_chinh.pack(side="right")

    def _gan_phim_tat(self) -> None:
        """Enter để kiểm tra, phím số để chọn nhanh phương án."""
        cua_so = self.winfo_toplevel()
        cua_so.bind("<Return>", self._phim_enter)
        for so in range(1, 5):
            cua_so.bind(str(so), self._tao_phim_so(so))

    def destroy(self) -> None:
        """Gỡ phím tắt khỏi cửa sổ trước khi màn hình biến mất."""
        cua_so = self.winfo_toplevel()
        if cua_so.winfo_exists():
            cua_so.unbind("<Return>")
            for so in range(1, 5):
                cua_so.unbind(str(so))
        super().destroy()

    # ------------------------------------------------------------------ #
    # Hiển thị câu hỏi
    # ------------------------------------------------------------------ #

    def _hien_cau_hoi(self) -> None:
        """Vẽ lại vùng giữa theo câu hỏi hiện tại, hoặc chuyển sang tổng kết."""
        if self._phien.trang_thai is not TrangThaiPhien.DANG_HOC:
            self._hien_tong_ket()
            return

        cau_hoi = self._phien.cau_hoi_hien_tai
        assert cau_hoi is not None  # trạng thái DANG_HOC luôn còn câu hỏi

        self._dap_an_chon = None
        self._the_theo_gia_tri.clear()
        self._o_nhap = None
        self._da_kiem_tra = False
        self._cho_ghep = None
        self._tu_dang_cho = None
        self._nut_mic = None
        self._nhan_mic = None
        self._vi_tri_da_chon = []
        self._nut_manh = {}
        self._kho_manh = None
        self._o_ghep_cau = None

        for con in self._vung_cau_hoi.winfo_children():
            con.destroy()

        self._thanh_tien_do.dat_gia_tri(self._phien.ty_le_hoan_thanh)
        self._dat_phan_hoi(None)
        self._nut_chinh.dat_chu("KIỂM TRA")
        self._nut_chinh.dat_bat(False)

        cot = ctk.CTkFrame(self._vung_cau_hoi, fg_color="transparent")
        cot.pack(expand=True)

        # Thanh chen vo hinh, giu cot luon rong dung nhu thiet ke: neu khong,
        # pack se co cot lai vua khit noi dung va bo cuc bi hep lai.
        ctk.CTkFrame(
            cot, fg_color="transparent", height=0, width=KichThuoc.RONG_NOI_DUNG
        ).pack()

        ctk.CTkLabel(
            cot,
            text=cau_hoi.de_bai,
            font=phong(22),
            text_color=Mau.CHU,
        ).pack(anchor="w", pady=(0, 22))

        match cau_hoi.loai:
            case LoaiBaiTap.GO_TU:
                self._dung_cau_go(cot, cau_hoi)
            case LoaiBaiTap.GHEP_DOI:
                self._dung_cau_ghep(cot, cau_hoi)
            case LoaiBaiTap.NGHE_CHON:
                self._dung_cau_nghe(cot, cau_hoi)
            case LoaiBaiTap.NGHE_VIET:
                self._dung_cau_nghe_viet(cot, cau_hoi)
            case LoaiBaiTap.NOI_THEO:
                self._dung_cau_noi(cot, cau_hoi)
            case LoaiBaiTap.DIEN_CHO_TRONG:
                self._dung_cau_dien(cot, cau_hoi)
            case LoaiBaiTap.SAP_XEP_CAU:
                self._dung_cau_sap_xep(cot, cau_hoi)
            case LoaiBaiTap.CHON_DANG_DUNG:
                self._dung_cau_chon_dang(cot, cau_hoi)
            case _:
                self._dung_cau_trac_nghiem(cot, cau_hoi)

    def _dung_cau_trac_nghiem(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Hiện từ cần dịch rồi liệt kê các phương án dạng lưới 2 cột."""
        self._dung_the_tu(cha, cau_hoi)

        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x", pady=(6, 0))
        luoi.grid_columnconfigure((0, 1), weight=1, uniform="lua_chon")

        for thu_tu, gia_tri in enumerate(cau_hoi.lua_chon):
            the = TheLuaChon(
                luoi,
                text=gia_tri,
                command=self._chon_dap_an,
                so_thu_tu=thu_tu + 1,
            )
            the.grid(
                row=thu_tu // 2,
                column=thu_tu % 2,
                sticky="ew",
                padx=6,
                pady=6,
            )
            self._the_theo_gia_tri[gia_tri] = the

    def _dung_the_tu(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Thẻ lớn chứa từ đang được hỏi và phiên âm của nó."""
        the = The(cha)
        the.pack(fill="x", pady=(0, 20))

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(fill="x", padx=24, pady=20)

        hang_tren = ctk.CTkFrame(trong, fg_color="transparent")
        hang_tren.pack(fill="x")

        ctk.CTkLabel(
            hang_tren,
            text=cau_hoi.cau_hoi,
            font=phong(30),
            text_color=Mau.CHU,
        ).pack(side="left")

        # Chi doc khi de bai dang hien chu tieng Anh, khong thi lo dap an.
        if self._am_thanh.kha_nang.doc and cau_hoi.loai is LoaiBaiTap.CHON_NGHIA:
            NutLoa(
                hang_tren, khi_bam=lambda: self._am_thanh.doc(cau_hoi.tu.en)
            ).pack(side="left", padx=(14, 0))

        hien_phien_am = (
            cau_hoi.loai is LoaiBaiTap.CHON_NGHIA and cau_hoi.tu.phien_am
        )
        if hien_phien_am:
            ctk.CTkLabel(
                trong,
                text=cau_hoi.tu.phien_am,
                font=phong(15, dam=False),
                text_color=Mau.CHU_MO,
            ).pack(anchor="w", pady=(4, 0))

    def _dung_cau_go(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Ô nhập để người học tự viết từ tiếng Anh."""
        self._dung_the_tu(cha, cau_hoi)

        o_nhap = ctk.CTkEntry(
            cha,
            height=62,
            corner_radius=KichThuoc.BO_GOC,
            border_width=2,
            border_color=Mau.VIEN,
            fg_color=Mau.NEN_THE,
            text_color=Mau.CHU,
            font=phong(20, dam=False),
            placeholder_text="Gõ câu trả lời bằng tiếng Anh...",
            placeholder_text_color=Mau.CHU_MO,
        )
        o_nhap.pack(fill="x")
        o_nhap.bind("<KeyRelease>", self._khi_go_phim)
        o_nhap.after(50, o_nhap.focus_set)
        self._o_nhap = o_nhap

    def _dung_cau_ghep(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Hai cột thẻ, bấm một thẻ tiếng Anh rồi tới thẻ tiếng Việt tương ứng."""
        rng = Random()
        ben_trai = list(cau_hoi.cac_cap)
        ben_phai = list(cau_hoi.cac_cap)
        rng.shuffle(ben_trai)
        rng.shuffle(ben_phai)
        self._con_lai_ghep = len(cau_hoi.cac_cap)

        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x")
        luoi.grid_columnconfigure((0, 1), weight=1, uniform="ghep")

        for hang, tu in enumerate(ben_trai):
            self._them_the_ghep(luoi, tu, hang, cot=0, hien_tieng_anh=True)
        for hang, tu in enumerate(ben_phai):
            self._them_the_ghep(luoi, tu, hang, cot=1, hien_tieng_anh=False)

    def _them_the_ghep(
        self,
        luoi: ctk.CTkFrame,
        tu: TuVung,
        hang: int,
        *,
        cot: int,
        hien_tieng_anh: bool,
    ) -> None:
        the = TheLuaChon(
            luoi,
            text=tu.en if hien_tieng_anh else tu.vi,
            chieu_cao=56,
            co_chu=16,
        )
        the.dat_hanh_dong(lambda _: self._chon_the_ghep(the, tu, hien_tieng_anh))
        the.grid(row=hang, column=cot, sticky="ew", padx=6, pady=5)

    def _dung_cau_nghe(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Nút loa lớn thay cho đề bài: người học phải nghe rồi mới chọn."""
        the = The(cha)
        the.pack(fill="x", pady=(0, 20))

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(pady=26)

        NutLoa(
            trong,
            khi_bam=lambda: self._am_thanh.doc(cau_hoi.tu.en),
            duong_kinh=76,
            co_chu=32,
        ).pack()
        ctk.CTkLabel(
            trong,
            text="Nhấn để nghe lại",
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(pady=(10, 0))

        # Đọc sẵn một lần cho người học khỏi phải bấm.
        self.after(320, lambda: self._am_thanh.doc(cau_hoi.tu.en))

        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x", pady=(6, 0))
        luoi.grid_columnconfigure((0, 1), weight=1, uniform="lua_chon")
        for thu_tu, gia_tri in enumerate(cau_hoi.lua_chon):
            the_chon = TheLuaChon(
                luoi, text=gia_tri, command=self._chon_dap_an, so_thu_tu=thu_tu + 1
            )
            the_chon.grid(
                row=thu_tu // 2, column=thu_tu % 2, sticky="ew", padx=6, pady=6
            )
            self._the_theo_gia_tri[gia_tri] = the_chon

    def _dung_cau_nghe_viet(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Bài chính tả: nghe cả câu rồi gõ lại."""
        the = The(cha)
        the.pack(fill="x", pady=(0, 18))

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(pady=24)

        NutLoa(
            trong,
            khi_bam=lambda: self._am_thanh.doc(cau_hoi.dap_an),
            duong_kinh=72,
            co_chu=30,
        ).pack()
        ctk.CTkLabel(
            trong,
            text="Nhấn để nghe lại cả câu",
            font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(pady=(10, 0))

        self.after(320, lambda: self._am_thanh.doc(cau_hoi.dap_an))

        o_nhap = ctk.CTkEntry(
            cha,
            height=58,
            corner_radius=KichThuoc.BO_GOC,
            border_width=2,
            border_color=Mau.VIEN,
            fg_color=Mau.NEN_THE,
            text_color=Mau.CHU,
            font=phong(18, dam=False),
            placeholder_text="Gõ lại câu em vừa nghe...",
            placeholder_text_color=Mau.CHU_MO,
        )
        o_nhap.pack(fill="x")
        o_nhap.bind("<KeyRelease>", self._khi_go_phim)
        o_nhap.after(50, o_nhap.focus_set)
        self._o_nhap = o_nhap

    def _dung_cau_noi(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Hiện từ cần đọc, kèm nút nghe mẫu và nút micro."""
        the = The(cha)
        the.pack(fill="x", pady=(0, 18))

        trong = ctk.CTkFrame(the, fg_color="transparent")
        trong.pack(pady=22)

        hang = ctk.CTkFrame(trong, fg_color="transparent")
        hang.pack()
        ctk.CTkLabel(
            hang, text=cau_hoi.tu.en, font=phong(34), text_color=Mau.CHU
        ).pack(side="left")
        if self._am_thanh.kha_nang.doc:
            NutLoa(
                hang, khi_bam=lambda: self._am_thanh.doc(cau_hoi.tu.en)
            ).pack(side="left", padx=(16, 0))

        if cau_hoi.tu.phien_am:
            ctk.CTkLabel(
                trong,
                text=cau_hoi.tu.phien_am,
                font=phong(15, dam=False),
                text_color=Mau.CHU_MO,
            ).pack(pady=(6, 0))

        self._nhan_mic = ctk.CTkLabel(
            cha,
            text="Nhấn micro rồi đọc to từ ở trên",
            font=phong(14, dam=False),
            text_color=Mau.CHU_PHU,
        )
        self._nhan_mic.pack(pady=(0, 12))

        self._nut_mic = NutDuo(
            cha,
            text="🎤  NÓI",
            command=lambda: self._bat_dau_noi(cau_hoi),
            kieu=KieuNut.THONG_TIN,
            chieu_rong=220,
        )
        self._nut_mic.pack()

        NutDuo(
            cha,
            text="Không nói được lúc này",
            command=self._bo_qua_cau_noi,
            kieu=KieuNut.PHU,
            chieu_rong=240,
            chieu_cao=40,
            co_chu=13,
        ).pack(pady=(14, 0))

    def _bat_dau_noi(self, cau_hoi: CauHoi) -> None:
        """Thu giọng người học rồi gửi đi chấm điểm phát âm."""
        if self._da_kiem_tra or self._nut_mic is None or self._nhan_mic is None:
            return

        if not self._am_thanh.cham_phat_am(cau_hoi.tu.en, self._khi_cham_xong):
            self._nhan_mic.configure(
                text="Không dùng được micro trên máy này.", text_color=Mau.DO_DAM
            )
            return

        self._nut_mic.dat_chu("🔴  ĐANG NGHE...")
        self._nut_mic.dat_bat(False)
        self._nhan_mic.configure(
            text=f"Đang thu {GIAY_THU_AM:.0f} giây, đọc to lên nào!",
            text_color=Mau.XANH_DUONG_DAM,
        )

    def _khi_cham_xong(self, ket_qua: KetQuaPhatAm) -> None:
        """Chạy ở luồng nền: phải đẩy về luồng giao diện trước khi vẽ."""
        if self.winfo_exists():
            self.after(0, lambda: self._hien_ket_qua_noi(ket_qua))

    def _hien_ket_qua_noi(self, ket_qua: KetQuaPhatAm) -> None:
        if self._da_kiem_tra or self._nut_mic is None or self._nhan_mic is None:
            return
        if not self.winfo_exists():
            return

        if ket_qua.loi is not None:
            self._nut_mic.dat_chu("🎤  THỬ LẠI")
            self._nut_mic.dat_bat(True)
            self._nhan_mic.configure(text=ket_qua.loi, text_color=Mau.CAM_DAM)
            return

        self._nhan_mic.configure(
            text=f"Máy nghe được: {ket_qua.nghe_duoc} · {ket_qua.diem}/100",
            text_color=Mau.XANH_LA_DAM if ket_qua.dat else Mau.DO_DAM,
        )
        if ket_qua.dat:
            self._dap_an_chon = DAP_AN_NOI_DUNG
            self._kiem_tra_dap_an()
            return

        self._nut_mic.dat_chu("🎤  THỬ LẠI")
        self._nut_mic.dat_bat(True)
        self._dap_an_chon = "__noi_chua_dat__"
        self._nut_chinh.dat_bat(True)

    def _bo_qua_cau_noi(self) -> None:
        """Bỏ qua bài nói mà không bị trừ tim.

        Giống nút "không nói được lúc này" của Duolingo: hỏng micro hay đang ở
        chỗ đông người thì không nên chặn người học lại.
        """
        if self._da_kiem_tra:
            return
        self._dap_an_chon = DAP_AN_NOI_DUNG
        self._kiem_tra_dap_an()

    # ------------------------------------------------------------------ #
    # Bài ngữ pháp
    # ------------------------------------------------------------------ #

    def _the_cau_ngu_phap(self, cha: ctk.CTkFrame, noi_dung: str) -> None:
        """Thẻ hiển thị câu đề bài của bài ngữ pháp."""
        the = The(cha)
        the.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            the,
            text=noi_dung,
            font=phong(21),
            text_color=Mau.CHU,
            wraplength=KichThuoc.RONG_NOI_DUNG - 60,
            justify="left",
        ).pack(anchor="w", padx=24, pady=22)

    def _dung_cau_dien(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Câu có chỗ trống, người học tự gõ phần còn thiếu."""
        self._the_cau_ngu_phap(cha, cau_hoi.cau_hoi)

        o_nhap = ctk.CTkEntry(
            cha,
            height=58,
            corner_radius=KichThuoc.BO_GOC,
            border_width=2,
            border_color=Mau.VIEN,
            fg_color=Mau.NEN_THE,
            text_color=Mau.CHU,
            font=phong(19, dam=False),
            placeholder_text="Điền vào chỗ trống...",
            placeholder_text_color=Mau.CHU_MO,
        )
        o_nhap.pack(fill="x")
        o_nhap.bind("<KeyRelease>", self._khi_go_phim)
        o_nhap.after(50, o_nhap.focus_set)
        self._o_nhap = o_nhap

    def _dung_cau_chon_dang(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Câu ngữ pháp trắc nghiệm bốn phương án."""
        self._the_cau_ngu_phap(cha, cau_hoi.cau_hoi)

        luoi = ctk.CTkFrame(cha, fg_color="transparent")
        luoi.pack(fill="x", pady=(6, 0))
        luoi.grid_columnconfigure((0, 1), weight=1, uniform="lua_chon")

        for thu_tu, gia_tri in enumerate(cau_hoi.lua_chon):
            the = TheLuaChon(
                luoi, text=gia_tri, command=self._chon_dap_an, so_thu_tu=thu_tu + 1
            )
            the.grid(row=thu_tu // 2, column=thu_tu % 2, sticky="ew", padx=6, pady=6)
            self._the_theo_gia_tri[gia_tri] = the

    def _dung_cau_sap_xep(self, cha: ctk.CTkFrame, cau_hoi: CauHoi) -> None:
        """Bấm các mảnh chữ để ghép thành câu, bấm lại để bỏ ra."""
        ctk.CTkLabel(
            cha,
            text=cau_hoi.cau_hoi,
            font=phong(20),
            text_color=Mau.CHU_PHU,
            wraplength=KichThuoc.RONG_NOI_DUNG - 20,
            justify="left",
        ).pack(anchor="w", pady=(0, 14))

        khung_ghep = ctk.CTkFrame(
            cha,
            fg_color=Mau.NEN_PHU,
            corner_radius=KichThuoc.BO_GOC,
            height=76,
        )
        khung_ghep.pack(fill="x", pady=(0, 18))
        khung_ghep.pack_propagate(False)

        self._o_ghep_cau = ctk.CTkLabel(
            khung_ghep,
            text="",
            font=phong(20),
            text_color=Mau.CHU,
            wraplength=KichThuoc.RONG_NOI_DUNG - 40,
            justify="left",
            anchor="w",
        )
        # Canh trái để câu lớn dần từ trái sang, chữ không nhảy chỗ mỗi lần bấm.
        self._o_ghep_cau.pack(fill="both", expand=True, padx=18, pady=10)
        # Bấm vào câu đang ghép để gỡ mảnh vừa thêm ra.
        for widget in (khung_ghep, self._o_ghep_cau):
            widget.bind("<Button-1>", lambda _: self._bo_manh_cuoi(cau_hoi))

        self._kho_manh = ctk.CTkFrame(cha, fg_color="transparent")
        self._kho_manh.pack(fill="x")
        self._ve_kho_manh(cau_hoi)

    def _ve_kho_manh(self, cau_hoi: CauHoi) -> None:
        """Vẽ lại các mảnh chữ chưa dùng, xếp thành nhiều dòng cho vừa bề ngang."""
        if self._kho_manh is None:
            return
        for con in self._kho_manh.winfo_children():
            con.destroy()
        self._nut_manh.clear()

        hang = ctk.CTkFrame(self._kho_manh, fg_color="transparent")
        hang.pack(fill="x", pady=4)
        rong_da_dung = 0

        da_dung = set(self._vi_tri_da_chon)
        for chi_so, manh in enumerate(cau_hoi.cac_manh):
            if chi_so in da_dung:
                continue

            rong = max(70, len(manh) * 13 + 34)
            if rong_da_dung + rong > KichThuoc.RONG_NOI_DUNG:
                hang = ctk.CTkFrame(self._kho_manh, fg_color="transparent")
                hang.pack(fill="x", pady=4)
                rong_da_dung = 0
            rong_da_dung += rong + 8

            nut = NutDuo(
                hang,
                text=manh,
                command=lambda i=chi_so: self._chon_manh(cau_hoi, i),
                kieu=KieuNut.PHU,
                chieu_rong=rong,
                chieu_cao=46,
                co_chu=16,
            )
            nut.pack(side="left", padx=4)
            self._nut_manh[chi_so] = nut

    def _chon_manh(self, cau_hoi: CauHoi, chi_so: int) -> None:
        """Thêm một mảnh vào câu đang ghép."""
        if self._da_kiem_tra or chi_so in self._vi_tri_da_chon:
            return
        self._vi_tri_da_chon.append(chi_so)
        self._cap_nhat_cau_ghep(cau_hoi)

    def _bo_manh_cuoi(self, cau_hoi: CauHoi) -> None:
        """Bấm vào câu đang ghép thì gỡ mảnh vừa thêm ra."""
        if self._da_kiem_tra or not self._vi_tri_da_chon:
            return
        self._vi_tri_da_chon.pop()
        self._cap_nhat_cau_ghep(cau_hoi)

    def _cap_nhat_cau_ghep(self, cau_hoi: CauHoi) -> None:
        cac_manh = [cau_hoi.cac_manh[i] for i in self._vi_tri_da_chon]
        cau = " ".join(cac_manh)

        if self._o_ghep_cau is not None:
            self._o_ghep_cau.configure(text=cau)
        self._ve_kho_manh(cau_hoi)

        self._dap_an_chon = cau or None
        self._nut_chinh.dat_bat(bool(cac_manh))

    # ------------------------------------------------------------------ #
    # Tương tác
    # ------------------------------------------------------------------ #

    def _chon_dap_an(self, gia_tri: str) -> None:
        if self._da_kiem_tra:
            return
        for gia_tri_the, the in self._the_theo_gia_tri.items():
            the.dat_trang_thai(
                TrangThaiThe.DANG_CHON
                if gia_tri_the == gia_tri
                else TrangThaiThe.MAC_DINH
            )
        self._dap_an_chon = gia_tri
        self._nut_chinh.dat_bat(True)

    def _chon_the_ghep(
        self, the: TheLuaChon, tu: TuVung, hien_tieng_anh: bool
    ) -> None:
        """Xử lý một lần bấm trong bài ghép đôi."""
        if self._da_kiem_tra:
            return

        cho = self._cho_ghep
        if cho is None:
            the.dat_trang_thai(TrangThaiThe.DANG_CHON)
            self._cho_ghep = the
            self._tu_dang_cho = tu
            self._ben_dang_cho = hien_tieng_anh
            return

        if cho is the:
            the.dat_trang_thai(TrangThaiThe.MAC_DINH)
            self._cho_ghep = None
            return

        if hien_tieng_anh == self._ben_dang_cho:
            cho.dat_trang_thai(TrangThaiThe.MAC_DINH)
            the.dat_trang_thai(TrangThaiThe.DANG_CHON)
            self._cho_ghep = the
            self._tu_dang_cho = tu
            self._ben_dang_cho = hien_tieng_anh
            return

        if tu == self._tu_dang_cho:
            self._ghep_thanh_cong(cho, the)
        else:
            self._ghep_that_bai(cho, the)

    def _ghep_thanh_cong(self, mot: TheLuaChon, hai: TheLuaChon) -> None:
        for the in (mot, hai):
            the.dat_trang_thai(TrangThaiThe.MO)
            the.dat_bat(False)
        self._cho_ghep = None
        self._con_lai_ghep -= 1
        if self._con_lai_ghep == 0:
            self._dap_an_chon = DAP_AN_GHEP_DUNG
            self.after(_CHO_GHEP_XONG, self._kiem_tra_dap_an)

    def _ghep_that_bai(self, mot: TheLuaChon, hai: TheLuaChon) -> None:
        """Nháy đỏ rồi trả về trạng thái ban đầu - không trừ tim."""
        for the in (mot, hai):
            the.dat_trang_thai(TrangThaiThe.SAI)
        self._cho_ghep = None

        def hoan_tac() -> None:
            for the in (mot, hai):
                if the.winfo_exists():
                    the.dat_trang_thai(TrangThaiThe.MAC_DINH)

        self.after(_CHO_GHEP_SAI, hoan_tac)

    def _khi_go_phim(self, _su_kien: object = None) -> None:
        if self._o_nhap is None:
            return
        noi_dung = self._o_nhap.get().strip()
        self._dap_an_chon = noi_dung or None
        self._nut_chinh.dat_bat(bool(noi_dung))

    def _phim_enter(self, _su_kien: object = None) -> None:
        self._khi_bam_nut_chinh()

    def _tao_phim_so(self, so: int) -> Callable[[object], None]:
        def xu_ly(_su_kien: object = None) -> None:
            if self._da_kiem_tra or self._o_nhap is not None:
                return
            if not self._the_theo_gia_tri:
                return
            cac_gia_tri = list(self._the_theo_gia_tri)
            if so <= len(cac_gia_tri):
                self._chon_dap_an(cac_gia_tri[so - 1])

        return xu_ly

    # ------------------------------------------------------------------ #
    # Chấm bài
    # ------------------------------------------------------------------ #

    def _khi_bam_nut_chinh(self) -> None:
        # Đã ở màn tổng kết thì nút (và cả phím Enter) chỉ còn việc thoát ra.
        if self._da_tong_ket:
            self._thoat()
        elif self._da_kiem_tra:
            self._hien_cau_hoi()
        elif self._dap_an_chon is not None:
            self._kiem_tra_dap_an()

    def _kiem_tra_dap_an(self) -> None:
        if self._da_kiem_tra or self._dap_an_chon is None:
            return
        self._da_kiem_tra = True

        cau_hoi = self._phien.cau_hoi_hien_tai
        ket_qua = self._phien.tra_loi(self._dap_an_chon)

        # Ghi ngay vào lịch ôn tập: phiên học có thất bại thì công sức với từng
        # từ vẫn được giữ lại.
        self.ung_dung.tien_do.ghi_nhan_tra_loi(ket_qua.khoa, ket_qua.dung)

        if self._nut_mic is not None:
            self._nut_mic.dat_bat(False)
        if self._day_tim is not None:
            self._day_tim.dat_so_tim(ket_qua.con_tim)
        self._cap_nhat_so_cau()
        self._thanh_tien_do.dat_gia_tri(self._phien.ty_le_hoan_thanh)
        self._to_mau_dap_an(cau_hoi, ket_qua.dung)
        self._dat_phan_hoi(
            ket_qua.dung, ket_qua.dap_an_dung, ket_qua.giai_thich
        )

        for the in self._the_theo_gia_tri.values():
            the.dat_bat(False)
        if self._o_nhap is not None:
            self._o_nhap.configure(state="disabled")

        ket_thuc = self._phien.trang_thai is not TrangThaiPhien.DANG_HOC
        self._nut_chinh.dat_chu("XEM KẾT QUẢ" if ket_thuc else "TIẾP TỤC")
        self._nut_chinh.dat_bat(True)

    def _cap_nhat_so_cau(self) -> None:
        """Bài kiểm tra hiện số câu đã làm thay cho dãy tim."""
        if self._nhan_so_cau is None:
            return
        da_lam = self._phien.tong_so_cau - len(self._phien._hang_doi)  # noqa: SLF001
        self._nhan_so_cau.configure(
            text=f"Câu {min(da_lam + 1, self._phien.tong_so_cau)}"
            f"/{self._phien.tong_so_cau}"
        )

    def _to_mau_dap_an(self, cau_hoi: CauHoi | None, dung: bool) -> None:
        """Tô xanh đáp án đúng và tô đỏ lựa chọn sai của người học."""
        if cau_hoi is None:
            return
        the_dung = self._the_theo_gia_tri.get(cau_hoi.dap_an)
        if the_dung is not None:
            the_dung.dat_trang_thai(TrangThaiThe.DUNG)
        if not dung and self._dap_an_chon is not None:
            the_sai = self._the_theo_gia_tri.get(self._dap_an_chon)
            if the_sai is not None:
                the_sai.dat_trang_thai(TrangThaiThe.SAI)
        if self._o_nhap is not None:
            self._o_nhap.configure(border_color=Mau.XANH_LA if dung else Mau.DO)

    def _dat_phan_hoi(
        self, dung: bool | None, dap_an: str = "", giai_thich: str = ""
    ) -> None:
        """Đổi màu thanh dưới và câu thông báo theo kết quả."""
        match dung:
            case None:
                self._thanh_duoi.configure(fg_color=Mau.NEN_PHU)
                self._nhan_phan_hoi.configure(text="")
            case True:
                self._thanh_duoi.configure(fg_color=Mau.XANH_LA_NHAT)
                self._nhan_phan_hoi.configure(
                    text="✓  Chính xác!", text_color=Mau.XANH_LA_DAM
                )
            case False:
                self._thanh_duoi.configure(fg_color=Mau.DO_NHAT)
                loi_nhan = f"✗  Đáp án đúng: {dap_an}"
                if giai_thich:
                    loi_nhan += f"\n{giai_thich}"
                self._nhan_phan_hoi.configure(
                    text=loi_nhan, text_color=Mau.DO_DAM
                )

    # ------------------------------------------------------------------ #
    # Kết thúc phiên học
    # ------------------------------------------------------------------ #

    def _hien_tong_ket(self) -> None:
        if self._noi_dung.la_kiem_tra:
            self._hien_ket_qua_kiem_tra()
            return

        thang_loi = self._phien.trang_thai is TrangThaiPhien.HOAN_THANH

        # Chỉ ghi công một lần: vẽ lại màn tổng kết không được cộng XP thêm.
        if thang_loi and not self._da_tong_ket:
            if self._noi_dung.danh_dau_hoan_thanh:
                self.ung_dung.tien_do.ghi_nhan_hoan_thanh(
                    self._noi_dung.ma, self._phien.xp_dat_duoc
                )
            else:
                self.ung_dung.tien_do.ghi_nhan_luyen_tap(self._phien.xp_dat_duoc)
            self.ung_dung.luu_tien_do()
        self._da_tong_ket = True

        for con in self._vung_cau_hoi.winfo_children():
            con.destroy()
        self._thanh_tien_do.dat_gia_tri(1.0 if thang_loi else 0.0)

        cot = ctk.CTkFrame(self._vung_cau_hoi, fg_color="transparent")
        cot.pack(expand=True)

        ctk.CTkLabel(cot, text="🎉" if thang_loi else "💔", font=phong(72)).pack()
        ctk.CTkLabel(
            cot,
            text=self._tieu_de_tong_ket(thang_loi),
            font=phong(30),
            text_color=Mau.XANH_LA_DAM if thang_loi else Mau.DO_DAM,
        ).pack(pady=(12, 6))
        ctk.CTkLabel(
            cot,
            text=(
                f"Bạn nhận được {self._phien.xp_dat_duoc} XP"
                if thang_loi
                else "Đừng lo, thử lại là được thôi!"
            ),
            font=phong(16, dam=False),
            text_color=Mau.CHU_PHU,
        ).pack()

        if thang_loi and self._phien.hoan_hao:
            ctk.CTkLabel(
                cot,
                text=f"⭐ Không sai câu nào: +{PhienHoc.XP_THUONG_HOAN_HAO} XP",
                font=phong(15),
                text_color=Mau.VANG_DAM,
            ).pack(pady=(10, 0))

        self._dat_phan_hoi(None)
        self._nhan_phan_hoi.configure(text="")
        self._nut_chinh.dat_chu("TIẾP TỤC" if thang_loi else "VỀ TRANG CHỦ")
        self._nut_chinh.dat_hanh_dong(self._thoat)
        self._nut_chinh.dat_bat(True)

    def _hien_ket_qua_kiem_tra(self) -> None:
        """Màn hình điểm số kiểu bài kiểm tra ở trường."""
        giay = int(time.monotonic() - self._luc_bat_dau)
        if not self._da_tong_ket:
            ket_qua = self.ung_dung.tien_do.ghi_nhan_kiem_tra(
                self._phien.tong_so_cau, self._phien.so_cau_dung, giay
            )
            self.ung_dung.luu_tien_do()
            self._ket_qua_kiem_tra = ket_qua
        self._da_tong_ket = True

        ket_qua = self._ket_qua_kiem_tra
        diem = ket_qua.diem
        mau_diem = (
            Mau.XANH_LA_DAM
            if diem >= 8
            else Mau.XANH_DUONG_DAM
            if diem >= 6.5
            else Mau.CAM_DAM
            if diem >= 5
            else Mau.DO_DAM
        )

        for con in self._vung_cau_hoi.winfo_children():
            con.destroy()
        self._thanh_tien_do.dat_gia_tri(1.0)

        cot = ctk.CTkFrame(self._vung_cau_hoi, fg_color="transparent")
        cot.pack(expand=True)

        ctk.CTkLabel(cot, text="📋", font=phong(56)).pack()
        ctk.CTkLabel(
            cot, text="Kết quả bài kiểm tra", font=phong(22), text_color=Mau.CHU
        ).pack(pady=(10, 16))

        ctk.CTkLabel(
            cot, text=f"{diem}", font=phong(64), text_color=mau_diem
        ).pack()
        ctk.CTkLabel(
            cot, text="trên thang điểm 10", font=phong(13, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(pady=(0, 14))

        ctk.CTkLabel(
            cot,
            text=f"{ket_qua.xep_loai} · Đúng {ket_qua.so_dung}/{ket_qua.so_cau} câu"
            f" · {giay // 60} phút {giay % 60} giây",
            font=phong(15),
            text_color=Mau.CHU_PHU,
        ).pack()

        cao_nhat = self.ung_dung.tien_do.diem_kiem_tra_cao_nhat
        if cao_nhat is not None and cao_nhat > diem:
            ctk.CTkLabel(
                cot,
                text=f"Điểm cao nhất của bạn: {cao_nhat}",
                font=phong(13, dam=False),
                text_color=Mau.CHU_MO,
            ).pack(pady=(8, 0))

        self._dat_phan_hoi(None)
        self._nut_chinh.dat_chu("XONG")
        self._nut_chinh.dat_hanh_dong(self._thoat)
        self._nut_chinh.dat_bat(True)

    def _tieu_de_tong_ket(self, thang_loi: bool) -> str:
        if not thang_loi:
            return "Hết tim rồi!"
        return {
            CheDoPhien.BAI_HOC: "Hoàn thành bài học!",
            CheDoPhien.LUYEN_TAP: "Xong buổi luyện tập!",
            CheDoPhien.NGU_PHAP: "Xong chủ điểm ngữ pháp!",
        }[self._noi_dung.che_do]

    def _thoat(self) -> None:
        match self._noi_dung.che_do:
            case CheDoPhien.LUYEN_TAP | CheDoPhien.KIEM_TRA:
                self.ung_dung.mo_luyen_tap()
            case CheDoPhien.NGU_PHAP:
                self.ung_dung.mo_ngu_phap()
            case _:
                self.ung_dung.mo_trang_chu()
