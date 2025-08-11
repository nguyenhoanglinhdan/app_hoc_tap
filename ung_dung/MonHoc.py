import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os


class man_hinh_them_mon_hoc(tk.Frame):
    folder_path = "du_lieu/mon_hoc"
    file_path = f"{folder_path}/mon_hoc.json"

    def __init__(self, root, cn_khoi_tao_man_hinh_chinh=None):
        self.root = root
        tk.Frame.__init__(self)
        self.cn_tao_man_hinh_chinh = cn_khoi_tao_man_hinh_chinh

        # cấu hình frame main
        self.configure(bg="#f0f2f5")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)
        self.mon_hoc = tk.StringVar()

        # cấu hình custom styles
        self.cn_setup_styles()

        # khởi tạo
        self.cn_khoi_tao_man_hinh_them_mon_hoc()

    def cn_setup_styles(self):
        """cấu hình custom styles cho giao diện"""
        style = ttk.Style()
        
        # cấu hình custom styles cho title
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 24, "bold"), 
                       foreground="#1a1a1a",
                       background="#B2B0E8")
        
        # cấu hình custom styles cho header
        style.configure("Header.TLabel", 
                       font=("Segoe UI", 12, "bold"), 
                       foreground="#2c3e50",
                       background="#B2B0E8")
        
        # cấu hình custom styles cho button thường
        style.configure("Modern.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=(15, 8),
                       background="#B2B0E8",
                       foreground="black")
        
        # cấu hình custom styles cho button thành công
        style.configure("Success.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=(15, 8),
                       background="#B2B0E8",
                       foreground="black")
        
        # cấu hình custom styles cho button thất bại
        style.configure("Danger.TButton",
                       font=("Segoe UI", 9, "bold"),
                       padding=(10, 5),
                       background="#B2B0E8",
                       foreground="black")
        
        # cấu hình custom styles cho button quay lại
        style.configure("Back.TButton",
                       font=("Segoe UI", 10),
                       padding=(12, 6),
                       background="#B2B0E8",
                       foreground="black")

    def cn_khoi_tao_man_hinh_them_mon_hoc(self):
        self.cn_khoi_tao_header()
        self.cn_khoi_tao_body()
        self.cn_hien_thi_danh_sach_mon_hoc()

    def cn_khoi_tao_header(self):
        title_frame = tk.Frame(self, bg="#f0f2f5", height=80)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        title_frame.grid_propagate(False)
        
        title_label = ttk.Label(title_frame, text="📚 Quản lý Môn học", style="Title.TLabel")
        title_label.pack(expand=True)
        
        back_frame = tk.Frame(self, bg="#f0f2f5")
        back_frame.grid(row=1, column=0, pady=(0, 20), sticky="w")
        
        nut_tro_lai = ttk.Button(back_frame, text="← Trở lại màn hình chính", 
                                style="Back.TButton",
                                command=self.cn_tro_lai_man_hinh_chinh)
        nut_tro_lai.pack()

    def cn_khoi_tao_body(self):
        input_frame = tk.Frame(self, bg="white", relief="flat", bd=0)
        input_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 20))
        input_frame.configure(highlightbackground="#e1e8ed", highlightthickness=1)
        
        inner_frame = tk.Frame(input_frame, bg="white", padx=20, pady=20)
        inner_frame.pack(fill="x", expand=True)
        
        subject_label = ttk.Label(inner_frame, text="Tên môn học:", style="Header.TLabel")
        subject_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        entry_frame = tk.Frame(inner_frame, bg="white")
        entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        entry = ttk.Entry(entry_frame, textvariable=self.mon_hoc, 
                         font=("Segoe UI", 11),
                         width=40)
        entry.pack(fill="x", expand=True)
        
        button_frame = tk.Frame(inner_frame, bg="white")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        them_button = ttk.Button(button_frame, text="➕ Thêm môn học", 
                                style="Success.TButton",
                                command=self.cn_them_mon_hoc)
        them_button.pack(side="left", expand=True)

    def cn_tro_lai_man_hinh_chinh(self):
        if self.cn_tao_man_hinh_chinh:
            self.destroy()  # xóa frame hiện tại
            self.cn_tao_man_hinh_chinh()  # tạo lại màn hình chính
        else:
            messagebox.showwarning("Cảnh báo", "Không thể trở lại màn hình chính")

    def cn_them_mon_hoc(self):
        mon_hoc = self.mon_hoc.get()

        # Kiểm tra xem môn học có rỗng không
        if mon_hoc.strip() == "":
            messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu!")
            return

        # Kiểm tra xem folder mon_hoc có tồn tại chưa
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                # Kiểm tra xem môn học đã tồn tại chưa
                if mon_hoc in data.get("mon_hoc", []):
                    messagebox.showwarning("Cảnh báo", "Môn học này đã tồn tại!")
                    return
                data["mon_hoc"].append(mon_hoc)

        except (FileNotFoundError, json.JSONDecodeError):
            data = {"mon_hoc": [mon_hoc]}

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Thành công", "Môn học đã được thêm thành công")
            self.mon_hoc.set("")
            # hiển thị lại danh sách môn học
            self.cn_load_mon_hoc()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {str(e)}")

    def cn_hien_thi_danh_sach_mon_hoc(self):
        # kiểm tra xem list_frame đã tồn tại chưa
        if hasattr(self, 'list_frame'):
            self.list_frame.destroy()
            
        # tạo một frame cho danh sách môn học
        self.list_frame = tk.Frame(self, bg="white", relief="flat", bd=0)
        self.list_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10)
        self.list_frame.configure(highlightbackground="#e1e8ed", highlightthickness=1)
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)

        # header cho danh sách môn học
        header_frame = tk.Frame(self.list_frame, bg="#f8f9fa", height=40)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 0))
        header_frame.grid_propagate(False)
        
        header_label = ttk.Label(header_frame, text="📋 Danh sách môn học", 
                                style="Header.TLabel")
        header_label.pack(side="left", padx=(0, 10))
        
        # label số lượng môn học
        self.count_label = ttk.Label(header_frame, text="", 
                                    font=("Segoe UI", 9),
                                    foreground="#7f8c8d",
                                    background="#f8f9fa")
        self.count_label.pack(side="right")

        # tạo một canvas cho danh sách môn học
        canvas_frame = tk.Frame(self.list_frame, bg="white")
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=15)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.subject_list_frame = tk.Frame(canvas, bg="white")                 

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # cấu hình canvas
        canvas.create_window((0, 0), window=self.subject_list_frame, anchor="nw")
        self.subject_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.cn_load_mon_hoc()

    def cn_load_mon_hoc(self):
        # xóa các dữ liệu đã tồn tại trong subject_list_frame
        for widget in self.subject_list_frame.winfo_children():
            widget.destroy()

        self.subject_list = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.subject_list = data["mon_hoc"]

                # cập nhật label số lượng môn học
                count_text = f"Tổng cộng: {len(self.subject_list)} môn học"
                if hasattr(self, 'count_label'):
                    self.count_label.configure(text=count_text)

                for i, mon_hoc in enumerate(self.subject_list):
                    # tạo một frame cho mỗi môn học
                    subject_frame = tk.Frame(self.subject_list_frame, bg="white", 
                                           relief="flat", bd=0)
                    subject_frame.pack(fill="x", padx=5, pady=3)
                    subject_frame.configure(highlightbackground="#ecf0f1", highlightthickness=1)
                    
                    # thêm hiệu ứng hover
                    def on_enter(e, frame=subject_frame):
                        frame.configure(bg="#f8f9fa")
                    
                    def on_leave(e, frame=subject_frame):
                        frame.configure(bg="white")
                    
                    subject_frame.bind("<Enter>", on_enter)
                    subject_frame.bind("<Leave>", on_leave)

                    number_label = tk.Label(subject_frame, text=f"{i+1}.", 
                                          font=("Segoe UI", 10, "bold"),
                                          fg="#34495e", bg="white")
                    number_label.pack(side="left", padx=(15, 10), pady=10)
                    
                    subject_label = tk.Label(subject_frame, text=f"{mon_hoc}",
                                           font=("Segoe UI", 11),
                                           fg="#2c3e50", bg="white",
                                           anchor="w")
                    subject_label.pack(side="left", fill="x", expand=True, pady=10)
                    
                    # bind hover effects to label
                    subject_label.bind("<Enter>", on_enter)
                    subject_label.bind("<Leave>", on_leave)

                    xoa_btn = ttk.Button(subject_frame, text="🗑️ Xóa",
                                        style="Danger.TButton",
                                        command=lambda w=mon_hoc: self.cn_xoa_mon_hoc(w))
                    xoa_btn.pack(side="right", padx=(5, 15), pady=10)

                    # bind double-click để xóa
                    subject_label.bind("<Double-Button-1>", lambda e, w=mon_hoc: self.cn_xoa_mon_hoc(w))

        except FileNotFoundError:
            # file không tồn tại, điều này là ổn
            if hasattr(self, 'count_label'):
                self.count_label.configure(text="Chưa có môn học nào")

    def cn_xoa_mon_hoc(self, mon_hoc):
        # yêu cầu xác nhận trước khi xóa
        result = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa môn học '{mon_hoc}'?")
        if not result:
            return
            
        try:
            # xóa môn học khỏi subject_list
            self.subject_list.remove(mon_hoc)

            # lưu lại subject_list
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump({"mon_hoc": self.subject_list}, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Thành công", f"Đã xóa môn học '{mon_hoc}'")
            # hiển thị lại subject_list
            self.cn_load_mon_hoc()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa môn học: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý Môn học - Hệ thống học tập")
    root.geometry("800x700")
    root.configure(bg="#f0f2f5")
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    man_hinh_them_mon_hoc = man_hinh_them_mon_hoc(root)
    root.mainloop()
