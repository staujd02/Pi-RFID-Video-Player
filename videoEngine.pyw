#!/home/athos/repos/bin/python3

# Python Packages
# from pynput import keyboard
import atexit
import logging
import pygame
import binascii
import sys
import time
import os.path
import psutil

# GUI Packages
from tkinter import *
from PIL import Image
from PIL import ImageTk

# Vidoe Player
from vlc import Instance

# 3rd Party Hardware Libraries
import board
import busio
import RPi.GPIO as GPIO

from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI
import adafruit_bitbangio as bitbangio
import adafruit_mpr121 as MPR121

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
                0: "quit",    
                1: "skip", 
                2: "play",
                3: "ff",  
                4: "rewind",
                5: "skip_back"
              }
MAX_EVENT_WAIT_SECONDS = 0.10
EVENT_WAIT_SLEEP_SECONDS = 0.01
EQL_DELAY = .85
VIDEO_SCAN_RELIEF = 1

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
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.mixer.init()
    scanSound = pygame.mixer.Sound(env.TOUCH_SOUND)
    soundBroke = pygame.mixer.Sound(env.BROKE_SOUND)
    scanSound.set_volume(4)
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Setup MPR121 Hardware
try:
    logging.info('Mounting MPR121 device...')
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = MPR121.MPR121(i2c)
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Setup PN532 Hardware
try:
    logging.info('Mounting PN532 device...')
    cs = DigitalInOut(board.D18)
    cs.switch_to_output(value=True)
    spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
    pn532 = PN532_SPI(spi, cs, debug=False)
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
player = Instance()
media=None
lastplay=''
keys=True
changeV = False
sub = None
ff = False
scanFQ = 0

# Loop controller
run=0

def shutdown():
    logging.info('Quit Command Recieved!')
    for proc in psutil.process_iter():                            
        try:                            
            pinfo = proc.as_dict(attrs=['name'])
        except psutil.NoSuchProcess:
            pass
        else:
            if 'vlc' == pinfo['name']:
                proc.kill()
            if 'python3' == pinfo['name']:
                proc.kill()
    sys.exit(0)

# def on_press(key):
#     try:
#         if key.char == 'x':
#             shutdown()
#     except AttributeError:
#         pass
# listener = keyboard.Listener(on_press=on_press)
# listener.start()


def maximize():
    # root.overrideredirect(True)
    root.deiconify()
    root.update()

def minimize():
    # root.overrideredirect(False)
    root.withdraw()
    root.update()

try:
    # Clear any pending interrupts by reading touch state.
    cap.touched()
    
    # Endless Process Loop
    while (run==0):
        # Check if a card is available to read.
        try:
            uid = pn532.read_passive_target()
        except Exception as e:
            logging.warn("Failed to read detected card: " + str(e))
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
                time.sleep(EQL_DELAY)
                changeV = media is None or not media.is_playing()
                keys=True
            else:    
                # Video is not playing or user has requested
                # a different Video
                if (time.time() - scanFQ) < VIDEO_SCAN_RELIEF:
                    # Scan window has not expired... 
                    changeV = False
                    keys = True
                else:
                    scanSound.play()
                    maximize()
                    changeV = True
            
            # Change the video
            if changeV:
                scanFQ = time.time()
                keys=False
                lastplay = uidt
                if media != None:
                    media.stop()
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
                    # Start Movice
                    media = player.media_player_new(video.getPath())
                    media.play()
                    time.sleep(2)
                    media.set_fullscreen(1)
                    time.sleep(.2)
                    minimize()
                except IOError as o:
                    # Video File is broken...
                    panel.config(image = imgBrokeV)
                    maximize()
                    soundBroke.play()
                    time.sleep(3)
                    panel.config(image = img)
                    root.update()
                    lastplay = ''
                    logging.error(o)
                except Exception as e:
                    # RFID card is not properly linked...
                    panel.config(image = imgBroke)
                    maximize()
                    root.update()
                    soundBroke.play()
                    time.sleep(3)
                    panel.config(image = img)
                    root.update()
                    lastplay = ''
                    logging.error(str(e))
        if keys:
            # Wait for the IRQ pin to drop or too much time ellapses (to help prevent
            # missing an IRQ event and waiting forever).
            start = time.time()
            while (time.time() - start) < MAX_EVENT_WAIT_SECONDS and not GPIO.event_detected(IRQ_PIN):
                time.sleep(EVENT_WAIT_SLEEP_SECONDS)
            for pin, key in KEY_MAPPING.items():
                # Check if pin is touched.
                pin_touched = cap[pin].value
                if not pin_touched: 
                    continue
                scanSound.play()
                if media is None:
                    continue
                # Emit key event when touched.
                if key == "ff":
                    if media.get_rate() != 2:
                        media.set_rate(2)
                    else:
                        media.set_rate(1)
                elif key == "play":
                    if media.is_playing():
                        media.pause()
                    else:
                        media.set_rate(1)
                        media.play()
                elif key == "skip":
                    media.set_rate(1)
                    media.next_chapter() 
                elif key == "skip_back":
                    media.set_rate(1)
                    media.previous_chapter() 
                elif key == "rewind":
                    media.set_rate(1)
                    media.set_time(media.get_time() - 5000)
                if key == "quit":
                    media.stop()
                    media = None
                    maximize()
                    lastplay=''
                    logging.info('Video Ended by user.')                            
except Exception as e:
    logging.critical('Unexpected Error: ' + str(e))
    sys.exit(1)