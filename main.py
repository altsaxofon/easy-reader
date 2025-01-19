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
from hardware import Hardware

# Import a global instance of state and books
import config
from books import books
from state import state
from player import audioPlayer
from speech import speech

# Initialize hardware

# Define callback functions
def play_callback():
    print("Play button pressed")
    play_pause()

def next_callback():
    print("Next button pressed")
    arrow_key_pushed(1)

def prev_callback():
    print("Previous button pressed")
    arrow_key_pushed(-1)

def switch_callback():
    print("Switch activated/deactivated")
    arrow_key_pushed(0)

callbacks = {
    'play': play_callback,
    'next': next_callback,
    'prev': prev_callback,
    'switch': switch_callback
}

# Initialize hardware
hardware = Hardware(callbacks)


if button_type == "play":
    settings_mode = False
    play_pause() 
elif button_type == "next":
    arrow_key_pushed(1)
elif button_type == "prev":
    arrow_key_pushed(-1)
elif button_type == "switch":
    arrow_key_pushed(0)


# Runtime variables

is_playing = False  # Default to not playing at startup
start_time = 0 
settings_mode = False
speech_sound = None  # Holds the pygame Sound object for TTS playback
speech_file = None  # Current temporary TTS file
is_generating = False

        
def save_position():
    """Save the current playback position."""
    
    # Add the elapsed playing time to the start_time
    current_position = start_time + (mixer.music.get_pos() // 1000)  # Convert to seconds
    print("Saving position")
    print(f"start time: {start_time}")
    print(f"Player position (ms): {mixer.music.get_pos()}")
    print(f"Current position (s): {current_position}")
    state.set_position(current_position)

def play_pause():
    """Toggle play/pause state of the current book."""
    global is_playing
    global start_time
    global settings_mode
    global is_generating

    if is_generating:
        print("TTS generation in progress. Please wait.")
        return

    current_file = books.get_chapter_file(state.current_book, state.get_chapter())
    print(f'Play_Pause(): current file: {current_file}')

    if is_playing or settings_mode:
        
        # Pausing playback
        is_playing = False

        # Calculate and save the elapsed time
        elapsed_time = mixer.music.get_pos() // 1000  # Convert milliseconds to seconds
        start_time += elapsed_time  # Add elapsed time to the start_time

        # Stop audio and save state
        audioPlayer.stop()
        save_position()

        # Turn off the LED
        button_led.off()

        print(f"Paused at position: {start_time}s in {current_file}")
   

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
            speech.speak(config.PHRASES["choose_book"])
        else:
            speech.speak(config.PHRASES["choose_capter"])
 

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
        speech.speak(config.PHRASES["the_end_of_book"])

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
    speech.speak(config.PHRASES["chapter"]+" "+ str(state.get_chapter() + 1))

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
    speech.speak(title+" "+config.PHRASES['by']+" "+author)

# Main loop

# Initate libraries


print("Starting Easy Reader")

# Blink led to indicate startup
blink_led()

# Main loop to update progress periodically
last_update = time.time()

# Main loop to periodically update the position
last_position_update = time.time()
                   
while True:
    #time.sleep(0.1)

    # Check if the music is playing and periodically save progress
    if audioPlayer.is_playing and is_playing:
        
        # Only save state every 1 second to avoid unnecessary writes
        if time.time() - last_position_update >= config.PROGRESS_UPDATE_INTERVAL:
            save_position()
            last_position_update = time.time()

    if not audioPlayer.is_playing and is_playing:
        play_next()
    
    time.sleep(0.1)