#!/usr/bin/env python

"""main.py: Easy reader application."""

__author__      = "Erik Arnell"

# TODO
# use python espeak-ng library instead of subprocess

# Add proper support for PIPER TTS as an alternative to espeak-ng (is it to slow - can we generate and store wavs instead)
# Remove the need to specify paths in the code, make the paths relative to the application.
# Add support for translation of TTS 

import os
import time
import json
from pygame import mixer
from mutagen.mp3 import MP3 
from gpiozero import Button, DigitalInputDevice, LED
import subprocess
import tempfile

# Constants
#AUDIO_FOLDER = "/home/admin/easyreader/audiobooks"  # Use a local folder in the project for MP3s
#STATE_FILE = "/home/admin/easyreader/playback_state.json"  # Save playback state locally

SD_CARD_PATH = "/media/admin/CF2B-FA41"  # Path to SD card (FAT32 partition) (update as necessary)
AUDIO_FOLDER = os.path.join(SD_CARD_PATH, "audiobooks")  # Audiobooks are stored here
STATE_FILE = os.path.join(SD_CARD_PATH, "playback_state.json")  # Progress state file

TEMP_DIR = tempfile.gettempdir()  # Temporary directory for generated audio files
REWIND_TIME = 5  # Seconds (adjust as needed)
PROGRESS_UPDATE_INTERVAL = 1  # Interval to update progress in seconds

# SETTINGS
TTS_SPEED = 120 # Speed for the speech syntesis. 200 is fast, 150 is slow
USE_PIPER = False  # Set to True to use the piper TTS tool

os.environ["PATH"] = os.environ["PATH"] + ":/home/admin/easyreader"

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

def button_play_callback():
    global settings_mode
    if settings_mode:
        settings_mode = False
    play_pause() 

def button_next_callback():
    arrow_key_pushed(1)

def button_prev_callback():
    arrow_key_pushed(-1)

def switch_callback():
    arrow_key_pushed(0)


# Attach the callback function to the button press event
button_play.when_pressed = button_play_callback
button_next.when_pressed = button_next_callback
button_prev.when_pressed = button_prev_callback

switch_a.when_activated = switch_callback
switch_a.when_deactivated = switch_callback

mixer.init()

# Helper functions

# Blink the LED 
def blink_led():
    button_led.on()
    time.sleep(0.5)  # LED on for 0.5 seconds
    button_led.off()
    time.sleep(0.5)  # LED off for 0.5 seconds
    button_led.on()
    time.sleep(0.5)  # LED on for 0.5 seconds
    button_led.off()


def speak(text):
    global speech_sound, speech_file
    print(f"Speaking: {text}")
    try:
        # Cleanup the previous temporary file
        cleanup_tts_file()

        # Generate a new temporary `.wav` file for the given text
        speech_file = os.path.join(TEMP_DIR, "speech.wav")
        if USE_PIPER:
            # Use the piper tool for TTS synthesis (NOT FUNCTIONING AT THE MOMENT)
            command = f'echo "{text}" | /home/admin/easyreader/piper/piper --model /home/admin/easyreader/piper/sv_SE-nst-medium.onnx --output-raw | aplay -r 22050 -f S16_LE -t raw -'
            subprocess.run(command, shell=True, check=True)  # Wait until the process finishes

            # --output file {speech_file}'
        else:
            command = f'espeak-ng -v sv+f3 -s {TTS_SPEED} "{text}" -w {speech_file}'
            #subprocess.call(command, shell=True)
            subprocess.run(command, shell=True, check=True)  # Wait until the process finishes

            # Stop any ongoing TTS playback
            if speech_sound and mixer.get_busy():
                print("Stopping current TTS playback.")
                speech_sound.stop()

            # Load the generated file and play it
            speech_sound = mixer.Sound(speech_file)
            speech_sound.play()

    except Exception as e:
        print(f"Error in speak(): {e}")
    finally:
        # Ensure temporary files are cleaned up
        cleanup_tts_file()

# Helper function to clean up temporary files
def cleanup_tts_file():
    global speech_file
    if speech_file and os.path.exists(speech_file):
        os.remove(speech_file)
        speech_file = None
        print("Temporary TTS file cleaned up.")


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
    if " - " in folder_name:
        author, title = folder_name.split(" - ", 1)
    else:
        # Default to entire folder name as title if the format is not followed
        author = "Unknown"
        title = folder_name

    # Get and return the list of MP3 files in the book folder and metadata
    mp3_files = sorted([
        os.path.join(book_path, f)
        for f in os.listdir(book_path)
        if f.endswith(".mp3")
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
            book_files, author, title = get_book_files(book)
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



# Main logic
state = load_books()  # Load and update the book list
is_playing = False  # Default to not playing at startup
start_time = 0 
settings_mode = False
speech_sound = None  # Holds the pygame Sound object for TTS playback
speech_file = None  # Current temporary TTS file



def play_pause():
    """Toggle play/pause state of the current book."""
    global state
    global is_playing
    global start_time
    global settings_mode
    global speech_sound
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
            speak("Välj bok. Nuvarande bok är: " + state["current_book"])
        else:
            speak("Välj del. Nuvarande del är: " + str(state["books"][state["current_book"]]["current_file"] + 1))
 

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

        speak(f"Byter till nästa bok: {state['current_book']}. Tryck på knappen för att fortsätta")
        play_pause()  # Pause playback after changing the book

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
    speak("Del " + str(book_state["current_file"] + 1))

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
    speak(current_book)


# Main loop


# Blink led to indicate startup
blink_led()

# Main loop to update progress periodically
last_update = time.time()

# Main loop to periodically update the position
last_position_update = time.time()


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
    
    # wait 0.1 sek IS THIS GOOD? (question to chat GPT)
    time.sleep(0.1)
