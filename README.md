# easy_reader
An audio book player for the visually impaired 

## Introduction

## Parts list

**Raspberry Pi Zero**<br/>
Raspberry pi Zero<br/>
micro SD to SD extension cable<br/>
micro usb power adapter<br/>

**Audio playback**<br/>
USB audio card<br/>
USB-A to micro USB adapter<br/>
Small 5v amplifier<br/>
2x 3w 4ohm Speakers<br/>

**UI**<br/>
2x Smaller momentary push buttons (direction buttons)<br/>
1x Big led-illuminated arcade style button<br/>
Rocker switch On-on 2-position<br/>



## Setup

### Folder structure
All audiobooks are stored in the directory /audiobooks/ as folders of MP3-files, prefereably one mp3 file per chapter of the book.
The player will use the folder names to identify the books using the format *Author - Book Title*

## Logic

### Listening
Pushing the play / pause button will play or pause the playback of the audiobook.
During playback the progress will be coninuasly saved to a text file on the SD card of the player.

When an audiobook is finished the playback the progress of that book will be reset to 0 and the playback will stop. The title of next audiobook on the SD-card will be read out loud by the speech synthesis, informing the user to push the play button to begin to listen to it.  

### Settings mode
Using the book/chapter switch or an or button will pause the music and set the player in "settings mode".
Depending on the state of the book/chapter switch the current book title or chapter will be read out loud by the speech synthesis. 

While in settings mode, using the arrow buttons will change book title or chapter. This change will immedatly be stored to the memory. 

Settings mode is exited by pushing the play button, wich resumes playback from the newly selected book or chapter. 

Changing books will not reset book progress. 
