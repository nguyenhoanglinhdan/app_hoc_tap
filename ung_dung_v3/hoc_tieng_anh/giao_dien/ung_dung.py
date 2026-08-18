"""Cửa sổ chính: thanh điều hướng bên trái và bộ chuyển màn hình."""

from __future__ import annotations

import logging
from enum import Enum, auto
from typing import Callable, Final, Sequence

import customtkinter as ctk

from ..am_thanh import DichVuAmThanh
from ..bai_tap import NoiDungPhien
from ..kho_du_lieu import KhoDuLieu, LoiDuLieu
from ..mo_hinh import BaiHoc, GiaoTrinh, TuVung
from ..ngu_phap import ChuDiemNguPhap
from .chu_de import KichThuoc, Mau, phong
from .man_hinh_bai_hoc import ManHinhBaiHoc
from .man_hinh_chinh import ManHinhChinh
from .man_hinh_goc import ManHinh
from .man_hinh_ho_so import ManHinhHoSo
from .man_hinh_luyen_tap import ManHinhLuyenTap
from .man_hinh_ngu_phap import ManHinhNguPhap
from .man_hinh_soan_tu import ManHinhSoanTu
from .man_hinh_tu_vung import ManHinhTuVung

__all__ = ["UngDung", "TEN_UNG_DUNG"]

_log = logging.getLogger(__name__)

TEN_UNG_DUNG: Final[str] = "Học Tiếng Anh"
_RONG_THANH_BEN: Final[int] = 216


class Muc(Enum):
    """Các mục trên thanh điều hướng."""

    HOC = auto()
    NGU_PHAP = auto()
    LUYEN_TAP = auto()
    TU_VUNG = auto()
    SOAN_TU = auto()
    HO_SO = auto()


_NHAN_MUC: Final[dict[Muc, tuple[str, str]]] = {
    Muc.HOC: ("🏠", "Học"),
    Muc.NGU_PHAP: ("📐", "Ngữ pháp"),
    Muc.LUYEN_TAP: ("🎯", "Luyện tập"),
    Muc.TU_VUNG: ("📖", "Từ vựng"),
    Muc.SOAN_TU: ("📝", "Soạn từ"),
    Muc.HO_SO: ("🦉", "Hồ sơ"),
}


class UngDung(ctk.CTk):
    """Cửa sổ gốc, đồng thời là bộ điều hướng cho các màn hình con."""

    def __init__(self, kho: KhoDuLieu) -> None:
        super().__init__()

        self._kho = kho
        self.giao_trinh = kho.tai_giao_trinh()
        self.ngu_phap = kho.tai_ngu_phap()
        self.tien_do = kho.tai_tien_do()
        self.am_thanh = DichVuAmThanh()

        self.title(TEN_UNG_DUNG)
        self.geometry(f"{KichThuoc.CUA_SO_RONG}x{KichThuoc.CUA_SO_CAO}")
        self.minsize(KichThuoc.CUA_SO_RONG_TOI_THIEU, KichThuoc.CUA_SO_CAO_TOI_THIEU)
        self.configure(fg_color=Mau.NEN)
        self.protocol("WM_DELETE_WINDOW", self._khi_dong_cua_so)

        self._man_hinh: ManHinh | None = None
        self._muc_hien_tai = Muc.HOC
        self._nut_muc: dict[Muc, ctk.CTkButton] = {}

        self._dung_bo_cuc()
        self.mo_trang_chu()

    # ------------------------------------------------------------------ #
    # Bố cục
    # ------------------------------------------------------------------ #

    def _dung_bo_cuc(self) -> None:
        self._thanh_ben = ctk.CTkFrame(
            self, width=_RONG_THANH_BEN, fg_color=Mau.NEN, corner_radius=0
        )
        self._thanh_ben.pack(side="left", fill="y")
        self._thanh_ben.pack_propagate(False)

        ctk.CTkLabel(
            self._thanh_ben,
            text=f"🦉 {TEN_UNG_DUNG}",
            font=phong(19),
            text_color=Mau.XANH_LA,
        ).pack(anchor="w", padx=20, pady=(26, 22))

        for muc in Muc:
            self._nut_muc[muc] = self._tao_nut_muc(muc)

        ctk.CTkLabel(
            self._thanh_ben,
            text="Học mỗi ngày một chút 💚",
            font=phong(12, dam=False),
            text_color=Mau.CHU_MO,
        ).pack(side="bottom", pady=18)

        ctk.CTkFrame(self, width=2, fg_color=Mau.VIEN, corner_radius=0).pack(
            side="left", fill="y"
        )

        self._vung_noi_dung = ctk.CTkFrame(self, fg_color=Mau.NEN, corner_radius=0)
        self._vung_noi_dung.pack(side="left", fill="both", expand=True)

    def _tao_nut_muc(self, muc: Muc) -> ctk.CTkButton:
        bieu_tuong, nhan = _NHAN_MUC[muc]
        nut = ctk.CTkButton(
            self._thanh_ben,
            text=f"  {bieu_tuong}   {nhan}",
            anchor="w",
            height=48,
            corner_radius=KichThuoc.BO_GOC,
            fg_color="transparent",
            hover_color=Mau.NEN_PHU,
            text_color=Mau.CHU_PHU,
            font=phong(15),
            command=lambda: self._chon_muc(muc),
        )
        nut.pack(fill="x", padx=12, pady=3)
        return nut

    def _to_dam_muc_dang_chon(self) -> None:
        """Mục đang mở được tô nền nhạt và chữ xanh."""
        for muc, nut in self._nut_muc.items():
            dang_chon = muc is self._muc_hien_tai
            nut.configure(
                fg_color=Mau.XANH_LA_NHAT if dang_chon else "transparent",
                text_color=Mau.CHU_NHAN_MANH if dang_chon else Mau.CHU_PHU,
            )

    def _chon_muc(self, muc: Muc) -> None:
        match muc:
            case Muc.HOC:
                self.mo_trang_chu()
            case Muc.NGU_PHAP:
                self.mo_ngu_phap()
            case Muc.LUYEN_TAP:
                self.mo_luyen_tap()
            case Muc.TU_VUNG:
                self.mo_tu_vung()
            case Muc.SOAN_TU:
                self.mo_soan_tu()
            case Muc.HO_SO:
                self.mo_ho_so()

    # ------------------------------------------------------------------ #
    # Điều hướng
    # ------------------------------------------------------------------ #

    def _thay_man_hinh(self, tao: Callable[[ctk.CTkFrame], ManHinh], muc: Muc) -> None:
        """Thay nội dung khung chính bằng màn hình mới."""
        if self._man_hinh is not None:
            self._man_hinh.destroy()

        self._muc_hien_tai = muc
        self._man_hinh = tao(self._vung_noi_dung)
        self._man_hinh.pack(fill="both", expand=True)

        if self._man_hinh.an_thanh_ben:
            self._thanh_ben.pack_forget()
        elif not self._thanh_ben.winfo_ismapped():
            self._thanh_ben.pack(side="left", fill="y", before=self._vung_noi_dung)

        self._to_dam_muc_dang_chon()

    def mo_trang_chu(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhChinh(cha, self), Muc.HOC)

    def mo_bai_hoc(self, bai_hoc: BaiHoc) -> None:
        noi_dung = NoiDungPhien.tu_bai_hoc(
            bai_hoc, self.giao_trinh.tat_ca_tu_vung, **self._tuy_chon_am_thanh()
        )
        self._mo_phien(noi_dung, self._muc_hien_tai)

    def mo_buoi_luyen(self, cac_tu: Sequence[TuVung]) -> None:
        """Mở buổi luyện tập gom từ nhiều đơn vị khác nhau."""
        noi_dung = NoiDungPhien.luyen_tap(
            cac_tu, self.giao_trinh.tat_ca_tu_vung, **self._tuy_chon_am_thanh()
        )
        self._mo_phien(noi_dung, Muc.LUYEN_TAP)

    def mo_chu_diem_ngu_phap(self, chu_diem: ChuDiemNguPhap) -> None:
        self._mo_phien(NoiDungPhien.tu_chu_diem(chu_diem), Muc.NGU_PHAP)

    def _mo_phien(self, noi_dung: NoiDungPhien, muc: Muc) -> None:
        self._thay_man_hinh(
            lambda cha: ManHinhBaiHoc(cha, self, noi_dung), muc
        )

    def _tuy_chon_am_thanh(self) -> dict[str, bool]:
        """Khả năng âm thanh hiện có, truyền xuống trình sinh câu hỏi."""
        kha_nang = self.am_thanh.kha_nang
        return {"co_loa": kha_nang.doc, "co_micro": kha_nang.thu_am}

    def mo_ngu_phap(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhNguPhap(cha, self), Muc.NGU_PHAP)

    def mo_luyen_tap(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhLuyenTap(cha, self), Muc.LUYEN_TAP)

    def mo_tu_vung(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhTuVung(cha, self), Muc.TU_VUNG)

    def mo_soan_tu(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhSoanTu(cha, self), Muc.SOAN_TU)

    def mo_ho_so(self) -> None:
        self._thay_man_hinh(lambda cha: ManHinhHoSo(cha, self), Muc.HO_SO)

    # ------------------------------------------------------------------ #
    # Lưu trữ
    # ------------------------------------------------------------------ #

    def luu_tien_do(self) -> None:
        self._kho.luu_tien_do(self.tien_do)

    def luu_giao_trinh(self, giao_trinh: GiaoTrinh) -> None:
        """Ghi giáo trình mới xuống tệp rồi nạp lại vào ứng dụng.

        Raises:
            LoiDuLieu: khi không ghi được tệp; màn hình gọi sẽ báo cho người dùng.
        """
        self._kho.luu_giao_trinh(giao_trinh)
        self.giao_trinh = giao_trinh

    def tai_lai_giao_trinh(self) -> None:
        """Đọc lại nội dung học từ đĩa, bỏ qua nếu tệp vừa bị hỏng."""
        try:
            self.giao_trinh = self._kho.tai_giao_trinh()
        except LoiDuLieu:
            _log.exception("Không nạp lại được giáo trình")

    def _khi_dong_cua_so(self) -> None:
        """Lưu lần cuối rồi mới đóng, tránh mất tiến độ vừa đạt được."""
        try:
            self.luu_tien_do()
        except Exception:  # pragma: no cover - không để lỗi chặn việc thoát
            _log.exception("Không lưu được tiến độ khi đóng ứng dụng")
        self.am_thanh.dong()
        self.destroy()
