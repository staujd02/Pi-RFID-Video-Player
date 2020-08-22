import unittest
import os
import subprocess

from source.utilities.devices import Devices
from source.informationManagers.search.scriptedFileSearch import ScriptedFileSearch
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.dataStorageMethods.database import Database

class Migrator_test(unittest.TestCase):

    TEST_SCAN_OUTPUT = "temp.test.csv"
    EMPTY_FILE = "temp.test.empty.csv"

    class ProcessProvider(object):
        cmdCalled = "not called"

        def call(self, cmd, shell=False):
            self.cmdCalled = cmd

    class FakeScriptedFileSearch:

        TEMP_LIST = "temp.test.csv"
        EMPTY_FILE = "temp.test.empty.csv"

        def __init__(self, processProvider):
            self.db = Database(CSVImplementation())
            self.db.init()

        def scan(self, scriptFile, mediaRoot):
            self.calledWithScriptFile = scriptFile 
            self.calledWithMediaRoot = mediaRoot 
            if(scriptFile == 'returnNothing.sh'):
                self.db.load(self.EMPTY_FILE)
            else:
                self.db.load(self.TEMP_LIST)

        def getList(self):
            return self.db.iterate()

        def getFile(self, key):
            return self.db.query(key)

        def scanHasRun(self):
            return True
    
    def test_devices_wont_crash_given_no_devices_are_found(self):
        devices = self.devices.getList("/media/pi/", "returnNothing.sh")
        self.assertEqual(devices, [])
    
    def test_devices_can_extract_a_device_name_from_a_path(self):
        device = self.devices.extractDeviceNameFromPath("/media/pi/usb4/file/some/odd.tst", "/media/pi/")
        self.assertEqual(device, "usb4")
    
    def test_devices_can_provide_a_list_of_devices(self):
        devices = self.devices.getList("/media/pi/", "scriptMe.sh")
        self.assertEqual(devices, [ "usb2", "usb3", "sourceDevice"])

    def setUp(self):
        self.createTestCSVs()
        self.scriptedFileSearch = self.FakeScriptedFileSearch(self.ProcessProvider())
        self.devices = Devices(self.scriptedFileSearch)

    def createTestCSVs(self):
        f = open(self.TEST_SCAN_OUTPUT, "w")
        f.writelines([
            "1,Title 1,/media/pi/usb2/Title 1\n",
            "2,Title 3,/media/pi/sourceDevice/Title 3\n",
            "2,Title 3,/media/pi/usb3/Title 3\n",
            "10,Title 8,/media/pi/usb2/Title 8\n",
            "11,Title 9,/media/pi/sourceDevice/Title 9\n"
        ])
        f.close()
        f = open(self.EMPTY_FILE, "w")
        f.writelines(["\n"])
        f.close()

    def tearDown(self):
        os.remove(self.TEST_SCAN_OUTPUT)
        os.remove(self.EMPTY_FILE)