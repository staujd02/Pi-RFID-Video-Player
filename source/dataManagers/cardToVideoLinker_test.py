import unittest
import os

from cardToVideoLinker import CardToVideoLinker

from database import Database
from csvImplementation import CSVImplementation

class CardToVideoLinker_test(unittest.TestCase):
    
    FILE='test.csv'
    STORE_FILE='videos.csv'
    videos = ["1,Jurassic Park,C:/Videos,True\n", "2,Star Wars,C:/DVDs,False\n", "5,Indiana Jones,C:/Videos,True"]

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
        self.fakeVideos = self.initDatabase(self.STORE_FILE, self.videos)
        self.linker = CardToVideoLinker(self.fakeVideos, self.FILE)
        self.linker.init()
    
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