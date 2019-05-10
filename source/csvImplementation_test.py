import unittest

from csvImplementation import CSVImplementation
from database import Database

class CSVImplementation_test(unittest.TestCase):

    TEST_DB = "TestDb.csv"

    def test_csv_can_load_a_specific_database(self):
        self.createTestCSV()
        self.db = Database(CSVImplementation())
        self.db.init()
        self.db.load(self.TEST_DB)

    def test_csv_can_query_by_the_first_column(self):
        self.createTestCSV()
        self.db = Database(CSVImplementation())
        self.db.init()
        self.db.load(self.TEST_DB)
        self.assertEqual(self.db.query("2"), ["2", "Donkey", "Dreary"])

    def test_csv_can_query_by_the_first_column_and_get_the_last_item(self):
        self.createTestCSV()
        self.db = Database(CSVImplementation())
        self.db.init()
        self.db.load(self.TEST_DB)
        self.assertEqual(self.db.query("5"), ["5", "Horse", "Champion"])

    def createTestCSV(self):
        f = open(self.TEST_DB, "w")
        f.writelines(["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"])
        f.close()