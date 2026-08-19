"""Tách một danh sách từ vựng dán vào thành các :class:`TuVung`.

Dùng cho tính năng nhập hàng loạt: học sinh dán nguyên danh sách từ cô giáo cho
thay vì gõ tay từng từ. Module thuần logic, không phụ thuộc giao diện.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Iterable

from .mo_hinh import TuVung, chuan_hoa

__all__ = ["DongLoi", "KetQuaTach", "tach_danh_sach", "DAU_PHAN_CACH"]

DAU_PHAN_CACH: Final[tuple[str, ...]] = ("=", "\t", ":", "|", " - ", " – ", " — ")
"""Các dấu ngăn giữa từ tiếng Anh và nghĩa tiếng Việt, xét theo thứ tự này."""

_KY_TU_MO_DAU_CHU_THICH: Final[tuple[str, ...]] = ("#", "//")

_SO_THU_TU = re.compile(r"^\s*\d+\s*[.)]\s*")
"""Đầu dòng kiểu "1." hoặc "2)" khi chép từ danh sách đánh số."""


@dataclass(frozen=True, slots=True)
class DongLoi:
    """Một dòng không tách được, kèm lý do để báo lại cho người dùng."""

    so_dong: int
    noi_dung: str
    ly_do: str


@dataclass(frozen=True, slots=True)
class KetQuaTach:
    """Kết quả của một lần tách danh sách."""

    tu_vung: tuple[TuVung, ...] = ()
    dong_loi: tuple[DongLoi, ...] = ()

    @property
    def so_tu(self) -> int:
        return len(self.tu_vung)

    @property
    def co_loi(self) -> bool:
        return bool(self.dong_loi)

    def __bool__(self) -> bool:
        return bool(self.tu_vung)


def _tach_mot_dong(dong: str) -> list[str] | None:
    """Cắt một dòng theo dấu ngăn xuất hiện sớm nhất trong dòng.

    Chọn theo vị trí chứ không theo thứ tự khai báo: dòng lẫn nhiều loại dấu như
    ``shout | hét = ví dụ`` phải cắt ở dấu người dùng gõ trước, nếu không cột
    tiếng Anh sẽ nuốt luôn cả dấu còn lại.
    """
    som_nhat: tuple[int, str] | None = None
    for dau in DAU_PHAN_CACH:
        vi_tri = dong.find(dau)
        if vi_tri != -1 and (som_nhat is None or vi_tri < som_nhat[0]):
            som_nhat = (vi_tri, dau)

    if som_nhat is None:
        return None
    return [phan.strip() for phan in dong.split(som_nhat[1])]


def tach_danh_sach(
    van_ban: str, ma_da_co: Iterable[str] = ()
) -> KetQuaTach:
    """Tách văn bản dán vào thành danh sách từ vựng.

    Mỗi dòng có dạng ``english = tiếng việt`` và có thể thêm phần thứ ba làm câu
    ví dụ. Dòng trống, dòng chú thích và số thứ tự đầu dòng đều được bỏ qua.

    Args:
        van_ban: nội dung người dùng dán vào.
        ma_da_co: các :attr:`TuVung.ma` đã có sẵn, dùng để báo trùng.

    Returns:
        Danh sách từ tách được cùng các dòng lỗi kèm lý do.
    """
    da_co = set(ma_da_co)
    tu_vung: list[TuVung] = []
    dong_loi: list[DongLoi] = []

    for so_dong, dong_goc in enumerate(van_ban.splitlines(), start=1):
        dong = _SO_THU_TU.sub("", dong_goc).strip()
        if not dong or dong.startswith(_KY_TU_MO_DAU_CHU_THICH):
            continue

        phan = _tach_mot_dong(dong)
        if phan is None:
            dong_loi.append(
                DongLoi(so_dong, dong_goc.strip(), "thiếu dấu ngăn giữa hai cột")
            )
            continue

        en, vi = phan[0], phan[1] if len(phan) > 1 else ""
        vi_du = phan[2] if len(phan) > 2 else ""

        if not en or not vi:
            dong_loi.append(
                DongLoi(so_dong, dong_goc.strip(), "thiếu từ tiếng Anh hoặc nghĩa")
            )
            continue

        ma = chuan_hoa(en)
        if ma in da_co:
            dong_loi.append(DongLoi(so_dong, dong_goc.strip(), "từ này đã có rồi"))
            continue

        da_co.add(ma)
        tu_vung.append(TuVung(en=en, vi=vi, vi_du=vi_du))

    return KetQuaTach(tu_vung=tuple(tu_vung), dong_loi=tuple(dong_loi))
