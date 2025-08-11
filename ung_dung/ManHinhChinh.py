import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk

class man_hinh_chinh(tk.Frame):
    topic_list = ["toán", "khoa học", "tiếng anh", "lịch sử", "địa lý", "sinh học", "hóa học", "vật lý", "xã hội",
                  "âm nhạc", "thể dục", "công nghệ", "tin học", "ngữ văn", "khác"]
    grade_list = ["lớp 1", "lớp 2", "lớp 3", "lớp 4", "lớp 5", "lớp 6", "lớp 7", "lớp 8", "lớp 9", "lớp 10", "lớp 11", "lớp 12"]

    def __init__(self, parent, switch_to_insert_form):
        tk.Frame.__init__(self, parent)
        self.switch_to_insert_form = switch_to_insert_form

        style = ttk.Style()
        style.configure("Blue.TFrame", background="#333333")
        self.pack(fill="both", expand=True, padx=15, pady=15)
        self.columnconfigure(1, weight=1)

        self.grade_var = tk.StringVar()
        self.topic_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_body()

    def create_header(self):
        ttk.Label(self, text="Quản lý từ vựng", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3,
                                                                                       pady=20)
        ttk.Label(self, text="Chọn lớp và chủ đề", font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=3,
                                                                                        pady=10)

    def create_body(self):
        # Grade selection
        ttk.Label(self, text="Lớp:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        grade_combo = ttk.Combobox(self, textvariable=self.grade_var, values=self.grade_list, width=20)
        grade_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Topic selection
        ttk.Label(self, text="Chủ đề:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        topic_combo = ttk.Combobox(self, textvariable=self.topic_var, values=self.topic_list, width=20)
        topic_combo.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Add button
        add_button = ttk.Button(self, text="Thêm từ vựng", command=self.add_vocabulary)
        add_button.grid(row=4, column=0, columnspan=2, pady=20)

    def add_vocabulary(self):
        if self.grade_var.get() == "" or self.topic_var.get() == "":
            messagebox.showerror("Lỗi", "Vui lòng chọn lớp và chủ đề")
            return

        # Switch to insert form with selected grade and topic
        self.switch_to_insert_form(self.grade_var.get(), self.topic_var.get())