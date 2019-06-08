import unittest
import os

from dataLinker import DataLinker
from database import Database
from csvImplementation import CSVImplementation

class DataLinker_test(unittest.TestCase):

    FILE='test.csv'
    STORE_FILE='videos.csv'

    def setUp(self):
        self.fakeVideos = self.initDatabase(self.STORE_FILE, self.videos)
        self.linker = DataLinker(self.fakeVideos, self.FILE)
        self.linker.init()

    def test_dataLinker_can_do_custom_checks_for_pairing(self):
        errorThrown = False
        try:
            self.linker.pair("Green_card", "Indiana Jones", precheck=lambda pair: pair[0][0] != 'J')
            self.linker.pair("Green_card", "Indiana Jones", precheck=lambda pair: pair[0][0] != 'I')
        except self.linker.PairPreCheckFailed:
            errorThrown = True
        self.assertTrue(errorThrown, msg="Expected exception to have been thrown")

    def test_datalinker_throws_error_for_unlinked_cards(self):
        errorThrown = False
        try:
            self.linker.resolve("Green_card")
        except self.linker.CardNotLinked:
            errorThrown = True
        self.assertTrue(errorThrown, msg="Expected exception to have been thrown")

    def test_datalinker_can_pair_entries(self):
        self.linker.pair("Green_card", "Indiana Jones")
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Green_card"))

    def test_datalinker_can_overwrite_a_previous_pair(self):
        self.linker.pair("Green_card", "Indiana Jones")
        self.linker.pair("Green_card", "Star Wars")
        self.assertEqual(["Star Wars", "C:/DVDs", "False"], self.linker.resolve("Green_card"))

    def test_datalinker_can_loads_an_existing_list(self):
        self.linker.pair("Red_Card", "Indiana Jones")
        self.linker = DataLinker(self.fakeVideos, self.FILE)
        self.linker.init()
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Red_Card"))
    
    def test_multiple_keys_can_link_to_the_same_stored_object(self):
        self.linker.pair("Green_Card", "Indiana Jones")
        self.linker.pair("Red_Card", "Indiana Jones")
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Green_Card"))
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Red_Card"))

    def test_multiple_keys_can_link_to_the_different_stored_objects(self):
        self.linker.pair("Green_card", "Indiana Jones")
        self.linker.pair("Red_Card", "Star Wars")
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Green_card"))
        self.assertEqual(["Star Wars", "C:/DVDs", "False"], self.linker.resolve("Red_Card"))

    videos = ["1,Jurassic Park,C:/Videos,True\n", "2,Star Wars,C:/DVDs,False\n", "5,Indiana Jones,C:/Videos,True"]

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