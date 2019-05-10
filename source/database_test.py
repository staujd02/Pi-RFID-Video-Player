import unittest

from database import Database

class Database_test(unittest.TestCase):

    class TestableDb(object):

        def init(self):
            pass

        def load(self, name):
            pass

        def save(self):
            pass

        def query(self, command):
            return "Lab"
        
        def update(self, command):
            pass

    def test_the_database_load_a_specific_database(self):
        self.db.load("MyDb")

    def test_the_database_can_save(self):
        self.db.save()
    
    def test_the_database_query(self):
        self.assertEqual("Lab", self.db.query("MyDog"))

    def test_the_database_can_update(self):
        self.db.update("MyDog")

    def setUp(self):
        self.db = Database(self.TestableDb())
        self.db.init()