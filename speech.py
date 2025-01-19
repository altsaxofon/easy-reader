#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from dimits import Dimits
import config
from player import audioPlayer
from books import books 

class Speech:
    
    def __init__(self):
        
        self.blink_led_callback = None  # Placeholder for blink callback
        self.led_on_callback = None  # Placeholder for blink callback
        self.led_off_callback = None  # Placeholder for blink callback

        # Initialize Dimits TTS library
        self.dt = Dimits(config.TTS_MODEL, modelDirectory=config.PATHS["TTS_MODEL_PATH"])  # Initialize TTS

        # Internal attribute for tracking the TTS generation state
        self._is_generating = False  # Use _ to indicate this is a private attribute

        # Pre generate speech on load
        self.pre_generate_tts()

    # Helper functions
    def register_blink_callback(self, callback):
        self.blink_led_callback = callback

    def register_led_on_callback(self, callback):
        self.led_on_callback = callback

    def register_led_off_callback(self, callback):
        self.led_off_callback = callback


    def _filepath_from_text(self, text):
        # Generate a safe filename from text
        filename = text.replace(" ", "_").replace(",", "").replace("ä", "a").replace("å", "a").replace("ö", "o").lower()

        # return filepath for speech
        filepath = config.PATHS["TTS_FILES_PATH"] / f"{filename}.wav"
        exists = filepath.exists() and filepath.stat().st_size > 0        
        return filename, filepath, exists

    def generate_speech(self, text):

        filename, filepath, exists  = self._filepath_from_text(text)
        # Check if the file exists
        if not exists:

            # If the file doesn't exist, generate it
            print(f"Generating audio file for: {text}")
            try:

                if self.blink_led_callback:
                    self.blink_led_callback(times=2, leaveOn=True)  # Blink LED using callback

                self.dt.text_2_audio_file(text, filename, "/home/pi/voice/", format="wav")
                print(f"Audio file generated successfully at {filepath}.")
            except Exception as e:
                print(f"Error in text_2_audio_file(): {e}")
                raise  # Re-raise the error for further handling
        else:
            #print(f"Audio file for '{text}' already exists.")
            pass

    def speak(self, text):
        
        _, filepath, exists  = self._filepath_from_text(text)

        if exists:
            audioPlayer.play(filepath)
            print(f'Speaking: {text}')
        else:
            print('Speech - Speak(): Filepath does not exist')

    def pre_generate_tts(self):
        """Pre-generate TTS for all common phrases and chapters."""
        print("Pre-generating TTS...")

        self._is_generating = True  # Set the flag to True
        if self.led_on_callback:
            self.led_on_callback()  #  Turn LED on using callback
        try:
            # Pre-generate TTS for all phrases
            for phrase in config.PHRASES.values():
                self.generate_speech(phrase)

            # Pre-generate TTS for chapter enumerations
            max_chapters = books.get_maximum_chapters()

            for chapter_num in range(1, max_chapters + 1):
                chapter_phrase = f"{config.PHRASES['chapter']} {chapter_num}"
                self.generate_speech(chapter_phrase)

            # Pre-generate TTS for book titles
            for book_name in books.get_books():
                author, title = books.get_author_and_title(book_name)
                self.generate_speech(title + " " + config.PHRASES['by'] + " " + author)

        except Exception as e:
            print(f"Error during TTS pre-generation: {e}")
        finally:
            print("Pre-generation finished.")
            if self.led_off_callback:
                self.led_off_callback()  #  Turn LED off using callback
            self._is_generating = False  # Set the flag to False
    
    @property
    def is_generating(self):
        return self._is_generating
    
    @is_generating.setter
    def is_generating(self, value):
        self._is_generating = value


speech = Speech()