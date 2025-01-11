# Easy reader
An easy to use audio book player for the elderly, made in python to run on a Raspberry Pi.

The goal of this project is to create a simple audiobook reader for users with impared vision, low mobility or that in any other way have a hard time interacting with touch screens. In this case, my grandmother in-law. 

The Easy Reader plays audiobooks in mp3 format from an SD card and is operated with one big illuminated button. When the button is pressed the audiobook starts playing from where you left off, with the option to skip back a selected number of seconds to recap. 

The reader can handle any number of books and will read them one after the other, pausing in between.

On the side of the reader there is an interface made of a switch and two directional buttons. This is interface is not needed to operate the player, but make it possible to select between books and chapters. The swich is used to choose between book and chapter, and the directional buttons are used to navigate.

The reader uses a simple text to speech engine to helop the user navigate between books and chapters.


## Hardware

### Parts list

**Raspberry Pi Zero**<br/>
[Raspberry pi Zero](https://www.aliexpress.com/item/1005008224603338.html)<br/>
[micro SD to SD extension cable](https://www.amazon.se/dp/B0C4L7DDZF)<br/>
[Pi Zero kit with enclosure with accesories](https://www.amazon.se/dp/B0BJ1WFGMN) <br/>
Micro usb power adapter. (Part of Pi Zero kit) <br/>
Micro SD 1tb
Micro SD to SD adapter

**Audio playback**<br/>
[USB audio card](https://www.amazon.se/dp/B00IRVQ0F8)<br/>
USB-A to micro USB adapter. (Part of Pi Zero kit)  <br/>
[Small 5v amplifier](https://www.aliexpress.com/item/1005005852252380.html)<br/>
2x 3w 4ohm Speakers<br/>

**UI**<br/>
[2x Smaller momentary push buttons](https://www.electrokit.com/en/tryckknapp-15mm-1-pol-off-onvit)<br/>
[1x Big led-illuminated arcade style button](https://www.aliexpress.com/item/1005007297493475.html)<br/>
[Rocker switch On-on 2-position](https://www.electrokit.com/en/vagomkopplare-2-pol-on-on-1)<br/>




## Software

### Folder structure
All audiobooks are stored in the directory /audiobooks/ as folders of MP3-files, prefereably one mp3 file per chapter of the book.
The player will use the folder names to identify the books using the format *Author - Book Title*

### Managing books
The player stores a list of books and listening progress in a json encoded txt file on the SD card. The player will scan the /audiobooks/ directory and add or remove books from the registry to reflect any changes in the folder. To add or remove a book, just add or remove a folder in the SD-card. 

## Logic

### Listening
Pushing the play / pause button will play or pause the playback of the audiobook.
During playback the progress will be coninuasly saved to a text file on the SD card of the player.

When an audiobook is finished the progress of the book will be reset and the playback will stop. The title of next audiobook on the SD-card will be read out loud by the speech synthesis, informing the user to push the play button to begin to listen to it.  

### Settings mode
Using the book/chapter switch or a directional button will pause the music and set the player in "settings mode".
Depending on the state of the book/chapter switch the current book title or chapter will be read out loud by the speech synthesis. 

While in settings mode, using the arrow buttons will change book title or chapter. This change will immedatly be stored to the memory and the selection will be read out load by the speech synthesis.

Settings mode is exited by pushing the play button, wich resumes playback from the newly selected book or chapter. 

Changing books will not reset book progress. The progress  will be reset when a book finnishes, or can be done manually by using the directional buttons.


### Create SD Card




## Setting up pi


Install RaspberryPi OS to an SD-card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
https://forums.raspberrypi.com/viewtopic.php?t=26826 - enable file sharing
- set up SSH
- 

### Repartition
I want to be able to manage the audiobooks on a mac or PC. For this I need a fat32 partition on the SD card. This was harder than I thought.

On my Macbook Air m2 I used [UTM](https://mac.getutm.app/) to create a virtual linux machine (using the Emulate setting) and adding the [GParted Live bootable ISO](https://gparted.org/liveusb.php).

In the virtual machine I added  I had a hard time geting it to work, the problem seemed to have something to do with the display drivers. In the end I got it to work using the 'virtio-vga-gl (GPU Supported)' driver under the virtual machines display settings and the 'Other modes of Gparted  Live > Gparted (KMS)' version of Gparted.<br /><br />

In Gparted i resized the linux pi partition and created a Fat32 partition, accesible to a mac, to store the audiofiles.

### Todo
**PI**
- create and partition SD card
- set up SSH
- set up filesharing
- test software
- setup autostart

**Software**
- clean code
- - remove 'duration' from JSON?
- create a list of requirements.txt
- create install?
  
** Hardware **
- set up audio
- cardboard prototype
- 


