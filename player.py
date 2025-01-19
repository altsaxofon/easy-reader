from pygame import mixer
from mutagen.mp3 import MP3 

from books import books

class AudioPlayer:
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
        print("Player - stopped current audio.")
    
    def play(self, audio_file_path, start_time_ms = 0):

        # If there's a file playing, stop it before starting the new one
        if self.is_playing:
            self.stop()
        
        print(f"Playback module: playing file: {audio_file_path}")
        self.current_file = audio_file_path
        mixer.music.load(audio_file_path)

        # Reset the position if longar then file
        if self._get_audio_length(audio_file_path) and start_time_ms >= self._get_audio_length(audio_file_path):
            start_time_ms = 0

        # Convert start time from milliseconds to seconds
        start_time_s = start_time_ms / 1000
        mixer.music.play(start=start_time_s)
        print(f"Player - Started audio at {start_time_s} seconds.")

    def get_position_ms():
        return mixer.music.get_pos()

    def _get_audio_length(self, file_path):
        """Get the length of an MP3 file."""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.mp3':
            # For MP3, use mutagen
            return int(MP3(file_path).info.length)
        else:
            return False
        
    @property
    def is_playing(self):
        return mixer.music.get_busy()

#Instanciaate audio player    
audioPlayer = AudioPlayer()
