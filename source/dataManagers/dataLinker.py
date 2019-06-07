import os

from database import Database
from csvImplementation import CSVImplementation

class DataLinker(object):

    def __init__(self, primaryStore, dataFile):
        self.dataFile = dataFile
        self.linkage = Database(CSVImplementation())
        self.primaryStore = primaryStore
    
    def init(self):
        self.linkage.init()
        if os.path.isfile(self.dataFile):
            self.linkage.load(self.dataFile)
        
    def pair(self, key, secondaryStoreValue):
        for item in self.primaryStore.iterate():
            if self.primaryStore.query(item)[0] == secondaryStoreValue:
                self.linkage.update(key, item)
                break
        self.linkage.save(self.dataFile)

    def resolve(self, key):
        pairedKey = self.linkage.query(key)
        return self.primaryStore.query(pairedKey[0])
    
