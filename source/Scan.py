import os

from database import Database
from csvImplementation import CSVImplementation


class Scan:

    # NAME = []
    # PATH = []
    # PK = []

    # processProvider = subprocess  ==> Main Class Consideration
    def __init__(self, processProvider):
        self.db = Database(CSVImplementation())
        self.db.init()
        self.processProvider = processProvider
        self.scanComplete = False

    # SCANNER = 'scanner.sh'  ==> Main Class Consideration
    def scan(self, scriptFile):
        self.scanComplete = True
        self.processProvider.call(
            '../' + scriptFile + ' > temp.list', shell=True)
        self.db.load("temp.list")
        self.delete("temp.list")

    def delete(self, fileName):
        if os.path.isfile("temp.list"):
            os.remove("temp.list")

    def getList(self):
        return self.db.iterate()

    def getFile(self, key):
        return self.db.query(key)

    def scanHasRun(self):
        return self.scanComplete
