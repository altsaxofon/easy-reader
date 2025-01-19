#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from dimits import Dimits
import config
from player import audioPlayer
from books import books 

class Speech:
    
    def __init__(self):
        # Initialize Dimits TTS library
        self.dt = Dimits(config.TTS_MODEL, modelDirectory=config.TTS_MODEL_PATH)  # Initialize TTS

        # Variables
        self.is_generating = False  # Flag to indicate if TTS generation is in progress

    # Helper functions

    def _filepath_from_text(text):
        
        # Generate a safe filename from text
        filename = text.replace(" ", "_").replace(",", "").replace("ä", "a").replace("å", "a").replace("ö", "o").lower()

        # return filepath for speech
        filepath = config.TTS_FILES_PATH / f"{filename}.wav"
        exists = filepath.exists() and filepath.stat().st_size > 0        
        return filename, filepath, exists

    def generate_speech(self, text):

        filename, _, exists  = self._filepath_from_text(text)
        # Check if the file exists
        if not exists:

            # If the file doesn't exist, generate it
            print(f"Generating audio file for: {text}")
            try:
                #blink_led(2, leaveOn = True)
                self.dt.text_2_audio_file(text, filename, "/home/pi/voice/", format="wav")
                print("Audio file generated successfully at {}.")
            except Exception as e:
                print(f"Error in text_2_audio_file(): {e}")
                raise  # Re-raise the error for further handling
        else:
            print(f"Audio file for '{text}' already exists.")
            pass

    def speak(self, text):
        
        _, filepath, exists  = self._filepath_from_text(text)

        if exists:
            audioPlayer.play(filepath)
        else:
            print('Speech - Speak(): Filepath does not exist')

    def pre_generate_tts(self):
        """Pre-generate TTS for all common phrases and chapters."""
        print("Pre-generating TTS...")

        is_generating = True
        try:
            # Pre-generate TTS for all phrases
            for phrase in config.PHRASES.values():
                self.generate_speech(phrase, speak_audio=False)

            # Pre-generate TTS for chapter enumerations
            max_chapters = books.get_maximum_chapters();

            for chapter_num in range(1, max_chapters + 1):
                chapter_phrase = f"{config.PHRASES['chapter']} {chapter_num}"
                self.generate_speech(chapter_phrase, speak_audio=False)

            # Pre-generate TTS for book titles
            for book_name in books.get_books():
                author, title = books.get_author_and_title(book_name)
                self.generate_speech(title+" "+config.PHRASES['by']+" "+author, speak_audio=False)
            

        except Exception as e:
            print(f"Error during TTS pre-generation: {e}")
        finally:
            print("Pre-generation finished.")
            is_generating = False