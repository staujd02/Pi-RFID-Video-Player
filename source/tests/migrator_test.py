import unittest
import os

from source.migrators.migrator import Migrator
# from source.informationManagers.dataStorageMethods.database import Database

class Migrator_test(unittest.TestCase):

    # TEST_DB = "TestDb.csv"

    def test_csv_can_query_by_the_first_column(self):
        self.assertIsNotNone(self.migrator)

    def setUp(self):
        # self.createTestCSV()
        # self.db = CSVImplementation.openDB(Database, self.TEST_DB)
        self.migrator = Migrator()

    def createTestCSV(self):
        # f = open(self.TEST_DB, "w")
        # f.writelines(["1,Monkey,Melvin\n", "2,Donkey,Dreary\n", "5,Horse,Champion"])
        # f.close()
        pass

    def tearDown(self):
        # os.remove(self.TEST_DB)
        pass