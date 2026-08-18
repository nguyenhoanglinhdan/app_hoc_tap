"""Hệ thống thiết kế: bảng màu, phông chữ và các hằng số bố cục.

Mọi giá trị hiển thị đều tập trung tại đây, các màn hình chỉ tham chiếu chứ
không tự đặt mã màu. Màu được khai báo dạng cặp ``(sáng, tối)`` theo quy ước của
CustomTkinter nên ứng dụng tự đổi giao diện theo chế độ sáng/tối.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Final

from ..mo_hinh import MauDonVi

__all__ = ["Mau", "BoMau", "MAU_THEO_DON_VI", "phong", "KichThuoc"]

CapMau = tuple[str, str]
"""Cặp màu (chế độ sáng, chế độ tối)."""


class Mau:
    """Bảng màu lấy cảm hứng từ Duolingo."""

    # Nền và khung
    NEN: Final[CapMau] = ("#FFFFFF", "#131F24")
    NEN_PHU: Final[CapMau] = ("#F7F7F7", "#1B2B32")
    NEN_THE: Final[CapMau] = ("#FFFFFF", "#202F36")
    VIEN: Final[CapMau] = ("#E5E5E5", "#37464F")

    # Chữ
    CHU: Final[CapMau] = ("#3C3C3C", "#F1F7FB")
    CHU_PHU: Final[CapMau] = ("#777777", "#8FA3AD")
    CHU_MO: Final[CapMau] = ("#AFAFAF", "#52656D")
    CHU_TREN_NEN_DAM: Final[CapMau] = ("#FFFFFF", "#FFFFFF")
    CHU_NHAN_MANH: Final[CapMau] = ("#4CA700", "#58CC02")
    """Chữ xanh lá dùng để nhấn mạnh; sáng lên ở chế độ tối cho dễ đọc."""

    # Màu thương hiệu
    XANH_LA: Final[CapMau] = ("#58CC02", "#58CC02")
    XANH_LA_DAM: Final[CapMau] = ("#4CA700", "#3E8C00")
    XANH_LA_NHAT: Final[CapMau] = ("#D7FFB8", "#202F36")

    XANH_DUONG: Final[CapMau] = ("#1CB0F6", "#1CB0F6")
    XANH_DUONG_DAM: Final[CapMau] = ("#1899D6", "#1476A5")
    XANH_DUONG_NHAT: Final[CapMau] = ("#DDF4FF", "#202F36")

    DO: Final[CapMau] = ("#FF4B4B", "#FF4B4B")
    DO_DAM: Final[CapMau] = ("#EA2B2B", "#C42020")
    DO_NHAT: Final[CapMau] = ("#FFDFE0", "#3B2226")

    VANG: Final[CapMau] = ("#FFC800", "#FFC800")
    VANG_DAM: Final[CapMau] = ("#E5B200", "#C29700")

    CAM: Final[CapMau] = ("#FF9600", "#FF9600")
    CAM_DAM: Final[CapMau] = ("#E58600", "#C27200")

    TIM: Final[CapMau] = ("#CE82FF", "#CE82FF")
    TIM_DAM: Final[CapMau] = ("#B45DF5", "#9A45D9")

    HONG: Final[CapMau] = ("#FF86D0", "#FF86D0")
    HONG_DAM: Final[CapMau] = ("#E5609F", "#C24A85")

    # Trạng thái khoá / vô hiệu
    XAM: Final[CapMau] = ("#E5E5E5", "#37464F")
    XAM_DAM: Final[CapMau] = ("#CFCFCF", "#2B3A42")


@dataclass(frozen=True, slots=True)
class BoMau:
    """Ba sắc độ của một màu: mặt trên, phần bóng dưới và nền nhạt."""

    chinh: CapMau
    dam: CapMau
    nhat: CapMau


MAU_THEO_DON_VI: Final[dict[MauDonVi, BoMau]] = {
    MauDonVi.XANH_LA: BoMau(Mau.XANH_LA, Mau.XANH_LA_DAM, Mau.XANH_LA_NHAT),
    MauDonVi.XANH_DUONG: BoMau(Mau.XANH_DUONG, Mau.XANH_DUONG_DAM, Mau.XANH_DUONG_NHAT),
    MauDonVi.TIM: BoMau(Mau.TIM, Mau.TIM_DAM, Mau.NEN_PHU),
    MauDonVi.CAM: BoMau(Mau.CAM, Mau.CAM_DAM, Mau.NEN_PHU),
    MauDonVi.HONG: BoMau(Mau.HONG, Mau.HONG_DAM, Mau.NEN_PHU),
    MauDonVi.VANG: BoMau(Mau.VANG, Mau.VANG_DAM, Mau.NEN_PHU),
}
"""Bộ màu tương ứng cho từng nhóm màu của đơn vị bài học."""


class KichThuoc:
    """Hằng số bố cục dùng chung."""

    CUA_SO_RONG: Final[int] = 980
    CUA_SO_CAO: Final[int] = 700
    CUA_SO_RONG_TOI_THIEU: Final[int] = 880
    CUA_SO_CAO_TOI_THIEU: Final[int] = 640

    BO_GOC: Final[int] = 16
    BO_GOC_NHO: Final[int] = 12
    DO_SAU_NUT: Final[int] = 4
    """Độ dày phần bóng dưới nút, tạo cảm giác nút nổi 3D."""

    LE: Final[int] = 24
    KHOANG_CACH: Final[int] = 12
    CAO_NUT: Final[int] = 50
    RONG_NOI_DUNG: Final[int] = 620
    """Bề ngang tối đa của vùng nội dung, giữ chữ không bị kéo quá dài."""


_PHONG_UU_TIEN: Final[tuple[str, ...]] = (
    "Nunito",
    "Baloo 2",
    "Quicksand",
    "Varela Round",
    "Segoe UI Variable Display",
    "Segoe UI",
    "Verdana",
)
"""Danh sách phông ưu tiên, chọn phông tròn trịa gần với Duolingo nhất."""


@lru_cache(maxsize=1)
def _ho_phong() -> str:
    """Chọn phông chữ đầu tiên có sẵn trong hệ thống.

    Chỉ gọi được sau khi cửa sổ Tk đã khởi tạo. Kết quả được nhớ lại vì việc
    liệt kê phông của hệ điều hành khá tốn thời gian.
    """
    try:
        from tkinter import font as tk_font

        co_san = {ten.lower() for ten in tk_font.families()}
    except Exception:  # pragma: no cover - chỉ xảy ra khi chưa có cửa sổ Tk
        return "Segoe UI"

    for ten in _PHONG_UU_TIEN:
        if ten.lower() in co_san:
            return ten
    return "Segoe UI"


def phong(kich_co: int = 15, *, dam: bool = True) -> tuple[str, int, str]:
    """Trả về bộ mô tả phông chữ cho widget Tk.

    Args:
        kich_co: cỡ chữ tính theo điểm.
        dam: dùng kiểu đậm hay không. Duolingo dùng chữ đậm gần như ở mọi nơi.
    """
    return (_ho_phong(), kich_co, "bold" if dam else "normal")
