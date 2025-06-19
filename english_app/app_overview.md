# English Pronunciation Practice App - Complete Overview

## 🎯 What This App Does

This is a **Python GUI application** that helps users practice English pronunciation. Here's what it does:

1. **Shows English sentences** for practice
2. **Records user's voice** when they speak
3. **Converts speech to text** using Google's service
4. **Compares** what the user said with the correct text
5. **Gives feedback** on pronunciation accuracy
6. **Plays correct pronunciation** for reference
7. **Saves practice history** for tracking progress

## 🏗️ Application Structure

The app is organized into **9 main parts**:

### Part 1: Imports and Dependencies
- **File**: `part1_imports.py`
- **Purpose**: Imports all necessary libraries
- **Key Libraries**:
  - `tkinter`: GUI framework
  - `sounddevice`: Audio recording
  - `speech_recognition`: Speech-to-text
  - `gtts`: Text-to-speech
  - `fuzzywuzzy`: Text comparison

### Part 2: Class Definition and Initialization
- **File**: `part2_class_definition.py`
- **Purpose**: Sets up the main app class and initializes everything
- **Key Features**:
  - Window setup (size, title, colors)
  - Variable initialization
  - Style configuration
  - File path setup

### Part 3: User Interface Creation
- **File**: `part3_user_interface.py`
- **Purpose**: Creates all visual elements
- **Components**:
  - App title and instructions
  - Text selection dropdown
  - Custom text editor
  - Control buttons (Record, Stop, Play)
  - Results display area
  - History button

### Part 4: Text Management
- **File**: `part4_text_management.py`
- **Purpose**: Handles practice text selection and editing
- **Functions**:
  - Load sentences from JSON file
  - Handle dropdown selection
  - Update custom text

### Part 5: Audio Recording
- **File**: `part5_audio_recording.py`
- **Purpose**: Records user's voice
- **Process**:
  - Start recording from microphone
  - Collect audio data in chunks
  - Stop recording and save to file

### Part 6: Text-to-Speech
- **File**: `part6_text_to_speech.py`
- **Purpose**: Plays correct pronunciation
- **Process**:
  - Convert text to speech using Google
  - Create temporary audio file
  - Play audio using pygame

### Part 7: Speech Analysis
- **File**: `part7_speech_analysis.py`
- **Purpose**: Analyzes user's pronunciation
- **Process**:
  - Convert speech to text
  - Compare with reference text
  - Calculate accuracy scores
  - Provide feedback

### Part 8: History Management
- **File**: `part8_history_management.py`
- **Purpose**: Saves and displays practice history
- **Features**:
  - Save practice sessions to JSON
  - Display history in new window
  - Track progress over time

### Part 9: Main Entry Point
- **File**: `part9_main_entry.py`
- **Purpose**: Starts the application
- **Process**:
  - Create main window
  - Initialize app
  - Start event loop

## 🔄 How It All Works Together

### 1. **App Startup**
```
User runs tin_hoc_tre.py
↓
Main window created
↓
Interface built
↓
Sample sentences loaded
↓
App ready for use
```

### 2. **Practice Session Flow**
```
User selects/edits text
↓
User clicks "Record"
↓
Audio recording starts
↓
User speaks into microphone
↓
User clicks "Stop"
↓
Audio saved to file
↓
Speech converted to text
↓
Text compared with reference
↓
Accuracy calculated
↓
Feedback displayed
↓
Results saved to history
```

### 3. **Text-to-Speech Flow**
```
User clicks "Play Standard"
↓
Text sent to Google TTS
↓
Audio file created
↓
Audio played through speakers
↓
Temporary file cleaned up
```

## 📁 File Structure

```
app_hoc_tap/
├── tin_hoc_tre.py              # Main application file
├── sentences.json              # Practice sentences
├── pronunciation_history.json  # Practice history (auto-created)
├── user_pronunciation.wav      # User recordings (auto-created)
├── part1_imports.py            # Part 1: Imports
├── part2_class_definition.py   # Part 2: Class setup
├── part3_user_interface.py     # Part 3: UI creation
├── part4_text_management.py    # Part 4: Text handling
├── part5_audio_recording.py    # Part 5: Audio recording
├── part6_text_to_speech.py     # Part 6: TTS
├── part7_speech_analysis.py    # Part 7: Analysis
├── part8_history_management.py # Part 8: History
├── part9_main_entry.py         # Part 9: Entry point
└── app_overview.md             # This overview file
```

## 🛠️ Key Technologies Used

### **GUI Framework**
- **tkinter**: Python's standard GUI library
- **ttk**: Modern-looking widgets

### **Audio Processing**
- **sounddevice**: Real-time audio recording
- **soundfile**: Audio file I/O
- **pydub**: Audio format conversion
- **pygame**: Audio playback

### **Speech Recognition**
- **speech_recognition**: Google Speech-to-Text API
- **fuzzywuzzy**: Fuzzy string matching for accuracy

### **Text-to-Speech**
- **gtts**: Google Text-to-Speech API

### **Data Storage**
- **JSON**: For sentences and history
- **WAV/MP3**: For audio files

## 🎨 User Interface Design

### **Color Scheme**
- **Background**: Light blue (`#e6f2ff`)
- **Record Button**: Green (`#4CAF50`)
- **Stop Button**: Red (`#E91E63`)
- **Play Button**: Blue (`#2196F3`)
- **Update Button**: Purple (`#6A1B9A`)

### **Layout**
- **Grid-based**: Organized in rows and columns
- **Responsive**: Elements resize with window
- **Modal windows**: History window blocks main window

## 🔧 Installation and Setup

### **Required Python Packages**
```bash
pip install sounddevice soundfile speech_recognition pydub fuzzywuzzy gtts pygame
```

### **System Dependencies**
- **FFmpeg**: For audio processing
- **Microphone**: For voice recording
- **Speakers**: For audio playback

### **Running the App**
```bash
python tin_hoc_tre.py
```

## 📊 Data Flow

### **Input Data**
- Practice sentences from `sentences.json`
- User voice input from microphone
- User text input from editor

### **Processing**
- Audio recording and conversion
- Speech-to-text conversion
- Text comparison and scoring
- Text-to-speech generation

### **Output Data**
- Pronunciation accuracy scores
- Feedback messages
- Practice history in `pronunciation_history.json`
- Audio files for playback

## 🎯 Learning Objectives

This app demonstrates:

1. **GUI Development**: Creating user interfaces with tkinter
2. **Audio Processing**: Recording, playing, and converting audio
3. **API Integration**: Using Google's speech services
4. **Data Management**: JSON file handling
5. **Error Handling**: Graceful error management
6. **Event-Driven Programming**: Responding to user actions
7. **Modular Design**: Organizing code into logical parts

## 🚀 Next Steps for Learning

1. **Study each part separately** to understand individual components
2. **Modify the UI** to change colors, fonts, or layout
3. **Add new features** like different languages or practice modes
4. **Improve error handling** for better user experience
5. **Add unit tests** to ensure reliability
6. **Optimize performance** for better responsiveness

This app is a great example of how multiple Python libraries can work together to create a useful, interactive application! 