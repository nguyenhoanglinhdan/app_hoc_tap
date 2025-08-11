import tkinter as tk
from tkinter import *
import LopHoc, MonHoc, TuVung
import json
import os
import random
from tkinter import ttk

# File path for storing learning progress
PROGRESS_FILE = "./du_lieu/learning_progress.json"

def create_menu(window):
    menu = Menu(window)
    window.config(menu=menu)

    file_menu = Menu(menu)
    menu.add_cascade(label="Lựa chọn", menu=file_menu)
    file_menu.add_command(label="Môn học", command=lambda: LopHoc.create_frame(window))
    file_menu.add_command(label="Lớp học", command=lambda: MonHoc.create_frame(window))
    file_menu.add_command(label="Từ vựng", command=lambda: TuVung.create_frame(window))
    file_menu.add_separator()
    file_menu.add_command(label="Kết thúc", command=window.destroy)


def create_header(window):
    header = Frame(window)
    header.pack(fill=X, pady=10, padx=10)

    label = Label(header, text="App học từ vựng", font=("Arial", 16, "bold"))
    label.pack(expand=True, side=LEFT)

    return header


def create_buttons(window):
    button_frame = Frame(window)
    button_frame.pack(pady=20)
    
    # Button 1 - Quản lý lớp học
    btn_lop_hoc = Button(button_frame, text="Quản lý lớp học",
                         command=lambda: LopHoc.hien_thi(),
                         width=20, height=2, font=("Arial", 12))
    btn_lop_hoc.pack(side=LEFT, padx=10)
    
    # Button 2 - Quản lý môn học
    btn_mon_hoc = Button(button_frame, text="Quản lý môn học",
                         command=lambda: MonHoc.hien_thi(),
                         width=20, height=2, font=("Arial", 12))
    btn_mon_hoc.pack(side=LEFT, padx=10)
    
    # Button 3 - Quản lý từ vựng
    btn_tu_vung = Button(button_frame, text="Quản lý từ vựng",
                          command=lambda: TuVung.hien_thi(),
                          width=20, height=2, font=("Arial", 12))
    btn_tu_vung.pack(side=RIGHT, padx=10)

def create_learning_section(window):
    """Create the vocabulary learning section with progress tracking"""
    learning_frame = Frame(window)
    learning_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Learning section header
    learning_header = Frame(learning_frame)
    learning_header.pack(fill=X, pady=(0, 15))
    
    Label(learning_header, text="Học từ vựng", font=("Arial", 14, "bold")).pack(side=LEFT)
    
    # Progress section
    progress_frame = Frame(learning_frame)
    progress_frame.pack(fill=X, pady=(0, 20))
    
    Label(progress_frame, text="Tiến độ học tập:", font=("Arial", 12)).pack(anchor=W)
    
    # Progress bar
    progress_var = DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=400)
    progress_bar.pack(fill=X, pady=(5, 5))
    
    # Progress percentage label
    progress_label = Label(progress_frame, text="0%", font=("Arial", 10))
    progress_label.pack(anchor=W)
    
    # Class and Subject selection for learning
    selection_frame = Frame(learning_frame)
    selection_frame.pack(fill=X, pady=(0, 20))
    
    # Class selection
    class_frame = Frame(selection_frame)
    class_frame.pack(fill=X, pady=(0, 10))
    
    Label(class_frame, text="Chọn lớp học:", font=("Arial", 11)).pack(side=LEFT)
    
    class_var = StringVar()
    class_combobox = ttk.Combobox(class_frame, textvariable=class_var, width=20, font=("Arial", 11))
    class_combobox.pack(side=LEFT, padx=(10, 10))
    
    # Subject selection
    subject_frame = Frame(selection_frame)
    subject_frame.pack(fill=X)
    
    Label(subject_frame, text="Chọn môn học:", font=("Arial", 11)).pack(side=LEFT)
    
    subject_var = StringVar()
    subject_combobox = ttk.Combobox(subject_frame, textvariable=subject_var, width=20, font=("Arial", 11))
    subject_combobox.pack(side=LEFT, padx=(10, 10))
    
    # Start learning button
    start_btn = Button(selection_frame, text="Bắt đầu học", 
                      command=lambda: start_learning(class_var.get(), subject_var.get(), window),
                      width=15, height=1, font=("Arial", 11), bg="#4CAF50", fg="white")
    start_btn.pack(side=RIGHT, padx=(20, 0))
    
    # Load classes and subjects
    load_classes_for_learning(class_combobox, subject_combobox)
    
    # Bind selection changes
    class_combobox.bind("<<ComboboxSelected>>", lambda e: load_subjects_for_learning(subject_combobox, class_var.get()))
    
    # Store references for later use
    window.progress_var = progress_var
    window.progress_label = progress_label
    window.class_var = class_var
    window.subject_var = subject_var
    
    # Update progress display
    update_progress_display(window)

def load_classes_for_learning(class_combobox, subject_combobox):
    """Load existing classes into the learning combobox"""
    classes = []
    if os.path.exists("./du_lieu/lop.json"):
        try:
            with open("./du_lieu/lop.json", 'r', encoding='utf-8') as file:
                classes = json.load(file)
        except:
            classes = []
    
    class_combobox['values'] = classes
    if classes:
        class_combobox.set(classes[0])
        load_subjects_for_learning(subject_combobox, classes[0])

def load_subjects_for_learning(subject_combobox, class_name):
    """Load subjects for the selected class in learning section"""
    subjects = []
    if class_name and os.path.exists("./du_lieu/mon_hoc.json"):
        try:
            with open("./du_lieu/mon_hoc.json", 'r', encoding='utf-8') as file:
                all_subjects = json.load(file)
                subjects = all_subjects.get(class_name, [])
        except:
            subjects = []
    
    subject_combobox['values'] = subjects
    if subjects:
        subject_combobox.set(subjects[0])

def start_learning(class_name, subject_name, main_window):
    """Start the vocabulary learning session"""
    if not class_name or not subject_name:
        show_message("Lỗi", "Vui lòng chọn lớp học và môn học trước!")
        return
    
    # Check if vocabulary exists for this class-subject combination
    if not os.path.exists("./du_lieu/tu_vung.json"):
        show_message("Lỗi", "Chưa có từ vựng nào cho lớp học và môn học này!")
        return
    
    try:
        with open("./du_lieu/tu_vung.json", 'r', encoding='utf-8') as file:
            all_vocabulary = json.load(file)
            class_vocab = all_vocabulary.get(class_name, {})
            subject_vocab = class_vocab.get(subject_name, [])
            
            if not subject_vocab:
                show_message("Lỗi", "Chưa có từ vựng nào cho môn học này!")
                return
    except:
        show_message("Lỗi", "Không thể đọc dữ liệu từ vựng!")
        return
    
    # Create learning window
    create_learning_window(class_name, subject_name, subject_vocab, main_window)

def create_learning_window(class_name, subject_name, vocabulary_list, main_window):
    """Create the actual learning interface"""
    learning_window = Toplevel()
    learning_window.title(f"Học từ vựng - {class_name} - {subject_name}")
    learning_window.geometry("600x500")
    learning_window.resizable(False, False)
    learning_window.transient()
    learning_window.grab_set()
    
    # Header
    header_frame = Frame(learning_window)
    header_frame.pack(fill=X, padx=20, pady=(20, 10))
    
    Label(header_frame, text=f"Học từ vựng: {class_name} - {subject_name}", 
          font=("Arial", 14, "bold")).pack()
    
    # Progress in this session
    session_progress_frame = Frame(learning_window)
    session_progress_frame.pack(fill=X, padx=20, pady=10)
    
    Label(session_progress_frame, text="Tiến độ phiên học:", font=("Arial", 11)).pack(anchor=W)
    
    session_progress_var = DoubleVar()
    session_progress_bar = ttk.Progressbar(session_progress_frame, variable=session_progress_var, 
                                          maximum=len(vocabulary_list), length=400)
    session_progress_bar.pack(fill=X, pady=(5, 5))
    
    session_progress_label = Label(session_progress_frame, text=f"0/{len(vocabulary_list)}", font=("Arial", 10))
    session_progress_label.pack(anchor=W)
    
    # Learning area
    learning_area = Frame(learning_window)
    learning_area.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Current word display
    word_frame = Frame(learning_area)
    word_frame.pack(fill=X, pady=(0, 20))
    
    current_word_label = Label(word_frame, text="", font=("Arial", 18, "bold"), fg="#2196F3")
    current_word_label.pack()
    
    # Answer input
    answer_frame = Frame(learning_area)
    answer_frame.pack(fill=X, pady=(0, 20))
    
    Label(answer_frame, text="Nhập từ tiếng Anh:", font=("Arial", 11)).pack()
    
    answer_entry = Entry(answer_frame, font=("Arial", 14), width=30)
    answer_entry.pack(pady=(5, 0))
    
    # Buttons
    button_frame = Frame(learning_area)
    button_frame.pack(fill=X, pady=(0, 20))
    
    check_btn = Button(button_frame, text="Kiểm tra", 
                      command=lambda: check_answer(answer_entry, current_word_label, 
                                                session_progress_var, session_progress_label,
                                                vocabulary_list, current_index, learning_window,
                                                class_name, subject_name, main_window),
                      width=15, height=1, font=("Arial", 11), bg="#2196F3", fg="white")
    check_btn.pack(side=LEFT, padx=(0, 10))
    
    skip_btn = Button(button_frame, text="Bỏ qua", 
                     command=lambda: skip_word(current_word_label, session_progress_var, 
                                             session_progress_label, vocabulary_list, current_index,
                                             learning_window, class_name, subject_name, main_window),
                     width=15, height=1, font=("Arial", 11), bg="#FF9800", fg="white")
    skip_btn.pack(side=LEFT)
    
    # Initialize learning session
    current_index = [0]  # Use list to store mutable value
    random.shuffle(vocabulary_list)  # Shuffle vocabulary for variety
    
    def show_next_word():
        if current_index[0] < len(vocabulary_list):
            current_word = vocabulary_list[current_index[0]]
            current_word_label.config(text=current_word['vietnamese'])
            answer_entry.delete(0, END)
            answer_entry.focus()
        else:
            # Session completed
            complete_session(learning_window, class_name, subject_name, main_window)
    
    # Show first word
    show_next_word()
    
    # Bind Enter key to check answer
    answer_entry.bind('<Return>', lambda e: check_answer(answer_entry, current_word_label, 
                                                       session_progress_var, session_progress_label,
                                                       vocabulary_list, current_index, learning_window,
                                                       class_name, subject_name, main_window))
    
    # Store functions for later use
    learning_window.show_next_word = show_next_word
    learning_window.current_index = current_index

def check_answer(answer_entry, current_word_label, session_progress_var, session_progress_label, 
                vocabulary_list, current_index, learning_window, class_name, subject_name, main_window):
    """Check if the user's answer is correct"""
    user_answer = answer_entry.get().strip().lower()
    current_word = vocabulary_list[current_index[0]]
    correct_answer = current_word['english'].lower()
    
    if user_answer == correct_answer:
        # Correct answer
        show_message("Chính xác!", f"Bạn đã trả lời đúng!\n{current_word['vietnamese']} = {current_word['english']}")
        
        # Update progress
        update_learning_progress(class_name, subject_name, current_word, True)
        
        # Move to next word
        current_index[0] += 1
        session_progress_var.set(current_index[0])
        session_progress_label.config(text=f"{current_index[0]}/{len(vocabulary_list)}")
        
        if current_index[0] < len(vocabulary_list):
            learning_window.show_next_word()
        else:
            complete_session(learning_window, class_name, subject_name, main_window)
    else:
        # Wrong answer
        show_message("Sai rồi!", f"Đáp án đúng là: {current_word['english']}\nHãy thử lại!")
        answer_entry.focus()

def skip_word(current_word_label, session_progress_var, session_progress_label, vocabulary_list, current_index, learning_window, class_name, subject_name, main_window):
    """Skip the current word"""
    current_word = vocabulary_list[current_index[0]]
    
    # Update progress (marked as skipped)
    update_learning_progress(class_name, subject_name, current_word, False)
    
    # Move to next word
    current_index[0] += 1
    session_progress_var.set(current_index[0])
    session_progress_label.config(text=f"{current_index[0]}/{len(vocabulary_list)}")
    
    if current_index[0] < len(vocabulary_list):
        current_word_label.config(text=vocabulary_list[current_index[0]]['vietnamese'])
    else:
        complete_session(learning_window, class_name, subject_name, main_window)

def complete_session(learning_window, class_name, subject_name, main_window):
    """Handle session completion"""
    show_message("Hoàn thành!", f"Bạn đã hoàn thành phiên học từ vựng!\nLớp: {class_name}\nMôn: {subject_name}")
    
    # Update main window progress
    update_progress_display(main_window)
    
    # Close learning window
    learning_window.destroy()

def update_learning_progress(class_name, subject_name, vocabulary_item, correct):
    """Update the learning progress for a specific vocabulary item"""
    progress_file = PROGRESS_FILE
    
    # Load existing progress
    progress_data = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as file:
                progress_data = json.load(file)
        except:
            progress_data = {}
    
    # Initialize structure if it doesn't exist
    if class_name not in progress_data:
        progress_data[class_name] = {}
    if subject_name not in progress_data[class_name]:
        progress_data[class_name][subject_name] = {}
    
    vocab_key = f"{vocabulary_item['vietnamese']}_{vocabulary_item['english']}"
    
    if vocab_key not in progress_data[class_name][subject_name]:
        progress_data[class_name][subject_name][vocab_key] = {
            'vietnamese': vocabulary_item['vietnamese'],
            'english': vocabulary_item['english'],
            'correct_count': 0,
            'total_attempts': 0,
            'last_attempt': None
        }
    
    # Update progress
    progress_data[class_name][subject_name][vocab_key]['total_attempts'] += 1
    if correct:
        progress_data[class_name][subject_name][vocab_key]['correct_count'] += 1
    
    # Save progress
    try:
        os.makedirs(os.path.dirname(progress_file), exist_ok=True)
        with open(progress_file, 'w', encoding='utf-8') as file:
            json.dump(progress_data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving progress: {e}")

def update_progress_display(main_window):
    """Update the progress bar and label in the main window"""
    if not hasattr(main_window, 'progress_var'):
        return
    
    # Calculate overall progress
    total_progress = calculate_overall_progress()
    
    # Update progress bar and label
    main_window.progress_var.set(total_progress)
    main_window.progress_label.config(text=f"{total_progress:.1f}%")

def calculate_overall_progress():
    """Calculate overall learning progress across all classes and subjects"""
    if not os.path.exists(PROGRESS_FILE):
        return 0.0
    
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as file:
            progress_data = json.load(file)
    except:
        return 0.0
    
    total_correct = 0
    total_attempts = 0
    
    for class_name, class_data in progress_data.items():
        for subject_name, subject_data in class_data.items():
            for vocab_key, vocab_progress in subject_data.items():
                total_correct += vocab_progress.get('correct_count', 0)
                total_attempts += vocab_progress.get('total_attempts', 0)
    
    if total_attempts == 0:
        return 0.0
    
    # Calculate percentage (correct answers / total attempts * 100)
    progress_percentage = (total_correct / total_attempts) * 100
    return min(progress_percentage, 100.0)

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

if __name__ == "__main__":
    window = tk.Tk()
    window.title("App học từ vựng")
    window.geometry("800x700")
    window.resizable(False, False)

    create_header(window)
    create_buttons(window)
    create_learning_section(window)
    window.mainloop()
