"""Sinh câu hỏi và điều khiển một phiên học.

Module này hoàn toàn thuần logic: không import tkinter, không đọc ghi tệp.
Mọi yếu tố ngẫu nhiên đều đi qua một đối tượng ``random.Random`` được tiêm vào,
nên bài kiểm thử có thể tái lập kết quả bằng cách truyền seed cố định.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum, auto
from random import Random
from typing import Sequence

from .mo_hinh import BaiHoc, TuVung, chuan_hoa
from .ngu_phap import CauNguPhap, ChuDiemNguPhap, DangNguPhap

__all__ = [
    "LoaiBaiTap",
    "CauHoi",
    "KetQuaTraLoi",
    "TrangThaiPhien",
    "TrinhTaoCauHoi",
    "TrinhTaoCauHoiNguPhap",
    "PhienHoc",
    "CheDoPhien",
    "NoiDungPhien",
    "DAP_AN_GHEP_DUNG",
    "DAP_AN_NOI_DUNG",
]

SO_LUA_CHON = 4
"""Số phương án của một câu trắc nghiệm (1 đúng + 3 nhiễu)."""

SO_CAP_GHEP_DOI = 4
"""Số cặp từ trong một câu ghép đôi."""

DAP_AN_GHEP_DUNG = "__ghep_dung__"
"""Giá trị giao diện gửi về khi người học ghép đúng toàn bộ các cặp."""

DAP_AN_NOI_DUNG = "__noi_dung__"
"""Giá trị giao diện gửi về khi người học phát âm đạt yêu cầu."""

MA_LUYEN_TAP = "__luyen_tap__"
"""Mã của lượt luyện tập tổng hợp, không thuộc lộ trình nào."""


class LoaiBaiTap(StrEnum):
    """Các dạng bài tập được hỗ trợ."""

    CHON_NGHIA = auto()
    """Hiện từ tiếng Anh, người học chọn nghĩa tiếng Việt."""

    CHON_TU = auto()
    """Hiện nghĩa tiếng Việt, người học chọn từ tiếng Anh."""

    GO_TU = auto()
    """Hiện nghĩa tiếng Việt, người học tự gõ từ tiếng Anh."""

    GHEP_DOI = auto()
    """Ghép các cặp Anh - Việt với nhau."""

    NGHE_CHON = auto()
    """Nghe máy đọc rồi chọn từ tiếng Anh vừa nghe."""

    NOI_THEO = auto()
    """Đọc to từ tiếng Anh để máy chấm phát âm."""

    DIEN_CHO_TRONG = auto()
    """Điền từ còn thiếu vào chỗ trống trong câu."""

    SAP_XEP_CAU = auto()
    """Bấm các mảnh chữ theo đúng thứ tự để thành câu hoàn chỉnh."""

    CHON_DANG_DUNG = auto()
    """Chọn dạng đúng của từ trong câu."""


_DAP_AN_NOI_BO: Final[frozenset[str]] = frozenset(
    {DAP_AN_GHEP_DUNG, DAP_AN_NOI_DUNG}
)
"""Các đáp án chỉ dùng nội bộ, không bao giờ hiện ra cho người học."""


@dataclass(frozen=True, slots=True)
class CauHoi:
    """Một câu hỏi đã sẵn sàng hiển thị.

    Câu hỏi từ vựng thì gắn với một :class:`TuVung`; câu ngữ pháp thì không có
    từ nào cả và tự mang khoá ôn tập riêng qua ``ma_muc``.
    """

    loai: LoaiBaiTap
    de_bai: str
    cau_hoi: str
    dap_an: str
    tu: TuVung | None = None
    ma_muc: str = ""
    lua_chon: tuple[str, ...] = ()
    cac_cap: tuple[TuVung, ...] = ()
    cac_manh: tuple[str, ...] = ()
    """Các mảnh chữ đã xáo trộn của bài sắp xếp câu."""

    giai_thich: str = ""
    """Lời giải thích hiện ra khi người học trả lời sai."""

    def __post_init__(self) -> None:
        match self.loai:
            case LoaiBaiTap.GHEP_DOI:
                if not self.cac_cap:
                    raise ValueError("Câu ghép đôi cần ít nhất một cặp từ")
            case LoaiBaiTap.SAP_XEP_CAU:
                if not self.cac_manh:
                    raise ValueError("Câu sắp xếp cần các mảnh chữ để bấm")
            case loai if loai in _DANG_GO_CHU or loai is LoaiBaiTap.NOI_THEO:
                pass  # không có phương án để đối chiếu
            case _:
                if self.dap_an not in self.lua_chon:
                    raise ValueError(
                        f"Đáp án {self.dap_an!r} không nằm trong các lựa chọn"
                    )

    @property
    def can_am_thanh(self) -> bool:
        """Câu hỏi chỉ làm được khi máy phát/thu được tiếng."""
        return self.loai in (LoaiBaiTap.NGHE_CHON, LoaiBaiTap.NOI_THEO)

    @property
    def la_ngu_phap(self) -> bool:
        return self.loai in _DANG_NGU_PHAP

    @property
    def khoa_on_tap(self) -> str:
        """Khoá dùng để ghi lịch ôn tập cho mục này."""
        if self.ma_muc:
            return self.ma_muc
        return self.tu.ma if self.tu is not None else ""

    @property
    def dap_an_hien_thi(self) -> str:
        """Đáp án ở dạng đọc được, dùng cho thanh phản hồi."""
        if self.dap_an in _DAP_AN_NOI_BO:
            return self.tu.en if self.tu is not None else ""
        return self.dap_an

    def kiem_tra(self, tra_loi: str) -> bool:
        """So khớp câu trả lời của người học với đáp án đúng.

        Các dạng phải gõ hoặc ghép chữ thì bỏ qua hoa thường, dấu câu và khoảng
        trắng thừa; các dạng bấm chọn thì so khớp đúng nguyên văn.
        """
        if self.loai in _DANG_GO_CHU:
            return chuan_hoa(tra_loi) == chuan_hoa(self.dap_an)
        return tra_loi == self.dap_an


@dataclass(frozen=True, slots=True)
class KetQuaTraLoi:
    """Phản hồi trả về sau mỗi lần người học trả lời."""

    dung: bool
    dap_an_dung: str
    khoa: str
    """Khoá của mục vừa trả lời, dùng để ghi lịch ôn tập."""

    con_tim: int
    giai_thich: str = ""


_DANG_GO_CHU: Final[frozenset[LoaiBaiTap]] = frozenset(
    {LoaiBaiTap.GO_TU, LoaiBaiTap.DIEN_CHO_TRONG, LoaiBaiTap.SAP_XEP_CAU}
)
"""Những dạng người học tự tạo ra chuỗi trả lời, cần so khớp linh hoạt."""

_DANG_NGU_PHAP: Final[frozenset[LoaiBaiTap]] = frozenset(
    {
        LoaiBaiTap.DIEN_CHO_TRONG,
        LoaiBaiTap.SAP_XEP_CAU,
        LoaiBaiTap.CHON_DANG_DUNG,
    }
)
"""Những dạng thuộc phần ngữ pháp, không gắn với từ vựng nào."""


class TrangThaiPhien(StrEnum):
    """Trạng thái của một phiên học."""

    DANG_HOC = auto()
    HOAN_THANH = auto()
    HET_TIM = auto()


class TrinhTaoCauHoi:
    """Sinh bộ câu hỏi cho một bài học.

    Các phương án nhiễu được lấy từ ``kho_nhieu`` (thường là toàn bộ từ vựng của
    giáo trình) để bài tập không bị lộ đáp án khi bài học chỉ có vài từ.
    """

    def __init__(
        self,
        kho_nhieu: Sequence[TuVung],
        rng: Random | None = None,
        *,
        co_loa: bool = False,
        co_micro: bool = False,
    ) -> None:
        self._kho_nhieu = tuple(kho_nhieu)
        self._rng = rng or Random()
        self._co_loa = co_loa
        self._co_micro = co_micro

    def tao(self, bai_hoc: BaiHoc) -> tuple[CauHoi, ...]:
        """Tạo danh sách câu hỏi cho ``bai_hoc``, đã xáo trộn thứ tự."""
        cac_dang = [
            LoaiBaiTap.CHON_NGHIA,
            LoaiBaiTap.CHON_TU,
            LoaiBaiTap.GO_TU,
        ]
        if self._co_loa:
            cac_dang.append(LoaiBaiTap.NGHE_CHON)

        cau_hoi = [
            self._tao_mot_cau(tu, cac_dang[chi_so % len(cac_dang)], bai_hoc)
            for chi_so, tu in enumerate(bai_hoc.tu_vung)
        ]
        self._rng.shuffle(cau_hoi)

        cau_ghep = self._tao_cau_ghep_doi(bai_hoc)
        if cau_ghep is not None:
            cau_hoi.insert(len(cau_hoi) // 2, cau_ghep)

        # Bài nói mất vài giây thu âm nên chỉ chèn đúng một câu mỗi lượt học.
        if self._co_micro:
            tu_noi = self._rng.choice(list(bai_hoc.tu_vung))
            cau_hoi.append(self._tao_mot_cau(tu_noi, LoaiBaiTap.NOI_THEO, bai_hoc))
        return tuple(cau_hoi)

    def _tao_mot_cau(self, tu: TuVung, loai: LoaiBaiTap, bai_hoc: BaiHoc) -> CauHoi:
        match loai:
            case LoaiBaiTap.CHON_NGHIA:
                return CauHoi(
                    loai=loai,
                    tu=tu,
                    de_bai="Từ này nghĩa là gì?",
                    cau_hoi=tu.en,
                    dap_an=tu.vi,
                    lua_chon=self._lua_chon(tu, bai_hoc, lay_tieng_anh=False),
                )
            case LoaiBaiTap.CHON_TU:
                return CauHoi(
                    loai=loai,
                    tu=tu,
                    de_bai="Chọn từ tiếng Anh đúng",
                    cau_hoi=tu.vi,
                    dap_an=tu.en,
                    lua_chon=self._lua_chon(tu, bai_hoc, lay_tieng_anh=True),
                )
            case LoaiBaiTap.GO_TU:
                return CauHoi(
                    loai=loai,
                    tu=tu,
                    de_bai="Viết từ này bằng tiếng Anh",
                    cau_hoi=tu.vi,
                    dap_an=tu.en,
                )
            case LoaiBaiTap.NGHE_CHON:
                return CauHoi(
                    loai=loai,
                    tu=tu,
                    de_bai="Nghe rồi chọn từ em vừa nghe",
                    cau_hoi="",  # giấu chữ đi, người học phải nghe
                    dap_an=tu.en,
                    lua_chon=self._lua_chon(tu, bai_hoc, lay_tieng_anh=True),
                )
            case LoaiBaiTap.NOI_THEO:
                return CauHoi(
                    loai=loai,
                    tu=tu,
                    de_bai="Nhấn nút và đọc to từ này",
                    cau_hoi=tu.en,
                    dap_an=DAP_AN_NOI_DUNG,
                )
            case _:
                raise ValueError(f"Dạng bài không tạo được theo từ đơn: {loai}")

    def _tao_cau_ghep_doi(self, bai_hoc: BaiHoc) -> CauHoi | None:
        """Tạo câu ghép đôi; trả về None nếu bài học có quá ít từ."""
        if len(bai_hoc) < 3:
            return None
        so_cap = min(SO_CAP_GHEP_DOI, len(bai_hoc))
        cac_cap = tuple(self._rng.sample(list(bai_hoc.tu_vung), so_cap))
        return CauHoi(
            loai=LoaiBaiTap.GHEP_DOI,
            tu=cac_cap[0],
            de_bai="Ghép các cặp từ với nhau",
            cau_hoi="",
            dap_an=DAP_AN_GHEP_DUNG,
            cac_cap=cac_cap,
        )

    def _lua_chon(
        self, tu: TuVung, bai_hoc: BaiHoc, *, lay_tieng_anh: bool
    ) -> tuple[str, ...]:
        """Trộn đáp án đúng với các phương án nhiễu rồi xáo vị trí."""
        lay = (lambda t: t.en) if lay_tieng_anh else (lambda t: t.vi)
        dap_an = lay(tu)

        ung_vien: list[str] = []
        da_co = {dap_an}
        for nguon in (self._kho_nhieu, bai_hoc.tu_vung):
            for khac in nguon:
                gia_tri = lay(khac)
                if gia_tri not in da_co:
                    da_co.add(gia_tri)
                    ung_vien.append(gia_tri)

        so_nhieu = min(SO_LUA_CHON - 1, len(ung_vien))
        phuong_an = [dap_an, *self._rng.sample(ung_vien, so_nhieu)]
        self._rng.shuffle(phuong_an)
        return tuple(phuong_an)


class TrinhTaoCauHoiNguPhap:
    """Chuyển một chủ điểm ngữ pháp thành bộ câu hỏi cho phiên học."""

    def __init__(self, rng: Random | None = None) -> None:
        self._rng = rng or Random()

    def tao(self, chu_diem: ChuDiemNguPhap) -> tuple[CauHoi, ...]:
        """Tạo câu hỏi cho toàn bộ chủ điểm, đã xáo trộn thứ tự."""
        cau_hoi = [self._tao_mot_cau(cau) for cau in chu_diem]
        self._rng.shuffle(cau_hoi)
        return tuple(cau_hoi)

    def _tao_mot_cau(self, cau: CauNguPhap) -> CauHoi:
        chung = {
            "de_bai": cau.de_bai,
            "cau_hoi": cau.cau,
            "dap_an": cau.dap_an,
            "ma_muc": cau.ma,
            "giai_thich": cau.giai_thich,
        }
        match cau.dang:
            case DangNguPhap.DIEN_CHO_TRONG:
                return CauHoi(loai=LoaiBaiTap.DIEN_CHO_TRONG, **chung)
            case DangNguPhap.SAP_XEP_CAU:
                manh = list(cau.manh_chu)
                self._rng.shuffle(manh)
                return CauHoi(
                    loai=LoaiBaiTap.SAP_XEP_CAU, cac_manh=tuple(manh), **chung
                )
            case _:
                lua_chon = list(cau.lua_chon)
                self._rng.shuffle(lua_chon)
                return CauHoi(
                    loai=LoaiBaiTap.CHON_DANG_DUNG,
                    lua_chon=tuple(lua_chon),
                    **chung,
                )


class CheDoPhien(StrEnum):
    """Một lượt học thuộc phần nào, quyết định cách ghi nhận kết quả."""

    BAI_HOC = auto()
    """Chặng trong lộ trình từ vựng: hoàn thành thì đánh dấu chặng đó."""

    LUYEN_TAP = auto()
    """Buổi ôn tập tổng hợp: chỉ cộng XP, không đánh dấu chặng nào."""

    NGU_PHAP = auto()
    """Chủ điểm ngữ pháp: hoàn thành thì đánh dấu chủ điểm đó."""


@dataclass(frozen=True, slots=True)
class NoiDungPhien:
    """Mọi thứ cần để mở một lượt học, dù là từ vựng hay ngữ pháp."""

    ma: str
    ten: str
    cau_hoi: tuple[CauHoi, ...]
    che_do: CheDoPhien

    def __post_init__(self) -> None:
        if not self.cau_hoi:
            raise ValueError(f"Nội dung phiên {self.ma!r} không có câu hỏi nào")

    @property
    def danh_dau_hoan_thanh(self) -> bool:
        """Buổi luyện tập không đánh dấu mục nào là đã xong."""
        return self.che_do is not CheDoPhien.LUYEN_TAP

    # ------------------------------------------------------------------ #

    @classmethod
    def tu_bai_hoc(
        cls,
        bai_hoc: BaiHoc,
        kho_nhieu: Sequence[TuVung],
        rng: Random | None = None,
        *,
        co_loa: bool = False,
        co_micro: bool = False,
    ) -> "NoiDungPhien":
        cau_hoi = TrinhTaoCauHoi(
            kho_nhieu, rng, co_loa=co_loa, co_micro=co_micro
        ).tao(bai_hoc)
        return cls(
            ma=bai_hoc.ma,
            ten=bai_hoc.ten,
            cau_hoi=cau_hoi,
            che_do=CheDoPhien.BAI_HOC,
        )

    @classmethod
    def luyen_tap(
        cls,
        cac_tu: Sequence[TuVung],
        kho_nhieu: Sequence[TuVung],
        rng: Random | None = None,
        *,
        co_loa: bool = False,
        co_micro: bool = False,
    ) -> "NoiDungPhien":
        """Gom các từ rời rạc từ nhiều đơn vị thành một lượt luyện tập."""
        bai_tam = BaiHoc(ma=MA_LUYEN_TAP, ten="Luyện tập", tu_vung=tuple(cac_tu))
        cau_hoi = TrinhTaoCauHoi(
            kho_nhieu, rng, co_loa=co_loa, co_micro=co_micro
        ).tao(bai_tam)
        return cls(
            ma=MA_LUYEN_TAP,
            ten="Luyện tập",
            cau_hoi=cau_hoi,
            che_do=CheDoPhien.LUYEN_TAP,
        )

    @classmethod
    def tu_chu_diem(
        cls, chu_diem: ChuDiemNguPhap, rng: Random | None = None
    ) -> "NoiDungPhien":
        return cls(
            ma=chu_diem.ma,
            ten=chu_diem.ten,
            cau_hoi=TrinhTaoCauHoiNguPhap(rng).tao(chu_diem),
            che_do=CheDoPhien.NGU_PHAP,
        )


class PhienHoc:
    """Máy trạng thái cho một lượt học.

    Giống Duolingo: trả lời sai sẽ mất một tim và câu hỏi bị đẩy xuống cuối hàng
    đợi để hỏi lại; hết tim thì phiên học thất bại.
    """

    SO_TIM_TOI_DA = 5
    XP_MOI_CAU = 2
    XP_THUONG_HOAN_HAO = 10

    def __init__(self, cau_hoi: Sequence[CauHoi]) -> None:
        if not cau_hoi:
            raise ValueError("Phiên học cần ít nhất một câu hỏi")
        self._hang_doi: deque[CauHoi] = deque(cau_hoi)
        self._tong_cau = len(cau_hoi)
        self._da_dung = 0
        self._so_loi = 0
        self._con_tim = self.SO_TIM_TOI_DA

    @property
    def cau_hoi_hien_tai(self) -> CauHoi | None:
        return self._hang_doi[0] if self._hang_doi else None

    @property
    def con_tim(self) -> int:
        return self._con_tim

    @property
    def so_loi(self) -> int:
        return self._so_loi

    @property
    def hoan_hao(self) -> bool:
        return self._so_loi == 0

    @property
    def ty_le_hoan_thanh(self) -> float:
        """Tỷ lệ 0.0 - 1.0 dùng cho thanh tiến độ phía trên màn hình."""
        return self._da_dung / self._tong_cau if self._tong_cau else 1.0

    @property
    def trang_thai(self) -> TrangThaiPhien:
        if self._con_tim <= 0:
            return TrangThaiPhien.HET_TIM
        if not self._hang_doi:
            return TrangThaiPhien.HOAN_THANH
        return TrangThaiPhien.DANG_HOC

    @property
    def xp_dat_duoc(self) -> int:
        """XP nhận được, chỉ tính khi phiên học hoàn thành."""
        if self.trang_thai is not TrangThaiPhien.HOAN_THANH:
            return 0
        thuong = self.XP_THUONG_HOAN_HAO if self.hoan_hao else 0
        return self._tong_cau * self.XP_MOI_CAU + thuong

    def tra_loi(self, dap_an: str) -> KetQuaTraLoi:
        """Ghi nhận câu trả lời cho câu hỏi hiện tại rồi chuyển sang câu kế tiếp."""
        cau_hoi = self.cau_hoi_hien_tai
        if cau_hoi is None:
            raise RuntimeError("Phiên học đã kết thúc, không còn câu hỏi để trả lời")

        dung = cau_hoi.kiem_tra(dap_an)
        self._hang_doi.popleft()
        if dung:
            self._da_dung += 1
        else:
            self._so_loi += 1
            self._con_tim -= 1
            self._hang_doi.append(cau_hoi)

        return KetQuaTraLoi(
            dung=dung,
            dap_an_dung=cau_hoi.dap_an_hien_thi,
            khoa=cau_hoi.khoa_on_tap,
            con_tim=self._con_tim,
            giai_thich=cau_hoi.giai_thich,
        )
