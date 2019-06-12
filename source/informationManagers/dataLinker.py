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
    
    def pair(self, key, target, precheck=None):
        if precheck == None:
            self.__pair(key, target, self.__passByDefault)
            return
        self.__pair(key, target, precheck)
    
    def resolve(self, key):
        try:
            return self.__resolve(key)
        except KeyError:
            raise self.CardNotLinked(key)

    def save(self):
        self.linkage.save(self.dataFile)
    
    def __passByDefault(self, ignore):
        return True

    def __pair(self, key, target, precheck):
        self.__updateLink(key, target, precheck)
    
    def __updateLink(self, key, target, precheck):
        for item in self.primaryStore.iterate():
            dboObject = self.primaryStore.query(item)
            if self.__objectMatchesPairRequest(dboObject, target, precheck):
                self.linkage.update(key, item)
                break

    def __objectMatchesPairRequest(self, dboObject, target, precheck):
        if self.__firstColumnMatchesTarget(dboObject, target):
            if not precheck(dboObject):
                raise self.PairPreCheckFailed(dboObject)
            return True

    def __firstColumnMatchesTarget(self, result, target):
        return result[0] == target

    def __resolve(self, key):
        pairedKey = self.linkage.query(key)
        return self.primaryStore.query(pairedKey[0])

    class CardNotLinked(Exception):
        def __init__(self, card):
            self.card = card

    class PairPreCheckFailed(Exception):
        def __init__(self, item):
            self.item = item
