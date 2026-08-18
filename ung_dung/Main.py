import tkinter as tk
from tkinter import *

#
#
#
# Label(window, text='First Name').grid(row=0)
# Label(window, text='Last Name').grid(row=1)
# e1 = Entry(window)
# e2 = Entry(window)
# e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)
#
# tk.Button(window, text="Stop", command=window.destroy).grid(row=3, column=1)
#
# scrollbar = Scrollbar(window)
# scrollbar.grid(row=2, column=2, sticky='ns')
# mylist = Listbox(window, yscrollcommand=scrollbar.set)
#
# for line in range(100):
#     mylist.insert(END,  "this is line number" + str(line))
#
# mylist.grid(row=2, column=0, columnspan=2, sticky='nsew')
# scrollbar.config(command=mylist.yview)
def create_mon_hoc(window):
    frame = Toplevel(window)
    frame.title("Môn học")
    frame.geometry("800x600")
    frame.mainloop()

def create_lop_hoc(window):
    frame = Toplevel(window)
    frame.title("Lớp học")
    frame.geometry("800x600")
    frame.mainloop()

def create_tu_vung(window):
    frame = Toplevel(window)
    frame.title("Từ vựng")
    frame.geometry("800x600")
    frame.mainloop()

def create_menu(window):
    menu = Menu(window)
    window.config(menu=menu)

    file_menu = Menu(menu)
    menu.add_cascade(label="Lựa chọn", menu=file_menu)
    file_menu.add_command(label="Môn học", command=lambda: create_mon_hoc(window))
    file_menu.add_command(label="Lớp học", command=lambda: create_lop_hoc(window))
    file_menu.add_command(label="Từ vựng", command=lambda: create_tu_vung(window))
    file_menu.add_separator()
    file_menu.add_command(label="Kết thúc", command=window.destroy)

if __name__ == "__main__":
    window = tk.Tk()
    window.title("App học từ vựng")
    window.geometry("800x600")
    create_menu(window)
    window.mainloop()
