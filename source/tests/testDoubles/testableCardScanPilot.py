from source.editorPilot import EditorPilot

class TestableCardScanPilot(EditorPilot):

    def __init__(self, cardBits="XXBB"):
        self.cardScan = self.TestableCardScan(cardBits)
        self.gui = self.TestableGui()
        self.messenger = self.TestableMessenger()
        self.env = self.TestableEnvironment()
        self.migrator = self.TestableMigrator()
        self.devices = self.TestableDeviceUtilities()

    class TestableEnvironment(object):
        DEFAULT_Usb = "not set"
        MEDIA_ROOT = 'mediaRoot'
        SCAN_SCRIPT = 'scriptFile'

    class TestableDeviceUtilities(object):
        def getList(self, mediaList, scriptFile):
            self.mediaList = mediaList
            self.scriptFile = scriptFile
            return ["usb1", "usb2"]

    class TestableMigrator(object):
        def migrate(self, sourceDeviceName, mediaRoot, scriptFile):
            self.sourceDeviceName = sourceDeviceName
            self.mediaRoot = mediaRoot
            self.scriptFile = scriptFile

    class TestableMessenger(object):
        showedMessage = False
        showedCardMessage = False
        showedInactiveMessage = False
        showedDefaultDeviceWarning = False

        def showDefaultDeviceWarning(self):
            self.showedDefaultDeviceWarning = True
        
        def showCannotPairToInactiveVideos(self):
            self.showedInactiveMessage = True

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
        device = "< Not Set >"
        startWasCalled = False
        setVideoListWasCalledWith = False
        deviceList = []

        def setDeviceList(self, l):
            self.deviceList = l

        def setVideoList(self, videoList):
            self.setVideoListWasCalledWith = videoList

        def start(self):
            self.startWasCalled = True

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
        
        def setCurrentDeviceName(self, _device):
            self.device = _device

        def currentDeviceName(self):
            return self.device
