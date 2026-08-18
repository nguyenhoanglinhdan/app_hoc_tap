"""Điểm khởi động ứng dụng học tiếng Anh.

Chạy bằng lệnh::

    python main.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from hoc_tieng_anh.kho_du_lieu import KhoDuLieu, LoiDuLieu
from hoc_tieng_anh.giao_dien.ung_dung import TEN_UNG_DUNG, UngDung

THU_MUC_DU_LIEU = Path(__file__).resolve().parent / "du_lieu"


def chay() -> int:
    """Khởi động ứng dụng, trả về mã thoát cho hệ điều hành."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    try:
        ung_dung = UngDung(KhoDuLieu(THU_MUC_DU_LIEU))
    except LoiDuLieu as loi:
        logging.getLogger(__name__).error("Không khởi động được: %s", loi)
        messagebox.showerror(TEN_UNG_DUNG, f"Không nạp được dữ liệu học:\n\n{loi}")
        return 1

    ung_dung.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(chay())
