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

# Connect hardware callbacks
speech.register_blink_callback(hardware.blink_led)
speech.register_led_on_callback(hardware.led_on)
speech.register_led_off_callback(hardware.led_off)
        
def save_position():
    """Save the current playback position."""
    
    # Add the elapsed playing time to the start_time
    current_position = start_time + (mixer.music.get_pos() // 1000)  # Convert to seconds
    state.set_position(current_position)

def play_pause():
    """Toggle playback or pause of the current book."""
    global is_playing, start_time, settings_mode, is_generating

    if is_generating:
        print("TTS generation in progress. Please wait.")
        return

    settings_mode = False

    if is_playing:
        # Pause playback
        pause_audio()
    else:
        # Resume or start playback
        resume_audio()

def pause_audio():
    """Handles pausing the audio."""
    global is_playing, start_time

    is_playing = False
    elapsed_time = mixer.music.get_pos() // 1000  # Elapsed time in seconds
    start_time += elapsed_time  # Update start time
    audioPlayer.stop()
    save_position()
    hardware.led_off()

def resume_audio():
    """Handles resuming or starting the audio."""
    global is_playing, start_time

    # Get current file
    current_file = books.get_chapter_file(state.current_book, state.get_chapter())

    is_playing = True
    start_time = state.get_position()  # Get playback position
    start_position = max(0, start_time - config.REWIND_TIME)
    audioPlayer.play(current_file, start_position)
    hardware.led_on()
    print(f"Playing current book: {current_file}")

def arrow_key_pushed(direction):
    """Handle button presses for settings and playback."""
    global settings_mode
    pause_audio()
    
    if settings_mode and direction != 0:
        # Adjust book or chapter based on switch status
        adjust_settings(direction)
    else:
        # Enter settings mode or toggle playback        
        settings_mode = True
        announce_settings_choice()

def adjust_settings(direction):
    """Adjust the book or chapter in settings mode."""
    if hardware.switch_status == 1:
        change_book(direction)
    else:
        change_chapter(direction)

def announce_settings_choice():
    """Announce whether the user is selecting a book or chapter."""
    print(f'Hardware switch is = {hardware.switch_status}')
    if hardware.switch_status == 1:
        speech.speak(config.PHRASES["choose_book"])
    else:
        speech.speak(config.PHRASES["choose_chapter"])

def change_chapter(direction):
    """Change the current chapter based on direction (-1 or 1)."""
    total_chapters = books.get_number_of_chapters(state.current_book)
    next_chapter = (state.get_chapter() + direction) % total_chapters  # Wrap around chapters

    state.set_chapter(next_chapter)
    state.set_position(0)  # Reset position for new chapter
    speech.speak(f"{config.PHRASES['chapter']} {next_chapter + 1}")
    state.save_state()

def change_book(direction):
    """Change the current book based on direction (-1 or 1)."""
    book_names = books.get_books()
    total_books = len(book_names)

    # Wrap around books using modular arithmetic
    current_index = book_names.index(state.current_book)
    next_index = (current_index + direction) % total_books

    state.current_book = book_names[next_index]
    author, title = books.get_author_and_title(state.current_book)
    speech.speak(f"{title} {config.PHRASES['by']} {author}")

def play_next():
    """Play the next file in the current book, or switch book """

    global start_time

    audioPlayer.stop()  # Stop audio player
    next_chapter = state.get_chapter()+1  # Add one to chapter index

    # If we've reached the end of the book, reset to the first file
    if next_chapter >= books.get_number_of_chapters(state.current_book):
        
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

        state.set_chapter(next_chapter) # Update our state
        state.set_position(0) # Reset position
        start_time = 0    # Reset position for the new file and play it
        
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

# Application

is_playing = False  # Flag for when audiobook is playing
is_generating = False # Flag for hwn TTS is being generated (playback disabled)
settings_mode = False # Flag for settings mode (choosing book / chapter)

start_time = 0  # Stores 

speech_sound = None  # Holds the pygame Sound object for TTS playback
speech_file = None  # Current temporary TTS file

print("Starting Easy Reader")

# Blink led to indicate startup
hardware.blink_led(3)

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