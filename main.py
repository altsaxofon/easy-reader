#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Todo:
# Implement a settings JSON file stored on the Fat32 partition

"""main.py: Easy reader application."""

__author__      = "Erik Arnell"

import os
import time
import json
from pygame import mixer
from mutagen.mp3 import MP3 
from gpiozero import Button, DigitalInputDevice, LED
from dimits import Dimits
from pathlib import Path
 
from books import Books

# Initiate classes

books = Books()
print(books.get_books())


# Settings 



REWIND_TIME = 5  # The amount of seconds the player will rewind / recap on play
PROGRESS_UPDATE_INTERVAL = 1  # Interval to update progress in seconds

TTS_MODEL = "sv_SE-nst-medium" # TTS voice model - for english use e.g. 'en_GB-alba-medium'

# Phrases used by the TTS. If translated, use a voice model of correct language 
PHRASES = {
    "choose_book": "Välj bok",
    "choose_capter": "Välj del",
    "chapter": "Del",
    "by": "av",
    "the_end_of_book" : "Boken är slut, tryck på knappen för att påbörja nästa bok"
    }

# Paths

# Since our service run as SUDO we need to identify the home folder by looking at the dir of this script
# This is a bit hacky - better solution should be found
HOME_DIR = Path(__file__).resolve().parent.parent
SD_CARD_PATH = "/mnt/sdcard"  # Path to SD card (FAT32 partition) (update as necessary)

AUDIO_FOLDER = Path(SD_CARD_PATH) / "audiobooks"  # Audiobooks are stored here

TTS_MODEL_PATH = Path(HOME_DIR) / "piper"
TTS_FILES_PATH = Path(HOME_DIR) / "voice"

# FILES
STATE_FILE = Path(SD_CARD_PATH) / "playback_state.json"  # Progress state file


# PIN definitions
PLAY_BUTTON_PIN = 17
NEXT_BUTTON_PIN = 27
PREV_BUTTON_PIN = 22

LED_PIN = 18

SWITCH_PIN_A = 23

# Initialize hardware

button_play = Button(PLAY_BUTTON_PIN, pull_up=True, bounce_time=0.03)  
button_next = Button(NEXT_BUTTON_PIN, pull_up=True, bounce_time=0.03) 
button_prev = Button(PREV_BUTTON_PIN, pull_up=True, bounce_time=0.03) 

switch_a = DigitalInputDevice(SWITCH_PIN_A, pull_up=True, bounce_time=0.5)

button_led = LED(LED_PIN)  # Create an LED object for GPIO 18

# Initialize hardware callbacks

def hardware_callback(button_type):
    global is_generating
    global settings_mode

    if is_generating:
        print("TTS generation in progress. Please wait.")
        return
    
    if button_type == "play":
        settings_mode = False
        play_pause() 
    elif button_type == "next":
        arrow_key_pushed(1)
    elif button_type == "prev":
        arrow_key_pushed(-1)
    elif button_type == "switch":
        arrow_key_pushed(0)


# Attach the callback function to the button press event
button_play.when_pressed = lambda: hardware_callback('play')
button_next.when_pressed = lambda: hardware_callback('next')
button_prev.when_pressed = lambda: hardware_callback('prev')

switch_a.when_activated = lambda: hardware_callback('switch')
switch_a.when_deactivated = lambda: hardware_callback('switch')

# INITIATE MIXER AND TTS

mixer.init() # Audio playback mixer
dt = Dimits(TTS_MODEL, modelDirectory=TTS_MODEL_PATH) # TTS library

# Runtime variables

is_playing = False  # Default to not playing at startup
start_time = 0 
settings_mode = False
speech_sound = None  # Holds the pygame Sound object for TTS playback
speech_file = None  # Current temporary TTS file
is_generating = False


# Helper functions

# Ensure all required directories exist
def ensure_directories():
    directories = [
        AUDIO_FOLDER, 
        TTS_MODEL_PATH, 
        TTS_FILES_PATH
    ]
    
    for directory in directories:
        if not directory.exists():
            print(f"Directory {directory} does not exist. Creating it...")
            directory.mkdir(parents=True, exist_ok=True)  # Create the directory, including parents if necessary

# Blink the LED 
def blink_led(times=3, leaveOn = False):

    button_led.off() #Turn of led if on

    for i in range(times):  # Start from 0 to times-1
        button_led.on()
        time.sleep(0.3)  # LED on for 0.3 seconds
        button_led.off()
        time.sleep(0.2)  # LED off for 0.2 seconds
    
    if leaveOn:
        button_led.on()
        
def speak(text, speak_audio=True, ):
    global speech_sound, speech_file
    global dt
 
    # Ensure that dt (the TTS library) is initialized
    if dt is None:
        raise ValueError("Dimits object 'dt' is required.")

    # Generate a safe filename for the WAV file 
    filename = text.replace(" ", "_").replace(",", "").replace("ä", "a").replace("å", "a").replace("ö", "o").lower()
    filename_wav = f"{filename}.wav"
    filepath =  Path(TTS_FILES_PATH) / filename_wav

    try:
        # Check if the file exists
        if not filepath.exists() or filepath.stat().st_size == 0:
            # If the file doesn't exist, generate it
            print(f"Generating audio file for: {text}")
            try:
                blink_led(2, leaveOn = True)
                print(f"Calling text_2_audio_file with text: {text}")
                dt.text_2_audio_file(text, filename, "/home/pi/voice/", format="wav")
                print("Audio file generated successfully.")
            except Exception as e:
                print(f"Error in text_2_audio_file(): {e}")
                raise  # Re-raise the error for further handling
        else:
            #print(f"Audio file for '{text}' already exists.")
            pass

        if speak_audio:
            # If the flag is True, play the generated audio file
            print(f"Speaking: {text}")
            # Stop any previous speech playback
            if speech_sound and mixer.get_busy():
                print("Stopping current TTS playback.")
                speech_sound.stop()

            # Load and play the speech sound
            speech_sound = mixer.Sound(filepath)
            speech_sound.play()
        else:
            #print(f"Pre-generated WAV for '{text}' is ready but not spoken.")
            pass

    except Exception as e:
        print(f"Error in speak(): {e}")


def pre_generate_tts():
    """Pre-generate TTS."""
    global is_generating
    global state

    print("Pre-generating TTS")


    # Turn on the LED to indicate TTS generation
    button_led.on()
    # Set the flag to indicate TTS generation is in progress
    is_generating = True    


    # Generate the TTS phrases

    try:
        # Pre-generate TTS for all phrases
        for phrase in PHRASES.values():
            speak(phrase, speak_audio=False)  # Generate TTS without speaking it
        
        # Pre-generate TTS for chapter enumerations based on number of books files
        max_chapters = 0
        for book_name in state["books"]:
            book_files, author, title = get_book_files(book_name)
            max_chapters = max(max_chapters, len(book_files))

        # Pre-generate TTS for chapters based on the maximum number of chapters
        for chapter_num in range(1, max_chapters + 1):
            chapter_phrase = f"{PHRASES['chapter']} {chapter_num}"
            speak(chapter_phrase, speak_audio=False)  # Generate TTS for chapter titles

        # Pre-generate TTS for book titles
        for book_name in state["books"]:
            author, title = get_author_and_title(book_name)
            speak(title+" "+PHRASES['by']+" "+author, speak_audio=False)

    except Exception as e:
        print(f"Error during TTS pre-generation: {e}")
    finally:
        print("Pre generation of TTS finnished")
        is_generating = False
        button_led.off()  # Ensure the LED is turned off after pre-generation is done

def load_state():
    if not os.path.exists(STATE_FILE):
        # If the JSON file doesn't exist, create it with a default structure
        print("State file not found. Creating a new one...")
        
        # Initialize state with default values
        state = {
            "current_book": "",  # Store the folder name as the current book
            "books": {}
        }
        
        # Save the default state to the JSON file
        save_state(state)
        
        return state
    else:
        # If the file exists, load it
        with open(STATE_FILE, 'r') as f:
            return json.load(f)

def save_state(state):
    """Saves the state to the STATE_FILE."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)  # Added indent for better readability
    os.chmod(STATE_FILE, 0o664)  # user read/write, group read/write, others read

def get_author_and_title(book_name):
    """Extracts the author and title from the book folder name."""
    author, title = "Unknown", book_name
    if " - " in book_name:
        author, title = book_name.split(" - ", 1)
    return author, title

def get_book_files(book_name):
    """Returns the list of MP3 files for the book, and its metadata."""
    # Get all subdirectories (books) in AUDIO_FOLDER, skipping non-directories
    book_folders = [
        d for d in sorted(os.listdir(AUDIO_FOLDER))
        if os.path.isdir(os.path.join(AUDIO_FOLDER, d))
    ]

    # Ensure the book_name is valid
    if book_name not in book_folders:
        raise ValueError(f"Book name {book_name} is not found in the audio folder.")
    
    # Get the path to the selected book folder
    book_path = os.path.join(AUDIO_FOLDER, book_name)

    # Extract author and title from folder name (e.g., "Author - Title")
    folder_name = book_name
    author, title = get_author_and_title(folder_name)

    # Get and return the list of MP3 files in the book folder and metadata
    mp3_files = sorted([
        os.path.join(book_path, f)
        for f in os.listdir(book_path)
        if f.endswith(".mp3") and not f.startswith("._")
    ])
    
    return mp3_files, author, title

def get_file_length(file_path):
    """Get the length of an MP3 file."""
    return int(MP3(file_path).info.length)

def load_books():
    """Loads all books from AUDIO_FOLDER and updates the JSON file."""
    book_folders = [
        d for d in sorted(os.listdir(AUDIO_FOLDER))
        if os.path.isdir(os.path.join(AUDIO_FOLDER, d))
    ]
    
    # Load the current state
    state = load_state()

    # Compare the current book list with the stored books
    existing_books = set(state["books"].keys())
    new_books = set(book_folders)

    # Add new books or update existing ones
    for book in book_folders:  # Using the folder name as the identifier
        if book not in existing_books:
            print(f"Adding new book: {book}")
            # Get the files and metadata for the book
            author, title = get_author_and_title(book)
            speak(title+" "+PHRASES['by']+" "+author)
            state["books"][book] = {
                "position": 0,
                "current_file": 0,
            }
    # Remove books that no longer exist
    for book in existing_books:
        if book not in new_books:
            print(f"Removing book: {book}")
            del state["books"][book]
    
    # Check if current_book exists, if not set to the first book
    if state["current_book"] not in book_folders:
        print(f"Current book {state['current_book']} not found, using the first book instead.")
        state["current_book"] = book_folders[0]  # Fallback to the first book in the folder

    save_state(state)
    return state

def play_pause():
    """Toggle play/pause state of the current book."""
    global state
    global is_playing
    global start_time
    global settings_mode
    global speech_sound
    global is_generating

    if is_generating:
        print("TTS generation in progress. Please wait.")
        return

    current_book = state["current_book"]  # Now referencing by folder name
    if current_book == "":
        print("Error: No current book selected.")
        return
    book_files, author, title = get_book_files(current_book)
 
 # Get current book's state (position and current_file)
    book_state = state["books"][current_book]

  # Validate current_file index
    if book_state["current_file"] >= len(book_files):
        print(f"Warning: current_file index out of range for {current_book}. Resetting to 0.")
        book_state["current_file"] = 0

    current_file = book_files[book_state["current_file"]]
    

    if is_playing or settings_mode:
        # Music is playing, so pause it
        mixer.music.stop()
        # Set the is_playing flag to False
        is_playing = False
        # Turn off the LED when paused
        button_led.off()  # Turn off LED when paused
        # Save the current position when paused
        save_state(state)
        # Print a message to the console
        print(f"Pausing current book: {current_book}")    

    elif not is_playing:
        if speech_sound and mixer.get_busy():
            speech_sound.stop()
        # Music is not playing, so start it from the saved position
        start_time = book_state["position"]
        start_position = max(0, book_state["position"]-REWIND_TIME)  # Start slightly earlier
        # Load the current file and play it from the saved position
        print(f"Attempting to load: {current_file}")
        mixer.music.load(current_file)         
        mixer.music.play(start=start_position)
        # Set the is_playing flag to True
        is_playing = True
        # Turn on the LED when playing
        button_led.on()
        # Save the current position when playing
        save_state(state)
        # Print a message to the console
        print(f"Playing current book: {current_book}")    

def arrow_key_pushed(direction):
    global state
    global is_playing
    global settings_mode

    # Check if the settings mode is active
    if settings_mode and not direction == 0:
        # If the A switch is active, change the book, otherwise change the chapter
        if switch_a.value == 1:
            change_book(direction)
        else:
            change_chapter(direction)
    else:
        settings_mode = True
        play_pause()

        if switch_a.value == 1:
            speak(PHRASES["choose_book"])
        else:
            speak(PHRASES["choose_capter"])
 

def play_next():
    """Play the next file in the current book."""
    global state
    global start_time
    global settings_mode

    current_book = state["current_book"]
    book_files, author, title = get_book_files(current_book)

    # Get the current file index and update to the next one
    book_state = state["books"][current_book]
    book_state["current_file"] += 1

    # If we've reached the end of the book, reset to the first file
    if book_state["current_file"] >= len(book_files):
        book_names = list(state["books"].keys())
        current_index = book_names.index(current_book)
        
        # Move to the next book, wrap around if at the last book
        current_index = (current_index + 1) % len(book_names)
        state["current_book"] = book_names[current_index]
        book_state = state["books"][state["current_book"]]
        book_state["current_file"] = 0  # Start from the first file of the new book

        speak(PHRASES["the_end_of_book"])
        #play_pause()  # Pause playback after changing the book

    # Reset position for the new file and play it
    book_state["position"] = 0
    start_time = 0
    current_file = book_files[book_state["current_file"]]
    mixer.music.load(current_file)
    mixer.music.play(start=book_state["position"])
    save_state(state)

def change_chapter(direction):

    current_book = state["current_book"]
    book_files, author, title = get_book_files(current_book)
    book_state = state["books"][current_book]

    book_state["current_file"] += direction

    # If we've reached the end of the book, reset to the first file
    if book_state["current_file"] >= len(book_files):
        book_state["current_file"] = 0  # Start from the first file
    elif book_state["current_file"] < 0:
        book_state["current_file"] = len(book_files) - 1  # Start from the last file

    # Reset position for the new file and play it
    book_state["position"] = 0
    start_time = 0
    current_file = book_files[book_state["current_file"]]
    speak(PHRASES["chapter"]+" "+ str(book_state["current_file"] + 1))

    save_state(state)

def change_book(direction):

    # Get the list of book names
    book_names = list(state["books"].keys())  # Convert dictionary keys to a list

    current_book = state["current_book"]
    current_index = book_names.index(current_book) if current_book in book_names else 0
    current_index += direction
    
    # Wrap the index around the list of books
    if current_index < 0:
        current_index = len(book_names) - 1
    elif current_index >= len(book_names):
        current_index = 0
    
    # Update the current book
    current_book = book_names[current_index]
    state["current_book"] = current_book
    save_state(state)  # Save updated state
    author, title = get_author_and_title(current_book)
    speak(title+" "+PHRASES['by']+" "+author)

# Main loop

# Initate libraries


print("Starting Easy Reader")

# Create directories if they not exist
ensure_directories()

# Load books into state
state = load_books()  # Load and update the book list

# Blink led to indicate startup
blink_led()

# Main loop to update progress periodically
last_update = time.time()

# Main loop to periodically update the position
last_position_update = time.time()

# Pre generate TTS:
pre_generate_tts()
                         
while True:
    #time.sleep(0.1)

    # Check if the music is playing and periodically save progress
    if mixer.music.get_busy() and is_playing:
        
        # Only save state every 1 second to avoid unnecessary writes
        if time.time() - last_position_update >= PROGRESS_UPDATE_INTERVAL:
            current_book = state["current_book"]
            book_state = state["books"][current_book]
            current_position = start_time + mixer.music.get_pos() // 1000  # Convert to seconds
            book_state["position"] = current_position
            save_state(state)
            last_position_update = time.time()

    if not mixer.music.get_busy() and is_playing:
        play_next()
    
    time.sleep(0.1)