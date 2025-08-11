from tkinter import *
import json
import os

# File path for storing grades data
GRADES_FILE = "./du_lieu/lop.json"

def hien_thi():
    create_frame()

def create_frame():
    top = Toplevel()
    top.title("Quản lý lớp học")
    top.geometry("800x600")
    top.resizable(False, False)

    # Center the window
    top.transient() # chức năng: khi click vào các button khác thì window này vẫn hiện
    top.grab_set() # chức năng: khi click vào các button khác thì window này vẫn hiện

    # Header
    header_frame = Frame(top) # Frame là một khung chứa các widget
    header_frame.pack(fill=X, padx=20, pady=(20, 10))
    
    label = Label(header_frame, text="Quản lý lớp học", font=("Arial", 16, "bold"))
    label.pack()

    # Input section for adding new grade
    input_frame = Frame(top)
    input_frame.pack(fill=X, padx=20, pady=10)
    
    Label(input_frame, text="Tên lớp học:", font=("Arial", 12)).pack(side=LEFT)
    
    grade_entry = Entry(input_frame, width=30, font=("Arial", 12))
    grade_entry.pack(side=LEFT, padx=(10, 10))
    
    add_button = Button(input_frame, text="Thêm", 
                       command=lambda: add_grade(grade_entry, top),
                       width=10, height=1, font=("Arial", 10))
    add_button.pack(side=LEFT)

    # List section with scrollbar
    list_frame = Frame(top)
    list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    Label(list_frame, text="Danh sách lớp học:", font=("Arial", 12, "bold")).pack(anchor=W)
    
    # Create canvas with scrollbar for custom grade items
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
    
    # Load existing grades
    load_grades(top)
    
    # Close button
    close_btn = Button(top, text="Đóng", command=top.destroy,
                       width=10, height=1, font=("Arial", 10))
    close_btn.pack(pady=20)

def load_grades(top):
    """Load existing grades from JSON file and display in scrollable frame"""
    scrollable_frame = top.scrollable_frame
    
    # Clear existing items
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    if os.path.exists(GRADES_FILE):
        try:
            with open(GRADES_FILE, 'r', encoding='utf-8') as file:
                grades = json.load(file)
                for grade in grades:
                    create_grade_item(scrollable_frame, grade, top)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, start with empty list
            grades = []
    else:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(GRADES_FILE), exist_ok=True)
        grades = []
    
    return grades

def save_grades(grades):
    """Save grades list to JSON file"""
    try:
        with open(GRADES_FILE, 'w', encoding='utf-8') as file:
            json.dump(grades, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving grades: {e}")
        return False

def add_grade(entry_widget, top):
    """Add a new grade to the list and save to file"""
    grade_name = entry_widget.get().strip()
    
    if not grade_name:
        # Show error message if input is empty
        show_message("Lỗi", "Vui lòng nhập tên lớp học!")
        return
    
    # Load current grades to check for duplicates
    grades = []
    if os.path.exists(GRADES_FILE):
        try:
            with open(GRADES_FILE, 'r', encoding='utf-8') as file:
                grades = json.load(file)
        except:
            grades = []
    
    # Check if grade already exists
    if grade_name in grades:
        show_message("Lỗi", "Lớp học này đã tồn tại!")
        return
    
    # Add new grade
    grades.append(grade_name)
    
    # Save to file
    if save_grades(grades):
        # Add to display
        create_grade_item(top.scrollable_frame, grade_name, top)
        # Clear input field
        entry_widget.delete(0, END)
        show_message("Thành công", f"Đã thêm lớp học: {grade_name}")
    else:
        show_message("Lỗi", "Không thể lưu lớp học!")

def delete_grade(grade_name, top):
    """Delete a specific grade from the list"""
    # Confirm deletion
    if show_confirm("Xác nhận", f"Bạn có chắc muốn xóa lớp học '{grade_name}'?"):
        # Load current grades
        grades = []
        if os.path.exists(GRADES_FILE):
            try:
                with open(GRADES_FILE, 'r', encoding='utf-8') as file:
                    grades = json.load(file)
            except:
                grades = []
        
        # Remove the grade
        if grade_name in grades:
            grades.remove(grade_name)
            
            # Save to file
            if save_grades(grades):
                # Refresh display
                load_grades(top)
                show_message("Thành công", f"Đã xóa lớp học: {grade_name}")
            else:
                show_message("Lỗi", "Không thể xóa lớp học!")

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
    result = [False]  # Use list to store result
    
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

def create_grade_item(parent_frame, grade_name, top):
    """Creates a custom widget for a grade item with a delete button."""
    grade_frame = Frame(parent_frame)
    grade_frame.pack(fill=X, pady=2, padx=5)
    
    # Grade name label
    grade_label = Label(grade_frame, text=grade_name, font=("Arial", 11))
    grade_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))
    
    # Delete button
    delete_button = Button(grade_frame, text="Xóa", 
                           command=lambda: delete_grade(grade_name, top),
                           width=5, height=1, font=("Arial", 9), 
                           bg="#ff6b6b", fg="white")
    delete_button.pack(side=RIGHT)
