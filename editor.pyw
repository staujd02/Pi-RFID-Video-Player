# SOFTWARE
import atexit
import logging
import subprocess
import sys
import os
import shutil
import binascii
import time
import pygame
from Tkinter import *
import tkMessageBox

# HARDWARE LIBRARIES
import Adafruit_PN532 as PN532

class Editor:
    # Configuration for a Raspberry Pi:
    CS   = 18
    MOSI = 23
    MISO = 24
    SCLK = 25
    
    # Timeout
    TIME_OUT = 5

    # Ini Info
    INI_FILE = 'library.ini'
    KILL_DEF='KillCommand'
    VIDEO_DEF='VideoList'
    UUID_DEF='UuidTable'
    USB_DEF='usb'

    # Info Defaults
    LOG_FILE='editior.log'
    VIDEO_LIST='vids.csv'
    UUID_MAP='UUID_Table.csv'
    FK_KILL = -255
    SCAN_SOUND = '/opt/sonic-pi/etc/samples/ambi_soft_buzz.flac'
    
    # Instance Variables
    USB = '< Not Set >'
    devices = []
    vidPK = []
    vidPATH = []
    vidNAME = []
    uuid = []
    uuidFK = []
    pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
        
    def __init__(self, master):
        self.load()
        frame = Frame(master)
        frame.pack()
        self.curR = StringVar()
        self.usbSpin = StringVar()
        self.usbSpin.set(self.USB)
        Label(frame,text='RFID Card').grid(row=0, column=0)
        Label(frame,text='Video').grid(row=0, column=2)
        self.ee = Entry(frame,textvariable=self.curR,state=DISABLED,disabledforeground='black')
        self.ee.grid(row=1, column=0)
        self.r = Button(frame, text='Read Card',command=self.readMiFare)
        self.r.grid(row=1,column=1)
        self.box = Listbox(frame)
        for entry in self.vidNAME:
             self.box.insert(END, entry)
        self.box.bind("<<ListboxSelect>>", self.newselection)
        self.box.grid(row=1,rowspan=5,column=2)
        self.scroll = Scrollbar(self.box,orient=VERTICAL)
        self.box.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.box.yview)
        Button(frame, text='Assign Kill Code',command=self.createKiller).grid(row=2,column=0)
        Label(frame, text='Source USB').grid(row=4, column=0)
        self.spin = Spinbox(frame, values=self.devices)
        self.spin.delete(0,END)
        self.spin.insert(0,self.USB)
        self.spin.grid(row=5,column=0)
        self.status = Button(frame, text='Scan and Update', command=self.merge, disabledforeground='blue')
        self.status.grid(row=6, column=0)
        Button(frame, text='Save and Close', command=self.close).grid(row=6, column=2)
        
        
    def readMiFare(self):
        # Disable button to prevent event stacking
        self.r.config(state=DISABLED)
        # Scans RFID cards and sets them to text box
        try:
            start = time.time()
            uid = None
            while (time.time() - start) < self.TIME_OUT and uid == None:
                uid = self.pn532.read_passive_target()
            if uid == None:
                # Card was not scanned before timeout
                self.r.config(state=NORMAL)
                return;
            self.soundS.play()
            uidt = '0x' + binascii.hexlify(uid)
            # Populate text box
            self.curR.set(uidt)
            # De-select anything active items in listbox
            self.box.selection_clear(0,END)
            try:
                i=self.uuid.index(uidt)
            except:
                # New card (or lost)
                self.uuid.append(uidt)
                self.uuidFK.append(-1)
                i = len(self.uuid) - 1
            if self.uuidFK[i] == self.FK_KILL:
                tkMessageBox.showinfo('Kill Card','This card is currently assigned to kill the application.')
                self.r.config(state=NORMAL)
                return
            try:
                i=self.vidPK.index(self.uuidFK[i])
            except:
                tkMessageBox.showinfo('Card Unassigned','Card is not currently assigned to a video')
            else:
                self.box.see(i)
                self.box.selection_clear(0,END)
                self.box.selection_set(i)
                self.box.activate(i)
        except Exception as e:
            tkMessageBox.showerror('Error Occurred','Error: ' + str(e))
            logging.error('Scan Failed: ' + str(e))
            
        self.r.config(state=NORMAL)
    
    def close(self):
        # Saves active memory to files and then closes app
        # Write video CSV into temp file
        try:
            f = open(self.VIDEO_LIST + '.temp','w')
            i=0
            while(i<len(self.vidPK) - 1):
                f.write(str(self.vidPK[i]) + ',' + self.vidNAME[i] + ',' + self.vidPATH[i] + '\n')
                i=i+1
            f.write(str(self.vidPK[i]) + ',' + self.vidNAME[i] + ',' + self.vidPATH[i] + '\n')
            f.close()
        except Exception as e:
            logging.error('Failed to create video list: ' + str(e))
        else:
            # Replace old file with temp
            try:
                if os.path.isfile(self.VIDEO_LIST):
                    os.remove(self.VIDEO_LIST)
                os.rename(self.VIDEO_LIST + '.temp',self.VIDEO_LIST)
            except Exception as e:
                logging.error('Failed to replace old video list: ' + str(e))
        
        # Write uuid CSV into temp file
        try:
            f = open(self.UUID_MAP + '.temp','w')
            i=0
            while(i<len(self.uuid) - 1):
                f.write(self.uuid[i] + ',' + str(self.uuidFK[i]) + '\n')
                i=i+1
            # Write the last line without the new line character
            f.write(self.uuid[i] + ',' + str(self.uuidFK[i]))
            f.close()
        except Exception as e:
            logging.error('Failed to create UUID list: ' + str(e))
        else:
            # Replace old file with temp
            try:
                if os.path.isfile(self.UUID_MAP):
                    os.remove(self.UUID_MAP)
                os.rename(self.UUID_MAP + '.temp',self.UUID_MAP)
            except Exception as e:
                logging.error('Failed to replace old uuid list: ' + str(e))
        sys.exit(0)
        
    def merge(self):
        # Runs a scan and merges files to usb list
        try:
            self.status.config(text = 'Scanning...',state=DISABLED)
            self.status.update_idletasks()
            scan = Scan()
        except Exception as e:
            tkMessageBox.showerror('Scan Failed','Scan error: ' + str(e))
            logging.error(str(e))
            return
        # Read contents of scan
        try:
            # Check if a scan turned up any results
            if len(scan.NAME) == 0:
                tkMessageBox.showwarning('No Files Found','A scan failed to find any files.')
                logging.warning('Empty Scan occurred when attempting a merge')
                return
            # Set and verifiy USB device
            if self.USB != self.spin.get():
                self.USB = self.spin.get()
                self.regenINI()
            i = 0
            j = 0
            newPK = []
            newName = []
            newPath = []
            self.status.config(text = 'Reading Files...')
            self.status.update_idletasks()
            # Iterate through list
            while i < len(scan.NAME):
                # Verifiy File
                try:
                    if scan.PATH[i].find(self.USB) >= 0:
                        # File resides on repository - update FK
                        try:
                            # Locate matching entry
                            fkk = self.vidNAME.index(scan.NAME[i])
                        except Exception as e:
                            # No matching entry
                            logging.info('New file found in repository: ' + str(e))
                            pass
                        else:
                            # Update FK on uuid table
                            for uu in self.uuidFK:
                                if uu == self.vidPK[fkk]:
                                    uu = scan.PK[i]
                        # Store entry in new Tables
                        newPK.append(scan.PK[i])
                        newName.append(scan.NAME[i])
                        newPath.append(scan.PATH[i])
                    else:
                        # Video resides on updating device - check if file already copied
                        found = False
                        while j < len(scan.NAME):
                            if str(scan.NAME[i]) == str(scan.NAME[j]) and scan.PATH[j].find(self.USB) >= 0:
                                found = True
                                break
                            j = j +1
                        if not found:
                            # Copy file and append
                            try:
                                # Get device name
                                device = scan.PATH[i].replace('/media/pi/','')
                                device = device[0:device.find('/')]
                                # Copy
                                self.status.config(text = 'Copying ' + scan.NAME[i] + '...')
                                self.status.update_idletasks()
                                shutil.copyfile(scan.PATH[i],scan.PATH[i].replace(device,self.USB))
                            except Exception as e:
                                logging.error('Failed to copy' + scan.NAME[i] + ': ' + str(e))
                            else:
                                # Add to new array
                                newPK.append(scan.PK[i])
                                newName.append(scan.NAME[i])
                                newPath.append(scan.PATH[i].replace(device, self.USB))
                except Exception as e:
                    logging.error(str(e))
                i=i+1
            # Clone array over
            del self.vidNAME[:]
            del self.vidPATH[:]
            del self.vidPK[:]
            self.vidNAME = newName
            self.vidPATH = newPath
            self.vidPK = newPK
            # Update box
            self.box.delete(0,END)
            for entry in self.vidNAME:
             self.box.insert(END, entry) 
        except Exception as e:
            tkMessageBox.showerror('Error','Error: ' + str(e))
            logging.error(str(e))
        self.status.config(text = 'Scan and Update', state=NORMAL)
        self.status.update_idletasks()
    
    def newselection(self, event):
        # Fires when a new item is selected in the listbox
        widget = event.widget
        selection=widget.curselection()
        try:
            txt = self.ee.get()
            if txt == '':
                return
            i = self.uuid.index(txt)
            self.uuidFK[i] = self.vidPK[selection[0]]
        except Exception as e:
            tkMessageBox('Error During Set','Error: ' + str(e))
            logging.error(str(e))
        
    def createKiller(self):
        try:
            i = self.uuid.index(self.ee.get())
            self.uuidFK[i] = self.FK_KILL
            self.box.selection_clear(0,END)
        except Exception as e:
            tkMessageBox.showinfo('Card Not Scanned','Please scan a card to assign it a [Kill Application] code.' + str(e))
            logging.error(str(e))
    
    def load(self):
        # Generate Log
        logging.basicConfig(filename=self.LOG_FILE,level=logging.INFO)
        # Load Sound file
        pygame.mixer.pre_init(44100, -16, 12, 512)
        pygame.init()
        self.soundS = pygame.mixer.Sound(self.SCAN_SOUND)
        self.soundS.set_volume(1)
        # Create an instance of the PN532 class.
        self.pn532.begin()
        # Configure PN532 to communicate with MiFare cards.
        self.pn532.SAM_configuration()
        self.loadFiles()
        self.loadUSB()
    
    def loadFiles(self):
        regen = False
        
        # Read ini file for file names
        try:
            logging.info("Loading ini file...")
            f = open(self.INI_FILE,'r')
            lines = f.read().splitlines()
            f.close()
            for setting in lines:
                s = setting.split('=')
                if s[0] == self.USB_DEF:
                    self.USB = s[1]
                elif s[0] == self.VIDEO_DEF:
                    self.VIDEO_LIST = s[1]
                elif s[0] == self.UUID_DEF:
                    self.UUID_MAP = s[1]
                elif s[0] == self.KILL_DEF:
                    self.FK_KILL = int(s[1])
        except Exception as e:
            logging.error('Failed to read ini file: ' + str(e))
            regen = True
        
        # Re-create file if neccessary
        if regen == True:
            self.regenINI()
        
        # Load video CSV into memory
        try:
            f = open(self.VIDEO_LIST,'r')
            vids = f.read().splitlines()
            f.close()
        except Exception as e:
            logging.error('Failed to load video list: ' + str(e))
        else:
            i=0
            while(i<len(vids)):
                split = vids[i].split(',')
                self.vidNAME.append(split[1])
                self.vidPATH.append(split[2])
                self.vidPK.append(int(split[0]))
                i=i+1
        try: 
           # Load UUID CSV into memory
           f = open(self.UUID_MAP,'r')
           rfid = f.read().splitlines()
           f.close()
        except Exception as e:
           logging.error('Failed to load UUID list: ' + str(e))
        else:
           i=0
           l = len(rfid)
           while (i < l):
               split = rfid[i].split(',')
               self.uuid.append(split[0])
               self.uuidFK.append(int(split[1]))
               i=i+1

    def regenINI(self):
        try:
            logging.info('Regenerating ini file...')
            f = open(self.INI_FILE,'w')
            f.write(self.USB_DEF + '=' + self.USB + '\n')
            f.write(self.KILL_DEF + '=' + str(self.FK_KILL) + '\n')
            f.write(self.VIDEO_DEF + '=' + self.VIDEO_LIST + '\n')
            f.write(self.UUID_DEF + '=' + self.UUID_MAP)
            f.close()
        except:
            logging.error('Failed to regenerate ini file!')

    def loadUSB(self):
        # Check if usb is set and present    
        try:
            scan = Scan()
        except Exception as e:
            logging.error('Device scan failed: ' + str(e))
        else:
            if len(scan.NAME) == 0:
                tkMessageBox.showerror('Scan Error','Initial scan detected no files. Open case and inspect USB, or perform a restart.')
                logging.error('Scan failed to detect files. (Do none exist?)')
            else:
                # Scan detected files... Pull usb name from path
                for path in scan.PATH:
                    try:
                        subpath = path.replace('/media/pi/','')
                        if subpath[0:subpath.find('/')] not in self.devices:
                            self.devices.append(subpath[0:subpath.find('/')])
                    except:
                        pass
                # Check if devices were found
                if len(self.devices) == 0:
                    tkMessageBox.showerror('Improper Storage','Media files should not be stored in /media/pi.\nPlease move files to subfolder, or a USB device.')
                    logging.error('User error: Files were stored on pi media root. Requested User Action...')
        if self.USB == '' and len(self.devices) == 0:
            # Bad news, no usb is set and no devices were detected!
            tkMessageBox.showerror('Storage Failure', 'No USB devices could be found, this editor will now close.')
            logging.critical('Failed to find any devices with any media. Closing...')
            sys.exit(1)
        else:
             # Either there is at least one device or usb is set
             if self.USB == '' or self.USB == '< Not Set >':
                 tkMessageBox.showwarning('No USB Set','Please select a USB as a source device and then perform a Scan and Update')
                 logging.warning('No USB device is set!')
             elif len(self.devices) == 0:
                 tkMessageBox.showerror('No Devices Detected','No devices were detected including the current USB respository.\nPlease inspect USB device, or contact help.')
                 logging.critical('Scanner detected no devices. Closing...')
                 sys.exit(1)
             elif self.USB not in self.devices:
                 tkMessageBox.showwarning('Missing USB Source','WARNING: The current USB repository was not found amoung the available devices.')
                 logging.warning('Current USB repository was not located in device scan!')

class WaitPrompt:
    def __init__(self, master):
        self.load()
        frame = Frame(master)
        frame.pack()
        self.msg = StringVar()
        Label(frame,text='Status').grid(row=0, column=0)
        Label(frame,text=self.msg).grid(row=1, column=0)
        
    def setMsg(self, Message):
        try:
            self.msg.set(str(Message))
            self.update()
        except Exception as e:
            logging.error('Message ' + str(Message) + ' failed to set.\n' + str(e))

class Scan:
    
    SCANNER = 'scanner.sh'
    TEMP = 'temp.list'
    
    NAME = []
    PATH = []
    PK = []
    
    scanComplete = False
    
    # Scan results
    contents = []
    
    def __init__(self):
        self.scan()
        self.scanComplete = True
    
    def scan(self):
        del self.NAME[:]
        del self.PATH[:]
        del self.PK[:]
        subprocess.call('./' + self.SCANNER + ' > ' + self.TEMP, shell=True)
        # Load scan output to memory
        f = open(self.TEMP)
        vids = f.read().splitlines()
        f.close()
        if os.path.isfile(self.TEMP):
            os.remove(self.TEMP)
        i=0
        while(i<len(vids)):
            split = vids[i].split(',')
            self.PK.append(int(split[0]))
            self.NAME.append(split[1])
            self.PATH.append(split[2])
            i=i+1

# Load GUI screen
root = Tk()
#root.config(background = 'black')
root.wm_title('RFID Editor')
app = Editor(root)
root.mainloop()