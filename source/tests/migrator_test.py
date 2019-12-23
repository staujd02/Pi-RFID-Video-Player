import unittest
import os
import subprocess

from source.migrators.migrator import Migrator
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.search.scriptedFileSearch import ScriptedFileSearch
from source.informationManagers.dataStorageMethods.database import Database


class Migrator_test(unittest.TestCase):

    TEST_DB = "TestDb.csv"
    TEST_SCAN_OUTPUT = "temp.list.csv"

    class CopyProvider(object):
        filesCopied = []

        def copyfile(self, source, dest):
            self.filesCopied.append([source, dest])

    class ProcessProvider(object):
        def call(self, cmd, shell=False):
            pass

    def test_migrator_throws_exception_when_source_usb_not_found_in_results(self):
        self.migrator.migrate("sourceDevice")
        self.assertIsNotNone(self.migrator)

    def test_migrator_copies_the_right_files(self):
        self.migrator.migrate("sourceDevice")
        self.assertEqual(self.CopyProvider.filesCopied, [
            ["/media/pi/usb2/Title 1", "/media/pi/sourceDevice/Title 1"],
            ["/media/pi/usb2/Title 7", "/media/pi/sourceDevice/Title 7"]
        ])

    def test_migrator_updates_the_database_appropriately(self):
        self.migrator.migrate("sourceDevice")
        l = [self.videoDatabase.query(i) for i in self.videoDatabase.iterate()]
        self.assertEqual(l, [
            ["Title 1","/media/pi/sourceDevice/Title_1",True],
            ["Title 2","/media/pi/sourceDevice/Title_2",False],
            ["Title 3","/media/pi/sourceDevice/Title_3",True],
            ["Title 4","/media/pi/sourceDevice/Title_4",True],
            ["Title 5","/media/pi/sourceDevice/sub_folder/Title_5",True],
            ["Title 6","/media/pi/sourceDevice/sub_folder/Title_6",True],
            ["Title 7","/media/pi/sourceDevice/Title_7",True],
            ["Title 8","/media/pi/sourceDevice/Title_8",True],
            ["Title 9","/media/pi/sourceDevice/Title_9",True]
        ])

    def setUp(self):
        self.createTestCSVs()
        self.videoDatabase = CSVImplementation.openDB(Database, self.TEST_DB)
        self.scriptedFileSearch = ScriptedFileSearch(self.ProcessProvider())
        self.migrator = Migrator(
            self.scriptedFileSearch, self.videoDatabase, self.CopyProvider)

    def createTestCSVs(self):
        f = open(self.TEST_DB, "w")
        f.writelines([
            "1,Title 1,/media/pi/sourceDevice/Title 1,True",
            "2,Title 2,/media/pi/sourceDevice/Title 2,True",
            "3,Title 3,/media/pi/sourceDevice/Title 3,True",
            "4,Title 4,/media/pi/sourceDevice/Title 4,True",
            "5,Title 5,/media/pi/sourceDevice/Title 5,True",
            "6,Title 6,/media/pi/sourceDevice/Title 6,True"
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
