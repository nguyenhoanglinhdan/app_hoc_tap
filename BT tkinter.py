import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext


class ToGiay(tk.Frame):

    def __init__(self, khung_anh):
        tk.Frame.__init__(self, khung_anh)  # lệnh tạo ra tờ giấy

        self.pack(fill="both", expand=True, padx=5, pady=5)  # đưa cho mình một tờ giấy hoàn chỉnh, bth
        self.columnconfigure(1, weight=2)

        ttk.Label(self, text='Tên cuốn sách').grid(row=0, column=0, padx=5, pady=5,
                                                   sticky='w')  # ttk.Label là lệnh dùng để thêm chữ, thêm gì đó vào tờ giấy, cửa sổ í
        ttk.Label(self, text='Tên tác giả').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self, text='giá tiền').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(self, text='Nội dung').grid(row=3, column=0, padx=5, pady=5, sticky='w')

        self.ten_sach = ttk.Entry(self)
        self.ten_sach.grid(row=0, column=1, padx=5, pady=5, sticky='ew')  # gắn ô nhập thông tin vào sát bên phải

        self.tac_gia = ttk.Entry(self)
        self.tac_gia.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.gia_tien = ttk.Entry(self)
        self.gia_tien.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        self.noi_dung = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=10, font=('Arial, 12'))
        self.noi_dung.grid(row=3, column=1)

        self.nut_bam = ttk.Button(self, text='nút bấm', command=self.hanh_dong_bam_nut)
        self.nut_bam.grid(row=10, column=1, pady=10, sticky='e')

    def hanh_dong_bam_nut(self):
        ten_sach = self.ten_sach.get()
        tac_gia = self.tac_gia.get()
        gia_tien = self.tac_gia.get()
        noi_dung = self.noi_dung.get("1.0", tk.END)

        print('Tên sách :' + ten_sach)
        print('Tác giả :' + tac_gia)
        print('Giá tiền :' + gia_tien)
        print('Nội dung :' + noi_dung)

        info = (
            f"Nội dung bạn đã nhập là: \n"
            f'Tên sách : {ten_sach}\n'
            f'Tác giả : {tac_gia}\n'
            f'Giá tiền : {gia_tien}\n'
            f'Nội dung : {noi_dung}\n'
        )

        messagebox.showinfo('Thông tin của cuốn sách', info)


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Nhập thông tin về cuốn sách')
    root.geometry('900x450')

    ToGiay(root)
    root.mainloop()