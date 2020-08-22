import logging
from tkinter import messagebox
import subprocess
import shutil

from source.environment.environment import Environment
from source.editorGUI import EditorGUI
from source.messenger.messenger import Messenger
from source.providers.rfidScannerProvider import RFIDScannerProvider
from source.providers.soundProvider import SoundProvider
from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.cardToVideoLinker import CardToVideoLinker
from source.wrapper.cardScanWrapper import CardScanWrapper
from source.migrators.migrator import Migrator
from source.informationManagers.search.scriptedFileSearch import ScriptedFileSearch
from source.utilities.devices import Devices
from source.utilities.fileManager import FileManager

class EditorController:

    def __init__(self, master, SoundResource, RFIDResource):
        self.master = master
        self.soundResource = SoundResource
        self.RFIDResource = RFIDResource

    def init(self):
        self.env = Environment()
        self.messenger = Messenger(logging, messagebox)
        self.configure()
        self.postConfiguration()

    def configure(self):
        self.configureGUI(self.master)
        self.configureScanners(self.soundResource, self.RFIDResource)
        self.configureDataProviders()
        self.configureMigrators()

    def configureGUI(self, master):
        self.gui = EditorGUI(master, self.events(), self.env.Usb)

    def configureScanners(self, SoundResource, RFIDResource):
        sound = self.configureSoundProvider(SoundResource)
        self.rfid = self.configureScannerProvider(RFIDResource)
        self.cardScan = CardScanWrapper(sound, self.rfid)

    def configureDataProviders(self):
        FileManager().guaranteeListOfFilesExist([self.env.VideoList, self.env.LinkedTable])
        self.videos = CSVImplementation.openDB(Database, self.env.VideoList)
        self.linker = CardToVideoLinker.openFullInstance(self.videos, self.env.LinkedTable)

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

    def configureMigrators(self):
        scriptedFileSearch = ScriptedFileSearch(subprocess)
        self.migrator = Migrator(scriptedFileSearch, self.videos, shutil, self.messenger)
        self.devices = Devices(scriptedFileSearch)

    # Abstract Overridables Hooks

    def postConfiguration(self):
        pass

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
