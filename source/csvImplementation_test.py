import unittest
import os

from csvImplementation import CSVImplementation
from database import Database

class CSVImplementation_test(unittest.TestCase):

    TEST_DB = "TestDb.csv"

    def test_csv_can_query_by_the_first_column(self):
        self.assertEqual(self.db.query("2"), ["Donkey", "Dreary"])

    def test_csv_can_query_by_the_first_column_and_get_the_last_item(self):
        self.assertEqual(self.db.query("5"), ["Horse", "Champion"])

    def test_csv_can_update_an_entry(self):
        self.db.update("5", ["Horse", "Starlight"])
        self.assertEqual(self.db.query("5"), ["Horse", "Starlight"])
    
    # def test_csv_can_save_modifications_to_data(self):
    #     self.db.update({"5", "Horse", "Dusty"})
    #     self.db.save()
    #     self.db.load(self.TEST_DB)
    #     self.assertEqual(self.db.query("5"), ["5", "Horse", "Dusty"])

    def setUp(self):
        self.createTestCSV()
        self.db = Database(CSVImplementation())
        self.db.init()
        self.db.load(self.TEST_DB)

    def createTestCSV(self):
        f = open(self.TEST_DB, "w")
        f.writelines(["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"])
        f.close()

    def tearDown(self):
        os.remove(self.TEST_DB)