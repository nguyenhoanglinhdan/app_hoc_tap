"""Ôn tập lặp ngắt quãng (spaced repetition) theo từng từ.

Dùng bản rút gọn của thuật toán SM-2: mỗi từ giữ một khoảng cách ôn tập và một
hệ số dễ. Trả lời đúng thì khoảng cách giãn ra theo hệ số dễ; trả lời sai thì
khoảng cách về 0 và hệ số dễ giảm, nên từ đó quay lại sớm hơn.

Module thuần logic, không import tkinter và không đọc ghi tệp.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum, auto
from typing import Any, Mapping, Self

from .mo_hinh import GiaoTrinh, TuVung

__all__ = [
    "MucThuoc",
    "TrangThaiTu",
    "LichOnTap",
    "DE_DANG_DAU",
    "DE_DANG_TOI_THIEU",
    "DE_DANG_TOI_DA",
    "KHOANG_CACH_TOI_DA",
]

DE_DANG_DAU = 2.5
"""Hệ số dễ ban đầu của một từ mới."""

DE_DANG_TOI_THIEU = 1.3
"""Sàn của hệ số dễ, tránh để từ khó bị hỏi lại liên tục tới mức nản."""

DE_DANG_TOI_DA = 2.8
"""Trần của hệ số dễ, tránh giãn khoảng cách quá nhanh."""

_THUONG_DE_DANG = 0.1
_PHAT_DE_DANG = 0.2

_KHOANG_CACH_DAU = 1
"""Số ngày chờ sau lần trả lời đúng đầu tiên."""

_KHOANG_CACH_HAI = 3
"""Số ngày chờ sau lần trả lời đúng thứ hai."""

KHOANG_CACH_TOI_DA = 365
"""Trần khoảng cách ôn tập, tính theo ngày.

Không có trần thì khoảng cách nhân dồn theo cấp số nhân và ``date`` sẽ tràn số
sau vài chục lần trả lời đúng. Một năm cũng là mốc hợp lý: quá mốc đó thì coi
như đã thuộc hẳn.
"""


class MucThuoc(StrEnum):
    """Mức độ thuộc của một từ, dùng để hiển thị cho người học."""

    MOI = auto()
    DANG_HOC = auto()
    QUEN_THUOC = auto()
    THUOC_LONG = auto()

    @property
    def nhan(self) -> str:
        return {
            MucThuoc.MOI: "Từ mới",
            MucThuoc.DANG_HOC: "Đang học",
            MucThuoc.QUEN_THUOC: "Quen thuộc",
            MucThuoc.THUOC_LONG: "Thuộc lòng",
        }[self]


@dataclass(slots=True)
class TrangThaiTu:
    """Lịch sử ôn tập của một từ."""

    ma: str
    dung_lien_tiep: int = 0
    khoang_cach: int = 0
    de_dang: float = DE_DANG_DAU
    ngay_on_ke_tiep: date | None = None
    tong_dung: int = 0
    tong_sai: int = 0

    # ------------------------------------------------------------------ #
    # Truy vấn
    # ------------------------------------------------------------------ #

    @property
    def tong_lan(self) -> int:
        return self.tong_dung + self.tong_sai

    @property
    def ty_le_dung(self) -> float:
        """Tỷ lệ trả lời đúng, 0.0 nếu chưa gặp lần nào."""
        return self.tong_dung / self.tong_lan if self.tong_lan else 0.0

    @property
    def muc_thuoc(self) -> MucThuoc:
        if self.tong_lan == 0:
            return MucThuoc.MOI
        if self.dung_lien_tiep >= 5:
            return MucThuoc.THUOC_LONG
        if self.dung_lien_tiep >= 3:
            return MucThuoc.QUEN_THUOC
        return MucThuoc.DANG_HOC

    def den_han(self, hom_nay: date | None = None) -> bool:
        """Từ đã tới hạn ôn lại hay chưa."""
        if self.ngay_on_ke_tiep is None:
            return True
        return self.ngay_on_ke_tiep <= (hom_nay or date.today())

    def so_ngay_cho(self, hom_nay: date | None = None) -> int:
        """Số ngày còn lại tới lần ôn kế tiếp, 0 nếu đã tới hạn."""
        if self.ngay_on_ke_tiep is None:
            return 0
        return max(0, (self.ngay_on_ke_tiep - (hom_nay or date.today())).days)

    # ------------------------------------------------------------------ #
    # Cập nhật
    # ------------------------------------------------------------------ #

    def ghi_nhan(self, dung: bool, hom_nay: date | None = None) -> None:
        """Cập nhật lịch ôn sau một lần trả lời."""
        hom_nay = hom_nay or date.today()
        if dung:
            self._ghi_nhan_dung()
        else:
            self._ghi_nhan_sai()
        self.ngay_on_ke_tiep = hom_nay + timedelta(days=self.khoang_cach)

    def _ghi_nhan_dung(self) -> None:
        self.tong_dung += 1
        self.dung_lien_tiep += 1
        match self.dung_lien_tiep:
            case 1:
                self.khoang_cach = _KHOANG_CACH_DAU
            case 2:
                self.khoang_cach = _KHOANG_CACH_HAI
            case _:
                self.khoang_cach = min(
                    KHOANG_CACH_TOI_DA,
                    max(_KHOANG_CACH_HAI, round(self.khoang_cach * self.de_dang)),
                )
        self.de_dang = min(DE_DANG_TOI_DA, self.de_dang + _THUONG_DE_DANG)

    def _ghi_nhan_sai(self) -> None:
        self.tong_sai += 1
        self.dung_lien_tiep = 0
        self.khoang_cach = 0
        self.de_dang = max(DE_DANG_TOI_THIEU, self.de_dang - _PHAT_DE_DANG)

    # ------------------------------------------------------------------ #
    # Chuyển đổi JSON
    # ------------------------------------------------------------------ #

    def sang_dict(self) -> dict[str, Any]:
        return {
            "dung_lien_tiep": self.dung_lien_tiep,
            "khoang_cach": self.khoang_cach,
            "de_dang": round(self.de_dang, 3),
            "ngay_on_ke_tiep": (
                self.ngay_on_ke_tiep.isoformat() if self.ngay_on_ke_tiep else None
            ),
            "tong_dung": self.tong_dung,
            "tong_sai": self.tong_sai,
        }

    @classmethod
    def tu_dict(cls, ma: str, du_lieu: Mapping[str, Any]) -> Self:
        """Dựng lại từ JSON, bỏ qua trường hỏng thay vì làm vỡ ứng dụng."""
        ngay_tho = du_lieu.get("ngay_on_ke_tiep")
        try:
            ngay = date.fromisoformat(ngay_tho) if ngay_tho else None
        except (TypeError, ValueError):
            ngay = None

        return cls(
            ma=ma,
            dung_lien_tiep=max(0, _so_nguyen(du_lieu.get("dung_lien_tiep"))),
            khoang_cach=min(
                KHOANG_CACH_TOI_DA, max(0, _so_nguyen(du_lieu.get("khoang_cach")))
            ),
            de_dang=_so_thuc(du_lieu.get("de_dang"), DE_DANG_DAU),
            ngay_on_ke_tiep=ngay,
            tong_dung=max(0, _so_nguyen(du_lieu.get("tong_dung"))),
            tong_sai=max(0, _so_nguyen(du_lieu.get("tong_sai"))),
        )


class LichOnTap:
    """Chọn từ để đưa vào các buổi luyện tập.

    Chỉ xét những từ người học đã từng gặp; từ chưa gặp thuộc về lộ trình chính
    chứ không thuộc phần ôn tập.
    """

    def __init__(
        self,
        giao_trinh: GiaoTrinh,
        trang_thai: Mapping[str, TrangThaiTu],
    ) -> None:
        self._giao_trinh = giao_trinh
        self._trang_thai = trang_thai

    # ------------------------------------------------------------------ #

    @property
    def tu_da_gap(self) -> tuple[TuVung, ...]:
        """Những từ đã xuất hiện ít nhất một lần trong bài học."""
        return tuple(
            tu
            for tu in self._giao_trinh.tat_ca_tu_vung
            if tu.ma in self._trang_thai
        )

    def den_han(self, hom_nay: date | None = None) -> tuple[TuVung, ...]:
        """Từ tới hạn ôn, sắp xếp theo mức độ quá hạn giảm dần."""
        hom_nay = hom_nay or date.today()
        den_han = [
            tu
            for tu in self.tu_da_gap
            if self._trang_thai[tu.ma].den_han(hom_nay)
        ]
        den_han.sort(key=lambda tu: self._trang_thai[tu.ma].so_ngay_cho(hom_nay))
        return tuple(den_han)

    def hay_sai(self, so_luong: int = 10) -> tuple[TuVung, ...]:
        """Những từ sai nhiều nhất, ưu tiên từ có tỷ lệ đúng thấp."""
        co_sai = [tu for tu in self.tu_da_gap if self._trang_thai[tu.ma].tong_sai > 0]
        co_sai.sort(
            key=lambda tu: (
                self._trang_thai[tu.ma].ty_le_dung,
                -self._trang_thai[tu.ma].tong_sai,
            )
        )
        return tuple(co_sai[:so_luong])

    def yeu_nhat(self, so_luong: int = 10) -> tuple[TuVung, ...]:
        """Từ có mức thuộc thấp nhất, dùng khi chưa có từ nào tới hạn."""
        theo_thu_tu = sorted(
            self.tu_da_gap,
            key=lambda tu: (
                self._trang_thai[tu.ma].dung_lien_tiep,
                self._trang_thai[tu.ma].ty_le_dung,
            ),
        )
        return tuple(theo_thu_tu[:so_luong])

    def dem_theo_muc(self) -> dict[MucThuoc, int]:
        """Đếm số từ ở mỗi mức thuộc, dùng cho phần thống kê."""
        dem = dict.fromkeys(MucThuoc, 0)
        for tu in self._giao_trinh.tat_ca_tu_vung:
            trang_thai = self._trang_thai.get(tu.ma)
            muc = trang_thai.muc_thuoc if trang_thai else MucThuoc.MOI
            dem[muc] += 1
        return dem

    def chon_cho_buoi_luyen(
        self, so_luong: int = 10, hom_nay: date | None = None
    ) -> tuple[TuVung, ...]:
        """Gom danh sách từ cho một buổi luyện tập tổng hợp.

        Ưu tiên từ tới hạn, thiếu thì bù bằng từ yếu nhất.
        """
        da_chon: list[TuVung] = list(self.den_han(hom_nay)[:so_luong])
        if len(da_chon) < so_luong:
            da_co = {tu.ma for tu in da_chon}
            for tu in self.yeu_nhat(so_luong):
                if len(da_chon) >= so_luong:
                    break
                if tu.ma not in da_co:
                    da_chon.append(tu)
        return tuple(da_chon)


def _so_nguyen(gia_tri: Any, mac_dinh: int = 0) -> int:
    try:
        return int(gia_tri)
    except (TypeError, ValueError):
        return mac_dinh


def _so_thuc(gia_tri: Any, mac_dinh: float) -> float:
    try:
        so = float(gia_tri)
    except (TypeError, ValueError):
        return mac_dinh
    return min(DE_DANG_TOI_DA, max(DE_DANG_TOI_THIEU, so))
