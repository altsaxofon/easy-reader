#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Todo:
# Implement a settings JSON file stored on the Fat32 partition
# only save state in state file! on update

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
 
# Import a global instance of state and books
import config
from books import books
from state import state
from player import audioPlayer


# test the new class
print(books.get_books())


# Settings 



REWIND_TIME = 1  # The amount of seconds the player will rewind / recap on play
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
mixer.pre_init(frequency=48000, buffer=2048)
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
            audioPlayer.play(filepath)
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
        max_chapters = books.get_maximum_chapters();

        for chapter_num in range(1, max_chapters + 1):
            chapter_phrase = f"{PHRASES['chapter']} {chapter_num}"
            speak(chapter_phrase, speak_audio=False)  # Generate TTS for chapter titles

        # Pre-generate TTS for book titles
        for book_name in books.get_books():
            author, title = books.get_author_and_title(book_name)
            speak(title+" "+PHRASES['by']+" "+author, speak_audio=False)

    except Exception as e:
        print(f"Error during TTS pre-generation: {e}")
    finally:
        print("Pre generation of TTS finnished")
        is_generating = False
        button_led.off()  # Ensure the LED is turned off after pre-generation is done

def save_position():
    global start_time
    current_position = start_time + mixer.music.get_pos() // 1000  # Convert to seconds
    print("Saving position")
    print(f"start time: {start_time}")
    print(f"Player position: {mixer.music.get_pos()}")
    current_position = start_time + mixer.music.get_pos() // 1000  # Convert to seconds
    print(f"current position: {current_position}")
    state.set_position(current_position)
    

def play_pause():
    """Toggle play/pause state of the current book."""
    global is_playing
    global start_time
    global settings_mode
    global speech_sound
    global is_generating

    if is_generating:
        print("TTS generation in progress. Please wait.")
        return

    current_file = books.get_chapter_file(state.current_book, state.get_chapter())
    print(f'Play_Pause(): current file: {current_file}')

    if is_playing or settings_mode:
        
        # Set is_playing flag to false
        is_playing = False

        # Stop audio
        audioPlayer.stop()

        # Turn off the LED 
        button_led.off() 
        
        # Save the current position when paused
        ######

        state.save_state() 
        
        # Print a message to the console
        print(f"Main - Pausing current book: {current_file}")    

    elif not is_playing:
        
        # Set the is_playing flag to True
        is_playing = True

        # Get start position
        start_time = state.get_position()
        start_position = max(0, start_time-config.REWIND_TIME)  # Start slightly earlier

        # Play the current file
        audioPlayer.play(current_file, start_position)

        # Turn on the LED when playing
        button_led.on()
        
        print(f"Playing current book: {current_file}")    

def arrow_key_pushed(direction):
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
    global start_time
    global settings_mode

    # Stop audio plauyer
    audioPlayer.stop()

    # Get the current file index and update to the next one
    next_chapter = state.get_chapter()+1

    print(f'Playing next chapter')
    print(f'Current chapter: {state.get_chapter()}')
    print(f'Next chapter before check: {next_chapter}')

    # If we've reached the end of the book, reset to the first file
    if next_chapter >= books.get_number_of_chapters(state.current_book):
        
        print(f'Next chapter: {next_chapter} >= {books.get_number_of_chapters(state.current_book)} ')

        # Get the index of the current book
        current_index = books.get_books().index(state.current_book)
        
        # Move to the next book, wrap around if at the last book
        current_index = (current_index + 1) % books.get_number_of_books()
        state.current_book = books.get_books()[current_index]

        # Reset progress for this book
        state.set_chapter(0)
        state.set_position(0)
        
        # Declare the end of the book
        speak(PHRASES["the_end_of_book"])

    else:
        print(f'Playn next chapter: {next_chapter}')
        state.set_chapter(next_chapter)
        state.set_position(0)


    # Reset position for the new file and play it

    print(f'Chapter updated to chapter {state.get_chapter()}');
    start_time = 0
    print(f'Next chapter file: {books.get_chapter_file(state.current_book, state.get_chapter())}')
    
    #Play next chapter from the start
    audioPlayer.play(books.get_chapter_file(state.current_book, state.get_chapter()), 0)

def change_chapter(direction):

    # Get current chapter
    currentChapter = state.get_chapter();
    numberOfChaptersInCurrentBook = books.get_number_of_chapters(state.current_book);
    #Get chapter and add or remove one depenging on direction
    nextChapter = currentChapter + direction
    # If we've reached the end of the book, reset to the first file
    if nextChapter >= numberOfChaptersInCurrentBook:
        nextChapter = 0  # Start from the first file
    # If we go back from 1, go to the last chapter of the book
    elif nextChapter < 0:
        nextChapter = numberOfChaptersInCurrentBook - 1  # Start from the last file

    # Update the chapter
    state.set_chapter(nextChapter)
    # Reset position for the new file and play it
    state.set_position(0)
    start_time = 0
    
    # Announce the selected chapter
    speak(PHRASES["chapter"]+" "+ str(state.get_chapter() + 1))

    state.save_state()

def change_book(direction):

    # Get the list of book names
    book_names = books.get_books()

    # Get total number of books
    total_amount_of_books = books.get_number_of_books();
 
    # Get index of current book 
    current_index = book_names.index(state.current_book) if state.current_book in book_names else 0
    next_book = current_index + direction
    
    # Wrap the index around the list of books
    if next_book < 0:
        next_book = total_amount_of_books - 1
    elif next_book >= total_amount_of_books:
        next_book = 0
    
    # Update the current book
    state.current_book = book_names[next_book]
    author, title = books.get_author_and_title(state.current_book)
    speak(title+" "+PHRASES['by']+" "+author)

# Main loop

# Initate libraries


print("Starting Easy Reader")

# Create directories if they not exist
ensure_directories()

# Load books into state
# state = load_books()  # Load and update the book list

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
    if AudioPlayer.is_playing and is_playing:
        
        # Only save state every 1 second to avoid unnecessary writes
        if time.time() - last_position_update >= PROGRESS_UPDATE_INTERVAL:
            save_position()
            last_position_update = time.time()

    if not AudioPlayer.is_playing and is_playing:
        play_next()
    
    time.sleep(0.1)