import logging
import subprocess
import sys
import os
import shutil
import binascii
import time

from tkinter import Tk, messagebox, Frame, Label, Entry, Button, Listbox, Scrollbar, Spinbox, END, DISABLED, StringVar, VERTICAL, NORMAL

from providers.scriptedFileSearch import ScriptedFileSearch
from wrapper.cardScanWrapper import CardScanWrapper
from providers.soundProvider import SoundProvider
from providers.rfidScannerProvider import RFIDScannerProvider
from environment.environment import Environment
from messenger.messenger import Messenger
from editorGUI import EditorGUI

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
        self.messenger = Messenger(logging, messagebox)
        self.configureScannerProvider(rfidScanner)
        self.load()
        self.gui = EditorGUI(master, self._getEvents())
        self.gui.start()

    def _getEvents(self):
        return {
            "save": self._save,
            "quit": self._quit,
            "assignKill": self._assignKill,
            "beginCardScan": self._beginCardScan,
            "updateRepository": self._updateRepository,
            "videoSelectedEvent": self._handleVideoSelectedEvent
        }
    
    def _save(self):
        pass

    def _quit(self):
        ans = messagebox.askquestion(
            'Save And Quit', 'Would you like to save your changes?')
        if ans == 'yes':
            self.save()
        sys.exit(0)

    def _assignKill(self):
        pass

    def _beginCardScan(self):
        self.processCard()
    
    def _updateRepository(self):
        pass

    def _handleVideoSelectedEvent(self):
        pass
    
    def configureScannerProvider(self, rfidScanner):
        provider = RFIDScannerProvider(rfidScanner)
        self.RFIDScannerProvider = provider.PN532(
            int(self.environment.CHIP_SELECT_PIN),
            int(self.environment.MASTER_OUTPUT_SLAVE_INPUT_PIN),
            int(self.environment.MASTER_INPUT_SLAVE_OUTPUT_PIN),
            int(self.environment.SERIAL_CLOCK_PIN))

    def processCard(self):
        # Scans RFID cards and sets them to text box
        try:
            self.processCardUnchecked()
        except Exception as e:
            self.messenger.displayScanError(e)

    def processCardUnchecked(self):
        cardScan = CardScanWrapper(self.soundS, self.RFIDScannerProvider)
        cardScan.runScan()
        self.processResult(cardScan.getFormattedResult())

    def processResult(self, scanResult):
        if scanResult == None:
            return
        self.gui.setCurrentCard(scanResult)
        self.deselectActiveListboxItems()
        self.linkCardWithListbox(scanResult)

    def deselectActiveListboxItems(self):
        self.gui.clearCurrentSelection()

    def linkCardWithListbox(self, scanResult):
        index = self.verifyCard(scanResult)
        if str(self.uuidFK[index]) == self.environment.KillCommand:
            messagebox.showinfo(
                'Kill Card', 'This card is currently assigned to kill the application.')
            return
        self.highlightItemInListbox(index)

    def highlightItemInListbox(self, index):
        try:
            i = self.vidPK.index(self.uuidFK[index])
        except:
            messagebox.showinfo('Card Unassigned',
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
        self.gui.setDeviceControlText('Update Device Repository')

    def safeScan(self):
        scan = None
        try:
            scan = self.runScannerWithNotification()
        except Exception as e:
            self.messenger.showScanErrorMessage(e)
        return scan

    def runScannerWithNotification(self):
        self.gui.setDeviceControlText('Scanning...', False)
        scan = ScriptedFileSearch(subprocess)
        scan.scan("scanner.sh")
        return scan

    def safeProcessScan(self, scan):
        try:
            self.processScan(scan)
        except Exception as e:
            self.messenger.showScanErrorMessage(e)

    def refreshListBox(self):
        self.gui.setVideoList(self.vidNAME)

    def processScan(self, scan):
        # Check if a scan turned up any results
        if self.scanIsEmpty(scan):
            self.messenger.showAbortScanMessage()
            return
        self.verifyUSB()
        self.processScanFiles(scan)
        self.refreshListBox()

    def scanIsEmpty(self, scan):
        return len(scan.NAME) == 0

    def verifyUSB(self):
        currentDevice = self.gui.currentDeviceName()
        if self.environment.Usb != currentDevice:
            self.Usb = currentDevice
            self.environment.update()

    def processScanFiles(self, scan):
        i = 0
        j = 0
        newPK = []
        newName = []
        newPath = []
        self.gui.setDeviceControlText('Reading Files...', False)
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
                            self.gui.setDeviceControlText('Copying ' + scan.NAME[i] + '...', False)
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
            txt = self.gui.getCurrentCard()
            if txt == '':
                return
            i = self.uuid.index(txt)
            self.uuidFK[i] = self.vidPK[selection[0]]
        except Exception as e:
            messagebox.showerror('Error During Set', 'Error: ' + str(e))
            logging.error(str(e))

    def createKiller(self):
        try:
            self.assignCurrentCardAsKiller()
            self.gui.clearCurrentSelection()
        except Exception as e:
            self.handleCardNotScannedError(e)

    def assignCurrentCardAsKiller(self):
        i = self.uuid.index(self.gui.getCurrentCard)
        self.uuidFK[i] = int(self.environment.KillCommand)

    def handleCardNotScannedError(self, e):
        messagebox.showinfo(
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
            scan = ScriptedFileSearch(subprocess)
            scan.scan("scanner.sh")
        except Exception as e:
            logging.error('Device scan failed: ' + str(e))
        else:
            self.searchScanForDevices(scan)

    def loadDevice(self):
        if self.environment.Usb == '' and len(self.devices) == 0:
            self.messenger.terminateWithNoDeviceFailureMessage()
            sys.exit(1)
        else:
            self.handleAnyDeviceSearchFailures()

    def handleAnyDeviceSearchFailures(self):
        if self.environment.Usb == '' or self.environment.Usb == '< Not Set >':
            self.messenger.showNoDeviceSetWarning()
        elif len(self.devices) == 0:
            self.messenger.terminateWithCurrentDeviceNotFoundMsg()
            sys.exit(1)
        elif self.environment.Usb not in self.devices:
            self.messenger.showCurrentDeviceNotFoundWarning()

    def searchScanForDevices(self, scan):
        if len(scan.NAME) == 0:
            self.messenger.showEmptyScanError()
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
            self.messenger.showImproperStorageWarning()