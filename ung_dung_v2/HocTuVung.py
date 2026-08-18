import json
import os
from datetime import datetime
import random
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from typing import List, Dict, Optional

from ung_dung_v2.LopHoc import create_frame

def hien_thi():
    create_frame()

def create_frame():
    top = tk.Toplevel()
    top.title("Học từ vựng")
    top.geometry("800x600")
    top.resizable(False, False)

    # Center the window
    top.transient()  # chức năng: khi click vào các button khác thì window này vẫn hiện
    top.grab_set()  # chức năng: khi click vào các button khác thì window này vẫn hiện

    # Header
    header_frame = Frame(top)  # Frame là một khung chứa các widget
    header_frame.pack(fill=X, padx=20, pady=(20, 10))

    label = Label(header_frame, text="Học từ vựng", font=("Arial", 16, "bold"))
    label.pack()

    # Hiển thị danh sách lớp
    hien_thi_danh_sach_lop(top)

def hien_thi_danh_sach_lop(top):
    """Hiển thị danh sách lớp"""
    # Xóa các widget cũ (trừ header)
    for widget in top.winfo_children():
        if widget != top.winfo_children()[0]:  # Giữ lại header
            widget.destroy()
    
    # Tạo frame cho danh sách lớp
    frame = Frame(top)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Tạo label cho tiêu đề
    label = Label(frame, text="Danh sách lớp", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    # Tạo danh sách lớp
    listbox = Listbox(frame, width=50, height=15, font=("Arial", 11))
    listbox.pack(pady=10)
    
    # Tải danh sách lớp từ file
    try:
        with open("du_lieu/lop.json", "r", encoding="utf-8") as f:
            lop_data = json.load(f)
        
        # Hiển thị danh sách lớp
        for lop in lop_data:
            lop_info = f"{lop.get('ten', '')} - {lop.get('mo_ta', '')}"
            listbox.insert(END, lop_info)
            # Lưu ID lớp vào listbox để sử dụng sau
            listbox.insert(END, f"ID: {lop.get('id', '')}")
            listbox.insert(END, "")  # Dòng trống để phân cách
        
        # Binding sự kiện double-click để chọn lớp
        listbox.bind('<Double-Button-1>', lambda event: chon_lop(top, listbox, lop_data))
        
    except FileNotFoundError:
        listbox.insert(END, "Không tìm thấy file dữ liệu lớp")
    except Exception as e:
        listbox.insert(END, f"Lỗi khi tải dữ liệu: {e}")
    
    # Nút quay lại
    btn_back = Button(frame, text="Quay lại", 
                      command=lambda: top.destroy(),
                      width=15, height=2, font=("Arial", 10))
    btn_back.pack(pady=20)

def chon_lop(top, listbox, lop_data):
    """Xử lý khi chọn lớp"""
    try:
        # Lấy index được chọn
        selection = listbox.curselection()
        if not selection:
            return
        
        # Tìm lớp được chọn
        selected_index = selection[0]
        lop_index = selected_index // 3  # Mỗi lớp chiếm 3 dòng (tên, ID, trống)
        
        if lop_index < len(lop_data):
            lop_duoc_chon = lop_data[lop_index]
            # Hiển thị danh sách môn học của lớp này
            hien_thi_danh_sach_mon_hoc(top, lop_duoc_chon)
    except Exception as e:
        print(f"Lỗi khi chọn lớp: {e}")

def hien_thi_danh_sach_mon_hoc(top, lop_duoc_chon):
    """Hiển thị danh sách môn học của lớp được chọn"""
    # Xóa các widget cũ (trừ header)
    for widget in top.winfo_children():
        if widget != top.winfo_children()[0]:  # Giữ lại header
            widget.destroy()
    
    # Tạo frame cho danh sách môn học
    frame = Frame(top)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Tạo label cho tiêu đề
    label = Label(frame, text=f"Môn học của lớp: {lop_duoc_chon.get('ten', '')}", 
                  font=("Arial", 14, "bold"))
    label.pack(pady=10)

    # Tạo danh sách môn học
    listbox = Listbox(frame, width=50, height=15, font=("Arial", 11))
    listbox.pack(pady=10)
    
    # Tải danh sách môn học từ file
    try:
        with open("du_lieu/mon_hoc.json", "r", encoding="utf-8") as f:
            mon_hoc_data = json.load(f)
        
        # Lọc môn học theo lớp
        mon_hoc_cua_lop = []
        for mon in mon_hoc_data:
            if mon.get('lop_id') == lop_duoc_chon.get('id'):
                mon_hoc_cua_lop.append(mon)
        
        if mon_hoc_cua_lop:
            # Hiển thị danh sách môn học
            for mon in mon_hoc_cua_lop:
                mon_info = f"{mon.get('ten', '')} - {mon.get('mo_ta', '')}"
                listbox.insert(END, mon_info)
                listbox.insert(END, f"ID: {mon.get('id', '')}")
                listbox.insert(END, "")  # Dòng trống để phân cách
            
            # Binding sự kiện double-click để chọn môn học
            listbox.bind('<Double-Button-1>', 
                        lambda event: chon_mon_hoc(top, listbox, mon_hoc_cua_lop, lop_duoc_chon))
        else:
            listbox.insert(END, "Không có môn học nào trong lớp này")
        
    except FileNotFoundError:
        listbox.insert(END, "Không tìm thấy file dữ liệu môn học")
    except Exception as e:
        listbox.insert(END, f"Lỗi khi tải dữ liệu: {e}")
    
    # Nút quay lại danh sách lớp
    btn_back = Button(frame, text="← Quay lại danh sách lớp", 
                      command=lambda: hien_thi_danh_sach_lop(top),
                      width=20, height=2, font=("Arial", 10))
    btn_back.pack(pady=20)

def chon_mon_hoc(top, listbox, mon_hoc_data, lop_duoc_chon):
    """Xử lý khi chọn môn học"""
    try:
        # Lấy index được chọn
        selection = listbox.curselection()
        if not selection:
            return
        
        # Tìm môn học được chọn
        selected_index = selection[0]
        mon_index = selected_index // 3  # Mỗi môn học chiếm 3 dòng (tên, ID, trống)
        
        if mon_index < len(mon_hoc_data):
            mon_duoc_chon = mon_hoc_data[mon_index]
            # Hiển thị giao diện học từ vựng
            hien_thi_giao_dien_hoc_tu_vung(top, mon_duoc_chon, lop_duoc_chon)
    except Exception as e:
        print(f"Lỗi khi chọn môn học: {e}")

def hien_thi_giao_dien_hoc_tu_vung(top, mon_duoc_chon, lop_duoc_chon):
    """Hiển thị giao diện học từ vựng cho môn học được chọn"""
    # Xóa các widget cũ (trừ header)
    for widget in top.winfo_children():
        if widget != top.winfo_children()[0]:  # Giữ lại header
            widget.destroy()
    
    # Tạo frame chính
    frame = Frame(top)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Tạo label cho tiêu đề
    label = Label(frame, text=f"Học từ vựng: {mon_duoc_chon.get('ten', '')}", 
                  font=("Arial", 14, "bold"))
    label.pack(pady=10)
    
    # Frame chọn loại bài tập
    bai_tap_frame = LabelFrame(frame, text="Chọn loại bài tập", font=("Arial", 12, "bold"))
    bai_tap_frame.pack(fill=X, pady=(20, 10))
    
    bai_tap_var = tk.StringVar(value="chon_dap_an")
    tk.Radiobutton(bai_tap_frame, text="Chọn đáp án đúng", variable=bai_tap_var, 
                   value="chon_dap_an").pack(anchor=W, padx=20, pady=5)
    tk.Radiobutton(bai_tap_frame, text="Điền từ vào chỗ trống", variable=bai_tap_var, 
                   value="dien_tu").pack(anchor=W, padx=20, pady=5)
    
    # Frame số lượng câu hỏi
    so_cau_frame = LabelFrame(frame, text="Số lượng câu hỏi", font=("Arial", 12, "bold"))
    so_cau_frame.pack(fill=X, pady=(10, 20))
    
    so_cau_var = tk.IntVar(value=10)
    tk.Scale(so_cau_frame, from_=5, to=20, orient=HORIZONTAL, variable=so_cau_var).pack(pady=10)
    
    # Nút bắt đầu học
    btn_bat_dau = Button(frame, text="Bắt đầu học", 
                         command=lambda: bat_dau_hoc(top, mon_duoc_chon, lop_duoc_chon, 
                                                   bai_tap_var.get(), so_cau_var.get()),
                         width=20, height=2, font=("Arial", 12), bg="#4CAF50", fg="white")
    btn_bat_dau.pack(pady=20)
    
    # Frame thống kê
    thong_ke_frame = LabelFrame(frame, text="Thống kê học tập", font=("Arial", 12, "bold"))
    thong_ke_frame.pack(fill=X, pady=(20, 0))
    
    # Hiển thị thống kê
    hien_thi_thong_ke(thong_ke_frame, mon_duoc_chon.get('id', ''))
    
    # Nút quay lại danh sách môn học
    btn_back = Button(frame, text="← Quay lại danh sách môn học", 
                      command=lambda: hien_thi_danh_sach_mon_hoc(top, lop_duoc_chon),
                      width=20, height=2, font=("Arial", 10))
    btn_back.pack(pady=20)

def hien_thi_thong_ke(parent_frame, mon_hoc_id):
    """Hiển thị thống kê học tập"""
    try:
        # Tạo instance HocTuVung để lấy thống kê
        hoc_tu_vung = HocTuVung()
        thong_ke = hoc_tu_vung.lay_thong_ke_hoc_tap(mon_hoc_id)
        
        # Hiển thị thống kê
        stats_text = f"""
Tổng từ vựng: {thong_ke['tong_tu_vung']}
Đã học: {thong_ke['da_hoc']}
Chưa học: {thong_ke['chua_hoc']}
Tỷ lệ đúng: {thong_ke['ti_le_dung']}%
Điểm số: {thong_ke['diem_so']}
Ngày học liên tiếp: {thong_ke['ngay_hoc_lien_tiep']}
        """
        
        label_stats = Label(parent_frame, text=stats_text, font=("Arial", 10), justify=LEFT)
        label_stats.pack(pady=10)
    except Exception as e:
        label_error = Label(parent_frame, text=f"Không thể tải thống kê: {e}", fg="red")
        label_error.pack(pady=10)

def bat_dau_hoc(top, mon_duoc_chon, lop_duoc_chon, loai_bai_tap, so_cau):
    """Bắt đầu học từ vựng"""
    try:
        hoc_tu_vung = HocTuVung()
        
        # Tạo bài tập
        bai_tap = hoc_tu_vung.tao_bai_tap(mon_duoc_chon.get('id', ''), loai_bai_tap, so_cau)
        
        if not bai_tap:
            tk.messagebox.showinfo("Thông báo", "Không có từ vựng nào để học!")
            return
        
        # Hiển thị giao diện học tập
        hien_thi_giao_dien_hoc_tap(top, bai_tap, hoc_tu_vung, mon_duoc_chon, lop_duoc_chon)
        
    except Exception as e:
        tk.messagebox.showerror("Lỗi", f"Không thể tạo bài tập: {e}")

def hien_thi_giao_dien_hoc_tap(top, bai_tap, hoc_tu_vung, mon_duoc_chon, lop_duoc_chon):
    """Hiển thị giao diện học tập"""
    # Xóa các widget cũ (trừ header)
    for widget in top.winfo_children():
        if widget != top.winfo_children()[0]:  # Giữ lại header
            widget.destroy()
    
    # Tạo frame chính
    frame = Frame(top)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Biến theo dõi
    current_question = 0
    score = 0
    
    # Label hiển thị câu hỏi
    question_label = Label(frame, text="", font=("Arial", 14), wraplength=600)
    question_label.pack(pady=20)
    
    # Frame đáp án
    answer_frame = Frame(frame)
    answer_frame.pack(pady=20)
    
    # Label kết quả
    result_label = Label(frame, text="", font=("Arial", 12, "bold"))
    result_label.pack(pady=20)
    
    # Nút tiếp theo
    next_button = Button(frame, text="Câu tiếp theo", 
                        command=lambda: next_question(), 
                        width=20, height=2, font=("Arial", 12))
    next_button.pack(pady=20)
    
    def display_question():
        """Hiển thị câu hỏi hiện tại"""
        nonlocal current_question
        if current_question < len(bai_tap):
            cau_hoi = bai_tap[current_question]
            question_label.config(text=cau_hoi['cau_hoi'])
            
            # Xóa đáp án cũ
            for widget in answer_frame.winfo_children():
                widget.destroy()
            
            # Tạo đáp án mới
            if cau_hoi['loai'] == 'chon_dap_an':
                for i, dap_an in enumerate(cau_hoi['dap_an']):
                    btn = Button(answer_frame, text=dap_an, 
                               command=lambda da=dap_an: check_answer(da),
                               width=30, height=2, font=("Arial", 10))
                    btn.pack(pady=5)
            else:  # dien_tu
                entry = Entry(answer_frame, font=("Arial", 12), width=30)
                entry.pack(pady=10)
                
                btn_check = Button(answer_frame, text="Kiểm tra", 
                                 command=lambda: check_answer(entry.get()),
                                 width=20, height=2, font=("Arial", 10))
                btn_check.pack(pady=5)
            
            result_label.config(text="")
            next_button.config(state=DISABLED)
        else:
            # Kết thúc bài tập
            show_final_results()
    
    def check_answer(answer):
        """Kiểm tra đáp án"""
        nonlocal score
        cau_hoi = bai_tap[current_question]
        is_correct = hoc_tu_vung.kiem_tra_dap_an(cau_hoi, answer)
        
        if is_correct:
            score += 1
            result_label.config(text="✓ Đúng rồi!", fg="green")
            # Cập nhật tiến độ
            hoc_tu_vung.cap_nhat_tien_do(cau_hoi['tu_goc'], True, mon_duoc_chon.get('id', ''))
        else:
            result_label.config(text=f"✗ Sai rồi! Đáp án đúng: {cau_hoi['dap_an_dung']}", fg="red")
            # Cập nhật tiến độ
            hoc_tu_vung.cap_nhat_tien_do(cau_hoi['tu_goc'], False, mon_duoc_chon.get('id', ''))
        
        next_button.config(state=NORMAL)
    
    def next_question():
        """Chuyển sang câu hỏi tiếp theo"""
        nonlocal current_question
        current_question += 1
        display_question()
    
    def show_final_results():
        """Hiển thị kết quả cuối cùng"""
        # Xóa giao diện cũ
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Hiển thị kết quả
        result_text = f"""
Kết quả học tập:
Điểm số: {score}/{len(bai_tap)}
Tỷ lệ đúng: {(score/len(bai_tap)*100):.1f}%
        """
        
        Label(frame, text=result_text, font=("Arial", 16, "bold")).pack(pady=50)
        
        # Nút quay lại
        Button(frame, text="Quay lại giao diện học", 
               command=lambda: hien_thi_giao_dien_hoc_tu_vung(top, mon_duoc_chon, lop_duoc_chon),
               width=20, height=2, font=("Arial", 12)).pack(pady=20)
    
    # Hiển thị câu hỏi đầu tiên
    display_question()

# Import HocTuVung class để sử dụng các phương thức
class HocTuVung:
    """
    Lớp quản lý việc học từ vựng
    """
    
    def __init__(self, du_lieu_path: str = "du_lieu"):
        self.du_lieu_path = du_lieu_path
        self.tu_vung_file = os.path.join(du_lieu_path, "tu_vung.json")
        self.progress_file = os.path.join(du_lieu_path, "learning_progress.json")
        self.tu_vung_data = self._load_tu_vung()
        self.progress_data = self._load_progress()
    
    def _load_tu_vung(self) -> Dict:
        """Tải dữ liệu từ vựng từ file JSON"""
        try:
            if os.path.exists(self.tu_vung_file):
                with open(self.tu_vung_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu từ vựng: {e}")
            return {}
    
    def _load_progress(self) -> Dict:
        """Tải dữ liệu tiến độ học từ file JSON"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"tu_vung": {}, "ngay_hoc": {}, "diem_so": {}}
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tiến độ: {e}")
            return {"tu_vung": {}, "ngay_hoc": {}, "diem_so": {}}
    
    def _save_progress(self):
        """Lưu dữ liệu tiến độ học vào file JSON"""
        try:
            os.makedirs(self.du_lieu_path, exist_ok=True)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu tiến độ: {e}")
    
    def lay_tu_vung_theo_mon(self, mon_hoc_id: str) -> List[Dict]:
        """Lấy danh sách từ vựng theo môn học"""
        if mon_hoc_id in self.tu_vung_data:
            return self.tu_vung_data[mon_hoc_id]
        return []
    
    def lay_thong_ke_hoc_tap(self, mon_hoc_id: str = "") -> Dict:
        """Lấy thống kê học tập"""
        thong_ke = {
            'tong_tu_vung': 0,
            'da_hoc': 0,
            'chua_hoc': 0,
            'ti_le_dung': 0,
            'diem_so': 0,
            'ngay_hoc_lien_tiep': 0
        }
        
        if mon_hoc_id:
            tu_vung_mon = self.lay_tu_vung_theo_mon(mon_hoc_id)
            thong_ke['tong_tu_vung'] = len(tu_vung_mon)
            
            for tu in tu_vung_mon:
                tu_id = tu.get('id', '')
                if tu_id in self.progress_data['tu_vung']:
                    thong_ke['da_hoc'] += 1
                    progress = self.progress_data['tu_vung'][tu_id]
                    tong_lan = progress['so_lan_hoc']
                    dung_lan = progress['so_lan_dung']
                    if tong_lan > 0:
                        thong_ke['ti_le_dung'] += dung_lan / tong_lan
            
            if thong_ke['da_hoc'] > 0:
                thong_ke['ti_le_dung'] = round(thong_ke['ti_le_dung'] / thong_ke['da_hoc'] * 100, 2)
            
            thong_ke['chua_hoc'] = thong_ke['tong_tu_vung'] - thong_ke['da_hoc']
            thong_ke['diem_so'] = self.progress_data['diem_so'].get(mon_hoc_id, 0)
        
        return thong_ke
    
    def tao_bai_tap(self, mon_hoc_id: str, loai_bai_tap: str = "chon_dap_an", so_cau: int = 10) -> List[Dict]:
        """Tạo bài tập học từ vựng"""
        tu_vung_mon = self.lay_tu_vung_theo_mon(mon_hoc_id)
        if len(tu_vung_mon) < so_cau:
            so_cau = len(tu_vung_mon)
        
        tu_vung_chon = random.sample(tu_vung_mon, so_cau)
        bai_tap = []
        
        for tu in tu_vung_chon:
            if loai_bai_tap == "chon_dap_an":
                cau_hoi = self._tao_cau_hoi_chon_dap_an(tu, tu_vung_mon)
            elif loai_bai_tap == "dien_tu":
                cau_hoi = self._tao_cau_hoi_dien_tu(tu)
            else:
                cau_hoi = self._tao_cau_hoi_chon_dap_an(tu, tu_vung_mon)
            
            bai_tap.append(cau_hoi)
        
        return bai_tap
    
    def _tao_cau_hoi_chon_dap_an(self, tu_dung: Dict, tat_ca_tu: List[Dict]) -> Dict:
        """Tạo câu hỏi chọn đáp án đúng"""
        dap_an_dung = tu_dung.get('nghia', '')
        dap_an_sai = []
        
        # Lấy 3 đáp án sai ngẫu nhiên
        tu_khac = [tu for tu in tat_ca_tu if tu.get('id') != tu_dung.get('id')]
        if len(tu_khac) >= 3:
            tu_sai = random.sample(tu_khac, 3)
            dap_an_sai = [tu.get('nghia', '') for tu in tu_sai]
        
        # Tạo danh sách đáp án và xáo trộn
        dap_an = [dap_an_dung] + dap_an_sai
        random.shuffle(dap_an)
        
        return {
            'cau_hoi': f"Từ '{tu_dung.get('tu', '')}' có nghĩa là gì?",
            'dap_an': dap_an,
            'dap_an_dung': dap_an_dung,
            'tu_goc': tu_dung.get('tu', ''),
            'loai': 'chon_dap_an'
        }
    
    def _tao_cau_hoi_dien_tu(self, tu: Dict) -> Dict:
        """Tạo câu hỏi điền từ vào chỗ trống"""
        tu_goc = tu.get('tu', '')
        nghia = tu.get('nghia', '')
        
        return {
            'cau_hoi': f"Điền từ thích hợp: {nghia}",
            'dap_an_dung': tu_goc,
            'tu_goc': tu_goc,
            'nghia': nghia,
            'loai': 'dien_tu'
        }
    
    def kiem_tra_dap_an(self, cau_hoi: Dict, dap_an_nguoi_dung: str) -> bool:
        """Kiểm tra đáp án của người dùng"""
        if cau_hoi['loai'] == 'chon_dap_an':
            return dap_an_nguoi_dung == cau_hoi['dap_an_dung']
        elif cau_hoi['loai'] == 'dien_tu':
            return dap_an_nguoi_dung.lower().strip() == cau_hoi['dap_an_dung'].lower().strip()
        return False
    
    def cap_nhat_tien_do(self, tu_id: str, ket_qua: bool, mon_hoc_id: str = ""):
        """Cập nhật tiến độ học của từ vựng"""
        ngay_hien_tai = datetime.now().date().isoformat()
        
        if tu_id not in self.progress_data['tu_vung']:
            self.progress_data['tu_vung'][tu_id] = {
                'so_lan_hoc': 0,
                'so_lan_dung': 0,
                'so_lan_sai': 0,
                'lan_hoc_cuoi': '',
                'do_kho': 1
            }
        
        progress = self.progress_data['tu_vung'][tu_id]
        progress['so_lan_hoc'] += 1
        progress['lan_hoc_cuoi'] = ngay_hien_tai
        
        if ket_qua:
            progress['so_lan_dung'] += 1
            progress['do_kho'] = max(0.5, progress['do_kho'] - 0.1)
        else:
            progress['so_lan_sai'] += 1
            progress['do_kho'] = min(3.0, progress['do_kho'] + 0.2)
        
        # Cập nhật ngày học
        if ngay_hien_tai not in self.progress_data['ngay_hoc']:
            self.progress_data['ngay_hoc'][ngay_hien_tai] = 0
        self.progress_data['ngay_hoc'][ngay_hien_tai] += 1
        
        # Cập nhật điểm số
        if mon_hoc_id not in self.progress_data['diem_so']:
            self.progress_data['diem_so'][mon_hoc_id] = 0
        
        if ket_qua:
            self.progress_data['diem_so'][mon_hoc_id] += 10
        else:
            self.progress_data['diem_so'][mon_hoc_id] = max(0, self.progress_data['diem_so'][mon_hoc_id] - 2)
        
        self._save_progress() 
    
