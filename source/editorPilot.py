from sys import exit

from editorController import EditorController
from dataStructures import Video

class EditorPilot(EditorController):
    
    def events(self):
        return {
            "save": self.save,
            "quit": self.quit,
            "assignKill": self.assignKill,
            "beginCardScan": self.beginCardScan,
            "updateRepository": self.updateRepository,
            "videoSelectedEvent": self.videoSelectedEvent
        }

    def save(self):
        self.env.update()
        for obj in [self.videos, self.cards, self.linker]:
            obj.save()

    def quit(self):
        ans = self.messenger.showSaveAndExit()
        if ans == 'yes':
            self.save()
        exit(0)
    
    def assignKill(self):
        pass
    
    def beginCardScan(self):
        self.cardScan.runScan()
        res = self.cardScan.getFormattedResult()
        if res != None:
            self.gui.setCurrentCard(res)
            self.gui.clearCurrentSelection()
            try:
                l = Video(self.linker.resolve(res))
                if l == self.linker.KillCode:
                    self.messenger.showCardScannedIsAKiller()
                    return
                self.gui.setListBoxSelection(l.name)
            except self.linker.CardNotLinked:
                pass
            
    def videoSelectedEvent(self, event):
        pass
    
    def updateRepository(self):
        pass
