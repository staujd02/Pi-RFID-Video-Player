import logging
from tkinter import messagebox

from source.environment.environment import Environment
from source.editorGUI import EditorGUI
from source.messenger.messenger import Messenger
from source.providers.rfidScannerProvider import RFIDScannerProvider
from source.providers.soundProvider import SoundProvider
from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.cardToVideoLinker import CardToVideoLinker
from source.wrapper.cardScanWrapper import CardScanWrapper

# Top TODO:
#     == Update Video Player (
#        > New way of accessing videos
#        > Environment
#        > Main engine could largely stay the same
#     )
#     == Create Migrator (
#         > Handle moving file list from one device to another
#         > Verify with monster scan function
#     )
#    == Add Optional features to GUI
#         > Toggle filter to hide inactive videos 
#         > Option to purge all inactive videos (with large warnings!)
#
#   -----> Create one test service, initial master list state --> end state (track copy calls)
#   --: Cases :--
#      Record in MasterList and not on local device, but is on external device (0,1)
#      Record in MasterList and not on any device (0,0)
#      Record in MasterList and on local device and on external device (1,1)
#      Record in MasterList and only on local device (1,0)
#      Record in MasterList and on local device, different location and on external device
#      Record in MasterList and only on local device, different location
#      Record not in MasterList and not on local device, but is on external device (0,1)
#      Record not in MasterList and on local device and on external device (1,1)
#      Record not in MasterList and only on local device (1,0)
#
#   -- Scan psudeo --
#   PreflightChecks() ==> is the source usb actually among connected devices?
#   MarkAllRecordsAsInactive()
#   list = ScanAndParse { title, and path parse into video records }
#   (onDevice, notOnDevice) = SplitList(list) ---> sorts between records on device and not
#   notOnDevice = FilterDuplicates(onDevice, notOnDevice) ---> remove records in external devices that also appear in local device 
#                                                           ---> group by title and remove all external references that appear in local
#                                                              ---> otherwise take the first title record
#   for each record onDevice:
#       UpdateFilePath(record)
#       MarkRecordAsActive(record)
#   for each record notOnDevice:
#       cpLocation = AddRecordOrFindExisting(record) -> adds/finds id: returns copy destinatation (does not mark as Active!)
#       Copy(source: record.loc, dst: cpLocation) // copy first so not adding bad records
#       MarkRecordAsActive(record)

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

    def configureGUI(self, master):
        self.gui = EditorGUI(master, self.events(), self.env.Usb)

    def configureScanners(self, SoundResource, RFIDResource):
        sound = self.configureSoundProvider(SoundResource)
        self.rfid = self.configureScannerProvider(RFIDResource)
        self.cardScan = CardScanWrapper(sound, self.rfid)

    def configureDataProviders(self):
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