from dataLinker import DataLinker

class CardToVideoLinker(DataLinker):

    KillCode = "<STOP APPLICATION>"
    
    @staticmethod
    def openFullInstance(primaryDb, path):
        l = CardToVideoLinker(primaryDb, path)
        l.init()
        return l

    def resolve(self, key):
        try:
            return self.__resolve(key)
        except KeyError:
            raise self.CardNotLinked(key)

    def __resolve(self, key):
        pairedKey = self.linkage.query(key)
        if pairedKey == self.KillCode:
            return self.KillCode
        return self.primaryStore.query(pairedKey[0])

    def pair(self, cardID, videoName):
        try:
            self.__killCodeWrappedPairing(cardID, videoName)
        except super(CardToVideoLinker, self).PairPreCheckFailed:
            raise self.CannotPairToInactiveVideo(videoName, cardID)

    def __killCodeWrappedPairing(self, cardID, videoName):
        if videoName == self.KillCode:
            self.__killCodePair(cardID)
            return
        super(CardToVideoLinker, self).pair(
            cardID, videoName, self.__checkVideoIsActive)
    
    def __killCodePair(self, cardID):
        self.linkage.update(cardID, self.KillCode)
        self.linkage.save(self.dataFile)

    def __checkVideoIsActive(self, video):
        return video[2] == 'True'

    class CannotPairToInactiveVideo(Exception):
        def __init__(self, video, card):
            self.video = video
            self.card = card
