"""Bộ widget dùng lại, dựng nên phong cách Duolingo.

Điểm nhận diện của Duolingo là nút bấm "nổi khối": một lớp bóng đậm màu nằm dưới
mặt nút, và mặt nút tụt xuống che lớp bóng khi được bấm. CustomTkinter không có
sẵn hiệu ứng này nên các lớp dưới đây tự dựng bằng hai widget xếp chồng.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable, Final

import customtkinter as ctk

from .chu_de import BoMau, CapMau, KichThuoc, Mau, phong

__all__ = [
    "KieuNut",
    "TrangThaiThe",
    "TrangThaiNut",
    "NutDuo",
    "TheLuaChon",
    "NutTron",
    "ThanhTienDo",
    "DayTim",
    "HuyHieu",
    "The",
    "NutLoa",
]

_THOI_GIAN_LUN: Final[int] = 90
"""Số mili giây mặt nút giữ ở vị trí bị nhấn xuống."""


class KieuNut(Enum):
    """Các kiểu nút theo mức độ nhấn mạnh."""

    CHINH = auto()
    """Hành động chính, màu xanh lá."""

    PHU = auto()
    """Hành động phụ, nền trắng viền xám."""

    THONG_TIN = auto()
    """Hành động mang tính thông tin, màu xanh dương."""

    NGUY_HIEM = auto()
    """Hành động cần cân nhắc, màu đỏ."""


_BO_MAU_NUT: Final[dict[KieuNut, BoMau]] = {
    KieuNut.CHINH: BoMau(Mau.XANH_LA, Mau.XANH_LA_DAM, Mau.XANH_LA_NHAT),
    KieuNut.PHU: BoMau(Mau.NEN_THE, Mau.VIEN, Mau.NEN_PHU),
    KieuNut.THONG_TIN: BoMau(Mau.XANH_DUONG, Mau.XANH_DUONG_DAM, Mau.XANH_DUONG_NHAT),
    KieuNut.NGUY_HIEM: BoMau(Mau.DO, Mau.DO_DAM, Mau.DO_NHAT),
}

_MAU_CHU_NUT: Final[dict[KieuNut, CapMau]] = {
    KieuNut.CHINH: Mau.CHU_TREN_NEN_DAM,
    KieuNut.PHU: Mau.CHU_PHU,
    KieuNut.THONG_TIN: Mau.CHU_TREN_NEN_DAM,
    KieuNut.NGUY_HIEM: Mau.CHU_TREN_NEN_DAM,
}


class NutDuo(ctk.CTkFrame):
    """Nút bấm nổi khối, lún xuống khi được nhấn."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        text: str,
        command: Callable[[], None] | None = None,
        kieu: KieuNut = KieuNut.CHINH,
        chieu_rong: int = 220,
        chieu_cao: int = KichThuoc.CAO_NUT,
        co_chu: int = 16,
        bat: bool = True,
    ) -> None:
        super().__init__(
            master,
            fg_color="transparent",
            width=chieu_rong,
            height=chieu_cao + KichThuoc.DO_SAU_NUT,
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._kieu = kieu
        self._command = command
        self._chieu_cao = chieu_cao
        self._dang_bam = False
        self._bat = bat

        bo_mau = _BO_MAU_NUT[kieu]
        self._bong = ctk.CTkFrame(
            self,
            corner_radius=KichThuoc.BO_GOC,
            fg_color=bo_mau.dam,
            height=chieu_cao,
        )
        self._bong.place(relx=0, y=KichThuoc.DO_SAU_NUT, relwidth=1)

        self._nut = ctk.CTkButton(
            self,
            text=text,
            command=self._khi_bam,
            corner_radius=KichThuoc.BO_GOC,
            fg_color=bo_mau.chinh,
            hover_color=bo_mau.nhat if kieu is KieuNut.PHU else bo_mau.dam,
            text_color=_MAU_CHU_NUT[kieu],
            border_width=2 if kieu is KieuNut.PHU else 0,
            border_color=Mau.VIEN,
            font=phong(co_chu),
            height=chieu_cao,
        )
        self._nut.place(relx=0, y=0, relwidth=1)

        if not bat:
            self.dat_bat(False)

    # ------------------------------------------------------------------ #

    def _khi_bam(self) -> None:
        """Cho mặt nút lún xuống rồi mới chạy hành động."""
        if self._dang_bam or not self._bat:
            return
        self._dang_bam = True
        self._nut.place_configure(y=KichThuoc.DO_SAU_NUT)
        self.after(_THOI_GIAN_LUN, self._nha_nut)

    def _nha_nut(self) -> None:
        if not self.winfo_exists():
            return
        self._nut.place_configure(y=0)
        self._dang_bam = False
        if self._command is not None:
            self._command()

    # ------------------------------------------------------------------ #

    def dat_bat(self, bat: bool) -> None:
        """Bật hoặc khoá nút."""
        self._bat = bat
        bo_mau = _BO_MAU_NUT[self._kieu]
        self._nut.configure(
            state="normal" if bat else "disabled",
            fg_color=bo_mau.chinh if bat else Mau.XAM,
            text_color=_MAU_CHU_NUT[self._kieu] if bat else Mau.CHU_MO,
        )
        self._bong.configure(fg_color=bo_mau.dam if bat else Mau.XAM_DAM)

    def dat_chu(self, text: str) -> None:
        self._nut.configure(text=text)

    def dat_hanh_dong(self, command: Callable[[], None] | None) -> None:
        self._command = command


class TrangThaiThe(Enum):
    """Trạng thái hiển thị của một thẻ đáp án."""

    MAC_DINH = auto()
    DANG_CHON = auto()
    DUNG = auto()
    SAI = auto()
    MO = auto()
    """Đã được ghép xong, làm mờ đi."""


_MAU_THE: Final[dict[TrangThaiThe, tuple[CapMau, CapMau, CapMau]]] = {
    # (nền, viền/bóng, chữ)
    TrangThaiThe.MAC_DINH: (Mau.NEN_THE, Mau.VIEN, Mau.CHU),
    TrangThaiThe.DANG_CHON: (Mau.XANH_DUONG_NHAT, Mau.XANH_DUONG, Mau.XANH_DUONG_DAM),
    TrangThaiThe.DUNG: (Mau.XANH_LA_NHAT, Mau.XANH_LA, Mau.XANH_LA_DAM),
    TrangThaiThe.SAI: (Mau.DO_NHAT, Mau.DO, Mau.DO_DAM),
    TrangThaiThe.MO: (Mau.NEN_PHU, Mau.NEN_PHU, Mau.CHU_MO),
}


class TheLuaChon(ctk.CTkFrame):
    """Thẻ đáp án bấm chọn được, có viền đổi màu theo trạng thái."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        text: str,
        command: Callable[[str], None] | None = None,
        so_thu_tu: int | None = None,
        chieu_cao: int = 62,
        co_chu: int = 17,
    ) -> None:
        super().__init__(
            master,
            fg_color="transparent",
            height=chieu_cao + KichThuoc.DO_SAU_NUT,
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.gia_tri = text
        self._command = command
        self._trang_thai = TrangThaiThe.MAC_DINH
        self._bat = True

        self._bong = ctk.CTkFrame(
            self, corner_radius=KichThuoc.BO_GOC, fg_color=Mau.VIEN, height=chieu_cao
        )
        self._bong.place(relx=0, y=KichThuoc.DO_SAU_NUT, relwidth=1)

        self._nut = ctk.CTkButton(
            self,
            text=text,
            command=self._khi_bam,
            corner_radius=KichThuoc.BO_GOC,
            fg_color=Mau.NEN_THE,
            hover_color=Mau.NEN_PHU,
            text_color=Mau.CHU,
            border_width=2,
            border_color=Mau.VIEN,
            font=phong(co_chu),
            height=chieu_cao,
        )
        self._nut.place(relx=0, y=0, relwidth=1)

        self._nhan_so: ctk.CTkLabel | None = None
        if so_thu_tu is not None:
            self._nhan_so = ctk.CTkLabel(
                self,
                text=str(so_thu_tu),
                font=phong(12),
                text_color=Mau.CHU_MO,
                fg_color="transparent",
                width=18,
            )
            self._nhan_so.place(x=14, y=chieu_cao / 2, anchor="w")
            self._nhan_so.bind("<Button-1>", lambda _: self._khi_bam())

    def _khi_bam(self) -> None:
        if self._bat and self._command is not None:
            self._command(self.gia_tri)

    def dat_trang_thai(self, trang_thai: TrangThaiThe) -> None:
        """Đổi màu thẻ theo trạng thái chọn / đúng / sai."""
        self._trang_thai = trang_thai
        nen, vien, chu = _MAU_THE[trang_thai]
        self._nut.configure(fg_color=nen, border_color=vien, text_color=chu)
        self._bong.configure(fg_color=vien)
        if self._nhan_so is not None:
            # Nhan so co nen rieng, phai to lai cho khop voi mat the.
            self._nhan_so.configure(fg_color=nen, text_color=chu)

    def dat_hanh_dong(self, command: Callable[[str], None] | None) -> None:
        """Gán hành động sau khi tạo thẻ, dùng khi hành động cần chính thẻ đó."""
        self._command = command

    def dat_bat(self, bat: bool) -> None:
        self._bat = bat
        self._nut.configure(hover=bat)


class TrangThaiNut(Enum):
    """Trạng thái của một chặng trên lộ trình học."""

    KHOA = auto()
    MO = auto()
    HOAN_THANH = auto()


class NutTron(ctk.CTkFrame):
    """Chặng học hình tròn trên lộ trình, kiểu bong bóng của Duolingo.

    Biểu tượng được vẽ bằng một nhãn phủ lên trên mặt nút thay vì đặt làm chữ
    của nút. Lý do: CTkButton tự nới rộng theo bề ngang của chữ, mà hình tròn
    lại cần bề ngang cố định - để chữ bên trong thì biểu tượng bị cắt mất.
    """

    DUONG_KINH: Final[int] = 82
    DO_SAU: Final[int] = 6

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        bo_mau: BoMau,
        trang_thai: TrangThaiNut,
        bieu_tuong: str,
        command: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            fg_color="transparent",
            width=self.DUONG_KINH,
            height=self.DUONG_KINH + self.DO_SAU,
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._khoa = trang_thai is TrangThaiNut.KHOA
        self._command = command
        self._dang_bam = False

        mat = Mau.XAM if self._khoa else bo_mau.chinh
        bong = Mau.XAM_DAM if self._khoa else bo_mau.dam
        chu = Mau.CHU_MO if self._khoa else Mau.CHU_TREN_NEN_DAM
        nhan = "🔒" if self._khoa else bieu_tuong

        ban_kinh = self.DUONG_KINH // 2
        self._bong = ctk.CTkFrame(
            self,
            corner_radius=ban_kinh,
            fg_color=bong,
            width=self.DUONG_KINH,
            height=self.DUONG_KINH,
        )
        self._bong.place(relx=0, y=self.DO_SAU, relwidth=1)

        self._nut = ctk.CTkButton(
            self,
            text="",
            command=self._khi_bam,
            corner_radius=ban_kinh,
            width=self.DUONG_KINH,
            height=self.DUONG_KINH,
            fg_color=mat,
            hover_color=bong,
            state="disabled" if self._khoa else "normal",
        )
        self._nut.place(relx=0, y=0, relwidth=1)

        self._nhan = ctk.CTkLabel(
            self,
            text=nhan,
            font=phong(30),
            text_color=chu,
            fg_color=mat,
            # corner_radius=0: nhan phu kin o vuong cua no bang dung mau mat nut.
            # Neu bo goc, bon goc con lai se lo ra mau nen trang cua khung cha.
            corner_radius=0,
        )
        self._nhan.place(relx=0.5, y=self.DUONG_KINH // 2, anchor="center")
        if not self._khoa:
            self._nhan.bind("<Button-1>", lambda _: self._khi_bam())

    def _khi_bam(self) -> None:
        """Lún mặt nút xuống rồi mới chạy hành động, giống nút bấm thật."""
        if self._dang_bam or self._khoa:
            return
        self._dang_bam = True
        self._nut.place_configure(y=self.DO_SAU)
        self._nhan.place_configure(y=self.DUONG_KINH // 2 + self.DO_SAU)
        self.after(_THOI_GIAN_LUN, self._nha_nut)

    def _nha_nut(self) -> None:
        if not self.winfo_exists():
            return
        self._nut.place_configure(y=0)
        self._nhan.place_configure(y=self.DUONG_KINH // 2)
        self._dang_bam = False
        if self._command is not None:
            self._command()


class NutLoa(ctk.CTkFrame):
    """Nút tròn hình loa, bấm để nghe máy đọc từ."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        khi_bam: Callable[[], None],
        duong_kinh: int = 42,
        co_chu: int = 18,
    ) -> None:
        super().__init__(
            master, fg_color="transparent", width=duong_kinh, height=duong_kinh
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._nut = ctk.CTkButton(
            self,
            text="",
            command=khi_bam,
            corner_radius=duong_kinh // 2,
            width=duong_kinh,
            height=duong_kinh,
            fg_color=Mau.XANH_DUONG,
            hover_color=Mau.XANH_DUONG_DAM,
        )
        self._nut.place(relx=0, y=0, relwidth=1)

        # Cùng lý do như NutTron: chữ nằm ở nhãn phủ lên trên để nút giữ đúng
        # bề ngang, không bị chữ kéo cho méo hình tròn.
        self._nhan = ctk.CTkLabel(
            self,
            text="🔊",
            font=phong(co_chu),
            text_color=Mau.CHU_TREN_NEN_DAM,
            fg_color=Mau.XANH_DUONG,
            corner_radius=0,
        )
        self._nhan.place(relx=0.5, rely=0.5, anchor="center")
        self._nhan.bind("<Button-1>", lambda _: khi_bam())


class ThanhTienDo(ctk.CTkFrame):
    """Thanh tiến độ bo tròn, chạy mượt tới giá trị mới."""

    _BUOC: Final[float] = 0.04
    _NHIP: Final[int] = 16

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        mau: CapMau = Mau.XANH_LA,
        chieu_cao: int = 16,
    ) -> None:
        super().__init__(master, fg_color="transparent", height=chieu_cao)
        self.pack_propagate(False)

        self._thanh = ctk.CTkProgressBar(
            self,
            height=chieu_cao,
            corner_radius=chieu_cao // 2,
            fg_color=Mau.VIEN,
            progress_color=mau,
        )
        self._thanh.pack(fill="x", expand=True)
        self._thanh.set(0)
        self._muc_tieu = 0.0
        self._viec_dang_chay: str | None = None

    def dat_gia_tri(self, gia_tri: float, *, muot: bool = True) -> None:
        """Đặt tiến độ trong khoảng 0.0 - 1.0."""
        self._muc_tieu = min(1.0, max(0.0, gia_tri))
        if not muot:
            self._thanh.set(self._muc_tieu)
            return
        if self._viec_dang_chay is None:
            self._chay_tiep()

    def _chay_tiep(self) -> None:
        if not self.winfo_exists():
            return
        hien_tai = self._thanh.get()
        chenh_lech = self._muc_tieu - hien_tai
        if abs(chenh_lech) < self._BUOC:
            self._thanh.set(self._muc_tieu)
            self._viec_dang_chay = None
            return
        self._thanh.set(hien_tai + self._BUOC * (1 if chenh_lech > 0 else -1))
        self._viec_dang_chay = self.after(self._NHIP, self._chay_tiep)


class DayTim(ctk.CTkFrame):
    """Dãy trái tim thể hiện số lượt sai còn lại."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        toi_da: int,
        co_chu: int = 18,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._toi_da = toi_da
        self._cac_tim = [
            ctk.CTkLabel(self, text="❤", font=phong(co_chu), text_color=Mau.DO)
            for _ in range(toi_da)
        ]
        for chi_so, tim in enumerate(self._cac_tim):
            tim.grid(row=0, column=chi_so, padx=1)

    def dat_so_tim(self, con_lai: int) -> None:
        """Tô xám những trái tim đã mất."""
        for chi_so, tim in enumerate(self._cac_tim):
            con = chi_so < con_lai
            tim.configure(text="❤" if con else "🤍", text_color=Mau.DO if con else Mau.XAM)


class HuyHieu(ctk.CTkFrame):
    """Nhãn tròn nhỏ hiển thị một chỉ số, ví dụ 🔥 7 hoặc ⚡ 120."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        bieu_tuong: str,
        gia_tri: str,
        mau_chu: CapMau = Mau.CHU_PHU,
        co_chu: int = 15,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._nhan = ctk.CTkLabel(
            self,
            text=f"{bieu_tuong} {gia_tri}",
            font=phong(co_chu),
            text_color=mau_chu,
        )
        self._nhan.pack()
        self._bieu_tuong = bieu_tuong

    def dat_gia_tri(self, gia_tri: str) -> None:
        self._nhan.configure(text=f"{self._bieu_tuong} {gia_tri}")


class The(ctk.CTkFrame):
    """Khung thẻ bo góc, có viền nhạt - dùng cho danh sách và thống kê."""

    def __init__(
        self,
        master: ctk.CTkBaseClass | ctk.CTk,
        *,
        mau_nen: CapMau = Mau.NEN_THE,
        **tuy_chon: object,
    ) -> None:
        super().__init__(
            master,
            fg_color=mau_nen,
            corner_radius=KichThuoc.BO_GOC,
            border_width=2,
            border_color=Mau.VIEN,
            **tuy_chon,  # type: ignore[arg-type]
        )
