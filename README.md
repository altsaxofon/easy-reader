> [!IMPORTANT]
> I am no electronics expert, and many parts of the code was made with the help of Chat GPT <br />
> Use common sense and follow at your own risk.


# Easy reader

An easy to use audio book player for the elderly, made in python to run on a Raspberry Pi.

The goal of this project is to create a simple audiobook reader for users with impared vision, low mobility or that in any other way have a hard time interacting with touch screens. In this case, my grandmother in-law. 

The Easy Reader plays audiobooks in mp3 format from an SD card and is operated with one big illuminated button. When the button is pressed the audiobook starts playing from where you left off, with the option to skip back a selected number of seconds to recap. 

The reader can handle any number of books and will read them one after the other, pausing in between.

On the side of the reader there is an interface made of a switch and two directional buttons. This is interface is not needed to operate the player, but make it possible to select between books and chapters. The swich is used to choose between book and chapter, and the directional buttons are used to navigate.

The reader uses a simple text to speech engine to helop the user navigate between books and chapters.



## Hardware

### Parts list

| **Category**      | **Item**                                                                                                      | **Link**                                                                                                  | **Price** |
|--------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|-----------|
| **Raspberry Pi Zero** | Raspberry Pi Zero   | [Electrokit](https://www.electrokit.com/raspberry-pi-zero-2-wh-med-header)         | TBD       |
|                    | Pi Zero kit with enclosure and accessories     | [Amazon](https://www.amazon.se/dp/B0BJ1WFGMN)    | TBD       |
|                    | Micro SD with SD adapter   | [Aliexpress](https://www.aliexpress.com/item/1005007182352564.html) |    TBD       |                 
|                    | micro SD to SD extension cable   | [Amazon](https://www.amazon.se/dp/B0C4L7DDZF)  | TBD       |
| **Audio Playback** | USB audio card                                                                                              | [Amazon](https://www.amazon.se/dp/B00IRVQ0F8)                                                              | TBD       |
|                    | USB-A to Micro USB adapter (Part of Pi Zero kit)                                                             | [Amazon](https://www.amazon.se/dp/B0BJ1WFGMN)                                                                                                       | TBD       |
|                    | Small 5V amplifier                                                                                          | [Ali express](https://www.aliexpress.com/item/1005005852252380.html)                                            | TBD       |
|                    | 3,5mm cable / plug                 | [A-Z parts]                      | TBD       |
|                    | 2x 3W 4ohm speakers  | [A-Z parts](https://www.az-delivery.de/en/products/2-stuck-dfplayer-mini-3-watt-8-ohm-mini-lautsprecher-mit-jst-ph2-0-mm-pin-schnittstelle-fur-arduino-raspberry-pi-und-elektronische-diy-projekte-inklusive-e-book)        | TBD       |
| **UI**            | 2x Smaller momentary push buttons                                                                            | [Electrokit](https://www.electrokit.com/en/tryckknapp-15mm-1-pol-off-onvit)                                    | TBD       |
|                    | 1x Big LED-illuminated arcade-style button                                                                   | [Aliexpress](https://www.aliexpress.com/item/1005007297493475.html)                                            | TBD       |
|                    | Rocker switch On-On 2-position                                                                              | [Electrokit](https://www.electrokit.com/en/vagomkopplare-2-pol-on-on-1)                                        | TBD       |


### Wiring diagram

![wiring](https://github.com/user-attachments/assets/e9837eb8-c2be-41e9-ae5c-0bdf428fd56c)
> [!NOTE]
> Note that the led is connected via a 330Ω resistor

This is how i connected my components to the Raspberry Pi Zero.
| Component | Pin | 
| :---   |    ---: |
| Play button|  GPIO**17**  |
| Play button led|  GPIO**18**    |
| Next button     | GPIO**27**      |
| Previous button     | GPIO**22**      |
| Rocker switch     | GPIO**23**      |

Note that only one of the poles of the rocker switch is needed for the player to work, and that the button LED is connected via a 330Ω resisitor



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


## Create SD Card




### Installing Pi OS


Install RaspberryPi OS to an SD-card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Add your Wifi and enable SSH in the `apply OS customization settings` options. .


### Repartition
The pi SD partition holsing the OS uses a Linux filesystem that is not easyli readable on mac or windows. Since I want to be able to manage the audiobooks from my mac i need to add a second, Fat 32 partition. To do this we need to use a disk utility running on a Linux system, I used [Gparted](https://gparted.org/).

On my Macbook Air m2 I used the virtual machine utility [UTM](https://mac.getutm.app/) to create a virtual linux machine (using the Emulate setting) and adding the [GParted Live bootable ISO](https://gparted.org/liveusb.php).

 I had a hard time geting Gparted to work - the problem seemed to have something to do with the display drivers. In the end I got it to work using the `virtio-vga` driver under the virtual linux machines display settings and the `Other modes of Gparted Live > Gparted (KMS)` version of Gparted Live.<br /><br />

In Gparted i resized the linux pi partition and created a Fat32 partition, accesible to a mac, to store the audiofiles.


### install 
`git clone https://github.com/altsaxofon/easy_reader.git``
`cd easy_reader/``
`chmod +x setup.sh`
`./setup.sh`
after the setup is run, you might have to change the adress of your USB audio card.
lookup the id of your USB audio device using `aplay -l``
open the easy_reader.service:
`sudo nano /etc/systemd/system/easyreader.service``
and edit the line where the audio device is specified
`Environment="AUDIODEV=hw:2,0" `
replace the 2,0 with the adress of your device (cardnumber, device number)


### Todo
**PI**
- [ ] create and partition SD card
- [ ] set up SSH
- [ ] set up filesharing
- [ ] test software
- [ ] setup autostart

**Software**
- [ ] clean code
- [x] remove 'duration' from JSON?
- [x] create a list of requirements.txt
- [x] create install?
  
**Hardware**
- [ ] set up audio
- [ ] cardboard prototype

**Documentation**
- [ ] fritizing


