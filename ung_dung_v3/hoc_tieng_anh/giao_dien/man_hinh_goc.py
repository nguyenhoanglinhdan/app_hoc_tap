"""Lớp nền cho mọi màn hình và giao ước điều hướng giữa chúng."""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

import customtkinter as ctk

from ..am_thanh import DichVuAmThanh
from ..mo_hinh import BaiHoc, GiaoTrinh, TuVung
from ..ngu_phap import BoNguPhap, ChuDiemNguPhap
from ..tien_do import TienDo
from .chu_de import Mau

__all__ = ["DieuHuong", "ManHinh"]


@runtime_checkable
class DieuHuong(Protocol):
    """Những gì một màn hình được phép yêu cầu ở ứng dụng chủ.

    Nhờ giao ước này, các màn hình không phụ thuộc trực tiếp vào lớp
    :class:`~hoc_tieng_anh.giao_dien.ung_dung.UngDung`, nên có thể thay thế hoặc
    kiểm thử bằng một đối tượng giả.
    """

    giao_trinh: GiaoTrinh
    ngu_phap: BoNguPhap
    tien_do: TienDo
    am_thanh: DichVuAmThanh

    def mo_trang_chu(self) -> None: ...

    def mo_bai_hoc(self, bai_hoc: BaiHoc) -> None: ...

    def mo_tu_vung(self) -> None: ...

    def mo_ho_so(self) -> None: ...

    def mo_luyen_tap(self) -> None: ...

    def mo_soan_tu(self) -> None: ...

    def mo_ngu_phap(self) -> None: ...

    def mo_chu_diem_ngu_phap(self, chu_diem: ChuDiemNguPhap) -> None: ...

    def mo_kiem_tra(self) -> None: ...

    def mo_buoi_luyen(self, cac_tu: "Sequence[TuVung]") -> None: ...

    def tai_lai_giao_trinh(self) -> None: ...

    def luu_tien_do(self) -> None: ...


class ManHinh(ctk.CTkFrame):
    """Khung nền chung của các màn hình.

    Lớp con chỉ cần cài đặt :meth:`dung_giao_dien`; phần khởi tạo khung, màu nền
    và tham chiếu điều hướng đã được lo sẵn.
    """

    an_thanh_ben: bool = False
    """Đặt True nếu màn hình muốn chiếm trọn cửa sổ, ví dụ khi đang làm bài."""

    def __init__(self, master: ctk.CTkBaseClass, ung_dung: DieuHuong) -> None:
        super().__init__(master, fg_color=Mau.NEN, corner_radius=0)
        self.ung_dung = ung_dung
        self.dung_giao_dien()

    def dung_giao_dien(self) -> None:
        """Dựng nội dung màn hình. Lớp con bắt buộc cài đặt."""
        raise NotImplementedError
