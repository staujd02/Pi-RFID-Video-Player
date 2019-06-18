
import unittest
import os

from editorPilot import EditorPilot
from testDoubles.testableCardScanPilot import TestableCardScanPilot
from informationManagers.cardToVideoLinker import CardToVideoLinker
from informationManagers.dataStorageMethods.database import Database
from informationManagers.dataStorageMethods.csvImplementation import CSVImplementation


class EditorGUI_test(unittest.TestCase):
    FILE = 'test.csv'
    STORE_FILE = 'videos.csv'

    def test_cards_can_be_scanned(self):
        test = TestableCardScanPilot()
        test.beginCardScan()
        self.assertTrue(test.cardScan.scanWasCalled)

    def test_scanned_cards_are_set_to_the_display(self):
        test = TestableCardScanPilot()
        test.beginCardScan()
        self.assertEqual("XXBB", test.gui.getCurrentCard())

    def test_when_no_card_is_scanned_the_display_is_blank(self):
        test = TestableCardScanPilot(None)
        test.beginCardScan()
        self.assertEqual("", test.gui.getCurrentCard())

    def test_when_a_valid_card_is_scanned_video_list_is_cleared(self):
        test = TestableCardScanPilot("BBYY")
        test.beginCardScan()
        self.assertTrue(test.gui.wasCleared)

    def test_when_a_valid_card_is_scanned_it_highlights_a_video_pair(self):
        videos = ["1,Jurassic Park,C:/Videos,True\n", "2,Star Wars,C:/DVDs,False\n", "5,Indiana Jones,C:/Videos,True"]
        test = self.createTestDouble(videos)
        test.linker.pair("BBMM", "Jurassic Park")
        test.beginCardScan()
        self.assertEqual("Jurassic Park", test.gui.selectedVideo)
    
    def createTestDouble(self, videos):
        testDouble = TestableCardScanPilot("BBMM")
        testDouble.videos = self.initDatabase(self.STORE_FILE, videos)
        testDouble.linker = CardToVideoLinker(testDouble.videos, self.FILE)
        testDouble.linker.init()
        return testDouble
    
    def initDatabase(self, name, data):
        self.createTestCSV(name, data)     
        db = Database(CSVImplementation())
        db.init()
        db.load(name)
        return db
    
    def createTestCSV(self, name, lines):
        f = open(name, "w")
        f.writelines(lines)
        f.close()

    def tearDown(self):
        if os.path.isfile(self.FILE):
            os.remove(self.FILE)
        if os.path.isfile(self.STORE_FILE):
            os.remove(self.STORE_FILE)

