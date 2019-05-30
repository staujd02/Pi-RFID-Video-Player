import unittest
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
            "assignKill": self.NOTHING,
            "beginCardScan": self.canScanCard,
            "updateRepository": self.canUpdateRepository
        }

    def performAllTests(self):
        self.saveClickable = True

    def canScanCard(self):
        self.gui.setCurrentCard("Card Was Set")

    def canAssignKiller(self):
        self.killerClickable = True

    def canUpdateRepository(self):
        self.repositoryClickable = True

    def quit(self):
        self.root.quit()

    def NOTHING(self):
        pass
