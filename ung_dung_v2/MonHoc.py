from tkinter import *
import json
import os
import tkinter.ttk as ttk

# File path for storing subjects data
SUBJECTS_FILE = "./du_lieu/mon_hoc.json"

def hien_thi():
    create_frame()

def create_frame():
    top = Toplevel()
    top.title("Quản lý môn học")
    top.geometry("800x600")
    top.resizable(False, False)

    # Center the window
    top.transient()
    top.grab_set()

    # Header
    header_frame = Frame(top)
    header_frame.pack(fill=X, padx=20, pady=(20, 10))
    
    label = Label(header_frame, text="Quản lý môn học", font=("Arial", 16, "bold"))
    label.pack()

    # Class selection section
    class_frame = Frame(top)
    class_frame.pack(fill=X, padx=20, pady=10)
    
    Label(class_frame, text="Chọn lớp học:", font=("Arial", 12)).pack(side=LEFT)
    
    class_var = StringVar()
    class_combobox = ttk.Combobox(class_frame, textvariable=class_var, width=20, font=("Arial", 12))
    class_combobox.pack(side=LEFT, padx=(10, 10))
    
    refresh_class_btn = Button(class_frame, text="Làm mới", 
                              command=lambda: load_classes(class_combobox),
                              width=10, height=1, font=("Arial", 10))
    refresh_class_btn.pack(side=LEFT)

    # Input section for adding new subject
    input_frame = Frame(top)
    input_frame.pack(fill=X, padx=20, pady=10)
    
    Label(input_frame, text="Tên môn học:", font=("Arial", 12)).pack(side=LEFT)
    
    subject_entry = Entry(input_frame, width=30, font=("Arial", 12))
    subject_entry.pack(side=LEFT, padx=(10, 10))
    
    add_button = Button(input_frame, text="Thêm", 
                       command=lambda: add_subject(subject_entry, top, class_var.get()),
                       width=10, height=1, font=("Arial", 10))
    add_button.pack(side=LEFT)

    # List section with scrollbar
    list_frame = Frame(top)
    list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    Label(list_frame, text="Danh sách môn học:", font=("Arial", 12, "bold")).pack(anchor=W)
    
    # Create canvas with scrollbar for custom subject items
    canvas_frame = Frame(list_frame)
    canvas_frame.pack(fill=BOTH, expand=True, pady=(5, 0))
    
    canvas = Canvas(canvas_frame)
    scrollbar = Scrollbar(canvas_frame, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    # Store the scrollable frame for later use
    top.scrollable_frame = scrollable_frame
    top.class_var = class_var
    
    # Load classes and subjects
    load_classes(class_combobox)
    
    # Bind class selection change
    class_combobox.bind("<<ComboboxSelected>>", lambda e: load_subjects(top))
    
    # Close button
    close_btn = Button(top, text="Đóng", command=top.destroy,
                       width=10, height=1, font=("Arial", 10))
    close_btn.pack(pady=20)

def load_classes(combobox):
    """Load existing classes into the combobox"""
    classes = []
    if os.path.exists("du_lieu/lop.json"):
        try:
            with open("du_lieu/lop.json", 'r', encoding='utf-8') as file:
                classes = json.load(file)
        except:
            classes = []
    
    combobox['values'] = classes
    if classes:
        combobox.set(classes[0])

def load_subjects(top):
    """Load subjects for the selected class"""
    class_name = top.class_var.get()
    if not class_name:
        return
    
    scrollable_frame = top.scrollable_frame
    
    # Clear existing items
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    if os.path.exists(SUBJECTS_FILE):
        try:
            with open(SUBJECTS_FILE, 'r', encoding='utf-8') as file:
                all_subjects = json.load(file)
                class_subjects = all_subjects.get(class_name, [])
                for subject in class_subjects:
                    create_subject_item(scrollable_frame, subject, top, class_name)
        except:
            pass

def save_subjects(all_subjects):
    """Save subjects data to JSON file"""
    try:
        os.makedirs(os.path.dirname(SUBJECTS_FILE), exist_ok=True)
        with open(SUBJECTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(all_subjects, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving subjects: {e}")
        return False

def add_subject(entry_widget, top, class_name):
    """Add a new subject to the selected class"""
    if not class_name:
        show_message("Lỗi", "Vui lòng chọn lớp học trước!")
        return
    
    subject_name = entry_widget.get().strip()
    
    if not subject_name:
        show_message("Lỗi", "Vui lòng nhập tên môn học!")
        return
    
    # Load current subjects
    all_subjects = {}
    if os.path.exists(SUBJECTS_FILE):
        try:
            with open(SUBJECTS_FILE, 'r', encoding='utf-8') as file:
                all_subjects = json.load(file)
        except:
            all_subjects = {}
    
    # Initialize class if it doesn't exist
    if class_name not in all_subjects:
        all_subjects[class_name] = []
    
    # Check if subject already exists in this class
    if subject_name in all_subjects[class_name]:
        show_message("Lỗi", "Môn học này đã tồn tại trong lớp này!")
        return
    
    # Add new subject
    all_subjects[class_name].append(subject_name)
    
    # Save to file
    if save_subjects(all_subjects):
        # Add to display
        create_subject_item(top.scrollable_frame, subject_name, top, class_name)
        # Clear input field
        entry_widget.delete(0, END)
        show_message("Thành công", f"Đã thêm môn học: {subject_name}")
    else:
        show_message("Lỗi", "Không thể lưu môn học!")

def delete_subject(subject_name, top, class_name):
    """Delete a specific subject from the class"""
    if show_confirm("Xác nhận", f"Bạn có chắc muốn xóa môn học '{subject_name}'?"):
        # Load current subjects
        all_subjects = {}
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, 'r', encoding='utf-8') as file:
                    all_subjects = json.load(file)
            except:
                all_subjects = {}
        
        # Remove the subject
        if class_name in all_subjects and subject_name in all_subjects[class_name]:
            all_subjects[class_name].remove(subject_name)
            
            # Save to file
            if save_subjects(all_subjects):
                # Refresh display
                load_subjects(top)
                show_message("Thành công", f"Đã xóa môn học: {subject_name}")
            else:
                show_message("Lỗi", "Không thể xóa môn học!")

def create_subject_item(parent_frame, subject_name, top, class_name):
    """Creates a custom widget for a subject item with a delete button."""
    subject_frame = Frame(parent_frame)
    subject_frame.pack(fill=X, pady=2, padx=5)
    
    # Subject name label
    subject_label = Label(subject_frame, text=subject_name, font=("Arial", 11))
    subject_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))
    
    # Delete button
    delete_button = Button(subject_frame, text="Xóa", 
                           command=lambda: delete_subject(subject_name, top, class_name),
                           width=5, height=1, font=("Arial", 9), 
                           bg="#ff6b6b", fg="white")
    delete_button.pack(side=RIGHT)

def show_message(title, message):
    """Show a simple message dialog"""
    top = Toplevel()
    top.title(title)
    top.geometry("300x150")
    top.resizable(False, False)
    top.transient()
    top.grab_set()
    
    Label(top, text=message, font=("Arial", 11), wraplength=250).pack(expand=True, pady=20)
    
    Button(top, text="OK", command=top.destroy, width=10).pack(pady=10)

def show_confirm(title, message):
    """Show a confirmation dialog, returns True if user confirms"""
    result = [False]
    
    def confirm():
        result[0] = True
        top.destroy()
    
    def cancel():
        result[0] = False
        top.destroy()
    
    top = Toplevel()
    top.title(title)
    top.geometry("350x150")
    top.resizable(False, False)
    top.transient()
    top.grab_set()
    
    Label(top, text=message, font=("Arial", 11), wraplength=300).pack(expand=True, pady=20)
    
    button_frame = Frame(top)
    button_frame.pack(pady=10)
    
    Button(button_frame, text="Có", command=confirm, width=8).pack(side=LEFT, padx=5)
    Button(button_frame, text="Không", command=cancel, width=8).pack(side=LEFT, padx=5)
    
    top.wait_window()
    return result[0]