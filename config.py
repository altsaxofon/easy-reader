import os
from pathlib import Path
import json

# Settings

DEFAULT_REWIND_TIME = 10  # The amount of seconds the player will rewind / recap on play
DEFAULT_UPDATE_INTERVAL = 10  # Interval to update progress in seconds

# Text to speech

TTS_MODEL = "sv_SE-nst-medium" # TTS voice model, Swedish

# Remove the line above and uncomment the one below to use an english voice model,or find other languages/models at https://rhasspy.github.io/piper-samples/
# TTS_MODEL = "en_GB-alba-medium" 

# Phrases for the speak synthesis in swedish
PHRASES = {
    "choose_book": "Välj bok",
    "choose_chapter": "Välj del",
    "chapter": "Del",
    "by": "av",
    "the_end_of_book" : "Boken är slut, tryck på knappen för att påbörja nästa bok",
    "player_ready" : "Tryck på knappen för att påbörja uppläsningen"

}

# Remove the PHRASES above and uncomment the ones below for english, or translate to another language

"""
PHRASES = {
    "choose_book": Select book",
    "choose_chapter": "Select chapter",
    "chapter": "Chapter",
    "by": "by",
    "the_end_of_book" : "The book is finished, press the button to start the next book.",
    "player_ready" : "Press the button to start the reading."
}
"""

# Base directories
HOME_DIR = Path(__file__).resolve().parent.parent
SD_CARD_PATH = "/mnt/sdcard"  # Path to SD card (FAT32 partition)

# Paths 
PATHS = {
    "AUDIO_FOLDER": Path(SD_CARD_PATH) / "audiobooks",
    "TTS_MODEL_PATH": Path(HOME_DIR) / "piper",
    "TTS_FILES_PATH": Path(HOME_DIR) / "voice"
}
# Files
STATE_FILE = Path(SD_CARD_PATH) / "playback_state.json"  # Progress state file
SETTINGS_FILE = Path(SD_CARD_PATH) / "settings.json"  # Progress state file

# PIN Definitions
PLAY_BUTTON_PIN = 17
NEXT_BUTTON_PIN = 27
PREV_BUTTON_PIN = 22
LED_PIN = 18
SWITCH_PIN_A = 23

# Make sure all paths exists
for name, path in PATHS.items():
    if not path.exists():
        print(f"Directory {path} does not exist. Creating it...")
        path.mkdir(parents=True, exist_ok=True)  # Create the directory, including parents if necessary

# Load settings from SD-CARD
def create_default_settings():
    """Creates the settings file with default values if it does not exist."""
    default_settings = {
        "rewind_time_seconds": DEFAULT_REWIND_TIME,
        "update_interval_seconds": DEFAULT_UPDATE_INTERVAL
    }

    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        SETTINGS_FILE.write_text(json.dumps(default_settings, indent=4))  # Write JSON
        print(f"Created default settings file at {SETTINGS_FILE}")
    except Exception as e:
        print(f"Error creating settings file: {e}")

def load_settings():
    """Loads rewind and sleep settings from the JSON file. Creates the file if missing."""
    if not SETTINGS_FILE.exists():
        create_default_settings()

    # Default values
    rewind_time = DEFAULT_REWIND_TIME
    update_interval = DEFAULT_UPDATE_INTERVAL

    try:
        settings = json.loads(SETTINGS_FILE.read_text())  # Read JSON

        # Validate and apply settings
        rewind_time = int(settings.get("rewind_time_seconds", rewind_time))
        sleep_time = int(settings.get("update_interval_seconds", update_interval))

        print(f"Loaded settings: Rewind {rewind_time}s, Update Interval {update_interval}s")

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"Warning: Failed to load settings.json ({e}). Using defaults.")

    return rewind_time, update_interval

# Ensure settings file exists & load settings
REWIND_TIME, UPDATE_INTERVAL = load_settings()