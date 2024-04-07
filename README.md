
## REQUIRED HARDWARE

- PN532 - RFID Reader (Configured for Mifare Format)

## OPTIONAL HARDWARE

- MPR121 - Capacitive Touch Sensor(Otherwise use GPIO Player)
   - Note: If you don't have the MPR121, you will need to use the `videoEngineGPIO.pyw` to start the video player

## REQUIRED SOFTWARE
- Python library for Adafruit_PN532
- Python library for Adafruit_MPR121 (If you're using the MPR121 board)
- Python library psutil, python-uinput
- Linux Distros: Omxplayer, gnome-terminal, python-imaging, and python-imaging-tk
- IMPORTS: atexit, logging, subprocess, sys, os, shutil, binascii, time
 pygame (for sound), Tkinter (GUIs), psutil, PIL.Image, PIL.ImageTk,
 uinput, RPi.GPIO
 
### Setup Instructions
 - Install the required python PN_532 library
     - Download forked PN_532 library
     - Run `pip install .`
 - Install the required MPR_121 library
     - Download forked MPR_121 library
     - Run `pip install .`
     - Enable ic2
     	- Open `/boot/config.txt`
	- Uncomment `ic2_dev, i2s`
 - Setup up video repository scanner
     - Ensure usb name has no spaces in it
     - Ensure scanner.sh is saved with UNIX file endings
     - Enable execute permissions for scanner.sh 
 - Install required system libraries
     - `sudo apt-get install libudev-dev`
     - `sudo apt-get install python3-pil.imagetk`
     - `sudo apt-get install gnome-terminal`
 - Install required python libraries
     - `sudo pip3 install python-uinput`

### Setting up auto-start service on boot

 - Copy the appropriate service file into `/etc/systemd/system`

### There are three executable python programs

 - editor.pyw
    - *This script launches a GUI used to edit the vids.csv and UUID_Table.csv, set the source USB, and copy videos from other USB's to the source USB.*
 - videoEngine.pyw
    - *This script launches the video player using the MPR121 for interactive video control.*
 - videoEngineGPIO.pyw
    - *This script launches the video player using GPIO pins as substitutes for the MPR121 capacitive touch sensors.*

### There are three info files.

 - library.ini
 - vids.csv
 - UUID_Table.csv

*library.ini*: Contains cross program constants for videoEngine.pyw and
editior.pyw. The most important line is the usb={File Name}. This line
determines where the videos are imported to and stored. This information
can be set in the editior, and the options vary upon what devices are 
found in the /media/pi directory.

*vids.csv*: Contains a record for each video discovered by the last scan
executed by the editior. The format is: 
   `[Primary Key],[Video Name],[Video Path]`
line deliminated. The primary key is unique to the video entry and used
by the UUID_Table.csv information to link videos to RFID cards.

*UUID_Table.csv*: Contains a record for each RFID card scanned while 
running the editor. The format is:
   [RFID Card UUID],[Foreign Key]
also line deliminated. The foreign key corresponds to a video primary
key. If the foreign key is not set during the editing process, the
blank card error will occur if the card is scanned when the video 
engine is running.

### Considerations for Configuration
To edit which files are discoverd/copied:

 - The easiest way to modifiy the files discovered and/or copied is by
    altering the scanner.sh bash file.
    - Adding a simple OR switch (i.g. -o '*.avi') after '*.mp4' would
       allow videos other than .mp4's to be scanned. Only .mp4 is 
       default, since omxplayer is touchy on codecs.
    - Altering the find path (/media/pi/) to a different directory would
       allow for the discovery of files in another location. /media/pi is default
       since usb directories appear as sub-directories in this location.

 - To modifiy the key assignements that control the video engine during
    runtime, edit the KEY_MAPPING array in videoEngine.pyw (or videoEngineGPIO.pyw).

 - Adding the a startup script  to /etc/profile.d is a way
	auto start the video player on user login

#### Problems?
- Check the .log files for errors and/or warnings...

#### This software was developed by Joel Stauffer.
- Developed: 08/25/2017
- Engine Version: 2.1
- Editor Version: 1.0
