# === PART 3: USER INTERFACE CREATION ===

def create_interface(self):
    """
    Creates all the visual elements of the app (buttons, text boxes, etc.)
    """
    # Create main container frame
    main_frame = ttk.Frame(self.cua_so, padding="25 25 25 25")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Configure grid weights (how much space each row/column takes)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=0)  # Title row
    main_frame.grid_rowconfigure(1, weight=0)  # Instruction row
    main_frame.grid_rowconfigure(2, weight=0)  # Text management row
    main_frame.grid_rowconfigure(3, weight=0)  # Control buttons row
    main_frame.grid_rowconfigure(4, weight=1)  # Results row (takes most space)
    main_frame.grid_rowconfigure(5, weight=0)  # History button row
    
    # === ROW 0: APP TITLE ===
    ttk.Label(main_frame, 
              text="Ứng dụng Luyện Phát âm Tiếng Anh", 
              font=self.font_header,
              foreground=self.color_button_cap_nhat_vb_va_tieu_de, 
              background='#e6f2f5').grid(row=0, column=0, pady=(0, 10), sticky="nsew")
    
    # === ROW 1: INSTRUCTION LABEL ===
    self.label_instruction = ttk.Label(main_frame, 
                                       text="Nhấn 'Ghi Âm' để bắt đầu luyện tập!",
                                       font=self.font_instruction_text, 
                                       foreground=self.color_text_dark,
                                       background='#e6f2f5')
    self.label_instruction.grid(row=1, column=0, pady=(0, 20), sticky="nsew")
    
    # === ROW 2: TEXT MANAGEMENT SECTION ===
    self.create_text_management_section(main_frame)
    
    # === ROW 3: CONTROL BUTTONS ===
    self.create_control_buttons(main_frame)
    
    # === ROW 4: RESULTS DISPLAY ===
    self.create_results_section(main_frame)
    
    # === ROW 5: HISTORY BUTTON ===
    self.btn_show_history = ttk.Button(main_frame, 
                                       text="Xem Lịch Sử Luyện Tập", 
                                       command=self.show_history_window,
                                       style='Blue.TButton')
    self.btn_show_history.grid(row=5, column=0, pady=(10, 0), sticky="s")

def create_text_management_section(self, main_frame):
    """
    Creates the section where users can select or edit practice text
    """
    # Create a labeled frame (box with title)
    self.frame_text_management = ttk.Labelframe(main_frame, 
                                                text="Chọn hoặc Tùy chỉnh Văn bản Luyện Tập",
                                                padding="15 15 15 15")
    self.frame_text_management.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
    self.frame_text_management.grid_columnconfigure(0, weight=1)
    
    # Label for sentence selection
    ttk.Label(self.frame_text_management, 
              text="Chọn câu mẫu từ danh sách có sẵn:").grid(row=0, column=0, pady=(0, 5), sticky="w")
    
    # Dropdown menu for selecting sentences
    self.selected_sentence_var = tk.StringVar()
    if self.sample_sentences:
        self.selected_sentence_var.set(self.sample_sentences[0])
    else:
        self.selected_sentence_var.set("No sentences available")
    
    self.sentence_combobox = ttk.Combobox(self.frame_text_management,
                                          textvariable=self.selected_sentence_var,
                                          values=self.sample_sentences,
                                          width=80)
    self.sentence_combobox.grid(row=1, column=0, pady=(0, 10), sticky="ew")
    self.sentence_combobox.bind("<<ComboboxSelected>>", self.on_sentence_selected)
    
    # Label for custom text input
    ttk.Label(self.frame_text_management, 
              text="Hoặc nhập/chỉnh sửa văn bản của riêng bạn:").grid(row=2, column=0, pady=(5, 5), sticky="w")
    
    # Text editor for custom text
    self.text_editor = scrolledtext.ScrolledText(self.frame_text_management, 
                                                 wrap=tk.WORD, 
                                                 height=4,
                                                 font=self.font_input, 
                                                 relief='solid', 
                                                 borderwidth=1,
                                                 highlightbackground=self.color_border,
                                                 highlightcolor=self.color_border, 
                                                 bg=self.color_neutral_light,
                                                 fg=self.color_text_dark)
    self.text_editor.insert(tk.END, self.reference_text.get())
    self.text_editor.grid(row=3, column=0, pady=(0, 5), sticky="nsew")
    self.frame_text_management.grid_rowconfigure(3, weight=1)
    
    # Update button
    self.btn_update_text = ttk.Button(self.frame_text_management, 
                                      text="Cập nhật Văn bản từ ô trên",
                                      command=self.update_reference_text_from_editor, 
                                      style='Blue.TButton')
    self.btn_update_text.grid(row=4, column=0, pady=(5, 0), sticky="e")

def create_control_buttons(self, main_frame):
    """
    Creates the main control buttons (Record, Stop, Play)
    """
    control_frame = ttk.Frame(main_frame, padding="15 0 15 15")
    control_frame.grid(row=3, column=0, pady=20)
    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(1, weight=1)
    control_frame.grid_columnconfigure(2, weight=1)
    
    # Record button (green)
    self.btn_record = ttk.Button(control_frame, 
                                 text="Ghi Âm", 
                                 command=self.start_recording, 
                                 style='Green.TButton')
    self.btn_record.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    
    # Stop button (red)
    self.btn_stop = ttk.Button(control_frame, 
                               text="Dừng Ghi Âm", 
                               command=self.stop_recording, 
                               state=tk.DISABLED,
                               style='Red.TButton')
    self.btn_stop.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    
    # Play standard pronunciation button (blue)
    self.btn_play_standard = ttk.Button(control_frame, 
                                        text="Phát Âm Chuẩn", 
                                        command=self.play_standard_audio,
                                        style='Orange.TButton')
    self.btn_play_standard.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

def create_results_section(self, main_frame):
    """
    Creates the section where results are displayed
    """
    # Results title
    self.label_feedback = ttk.Label(main_frame, 
                                    text="KẾT QUẢ PHÂN TÍCH:", 
                                    font=self.font_section_title,
                                    foreground=self.color_button_cap_nhat_vb_va_tieu_de, 
                                    background='#e6f2f5')
    self.label_feedback.grid(row=4, column=0, pady=(15, 5), sticky="n")
    
    # Results display area
    self.result_text_var = tk.StringVar()
    self.result_text_var.set("Chưa có kết quả phân tích.")
    self.result_display = tk.Message(main_frame, 
                                     textvariable=self.result_text_var,
                                     font=self.font_feedback,
                                     bg='#e6f2ff',
                                     fg=self.color_text_dark,
                                     width=780,
                                     justify=tk.CENTER)
    self.result_display.grid(row=4, column=0, pady=(40, 10), sticky="nsew")

"""
EXPLANATION:
- create_interface: Main function that builds the entire UI
- Uses grid layout system to organize elements in rows and columns
- Each section (text management, controls, results) is created separately
- Widgets like buttons, labels, text boxes are created and positioned
- The interface is divided into logical sections for better organization
""" 