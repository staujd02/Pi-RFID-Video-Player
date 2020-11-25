# Python Packages
import atexit
import logging
import subprocess
import sys
import binascii
import time
import pygame
import os.path
import uinput
import psutil as util

# GUI Packages
from tkinter import *
from PIL import Image
from PIL import ImageTk

# 3rd Party Hardware Libraries
import Adafruit_PN532 as PN532
import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO

# Internal Libraries
from source.wrapper.cardScanWrapper import CardScanWrapper
from source.providers.rfidScannerProvider import RFIDScannerProvider
from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.cardToVideoLinker import CardToVideoLinker
from source.environment.environment import Environment
from source.dataStructures import Video

CS   = 18
MOSI = 23
MISO = 24
SCLK = 25
IRQ_PIN = 26

KEY_MAPPING = {
                0: uinput.KEY_Q,    
                1: uinput.KEY_LEFT, 
                2: uinput.KEY_SPACE,
                3: uinput.KEY_DOT,  
                4: uinput.KEY_RIGHT,
                5: uinput.KEY_UP,
                6: uinput.KEY_X
              }
MAX_EVENT_WAIT_SECONDS = 0.25
EVENT_WAIT_SLEEP_SECONDS = 0.01
EQL_DELAY = .85
VIDEO_SCAN_RELIEF = 2

# Begin setup Operations

# Read ini file for file names
try:
    env = Environment(logFile="engine.log")
except Exception as e:
    print('Failed to read ini file, exiting...')
    sys.exit(1)

logging.info('Initializing Program...')

# Load GUI screen
try:
    logging.info('Creating GUI background...')
    root = Tk()
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),root.winfo_screenheight()))
    root.config(background = 'black')
    img = ImageTk.PhotoImage(Image.open(env.IDLE))
    imgBroke = ImageTk.PhotoImage(Image.open(env.BROKE))
    imgBrokeV = ImageTk.PhotoImage(Image.open(env.BROKE_LINK))
    panel = Label(root, image = img)
    panel.config(background = 'black')
    panel.pack(side = 'bottom', fill = 'both', expand = 'yes')
    root.update()
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

try:
    # Load Sounds
    logging.info('Loading Sound Files...')
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()
    sound = pygame.mixer.Sound(env.TOUCH_SOUND)
    soundBroke = pygame.mixer.Sound(env.BROKE_SOUND)
    sound.set_volume(4)
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)


# Load Keyboard Interface
try:
    logging.info('Loading uinput keyboard interface...')
    subprocess.check_call(['modprobe', 'uinput'])
    device = uinput.Device(KEY_MAPPING.values())
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Setup MPR121 Hardware
try:
    logging.info('Mounting MPR121 device...')
    cap = MPR121.MPR121()
    if not cap.begin():
        raise Exception('Failed to initialize MPR121, check your wiring!')
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Setup PN532 Hardware
try:
    logging.info('Mounting PN532 device...')
    pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
    pn532.begin()
    pn532.SAM_configuration()
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)


# Configure GPIO pins
try:
    logging.info('Configuring GPIO pins...')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING)
    atexit.register(GPIO.cleanup)
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Load videos and cards
try:
    videos = CSVImplementation.openDB(Database, env.VideoList)
    linker = CardToVideoLinker.openFullInstance(videos, env.LinkedTable)
except Exception as e:
    logging.critical('File Setup Failed: ' + str(e))
    sys.exit(1)

logging.info('Setup Complete')

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

def shutdown():
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
                    entry=linker.resolve('0x' + uidt.decode())
                    if entry == linker.KillCode:
                        # Kill card was scanned, cleanup and exit
                        shutdown()
                    video = Video(entry)
                    # i=vidPK.index(uuidFK[i])
                    logging.info('Playing Video: ' + video.getName())
                    if not os.path.isfile(video.getPath()):
                        raise IOError('Video link did not resolve.')
                    subprocess.call('gnome-terminal -x omxplayer -b -o hdmi ' + video.getPath(),shell=True)
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
            for pin, key in KEY_MAPPING.items():
                # Check if pin is touched.
                pin_bit = 1 << pin
                if touched & pin_bit:
                    # Emit sound
                    sound.play()
                    # Emit key event when touched.
                    if key == uinput.X:
                        shutdown()
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
