import unittest
import time
from tkinter import Tk

from editorGUI import EditorGUI


class EditorGUI_test(unittest.TestCase):

    saveClickable = False
    killerClickable = False
    repositoryClickable = False
    itemClickRegistered = False
    itemClicked = ""
    itemSelected = ""
    itemAfterClearingSelection = ""

    def setUp(self):
        self.root = Tk()
        self.root.wm_title('RFID Editor')

    def test_editor_gui_is_functional(self):
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
        return l

    def canDetectSelectionEvent(self, item):
        self.canDetectVideoClick = True
        self.itemClicked = item
        self.itemSelected = self.gui.getTextOfCurrentListBoxSelection()
        self.gui.clearCurrentSelection()
        self.itemAfterClearingSelection = self.gui.getTextOfCurrentListBoxSelection()

    # Can Know what USB device is active

    # Can Highlight an box item
    #         self.videoList.see(i)
    #         self.videoList.selection_clear(0, END)
    #         self.videoList.selection_set(i)
    #         self.videoList.activate(i)

    # Can refresh list box contents
    #     self.videoList.delete(0, END)
    #     for entry in self.vidNAME:
    #         self.videoList.insert(END, entry)