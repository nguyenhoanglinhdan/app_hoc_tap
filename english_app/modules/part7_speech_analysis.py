# === PART 7: SPEECH RECOGNITION AND ANALYSIS ===

def analyze_pronunciation(self):
    """
    Analyzes the user's recorded pronunciation by:
    1. Converting speech to text
    2. Comparing with reference text
    3. Calculating accuracy scores
    4. Providing feedback
    """
    # Update UI to show processing
    self.result_text_var.set("Đang phân tích phát âm của bạn... Vui lòng chờ.")
    self.cua_so.update_idletasks()
    
    # Check if audio file exists
    if not os.path.exists(self.audio_filename):
        self.result_text_var.set("Lỗi: Không tìm thấy tệp ghi âm để phân tích.")
        messagebox.showerror("Lỗi", "Không tìm thấy tệp ghi âm. Vui lòng ghi âm trước.")
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
        self.cua_so.update_idletasks()
        return
    
    # Create speech recognizer
    recognizer = sr.Recognizer()
    
    # Convert audio to proper format for speech recognition
    temp_audio_file = "temp_converted_audio.wav"
    try:
        # Load the recorded audio
        audio = AudioSegment.from_wav(self.audio_filename)
        
        # Convert to format needed by speech recognition:
        # - 1 channel (mono)
        # - 16000 Hz sample rate
        # - 16-bit depth
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        
        # Save converted audio
        audio.export(temp_audio_file, format="wav")
        
    except Exception as e:
        self.result_text_var.set(f"Lỗi xử lý tệp âm thanh: {e}.\nVui lòng kiểm tra cài đặt FFmpeg.")
        messagebox.showerror("Lỗi xử lý âm thanh",
                             f"Không thể xử lý tệp âm thanh: {e}\n"
                             f"Bạn đã cài đặt và cấu hình FFmpeg đúng cách chưa?")
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
        self.cua_so.update_idletasks()
        return
    
    try:
        # Load the converted audio file
        with sr.AudioFile(temp_audio_file) as source:
            audio_data = recognizer.record(source)
        
        # Convert speech to text using Google's service
        user_spoken_text = recognizer.recognize_google(audio_data, language="en-US")
        
        # Get the reference text (what user should have said)
        current_reference_text = self.reference_text.get()
        
        # Calculate accuracy scores using fuzzy string matching
        ratio = fuzz.ratio(current_reference_text.lower(), user_spoken_text.lower())
        partial_ratio = fuzz.partial_ratio(current_reference_text.lower(), user_spoken_text.lower())
        
        # Generate feedback based on accuracy
        feedback = ""
        color_feedback = self.color_text_dark
        
        if ratio >= 90:
            feedback = "Tuyệt vời! Phát âm của bạn rất chính xác."
            color_feedback = self.color_button_ghi_am  # Green
        elif ratio >= 70:
            feedback = "Tốt! Phát âm của bạn khá rõ ràng."
            color_feedback = '#FFC107'  # Yellow
        elif ratio >= 50:
            feedback = "Cần cải thiện. Hãy cố gắng luyện tập thêm."
            color_feedback = '#fd7e14'  # Orange
        else:
            feedback = "Cần rất nhiều luyện tập. Đừng nản lòng!"
            color_feedback = self.color_phan_ung_tieu_cuc  # Pink
        
        # Create result message
        result_message = (f"Bạn đã nói:\n\"{user_spoken_text}\"\n\n"
                          f"Văn bản chuẩn:\n\"{current_reference_text}\"\n\n"
                          f"Độ chính xác tương đối: {ratio}%\n"
                          f"Độ chính xác một phần: {partial_ratio}%\n\n"
                          f"Phản hồi: {feedback}")
        
        # Display results
        self.result_text_var.set(result_message)
        self.result_display.config(fg=color_feedback)
        self.cua_so.update_idletasks()
        
        # Save to history
        self.save_history({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reference_text": current_reference_text,
            "user_spoken_text": user_spoken_text,
            "accuracy_ratio": ratio,
            "accuracy_partial_ratio": partial_ratio,
            "feedback": feedback
        })
        
    except sr.UnknownValueError:
        # Speech was not recognized
        self.result_text_var.set(
            "Kết quả: KHÔNG THỂ NHẬN DẠNG GIỌC NÓI của bạn.\n"
            "Vui lòng nói rõ hơn hoặc thử lại. (UnknownValueError)")
        self.result_display.config(fg=self.color_phan_ung_tieu_cuc)
        
    except sr.RequestError as e:
        # Network or service error
        self.result_text_var.set(
            f"Kết quả: LỖI KẾT NỐI đến dịch vụ nhận dạng giọng nói;\n"
            f"Kiểm tra internet của bạn. (RequestError: {e})")
        self.result_display.config(fg=self.color_phan_ung_tieu_cuc)
        
    except Exception as e:
        # Any other error
        self.result_text_var.set(f"Kết quả: ĐÃ XẢY RA LỖI không mong muốn:\n{e}")
        self.result_display.config(fg=self.color_phan_ung_tieu_cuc)
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        
        # Update instruction text
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
        self.cua_so.update_idletasks()

"""
EXPLANATION:
- analyze_pronunciation: The core function that evaluates user's pronunciation
- Process:
  1. Loads the recorded audio file
  2. Converts audio format for speech recognition
  3. Uses Google Speech Recognition to convert speech to text
  4. Compares user's text with reference text using fuzzy matching
  5. Calculates accuracy percentages
  6. Provides feedback based on accuracy level
  7. Saves results to history
- Error handling for various speech recognition issues
- Uses fuzzy string matching to account for pronunciation variations
""" 