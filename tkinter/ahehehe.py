import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

class ToGiay(tk.Frame):

    def __init__(self, khung_anh):
        tk.Frame.__init__(self, khung_anh)         # lệnh tạo ra tờ giấy

        self.pack(fill ="both", expand = True, padx = 5, pady = 5)     # đưa cho mình một tờ giấy hoàn chỉnh, bth
        self.columnconfigure(1, weight = 2)

        ttk.Label(self, text = 'Ten').grid(row = 0, column = 0, padx = 5, pady = 5, sticky = 'w')                     # ttk.Label là lệnh dùng để thêm chữ, thêm gì đó vào tờ giấy, cửa sổ í
        ttk.Label(self, text = 'Noi Dung').grid(row = 1, column = 0, padx= 5, pady = 5, sticky = 'w')

        self.ten = ttk.Entry(self)
        self.ten.grid(row = 0, column = 1,padx = 5, pady = 5, sticky = 'ew')       # gắn ô nhập thông tin vào sát bên phải

        self.noi_dung = scrolledtext.ScrolledText(self, wrap = tk.WORD, width = 40, height = 10, font = ('Arial, 12'))
        self.noi_dung.grid(row = 1, column = 1)

        self.nut_bam = ttk.Button(self, text = 'nút bấm', command = self.hanh_dong_bam_nut)
        self.nut_bam.grid(row = 2, column = 1, pady = 10, sticky = 'e')

    def hanh_dong_bam_nut(self):
        ten = self.ten.get()
        noi_dung = self.noi_dung.get("1.0", tk.END)
        print("ten :" + ten)
        print("noi_dung :" + noi_dung)

        info = (
            f"Noi dung ban da nhap la: \n"
            f"Ten: {ten}\n"
            f"Noi dung: {noi_dung}\n"
        )

        messagebox.showinfo('xin chào linh Đan', info)

if __name__ == "__main__" :
    root = tk.Tk()
    root.title('Nhap thong tin')
    root.geometry('900x450')

    ToGiay(root)
    root.mainloop()