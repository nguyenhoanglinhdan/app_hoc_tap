"""Dịch vụ âm thanh: đọc từ tiếng Anh và chấm điểm phát âm của người học.

Toàn bộ thư viện âm thanh ở đây đều **không bắt buộc**. Thiếu thư viện, thiếu
micro hay mất mạng thì ứng dụng vẫn chạy bình thường, chỉ ẩn bớt nút bấm liên
quan - xem :attr:`DichVuAmThanh.kha_nang`.

Mọi tác vụ nặng đều chạy ở luồng nền để giao diện không bị treo. Hàm gọi lại
(callback) vì thế **chạy ở luồng nền**, bên giao diện phải đẩy về luồng chính
bằng ``widget.after(0, ...)`` trước khi đụng tới widget.
"""

from __future__ import annotations

import logging
import queue
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final

from .mo_hinh import chuan_hoa

__all__ = [
    "KhaNangAmThanh",
    "KetQuaPhatAm",
    "DichVuAmThanh",
    "DIEM_DAT",
    "GIAY_THU_AM",
]

_log = logging.getLogger(__name__)

DIEM_DAT: Final[int] = 70
"""Điểm giống nhau tối thiểu (0-100) để coi là phát âm đạt."""

GIAY_THU_AM: Final[float] = 4.0
"""Thời lượng thu âm mỗi lần người học nói."""

_TOC_DO_DOC: Final[int] = 150
"""Tốc độ đọc, chậm hơn mặc định (200) cho người mới học dễ nghe."""


# ---------------------------------------------------------------------- #
# Dò khả năng của máy
# ---------------------------------------------------------------------- #


def _thu_nap(ten: str) -> object | None:
    """Nạp một module tuỳ chọn, trả về None nếu máy chưa cài hoặc lỗi."""
    try:
        import importlib

        return importlib.import_module(ten)
    except Exception as loi:  # nhiều thư viện âm thanh ném OSError, không chỉ ImportError
        _log.info("Không dùng được %s: %s", ten, loi)
        return None


_pyttsx3 = _thu_nap("pyttsx3")
_sd = _thu_nap("sounddevice")
_sf = _thu_nap("soundfile")
_sr = _thu_nap("speech_recognition")
_rapidfuzz = _thu_nap("rapidfuzz")


@dataclass(frozen=True, slots=True)
class KhaNangAmThanh:
    """Những việc máy hiện tại làm được."""

    doc: bool
    """Đọc được từ tiếng Anh thành tiếng."""

    thu_am: bool
    """Thu được giọng người học và chấm điểm phát âm."""

    @property
    def co_gi_do(self) -> bool:
        return self.doc or self.thu_am


@dataclass(frozen=True, slots=True)
class KetQuaPhatAm:
    """Kết quả một lần chấm phát âm."""

    nghe_duoc: str
    """Chuỗi mà máy nghe ra được, rỗng nếu không nhận dạng nổi."""

    diem: int
    """Độ giống với từ mục tiêu, thang 0-100."""

    dat: bool
    loi: str | None = None
    """Thông báo lỗi thân thiện, None nếu chấm được bình thường."""

    @classmethod
    def tu_loi(cls, thong_bao: str) -> "KetQuaPhatAm":
        return cls(nghe_duoc="", diem=0, dat=False, loi=thong_bao)


# ---------------------------------------------------------------------- #
# Luồng đọc
# ---------------------------------------------------------------------- #


class _LuongDoc(threading.Thread):
    """Luồng riêng sở hữu bộ đọc SAPI.

    pyttsx3 không an toàn khi gọi từ nhiều luồng và ``runAndWait`` không cho
    chạy lồng nhau, nên chỉ một luồng duy nhất được đụng vào bộ đọc; các yêu
    cầu khác xếp hàng chờ.
    """

    def __init__(self) -> None:
        super().__init__(daemon=True, name="doc-tieng-anh")
        self._hang_cho: queue.Queue[str | None] = queue.Queue()

    def doc(self, van_ban: str) -> None:
        self._hang_cho.put(van_ban)

    def dung(self) -> None:
        self._hang_cho.put(None)

    def run(self) -> None:
        bo_doc = self._tao_bo_doc()
        if bo_doc is None:
            return
        while True:
            van_ban = self._hang_cho.get()
            if van_ban is None:
                break
            try:
                bo_doc.say(van_ban)
                bo_doc.runAndWait()
            except Exception:
                _log.exception("Lỗi khi đọc %r", van_ban)

    @staticmethod
    def _tao_bo_doc() -> object | None:
        """Khởi tạo bộ đọc ngay trong luồng này và chọn giọng tiếng Anh."""
        if _pyttsx3 is None:
            return None
        try:
            bo_doc = _pyttsx3.init()
            bo_doc.setProperty("rate", _TOC_DO_DOC)
            for giong in bo_doc.getProperty("voices"):
                if "en" in f"{giong.id} {giong.name}".lower():
                    bo_doc.setProperty("voice", giong.id)
                    break
            return bo_doc
        except Exception:
            _log.exception("Không khởi tạo được bộ đọc")
            return None


# ---------------------------------------------------------------------- #
# Chọn micro
# ---------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class _Micro:
    """Thiết bị thu âm đã chọn kèm tần số lấy mẫu của nó."""

    chi_so: int
    tan_so: int
    ten: str


_TU_KHOA_BO_QUA: Final[tuple[str, ...]] = (
    "stereo mix",
    "loopback",
    "what u hear",
    "wave out",
)
"""Các thiết bị ghi lại âm thanh hệ thống chứ không phải giọng người."""


def _chon_micro() -> _Micro | None:
    """Chọn micro dùng được.

    Không dựa vào thiết bị mặc định của hệ điều hành: nhiều máy không đặt thiết
    bị vào mặc định, khi đó PortAudio báo lỗi ``Error querying device -1``.
    Thay vào đó tự duyệt danh sách và ưu tiên micro có tần số cao nhất, vì các
    mục 8 kHz thường là tai nghe Bluetooth chưa kết nối.
    """
    if _sd is None:
        return None
    try:
        danh_sach = _sd.query_devices()
    except Exception as loi:
        _log.info("Không liệt kê được thiết bị âm thanh: %s", loi)
        return None

    ung_vien: list[_Micro] = []
    for chi_so, thiet_bi in enumerate(danh_sach):
        if thiet_bi["max_input_channels"] <= 0:
            continue
        ten = str(thiet_bi["name"])
        if any(tu in ten.lower() for tu in _TU_KHOA_BO_QUA):
            continue
        ung_vien.append(
            _Micro(chi_so, int(thiet_bi["default_samplerate"]), ten)
        )

    if not ung_vien:
        return None
    chon = max(ung_vien, key=lambda m: m.tan_so)
    _log.info("Dùng micro: %s (%d Hz)", chon.ten, chon.tan_so)
    return chon


# ---------------------------------------------------------------------- #
# Dịch vụ
# ---------------------------------------------------------------------- #


class DichVuAmThanh:
    """Cổng vào duy nhất cho mọi việc liên quan tới âm thanh."""

    def __init__(self) -> None:
        self._micro: _Micro | None = None
        self._kha_nang = KhaNangAmThanh(
            doc=_pyttsx3 is not None,
            thu_am=self._thu_am_kha_thi(),
        )
        self._luong_doc: _LuongDoc | None = None
        self._dang_thu_am = False

    @property
    def kha_nang(self) -> KhaNangAmThanh:
        return self._kha_nang

    @property
    def dang_thu_am(self) -> bool:
        return self._dang_thu_am

    # ------------------------------------------------------------------ #

    def _thu_am_kha_thi(self) -> bool:
        """Cần đủ thư viện thu âm, nhận dạng, và một micro dùng được."""
        if None in (_sd, _sf, _sr, _rapidfuzz):
            return False
        self._micro = _chon_micro()
        return self._micro is not None

    # ------------------------------------------------------------------ #
    # Đọc
    # ------------------------------------------------------------------ #

    def doc(self, van_ban: str) -> None:
        """Đọc to một từ hoặc câu tiếng Anh. Trả về ngay, không chờ đọc xong."""
        if not self._kha_nang.doc or not van_ban.strip():
            return
        if self._luong_doc is None:
            self._luong_doc = _LuongDoc()
            self._luong_doc.start()
        self._luong_doc.doc(van_ban)

    # ------------------------------------------------------------------ #
    # Thu âm và chấm điểm
    # ------------------------------------------------------------------ #

    def cham_phat_am(
        self,
        muc_tieu: str,
        khi_xong: Callable[[KetQuaPhatAm], None],
        giay: float = GIAY_THU_AM,
    ) -> bool:
        """Thu giọng người học rồi so với ``muc_tieu``.

        Trả về False nếu không thể bắt đầu (thiếu thiết bị, hoặc đang thu dở).
        ``khi_xong`` chạy ở luồng nền.
        """
        if not self._kha_nang.thu_am or self._dang_thu_am:
            return False

        self._dang_thu_am = True
        threading.Thread(
            target=self._chay_cham_phat_am,
            args=(muc_tieu, khi_xong, giay),
            daemon=True,
            name="cham-phat-am",
        ).start()
        return True

    def _chay_cham_phat_am(
        self, muc_tieu: str, khi_xong: Callable[[KetQuaPhatAm], None], giay: float
    ) -> None:
        try:
            ket_qua = self._thu_va_nhan_dang(muc_tieu, giay)
        except Exception:
            _log.exception("Lỗi khi chấm phát âm")
            ket_qua = KetQuaPhatAm.tu_loi("Có lỗi khi xử lý âm thanh, thử lại nhé!")
        finally:
            self._dang_thu_am = False
        khi_xong(ket_qua)

    def _thu_va_nhan_dang(self, muc_tieu: str, giay: float) -> KetQuaPhatAm:
        """Thu âm ra tệp tạm, gửi đi nhận dạng, rồi tính điểm giống nhau."""
        micro = self._micro
        if micro is None:
            return KetQuaPhatAm.tu_loi("Không tìm thấy micro nào để thu âm.")

        du_lieu = _sd.rec(
            int(giay * micro.tan_so),
            samplerate=micro.tan_so,
            channels=1,
            device=micro.chi_so,
        )
        _sd.wait()
        tan_so = micro.tan_so

        tep_tam = Path(tempfile.gettempdir()) / "hoc_tieng_anh_phat_am.wav"
        _sf.write(tep_tam, du_lieu, tan_so)

        bo_nhan_dang = _sr.Recognizer()
        with _sr.AudioFile(str(tep_tam)) as nguon:
            am_thanh = bo_nhan_dang.record(nguon)

        try:
            nghe_duoc = bo_nhan_dang.recognize_google(am_thanh, language="en-US")
        except _sr.UnknownValueError:
            return KetQuaPhatAm.tu_loi("Chưa nghe rõ, bạn nói to hơn một chút nhé!")
        except _sr.RequestError:
            return KetQuaPhatAm.tu_loi("Cần mạng Internet để chấm phát âm.")
        finally:
            tep_tam.unlink(missing_ok=True)

        diem = int(
            _rapidfuzz.fuzz.ratio(chuan_hoa(nghe_duoc), chuan_hoa(muc_tieu))
        )
        return KetQuaPhatAm(nghe_duoc=nghe_duoc, diem=diem, dat=diem >= DIEM_DAT)

    # ------------------------------------------------------------------ #

    def dong(self) -> None:
        """Dừng luồng đọc khi thoát ứng dụng."""
        if self._luong_doc is not None:
            self._luong_doc.dung()
            self._luong_doc = None
