"""Mô hình miền (domain models) của ứng dụng học tiếng Anh.

Toàn bộ các lớp ở đây là bất biến (immutable) và không phụ thuộc vào giao diện,
nhờ vậy có thể kiểm thử độc lập, không cần khởi tạo cửa sổ Tk.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterator, Self, Sequence

__all__ = [
    "SO_TU_MOI_BAI",
    "MauDonVi",
    "TuVung",
    "BaiHoc",
    "DonVi",
    "GiaoTrinh",
    "chuan_hoa",
]


SO_TU_MOI_BAI = 5
"""Số từ vựng tối đa của một bài học khi cắt nhỏ một đơn vị."""


class MauDonVi(StrEnum):
    """Nhóm màu Duolingo dùng cho từng đơn vị bài học."""

    XANH_LA = "xanh_la"
    XANH_DUONG = "xanh_duong"
    TIM = "tim"
    CAM = "cam"
    HONG = "hong"
    VANG = "vang"

    @classmethod
    def tu_chuoi(cls, gia_tri: str) -> MauDonVi:
        """Trả về màu tương ứng, mặc định XANH_LA nếu dữ liệu không hợp lệ."""
        try:
            return cls(gia_tri)
        except ValueError:
            return cls.XANH_LA


def chuan_hoa(van_ban: str) -> str:
    """Chuẩn hoá chuỗi để so khớp đáp án người dùng gõ vào.

    Bỏ dấu tiếng Việt, hạ chữ thường, gộp khoảng trắng và loại bỏ dấu câu ở
    hai đầu. Nhờ vậy "Xin chào!", "xin chao" và " Xin  Chào " là như nhau.
    """
    khong_dau = "".join(
        ky_tu
        for ky_tu in unicodedata.normalize("NFD", van_ban)
        if unicodedata.category(ky_tu) != "Mn"
    )
    return " ".join(khong_dau.casefold().strip(" .,!?;:\"'").split())


@dataclass(frozen=True, slots=True)
class TuVung:
    """Một cặp từ Anh - Việt, kèm phiên âm và câu ví dụ."""

    en: str
    vi: str
    phien_am: str = ""
    vi_du: str = ""
    """Câu ví dụ tiếng Anh chứa từ này."""

    vi_du_dich: str = ""
    """Nghĩa tiếng Việt của câu ví dụ."""

    @property
    def co_vi_du(self) -> bool:
        return bool(self.vi_du.strip())

    def __post_init__(self) -> None:
        if not self.en.strip() or not self.vi.strip():
            raise ValueError(f"Từ vựng thiếu nội dung: en={self.en!r} vi={self.vi!r}")

    @property
    def ma(self) -> str:
        """Khoá định danh ổn định, dùng làm key khi lưu tiến độ."""
        return chuan_hoa(self.en)

    def khop_dap_an(self, tra_loi: str) -> bool:
        """Kiểm tra câu trả lời gõ tay có khớp với từ tiếng Anh hay không."""
        return chuan_hoa(tra_loi) == chuan_hoa(self.en)


@dataclass(frozen=True, slots=True)
class BaiHoc:
    """Một bài học nhỏ, gồm vài từ vựng được luyện trong cùng một phiên."""

    ma: str
    ten: str
    tu_vung: tuple[TuVung, ...]

    def __post_init__(self) -> None:
        if not self.tu_vung:
            raise ValueError(f"Bài học {self.ma!r} không có từ vựng nào")

    def __len__(self) -> int:
        return len(self.tu_vung)

    def __iter__(self) -> Iterator[TuVung]:
        return iter(self.tu_vung)


@dataclass(frozen=True, slots=True)
class DonVi:
    """Một chủ đề lớn (Unit), chứa nhiều bài học nối tiếp nhau."""

    ma: str
    ten: str
    mo_ta: str
    mau: MauDonVi
    bieu_tuong: str
    bai_hoc: tuple[BaiHoc, ...]
    lop: int | None = None
    """Lớp trong chương trình phổ thông, None nghĩa là không gắn với lớp nào."""

    unit: str = ""
    """Tên bài trong sách giáo khoa, ví dụ "Unit 1"."""

    @property
    def nhan_sgk(self) -> str:
        """Nhãn ngắn kiểu "Lớp 6 · Unit 1", rỗng nếu chưa gắn gì."""
        phan = []
        if self.lop is not None:
            phan.append(f"Lớp {self.lop}")
        if self.unit:
            phan.append(self.unit)
        return " · ".join(phan)

    def __post_init__(self) -> None:
        if not self.bai_hoc:
            raise ValueError(f"Đơn vị {self.ma!r} không có bài học nào")

    @property
    def tat_ca_tu_vung(self) -> tuple[TuVung, ...]:
        return tuple(tu for bai in self.bai_hoc for tu in bai)

    @classmethod
    def tu_danh_sach_tu(
        cls,
        *,
        ma: str,
        ten: str,
        mo_ta: str,
        mau: MauDonVi,
        bieu_tuong: str,
        tu_vung: Sequence[TuVung],
        lop: int | None = None,
        unit: str = "",
    ) -> Self:
        """Dựng một đơn vị từ danh sách từ phẳng, tự cắt thành các bài nhỏ.

        Dùng chung cho lúc nạp tệp và lúc người dùng sửa từ vựng trong ứng dụng,
        để hai đường đi luôn cắt bài giống hệt nhau.
        """
        cac_bai = tuple(
            BaiHoc(
                ma=f"{ma}-{thu_tu}",
                ten=f"Bài {thu_tu}",
                tu_vung=tuple(tu_vung[dau : dau + SO_TU_MOI_BAI]),
            )
            for thu_tu, dau in enumerate(
                range(0, len(tu_vung), SO_TU_MOI_BAI), start=1
            )
        )
        return cls(
            ma=ma,
            ten=ten,
            mo_ta=mo_ta,
            mau=mau,
            bieu_tuong=bieu_tuong,
            bai_hoc=cac_bai,
            lop=lop,
            unit=unit,
        )


@dataclass(frozen=True, slots=True)
class GiaoTrinh:
    """Toàn bộ nội dung học: danh sách các đơn vị theo thứ tự."""

    don_vi: tuple[DonVi, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        ma_da_thay: set[str] = set()
        for bai in self.tat_ca_bai_hoc:
            if bai.ma in ma_da_thay:
                raise ValueError(f"Mã bài học bị trùng: {bai.ma!r}")
            ma_da_thay.add(bai.ma)

    @property
    def tat_ca_bai_hoc(self) -> tuple[BaiHoc, ...]:
        return tuple(bai for dv in self.don_vi for bai in dv.bai_hoc)

    @property
    def tat_ca_tu_vung(self) -> tuple[TuVung, ...]:
        return tuple(tu for dv in self.don_vi for tu in dv.tat_ca_tu_vung)

    @property
    def cac_lop(self) -> tuple[int, ...]:
        """Các lớp có nội dung từ vựng, đã sắp xếp tăng dần."""
        return tuple(
            sorted({dv.lop for dv in self.don_vi if dv.lop is not None})
        )

    def tim_bai_hoc(self, ma: str) -> BaiHoc | None:
        return next((bai for bai in self.tat_ca_bai_hoc if bai.ma == ma), None)

    def don_vi_chua(self, ma_bai: str) -> DonVi | None:
        return next(
            (dv for dv in self.don_vi if any(bai.ma == ma_bai for bai in dv.bai_hoc)),
            None,
        )

    def thu_tu_bai_hoc(self, ma: str) -> int:
        """Vị trí của bài học trong toàn giáo trình, -1 nếu không tìm thấy."""
        for chi_so, bai in enumerate(self.tat_ca_bai_hoc):
            if bai.ma == ma:
                return chi_so
        return -1

    def bai_ke_tiep(self, ma: str) -> BaiHoc | None:
        chi_so = self.thu_tu_bai_hoc(ma)
        danh_sach = self.tat_ca_bai_hoc
        if chi_so < 0 or chi_so + 1 >= len(danh_sach):
            return None
        return danh_sach[chi_so + 1]

    @classmethod
    def rong(cls) -> Self:
        return cls(don_vi=())
