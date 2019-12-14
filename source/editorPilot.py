from sys import exit

from source.editorController import EditorController
from source.dataStructures import Video

class EditorPilot(EditorController):
    
    def save(self):
        self.env.update()
        self.videos.save(self.env.VideoList)
        self.linker.save()

    def quit(self):
        ans = self.messenger.showSaveAndExit()
        if ans == 'yes':
            self.save()
        exit(0)
    
    def assignKill(self):
        self.gui.clearCurrentSelection()
        currentCard = self.gui.getCurrentCard()
        if currentCard:
            self.linker.pair(currentCard, self.linker.KillCode)
    
    def scanButtonHandler(self):
        self.cardScan.runScan()
        cardKey = self.cardScan.getFormattedResult()
        if cardKey != None:
            self.resolvePositiveScanResults(cardKey)

    def resolvePositiveScanResults(self, cardKey):
        self.gui.setCurrentCard(cardKey)
        self.gui.clearCurrentSelection()
        entry = self.lookUpMatchingEntry(cardKey)
        self.resolveEntry(entry)

    def resolveEntry(self, entry):
        self.lastSelection = None
        if entry == self.linker.CardNotLinked:
            self.messenger.showCardIsNotPaired()
            return
        if entry == self.linker.KillCode:
            self.messenger.showCardScannedIsAKiller()
            return
        self.highlightMatchingVideo(Video(entry))

    def lookUpMatchingEntry(self, cardKey):
        try:
            return self.linker.resolve(cardKey)
        except self.linker.CardNotLinked:
            return self.linker.CardNotLinked

    def highlightMatchingVideo(self, video):
        self.gui.setListBoxSelection(video.name)
        self.lastSelection = video.name
            
    def videoSelectedEvent(self, event):
        if self.gui.getCurrentCard() != "":
            self.linkVideo(self.gui.getCurrentCard(), event, self.handleUnlinkedCard)
    
    def linkVideo(self, card, videoName, handler):
        try:
            self.linker.pair(card, videoName)
        except self.linker.CannotPairToInactiveVideo:
            handler()
    
    def handleUnlinkedCard(self):
        self.gui.setListBoxSelection(self.lastSelection)
        self.messenger.showCannotPairToInactiveVideos()

    def updateRepository(self):
        pass
    
    # Implementation Hooks

    def events(self):
        return {
            "save": self.save,
            "quit": self.quit,
            "assignKill": self.assignKill,
            "beginCardScan": self.scanButtonHandler,
            "updateRepository": self.updateRepository,
            "videoSelectedEvent": self.videoSelectedEvent
        }
    
    def postConfiguration(self):
        self.gui.start()
        detailList = [self.videos.query(vid)[0] for vid in self.videos.iterate()]
        self.gui.setVideoList(detailList)
        if self.gui.currentDeviceName() == self.env.DEFAULT_Usb:
            self.messenger.showDefaultDeviceWarning()
