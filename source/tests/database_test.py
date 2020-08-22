import unittest

from source.informationManagers.dataStorageMethods.database import Database

class Database_test(unittest.TestCase):

    class TestableDb(object):

        def init(self):
            pass

        def load(self, name):
            pass

        def save(self, name):
            pass

        def query(self, command):
            return "Lab"

        def iterate(self):
            return iter(["dog", "cat"])
        
        def update(self, key, value):
            pass

    def test_the_database_load_a_specific_database(self):
        self.db.load("MyDb")

    def test_the_database_can_save(self):
        self.db.save("MyDb")
    
    def test_the_database_query(self):
        self.assertEqual("Lab", self.db.query("MyDog"))

    def test_the_database_can_update(self):
        self.db.update("MyDog", "Beagle")

    def test_the_database_can_be_iterated(self):
        iterator = self.db.iterate()
        for x in ["dog", "cat"]:
            self.assertEqual(next(iterator), x)

    def setUp(self):
        self.db = Database(self.TestableDb())
        self.db.init()