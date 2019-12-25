import os

from source.informationManagers.dataStorageMethods.database import Database
from source.informationManagers.dataStorageMethods.csvImplementation import CSVImplementation

class ScriptedFileSearch:

    TEMP_LIST = "temp.list.csv"

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
            '../' + scriptFile + ' > ' + self.TEMP_LIST, shell=True)
        self.db.load(self.TEMP_LIST)
        self.__delete(self.TEMP_LIST)

    def __delete(self, fileName):
        if os.path.isfile(self.TEMP_LIST):
            os.remove(self.TEMP_LIST)

    def getList(self):
        return self.db.iterate()

    def getFile(self, key):
        return self.db.query(key)

    def scanHasRun(self):
        return self.scanComplete
