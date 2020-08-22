import unittest
import time
from tkinter import Tk

from source.editorGUI import EditorGUI

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

    def startGUI(self):
        gui = EditorGUI(self.root, self.eventDictionary())
        gui.start()
        return gui

    def DISABLED_test_device_button_text_can_be_set(self):
        gui = self.startGUI()
        gui.setDeviceControlText("Scanning..", False)
        self.root.mainloop()

    def DISABLED_test_usb_devices_are_accessible(self):
        gui = self.startGUI()
        devices = ["USB1", "USB2"]
        gui.setDeviceList(devices)
        self.assertEqual(gui.activeDevices,  devices)
        self.assertEqual(gui.currentDeviceName(),  devices[0])
        gui.setActiveDevice("USB2")
        self.assertEqual(devices[1], gui.currentDeviceName())
        errorThrown = False
        try:
            gui.setActiveDevice("Missing_USB")
        except gui.DeviceNotFound:
            errorThrown = True
        self.assertTrue(errorThrown)

    def DISABLED_test_editor_gui_is_functional(self):
        self.gui = self.startGUI()
        self.root.mainloop()
        self.assertEqual(True, self.saveClickable)
        self.assertEqual(True, self.killerClickable)
        self.assertEqual(True, self.repositoryClickable)
        self.assertEqual("Card Was Set", self.gui.getCurrentCard())
        self.assertNotEqual("", self.itemClicked)
        self.assertEqual(self.itemSelected, self.itemClicked)
        self.assertEqual(None, self.itemAfterClearingSelection)
        self.assertEqual("Extra Device", self.gui.currentDeviceName())
        self.assertEqual("Lost World", self.itemAfterMakingSelection)
        self.assertEqual(False, self.threwCustomError)
        self.assertEqual("Jurassic Park", self.selectionSuccessfullyMade)

    def eventDictionary(self):
        return {
            "save": self.performAllTests,
            "quit": self.quit,
            "assignKill": self.canAssignKiller,
            "beginCardScan": self.canScanCard,
            "updateRepository": self.canUpdateRepository,
            "videoSelectedEvent": self.canManageSelectionList
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

    def canManageSelectionList(self, item):
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