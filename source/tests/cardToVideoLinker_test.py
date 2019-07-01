import unittest
import os

from source.informationManagers.cardToVideoLinker import CardToVideoLinker

from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation

class CardToVideoLinker_test(unittest.TestCase):
    
    FILE='test.csv'
    STORE_FILE='videos.csv'
    KILLER_FILE='killers.csv'
    videos = ["1,Jurassic Park,C:/Videos,True\n", "2,Star Wars,C:/DVDs,False\n", "5,Indiana Jones,C:/Videos,True"]
    killers = []
    
    def test_linker_can_loads_an_existing_list(self):
        self.linker.pair("Red_Card", "Indiana Jones")
        self.linker.save()
        self.linker = CardToVideoLinker(self.fakeVideos, self.killers, self.FILE)
        self.linker.init()
        self.assertEqual(["Indiana Jones", "C:/Videos","True"], self.linker.resolve("Red_Card"))

    def test_cards_can_be_linked_to_kill_code(self):
        self.linker.pair("Green_Card", self.linker.KillCode)
        self.assertEqual(self.linker.KillCode, self.linker.resolve("Green_Card"))
    
    def test_cards_linked_to_the_kill_code_can_be_saved(self):
        self.linker.pair("Green_Card", self.linker.KillCode)
        self.linker.save()
        self.fakeVideos = self.initDatabase(self.STORE_FILE)
        self.linker = CardToVideoLinker(self.fakeVideos, self.killers, self.FILE)
        self.linker.init()
        self.assertEqual(self.linker.KillCode, self.linker.resolve("Green_Card"))

    def test_cardToVideoLinker_exists(self):
        self.assertIsNotNone(self.linker)

    def test_cards_paired_to_inactive_videos_throw_an_exception(self):
        errorThrown = False
        try:
            self.linker.pair("Green_Card", "Indiana Jones")
            self.linker.pair("Green_Card", "Star Wars")
        except self.linker.CannotPairToInactiveVideo:
            errorThrown = True
        self.assertTrue(errorThrown)

    def setUp(self):
        self.createTestCSV(self.STORE_FILE, self.videos)     
        self.createTestCSV(self.KILLER_FILE, self.killers)     
        self.fakeVideos = self.initDatabase(self.STORE_FILE)
        self.fakeKillers = self.initDatabase(self.KILLER_FILE)
        self.linker = CardToVideoLinker(self.fakeVideos, self.fakeKillers, self.FILE)
        self.linker.init()
    
    def initDatabase(self, name):
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
        if os.path.isfile(self.KILLER_FILE):
            os.remove(self.KILLER_FILE)