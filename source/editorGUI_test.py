import unittest
import time
from tkinter import Tk

from editorGUI import EditorGUI


class EditorGUI_test(unittest.TestCase):

    saveClickable = False
    killerClickable = False
    repositoryClickable = False

    def setUp(self):
        self.root = Tk()
        self.root.wm_title('RFID Editor')

    def test_editor_gui_is_functional(self):
        gui = EditorGUI(self.root, "Mine Is", [], [
                        "Burlap", "Sandlot"], self.eventDictionary())
        gui.start()
        self.gui = gui
        self.root.mainloop()
        self.assertEqual(True, self.saveClickable)
        self.assertEqual(True, self.killerClickable)
        self.assertEqual(True, self.repositoryClickable)
        self.assertEqual("Card Was Set", gui.getCurrentCard())

    def eventDictionary(self):
        return {
            "save": self.performAllTests,
            "quit": self.quit,
            "assignKill": self.canAssignKiller,
            "beginCardScan": self.canScanCard,
            "updateRepository": self.canUpdateRepository
        }

    def performAllTests(self):
        self.saveClickable = True

    def canScanCard(self):
        self.gui.setCurrentCard("Card Was Set")
        self.gui.startCardScan(self.timerFunction)
        
    def timerFunction(self):
        t = time.time()
        while time.time() - t < 5:
            pass

    def canAssignKiller(self):
        self.killerClickable = True

    def canUpdateRepository(self):
        self.repositoryClickable = True

    def quit(self):
        self.root.quit()

    # can disable button r?
    # can enable button r?
        # perhaps, disable while running is appropriate

    # Can deselect an active Box item
    #     self.videoList.selection_clear(0, END)
    # Can Highlight an box item
    #         self.videoList.see(i)
    #         self.videoList.selection_clear(0, END)
    #         self.videoList.selection_set(i)
    #         self.videoList.activate(i)
    # Can refresh list box contents
    #     self.videoList.delete(0, END)
    #     for entry in self.vidNAME:
    #         self.videoList.insert(END, entry)
    # Can know when an item is selected
    #     selection = event.widget.curselection()