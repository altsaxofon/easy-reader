# easy_reader
An audio book player for the visually impaired 

## Introduction

## Parts list

**Raspberry Pi Zero**<br/>
[Raspberry pi Zero](https://www.aliexpress.com/item/1005008224603338.html)<br/>
[micro SD to SD extension cable](https://www.amazon.se/dp/B0C4L7DDZF)<br/>
[Pi Zero kit with enclosure with accesories](https://www.amazon.se/dp/B0BJ1WFGMN) <br/>
Micro usb power adapter. (Part of Pi Zero kit) <br/>

**Audio playback**<br/>
[USB audio card](https://www.amazon.se/dp/B00IRVQ0F8)<br/>
USB-A to micro USB adapter. (Part of Pi Zero kit)  <br/>
[Small 5v amplifier](https://www.aliexpress.com/item/1005005852252380.html)<br/>
2x 3w 4ohm Speakers<br/>

**UI**<br/>
[2x Smaller momentary push buttons](https://www.electrokit.com/en/tryckknapp-15mm-1-pol-off-onvit)<br/>
[1x Big led-illuminated arcade style button](https://www.aliexpress.com/item/1005007297493475.html)<br/>
[Rocker switch On-on 2-position](https://www.electrokit.com/en/vagomkopplare-2-pol-on-on-1)<br/>



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
