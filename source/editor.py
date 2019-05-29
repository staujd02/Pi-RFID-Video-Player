import atexit
import logging
import subprocess
import sys
import os
import shutil
import binascii
import time

from tkinter import Tk, messagebox, Frame, Label, Entry, Button, Listbox, Scrollbar, Spinbox, END, DISABLED, StringVar, VERTICAL, NORMAL

from Scan import Scan
from cardScan import CardScan
from soundProvider import SoundProvider
from rfidScannerProvider import RFIDScannerProvider
from environment import Environment

class Editor:

    # Info Defaults
    LOG_FILE = 'editor.log'

    devices = []
    vidPK = []
    vidPATH = []
    vidNAME = []
    uuid = []
    uuidFK = []

    def __init__(self, master, soundGenerator, rfidScanner):
        self.environment = Environment()
        self.soundProvider = SoundProvider(soundGenerator)
        self.configureScannerProvider(rfidScanner)
        self.load()
        frame = Frame(master)
        frame.pack()
        self.activeCardNumber = StringVar()
        self.usbSpin = StringVar()
        self.usbSpin.set(self.environment.Usb)
        Label(frame, text='RFID Card').grid(row=0, column=0)
        Label(frame, text='Video').grid(row=0, column=2)
        self.ee = Entry(frame, textvariable=self.activeCardNumber,
                        state=DISABLED, disabledforeground='black')
        self.ee.grid(row=1, column=0)
        self.r = Button(frame, text='Read Card', command=self.startCardProcess)
        self.r.grid(row=1, column=1)
        self.box = Listbox(frame)
        for entry in self.vidNAME:
            self.box.insert(END, entry)
        self.box.bind("<<ListboxSelect>>", self.newselection)
        self.box.grid(row=1, rowspan=5, column=2, columnspan=2)
        self.scroll = Scrollbar(self.box, orient=VERTICAL)
        self.box.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.box.yview)
        Button(frame, text='Assign Kill Code',
               command=self.createKiller).grid(row=2, column=0)
        Label(frame, text='Source USB').grid(row=4, column=0)
        self.spin = Spinbox(frame, values=self.devices)
        self.spin.delete(0, END)
        self.spin.insert(0, self.environment.Usb)
        self.spin.grid(row=5, column=0)
        self.status = Button(frame, text='Update Device Repository',
                             command=self.updateDevice, disabledforeground='blue')
        self.status.grid(row=6, column=0)
        Button(frame, text='Save', command=self.save).grid(row=6, column=2)
        Button(frame, text='Quit', command=self.closeWithSavePrompt).grid(
            row=6, column=3)
    
    def configureScannerProvider(self, rfidScanner):
        provider = RFIDScannerProvider(rfidScanner)
        self.RFIDScannerProvider = provider.PN532(
            int(self.environment.CHIP_SELECT_PIN),
            int(self.environment.MASTER_OUTPUT_SLAVE_INPUT_PIN),
            int(self.environment.MASTER_INPUT_SLAVE_OUTPUT_PIN),
            int(self.environment.SERIAL_CLOCK_PIN))

    def closeWithSavePrompt(self):
        ans = MessageBox.askquestion(
            'Save And Quit', 'Would you like to save your changes?')
        if ans == 'yes':
            self.save()
        sys.exit(0)

    def startCardProcess(self):
        # Disable button to prevent event stacking
        self.r.config(state=DISABLED)
        self.processCard()
        self.r.config(state=NORMAL)

    def processCard(self):
        # Scans RFID cards and sets them to text box
        try:
            self.processCardUnchecked()
        except Exception as e:
            self.displayScanError(e)

    def processCardUnchecked(self):
        cardScan = CardScan(self.soundS, self.RFIDScannerProvider)
        cardScan.runScan()
        self.processResult(cardScan.getFormattedResult())

    def processResult(self, scanResult):
        if scanResult == None:
            return
        self.activeCardNumber.set(scanResult)     # Populate text box
        self.deselectActiveListboxItems()
        self.linkCardWithListbox(scanResult)

    def deselectActiveListboxItems(self):
        # De-select any active items in listbox
        self.box.selection_clear(0, END)

    def linkCardWithListbox(self, scanResult):
        index = self.verifyCard(scanResult)
        if str(self.uuidFK[index]) == self.environment.KillCommand:
            MessageBox.showinfo(
                'Kill Card', 'This card is currently assigned to kill the application.')
            return
        self.highlightItemInListbox(index)

    def highlightItemInListbox(self, index):
        try:
            i = self.vidPK.index(self.uuidFK[index])
        except:
            MessageBox.showinfo('Card Unassigned',
                                'Card is not currently assigned to a video')
        else:
            self.box.see(i)
            self.box.selection_clear(0, END)
            self.box.selection_set(i)
            self.box.activate(i)

    def verifyCard(self, uidt):
        try:
            uuidIndex = self.uuid.index(uidt)
        except:
            uuidIndex = self.addNewCard(uidt)
        return uuidIndex

    def addNewCard(self, uidt):
        self.uuid.append(uidt)
        self.uuidFK.append(-1)
        newIndex = len(self.uuid) - 1
        return newIndex

    def displayScanError(self, e):
        MessageBox.showerror('Error Occurred', 'Error: ' + str(e))
        logging.error('Scan Failed: ' + str(e))

    def save(self):
        toSaveList = self.makePairedList(
            self.vidPK, self.vidNAME, self.vidPATH)
        self.safeSaveToFile(self.environment.VideoList, toSaveList)
        toSaveList = self.makePairedList(self.uuid, self.uuidFK)
        self.safeSaveToFile(self.environment.UuidTable, toSaveList)

    def makePairedList(self, *itemLists):
        stop = len(itemLists)
        subList = []
        listAll = []
        for listIndex in range(len(itemLists[0])):
            del subList[:]
            for indice in range(stop):
                subList.append(itemLists[indice][listIndex])
            listAll.append(list(subList))
        return listAll

    def safeSaveToFile(self, fileName, pairList):
        try:
            self.writePairedListToTempFile(fileName, pairList)
        except Exception as e:
            logging.error('Failed to create video list: ' + str(e))
        else:
            self.replaceOriginalFileWithItsTemp(fileName)

    def replaceOriginalFileWithItsTemp(self, fileName):
        try:
            if os.path.isfile(fileName):
                os.remove(fileName)
            os.rename(fileName + '.temp', fileName)
        except Exception as e:
            logging.error('Failed to replace old video list: ' + str(e))

    def writePairedListToTempFile(self, fileName, pairedList):
        f = open(fileName + '.temp', 'w')
        self.writePairedListGivenFile(f, pairedList)
        f.close()

    def writePairedListGivenFile(self, f, pairedList):
        i = 0
        while(i < len(pairedList) - 1):
            self.writeSingleLineOfPairedListToOpenFile(f, pairedList, i)
            f.write('\n')
            i = i+1
        self.writeSingleLineOfPairedListToOpenFile(f, pairedList, i)

    def writeSingleLineOfPairedListToOpenFile(self, f, pairedList, itemIndex):
        fLine = ""
        for item in range(len(pairedList[itemIndex])):
            fLine = fLine + str(pairedList[itemIndex][item]) + ','
        f.write(fLine[:-1])

    def updateDevice(self):
        scan = self.safeScan()
        if scan != None:
            self.safeProcessScan(scan)
        self.status.config(text='Update Device Repository', state=NORMAL)
        self.status.update_idletasks()

    def safeScan(self):
        scan = None
        try:
            scan = self.runScannerWithNotification()
        except Exception as e:
            self.showScanErrorMessage(e)
        return scan

    def runScannerWithNotification(self):
        self.status.config(text='Scanning...', state=DISABLED)
        self.status.update_idletasks()
        scan = Scan(subprocess)
        scan.scan("scanner.sh")
        return scan

    def showScanErrorMessage(self, e):
        MessageBox.showerror('Scan Failed', 'Scan error: ' + str(e))
        logging.error(str(e))

    def safeProcessScan(self, scan):
        try:
            self.processScan(scan)
        except Exception as e:
            self.showErrorMessage(e)

    def showErrorMessage(self, e):
        MessageBox.showerror('Error', 'Error: ' + str(e))
        logging.error(str(e))

    def refreshListBox(self):
        self.box.delete(0, END)
        for entry in self.vidNAME:
            self.box.insert(END, entry)

    def processScan(self, scan):
        # Check if a scan turned up any results
        if self.scanIsEmpty(scan):
            self.showAbortScanMessage()
            return
        self.verifyUSB()
        self.processScanFiles(scan)
        self.refreshListBox()

    def showAbortScanMessage(self):
        MessageBox.showwarning(
            'No Files Found', 'A scan failed to find any files.')
        logging.warning('Empty Scan occurred when attempting a merge')

    def scanIsEmpty(self, scan):
        return len(scan.NAME) == 0

    def verifyUSB(self):
        if self.environment.Usb != self.spin.get():
            self.Usb = self.spin.get()
            self.environment.update()

    def processScanFiles(self, scan):
        i = 0
        j = 0
        newPK = []
        newName = []
        newPath = []
        self.status.config(text='Reading Files...')
        self.status.update_idletasks()
        # Iterate through list
        while i < len(scan.NAME):
            # Verifiy File
            try:
                if scan.PATH[i].find(self.environment.Usb) >= 0:
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
                        if str(scan.NAME[i]) == str(scan.NAME[j]) and scan.PATH[j].find(self.environment.Usb) >= 0:
                            found = True
                            break
                        j = j + 1
                    if not found:
                        # Copy file and append
                        try:
                            # Get device name
                            device = scan.PATH[i].replace('/media/pi/', '')
                            device = device[0:device.find('/')]
                            # Copy
                            self.status.config(
                                text='Copying ' + scan.NAME[i] + '...')
                            self.status.update_idletasks()
                            shutil.copyfile(
                                scan.PATH[i], scan.PATH[i].replace(device, self.environment.Usb))
                        except Exception as e:
                            logging.error('Failed to copy' +
                                          scan.NAME[i] + ': ' + str(e))
                        else:
                            # Add to new array
                            newPK.append(scan.PK[i])
                            newName.append(scan.NAME[i])
                            newPath.append(
                                scan.PATH[i].replace(device, self.environment.Usb))
            except Exception as e:
                logging.error(str(e))
            i = i+1
        del self.vidNAME[:]
        del self.vidPATH[:]
        del self.vidPK[:]
        self.vidNAME = newName
        self.vidPATH = newPath
        self.vidPK = newPK

    def newselection(self, event):
        # Fires when a new item is selected in the listbox
        selection = event.widget.curselection()
        try:
            txt = self.ee.get()
            if txt == '':
                return
            i = self.uuid.index(txt)
            self.uuidFK[i] = self.vidPK[selection[0]]
        except Exception as e:
            MessageBox.showerror('Error During Set', 'Error: ' + str(e))
            logging.error(str(e))

    def createKiller(self):
        try:
            self.assignCurrentCardAsKiller()
            self.box.selection_clear(0, END)
        except Exception as e:
            self.handleCardNotScannedError(e)

    def assignCurrentCardAsKiller(self):
        i = self.uuid.index(self.ee.get())
        self.uuidFK[i] = int(self.environment.KillCommand)

    def handleCardNotScannedError(self, e):
        MessageBox.showinfo(
            'Card Not Scanned', 'Please scan a card to assign it a [Kill Application] code.' + str(e))
        logging.error(str(e))

    def load(self):
        # Generate Log
        logging.basicConfig(filename=self.LOG_FILE, level=logging.INFO)
        # Load Sound file
        self.soundProvider.init()
        self.soundProvider.mixer.pre_init(44100, -16, 12, 512)
        # pygame.init() IS this only for linux distribution?
        self.soundS = self.soundProvider.mixer.Sound(self.environment.SCAN_SOUND)
        self.soundS.set_volume(1)
        # Create an instance of the PN532 class.
        self.RFIDScannerProvider.begin()
        # Configure PN532 to communicate with MiFare cards.
        self.RFIDScannerProvider.SAM_configuration()
        self.loadFiles()
        self.locateDevices()
        self.loadDevice()

    def loadFiles(self):
        self.readCSV(self.environment.VideoList, (int, self.vidPK),
                     (str, self.vidNAME), (str, self.vidPATH))
        self.readCSV(self.environment.UuidTable,
                     (str, self.uuid), (int, self.uuidFK))

    def readCSV(self, fileName, *storageList):
        try:
            fileContents = self.splitFileContentsIntoLines(fileName)
        except Exception as e:
            logging.error('Failed to load video list: ' + str(e))
        else:
            self.processCSV(fileContents, storageList)

    def splitFileContentsIntoLines(self, fileName):
        f = open(fileName, 'r')
        fileContents = f.read().splitlines()
        f.close()
        return fileContents

    def processCSV(self, fileContents, storageList):
        i = 0
        while (i < len(fileContents)):
            split = fileContents[i].split(',')
            for item in range(len(storageList)):
                if storageList[item][0] is int:
                    storageList[item][1].append(int(split[item]))
                else:
                    storageList[item][1].append(split[item])
            i = i+1

    def locateDevices(self):
        try:
            scan = Scan(subprocess)
            scan.scan("scanner.sh")
        except Exception as e:
            logging.error('Device scan failed: ' + str(e))
        else:
            self.searchScanForDevices(scan)

    def loadDevice(self):
        if self.environment.Usb == '' and len(self.devices) == 0:
            self.terminateWithNoDeviceFailureMessage()
        else:
            self.handleAnyDeviceSearchFailures()

    def handleAnyDeviceSearchFailures(self):
        if self.environment.Usb == '' or self.environment.Usb == '< Not Set >':
            self.showNoDeviceSetWarning()
        elif len(self.devices) == 0:
            self.terminateWithCurrentDeviceNotFoundMsg()
        elif self.environment.Usb not in self.devices:
            self.showCurrentDeviceNotFoundWarning()

    def showNoDeviceSetWarning(self):
        MessageBox.showwarning(
            'No USB Set', 'Please select a USB as a source device and then perform a Scan and Update')
        logging.warning('No USB device is set!')

    def showCurrentDeviceNotFoundWarning(self):
        MessageBox.showwarning(
            'Missing USB Source', 'WARNING: The current USB repository was not found amoung the available devices.')
        logging.warning(
            'Current USB repository was not located in device scan!')

    def terminateWithCurrentDeviceNotFoundMsg(self):
        MessageBox.showerror(
            'No Devices Detected', 'No devices were detected including the current USB respository.\nPlease inspect USB device, or contact help.')
        logging.critical('Scanner detected no devices. Closing...')
        sys.exit(1)

    def terminateWithNoDeviceFailureMessage(self):
        MessageBox.showerror(
            'Storage Failure', 'No USB devices could be found, this editor will now close.')
        logging.critical(
            'Failed to find any devices with any media. Closing...')
        sys.exit(1)

    def searchScanForDevices(self, scan):
        if len(scan.NAME) == 0:
            self.showEmptyScanError()
        else:
            self.pullDeviceNamesFromPath(scan)
            self.ensureDeviceWasFound()

    def pullDeviceNamesFromPath(self, scan):
        for path in scan.PATH:
            try:
                subpath = path.replace('/media/pi/', '')
                if subpath[0:subpath.find('/')] not in self.devices:
                    self.devices.append(subpath[0:subpath.find('/')])
            except:
                pass

    def ensureDeviceWasFound(self):
        if len(self.devices) == 0:
            MessageBox.showerror(
                'Improper Storage', 'Media files should not be stored in /media/pi.\nPlease move files to subfolder, or a USB device.')
            logging.error(
                'User error: Files were stored on pi media root. Requested User Action...')

    def showEmptyScanError(self):
        MessageBox.showerror(
            'Scan Error', 'Initial scan detected no files. Open case and inspect USB, or perform a restart.')
        logging.error('Scan failed to detect files. (Do none exist?)')
