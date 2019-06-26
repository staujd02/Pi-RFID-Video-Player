from source.editorPilot import EditorPilot

class TestableCardScanPilot(EditorPilot):

    def __init__(self, cardBits="XXBB"):
        self.cardScan = self.TestableCardScan(cardBits)
        self.gui = self.TestableGui()
        self.messenger = self.TestableMessenger()

    class TestableMessenger(object):
        showedMessage = False
        showedCardMessage = False

        def showCardScannedIsAKiller(self):
            self.showedCardMessage = True

        def showCardIsNotPaired(self):
            self.showedMessage = True

    class TestableCardScan(object):
        scanWasCalled = False

        def __init__(self, bits):
            self.bits = bits

        def runScan(self):
            self.scanWasCalled = True

        def getFormattedResult(self):
            return self.bits

    class TestableGui(object):
        currentCard = ""
        wasCleared = False
        selectedVideo = ""

        def getTextOfCurrentListBoxSelection(self):
            return self.selectedVideo

        def setCurrentCard(self, card):
            self.currentCard = card

        def getCurrentCard(self):
            return self.currentCard

        def setListBoxSelection(self, selection):
            self.selectedVideo = selection

        def clearCurrentSelection(self):
            self.wasCleared = True
