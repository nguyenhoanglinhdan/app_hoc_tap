# === PART 6: TEXT-TO-SPEECH (PLAY STANDARD PRONUNCIATION) ===

def play_standard_audio(self):
    """
    Converts the reference text to speech and plays it
    This shows the user how the text should be pronounced
    """
    # Get the current text to pronounce
    current_text = self.reference_text.get()
    
    # Check if there's text to pronounce
    if not current_text:
        messagebox.showwarning("Cảnh báo", "Không có văn bản nào để phát âm!")
        return
    
    temp_mp3_path = None  # Will store the temporary file path
    
    try:
        # Update instruction text
        self.label_instruction.config(
            text="Đang phát âm chuẩn... Vui lòng chờ.", 
            font=self.font_instruction_text)
        self.cua_so.update_idletasks()
        
        # Create text-to-speech object using Google's service
        tts = gTTS(text=current_text, lang='en', slow=False)
        
        # Create a temporary MP3 file
        # NamedTemporaryFile creates a unique temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3_file:
            tts.write_to_fp(temp_mp3_file)  # Write audio data to file
            temp_mp3_path = temp_mp3_file.name  # Get the file path
        
        # Small delay to ensure file is fully written
        time.sleep(0.1)
        
        # Load and play the audio using pygame
        pygame.mixer.music.load(temp_mp3_path)
        pygame.mixer.music.play()
        
        # Wait for audio to finish playing
        while pygame.mixer.music.get_busy():
            self.cua_so.update()  # Keep UI responsive
            time.sleep(0.01)
        
        # Show completion message
        messagebox.showinfo("Phát Âm Chuẩn", "Đã phát âm chuẩn xong.")
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
        
    except Exception as e:
        # Handle any errors (network issues, file problems, etc.)
        messagebox.showerror("Lỗi Phát Âm Chuẩn",
                             f"Không thể tạo/phát âm thanh cho câu này. Vui lòng kiểm tra:\n"
                             f"1. Kết nối Internet của bạn.\n"
                             f"2. Câu văn có quá dài hoặc phức tạp.\n"
                             f"3. Tệp âm thanh không bị khóa bởi chương trình khác.\n\n"
                             f"Lỗi chi tiết: {e}")
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
    
    finally:
        # Always clean up resources
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
        # Delete the temporary file
        if temp_mp3_path is not None and os.path.exists(temp_mp3_path):
            try:
                os.remove(temp_mp3_path)
            except OSError as e:
                print(f"Cảnh báo: Không thể xóa tệp tạm thời {temp_mp3_path}: {e}")
                messagebox.showwarning("Cảnh báo", 
                                       f"Không thể xóa tệp tạm thời: {e}\nVui lòng xóa thủ công sau.")

"""
EXPLANATION:
- play_standard_audio: Converts text to speech and plays it
- Process:
  1. Gets the reference text (what user should say)
  2. Uses Google Text-to-Speech (gTTS) to convert text to audio
  3. Creates a temporary MP3 file
  4. Plays the audio using pygame
  5. Waits for audio to finish
  6. Cleans up temporary files
- Error handling for network issues, file problems, etc.
- Uses temporary files to avoid cluttering the system
""" 