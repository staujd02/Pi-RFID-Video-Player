import unittest
import os

from dataLinker import DataLinker
from database import Database
from csvImplementation import CSVImplementation

class DataLinker_test(unittest.TestCase):

    def test_datalinker_exists(self):
        self.createStores()
        linker = DataLinker(self.fakeVideos, self.fakeCards)
        self.assertNotEqual(None, linker)
    
    videos = ["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"]
    cards = ["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"]

    def createStores(self):
        self.fakeCards = self.initDatabase("vids.csv", self.cards)
        self.fakeVideos = self.initDatabase("cards.csv", self.videos)

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

