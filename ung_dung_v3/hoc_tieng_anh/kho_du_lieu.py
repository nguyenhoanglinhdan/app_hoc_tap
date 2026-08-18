"""Lớp truy cập dữ liệu: đọc giáo trình và đọc/ghi tiến độ.

Đây là ranh giới vào/ra duy nhất của phần lõi. Tiến độ được ghi theo kiểu
"ghi tạm rồi thay thế" (:func:`os.replace`) để tệp không bị hỏng nếu ứng dụng
bị tắt giữa chừng.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from .mo_hinh import SO_TU_MOI_BAI, DonVi, GiaoTrinh, MauDonVi, TuVung
from .tien_do import TienDo

__all__ = ["KhoDuLieu", "LoiDuLieu", "SO_TU_MOI_BAI"]

_log = logging.getLogger(__name__)

TEN_TEP_GIAO_TRINH = "tu_vung.json"
TEN_TEP_TIEN_DO = "tien_do.json"


class LoiDuLieu(RuntimeError):
    """Lỗi không thể phục hồi khi nạp dữ liệu học."""


class KhoDuLieu:
    """Đọc ghi dữ liệu của ứng dụng trong một thư mục cho trước."""

    def __init__(self, thu_muc: Path | str) -> None:
        self.thu_muc = Path(thu_muc)

    @property
    def duong_dan_giao_trinh(self) -> Path:
        return self.thu_muc / TEN_TEP_GIAO_TRINH

    @property
    def duong_dan_tien_do(self) -> Path:
        return self.thu_muc / TEN_TEP_TIEN_DO

    # ------------------------------------------------------------------ #
    # Giáo trình
    # ------------------------------------------------------------------ #

    def tai_giao_trinh(self) -> GiaoTrinh:
        """Nạp toàn bộ nội dung học.

        Raises:
            LoiDuLieu: khi tệp không tồn tại, sai định dạng JSON hoặc rỗng.
        """
        duong_dan = self.duong_dan_giao_trinh
        try:
            noi_dung = duong_dan.read_text(encoding="utf-8")
        except FileNotFoundError as loi:
            raise LoiDuLieu(f"Không tìm thấy tệp giáo trình: {duong_dan}") from loi
        except OSError as loi:
            raise LoiDuLieu(f"Không đọc được tệp giáo trình: {duong_dan}") from loi

        try:
            du_lieu = json.loads(noi_dung)
        except json.JSONDecodeError as loi:
            raise LoiDuLieu(f"Tệp giáo trình sai định dạng JSON: {duong_dan}") from loi

        if not isinstance(du_lieu, Mapping):
            raise LoiDuLieu("Giáo trình phải là một đối tượng JSON")

        cac_don_vi = du_lieu.get("cac_don_vi")
        if not isinstance(cac_don_vi, Sequence) or not cac_don_vi:
            raise LoiDuLieu("Giáo trình không có đơn vị bài học nào")

        try:
            return GiaoTrinh(
                don_vi=tuple(self._doc_don_vi(dv) for dv in cac_don_vi)
            )
        except (ValueError, TypeError, KeyError, AttributeError) as loi:
            raise LoiDuLieu(f"Nội dung giáo trình không hợp lệ: {loi}") from loi

    def _doc_don_vi(self, du_lieu: Mapping[str, Any]) -> DonVi:
        return DonVi.tu_danh_sach_tu(
            ma=str(du_lieu["ma"]),
            ten=str(du_lieu["ten"]),
            mo_ta=str(du_lieu.get("mo_ta", "")),
            mau=MauDonVi.tu_chuoi(str(du_lieu.get("mau", ""))),
            bieu_tuong=str(du_lieu.get("bieu_tuong", "📘")),
            tu_vung=tuple(self._doc_tu_vung(tu) for tu in du_lieu["tu_vung"]),
        )

    @staticmethod
    def _doc_tu_vung(du_lieu: Mapping[str, Any]) -> TuVung:
        return TuVung(
            en=str(du_lieu["en"]).strip(),
            vi=str(du_lieu["vi"]).strip(),
            phien_am=str(du_lieu.get("phien_am", "")).strip(),
        )

    # ------------------------------------------------------------------ #
    # Tiến độ
    # ------------------------------------------------------------------ #

    def tai_tien_do(self) -> TienDo:
        """Nạp tiến độ đã lưu.

        Tiến độ hỏng hoặc thiếu không phải lỗi nghiêm trọng: ứng dụng bắt đầu
        lại từ đầu thay vì từ chối khởi động.
        """
        duong_dan = self.duong_dan_tien_do
        try:
            du_lieu = json.loads(duong_dan.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return TienDo()
        except (OSError, json.JSONDecodeError):
            _log.warning("Tệp tiến độ hỏng, bắt đầu lại từ đầu: %s", duong_dan)
            return TienDo()

        if not isinstance(du_lieu, Mapping):
            _log.warning("Tệp tiến độ sai cấu trúc, bỏ qua: %s", duong_dan)
            return TienDo()
        return TienDo.tu_dict(du_lieu)

    def luu_tien_do(self, tien_do: TienDo) -> None:
        """Ghi tiến độ xuống đĩa một cách nguyên tử."""
        try:
            self._ghi_json(self.duong_dan_tien_do, tien_do.sang_dict())
        except OSError:
            _log.exception("Không lưu được tiến độ vào %s", self.duong_dan_tien_do)

    # ------------------------------------------------------------------ #
    # Ghi tệp
    # ------------------------------------------------------------------ #

    def luu_giao_trinh(self, giao_trinh: GiaoTrinh) -> None:
        """Ghi lại toàn bộ nội dung học sau khi người dùng chỉnh sửa.

        Các bài học nhỏ được ghép lại thành danh sách từ phẳng của từng đơn vị,
        đúng như định dạng lúc đọc lên.

        Raises:
            LoiDuLieu: khi không ghi được tệp.
        """
        du_lieu = {
            "phien_ban": 1,
            "cac_don_vi": [
                {
                    "ma": don_vi.ma,
                    "ten": don_vi.ten,
                    "mo_ta": don_vi.mo_ta,
                    "mau": don_vi.mau.value,
                    "bieu_tuong": don_vi.bieu_tuong,
                    "tu_vung": [
                        {"en": tu.en, "vi": tu.vi, "phien_am": tu.phien_am}
                        for tu in don_vi.tat_ca_tu_vung
                    ],
                }
                for don_vi in giao_trinh.don_vi
            ],
        }
        try:
            self._ghi_json(self.duong_dan_giao_trinh, du_lieu)
        except OSError as loi:
            raise LoiDuLieu(
                f"Không ghi được tệp giáo trình: {self.duong_dan_giao_trinh}"
            ) from loi

    def _ghi_json(self, duong_dan: Path, du_lieu: object) -> None:
        """Ghi JSON theo kiểu ghi tạm rồi thay thế, tránh hỏng tệp giữa chừng."""
        self.thu_muc.mkdir(parents=True, exist_ok=True)
        noi_dung = json.dumps(du_lieu, ensure_ascii=False, indent=2)

        tep_tam: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.thu_muc,
                prefix=f".{duong_dan.stem}-",
                suffix=".tmp",
                delete=False,
            ) as tep:
                tep_tam = tep.name
                tep.write(noi_dung)
                tep.flush()
                os.fsync(tep.fileno())
            os.replace(tep_tam, duong_dan)
            tep_tam = None
        finally:
            if tep_tam is not None:
                Path(tep_tam).unlink(missing_ok=True)
