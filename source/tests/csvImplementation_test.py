import unittest
import os

from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation
from source.informationManagers.dataStorageMethods.database import Database

class CSVImplementation_test(unittest.TestCase):

    TEST_DB = "TestDb.csv"

    def test_csv_can_query_by_the_first_column(self):
        self.assertEqual(self.db.query("2"), ["Donkey", "Dreary"])

    def test_csv_can_query_by_the_first_column_and_get_the_last_item(self):
        self.assertEqual(self.db.query("5"), ["Horse", "Champion"])

    def test_csv_can_update_an_entry(self):
        self.db.update("5", ["Horse", "Starlight"])
        self.assertEqual(self.db.query("5"), ["Horse", "Starlight"])
    
    def test_csv_can_save_modifications_to_data(self):
        self.db.update("5", ["Horse", "Dusty"])
        self.db.save(self.TEST_DB)
        self.db.load(self.TEST_DB)
        self.assertEqual(self.db.query("5"), ["Horse", "Dusty"])
        self.assertEqual(self.db.query("2"), ["Donkey", "Dreary"])

    def test_csv_can_be_iterated(self):
        iterator = self.db.iterate()
        self.assertEqual(["Monkey", "Melvin"], self.db.query(next(iterator)))
        self.assertEqual(["Donkey", "Dreary"], self.db.query(next(iterator)))
        self.assertEqual(["Horse", "Champion"], self.db.query(next(iterator)))

    def setUp(self):
        self.createTestCSV()
        self.db = CSVImplementation.openDB(Database, self.TEST_DB)

    def createTestCSV(self):
        f = open(self.TEST_DB, "w")
        f.writelines(["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"])
        f.close()

    def tearDown(self):
        os.remove(self.TEST_DB)