
from database import Database
from csvImplementation import CSVImplementation

class DataLinker(object):

    def __init__(self, primaryStore):
        self.primaryStore = primaryStore
        self.linkage = {}

    def pair(self, key1, secondaryStoreValue):
        for item in self.primaryStore.iterate():
            if self.primaryStore.query(item)[0] == secondaryStoreValue:
                self.linkage.update({key1: item})
                return

    def resolve(self, key):
        pairedKey = self.linkage.get(key)
        return self.primaryStore.query(pairedKey)
    
