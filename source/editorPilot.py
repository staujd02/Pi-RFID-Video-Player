from sys import exit

from source.editorController import EditorController
from source.dataStructures import Video

class EditorPilot(EditorController):
    
    def events(self):
        return {
            "save": self.save,
            "quit": self.quit,
            "assignKill": self.assignKill,
            "beginCardScan": self.scanButtonHandler,
            "updateRepository": self.updateRepository,
            "videoSelectedEvent": self.videoSelectedEvent
        }

    def save(self):
        self.env.update()
        self.videos.save(self.env.VideoList)
        self.cards.save(self.env.UuidTable)
        self.linker.save(self.env.LinkedTable)

    def quit(self):
        ans = self.messenger.showSaveAndExit()
        if ans == 'yes':
            self.save()
        exit(0)
    
    def assignKill(self):
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
            
    def videoSelectedEvent(self, event):
        if self.gui.getCurrentCard() != "":
            self.linker.pair(self.gui.getCurrentCard(), event)
    
    def updateRepository(self):
        pass
