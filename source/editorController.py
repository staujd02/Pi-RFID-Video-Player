import logging
from tkinter import messagebox
from sys import exit

from environment.environment import Environment
from editorGUI import EditorGUI
from messenger.messenger import Messenger
from providers.rfidScannerProvider import RFIDScannerProvider
from providers.soundProvider import SoundProvider

from wrapper.cardScanWrapper import CardScanWrapper

# from providers.rfidScannerProvider import RFIDScannerProvider from providers.soundProvider import SoundProvider

# Top TODO:
#     == Create Migrator (
#         > Handle moving file list from one device to another
#         > Verify with monster scan function
#     )

class EditorController:

    def __init__(self, master, SoundResource, RFIDResource):
        self.env = Environment()
        self.soundProvider = SoundProvider(SoundResource)
        self.rfid = self.configureScannerProvider(RFIDResource)
        self.cardScan = CardScanWrapper(SoundProvider(SoundResource), self.rfid)
        self.messenger = Messenger(logging, messagebox)
        self.gui = EditorGUI(master, self.events(), self.env.Usb)
        self.gui.start()
    
    def configureScannerProvider(self, rfidScanner):
        provider = RFIDScannerProvider(rfidScanner)
        return provider.PN532(
            int(self.env.CHIP_SELECT_PIN),
            int(self.env.MASTER_OUTPUT_SLAVE_INPUT_PIN),
            int(self.env.MASTER_INPUT_SLAVE_OUTPUT_PIN),
            int(self.env.SERIAL_CLOCK_PIN))

    def configureSoundProvider(self, SoundProvider):
        self.soundProvider.init()
        self.soundProvider.mixer.pre_init(44100, -16, 12, 512)
        # pygame.init() IS this only for linux distribution?
        self.soundS = self.soundProvider.mixer.Sound(self.env.SCAN_SOUND)
        self.soundS.set_volume(1)

    def events(self):
        return {
            "save": self.save,
            "quit": self.quit,
            "assignKill": self.assignKill,
            "beginCardScan": self.beginCardScan,
            "updateRepository": self.updateRepository,
            "videoSelectedEvent": self.videoSelectedEvent
        }
    
    def save(self):
        pass

    def quit(self):
        ans = self.messenger.showSaveAndExit()
        if ans == 'yes':
            self.save()
        exit(0)
    
    def assignKill(self):
        pass
    
    def beginCardScan(self):
        self.cardScan.runScan()
        if cardScan.getFormattedResult():
            pass
            
    def videoSelectedEvent(self, event):
        pass
    
    def updateRepository(self):
        pass