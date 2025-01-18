import os
from pathlib import Path

# Settings

REWIND_TIME = 5  # The amount of seconds the player will rewind / recap on play
PROGRESS_UPDATE_INTERVAL = 1  # Interval to update progress in seconds

TTS_MODEL = "sv_SE-nst-medium" # TTS voice model
PHRASES = {
    "choose_book": "Välj bok",
    "choose_capter": "Välj del",
    "chapter": "Del",
    "by": "av",
    "the_end_of_book" : "Boken är slut, tryck på knappen för att påbörja nästa bok"
}

# Paths
HOME_DIR = Path(__file__).resolve().parent.parent
SD_CARD_PATH = "/mnt/sdcard"  # Path to SD card (FAT32 partition)

AUDIO_FOLDER = Path(SD_CARD_PATH) / "audiobooks"  # Audiobooks are stored here
TTS_MODEL_PATH = Path(HOME_DIR) / "piper"
TTS_FILES_PATH = Path(HOME_DIR) / "voice"

# Files
STATE_FILE = Path(SD_CARD_PATH) / "playback_state.json"  # Progress state file

# PIN Definitions
PLAY_BUTTON_PIN = 17
NEXT_BUTTON_PIN = 27
PREV_BUTTON_PIN = 22
LED_PIN = 18
SWITCH_PIN_A = 23