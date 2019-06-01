import unittest
import time
from tkinter import Tk

from editorGUI import EditorGUI

class EditorGUI_test(unittest.TestCase):

    saveClickable = False
    killerClickable = False
    repositoryClickable = False
    itemClickRegistered = False
    threwCustomError = False
    itemClicked = ""
    itemSelected = ""
    itemAfterClearingSelection = ""
    itemAfterMakingSelection = ""
    selectionSuccessfullyMade = ""

    def setUp(self):
        self.root = Tk()
        self.root.wm_title('RFID Editor')

    def DISABLED_test_editor_gui_is_functional(self):
        gui = EditorGUI(self.root, "Mine Is", ["Extra Device", "Mine Is"],
                        self.createVideoList(), self.eventDictionary())
        gui.start()
        self.gui = gui
        self.root.mainloop()
        self.assertEqual(True, self.saveClickable)
        self.assertEqual(True, self.killerClickable)
        self.assertEqual(True, self.repositoryClickable)
        self.assertEqual("Card Was Set", gui.getCurrentCard())
        self.assertNotEqual("", self.itemClicked)
        self.assertEqual(self.itemSelected, self.itemClicked)
        self.assertEqual(None, self.itemAfterClearingSelection)
        self.assertEqual("Extra Device", gui.currentDeviceName())
        self.assertEqual("Lost World", self.itemAfterMakingSelection)
        self.assertEqual(True, self.threwCustomError)
        self.assertEqual("Jurassic Park", self.selectionSuccessfullyMade)

    def eventDictionary(self):
        return {
            "save": self.performAllTests,
            "quit": self.quit,
            "assignKill": self.canAssignKiller,
            "beginCardScan": self.canScanCard,
            "updateRepository": self.canUpdateRepository,
            "videoSelectedEvent": self.canDetectSelectionEvent
        }

    def performAllTests(self):
        self.saveClickable = True

    def canScanCard(self):
        self.gui.setCurrentCard("Card Was Set")
        self.gui.startCardScan(self.timerFunction)

    def timerFunction(self):
        t = time.time()
        while time.time() - t < 1:
            pass

    def canAssignKiller(self):
        self.killerClickable = True

    def canUpdateRepository(self):
        self.repositoryClickable = True

    def quit(self):
        self.root.quit()

    def createVideoList(self):
        l = ["Burlap", "Sandlot"]
        for x in range(10):
            l.append("Unnamed: " + str(x))
        l.append("Lost World")
        return l

    def canDetectSelectionEvent(self, item):
        self.canDetectVideoClick = True
        self.itemClicked = item
        self.itemSelected = self.gui.getTextOfCurrentListBoxSelection()
        self.gui.clearCurrentSelection()
        self.itemAfterClearingSelection = self.gui.getTextOfCurrentListBoxSelection()
        self.gui.setListBoxSelection("Lost World")
        self.itemAfterMakingSelection = self.gui.getTextOfCurrentListBoxSelection()
        try:
            self.gui.setListBoxSelection("Jurassic Park")
        except self.gui.VideoUnavailable:
            self.threwCustomError = True
        self.gui.setVideoList(self.secondVideoList())
        self.gui.setListBoxSelection("Jurassic Park")
        self.selectionSuccessfullyMade = self.gui.getTextOfCurrentListBoxSelection()

    def secondVideoList(self):
        return ["Jurassic Park", "Jaws", "Star Wars", "Indiana Jones"]