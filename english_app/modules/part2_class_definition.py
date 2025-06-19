# === PART 2: CLASS DEFINITION AND INITIALIZATION ===

class PronunciationApp:
    """
    This is the main class that contains everything for the pronunciation app.
    Think of it as a blueprint for creating the app.
    """
    
    def __init__(self, cua_so):
        """
        This is the constructor - it runs when we create a new app.
        'cua_so' means 'window' in Vietnamese - it's the main window of our app.
        """
        # Store the main window
        self.cua_so = cua_so
        
        # Set up the window properties
        cua_so.title("Ứng dụng Luyện Phát âm Tiếng Anh")  # App title
        cua_so.geometry("900x900")                       # Window size (width x height)
        cua_so.resizable(False, False)                   # Can't resize window
        cua_so.config(background='#e6f2ff')              # Background color (light blue)
        
        # Initialize audio player
        pygame.mixer.init()
        
        # Set up visual styles and colors
        self.setup_styles()
        
        # Initialize variables for recording
        self.is_recording = False        # Are we currently recording?
        self.audio_frames = []           # Store recorded audio data
        self.samplerate = 44100          # Audio quality (samples per second)
        self.channels = 1                # Mono audio (1 channel)
        
        # File names for saving data
        self.audio_filename = "../../user_pronunciation.wav"  # User's recording
        self.standard_audio_filename = "standard_pronunciation.mp3"  # Correct pronunciation
        self.history_file = "../../pronunciation_history.json"  # Practice history
        self.sentences_file = "../../sentences.json"  # Sample sentences
        
        # Load sample sentences from file
        self.sample_sentences = self.load_sample_sentences()
        
        # Set up the reference text (what user should say)
        self.reference_text = tk.StringVar()
        if self.sample_sentences:
            self.reference_text.set(self.sample_sentences[0])  # Use first sentence
        else:
            self.reference_text.set("Welcome! Please add sentences to 'sentences.json' to begin.")
        
        # Create the user interface
        self.create_interface()
    
    def setup_styles(self):
        """
        Sets up colors and fonts for the app to look nice
        """
        # Create style object for modern-looking widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define colors
        self.color_button_ghi_am = '#4CAF50'              # Green for record button
        self.color_button_cap_nhat_vb_va_tieu_de = '#6A1B9A'  # Purple for update button
        self.color_button_phat_am_va_highlight = '#2196F3'     # Blue for play button
        self.color_phan_ung_tieu_cuc = '#E91E63'              # Pink for stop button
        self.color_neutral_bg = '#f0f2f5'                     # Light gray background
        self.color_neutral_light = '#ffffff'                  # White
        self.color_text_dark = '#333333'                      # Dark gray text
        self.color_text_light = '#ffffff'                     # White text
        self.color_border = '#bbdefb'                         # Light blue border
        
        # Define fonts
        self.font_header = ('Arial', 24, 'bold')              # Big title font
        self.font_instruction_text = ('Arial', 18, 'bold')    # Instruction font
        self.font_section_title = ('Arial', 14, 'bold')       # Section title font
        self.font_body = ('Arial', 12)                        # Normal text font
        self.font_input = ('Arial', 13)                       # Input text font
        self.font_button = ('Arial', 12, 'bold')              # Button text font
        self.font_feedback = ('Arial', 15)                    # Feedback text font
        
        # Apply styles to different widget types
        self.style.configure('TLabel', font=self.font_body, background='#e6f2ff', foreground=self.color_text_dark)
        self.style.configure('TButton', font=self.font_button, padding=(15, 10))
        # ... more style configurations ...

"""
EXPLANATION:
- __init__: This is called when we create a new app instance
- It sets up the window, colors, fonts, and initializes variables
- setup_styles: Makes the app look modern and professional
- Variables like is_recording track the app's current state
- File names are defined for saving user data and history
""" 