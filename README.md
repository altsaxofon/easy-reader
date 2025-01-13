# Easy reader

An easy to use audio book player for the elderly, made in python to run on a Raspberry Pi.

The goal of this project is to create a simple audiobook reader for users with impared vision, low mobility or that in any other way have a hard time interacting with touch screens. In this case, my grandmother in-law. 

The Easy Reader plays audiobooks in mp3 format from an SD card and is operated with one big illuminated button. When the button is pressed the audiobook starts playing from where you left off, with the option to skip back a selected number of seconds to recap. 

The reader can handle any number of books and will read them one after the other, pausing in between.

On the side of the reader there is an interface made of a switch and two directional buttons. This is interface is not needed to operate the player, but make it possible to select between books and chapters. The swich is used to choose between book and chapter, and the directional buttons are used to navigate.

The reader uses a simple text to speech engine to helop the user navigate between books and chapters.

> [!IMPORTANT]
> I am no electronics expert, and many parts of the code was made with the help of Chat GPT <br />
> Use common sense and follow at your own risk. Happy building!


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
> Note that the led is connected via a 330Ω resistor.

This is how i connected my components to the Raspberry Pi Zero.
| Component | Pin | 
| :---   |    ---: |
| Play button|  GPIO**17**  |
| Play button led|  GPIO**18**    |
| Next button     | GPIO**27**      |
| Previous button     | GPIO**22**      |
| Rocker switch     | GPIO**23**      |

The pin numbers are defined in `main.py`, change them if you want to use other pins.

## Software
### How to use
#### Managing books
All audiobooks are stored in the directory /audiobooks/ on the Fat32 partition of the SD card that is accesible form mac / windows. Each book is a folder of MP3-files (prefereably one mp3 file per chapter of the book). The player uses the folder names to identify the books using the format `Author - Book Title`

The player stores a list of books and listening progress in a json encoded txt file on the SD card. The player will scan the /audiobooks/ directory and add or remove books from the registry to reflect any changes in the folder. To add or remove a book, just add or remove a folder in the SD-card. 

#### Listening
Pushing the play / pause button will play or pause the playback of the audiobook. When playback resumes the player rewinds 15 seconds for a small recap. The number of esonds can be changed in `main.py`
During playback the progress will be coninuasly saved to a text file on the SD card of the player.

When an audiobook is finished the progress of the book will be reset and the playback will stop. The title of next audiobook on the SD-card will be read out loud by the speech synthesis, informing the user to push the play button to begin to listen to it.  

#### Changing book or chapter
Using the book/chapter switch or a directional button will pause the music and set the player in "settings mode".
Depending on the state of the book/chapter switch the current book title or chapter will be read out loud by the speech synthesis. 

While in settings mode, using the arrow buttons will change book title or chapter. This change will immedatly be stored to the memory and the selection will be read out load by the speech synthesis.

Settings mode is exited by pushing the play button, wich resumes playback from the newly selected book or chapter. 

Changing books will not reset book progress. The progress  will be reset when a book finnishes, or can be done manually by using the directional buttons.

#### Speech synthesis
The easy reader gives spoken feedback text to speech engine when the interface is used. The speech is pre generated and is stored on the PI partition as wav files. The first time the player is turned on it will generate the neccecary files, and this might take some time (10+ minutes). When a new book is added to the `audiobooks` folder a wav file for the book title will be generated, wich also will take a little time. Playback is disabled during the speech generation and the big button will light up as an indication. 


## How to setup
### 1. Create the SD Card

#### 1.1 Insatll Pi OS

Create a  RaspberryPi OS SD-card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
I chose to install the lite version of the Pi OS, since our reader does not have a creen we do not need the desktop environment.

*(I did, however, use a full installation of Pi OS with GUI to develop and prototype. If you, like me, are new to Pi and python this makes the process way easier)*

Add your Wifi and enable SSH in the `apply OS customization settings` dialog .

#### 1.2 Repartition
The SD partition holsing the Pi OS uses a Linux filesystem `ext4` that cannot be read on mac or windows. Since I want to be able to manage the audiobooks from my mac we need to add a second, `Fat 32` partition. Since this (as far as I know) is not doable in macOS we need to jump thru some hoops to achieve it. 

On my Macbook Air M2 running Sequoia I used the virtual machine utility [UTM](https://mac.getutm.app/) to create a virtual linux machine (using the Emulate setting) and adding the [GParted Live bootable ISO](https://gparted.org/liveusb.php).

I had a hard time geting Gparted to work with UTM - the problem seemed to have something to do with the display drivers. After some trial and error I got it to work using the `virtio-vga` driver under the VMs display settings together with the `Other modes of Gparted Live > Gparted (KMS)` version of Gparted Live. 

In Gparted i resized the linux pi partition and created a Fat32 partition, accesible to a mac, to store the audiobooks. 
On my 32GB SD card I left ~6gb for the Pi Os and made a ~23gb large partition for the audiobooks.  

<img width="700" alt="Layer 1" src="https://github.com/user-attachments/assets/afebfa0e-f34e-4e67-ae76-3092e302d381" /><br />
SD card before partitioning

<img width="700" alt="Layer 2" src="https://github.com/user-attachments/assets/669ccbd6-89a6-48bb-8cac-6f7838c473b6" /><br />
SD card after partitioning

### 2.  Install Easyreader
Log in to pi with SSH `ssh pi@raspberrypi.local`

#### Prepare the Pi
I set up file sharing with samba using the description [here](https://subscription.packtpub.com/book/iot-and-hardware/9781849696623/1/ch01lvl1sec19/sharing-the-home-folder-of-the-raspberry-pi-with-smb
)

#### Download and setup
Install git and download Easyreader (or copy it over to the PI some other way)
`sudo apt install git`
`git clone https://github.com/altsaxofon/easy_reader.git`

Navigate to the easy reader directory
`cd easy_reader/`

Make the setup script executable and run it
`chmod +x setup.sh`
`./setup.sh`

The setup script creates a service that mounts the fat32 partition and loads the easy_reader python script. It will auto run when the pi is booted. 

> [!NOTE]
>The first time the easyreader boots it will generate wav files for the speech wynthesis, and this might take som time 

### 3. Configure Easyreader



### Not working?
If the software is not working it can be a good idea to activate the virtual environment and run the `main.py` from the terminal to see any error messages.
```
/home/pi/easy_reader/easyreader_ve/bin/python /home/pi/easy_reader/main.py
```
*assuming `pi`is the username*

It might be neccecary to stop the service first using the command


```
sudo systemctl stop easy_reader.service
```

If the script is working from the terminal but not on boot it can be helpful to look at the log for the easy_reader.service with the command.

```
journalctl -u easy_reader.service -b
```

For example, the service could be trying to mount the wrong `Fat32`partition.
You can open and edit the service with the command

```
sudo nano /etc/systemd/system/easy_reader.service
```


## Software



Then open the easy_reader.service:
"""
sudo nano /etc/systemd/system/easy_reader.service
"""

and edit the line where the audio device is specified
`Environment="AUDIODEV=hw:2,0" `
replace the 2,0 with the adress of your device (cardnumber, device number)

sudo systemctl start easy_reader.service
sudo systemctl status easy_reader.service

/home/pi/easy_reader/easyreader_ve/bin/python /home/pi/easy_reader/main.py

logs:
journalctl -u easy_reader.service -b


#### Change settings

#### Add books





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


