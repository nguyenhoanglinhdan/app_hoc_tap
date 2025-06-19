# === PART 5: AUDIO RECORDING FUNCTIONS ===

def start_recording(self):
    """
    Starts recording audio from the user's microphone
    """
    # Don't start if already recording
    if self.is_recording:
        return
    
    # Set recording state to True
    self.is_recording = True
    self.audio_frames = []  # Clear previous audio data
    
    # Update button states
    self.btn_record.config(state=tk.DISABLED)  # Disable record button
    self.btn_stop.config(state=tk.NORMAL)      # Enable stop button
    
    # Update instruction text
    self.label_instruction.config(
        text=f"ĐANG GHI ÂM... Vui lòng đọc to và rõ ràng: \"{self.reference_text.get()}\"",
        font=self.font_instruction_text)
    
    # Clear previous results
    self.result_text_var.set("...")
    
    # Force UI update
    self.cua_so.update_idletasks()
    
    # Start audio recording stream
    self.stream = sd.InputStream(
        samplerate=self.samplerate,  # 44100 Hz (CD quality)
        channels=self.channels,      # 1 channel (mono)
        callback=self.audio_callback # Function called for each audio chunk
    )
    self.stream.start()
    
    # Show notification
    messagebox.showinfo("Thông báo", "Bắt đầu ghi âm. Hãy nói vào microphone của bạn!")

def audio_callback(self, indata, frames, time, status):
    """
    Called automatically by sounddevice for each chunk of audio data
    This function runs in a separate thread
    """
    if status:
        print(status)  # Print any errors
    
    if self.is_recording:
        # Store the audio data (copy to avoid reference issues)
        self.audio_frames.append(indata.copy())

def stop_recording(self):
    """
    Stops recording and processes the recorded audio
    """
    # Don't stop if not recording
    if not self.is_recording:
        return
    
    # Stop recording
    self.is_recording = False
    self.stream.stop()
    self.stream.close()
    
    # Update button states
    self.btn_record.config(state=tk.NORMAL)   # Enable record button
    self.btn_stop.config(state=tk.DISABLED)   # Disable stop button
    
    # Update instruction text
    self.label_instruction.config(
        text="Ghi âm hoàn tất. Đang xử lý...", 
        font=self.font_instruction_text)
    
    # Force UI update
    self.cua_so.update_idletasks()
    
    # Show notification
    messagebox.showinfo("Thông báo", "Ghi âm đã dừng. Đang phân tích phát âm của bạn...")
    
    # Process the recorded audio
    if self.audio_frames:
        # Combine all audio chunks into one file
        import numpy as np
        full_audio_data = np.concatenate(self.audio_frames, axis=0)
        
        # Save to WAV file
        sf.write(self.audio_filename, full_audio_data, self.samplerate)
        
        # Analyze the pronunciation
        self.analyze_pronunciation()
    else:
        # No audio was recorded
        self.result_text_var.set("Không có âm thanh nào được ghi.")
        messagebox.showwarning("Cảnh báo", "Không có âm thanh nào được ghi. Vui lòng thử lại.")
        self.label_instruction.config(
            text="Nhấn 'Ghi Âm' để tiếp tục luyện tập!", 
            font=self.font_instruction_text)
    
    # Final UI update
    self.cua_so.update_idletasks()

"""
EXPLANATION:
- start_recording: Begins recording from microphone
- audio_callback: Automatically called for each piece of audio data
- stop_recording: Ends recording and saves the audio file
- The recording process:
  1. User clicks "Record" button
  2. App starts listening to microphone
  3. Audio data is collected in chunks
  4. User clicks "Stop" button
  5. Audio is saved to file
  6. Pronunciation analysis begins
""" 