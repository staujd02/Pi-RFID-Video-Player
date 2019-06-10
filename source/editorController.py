import logging
from tkinter import messagebox

from environment.environment import Environment
from editorGUI import EditorGUI
from messenger.messenger import Messenger
from providers.rfidScannerProvider import RFIDScannerProvider
from providers.soundProvider import SoundProvider
from dataManagers.database import Database
from dataManagers.csvImplementation import CSVImplementation
from dataManagers.cardToVideoLinker import CardToVideoLinker
from wrapper.cardScanWrapper import CardScanWrapper

# Top TODO:
#     == Create Migrator (
#         > Handle moving file list from one device to another
#         > Verify with monster scan function
#     )


class EditorController:

    def __init__(self, master, SoundResource, RFIDResource):
        self.env = Environment()
        self.configureDataProviders()
        self.configureScanners(SoundResource, RFIDResource)
        self.messenger = Messenger(logging, messagebox)
        self.configureGUI(master)

    def configureGUI(self, master):
        self.gui = EditorGUI(master, self.events(), self.env.Usb)
        self.gui.start()

    def configureScanners(self, SoundResource, RFIDResource):
        sound = self.configureSoundProvider(SoundResource)
        self.rfid = self.configureScannerProvider(RFIDResource)
        self.cardScan = CardScanWrapper(sound, self.rfid)

    def configureDataProviders(self):
        self.cards = CSVImplementation.openDB(Database, self.env.UuidTable)
        self.videos = CSVImplementation.openDB(Database, self.env.VideoList)
        self.linker = CardToVideoLinker(self.videos, self.env.LinkedTable)

    def configureScannerProvider(self, rfidScanner):
        provider = RFIDScannerProvider(rfidScanner)
        return provider.PN532(
            int(self.env.CHIP_SELECT_PIN),
            int(self.env.MASTER_OUTPUT_SLAVE_INPUT_PIN),
            int(self.env.MASTER_INPUT_SLAVE_OUTPUT_PIN),
            int(self.env.SERIAL_CLOCK_PIN))

    def configureSoundProvider(self, SoundProvider):
        SoundProvider.init()
        SoundProvider.mixer.pre_init(44100, -16, 12, 512)
        scanSound = SoundProvider.mixer.Sound(self.env.SCAN_SOUND)
        scanSound.set_volume(1)
        return scanSound

    def events(self):
        return {
            "save": self.empty,
            "quit": self.empty,
            "assignKill": self.empty,
            "beginCardScan": self.empty,
            "updateRepository": self.empty,
            "videoSelectedEvent": self.empty
        }

    def empty(self, opt="nothing"):
        pass