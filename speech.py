#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from pygame import mixer
from pathlib import Path
from dimits import Dimits
import config

# Settings
TTS_MODEL = "sv_SE-nst-medium"  # Change to your TTS model
TTS_MODEL_PATH = Path("/home/pi/piper")  # Path to TTS model
TTS_FILES_PATH = Path("/home/pi/voice")  # Path to store generated TTS files

# Phrases used by the TTS
PHRASES = {
    "choose_book": "Välj bok",
    "choose_capter": "Välj del",
    "chapter": "Del",
    "by": "av",
    "the_end_of_book": "Boken är slut, tryck på knappen för att påbörja nästa bok"
}

# Initialize mixer
mixer.pre_init(frequency=48000, buffer=2048)
mixer.init()  # Audio playback mixer

# Initialize Dimits TTS library
dt = Dimits(config.TTS_MODEL, modelDirectory=config.TTS_MODEL_PATH)  # Initialize TTS

# Variables
speech_sound = None  # Holds the pygame Sound object for TTS playback
is_generating = False  # Flag to indicate if TTS generation is in progress

# Helper functions
def speak(text, speak_audio=True):
    """Generate and play the speech for a given text."""
    global speech_sound
    filename = text.replace(" ", "_").replace(",", "").replace("ä", "a").replace("å", "a").replace("ö", "o").lower()
    filepath = TTS_FILES_PATH / f"{filename}.wav"

    try:
        # If the file doesn't exist, generate it
        if not filepath.exists() or filepath.stat().st_size == 0:
            print(f"Generating audio file for: {text}")
            dt.text_2_audio_file(text, filename, "/home/pi/voice/", format="wav")

        if speak_audio:
            print(f"Speaking: {text}")
            # Stop any previous speech playback
            if speech_sound and mixer.get_busy():
                speech_sound.stop()

            # Load and play the speech sound
            speech_sound = mixer.Sound(filepath)
            speech_sound.play()

    except Exception as e:
        print(f"Error in speak(): {e}")

def pre_generate_tts():
    """Pre-generate TTS for all common phrases and chapters."""
    global is_generating
    print("Pre-generating TTS...")

    is_generating = True
    try:
        # Pre-generate TTS for all phrases
        for phrase in PHRASES.values():
            speak(phrase, speak_audio=False)

        # Pre-generate TTS for chapter enumerations
        for chapter_num in range(1, 21):  # Example: Pre-generate up to 20 chapters
            chapter_phrase = f"{PHRASES['chapter']} {chapter_num}"
            speak(chapter_phrase, speak_audio=False)

    except Exception as e:
        print(f"Error during TTS pre-generation: {e}")
    finally:
        print("Pre-generation finished.")
        is_generating = False