# === PART 1: IMPORTS AND DEPENDENCIES ===

# GUI (Graphical User Interface) libraries
import tkinter as tk                    # Main GUI library for Python
from tkinter import messagebox         # For showing popup messages
from tkinter import scrolledtext       # For text areas with scrollbars
from tkinter import ttk                # Modern-looking GUI widgets

# Audio processing libraries
import sounddevice as sd               # For recording audio from microphone
import soundfile as sf                 # For reading/writing audio files
import speech_recognition as sr        # For converting speech to text
from pydub import AudioSegment        # For audio file manipulation

# Text comparison library
from fuzzywuzzy import fuzz           # For comparing how similar two texts are

# Text-to-speech library
from gtts import gTTS                  # Google Text-to-Speech
import pygame.mixer                    # For playing audio

# Standard Python libraries
import os                              # For file operations
import time                            # For delays
import tempfile                        # For creating temporary files
import json                            # For reading/writing JSON files
from datetime import datetime          # For timestamps

"""
EXPLANATION:
- tkinter: Creates the visual interface (buttons, text boxes, etc.)
- sounddevice: Records audio from your microphone
- speech_recognition: Converts your spoken words into text
- fuzzywuzzy: Compares what you said vs what you should have said
- gTTS: Creates audio from text (plays correct pronunciation)
- pygame: Plays the audio files
""" 