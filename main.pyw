from tkinter import *
from source.editorPilot import EditorPilot

import pygame
# import Adafruit_PN532 as PN532

class DummyRFID(object):

    class StandInPN532:
        def begin(self):
            pass
        def SAM_configuration(self):
            pass
        def read_passive_target(self):
            return bytearray([0xb4,0xff,0x25,0x5d])

    def PN532(self, cs=11, sclk=22, mosi=11, miso=55):
        return self.StandInPN532()

root = Tk()
root.wm_title('RFID Editor')
app = EditorPilot(root, pygame, DummyRFID())
root.mainloop()