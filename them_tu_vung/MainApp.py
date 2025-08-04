import tkinter as tk

from them_tu_vung.thanh_phan.man_hinh_chinh import man_hinh_chinh
from them_tu_vung.thanh_phan.man_hinh_them_tu_vung import man_hinh_them_tu_vung

class chuong_trinh_chinh:
    def __init__(self, root):
        self.root = root
        self.man_hinh_hien_tai = None
        self.hien_thi_man_hinh_chinh()

    def hien_thi_man_hinh_chinh(self):
        if self.man_hinh_hien_tai:
            self.man_hinh_hien_tai.destroy()
        self.man_hinh_hien_tai = man_hinh_chinh(self.root, self.hien_thi_man_hinh_them_tu_vung)

    def hien_thi_man_hinh_them_tu_vung(self, lop_hoc, mon_hoc):
        if self.man_hinh_hien_tai:
            self.man_hinh_hien_tai.destroy()
        self.man_hinh_hien_tai = man_hinh_them_tu_vung(self.root, lop_hoc, mon_hoc, self.hien_thi_man_hinh_chinh)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý học từ vựng.")
    root.geometry("800x600")
    app = chuong_trinh_chinh(root)
    root.mainloop()
