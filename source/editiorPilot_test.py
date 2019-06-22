
import unittest
import os

from editorPilot import EditorPilot
from testDoubles.testableCardScanPilot import TestableCardScanPilot
from source.dataStructures import Video
from informationManagers.cardToVideoLinker import CardToVideoLinker
from informationManagers.dataStorageMethods.database import Database
from informationManagers.dataStorageMethods.csvImplementation import CSVImplementation


class EditorGUI_test(unittest.TestCase):
    FILE = 'test.csv'
    STORE_FILE = 'videos.csv'
    videos = ["1,Jurassic Park,C:/Videos,True\n",
              "2,Star Wars,C:/DVDs,False\n",
              "5,Indiana Jones,C:/Videos,True"]

    def test_cards_can_be_scanned(self):
        self.createTest(None)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.cardScan.scanWasCalled)
    
    def test_given_a_card_was_scanned_whenAVideoIsSelected_its_linked(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Jurassic Park")
        self.assertEqual("Jurassic Park", Video(self.test.linker.resolve("DUMMY_CARD_ID")).name)
    
    def test_given_a_card_was_scanned_when_multiple_VideoIsSelected_the_last_is_linked(self):
        self.createTest("NEW_DUMMY_CARD_ID")
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Jurassic Park")
        self.test.videoSelectedEvent("Indiana Jones")
        self.assertEqual("Indiana Jones", Video(self.test.linker.resolve("NEW_DUMMY_CARD_ID")).name)
    
    def test_given_no_card_was_scanned_and_a_VideoIsSelected_nothing_is_paired(self):
        self.createTest("NEW_DUMMY_CARD_ID")
        self.test.videoSelectedEvent("Indiana Jones")
        error = False
        try:
            self.test.linker.resolve("")
        except self.test.linker.CardNotLinked:
            error = True
        self.assertTrue(error)

    # Rejects pairing when an inactive video is selected - old pair is selected    
    # def test_given_a_card_was_scanned_when_multiple_VideoIsSelected_the_last_is_linked(self):
    #     self.createTest("NEW_DUMMY_CARD_ID")
    #     self.test.scanButtonHandler()
    #     self.test.videoSelectedEvent("Star Wars")
    #     self.assertEqual("Star Wars", Video(self.test.linker.resolve("DUMMY_CARD_ID")).name)
    
    def test_when_no_card_is_scanned_the_display_is_blank(self):
        self.createTest(None)
        self.test.scanButtonHandler()
        self.assertEqual("", self.test.gui.getCurrentCard())

    def test_scanned_cards_are_set_to_the_display(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertEqual("DUMMY_CARD_ID", self.test.gui.getCurrentCard())

    def test_when_a_valid_card_is_scanned_the_video_list_is_cleared(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.gui.wasCleared)
    
    def test_when_a_valid_kill_card_is_scanned_it_has_nothing_selected(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertEqual("", self.test.gui.selectedVideo)
    
    def test_when_a_valid_kill_card_is_scanned_it_shows_a_message(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.messenger.showedCardMessage)

    def test_when_a_valid_card_is_scanned_it_highlights_a_video_pair(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.linker.pair("DUMMY_CARD_ID", "Jurassic Park")
        self.test.scanButtonHandler()
        self.assertEqual("Jurassic Park", self.test.gui.selectedVideo)

    def test_when_an_unlinked_card_is_scanned_it_shows_a_message(self):
        self.createTest("DUMMY_CARD_ID")
        self.test.scanButtonHandler()
        self.assertEqual("", self.test.gui.selectedVideo)
        self.assertTrue(self.test.messenger.showedMessage)
    
    def createTest(self, defaultCardId=None):
        self.test = self.createTestDouble(defaultCardId)

    def createTestDouble(self, card):
        testDouble = TestableCardScanPilot(card)
        testDouble.videos = self.initDatabase(self.STORE_FILE, self.videos)
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
