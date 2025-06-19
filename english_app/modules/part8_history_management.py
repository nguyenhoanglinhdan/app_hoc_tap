# === PART 8: HISTORY MANAGEMENT ===

def load_history(self):
    """
    Loads practice history from JSON file
    Returns a list of practice sessions
    """
    # Check if history file exists
    if not os.path.exists(self.history_file):
        return []
    
    try:
        # Read and parse JSON file
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If JSON is corrupted
        messagebox.showwarning("Lỗi lịch sử", "Không thể đọc tệp lịch sử. Tệp có thể bị hỏng.")
        return []
    except Exception as e:
        # Any other error
        messagebox.showerror("Lỗi lịch sử", f"Đã xảy ra lỗi khi tải lịch sử: {e}")
        return []

def save_history(self, entry):
    """
    Saves a new practice session to history
    entry: Dictionary containing practice session data
    """
    # Load existing history
    history = self.load_history()
    
    # Add new entry
    history.append(entry)
    
    try:
        # Save updated history to file
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Lỗi lưu lịch sử", f"Không thể lưu lịch sử: {e}")

def show_history_window(self):
    """
    Opens a new window showing all practice history
    """
    # Create new window
    history_window = tk.Toplevel(self.cua_so)
    history_window.title("Lịch Sử Luyện Tập")
    history_window.geometry("850x650")
    history_window.transient(self.cua_so)  # Window belongs to main window
    history_window.grab_set()              # Make window modal (user must close it)
    history_window.focus_set()             # Give focus to this window
    history_window.config(bg='#e6f2ff')
    
    # Title label
    history_label = ttk.Label(history_window, 
                              text="LỊCH SỬ CÁC PHIÊN LUYỆN TẬP", 
                              font=self.font_instruction_text,
                              foreground=self.color_button_cap_nhat_vb_va_tieu_de, 
                              background='#e6f2f5')
    history_label.pack(pady=15)
    
    # Text area for displaying history
    history_text_area = scrolledtext.ScrolledText(history_window, 
                                                  wrap=tk.WORD, 
                                                  width=95, 
                                                  height=28,
                                                  font=self.font_body, 
                                                  relief='solid', 
                                                  borderwidth=1,
                                                  highlightbackground=self.color_border,
                                                  highlightcolor=self.color_border, 
                                                  bg=self.color_neutral_light,
                                                  fg=self.color_text_dark)
    history_text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    # Load and display history data
    history_data = self.load_history()
    
    if not history_data:
        # No history available
        history_text_area.insert(tk.END, "Chưa có dữ liệu lịch sử nào.")
    else:
        # Display each practice session
        for i, entry in enumerate(history_data):
            # Session header
            history_text_area.insert(tk.END, 
                                     f"--- PHIÊN {i + 1} ({entry.get('timestamp', 'N/A')}) ---\n", 
                                     'header')
            
            # Session details
            history_text_area.insert(tk.END, 
                                     f"Văn bản chuẩn: {entry.get('reference_text', 'N/A')}\n")
            history_text_area.insert(tk.END, 
                                     f"Bạn đã nói: {entry.get('user_spoken_text', 'N/A')}\n")
            history_text_area.insert(tk.END, 
                                     f"Độ chính xác: {entry.get('accuracy_ratio', 'N/A')}%\n")
            history_text_area.insert(tk.END, 
                                     f"Độ chính xác một phần: {entry.get('accuracy_partial_ratio', 'N/A')}%\n")
            history_text_area.insert(tk.END, 
                                     f"Phản hồi: {entry.get('feedback', 'N/A')}\n")
            history_text_area.insert(tk.END, 
                                     "---------------------------------------------------\n\n")
    
    # Configure header style (bold, colored text)
    history_text_area.tag_configure('header', 
                                    font=('Arial', 11, 'bold'), 
                                    foreground=self.color_button_cap_nhat_vb_va_tieu_de)
    
    # Make text area read-only
    history_text_area.config(state=tk.DISABLED)
    
    # Handle window close event
    history_window.protocol("WM_DELETE_WINDOW", 
                            lambda: self.on_history_window_close(history_window))

def on_history_window_close(self, history_window):
    """
    Handles closing of history window
    """
    history_window.destroy()      # Close the window
    self.cua_so.grab_release()    # Release modal state

"""
EXPLANATION:
- load_history: Reads practice history from JSON file
- save_history: Saves new practice session to history
- show_history_window: Opens a new window showing all practice history
- on_history_window_close: Handles closing the history window
- History data includes:
  - Timestamp of practice session
  - Reference text (what user should say)
  - User's spoken text (what they actually said)
  - Accuracy scores
  - Feedback message
- Uses JSON format for easy reading and writing
- Error handling for file operations
""" 