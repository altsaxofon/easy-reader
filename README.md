# Easy reader

![20250302_102227](https://github.com/user-attachments/assets/15893e17-84b6-4ef4-9b7f-e4d2df7436cc)




An easy to use audio book player for the elderly, runnin in python on Raspberry Pi Zero 2W.

The goal of this project is to create a simple audiobook reader for users with impared vision, low mobility or that in any other way have a hard time interacting with touch screens. In this case, my grandmother in-law. 

The Easy Reader plays audiobooks in mp3 format from an SD card and is operated with one big illuminated button. When the button is pressed the audiobook starts playing from where you left off, with the option to skip back a selected number of seconds to recap. 

The reader can handle any number of books and will read them one after the other, pausing in between.

On the right side of the reader there is an interface made of a switch and two directional buttons. This is interface is not needed to operate the player, but make it possible to select between books and chapters. The swich is used to choose between book and chapter, and the directional buttons are used to navigate.

The reader uses a simple text to speech engine to helop the user navigate between books and chapters.

> [!IMPORTANT]
> I am no electronics expert, and many parts of the code was made with the help of Chat GPT <br />
> Use common sense and follow at your own risk. Happy building!

## Table of Contents  

1. [Introduction](#easy-reader)  
2. [Hardware](#hardware)  
3. [Software](#software)  
4. [How to Set Up](#how-to-setup)  
5. [Troubleshooting](#not-working)  

## Circuit

<img width="1052" alt="Skärmavbild 2025-02-26 kl  14 57 40" src="https://github.com/user-attachments/assets/d924b353-8c2b-49ee-afe0-1c46608ea232" />


### Parts list

| **Category**      | **Item**                | **Source**                      | 
|--------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| **Raspberry Pi Zero** | Raspberry Pi Zero   | [Electrokit](https://www.electrokit.com/raspberry-pi-zero-2-wh-med-header)         | 
|                    | Pi Zero kit with enclosure and accessories     | [Amazon](https://www.amazon.se/dp/B0BJ1WFGMN)    | 
|                    | 32Gb Micro SD with SD adapter   | Local store |                
|                    | micro SD to SD extension cable   | [Amazon](https://www.amazon.se/dp/B0C4L7DDZF)  | 
| **Audio Playback** | USB audio card            | [Amazon](https://www.amazon.se/dp/B00IRVQ0F8)         |
|                    | USB-A to Micro USB adapter (Part of Pi Zero kit)             | [Amazon](https://www.amazon.se/dp/B0BJ1WFGMN)         | 
|                    | Amplifier board       | Computer speakers from goodwill                                            | 
|                    | 3,5mm cable / plug                 | Goodwill                   |
|                    | 2x  speakers  |   Computer speakers from goodwill     | 
|                    | Ground loop isolator  |   [Amazon](https://www.amazon.se/dp/B0CSDKGQQP)     |
| **UI**             | 2x Smaller momentary push buttons          | [Electrokit](https://www.electrokit.com/en/tryckknapp-15mm-1-pol-off-onvit)                                    | 
|                    | 1x Big LED-illuminated arcade-style button                | [Aliexpress](https://www.aliexpress.com/item/1005007297493475.html)                                            |
|                    | Rocker switch On-On 2-position              | [Electrokit](https://www.electrokit.com/en/vagomkopplare-2-pol-on-on-1)                                        | 
| **Power supply**   | USB-PD Power supply board 5-20V              | [Electrokit](https://www.electrokit.com/en/usb-pd-stromforsorjningskort-5-20v)                                    | 


<br /><br />


### Wiring diagram

![Artboard 1@4x](https://github.com/user-attachments/assets/e9e4d85e-1d8d-4b62-9bac-3ec25f64fa88)

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


Connecting both the PI and the amplifier to the USB-C power board caused a really bad noise. Altough the cuase is probably some bad connection / soldering from my end, the ground loop isolator solved the issue.
<br /><br />
The pin numbers are defined in `config.py`, change them if you want to use other pins.
<br /><br />

## The build

![the build](https://github.com/user-attachments/assets/7cf9db79-9f3b-404c-945b-a5ab0253881d)


## Software
<img width="1416" alt="Skärmavbild 2025-02-27 kl  17 22 11" src="https://github.com/user-attachments/assets/45e909e5-fb26-4792-bc41-c573092b3cff" />

### How to use

#### Listening
The reader is powered on by connecting a usb-c cable to the outlet in the back (6). takes about 30 seconds to to power on. The button will blink three times to indicate that the player is ready for playback. 

Pushing the play / pause button (1) will play or pause the playback of the audiobook. When playback resumes the player rewinds a couple of seconds for a small recap. The volume is adjusted with the volume knob (2).

The progress is coninously saved to a text file on the SD card of the player. When an audiobook is finished the progress of the book will be reset and the playback will stop. The player will tell the user to push the play button to start to listen to the next book.  

#### Changing book or chapter
Using the book/chapter switch or a directional button will pause the music and set the player in "settings mode".

Depending on the state of the book/chapter switch the current book title or chapter will be read out loud by the speech synthesis. 

While in settings mode, using the arrow buttons will change book title or chapter. This change will immedatly be stored to the memory and the selection will be read out load by the speech synthesis.

Settings mode is exited by pushing the play button, wich resumes playback from the newly selected book or chapter. 

Changing books will not reset book progress. The progress  will be reset when a book finnishes, or can be done manually by using the directional buttons.

#### Managing books
All audiobooks are stored in the directory /audiobooks/ on the Fat32 partition of the SD card that is accesible form mac / windows. Each book is a folder of MP3-files (prefereably one mp3 file per chapter of the book). The player uses the folder names to identify the books using the format `Author - Book Title`

The player stores a list of books and listening progress in a json encoded txt file on the SD card. The player will scan the /audiobooks/ directory and add or remove books from the registry to reflect any changes in the folder. To add or remove a book, just add or remove a folder in the SD-card. 

#### Speech synthesis
The easy reader gives spoken feedback text to speech engine when the interface is used. The speech is pre generated and is stored on the PI partition as wav files. The first time the player is turned on it will generate the neccecary files, and this might take some time (10+ minutes). When a new book is added to the `audiobooks` folder a wav file for the book title will be generated, wich also will take a little time. Playback is disabled during the speech generation and the big button will light up as an indication. 

### Changing settings
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
```
sudo apt install git
git clone https://github.com/altsaxofon/easy_reader.git
```

Navigate to the easy reader directory
```
cd easy_reader/
```

Make the setup script executable and run it
```
chmod +x setup.sh
./setup.sh
```

The setup script creates a service that mounts the fat32 partition and loads the easy_reader python script in it's virtual environment. 
It will auto run when the pi is booted. 

#### Translate

The easy reader is configured to speak swedish. You can change language by changing the settings in the `config.py`file.
Change model, Translate phrases. 

> [!NOTE]
>The first time the easyreader boots it will generate wav files for the speech synthesis, and this might take som time (10+ minutes)
> [!NOTE]
> The easyreader must be connected to WiFi to download the TTS model. After this, the reader can generate speech (e.g. when adding a new book) without connection to the internet. 



### Not working?

#### Look at the logs from easy_reader.service
It can be helpful to look at the log for the easy_reader.service with the command.

```
journalctl -u easy_reader.service -b
```

For example, the service could be trying to mount the wrong `Fat32`partition.
You can open and edit the service with the command

```
sudo nano /etc/systemd/system/easy_reader.service
```

#### Run Easyreader from terminal
Another debuging strategy is to run `main.py` from the terminal to see any error messages.

First stop the service and reload
```
sudo systemctl stop easy_reader.service
sudo systemctl daemon-reload
```

Next mount the Fat32 partition as `sdcard` 
```
sudo  /bin/mount -o uid=1000,gid=1000,umask=0022 /dev/mmcblk0p3 /mnt/sdcard
```

Run Easy reader (`main.py`)
```
/home/pi/easy_reader/easyreader_ve/bin/python /home/pi/easy_reader/main.py
```
*assuming `pi`is the username*


### 3. Configure Easyreader


### Architecture

The software is made up of a main script `main.py` and 6 modules with different responsibilites

**config.py** for loading and managing settings
**books.py** for managing the book library
**hardware.py** for communicating with buttons, switches and leds
**player.py** for controlling audio playback
**speech.py** for managing speech synthesis
**state.py** for loading and saving listening progress

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




