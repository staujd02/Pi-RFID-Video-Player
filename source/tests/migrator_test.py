import unittest
import os
import subprocess

from source.migrators.migrator import Migrator
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.search.scriptedFileSearch import ScriptedFileSearch
from source.informationManagers.dataStorageMethods.database import Database

class Migrator_test(unittest.TestCase):

    TEST_DB = "TestDb.csv"
    TEST_SCAN_OUTPUT = "temp.test.csv"

    class CopyProvider(object):
        filesCopied = []

        def copyfile(self, source, dest):
            self.filesCopied.append([source, dest])

    class FakeMessenger(object):
        def __init__(self):
            self.messages = []
            self.updates = []

        def sendMessage(self, message):
            self.messages.append(message)
        
        def sendUpdate(self, message):
            self.updates.append(message)

    class ProcessProvider(object):
        cmdCalled = "not called"

        def call(self, cmd, shell=False):
            self.cmdCalled = cmd

    class FakeScriptedFileSearch:

        TEMP_LIST = "temp.test.csv"

        def __init__(self, processProvider):
            self.db = Database(CSVImplementation())
            self.db.init()

        def scan(self, scriptFile, mediaRoot):
            self.calledWithScriptFile = scriptFile 
            self.calledWithMediaRoot = mediaRoot 
            self.db.load(self.TEMP_LIST)

        def getList(self):
            return self.db.iterate()

        def getFile(self, key):
            return self.db.query(key)

        def scanHasRun(self):
            return True
    
    def test_migrator_correctly_interfaces_with_the_scanner(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scriptMe.sh")
        self.assertEqual(self.scriptedFileSearch.calledWithScriptFile, "scriptMe.sh")
        self.assertEqual(self.scriptedFileSearch.calledWithMediaRoot, "/media/pi/")
    
    def test_migrator_correctly_projects_its_activities(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scriptMe.sh")
        self.assertEqual(self.messenger.updates, [
            "Scanning...",
            "Copying Title 1",
            "Copying Title 7",
            "Done"
        ])
    
    def test_migrator_correctly_records_its_activities(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scriptMe.sh")
        self.assertEqual(self.messenger.messages, [
            "Marking all records as inactive...",
            "Scanning media devices...",
            "Found 6 record(s) on source device",
            "Found 5 record(s) on non-source devices",
            "6 unique record(s) confirmed on the source device",
            "2 new title(s) discovered",
            "Copying Title 1 from /media/pi/sourceDevice/Title 1 to /media/pi/sourceDevice/Title 1",
            "Copying Title 7 from /media/pi/usb2/Title 7 to /media/pi/sourceDevice/Title 7",
            "Migration complete"
        ])

    def test_migrator_throws_exception_when_source_usb_not_found_in_results(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scanner.sh")
        self.assertIsNotNone(self.migrator)

    def test_migrator_copies_the_right_files(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scanner.sh")
        self.assertEqual(self.CopyProvider.filesCopied, [
            ["/media/pi/usb2/Title 1", "/media/pi/sourceDevice/Title 1"],
            ["/media/pi/usb2/Title 7", "/media/pi/sourceDevice/Title 7"]
        ])

    def test_migrator_updates_the_database_appropriately(self):
        self.migrator.migrate("sourceDevice", "/media/pi/", "scanner.sh")
        l = [self.videoDatabase.query(i) for i in self.videoDatabase.iterate()]
        self.assertEqual(l, [
            ["Title 1","/media/pi/sourceDevice/Title 1",'True'],
            ["Title 2","/media/pi/sourceDevice/Title 2",'False'],
            ["Title 3","/media/pi/sourceDevice/Title 3",'True'],
            ["Title 4","/media/pi/sourceDevice/Title 4",'True'],
            ["Title 5","/media/pi/sourceDevice/sub_folder/Title 5",'True'],
            ["Title 6","/media/pi/sourceDevice/sub_folder/Title 6",'True'],
            ["Title 8","/media/pi/sourceDevice/Title 8",'True'],
            ["Title 9","/media/pi/sourceDevice/Title 9",'True'],
            ["Title 7","/media/pi/sourceDevice/Title 7",'True'],
        ])

    def setUp(self):
        self.createTestCSVs()
        self.videoDatabase = CSVImplementation.openDB(Database, self.TEST_DB)
        self.scriptedFileSearch = self.FakeScriptedFileSearch(self.ProcessProvider())
        self.messenger = self.FakeMessenger()
        self.migrator = Migrator(
            self.scriptedFileSearch, self.videoDatabase, self.CopyProvider(), self.messenger
        )

    def createTestCSVs(self):
        f = open(self.TEST_DB, "w")
        f.writelines([
            "1,Title 1,/media/pi/sourceDevice/Title 1,True\n",
            "2,Title 2,/media/pi/sourceDevice/Title 2,True\n",
            "3,Title 3,/media/pi/sourceDevice/Title 3,True\n",
            "4,Title 4,/media/pi/sourceDevice/Title 4,True\n",
            "5,Title 5,/media/pi/sourceDevice/Title 5,True\n",
            "6,Title 6,/media/pi/sourceDevice/Title 6,True\n"
        ])
        f.close()
        f = open(self.TEST_SCAN_OUTPUT, "w")
        f.writelines([
            "1,Title 1,/media/pi/usb2/Title 1\n",
            "2,Title 3,/media/pi/sourceDevice/Title 3\n",
            "3,Title 3,/media/pi/usb2/Title 3\n",
            "4,Title 4,/media/pi/sourceDevice/Title 4\n",
            "5,Title 5,/media/pi/sourceDevice/sub_folder/Title 5\n",
            "6,Title 5,/media/pi/usb2/Title 5\n",
            "7,Title 6,/media/pi/sourceDevice/sub_folder/Title 6\n",
            "8,Title 7,/media/pi/usb2/Title 7\n",
            "9,Title 8,/media/pi/sourceDevice/Title 8\n",
            "10,Title 8,/media/pi/usb2/Title 8\n",
            "11,Title 9,/media/pi/sourceDevice/Title 9\n"
        ])
        f.close()

    def tearDown(self):
        os.remove(self.TEST_DB)
        os.remove(self.TEST_SCAN_OUTPUT)

#  --: Cases :--
# Title 1: Record in MasterList and not on local device, but is on external device [CC]
# Title 2: Record in MasterList and not on any device (0,0)
# Title 3: Record in MasterList and on local device and on external device (1,1)
# Title 4: Record in MasterList and only on local device (1,0)
# Title 5: Record in MasterList and on local device, different location and on external device
# Title 6: Record in MasterList and only on local device, different location
# Title 7: Record not in MasterList and not on local device, but is on external device (0,1) [CC]
# Title 8: Record not in MasterList and on local device and on external device (1,1)
# Title 9: Record not in MasterList and only on local device (1,0)

#  --: Edge Cases :--
# Title 10: Record not in MasterList and on local device twice in different locations (1,0)
# Title 11: Record in MasterList and on local device twice in different locations (1,0)
# Title 12: Record not in MasterList and on two external devices (1,0)
# Title 13: Record in MasterList and on two external devices (1,0)
# Title 14: Record in MasterList and on two external devices (1,0)
