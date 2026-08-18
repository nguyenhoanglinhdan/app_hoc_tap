"""Tiến độ học tập: XP, cấp độ, chuỗi ngày và các bài đã hoàn thành.

Đây là logic thuần, không đụng tới tệp tin. Việc đọc ghi do
:mod:`hoc_tieng_anh.kho_du_lieu` đảm nhiệm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Mapping, Self

from .on_tap import TrangThaiTu

__all__ = ["TienDo", "XP_MOI_CAP"]

XP_MOI_CAP = 100
"""Số XP cần thiết để lên một cấp."""


@dataclass(slots=True)
class TienDo:
    """Trạng thái học tập tích luỹ của người dùng."""

    xp: int = 0
    chuoi_ngay: int = 0
    ngay_hoc_cuoi: date | None = None
    so_lan_hoan_thanh: dict[str, int] = field(default_factory=dict)
    trang_thai_tu: dict[str, TrangThaiTu] = field(default_factory=dict)
    """Lịch ôn tập của từng từ, khoá là ``TuVung.ma``."""

    # ------------------------------------------------------------------ #
    # Truy vấn
    # ------------------------------------------------------------------ #

    @property
    def cap_do(self) -> int:
        """Cấp độ hiện tại, bắt đầu từ 1."""
        return self.xp // XP_MOI_CAP + 1

    @property
    def xp_trong_cap(self) -> int:
        """Số XP đã tích được trong cấp hiện tại."""
        return self.xp % XP_MOI_CAP

    @property
    def ty_le_len_cap(self) -> float:
        """Tỷ lệ 0.0 - 1.0 để vẽ thanh tiến độ lên cấp."""
        return self.xp_trong_cap / XP_MOI_CAP

    @property
    def so_bai_da_xong(self) -> int:
        return len(self.so_lan_hoan_thanh)

    @property
    def so_tu_da_gap(self) -> int:
        return len(self.trang_thai_tu)

    def da_hoan_thanh(self, ma_bai: str) -> bool:
        return ma_bai in self.so_lan_hoan_thanh

    def da_hoc_hom_nay(self, hom_nay: date | None = None) -> bool:
        return self.ngay_hoc_cuoi == (hom_nay or date.today())

    # ------------------------------------------------------------------ #
    # Cập nhật
    # ------------------------------------------------------------------ #

    def ghi_nhan_hoan_thanh(
        self, ma_bai: str, xp_nhan: int, hom_nay: date | None = None
    ) -> None:
        """Ghi nhận việc hoàn thành một bài học.

        Cộng XP, tăng số lần hoàn thành của bài và cập nhật chuỗi ngày học.
        """
        self.so_lan_hoan_thanh[ma_bai] = self.so_lan_hoan_thanh.get(ma_bai, 0) + 1
        self.ghi_nhan_luyen_tap(xp_nhan, hom_nay)

    def ghi_nhan_luyen_tap(self, xp_nhan: int, hom_nay: date | None = None) -> None:
        """Cộng XP và cập nhật chuỗi ngày mà không đánh dấu bài học nào hoàn thành.

        Dùng cho buổi luyện tập tổng hợp: người học vẫn được ghi công, nhưng lộ
        trình chính không bị đánh dấu sai.
        """
        if xp_nhan < 0:
            raise ValueError("XP nhận được không thể âm")
        self.xp += xp_nhan
        self._cap_nhat_chuoi_ngay(hom_nay or date.today())

    def dat_lai(self) -> None:
        """Xoá sạch tiến độ, đưa người học về vạch xuất phát."""
        self.xp = 0
        self.chuoi_ngay = 0
        self.ngay_hoc_cuoi = None
        self.so_lan_hoan_thanh.clear()
        self.trang_thai_tu.clear()

    def ghi_nhan_tra_loi(
        self, ma_tu: str, dung: bool, hom_nay: date | None = None
    ) -> TrangThaiTu:
        """Ghi nhận một lần trả lời cho một từ và cập nhật lịch ôn của nó.

        Gọi ngay khi người học trả lời, không chờ hết bài: dù phiên học có thất
        bại thì công sức với từng từ vẫn được giữ lại.
        """
        trang_thai = self.trang_thai_tu.get(ma_tu)
        if trang_thai is None:
            trang_thai = TrangThaiTu(ma=ma_tu)
            self.trang_thai_tu[ma_tu] = trang_thai
        trang_thai.ghi_nhan(dung, hom_nay)
        return trang_thai

    def _cap_nhat_chuoi_ngay(self, hom_nay: date) -> None:
        """Chuỗi ngày tăng khi học liên tiếp, giữ nguyên nếu học lại trong ngày."""
        match self.ngay_hoc_cuoi:
            case None:
                self.chuoi_ngay = 1
            case ngay_cuoi if ngay_cuoi == hom_nay:
                pass
            case ngay_cuoi if ngay_cuoi == hom_nay - timedelta(days=1):
                self.chuoi_ngay += 1
            case _:
                self.chuoi_ngay = 1
        self.ngay_hoc_cuoi = hom_nay

    def chuoi_ngay_thuc_te(self, hom_nay: date | None = None) -> int:
        """Chuỗi ngày còn hiệu lực tính đến ``hom_nay``.

        Chuỗi được coi là đã đứt nếu buổi học gần nhất cách đây hơn một ngày.
        """
        hom_nay = hom_nay or date.today()
        if self.ngay_hoc_cuoi is None:
            return 0
        if hom_nay - self.ngay_hoc_cuoi > timedelta(days=1):
            return 0
        return self.chuoi_ngay

    # ------------------------------------------------------------------ #
    # Chuyển đổi JSON
    # ------------------------------------------------------------------ #

    def sang_dict(self) -> dict[str, Any]:
        return {
            "xp": self.xp,
            "chuoi_ngay": self.chuoi_ngay,
            "ngay_hoc_cuoi": self.ngay_hoc_cuoi.isoformat() if self.ngay_hoc_cuoi else None,
            "so_lan_hoan_thanh": dict(self.so_lan_hoan_thanh),
            "trang_thai_tu": {
                ma: trang_thai.sang_dict()
                for ma, trang_thai in self.trang_thai_tu.items()
            },
        }

    @classmethod
    def tu_dict(cls, du_lieu: Mapping[str, Any]) -> Self:
        """Dựng lại tiến độ từ JSON, bỏ qua các trường hỏng thay vì vỡ ứng dụng."""
        ngay_tho = du_lieu.get("ngay_hoc_cuoi")
        try:
            ngay_hoc_cuoi = date.fromisoformat(ngay_tho) if ngay_tho else None
        except (TypeError, ValueError):
            ngay_hoc_cuoi = None

        so_lan = du_lieu.get("so_lan_hoan_thanh") or {}
        if not isinstance(so_lan, Mapping):
            so_lan = {}

        tu_tho = du_lieu.get("trang_thai_tu") or {}
        if not isinstance(tu_tho, Mapping):
            tu_tho = {}
        trang_thai_tu = {
            str(ma): TrangThaiTu.tu_dict(str(ma), gia_tri)
            for ma, gia_tri in tu_tho.items()
            if isinstance(gia_tri, Mapping)
        }

        return cls(
            xp=max(0, _so_nguyen(du_lieu.get("xp"))),
            chuoi_ngay=max(0, _so_nguyen(du_lieu.get("chuoi_ngay"))),
            ngay_hoc_cuoi=ngay_hoc_cuoi,
            so_lan_hoan_thanh={
                str(ma): _so_nguyen(lan) for ma, lan in so_lan.items()
            },
            trang_thai_tu=trang_thai_tu,
        )


def _so_nguyen(gia_tri: Any, mac_dinh: int = 0) -> int:
    """Ép kiểu số nguyên an toàn cho dữ liệu đọc từ tệp JSON."""
    try:
        return int(gia_tri)
    except (TypeError, ValueError):
        return mac_dinh
