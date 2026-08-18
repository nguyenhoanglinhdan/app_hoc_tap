"""Mô hình miền cho phần ngữ pháp.

Khác với từ vựng, một mục ngữ pháp không gắn với từ đơn lẻ nào mà gắn với một
chủ điểm (thì hiện tại đơn, so sánh hơn...). Module thuần logic, không import
tkinter và không đọc ghi tệp.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Iterator, Self

from .mo_hinh import MauDonVi

__all__ = [
    "DangNguPhap",
    "CauNguPhap",
    "ChuDiemNguPhap",
    "BoNguPhap",
    "LOP_CAP_HAI",
]

LOP_CAP_HAI: tuple[int, ...] = (6, 7, 8, 9)
"""Các lớp của bậc trung học cơ sở."""


class DangNguPhap(StrEnum):
    """Các dạng bài tập ngữ pháp."""

    DIEN_CHO_TRONG = auto()
    """Điền từ còn thiếu vào chỗ trống."""

    SAP_XEP_CAU = auto()
    """Bấm các mảnh chữ theo đúng thứ tự để tạo thành câu."""

    CHON_DANG_DUNG = auto()
    """Chọn dạng đúng trong bốn phương án."""

    @classmethod
    def tu_chuoi(cls, gia_tri: str) -> DangNguPhap:
        try:
            return cls(gia_tri)
        except ValueError:
            return cls.CHON_DANG_DUNG


@dataclass(frozen=True, slots=True)
class CauNguPhap:
    """Một câu hỏi ngữ pháp."""

    ma: str
    dang: DangNguPhap
    de_bai: str
    cau: str
    """Đề bài hiển thị: câu có chỗ trống, hoặc câu tiếng Việt cần dịch."""

    dap_an: str
    lua_chon: tuple[str, ...] = ()
    cac_manh: tuple[str, ...] = ()
    """Mảnh chữ của bài sắp xếp; bỏ trống thì tự tách theo khoảng trắng."""

    giai_thich: str = ""
    dich: str = ""
    """Nghĩa tiếng Việt của câu đáp án, hiện ra sau khi trả lời."""

    def __post_init__(self) -> None:
        if not self.dap_an.strip():
            raise ValueError(f"Câu ngữ pháp {self.ma!r} thiếu đáp án")
        if self.dang is DangNguPhap.CHON_DANG_DUNG:
            if self.dap_an not in self.lua_chon:
                raise ValueError(
                    f"Câu {self.ma!r}: đáp án không nằm trong các lựa chọn"
                )
            if len(set(self.lua_chon)) != len(self.lua_chon):
                raise ValueError(f"Câu {self.ma!r}: các lựa chọn bị trùng nhau")

    @property
    def manh_chu(self) -> tuple[str, ...]:
        """Các mảnh chữ để người học bấm ghép thành câu."""
        return self.cac_manh or tuple(self.dap_an.split())


@dataclass(frozen=True, slots=True)
class ChuDiemNguPhap:
    """Một chủ điểm ngữ pháp, ví dụ "Thì hiện tại đơn"."""

    ma: str
    ten: str
    mo_ta: str
    lop: int
    mau: MauDonVi
    bieu_tuong: str
    cau_hoi: tuple[CauNguPhap, ...]

    def __post_init__(self) -> None:
        if not self.cau_hoi:
            raise ValueError(f"Chủ điểm {self.ma!r} không có câu hỏi nào")

    def __len__(self) -> int:
        return len(self.cau_hoi)

    def __iter__(self) -> Iterator[CauNguPhap]:
        return iter(self.cau_hoi)


@dataclass(frozen=True, slots=True)
class BoNguPhap:
    """Toàn bộ nội dung ngữ pháp."""

    chu_diem: tuple[ChuDiemNguPhap, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        da_thay: set[str] = set()
        for chu_diem in self.chu_diem:
            if chu_diem.ma in da_thay:
                raise ValueError(f"Mã chủ điểm bị trùng: {chu_diem.ma!r}")
            da_thay.add(chu_diem.ma)

    def __bool__(self) -> bool:
        return bool(self.chu_diem)

    @property
    def cac_lop(self) -> tuple[int, ...]:
        """Các lớp thực sự có nội dung, đã sắp xếp tăng dần."""
        return tuple(sorted({chu_diem.lop for chu_diem in self.chu_diem}))

    @property
    def tong_so_cau(self) -> int:
        return sum(len(chu_diem) for chu_diem in self.chu_diem)

    def theo_lop(self, lop: int | None) -> tuple[ChuDiemNguPhap, ...]:
        """Lọc chủ điểm theo lớp; ``None`` nghĩa là lấy tất cả."""
        if lop is None:
            return self.chu_diem
        return tuple(cd for cd in self.chu_diem if cd.lop == lop)

    def tim(self, ma: str) -> ChuDiemNguPhap | None:
        return next((cd for cd in self.chu_diem if cd.ma == ma), None)

    @classmethod
    def rong(cls) -> Self:
        return cls(chu_diem=())
