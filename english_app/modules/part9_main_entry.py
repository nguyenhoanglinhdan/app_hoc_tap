# === PART 9: MAIN APPLICATION ENTRY POINT ===

# --- Khởi chạy ứng dụng ---
if __name__ == "__main__":
    """
    This is the entry point of the application.
    It runs when you execute the Python file directly.
    """
    
    # Create the main window
    root = tk.Tk()
    
    # Create the pronunciation app instance
    app = PronunciationApp(root)
    
    # Start the main event loop
    # This keeps the application running and responsive to user input
    root.mainloop()

"""
EXPLANATION:
- if __name__ == "__main__": This ensures the code only runs when the file is executed directly
- tk.Tk(): Creates the main application window
- PronunciationApp(root): Creates our app instance and sets up the interface
- root.mainloop(): Starts the event loop that:
  - Listens for user interactions (button clicks, etc.)
  - Updates the display
  - Handles all GUI events
  - Keeps the app running until the window is closed

HOW TO RUN THE APP:
1. Make sure you have all required libraries installed:
   pip install tkinter sounddevice soundfile speech_recognition pydub fuzzywuzzy gtts pygame

2. Make sure you have the sentences.json file with practice sentences

3. Run the Python file:
   python tin_hoc_tre.py

4. The app window will open and you can start practicing pronunciation!

REQUIRED FILES:
- tin_hoc_tre.py (main application file)
- sentences.json (practice sentences)
- pronunciation_history.json (will be created automatically)
- user_pronunciation.wav (will be created automatically)

DEPENDENCIES:
- Python 3.x
- tkinter (usually comes with Python)
- sounddevice (for audio recording)
- soundfile (for audio file handling)
- speech_recognition (for speech-to-text)
- pydub (for audio processing)
- fuzzywuzzy (for text comparison)
- gtts (for text-to-speech)
- pygame (for audio playback)
- FFmpeg (system dependency for audio processing)
""" 