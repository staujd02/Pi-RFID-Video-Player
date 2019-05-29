# SOFTWARE
import atexit
import logging
import subprocess
import sys
import binascii
import time
import pygame
import os.path
import psutil as util

import Tkinter
from PIL import Image
from PIL import ImageTk

# HARDWARE LIBRARIES
import Adafruit_PN532 as PN532

import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO
import uinput

# Configuration for a Raspberry Pi:
CS   = 18
MOSI = 23
MISO = 24
SCLK = 25

# Input pin connected to the capacitive touch sensor's IRQ output.
# For the capacitive touch HAT this should be pin 26!
IRQ_PIN = 26

# Define mapping of capacitive touch pin presses to keyboard button presses.
KEY_MAPPING = {
                0: uinput.KEY_Q,     # 
                1: uinput.KEY_LEFT,  # that maps the capacitive touch input number
                2: uinput.KEY_SPACE, # to an appropriate key press.
                3: uinput.KEY_DOT,   #
                4: uinput.KEY_RIGHT, # For reference the list of possible uinput.KEY_*
                5: uinput.KEY_UP,   # values you can specify is defined in linux/input.h:
                #6: uinput.KEY_Q,     # http://www.cs.fsu.edu/~baker/devices/lxr/http/source/linux/include/linux/input.h?v=2.6.11.8
                #7: uinput.KEY_SPACE, #
              }                      # Make sure a cap touch input is defined only
                                     # once or else the program will fail to run!

##
##0:              0: uinput.KEY_UP,     # 
##                1: uinput.KEY_DOWN,  # that maps the capacitive touch input number
##                2: uinput.KEY_LEFT,  # to an appropriate key press.
##                3: uinput.KEY_RIGHT, #
##                4: uinput.KEY_COMMA, # For reference the list of possible uinput.KEY_*
##                5: uinput.KEY_DOT,   # values you can specify is defined in linux/input.h:
##                6: uinput.KEY_Q,     # http://www.cs.fsu.edu/~baker/devices/lxr/http/source/linux/include/linux/input.h?v=2.6.11.8
##                7: uinput.KEY_SPACE, 

# Don't change the below values unless you know what you're doing.  These help
# adjust the load on the CPU vs. responsiveness of the key detection.
MAX_EVENT_WAIT_SECONDS = 0.25
EVENT_WAIT_SLEEP_SECONDS = 0.01
EQL_DELAY = .85
VIDEO_SCAN_RELIEF = 2

# Ini Info
INI_FILE = 'library.ini'
KILL_DEF='KillCommand'
VIDEO_DEF='VideoList'
UUID_DEF='UuidTable'

# Info Defaults
VIDEO_LIST='vids.csv'
UUID_MAP='UUID_Table.csv'
FK_KILL = -255

# Program Constants
LOG_FILE='engine.log'
IDLE = 'bg.jpg'
BROKE = 'broke.png'
BROKE_LINK = 'brokenLink.png'
TOUCH_SOUND = '/opt/sonic-pi/etc/samples/elec_plip.flac'
BROKE_SOUND = '/opt/sonic-pi/etc/samples/bass_dnb_f.flac'

# Begin setup Operations
try:
    logging.basicConfig(filename=LOG_FILE,level=logging.INFO)
    logging.info('Initializing Program...')
    
    # Load GUI screen
    logging.info('Creating GUI background...')
    root = Tkinter.Tk()
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),root.winfo_screenheight()))
    root.config(background = 'black')
    img = ImageTk.PhotoImage(Image.open(IDLE))
    imgBroke = ImageTk.PhotoImage(Image.open(BROKE))
    imgBrokeV = ImageTk.PhotoImage(Image.open(BROKE_LINK))
    panel = Tkinter.Label(root, image = img)
    panel.config(background = 'black')
    panel.pack(side = 'bottom', fill = 'both', expand = 'yes')
    root.update()
    
    # Load Sounds
    logging.info('Loading Sound Files...')
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()
    sound = pygame.mixer.Sound(TOUCH_SOUND)
    soundBroke = pygame.mixer.Sound(BROKE_SOUND)
    sound.set_volume(4)
    
    # Load Keyboard Interface
    logging.info('Loading uinput keyboard interface...')
    # Make sure uinput kernel module is loaded.
    subprocess.check_call(['modprobe', 'uinput'])
    # Configure virtual keyboard.
    device = uinput.Device(KEY_MAPPING.values())
    
    # Setup MPR121 Hardware
    logging.info('Mounting MPR121 device...')
    cap = MPR121.MPR121()
    if not cap.begin():
        raise Exception('Failed to initialize MPR121, check your wiring!')
    
    # Setup PN532 Hardware
    logging.info('Mounting PN532 device...')
    pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
    pn532.begin()
    # Configure PN532 to communicate with MiFare cards.
    pn532.SAM_configuration()
    
    # Configure GPIO pins
    logging.info('Configuring GPIO pins...')
    # Be sure to configure pin with a pull-up because it is open collector when not
    # enabled.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING)
    atexit.register(GPIO.cleanup)
    
    # Mark completion
    logging.info('Setup Complete')
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)


# Read ini file for file names
try:
    logging.info("Loading ini file...")
    f = open(INI_FILE,'r')
    lines = f.read().splitlines()
    f.close()
    for setting in lines:
        s = setting.split('=')
        if s[0] == KILL_DEF:
            FK_KILL = int(s[1])
        elif s[0] == VIDEO_DEF:
            VIDEO_LIST = s[1]
        elif s[0] == UUID_DEF:
            UUID_MAP = s[1]
except Exception as e:
    logging.error('Failed to read ini file, using defaults...')

try:
    # Load video CSV into active memory
    logging.info('Loading Video References...')
    f = open(VIDEO_LIST,'r')
    vids = f.read().splitlines()
    f.close()
    # Fracture array
    vidPK = []
    vidPATH = []
    vidNAME = []
    i=0
    while(i<len(vids)):
        split = vids[i].split(',')
        vidNAME.append(split[1])
        vidPATH.append(split[2])
        vidPK.append(int(split[0]))
        i=i+1
    
    # Load RFID cards' uuids into active memory
    logging.info('Loading RFID Card References...')
    f = open(UUID_MAP,'r')
    rfid = f.read().splitlines()
    f.close()
    # Fracture array
    uuid = []
    uuidFK = []
    i=0
    l = len(rfid)
    while (i < l):
        split = rfid[i].split(',')
        uuid.append(split[0])
        uuidFK.append(int(split[1]))
        i=i+1
    
    # Log completion
    logging.info('Files loaded')
except Exception as e:
    logging.critical('File Setup Failed: ' + str(e))
    sys.exit(1)


# Start Processing ------------------------------------

# Instance Trackers
lastplay=''
keys=True
changeV = False
sub = None
p = None
ff = False
scanFQ = 0

# Loop controller
run=0

try:
    # Clear any pending interrupts by reading touch state.
    cap.touched()
    
    # Endless Process Loop
    while (run==0):
        # Check if a card is available to read.
        uid = pn532.read_passive_target()
        if uid is None:
            # Card Not Found: Process keys
            keys=True
        else:
            # Card Found: Process Card
            uidt = binascii.hexlify(uid)
            # Check if card scan matches the last scan
            if uidt == lastplay:
                # Reset scan effect window
                scanFQ = time.time()
                # Check to see if the video has ended...
                running = False
                # See if a process object is already set
                if p is not None:
                    # process is set, try querying status
                    try:
                        p.status()
                    except util.NoSuchProcess:
                        # Process is dead, check if another one is active
                        p = None
                        running = False
                        for proc in util.process_iter():
                            try:
                                pinfo = proc.as_dict(attrs=['name'])
                            except util.NoSuchProcess:
                                pass
                            else:
                                if 'omxplayer' == pinfo['name']:
                                    running = True
                                    p = proc
                                    break
                        if p is not None:
                            logging.info('Video Ended')
                    else:
                        running = True
                        # Slight delay to match rfid timeout scenerio
                        time.sleep(EQL_DELAY)
                else:
                    # process is not set, try to find it
                    for proc in util.process_iter():
                        try:
                            pinfo = proc.as_dict(attrs=['name'])
                        except util.NoSuchProcess:
                            pass
                        else:
                            if 'omxplayer' == pinfo['name']:
                                running = True
                                p = proc
                                break
                changeV = not running
                keys=True
            else:    
                # Video is not playing or user has requested
                # a different Video
                if (time.time() - scanFQ) < VIDEO_SCAN_RELIEF:
                    # Scan window has not expired... 
                    changeV = False
                    keys = True
                else:
                    changeV = True
            
            # Change the video
            if changeV:
                scanFQ = time.time()
                keys=False
                sound.play()
                lastplay = uidt
                # Tell omxplayer to quit
                device.emit_click(uinput.KEY_Q)
                try:
                    i=uuid.index('0x' + uidt)
                    if uuidFK[i] == FK_KILL:
                        # Kill card was scanned, cleanup and exit
                        logging.info('Quit Command Recieved!')
                        for proc in util.process_iter():                            
                            try:                            
                                pinfo = proc.as_dict(attrs=['name'])
                            except util.NoSuchProcess:
                                pass
                            else:
                                if 'omxplayer' == pinfo['name']:
                                    proc.kill()
                        sys.exit(0)
                    i=vidPK.index(uuidFK[i])
                    logging.info('Playing Video: ' + vidNAME[i])
                    if not os.path.isfile(vidPATH[i]):
                        raise IOError('Video link did not resolve.')
                    subprocess.call('gnome-terminal -x omxplayer -b -o hdmi ' + vidPATH[i],shell=True)
                except IOError as o:
                    # Video File is broken...
                    panel.config(image = imgBrokeV)
                    root.update()
                    soundBroke.play()
                    time.sleep(3)
                    panel.config(image = img)
                    root.update()
                    lastplay = ''
                    p = None
                    logging.error(o)
                except Exception as e:
                    # RFID card is not properly linked...
                    panel.config(image = imgBroke)
                    root.update()
                    soundBroke.play()
                    time.sleep(3)
                    panel.config(image = img)
                    root.update()
                    lastplay = ''
                    p = None
                    logging.error(str(e))
        if keys:
            # Wait for the IRQ pin to drop or too much time ellapses (to help prevent
            # missing an IRQ event and waiting forever).
            start = time.time()
            while (time.time() - start) < MAX_EVENT_WAIT_SECONDS and not GPIO.event_detected(IRQ_PIN):
                time.sleep(EVENT_WAIT_SLEEP_SECONDS)
            # Read touch state.
            touched = cap.touched()
            # Emit key presses for any touched keys.
            for pin, key in KEY_MAPPING.iteritems():
                # Check if pin is touched.
                pin_bit = 1 << pin
                if touched & pin_bit:
                    # Emit sound
                    sound.play()
                    # Emit key event when touched.
                    if key == uinput.KEY_DOT:
                        if ff:
                            ff = False
                            device.emit_click(uinput.KEY_SPACE)
                            time.sleep(.15)
                            device.emit_click(uinput.KEY_SPACE)
                        else:
                            ff = True
                            device.emit_click(key)
                            time.sleep(.15)
                            device.emit_click(key)
                    elif key == uinput.KEY_SPACE:
                        ff = False
                        device.emit_click(key)
                    else:
                        device.emit_click(key)
                    if key == uinput.KEY_Q:
                        lastplay=''
                        p = None
                        logging.info('Video Ended by user.')                            
except Exception as e:
    logging.critical('Unexpected Error: ' + str(e))
    sys.exit(1)
