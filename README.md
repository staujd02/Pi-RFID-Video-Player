This software was developed by Joel Stauffer.
Developed: 08/25/2017
Engine Version: 1.1
Editor Version: 1.0
========================================================================
>>>>>>>><<<<<<<<
:: Change Log ::
>>>>>>>><<<<<<<<
Engine:
   1.1:
      - Kill Cards now kill all running oxmplayer processes
      - Card scan window was added to prevent rapid (millisecond) switches
========================================================================
---------------------
::REQUIRED HARDWARE::
---------------------
PN532 - RFID Reader (Configured for Mifare Format)
MPR121 - Capacitive Touch Sensor
========================================================================
---------------------
::REQUIRED SOFTWARE::
---------------------
Python library for Adafruit_PN532
Python library for Adafruit_MPR121
Omxplayer
IMPORTS: atexit, logging, subprocess, sys, os, shutil, binascii, time
pygame (for sound), Tkinter (GUIs), psutil, PIL.Image, PIL.ImageTk,
uinput, RPi.GPIO
========================================================================

There are two python scripts contained with the engine files.

 - editor.pyw
 - videoEngine.pyw

editor.pyw: This script launches a GUI used to edit the vids.csv and
UUID_Table.csv. It is also used to copy videos to the source usb.

videoEngine.pyw: This script launches the video player.
------------------------------------------------------------------------
There are three info files.

 - library.ini
 - vids.csv
 - UUID_Table.csv

library.ini: Contains cross program constants for videoEngine.pyw and
editior.pyw. The most important line is the usb={File Name}. This line
determines where the videos are imported to and stored. This information
can be set in the editior, and the options vary upon what devices are 
found in the /media/pi directory.

vids.csv: Contains a record for each video discovered by the last scan
executed by the editior. The format is: 
   [Primary Key],[Video Name],[Video Path]
line deliminated. The primary key is unique to the video entry and used
by the UUID_Table.csv information to link videos to RFID cards.

UUID_Table.csv: Contains a record for each RFID card scanned while 
running the editor. The format is:
   [RFID Card UUID],[Foreign Key]
also line deliminated. The foreign key corresponds to a video primary
key. If the foreign key is not set during the editing process, the
blank card error will occur if the card is scanned when the video 
engine is running.
========================================================================
Considerations for Modifications
========================================================================
To edit which files are discoverd/copied:

 - The easiest way to modifiy the files discovered and/or copied is by
    altering the scanner.sh bash file.
    > Adding a simple OR switch (i.g. -o '*.avi') after '*.mp4' would
       allow videos other than .mp4's to be scanned. Only .mp4 is 
       default, since omxplayer is touchy on codecs.
    > Altering the find path (/media/pi/) to a different directory would
       allow for the discovery of different files. /media/pi is default
       since usb directories appear as sub-directories in this location.

 - To modifiy the key assignements that control the video engine during
    runtime, edit the KEY_MAPPING array in videoEngine.pyw.
========================================================================
ERRORS ? ? ? ?
--------------
=> check the .log file for the python script you ran...
