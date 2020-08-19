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

# New Imports
from source.wrapper.cardScanWrapper import CardScanWrapper
from source.providers.rfidScannerProvider import RFIDScannerProvider
from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.cardToVideoLinker import CardToVideoLinker
from source.environment.environment import Environment
from source.dataStructures import Video

# HARDWARE LIBRARIES
import Adafruit_PN532 as PN532
import RPi.GPIO as GPIO
import uinput

CS   = 18
MOSI = 23
MISO = 24
SCLK = 25

KEY_ACTION = {
    "quit": uinput.KEY_Q,     
    "skip": uinput.KEY_LEFT, 
    "play": uinput.KEY_SPACE, 
    "ff": uinput.KEY_DOT,   
    "rewind": uinput.KEY_RIGHT  
}

KEY_PINS = {
    "quit":16, 
    "skip":15, 
    "play":14, 
    "ff":13,  
    "rewind":12 
}

# Pause Delays
EQL_DELAY = .85
VIDEO_SCAN_RELIEF = 2
BOUNCE = 750

# Ini Info
INI_FILE = 'library.ini'
KILL_DEF='KillCommand'
VIDEO_DEF='VideoList'
UUID_DEF='UuidTable'

# Info Defaults
VIDEO_LIST='../vids.csv'
UUID_MAP='../UUID_Table.csv'
FK_KILL = -255

# Read ini file for file names
try:
    env = Environment()
except Exception as e:
    logging.error('Failed to read ini file, exiting...')
    sys.exit(1)

logging.basicConfig(filename=env.LOG_FILE,level=logging.INFO)
logging.info('Initializing Program...')

# Declare statics
class Instance:
    KEY_GATE = 0
    sound = 1
    device = 1
    ff = False
    lastplay = ''

# Establish new intstance of the class
inst = Instance()

try:
    # Load Sounds
    logging.info('Loading Sound Files...')
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()
    Instance.sound = pygame.mixer.Sound(env.TOUCH_SOUND)
    soundBroke = pygame.mixer.Sound(env.BROKE_SOUND)
    Instance.sound.set_volume(4)
    Instance.sound.play()
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

# Define Button Function
def quitKey(evt):
    if Instance.KEY_GATE == 1:
        Instance.sound.play()
        Instance.device.emit_click(KEY_ACTION.get("quit"))
        Instance.lastplay=''
        logging.info('Video Ended by user.')

def skipKey(evt):
    if Instance.KEY_GATE == 1:
        Instance.sound.play()
        Instance.device.emit_click(KEY_ACTION.get("skip"))

def playKey(evt):
    if Instance.KEY_GATE == 1:
        Instance.sound.play()
        if Instance.ff:
            Instance.ff = False 
            Instance.device.emit_click(KEY_ACTION.get("play"))
            time.sleep(.15)
            Instance.device.emit_click(KEY_ACTION.get("play"))
        else:
            Instance.device.emit_click(KEY_ACTION.get("play"))

def ffKey(evt):
    if Instance.KEY_GATE == 1:
        Instance.sound.play()
        if Instance.ff:
            Instance.ff = False
            Instance.device.emit_click(KEY_ACTION.get("play"))
            time.sleep(.15)
            Instance.device.emit_click(KEY_ACTION.get("play"))
        else:
            Instance.ff = True
            Instance.device.emit_click(KEY_ACTION.get("ff"))
            time.sleep(.15)
            Instance.device.emit_click(KEY_ACTION.get("ff"))

def rewindKey(evt):
    if Instance.KEY_GATE == 1:
        Instance.sound.play()
        Instance.device.emit_click(KEY_ACTION.get("rewind"))

# Begin setup Operations
    
try:
    # Load GUI screen
    logging.info('Creating GUI background...')
    root = Tkinter.Tk()
    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),root.winfo_screenheight()))
    root.config(background = 'black')
    img = ImageTk.PhotoImage(Image.open(env.IDLE))
    imgBroke = ImageTk.PhotoImage(Image.open(env.BROKE))
    imgBrokeV = ImageTk.PhotoImage(Image.open(env.BROKE_LINK))
    panel = Tkinter.Label(root, image = img)
    panel.config(background = 'black')
    panel.pack(side = 'bottom', fill = 'both', expand = 'yes')
    root.update()
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

    
try:
    # Load Keyboard Interface
    logging.info('Loading uinput keyboard interface...')
    # Make sure uinput kernel module is loaded.
    subprocess.check_call(['modprobe', 'uinput'])
    # Configure virtual keyboard.
    Instance.device = uinput.Device(KEY_ACTION.values())
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)
    
try:
    # Setup PN532 Hardware
    logging.info('Mounting PN532 device...')
    pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
    pn532.begin()
    # Configure PN532 to communicate with MiFare cards.
    pn532.SAM_configuration()
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)
    
try:
    # Configure GPIO pins 
    logging.info('Configuring GPIO pins...')
    GPIO.setmode(GPIO.BCM)
    for key, pin in iter(KEY_PINS):
        GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(KEY_PINS.get("quit"),GPIO.FALLING,callback=quitKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("skip"),GPIO.FALLING,callback=skipKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("play"),GPIO.FALLING,callback=playKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("ff"),GPIO.FALLING,callback=ffKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("rewind"),GPIO.FALLING,callback=rewindKey,bouncetime=BOUNCE)
except Exception as e:
    logging.critical('Setup Failed: ' + str(e))
    sys.exit(1)

try:
    # Load videos
    videos = CSVImplementation.openDB(Database, env.VideoList)
    linker = CardToVideoLinker.openFullInstance(videos, env.LinkedTable)
except Exception as e:
    logging.critical('File Setup Failed: ' + str(e))
    sys.exit(1)

logging.info('Setup Complete')

# Start Processing ------------------------------------

# Static Instance Trackers
Instance.lastplay = ''
Instance.KEY_GATE = 0

# Local Trackers
changeV = False
sub = None
p = None
scanFQ = 0

# Loop controller
run=0

try:
    # Endless Process Loop
    while (run==0):
        # Run a scan on the card
        uid = pn532.read_passive_target(pn532.read_passive_target.func_defaults[0],.5)
        if uid is None:
            # Card Not Found: Process keys
            Instance.KEY_GATE=1
        else:
            # Card Found: Process Card and kill keys
            Instance.KEY_GATE=0
            uidt = binascii.hexlify(uid)
            # Check if card scan matches the last scan
            if uidt == Instance.lastplay:
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
                        # time.sleep(EQL_DELAY)
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
                Instance.KEY_GATE=1
            else:    
                # Video is not playing or user has requested
                # a different Video
                if (time.time() - scanFQ) < VIDEO_SCAN_RELIEF:
                    # Scan window has not expired... 
                    changeV = False
                    Instance.KEY_GATE=1
                else:
                    changeV = True
            
            # Change the video
            if changeV:
                scanFQ = time.time()
                Instance.KEY_GATE=0
                Instance.sound.play()
                Instance.lastplay = uidt
                # Tell omxplayer to quit
                Instance.device.emit_click(uinput.KEY_Q)
                try:
                    entry=linker.resolve('0x' + uidt)
                    # i=linker.resolve('0x' + uidt)
                    if entry == linker.KillCode:
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
                    video = Video(entry)
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
                    Instance.lastplay = ''
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
                    Instance.lastplay = ''
                    p = None
                    logging.error(str(e))
except Exception as e:
    logging.critical('Unexpected Error: ' + str(e))
    sys.exit(1)
