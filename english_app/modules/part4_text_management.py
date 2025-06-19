# === PART 4: TEXT MANAGEMENT FUNCTIONS ===

def load_sample_sentences(self):
    """
    Loads sample sentences from the sentences.json file
    Returns a list of strings (sentences to practice)
    """
    # Check if the file exists
    if not os.path.exists(self.sentences_file):
        messagebox.showwarning("Cảnh báo",
                               f"Không tìm thấy tệp '{self.sentences_file}'. Vui lòng tạo tệp này với định dạng JSON (danh sách chuỗi).")
        return []
    
    try:
        # Open and read the JSON file
        with open(self.sentences_file, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
            
            # Validate that it's a list of strings
            if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
                messagebox.showerror("Lỗi tệp câu mẫu",
                                     "Định dạng tệp 'sentences.json' không hợp lệ. Phải là một danh sách các chuỗi.")
                return []
            return sentences
            
    except json.JSONDecodeError:
        # If JSON is malformed
        messagebox.showerror("Lỗi tệp câu mẫu", "Lỗi đọc tệp 'sentences.json'. Đảm bảo nó là JSON hợp lệ.")
        return []
    except Exception as e:
        # Any other error
        messagebox.showerror("Lỗi tệp câu mẫu", f"Đã xảy ra lỗi khi tải câu mẫu: {e}")
        return []

def on_sentence_selected(self, event):
    """
    Called when user selects a sentence from the dropdown menu
    Updates the reference text and text editor with the selected sentence
    """
    # Get the selected text from dropdown
    selected_text = self.selected_sentence_var.get()
    
    # Update the reference text (what user should say)
    self.reference_text.set(selected_text)
    
    # Update the text editor to show the selected sentence
    self.text_editor.delete("1.0", tk.END)  # Clear the editor
    self.text_editor.insert(tk.END, selected_text)  # Insert selected text
    
    # Show confirmation message
    messagebox.showinfo("Cập nhật", "Văn bản luyện tập đã được chọn từ danh sách!")

def update_reference_text_from_editor(self):
    """
    Called when user clicks the "Update Text" button
    Takes text from the editor and makes it the reference text
    """
    # Get text from the editor (remove leading/trailing whitespace)
    new_text = self.text_editor.get("1.0", tk.END).strip()
    
    if new_text:  # If text is not empty
        # Update the reference text
        self.reference_text.set(new_text)
        
        # Update the dropdown selection
        self.selected_sentence_var.set(new_text)
        
        # Show confirmation message
        messagebox.showinfo("Cập nhật", "Văn bản luyện tập đã được cập nhật từ trình soạn thảo!")
    else:
        # If text is empty, show warning and restore original text
        messagebox.showwarning("Cảnh báo", "Văn bản luyện tập không được để trống!")
        self.text_editor.insert(tk.END, self.reference_text.get())

"""
EXPLANATION:
- load_sample_sentences: Reads practice sentences from a JSON file
- on_sentence_selected: Handles when user picks a sentence from dropdown
- update_reference_text_from_editor: Handles when user types custom text
- These functions manage what text the user will practice pronouncing
- Error handling ensures the app doesn't crash if files are missing or corrupted
""" 