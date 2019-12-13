
import unittest
import os

from source.editorPilot import EditorPilot
from source.tests.testDoubles.testableCardScanPilot import TestableCardScanPilot
from source.dataStructures import Video
from source.informationManagers.cardToVideoLinker import CardToVideoLinker
from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation

class EditorGUI_test(unittest.TestCase):
    FILE = 'test.csv'
    STORE_FILE = 'videos.csv'
    videos = ["1,Jurassic Park,C:/Videos,True\n",
              "2,Star Wars,C:/DVDs,False\n",
              "5,Indiana Jones,C:/Videos,True"]

    def setUp(self):
        self.createTest("DUMMY_CARD_ID")

    def test_when_the_default_source_is_active_a_warning_is_shown(self):
        self.createTest("NEW_DUMMY_CARD_ID")
        self.test.gui.setCurrentDeviceName(self.test.env.DEFAULT_Usb)
        self.test.postConfiguration()
        self.assertTrue(self.test.messenger.showedDefaultDeviceWarning)
    
    def test_when_a_non_default_source_is_set_a_warning_is_NOT_shown(self):
        self.createTest("NEW_DUMMY_CARD_ID")
        self.test.postConfiguration()
        self.assertFalse(self.test.messenger.showedDefaultDeviceWarning)

    def test_cards_can_be_scanned(self):
        self.createTest(None)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.cardScan.scanWasCalled)
    
    def test_given_a_card_was_scanned_whenAVideoIsSelected_its_linked(self):
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

    def test_when_a_pairing_is_rejected_the_old_link_is_highlighted(self):
        self.test.linker.pair("DUMMY_CARD_ID", "Indiana Jones")
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Indiana Jones")
        self.test.videoSelectedEvent("Star Wars")
        self.assertEqual("Indiana Jones", Video(self.test.linker.resolve("DUMMY_CARD_ID")).name)
        self.assertEqual("Indiana Jones", self.test.gui.selectedVideo)

    def when_no_video_was_linked_and_pairing_is_rejected_it_reverts_to_no_selection(self, parameter_list):
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Star Wars")
        self.assertEqual(None, self.test.gui.selectedVideo)
    
    def test_when_no_card_is_scanned_the_display_is_blank(self):
        self.createTest(None)
        self.test.scanButtonHandler()
        self.assertEqual("", self.test.gui.getCurrentCard())

    def test_scanned_cards_are_set_to_the_display(self):
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertEqual("DUMMY_CARD_ID", self.test.gui.getCurrentCard())

    def test_when_a_valid_card_is_scanned_the_video_list_is_cleared(self):
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.gui.wasCleared)
    
    def test_when_a_valid_kill_card_is_scanned_it_has_nothing_selected(self):
        self.test.lastSelection = "Ghost Busters"
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Star Wars")
        self.assertEqual(None, self.test.gui.selectedVideo)
    
    def test_when_a_valid_kill_card_is_assigned_no_video_is_active(self):
        self.test.lastSelection = "Ghost Busters"
        self.test.linker.pair("DUMMY_CARD_ID", "Jurassic Park")
        self.test.scanButtonHandler()
        self.test.assignKill()
        self.assertEqual(True, self.test.gui.wasCleared)
    
    def test_when_a_valid_kill_card_is_scanned_it_shows_a_message(self):
        self.test.linker.pair("DUMMY_CARD_ID", self.test.linker.KillCode)
        self.test.scanButtonHandler()
        self.assertTrue(self.test.messenger.showedCardMessage)
    
    def test_when_a_card_is_linked_to_an_inactive_video_a_message_is_displayed(self):
        self.test.linker.pair("DUMMY_CARD_ID", "Jurassic Park")
        self.test.scanButtonHandler()
        self.test.videoSelectedEvent("Star Wars")
        self.assertTrue(self.test.messenger.showedInactiveMessage)
    
    def test_when_a_valid_card_is_scanned_it_highlights_a_video_pair(self):
        self.test.linker.pair("DUMMY_CARD_ID", "Jurassic Park")
        self.test.scanButtonHandler()
        self.assertEqual("Jurassic Park", self.test.gui.selectedVideo)

    def test_when_an_unlinked_card_is_scanned_it_shows_a_message(self):
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