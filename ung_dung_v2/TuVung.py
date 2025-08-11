from tkinter import *
import json
import os
import tkinter.ttk as ttk

# File path for storing vocabulary data
VOCABULARY_FILE = "./du_lieu/tu_vung.json"

def hien_thi():
    create_frame()

def create_frame():
    top = Toplevel()
    top.title("Quản lý từ vựng")
    top.geometry("900x700")
    top.resizable(False, False)

    # Center the window
    top.transient()
    top.grab_set()

    # Header
    header_frame = Frame(top)
    header_frame.pack(fill=X, padx=20, pady=(20, 10))
    
    label = Label(header_frame, text="Quản lý từ vựng", font=("Arial", 16, "bold"))
    label.pack()

    # Class and Subject selection section
    selection_frame = Frame(top)
    selection_frame.pack(fill=X, padx=20, pady=10)
    
    # Class selection
    class_frame = Frame(selection_frame)
    class_frame.pack(fill=X, pady=(0, 10))
    
    Label(class_frame, text="Chọn lớp học:", font=("Arial", 12)).pack(side=LEFT)
    
    class_var = StringVar()
    class_combobox = ttk.Combobox(class_frame, textvariable=class_var, width=20, font=("Arial", 12))
    class_combobox.pack(side=LEFT, padx=(10, 10))
    
    refresh_class_btn = Button(class_frame, text="Làm mới", 
                              command=lambda: load_classes(class_combobox, subject_combobox),
                              width=10, height=1, font=("Arial", 10))
    refresh_class_btn.pack(side=LEFT)
    
    # Subject selection
    subject_frame = Frame(selection_frame)
    subject_frame.pack(fill=X)
    
    Label(subject_frame, text="Chọn môn học:", font=("Arial", 12)).pack(side=LEFT)
    
    subject_var = StringVar()
    subject_combobox = ttk.Combobox(subject_frame, textvariable=subject_var, width=20, font=("Arial", 12))
    subject_combobox.pack(side=LEFT, padx=(10, 10))
    
    refresh_subject_btn = Button(subject_frame, text="Làm mới", 
                                command=lambda: load_subjects_for_class(subject_combobox, class_var.get()),
                                width=10, height=1, font=("Arial", 10))
    refresh_subject_btn.pack(side=LEFT)

    # Input section for adding new vocabulary
    input_frame = Frame(top)
    input_frame.pack(fill=X, padx=20, pady=10)
    
    # Vietnamese word input
    vietnamese_frame = Frame(input_frame)
    vietnamese_frame.pack(fill=X, pady=(0, 5))
    
    Label(vietnamese_frame, text="Từ tiếng Việt:", font=("Arial", 12)).pack(side=LEFT)
    
    vietnamese_entry = Entry(vietnamese_frame, width=30, font=("Arial", 12))
    vietnamese_entry.pack(side=LEFT, padx=(10, 10))
    
    # English word input
    english_frame = Frame(input_frame)
    english_frame.pack(fill=X, pady=(0, 10))
    
    Label(english_frame, text="Từ tiếng Anh:", font=("Arial", 12)).pack(side=LEFT)
    
    english_entry = Entry(english_frame, width=30, font=("Arial", 12))
    english_entry.pack(side=LEFT, padx=(10, 10))
    
    # Add button
    add_button = Button(input_frame, text="Thêm từ vựng", 
                       command=lambda: add_vocabulary(vietnamese_entry, english_entry, top, class_var.get(), subject_var.get()),
                       width=15, height=1, font=("Arial", 10))
    add_button.pack(side=LEFT)

    # List section with scrollbar
    list_frame = Frame(top)
    list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    Label(list_frame, text="Danh sách từ vựng:", font=("Arial", 12, "bold")).pack(anchor=W)
    
    # Create canvas with scrollbar for custom vocabulary items
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
    top.subject_var = subject_var
    
    # Load classes and subjects
    load_classes(class_combobox, subject_combobox)
    
    # Bind selection changes
    class_combobox.bind("<<ComboboxSelected>>", lambda e: on_class_change(top, subject_combobox))
    subject_combobox.bind("<<ComboboxSelected>>", lambda e: load_vocabulary(top))
    
    # Close button
    close_btn = Button(top, text="Đóng", command=top.destroy,
                       width=10, height=1, font=("Arial", 10))
    close_btn.pack(pady=20)

def load_classes(class_combobox, subject_combobox):
    """Load existing classes into the combobox"""
    classes = []
    if os.path.exists("du_lieu/lop.json"):
        try:
            with open("du_lieu/lop.json", 'r', encoding='utf-8') as file:
                classes = json.load(file)
        except:
            classes = []
    
    class_combobox['values'] = classes
    if classes:
        class_combobox.set(classes[0])
        load_subjects_for_class(subject_combobox, classes[0])

def load_subjects_for_class(subject_combobox, class_name):
    """Load subjects for the selected class"""
    subjects = []
    if class_name and os.path.exists("du_lieu/mon_hoc.json"):
        try:
            with open("du_lieu/mon_hoc.json", 'r', encoding='utf-8') as file:
                all_subjects = json.load(file)
                subjects = all_subjects.get(class_name, [])
        except:
            subjects = []
    
    subject_combobox['values'] = subjects
    if subjects:
        subject_combobox.set(subjects[0])

def on_class_change(top, subject_combobox):
    """Handle class selection change"""
    class_name = top.class_var.get()
    load_subjects_for_class(subject_combobox, class_name)
    # Clear vocabulary list when class changes
    for widget in top.scrollable_frame.winfo_children():
        widget.destroy()

def load_vocabulary(top):
    """Load vocabulary for the selected class and subject"""
    class_name = top.class_var.get()
    subject_name = top.subject_var.get()
    
    if not class_name or not subject_name:
        return
    
    scrollable_frame = top.scrollable_frame
    
    # Clear existing items
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    if os.path.exists(VOCABULARY_FILE):
        try:
            with open(VOCABULARY_FILE, 'r', encoding='utf-8') as file:
                all_vocabulary = json.load(file)
                class_vocab = all_vocabulary.get(class_name, {})
                subject_vocab = class_vocab.get(subject_name, [])
                for vocab in subject_vocab:
                    create_vocabulary_item(scrollable_frame, vocab, top, class_name, subject_name)
        except:
            pass

def save_vocabulary(all_vocabulary):
    """Save vocabulary data to JSON file"""
    try:
        os.makedirs(os.path.dirname(VOCABULARY_FILE), exist_ok=True)
        with open(VOCABULARY_FILE, 'w', encoding='utf-8') as file:
            json.dump(all_vocabulary, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving vocabulary: {e}")
        return False

def add_vocabulary(vietnamese_entry, english_entry, top, class_name, subject_name):
    """Add a new vocabulary item to the selected class and subject"""
    if not class_name:
        show_message("Lỗi", "Vui lòng chọn lớp học trước!")
        return
    
    if not subject_name:
        show_message("Lỗi", "Vui lòng chọn môn học trước!")
        return
    
    vietnamese_word = vietnamese_entry.get().strip()
    english_word = english_entry.get().strip()
    
    if not vietnamese_word or not english_word:
        show_message("Lỗi", "Vui lòng nhập đầy đủ từ tiếng Việt và tiếng Anh!")
        return
    
    # Load current vocabulary
    all_vocabulary = {}
    if os.path.exists(VOCABULARY_FILE):
        try:
            with open(VOCABULARY_FILE, 'r', encoding='utf-8') as file:
                all_vocabulary = json.load(file)
        except:
            all_vocabulary = {}
    
    # Initialize class and subject if they don't exist
    if class_name not in all_vocabulary:
        all_vocabulary[class_name] = {}
    if subject_name not in all_vocabulary[class_name]:
        all_vocabulary[class_name][subject_name] = []
    
    # Check if vocabulary already exists
    for vocab in all_vocabulary[class_name][subject_name]:
        if vocab['vietnamese'] == vietnamese_word or vocab['english'] == english_word:
            show_message("Lỗi", "Từ vựng này đã tồn tại!")
            return
    
    # Add new vocabulary
    new_vocab = {
        'vietnamese': vietnamese_word,
        'english': english_word
    }
    all_vocabulary[class_name][subject_name].append(new_vocab)
    
    # Save to file
    if save_vocabulary(all_vocabulary):
        # Add to display
        create_vocabulary_item(top.scrollable_frame, new_vocab, top, class_name, subject_name)
        # Clear input fields
        vietnamese_entry.delete(0, END)
        english_entry.delete(0, END)
        show_message("Thành công", f"Đã thêm từ vựng: {vietnamese_word} - {english_word}")
    else:
        show_message("Lỗi", "Không thể lưu từ vựng!")

def delete_vocabulary(vocab_item, top, class_name, subject_name):
    """Delete a specific vocabulary item"""
    vietnamese_word = vocab_item['vietnamese']
    english_word = vocab_item['english']
    
    if show_confirm("Xác nhận", f"Bạn có chắc muốn xóa từ vựng '{vietnamese_word} - {english_word}'?"):
        # Load current vocabulary
        all_vocabulary = {}
        if os.path.exists(VOCABULARY_FILE):
            try:
                with open(VOCABULARY_FILE, 'r', encoding='utf-8') as file:
                    all_vocabulary = json.load(file)
            except:
                all_vocabulary = {}
        
        # Remove the vocabulary
        if (class_name in all_vocabulary and 
            subject_name in all_vocabulary[class_name]):
            vocab_list = all_vocabulary[class_name][subject_name]
            for i, vocab in enumerate(vocab_list):
                if (vocab['vietnamese'] == vietnamese_word and 
                    vocab['english'] == english_word):
                    vocab_list.pop(i)
                    break
            
            # Save to file
            if save_vocabulary(all_vocabulary):
                # Refresh display
                load_vocabulary(top)
                show_message("Thành công", f"Đã xóa từ vựng: {vietnamese_word} - {english_word}")
            else:
                show_message("Lỗi", "Không thể xóa từ vựng!")

def create_vocabulary_item(parent_frame, vocab_item, top, class_name, subject_name):
    """Creates a custom widget for a vocabulary item with a delete button."""
    vocab_frame = Frame(parent_frame)
    vocab_frame.pack(fill=X, pady=2, padx=5)
    
    # Vietnamese word label
    vietnamese_label = Label(vocab_frame, text=vocab_item['vietnamese'], font=("Arial", 11), width=20)
    vietnamese_label.pack(side=LEFT, padx=(0, 10))
    
    # Arrow separator
    arrow_label = Label(vocab_frame, text="→", font=("Arial", 11, "bold"))
    arrow_label.pack(side=LEFT, padx=(0, 10))
    
    # English word label
    english_label = Label(vocab_frame, text=vocab_item['english'], font=("Arial", 11), width=20)
    english_label.pack(side=LEFT, padx=(0, 10))
    
    # Delete button
    delete_button = Button(vocab_frame, text="Xóa", 
                           command=lambda: delete_vocabulary(vocab_item, top, class_name, subject_name),
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
