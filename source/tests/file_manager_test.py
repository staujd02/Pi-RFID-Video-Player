import unittest
import os

from source.utilities.fileManager import FileManager

class FileManager_test(unittest.TestCase):

    TEST_FILE = 'test.txt'
    EXTRA_TEST_FILE = 'test.txt'
    
    def test_file_manager_can_create_a_file(self):
        FileManager.guaranteeFileExist(self.TEST_FILE)
        self.assertTrue(os.path.isfile(self.TEST_FILE))
    
    def test_file_manager_can_create_a_list_of_files(self):
        FileManager.guaranteeListOfFilesExist([self.TEST_FILE, self.EXTRA_TEST_FILE])
        self.assertTrue(os.path.isfile(self.TEST_FILE))
        self.assertTrue(os.path.isfile(self.EXTRA_TEST_FILE))
    
    def tearDown(self):
        if os.path.isfile(self.TEST_FILE):
            os.remove(self.TEST_FILE)
        if os.path.isfile(self.EXTRA_TEST_FILE):
            os.remove(self.EXTRA_TEST_FILE)