import os
import time
import wave
import contextlib

from pygame import mixer
from mutagen.mp3 import MP3 

from books import books
from state import state

class Playback:
    def __init__(self):

        self.current_file = None  # Store the current file being played
        self.start_time = 0  # Time tracking for the playback position
        
        # Initialize the pygame mixer
        mixer.pre_init(frequency=48000, buffer=2048)
        mixer.init()
        
    def stop(self):
        """Stop the current audio."""
        if self.is_playing:
            mixer.music.stop()
        print("Stopped current audio.")
    
    def play(self, audio_file_path, position):

        # If there's a file playing, stop it before starting the new one
        if self.is_playing:
            self.stop_current()
        
        print(f"Playback module: playing file: {audio_file_path}")
        self.current_file = audio_file_path
        mixer.music.load(audio_file_path)

        # Reset the position if longar then file
        if position >= self._get_audio_length(audio_file_path):
            position = 0
        
        mixer.music.play(start=position)
        print("Started playback.")    
        
    def save_position(self):
        """Save the current playback position."""
        current_position = self.start_time + mixer.music.get_pos() // 1000  # Convert to seconds
        self.state.set_position(current_position)
        print(f"Position saved: {current_position}s")

    def _get_audio_length(file_path):
        """Get the length of an MP3 or WAV file."""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.mp3':
            # For MP3, use mutagen
            return int(MP3(file_path).info.length)
        elif file_extension == '.wav':
            # For WAV, use the wave module
            with contextlib.closing(wave.open(file_path, 'r')) as f:
                return f.getnframes() / float(f.getframerate())
        else:
            raise ValueError("Unsupported file type. Only MP3 and WAV are supported.")   
        
    @property
    def is_playing(self):
        """Returns the current book name."""
        return mixer.music.get_busy()
    
