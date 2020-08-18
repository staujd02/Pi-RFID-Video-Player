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

# Program Constants
LOG_FILE='engine.log'
IDLE = '../resources/images/bg.jpg'
BROKE = '../resources/images/broke.png'
BROKE_LINK = '../resources/images/brokenLink.png'
TOUCH_SOUND = '/opt/sonic-pi/etc/samples/elec_plip.flac'
BROKE_SOUND = '/opt/sonic-pi/etc/samples/bass_dnb_f.flac'

# Declare statics
class Instance:
    KEY_GATE = 0
    sound = 1
    device = 1
    ff = False
    lastplay = ''

# Establish new intstance of the class
inst = Instance()

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

##def buttonEventHandler(pin):
##    key = KEY_MAPPING.get(pin)
##    if KEY_GATE == 1:
##        sound.play()
##        if key == uinput.KEY_DOT:
##            if ff:
##                ff = False
##                device.emit_click(uinput.KEY_SPACE)
##                time.sleep(.15)
##                device.emit_click(uinput.KEY_SPACE)
##            else:
##                ff = True
##                device.emit_click(key)
##                time.sleep(.15)
##                device.emit_click(key)
##        elif key == uinput.KEY_SPACE:
##            if ff:
##                device.emit_click(key)
##                time.sleep(.15)
##            ff = False
##            device.emit_click(key)
##        else:
##            device.emit_click(key)
##        if key == uinput.KEY_Q:
##            lastplay=''
##            p = None
##            logging.info('Video Ended by user.')
##        time.sleep(0.1)        

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
    Instance.sound = pygame.mixer.Sound(TOUCH_SOUND)
    soundBroke = pygame.mixer.Sound(BROKE_SOUND)
    Instance.sound.set_volume(4)
    Instance.sound.play()
    
    # Load Keyboard Interface
    logging.info('Loading uinput keyboard interface...')
    # Make sure uinput kernel module is loaded.
    subprocess.check_call(['modprobe', 'uinput'])
    # Configure virtual keyboard.
    Instance.device = uinput.Device(KEY_ACTION.values())
    
    # Setup PN532 Hardware
    logging.info('Mounting PN532 device...')
    pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
    pn532.begin()
    # Configure PN532 to communicate with MiFare cards.
    pn532.SAM_configuration()
    
    # Configure GPIO pins 
    logging.info('Configuring GPIO pins...')
    GPIO.setmode(GPIO.BCM)
    for key,pin in KEY_PINS.iteritems():
        GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(KEY_PINS.get("quit"),GPIO.FALLING,callback=quitKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("skip"),GPIO.FALLING,callback=skipKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("play"),GPIO.FALLING,callback=playKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("ff"),GPIO.FALLING,callback=ffKey,bouncetime=BOUNCE)
    GPIO.add_event_detect(KEY_PINS.get("rewind"),GPIO.FALLING,callback=rewindKey,bouncetime=BOUNCE)
    #GPIO.add_event_detect(pin,GPIO.FALLING,callback=lambda x:buttonEventHandler(pin),bouncetime=1000)                     

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
